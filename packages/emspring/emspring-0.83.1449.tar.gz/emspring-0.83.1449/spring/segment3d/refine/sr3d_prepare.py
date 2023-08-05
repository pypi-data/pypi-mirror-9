# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import EMData, Util
from collections import namedtuple
from filter import filt_table
from fundamentals import rot_shift2D, fft
from morphology import threshold_to_zero, ctf_2, binarize, dilation
from scipy import interpolate
from scipy.interpolate.fitpack2 import InterpolatedUnivariateSpline
from spring.csinfrastr.csdatabase import SpringDataBase, base, SegmentTable, refine_base, RefinementCycleSegmentTable, \
    RefinementCycleTable, HelixTable
from spring.csinfrastr.cslogger import Logger
from spring.micprgs.scansplit import Micrograph
from spring.segment2d.segment import Segment
from spring.segment2d.segmentalign2d import SegmentAlign2d
from spring.segment2d.segmentctfapply import SegmentCtfApply
from spring.segment2d.segmentexam import SegmentExam, SegmentExamMask
from spring.segment3d.refine.sr3d_parameters import SegmentRefine3dReadParameters
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from sqlalchemy.sql.expression import desc
from tabulate import tabulate
from utilities import model_blank, generate_ctf, model_circle
import numpy as np
import os
import shutil


