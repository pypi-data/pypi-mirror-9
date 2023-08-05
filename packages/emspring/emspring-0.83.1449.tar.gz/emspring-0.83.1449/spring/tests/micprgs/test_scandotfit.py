#!/usr/bin/env python
"""
Test module to check scandotfit
"""
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.micprgs.scandotfit import ScanDotFitPar, ScanDotFit
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.micprgs.test_scansplit import ScanPreparation
from utilities import model_gauss_noise
import numpy as np
import os


class DotScanPreparation(ScanPreparation):
    def prepare_dot_micrograph(self):
        self.row_count = 4
        self.column_count = 6
        self.dot_tile_size_in_pixel = 89

        self.make_dot_tile()
        self.stack_reference_micrographs_to_scan()
        self.add_noise_to_scan()
        self.scan.write_image('test_dotmic.mrc')

    def make_dot_tile(self):
        self.reference_micrograph_array = np.zeros((self.dot_tile_size_in_pixel, self.dot_tile_size_in_pixel))
        self.reference_micrograph_array[int(self.dot_tile_size_in_pixel/2)][int(self.dot_tile_size_in_pixel/2)] += 1

    def add_noise_to_scan(self):
        self.noise = model_gauss_noise(0.001, self.scan.get_xsize(), self.scan.get_ysize())
        self.scan += self.noise


class TestScanDotFit(ScanDotFit, DotScanPreparation):
    """
    Test class that tests work of scandotfit
    """
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = ScanDotFitPar()
        self.prepare_dot_micrograph()

        self.feature_set.parameters['Micrograph']='test_dotmic.mrc'
        self.feature_set.parameters['Diagnostic plot']='test_visoutput.png'
        self.feature_set.parameters['Scanner step size in micrometer']=float(2500/self.dot_tile_size_in_pixel)
        self.feature_set.parameters['Width of integration in pixels']=45
        self.feature_set.parameters['Topleft coordinates of dot grid']=((59, 310))
        self.feature_set.parameters['Topright coordinates of dot grid']=((504, 336))
        
        self.feature_set.parameters['Bottomleft coordinates of dot grid']=((int(self.dot_tile_size_in_pixel/2),
        int(self.dot_tile_size_in_pixel/2)))

        super(TestScanDotFit, self).__init__(self.feature_set)


    def compare_distance_mean_stdev(self):
        assert round(self.horizontal_mean*2)/2 == 2.5
        assert round(self.vertical_mean*2)/2 == 2.5
        assert self.horizontal_stdev < 1
        assert self.vertical_stdev < 1


    def teardown(self):
        os.remove('test_dotmic.mrc')
        os.remove('test_visoutput.png')

        self.testingdir.remove()


class TestScanDotFitMain(TestScanDotFit):
    def do_test_case_df1(self):
        self.perform_scandotfit()

        self.compare_distance_mean_stdev()


class TestScanDotFitMore(TestScanDotFit):
    def do_end_to_end_test_lf_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_lf_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)

def main():
    tdf = TestScanDotFitMain()
    tdf.setup()
    tdf.do_test_case_df1()
        
if __name__ == '__main__':
    main()
