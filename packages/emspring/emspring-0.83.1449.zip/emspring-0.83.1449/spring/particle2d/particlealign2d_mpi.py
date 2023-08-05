# Author: Carsten Sachse 6-Aug-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from spring.csinfrastr.csproductivity import OpenMpi
from spring.particle2d.particlealign2d import ParticleAlign2dPar, \
    ParticleAlign2d
from spring.segment2d.segmentalign2d_mpi import SegmentAlign2dMpi

class ParticleAlign2dMpi(ParticleAlign2d, SegmentAlign2dMpi):
    pass

def main():
    parset = ParticleAlign2dPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    stack = ParticleAlign2dMpi(reduced_parset)
    stack.perform_segmentalign2d_mpi()

if __name__ == '__main__':
    main()
