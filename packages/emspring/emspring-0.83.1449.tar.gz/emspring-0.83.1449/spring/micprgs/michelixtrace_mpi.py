# Author: Carsten Sachse 03-Nov-2013
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from spring.csinfrastr.csproductivity import OpenMpi
from spring.micprgs.micctfdetermine_mpi import ScanMpi
from spring.micprgs.michelixtrace import MicHelixTrace, MicHelixTracePar

class MicHelixTraceMpi(MicHelixTrace, ScanMpi):

    def trace_helices(self):
        self.startup_scan_mpi_programs()
        
        if self.micrograph_files != []:
            self.trace_helices_in_micrographs(self.micrograph_files, self.outfiles)
        
        self.end_scan_mpi_programs()

def main():
    parset = MicHelixTracePar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    micrograph = MicHelixTraceMpi(reduced_parset)
    micrograph.trace_helices()


if __name__ == '__main__':
    main()
