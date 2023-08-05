#!/usr/bin/env python
"""
Test module to check segmultirefine3d
"""
from glob import glob
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment3d.segmultirefine3d import SegMultiRefine3dPar, SegMultiRefine3d
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment3d.test_segmentrefine3d import TestSegmentRefine3dClean, TestSegmentRefine3dSetup
from utilities import model_gauss_noise
import os

        
class TestSegMultiRefine3dSetup(TestSegmentRefine3dSetup):
        
    def setup_of_common_sr3dg_non_mpi_parameters(self):
        self.feature_set = SegMultiRefine3dPar()
        self.input_stack = 'test_stack.hdf'
        self.setup_main_segmentrefine3d_parameters()
        
        self.feature_set.parameters.__delitem__('Helical symmetry in Angstrom or degrees')
        self.feature_set.parameters.__delitem__('Reference volume')
        self.feature_set.parameters.__delitem__('Rotational symmetry')
        self.feature_set.parameters.__delitem__('Helix polarity')
        self.feature_set.parameters.__delitem__('Filter layer-lines option')

        self.feature_set.parameters['Helical symmetries in Angstrom or degrees']='(10, 50); (20, 80); (30, 30)'
        self.feature_set.parameters['Reference volumes']='models???.hdf'
        self.feature_set.parameters['Rotational symmetries']='1, 1, 2'
        self.feature_set.parameters['Helix polarities']='polar, apolar, polar'
        
        
class TestSegMultiRefine3d(TestSegMultiRefine3dSetup, SegMultiRefine3d):
    def setup_srg3d(self):
        self.setup_of_common_sr3dg_non_mpi_parameters()
        
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(2, cpu_count())
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)
        
        self.prepare_apolar_helix = False
        self.generate_input_stack_from_helix()
        
        super(TestSegMultiRefine3dSetup, self).__init__(self.feature_set)
        
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.setup_srg3d()
        
    def teardown(self):
        self.cleanup_segmentrefine3d()

        self.testingdir.remove()
            
        
class TestSegMultiRefine3dMain(TestSegMultiRefine3d):
    def do_test_case_smr3d1(self):
        """
        * Standard single-CPU segmultirefine3d test
        """
        self.perform_iterative_projection_matching_and_3d_reconstruction()

        models = glob('{prefix}*{iter:03}{ext}'.format(prefix=os.path.splitext(self.test_reference_volume)[0],
        iter=self.iteration_count, ext=os.path.splitext(self.test_reference_volume)[1]))

        TestSegmentRefine3dClean().prepare_final_prj_for_documentation(models, self.test_reference_volume)


class TestSegMultiRefine3dMore(TestSegMultiRefine3d):
    def do_test_case_smr3d2(self):
        """
        * Standard single-CPU segmultirefine3d test with single reference
        """
        self.feature_set.parameters['Reference structure option']=True
        self.feature_set.parameters['Reference volumes']='models000.hdf'
        vol = model_gauss_noise(1, 100, 100, 100)
        vol.write_image('models000.hdf')

        super(TestSegMultiRefine3dSetup, self).__init__(self.feature_set)

        self.perform_iterative_projection_matching_and_3d_reconstruction()
        os.remove('models000.hdf')


class TestSegMultiRefine3dMpi(TestSegMultiRefine3d):
    def do_end_to_end_test_smr3d_inputfile_with_MPI(self):
        self.feature_set.parameters['MPI option'] = True
         
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

class TestSegMultiRefine3dEndToEnd(TestSegMultiRefine3d):
    def do_end_to_end_test_smr3d_inputfile(self):

        references = ['models001.hdf', 'models002.hdf', 'models003.hdf']
        for each_model in references:
            vol = model_gauss_noise(1, 100, 100, 100)
            vol.write_image(each_model)

        self.feature_set.parameters['Reference structure option']=True
        self.feature_set.parameters['Reference volumes']=', '.join([os.path.abspath(each) for each in references])
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
 
        [os.remove(each_model) for each_model in references]


    def do_end_to_end_test_smr3d_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        
        
def main():
    tsr3d = TestSegMultiRefine3dMain()
    tsr3d.setup()
    tsr3d.do_test_case_smr1()
        
if __name__ == '__main__':
    main()
