# Author: Carsten Sachse 18-Aug-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from spring.csinfrastr.csproductivity import OpenMpi
from spring.segment3d.refine.sr3d_mpi import SegmentRefine3dMpi
from spring.segment3d.segmultirefine3d import SegMultiRefine3dPar


class SegMultiRefine3dMpi(SegmentRefine3dMpi):
    pass

def main():
    parset = SegMultiRefine3dPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    segment_stack = SegMultiRefine3dMpi(reduced_parset)
    segment_stack.perform_iterative_projection_matching_and_3d_reconstruction()


if __name__ == '__main__':
    main()
