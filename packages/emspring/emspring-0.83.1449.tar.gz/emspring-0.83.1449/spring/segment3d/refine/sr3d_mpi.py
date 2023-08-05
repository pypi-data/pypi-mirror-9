# Author: Carsten Sachse 18-Aug-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from EMAN2 import EMUtil, EMData
from collections import namedtuple
import os
import shutil
from spring.csinfrastr.csdatabase import SpringDataBase, base, HelixTable, SegmentTable, RefinementCycleSegmentTable, \
    refine_base, RefinementCycleHelixTable, RefinementCycleTable
from spring.csinfrastr.csproductivity import OpenMpi, Temporary
from spring.segment2d.segmentalign2d_mpi import SegmentAlign2dMpi
from spring.segment2d.segmentselect import SegmentSelect
from spring.segment3d.refine.sr3d_main import SegmentRefine3dPar, SegmentRefine3d
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from utilities import model_blank

from sqlalchemy.sql.expression import desc

import numpy as np


class SegmentRefine3dMpiDatabase(SegmentRefine3d):

    def copy_one_entry_from_one_session_to_local_session_by_id(self, session, table, local_session, columns,
    each_entry_id):
        each_entry = session.query(table).get(each_entry_id)
#         SpringDataBase().copy_search_result_to_another_database(table, local_session, [each_entry])
        data = SpringDataBase().get_data_from_entry(columns, each_entry)

        local_session.add(table(**data))
        
        return session, local_session
    

    def select_segment_ids_and_corresponding_helices_from_spring_db(self, session, temp_db):
        included_segments_non_orientation, excluded_non_orientation_counts =\
        SegmentSelect().filter_non_orientation_parameters_based_on_selection_criteria(self, temp_db,
        keep_helices_together=True)
        
        segments = session.query(SegmentTable).order_by(SegmentTable.id).all()
        seg_ids_per_helix = []
        segment_ids = []
        current_helix_id = 1
        helix_ids = []
        for each_segment in segments:
            if each_segment.stack_id in included_segments_non_orientation:
                if current_helix_id != each_segment.helix_id:
                    helix_ids.append(current_helix_id)
                    current_helix_id = each_segment.helix_id
                    seg_ids_per_helix.append(segment_ids)
                    segment_ids = []
                segment_ids.append(each_segment.id)
        
        helix_ids.append(current_helix_id)
        seg_ids_per_helix.append(segment_ids)
        
        return seg_ids_per_helix, helix_ids


    def create_new_spring_db_with_specified_ids(self, session, seg_ids_per_helix, helix_ids, spring_db):
        local_session = SpringDataBase().setup_sqlite_db(base, spring_db)
        hel_columns = SpringDataBase().get_columns_from_table(HelixTable)
        for each_helix_id in helix_ids:
            session, local_session = self.copy_one_entry_from_one_session_to_local_session_by_id(session, HelixTable, 
                local_session, hel_columns, each_helix_id)
        
        seg_columns = SpringDataBase().get_columns_from_table(SegmentTable)
        seg_ids = [each_seg_id for helix_seg_ids in seg_ids_per_helix for each_seg_id in helix_seg_ids]
        for each_seg_id in seg_ids:
            session, local_session = self.copy_one_entry_from_one_session_to_local_session_by_id(session, SegmentTable, 
                local_session, seg_columns, each_seg_id)
        
        local_session.commit()
        
        return seg_ids


    def split_spring_db_according_to_helix_entities_to_local_db(self):
        
        temp_db = self.copy_spring_db_to_tempdir()
        session = SpringDataBase().setup_sqlite_db(base, temp_db)
        if self.rank == 0:
            seg_ids_per_helix, helix_ids = self.select_segment_ids_and_corresponding_helices_from_spring_db(session,
            temp_db)
            
            seg_ids_per_helix = OpenMpi().split_sequence_evenly(seg_ids_per_helix, self.size)
            helix_ids = OpenMpi().split_sequence_evenly(helix_ids, self.size)
        else:
            seg_ids_per_helix = None
            helix_ids = None
            
        seg_ids_per_helix = self.comm.scatter(seg_ids_per_helix, root=0)
        helix_ids = self.comm.scatter(helix_ids, root=0)
        self.comm.barrier()
        
        if helix_ids != []:
            spring_db = os.path.join(self.tempdir, 'spring.db')
            seg_ids = self.create_new_spring_db_with_specified_ids(session, seg_ids_per_helix, helix_ids, spring_db)
        else:
            spring_db = None
            seg_ids = []
        
        all_seg_ids = self.comm.gather(seg_ids, root=0)
        if self.rank == 0:
            new_continuous_list = []
            continuous_id = 1
            for each_rank_list in all_seg_ids:
                rank_list = []
                for each_image in each_rank_list:
                    rank_list.append(continuous_id)
                    continuous_id += 1
                new_continuous_list.append(rank_list)
        else:
            new_continuous_list = None
        
        self.comm.barrier()
        updated_seg_ids = self.comm.scatter(new_continuous_list, root=0)
                    
        self.comm.barrier()
        session.close()
        os.remove(temp_db)
                
        return spring_db, updated_seg_ids
        
        
    def split_refinement_db_according_to_seg_ids(self, seg_ids, ref_db):
        ref_session = SpringDataBase().setup_sqlite_db(refine_base, ref_db)
        local_ref_db = '_{0:03}'.format(self.rank).join(os.path.splitext(ref_db)) #os.path.join(self.tempdir, ref_db)
        local_ref_session = SpringDataBase().setup_sqlite_db(refine_base, local_ref_db)
        
        ref_cycles = ref_session.query(RefinementCycleTable).order_by(RefinementCycleTable.id).all()
        cycle_columns = SpringDataBase().get_columns_from_table(RefinementCycleTable)
        for each_ref_cycle in ref_cycles:
            ref_session, local_ref_session = self.copy_one_entry_from_one_session_to_local_session_by_id(ref_session,
            RefinementCycleTable, local_ref_session, cycle_columns, each_ref_cycle.id)
        
        ref_columns = SpringDataBase().get_columns_from_table(RefinementCycleSegmentTable)
        for each_seg_id in seg_ids:
            ref_session, local_ref_session = self.copy_one_entry_from_one_session_to_local_session_by_id(ref_session,
            RefinementCycleSegmentTable, local_ref_session, ref_columns, each_seg_id)
            
        local_ref_session.commit()
        
        return local_ref_session, local_ref_db    
        
            
    def transfer_records_from_local_table_to_global(self, ref_columns, table, ref_session, local_ref_session,
    unique_id):
        local_ref_segments = local_ref_session.query(table).order_by(table.id).all()
        for each_ref_segment in local_ref_segments:
            data = SpringDataBase().get_data_from_entry(ref_columns, each_ref_segment)
            if unique_id is True:
                data['id']=None
            ref_session.merge(table(**data))
        
        return ref_session
    

    def merge_local_db_table_entries_to_single_db(self, local_dbs, table, db_base, single_db, unique_id=True):
        seg_columns = SpringDataBase().get_columns_from_table(table)
        session = SpringDataBase().setup_sqlite_db(db_base, single_db)
        for each_local_db in local_dbs:
            temp_local_db = '_{0:03}'.format(self.rank).join(os.path.splitext(each_local_db)) #os.path.join(self.tempdir, each_local_db)
            shutil.copy(each_local_db, temp_local_db)
            local_session = SpringDataBase().setup_sqlite_db(db_base, temp_local_db)
            
            session = self.transfer_records_from_local_table_to_global(seg_columns, table, session, local_session,
            unique_id)
            
            local_session.close()
            os.remove(temp_local_db)
        
        session.commit()
        

    def merge_local_entries_from_spring_db(self, local_spring_db):