class SegmentRefine3dUnbending(SegmentRefine3dReadParameters):

    def get_ref_session_and_last_cycle(self, ref_cycle_id, ref_db_dir=''):
        ref_db = os.path.join(ref_db_dir, 'refinement{0:03}.db'.format(ref_cycle_id))
        temp_ref_db = os.path.join(self.tempdir, 'ref_temp_{0:03}.db'.format(ref_cycle_id))
        shutil.copy(ref_db, temp_ref_db)
        ref_session = SpringDataBase().setup_sqlite_db(refine_base, temp_ref_db)
        
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
            
        return ref_session, temp_ref_db, last_cycle
    

    def get_all_helices_from_last_refinement_cycle(self, ref_cycle_id, spring_db):
        session = SpringDataBase().setup_sqlite_db(base, spring_db)
        current_ref_db = os.path.join(os.path.dirname(spring_db), 'refinement{0:03}.db'.format(ref_cycle_id))
        if os.path.exists(current_ref_db):
            ref_session, temp_ref_db, last_cycle = self.get_ref_session_and_last_cycle(ref_cycle_id, os.path.dirname(spring_db))
        else:
            ref_session = None
            temp_ref_db = None
            last_cycle = None
        
        helices = session.query(HelixTable).order_by(HelixTable.id).all()
        
        return helices, session, ref_session, temp_ref_db, last_cycle
    

    def get_segments_from_helix(self, session, each_helix):
        each_helix_segments = session.query(SegmentTable.stack_id).filter(SegmentTable.helix_id == each_helix.id).all()
    
        return each_helix_segments
    

    def get_segment_ids_from_helix(self, session, each_helix):
        each_helix_segments = self.get_segments_from_helix(session, each_helix)
        each_helix_segments, = list(zip(*each_helix_segments))
        
        return each_helix_segments


    def get_all_segments_from_refinement_cycle(self, ref_session, last_cycle, helix_segments):
        each_ref_segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
        filter(RefinementCycleSegmentTable.stack_id.in_(helix_segments)).\
        order_by(RefinementCycleSegmentTable.id).all()
        
        return each_ref_segments
    

    def get_avg_helix_shift_x_and_y_and_avg_inplane_angles(self, orientation_result):
        avg_helix_x_shifts = np.array([each_result.lavg_helix_shift_x_A for each_result in orientation_result])
        helix_y_shifts = np.array([each_result.helix_shift_y_A for each_result in orientation_result])
        inplane_angles = np.array([each_result.lavg_inplane_angle for each_result in orientation_result])
        
        return avg_helix_x_shifts, helix_y_shifts, inplane_angles
    

    def sort_data_and_discard_duplicates(self, x, y):
        """
         * http://mail.scipy.org/pipermail/scipy-user/2011-February/028341.html
        """
        # Sort data
        j = np.argsort(x)
        x = x[j]
        y = y[j]
    
        # De-duplicate data
        mask = np.r_[True, (np.diff(x) > 0)]
        if not mask.all():
            pass
            # could do something smarter here
        x = x[mask]
        y = y[mask]
        
        return x, y
    

    def extrapolate_second_order_to_end_of_box(self, xcoord, ycoord, avg_rot_angle, alignment_size, stepsize):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.extrapolate_second_order_to_end_of_box(np.arange(10) + 10, np.arange(10) + 5, 45, 5 * np.sqrt(2), np.sqrt(2)) #doctest: +NORMALIZE_WHITESPACE
        (array([  6.,   7.,   8.,   9.,  10.,  11.,  12.,  13.,  14.,  15.,  16.,
                17.,  18.,  19.,  20.,  21.,  22.,  23.]), 
                array([  1.,   2.,   3.,   4.,   5.,   6.,   7.,   8.,   9.,  10.,  11.,
                12.,  13.,  14.,  15.,  16.,  17.,  18.]))
        """
        rotx, roty = Segment().rotate_coordinates_by_angle(xcoord, ycoord, avg_rot_angle, xcoord[0], ycoord[0])
        
        rotx, roty = self.sort_data_and_discard_duplicates(rotx, roty)
        
        left_append = (rotx[0] - np.arange(0, alignment_size, stepsize)[1:])[::-1]
        rotx_append = np.insert(rotx, np.zeros(len(left_append)), left_append)
        
        right_append = (rotx[-1] + np.arange(0, alignment_size, stepsize))[1:]
        rotx_extra = np.append(rotx_append, right_append)
        
        spline = InterpolatedUnivariateSpline(rotx, roty, k=1)
        roty_extra = spline(rotx_extra)
        
        roty_extra = np.polyval(np.polyfit(rotx_extra, roty_extra, 2), rotx_extra)
        
        xcoord_extra, ycoord_extra = Segment().rotate_coordinates_by_angle(rotx_extra, roty_extra, -avg_rot_angle, 
        xcoord[0], ycoord[0])
        
        return xcoord_extra, ycoord_extra
        

    def get_picked_segment_coordinates(self, each_helix_segments, pixelsize):
        hel_x_coordinates = np.array([each_segment.picked_x_coordinate_A / pixelsize 
                                      for each_segment in each_helix_segments])
        hel_y_coordinates = np.array([each_segment.picked_y_coordinate_A / pixelsize 
                                      for each_segment in each_helix_segments])
        
        return hel_x_coordinates, hel_y_coordinates
    

    def fill_in_excluded_quantities_by_interpolation(self, each_helix_segments, each_segment, unbending_angles,
    x_coord, y_coord, each_sel_helix_segments, avg_rot_angle, complete_x, complete_y):
        
        rotx, roty = Segment().rotate_coordinates_by_angle(x_coord, y_coord, avg_rot_angle, complete_x[0], complete_y[0])
        
        comp_rotx, comp_roty = Segment().rotate_coordinates_by_angle(complete_x, complete_y, avg_rot_angle,
        complete_x[0], complete_y[0])
        
        try:
            spline = InterpolatedUnivariateSpline(rotx, roty, k=2)
            int_comp_roty = spline(comp_rotx)
        except:
            int_comp_roty = np.polyval(np.polyfit(rotx, roty, 2), comp_rotx)
            
#            rotx, roty = self.sort_data_and_discard_duplicates(rotx, roty)
#            spline = InterpolatedUnivariateSpline(rotx, roty, k=2)
        
        x_coord, y_coord = Segment().rotate_coordinates_by_angle(comp_rotx, int_comp_roty, -avg_rot_angle,
        complete_x[0], complete_y[0])
        
        distances = np.array([each_segment.distance_from_start_A for each_segment in each_helix_segments])
        sel_distances = np.array([each_segment.distance_from_start_A for each_segment in 
                each_sel_helix_segments])
        
        spline = InterpolatedUnivariateSpline(sel_distances, unbending_angles, k=2)
        unbending_angles = spline(distances)

        return x_coord, y_coord, unbending_angles


    def get_cut_coordinates_named_tuple(self):
        cut_coord = namedtuple('cut_coord', 'x_coord y_coord unbending_angle second_order_fit helix_id')

        return cut_coord



    def get_helix_coordinates_named_tuple(self):
        helix_coord = namedtuple('helix_coord', 'x_coord y_coord')
        
        return helix_coord
    

    def get_helices_coordinates_required_for_unbending_from_database(self, prev_ref_cycle_id, each_binfactor,
    info_series, segment_stack, pixelsize, spring_db='spring.db'):
        large_segment = EMData()
        large_segment.read_image(segment_stack)
        large_segment_size = large_segment.get_xsize()
        
        helices, session, ref_session, temp_ref_db, last_cycle = \
        self.get_all_helices_from_last_refinement_cycle(prev_ref_cycle_id, spring_db)
        
        cut_coordinates = []
        helices_coordinates = []
        
        cut_coord = self.get_cut_coordinates_named_tuple()
        helix_coord = self.get_helix_coordinates_named_tuple()
        
        for each_helix_id, each_helix in enumerate(helices):
            each_helix_segments = session.query(SegmentTable).filter(SegmentTable.helix_id == each_helix.id).all()
            each_helix_stack_ids = [each_segment.stack_id for each_segment in each_helix_segments]
            
            second_order_fits = np.array([each_segment.second_order_fit for each_segment in each_helix_segments])
#            if each_binfactor == info_series[0].bin_factor:
#                if second_order_fits[0] is not None:
#                    second_order_fits /= pixelsize
#            else:
            second_order_fits = np.array([None] * len(second_order_fits))
            
            unbending_angles = [-each_segment.lavg_inplane_angle for each_segment in each_helix_segments]
            
            complete_hel_x_coordinates, complete_hel_y_coordinates = \
            self.get_picked_segment_coordinates(each_helix_segments, pixelsize)
            
            inplane_angles = [each_segment.inplane_angle for each_segment in each_helix_segments]
            avg_ip_angle = inplane_angles[int(len(inplane_angles) / 2)] - 90.0
            
            x_coordinates = complete_hel_x_coordinates
            y_coordinates = complete_hel_y_coordinates
            if last_cycle is not None:
                helix_segment_count = len(each_helix_stack_ids)
                
                each_ref_helix_segments = ref_session.query(RefinementCycleSegmentTable).\
                filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
                filter(RefinementCycleSegmentTable.selected == True).\
                filter(RefinementCycleSegmentTable.stack_id.in_(each_helix_stack_ids)).\
                order_by(RefinementCycleSegmentTable.id).all()
                
                each_ref_helix_stack_ids = [each_segment.stack_id for each_segment in each_ref_helix_segments]
                    
                each_sel_helix_segments = session.query(SegmentTable).\
                filter(SegmentTable.stack_id.in_(each_ref_helix_stack_ids)).all()
                    
                select_ratio = len(each_ref_helix_segments) / float(helix_segment_count)
                if select_ratio > 0.4:
                    
                    hel_x_coordinates, hel_y_coordinates = self.get_picked_segment_coordinates(each_sel_helix_segments,
                    pixelsize)
                    
                    avg_helix_x_shifts, helix_y_shifts, inplane_angles = \
                    self.get_avg_helix_shift_x_and_y_and_avg_inplane_angles(each_ref_helix_segments)
                    
                    fitted_x_shifts, fitted_y_shifts = \
                    SegClassReconstruct().compute_sx_sy_from_shifts_normal_and_parallel_to_helix_axis_with_inplane_angle(
                    avg_helix_x_shifts, helix_y_shifts, inplane_angles)
                    
                    x_coordinates = hel_x_coordinates + fitted_x_shifts
                    y_coordinates = hel_y_coordinates + fitted_y_shifts
                    unbending_angles = (-inplane_angles) % 360
                    
                    if len(complete_hel_x_coordinates) > len(x_coordinates):
                        x_coordinates, y_coordinates, unbending_angles =\
                        self.fill_in_excluded_quantities_by_interpolation(each_helix_segments, each_segment,
                        unbending_angles, x_coordinates, y_coordinates, each_sel_helix_segments, avg_ip_angle,
                        complete_hel_x_coordinates, complete_hel_y_coordinates)
        
                    self.log.ilog('Helix {0} will be unbent using refined coordinates.'.format(each_helix.id))
                ref_session.close()
                os.remove(temp_ref_db)
            else:
                self.log.ilog('Helix {0} will be unbent using picked coordinates.'.format(each_helix.id))
            
            extra_x_coord, extra_y_coord = self.extrapolate_second_order_to_end_of_box(x_coordinates, y_coordinates, 
            avg_ip_angle, large_segment_size, self.stepsize / pixelsize)
                    
#            import matplotlib.pyplot as plt
#            plt.plot(complete_hel_x_coordinates, complete_hel_y_coordinates, 'o', x_coordinates, y_coordinates, '.',
#            extra_x_coord, extra_y_coord, 'x')
#            plt.savefig('tt.pdf')
            
            for each_x_coord, each_y_coord, each_angle, each_fit in zip(x_coordinates, y_coordinates, unbending_angles,
            second_order_fits):
                cut_coordinates.append(cut_coord(each_x_coord, each_y_coord, each_angle, each_fit, each_helix.id))
                
            helices_coordinates.append(helix_coord(extra_x_coord, extra_y_coord))
        
        return helices_coordinates, cut_coordinates
    

    def make_unbending_named_tuple(self):
        unbending = namedtuple('info', 'angle shift_x shift_y')
                
        return unbending
                

    def prepare_unique_updated_stack_name(self, segment_stack, ref_cycle_id):
        large_straightened_segment_stack = '{0}{1}{2}{3}'.format(self.tempdir,
        os.path.splitext(os.path.basename(segment_stack))[0], ref_cycle_id, 
        os.path.splitext(os.path.basename(segment_stack))[-1])

        return large_straightened_segment_stack


    def unbend_window_and_mask_input_stack(self, segment_stack, ref_cycle_id, pixelinfo,
    previous_parameters, mask_params, helices_coordinates, cut_coordinates, masked_segment_stack, resolution_aim):
        self.log.fcttolog()
        self.log.in_progress_log()
        large_segment = EMData()
        large_segment.read_image(segment_stack)
        large_segment_size = large_segment.get_xsize()
        
        large_straightened_segment_stack = self.prepare_unique_updated_stack_name(segment_stack, ref_cycle_id)
        masked_segment_stack = os.path.join(self.tempdir, masked_segment_stack)
        
        unique_tilts, ideal_power_imgs, circle_mask, padsize = \
        self.prepare_binary_layer_line_filters_if_layer_line_filtering_demanded(resolution_aim, ref_cycle_id - 1,
        pixelinfo, self.helical_symmetries[0], self.rotational_symmetry_starts[0])
        
        rectangular_mask = SegmentExam().make_smooth_rectangular_mask(pixelinfo.helixwidthpix, pixelinfo.helix_heightpix,
        pixelinfo.alignment_size)
        
        unbending = self.make_unbending_named_tuple()
        unbending_info = []
        unbending_loginfo = []
        for each_index, each_parameter in enumerate(previous_parameters):

            cut_coord = cut_coordinates[each_parameter.local_id] 
            
            current_coordinates = (cut_coord.x_coord, cut_coord.y_coord)
#             large_segment.read_image(segment_stack, each_parameter.local_id)
            large_segment, frame_stack_names = \
            self.read_large_segment_average_if_running_avg_frames_requested(segment_stack, large_segment,
            each_parameter)

            hel_x = helices_coordinates[cut_coord.helix_id - 1].x_coord
            hel_y = helices_coordinates[cut_coord.helix_id - 1].y_coord
            
            helix_shift_x, helix_shift_y = \
            SegClassReconstruct().compute_distances_to_helical_axis(each_parameter.shift_x, each_parameter.shift_y,
            each_parameter.inplane_angle)
             
            shift_x, shift_yy = \
            SegClassReconstruct().compute_sx_sy_from_shifts_normal_and_parallel_to_helix_axis_with_inplane_angle(
            helix_shift_x, 0.0, -each_parameter.inplane_angle)

            shifted_helix_coord = zip(np.array(hel_x) - shift_x, np.array(hel_y) - shift_yy)
            
            large_straightened_segment, straightened_fit, central_ip_angle = \
            Segment().unbend_segment_using_coordinates(large_segment, large_segment_size, shifted_helix_coord,
            current_coordinates, (cut_coord.x_coord, cut_coord.y_coord), (-cut_coord.unbending_angle)%360,
            cut_coord.second_order_fit)
            
            unbending_loginfo += [[each_parameter.stack_id, each_parameter.local_id, straightened_fit[0],
            straightened_fit[1], straightened_fit[2], self.layer_line_filter]]
            
#            previous_parameters[each_index] = previous_parameters[each_index]._replace(psi=270.0, shift_x=0.0,
#            shift_y=helix_shift_y)
            
            previous_parameters[each_index] = previous_parameters[each_index]._replace(psi=270.0, shift_x=0.0,
            shift_y=helix_shift_y)
            
            unbending_info.append(unbending(central_ip_angle, each_parameter.shift_x, each_parameter.shift_y))
            
            if self.layer_line_filter:# and resolution_aim in ['high', 'max']:
                closest_tilt_id = np.argmin(np.abs(unique_tilts - mask_params[each_index].out_of_plane_tilt))
                
                large_straightened_segment = \
                SegClassReconstruct().filter_image_by_fourier_filter_while_padding(large_straightened_segment,
                large_segment_size, padsize, ideal_power_imgs[closest_tilt_id])
                
            straightened_segment = Util.window(large_straightened_segment, pixelinfo.alignment_size,
            pixelinfo.alignment_size, 1, 0, 0, 0)

            straightened_segment *= rectangular_mask
            straightened_segment.write_image(masked_segment_stack, each_parameter.local_id)
            large_straightened_segment.write_image(large_straightened_segment_stack, each_parameter.local_id)
            
        header = ['stack_id', 'local_id', 'a*x^2', 'b*x', 'c', 'layer-line_filter']
        msg = tabulate(unbending_loginfo, header)
        self.log.tlog('The following segments were straightened according to the square ' + \
        'function:\n{0}'.format(msg))
            
        self.remove_frames_if_running_avg_frames_requested(frame_stack_names)

        return previous_parameters, unbending_info, masked_segment_stack, segment_stack, large_straightened_segment_stack
    

class SegmentRefine3dPreparation(SegmentRefine3dUnbending):

    def define_all_segmentrefine3d_parameters(self, p):
        self.define_input_output_iteration(p)
        self.define_refinement_strategy_options(p)
        self.define_helical_symmetry_parameters(p)
        self.define_alignment_parameters(p)
        self.define_selection_parameters(p)
        self.define_filter_parameters(p)
        self.define_reconstruction_parameters(p)
        self.define_mpi_parameters(p)


    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.define_all_segmentrefine3d_parameters(p)
    

class SegmentRefine3dSymmetry(SegmentRefine3dPreparation):
#     def compute_zsection_percentage_from_width(self, pixelsize, helixwidth, volume_radius):
#         """
#         >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
#         >>> s = SegmentRefine3d()
#         >>> s.compute_zsection_percentage_from_width(1, 50, 50)
#         0.8660254037844386
#         """
#         section_z = np.sqrt(volume_radius ** 2 - ((helixwidth / float(pixelsize)) ** 2 / 4)) / float(volume_radius)
#         
#         return section_z
#     
#     
#     def compute_zsection_percentage_from_rise(self, pixelsize, helical_rise, z_height):
#         """
#         >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
#         >>> s = SegmentRefine3d()
#         >>> s.compute_zsection_percentage_from_rise(1, 40, 100)
#         0.8
#         >>> s.compute_zsection_percentage_from_rise(1, 50, 100)
#         1.0
#         """
#         z_height_pix = z_height * pixelsize
#         multiple_rise = int(z_height_pix / float(helical_rise))
#         section_z = (helical_rise * multiple_rise) / float(z_height_pix)
#         
#         return section_z
#     
# 
#     def symmetrize_volume_old(self, volume, pixelsize, helical_symmetry, point_symmetry, helixwidth, min_zsection=None):
#         helical_rise, helical_rotation = helical_symmetry
#         if helical_rise != 0:
#             volume_radius = volume.get_zsize() / 2
#             z_height = volume.get_zsize() 
#             if min_zsection is None:
#                 section_z = min(self.compute_zsection_percentage_from_width(pixelsize, helixwidth, volume_radius), 
#                         self.compute_zsection_percentage_from_rise(pixelsize, helical_rise, z_height) - 0.01,
#                         0.8)
#             else:
#                 section_z = min_zsection
#                 
#             self.log.ilog('The volume will be helically symmetrized: {0}, {1}, {2}, {3}, {4}'.format(pixelsize, 
#             helical_rise, helical_rotation, section_z, z_height) + ' (pixelsize, rise, rotation, z_section, z_height)')
#             
#             try:
#                 helix_volume_helicise = volume.helicise(pixelsize, helical_rise, -helical_rotation, section_z)
#             except:
#                 helix_volume_helicise = volume.helicise(1, helical_rise / float(pixelsize), -helical_rotation,
#                 section_z)
#         elif helical_rise == 0 and helical_rotation == 0: 
#             helix_volume_helicise = volume.copy()
#         elif helical_rise == 0:
#             multiple = abs(int(360.0 / helical_rotation + 0.5))
#             helix_volume_helicise = volume.symvol('c{0}'.format(multiple))
#             
#         if point_symmetry != 'c1':
#             helix_volume_helicise = helix_volume_helicise.symvol(point_symmetry)
#             
#         return helix_volume_helicise
#     
#  
#     def generate_helical_volume_of_projection_size(self, reference_volume, reconstruction_size, alignment_size,
#     helical_symmetry, pixelsize, point_symmetry, helixwidth, symmetrize=True):
#         reference_volume, padded_in_z = self.adjust_volume_dimension_by_padding_or_windowing(reference_volume,
#         reconstruction_size, alignment_size)
#         
#         assert reference_volume.get_xsize() == reconstruction_size 
#         assert reference_volume.get_ysize() == reconstruction_size 
#         assert reference_volume.get_zsize() == alignment_size
#             
#         if padded_in_z and symmetrize:
#             reference_volume = self.symmetrize_volume(reference_volume, pixelsize, helical_symmetry, point_symmetry, 
#             helixwidth)
#             
#         return reference_volume
    

    def adjust_volume_dimension_by_padding_or_windowing(self, reference_volume, reconstruction_size, alignment_size):
        volsize_x = reference_volume.get_xsize()
        volsize_y = reference_volume.get_ysize()
        volsize_z = reference_volume.get_zsize()
        if volsize_x > reconstruction_size:
            reference_volume = Util.window(reference_volume, reconstruction_size, reference_volume.get_ysize(),
            reference_volume.get_zsize(), 0, 0, 0)
        elif volsize_x < reconstruction_size:
            reference_volume = Util.pad(reference_volume, reconstruction_size, reference_volume.get_ysize(),
            reference_volume.get_zsize(), 0, 0, 0, 'average')
        if volsize_y > reconstruction_size:
            reference_volume = Util.window(reference_volume, reference_volume.get_xsize(), reconstruction_size,
            reference_volume.get_zsize(), 0, 0, 0)
        elif volsize_y < reconstruction_size:
            reference_volume = Util.pad(reference_volume, reference_volume.get_xsize(), reconstruction_size,
            reference_volume.get_zsize(), 0, 0, 0, 'average')
        padded_in_z = False
        if volsize_z > alignment_size:
            reference_volume = Util.window(reference_volume, reference_volume.get_xsize(), reference_volume.get_ysize(),
            alignment_size, 0, 0, 0)
        elif volsize_z < alignment_size:
            reference_volume = Util.pad(reference_volume, reference_volume.get_xsize(), reference_volume.get_ysize(),
            alignment_size, 0, 0, 0, 'average')
            
            padded_in_z = True

        return reference_volume, padded_in_z


    def get_sizes_that_increase_by_percent(self, cur_zsize, max_zsize, percent):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.get_sizes_that_increase_by_percent(20, 100, 0.2)
        [24, 28, 34, 40, 48, 58, 70, 84, 100]
        >>> s.get_sizes_that_increase_by_percent(100, 100, 0.2)
        [100]
        """
        inc = int(cur_zsize * percent)
        sizes = list(range(cur_zsize, max_zsize, inc))
        
        per_sizes = []
        per_size = cur_zsize
        even = 0
        for each_size in sizes:
            per_size += int(per_size * percent)
            if per_size %2 != even:
                per_size +=1
            per_sizes.append(per_size)
            
        vol_sizes = [int(each_size) for each_size in per_sizes if each_size < max_zsize] + [max_zsize]
        
        return vol_sizes
        

    def symmetrize_volume(self, vol, pixelsize, section_size, rise, rotation):
        if rise != 0:
            vol = vol.helicise(pixelsize, rise, -rotation, section_size)
        elif rise == 0 and rotation == 0:
            vol = vol.copy()
        elif rise == 0:
            multiple = abs(int(360.0 / float(rotation) + 0.5))
            vol = vol.symvol('c{0}'.format(multiple))
        
        return vol
        

    def symmetrize_long_volume_in_steps(self, vol, helical_symmetry, pixelsize, xy_size, z_size):
        section_size = 0.8
        rise, rotation = helical_symmetry
        z_sizes = self.get_sizes_that_increase_by_percent(vol.get_zsize(), z_size, 1 - section_size)
        sections = [0.7] + (len(z_sizes) - 1) * [section_size]
        for each_zsize, each_section_size in zip(z_sizes, sections):
            vol, padded_in_z = self.adjust_volume_dimension_by_padding_or_windowing(vol, xy_size, each_zsize)
            vol = self.symmetrize_volume(vol, pixelsize, each_section_size, rise, rotation)
            
        return vol


    def generate_long_helix_volume(self, vol, xy_size, z_size, helical_symmetry, pixelsize, point_symmetry):
        vol = self.symmetrize_long_volume_in_steps(vol, helical_symmetry, pixelsize, xy_size, z_size)
        
        hel_vol = vol.copy()
        if point_symmetry != 'c1':
            apix_attr = ['apix_x', 'apix_y', 'apix_z']
            apix_vals = [hel_vol.get_attr(each_attr) for each_attr in apix_attr]
            
            hel_vol = hel_vol.symvol(point_symmetry)
            [hel_vol.set_attr(each_attr, each_val) for each_val, each_attr in zip(apix_vals, apix_attr)]
            
        return hel_vol
    

    def compute_rec_size_for_helix(self, helixwidth, helical_rise, pixelsize):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> SegmentRefine3d().compute_rec_size_for_helix(200, 1.408, 1.2)
        220
        """
        rec_size_in_Angstrom = 2 * np.sqrt((1.1 * helixwidth / 2.0) ** 2 + (max(helical_rise, 60.0)) ** 2)
        reconstruction_size = rec_size_in_Angstrom / pixelsize
        if reconstruction_size >= 32:
            reconstruction_size = Segment().determine_boxsize_closest_to_fast_values(reconstruction_size)
        else:
            reconstruction_size = int(reconstruction_size)
        
        return reconstruction_size
    
    
    def compute_alignment_size_in_pixels(self, alignment_size_in_A, pixelsize):
        alignment_size = alignment_size_in_A / pixelsize
        if alignment_size >= 32:
            alignment_size = Segment().determine_boxsize_closest_to_fast_values(alignment_size)
        else:
            alignment_size = int(alignment_size)
        
        return alignment_size


    def compute_alignment_and_reconstruction_size_in_pixels(self, alignment_size_in_A, helical_rise, helixwidth_in_A,
    pixelsize):
        """
        # values for fast boxsizes from http://blake.bcm.edu/emanwiki/EMAN2/BoxSize
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.compute_alignment_and_reconstruction_size_in_pixels(200, 1.408, 100, 1.0)
        (220, 168)
        >>> s.compute_alignment_and_reconstruction_size_in_pixels(200, 1.408, 300, 1.0)
        (352, 352)
        """
        reconstruction_size = self.compute_rec_size_for_helix(helixwidth_in_A, helical_rise, pixelsize)
        alignment_size = self.compute_alignment_size_in_pixels(alignment_size_in_A, pixelsize)
        alignment_size = max(alignment_size, reconstruction_size)
        
        return alignment_size, reconstruction_size 
    

    def rescale_reference_volume_in_case_vol_pixelsize_differs_from_current_pixelsize(self, reconstruction_size,
    reference_volume, pixelsize, alignment_size=None):
        if alignment_size is None:
            alignment_size = reconstruction_size
        if reference_volume.has_attr('apix_z'):
            if reference_volume.get_attr('apix_z') != 1.0:
                ref_pixelsize = reference_volume.get_attr('apix_z')
                scaling_factor = ref_pixelsize / pixelsize
                if scaling_factor > 1:
                    reference_volume, padded_in_z = \
                    self.adjust_volume_dimension_by_padding_or_windowing(reference_volume,
                    reconstruction_size, alignment_size)
                    reference_volume.scale(scaling_factor)
                elif scaling_factor < 1:
                    reference_volume.scale(scaling_factor)

        return reference_volume


    def get_ref_file_name(self, ref_id):
        reference_file = '{prefix}_ref_mod{ref_id:03}{ext}'.format(prefix=os.path.splitext(self.outfile_prefix)[0],
        ref_id=ref_id, ext=os.path.splitext(self.outfile_prefix)[-1])

        return reference_file


    def make_reference_info_named_tuple(self):
        return namedtuple('ref_info', 'model_id ref_file prj_stack fine_prj_stack helical_symmetry point_symmetry ' + \
                          'rotational_symmetry fsc')


    def prepare_reference_volumes(self):
        rises = np.array([each_hel_sym[0] for each_hel_sym in self.helical_symmetries])
        rotations = np.array([each_hel_sym[1] for each_hel_sym in self.helical_symmetries])
        
        reference_volume = EMData()
        reference_info = []
        ref_info_nt = self.make_reference_info_named_tuple()

        if len(set(self.polar_helices)) == 1:
            self.polar_helix = list(set(self.polar_helices))[0]
        else:
            self.polar_helix = 'polar'

        point_symmetries = [] 
        for each_ref_id in list(range(len(self.helical_symmetries))):
            point_symmetries.append(SegClassReconstruct().determine_point_group_symmetry_from_input(self.polar_helices[each_ref_id],
            self.rotational_symmetry_starts[each_ref_id]))
        
        read_sym = True
        if len(self.references) == 1 and len(self.helical_symmetries) > 1:
            self.references = len(self.helical_symmetries) * self.references
            read_sym = False

        for each_ref_id, (each_helical_symmetry, each_point_sym, each_rot_sym) in enumerate(zip(
        self.helical_symmetries, point_symmetries, self.rotational_symmetry_starts)):
            alignment_size, reconstruction_size = \
            self.compute_alignment_and_reconstruction_size_in_pixels(self.alignment_size_in_A, each_helical_symmetry[0],
            self.helixwidth, self.ori_pixelsize)
        
            if self.reference_option:
                reference_volume.read_image(self.references[each_ref_id])
                if reference_volume.has_attr('helical rise') and reference_volume.has_attr('helical rotation') and read_sym:
                    vol_rise = reference_volume.get_attr('helical rise')
                    vol_rot = reference_volume.get_attr('helical rotation')
                    
                    closest_sym_id = np.argmin(np.sqrt((rises - vol_rise) ** 2 + (rotations - vol_rot) ** 2))
                    helical_symmetry = self.helical_symmetries[closest_sym_id]
                    point_sym = point_symmetries[closest_sym_id]
                    rotational_symmetry = self.rotational_symmetry_starts[closest_sym_id]
                else:
                    helical_symmetry = each_helical_symmetry
                    point_sym = each_point_sym
                    rotational_symmetry = each_rot_sym

                reference_volume = \
                self.rescale_reference_volume_in_case_vol_pixelsize_differs_from_current_pixelsize(reconstruction_size,
                reference_volume, self.ori_pixelsize, alignment_size)

            else:
                helix_inner_widthpix = int(round(self.helix_inner_width / self.ori_pixelsize))
                helixwidthpix = int(round(self.helixwidth / self.ori_pixelsize))
                reference_volume = SegClassReconstruct().make_smooth_cylinder_mask(helixwidthpix,
                helix_inner_widthpix, alignment_size, width_falloff=0.1)
                helical_symmetry = each_helical_symmetry
                rotational_symmetry = each_rot_sym
                point_sym = each_point_sym

            reference_file = self.get_ref_file_name(each_ref_id)
            reference_volume.write_image(reference_file)

            reference_info.append(ref_info_nt(each_ref_id, reference_file, None, None, helical_symmetry, point_sym,
            rotational_symmetry, None))
            
        return reference_info


    def prepare_3dctf_avg_squared(self, reconstruction_size, pixelsize):
        
        temp_db = self.copy_spring_db_to_tempdir()
        session = SpringDataBase().setup_sqlite_db(base, temp_db)
        
        matched_segment = session.query(SegmentTable).filter(SegmentTable.stack_id == 0).first()
        session.close()
        os.remove(temp_db)

        if matched_segment.ctf_convolved:
            if matched_segment.ctftilt_applied:
                choice = 'ctftilt'
            if matched_segment.ctffind_applied:
                choice = 'ctffind'
            
            astigmatism_option = True
            
            ctf_parameters = SegmentCtfApply().get_ctf_values_from_database_and_compute_local_ctf_based_if_demanded(choice,
            'convolve', astigmatism_option, pixelsize, self.spring_path)
            
            first_ctf = generate_ctf(ctf_parameters[0])
            ctf1d_length = len(ctf_2(reconstruction_size, first_ctf))
            avg_ctf_squared_profile = np.zeros(ctf1d_length)
            for each_ctf_param in ctf_parameters:
                each_ctf = generate_ctf(each_ctf_param)
                each_ctf_2_profile = np.array(ctf_2(reconstruction_size, each_ctf))
                avg_ctf_squared_profile += each_ctf_2_profile
            
            avg_ctf_squared_profile /= float(len(ctf_parameters))
                
            ctf3d_avg_squared = model_blank(reconstruction_size, reconstruction_size, reconstruction_size)
            ctf3d_avg_squared.set_value_at(0, 0, 0, 1)
            ctf3d_avg_squared = fft(filt_table(ctf3d_avg_squared, avg_ctf_squared_profile.tolist()))
            ctf3d_avg_squared_file = self.tempdir + 'ctf3d_avg_squared.hdf'
            ctf3d_avg_squared.write_image(ctf3d_avg_squared_file)
        elif matched_segment.ctf_phase_flipped:
            ctf3d_avg_squared_file = None
            self.ctf_correction = False
            self.log.wlog('3D CTF correction was demanded but according to specified spring.db segments were ' + \
            'previously phase-flipped. Therefore, no further 3D CTF correction required.')
        elif not matched_segment.ctf_phase_flipped and not matched_segment.ctf_convolved:
            msg = 'You requested 3D CTF correction but according to the provided spring.db your input segments ' + \
            'were not CTF corrected (neither phase-flipped nor convolved). Please perform CTF ' + \
            'correction in the program \'segment\' or do not request 3D CTF correction option.'
            raise ValueError(msg)
            
        return ctf3d_avg_squared_file
    

    def prepare_binary_layer_line_filters_if_layer_line_filtering_demanded(self, resolution_aim, each_iteration_number,
    pixelinfo, helical_symmetry, rotational_sym):
        if self.layer_line_filter:# and resolution_aim in ['high', 'max']:
            angular_blur = self.compute_angular_blur_based_on_Crowther_criterion(each_iteration_number,
            self.alignment_size_in_A, pixelinfo.pixelsize)
            
