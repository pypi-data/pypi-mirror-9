# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from collections import namedtuple
import os
import shutil
from spring.csinfrastr.csdatabase import SpringDataBase, refine_base, base, RefinementCycleTable, \
    RefinementCycleHelixTable, RefinementCycleSegmentTable, SegmentTable, HelixTable, CtfMicrographTable
from spring.segment2d.segmentselect import SegmentSelect
from spring.segment3d.refine.sr3d_align import SegmentRefine3dAlign
from spring.segment3d.segclassreconstruct import SegClassReconstruct

from sqlalchemy.sql.expression import or_, desc, and_

import numpy as np


class SegmentRefine3dSelectionFilter(SegmentRefine3dAlign):
    def get_excluded_refinement_count(self, session, included_segments_classes):
        segment_count = session.query(SegmentTable).order_by(SegmentTable.stack_id).count()
        excluded_count = segment_count - len(set(included_segments_classes))
        
        return excluded_count
    
    
    def filter_refined_segments_by_property(self, session, ref_session, refined_segment_table_property, last_cycle,
    property_selection, property_in_or_exclude, property_range):
        included_segments_property = []
        if property_selection:
            if property_in_or_exclude == 'include':
                included_segments = ref_session.query(RefinementCycleSegmentTable).\
                filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
                filter(and_(refined_segment_table_property >= property_range[0], 
                            refined_segment_table_property <=property_range[1])).all()
                
                included_segments_property = [each_segment.stack_id for each_segment in included_segments]

            elif property_in_or_exclude == 'exclude':
                included_segments = ref_session.query(RefinementCycleSegmentTable).\
                filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
                filter(or_(refined_segment_table_property < property_range[0], 
                           refined_segment_table_property > property_range[1])).all()
                           
                included_segments_property = [each_segment.stack_id for each_segment in included_segments]

        elif not property_selection:
            included_segments = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).all()
            included_segments_property = [each_segment.stack_id for each_segment in included_segments]
            
        excluded_segment_count = self.get_excluded_refinement_count(session, included_segments_property)
        
        return included_segments_property, excluded_segment_count
    
    
    def filter_segments_by_ccc_against_projections(self, session, ref_session, last_cycle, ccc_proj_selection,
    ccc_proj_in_or_exclude, ccc_proj_range):
        included_segments_ccc_proj, excluded_proj_cc_count = self.filter_refined_segments_by_property(session,
        ref_session, RefinementCycleSegmentTable.peak, last_cycle, ccc_proj_selection, ccc_proj_in_or_exclude,
        ccc_proj_range)
                    
        return included_segments_ccc_proj, excluded_proj_cc_count
    
    
    def filter_segments_by_out_of_plane_tilt(self, session, ref_session, last_cycle, out_of_plane_selection,
    out_of_plane_in_or_exclude, out_of_plane_in_or_ex_range):
        
        included_segments_oop_tilt, excluded_segments_oop_tilt_count = \
        self.filter_refined_segments_by_property(session, ref_session, RefinementCycleSegmentTable.theta - 90,
        last_cycle, out_of_plane_selection, out_of_plane_in_or_exclude, out_of_plane_in_or_ex_range)
        
        return included_segments_oop_tilt, excluded_segments_oop_tilt_count


    def filter_segments_when_located_at_end_of_helix(self, session, alignment_size):
        helices = session.query(HelixTable).order_by(HelixTable.id).all()
        included_segments_no_ends = []
        for each_helix in helices:
            each_helix_segments = self.get_segment_ids_from_helix(session, each_helix)
            
            segments_at_helix_center = session.query(SegmentTable).\
            filter(SegmentTable.stack_id.in_(each_helix_segments)).\
            filter(and_(SegmentTable.distance_from_start_A > alignment_size/2, 
                        SegmentTable.distance_from_start_A < (each_helix.length - alignment_size/2))).all()
            
            if segments_at_helix_center is not None:
                stack_ids_at_helix_center = [ each_segment.stack_id for each_segment in segments_at_helix_center ]
                included_segments_no_ends += stack_ids_at_helix_center
            
        excluded_segments_at_ends_count = self.get_excluded_refinement_count(session, included_segments_no_ends)
        
        return included_segments_no_ends, excluded_segments_at_ends_count
    
    
    def get_selected_segments_from_last_cycle(self, ref_session):
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
        
        selected_ref_segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
        filter(RefinementCycleSegmentTable.selected == True).all()
        
        return selected_ref_segments, last_cycle
            
            
    def filter_phis_such_that_distribution_remains_even(self, phis, peaks, azimuthal_angle_count, min_bin=None):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> phis = np.array([0, 0, 0, 0, 120, 240,240,240,240,240])
        >>> s = SegmentRefine3d()
        >>> s.filter_phis_such_that_distribution_remains_even(phis, np.arange(100,110), 3)
        ([3, 2, 4, 9, 8], array([  0,   0, 120, 240, 240]))
        """
        multiple = 10.0
        if azimuthal_angle_count < multiple:
            multiple = 1
        bin_count = int(azimuthal_angle_count / float(multiple))
        freq, bound = np.histogram(phis, bin_count, (0.0, 360.0))
        mean_freq = np.mean(freq)
        cutoff_max = freq[freq <= mean_freq]
    
        if min_bin is None:
            min_bin = 2.0 * int(np.mean(cutoff_max) / float(multiple))
            
        selected_ids = []
        stack_ids = np.arange(len(phis))
        for each_id, each_bound in enumerate(bound[:-1]):
            lower_bound = each_bound
            upper_bound = bound[each_id + 1]
            filtered_peaks = peaks[(lower_bound <= phis) & (phis < upper_bound)]
            filtered_ids = stack_ids[(lower_bound <= phis) & (phis < upper_bound)]
            sorted_ids = np.flipud(np.argsort(filtered_peaks))
            sorted_filtered_ids = filtered_ids[sorted_ids]
            
            sel_id_count = min(len(sorted_filtered_ids), min_bin)
            selected_ids += sorted_filtered_ids[:sel_id_count].tolist()
        self.log.ilog('Even phi angle distribution is enforced. The following bin frequency is used as a threshold: '+ \
        '{0}'.format(min_bin))
                    
        return selected_ids, phis[selected_ids]
    

    def randomize_phi_and_corresponding_helix_y_shift_based_to_pitch(self, pitch, rand_val, each_included_segment):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> seg_info = namedtuple('seg_info', 'inplane_angle phi helix_shift_x_A helix_shift_y_A shift_x_A shift_y_A')
        >>> each_segment = seg_info(0., 0., 0., 0., None, None)
        >>> SegmentRefine3d().randomize_phi_and_corresponding_helix_y_shift_based_to_pitch(180, 0, each_segment)
        (0.0, 0.0, 0.0, 0.0)
        >>> SegmentRefine3d().randomize_phi_and_corresponding_helix_y_shift_based_to_pitch(180, 1, each_segment)
        (0.0, 180.0, 0.0, 180.0)
        >>> SegmentRefine3d().randomize_phi_and_corresponding_helix_y_shift_based_to_pitch(180, 0.5, each_segment)
        (180.0, 90.0, 0.0, 90.0)
        >>> SegmentRefine3d().randomize_phi_and_corresponding_helix_y_shift_based_to_pitch(180, -0.5, each_segment)
        (180.0, -90.0, 0.0, -90.0)
        >>> SegmentRefine3d().randomize_phi_and_corresponding_helix_y_shift_based_to_pitch(0, 1, each_segment)
        (0.0, 0.0, 0.0, 0.0)
        """
        phi = each_included_segment.phi + (rand_val * 360.0) % 360
        helix_shift_y_A = each_included_segment.helix_shift_y_A + rand_val * pitch
        
        x_shift, y_shift = \
        SegClassReconstruct().compute_sx_sy_from_shifts_normal_and_parallel_to_helix_axis_with_inplane_angle(
        each_included_segment.helix_shift_x_A, helix_shift_y_A,
        each_included_segment.inplane_angle)
        
        return phi, helix_shift_y_A, x_shift, y_shift
    
    
    def enter_results_to_segments(self, results, each_segment):
        phi, helix_shift_y_A, x_shift, y_shift = results
        
        each_segment.phi = phi
        each_segment.helix_shift_y_A = helix_shift_y_A
        each_segment.shift_x_A = x_shift
        each_segment.shift_y_A = y_shift
        
        return each_segment
    

    def enforce_even_phi_distribution(self, enforce_even_phi, release_cycle, ref_session, each_info):
        excluded_ids = []
        if enforce_even_phi:
            selected_segments, last_cycle = self.get_selected_segments_from_last_cycle(ref_session)
            
            if last_cycle.id == 1 and not self.reference_option:
                for each_included_segment in selected_segments:
                    rand_val = 2 * np.random.random() - 1
                    
                    results = self.randomize_phi_and_corresponding_helix_y_shift_based_to_pitch(self.pitch_enforce,
                    rand_val, each_included_segment)
                    
                    each_included_segment = self.enter_results_to_segments(results, each_included_segment)
                    
                    ref_session.merge(each_included_segment)
            else:
                phis = np.array([each_segment.phi for each_segment in selected_segments])
                peaks = np.array([each_segment.peak for each_segment in selected_segments])
                sel_ids = np.array([each_segment.stack_id for each_segment in selected_segments])
                
                if self.bin_cutoff_enforce > len(phis) or self.bin_cutoff_enforce == 0:
                    min_bin = None
                else:
                    min_bin = self.bin_cutoff_enforce
                    
                filtered_ids, filtered_phis = self.filter_phis_such_that_distribution_remains_even(phis, peaks, 
                self.azimuthal_angle_count, min_bin)
                
                filt_sel_ids = sel_ids[filtered_ids]
            
                enforce_even_cycle = release_cycle / 2
                for each_selected_segment in selected_segments:
                    if each_selected_segment.stack_id not in filt_sel_ids:
                        if last_cycle.id <= enforce_even_cycle:
                            rand_val = 2 * np.random.random() - 1 
                            
                            results =\
                            self.randomize_phi_and_corresponding_helix_y_shift_based_to_pitch(self.pitch_enforce,
                            rand_val, each_selected_segment)
                            
                            each_selected_segment = self.enter_results_to_segments(results, each_selected_segment)
                            ref_session.merge(each_selected_segment)
                        elif enforce_even_cycle <= last_cycle.id <= release_cycle or min_bin is not None:
                            excluded_ids.append(each_selected_segment.stack_id)
            
            last_cycle.excluded_phi_count = len(excluded_ids)
            ref_session.commit()
        
        return excluded_ids


