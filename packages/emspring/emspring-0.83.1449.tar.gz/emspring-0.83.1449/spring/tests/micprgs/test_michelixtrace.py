#!/usr/bin/env python
"""
Test module to check michelixtrace module
"""
from EMAN2 import EMData
from fundamentals import window2d, rot_shift2D, shift2d
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.micprgs.michelixtrace import MicHelixTrace, MicHelixTracePar
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segment import MicrographHelixPreparation
from utilities import model_circle
import os


class TestMicHelixTracePrepare(object):
    def prepare_micrograph_and_reference(self):
        MicrographHelixPreparation().prepare_ctf_micrograph(self.micrograph_test_file, self.avg_defocus, self.cs,
        self.voltage, self.pixelsize, self.ampcont, self.astigmatism, self.astigmatism_angle)

        left_x, left_y = 88, 80
        img = EMData()
        img.read_image(self.micrograph_test_file)
        shifted_img_zero = shift2d(img, img.get_xsize() / 4.0, img.get_ysize() / 4.0)
        shifted_img_one = shift2d(img, img.get_xsize() / 2, img.get_ysize() / 3)
        shifted_img_two = rot_shift2D(shifted_img_one, 103, 450, 400)
        shifted_img_three = rot_shift2D(shifted_img_one, 33, -350, 100)
        shifted_img_four = rot_shift2D(shifted_img_one, 103, 150, 300)
        new_mic = img + shifted_img_zero + shifted_img_one + shifted_img_two + shifted_img_three + shifted_img_four
        new_mic.write_image(self.micrograph_test_file)
        
        wimg = window2d(img, 150, 150, 'l', left_x, left_y)
        wimg = rot_shift2D(wimg, -45)
        wimg *= model_circle(75, 150, 150)
        wimg.write_image(self.ref_test_image)


    def check_detected_helix_count(self, expected_count=4):
        f = open(self.helix_box_file, 'r')
        helix_count = 0
        for each_line in f.readlines():
            if '-2' in each_line:
                helix_count += 1
        
        print helix_count
        assert helix_count == expected_count


class TestMicHelixTrace(TestMicHelixTracePrepare, MicHelixTrace):
    def setup_of_common_non_mpi_parameters(self):
        self.feature_set = MicHelixTracePar()
        self.micrograph_test_file = 'test_mic.hdf'
        self.test_diagnostic = 'test_diagnostic.png'
        self.helix_box_file = os.path.splitext(self.micrograph_test_file)[0] + os.extsep + 'box'
        self.avg_defocus = 20000
        self.cs = 2.0
        self.voltage = 200.0
        self.pixelsize = 5.0
        self.ampcont = 0.10
        self.astigmatism = 1000
        self.astigmatism_angle = 35.0
        self.ref_test_image = 'test_reference.hdf'

        self.prepare_micrograph_and_reference()
        
        self.feature_set.parameters['Micrographs']=self.micrograph_test_file
        self.feature_set.parameters['Diagnostic plot pattern']=self.test_diagnostic
        self.feature_set.parameters['Helix reference']=self.ref_test_image
            
        self.feature_set.parameters['Pixel size in Angstrom'] = self.pixelsize
        self.feature_set.parameters['Tile size power spectrum in Angstrom'] = 640
        self.feature_set.parameters['Tile overlap in percent']= 80

        self.feature_set.parameters['Binning option'] = True
        self.feature_set.parameters['Binning factor'] = 2
        self.feature_set.parameters['Cross-correlation threshold']= 0.4
        self.feature_set.parameters['Order fit']= 2
        self.feature_set.parameters['Exclude carbon']=True
        self.feature_set.parameters['Hole diameter in micrometer']= 1.3

        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
            
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)

    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()
        
        self.setup_of_common_non_mpi_parameters()
        super(TestMicHelixTrace, self).__init__(self.feature_set)

    def teardown(self):
        pass
        os.remove(self.micrograph_test_file)
        os.remove(self.test_diagnostic)
        os.remove(self.helix_box_file)
        os.remove(self.ref_test_image)
        
        self.testingdir.remove()


class TestMicHelixTraceMain(TestMicHelixTrace):
    def do_test_case_mt1(self):
        """
        Mictrace test to trace filaments using a reference
        """
        self.trace_helices()
        self.check_detected_helix_count(4)


class TestMicHelixTraceMore(TestMicHelixTrace):
    def do_test_case_mt2(self):
        """
        Mictrace test without edge exclusion
        """
        self.feature_set.parameters['Exclude carbon']=False
        super(TestMicHelixTrace, self).__init__(self.feature_set)

        self.trace_helices()
        self.check_detected_helix_count(6)


class TestMicHelixTraceEndToEnd(TestMicHelixTrace):
    def do_end_to_end_test_mt_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_mt_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)


class TestMicHelixTraceMpi(TestMicHelixTrace):
    def do_end_to_end_test_mt_inputfile_with_MPI(self):
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs']=2
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

def main():
    tseg = TestMicHelixTraceMain()
    tseg.setup()
    tseg.do_test_case_mt1()
        
if __name__ == '__main__':
    main()