#         local_spring_db = os.path.join(self.tempdir, 'spring.db')
        if local_spring_db is not None:
            local_cp_spring_db = 'spring_{0:03}.db'.format(self.rank)
            shutil.copy(local_spring_db, local_cp_spring_db)
        else:
            local_cp_spring_db = None
            
        local_dbs = self.comm.gather(local_cp_spring_db, root=0)
            
        if self.rank == 0:
            local_dbs = [each_db for each_db in local_dbs if each_db is not None]
            local_temp_dbs = [os.path.join(self.tempdir, each_db) for each_db in local_dbs]
            [shutil.move(each_db, each_temp_db) for each_db, each_temp_db in zip(local_dbs, local_temp_dbs)]
            temp_db = self.copy_spring_db_to_tempdir()
            self.merge_local_db_table_entries_to_single_db(local_temp_dbs, SegmentTable, base, temp_db, unique_id=False)
            shutil.copy(temp_db, 'spring.db')
            os.remove(temp_db)
            local_temp_dbs = [os.remove(each_db) for each_db in local_temp_dbs]
            
        self.comm.barrier()


    def merge_local_entries_from_refinement_segment_and_refinement_helix_table(self, ref_cycle_id, local_ref_cycle_db):
        if local_ref_cycle_db is not None:
            local_ref_cp_cycle_db = 'refinement{0:03}_{1:03}.db'.format(ref_cycle_id, self.rank)
            shutil.move(local_ref_cycle_db, local_ref_cp_cycle_db)
        else:
            local_ref_cp_cycle_db = None
        
        global_ref_db = os.path.join(self.tempdir, 'refinement_global{0:03}.db'.format(ref_cycle_id))
        local_dbs = self.comm.gather(local_ref_cp_cycle_db, root=0)
        self.comm.barrier()
        if self.rank == 0:
            local_dbs = [each_db for each_db in local_dbs if each_db is not None]
            local_temp_dbs = [os.path.join(self.tempdir, each_db) for each_db in local_dbs]
            [shutil.move(each_db, each_temp_db) for each_db, each_temp_db in zip(local_dbs, local_temp_dbs)]

            self.merge_local_db_table_entries_to_single_db(local_temp_dbs, RefinementCycleSegmentTable, refine_base,
            global_ref_db)
            
            self.merge_local_db_table_entries_to_single_db(local_temp_dbs, RefinementCycleHelixTable, refine_base,
            global_ref_db)
        else:
            local_temp_dbs = None
        self.comm.barrier()
        
        return global_ref_db, local_temp_dbs


    def merge_and_reduce_local_entries_from_refinement_cycle_table(self, global_ref_db, local_dbs):
        if self.rank == 0:
            first_existing_db = local_dbs[0]
            
            self.merge_local_db_table_entries_to_single_db([first_existing_db], RefinementCycleTable, refine_base,
            global_ref_db)
            
            self.log.ilog('Header and cycle information was copied from split refinement file ' +\
            '{0}'.format(first_existing_db))
            
            count_criteria_to_be_summed = [
                'excluded_helix_shift_x_count', 'excluded_prj_cc_count', 'excluded_layer_cc_count', 
                'excluded_defocus_count', 'excluded_phi_count', 'excluded_helix_ends_count', 
                'excluded_out_of_plane_tilt_count', 'excluded_inplane_count', 
                'total_excluded_count', 'segment_count']
            
            ref_session = SpringDataBase().setup_sqlite_db(refine_base, global_ref_db)
            for each_count in count_criteria_to_be_summed:
                each_count_sum = 0
                for each_db in local_dbs:
                    ref_local_session = SpringDataBase().setup_sqlite_db(refine_base, each_db)
                    
                    last_cycle =\
                    ref_local_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
                    
                    if getattr(last_cycle, each_count) is not None:
                        each_count_sum += getattr(last_cycle, each_count)
                    ref_local_session.close()
                
                last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
                if getattr(last_cycle, each_count) is not None:
                    setattr(last_cycle, each_count, each_count_sum)
            
            ref_session.merge(last_cycle)
            included_counts = []
            peaks = []
            for each_db in local_dbs:
                ref_local_session = SpringDataBase().setup_sqlite_db(refine_base, each_db)
                last_cycle = ref_local_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
                if last_cycle.mean_peak is not None:
                    included_counts.append(last_cycle.segment_count - last_cycle.total_excluded_count)
                    peaks.append(last_cycle.mean_peak)
                ref_local_session.close()
            
            last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
            if peaks != []:
                last_cycle.mean_peak = np.average(peaks, weights=included_counts)
            ref_session.merge(last_cycle)
            ref_session.commit()
            
        self.comm.barrier()
        if self.rank == 0:
            [os.remove(each_db) for each_db in local_dbs]
            shutil.move(global_ref_db, 'refinement{0:03}.db'.format(last_cycle.id))
            

    def merge_local_db_into_global_databases(self, ref_cycle_id, spring_db, local_ref_db):
        self.merge_local_entries_from_spring_db(spring_db)
        
        global_ref_db, local_dbs = \
        self.merge_local_entries_from_refinement_segment_and_refinement_helix_table(ref_cycle_id, local_ref_db)
        
        self.merge_and_reduce_local_entries_from_refinement_cycle_table(global_ref_db, local_dbs)
        
        
