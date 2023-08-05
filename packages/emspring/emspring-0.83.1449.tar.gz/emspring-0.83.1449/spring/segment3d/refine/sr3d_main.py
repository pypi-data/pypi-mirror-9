# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import EMData, EMUtil, Util
from collections import namedtuple
from spring.csinfrastr.csdatabase import SpringDataBase, base, SegmentTable, refine_base, RefinementCycleTable, \
    RefinementCycleSegmentTable, HelixTable, CtfMicrographTable
from spring.csinfrastr.csproductivity import OpenMpi, Temporary, Support, DiagnosticPlot
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segment import Segment
from spring.segment2d.segmentexam import SegmentExam
from spring.segment2d.segmentselect import SegmentSelect
from spring.segment3d.refine.sr3d_diagnostics import SegmentRefine3dSummary
from spring.segment3d.refine.sr3d_parameters import SegmentRefine3dPar
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from sqlalchemy.sql.expression import desc, asc, and_
from tabulate import tabulate
import numpy as np
import os
import shutil


class SegmentRefine3dCheck(SegmentRefine3dSummary):

    def remove_intermediate_files_if_desired(self, *files):
        if not self.keep_intermediate_files:
            for each_file in files:
                os.remove(each_file)


    def get_aim_dict(self):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> SegmentRefine3d().get_aim_dict()
        {'high': 2, 'max': 3, 'medium': 1, 'low': 0}
        """
        return dict(zip(['low', 'medium', 'high', 'max'], list(range(4))))


    def check_whether_search_restraints_are_correctly_set_for_half_set_refinement(self, info_series):
        if self.halfset_refinement:
            aim_ref = self.get_aim_dict()
            half_info_ids = [each_info_id for each_info_id, each_info in enumerate(info_series) \
                          if aim_ref[each_info.resolution_aim] >= aim_ref[self.halfset_start]]
            
            for each_half_id in half_info_ids:
                if info_series[each_half_id].azimuthal_restraint == 180.0:
                    info_series[each_half_id] = info_series[each_half_id]._replace(azimuthal_restraint = 179.9999)
                if info_series[each_half_id].out_of_plane_restraint == 180.0:
                    info_series[each_half_id] = info_series[each_half_id]._replace(out_of_plane_restraint = 179.9999)
        
        return info_series
    

    def check_whether_search_restraints_and_refinement_option_are_correctly_set(self, info_series):
        if info_series[0].azimuthal_restraint < 180.0 and not self.resume_refinement_option or \
        info_series[0].out_of_plane_restraint < 180.0 and not self.resume_refinement_option:
            msg = 'You have specified a refinement strategy with a resolution aim of ' + \
            '\'{0}\' and an azimuthal/out-of-plane search restraint '.format(info_series[0].resolution_aim) + \
            '< 180.0 degrees. These parameters require a starting search angle that can be specified by ' + \
            '\'Continue refinement option\' and the corresponding \'refinement.db file\'. ' + \
            'Re-launch {0} with these options or release the '.format(self.feature_set.progname) + \
            'azimuthal/out-of-plane search restraint to 180 degrees.'

            raise ValueError(msg)


    def check_wether_search_restraints_make_sense_in_multi_model_refinement_and_half_set_refinement(self, info_series):
        aim_ref = self.get_aim_dict()
        if self.halfset_refinement and aim_ref[info_series[0].resolution_aim] >= aim_ref[self.halfset_start] and \
        len(self.helical_symmetries) > 1 and not self.resume_refinement_option:
                msg = 'You have specified \'independent half set refinement\' for your first resolution aim and ' + \
                'requested a multi-model refinement. This combination will only work if you have starting search ' + \
                'parameters, i.e. run the multi-model refinement at low resolution without independent ' + \
                'half set refinement and continue refinement with the independent half set refwinement option.'
                
                raise ValueError(msg)


    def estimate_required_tmp_disk_space(self):

        alignment_size = self.compute_alignment_size_in_pixels(self.alignment_size_in_A, self.ori_pixelsize)
        helixwidthpix = int(round(self.helixwidth / self.ori_pixelsize))
        prj_size = self.compute_prj_size_from_max_out_of_plane_tilt_and_diameter(alignment_size,
        self.out_of_plane_tilt_angle_range, helixwidthpix)
        
        if not self.high_resolution_aim and not self.max_resolution_aim:
            prj_count = self.azimuthal_angle_count * self.out_of_plane_tilt_angle_count
        else:
            prj_count = 25 * self.azimuthal_angle_count * self.out_of_plane_tilt_angle_count
            
        info_series, self.iteration_count = self.define_series_of_search_steps(self.ori_pixelsize, self.refine_strategy,
        (self.low_resolution_aim, self.low_resolution_ang_range, self.low_resolution_trans_range),
        (self.medium_resolution_aim, self.medium_resolution_ang_range, self.medium_resolution_trans_range),
        (self.high_resolution_aim, self.high_resolution_ang_range, self.high_resolution_trans_range),
        (self.max_resolution_aim, self.max_resolution_ang_range, self.max_resolution_trans_range), self.iteration_count)
        
        info_series = self.check_whether_search_restraints_are_correctly_set_for_half_set_refinement(info_series)

        self.check_whether_search_restraints_and_refinement_option_are_correctly_set(info_series)       
        self.check_wether_search_restraints_make_sense_in_multi_model_refinement_and_half_set_refinement(info_series)

        min_binfactor = min([each_info.bin_factor for each_info in info_series])
        
        model_count = len(self.helical_symmetries)

        byte_size = model_count * int(Support().compute_byte_size_of_image_stack(prj_size, prj_size, prj_count) /
        float(min_binfactor))
        
        return byte_size, info_series
    

    def check_helical_rise_and_segmentation_step(self, helical_symmetry):
        helical_rise, helical_rotation = helical_symmetry
        if helical_rise == 0 and helical_rotation == 0:
            sym_view_count = 1
        else:
            sym_view_count = SegClassReconstruct().determine_symmetry_view_count(
                (self.alignment_size_in_A + self.stepsize) / self.ori_pixelsize, self.alignment_size_in_A / self.ori_pixelsize, 
                (helical_rise, helical_rotation), self.ori_pixelsize, 1)
            if helical_rise > 1.4 * self.stepsize:
                msg = 'Helical rise of {0} Angstrom is significantly larger than '.format(helical_rise)
                msg += 'segmentation step size of {0} Angstrom. '.format(self.stepsize)
                msg += 'This will result in multiple inclusion of the same asymmetric unit '
                msg += 'in the 3D final reconstruction. '
                msg += 'Please run \'segment\' again with a step size >= {0} '.format(helical_rise)
                msg += 'Angstrom (preferably using a multiple of the helical rise, e.g. '
                msg += '{0}, {1}, {2}...))'.format(helical_rise, 2 * helical_rise, 3 * helical_rise)
                raise ValueError(msg)
            
        return sym_view_count


    def copy_spring_db_to_tempdir(self):
        temp_db = os.path.join(self.tempdir, 'spring_temp.db')
        shutil.copy('spring.db', temp_db)

        return temp_db


    def get_frame_id_from_mic_stack_file(self, segment_mic):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> from collections import namedtuple
        >>> mic = namedtuple('mic', 'micrograph_name')
        >>> segment_mic = mic('stack_name@2.mrcs')
        >>> s.get_frame_id_from_mic_stack_file(segment_mic)
        2
        """
        return int(segment_mic.micrograph_name.split('@')[-1].strip(os.extsep + 'mrcs'))


    def determine_upper_and_lower_bound_from_central_frame_id(self, frame_avg_window, frame_id, frame_count):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> from collections import namedtuple
        >>> mic = namedtuple('mic', 'micrograph_name')
        >>> segment_mic = mic('stack_name@2.mrcs')
        >>> s.determine_upper_and_lower_bound_from_central_frame_id(3, 4, 7)
        (3, 5)
        >>> s.determine_upper_and_lower_bound_from_central_frame_id(3, 0, 7)
        (0, 2)
        >>> s.determine_upper_and_lower_bound_from_central_frame_id(5, 1, 7)
        (0, 4)
        >>> s.determine_upper_and_lower_bound_from_central_frame_id(5, 6, 7)
        (2, 6)
        """
        lower_frame_id = frame_id - (frame_avg_window - 1) / 2
        upper_frame_id = frame_id + (frame_avg_window - 1) / 2
        
        if lower_frame_id < 0:
            diff = 0 - lower_frame_id 
            lower_frame_id += diff
            upper_frame_id += diff
        elif upper_frame_id >= frame_count:
            diff = frame_count - 1 - upper_frame_id
            lower_frame_id += diff
            upper_frame_id += diff

        return lower_frame_id, upper_frame_id


    def assert_segment_count_on_stack_equals_that_in_database(self):
        segment_count = EMUtil.get_image_count(self.infile)
        shutil.copy(self.spring_path, 'spring.db')
        temp_db = self.copy_spring_db_to_tempdir()
        session = SpringDataBase().setup_sqlite_db(base, temp_db)
        
        database_count = session.query(SegmentTable).count()
        session.close()

        if segment_count != database_count:
            msg = 'The specified spring.db file does not have the same number of segments than the provided segment '
            msg += 'stack. Make sure that the correct input segment stack and the corresponding spring.db generated '
            msg += 'by the same segmentation run are specified.'
            raise ValueError(msg)
        
        self.curvature_range, self.ccc_layer_range = SegmentSelect().convert_curvature_ccc_layer_range('spring.db',
        self.straightness_selection, self.curvature_range_perc, self.ccc_layer_selection, self.ccc_layer_range_perc)
        
        image_list, excluded_non_orientation_counts = \
        SegmentSelect().filter_non_orientation_parameters_based_on_selection_criteria(self, temp_db,
        keep_helices_together=True)
        
        if self.frame_motion_corr and self.frame_avg_window > 2:
            image_frame_list = []
            first_mic = session.query(CtfMicrographTable).first()
            if '@' not in first_mic.micrograph_name:
                err_msg = 'Your spring.db does not the required information about frames. Re-create the appropriate ' + \
                'frame information by running \'segment\' with the \'Frame processing option\'.'
                raise ValueError(err_msg)
            
            frame_counts = []
            for each_image_id in image_list:
                segment = session.query(SegmentTable).filter(SegmentTable.stack_id == each_image_id).first()
                segment_mic = session.query(CtfMicrographTable).filter(CtfMicrographTable.id == segment.mic_id).first()

                frame_prefix = segment_mic.micrograph_name.split('@')[0]
                frame_id = self.get_frame_id_from_mic_stack_file(segment_mic)

                frame_mics = session.query(CtfMicrographTable).\
                filter(CtfMicrographTable.micrograph_name.startswith(frame_prefix)).all()
                
                frame_count = len([each_frame_mic for each_frame_mic in frame_mics])
                frame_counts.append(frame_count)

                lower_frame_id, upper_frame_id = \
                self.determine_upper_and_lower_bound_from_central_frame_id(self.frame_avg_window, frame_id, frame_count)

                frame_mic_ids = [each_frame_mic.id for each_frame_mic in frame_mics \
                if lower_frame_id <= self.get_frame_id_from_mic_stack_file(each_frame_mic) <= upper_frame_id]

                frame_segments = session.query(SegmentTable).\
                filter(SegmentTable.picked_x_coordinate_A == segment.picked_x_coordinate_A).\
                filter(SegmentTable.mic_id.in_(frame_mic_ids)).all()

                frame_segment_ids = [each_image_id] + \
                                    [each_frame_segment.stack_id for each_frame_segment in frame_segments \
                                     if each_frame_segment.stack_id != each_image_id] 

                image_frame_list.append([each_image_id, frame_segment_ids])

            image_list = list(image_frame_list)
            if len(set(frame_counts)) > 0:
                self.frame_count = list(set(frame_counts))[0]
            else:
                err_msg = 'You have provided a spring.db database file that contains different number of frames ' + \
                'for different segments. Please make sure the spring.db was generated with \'segment\' using the ' + \
                '\'frame averaging option\'.'
                raise ValueError(msg)

        os.remove(temp_db)
        
        return segment_count, image_list


    def get_last_cycle_from_refinement_database(self, refine_db):
        ref_session = SpringDataBase().setup_sqlite_db(refine_base, refine_db)
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
        
        return last_cycle, ref_session
    

    def get_original_image_list(self, image_list):
        if self.frame_motion_corr and self.frame_avg_window > 2:
            ori_image_list, b = zip(*image_list)
        else:
            ori_image_list = list(image_list)

        return ori_image_list


    def check_whether_ref_db_has_fewer_segment_entries_than_requested_in_case_of_continued_refinement(self, image_list):
        if self.resume_refinement_option:
            shutil.copy(self.refinementdb_path, 'refinement.db')
            temp_ref_db = self.copy_ref_db_to_tempdir()
            last_cycle, ref_session = self.get_last_cycle_from_refinement_database(temp_ref_db)

            orientation_results = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
            order_by(asc(RefinementCycleSegmentTable.stack_id)).all()

            ref_session.close()
            os.remove(temp_ref_db)
        
            ref_stack_ids = set([each_ref_segment.stack_id for each_ref_segment in orientation_results])
            ori_image_list = self.get_original_image_list(image_list)

            if len(ref_stack_ids.intersection(ori_image_list)) < len(ori_image_list):
                msg = 'This refinement cannot be continued as requested. Your previous refinement was run with ' + \
                'less segments than the currently requested one. This is probably due to a more stringent segment ' + \
                'selection this time. If you want to work with this segment selection re-launch the entire ' + \
                'refinement from the start instead.'  
                raise ValueError(msg)


    def check_entry_count_for_segmultirefine3d(self):
        max_entries = max(len(self.helical_symmetries), len(self.polar_helices), len(self.rotational_symmetry_starts))
        min_entries = min(len(self.helical_symmetries), len(self.polar_helices), len(self.rotational_symmetry_starts))
        
        if max_entries != min_entries:
            msg = 'You have not entered the same number of values for \'Helical symmetries\', \'Polar helices\' and ' + \
            '\'Rotational symmetries\'. Instead {0} received: '.format(self.feature_set.progname) + \
            'Helical symmetries: {0} (counted: {1}). '.format(
            ', '.join([each_sym.__str__() for each_sym in self.helical_symmetries]), len(self.helical_symmetries)) + \
            'Polar helices: {0} (counted: {1}). '.format(', '.join(self.polar_helices), len(self.polar_helices)) + \
            'Rotational symmetries: {0} (counted: {1}).'.format(
            ', '.join([each_rot.__str__() for each_rot in self.rotational_symmetry_starts]), len(self.rotational_symmetry_starts))

            raise ValueError(msg)

        if len(self.references) > 1 and len(self.references) != max_entries and self.reference_option:
            msg = 'You have not entered the same number of references as for other entries that are required ' + \
            'in competitive refinement in {0}. '.format(self.feature_set.progname)
            'Helical symmetries: {0} (counted: {1}). '.format(
            ', '.join([each_sym.__str__() for each_sym in self.helical_symmetries]), len(self.helical_symmetries)) + \
            'References: {0} (counted: {1})'.format(
            ', '.join([os.path.basename(each_ref) for each_ref in self.references]), len(self.references))
            
            raise ValueError(msg)

            
    def assert_at_least_view_count_of_100_for_3dreconstruction(self, sym_view_count, polar_helix,
    rotational_symmetry_start, segment_count):
        sym_transformations = SegClassReconstruct().get_symmetry_transformations_from_helix_input(polar_helix,
        rotational_symmetry_start)
        
        rec_view_count = len(sym_transformations) * sym_view_count * int(segment_count / float(self.cpu_count))
        if rec_view_count < 100 and self.mpi_option:
            msg = '{0} CPUs requested for {1} images in stack. '.format(self.cpu_count, segment_count)
            msg += 'With the given symmetry-related input this will result in {0} images '.format(rec_view_count)
            msg += '(less than 100) per parallel reconstruction. '
            msg += 'Please lower number of requested CPUs, e.g. Number of CPUs {0} '.format(int(
                    self.cpu_count * rec_view_count / 100.0))
            msg += '= (if number of images for reconstruction is 100).'
            raise ValueError(msg)
        

    def check_sanity_of_input_parameters(self):
        segment_count, image_list = self.assert_segment_count_on_stack_equals_that_in_database() 

        self.check_whether_ref_db_has_fewer_segment_entries_than_requested_in_case_of_continued_refinement(image_list)
            
        self.check_entry_count_for_segmultirefine3d()

        for each_helical_sym, each_point_sym, each_rot_start in zip(self.helical_symmetries, self.polar_helices,
        self.rotational_symmetry_starts):
            sym_view_count = self.check_helical_rise_and_segmentation_step(each_helical_sym)

            self.assert_at_least_view_count_of_100_for_3dreconstruction(sym_view_count, each_point_sym, each_rot_start,
            segment_count)
        
        return image_list
        
            
    def copy_ref_db_to_tempdir(self, cycle_id=None):
        if cycle_id is None:
            temp_ref_db = os.path.join(self.tempdir, 'ref_temp.db')
            shutil.copy('refinement.db', temp_ref_db)
        else:
            temp_ref_db = os.path.join(self.tempdir, 'ref_temp_{0:03}.db'.format(cycle_id))
            shutil.copy('refinement{0:03}.db'.format(cycle_id), temp_ref_db)

        return temp_ref_db


    def merge_model_ids_into_presplit_state(self, ref_session, last_cycle, reference_files):

        ref_segments = ref_session.query(RefinementCycleSegmentTable).all()
        model_ids = set([each_ref_segment.model_id for each_ref_segment in ref_segments])
        if len(model_ids) != len(reference_files) * 2:
            msg = 'You have specified to continue a refinement with a refinement.db that has been used for ' + \
            'independent half-set refinement. The number of models you specified to refine does not match the ' + \
            'number from the half-set refinement. Please adapt your input or activate half-set refinement.'
            raise ValueError(msg)
        
        for each_reference in reference_files: 
            ref_segments = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
            filter(and_(RefinementCycleSegmentTable.model_id >= 2 * each_reference.model_id, 
                        RefinementCycleSegmentTable.model_id <= 2 * each_reference.model_id + 1)).all()
            
            for each_ref_segment in ref_segments:
                each_ref_segment.model_id = each_reference.model_id
                ref_session.merge(each_ref_segment)

        last_cycle.fsc_split = False
        ref_session.merge(last_cycle)
        ref_session.commit()

        return ref_session
    

    def get_last_cycle_id_from_refinement_database(self, refinementdb_path, reference_files):
        shutil.copy(self.refinementdb_path, 'refinement.db')
        temp_ref_db = self.copy_ref_db_to_tempdir()
        last_cycle, ref_session = self.get_last_cycle_from_refinement_database(temp_ref_db)

        if last_cycle is None:
            ref_cycle_id = 0
            ref_session.close()
            os.remove(temp_ref_db)
        else:
            ref_cycle_id = last_cycle.id
            if last_cycle.fsc_split and not self.halfset_refinement:
                ref_session = self.merge_model_ids_into_presplit_state(ref_session, last_cycle, reference_files)
                ref_session.close()
            shutil.move(temp_ref_db, 'refinement{0:03}.db'.format(ref_cycle_id))
            os.remove('refinement.db')
            
        return ref_cycle_id
    

    def update_image_list_after_file_transfer(self, ori_image_list, image_list):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.frame_motion_corr = False
        >>> s.frame_avg_window = 5
        >>> ori_image_list = list(range(0, 10, 2))
        >>> s.update_image_list_after_file_transfer(ori_image_list, ori_image_list)
        [0, 1, 2, 3, 4]
        >>> s.frame_motion_corr = True
        >>> frame_list = [[0, 2, 4], [0, 2, 4], [2, 4, 6], [4, 6, 8], [4, 6, 8]]
        >>> image_list = zip(ori_image_list, frame_list)
        >>> s.update_image_list_after_file_transfer(ori_image_list, image_list)
        [(0, [0, 1, 2]), (1, [0, 1, 2]), (2, [1, 2, 3]), (3, [2, 3, 4]), (4, [2, 3, 4])]
        """
        if self.frame_motion_corr and self.frame_avg_window > 2:
            img_ids, frame_img_ids = zip(*image_list)
            updated_frame_img_ids = []
            for each_local_id, each_image_number in enumerate(ori_image_list):
                updated_frame_ids = [each_local_id_id for each_local_id_id, each_image_id in enumerate(ori_image_list) \
                                         if each_image_id in frame_img_ids[each_local_id]]

                updated_frame_img_ids.append(updated_frame_ids)
            
            image_list = zip(list(range(len(ori_image_list))), updated_frame_img_ids)
        else:
            image_list = list(range(len(ori_image_list)))

        return image_list


    def pre_cycle_setup(self, info_series):
        image_list = self.check_sanity_of_input_parameters()
        reference_files = self.prepare_reference_volumes()
        
        masked_segment_stack = '{inp}_masked{ext}'.format(inp=os.path.splitext(os.path.basename(self.infile))[0],
        ext=os.path.splitext(self.infile)[-1])
        
        large_segment_stack = os.path.splitext(os.path.basename(self.infile))[0] + '_temp' + \
        os.path.splitext(os.path.basename(self.infile))[-1]
        
        ori_image_list = self.get_original_image_list(image_list)
        segment = EMData()
        for each_local_id, each_image_number in enumerate(ori_image_list):
            segment.read_image(self.infile, each_image_number)
            segment.write_image(large_segment_stack, each_local_id)
            
        image_list = self.update_image_list_after_file_transfer(ori_image_list, image_list)

        self.tempfiles = []
        self.tempfiles.append(large_segment_stack)
            
        if self.resume_refinement_option:
            ref_cycle_id = self.get_last_cycle_id_from_refinement_database(self.refinementdb_path, reference_files)
        else:
            ref_cycle_id = 0

        lambda_sirt = 1.0e-5
        
        return large_segment_stack, masked_segment_stack, image_list, reference_files, lambda_sirt, ref_cycle_id
    

    def define_original_input_values_before_binning(self, large_segment_stack, reference_files):
        ori_large_segment_stack = large_segment_stack
        ori_reference_files = reference_files
        alignment_size = self.compute_alignment_size_in_pixels(self.alignment_size_in_A, self.ori_pixelsize)
        ori_alignment_size = alignment_size
        ori_pixelsize = self.ori_pixelsize
        ori_helixwidthpix = int(round(self.helixwidth / self.ori_pixelsize))
        
        return ori_large_segment_stack, ori_reference_files, ori_alignment_size, ori_helixwidthpix, ori_pixelsize
    
    
    def volume_decimate(self, vol, decimation=2, fit_to_fft = True, frequency_low=0, frequency_high=0):
        """
            Window 3D volume to FFT-friendly size, apply Butterworth low pass filter,
            and decimate image by integer factor
            cs: adapted from image_decimate (fundamentals)
        """
        from filter       import filt_btwl
        from fundamentals import smallprime
        
        if decimation == 1.0:     
            return  vol.copy()
        if frequency_low <= 0  :    
            frequency_low = 0.5/decimation-0.02
            frequency_high = min(0.5/decimation + 0.02, 0.499)
        if fit_to_fft:
            nx = vol.get_xsize()
            ny = vol.get_ysize()
            nz = vol.get_ysize()
            nx_fft_m = smallprime(nx)
            ny_fft_m = smallprime(ny)
            nz_fft_m = smallprime(nz)
            e = Util.window(vol, nx_fft_m, ny_fft_m, nz_fft_m, 0,0,0)
            e = filt_btwl(e, frequency_low, frequency_high)
        else:
            e = filt_btwl(vol, frequency_low, frequency_high)
        
        return Util.decimate(e, int(decimation), int(decimation), int(decimation))


    def give_name_and_write_out_reference(self, reference_vol, each_reference, ref_cycle_id, updated_references):
        ref_prefix = '{0}_rescale_mod{1:03}_{2:03}{3}'.format(os.path.splitext(self.outfile_prefix)[0],
        each_reference.model_id, ref_cycle_id, os.path.splitext(self.outfile_prefix)[-1])

        new_reference = self.generate_reconstruction_name_with_Angstrom_per_pixel_and_set_header(0, reference_vol, 
        ref_prefix, self.ori_pixelsize, each_reference.helical_symmetry, each_reference.point_symmetry)

        reference_vol.write_image(new_reference)
        each_reference = each_reference._replace(ref_file=new_reference)
        updated_references.append(each_reference)
        
        return updated_references


    def make_pixel_info_named_tuple(self):
        return namedtuple('pixel_info', 'pixelsize alignment_size reconstruction_size helixwidthpix ' + \
        'helix_inner_widthpix helix_heightpix')


    def update_reference_info(self, reference_files):
        upd_reference_files = []
        for each_model_id, each_reference in enumerate(reference_files):
            even_model_id = each_model_id * 2
            each_first_reference = each_reference._replace(model_id=even_model_id)
            each_second_reference = each_reference._replace(model_id=even_model_id + 1)
            upd_reference_files.append(each_first_reference)
            upd_reference_files.append(each_second_reference)
        
        return upd_reference_files


    def distribute_segment_ids_into_two_halves_based_on_helices(self, stack_ids, helix_ids, length_sorted_helices):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.distribute_segment_ids_into_two_halves_based_on_helices(range(5), [0] * 2 + [1] * 3, [0, 1])
        (array([0, 1]), array([2, 3, 4]))
        >>> s.distribute_segment_ids_into_two_halves_based_on_helices(range(5), [0] * 5, [0])
        (array([0, 1]), array([2, 3, 4]))
        """
        even_helices = [each_helix_id for each_helix, each_helix_id in enumerate(length_sorted_helices) \
                        if (each_helix) % 2 == 0]

        even_stack_ids = np.array([each_stack_id for (each_stack_id, each_helix_id) in zip(stack_ids, helix_ids) \
                                   if each_helix_id in even_helices])

        odd_stack_ids = np.array([each_stack_id for (each_stack_id, each_helix_id) in zip(stack_ids, helix_ids) \
                                  if each_helix_id not in even_helices])
        
        if len(even_stack_ids) == 0 or len(odd_stack_ids) == 0:
            even_stack_ids = np.array(stack_ids[:len(stack_ids) / 2])
            odd_stack_ids = np.array(stack_ids[len(stack_ids) / 2:])

        return even_stack_ids, odd_stack_ids


    def split_ref_ids_according_to_even_and_odd_helices(self, reference_files, session, ref_session, last_cycle):
        model_ref_segments = []
        for each_reference in reference_files:
            model_segments = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
            filter(RefinementCycleSegmentTable.model_id == each_reference.model_id).\
            order_by(asc(RefinementCycleSegmentTable.stack_id)).all()

            ref_segment_ids = np.array([each_ref_segment.id for each_ref_segment in model_segments])
            stack_ids = [each_ref_segment.stack_id for each_ref_segment in model_segments]
            helix_ids = []
            for each_stack_id in stack_ids:
                segment = session.query(SegmentTable).get(each_stack_id + 1)
                helix_ids.append(segment.helix_id)
            
            helices = session.query(HelixTable).order_by(desc(HelixTable.length)).all()
            length_sorted_helices = [each_helix.id for each_helix in helices]

            even_stack_ids, odd_stack_ids = self.distribute_segment_ids_into_two_halves_based_on_helices(stack_ids,
            helix_ids, length_sorted_helices)

            model_ref_segments.append(ref_segment_ids[np.in1d(stack_ids, odd_stack_ids)])
            model_ref_segments.append(ref_segment_ids[np.in1d(stack_ids, even_stack_ids)])
        
        return model_ref_segments


    def prepare_reference_files_for_halfset_refinement(self, reference_files, cycle_id):
        
        self.fsc_split = True
        temp_db = self.copy_spring_db_to_tempdir()
        session = SpringDataBase().setup_sqlite_db(base, temp_db)
        
        temp_ref_db = self.copy_ref_db_to_tempdir(cycle_id)
        ref_session = SpringDataBase().setup_sqlite_db(refine_base, temp_ref_db)

        upd_reference_files = self.update_reference_info(reference_files)

        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()

        if not last_cycle.fsc_split:
            model_ref_segments = self.split_ref_ids_according_to_even_and_odd_helices(reference_files, session, ref_session,
            last_cycle)
            
            for each_model_id, each_model_ref_segments in enumerate(model_ref_segments):
                for each_model_id_segment in each_model_ref_segments:
                    ref_segment = ref_session.query(RefinementCycleSegmentTable).get(int(each_model_id_segment))
                    ref_segment.model_id = each_model_id
                    ref_session.merge(ref_segment)
    
            ref_session.commit()
            ref_session.close()
        
        os.remove(temp_db)
        shutil.copy(temp_ref_db, 'refinement{0:03}.db'.format(cycle_id))
        os.remove(temp_ref_db)

        return upd_reference_files


    def update_pixelinfo_based_on_different_helical_symmetries(self, segment_size_pix, helixwidthpix, pixelsize):
        alignment_sizes = []
        reconstruction_sizes = []
        helix_heights = []
        for each_helical_symmetry in self.helical_symmetries:
            helical_rise, helical_rotation = each_helical_symmetry

            alignment_size, reconstruction_size = \
            self.compute_alignment_and_reconstruction_size_in_pixels(self.alignment_size_in_A, helical_rise,
            self.helixwidth, pixelsize)

            helix_heights.append(min(alignment_size, int(self.alignment_size_in_A / pixelsize)))
            if helical_rise == 0 and helical_rotation == 0:
                reconstruction_size = alignment_size
            else:
                reconstruction_size = self.compute_rec_size_for_helix(self.helixwidth, helical_rise, pixelsize)

            reconstruction_sizes.append(min(reconstruction_size, segment_size_pix))
            alignment_sizes.append(min(alignment_size, segment_size_pix))
        
        pixelinfo_nt = self.make_pixel_info_named_tuple()

        helix_inner_widthpix = int(round(self.helix_inner_width / (pixelsize)))

        pixelinfo = pixelinfo_nt(pixelsize, max(alignment_sizes), max(reconstruction_sizes), helixwidthpix,
        helix_inner_widthpix, max(helix_heights))

        return pixelinfo, reconstruction_sizes


    def precycle_setup_before_binning(self, info_series, large_segment_stack, reference_files, ori_reference_files,
    ori_pixelsize, each_binindex, ref_cycle_id, segment_size_pix, helixwidthpix):
        reference_vol = EMData()
        current_binfactor = info_series[each_binindex].bin_factor
        current_res_aim = info_series[each_binindex].resolution_aim
        updated_references = []
        if current_res_aim == info_series[0].resolution_aim:
            aim_ref = self.get_aim_dict()
            if self.halfset_refinement and aim_ref[info_series[0].resolution_aim] >= aim_ref[self.halfset_start] and\
            self.reference_option:
                ori_reference_files = self.prepare_reference_files_for_halfset_refinement(ori_reference_files,
                ref_cycle_id)

            for each_ref_id, each_ori_ref in enumerate(ori_reference_files):
                reference_vol.read_image(each_ori_ref.ref_file)
                reference_vol = self.volume_decimate(reference_vol, current_binfactor, fit_to_fft=False)
                ref_size = reference_vol.get_xsize()
                reference_vol = Util.window(reference_vol, ref_size, ref_size, ref_size, 0, 0, 0)

                updated_references = self.give_name_and_write_out_reference(reference_vol, each_ori_ref, ref_cycle_id,
                updated_references)
                if self.halfset_refinement and aim_ref[info_series[0].resolution_aim] >= aim_ref[self.halfset_start]:
                    if each_ref_id % 2 == 1:
                        os.remove(each_ori_ref.ref_file)
                else:
                    os.remove(each_ori_ref.ref_file)
        else:
            if self.halfset_refinement and current_res_aim == self.halfset_start:
                reference_files = self.prepare_reference_files_for_halfset_refinement(reference_files,
                ref_cycle_id)

            for each_reference in reference_files:
                reference_vol.read_image(each_reference.ref_file)
                scaling_factor = info_series[each_binindex - 1].bin_factor / float(current_binfactor)
                ref_size = Segment().determine_boxsize_closest_to_fast_values(reference_vol.get_xsize() * scaling_factor)
                reference_vol = Util.pad(reference_vol, ref_size, ref_size, ref_size, 0, 0, 0, 'avg')
                reference_vol.scale(scaling_factor)
                
                updated_references = self.give_name_and_write_out_reference(reference_vol, each_reference, ref_cycle_id,
                updated_references)
       
        pixelsize = ori_pixelsize * current_binfactor

        pixelinfo, reconstruction_sizes = \
        self.update_pixelinfo_based_on_different_helical_symmetries(segment_size_pix, helixwidthpix,
        pixelsize)

        if self.ctf_correction:
            ctf3d_avg_squared = self.prepare_3dctf_avg_squared(max(reconstruction_sizes), pixelsize)
        else:
            ctf3d_avg_squared = None
        
        return updated_references, ctf3d_avg_squared, pixelinfo
    

    def generate_reconstruction_name_with_Angstrom_per_pixel_and_set_header(self, each_iteration_number, reconstruction,
    outfile_prefix, pixelsize, helical_symmetry, point_symmetry):
    
        latest_reconstruction = self.generate_file_name_with_apix(each_iteration_number, outfile_prefix, pixelsize)
        
        reconstruction = SegClassReconstruct().set_isotropic_pixelsize_in_volume(pixelsize, reconstruction)
        reconstruction = SegClassReconstruct().set_header_with_helical_parameters(helical_symmetry, reconstruction,
        point_symmetry)
        
        return latest_reconstruction
    
    
    def clean_up_temporary_large_stack(self, large_segment_stack, masked_segment_stack):
        temp_large_segment_stack = os.path.join(self.tempdir, os.path.basename(large_segment_stack))
        if os.path.exists(temp_large_segment_stack):
            os.remove(temp_large_segment_stack)
        os.remove(masked_segment_stack)


class SegmentRefine3d(SegmentRefine3dCheck):
    def setup_dummies_for_iteration(self, start_ref_cycle_id):
        unbending_info = None
        large_straightened_stack = None
        ref_cycle_id = start_ref_cycle_id
        
        return ref_cycle_id, unbending_info, large_straightened_stack
    

    def get_prj_named_tuple(self):
        prj_nt = namedtuple('prj_info', 'projection_stack fine_projection_stack projection_parameters ' + \
        'fine_projection_parameters')

        return prj_nt


    def package_parameters_and_stack_name_into_prj_info(self, merged_prj_params, merged_fine_prj_params,
    merged_prj_stack, merged_prj_fine_stack):
        prj_nt = self.get_prj_named_tuple()
        prj_info = prj_nt(merged_prj_stack, merged_prj_fine_stack, merged_prj_params, merged_fine_prj_params)

        return prj_info


    def project_including_masking_and_filtering(self, required_byte, info_series, reference_files, start_ref_cycle_id,
    ref_cycle_id, each_info, each_iteration_number, pixelinfo):
        
        Temporary().check_available_space_in_temppath_and_raise_error_if_not_enough_space_available(self.temppath,
        required_byte)
        
        updated_ref_files = []
        merged_prj_params = []
        merged_fine_prj_params = []
        if self.resume_refinement_option and not self.reference_option and each_iteration_number == 1:
            merged_prj_stack = None
            merged_prj_fine_stack = None
            updated_ref_files = reference_files
        else:
            for each_reference in reference_files:
                reference_volume = self.filter_and_mask_reference_volume(each_info.resolution_aim, each_reference,
                pixelinfo, each_reference.fsc)
            
                each_reference, prj_prefix = \
                self.write_out_reference_and_get_prj_prefix_depending_on_number_of_models(reference_files, ref_cycle_id,
                each_iteration_number, each_reference, reference_volume)
    
                projection_stack, projection_parameters, fine_projection_stack, fine_projection_parameters = \
                self.project_through_reference_volume_in_helical_perspectives(each_info.resolution_aim, ref_cycle_id,
                each_reference.ref_file, pixelinfo, each_reference.helical_symmetry, each_reference.rotational_symmetry,
                prj_prefix)
                
                updated_ref_files, merged_prj_params, merged_fine_prj_params = \
                self.collect_prj_params_and_update_reference_info(updated_ref_files, each_reference, projection_stack,
                projection_parameters, fine_projection_stack, fine_projection_parameters, merged_prj_params,
                merged_fine_prj_params)
        
            merged_prj_stack = self.merge_prj_ref_stacks_into_single_prj_stack(updated_ref_files, 'prj_stack')
            merged_prj_fine_stack = self.merge_prj_ref_stacks_into_single_prj_stack(updated_ref_files, 'fine_prj_stack')
        
        self.log.plog(90 * (ref_cycle_id - start_ref_cycle_id + 0.2 - 1) / float(self.iteration_count) + 5)

        previous_params, mask_params =\
        self.prepare_previous_parameters_either_from_inplane_angle_or_from_previous_cycle(each_info, info_series,
        ref_cycle_id, each_iteration_number, reference_files)
        
        prj_info = self.package_parameters_and_stack_name_into_prj_info(merged_prj_params, merged_fine_prj_params,
        merged_prj_stack, merged_prj_fine_stack)

        return mask_params, previous_params, prj_info, updated_ref_files
        

    def mask_and_window_and_unbend_if_required(self, info_series, masked_segment_stack, start_ref_cycle_id,
    ref_cycle_id, each_info, large_segment_stack, each_iteration_number, mask_params, previous_params, unbending_info,
    large_straightened_stack, pixelinfo):
        
        if not self.unbending and each_iteration_number == 1 or \
        not self.unbending and self.layer_line_filter:
            masked_segment_stack, large_segment_stack, large_straightened_stack = \
            self.window_and_mask_input_stack(large_segment_stack, pixelinfo, mask_params, masked_segment_stack,
            each_info, ref_cycle_id)
            
        elif self.unbending and each_iteration_number == 1:
            helices_coordinates, cut_coordinates = \
            self.get_helices_coordinates_required_for_unbending_from_database(ref_cycle_id - 1, each_info.bin_factor,
            info_series, large_segment_stack, pixelinfo.pixelsize)
            
            previous_params, unbending_info, masked_segment_stack, large_segment_stack, large_straightened_stack = \
            self.unbend_window_and_mask_input_stack(large_segment_stack, ref_cycle_id, pixelinfo,
            previous_params, mask_params, helices_coordinates, cut_coordinates, masked_segment_stack,
            each_info.resolution_aim)
            
        self.log.plog(90 * (ref_cycle_id - start_ref_cycle_id + 0.3 - 1) / float(self.iteration_count) + 5)

        return masked_segment_stack, previous_params, unbending_info, large_straightened_stack, large_segment_stack


    def add_model_id_to_prefix(self, prefix, model_id):
        outfile_prefix = os.path.splitext(prefix)[0] + '_mod{0:03}'.format(model_id) + os.path.splitext(prefix)[-1]

        return outfile_prefix


    def write_out_reconstruction_and_remove_reference(self, reference_files, ref_cycle_id, pixelinfo, each_reference,
    reconstructed_volume):
        if len(reference_files) > 1:
            outfile_prefix = self.add_model_id_to_prefix(self.outfile_prefix, each_reference.model_id)
            diagnostic_prefix = self.add_model_id_to_prefix(self.diagnostic_plot_prefix, each_reference.model_id)
            fsc_prefix = self.add_model_id_to_prefix('fsc.dat', each_reference.model_id)
        else:
            outfile_prefix = self.outfile_prefix
            diagnostic_prefix = self.diagnostic_plot_prefix
            fsc_prefix = 'fsc.dat'

        latest_reconstruction = self.generate_reconstruction_name_with_Angstrom_per_pixel_and_set_header(ref_cycle_id, 
        reconstructed_volume, outfile_prefix, pixelinfo.pixelsize, each_reference.helical_symmetry, 
        each_reference.point_symmetry)

        reconstructed_volume.write_image(latest_reconstruction)
        self.remove_intermediate_files_if_desired(each_reference.ref_file)
        reference_files[each_reference.model_id] = each_reference._replace(ref_file=latest_reconstruction)

        return latest_reconstruction, diagnostic_prefix, fsc_prefix, reference_files


    def determine_whether_is_last_cycle(self, start_ref_cycle_id, ref_cycle_id):
        current_cycle = ref_cycle_id - start_ref_cycle_id
        if current_cycle == self.iteration_count:
            is_last_cycle = True
        else:
            is_last_cycle = False

        return is_last_cycle


    def choose_reconstruction_stack_based_on_unbending(self, large_straightened_stack, large_reconstruction_stack):
        if large_straightened_stack is not None:
            reconstruction_stack = large_straightened_stack
        else:
            reconstruction_stack = large_reconstruction_stack
            
        return reconstruction_stack
    

    def cleanup_of_prj_stacks(self, prj_info):
        if prj_info.projection_stack is not None:
            if prj_info.projection_stack.startswith(self.tempdir):
                azimuthal_prj_stack = self.get_prj_stack_name_with_ending(prj_info.projection_stack, 'az')
                tilt_prj_stack = self.get_prj_stack_name_with_ending(prj_info.projection_stack, 'out')
    
                os.remove(azimuthal_prj_stack)
                os.remove(tilt_prj_stack)


    def reconstruct_volume(self, reference_files, lambda_sirt, start_ref_cycle_id, ref_cycle_id, each_info, pixelinfo,
    ctf3d_avg_squared, large_reconstruction_stack, selected_parameters, prj_info):
    
        if max([len(each_model) for each_model in selected_parameters]) == 0:
            self.if_no_selected_images_left_abort_refinement()

        rec_stack_info = SegClassReconstruct().make_rec_stack_info()
        for each_reference in reference_files:
            rec_stack = rec_stack_info(os.path.join(self.tempdir, 'rec_stack.hdf'), each_reference.ref_file,
            pixelinfo.alignment_size)
            
            if len(selected_parameters[each_reference.model_id]) > 1:
                uncorrected_reconstruction, alignment_parameters, symmetry_alignment_parameters, fsc_lines, lambda_sirt, Euler_angles_rec = \
                self.apply_orientation_parameters_and_reconstruct_imposing_helical_symmetry(selected_parameters[each_reference.model_id],
                ref_cycle_id, each_info.resolution_aim, large_reconstruction_stack, ctf3d_avg_squared, pixelinfo,
                each_reference, self.stepsize, rec_stack, lambda_sirt, self.unbending)
                
                helical_error = self.perform_mean_ccc_evaluation_of_images_with_symmetry_related_projections(rec_stack,
                alignment_parameters, Euler_angles_rec, pixelinfo.helixwidthpix)
                
                reconstructed_volume = self.perform_volume_operations_ctf_and_symmetrization(each_info.resolution_aim,
                uncorrected_reconstruction, ctf3d_avg_squared, pixelinfo.pixelsize, each_reference)
                
                self.log_helical_error(helical_error)
        
                latest_reconstruction, diagnostic_prefix, fsc_prefix, reference_files = \
                self.write_out_reconstruction_and_remove_reference(reference_files, ref_cycle_id, pixelinfo,
                each_reference, reconstructed_volume)
    
                self.log.plog(90 * (ref_cycle_id - start_ref_cycle_id + 0.9 - 1) / float(self.iteration_count) + 5)
                
                amp_cc, variance = self.summarize_each_bin_round_with_simulated_vs_experimental_images_and_powerspectra(
                each_info.resolution_aim, large_reconstruction_stack, latest_reconstruction, ref_cycle_id,
                each_reference, pixelinfo, diagnostic_prefix, prj_info)
                
                is_last_cycle = self.determine_whether_is_last_cycle(start_ref_cycle_id, ref_cycle_id)

                self.enter_additional_ref_parameters_in_database(ref_cycle_id, symmetry_alignment_parameters,
                fsc_lines.cylinder_masked, amp_cc, variance, helical_error, pixelinfo.pixelsize,
                each_reference, is_last_cycle)
                
                self.write_out_fsc_line(fsc_lines, pixelinfo.pixelsize, fsc_prefix, ref_cycle_id)
                reference_files[each_reference.model_id] = reference_files[each_reference.model_id]._replace(fsc=fsc_lines)
            
                self.evaluate_alignment_parameters_and_summarize_in_plot(alignment_parameters,
                symmetry_alignment_parameters, fsc_lines, ref_cycle_id, each_reference, pixelinfo, diagnostic_prefix,
                each_info.resolution_aim)
            else:
                reference_vol = EMData()
                reference_vol.read_image(each_reference.ref_file)
                latest_reconstruction, diagnostic_prefix, fsc_prefix, reference_files = \
                self.write_out_reconstruction_and_remove_reference(reference_files, ref_cycle_id, pixelinfo,
                each_reference, reference_vol)
            
        self.cleanup_of_prj_stacks(prj_info)

        return reference_files, lambda_sirt
    

    def print_fsc_to_diagnostic_plot(self, reference_files, pixelinfo, ref_cycle_id, each_ref_id, each_reference,
    fsc_lines, fsc_prefix):
        fsc_plot = DiagnosticPlot()
        column_count = 1
        row_count = 2
        ax1 = fsc_plot.plt.subplot2grid((row_count, column_count), (0, 0), rowspan=1, colspan=1)
        ax2 = fsc_plot.plt.subplot2grid((row_count, column_count), (1, 0), rowspan=1, colspan=1)

        ax1.set_title('FSC from independent half-set halves (top) and independent cross-FSC (bottom)', fontsize=10)
        fsc_plot.set_fontsize_to_all_ticklabels_of_subplots([ax1, ax2], font_size=6)
        ax1, res_cutoff = self.plot_fsc_lines(ax1, reference_files[2 * each_ref_id].fsc, pixelinfo.pixelsize)
        ax1, res_cutoff = self.plot_fsc_lines(ax1, reference_files[2 * each_ref_id + 1].fsc, pixelinfo.pixelsize)

        ax2, (res_0143, res_05) = self.plot_fsc_lines(ax2, fsc_lines, pixelinfo.pixelsize)
        fsc_name = self.write_out_fsc_line(fsc_lines, pixelinfo.pixelsize, fsc_prefix, ref_cycle_id)
        plotname = os.path.splitext(fsc_name)[0] + os.path.splitext(self.diagnostic_plot_prefix)[-1]
        fsc_plot.fig.savefig(plotname, dpi=600)

        table_data = [['Resolution at FSC (0.5/0.143) (Angstrom)', res_05, res_0143]]
        self.log.ilog('The cross FSC from independent half-set refinements was determined:\n{0}'.format(tabulate(table_data)))

        resolution = SegmentExam().make_oneoverres(fsc_lines[0], pixelinfo.pixelsize)
        msg = tabulate(zip(resolution.tolist(), fsc_lines.unmasked, fsc_lines.cylinder_masked), 
            ['resolution (1/Angstrom)', 'FSC (unmasked)', 'FSC (cylinder-masked)'])
        self.log.ilog('\n{0}'.format(msg))
            
        return res_0143, res_05


    def update_highest_fsc_database(self, ref_cycle_id, model_fscs, model_resolution):
        if model_resolution != []:
            temp_ref_db = self.copy_ref_db_to_tempdir(ref_cycle_id)
            ref_session = SpringDataBase().setup_sqlite_db(refine_base, temp_ref_db)
    
            model_0143, model_05 = zip(*model_resolution)
            fsc_to_be_entered = model_fscs[np.argmax(model_0143)]
    
            last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
            last_cycle.fsc_0143 = model_0143[np.argmax(model_0143)]
            last_cycle.fsc_05 = model_05[np.argmax(model_0143)]
            last_cycle.fsc = fsc_to_be_entered
            last_cycle.fsc_split = True
    
            ref_session.merge(last_cycle)
            ref_session.commit()
    
            shutil.copy(temp_ref_db, 'refinement{0:03}.db'.format(ref_cycle_id))
            os.remove(temp_ref_db)


    def compute_cross_fsc_and_write_out_merged_volume(self, reference_files, resolution_aim, pixelinfo, ref_cycle_id):
        model_fscs = []
        model_resolution = []
        for each_ref_id in list(range(len(reference_files) / 2)):
            each_reference = reference_files[2 * each_ref_id]
            rec_odd = reference_files[2 * each_ref_id].ref_file
            rec_even = reference_files[2 * each_ref_id + 1].ref_file
            
            first_rec = EMData()
            second_rec = EMData()
            first_rec.read_image(rec_odd)
            second_rec.read_image(rec_even)
            
            helical_symmetry = each_reference.helical_symmetry
            rotational_sym = each_reference.rotational_symmetry
            point_symmetry = each_reference.point_symmetry

            reconstructed_volume, fsc_lines = self.compute_fsc_on_volumes_from_half_the_dataset(resolution_aim, first_rec,
            second_rec, pixelinfo, helical_symmetry, rotational_sym)
            
            if len(reference_files) > 2:
                outfile_prefix = self.add_model_id_to_prefix(self.outfile_prefix, each_reference.model_id)
                fsc_prefix = self.add_model_id_to_prefix('fsc_indpndnt.dat', each_reference.model_id)
            else:
                outfile_prefix = self.outfile_prefix
                fsc_prefix = 'fsc_indpndnt.dat'

            latest_reconstruction = \
            self.generate_reconstruction_name_with_Angstrom_per_pixel_and_set_header(ref_cycle_id, reconstructed_volume,
            outfile_prefix, pixelinfo.pixelsize, helical_symmetry, point_symmetry)
            reconstructed_volume.write_image(latest_reconstruction)

            res_cutoffs = self.print_fsc_to_diagnostic_plot(reference_files, pixelinfo, ref_cycle_id, each_ref_id, each_reference,
            fsc_lines, fsc_prefix)
            
            model_fscs.append(fsc_lines.cylinder_masked)
            model_resolution.append(res_cutoffs)

            reference_files[2 * each_ref_id] = each_reference._replace(fsc=fsc_lines)
            reference_files[2 * each_ref_id + 1] = reference_files[2 * each_ref_id + 1]._replace(fsc=fsc_lines)

        self.update_highest_fsc_database(ref_cycle_id, model_fscs, model_resolution)

        return reference_files


    def bin_including_copies_of_frames_if_requested(self, image_list, ori_large_segment_stack, ori_alignment_size,
    ori_helixwidthpix, ori_pixelsize, each_info):
        if self.frame_motion_corr and self.frame_avg_window > 2:
            frames_list = zip(*zip(*image_list)[1])
            large_binned_segment_stack = os.path.join(self.tempdir, ori_large_segment_stack)
            for each_frame_id, each_frame_image_ids in enumerate(frames_list):
                frame_stack_path = self.get_frame_stack_path(ori_large_segment_stack, each_frame_id)

                large_binned_frame_stack, segment_size_pix, helixwidthpix, pixelsize = \
                SegmentExam().apply_binfactor(each_info.bin_factor, ori_large_segment_stack, ori_alignment_size,
                ori_helixwidthpix, ori_pixelsize, each_frame_image_ids, frame_stack_path)
            
            os.rename(self.get_frame_stack_path(ori_large_segment_stack, 0), large_binned_segment_stack)
            os.symlink(large_binned_segment_stack, self.get_frame_stack_path(ori_large_segment_stack, 0))
        else:
            large_binned_segment_stack, segment_size_pix, helixwidthpix, pixelsize = \
            SegmentExam().apply_binfactor(each_info.bin_factor, ori_large_segment_stack, ori_alignment_size,
            ori_helixwidthpix, ori_pixelsize, image_list, os.path.join(self.tempdir, ori_large_segment_stack))

        return large_binned_segment_stack, segment_size_pix, helixwidthpix


    def perform_iterative_projection_matching_and_3d_reconstruction(self):
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        
        required_byte, info_series = self.estimate_required_tmp_disk_space()
        self.tempdir = Temporary().mktmpdir(self.temppath, required_byte)
        
        large_segment_stack, masked_segment_stack, image_list, reference_files, lambda_sirt, start_ref_cycle_id = \
        self.pre_cycle_setup(info_series)
        
        ori_large_segment_stack, ori_reference_files, ori_alignment_size, ori_helixwidthpix, ori_pixelsize = \
        self.define_original_input_values_before_binning(large_segment_stack, reference_files)
        
        self.log.plog(5)
        
        ref_cycle_id, unbending_info, large_straightened_stack = \
        self.setup_dummies_for_iteration(start_ref_cycle_id)
        
        for each_index, each_info in enumerate(info_series):
            large_binned_segment_stack, segment_size_pix, helixwidthpix = \
            self.bin_including_copies_of_frames_if_requested(image_list, ori_large_segment_stack, ori_alignment_size,
            ori_helixwidthpix, ori_pixelsize, each_info)
            
            reference_files, ctf3d_avg_squared, pixelinfo = self.precycle_setup_before_binning(info_series,
            large_binned_segment_stack, reference_files, ori_reference_files, ori_pixelsize, each_index, ref_cycle_id,
            segment_size_pix, helixwidthpix)
        
            for each_iteration_number in list(range(1, each_info.iteration_count + 1)):
                ref_cycle_id += 1
                
                mask_params, previous_params, prj_info, reference_files = \
                self.project_including_masking_and_filtering(required_byte, info_series, reference_files,
                start_ref_cycle_id, ref_cycle_id, each_info, each_iteration_number, pixelinfo)
        
                masked_segment_stack, previous_params, unbending_info, large_straightened_stack, \
                large_reconstruction_stack = self.mask_and_window_and_unbend_if_required(info_series,
                masked_segment_stack, start_ref_cycle_id, ref_cycle_id, each_info, large_binned_segment_stack,
                each_iteration_number, mask_params, previous_params, unbending_info, large_straightened_stack,
                pixelinfo)
                    
                if self.resume_refinement_option and not self.reference_option and each_iteration_number == 1:
                    current_parameters = previous_params
                    translation_step = 1.0
                else:
                    current_parameters, translation_step, prj_info = \
                    self.perform_coarse_and_fine_projection_matching(each_info, masked_segment_stack, prj_info,
                    previous_params, pixelinfo.alignment_size)
            
                large_binned_segment_stack = large_reconstruction_stack

                self.log.plog(90 * (ref_cycle_id - start_ref_cycle_id + 0.7 - 1) / float(self.iteration_count) + 5)
                
                selected_parameters = self.select_segments_based_on_specified_criteria(current_parameters,
                unbending_info, translation_step, ref_cycle_id, each_info, pixelinfo, reference_files)
                
                reconstruction_stack = self.choose_reconstruction_stack_based_on_unbending(large_straightened_stack,
                large_reconstruction_stack)
                    
                reference_files, lambda_sirt = self.reconstruct_volume(reference_files, lambda_sirt,
                start_ref_cycle_id, ref_cycle_id, each_info, pixelinfo, ctf3d_avg_squared,
                reconstruction_stack, selected_parameters, prj_info)
                
                self.log.plog(90 * (ref_cycle_id - start_ref_cycle_id) / float(self.iteration_count) + 5)
                
                aim_ref = self.get_aim_dict()
                if self.halfset_refinement and aim_ref[each_info.resolution_aim] >= aim_ref[self.halfset_start]:
                    reference_files = self.compute_cross_fsc_and_write_out_merged_volume(reference_files, each_info,
                    pixelinfo, ref_cycle_id)

                if self.layer_line_filter and not self.unbending:
                    os.remove(large_straightened_stack)
        
            if self.unbending:
                os.remove(large_straightened_stack)
                
            os.remove(large_reconstruction_stack)
        
        self.update_persistence_length_in_spring_db()

        os.remove(large_segment_stack)
        self.clean_up_temporary_large_stack(large_segment_stack, masked_segment_stack)
        if self.ctf_correction:
            os.remove(ctf3d_avg_squared)
        os.rmdir(self.tempdir)
        
        self.log.endlog(self.feature_set)
            
def main():
    # Option handling
    parset = SegmentRefine3dPar()
    mergeparset = OptHandler(parset)

    ######## Program
    stack = SegmentRefine3d(mergeparset)
    stack.perform_iterative_projection_matching_and_3d_reconstruction()


if __name__ == '__main__':
    main()
