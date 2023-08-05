#!/usr/bin/env python
"""
Test module to check segmentexam
"""
from EMAN2 import EMNumPy
from fundamentals import image_decimate
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment2d.segmentexam import SegmentExam, SegmentExamPar
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segmentselect import TestSegmentSelect
from spring.tests.segment3d.test_segmentrefine3d import TestSegmentRefine3dSetupForOthers
from utilities import model_gauss_noise
import numpy as np
import os
import shutil


class HelixProjectionPreparation(object):
    def prepare_helix_projection(self):
        """
        * Function to generate a projection of a dummy helix
        """
        self.pixelsize = float(5)
        self.width_of_helix_in_pixel = self.width_of_helix_in_angstrom/self.pixelsize
        self.micrograph_size_in_angstrom = 1000
        
        self.make_empty_segment()
        self.compute_intersect_sine_waves()
        self.add_intersects_to_segment_image()
        self.append_helix_segments_to_stack()
        
    def make_empty_segment(self):
        self.decimation_factor_for_better_layer_lines = 10
        
        self.temporary_segment_size_in_pixels = \
        self.decimation_factor_for_better_layer_lines*self.micrograph_size_in_angstrom/self.pixelsize
        
        self.helix_segment = np.zeros((self.temporary_segment_size_in_pixels, self.temporary_segment_size_in_pixels))

    def compute_intersect_sine_waves(self):
        self.pixels = np.arange(0, self.temporary_segment_size_in_pixels, 0.01)
        
        self.frequency_one = 9
        self.frequency_two = self.frequency_one - 5
        self.sine_wave = []
        for frequency in [self.frequency_one, self.frequency_two]:
            self.sine_wave.append(np.round(self.width_of_helix_in_pixel*2*np.sin(frequency*self.pixels) + \
            self.temporary_segment_size_in_pixels/2, 1))

        self.sine_wave_one = self.sine_wave[0]
        self.sine_wave_two = self.sine_wave[1]

        self.intersect = np.where(np.rint(self.sine_wave_one) == np.rint(self.sine_wave_two))[0]

    def add_intersects_to_segment_image(self):
        for point in self.intersect:
            row = np.rint(self.pixels[point])
            column = np.rint(self.sine_wave_one[point])
            if row < self.temporary_segment_size_in_pixels and column < self.temporary_segment_size_in_pixels:
                self.helix_segment[row][column] = 1

        self.helix_segment_img = EMNumPy.numpy2em(np.copy(self.helix_segment))

        self.helix_segment_img = image_decimate(self.helix_segment_img, self.decimation_factor_for_better_layer_lines,
        fit_to_fft=False)

        self.helix_segment_img.process_inplace('normalize')
        self.helix_segment_img *= 0.1
        
        return self.helix_segment_img
    

    def append_helix_segments_to_stack(self, number=60):
        for segment in list(range(number)):
            self.helix_micrograph = self.helix_segment_img.copy()
            self.add_noise_to_helix_micrograph()
            self.helix_micrograph.append_image('test_segments.hdf')

    def add_noise_to_helix_micrograph(self):
        self.noise = model_gauss_noise(0.1, self.helix_micrograph.get_xsize(), self.helix_micrograph.get_ysize())
        self.helix_micrograph += self.noise

class TestSegmentExam(HelixProjectionPreparation, SegmentExam):
    def setup_segmentrefine3d(self):
        self.tsr3d = TestSegmentRefine3dSetupForOthers()
        self.tsr3d.setup_sr3d()
        os.remove(self.tsr3d.input_stack)

    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = SegmentExamPar()
        self.width_of_helix_in_angstrom = 100
        self.pixelsize = float(5)
        self.width_of_helix_in_pixel = self.width_of_helix_in_angstrom/self.pixelsize
        self.micrograph_size_in_angstrom = 1000
        
        self.prepare_helix_projection()
        self.feature_set.parameters['Image input stack']='test_segments.hdf'
        self.feature_set.parameters['Diagnostic plot']='test_segmentexam.png'
        
        self.feature_set.parameters['spring.db file']=os.path.join(os.pardir, 'spring.db')
            
        self.feature_set.parameters['Power spectrum output image']='test_power.hdf'
        self.feature_set.parameters['Enhanced power spectrum option']=True
        self.feature_set.parameters['Enhanced power spectrum output image']='test_power_enhanced.hdf'
        self.feature_set.parameters['Pixel size in Angstrom']=float(self.pixelsize)
        self.feature_set.parameters['Estimated helix width in Angstrom']=int(1.1*self.width_of_helix_in_angstrom)
        self.feature_set.parameters['Power spectrum resolution cutoff in 1/Angstrom']=float(1/(self.pixelsize*4))
        self.feature_set.parameters['Reference power spectrum']=False
        self.feature_set.parameters['Power spectrum input image']='ref_power.hdf'
        
        self.feature_set.parameters['Compute layer-line correlation option']=False
        self.feature_set.parameters['Layer-line region in 1/Angstrom']=((0.03, 0.04))

        self.tsegsel = TestSegmentSelect()
        self.tsegsel.test_segment_file = 'test.dat'
        self.feature_set = self.tsegsel.setup_selection_criteria_from_segment_table(self.feature_set)
        self.tsegsel.prepare_segment_file()

        self.setup_segmentrefine3d()

        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)

        super(TestSegmentExam, self).__init__(self.feature_set)


    def check_width_of_helix(self):
        assert round(self.width_of_helix_in_angstrom, -2) == round(np.mean(self.widths), -2) or \
            round(self.width_of_helix_in_angstrom - 100, -2) == round(np.mean(self.widths), -2)

        
    def teardown(self):
        os.remove(os.path.join(os.pardir, 'spring.db'))
        os.remove('spring.db')
        os.remove(self.tsegsel.test_segment_file)
        os.remove('test_segments.hdf')
        os.remove('test_segmentexam.png')
        os.remove('test_power.hdf')
        os.remove('test_power_enhanced.hdf')

        self.testingdir.remove()

        
class TestSegmentExamMain(TestSegmentExam):
    def do_test_case_se1(self):
        self.add_up_power_spectra()
        self.check_width_of_helix()


class TestSegmentExamMore(TestSegmentExam):
    def do_test_case_se2(self):
        """
        * Segementexam test with correlate layer-line option
        """
        self.feature_set.parameters['Pixel size in Angstrom']=self.tsr3d.pixelsize
        self.feature_set.parameters['Compute layer-line correlation option']=True
         
        super(TestSegmentExam, self).__init__(self.feature_set)
         
        self.add_up_power_spectra()
        
        
    def do_test_case_se3(self):
        """
        * Segementexam test with correlate layer-line option and reference power spectrum
        """
        self.add_up_power_spectra()
        
        shutil.copy('test_power.hdf', 'ref_power.hdf')
        self.feature_set.parameters['Reference power spectrum']=True
        super(TestSegmentExam, self).__init__(self.feature_set)
        
        self.add_up_power_spectra()
        os.remove('ref_power.hdf')


class TestSegmentExamEndToEnd(TestSegmentExam):
    def do_end_to_end_test_se_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_se_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)

class TestSegmentExamMpi(TestSegmentExam):
    def do_end_to_end_test_sa_inputfile_with_MPI(self):
        self.feature_set.parameters['Compute layer-line correlation option']=True
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs']=2
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        
def main():
    tse = TestSegmentExamMain()
    tse.setup()
    tse.do_test_case_se1()
        
if __name__ == '__main__':
    main()
