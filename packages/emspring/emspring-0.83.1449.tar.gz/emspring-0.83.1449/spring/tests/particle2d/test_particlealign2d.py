#!/usr/bin/env python
"""
Test module to check new particlealign2d module
"""
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.particle2d.particlealign2d import ParticleAlign2d, ParticleAlign2dPar
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segmentalign2d import TestSegmentAlign2d, \
    TestSegmentAlign2dPreparation
import os


class TestParticleAlign2dPreparation(object):
    def setup_helix_or_particle_dimension(self):
        self.feature_set.parameters['Estimated inner and outer particle diameter in Angstrom'] = ((200, 750))

        
class TestParticleAlign2d(TestParticleAlign2dPreparation, TestSegmentAlign2dPreparation, ParticleAlign2d):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = ParticleAlign2dPar()
        
        self.setup_of_common_non_mpi_parameters()
        self.feature_set.parameters['MPI option'] = False
        
        super(TestParticleAlign2d, self).__init__(self.feature_set)
        
    def do_test_case_pa1(self):

        self.perform_segmentalign2d()

        TestSegmentAlign2d().check_rotation(self.helix_stack, self.applied_rotations, self.delta_in_plane_rotation,
        self.rotation_step, self.restrain_option)
        
    def teardown(self):
        self.teardown_segmentalign2d()
        self.testingdir.remove()

        
class TestParticleAlign2dMore(TestParticleAlign2d):
    def do_test_case_pa2(self):
        self.restrain_option=False
        self.feature_set.parameters['Limit in-plane rotation']=self.restrain_option
        
        super(TestParticleAlign2d, self).__init__(self.feature_set)
        
        self.perform_segmentalign2d()

        TestSegmentAlign2d().check_rotation(self.helix_stack, self.applied_rotations, self.delta_in_plane_rotation,
        self.rotation_step, self.restrain_option)
        
    def do_end_to_end_test_sa_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
 
    def do_end_to_end_test_sa_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        
class TestParticleAlign2dMpi(TestParticleAlign2d):
    def do_end_to_end_test_sa_inputfile_with_MPI(self):
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

def main():
    talign = TestParticleAlign2d()
    talign.setup()
    talign.do_test_case_pa1()
        
if __name__ == '__main__':
    main()
