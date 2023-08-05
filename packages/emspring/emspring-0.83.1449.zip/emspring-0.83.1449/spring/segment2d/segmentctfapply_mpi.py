# Author: Carsten Sachse 21-Sep-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from spring.csinfrastr.csproductivity import OpenMpi
from spring.segment2d.segmentctfapply import SegmentCtfApply, SegmentCtfApplyPar
import os
import shutil

        
class SegmentCtfApplyMpi(SegmentCtfApply):
    def apply_ctf_to_segment_stack(self):
        
        self.comm, self.rank, self.size, self.log, self.tempdir = OpenMpi().setup_mpi_and_simultaneous_logging(self.log,
        self.feature_set.logfile, self.temppath)
        
        if self.rank == 0:
            shutil.copy(self.spring_path, 'spring.db')
            
            ctf_parameters = \
            self.get_ctf_values_from_database_and_compute_local_ctf_based_if_demanded(self.ctffind_or_ctftilt_choice,
            self.convolve_or_phaseflip_choice, self.astigmatism_option, self.pixelsize, self.spring_path)
            
            segment_ids = list(range(len(ctf_parameters)))
            
            ctf_parameters = OpenMpi().split_sequence_evenly(ctf_parameters, self.size)
            segment_ids = OpenMpi().split_sequence_evenly(segment_ids, self.size)
        else:
            ctf_parameters = None
            segment_ids = None
        
        ctf_parameters = self.comm.scatter(ctf_parameters, root=0)
        segment_ids = self.comm.scatter(segment_ids, root=0)
        
        local_outfile = self.tempdir + self.outfile
        
        self.apply_ctf_to_segments(segment_ids, ctf_parameters, self.convolve_or_phaseflip_choice, self.infile,
        local_outfile)
        
        self.comm.barrier()
        OpenMpi().gather_stacks_from_cpus_to_common_stack(self.comm, local_outfile, self.outfile)
        
        os.rmdir(self.tempdir)
        if self.rank == 0:
            self.log.endlog(self.feature_set)
        

def main():
    parset = SegmentCtfApplyPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    segment_stack = SegmentCtfApplyMpi(reduced_parset)
    segment_stack.apply_ctf_to_segment_stack()


if __name__ == '__main__':
    main()
