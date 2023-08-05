#!/usr/bin/env python
"""
Test module to check segclassreconstruct
"""
from EMAN2 import EMData, Transform
from fundamentals import fshift, rot_shift2D
from glob import glob
from multiprocessing import cpu_count
from nose.tools import raises
from projection import prj
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.micprgs.scansplit import Micrograph
from spring.segment3d.segclassreconstruct import SegClassReconstructPar, SegClassReconstruct
from spring.springgui.spring_launch import DataBaseUpdate
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from utilities import model_circle, model_gauss_noise, model_square
import os
import sys

class TestSegClassReconstructPreparation(object):

    def shift_volume_and_helicise(self, pixelsize, helix_radius_in_angstrom, helical_rise, helical_rotation, vol):
        helix_radius = helix_radius_in_angstrom / pixelsize
        subunit_volume = fshift(vol, helix_radius)
        helix_volume = subunit_volume.helicise(pixelsize, helical_rise, -helical_rotation, 0.8)
        return helix_volume


    def generate_helical_volume_square(self, size_of_subunit_in_angstrom, pixelsize, larger_dimension,
    helix_radius_in_angstrom, helical_rise, helical_rotation):
        radius = size_of_subunit_in_angstrom/(2*pixelsize)
        s = model_square(radius, larger_dimension, larger_dimension, larger_dimension)
        t1 = Transform({'type':'spider', 'psi':33, 'theta':100, 'phi':77, 'scale':1.0})
        small_radius = radius/2.0
        ss = model_square(small_radius, larger_dimension, larger_dimension, larger_dimension)
        ss.transform(t1)
        vol = s - ss
        
        helix_volume = self.shift_volume_and_helicise(pixelsize, helix_radius_in_angstrom, helical_rise,
        helical_rotation, vol)
        
#        helix_volume.write_image('test_helix.hdf')
        
        return helix_volume


    def generate_helical_volume(self, size_of_subunit_in_angstrom, pixelsize, larger_dimension,
    helix_radius_in_angstrom, helical_rise, helical_rotation):
        radius = size_of_subunit_in_angstrom/(2*pixelsize)
        vol = model_circle(radius, larger_dimension, larger_dimension, larger_dimension)
        
        helix_volume = self.shift_volume_and_helicise(pixelsize, helix_radius_in_angstrom, helical_rise,
        helical_rotation, vol)
        
#        helix_volume.write_image('test_helix.hdf')
        
        return helix_volume


    def generate_noise_projections_from_helix(self, projection_file, helix_volume, projection_parameters):
        
        helical_projections = prj(helix_volume, projection_parameters)
        
        larger_dimension = helix_volume.get_xsize()
        noise_projections = []
        for each_segment_index, each_helical_projection in enumerate(helical_projections):
            stat = Micrograph().get_statistics_from_image(each_helical_projection)
            noise = model_gauss_noise(0.5 * stat.sigma, larger_dimension, larger_dimension)
            each_helical_projection += noise
            noise_projections.append(each_helical_projection)
            if projection_file is not None:
                each_helical_projection.write_image(projection_file, each_segment_index)

        return noise_projections
    
    
    def prepare_helical_projection(self, projection_file, rotational_sym=1):
        length_of_helix_in_pixels = int(self.volume_size_in_angstrom/self.pixelsize)
        self.percent_reconstruction_size = 50
        larger_dimension = int(round(100*length_of_helix_in_pixels/self.percent_reconstruction_size, -1))
        phi = 0; theta = 90; psi = 270; shift_x = 0; shift_y = 0
        projection_parameters = [[phi, theta, psi, shift_x, shift_y]]
        
        helix_volume = self.generate_helical_volume(self.size_of_subunit_in_angstrom, self.pixelsize, larger_dimension,
        self.helix_radius_in_angstrom, self.helical_rise, self.helical_rotation)
        
        if rotational_sym > 1:
            helix_volume = helix_volume.symvol('c{0}'.format(rotational_sym))
        
        projections = self.generate_noise_projections_from_helix(projection_file, helix_volume, projection_parameters)
        self.helical_projection = projections[0]
        
        return helix_volume, self.helical_projection
        
    def setup_of_common_non_mpi_parameters(self):
        self.pixelsize = 10.0
        self.projection_file = 'test_projection.hdf'
        
        self.grid_volume_name = 'grid_volume_name.hdf'
        self.test_mont_reprojection_stack = 'test_mont_repr.hdf'
        self.test_mont_power_stack = 'test_mont_power.hdf'
        self.helical_rise = 10.0
        self.helical_rise_increment = 4.0
        self.helical_rotation = 50.0
        self.helical_rotation_increment = 15.0
        self.size_of_subunit_in_angstrom = 20
        self.helix_radius_in_angstrom = 50
        self.volume_size_in_angstrom = 500
        self.helix_offcenter_shift = 4
        self.helix_rotation = 6
        
        self.prepare_helical_projection(self.projection_file)
        self.feature_set.parameters['Class average stack'] = self.projection_file
        self.feature_set.parameters['Volume name']=self.grid_volume_name
