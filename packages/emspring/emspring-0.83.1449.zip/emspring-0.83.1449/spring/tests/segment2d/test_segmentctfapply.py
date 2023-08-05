#!/usr/bin/env python
"""
Test module to check segmentctfapply
"""
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment2d.segmentctfapply import SegmentCtfApply, SegmentCtfApplyPar
from spring.tests.micprgs.test_micctfdetermine import TestMicCtfDetermineMain
from spring.tests.segment2d.test_segment import TestSegmentMain
import os
import shutil
# from spring.tests.csinfrastr.test_csreadinput import EndToEndTest

        
class TestSegmentCtfApplyPreparation(object):
    def generate_helix_stack_from_micrograph(self):
        self.tscd = TestMicCtfDetermineMain()
        self.tscd.setup()
        self.tscd.do_test_case_scd1()
        
        shutil.copy('spring.db', os.path.join(os.pardir, 'spring.db'))
        self.tscd.teardown()
        
        self.tseg = TestSegmentMain()
        self.tseg.micrograph_test_file = self.tscd.micrograph_file
        self.tseg.setup()
        self.tseg.do_test_case_seg1()
        
        os.remove(self.tseg.micrograph_test_file)
        shutil.move('spring.db', os.path.join(os.pardir, 'segment_spring.db'))
        shutil.copy(self.image_inp_stack, os.path.join(os.pardir, 'segmented_stack.hdf'))
        self.tseg.teardown()
        shutil.move('segmented_stack.hdf', self.image_inp_stack)
        

class TestSegmentCtfApply(SegmentCtfApply, TestSegmentCtfApplyPreparation):
        
    def setup_of_common_non_mpi_parameters(self):
        self.feature_set = SegmentCtfApplyPar()
        
        self.image_inp_stack = 'test_output_stack.hdf'
        self.image_out_stack = 'test_segments_ctf.hdf'
        self.test_ctfvolume = 'test_ctfvolume.hdf'
        
        self.feature_set.parameters['Image input stack'] = self.image_inp_stack
        self.feature_set.parameters['Image output stack'] = self.image_out_stack
        
        self.feature_set.parameters['spring.db file']='segment_spring.db'#os.path.join(os.pardir, 'spring.db')
            
        self.feature_set.parameters['Pixel size in Angstrom']=5.0
        self.feature_set.parameters['CTFFIND or CTFTILT'] = 'ctftilt'
        self.feature_set.parameters['convolve or phase-flip'] = 'convolve'
        self.feature_set.parameters['Astigmatism correction'] = True
        
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.setup_of_common_non_mpi_parameters()
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)
        
        self.generate_helix_stack_from_micrograph()
        super(TestSegmentCtfApply, self).__init__(self.feature_set)
        
    def teardown(self):
        os.remove(self.image_inp_stack)
        os.remove(self.image_out_stack)
        
        self.testingdir.remove()
    

class TestSegmentCtfApplyMain(TestSegmentCtfApply):
    def do_test_case_sca1(self):
        self.apply_ctf_to_segment_stack()


class TestSegmentCtfApplyMore(TestSegmentCtfApply):
    def do_test_case_sca2(self):
        self.feature_set.parameters['CTFFIND or CTFTILT'] = 'ctffind'
        super(TestSegmentCtfApply, self).__init__(self.feature_set)
        
        self.apply_ctf_to_segment_stack()
        
    def do_test_case_sca3(self):
        self.feature_set.parameters['convolve or phase-flip'] = 'phase-flip'
        super(TestSegmentCtfApply, self).__init__(self.feature_set)
        
        self.apply_ctf_to_segment_stack()
        
# class TestSegmentCtfApplyEndToEnd(TestSegmentCtfApply):
#     def do_end_to_end_test_sca3_inputfile(self):
#         EndToEndTest().do_end_to_end_inputfile(self.feature_set)
#  
#     def do_end_to_end_test_sca4_prompt(self):
#         EndToEndTest().do_end_to_end_prompt(self.feature_set)
#         
#         
# class TestSegmentCtfApplyMpi(TestSegmentCtfApply):
#     def do_end_to_end_test_sa_inputfile_with_MPI(self):
#         self.feature_set.parameters['MPI option'] = True
#         self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
#         
#         EndToEndTest().do_end_to_end_inputfile(self.feature_set)


def main():
    tsca = TestSegmentCtfApplyMain()
    tsca.setup()
    tsca.do_test_case_sca1()
        
if __name__ == '__main__':
    main()
