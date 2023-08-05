#!/usr/bin/env python
"""
Test module to check segclassmodel
"""
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment3d.refine.sr3d_main import SegmentRefine3d
from spring.segment3d.segclassmodel import SegClassModelPar, SegClassModel
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segmentclass import HelixClassPreparation
from spring.tests.segment3d.test_segclassreconstruct import TestSegClassReconstructPreparation
from spring.tests.segment3d.test_segmentrefine3d import TestSegmentRefine3dClean, TestSegmentRefine3dPreparationDatabase
import numpy as np
import os
import random


class TestSegClassModelPreparation(object):
    def generate_series_of_volumes(self):
        segment_size = int(self.volume_size_in_angstrom/self.pixelsize)
        class_stack = []
        prj_params = []
        for each_rise_rotation, each_radius, each_model in zip(self.symmetries, self.helix_radii_in_angstrom, self.models):
            helical_rise, helical_rotation = each_rise_rotation
            complete_euler = SegmentRefine3d().generate_Euler_angles_for_projection(self.azimuthal_count,
            self.out_of_plane_range, self.out_of_plane_count, helical_rotation)
        
            helix_volume =\
            TestSegClassReconstructPreparation().generate_helical_volume_square(self.size_of_subunit_in_angstrom,
            self.pixelsize, segment_size, each_radius, helical_rise, helical_rotation)
            
            helix_volume = SegClassReconstruct().set_header_with_helical_parameters(each_rise_rotation, helix_volume,
            'c{0}'.format(self.helix_start))
            helix_volume.write_image(each_model)
            
            random_prj_params = [complete_euler[random.randint(0, len(complete_euler) - 1)] for each in list(range(3))]
            prj_params.append(random_prj_params)
            class_stack += TestSegClassReconstructPreparation().generate_noise_projections_from_helix(None,
            helix_volume, random_prj_params)

        coord = np.arange(len(prj_params) * 10 * self.pixelsize)
        coordinates = ((coord, coord))
        TestSegmentRefine3dPreparationDatabase().prepare_database_for_refinement(np.vstack(prj_params), self.pixelsize,
        coordinates)

        for each_id, each_class in enumerate(class_stack):
            each_class.write_image(self.test_averages, each_id)
        
        
class TestSegClassModelSetup(TestSegClassModelPreparation):
    def setup_main_segclassmodel_params(self):
        self.size_of_subunit_in_angstrom = 50
        self.helix_radii_in_angstrom = [25, 50, 50]
        self.width_of_helix_in_angstrom = max(self.helix_radii_in_angstrom)
        self.symmetries = [(8, 40), (10, 50), (12, 60)]
        self.models = ['model{0:03}.hdf'.format(each_model) for each_model in list(range(3))]
        self.volume_size_in_angstrom = 400
        
        self.test_averages = 'test_averages.hdf'
        self.x_translation = 50
        self.y_translation = 10
        self.azimuthal_count = 3
        self.out_of_plane_range = (-8, 8)
        self.out_of_plane_count = 3
        self.helix_start = 1
        self.pixelsize = 10.0


    def setup_common_non_mpi_parameters(self):
        self.custom_filter_file = 'test_filter_file.dat'
        self.test_bin_factor = 2
        HelixClassPreparation().prepare_custom_filter_file(self.custom_filter_file, self.test_bin_factor)
        self.generate_series_of_volumes()

        self.feature_set.parameters['Class average stack'] = self.test_averages
        self.feature_set.parameters['Reference volumes']='model00?.hdf'
        
        self.feature_set.parameters['spring.db file']=os.path.join(os.pardir, 'spring.db')
        
        self.feature_set.parameters['Classes select option']=False
        self.feature_set.parameters['Include or exclude classes']='exclude'           
        self.feature_set.parameters['Classes list']='3, 4' 

        self.feature_set.parameters['Limit in-plane rotation']=True
        self.feature_set.parameters['Delta in-plane rotation angle']=10.0
        self.feature_set.parameters['X and Y translation range in Angstrom']=((self.x_translation, self.y_translation))
        self.feature_set.parameters['Out-of-plane tilt angle range']=self.out_of_plane_range

        self.feature_set.parameters['Number of projections azimuthal/out-of-plane angle']=((self.azimuthal_count,
        self.out_of_plane_count))

        self.feature_set.parameters['Keep intermediate files']=False

        self.feature_set.parameters['Pixel size in Angstrom'] = float(self.pixelsize)
        self.feature_set.parameters['Estimated helix width and height in Angstrom'] = ((self.width_of_helix_in_angstrom,
        int(1.5 * self.width_of_helix_in_angstrom)))

        self.feature_set.parameters['Internal binning factor'] = self.test_bin_factor

        self.feature_set.parameters['Limit in-plane rotation'] = True
        self.feature_set.parameters['Delta in-plane rotation angle'] = 10.0
        self.feature_set.parameters['X and Y translation range in Angstrom'] = (20, 15)
        self.feature_set.parameters['High-pass filter option'] = False
        self.feature_set.parameters['Low-pass filter option'] = False
        self.feature_set.parameters['High and low-pass filter cutoffs in 1/Angstrom'] = (0.01, 0.06)
        self.feature_set.parameters['Custom filter option'] = False
        self.feature_set.parameters['Custom-built filter file'] = self.custom_filter_file
        self.feature_set.parameters['B-Factor']=0

        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=1
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)
            

class TestSegClassModel(TestSegClassModelSetup, SegClassModel):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = SegClassModelPar()
        self.setup_main_segclassmodel_params()
        self.setup_common_non_mpi_parameters()
        
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())

        super(TestSegClassModel, self).__init__(self.feature_set)


    def teardown(self):
        os.remove(self.custom_filter_file)
        os.remove(self.test_averages)
        [os.remove(each_file) for each_file in self.models if os.path.exists(each_file)]
        os.remove('spring.db')
        os.remove(os.path.join(os.pardir, 'spring.db'))
        
        self.testingdir.remove()


class TestSegClassModelMain(TestSegClassModel):

    def do_test_case_scm1(self):
        """
        * Standard single-CPU segclassmodel test
        """
        self.match_reprojections_to_classes()
        TestSegmentRefine3dClean().prepare_final_prj_for_documentation(self.models)


class TestSegClassModelMore(TestSegClassModel):
    def do_test_case_scm2(self):
        """
        * Single-CPU segclassmodel test including class selection
        """
        self.feature_set.parameters['Classes select option']=True
        super(TestSegClassModel, self).__init__(self.feature_set)
        self.match_reprojections_to_classes()


class TestSegClassModelEndToEnd(TestSegClassModel):
    def do_end_to_end_test_scm_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_scm_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)


class TestSegClassModelMpi(TestSegClassModel):
    def do_end_to_end_test_scm_inputfile_MPI(self):

        self.feature_set.parameters['MPI option']=True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)


def main():
    tsce = TestSegClassModelMain()
    tsce.setup()
    tsce.do_test_case_scm1()
        
if __name__ == '__main__':
    main()