#        self.feature_set.parameters['Image output stack'] = self.reprojection_file
        self.feature_set.parameters['Keep intermediate files']=True
        self.feature_set.parameters['Montage stack of class average vs. reprojection ' + \
        'images']=self.test_mont_reprojection_stack
        
        self.feature_set.parameters['Montage stack of class average vs. reprojection power ' + \
        'spectra']=self.test_mont_power_stack
        
        self.feature_set.parameters['Class number to be analyzed'] = 0
        self.feature_set.parameters['Pixel size in Angstrom'] = self.pixelsize
        
        self.feature_set.parameters['Estimated helix inner and outer diameter in ' + \
        'Angstrom']=((int(0.5*self.helix_radius_in_angstrom), int(3.3*self.helix_radius_in_angstrom)))
        
        self.feature_set.parameters['Helical rise/rotation or pitch/number of units per turn choice']='rise/rotation'
        
        self.feature_set.parameters['Range of helical rise or pitch search in Angstrom'] = (self.helical_rise - \
        self.helical_rise_increment, self.helical_rise + self.helical_rise_increment)
        
        self.feature_set.parameters['Range of helical rotation in degrees or number of units per turn search'] = \
        (self.helical_rotation - self.helical_rotation_increment, self.helical_rotation +
        self.helical_rotation_increment)
        
        self.feature_set.parameters['Increments of helical symmetry steps in Angstrom or degrees'] = \
        (self.helical_rise_increment, self.helical_rotation_increment/3)
        
        self.feature_set.parameters['Rotational symmetry']=1
        self.feature_set.parameters['Helix polarity']='polar'
        self.feature_set.parameters['Out-of-plane tilt angle']=0
        
        self.feature_set.parameters['Percent of image reconstruction size'] = self.percent_reconstruction_size
        self.feature_set.parameters['Minimum number of images for 3D reconstruction']=int(8)
        self.feature_set.parameters['Center option']=True
        self.feature_set.parameters['Local symmetry grid search']=False
        
        
class TestSegClassReconstruct(TestSegClassReconstructPreparation, SegClassReconstruct):

    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = SegClassReconstructPar()
        self.setup_of_common_non_mpi_parameters()
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)
            
        super(TestSegClassReconstruct, self).__init__(self.feature_set)
        
    def produce_a_projection_of_final_volume(self):
        symmetry_helix_volume = self.get_symmetry_file_name((self.helical_rise, self.helical_rotation), self.volume_name)
        last_volume = EMData()
        last_volume.read_image(symmetry_helix_volume)
        
        projection_parameters = [[0., 90., 270., 0., 0.]]
        helical_projections = self.project_locally(last_volume, projection_parameters, self.volume_name)
        

    def teardown(self):
        files_to_be_deleted = [self.projection_file, self.test_mont_power_stack, self.test_mont_reprojection_stack,
        'grid.db']

        files_to_be_deleted +=glob('{0}*'.format(os.path.splitext(self.grid_volume_name)[0]))
        for each_file in files_to_be_deleted:
            os.remove(each_file)
        
        if self.feature_set.parameters['Center option'] is True:
            centered_class_avg = '{0}_centered{1}'.format(os.path.splitext(self.projection_file)[0],
            os.path.splitext(self.projection_file)[-1])
            
            os.remove(centered_class_avg)

        self.testingdir.remove()


class TestSegClassReconstructMain(TestSegClassReconstruct):
    def do_test_case_cr1(self):
        self.perform_reconstructions_from_class_for_symmetry_combinations()
         
        self.produce_a_projection_of_final_volume()
            

class TestSegClassReconstructMore(TestSegClassReconstruct):
    def check_and_remove_symgrid_volumes(self, grid_volume_name):
        for each_symmetry_pair in self.symmetry_sequence:
            symgrid_volume = self.generate_symmetry_grid_file_name(each_symmetry_pair, grid_volume_name,
            self.rise_rot_or_pitch_unit_choice)
            
            assert os.path.isfile(symgrid_volume)
    
    @raises(ValueError)
    def do_impossible_crtest(self):
        self.percent_reconstruction_size = 99
        self.perform_reconstructions_from_class_for_symmetry_combinations()
        
    def do_test_case_cr0(self):
        self.perform_reconstructions_from_class_for_symmetry_combinations()
         
        self.produce_a_projection_of_final_volume()
        DataBaseUpdate().update_grid_db('grid.db', 'grid_up.db')
        os.remove('grid_up.db')
            
    def do_test_case_cr2(self):
        self.helical_projection = rot_shift2D(self.helical_projection, self.helix_rotation, self.helix_offcenter_shift, 0)
        self.helical_projection.write_image(self.projection_file)
        
        self.perform_reconstructions_from_class_for_symmetry_combinations()
        sys.stderr.write('\n{0} == {1}'.format(self.helix_offcenter_shift, -self.centerx))
        sys.stderr.write('\n{0} == {1}'.format(self.helix_rotation, -self.inplane_rotation))
#        assert self.helix_offcenter_shift == -(int(round(self.centerx)) - 1)
#        assert self.helix_rotation == int(-self.inplane_rotation + 0.5)
        
        self.check_and_remove_symgrid_volumes(self.grid_volume_name)
    
        
    def do_test_case_cr3(self):
        self.feature_set.parameters['Local symmetry grid search']=True
        super(TestSegClassReconstruct, self).__init__(self.feature_set)
        self.perform_reconstructions_from_class_for_symmetry_combinations()
        
        
class TestSegClassReconstructEndtoEnd(TestSegClassReconstruct):
    def do_end_to_end_test_cr_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
 
    def do_end_to_end_test_cr_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        
class TestSegClassReconstructMpi(TestSegClassReconstruct):
    def do_end_to_end_test_sa_inputfile_with_MPI(self):
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

def main():
    trc = TestSegClassReconstructMain()
    trc.setup()
    trc.do_test_case_cr1()
        
if __name__ == '__main__':
    main()