class SegmentRefine3dMpiBinning(SegmentRefine3dMpiDatabase):
    def prepare_pre_cycle_setup_mpi(self):
        required_byte, info_series = self.estimate_required_tmp_disk_space()
        
        self.comm, self.rank, self.size, self.log, self.tempdir = OpenMpi().setup_mpi_and_simultaneous_logging(self.log,
        self.feature_set.logfile, self.temppath, required_byte)
        
        if self.rank == 0:
            large_segment_stack, masked_segment_stack, complete_image_list, reference_files, lambda_sirt,\
            start_ref_cycle_id = self.pre_cycle_setup(info_series)
            reference_files = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(reference_files)
            
            image_list = OpenMpi().split_sequence_evenly(complete_image_list, self.size)
        else:
            reference_files = None
            large_segment_stack = None
            masked_segment_stack = None
            lambda_sirt = None
            start_ref_cycle_id = None
            image_list = None
            self.polar_helix = None
            self.curvature_range = None
            self.ccc_layer_range = None
            
        self.comm.barrier()
        self.curvature_range = self.comm.bcast(self.curvature_range, root=0)
        self.ccc_layer_range = self.comm.bcast(self.ccc_layer_range, root=0)
        
        reference_files = self.comm.bcast(reference_files, root=0)
        self.polar_helix = self.comm.bcast(self.polar_helix, root=0)

        reference_files = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(reference_files,
        self.make_reference_info_named_tuple())

        large_segment_stack = self.comm.bcast(large_segment_stack, root=0)
        masked_segment_stack = self.comm.bcast(masked_segment_stack, root=0)
        lambda_sirt = self.comm.bcast(lambda_sirt, root=0)
        start_ref_cycle_id = self.comm.bcast(start_ref_cycle_id, root=0)
        image_list = self.comm.scatter(image_list, root=0)
        masked_segment_stack = os.path.join(self.tempdir, masked_segment_stack)
        
        return info_series, reference_files, image_list, masked_segment_stack, large_segment_stack, lambda_sirt, \
        start_ref_cycle_id, required_byte


    def mask_and_window_and_unbend_if_required_mpi(self, masked_segment_stack, large_segment_stack,
    each_iteration_number, ref_cycle_id, previous_params, mask_params, info_series, each_index, unbending_info,
    large_straightened_stack, pixelinfo):
        if not self.unbending and each_iteration_number == 1 or \
        not self.unbending and self.layer_line_filter:
            masked_segment_stack, large_segment_stack, large_straightened_stack = \
            self.window_and_mask_input_stack(large_segment_stack, pixelinfo, mask_params,
            masked_segment_stack, info_series[each_index], ref_cycle_id)
            
        elif self.unbending and each_iteration_number == 1:
            spring_db, seg_ids = self.split_spring_db_according_to_helix_entities_to_local_db()
            if spring_db is not None:
                ref_db = 'refinement{0:03}.db'.format(ref_cycle_id - 1)
                if os.path.exists(ref_db):
                    temp_ref_db = self.copy_ref_db_to_tempdir(ref_cycle_id - 1)
                    ref_session, local_ref_db = self.split_refinement_db_according_to_seg_ids(seg_ids, temp_ref_db)
            
                helices_coordinates, cut_coordinates = \
                self.get_helices_coordinates_required_for_unbending_from_database(ref_cycle_id - 1,
                info_series[each_index].bin_factor, info_series, large_segment_stack, pixelinfo.pixelsize, spring_db)
                
                os.remove(spring_db)
                if os.path.exists(ref_db):
                    os.remove(temp_ref_db)
                    os.remove(local_ref_db)
        
                cut_coordinates = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(cut_coordinates)
                helices_coordinates = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(helices_coordinates)
            else:
                helices_coordinates = []
                cut_coordinates = []
            
            self.comm.barrier()
            helices_coordinates = self.comm.gather(helices_coordinates, root=0)
            cut_coordinates = self.comm.gather(cut_coordinates, root=0)
            
            if self.rank == 0:
                cut_coordinates = OpenMpi().merge_sequence_of_sequences(cut_coordinates)
                helices_coordinates = OpenMpi().merge_sequence_of_sequences(helices_coordinates)
                cut_coordinates = OpenMpi().split_sequence_evenly(cut_coordinates, self.size)
            else:
                helices_coordinates = None
                cut_coordinates = None
            
            helices_coordinates = self.comm.bcast(helices_coordinates, root=0)
            cut_coordinates = self.comm.scatter(cut_coordinates, root=0)
            
            cut_coordinates = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(cut_coordinates,
            self.get_cut_coordinates_named_tuple())
            
            helices_coordinates = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(helices_coordinates, 
            self.get_helix_coordinates_named_tuple())
            
            previous_params, unbending_info, masked_segment_stack, large_segment_stack, large_straightened_stack = \
            self.unbend_window_and_mask_input_stack(large_segment_stack, ref_cycle_id, pixelinfo,
            previous_params, mask_params, helices_coordinates, cut_coordinates, masked_segment_stack,
            info_series[each_index].resolution_aim)
            
        self.comm.barrier()
        
        return masked_segment_stack, previous_params, unbending_info, large_segment_stack, large_straightened_stack


    def perform_binning_mpi(self, info_series, reference_files, ori_large_segment_stack, ori_reference_file,
    ori_reconstruction_size, ori_helixwidthpix, ori_pixelsize, each_index, image_list, ref_cycle_id):
        
        large_segment_stack, segment_size_pix, helixwidthpix = \
        self.bin_including_copies_of_frames_if_requested(image_list, ori_large_segment_stack, ori_reconstruction_size,
        ori_helixwidthpix, ori_pixelsize, info_series[each_index])
            
        if self.rank == 0:
            reference_files, ctf3d_avg_squared, pixelinfo = self.precycle_setup_before_binning(info_series,
            large_segment_stack, reference_files, ori_reference_file, ori_pixelsize, each_index, ref_cycle_id,
            segment_size_pix, helixwidthpix)
            
            if reference_files[0].fsc is not None:
                fsc_lines = [list(each_reference.fsc) for each_reference in reference_files]
            else:
                fsc_lines = 4 * [None]

            reference_files = [each_reference._replace(fsc=None) for each_reference in reference_files]
            reference_files = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(reference_files)
            pixelinfo = list(pixelinfo)
        else:
            ctf3d_avg_squared = None
            reference_files = None
            fsc_lines = None
            pixelinfo = None
        
        reference_files = self.comm.bcast(reference_files, root=0)
        pixelinfo = self.comm.bcast(pixelinfo, root=0)
        fsc_lines = self.comm.bcast(fsc_lines, root=0)
        
        reference_files = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(reference_files,
        self.make_reference_info_named_tuple())
            
        if fsc_lines[0] is not None:
            fsc_lines = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(fsc_lines,
            self.make_fsc_line_named_tuple())

            for each_model_id, each_fsc in enumerate(fsc_lines):
                reference_files[each_model_id] = reference_files[each_model_id]._replace(fsc=each_fsc)
            
        pixelinfo = self.make_pixel_info_named_tuple()._make(pixelinfo)
            
        self.comm.barrier()
        
        return reference_files, large_segment_stack, ctf3d_avg_squared, pixelinfo
    