#            angular_blur = None
            projection_parameters = self.generate_Euler_angles_for_projection(self.azimuthal_angle_count,
            self.out_of_plane_tilt_angle_range, self.out_of_plane_tilt_angle_count, helical_symmetry[1])
            
            unique_tilts, padsize, ideal_power_imgs = \
            self.generate_binary_layer_line_filters_including_angular_blur(projection_parameters, pixelinfo,
            helical_symmetry, rotational_sym, angular_blur / 5.0)
            
            circle_mask = model_circle(padsize / 2, padsize, padsize)
        else:
            unique_tilts = None
            ideal_power_imgs = None
            circle_mask = None
            padsize = None
            
        return unique_tilts, ideal_power_imgs, circle_mask, padsize
    


    def add_tempdir_directory_to_filename(self, tempdir, segment_stack, masked_segment_stack):
        local_segment_stack = os.path.join(tempdir, os.path.basename(segment_stack))
        masked_segment_stack = os.path.join(tempdir, os.path.basename(masked_segment_stack))
        
        return local_segment_stack, masked_segment_stack
    

    def get_frame_stack_path(self, ori_large_segment_stack, each_frame_id):
        frame_stack_name = os.path.splitext(ori_large_segment_stack)[0] + '-{0}'.format(each_frame_id) + \
        os.path.splitext(ori_large_segment_stack)[-1]

        frame_stack_path = os.path.join(self.tempdir, os.path.basename(frame_stack_name))
        return frame_stack_path


    def read_large_segment_average_if_running_avg_frames_requested(self, segment_stack, large_segment, each_parameter):
        frame_stack_names = []
        if self.frame_motion_corr and self.frame_avg_window > 2:
            frame_segment = EMData()
            for each_frame_id in list(range(self.frame_avg_window)):
                stack_name = self.get_frame_stack_path(segment_stack, each_frame_id)
                frame_stack_names.append(stack_name)
                if each_frame_id == 0:
                    large_segment.read_image(stack_name, each_parameter.local_id)
                else:
                    frame_segment.read_image(stack_name, each_parameter.local_id)
                    large_segment += frame_segment
        else:
            large_segment.read_image(segment_stack, each_parameter.local_id)

        return large_segment, frame_stack_names


    def remove_frames_if_running_avg_frames_requested(self, frame_stack_names):
        if self.frame_motion_corr and self.frame_avg_window > 2:
            for each_frame_stack in frame_stack_names:
                os.remove(each_frame_stack)


    def window_and_mask_input_stack(self, segment_stack, pixelinfo, mask_params, masked_segment_stack, each_info,
    ref_cycle_id):
        self.log.fcttolog()
        self.log.in_progress_log()
        large_segment = EMData()
        large_segment.read_image(segment_stack)
        large_segment_size = large_segment.get_xsize()
        
        masked_segment_stack = os.path.join(self.tempdir, masked_segment_stack)
        if self.layer_line_filter:
            local_segment_stack = self.prepare_unique_updated_stack_name(segment_stack, ref_cycle_id)
        else:
            local_segment_stack = None
        
        rectangular_mask = SegmentExam().make_smooth_rectangular_mask(pixelinfo.helixwidthpix, pixelinfo.helix_heightpix,
        large_segment_size)
        
        masking_log_info = []
        
        unique_tilts, ideal_power_imgs, circle_mask, padsize = \
        self.prepare_binary_layer_line_filters_if_layer_line_filtering_demanded(each_info.resolution_aim,
        ref_cycle_id, pixelinfo, self.helical_symmetries[0], self.rotational_symmetry_starts[0])
            
        for each_parameter in mask_params:
            large_segment, frame_stack_names = \
            self.read_large_segment_average_if_running_avg_frames_requested(segment_stack, large_segment,
            each_parameter)

            if self.layer_line_filter:# and each_info.resolution_aim in ['high', 'max']:
                closest_tilt_id = np.argmin(np.abs(unique_tilts - each_parameter.out_of_plane_tilt))
                
                rotated_binary_filter = rot_shift2D(ideal_power_imgs[closest_tilt_id],
                -each_parameter.lavg_inplane_angle)
                
                rotated_binary_filter = binarize(rotated_binary_filter, 0.01)
                rotated_binary_filter *= circle_mask
