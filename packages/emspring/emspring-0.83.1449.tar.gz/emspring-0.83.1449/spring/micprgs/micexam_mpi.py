# Author: Carsten Sachse 11-Nov-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from spring.csinfrastr.csproductivity import OpenMpi
from spring.micprgs.micctfdetermine_mpi import ScanMpi
from spring.micprgs.micexam import MicrographExam, MicrographExamPar

class MicrographExamMpi(MicrographExam, ScanMpi):

    def exam_scans(self):
        self.startup_scan_mpi_programs()
        
        if self.micrograph_files != []:
            self.examine_scans_computing_total_and_local_powerspectra(self.micrograph_files, self.outfiles)
        
        self.end_scan_mpi_programs()

def main():
    parset = MicrographExamPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    micrograph = MicrographExamMpi(reduced_parset)
    micrograph.exam_scans()


if __name__ == '__main__':
    main()
