#!/usr/bin/env python
"""
Test module to check seglayer2lattice
"""
from EMAN2 import periodogram
from filter import filt_gaussl
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment2d.seglayer2lattice import SegLayer2Lattice, SegLayer2LatticePar
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment3d.test_segclassreconstruct import TestSegClassReconstructPreparation
from utilities import model_gauss_noise
import os


class TestSegLayer2LatticePreparation(TestSegClassReconstructPreparation):
    def prepare_power_spectrum(self):
        self.projection_file = 'test_projection.hdf'
        volume, helix_projection = self.prepare_helical_projection(self.projection_file, self.rotational_sym)
        
        power = periodogram(helix_projection)
        power.write_image(self.power_file)
        
        os.remove(self.projection_file)
        
class TestSegLayer2Lattice(TestSegLayer2LatticePreparation, SegLayer2Lattice):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = SegLayer2LatticePar()
        self.pixelsize = 10.0
        self.helical_rotation = 50.0
        self.helical_rise = 10.0
        self.size_of_subunit_in_angstrom = 20
        self.helix_radius_in_angstrom = 50
        self.volume_size_in_angstrom = 500
        self.helix_offcenter_shift = 4
        self.rotational_sym = 2
                
        self.width_of_helix_in_angstrom = 100
        self.power_file = 'test_power.hdf'
        
        self.prepare_power_spectrum()
        
        self.feature_set.parameters['Analyze power spectrum']=True
        self.feature_set.parameters['Power spectrum input image']=self.power_file
        self.feature_set.parameters['Batch mode']=True
        self.feature_set.parameters['Diagnostic plot']='test_seglayer2lattice.png'
        self.feature_set.parameters['Pixel size in Angstrom']=self.pixelsize
        
        self.feature_set.parameters['High-pass filter option']=False
        self.feature_set.parameters['Low-pass filter option']=False
        self.feature_set.parameters['High and low-pass filter cutoffs in 1/Angstrom']=((0.005, 1/(2*self.pixelsize)))
#        self.feature_set.parameters['High and low-pass filter cutoffs in 1/Angstrom']=((0.005, 0.04))
        
        self.feature_set.parameters['Precise helix width in Angstrom']=int(self.width_of_helix_in_angstrom)
        self.feature_set.parameters['Layer line/Bessel order or helical rise/rotation choice']='rise/rotation'
        
        self.feature_set.parameters['Layer line/Bessel or rise/rotation pair(s)']='({rise}, {rotation})'.\
        format(rise=self.helical_rise, rotation=self.helical_rotation)
        self.feature_set.parameters['Rotational symmetry']=self.rotational_sym

        super(TestSegLayer2Lattice, self).__init__(self.feature_set)


    def teardown(self):
        os.remove('test_seglayer2lattice.png')
        os.remove(self.power_file)
        pass

        self.testingdir.remove()


class TestSegLayer2LatticeMain(TestSegLayer2Lattice):
    def do_test_case_sl2l_1(self):
        """
        * Test standard rise/rotation pair
        """
        self.plot_layer_lines_to_power_and_lattice()


class TestSegLayer2LatticeMore(TestSegLayer2Lattice):
        
    def do_test_case_sl2l_2(self):
        """
        * Test pitch/unit_number
        """
        self.feature_set.parameters['Layer line/Bessel order or helical rise/rotation choice']='pitch/unit_number'
        self.feature_set.parameters['Layer line/Bessel or rise/rotation pair(s)']='({0}, {1})'.format(23, 16.34)
        self.feature_set.parameters['Rotational symmetry']=1
        
        super(TestSegLayer2Lattice, self).__init__(self.feature_set)
        
        self.plot_layer_lines_to_power_and_lattice()
        
        
    def do_test_case_sl2l_3(self):
        """
        * Test layer/bessel pair
        """
        self.feature_set.parameters['Layer line/Bessel order or helical rise/rotation choice']='layer/bessel'
        self.feature_set.parameters['Layer line/Bessel or rise/rotation pair(s)']='(0.014, 1); (0.028, -2); (0.042, 3)'
        
        super(TestSegLayer2Lattice, self).__init__(self.feature_set)
        
        self.plot_layer_lines_to_power_and_lattice()
        
        
    def do_test_case_sl2l_4(self):
        """
        * Test without filters
        """
        self.feature_set.parameters['High-pass filter option']=False
        self.feature_set.parameters['Low-pass filter option']=False
        
        super(TestSegLayer2Lattice, self).__init__(self.feature_set)
        
        self.plot_layer_lines_to_power_and_lattice()
        
        
class TestSegLayer2LatticeEndToEnd(TestSegLayer2Lattice):
    def do_end_to_end_test_scl_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_scl_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)

class TestSegLayerMask(object):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.noise_img = model_gauss_noise(1, 200,200)
        self.filter_noise_img = filt_gaussl(self.noise_img, 0.2)
    
        layerline_bessel_pairs = SegClassReconstruct().generate_layerline_bessel_pairs_from_rise_and_rotation((1.408,
        22.03), 1, 180, 5.0, 300, 10)
        
        self.ideal_power_img, linex_fine = \
        SegClassReconstruct().prepare_ideal_power_spectrum_from_layer_lines(layerline_bessel_pairs, 180, 200, 5.0)
        
    def do_test_masking(self):
        hybrid_img = self.noise_img.filter_by_image(self.ideal_power_img)
        hybrid_img.write_image('hybrid_img.hdf')
        self.filter_noise_img.write_image('filter_noise.hdf')
        
    def teardown(self):
        os.remove('hybrid_img.hdf')
        os.remove('filter_noise.hdf')
        
        self.testingdir.remove()

    
def main():
    tscl = TestSegLayer2LatticeMain()
    tscl.setup()
    tscl.do_test_case_sl2l_1()
        
if __name__ == '__main__':
    main()