class SegmentRefine3dSelection(SegmentRefine3dSelectionFilter):
    
    def setup_new_refinement_db_for_each_cycle(self, ref_cycle_id):
        temp_current_ref_db = os.path.join(self.tempdir, 'ref_temp{0}{1:03}.db'.format(os.getpid(), ref_cycle_id))
        current_ref_session = SpringDataBase().setup_sqlite_db(refine_base, temp_current_ref_db)
            
        prev_ref_db = 'refinement{0:03}.db'.format(ref_cycle_id - 1)
        if os.path.exists(prev_ref_db):
            temp_prev_ref_db = self.copy_ref_db_to_tempdir(ref_cycle_id - 1)
            prev_ref_session = SpringDataBase().setup_sqlite_db(refine_base, temp_prev_ref_db)

            current_ref_session = \
            SpringDataBase().copy_all_table_data_from_one_session_to_another_session(RefinementCycleTable,
            current_ref_session, prev_ref_session)
            prev_ref_session.close()
            os.remove(temp_prev_ref_db)
                
        return current_ref_session, temp_current_ref_db
    

    def enter_refinement_parameters_in_database(self, ref_session, orientation_parameters, unbending_info,
    current_translation_step, ref_cycle_id, each_info, pixelinfo, rank=None):
        
        refinement_cycle = RefinementCycleTable()
        refinement_cycle.iteration_id = ref_cycle_id
        refinement_cycle.pixelsize = pixelinfo.pixelsize
        refinement_cycle.alignment_size_A = pixelinfo.alignment_size * pixelinfo.pixelsize
        refinement_cycle.reconstruction_size_A = pixelinfo.reconstruction_size * pixelinfo.pixelsize
        refinement_cycle.restrict_inplane = self.restrain_in_plane_rotation
        refinement_cycle.delta_inplane = self.delta_in_plane_rotation
        refinement_cycle.unbending = self.unbending
        refinement_cycle.azimuthal_restraint = each_info.azimuthal_restraint
        refinement_cycle.out_of_plane_restraint = each_info.out_of_plane_restraint
        refinement_cycle.out_of_plane_min = min(self.out_of_plane_tilt_angle_range)
        refinement_cycle.out_of_plane_max = max(self.out_of_plane_tilt_angle_range)
        refinement_cycle.out_of_plane_count = self.out_of_plane_tilt_angle_count
        refinement_cycle.azimuthal_count = self.azimuthal_angle_count
        refinement_cycle.translation_step = current_translation_step * pixelinfo.pixelsize
        refinement_cycle.x_translation_range_A = each_info.x_range * pixelinfo.pixelsize
        refinement_cycle.y_translation_range_A = each_info.y_range * pixelinfo.pixelsize
        
        for each_orient_param in orientation_parameters:
            refinement_segment = RefinementCycleSegmentTable()
            refinement_segment.cycles  = refinement_cycle
            refinement_segment.stack_id = each_orient_param.stack_id
            refinement_segment.local_id = each_orient_param.local_id
            refinement_segment.rank_id = each_orient_param.rank_id
            refinement_segment.model_id = each_orient_param.model_id
            refinement_segment.phi = each_orient_param.phi
            refinement_segment.theta = each_orient_param.theta
            refinement_segment.psi = each_orient_param.psi
            if self.unbending:
                refinement_segment.unbent_ip_angle = each_orient_param.inplane_angle
                refinement_segment.unbent_shift_x_A = each_orient_param.shift_x * pixelinfo.pixelsize
                refinement_segment.unbent_shift_y_A = each_orient_param.shift_y * pixelinfo.pixelsize
                updated_inplane_angle = -(unbending_info[each_orient_param.local_id].angle + \
                                          each_orient_param.inplane_angle) % 360
                refinement_segment.unbending_angle = updated_inplane_angle
                
                x_distance = each_orient_param.shift_x + unbending_info[each_orient_param.local_id].shift_x
                y_distance = each_orient_param.shift_y + unbending_info[each_orient_param.local_id].shift_y
                
                shift_x_A = x_distance * pixelinfo.pixelsize
                shift_y_A = y_distance * pixelinfo.pixelsize
                
                x_distance, y_distance = SegClassReconstruct().compute_distances_to_helical_axis(x_distance, y_distance,
                updated_inplane_angle)
                 
            else:
                x_distance, y_distance = \
                SegClassReconstruct().compute_distances_to_helical_axis(each_orient_param.shift_x,
                each_orient_param.shift_y, each_orient_param.inplane_angle)
                
                shift_x_A = each_orient_param.shift_x * pixelinfo.pixelsize
                shift_y_A = each_orient_param.shift_y * pixelinfo.pixelsize
                updated_inplane_angle = each_orient_param.inplane_angle
            
            refinement_segment.shift_x_A = shift_x_A
            refinement_segment.shift_y_A = shift_y_A
            refinement_segment.inplane_angle = updated_inplane_angle

