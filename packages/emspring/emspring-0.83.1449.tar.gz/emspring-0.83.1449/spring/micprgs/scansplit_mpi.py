# Author: Carsten Sachse 11-Nov-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from spring.csinfrastr.csproductivity import OpenMpi
from spring.micprgs.micctfdetermine_mpi import ScanMpi
from spring.micprgs.scansplit import ScanSplit, ScanSplitPar

class ScanSplitMpi(ScanSplit, ScanMpi):

    def perform_splitscan(self):
        self.startup_scan_mpi_programs()
        
        if self.micrograph_files != []:
            self.perform_splitscan_by_finding_location_with_respect_to_reference_micrograph(self.micrograph_files,
            self.outfiles)
        
        self.end_scan_mpi_programs()

def main():
    parset = ScanSplitPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    micrograph = ScanSplitMpi(reduced_parset)
    micrograph.perform_splitscan()

if __name__ == '__main__':
    main()
