# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import EMData, EMUtil, Util, Transform
from collections import namedtuple
import gc
import os
from spring.csinfrastr.csdatabase import SpringDataBase, grid_base, GridRefineTable, GridTable
from spring.csinfrastr.csproductivity import OpenMpi, Temporary
from spring.csinfrastr.csreadinput import OptHandler
from spring.micprgs.scansplit import Micrograph
from spring.segment2d.segment import Segment
from spring.segment2d.segmentexam import SegmentExam
from spring.segment3d.segclassreconstruct_compare import SegClassReconstructCompareVisual
from spring.segment3d.segclassreconstruct_prep import SegClassReconstructPar
import sys

import numpy as np


class SegClassReconstruct3d(SegClassReconstructCompareVisual):
            
    def determine_best_in_plane_rotation_angle(self, class_avg, inplane_rotations, helix_mask=None, helix_shift_x=0.0):
        
        sigmas = []
        for each_inplane_angle in inplane_rotations:
            rot_class_avg = Segment().shift_and_rotate_image(class_avg, each_inplane_angle, helix_shift_x, 0.0)
            if helix_mask is not None:
                rot_class_avg *= helix_mask
            class_avg_profile = SegmentExam().project_helix(rot_class_avg)
            stat = Micrograph().get_statistics_from_image(class_avg_profile)
            sigmas.append(stat.sigma)
            
        rotation = inplane_rotations[np.argmax(sigmas)]
        
        return rotation
    

    def center_and_rotate_image_by_helix_projection(self, helix_width_pixel, inplane_rotations, class_avg, segment_size,
    helix_height):
        helix_mask = SegmentExam().make_smooth_rectangular_mask(helix_width_pixel * 1.5, helix_height, segment_size)
        class_avg_profile = SegmentExam().project_helix(class_avg * helix_mask)
        centerx, symimg_par = Segment().minimize_xposition(class_avg_profile, 0.3 * helix_width_pixel)
        
        inplane_rotation = self.determine_best_in_plane_rotation_angle(class_avg, inplane_rotations, helix_mask,
        centerx)
        
        class_avg_centered = Segment().shift_and_rotate_image(class_avg, inplane_rotation, centerx, 0.0)

        return class_avg_centered, centerx, inplane_rotation


    def center_class_avg(self, infile, centered_class_avg_file, helix_width_pixel, percent_reconstruction_size,
    out_of_plane_tilt_angle):
        class_avg = EMData()
        class_avg.read_image(infile)
        segment_size = class_avg.get_ysize()
        reconstruction_length = percent_reconstruction_size * segment_size / 100
        
        inplane_rotations = np.arange(-10.0, 10.0, 0.05)
        
        class_avg_centered, centerx, inplane_rotation = \
        self.center_and_rotate_image_by_helix_projection(helix_width_pixel, inplane_rotations, class_avg, segment_size,
        reconstruction_length)
        
        class_avg_centered.write_image(centered_class_avg_file)
        
        self.centerx = centerx
        self.inplane_rotation = inplane_rotation
        phi, theta, psi, sx, sy = self.get_standard_proj_parameters(out_of_plane_tilt_angle)
        
        trans = Transform({'type':'SPIDER', 'phi':phi, 'theta':theta, 'psi': psi - self.inplane_rotation, 
        'tx': sx - self.centerx, 'ty':sy, 'scale':1.0})
        
        class_avg.set_attr('xform.projection', trans)
        class_avg.write_image(os.path.basename(infile))
        
        return centered_class_avg_file


    def generate_symmetry_grid_file_name(self, symmetry_pair, volume_name, rise_rot_or_pitch_unit_choice='rise/rotation'):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> SegClassReconstruct().generate_symmetry_grid_file_name([12,50], 'rec_vol.hdf', 'rise/rotation')
        'rec_vol_rise12_rot50.hdf'
        >>> SegClassReconstruct().generate_symmetry_grid_file_name([12,50], 'rec_vol.hdf', 'pitch/unit_number')
        'rec_vol_pitch12_unitno50.hdf'
        >>> SegClassReconstruct().generate_symmetry_grid_file_name([12.003,50.333356], 'rec_vol.hdf', 'rise/rotation')
        'rec_vol_rise12003_rot50333356.hdf'
        >>> SegClassReconstruct().generate_symmetry_grid_file_name([12,50], '/test/rec_vol.hdf', 'pitch/unit_number')
        '/test/rec_vol_pitch12_unitno50.hdf'
        """
        
        if rise_rot_or_pitch_unit_choice == 'rise/rotation':
            symmetry_pair_no_dots = '_rise' + ''.join(str(symmetry_pair[0]).split('.')) + '_rot' + \
            ''.join(str(symmetry_pair[1]).split('.'))
        elif rise_rot_or_pitch_unit_choice == 'pitch/unit_number':
            symmetry_pair_no_dots = '_pitch' + ''.join(str(symmetry_pair[0]).split('.')) + '_unitno' + \
            ''.join(str(symmetry_pair[1]).split('.'))
        symmetry_helix_volume = '{name}{pair}{ext}'.format(name=os.path.splitext(volume_name)[0],
        pair=symmetry_pair_no_dots, ext=os.path.splitext(volume_name)[-1])
        
        return symmetry_helix_volume
    

    def determine_trimmed_image_size(self, infile, percent_reconstruction_size, helixwidth_pix, pixelsize):
        temp = EMData()
        temp.read_image(infile, 0)
        segment_size_in_pixel = temp.get_xsize()
        
        helixheight_pix = int(round(segment_size_in_pixel * percent_reconstruction_size / 100.0, -1))
        trimmed_image_size = max(helixwidth_pix, helixheight_pix)
        if trimmed_image_size - helixheight_pix == 1:
            helixheight_pix -= 1
        
        if helixheight_pix * pixelsize < 2:
            msg = 'Your resulting helix height will be smaller than 2 Angstrom ' + \
            '(\'Percent image reconstruction size\' * segment size * pixelsize) = '
            '({0} * {1} * {2}) < 2 Angstrom '.format(percent_reconstruction_size * segment_size_in_pixel * pixelsize)
            raise ValueError(msg)
            
        return segment_size_in_pixel, trimmed_image_size, helixheight_pix
    
    
    def determine_symmetry_view_count_for_average_helical_rise(self, symmetry_sequence, segment_size_in_pixel,
    trimmed_image_size):
        helical_rises = np.unique([each_pair[0] for each_pair in symmetry_sequence])
        avg_helical_rise = np.mean(helical_rises)
        
        symmetry_views_count = self.determine_symmetry_view_count(segment_size_in_pixel, trimmed_image_size,
        (avg_helical_rise, 0), self.pixelsize, self.minimum_image_count_3d)
        
        return symmetry_views_count


    def determine_symmetry_view_count(self, segment_size_in_pixel, trimmed_image_size, each_symmetry_pair, pixelsize,
    minimum_image_count_3d=8):
        """
        >>> sg = SegClassReconstruct()
        >>> sg.determine_symmetry_view_count(530, 500, ((77.3, 34)), 1, 0)
        1
        >>> sg.determine_symmetry_view_count(575, 500, ((77.3, 34)), 1, 0)
        1
        >>> sg.determine_symmetry_view_count(100, 90, ((10, 34)), 10)
        10
        >>> sg.determine_symmetry_view_count(530, 500, ((0, 0)), 1, 0)
        1
        >>> sg.determine_symmetry_view_count(100, 90, ((20, 34)), 10, 8) #doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
          File '<stdin>', line 1, in <module>
          File 'spring/segment2d/segclassreconstruct.py', line 444, in determine_symmetry_view_count
            raise ValueError, error_message
        ValueError: Number of computed symmetry-related views useful for reconstruction is smaller than 8 (with 
        segment_size of 90/100 pixels and helical rise: 20). No sensible 3D reconstruction possible. Either decrease 
        'Helical rise' < 12 Angstrom or 'percent of reconstruction size' < 84 % parameters. In addition, you can also 
        decrease 'Minimum number of images for 3D reconstruction'.
        
        """
        helical_rise = each_symmetry_pair[0]
        if each_symmetry_pair != (0, 0):
            symmetry_views_count = max(1, int((segment_size_in_pixel - trimmed_image_size) / \
            (helical_rise / pixelsize) + 0.5))
        else:
            symmetry_views_count = 1
        
        if symmetry_views_count < minimum_image_count_3d:
            new_percentage = 100 * (segment_size_in_pixel - (helical_rise * 8 / pixelsize)) / segment_size_in_pixel
            if new_percentage < 0:
                new_percentage = 0
            error_message = 'Number of computed symmetry-related views useful for reconstruction is smaller than ' + \
            '{min_img} '.format(min_img=minimum_image_count_3d)
            
            error_message += '(with segment_size of {0}/{1} pixels '.format(trimmed_image_size, segment_size_in_pixel)+\
            'and helical rise: {0}). No sensible 3D reconstruction possible. '.format(helical_rise)
            
            new_rise=(segment_size_in_pixel-trimmed_image_size) * pixelsize/minimum_image_count_3d
            error_message += 'Either decrease \'Helical rise\' < {0} Angstrom '.format(new_rise) + \
            'or \'percent of reconstruction size\' < {0} % parameters. '.format(new_percentage)
            
            error_message += 'In addition, you can also decrease \'Minimum number of images for 3D reconstruction\'.'
                   
            raise ValueError(error_message)
        
        return symmetry_views_count


    def get_symmetry_transformations_from_helix_input(self, polar_helix, rotational_symmetry_start):
        point_symmetry = self.determine_point_group_symmetry_from_input(polar_helix, rotational_symmetry_start)
        sym_transformations = self.get_symmetry_transformations(point_symmetry)
        
        return sym_transformations
    

    def check_parameter_integritry_and_start_setup(self):
        if EMUtil.get_image_count(self.infile) < self.classno:
            errormsg = 'Requested class number higher than number of images on class average stack.'
            raise ValueError(errormsg)
        
        entered_symmetry_grid = \
        self.generate_rise_rotation_or_pitch_unitnumber_pairs_for_symmetry_grid(self.helical_rise_or_pitch_range,
        self.helical_rise_or_pitch_increment, self.helical_rotation_or_unit_range,
        self.helical_rotation_or_unit_increment)
        
        if self.rise_rot_or_pitch_unit_choice in ['pitch/unit_number']:
            symmetry_grid = SegClassReconstruct().convert_pitch_unit_grid_to_rise_rotation_grid(entered_symmetry_grid)
        else:
            symmetry_grid = entered_symmetry_grid
        
        segment_size_in_pixel, trimmed_image_size, helixheight_pix = self.determine_trimmed_image_size(self.infile,
        self.percent_reconstruction_size, self.helixwidthpix, self.pixelsize)
        
        symmetry_seq = symmetry_grid.ravel()
        entered_symmetry_seq = entered_symmetry_grid.ravel()
        
        if not self.local_grid_option:
            sym_transformations = self.get_symmetry_transformations_from_helix_input(self.polar_helix,
            self.rotational_symmetry_start)
            
            minimum_image_count_3d = self.minimum_image_count_3d / float(len(sym_transformations))
            for each_symmetry_pair in symmetry_seq:
                views = self.determine_symmetry_view_count(segment_size_in_pixel, trimmed_image_size,
                each_symmetry_pair, self.pixelsize, minimum_image_count_3d)
        else:
            minimum_image_count_3d = self.minimum_image_count_3d
                
        return symmetry_seq, entered_symmetry_seq, minimum_image_count_3d
 

class SegClassReconstruct(SegClassReconstruct3d): 

    def make_named_tuple_for_reconstruction(self):
        rec_named_tuple = namedtuple('rec_parameters', 'stack_id local_id phi theta psi x_shift y_shift ' + \
        'inplane_angle mirror seg_ref_id')
        
        return rec_named_tuple
    
    
    def get_alignment_parameters_from_infile(self, infile):
        segment = EMData()
        segment.read_image(infile, 0)
        segment_transform = segment.get_attr('xform.projection')
        determined = segment_transform.get_params('spider')
        rec_parameters = self.make_named_tuple_for_reconstruction()
        
        alignment_parameters = [rec_parameters(0, 0, determined['phi'], determined['theta'], determined['psi'],
        -determined['tx'], -determined['ty'], 0, 1, 0)]
        
        return alignment_parameters, segment
    

    def log_and_stack_alignment_parameters_into_numpy_array(self, alignment_parameters, symmetry_parameters,
    symmetry_rec_loginfo):
        if symmetry_parameters != []:
            self.log.tlog('Asymmetric units count: {0} from segments '.format(len(alignment_parameters)) + \
            '{0}-{1} were prepared for 3D '.format(int(alignment_parameters[0][0]), (alignment_parameters[-1][0])) + \
            'reconstruction with the following alignment parameters:\n{0}'.format(symmetry_rec_loginfo))
            symmetry_parameters = np.vstack(symmetry_parameters)
            
        return symmetry_parameters
    

    def determine_point_group_symmetry_from_input(self, polar_helix, rotational_symmetry):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> SegClassReconstruct().determine_point_group_symmetry_from_input('polar', 2)
        'c2'
        >>> SegClassReconstruct().determine_point_group_symmetry_from_input('apolar', 4)
        'd4'
        """
        if polar_helix in ['apolar']:
            dihedral_symmetry = 'd'
        else:
            dihedral_symmetry = 'c'
        
        point_symmetry = dihedral_symmetry + str(rotational_symmetry)
            
        return point_symmetry
    

    def reconstruct_volume_from_class_average(self, infile, vol_name, segment_size_in_pixel, trimmed_image_size,
    symmetry_views_count, each_rec_number, each_symmetry_pair, point_symmetry, montage_reprj, montage_power):
        if symmetry_views_count is None:
            symmetry_views_count = self.determine_symmetry_view_count(segment_size_in_pixel, trimmed_image_size,
            each_symmetry_pair, self.pixelsize, self.minimum_image_count_3d)
            
        alignment_parameters, class_avg = self.get_alignment_parameters_from_infile(infile)
        
        self.log.fcttolog()
        self.log.in_progress_log()
        
        gc.collect()

        rec_volume, fftvol, weight = self.setup_reconstructor(trimmed_image_size)
        
        rec_stack_info = self.make_rec_stack_info()
        symmetry_helix_volume = self.get_symmetry_file_name(each_symmetry_pair, vol_name)
            
        rec_stack = rec_stack_info(os.path.join(self.tempdir, 'rec_stack.hdf'), symmetry_helix_volume,
        trimmed_image_size)

        rec_volume, symmetry_parameters, symmetry_rec_loginfo, Euler_angles_rec = \
        self.compute_and_write_symmetry_related_views(rec_volume, infile, alignment_parameters, each_symmetry_pair,
        self.pixelsize, symmetry_views_count, trimmed_image_size, rec_stack, point_symmetry)
        
        symmetry_parameters = self.log_and_stack_alignment_parameters_into_numpy_array(alignment_parameters,
        symmetry_parameters, symmetry_rec_loginfo)
        
        symmetry_phi_angles = np.array(symmetry_parameters)[:,1]
        diff_angles = np.diff(np.sort(symmetry_phi_angles))
        
        vol = rec_volume.finish(True)
        
        symmetry_helix_volume, variance = \
        self.write_reconstruction_file_and_set_isotropic_pixelsize(each_symmetry_pair, symmetry_helix_volume,
        self.pixelsize, fftvol, point_symmetry)
            
        helical_error, central_prj, central_class_img = \
        self.determine_mean_ccc_deviation_within_symmetry_related_views(rec_stack, Euler_angles_rec, self.helixwidthpix,
        True, True, True)

        os.remove(rec_stack.file_name)
        if not self.keep_intermediate_files:
            os.remove(symmetry_helix_volume)
            symmetry_helix_volume = None
        else:
            self.write_out_side_by_side_display_of_images_and_power_spectra(central_class_img[0], central_prj[0], 
            each_rec_number, montage_reprj, montage_power, each_symmetry_pair)
        
        avg_azimuth_sampling = np.mean(diff_angles)
        dev_azimuth_sampling = np.std(diff_angles)
        
        sym_vol_nt = self.make_symmetry_vol_named_tuple()
        vol_stat = sym_vol_nt(*((symmetry_helix_volume, variance, avg_azimuth_sampling, dev_azimuth_sampling) + \
                                helical_error))
            
        return vol_stat


    def get_symmetry_file_name(self, each_symmetry_pair, vol_name):
        if self.rise_rot_or_pitch_unit_choice == 'pitch/unit_number':
            pitch_unit_pair = self.convert_rise_rotation_pair_to_pitch_unit_pair(each_symmetry_pair)
            
            symmetry_helix_volume = self.generate_symmetry_grid_file_name(pitch_unit_pair, vol_name,
            self.rise_rot_or_pitch_unit_choice)
        else:
            symmetry_helix_volume = self.generate_symmetry_grid_file_name(each_symmetry_pair, vol_name)
            
        return symmetry_helix_volume


    def set_isotropic_pixelsize_in_volume(self, pixelsize, volume):
        volume.set_attr('apix_x', pixelsize)
        volume.set_attr('apix_y', pixelsize)
        volume.set_attr('apix_z', pixelsize)
        
        return volume
    

    def write_reconstruction_file_and_set_isotropic_pixelsize(self, each_symmetry_pair, symmetry_helix_volume,
    pixelsize, rec_vol, point_symmetry):
        stat = Micrograph().get_statistics_from_image(rec_vol)

        rec_vol = self.set_isotropic_pixelsize_in_volume(pixelsize, rec_vol)
        rec_vol = self.set_header_with_helical_parameters(each_symmetry_pair, rec_vol, point_symmetry)
        rec_vol.write_image(symmetry_helix_volume)

        return symmetry_helix_volume, stat.sigma
    

    def generate_isosurface_or_slice_views_from_volume_if_demanded(self, isosurface_stack, slice_stack, each_rec_number,
    each_symmetry_pair, helix_volume, noise_data=False):
        if not noise_data:
            try:
                trimmed_helix_volume = Util.window(helix_volume, int(1.1*self.helixwidthpix),
                int(1.1*self.helixwidthpix), helix_volume.get_zsize(), 0, 0, 0)
            except:
                trimmed_helix_volume = helix_volume
            if self.isosurface_projection_option:
                if sys.argv[0].endswith('mpi'):
                    isosurface_stack = self.tempdir + isosurface_stack
                isosurface_view = self.generate_isosurface_view_from_reconstruction(trimmed_helix_volume,
                each_symmetry_pair, self.pixelsize, each_rec_number)
                
                isosurface_view.write_image(isosurface_stack, each_rec_number)
            if self.slice_views_option:
                if sys.argv[0].endswith('mpi'):
                    slice_stack = self.tempdir + slice_stack
                slice_view = self.generate_slice_view_from_reconstruction(trimmed_helix_volume, each_symmetry_pair,
                self.pixelsize, each_rec_number)
                
                slice_view.write_image(slice_stack, each_rec_number)
        
        return isosurface_stack, slice_stack
                
                
    def prepare_segclassreconstruct(self):
        self.log.fcttolog()
        
        self.infile = self.clear_previous_alignment_parameters_and_copy_class_to_local_directory(self.infile,
        self.classno, self.out_of_plane_tilt_angle)
        
        if self.centeroption:
            self.centered_class_avg = '{0}_centered{1}'.format(os.path.splitext(self.infile)[0],
            os.path.splitext(self.infile)[-1])
            
            self.infile = self.center_class_avg(self.infile, self.centered_class_avg, self.helixwidthpix,
            self.percent_reconstruction_size, self.out_of_plane_tilt_angle)

        return self.infile


    def make_symmetry_vol_named_tuple(self):
        sym_vol_nt = namedtuple('symmetry_vol', 'helix_vol variance avg_azimuth_sampling dev_azimuth_sampling ' + \
        self.get_helical_error_string())
        return sym_vol_nt


    def reconstruct_volumes_for_each_symmetry_pair(self, symmetry_sequence, total_symmetry_pair_id, infile, vol_name,
    montage_repr, montage_power):
        self.log.fcttolog()
        
        segment_size_in_pixel, trimmed_image_size, helixheight_pix = self.determine_trimmed_image_size(self.infile,
        self.percent_reconstruction_size, self.helixwidthpix, self.pixelsize)
        
        if self.local_grid_option:
            if not sys.argv[0].endswith('mpi'):
                symmetry_views_count = self.determine_symmetry_view_count_for_average_helical_rise(symmetry_sequence,
                segment_size_in_pixel, helixheight_pix)
            if sys.argv[0].endswith('mpi'):
                symmetry_views_count = \
                self.determine_symmetry_view_count_for_average_helical_rise(self.total_symmetry_sequence,
                segment_size_in_pixel, helixheight_pix)
        else:
            symmetry_views_count = None
            
        point_symmetry = self.determine_point_group_symmetry_from_input(self.polar_helix,
        self.rotational_symmetry_start)
        
        symmetry_helix_volumes = []
        for each_rec_number, each_symmetry_pair in enumerate(symmetry_sequence):
            
            vol_stat = self.reconstruct_volume_from_class_average(infile, vol_name, segment_size_in_pixel,
            trimmed_image_size, symmetry_views_count, each_rec_number, each_symmetry_pair, point_symmetry, montage_repr,
            montage_power)
            
            self.log.tlog('Reconstruction: {0}, '.format(total_symmetry_pair_id[each_rec_number]) + \
            'symmetry pair: {0} completed: {1}'.format(vol_stat.helix_vol, each_symmetry_pair.__str__()))
            symmetry_helix_volumes.append(vol_stat)
            
        return symmetry_helix_volumes
    
    
    def get_correct_primary_and_secondary_variables_for_database(self, rise_rot_or_pitch_unit_choice,
    ssecondary_variable=''):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> s = SegClassReconstruct()
        >>> hel_rot_n_u_t = 'Helical rotation or number of units per turn'
        >>> s.get_correct_primary_and_secondary_variables_for_database('rise/rotation', hel_rot_n_u_t)
        ('Helical rise in Angstrom', 'Helical rotation in degrees')
        >>> s.get_correct_primary_and_secondary_variables_for_database('pitch/number_of_unit_per_turn')
        ('Helical pitch in Angstrom', 'Number of units per turn')
        >>> s.get_correct_primary_and_secondary_variables_for_database('rise/rotation', None)
        ('Helical rise in Angstrom', '')
        """
        if rise_rot_or_pitch_unit_choice == 'rise/rotation':
            primary_variable = 'Helical rise in Angstrom'
            secondary_variable = 'Helical rotation in degrees'
        else:
            primary_variable = 'Helical pitch in Angstrom'
            secondary_variable = 'Number of units per turn'
        
        if ssecondary_variable is None:
            secondary_variable = ''
            
        return primary_variable, secondary_variable
    

    def get_correct_primary_and_secondary_variables_from_database(self, primary_variable, secondary_variable):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> s = SegClassReconstruct()
        >>> s.get_correct_primary_and_secondary_variables_from_database('Helical rise in Angstrom', 'Helical rotation in degrees')
        ('rise/rotation', 'helical_rise_or_pitch', 'helical_rotation_or_number_of_units_per_turn')
        >>> s.get_correct_primary_and_secondary_variables_from_database('Helical pitch in Angstrom', 'Number of units per turn')
        ('pitch/unit_number', 'helical_rise_or_pitch', 'helical_rotation_or_number_of_units_per_turn')
        """
        if primary_variable == 'Helical rise in Angstrom' and secondary_variable == 'Helical rotation in degrees':
            rise_rot_or_pitch_unit_choice = 'rise/rotation'
        elif primary_variable == 'Helical pitch in Angstrom' and secondary_variable == 'Number of units per turn':
            rise_rot_or_pitch_unit_choice = 'pitch/unit_number'
            
        primary_variable = 'helical_rise_or_pitch'
        secondary_variable = 'helical_rotation_or_number_of_units_per_turn'
        
        return rise_rot_or_pitch_unit_choice, primary_variable, secondary_variable
            
    
    def enter_starting_parameters_of_grid_search(self, primary_variable, secondary_variable, primary_range, primary_inc,
    secondary_range, second_inc):
        primary_min, primary_max = primary_range
        grid_cycle = GridTable()
        grid_cycle.dirname = os.path.abspath(os.curdir)
        grid_cycle.primary_variable = primary_variable
        grid_cycle.primary_min = primary_min
        grid_cycle.primary_max = primary_max
        grid_cycle.primary_inc = primary_inc
        
        second_min, second_max = secondary_range
        grid_cycle.secondary_variable = secondary_variable
        grid_cycle.second_min = second_min
        grid_cycle.second_max = second_max
        grid_cycle.second_inc = second_inc
        
        return grid_cycle
    

    def enter_grid_values_in_database(self, symmetry_sequence, symmetry_helix_volumes, montaged_reprojection_stack,
    montaged_power_stack):
        self.log.fcttolog()
        grid_session = SpringDataBase().setup_sqlite_db(grid_base, 'grid.db')
        
        primary_variable, secondary_variable = \
        self.get_correct_primary_and_secondary_variables_for_database(self.rise_rot_or_pitch_unit_choice)
            
        grid_cycle = self.enter_starting_parameters_of_grid_search(primary_variable, secondary_variable,
        self.helical_rise_or_pitch_range, self.helical_rise_or_pitch_increment, self.helical_rotation_or_unit_range,
        self.helical_rotation_or_unit_increment)
        
        grid_session.add(grid_cycle)
            
        for each_grid_id, (each_rise_or_pitch, each_rotation_or_unitnumber) in enumerate(symmetry_sequence):
            grid_refine = GridRefineTable()
            grid_refine.grid = grid_cycle

            if self.keep_intermediate_files:
                vol_name = os.path.abspath(symmetry_helix_volumes[each_grid_id].helix_vol)
                mont_reproj = (os.path.abspath(montaged_reprojection_stack), each_grid_id)
                mont_power = (os.path.abspath(montaged_power_stack), each_grid_id)
                em_files_3d = [vol_name]
                em_files_2d = [mont_reproj, mont_power]
            else:
                em_files_3d = None
                em_files_2d = None

            grid_refine.em_files_2d = em_files_2d
            grid_refine.em_files_3d = em_files_3d
            grid_refine.primary_value = each_rise_or_pitch
            grid_refine.secondary_value = each_rotation_or_unitnumber

            for each_field in symmetry_helix_volumes[each_grid_id]._fields:
                setattr(grid_refine, each_field, getattr(symmetry_helix_volumes[each_grid_id], each_field))
        
            grid_session.add(grid_refine)
            
        grid_session.commit()
        
        return grid_session
    

    def cleanup_at_end(self):
        os.rmdir(self.tempdir)
        

    def perform_reconstructions_from_class_for_symmetry_combinations(self):
        
        self.symmetry_sequence, entered_symmetry_seq, self.minimum_image_count_3d = \
        self.check_parameter_integritry_and_start_setup()
        
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        self.tempdir = Temporary().mktmpdir(self.temppath)
        
        self.infile = self.prepare_segclassreconstruct()
        self.log.plog(10)
        
        total_symmetry_pair_id = list(range(len(self.symmetry_sequence)))
        self.log.plog(40)
            
        symmetry_helix_volumes = self.reconstruct_volumes_for_each_symmetry_pair(self.symmetry_sequence,
        total_symmetry_pair_id, self.infile, self.volume_name, self.montaged_reprojection_stack,
        self.montaged_power_stack)
        
        self.log.plog(80)

        self.enter_grid_values_in_database(entered_symmetry_seq, symmetry_helix_volumes,
        self.montaged_reprojection_stack, self.montaged_power_stack)

        self.log.plog(90)
            
        self.cleanup_at_end()
        self.log.endlog(self.feature_set)
        
def main():
    # Option handling
    parset = SegClassReconstructPar()
    mergeparset = OptHandler(parset)

    ######## Program
    class_average = SegClassReconstruct(mergeparset)
    class_average.perform_reconstructions_from_class_for_symmetry_combinations()


if __name__ == '__main__':
    main()
