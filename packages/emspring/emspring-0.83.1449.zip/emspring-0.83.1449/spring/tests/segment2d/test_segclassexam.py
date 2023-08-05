#!/usr/bin/env python
"""
Test module to check segclassexam
"""
from glob import glob
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment2d.segclassexam import SegClassExam, SegClassExamPar
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segmentexam import HelixProjectionPreparation
from statistics import add_series
import os


class HelixClassAvgPreparation(HelixProjectionPreparation):
    def prepare_helix_class_averages_and_variances(self):
        """
        * Function to generate a projection of one class
        """
        self.width_of_helix_in_angstrom = 200
        self.prepare_helix_projection()

        self.average =  'test_averages.hdf' 
        self.variance = 'test_variances.hdf'

        self.avg, self.var = add_series('test_segments.hdf')
        self.avg.append_image(self.average)
        self.var.append_image(self.variance)

class TestSegClassExam(HelixClassAvgPreparation, SegClassExam):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = SegClassExamPar()
        self.prepare_helix_class_averages_and_variances()

        self.feature_set.parameters['Class average stack']=self.average
        self.feature_set.parameters['Diagnostic plot']='test_segclassexam.png'
        self.feature_set.parameters['Class variance option']=True
        self.feature_set.parameters['Class variance stack']=self.variance
        
        self.feature_set.parameters['Power spectrum output image']='test_power.hdf'
        self.feature_set.parameters['Enhanced power spectrum option']=True
        self.feature_set.parameters['Enhanced power spectrum output image']='test_power_enhanced.hdf'
        self.feature_set.parameters['Pixel size in Angstrom']=self.pixelsize
        self.feature_set.parameters['Estimated helix width in Angstrom']=int(1.2*self.width_of_helix_in_angstrom)
        self.feature_set.parameters['Power spectrum resolution cutoff in 1/Angstrom']=float(1/(self.pixelsize*8))
        self.feature_set.parameters['Class number range to be analyzed']=((0, 0))

        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)

        super(TestSegClassExam, self).__init__(self.feature_set)

    def teardown(self):
        os.remove(self.average)
        os.remove(self.avgstack)
        os.remove(self.variance)
        if self.feature_set.parameters['Class variance option']:
            os.remove(self.varstack)
        diagnostic_files = glob('test_segclassexam*')
        for each_file in diagnostic_files:
            os.remove(each_file)
        os.remove('test_segments.hdf')
        os.remove('test_power.hdf')
        os.remove('test_power_enhanced.hdf')
        
        self.testingdir.remove()

        
class TestSegClassExamMain(TestSegClassExam):
    def do_test_case_sce1(self):
        self.exam_classes()


class TestSegClassExamMore(TestSegClassExam):
    def do_test_case_sce2(self):
        self.prepare_helix_class_averages_and_variances()
        self.prepare_helix_class_averages_and_variances()
        self.feature_set.parameters['Diagnostic plot']='test_segclassexam.pdf'
        self.feature_set.parameters['Class number range to be analyzed']=((0, 200))
        super(TestSegClassExam, self).__init__(self.feature_set)

        self.exam_classes()
        

    def do_test_case_sce3(self):
        self.feature_set.parameters['Class variance option']=False
        self.feature_set.parameters['Class variance stack']=self.variance

        super(TestSegClassExam, self).__init__(self.feature_set)

        self.exam_classes()


class TestSegClassExamEndToEnd(TestSegClassExam):
    def do_end_to_end_test_sce_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_sce_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)


class TestSegClassExamMpi(TestSegClassExam):
    def do_end_to_end_test_sa_inputfile_with_MPI(self):
        self.prepare_helix_class_averages_and_variances()
        self.prepare_helix_class_averages_and_variances()
        self.feature_set.parameters['Diagnostic plot']='test_segclassexam.pdf'
        self.feature_set.parameters['Class number range to be analyzed']=((0, 2))
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs']=2
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        
def main():
    tsce = TestSegClassExamMain()
    tsce.setup()
    tsce.do_test_case_sce1()
        
if __name__ == '__main__':
    main()
