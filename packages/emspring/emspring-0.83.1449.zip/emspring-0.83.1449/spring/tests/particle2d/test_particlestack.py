#!/usr/bin/env python
"""
Test module to check particlestack
"""
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.particle2d.particlestack import ParticleStack, ParticleStackPar
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segment import MicrographHelixPreparation, TestSegment
import os


class TestParticleStackPreparation(object):
    def setup_helix_or_particle_dimensions(self):
        self.feature_set.parameters['Particle coordinates'] = self.helix_coordinate_file
        self.feature_set.parameters['Estimated inner and outer particle diameter in Angstrom'] = ((200, 700))

class TestParticleStack(TestParticleStackPreparation, ParticleStack, MicrographHelixPreparation):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.prepare_helix_on_micrograph()
        
        self.feature_set = ParticleStackPar()
        self.setup_of_common_non_mpi_parameters()
        
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())

        super(TestParticleStack, self).__init__(self.feature_set)

    def do_test_case_ps1(self):
        self.window_particles()

    def teardown(self):
        TestSegment().remove_coordfile_micrographdir_and_linkfiles(self.helix_coordinate_file, self.micrograph_test_file)
        os.remove(self.micrograph_test_file)
        os.remove('test_output_stack-6xbin.hdf')
        self.testingdir.remove()


class TestParticleStackMore(TestParticleStack):
    def do_end_to_end_test_pc_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_pc_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)

class TestParticleStackMpi(TestParticleStack):
    def do_end_to_end_test_pc_inputfile_MPI(self):

        self.feature_set.parameters['MPI option']=True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)


def main():
    tsce = TestParticleStack()
    tsce.setup()
    tsce.do_test_case_ps1()
        
if __name__ == '__main__':
    main()
