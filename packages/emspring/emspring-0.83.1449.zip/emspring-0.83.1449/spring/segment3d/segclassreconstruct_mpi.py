# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from spring.csinfrastr.csproductivity import OpenMpi
from spring.segment3d.segclassreconstruct import SegClassReconstructPar, \
    SegClassReconstruct
import os


class SegClassReconstructMpi(SegClassReconstruct):
    def prepare_segclassreconstruct_mpi(self):
        if self.rank == 0:
            self.total_symmetry_sequence, entered_symmetry_seq, self.minimum_image_count_3d = \
            self.check_parameter_integritry_and_start_setup()
            
            self.infile = self.clear_previous_alignment_parameters_and_copy_class_to_local_directory(self.infile,
            self.classno, self.out_of_plane_tilt_angle)
            
            if self.centeroption is True:
                centered_class_avg = '{0}_centered{1}'.format(os.path.splitext(self.infile)[0],
                os.path.splitext(self.infile)[-1])
                
                self.infile = self.center_class_avg(self.infile, centered_class_avg, self.helixwidthpix,
                self.percent_reconstruction_size, self.out_of_plane_tilt_angle)
            if len(self.total_symmetry_sequence) < self.size:
                self.log.wlog('More CPUs than symmetry grid point requested. Will result in idle CPUs. Lower the ' + \
                'number of requested CPUs to the number of symmetry grid points.')
            total_symmetry_pair_id = OpenMpi().split_sequence_evenly(list(range(len(self.total_symmetry_sequence))),
            self.size)
            
            symmetry_sequence = OpenMpi().split_sequence_evenly(self.total_symmetry_sequence, self.size)
        else:
            total_symmetry_pair_id = None
            symmetry_sequence = None
            self.total_symmetry_sequence = None
            entered_symmetry_seq = None
            self.minimum_image_count_3d = None
            
        self.comm.barrier()
        self.infile = self.comm.bcast(self.infile, root=0)
        self.minimum_image_count_3d = self.comm.bcast(self.minimum_image_count_3d, root=0)
        self.total_symmetry_sequence = self.comm.bcast(self.total_symmetry_sequence, root=0)
        symmetry_sequence = self.comm.scatter(symmetry_sequence, root=0)
        total_symmetry_pair_id = self.comm.scatter(total_symmetry_pair_id, root=0)

        return symmetry_sequence, total_symmetry_pair_id, entered_symmetry_seq
    

    def setup_segclassreconstruct_mpi(self):
        self.comm, self.rank, self.size, self.log, self.tempdir = OpenMpi().setup_mpi_and_simultaneous_logging(self.log,
        self.feature_set.logfile, self.temppath)
        
        symmetry_sequence, total_symmetry_pair_id, entered_symmetry_seq = self.prepare_segclassreconstruct_mpi()
        
        return symmetry_sequence, total_symmetry_pair_id, entered_symmetry_seq


    def reconstruct_volumes_from_class_avg(self, symmetry_sequence, total_symmetry_pair_id, entered_symmetry_seq):
        if self.rank == 0:
            self.log.plog(10)
            
        local_vol_name = os.path.join(self.tempdir, self.volume_name)
        local_reprj_stack = os.path.join(self.tempdir, self.montaged_reprojection_stack)
        local_power_stack = os.path.join(self.tempdir, self.montaged_power_stack)

        local_helix_volumes = self.reconstruct_volumes_for_each_symmetry_pair(symmetry_sequence, total_symmetry_pair_id,
        self.infile, local_vol_name, local_reprj_stack, local_power_stack)
        
        self.comm.barrier()
        
        local_helix_volume_files = [each_vol.helix_vol for each_vol in local_helix_volumes]
        if self.keep_intermediate_files:
            local_helix_volume_files = OpenMpi().transfer_series_of_images_from_cpus_to_common_disk(self.comm,
            local_helix_volume_files)
        
            OpenMpi().gather_stacks_from_cpus_to_common_stack(self.comm, local_reprj_stack,
            self.montaged_reprojection_stack)

            OpenMpi().gather_stacks_from_cpus_to_common_stack(self.comm, local_power_stack,
            self.montaged_power_stack)

        symmetry_helix_volume_files = self.comm.gather(local_helix_volume_files, root=0)
        
        local_helix_volumes = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(local_helix_volumes)
        local_helix_volumes = self.comm.gather(local_helix_volumes, root=0)
        
        if self.rank == 0:
            self.log.plog(80)
            symmetry_helix_volume_files = OpenMpi().merge_sequence_of_sequences(symmetry_helix_volume_files)
            
            local_helix_volumes = OpenMpi().merge_sequence_of_sequences(local_helix_volumes)
            
            helix_vol_nt = self.make_symmetry_vol_named_tuple()
            
            local_helix_volumes = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(local_helix_volumes,
            helix_vol_nt)
            
            symmetry_helix_volumes = [local_helix_volumes[each_id]._replace(helix_vol=each_vol) \
                                      for each_id, each_vol in enumerate(symmetry_helix_volume_files)]
            
            self.enter_grid_values_in_database(entered_symmetry_seq, symmetry_helix_volumes, 
            self.montaged_reprojection_stack, self.montaged_power_stack)
            
        self.comm.barrier()


    def perform_reconstructions_from_class_for_symmetry_combinations(self):
        symmetry_sequence, total_symmetry_pair_id, entered_symmetry_seq = self.setup_segclassreconstruct_mpi()
        
        self.reconstruct_volumes_from_class_avg(symmetry_sequence, total_symmetry_pair_id, entered_symmetry_seq)
        self.cleanup_at_end()
        
        self.comm.barrier()
        if self.rank == 0:
            self.log.endlog(self.feature_set)
        
def main():
    parset = SegClassReconstructPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    class_average = SegClassReconstructMpi(reduced_parset)
    class_average.perform_reconstructions_from_class_for_symmetry_combinations()


if __name__ == '__main__':
    main()
