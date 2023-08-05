#!/usr/bin/env python
"""
Dummy module to check seggridexplore
"""
from glob import glob
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment3d.seggridexplore import SegGridExplore, SegGridExplorePar
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment3d.test_segclassreconstruct import TestSegClassReconstructMain
import os


class TestSegGridExplorePreparation(object):
    def setup_segclassreconstruct(self):
        self.tsrce = TestSegClassReconstructMain()
        self.tsrce.setup()
        self.tsrce.do_test_case_cr1()

    def setup_of_sgx_parameters(self):
        self.feature_set = SegGridExplorePar()
        
        self.pixelsize = 10.0
        self.reprojection_file = 'test_prefix.hdf'
        self.symmetry_grid_testfile = 'grid.db'
        
        self.feature_set.parameters['Grid database']=os.path.join(os.pardir, self.symmetry_grid_testfile)
        self.feature_set.parameters['Subgrid merge option']=False
        self.feature_set.parameters['Reconstitute Grid']=False
        self.feature_set.parameters['Batch mode']=True#False#
        self.feature_set.parameters['EM name']=self.reprojection_file
        self.feature_set.parameters['Parameter pair']=((10.0, 50.0))
            
        
class TestSegGridExplore(SegGridExplore, TestSegGridExplorePreparation):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.setup_segclassreconstruct()
        self.setup_of_sgx_parameters()
        os.rename(self.symmetry_grid_testfile, os.path.join(os.pardir, self.symmetry_grid_testfile))
        
        super(TestSegGridExplore, self).__init__(self.feature_set)
        
    def teardown(self):
        if self.batch_mode:
            files = glob('{0}*{1}'.format(os.path.splitext(self.reprojection_file)[0],
            os.path.splitext(self.reprojection_file)[-1]))
             
            for each_file in files:
                os.remove(each_file)
        self.tsrce.teardown()
        
        self.testingdir.remove()


class TestSegGridExploreMain(TestSegGridExplore):
    def do_test_sgx1(self):
        self.launch_seggridexplore()
        
class TestSegGridExploreEndToEnd(TestSegGridExplore):
    def do_end_to_end_test_sge_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
 
    def do_end_to_end_test_sge_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        
def main():
    ssx = TestSegGridExploreMain()
    ssx.setup()
    ssx.do_test_sgx1()
        
if __name__ == '__main__':
    main()
