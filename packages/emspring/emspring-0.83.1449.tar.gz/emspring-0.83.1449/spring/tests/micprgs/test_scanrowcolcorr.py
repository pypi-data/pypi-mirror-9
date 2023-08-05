#!/usr/bin/env python
"""
Test module to check scanrowcolcorr
"""
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.micprgs.scanrowcolcorr import ScanRowColCorrPar, ScanRowColCorr
from spring.micprgs.scansplit import ScanSplit
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.micprgs.test_scansplit import ScanPreparation
import os


class TestScanRowColCorr(ScanRowColCorr, ScanSplit, ScanPreparation):
    """
    Test class that tests work of scanrowcolcorr
    """
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = ScanRowColCorrPar()
        self.prepare_noise_micrograph()
        self.reference_micrograph.write_image('test_noise.mrc')

        self.feature_set.parameters['Micrograph']='test_noise.mrc'
        self.feature_set.parameters['Diagnostic plot']='test_diagnostic.png'
        self.feature_set.parameters['Percentage of micrograph area to be analyzed']=80

        super(TestScanRowColCorr, self).__init__(self.feature_set)

    def check_cross_correlation(self):
        for cross_correlation in self.ccrow:
            assert cross_correlation <= 1
        for cross_correlation in self.cccol:
            assert cross_correlation <= 1

    def teardown(self):
        os.remove('test_noise.mrc')
        os.remove('test_diagnostic.png')

        self.testingdir.remove()


class TestScanRowColCorrMain(TestScanRowColCorr):
    def do_test_case_rcc1(self):
        self.perform_scanrowcolcorr()

        self.check_cross_correlation()


class TestScanRowColCorrMainEndToEnd(TestScanRowColCorr):
    def do_end_to_end_test_rcc_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_rcc_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)


def main():
    tdf = TestScanRowColCorrMain()
    tdf.setup()
    tdf.do_test_case_rcc1()
        
if __name__ == '__main__':
    main()