#                rotated_binary_filter.write_image(self.tempdir + 'layer_filter.hdf', each_parameter.local_id)

                large_segment = SegClassReconstruct().filter_image_by_fourier_filter_while_padding(large_segment,
                large_segment_size, padsize, rotated_binary_filter)
                
                large_segment.write_image(local_segment_stack, each_parameter.local_id)
            
            rotated_rectangular_mask = Segment().shift_and_rotate_image(rectangular_mask,
            -each_parameter.lavg_inplane_angle, each_parameter.lavg_helix_shift_x, 0)
            
            large_segment *= rotated_rectangular_mask
            segment = Util.window(large_segment, pixelinfo.alignment_size, pixelinfo.alignment_size, 1, 0, 0, 0)
            segment.write_image(masked_segment_stack, each_parameter.local_id)
            
            masking_log_info += [[each_parameter.stack_id, each_parameter.local_id,
            (-each_parameter.lavg_inplane_angle)%360, each_parameter.lavg_helix_shift_x, self.layer_line_filter]]
            
        msg = tabulate(masking_log_info, list(each_parameter._fields)[0:4] + ['layer line filter'])
        self.log.tlog('The following segments were masked by a rotated rectangle according to their previous ' + \
                      'picking parameters:\n{0}'.format(msg))
            
        self.remove_frames_if_running_avg_frames_requested(frame_stack_names)
                
        return masked_segment_stack, segment_stack, local_segment_stack
            
            
    def build_structural_mask_from_volume(self, reference_vol, helixwidthpix, helix_inner_width_pix, pixelsize,
    sigma_factor=1.0, width_falloff=0.03):
        
        reconstruction_size = reference_vol.get_xsize()
        alignment_size = reference_vol.get_zsize()
        
        cylinder_mask = SegClassReconstruct().make_smooth_cylinder_mask(helixwidthpix, helix_inner_width_pix,
        reconstruction_size, alignment_size, width_falloff)
        
        stat = Micrograph().get_statistics_from_image(reference_vol, cylinder_mask)
        
        binary_vol = binarize(reference_vol * cylinder_mask, sigma_factor * stat.sigma)
        if width_falloff != 0:
            dilation_pixels = 7
            odd = 1
            if (dilation_pixels) % 2 != odd:
                dilation_pixels += 1
            dilation_mask = model_blank(dilation_pixels, dilation_pixels, dilation_pixels, bckg = 1.0)
            structural_mask = dilation(binary_vol, dilation_mask)
        else:
            structural_mask = binary_vol
        
        return structural_mask
    
    
    def compute_prj_size_from_max_out_of_plane_tilt_and_diameter(self, alignment_size, tilt_range, helixwidthpix):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.compute_prj_size_from_max_out_of_plane_tilt_and_diameter(600, [-12, 12], 180)
        675
        """
        max_tilt = max([abs(each_extrema) for each_extrema in tilt_range])
        single_walled_distance_at_end = helixwidthpix * np.sin(np.deg2rad(max_tilt))
        projection_size = alignment_size + int(round(2 * single_walled_distance_at_end))
        
        return projection_size
    
    
    def prepare_volume_for_projection_by_masking_and_thresholding(self, resolution_aim, reference_volume,
    pixelinfo, helical_symmetry, point_symmetry):
        vol_x = reference_volume.get_xsize()
        vol_z = reference_volume.get_zsize()
        if resolution_aim in ['low', 'medium']: 
            vol_mask = SegClassReconstruct().make_smooth_cylinder_mask(pixelinfo.helixwidthpix,
            pixelinfo.helix_inner_widthpix, vol_x, vol_z, width_falloff=0.1)
            
        elif resolution_aim in ['high', 'max']:
            vol_mask = self.build_structural_mask_from_volume(reference_volume, pixelinfo.helixwidthpix,
            pixelinfo.helix_inner_widthpix, pixelinfo.pixelsize)
            
            vol_mask = SegmentExamMask().add_smooth_gaussian_falloff_to_edge_of_binary_mask(vol_x, 0.05, vol_mask)
            
        stat = Micrograph().get_statistics_from_image(reference_volume, vol_mask)
        reference_volume *= vol_mask
        reference_volume = threshold_to_zero(reference_volume, stat.avg)
            
        projection_size = self.compute_prj_size_from_max_out_of_plane_tilt_and_diameter(pixelinfo.alignment_size,
        self.out_of_plane_tilt_angle_range, pixelinfo.helixwidthpix)
        
        reference_volume = self.generate_long_helix_volume(reference_volume, pixelinfo.reconstruction_size,
        projection_size, helical_symmetry, pixelinfo.pixelsize, point_symmetry)

#         reference_volume = self.generate_helical_volume_of_projection_size(reference_volume,
#         pixelinfo.reconstruction_size, projection_size, helical_symmetry, pixelinfo.pixelsize, point_symmetry,
#         self.helixwidth)
        
        return projection_size, reference_volume, stat.sigma
    

    def apply_square_root_fsc_filter_to_coefficients(self, fsc_lines, filter_coefficients, projection_size,
    custom_filter_file, pixelsize):
        if self.fsc_filter and fsc_lines is not None:
            fsc_arr = np.array(fsc_lines.cylinder_masked)
            fsc_arr[fsc_arr < 0] = 0
            fsc_arr = np.sqrt(fsc_arr)
            
            res = SegmentExam().make_oneoverres(filter_coefficients, pixelsize)
            f = interpolate.interp1d(np.linspace(res[0], res[-1], len(fsc_arr)), fsc_arr)
            res_int = np.linspace(res[0], res[-1], len(res))
            fsc_int = f(res_int)
            first_005 = np.where(fsc_int < 0.05)[0]
            
            if len(first_005) != 0:
                if res_int[first_005[0]] > 0.05:
                    fsc_int[first_005[0]:] = 0.0
                else:
                    fsc_int = SegmentAlign2d().prepare_filter_function(self.high_pass_filter_option,
                    self.high_pass_filter_cutoff, self.low_pass_filter_option, 0.05, pixelsize,
                    projection_size, 0.08, self.custom_filter_option, custom_filter_file, self.bfactor)
                    fsc_int = np.array(fsc_int)
            
            filter_coefficients = np.array(filter_coefficients) * fsc_int
            filter_coefficients = filter_coefficients.tolist()
            log_pairs = list(zip(res, filter_coefficients))
            log_info = tabulate(log_pairs, ['Resolution', 'filter_coefficients'])
            
            self.log.ilog('The reference volume is filtered by the square root of the FSC curve:{0}'.format(log_info))
            
        return filter_coefficients
    

    def rescale_freq_filter_columns(self, ori_pixelsize, rescaled_dimension, rescaled_apix, spat_freq, fourier_coeff):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> freq = np.linspace(0, 0.5, 100)
        >>> coeff = np.abs(np.cos(np.linspace(0, np.pi, 100)))
        >>> rescaled_freq, rescaled_coeff = s.rescale_freq_filter_columns(1.2, 44, 2.4, freq, coeff)
        >>> len(rescaled_freq)
        22
        >>> rescaled_coeff
        array([ 1.        ,  0.99725998,  0.98905491,  0.97542979,  0.95645925,
                0.93224727,  0.90292654,  0.86865772,  0.82962861,  0.78605309,
                0.73816997,  0.68624164,  0.63055267,  0.57140824,  0.50913246,
                0.44406661,  0.37656726,  0.3070043 ,  0.23575894,  0.1632216 ,
                0.08978981,  0.01586596])
        """
        binfactor = rescaled_apix / ori_pixelsize
        reduced_length = int(len(fourier_coeff) / binfactor)
        red_fourier_coefficients = fourier_coeff[:reduced_length]
        red_spat_freq = np.linspace(spat_freq[0], spat_freq[-1], reduced_length)
        
        spline = InterpolatedUnivariateSpline(red_spat_freq, red_fourier_coefficients)
        rescaled_spat_freq = np.linspace(spat_freq[0], spat_freq[-1], rescaled_dimension / 2)
        rescaled_f_coeff = np.abs(spline(rescaled_spat_freq))
    
        return rescaled_spat_freq, rescaled_f_coeff
    

    def rescale_custom_filter_file(self, custom_filter_file, ori_pixelsize, rescaled_dimension, rescaled_apix):
        
        ffile = open(custom_filter_file, 'r')
        coeff_lines = ffile.readlines()
        spat_freq = np.array([float(each_line.split()[0]) for each_line in coeff_lines])
        fourier_coeff = np.array([float(each_line.split()[-1]) for each_line in coeff_lines])
        ffile.close()
        
        rescaled_spat_freq, rescaled_f_coeff = self.rescale_freq_filter_columns(ori_pixelsize, rescaled_dimension,
        rescaled_apix, spat_freq, fourier_coeff)
        
        dat_str = '\n'.join(['{0}\t{1}'.format(each_freq, each_f_coeff) 
                             for each_freq, each_f_coeff in zip(rescaled_spat_freq, rescaled_f_coeff)])
        
        rescaled_filter_file = '{0}_rescaled.dat'.format(os.path.splitext(custom_filter_file)[0])
        ffile = open(rescaled_filter_file, 'w')
        ffile.write(dat_str)
        ffile.close()
        
        return rescaled_filter_file
        

    def write_out_reference_volume(self, reference_file, each_iteration_number, ref_cycle_id, reference_volume,
    model_id=None):
        if each_iteration_number == 1:
            os.remove(reference_file.ref_file)
        
        if model_id is None:
            ref_file_name = '{prefix}_ref_{iter:03}{ext}'.format(prefix=os.path.splitext(self.outfile_prefix)[0], 
            iter=ref_cycle_id, ext=os.path.splitext(self.outfile_prefix)[-1])
        else:
            ref_file_name = '{prefix}_mod_{mod:03}_ref_{iter:03}{ext}'.format(prefix=os.path.splitext(self.outfile_prefix)[0], 
            mod=model_id, iter=ref_cycle_id, ext=os.path.splitext(self.outfile_prefix)[-1])

        reference_file = reference_file._replace(ref_file = ref_file_name)

        reference_volume.write_image(reference_file.ref_file)

        return reference_file


    def filter_and_mask_reference_volume(self, resolution_aim, each_reference, pixelinfo, fsc_lines=None):
        self.log.fcttolog()
        
        reference_volume = EMData()
        reference_volume.read_image(each_reference.ref_file)

        projection_size, reference_volume, sigma = \
        self.prepare_volume_for_projection_by_masking_and_thresholding(resolution_aim, reference_volume, pixelinfo,
        each_reference.helical_symmetry, each_reference.point_symmetry)
                                      
        if self.high_pass_filter_option or self.low_pass_filter_option or self.custom_filter_option or \
        self.bfactor != 0 or self.fsc_filter:
            if self.custom_filter_option:
                custom_filter_file = self.rescale_custom_filter_file(self.custom_filter_file, self.ori_pixelsize,
                projection_size, pixelinfo.pixelsize)
            else:
                custom_filter_file = self.custom_filter_file
                
            filter_coefficients = SegmentAlign2d().prepare_filter_function(self.high_pass_filter_option,
            self.high_pass_filter_cutoff, self.low_pass_filter_option, self.low_pass_filter_cutoff, pixelinfo.pixelsize,
            projection_size, 0.08, self.custom_filter_option, custom_filter_file, self.bfactor)
            
            if fsc_lines is not None:
                filter_coefficients = self.apply_square_root_fsc_filter_to_coefficients(fsc_lines, filter_coefficients,
                projection_size, custom_filter_file, pixelinfo.pixelsize)
            
            if self.custom_filter_option:
                os.remove(custom_filter_file)
                
            reference_volume = filt_table(reference_volume, filter_coefficients)
                                                                
        return reference_volume
        
        