#             refinement_segment.out_of_plane_angle = \
#             self.compute_out_of_plane_angle_with_respect_to_avg_inplane_angle(each_orient_param.theta, 
#             each_orient_param.psi, updated_inplane_angle)
            refinement_segment.out_of_plane_angle = each_orient_param.theta - 90.0

            refinement_segment.helix_shift_x_A = x_distance * pixelinfo.pixelsize
            refinement_segment.helix_shift_y_A = y_distance * pixelinfo.pixelsize
            
            refinement_segment.peak = each_orient_param.peak
            refinement_segment.mirror = each_orient_param.mirror
        
            ref_session.add(refinement_segment)
        
        ref_session.commit()
        
        return ref_session
    
    
    def get_exluded_ref_count_named_tuple(self):
        excluded_counts = namedtuple('refinement_counts', 'out_of_plane_tilt_count cc_prj_count helix_shift_x_count')
        return excluded_counts


    def enter_excluded_refinement_counts_in_database(self, ref_segment_count, ref_session,
    excluded_refinement_counts):
        
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
        
        last_cycle.excluded_out_of_plane_tilt_count = excluded_refinement_counts.out_of_plane_tilt_count
        last_cycle.excluded_prj_cc_count = excluded_refinement_counts.cc_prj_count
        last_cycle.excluded_helix_shift_x_count = excluded_refinement_counts.helix_shift_x_count
        
        last_cycle.segment_count = ref_segment_count
        
        ref_session.merge(last_cycle)
        ref_session.commit()
        
    