class SegmentRefine3dMpiProjection(SegmentRefine3dMpiBinning):

    def generate_projection_stack_mpi(self, resolution_aim, cycle_number, reference_volume, pixelinfo,
    azimuthal_angle_count, out_of_plane_tilt_angle_count, projection_stack, helical_symmetry, rotational_sym):
        if self.rank == 0:
            projection_parameters = self.generate_Euler_angles_for_projection(azimuthal_angle_count,
            self.out_of_plane_tilt_angle_range, out_of_plane_tilt_angle_count, helical_symmetry[1])
            
            local_prj_ids = list(range(len(projection_parameters)))
            local_projection_parameters = OpenMpi().split_sequence_evenly(projection_parameters, self.size)
            local_prj_ids = OpenMpi().split_sequence_evenly(local_prj_ids, self.size)
        else:
            projection_parameters = None
            local_projection_parameters = None
            local_prj_ids = None
            
        local_projection_parameters = self.comm.scatter(local_projection_parameters, root=0)
        local_prj_ids = self.comm.scatter(local_prj_ids, root=0)
        local_projection_stack = os.path.join(self.tempdir, projection_stack)
        
        if local_prj_ids != []:
            SegClassReconstruct().project_through_reference_using_parameters_and_log(local_projection_parameters,
            pixelinfo.alignment_size, local_prj_ids, local_projection_stack, reference_volume)
            
            self.filter_layer_lines_if_demanded(resolution_aim, local_projection_parameters, local_prj_ids,
            local_projection_stack, pixelinfo, helical_symmetry, rotational_sym)
            
        OpenMpi().gather_stacks_from_cpus_to_common_stack(self.comm, local_projection_stack, projection_stack)
        projection_parameters = self.comm.bcast(projection_parameters, root=0)
        self.comm.barrier()
        
        first_local_tempdir = OpenMpi().get_first_local_tempdir(self.comm, self.tempdir)

        local_projection_stack = os.path.join(first_local_tempdir, projection_stack)
        if first_local_tempdir == self.tempdir:
            self.copy_image_stack_to_new_stack(projection_stack, local_projection_stack)
        self.comm.barrier()
        
        if self.rank == 0:
            self.remove_intermediate_files_if_desired(projection_stack)

        return local_projection_stack, projection_parameters
    

    def check_for_each_node_wether_sufficient_temporary_disk_space_available(self, required_byte):
        local_job_count, this_node, unique_nodes = OpenMpi().get_job_current_count_on_this_node(self.comm)
        
        total_byte_on_node = required_byte
        for each_node in unique_nodes:
            if each_node == this_node:
                Temporary().check_available_space_in_temppath_and_raise_error_if_not_enough_space_available(self.temppath,
                total_byte_on_node)
                
            self.comm.barrier()
            

    def project_including_masking_and_filtering_mpi(self, each_info, reference_files, each_iteration_number,
    ref_cycle_id, info_series, required_byte, pixelinfo):
         
        self.check_for_each_node_wether_sufficient_temporary_disk_space_available(required_byte)
        
        updated_ref_files = []
        merged_prj_params = []
        merged_fine_prj_params = []

        if self.resume_refinement_option and not self.reference_option and each_iteration_number == 1:
            merged_prj_stack = None
            merged_prj_fine_stack = None
            updated_ref_files = reference_files
        else:
            for each_reference in reference_files:
                if self.rank == 0:
                    reference_volume = self.filter_and_mask_reference_volume(each_info.resolution_aim, each_reference,
                    pixelinfo, each_reference.fsc)
        
                    each_reference, prj_prefix = \
                    self.write_out_reference_and_get_prj_prefix_depending_on_number_of_models(reference_files, ref_cycle_id,
                    each_iteration_number, each_reference, reference_volume)
                    
                    if each_reference.fsc is not None:
                        fsc_lines = list(each_reference.fsc)
                    else:
                        fsc_lines = None
                    each_reference = list(each_reference._replace(fsc=None))
        
                else:
                    each_reference = None
                    prj_prefix = None
                    fsc_lines = None
                    
                each_reference = self.comm.bcast(each_reference, root=0)
                prj_prefix = self.comm.bcast(prj_prefix, root=0)
                fsc_lines = self.comm.bcast(fsc_lines, root=0)
                
                each_reference = self.make_reference_info_named_tuple()._make(each_reference)
                if fsc_lines is not None:
                    each_reference = each_reference._replace(fsc=self.make_fsc_line_named_tuple()._make(fsc_lines))
        
                self.comm.barrier()
        
                projection_stack, projection_parameters, fine_projection_stack, fine_projection_parameters = \
                self.project_through_reference_volume_in_helical_perspectives(each_info.resolution_aim, ref_cycle_id,
                each_reference.ref_file, pixelinfo, each_reference.helical_symmetry, each_reference.rotational_symmetry,
                prj_prefix)
                
                updated_ref_files, merged_prj_params, merged_fine_prj_params = \
                self.collect_prj_params_and_update_reference_info(updated_ref_files, each_reference, projection_stack,
                projection_parameters, fine_projection_stack, fine_projection_parameters, merged_prj_params,
                merged_fine_prj_params)
            
            self.comm.barrier()
            merged_prj_stack = self.merge_prj_ref_stacks_into_single_prj_stack(updated_ref_files, 'prj_stack')
            merged_prj_fine_stack = self.merge_prj_ref_stacks_into_single_prj_stack(updated_ref_files, 'fine_prj_stack')

        self.comm.barrier()
        if self.rank == 0:
            previous_params, mask_params = \
            self.prepare_previous_parameters_either_from_inplane_angle_or_from_previous_cycle(each_info, info_series,
            ref_cycle_id, each_iteration_number, reference_files)
            
            previous_params = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(previous_params)
            previous_params = OpenMpi().split_sequence_evenly(previous_params, self.size)
            
            mask_params = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(mask_params)
            mask_params = OpenMpi().split_sequence_evenly(mask_params, self.size)
        else:
            previous_params = None
            mask_params = None
        
        previous_params = self.comm.scatter(previous_params, root=0)
        mask_params = self.comm.scatter(mask_params, root=0)
        
        previous_params = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(previous_params,
        self.make_named_tuple_of_orientation_parameters())

        previous_params = [each_item._replace(rank_id = self.rank) for each_item in previous_params]

        mask_params = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(mask_params,
        self.make_named_tuple_of_masking_parameters())
            
        previous_params = SegmentAlign2dMpi().update_local_ids_in_list_of_named_tuple(previous_params)
        mask_params = SegmentAlign2dMpi().update_local_ids_in_list_of_named_tuple(mask_params)
        
        self.comm.barrier() 
        
        prj_info = self.package_parameters_and_stack_name_into_prj_info(merged_prj_params, merged_fine_prj_params,
        merged_prj_stack, merged_prj_fine_stack)
        
        return mask_params, previous_params, prj_info, updated_ref_files

        
class SegmentRefine3dMpiSelect(SegmentRefine3dMpiProjection):

    def perform_local_frame_averaging_and_ref_database_update_mpi(self, ref_cycle_id):
        if self.frame_motion_corr and self.frame_local_avg_dstnce > 0:
            temp_db = self.copy_spring_db_to_tempdir()
            session = SpringDataBase().setup_sqlite_db(base, temp_db)

            ref_db = self.copy_ref_db_to_tempdir(ref_cycle_id)
            ref_session = SpringDataBase().setup_sqlite_db(refine_base, ref_db)
            if self.rank == 0:
                helix_ids = self.get_helices_from_corresponding_frames(session, ref_session)
                helix_ids = OpenMpi().split_sequence_evenly(helix_ids, self.size)
            else:
                helix_ids = None
                
            helix_ids = self.comm.scatter(helix_ids, root=0)
                
            stack_ids, x_shifts, y_shifts = self.perform_local_averaging_across_frames(session, ref_session, helix_ids)
            stack_ids = self.comm.gather(stack_ids, root=0)
            x_shifts = self.comm.gather(x_shifts, root=0)
            y_shifts = self.comm.gather(y_shifts, root=0)
            
            if self.rank == 0:
                stack_ids = OpenMpi().merge_sequence_of_sequences(stack_ids)
                x_shifts = OpenMpi().merge_sequence_of_sequences(x_shifts)
                y_shifts = OpenMpi().merge_sequence_of_sequences(y_shifts)

                self.sort_and_enter_averaged_shifts(ref_session, 
                (np.array(stack_ids), np.array(x_shifts), np.array(y_shifts)))
                
                shutil.copy(temp_db, 'spring.db')
                shutil.copy(ref_db, 'refinement{0:03}.db'.format(ref_cycle_id))
                
            os.remove(temp_db)
            os.remove(ref_db)


    def select_segments_based_on_specified_criteria_mpi(self, orientation_parameters, unbending_info,
    current_translation_step, ref_cycle_id, each_info, pixelinfo, reference_files):
    
        self.log.fcttolog()
        self.log.in_progress_log()
        
        orientation_parameters = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(orientation_parameters)
        orientation_parameters = self.comm.gather(orientation_parameters, root=0)
        if self.rank == 0:
            orientation_parameters = OpenMpi().merge_sequence_of_sequences(orientation_parameters)
            
            orientation_parameters = \
            OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(orientation_parameters,
            self.make_named_tuple_of_orientation_parameters())

            ref_session, temp_current_ref_db, ccc_proj_range_vals = \
            self.prepare_databases_for_selection(orientation_parameters, unbending_info, current_translation_step,
            ref_cycle_id, each_info, pixelinfo)
            
            ref_session.close()
            shutil.copy(temp_current_ref_db, 'refinement{0:03}.db'.format(ref_cycle_id))
            os.remove(temp_current_ref_db)
        else:
            ccc_proj_range_vals = None
        
        self.comm.barrier()
        self.perform_local_frame_averaging_and_ref_database_update_mpi(ref_cycle_id)

        self.comm.barrier()
        ccc_proj_range_vals = self.comm.bcast(ccc_proj_range_vals, root=0)
        spring_db, seg_ids = self.split_spring_db_according_to_helix_entities_to_local_db()
                                                                       
        temp_ref_db = self.copy_ref_db_to_tempdir(ref_cycle_id)
        if seg_ids != []:
            local_ref_session, local_ref_db = self.split_refinement_db_according_to_seg_ids(seg_ids, temp_ref_db)
    
            self.perform_helix_based_computations_and_selection(each_info, spring_db, local_ref_session,
            ccc_proj_range_vals)

            local_ref_session.close()
        else:
            local_ref_db = None

        self.comm.barrier()
        os.remove(temp_ref_db)
        
        self.merge_local_db_into_global_databases(ref_cycle_id, spring_db, local_ref_db)
        if spring_db is not None:
            os.remove(spring_db)
        
        self.comm.barrier()
        if self.rank == 0:
            spring_db = self.copy_spring_db_to_tempdir()
            temp_ref_db = self.copy_ref_db_to_tempdir(ref_cycle_id)
            ref_session = SpringDataBase().setup_sqlite_db(refine_base, temp_ref_db)
            self.update_total_nonorientation_counts_in_ref_db(ref_cycle_id, spring_db, ref_session)
            os.remove(spring_db)
            ref_db = 'refinement{0:03}.db'.format(ref_cycle_id)
            shutil.copy(temp_ref_db, ref_db)
            os.remove(temp_ref_db)

        self.comm.barrier()
        selected_parameters = self.prepare_refined_alignment_parameters_from_database(ref_cycle_id, pixelinfo.pixelsize,
        self.unbending, reference_files, self.rank)
         
        return selected_parameters
        
        
