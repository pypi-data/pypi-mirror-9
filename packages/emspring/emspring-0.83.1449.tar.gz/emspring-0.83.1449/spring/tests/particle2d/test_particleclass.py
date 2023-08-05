#!/usr/bin/env python
"""
Test module to check particleclass
"""
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.particle2d.particleclass import ParticleClass, ParticleClassPar
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segmentclass import TestSegmentClassClear, \
    HelixClassPreparation
import os


class TestParticleClassPreparation(object):
    def setup_helix_or_particle_dimensions(self):
        self.feature_set.parameters['Estimated inner and outer particle diameter in Angstrom'] = ((200, 700))

class TestParticleClass(TestParticleClassPreparation, ParticleClass, TestSegmentClassClear, HelixClassPreparation):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = ParticleClassPar()
        self.setup_common_non_mpi_parameters()
        
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())

        super(TestParticleClass, self).__init__(self.feature_set)

    def do_test_case_pc1(self):
        self.classify()

    def teardown(self):
        self.teardown_segmentclass()
        self.testingdir.remove()


class TestParticleClassMore(TestParticleClass):
    def do_test_case_sc2(self):
        self.feature_set.parameters['Reference option']=True

        super(TestParticleClass, self).__init__(self.feature_set)
        self.classify()

class TestParticleClassEndToEnd(TestParticleClass):
    def do_end_to_end_test_pc_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_pc_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)

class TestParticleClassMpi(TestParticleClass):
    def do_end_to_end_test_pc_inputfile_MPI(self):

        self.feature_set.parameters['MPI option']=True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)


def main():
    tsce = TestParticleClass()
    tsce.setup()
    tsce.do_test_case_pc1()
        
if __name__ == '__main__':
    main()
