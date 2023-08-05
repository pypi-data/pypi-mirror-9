#!/usr/bin/env python
"""
Test module to check scansplit
"""
from EMAN2 import EMData, EMNumPy, Util
from fundamentals import mirror
from glob import glob
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.micprgs.scansplit import ScanSplit, ScanSplitPar, Micrograph
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from utilities import model_gauss_noise
import numpy as np
import os
import random
import sys

class ScanPreparation(object):
    def prepare_scan(self):
        """
        * Function to prepare a dummy test scan containing 3 x 2 micrographs
        """
        self.scanned_micrograph = 'test_scanmic.tif'
        self.row_count = 2
        self.column_count = 3
        self.number_of_micrographs = self.row_count*self.column_count
        self.micrograph_width_cm = 8.0
        self.micrograph_height_cm = 9.0
        self.label_width_cm = 3.0
        self.label_height_cm = 2.0
        self.scanner_stepsize_micrometer = 1000
        self.cross_correlation_criterion = 0.5

        self.reference_micrograph = self.make_refmic(self.micrograph_width_cm, self.micrograph_height_cm,
        self.label_width_cm, self.label_height_cm, self.scanner_stepsize_micrometer)
        
        self.reference_micrograph = self.add_noise_to_reference_micrograph(self.reference_micrograph)
        self.change_sigma_of_columns()
        self.pad_reference_micrograph()
        self.stack_reference_micrographs_to_scan()
        self.scan.write_image(self.scanned_micrograph)

#        mirrored_micrograph = mirror(self.scan, axis='y')
#        mirrored_micrograph.write_image(self.scanned_micrograph)
    def add_noise_to_reference_micrograph(self, micrograph):
        self.noise = model_gauss_noise(0.5, micrograph.get_xsize(), micrograph.get_ysize()) + 1
        micrograph += self.noise

        return micrograph

    def change_sigma_of_columns(self):
        column_numbers = [random.randint(int(0.06*self.reference_micrograph.get_xsize()),
        int(0.94*self.reference_micrograph.get_xsize())) for column_number in range(random.randint(2, 10))]
        
        for column_number in column_numbers:
            column = self.reference_micrograph.get_col(column_number)
            column = column*random.random() - random.random()
            self.reference_micrograph.set_col(column, column_number)

    def pad_reference_micrograph(self):
        border_dimension_x = int(1.2*self.micrograph_width_cm*1e+4/(self.scanner_stepsize_micrometer))
        border_dimension_y = int(1.2*self.micrograph_height_cm*1e+4/(self.scanner_stepsize_micrometer))

        self.reference_micrograph = Util.pad(self.reference_micrograph, border_dimension_x, border_dimension_y, 1, 0, 0, 0, '0')
        self.reference_micrograph_array = np.copy(EMNumPy.em2numpy(self.reference_micrograph))
        return self.reference_micrograph_array

    def stack_reference_micrographs_to_scan(self):
        shifted_micrographs = {}
        horizontally_stacked_micrographs = {}
        for row_number in range(self.row_count):
            for column_number in range(self.column_count):
                shifted_micrograph_x = np.roll(self.reference_micrograph_array, 5*row_number)
                shifted_micrograph_xy = np.roll(shifted_micrograph_x, 5*column_number, axis=-2)
                shifted_micrographs['column{0}row{1}'.format(column_number, row_number)] = shifted_micrograph_xy 
                
            horizontally_stacked_micrographs['row{0}'.format(row_number)] = \
            np.hstack([shifted_micrographs['column{0}row{1}'.format(column_number, row_number)] for column_number in \
            range(self.column_count)])
    
        self.stacked_scan = np.vstack([horizontally_stacked_micrographs['row{0}'.format(row_number)] for row_number in \
        range(self.row_count)])
        
        self.scan = EMNumPy.numpy2em(np.copy(self.stacked_scan))

        return self.scan

    def prepare_noise_micrograph(self, scan_stepsize=1000.0, width=8.0, height=9, label_w=3.0, label_height=2.0):
#        self.micrograph_width_cm = 8
#        self.micrograph_height_cm = 9
#        self.label_width_cm = 3
#        self.label_height_cm = 2
#        self.scanner_stepsize_micrometer = 1000