class SegmentRefine3dMpiDiagnostics(SegmentRefine3dMpiSelect):
    
    def get_segment_entries_closest_to_phi_on_rank0_and_broadcast_results(self, ref_session, last_cycle, ref_columns,
    ref_namedtuple, each_phi, each_theta, model_id):
        if self.rank == 0:
            max_cc_segments = self.get_segment_closest_to_given_phi(ref_session, last_cycle, each_theta, each_phi,
            model_id)

            if max_cc_segments is not None:
                max_cc_segments_nt = []
                for each_segment in max_cc_segments:
                    entries = [getattr(each_segment, each_ref_column) for each_ref_column in ref_columns]
                    max_cc_segments_nt.append(ref_namedtuple._make(entries))
                
                max_cc_segments_list = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(max_cc_segments_nt)
            else:
                max_cc_segments_list = None
        else:
            max_cc_segments_list = None
        self.comm.barrier()
        max_cc_segments_list = self.comm.bcast(max_cc_segments_list, root=0)
        
        return max_cc_segments_list


    def gather_images_from_distributed_stacks_or_add_blank(self, large_binned_stack, combined_stack,
    segment_info, segment_prop, ref_namedtuple, max_cc_segments_list, combined_stack_id):
        segment = EMData()
        if max_cc_segments_list is not None:
            max_cc_segments = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(max_cc_segments_list,
            ref_namedtuple)
            
            segment_prj = []
            for each_segment in max_cc_segments:
                if not self.unbending:
                    segment_p = segment_prop(combined_stack_id, each_segment.inplane_angle, each_segment.shift_x_A, 
                        each_segment.shift_y_A, None, None, None, each_segment.peak)
                elif self.unbending:
                    segment_p = segment_prop(combined_stack_id, None, None, None, each_segment.unbent_ip_angle,
                    each_segment.unbent_shift_x_A, each_segment.unbent_shift_y_A, each_segment.peak)
                segment_prj.append(segment_p)
                self.comm.barrier()
                if each_segment.rank_id == self.rank:
                    segment.read_image(large_binned_stack, each_segment.local_id)
                    segment.write_image(combined_stack, combined_stack_id)
                combined_stack_id += 1
                self.comm.barrier()
            
            segment_info.append(segment_prj)
        else:
            if self.rank == 0:
                segment.read_image(large_binned_stack)
                blank = model_blank(segment.get_xsize(), segment.get_ysize(), 1)
                blank.write_image(combined_stack, combined_stack_id)
                combined_stack_id += 1
            segment_info.append(None)

        return segment_info, combined_stack_id
    

    def collect_selected_images_from_large_binned_stack_to_common_disk(self, ref_session, last_cycle,
    predominant_out_of_plane, projection_parameters, large_binned_stack, model_id):
        
        combined_stack = 'combined_stack.hdf'
        
        segment_prop = namedtuple('segment_prop', 'local_id inplane_angle shift_x_A shift_y_A unbent_ip_angle ' + \
        'unbent_shift_x_A unbent_shift_y_A peak')
        
        ref_columns = SpringDataBase().get_columns_from_table(RefinementCycleSegmentTable)
        ref_namedtuple = namedtuple('ref_info', ' '.join(ref_columns))
        
        segment_info = []
        combined_stack_id = 0
        for (each_phi, each_theta, each_psi, each_x, each_y) in projection_parameters:
            max_cc_segments_list = self.get_segment_entries_closest_to_phi_on_rank0_and_broadcast_results(ref_session,
            last_cycle, ref_columns, ref_namedtuple, each_phi, each_theta, model_id)
            
            segment_info, combined_stack_id =\
            self.gather_images_from_distributed_stacks_or_add_blank(large_binned_stack, combined_stack, segment_info,
            segment_prop, ref_namedtuple, max_cc_segments_list, combined_stack_id)
        
        return segment_info, combined_stack


    def copy_stack_from_to(self, src_stack, target_stack):
        img = EMData()
        img_count = EMUtil.get_image_count(src_stack)
        for each_img_id in list(range(img_count)):
            img.read_image(src_stack, each_img_id)
            img.write_image(target_stack, each_img_id)
        

    def summarize_each_bin_round_with_simulated_vs_experimental_images_and_powerspectra_mpi(self, resolution_aim,
    large_binned_stack, latest_reconstruction, ref_cycle_id, each_reference, pixelinfo, diagnostic_prefix, prj_info):
        ref_session, temp_ref_db, last_cycle = self.get_ref_session_and_last_cycle(ref_cycle_id)
        if self.rank == 0:
            predominant_out_of_plane, segmentrefine3d_sumfig = self.prepare_gallery_figure(ref_session, last_cycle,
            each_reference.model_id)
        else:
            predominant_out_of_plane = None
        
        self.comm.barrier()
        predominant_out_of_plane = self.comm.bcast(predominant_out_of_plane, root=0)
        
        exp_power, segment_size = self.generate_experimental_sum_of_powerspectra(ref_session, last_cycle,
        large_binned_stack, predominant_out_of_plane, pixelinfo, each_reference.model_id)
        
        self.comm.barrier()
        
        emdata_files = OpenMpi().write_out_emdata_from_distributed_nodes_to_common_disk(self.comm, exp_power,
        'exp_power.hdf')
        
        if self.rank == 0:
            exp_power = OpenMpi().reduce_emdata_on_main_node(exp_power, emdata_files)
            
            diagnostic_stack, projection_parameters, total_cc, variance = \
            self.prepare_upper_part_of_figure(resolution_aim, latest_reconstruction, each_reference, pixelinfo,
            predominant_out_of_plane, exp_power, segment_size, ref_cycle_id, diagnostic_prefix)
        else:
            projection_parameters = None
            total_cc = None
            variance = None
            
        projection_parameters = self.comm.bcast(projection_parameters, root=0)
        
        segment_info, combined_stack = \
        self.collect_selected_images_from_large_binned_stack_to_common_disk(ref_session, last_cycle,
        predominant_out_of_plane, projection_parameters, large_binned_stack, each_reference.model_id)
        
        if self.rank == 0:
            self.ax23 = self.generate_nice_gallery_of_ten_images_corresponding_projections(ref_session, last_cycle,
            ref_cycle_id, combined_stack, diagnostic_stack, projection_parameters, pixelinfo, each_reference,
            diagnostic_prefix, prj_info, segment_info)
            
            self.copy_stack_from_to(diagnostic_stack, os.path.basename(diagnostic_stack))

            cc_map_ids = [3 * len(projection_parameters) + each_cc_map_id \
                       for each_cc_map_id, each_cc_map in enumerate(projection_parameters)]

            img_ids = [2 * len(projection_parameters) + each_img_id \
                       for each_img_id, each_param in enumerate(projection_parameters)]

            prj_ids = [each_img_id for each_img_id, each_param in enumerate(projection_parameters)]

            cc_map_ids = OpenMpi().split_sequence_evenly(cc_map_ids, self.size)
            projection_parameters = OpenMpi().split_sequence_evenly(projection_parameters, self.size) 
            img_ids = OpenMpi().split_sequence_evenly(img_ids, self.size)
            prj_ids = OpenMpi().split_sequence_evenly(prj_ids, self.size)
        else:
            cc_map_ids = None
            img_ids = None
            prj_ids = None
            projection_parameters = None
            diagnostic_stack = None

        self.comm.barrier()
        cc_map_ids = self.comm.scatter(cc_map_ids, root=0)
        img_ids = self.comm.scatter(img_ids, root=0)
        prj_ids = self.comm.scatter(prj_ids, root=0)
        projection_parameters = self.comm.scatter(projection_parameters, root=0)
        diagnostic_stack = self.comm.bcast(diagnostic_stack, root=0)

        diagnostic_stack = os.path.join(self.tempdir, os.path.basename(diagnostic_stack))
        self.copy_stack_from_to(os.path.basename(diagnostic_stack), diagnostic_stack)
        
        x_err_data, y_err_data = self.get_error_estimates_from_cc_maps(diagnostic_stack, cc_map_ids, pixelinfo,
        each_reference)

        x_err_data = self.comm.gather(x_err_data, root=0)
        y_err_data = self.comm.gather(y_err_data, root=0)

        if prj_info.projection_stack is not None:
            azimuth_err, tilt_err = self.get_error_estimates_from_angles(prj_info, diagnostic_stack,
            projection_parameters, img_ids, each_reference)

            rot_err = self.get_error_estimates_for_inplane_rotation(diagnostic_stack, img_ids, prj_ids)

            azimuth_err = self.comm.gather(azimuth_err, root=0)
            tilt_err = self.comm.gather(tilt_err, root=0)
            rot_err = self.comm.gather(rot_err, root=0)
        
        self.comm.barrier()
        projection_parameters = self.comm.gather(projection_parameters, root=0)
        if self.rank == 0:
            x_err_data = OpenMpi().merge_sequence_of_sequences(x_err_data)
            y_err_data = OpenMpi().merge_sequence_of_sequences(y_err_data)
            projection_parameters = OpenMpi().merge_sequence_of_sequences(projection_parameters)

            shift_msg = self.average_and_summarize_results_of_error_esimation(projection_parameters, x_err_data,
            y_err_data)

            if prj_info.projection_stack is not None:
                azimuth_err = OpenMpi().merge_sequence_of_sequences(azimuth_err)
                tilt_err = OpenMpi().merge_sequence_of_sequences(tilt_err)
                rot_err = OpenMpi().merge_sequence_of_sequences(rot_err)

                angle_msg = self.average_and_summarize_results_of_ang_error_estimation(projection_parameters,
                azimuth_err, tilt_err, rot_err)
            else:
                angle_msg = ''

            os.remove(combined_stack)
            os.remove(os.path.basename(diagnostic_stack))

            self.finalize_figure_with_gallery(ref_cycle_id, segmentrefine3d_sumfig, self.ax23, pixelinfo.pixelsize,
            diagnostic_prefix, shift_msg, angle_msg)
        
        self.comm.barrier()
        os.remove(diagnostic_stack)
        ref_session.close()
        os.remove(temp_ref_db)
        
        return total_cc, variance
    
    
