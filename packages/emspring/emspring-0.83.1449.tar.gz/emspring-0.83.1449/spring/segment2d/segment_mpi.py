# Author: Carsten Sachse 8-Jul-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from spring.csinfrastr.csproductivity import OpenMpi
from spring.segment2d.segment import Segment, SegmentPar
import os


class SegmentMpiPreparation(Segment):
    def prepare_segmentation_mpi(self):
        self.comm, self.rank, self.size, self.log, tempdir = OpenMpi().setup_mpi_and_simultaneous_logging(self.log,
        self.feature_set.logfile, self.temppath)
        
        if self.rank == 0:
            assigned_mics = self.validate_input()
            pair = self.assign_reorganize(self.micrograph_files, self.coordinate_files)

            helices, assigned_stack_ids, assigned_helix_ids = self.single_out(pair, self.stepsize, self.pixelsize,
            assigned_mics)

            helices = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(helices)
            
            helices = OpenMpi().split_sequence_evenly(helices, self.size)
        
        else:
            helices = None
            assigned_stack_ids = None
            assigned_helix_ids = None
            
        helices = self.comm.scatter(helices, root=0)
        
        helixinfo = self.make_helixinfo_named_tuple()
        helices = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(helices, helixinfo)
        
        return helices, tempdir, assigned_stack_ids, assigned_helix_ids
            

class SegmentMpi(SegmentMpiPreparation):
    def gather_distributed_helices_to_root(self, helices):
        helices = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(helices)
        
        helices = self.comm.gather(helices, root=0)
        
        if self.rank == 0:
            helices = OpenMpi().merge_sequence_of_sequences(helices)
            
            helixinfo = self.make_helixinfo_named_tuple()
            helices = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(helices, helixinfo)
        else:
            helices = None
        
        return helices
    
    
    def extract_segments_mpi(self, tempdir):
        if self.rank == 0:
            self.log.plog(10)
        imgstack = self.outfile
        local_windowed_stack = '{dir}{sep}temp_segments{rank}.hdf'.format(dir=tempdir, sep=os.sep, rank=self.rank)
        self.helices = self.cut_segments(self.helices, local_windowed_stack)
        
        if self.rank == 0:
            self.log.plog(80)
        return local_windowed_stack, imgstack


    def perform_binning_if_demanded(self, imgstack, local_windowed_stack):
        if self.binoption is True:
            local_binned_stack = '{0}binned{1}'.format(os.path.splitext(local_windowed_stack)[0],
            os.path.splitext(local_windowed_stack)[-1])
            
            binned_imgstack = '{0}-{1}xbin{2}'.format(os.path.splitext(imgstack)[0], self.binfactor,
            os.path.splitext(imgstack)[-1])
            
            if self.helices != []:
                self.binstack(local_windowed_stack, local_binned_stack, self.binfactor)
            self.comm.barrier()
            OpenMpi().gather_stacks_from_cpus_to_common_stack(self.comm, local_binned_stack, binned_imgstack)
        self.comm.barrier()


    def finish_segmentation_mpi(self, tempdir, imgstack, local_windowed_stack, assigned_stack_ids, assigned_helix_ids):
        OpenMpi().gather_stacks_from_cpus_to_common_stack(self.comm, local_windowed_stack, imgstack)
        self.helices = self.gather_distributed_helices_to_root(self.helices)
        self.comm.barrier()
        if self.rank == 0:
            self.enter_helix_parameters_in_database(self.helices, assigned_stack_ids, assigned_helix_ids)
        os.rmdir(tempdir)
        self.comm.barrier()
        if self.rank == 0:
            self.log.endlog(self.feature_set)


    def segment(self):
        self.helices, self.tempdir, assigned_stack_ids, assigned_helix_ids = self.prepare_segmentation_mpi()
        local_windowed_stack, imgstack = self.extract_segments_mpi(self.tempdir)
        self.perform_binning_if_demanded(imgstack, local_windowed_stack)

        self.finish_segmentation_mpi(self.tempdir, imgstack, local_windowed_stack,
        assigned_stack_ids, assigned_helix_ids)
        
            
def main():
    parset = SegmentPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    stack = SegmentMpi(reduced_parset)
    stack.segment()


if __name__ == '__main__':
    main()
