#!/usr/bin/env python
"""
Test module to check segclasslayer
"""
import os
from statistics import add_series
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment2d.segclasslayer import SegClassLayer, SegClassLayerPar
from spring.tests.segment2d.test_segmentexam import HelixProjectionPreparation
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest


class HelixSingleClassPreparation(HelixProjectionPreparation):
    def prepare_helix_class(self):
        """
        * Function to generate a projection of 4 classes
        """
        self.width_of_helix_in_angstrom = 200
        self.prepare_helix_projection()
        self.helix_class_average, self.helix_class_variance = add_series('test_segments.hdf')
        self.class_average = 'test_class_avg_segments.hdf'
        self.helix_class_average.append_image(self.class_average)
        self.class_variance = 'test_class_var_segments.hdf'

class TestSegClassLayer(HelixSingleClassPreparation, SegClassLayer):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = SegClassLayerPar()
        self.prepare_helix_class()

        self.feature_set.parameters['Class average stack']=self.class_average
        self.feature_set.parameters['Batch mode']=True#
        self.feature_set.parameters['Diagnostic plot']='test_segclasslayer.png'
        self.feature_set.parameters['Class format']='real'
        self.feature_set.parameters['Pixel size in Angstrom']=float(self.pixelsize)
        self.feature_set.parameters['Precise helix width in Angstrom']=int(1.1*self.width_of_helix_in_angstrom)
        self.feature_set.parameters['Power spectrum resolution cutoff in 1/Angstrom']=float(1/(self.pixelsize*8))
        self.feature_set.parameters['Class number range to be analyzed']=((0, 0))
        self.feature_set.parameters['Layer line positions']='0.014, 0.029'
        self.feature_set.parameters['Pad option']=bool(True)

        super(TestSegClassLayer, self).__init__(self.feature_set)


    def teardown(self):
        os.remove('test_segments.hdf')
        os.remove(self.class_average)

        if os.path.splitext(self.feature_set.parameters['Diagnostic plot'])[-1].endswith('pdf'):
            os.remove('test_segclasslayer.pdf')
        else:
            os.remove('test_segclasslayer.png')
        os.remove('test_class_avg_segments4binned.hdf')

        self.testingdir.remove()


class TestSegClassLayerMain(TestSegClassLayer):
    def do_test_case_scl1(self):
        self.extract_and_visualize_layer_lines()


class TestSegClassLayerMore(TestSegClassLayer):
    def do_test_case_scl2(self):
        self.prepare_helix_class()
        self.feature_set.parameters['Class number range to be analyzed']=((0, 100))
        self.feature_set.parameters['Diagnostic plot']='test_segclasslayer.pdf'
        super(TestSegClassLayer, self).__init__(self.feature_set)
        
        self.extract_and_visualize_layer_lines()
        

class TestSegClassLayerEndToEnd(TestSegClassLayer):
    def do_end_to_end_test_scl_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_scl_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)

def main():
    tscl = TestSegClassLayerMain()
    tscl.setup()
    tscl.do_test_case_scl1()
        
if __name__ == '__main__':
    main()