class SegmentRefine3dMpiReconstruct(SegmentRefine3dMpiDiagnostics):

    def reconstruct_volume_on_single_node(self, alignment_parameters, ref_cycle_id, each_info, ctf3d_avg_squared,
    large_reconstruction_stack, rec_stack, lambda_sirt, each_reference, pixelinfo):
        common_rec_stack = 'common_rec_stack.hdf'

        img = EMData()
        for each_rank in list(range(self.size)):
            if each_rank == self.rank:
                if each_rank != 0:
                    common_local_id = EMUtil.get_image_count(common_rec_stack)
                else:
                    common_local_id = 0

                for each_par_id, each_align_param in enumerate(alignment_parameters):
                    img.read_image(large_reconstruction_stack, each_align_param.local_id)
                    img.write_image(common_rec_stack, common_local_id)
                    alignment_parameters[each_par_id] = each_align_param._replace(local_id=common_local_id)
                    common_local_id += 1
            self.comm.barrier()

        alignment_parameters = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(alignment_parameters)
        alignment_parameters = self.comm.gather(alignment_parameters, root=0)
          
        if self.rank == 0:
            alignment_parameters = OpenMpi().merge_sequence_of_sequences(alignment_parameters)
              
            alignment_parameters = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(alignment_parameters, 
            SegClassReconstruct().make_named_tuple_for_reconstruction())
          
            reconstructed_volume, alignment_parameters, symmetry_alignment_parameters, fsc_lines, lambda_sirt, Euler_angles_rec = \
            self.apply_orientation_parameters_and_reconstruct_imposing_helical_symmetry(alignment_parameters,
            ref_cycle_id, each_info.resolution_aim, common_rec_stack, ctf3d_avg_squared, pixelinfo,
            each_reference, self.stepsize, rec_stack, lambda_sirt, self.unbending, self.rank)
          
            reconstructed_volume = self.perform_ctf_correction_and_volume_symmetrization(each_info.resolution_aim,
            reconstructed_volume, ctf3d_avg_squared, pixelinfo.pixelsize)
  
            helical_error = self.perform_mean_ccc_evaluation_of_images_with_symmetry_related_projections(rec_stack,
            alignment_parameters, Euler_angles_rec, pixelinfo.helixwidthpix)
            os.remove(common_rec_stack)
        else:
            reconstructed_volume = None
            fsc_lines = None
            helical_error = self.prepare_empty_helical_error()
            symmetry_alignment_parameters = []
            alignment_parameters = []
 
        self.comm.barrier()
        symmetry_alignment_parameters = self.comm.gather(symmetry_alignment_parameters, root=0)
 
        return reconstructed_volume, alignment_parameters, symmetry_alignment_parameters, fsc_lines, helical_error


    def get_first_half_reconstruction_files(self, rec_files):
        """
        >>> from spring.segment3d.refine.sr3d_mpi import SegmentRefine3dMpi
        >>> SegmentRefine3dMpi().get_first_half_reconstruction_files(list(range(10)))
        [0, 1, 2, 3, 4]
        """
        first_half_rec_files = [each_file for each_file_id, each_file in enumerate(rec_files) \
                               if (each_file_id) < len(rec_files) / 2]

        return first_half_rec_files


    def get_second_half_reconstruction_files(self, rec_files):
        """
        >>> from spring.segment3d.refine.sr3d_mpi import SegmentRefine3dMpi
        >>> SegmentRefine3dMpi().get_second_half_reconstruction_files(list(range(10)))
        [5, 6, 7, 8, 9]
        """
        first_half_rec_files = [each_file for each_file_id, each_file in enumerate(rec_files) \
                               if (each_file_id) >= len(rec_files) / 2]

        return first_half_rec_files


    def get_even_reconstruction_files(self, rec_files):
        """
        >>> from spring.segment3d.refine.sr3d_mpi import SegmentRefine3dMpi
        >>> SegmentRefine3dMpi().get_even_reconstruction_files(list(range(10)))
        [0, 2, 4, 6, 8]
        """
        even_half_rec_files = [each_file for each_file_id, each_file in enumerate(rec_files) if (each_file_id) % 2 == 0]

        return even_half_rec_files


    def get_odd_reconstruction_files(self, rec_files):
        """
        >>> from spring.segment3d.refine.sr3d_mpi import SegmentRefine3dMpi
        >>> SegmentRefine3dMpi().get_odd_reconstruction_files(list(range(10)))
        [1, 3, 5, 7, 9]
        >>> SegmentRefine3dMpi().get_odd_reconstruction_files(10 * [50])
        [50, 50, 50, 50, 50]
        """
        odd_half_rec_files = [each_file for each_file_id, each_file in enumerate(rec_files) if (each_file_id) % 2 == 1]
        
        return odd_half_rec_files


    def reconstruct_partial_volumes_on_distributed_nodes(self, alignment_parameters, ref_cycle_id, each_info,
    ctf3d_avg_squared, large_reconstruction_stack, rec_stack, lambda_sirt, each_reference, pixelinfo):
        sr3d = SegmentRefine3d()
        sr3d.tempdir = self.tempdir
        
        reconstructed_volume, alignment_parameters, symmetry_alignment_parameters, fsc_lines, lambda_sirt, Euler_angles_rec = \
        sr3d.apply_orientation_parameters_and_reconstruct_imposing_helical_symmetry(alignment_parameters,
        ref_cycle_id, each_info.resolution_aim, large_reconstruction_stack, ctf3d_avg_squared, pixelinfo,
        each_reference, self.stepsize, rec_stack, lambda_sirt, self.unbending, self.rank, split_reconstruction=False)
        
        rec_files = OpenMpi().write_out_emdata_from_distributed_nodes_to_common_disk(self.comm,
        reconstructed_volume, 'recvol.hdf')
        
        self.comm.barrier()
        if self.rank == 0:
            self.comm.send(rec_files, dest=1, tag=11)
        
            even_half_rec_files = self.get_even_reconstruction_files(rec_files)
            
            even_rec = OpenMpi().reduce_emdata_on_main_node(reconstructed_volume, even_half_rec_files,
            read_first=False)
            
        if self.rank == 1:
            rec_files = self.comm.recv(source=0, tag=11)

            odd_half_rec_files = self.get_odd_reconstruction_files(rec_files)
            
            odd_rec = OpenMpi().reduce_emdata_on_main_node(reconstructed_volume, odd_half_rec_files,
            read_first=False)
            
            odd_rec.write_image('rec_fsc_odd.hdf')
        self.comm.barrier()
        if self.rank == 0:
            odd_rec = EMData()
            odd_rec.read_image('rec_fsc_odd.hdf')
            if self.keep_intermediate_files:
                even_rec.write_image('rec_fsc_even.hdf')
            else:
                os.remove('rec_fsc_odd.hdf')
            
            uncorrected_reconstruction, fsc_lines = \
            self.compute_fsc_on_volumes_from_half_the_dataset(each_info.resolution_aim, even_rec, odd_rec,
            pixelinfo, each_reference.helical_symmetry, each_reference.rotational_symmetry)
            
            reconstructed_volume = self.perform_ctf_correction_and_volume_symmetrization(each_info.resolution_aim,
            uncorrected_reconstruction, ctf3d_avg_squared, pixelinfo.pixelsize, each_reference)
                
        self.comm.barrier()

        helical_error = self.perform_mean_ccc_evaluation_of_images_with_symmetry_related_projections(rec_stack,
        alignment_parameters, Euler_angles_rec, pixelinfo.helixwidthpix)
        
        alignment_parameters = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(alignment_parameters)
        alignment_parameters = self.comm.gather(alignment_parameters, root=0)

        symmetry_alignment_parameters = self.comm.gather(symmetry_alignment_parameters, root=0)
        self.comm.barrier()
        
        if self.rank == 0:
            alignment_parameters = OpenMpi().merge_sequence_of_sequences(alignment_parameters)
            symmetry_alignment_parameters = OpenMpi().merge_sequence_of_sequences(symmetry_alignment_parameters)
             
        return reconstructed_volume, alignment_parameters, symmetry_alignment_parameters, fsc_lines, lambda_sirt,\
        helical_error
    
    
    def collect_and_avearge_helical_error(self, helical_error):
        helical_error = list(helical_error)
        helical_error = self.comm.gather(helical_error, root=0)
        if self.rank == 0:
            helical_error = self.merge_list_of_helical_errors(helical_error)

            self.log_helical_error(helical_error)

        return helical_error


    def write_out_reconstruction_on_rank0(self, reference_files, pixelinfo, ref_cycle_id, each_reference,
    reconstructed_volume):
        if self.rank == 0:
            latest_reconstruction, diagnostic_prefix, fsc_prefix, reference_files = \
            self.write_out_reconstruction_and_remove_reference(reference_files, ref_cycle_id, pixelinfo,
            each_reference, reconstructed_volume)
        else:
            latest_reconstruction = None
            diagnostic_prefix = None
            fsc_prefix = None

        latest_reconstruction = self.comm.bcast(latest_reconstruction, root=0)

        return latest_reconstruction, diagnostic_prefix, fsc_prefix, reference_files


    def post_processing_of_reconstruct_mpi(self, each_info, reference_files, pixelinfo, ref_cycle_id,
    large_reconstruction_stack, each_reference, reconstructed_volume, alignment_parameters,
    symmetry_alignment_parameters, fsc_lines, helical_error, prj_info, is_last_cycle):

        latest_reconstruction, diagnostic_prefix, fsc_prefix, reference_files = \
        self.write_out_reconstruction_on_rank0(reference_files, pixelinfo, ref_cycle_id, each_reference,
        reconstructed_volume)

        amp_cc, variance = self.summarize_each_bin_round_with_simulated_vs_experimental_images_and_powerspectra_mpi(
        each_info.resolution_aim, large_reconstruction_stack, latest_reconstruction, ref_cycle_id, 
        each_reference, pixelinfo, diagnostic_prefix, prj_info)

        if self.rank == 0:
            self.write_out_fsc_line(fsc_lines, pixelinfo.pixelsize, fsc_prefix, ref_cycle_id)

            self.evaluate_alignment_parameters_and_summarize_in_plot(alignment_parameters,
            symmetry_alignment_parameters, fsc_lines, ref_cycle_id, each_reference, pixelinfo, diagnostic_prefix,
            each_info.resolution_aim)

            self.enter_additional_ref_parameters_in_database(ref_cycle_id, symmetry_alignment_parameters,
            fsc_lines.cylinder_masked, amp_cc, variance, helical_error, pixelinfo.pixelsize, each_reference,
            is_last_cycle)

        return reference_files


    def reconstruct_volume_mpi(self, selected_parameters, each_info, info_series, reference_files, ctf3d_avg_squared,
    each_index, pixelinfo, ref_cycle_id, start_ref_cycle_id, large_reconstruction_stack, lambda_sirt, prj_info):
    
        sel_image_count = self.comm.gather(max([len(each_model) for each_model in selected_parameters]), root=0)
        if self.rank == 0:
            if sum(sel_image_count) == 0:
                self.if_no_selected_images_left_abort_refinement()

        rec_stack_info = SegClassReconstruct().make_rec_stack_info()
        for each_reference in reference_files:
            rec_stack = rec_stack_info(os.path.join(self.tempdir, 'rec_stack.hdf'), each_reference.ref_file,
            pixelinfo.alignment_size)
            
            comb_sel_params = \
            OpenMpi().convert_list_of_namedtuples_to_list_of_lists(selected_parameters[each_reference.model_id])

            comb_sel_params = self.comm.gather(comb_sel_params, root=0)
            if self.rank == 0:
                comb_sel_params = OpenMpi().merge_sequence_of_sequences(comb_sel_params)
            comb_sel_params = self.comm.bcast(comb_sel_params, root=0)

            if len(comb_sel_params) > 1:
                volume_unified_on_single_node = False
                if volume_unified_on_single_node:
                    reconstructed_volume, alignment_parameters, symmetry_alignment_parameters, fsc_lines, helical_error = \
                    self.reconstruct_volume_on_single_node(selected_parameters[each_reference.model_id], ref_cycle_id, 
                    each_info, ctf3d_avg_squared, large_reconstruction_stack, rec_stack, lambda_sirt, each_reference, 
                    pixelinfo)
                    
                if not volume_unified_on_single_node:
                    reconstructed_volume, alignment_parameters, symmetry_alignment_parameters, fsc_lines, lambda_sirt, helical_error = \
                    self.reconstruct_partial_volumes_on_distributed_nodes(selected_parameters[each_reference.model_id], 
                    ref_cycle_id, each_info, ctf3d_avg_squared, large_reconstruction_stack, rec_stack, lambda_sirt, 
                    each_reference, pixelinfo)
        
                helical_error = self.collect_and_avearge_helical_error(helical_error)
                    
                if self.rank == 0:
                    self.log.plog(90 * (ref_cycle_id - start_ref_cycle_id + 0.9 - 1) / float(self.iteration_count) + 5)
            
                is_last_cycle = self.determine_whether_is_last_cycle(start_ref_cycle_id, ref_cycle_id)

                reference_files = \
                self.post_processing_of_reconstruct_mpi(each_info, reference_files, pixelinfo, ref_cycle_id,
                large_reconstruction_stack, each_reference, reconstructed_volume, alignment_parameters,
                symmetry_alignment_parameters, fsc_lines, helical_error, prj_info, is_last_cycle)

                reference_files[each_reference.model_id] = reference_files[each_reference.model_id]._replace(fsc=fsc_lines)
                    
            else:
                reference_vol = EMData()
                reference_vol.read_image(each_reference.ref_file)

                latest_reconstruction, diagnostic_prefix, fsc_prefix, reference_files = \
                self.write_out_reconstruction_on_rank0(reference_files, pixelinfo, ref_cycle_id, each_reference,
                reference_vol)
    
                fsc_lines = None
            
        self.comm.barrier()
        self.cleanup_of_prj_stacks(prj_info)

        return reference_files, lambda_sirt
    