class SegmentRefine3dParameterAveraging(SegmentRefine3dSelection):
    def get_selected_segments_from_last_refinement_cycle(self, session, ref_session, last_cycle, each_helix):
        each_helix_segments = self.get_segment_ids_from_helix(session, each_helix)
        segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
        filter(RefinementCycleSegmentTable.stack_id.in_(each_helix_segments)).\
        filter(RefinementCycleSegmentTable.selected == True).all()
        
        return segments


    def get_distances_from_segment_ids(self, session, segment_ids):
        segments = session.query(SegmentTable).filter(SegmentTable.stack_id.in_(segment_ids))
        
        distances_from_start = np.array([each_segment.distances_from_start for each_segment in segments])
        
        return distances_from_start
    

    def sort_inplane_angles_into_0_360_or_180_degrees(self, selected_inplane_angles, cropped_segment_ids,
    lavg_inplane_angles, distances_from_start):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> sel = np.array([300.0, 301.0, 119.0])
        >>> ids = np.array([0, 1, 2])
        >>> angles = np.array([300.0, 300.0, 300.0])
        >>> dist = np.array([10, 20, 30])
        >>> s.sort_inplane_angles_into_0_360_or_180_degrees(sel, ids, angles, dist) #doctest: +NORMALIZE_WHITESPACE
        (array([30]), array([ 300.]), array([10, 20]), array([ 300.,  300.]), 
        array([2]), array([0, 1]), array([ 59.]), array([ 240.,  241.]))
        """
        inplane_angles_normalized = (selected_inplane_angles + lavg_inplane_angles) % 360 
        cropped_segment_ids = np.array(cropped_segment_ids)
        smaller_90_and_larger_270 = (inplane_angles_normalized < 90) ^ (inplane_angles_normalized > 270)
        close_to_0_360 = inplane_angles_normalized[smaller_90_and_larger_270]
        lavg_close_to_0_360 = lavg_inplane_angles[smaller_90_and_larger_270]
        dist_close_to_0_360 = distances_from_start[smaller_90_and_larger_270]
        ids_close_to_0_360 = cropped_segment_ids[smaller_90_and_larger_270]
        
        between_90_and_270 = (inplane_angles_normalized > 90) & (inplane_angles_normalized < 270)
        close_to_180 = inplane_angles_normalized[between_90_and_270]
        lavg_close_to_180 = lavg_inplane_angles[between_90_and_270]
        dist_close_to_180 = distances_from_start[between_90_and_270]
        ids_close_to_180 = cropped_segment_ids[between_90_and_270]
        
        return dist_close_to_0_360, lavg_close_to_0_360, dist_close_to_180, lavg_close_to_180, ids_close_to_0_360, \
        ids_close_to_180, close_to_0_360, close_to_180
    

    def compute_fitted_parameters(self, distances, parameters, new_distances=None):
        if new_distances is None:
            new_distances = distances
#        try:
#        spline_coefficients = interpolate.splrep(distances, parameters, k=2, s=3)
#        spline_fitted_parameters = interpolate.splev(new_distances, spline_coefficients)
        
        polyfit = np.polyfit(distances, parameters, max(1, int(max(distances)/1000)))
        spline_fitted_parameters = np.polyval(polyfit, new_distances)
#        except:
#            spline_fitted_parameters = parameters
        
        return spline_fitted_parameters
    

    def get_inplane_angles_per_segment_and_interpolate_two_oposite_angles(self, session, ref_session, current_cycle,
    each_helix):
        segments = self.get_selected_segments_from_last_refinement_cycle(session, ref_session, current_cycle,
        each_helix)
        
        selected_inplane_angles = np.array([each_segment.inplane_angle for each_segment in segments])
        cropped_segment_ids = [each_segment.stack_id for each_segment in segments]
        cropped_segments = session.query(SegmentTable).filter(SegmentTable.stack_id.in_(cropped_segment_ids))
        lavg_inplane_angles = np.array([each_segment.lavg_inplane_angle for each_segment in cropped_segments])
        
        if each_helix.flip_inplane_angle and current_cycle.id != 1:
            lavg_inplane_angles = (lavg_inplane_angles + 180) % 360
            flip = 1
        else:
            flip = 0
        distances_from_start = self.get_distances_from_segment_ids(session, cropped_segment_ids)
        
        dist_close_to_0_360, lavg_close_to_0_360, dist_close_to_180, lavg_close_to_180, ids_close_to_0_360, \
        ids_close_to_180, close_to_0_360, close_to_180 = \
        self.sort_inplane_angles_into_0_360_or_180_degrees(selected_inplane_angles, cropped_segment_ids,
        lavg_inplane_angles, distances_from_start)
        
        continuous_close_to_0_360 = (close_to_0_360 + 180) % 360
        spline_fitted_angles_0_360 = self.compute_fitted_parameters(dist_close_to_0_360, continuous_close_to_0_360)
        discont_spline_fitted_angles_0_360 = (spline_fitted_angles_0_360 - 180) % 360
        spline_fitted_angles_180 = self.compute_fitted_parameters(dist_close_to_180, close_to_180)
        
        return flip, segments, lavg_close_to_0_360, lavg_close_to_180, ids_close_to_0_360, ids_close_to_180, \
        close_to_0_360, close_to_180, discont_spline_fitted_angles_0_360, spline_fitted_angles_180


    def measure_inplane_angle_and_decide_for_predominant_angle(self, ref_session, segments, flip, lavg_close_to_0_360,
    lavg_close_to_180, ids_close_to_0_360, ids_close_to_180, close_to_0_360, close_to_180,
    discont_spline_fitted_angles_0_360, spline_fitted_angles_180):
        for each_ref_segment in segments:
            if each_ref_segment.stack_id in ids_close_to_0_360:
                index = ids_close_to_0_360.tolist().index(each_ref_segment.stack_id)
                lavg_inplane = (-(discont_spline_fitted_angles_0_360[index] - np.mean(lavg_close_to_0_360 + 180))) % 360
            if each_ref_segment.stack_id in ids_close_to_180:
                index = ids_close_to_180.tolist().index(each_ref_segment.stack_id)
                lavg_inplane = (-(spline_fitted_angles_180[index] - np.mean(lavg_close_to_180))) % 360
            each_ref_segment.lavg_inplane = lavg_inplane
            ref_session.add(each_ref_segment)
        
        if close_to_0_360.size >= close_to_180.size:
            avg_inplane_angle = (np.mean((close_to_0_360 + 180) % 360 - 180) - lavg_close_to_0_360) % 360
        else:
            avg_inplane_angle = (np.mean(close_to_180) - lavg_close_to_180) % 360
            flip = flip + 1
            
        return flip, avg_inplane_angle
    

    def enter_helix_inplane_parameters_in_database(self, session, ref_session, current_cycle, each_helix, flip,
    close_to_0_360, close_to_180):
        ref_helix = RefinementCycleHelixTable()
        ref_helix.segment_count_0_degree = close_to_0_360.size
        ref_helix.segment_count_180_degree = close_to_180.size
        ref_helix.cycle_id = current_cycle.id
        ref_helix.helix_id = each_helix.id
        ref_helix.flip_inplane_angle = (flip) % 2
        ref_session.add(ref_helix)
        each_helix.flip_inplane_angle = (flip) % 2
        session.merge(each_helix)


    def normalize_inplane_angles_by_picked_angles(self, picked_segment_angles, ref_inplane_angles):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> picked = np.arange(80, 90)
        >>> refined = np.arange(80.5, 90.5)
        >>> s.normalize_inplane_angles_by_picked_angles(picked, refined)
        array([ 0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5])
        """
        inplane_angles_normalized = (ref_inplane_angles - picked_segment_angles) % 360
        
        return inplane_angles_normalized
    

    def determine_predominant_side_of_angles(self, picked_segment_angles, flip, ref_inplane_angles,
    each_helix_stack_ids):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> picked = np.arange(80, 90)
        >>> flip = 0 
        >>> refined = np.arange(80.5, 90.5)
        >>> ids = np.arange(10)
        >>> s.determine_predominant_side_of_angles(picked, flip, refined, ids) #doctest: +NORMALIZE_WHITESPACE
        (0, array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), array([], dtype=int64), 
        array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), 
        array([ 0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5]))
        
        >>> picked = np.arange(80, 90)
        >>> flip = 0
        >>> refined = np.arange(260.5, 270.5)
        >>> ids = np.arange(20, 30)
        >>> s.determine_predominant_side_of_angles(picked, flip, refined, ids) #doctest: +NORMALIZE_WHITESPACE
        (1, array([], dtype=int64), 
        array([20, 21, 22, 23, 24, 25, 26, 27, 28, 29]), 
        array([20, 21, 22, 23, 24, 25, 26, 27, 28, 29]), 
        array([ 0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5]))
        """
        each_helix_stack_ids = np.array(each_helix_stack_ids)
        
        inplane_angles_normalized  = self.normalize_inplane_angles_by_picked_angles(picked_segment_angles,
        ref_inplane_angles)
        
        smaller_90_and_larger_270 = (inplane_angles_normalized < 90) ^ (inplane_angles_normalized > 270)
        close_to_0_360 = each_helix_stack_ids[smaller_90_and_larger_270]
        between_90_and_270 = (inplane_angles_normalized > 90) & (inplane_angles_normalized < 270)
        close_to_180 = each_helix_stack_ids[between_90_and_270]
        
        if close_to_0_360.size >= close_to_180.size:
            predominant_set = close_to_0_360
        else:
            predominant_set = close_to_180
            inplane_angles_normalized -= 180.0
            flip = flip + 1
            
        return flip, close_to_0_360, close_to_180, predominant_set, inplane_angles_normalized
    

    def get_all_selected_stack_ids(self, ref_session, current_cycle):
        selected_ref_segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == current_cycle.id).\
        filter(RefinementCycleSegmentTable.selected == True).all()
        
        selected_segments = [each_ref_segment.stack_id for each_ref_segment in selected_ref_segments]
        selected_segments = list(set(selected_segments))
        
        return selected_segments


    def enter_selected_information(self, polar_helix, ref_session, ref_segments, predominant_set,
    inplane_angles_normalized, excluded_polarity_ids):
        for each_seg_index, each_ref_segment in enumerate(ref_segments):
            if each_ref_segment.stack_id in predominant_set or polar_helix in ['apolar'] or not self.force_hel_continue:
                each_ref_segment.selected = True
            else:
                each_ref_segment.selected = False
                excluded_polarity_ids.append(each_ref_segment.stack_id)
            each_ref_segment.norm_inplane_angle = inplane_angles_normalized[each_seg_index]
            ref_session.merge(each_ref_segment)
        
        return excluded_polarity_ids
    

    def exclude_inplane_angles_outside_delta_psi(self, restrain_in_plane_rotation, delta_in_plane_rotation, ref_session,
    current_cycle):
        if restrain_in_plane_rotation:
            selected_ref_segments = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == current_cycle.id).\
            filter(RefinementCycleSegmentTable.selected == True).\
            filter(or_(*
                       [and_(*[RefinementCycleSegmentTable.norm_inplane_angle > delta_in_plane_rotation, 
                               RefinementCycleSegmentTable.norm_inplane_angle < 180.0 - delta_in_plane_rotation]), 
                        and_(*[RefinementCycleSegmentTable.norm_inplane_angle > 180.0 + delta_in_plane_rotation, 
                               RefinementCycleSegmentTable.norm_inplane_angle < 360.0 - delta_in_plane_rotation])]
                       )).all()
                       
            for each_selected_segment in selected_ref_segments:
                each_selected_segment.selected = False
                ref_session.merge(each_selected_segment)
            
            excluded_inplane_ids = [each_selected_segment.stack_id for each_selected_segment in selected_ref_segments]
            ref_session.commit()
        else:
            excluded_inplane_ids = []
            
        return excluded_inplane_ids
    

    def select_segments_based_on_in_plane_rotation(self, session, ref_session, last_cycle, helices, polar_helix,
    restrain_in_plane_rotation, delta_in_plane_rotation, included_non_orientation):
        
        excluded_polarity_ids = []
        for each_helix in helices:
            each_helix_segments = session.query(SegmentTable).filter(SegmentTable.helix_id == each_helix.id).all()

            each_helix_segment_ids = [each_segment.stack_id for each_segment in each_helix_segments 
                                      if each_segment.stack_id in included_non_orientation]
            picked_segment_angles = np.array([each_segment.lavg_inplane_angle for each_segment in each_helix_segments
                                      if each_segment.stack_id in included_non_orientation])
            
            if each_helix.flip_inplane_angle:
                picked_segment_angles = (picked_segment_angles + 180) % 360
                flip = 1
            else:
                flip = 0 
            
            ref_segments = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
            filter(RefinementCycleSegmentTable.stack_id.in_(each_helix_segment_ids)).\
            order_by(RefinementCycleSegmentTable.id).all()
            
            ref_inplane_angles = np.array([each_ref_segment.inplane_angle for each_ref_segment in ref_segments])
            
            flip, close_to_0_360, close_to_180, predominant_set, inplane_angles_normalized = \
            self.determine_predominant_side_of_angles(picked_segment_angles, flip, ref_inplane_angles,
            each_helix_segment_ids)
                
            self.enter_helix_inplane_parameters_in_database(session, ref_session, last_cycle, each_helix, flip,
            close_to_0_360, close_to_180)
            
            excluded_polarity_ids = self.enter_selected_information(polar_helix, ref_session, ref_segments,
            predominant_set, inplane_angles_normalized, excluded_polarity_ids)
            
        ref_session.commit()
        
        excluded_inplane_ids = self.exclude_inplane_angles_outside_delta_psi(restrain_in_plane_rotation,
        delta_in_plane_rotation, ref_session, last_cycle)
            
        last_cycle.excluded_inplane_count = len(set(excluded_polarity_ids + excluded_inplane_ids))
        ref_session.commit()
        session.commit()
            
        selected_segments = self.get_all_selected_stack_ids(ref_session, last_cycle)
        
        return selected_segments
        
        
#     def compute_out_of_plane_angle_with_respect_to_inplane_angle(self, theta, inplane_angle):
#         if 90.0 < inplane_angle <= 270.0:
#             out_of_plane_angle = -(90.0 - theta)
#         else:
#             out_of_plane_angle = 90 - theta
#             
#         return out_of_plane_angle
#     
#             
#     def compute_out_of_plane_angle_with_respect_to_avg_inplane_angle(self, theta, psi, avg_inplane_angle):
#         """
#         >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
#         >>> s = SegmentRefine3d()
#         >>> s.compute_out_of_plane_angle_with_respect_to_avg_inplane_angle(90, 275, 5)
#         0
#         >>> s.compute_out_of_plane_angle_with_respect_to_avg_inplane_angle(86, 275, 5)
#         4
#         >>> s.compute_out_of_plane_angle_with_respect_to_avg_inplane_angle(86, 95, 5)
#         -4
#         >>> s.compute_out_of_plane_angle_with_respect_to_avg_inplane_angle(94, 95, 5)
#         4
#         >>> s.compute_out_of_plane_angle_with_respect_to_avg_inplane_angle(94, 275, 5)
#         -4
#         """
#         psi_norm = (psi - avg_inplane_angle - 270.0) % 360
#         if psi_norm < 90 or psi_norm > 270:
#             out_of_plane_angle = 90 - theta
#         elif 90 <= psi_norm <= 270:
#             out_of_plane_angle = -(90 - theta)
#         
#         return out_of_plane_angle
        

    def get_all_distances_and_selection_mask_from_ref_segments(self, session, ref_session, last_cycle, each_helix,
    included_non_orientation):
        
        each_helix_segments = session.query(SegmentTable).filter(SegmentTable.helix_id == each_helix.id).all()
        
        all_helix_segment_ids = [each_segment.stack_id for each_segment in each_helix_segments
                                 if each_segment.stack_id in included_non_orientation]
        all_distances_from_start = [each_segment.distance_from_start_A for each_segment in each_helix_segments
                                 if each_segment.stack_id in included_non_orientation]
        
        if all_helix_segment_ids != []:
            all_ref_helix_segments = self.get_all_segments_from_refinement_cycle(ref_session, last_cycle,
            all_helix_segment_ids)
        
            excluded_segments = np.invert([bool(each_segment.selected) for each_segment in all_ref_helix_segments])
        else:
            all_ref_helix_segments = []
            excluded_segments = []

        all_shift_y = np.array([each_segment.helix_shift_y_A for each_segment in all_ref_helix_segments])
        all_distances_from_start += all_shift_y
            
        return all_ref_helix_segments, each_helix_segments, excluded_segments, all_distances_from_start
    

    def compute_fit_if_more_than_three_datapoints(self, all_distances_from_start, quantity, sel_distances_from_start,
    selected_quantity):
        if len(sel_distances_from_start) > 3:
            spline_fitted_inplane_angle = self.compute_fitted_parameters(sel_distances_from_start, selected_quantity,
            all_distances_from_start)
        else:
            spline_fitted_inplane_angle = quantity

        return spline_fitted_inplane_angle


    def update_average_in_plane_rotation_angle_per_helix(self, session, ref_session, last_cycle, helices,
    included_non_orientation):
    
        for each_helix in helices:
            all_ref_helix_segments, each_helix_segments, excluded_segments, all_distances_from_start = \
            self.get_all_distances_and_selection_mask_from_ref_segments(session, ref_session, last_cycle, each_helix,
            included_non_orientation)
            
            if all_ref_helix_segments != []:
                inplane_angles_normalized = np.array([each_ref_segment.norm_inplane_angle for each_ref_segment in \
                all_ref_helix_segments])
                
                if self.polar_helix in ['polar']:
                    inplane_angles_normalized = (inplane_angles_normalized + 180.0) % 360
                elif self.polar_helix in ['apolar']:
                    inplane_angles_normalized = (inplane_angles_normalized + 90.0) % 180
                
                sel_distances_from_start = np.ma.masked_array(all_distances_from_start, mask=excluded_segments).compressed()
                selected_inplane_angles = np.ma.masked_array(inplane_angles_normalized, mask=excluded_segments).compressed()
                
                spline_fitted_inplane_angle = self.compute_fit_if_more_than_three_datapoints(all_distances_from_start,
                inplane_angles_normalized, sel_distances_from_start, selected_inplane_angles)
                
                if self.polar_helix in ['polar']:
                    spline_fitted_inplane_angle = (spline_fitted_inplane_angle - 180.0 ) % 360
                elif self.polar_helix in ['apolar']:
                    spline_fitted_inplane_angle = (spline_fitted_inplane_angle - 90.0 ) % 360
                
                picked_segment_angles = np.array([each_segment.lavg_inplane_angle for each_segment in each_helix_segments
                                                  if each_segment.stack_id in included_non_orientation])
                
                if each_helix.flip_inplane_angle:
                    picked_segment_angles = (picked_segment_angles + 180.0) % 360
                    
                corrected_inplane_angles = self.normalize_inplane_angles_by_picked_angles(-picked_segment_angles,
                spline_fitted_inplane_angle)
                
                for each_index, each_ref_segment in enumerate(all_ref_helix_segments):
                    each_ref_segment.lavg_inplane_angle = corrected_inplane_angles[each_index]
                    ref_session.merge(each_ref_segment)
            
        ref_session.commit()
        
    
    def update_average_out_of_plane_per_helix(self, session, ref_session, last_cycle, helices,
    included_non_orientation):
        
        for each_helix in helices:
            all_ref_helix_segments, each_helix_segments, excluded_segments, all_distances_from_start = \
            self.get_all_distances_and_selection_mask_from_ref_segments(session, ref_session, last_cycle, each_helix,
            included_non_orientation)
            
            if all_ref_helix_segments != []:
                out_of_plane_angles = [each_segment.out_of_plane_angle for each_segment in all_ref_helix_segments]
    
                selected_out_of_plane = np.ma.masked_array(out_of_plane_angles, mask=excluded_segments).compressed()
                sel_distances_from_start = np.ma.masked_array(all_distances_from_start, mask=excluded_segments).compressed()
                
                spline_fitted_outofplane = self.compute_fit_if_more_than_three_datapoints(all_distances_from_start,
                out_of_plane_angles, sel_distances_from_start, selected_out_of_plane)
                
                for each_index, each_ref_segment in enumerate(all_ref_helix_segments):
                    each_ref_segment.lavg_out_of_plane = spline_fitted_outofplane[each_index]
                    ref_session.merge(each_ref_segment)
            
        ref_session.commit()
        
    
    def update_average_helix_shift_x_per_helix(self, session, ref_session, last_cycle, helices,
    included_segments_non_orientation):
        for each_helix in helices:
            all_ref_helix_segments, each_helix_segments, excluded_segments, all_distances_from_start = \
            self.get_all_distances_and_selection_mask_from_ref_segments(session, ref_session, last_cycle, each_helix,
            included_segments_non_orientation)
            
            if all_ref_helix_segments != []:
                all_shift_x = np.array([each_segment.helix_shift_x_A for each_segment in all_ref_helix_segments])
                
                sel_distances_from_start = np.ma.masked_array(all_distances_from_start, mask=excluded_segments).compressed()
                selected_shift_x = np.ma.masked_array(all_shift_x, mask=excluded_segments).compressed()
                
                spline_fitted_shift_x = self.compute_fit_if_more_than_three_datapoints(all_distances_from_start,
                all_shift_x, sel_distances_from_start, selected_shift_x)
                
                for each_index, each_ref_segment in enumerate(all_ref_helix_segments):
                    each_ref_segment.lavg_helix_shift_x_A = spline_fitted_shift_x[each_index]
                    ref_session.merge(each_ref_segment)
            
        ref_session.commit()
        
            
    def enter_final_ids_into_database(self, ref_session, last_cycle, final_combined_ids):
        self.log.tlog('The following segments are included in the reconstruction ' + \
        'procedure:\n{0}'.format(', '.join([str(each_seg_id) for each_seg_id in final_combined_ids])))
        
        ref_segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).all()
        
        total_excluded = 0
        for each_segment in ref_segments:
            if not self.force_hel_continue:
                each_segment.out_of_plane_angle = each_segment.theta - 90.0
            if each_segment.stack_id in final_combined_ids:
                each_segment.selected = True
            else:
                each_segment.selected = False
                total_excluded += 1
            ref_session.merge(each_segment)
        
        last_cycle.total_excluded_count = total_excluded 
        
        ref_session.merge(last_cycle)
        ref_session.commit()
    

    def determine_forward_difference_and_set_ref_segments(self, ref_segments, helix_shift_x_A, attr_to_set):
        diffs = np.diff(helix_shift_x_A)
        forward_diffs = (np.append(diffs, 0) + np.insert(diffs, 0, 0)) / np.sqrt(2.0)

        [setattr(each_ref_segment, attr_to_set, forward_diffs[each_id]) 
         for each_id, each_ref_segment in enumerate(ref_segments)]
        
        return forward_diffs, ref_segments
        

    def compute_forward_difference_for_selected_segments_and_select(self, session, ref_session, last_cycle):
        
        helices = session.query(HelixTable).order_by(HelixTable.id).all()
        
        peaks = np.array([])
        excluded_helix_shift_x_count = 0
        included_segments_helix_shift_x = np.array([])
        for each_helix in helices:
            each_helix_segments = session.query(SegmentTable).filter(SegmentTable.helix_id == each_helix.id).all()
            each_helix_segment_ids = [each_helix_segment.stack_id for each_helix_segment in each_helix_segments]
            
            ref_segments = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
            filter(RefinementCycleSegmentTable.selected == True).\
            filter(RefinementCycleSegmentTable.stack_id.in_(each_helix_segment_ids)).all()

            helix_shift_x_A = np.array([each_ref_segment.helix_shift_x_A for each_ref_segment in ref_segments])
            inplane_rot = (np.array([each_ref_segment.norm_inplane_angle for each_ref_segment in ref_segments]) + 180) % 360
            outofplane_tilt = np.abs([each_ref_segment.out_of_plane_angle for each_ref_segment in ref_segments])

            if 'apolar' in self.polar_helices:
                helix_shift_x_A = np.abs(helix_shift_x_A)

            forward_diffs, ref_segments = self.determine_forward_difference_and_set_ref_segments(ref_segments,
            helix_shift_x_A, 'forward_diff_x_shift_A')
            
            forward_diffs_rot, ref_segments = self.determine_forward_difference_and_set_ref_segments(ref_segments,
            inplane_rot, 'forward_diff_inplane')
            
            forward_diffs_tilt, ref_segments = self.determine_forward_difference_and_set_ref_segments(ref_segments,
            outofplane_tilt, 'forward_diff_outofplane')
            
            abs_forward_diffs = np.abs(forward_diffs)
            if self.helix_shift_x_selection and self.helix_shift_x_in_or_exclude == 'include':
                ex_seg = [setattr(each_ref_segment, 'selected', False) for each_id, each_ref_segment in enumerate(ref_segments)\
                 if abs_forward_diffs[each_id] > self.helix_shift_x_in_or_ex_cutoff]

                incl_ref_stack_ids = [each_ref_segment.stack_id for each_id, each_ref_segment in enumerate(ref_segments)\
                 if abs_forward_diffs[each_id] <= self.helix_shift_x_in_or_ex_cutoff]
            elif self.helix_shift_x_selection and self.helix_shift_x_in_or_exclude == 'exclude':
                ex_seg = [setattr(each_ref_segment, 'selected', False) for each_id, each_ref_segment in enumerate(ref_segments)\
                 if abs_forward_diffs[each_id] <= self.helix_shift_x_in_or_ex_cutoff]

                incl_ref_stack_ids = [each_ref_segment.stack_id for each_id, each_ref_segment in enumerate(ref_segments)\
                 if abs_forward_diffs[each_id] > self.helix_shift_x_in_or_ex_cutoff]
            else:
                ex_seg = []
                incl_ref_stack_ids = np.array([each_ref_segment.stack_id for each_ref_segment in ref_segments])
            
            excluded_helix_shift_x_count += len(ex_seg)
            included_segments_helix_shift_x = np.append(included_segments_helix_shift_x, incl_ref_stack_ids)

            [ref_session.merge(each_ref_segment) for each_id, each_ref_segment in enumerate(ref_segments)]
            
            peaks = np.append(peaks, [each_ref_segment.peak for each_ref_segment in ref_segments])
        
        last_cycle.mean_peak = np.mean(peaks)
        
        ref_session.merge(last_cycle)
        ref_session.commit()
        
        included_segments_helix_shift_x = np.int32(included_segments_helix_shift_x)
        included_segments_helix_shift_x = included_segments_helix_shift_x.tolist()

        return included_segments_helix_shift_x, excluded_helix_shift_x_count
            

    def prepare_databases_for_selection(self, orientation_parameters, unbending_info, current_translation_step,
    ref_cycle_id, each_info, pixelinfo):
        self.log.fcttolog()
        self.log.in_progress_log()
        
        mean_peaks = [each_param.peak for each_param in orientation_parameters]

        ccc_proj_range_vals = SegmentSelect().convert_relative_range_to_absolute_range_values(mean_peaks,
        self.ccc_proj_range)

        ref_session, temp_current_ref_db = self.setup_new_refinement_db_for_each_cycle(ref_cycle_id)
        ref_session = self.enter_refinement_parameters_in_database(ref_session, orientation_parameters, 
        unbending_info, current_translation_step, ref_cycle_id, each_info, pixelinfo)
        
        return ref_session, temp_current_ref_db, ccc_proj_range_vals
    

    def select_segments_based_on_out_of_plane_tilt(self, ref_session, session, last_cycle):
        included_segments_oop_tilt, excluded_oop_tilt_count = self.filter_segments_by_out_of_plane_tilt(session,
        ref_session, last_cycle, self.out_of_plane_selection, self.out_of_plane_in_or_exclude,
        self.out_of_plane_in_or_ex_range)

        ref_segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
        filter(RefinementCycleSegmentTable.selected == True).all()
        
        for each_sel_segment in ref_segments:
            if each_sel_segment.stack_id not in included_segments_oop_tilt:
                each_sel_segment.selected = False
                ref_session.merge(each_sel_segment)
        
        ref_session.commit()
        
        return included_segments_oop_tilt, excluded_oop_tilt_count


    def select_refinement_parameters_based_on_selection_criteria_hierarchically(self, ref_session, ccc_proj_range_vals,
    session, last_cycle, helices, included_segments_non_orientation):
        ref_segments = ref_session.query(RefinementCycleSegmentTable).all()

        ref_stack_ids = [each_ref_segment.stack_id for each_ref_segment in ref_segments]
        ref_segment_count = len(ref_stack_ids)

        included_segments_non_orientation = list(set(included_segments_non_orientation).intersection(ref_stack_ids))

        included_segments_inplane = self.select_segments_based_on_in_plane_rotation(session, ref_session, last_cycle, 
        helices, self.polar_helix, self.restrain_in_plane_rotation, self.delta_in_plane_rotation, 
        included_segments_non_orientation)

        included_segments_oop_tilt, excluded_oop_tilt_count = \
        self.select_segments_based_on_out_of_plane_tilt(ref_session, session, last_cycle)

        included_segments_helix_shift_x, excluded_helix_shift_x_count = \
        self.compute_forward_difference_for_selected_segments_and_select(session, ref_session, last_cycle)

        included_segments_ccc_proj, excluded_cc_prj_count = self.filter_segments_by_ccc_against_projections(session, 
        ref_session, last_cycle, self.ccc_proj_selection, self.ccc_proj_in_or_exclude, ccc_proj_range_vals)

        excluded_counts = self.get_exluded_ref_count_named_tuple()

        excluded_refinement_counts = excluded_counts(excluded_oop_tilt_count, excluded_cc_prj_count,
        excluded_helix_shift_x_count)

        included_ref_segments = set(included_segments_oop_tilt).intersection(included_segments_ccc_proj,
        included_segments_helix_shift_x, included_segments_inplane)

        return included_ref_segments, ref_segment_count, excluded_refinement_counts


    def perform_helix_based_computations_and_selection(self, each_info, spring_db, ref_session, ccc_proj_range_vals):
        session = SpringDataBase().setup_sqlite_db(base, spring_db)
        
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
        helices = session.query(HelixTable).order_by(HelixTable.id).all()
        
        included_segments_non_orientation, excluded_non_orientation_counts = \
        SegmentSelect().filter_non_orientation_parameters_based_on_selection_criteria(self, spring_db,
        keep_helices_together=True)
        
        included_ref_segments, ref_segment_count, excluded_refinement_counts =\
        self.select_refinement_parameters_based_on_selection_criteria_hierarchically(ref_session, ccc_proj_range_vals,
        session, last_cycle, helices, included_segments_non_orientation)

        if self.force_hel_continue:
            self.update_average_in_plane_rotation_angle_per_helix(session, ref_session, last_cycle, helices,
            included_segments_non_orientation)
            
            self.update_average_out_of_plane_per_helix(session, ref_session, last_cycle, helices,
            included_segments_non_orientation)
            
            self.update_average_helix_shift_x_per_helix(session, ref_session, last_cycle, helices,
            included_segments_non_orientation)
            
        excluded_phi_ids = self.enforce_even_phi_distribution(self.enforce_even_phi, self.release_cycle, ref_session,
        each_info)
        
        included_segments_non_orientation, excluded_non_orientation_counts = \
        SegmentSelect().filter_non_orientation_parameters_based_on_selection_criteria(self, spring_db,
        keep_helices_together=False)
        
        self.enter_excluded_refinement_counts_in_database(ref_segment_count, ref_session,
        excluded_refinement_counts)
            
        final_combined_ids = list(set(included_ref_segments).intersection(included_segments_non_orientation).\
                                  difference(excluded_phi_ids))
        
        self.enter_final_ids_into_database(ref_session, last_cycle, final_combined_ids)
        
        return ref_session
    

    def get_helices_from_corresponding_frames(self, session, ref_session):
        first_mic = session.query(CtfMicrographTable).first()

        frame_ending = first_mic.micrograph_name.split('@')[-1]

        unique_mics = session.query(CtfMicrographTable).\
        filter(CtfMicrographTable.micrograph_name.endswith(frame_ending)).all()
        unique_mic_ids = [each_mic.id for each_mic in unique_mics]
            
        helices = session.query(HelixTable).order_by(HelixTable.id).all()
        unique_helices = [each_helix for each_helix in helices if each_helix.mic_id in unique_mic_ids]
        helix_ids = []
        for each_helix in unique_helices:
            segment = session.query(SegmentTable).filter(SegmentTable.helix_id == each_helix.id).first()
            segment_mic = session.query(CtfMicrographTable).filter(CtfMicrographTable.id == segment.mic_id).first()

            frame_prefix = segment_mic.micrograph_name.split('@')[0]

            frame_mics = session.query(CtfMicrographTable).\
            filter(CtfMicrographTable.micrograph_name.startswith(frame_prefix)).all()
            
            frame_mic_ids = [each_frame_mic.id for each_frame_mic in frame_mics]

            frame_segments = session.query(SegmentTable).\
            filter(SegmentTable.picked_x_coordinate_A == segment.picked_x_coordinate_A).\
            filter(SegmentTable.mic_id.in_(frame_mic_ids)).order_by(SegmentTable.helix_id).all()
            
            helix_ids.append([each_frame_segment.helix_id for each_frame_segment in frame_segments])

        return helix_ids


    def average_shifts_between_frames_along_helix(self, x_shifts, window_size):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> shifts = [[each_frame] * 20 for each_frame in list(range(10))]
        >>> shifts = [list(range(each_frame, each_frame + 12)) for each_frame in list(range(10))]
        >>> shifts = np.array(shifts) ** 2
        >>> shifts
        array([[  0,   1,   4,   9,  16,  25,  36,  49,  64,  81, 100, 121],
               [  1,   4,   9,  16,  25,  36,  49,  64,  81, 100, 121, 144],
               [  4,   9,  16,  25,  36,  49,  64,  81, 100, 121, 144, 169],
               [  9,  16,  25,  36,  49,  64,  81, 100, 121, 144, 169, 196],
               [ 16,  25,  36,  49,  64,  81, 100, 121, 144, 169, 196, 225],
               [ 25,  36,  49,  64,  81, 100, 121, 144, 169, 196, 225, 256],
               [ 36,  49,  64,  81, 100, 121, 144, 169, 196, 225, 256, 289],
               [ 49,  64,  81, 100, 121, 144, 169, 196, 225, 256, 289, 324],
               [ 64,  81, 100, 121, 144, 169, 196, 225, 256, 289, 324, 361],
               [ 81, 100, 121, 144, 169, 196, 225, 256, 289, 324, 361, 400]])
        >>> avg_shifts = s.average_shifts_between_frames_along_helix(shifts.tolist(), 3)
        >>> np.int64(avg_shifts)
        array([[ -6,   1,   4,   9,  16,  25,  36,  48,  63,  80,  99, 123],
               [ -3,   4,   9,  16,  25,  36,  48,  63,  80,  99, 120, 146],
               [  0,   9,  16,  25,  36,  49,  63,  80,  99, 120, 143, 170],
               [  6,  16,  25,  36,  49,  64,  81,  99, 121, 143, 168, 196],
               [ 15,  25,  36,  49,  64,  81, 100, 121, 144, 169, 195, 225],
               [ 25,  36,  48,  63,  81, 100, 121, 144, 169, 196, 225, 255],
               [ 38,  49,  63,  80,  99, 121, 144, 169, 196, 225, 256, 288],
               [ 52,  63,  80,  99, 120, 144, 169, 196, 225, 256, 289, 322],
               [ 68,  80,  99, 120, 143, 168, 196, 225, 256, 289, 324, 358],
               [ 87, 100, 120, 143, 168, 195, 225, 256, 289, 324, 361, 397]])
        """
        x_shifts = np.vstack(x_shifts)

        helix_length = len(x_shifts[0])
        avg_x_shifts = np.copy(x_shifts)
        for each_segment in list(range(helix_length)):
            avg_x_shifts[:,each_segment]=np.average(x_shifts[:,each_segment])
        
        x_shift_diffs = x_shifts - avg_x_shifts

        avg_x_shift_diffs = np.zeros(x_shifts.shape)
        for each_id, each_frame in enumerate(x_shift_diffs):
            avg_x_shift_diffs[each_id] = SegmentSelect().compute_local_average_from_measurements(each_frame, window_size)
        
        helix_avg_x_shifts = avg_x_shifts + avg_x_shift_diffs

        return helix_avg_x_shifts


    def perform_local_averaging_across_frames(self, session, ref_session, helix_ids):
        if len(helix_ids) > 0:
            segments = session.query(SegmentTable).filter(SegmentTable.helix_id == helix_ids[0][0]).all()
            distance = np.average(np.diff([each_segment.distance_from_start_A for each_segment in segments]))
            window_size = int(round(self.frame_local_avg_dstnce / distance))

            ref_segments = ref_session.query(RefinementCycleSegmentTable).all()

            for each_helix_ids in helix_ids:
                x_shifts = []
                y_shifts = []
                stack_ids = []
                for each_helix_id in each_helix_ids:
                    segments = session.query(SegmentTable).filter(SegmentTable.helix_id == each_helix_id).all()
                    hel_stack_ids = [each_segment.stack_id for each_segment in segments]
                    
                    ref_helix_segments = [each_ref_segment for each_ref_segment in ref_segments \
                                          if each_ref_segment.stack_id in hel_stack_ids]
                    
                    stack_ids.append(hel_stack_ids)
                    x_shifts.append([each_ref_segment.shift_x_A for each_ref_segment in ref_helix_segments])
                    y_shifts.append([each_ref_segment.shift_y_A for each_ref_segment in ref_helix_segments])
            
                stack_ids = np.vstack(stack_ids)
    
                x_shifts = self.average_shifts_between_frames_along_helix(x_shifts, window_size)
                y_shifts = self.average_shifts_between_frames_along_helix(y_shifts, window_size)
            
            stack_ids = stack_ids.ravel()
            x_shifts = x_shifts.ravel()
            y_shifts = y_shifts.ravel()
        else:
            stack_ids = []
            x_shifts = []
            y_shifts = []

        return stack_ids, x_shifts, y_shifts


    def sort_and_enter_averaged_shifts(self, ref_session, shift_info):
        stack_iids, x_shifts, y_shifts = shift_info

        argsort_ids = np.argsort(stack_iids)
        shift_info = zip(stack_iids[argsort_ids], x_shifts[argsort_ids], y_shifts[argsort_ids])

        for each_stack_id, each_x_shift, each_y_shift in shift_info:
            ref_segment = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.stack_id == int(each_stack_id)).first()

            ref_segment.shift_x_A = each_x_shift
            ref_segment.shift_y_A = each_y_shift
            ref_session.merge(ref_segment)
        
        ref_session.commit()


    def perform_local_frame_averaging_and_ref_database_update(self, spring_db, ref_db, ref_session):
        if self.frame_motion_corr and self.frame_local_avg_dstnce > 0:
            session = SpringDataBase().setup_sqlite_db(base, spring_db)
            helix_ids = self.get_helices_from_corresponding_frames(session, ref_session)
            shift_info = self.perform_local_averaging_across_frames(session, ref_session, helix_ids)
            self.sort_and_enter_averaged_shifts(ref_session, shift_info)


    def get_selected_alignment_parameters_from_last_cycle(self, ref_cycle_id, model_id, rank):
        temp_ref_db = self.copy_ref_db_to_tempdir(ref_cycle_id)
        ref_session = SpringDataBase().setup_sqlite_db(refine_base, temp_ref_db)
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
        if rank is None:
            selected_ref_segments = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
            filter(RefinementCycleSegmentTable.model_id == model_id).\
            filter(RefinementCycleSegmentTable.selected == True).all()
        elif rank is not None:
            selected_ref_segments = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
            filter(RefinementCycleSegmentTable.model_id == model_id).\
            filter(RefinementCycleSegmentTable.rank_id == rank).\
            filter(RefinementCycleSegmentTable.selected == True).all()
            
        ref_session.close()
        os.remove(temp_ref_db)
        
        return selected_ref_segments
    
    
    def update_total_nonorientation_counts_in_ref_db(self, ref_cycle_id, spring_db, ref_session):
        included_segments_non_orientation, excluded_non_orientation_counts = \
        SegmentSelect().filter_non_orientation_parameters_based_on_selection_criteria(self, spring_db,
        keep_helices_together=False)
        
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()

        last_cycle.excluded_mic_count = excluded_non_orientation_counts.mic_count
        last_cycle.excluded_helix_count = excluded_non_orientation_counts.helix_count
        last_cycle.excluded_class_count = excluded_non_orientation_counts.class_count
        last_cycle.excluded_curvature_count = excluded_non_orientation_counts.curvature_count
        last_cycle.excluded_defocus_count = excluded_non_orientation_counts.defocus_count
        last_cycle.excluded_astigmatism_count = excluded_non_orientation_counts.astig_count
        last_cycle.excluded_layer_cc_count = excluded_non_orientation_counts.layer_cc_count
        last_cycle.excluded_helix_ends_count = 0

        ref_session.merge(last_cycle)
        ref_session.commit()
        ref_session.close()


    def prepare_refined_alignment_parameters_from_database(self, ref_cycle_id, pixelsize, unbending, reference_files,
    rank=None):
        comb_orientation_parameters = []
        for each_reference in reference_files:
            selected_ref_segments = self.get_selected_alignment_parameters_from_last_cycle(ref_cycle_id,
            each_reference.model_id, rank)
            
            orientation_parameters = []
            rec_parameters = SegClassReconstruct().make_named_tuple_for_reconstruction()
            for each_segment in selected_ref_segments:
                if unbending:
                    orientation_parameters.append(rec_parameters(each_segment.stack_id, each_segment.local_id,
                    each_segment.phi, each_segment.theta, each_segment.psi, each_segment.unbent_shift_x_A / pixelsize,
                    each_segment.unbent_shift_y_A / pixelsize, each_segment.unbent_ip_angle, each_segment.mirror,
                    each_segment.id))
                else:
                    orientation_parameters.append(rec_parameters(each_segment.stack_id, each_segment.local_id,
                    each_segment.phi, each_segment.theta, each_segment.psi, each_segment.shift_x_A / pixelsize,
                    each_segment.shift_y_A / pixelsize, each_segment.inplane_angle, each_segment.mirror, each_segment.id))
            
            comb_orientation_parameters.append(orientation_parameters)
        
        return comb_orientation_parameters
        
    
    def select_segments_based_on_specified_criteria(self, orientation_parameters, unbending_info,
    current_translation_step, ref_cycle_id, each_info, pixelinfo, reference_files):
    
        ref_session, temp_ref_db, ccc_proj_range_vals = self.prepare_databases_for_selection(orientation_parameters,
        unbending_info, current_translation_step, ref_cycle_id, each_info, pixelinfo)
        
        temp_db = self.copy_spring_db_to_tempdir()
        self.perform_local_frame_averaging_and_ref_database_update(temp_db, temp_ref_db, ref_session)
            
        ref_session = self.perform_helix_based_computations_and_selection(each_info, temp_db, ref_session,
        ccc_proj_range_vals)
        
        self.update_total_nonorientation_counts_in_ref_db(ref_cycle_id, temp_db, ref_session)

        os.remove(temp_db)
        shutil.copy(temp_ref_db, 'refinement{0:03}.db'.format(ref_cycle_id))
        os.remove(temp_ref_db)
        
        selected_parameters = self.prepare_refined_alignment_parameters_from_database(ref_cycle_id, pixelinfo.pixelsize,
        self.unbending, reference_files)
        
        return selected_parameters