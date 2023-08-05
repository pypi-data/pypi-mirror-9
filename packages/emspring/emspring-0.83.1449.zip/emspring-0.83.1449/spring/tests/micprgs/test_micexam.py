#!/usr/bin/env python
"""
Test module to check micexam
"""
from filter import filt_ctf
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.micprgs.micexam import MicrographExam, MicrographExamPar
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.micprgs.test_scansplit import ScanPreparation
from utilities import generate_ctf
import os


class TestMicrographExam(MicrographExam):
    """
    Test class that tests work of micexam
    """
    def convolute_micrograph_with_CTF(self, micrograph):
        contrast_transfer_function = generate_ctf([3.0, 2.0, 200, self.pixelsize, 0, 10])
        conv_micrograph = filt_ctf(micrograph, contrast_transfer_function)
        
        return conv_micrograph

    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = MicrographExamPar()
        self.pixelsize = 3.5
        self.reference_micrograph = ScanPreparation().prepare_noise_micrograph(scan_stepsize=150.0)
        self.reference_micrograph = self.convolute_micrograph_with_CTF(self.reference_micrograph)
        self.reference_micrograph.write_image('test_noise.hdf')

        self.feature_set.parameters['Micrographs']='test_noise.hdf'
        self.feature_set.parameters['Diagnostic plot pattern']='test_diagnostic.png'
        self.feature_set.parameters['Tile size power spectrum in Angstrom']=420
        self.feature_set.parameters['Tile overlap in percent']=50
        self.feature_set.parameters['Complete tile array option']=False
        self.feature_set.parameters['Pixel size in Angstrom']=float(self.pixelsize)
        self.feature_set.parameters['Binning option']=True
        self.feature_set.parameters['Binning factor']=2
        
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)

        super(TestMicrographExam, self).__init__(self.feature_set)


    def teardown(self):
        pass
        os.remove('test_noise.hdf')
        os.remove('test_diagnostic.png')

        self.testingdir.remove()


class TestMicrographExamMain(TestMicrographExam):
    def do_test_case_se1(self):
        self.exam_scans()


class TestMicrographExamEndToEnd(TestMicrographExam):
    def do_end_to_end_test_se_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_se_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)

class TestMicrographExamMpi(TestMicrographExam):
    def do_end_to_end_test_sa_inputfile_with_MPI(self):
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

def main():
    tse = TestMicrographExamMain()
    tse.setup()
    tse.do_test_case_se1()
        
if __name__ == '__main__':
    main()