#        self.reference_micrograph = self.make_refmic(self.micrograph_width_cm, self.micrograph_height_cm, self.label_width_cm, self.label_height_cm, self.scanner_stepsize_micrometer)
        self.reference_micrograph = ScanSplit().make_refmic(width, height, label_w, label_height, scan_stepsize)
        
        self.reference_micrograph = self.add_noise_to_reference_micrograph(self.reference_micrograph)
        
        return self.reference_micrograph
    

class TestScanSplit(ScanSplit, ScanPreparation):
    """
    Test class that tests work of scansplit
    """
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = ScanSplitPar()
        
        self.prepare_scan()
        
        self.feature_set.parameters['Micrographs']=self.scanned_micrograph
        self.feature_set.parameters['Output micrograph pattern']='test_split999.hdf'
        self.feature_set.parameters['Number of columns x rows']=(self.column_count, self.row_count)
        self.feature_set.parameters['Number of micrographs to be cropped']=self.number_of_micrographs
        
        self.feature_set.parameters['Micrograph width x height in cm']=(self.micrograph_width_cm,
        self.micrograph_height_cm)
        
        self.feature_set.parameters['Label width x height in cm']=(self.label_width_cm, self.label_height_cm)
        self.feature_set.parameters['Scanner step size in micrometer']=float(self.scanner_stepsize_micrometer)
        self.feature_set.parameters['Cross-correlation rejection criterion']=float(self.cross_correlation_criterion)
        self.feature_set.parameters['Normscan option']=True
        self.feature_set.parameters['Binning option']=True
        self.feature_set.parameters['Contact print option']=True
        self.feature_set.parameters['Final print option']=True
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)


        super(TestScanSplit, self).__init__(self.feature_set)

    
    def test_top_and_bottom_label_position(self):
        self.scan.write_image(self.scanned_micrograph)
        self.img = mirror(self.scan, axis='y')
        self.img = mirror(self.img, axis='x')

        self.perform_splitscan()

    def compare_shifts(self):
        micrograph_number = 0 
        for row_number in range(self.row_count):
            for column_number in range(self.column_count):
                sys.stderr.write('{0} = {1}\n'.format(self.xoffset[micrograph_number], 5*row_number))
                assert 5*row_number - 1 <= self.xoffset[micrograph_number] <= 5*row_number + 1
                sys.stderr.write('{0} = {1}\n'.format(self.yoffset[micrograph_number], 5*column_number))
                assert 5*column_number -1 <= self.yoffset[micrograph_number] <= 5*column_number + 1
                micrograph_number += 1

    def get_mean_and_sigma_of_reference_micrograph(self):
        self.reference_stat = Micrograph().get_statistics_from_image(self.reference_micrograph)

    def compare_mean_and_sigma_of_normalized_micrograph(self):
        """
        Test whether normalization worked
        """
        split_stat = Micrograph().get_statistics_from_image(self.micrograph)

        assert self.reference_stat.avg > split_stat.avg
        assert self.reference_stat.sigma < split_stat.sigma

    def prepare_split_micrographs_on_stack_for_gallery(self):
        files = glob('*test_split999_???.hdf')
        img = stackimg = EMData()
        for index, file in enumerate(files):
            img.read_image(file)
            stackimg.write_image('test_split999.hdf', index)
            
    def teardown(self):
        os.remove(self.scanned_micrograph)
        os.remove('test_scanmic_cprint.pdf')

        files = glob('*split999*')
        for each_file in files:
            os.remove(each_file)

        self.testingdir.remove()


class TestScanSplitMain(TestScanSplit):
    def do_test_case_ss1(self):
        self.get_mean_and_sigma_of_reference_micrograph()
        self.perform_splitscan()
        self.compare_mean_and_sigma_of_normalized_micrograph()
        self.prepare_split_micrographs_on_stack_for_gallery()


class TestScanSplitEndToEnd(TestScanSplit):
    def do_end_to_end_test_ss_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_ss_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)


class TestScanSplitMpi(TestScanSplit):
    def do_end_to_end_test_sa_inputfile_with_MPI(self):
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        
def main():
    tss = TestScanSplitMain()
    tss.setup()
    tss.do_test_case_ss1()
        
if __name__ == '__main__':
    main()