class SegmentRefine3dMpi(SegmentRefine3dMpiReconstruct):

    def perform_iterative_projection_matching_and_3d_reconstruction(self):
        info_series, reference_files, image_list, masked_segment_stack, large_segment_stack, lambda_sirt, \
        start_ref_cycle_id, required_byte = self.prepare_pre_cycle_setup_mpi()
        
        ori_large_segment_stack, ori_reference_file, ori_alignment_size, ori_helixwidthpix, ori_pixelsize = \
        self.define_original_input_values_before_binning(large_segment_stack, reference_files)
        
        if self.rank == 0:
            self.log.plog(5)
            
        ref_cycle_id, unbending_info, large_straightened_stack = \
        self.setup_dummies_for_iteration(start_ref_cycle_id)
        
        for each_index, each_info in enumerate(info_series):
            
            reference_files, large_binned_segment_stack, ctf3d_avg_squared, pixelinfo = self.perform_binning_mpi(info_series,
            reference_files, ori_large_segment_stack, ori_reference_file, ori_alignment_size, ori_helixwidthpix,
            ori_pixelsize, each_index, image_list, ref_cycle_id)
            
            for each_iteration_number in range(1, each_info.iteration_count + 1):
                ref_cycle_id += 1
                
                mask_params, previous_params, prj_info, reference_files = \
                self.project_including_masking_and_filtering_mpi(each_info, reference_files, each_iteration_number,
                ref_cycle_id, info_series, required_byte, pixelinfo)
                
                if self.rank == 0:
                    self.log.plog(90 * (ref_cycle_id - start_ref_cycle_id + 0.2 - 1) / float(self.iteration_count) + 5)
                
                masked_segment_stack, previous_params, unbending_info, large_reconstruction_stack, \
                large_straightened_stack = \
                self.mask_and_window_and_unbend_if_required_mpi(masked_segment_stack, large_binned_segment_stack,
                each_iteration_number, ref_cycle_id, previous_params, mask_params, info_series, each_index,
                unbending_info, large_straightened_stack, pixelinfo)
                
                large_binned_segment_stack = large_reconstruction_stack
                if self.rank == 0:
                    self.log.plog(90 * (ref_cycle_id - start_ref_cycle_id + 0.3 - 1) / float(self.iteration_count) + 5)
                    
                if self.resume_refinement_option and not self.reference_option and each_iteration_number == 1:
                    current_parameters = previous_params
                    translation_step = 1.0
                else:
                    current_parameters, translation_step, prj_info = \
                    self.perform_coarse_and_fine_projection_matching(each_info, masked_segment_stack, prj_info,
                    previous_params, pixelinfo.alignment_size)
                
                if self.rank == 0:
                    self.log.plog(90 * (ref_cycle_id - start_ref_cycle_id + 0.7 - 1) / float(self.iteration_count) + 5)
                
                selected_parameters = self.select_segments_based_on_specified_criteria_mpi(current_parameters,
                unbending_info, translation_step, ref_cycle_id, each_info, pixelinfo, reference_files)
                
                reconstruction_stack = self.choose_reconstruction_stack_based_on_unbending(large_straightened_stack,
                large_reconstruction_stack)
                    
                reference_files, lambda_sirt = self.reconstruct_volume_mpi(selected_parameters, each_info,
                info_series, reference_files, ctf3d_avg_squared, each_index, pixelinfo, ref_cycle_id, start_ref_cycle_id,
                reconstruction_stack, lambda_sirt, prj_info)
                
                if self.rank == 0:
                    aim_ref = self.get_aim_dict()
                    if self.halfset_refinement and aim_ref[each_info.resolution_aim] >= aim_ref[self.halfset_start]:
                        reference_files = self.compute_cross_fsc_and_write_out_merged_volume(reference_files, each_info,
                        pixelinfo, ref_cycle_id)
                    self.log.plog(90 * (ref_cycle_id - start_ref_cycle_id) / float(self.iteration_count) + 5)
                
                self.comm.barrier()
                if self.layer_line_filter and not self.unbending:
                    os.remove(large_straightened_stack)
        
            if self.unbending:
                os.remove(large_straightened_stack)
        
            os.remove(large_reconstruction_stack)
        if self.rank == 0:
            self.update_persistence_length_in_spring_db()
            os.remove(os.path.basename(ori_large_segment_stack))
            if self.ctf_correction:
                os.remove(ctf3d_avg_squared)
            self.log.endlog(self.feature_set)
        self.comm.barrier()
        
        self.clean_up_temporary_large_stack(ori_large_segment_stack, masked_segment_stack)
        
        os.rmdir(self.tempdir)
        
def main():
    parset = SegmentRefine3dPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    segment_stack = SegmentRefine3dMpi(reduced_parset)
    segment_stack.perform_iterative_projection_matching_and_3d_reconstruction()


if __name__ == '__main__':
    main()
