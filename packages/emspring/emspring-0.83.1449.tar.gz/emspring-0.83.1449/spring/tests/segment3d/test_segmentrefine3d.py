#!/usr/bin/env python
"""
Test module to check segmentrefine3d
"""
from EMAN2 import EMData, EMUtil, Util, Transform
from fundamentals import rot_shift2D, image_decimate
from glob import glob
from morphology import ctf_img
from multiprocessing import cpu_count
from projection import prj
from spring.csinfrastr.csdatabase import SpringDataBase, base, CtfMicrographTable, HelixTable, SegmentTable, \
    CtfFindMicrographTable, CtfTiltMicrographTable, refine_base, RefinementCycleTable
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment2d.segment import Segment
from spring.segment2d.segmentalign2d import SegmentAlign2d
from spring.segment3d.refine.sr3d_diagnostics import EulerPlot
from spring.segment3d.refine.sr3d_main import SegmentRefine3d, SegmentRefine3dPar
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from spring.springgui.spring_launch import DataBaseUpdate
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment3d.test_segclassreconstruct import TestSegClassReconstructPreparation
from sqlalchemy.sql.expression import desc
from statistics import ccc
from utilities import set_params_proj, generate_ctf, get_params_proj, model_circle, model_blank, compose_transform2, \
    model_gauss_noise, model_square
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import shutil
import sys


class TestSegmentRefine3dPreparationDatabase(object):
    def setup_micrograph(self, pixelsize):
        micrograph = CtfMicrographTable()
        micrograph.amplitude_contrast = 0.1
        micrograph.ctffind_determined = True
        micrograph.ctftilt_determined = True
        micrograph.dirname = os.path.abspath(os.curdir)
        micrograph.micrograph_name = 'test_mic.hdf'
        micrograph.pixelsize = pixelsize
        micrograph.spherical_aberration = 2.0
        micrograph.voltage = 200
    
        ctffind_mic = CtfFindMicrographTable()
        ctffind_mic.dirname = os.path.abspath(os.curdir)
        ctffind_mic.micrograph_name = 'test_mic.hdf'
        ctffind_mic.pixelsize = pixelsize
        ctffind_mic.defocus_avg = 15000
        ctffind_mic.defocus1 = 12500
        ctffind_mic.defocus2 = 17500
        ctffind_mic.astigmation_angle = 35
        ctffind_mic.cc_score = 3233
        ctffind_mic.ctf_micrographs = micrograph
        
        ctftilt_mic = CtfTiltMicrographTable()
        ctftilt_mic.defocus_avg = 15500
        ctftilt_mic.defocus1 = 13000
        ctftilt_mic.defocus2 = 18000
        ctftilt_mic.astigmation_angle = 40
        ctftilt_mic.tilt_angle = 0
        ctftilt_mic.tilt_axis= 135.10
        ctftilt_mic.center_x = 500
        ctftilt_mic.center_y = 500
        
        ctftilt_mic.ctffind_ids = ctffind_mic
        ctftilt_mic.ctf_micrographs = micrograph
        
        return micrograph, ctftilt_mic
    
    
    def setup_helix(self, parameters, micrograph, pixelsize, inplane_angles, max_dist):
        phi, theta, psi, shift_x, shift_y = np.hsplit(parameters, 5)
        
        helix = HelixTable()
        helix.avg_curvature = abs(random.gauss(0.001, 0.001))
        helix.avg_inplane_angle = inplane_angles.mean()
        helix.avg_theta = theta.mean()
        helix.dirname = os.path.abspath(os.path.curdir)
        helix.helix_name = 'helix1'
        helix.micrographs = micrograph
        helix.length = max_dist
        helix.ccc_layer_position_start = 0.1
        helix.ccc_layer_position_end = 0.3
        
        return helix
        
    
    def setup_segments(self, seg_id, parameters, micrograph, helix, pixelsize, coord, ip_angle, dist):
        phi, theta, psi, shift_x, shift_y = np.hsplit(parameters, 5)
        
        segment = SegmentTable()
        segment.astigmation_angle = random.randint(0,180)
        segment.astigmatism = abs(random.gauss(0, 1000))
        segment.avg_defocus = abs(random.gauss(20000, 5000))
        segment.ccc_layer = random.gauss(0.5, 0.1)
        segment.ccc_prj = random.gauss(0.5, 0.1)
        segment.class_id = random.randint(0, 3)
        segment.class_model_id = random.randint(0, 3)
        segment.ctffind_applied = False
        segment.ctftilt_applied = True
        segment.ctf_convolved = True
        segment.ctf_phase_flipped = False
        segment.curvature = abs(random.gauss(0.001, 0.001))
        segment.inplane_angle = ip_angle
        x_coord, y_coord = coord
        segment.second_order_fit = None #1.0e-02
        segment.x_coordinate_A = x_coord
        segment.y_coordinate_A = y_coord
        segment.picked_x_coordinate_A = x_coord + (20 * pixelsize)
        segment.picked_y_coordinate_A = y_coord
        segment.distance_from_start_A = dist
        segment.lavg_inplane_angle = ip_angle
        segment.psi = psi
        segment.theta = theta
        segment.phi = phi
        segment.stack_id = seg_id
        segment.helices = helix
        segment.micrographs = micrograph
    
        return segment
    
        
    def compute_inplane_angles_and_distance_from_start(self, x_coordinates, y_coordinates):
        x_y_coord = zip(x_coordinates, y_coordinates)
        
        inplane_angles = (-np.rad2deg(np.arctan(np.diff(x_coordinates) / np.diff(y_coordinates)))) % 360
        inplane_angles = np.append(inplane_angles, inplane_angles[-1])
        
        distances = np.sqrt(np.diff(x_coordinates) ** 2 + np.diff(y_coordinates) ** 2)
        distances = np.insert(distances, 0, 0)
        distance_from_start = np.cumsum(distances)
        
        return x_y_coord, inplane_angles, distance_from_start


    def add_parameters_to_segment(self, parameters, pixelsize, session, micrograph, helix, x_y_coord, inplane_angles,
    distance_from_start, start_id=0):
        for seg_id, each_param_set in enumerate(parameters):
            coord = x_y_coord[seg_id]
            ip_angle = inplane_angles[seg_id]
            dist = distance_from_start[seg_id]

            segment = self.setup_segments(seg_id + start_id, each_param_set, micrograph, helix, pixelsize, coord,
            ip_angle, dist)

            session.add(segment)
        
        return session
    

    def prepare_database_for_refinement(self, parameters, pixelsize, coordinates, start_id=0):
        """
        >>> from spring.tests.segment3d.test_segmentrefine3d import TestSegmentRefine3dPreparationDatabase
        >>> tsar = TestSegmentRefine3dPreparationDatabase()
        >>> tsar.prepare_database_for_refinement(np.array([[33, 90, 0, 1, 2], [34, 90, 135, -1, -2]]), 5, ((np.arange(2), np.arange(2))))
        >>> if os.path.isfile(os.path.join(os.path.pardir, 'spring.db')): os.remove(os.path.join(os.path.pardir, 'spring.db'))
        """
        session = SpringDataBase().setup_sqlite_db(base, os.path.join(os.pardir, 'spring.db'))
        
        micrograph, ctftilt_mic = self.setup_micrograph(pixelsize)
        session.add(ctftilt_mic)
        
        x_coordinates, y_coordinates = coordinates
        
        x_y_coord, inplane_angles, distance_from_start =\
        self.compute_inplane_angles_and_distance_from_start(x_coordinates, y_coordinates)
        
        helix = self.setup_helix(parameters, micrograph, pixelsize, inplane_angles, max(distance_from_start))
        
        session = self.add_parameters_to_segment(parameters, pixelsize, session, micrograph, helix, x_y_coord,
        inplane_angles, distance_from_start, start_id)
        
        session.commit()
            
        
class TestSegmentRefine3dPreparation(TestSegmentRefine3dPreparationDatabase):
    def apply_random_rotations_x_and_y_shifts_to_projection_parameters(self, projection_parameters, x_range):
        perturbed_parameters = np.zeros((len(projection_parameters), 5))
        for each_projection_index, (each_phi, each_theta, each_psi, each_x, each_y) in enumerate(projection_parameters):
            if each_projection_index <= len(projection_parameters) / 2:
                inplane_angle = 45.0
            else:
                inplane_angle = 45.0# + 90.0
                
            each_psi = 270 + inplane_angle 

            each_x, each_y = SegClassReconstruct().compute_sx_sy_from_shifts_normal_and_parallel_to_helix_axis_with_inplane_angle(0.5*x_range, 0, -inplane_angle)
#            each_x = 4.0
#            each_y = -2.0

            perturbed_parameters[each_projection_index]=np.array([each_phi, each_theta, each_psi, each_x, each_y], dtype=float)
        
        return perturbed_parameters
            
            
    def generate_3d_ctf_file(self, ctf_3d, volume_dimension):
        
        avg_defocus=20000.0
        voltage=200
        cs=2.0
        ampcont=0.1
        
        ctf = generate_ctf([avg_defocus, cs, voltage, self.pixelsize, 0, ampcont])
        
        ctf_volume = ctf_img(volume_dimension, ctf, 1, volume_dimension, volume_dimension)
        ctf_volume.write_image(ctf_3d)
        
    
    def clean_projection_parameters_from_input_stack(self, input_stack):
        image_count = EMUtil.get_image_count(input_stack)
        
        img = EMData()
        for each_image_number in range(image_count):
            img.read_image(input_stack, each_image_number)
            determined = get_params_proj(img)
            set_params_proj(img, [determined[0], determined[1], determined[2], -0., -0.])
            img.write_image(input_stack, each_image_number)
            
        return input_stack
    

    def setup_for_all_options_true(self, helix_volume):
        from spring.tests.segment2d.test_segmentclass import HelixClassPreparation
        if self.all_options is True:
            helix_volume.write_image(self.test_reference_volume)
            self.generate_3d_ctf_file(self.ctf_3d_avg_file, self.alignment_size)
            HelixClassPreparation().prepare_custom_filter_file(self.custom_filter_file, self.alignment_size)
            for each_key in self.feature_set.parameters:
                if type(self.feature_set.parameters[each_key]) is bool and each_key != 'MPI option':
                    self.feature_set.parameters[each_key] = True

    def generate_input_stack_from_helix(self):
        segment_size = int(self.volume_size_in_angstrom/self.pixelsize)
        
        self.euler_list = SegmentRefine3d().generate_Euler_angles_for_projection(self.azimuthal_count,
        self.out_of_plane_range, self.out_of_plane_count, self.helical_rotation)
        
        self.perturbed_alignment_parameters = \
        self.apply_random_rotations_x_and_y_shifts_to_projection_parameters(self.euler_list,
        self.x_translation/self.pixelsize)
        
        coord = np.arange(len(self.perturbed_alignment_parameters) / 2) * 10 * self.pixelsize
        coordinates = ((coord, coord))
        half_params = self.perturbed_alignment_parameters[len(self.perturbed_alignment_parameters)/2:]
        self.prepare_database_for_refinement(half_params, self.pixelsize, coordinates)
        
        coord = np.arange(len(self.perturbed_alignment_parameters) / 2, 
                          len(self.perturbed_alignment_parameters)) * 10 * self.pixelsize
        
        coordinates = ((coord, coord))
#         coordinates = ((coord, -1 * coord))
        other_half_params = self.perturbed_alignment_parameters[:len(self.perturbed_alignment_parameters)/2]
        
        self.prepare_database_for_refinement(other_half_params, self.pixelsize, coordinates,
        len(self.perturbed_alignment_parameters)/2)
        
        helix_volume =\
        TestSegClassReconstructPreparation().generate_helical_volume_square(self.size_of_subunit_in_angstrom,
        self.pixelsize, segment_size, self.helix_radius_in_angstrom, self.helical_rise, self.helical_rotation)
        
        if self.prepare_apolar_helix:
            point_symmetry = SegClassReconstruct().determine_point_group_symmetry_from_input('apolar', self.helix_start)
        else:
            point_symmetry = SegClassReconstruct().determine_point_group_symmetry_from_input('polar', self.helix_start)
        self.helix_volume = helix_volume.symvol(point_symmetry)
#            self.helix_volume = SegClassReconstruct().impose_apolar_symmetry_on_helix(self.helix_volume)
#        self.helix_volume.write_image('test_volume.hdf')
        
        TestSegClassReconstructPreparation().generate_noise_projections_from_helix(self.input_stack, self.helix_volume,
        self.perturbed_alignment_parameters)
        
        self.input_stack = self.clean_projection_parameters_from_input_stack(self.input_stack)
        

class TestSegmentRefine3dClean(TestSegmentRefine3dPreparation):
    def generate_iteration_filename_and_remove(self, file_prefix_name, each_iteration):
        file_name_iteration = '{prefix}*{iter:03}{ext}'.format(prefix=os.path.splitext(file_prefix_name)[0],
        iter=each_iteration + 1, ext=os.path.splitext(file_prefix_name)[-1])
        
        files = glob(file_name_iteration)
        for each_file in files:
            if os.path.isfile(each_file):
                os.remove(each_file)
            
        return file_name_iteration


    def clean_files_from_iterations(self):
        os.remove('spring.db')
        for each_iteration in list(range(self.test_iteration_count)):
            self.generate_iteration_filename_and_remove('refinement.db', each_iteration)
            self.generate_iteration_filename_and_remove(self.test_reference_volume, each_iteration)
            self.generate_iteration_filename_and_remove('fsc.dat', each_iteration)
            self.generate_iteration_filename_and_remove('fsc_indpndnt.png', each_iteration)
            self.generate_iteration_filename_and_remove('exp_vs_reproj.png', each_iteration)
            self.generate_iteration_filename_and_remove(self.diagnostic_plot_file, each_iteration)

        if os.path.isfile(self.test_reference_volume):
            os.remove(self.test_reference_volume)

    
    def cleanup_segmentrefine3d(self):
        os.remove(self.input_stack)
        os.remove(os.path.join(os.path.pardir, 'spring.db'))

        self.clean_files_from_iterations()
        
        if self.all_options:
            os.remove(self.custom_filter_file)
            os.remove(self.ctf_3d_avg_file)

    def prepare_final_prj_for_documentation(self, models, outfile=None):
        each_vol = EMData()
        max_dims = []
        for each_model in models:
            each_vol.read_image(each_model)
            max_dims.append(max(each_vol.get_xsize(), each_vol.get_ysize(), each_vol.get_zsize()))
        
        max_dim = max(max_dims)
        for each_model in models: 
            each_vol.read_image(each_model)
            each_vol.process_inplace('normalize')
            each_vol = Util.pad(each_vol, max_dim, max_dim, max_dim, 0, 0, 0, 'average')
            projection_parameters = [[0., 90., 270., 0., 0.]]
            helical_projections = prj(each_vol, projection_parameters, each_model)
            
        if outfile is None:
            outfile = models[0]
        for each_model_id, each_model in enumerate(models):
            each_vol.read_image(each_model)
            each_vol.write_image(outfile, each_model_id)
            if each_model_id > 0:
                os.remove(each_model)


class TestSegmentRefine3dSetup(TestSegmentRefine3dClean):
    def setup_input_output_iteration(self):
        self.feature_set.parameters['Image input stack refinement']=self.input_stack
        self.feature_set.parameters['Output volume name']=self.test_reference_volume
        self.feature_set.parameters['spring.db file']=os.path.join(os.pardir, 'spring.db')
        self.feature_set.parameters['Continue refinement option']=False
        self.feature_set.parameters['refinement.db file']='refinement003.db'
            
        self.feature_set.parameters['Diagnostic plot prefix']=self.diagnostic_plot_file
        self.feature_set.parameters['Number of iterations']=self.test_iteration_count
        self.feature_set.parameters['Reference structure option']=False
        self.feature_set.parameters['Reference volume']=os.path.join(os.pardir, 'test_recvol_100apix_003.hdf')
        self.feature_set.parameters['Keep intermediate files']=False
        
    def setup_helical_symmetry_parameters(self):
        self.feature_set.parameters['Pixel size in Angstrom']=self.pixelsize
        self.feature_set.parameters['Estimated helix inner and outer diameter in Angstrom']=((50, 170))
        self.feature_set.parameters['Symmetrize helix']=True
        self.feature_set.parameters['Enforce even phi option']=False
        self.feature_set.parameters['Release cycle even phi']=6
        self.feature_set.parameters['Pitch enforce even phi']=self.helical_rise * 360.0 / self.helical_rotation
        self.feature_set.parameters['Bin cutoff of phi angles']=10000
        self.feature_set.parameters['Helical rise/rotation or pitch/number of units per turn choice']='rise/rotation'
        
        self.feature_set.parameters['Helical symmetry in Angstrom or degrees']=((self.helical_rise,
        self.helical_rotation))

    def setup_alignment_parameters(self):
        self.feature_set.parameters['Force helical continuity']=True
        self.feature_set.parameters['Limit in-plane rotation']=True
        self.feature_set.parameters['Delta in-plane rotation angle']=5.0
        self.feature_set.parameters['Out-of-plane tilt angle range']=self.out_of_plane_range
        
        self.feature_set.parameters['Number of projections azimuthal/out-of-plane angle']=((self.azimuthal_count,
        self.out_of_plane_count))


    def setup_selection_criteria_from_segment_table(self, feature_set):
        feature_set.parameters['Segments select option'] = False
        feature_set.parameters['Include or exclude segments'] = 'include'
        feature_set.parameters['Segment file'] = 'test_select_segment.dat'
        
        feature_set.parameters['Micrographs select option'] = False
        feature_set.parameters['Include or exclude micrographs'] = 'include'
        feature_set.parameters['Micrographs list'] = '1'
        
        feature_set.parameters['Helices select option'] = False
        feature_set.parameters['Include or exclude helices'] = 'include'
        feature_set.parameters['Helices list'] = '1'
        
        feature_set.parameters['Classes select option'] = False
        feature_set.parameters['Include or exclude classes'] = 'include'
        feature_set.parameters['Class type'] = 'class_id'
        feature_set.parameters['Classes list'] = '0-2'
        
        feature_set.parameters['Persistence class option'] = False
        feature_set.parameters['Persistence class length in Angstrom'] = 700
        feature_set.parameters['Class occupancy threshold']=0.5

        feature_set.parameters['Straightness select option'] = False
        feature_set.parameters['Include or exclude straight helices'] = 'include'
        feature_set.parameters['Persistence length range'] = (10, 100)
        
        feature_set.parameters['Defocus select option'] = False
        feature_set.parameters['Include or exclude defocus range'] = 'include'
        feature_set.parameters['Defocus range'] = (0, 20000)
        
        feature_set.parameters['Astigmatism select option'] = False
        feature_set.parameters['Include or exclude astigmatic segments'] = 'include'
        feature_set.parameters['Astigmatism range'] = (0, 10000)
        
        feature_set.parameters['Layer line correlation select option'] = False
        feature_set.parameters['Include or exclude segments based on layer-line correlation'] = 'include'
        feature_set.parameters['Correlation layer line range']=((50, 100))
        
        return feature_set
    

    def setup_selection_parameters(self):
        self.feature_set = self.setup_selection_criteria_from_segment_table(self.feature_set)
        
        self.feature_set.parameters['Out-of-plane tilt select option']=False
        self.feature_set.parameters['Include or exclude out-of-plane tilted segments']='include'
        self.feature_set.parameters['Out-of-plane tilt range']=((-8,8))
        
        self.feature_set.parameters['Projection correlation select option']=False
        self.feature_set.parameters['Include or exclude segments based on projection correlation']='include'
        self.feature_set.parameters['Correlation projection range']=((0, 100))
        
        self.feature_set.parameters['Shift normal to helix select option']=False
        self.feature_set.parameters['Include or exclude segments with shift normal to helix']='include'
        self.feature_set.parameters['Shift normal to helix in Angstrom']=10.0
        
    def setup_refinement_strategy_parameters(self):
        self.feature_set.parameters['Absolute X and Y translation limit in Angstrom']= (int(0.5 * self.x_translation),
        int(0.5* self.y_translation))

        self.feature_set.parameters['Assemble refinement strategy']=True
        self.feature_set.parameters['LR - Low resolution aim']=True
        self.feature_set.parameters['LR - azimuthal and out-of-plane search restraint in degrees']=((180.0, 180.0))
        
        self.feature_set.parameters['LR - X and Y translation range in Angstrom']=((self.x_translation,
        self.y_translation))
        
        self.feature_set.parameters['MR - Medium resolution aim']=True
        self.feature_set.parameters['MR - azimuthal and out-of-plane search restraint in degrees']=((80.0, 20.0))
        
        self.feature_set.parameters['MR - X and Y translation range in Angstrom']=((int(self.x_translation / 2.0),
        int(self.y_translation / 2.0)))
        
        self.feature_set.parameters['HR - High resolution aim']=False
        self.feature_set.parameters['HR - azimuthal and out-of-plane search restraint in degrees']=((20.0, 20.0))
        
        self.feature_set.parameters['HR - X and Y translation range in Angstrom']=((int(self.x_translation / 3.0),
        int(self.y_translation / 3.0)))
        
        self.feature_set.parameters['MaxR - Maximum resolution aim']=False
        self.feature_set.parameters['MaxR - azimuthal and out-of-plane search restraint in degrees']= ((2.0, 2.0))
        
        self.feature_set.parameters['MaxR - X and Y translation range in Angstrom']=((int(self.x_translation / 6.0),
        int(self.y_translation / 6.0)))
        
        self.feature_set.parameters['Independent half-set refinement']=False
        self.feature_set.parameters['Half-set refinement start']='medium'
        
        self.feature_set.parameters['Frame motion correction']=False
        self.feature_set.parameters['Frame average window size']= 3
        self.feature_set.parameters['Frame local averaging distance']= 700

        
    def setup_filter_parameters(self):
        self.feature_set.parameters['High-pass filter option']=False
        self.feature_set.parameters['Low-pass filter option']=True
        self.feature_set.parameters['High and low-pass filter cutoffs in 1/Angstrom']=((0.01, 0.1))
        self.feature_set.parameters['Custom filter option']=False
        self.feature_set.parameters['Custom-built filter file']=self.custom_filter_file
        self.feature_set.parameters['Automatic FSC filter']=True
        self.feature_set.parameters['B-Factor']=0
        self.feature_set.parameters['Filter layer-lines option']=False
        

    def setup_reconstruction_parameters(self):
        self.feature_set.parameters['Rotational symmetry']=self.helix_start
        self.feature_set.parameters['Helix polarity']='polar'
        self.feature_set.parameters['Unbending option']=False#True
        self.feature_set.parameters['Image alignment size in Angstrom']=280
        self.feature_set.parameters['Step size of segmentation in Angstrom']=70
        self.feature_set.parameters['3D CTF correction']=False
        self.feature_set.parameters['3D CTF correction intensity']='low'
        

    def setup_main_segmentrefine3d_parameters(self):
        self.test_reference_volume = 'test_recvol.hdf'
        self.diagnostic_plot_file = 'test_diagnostic_plot.png'
        self.ctf_3d_avg_file = 'test_3d_ctfaverage.hdf'
        self.custom_filter_file = 'test_custom_filter_file.dat'
        self.all_options = False
        self.test_iteration_count = 6
        self.pixelsize = 5.0
        self.helical_rise = 10.0
        self.helical_rotation = 50.0
        self.size_of_subunit_in_angstrom = 50
        self.helix_radius_in_angstrom = 50
        self.volume_size_in_angstrom = 400
        self.x_translation = 50
        self.y_translation = 10
        self.azimuthal_count = 12
        self.out_of_plane_range = (-8, 8)
        self.out_of_plane_count = 5
        self.helix_start = 1
        self.setup_input_output_iteration()
        self.setup_helical_symmetry_parameters()
        self.setup_refinement_strategy_parameters()
        self.setup_alignment_parameters()
        self.setup_selection_parameters()
        self.setup_filter_parameters()
        self.setup_reconstruction_parameters()

    def setup_of_common_non_mpi_parameters(self):
        self.feature_set = SegmentRefine3dPar()
        self.input_stack = 'test_stack.hdf'
        self.setup_main_segmentrefine3d_parameters()
        
        
class TestSegmentRefine3dSetupForOthers(TestSegmentRefine3dSetup, SegmentRefine3d):
    def setup_sr3d(self):
        self.setup_of_common_non_mpi_parameters()
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(3, cpu_count())
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)
        
        self.prepare_apolar_helix = False
        self.generate_input_stack_from_helix()
        
        super(TestSegmentRefine3dSetupForOthers, self).__init__(self.feature_set)
        

class TestSegmentRefine3d(TestSegmentRefine3dSetupForOthers):

    def produce_a_projection_of_final_volume(self):
        last_volume_file = self.generate_file_name_with_apix(self.test_iteration_count, self.test_reference_volume,
        self.pixelsize)
        
        self.prepare_final_prj_for_documentation([last_volume_file], self.test_reference_volume)
#         last_volume = EMData()
#         last_volume.read_image(last_volume_file)
#         
#         projection_parameters = [[0., 90., 270., 0., 0.]]
#         helical_projections = prj(last_volume, projection_parameters, self.test_reference_volume)

    def check_determined_alignment_parameters(self, determined_alignment_parameters, perturbed_alignment_parameters):
        for each_determined_index, each_determined_five in enumerate(determined_alignment_parameters):
            each_perturbed_five = perturbed_alignment_parameters[each_determined_index]
            
            sys.stderr.write('\n{determined} = {perturbed}'.format(determined=each_determined_five,
            perturbed=each_perturbed_five))
            
            
    def check_average_peak_value(self, peak_threshold):
        ref_session = SpringDataBase().setup_sqlite_db(refine_base,
        'refinement{0:03}.db'.format(self.test_iteration_count))
        
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
        
        avg_peak_value = last_cycle.mean_peak
        sys.stderr.write('\naverage peak value {0} > {1}'.format(avg_peak_value, peak_threshold))
        assert last_cycle.iteration_id == self.test_iteration_count
        assert avg_peak_value > peak_threshold
        
        
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.setup_sr3d()
         

    def teardown(self):
        pass
        self.cleanup_segmentrefine3d()
         
        self.testingdir.remove()


class TestSegmentRefine3dMain(TestSegmentRefine3d):
    def do_test_case_sr1(self):
        """
        * Standard single CPU segmentrefine3d run
        """
        self.perform_iterative_projection_matching_and_3d_reconstruction()
        self.produce_a_projection_of_final_volume()
            
        self.check_average_peak_value(1300)

        
class TestSegmentRefine3dEndToEnd(TestSegmentRefine3d):
    def do_end_to_end_test_sr3d_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
 

    def do_end_to_end_test_sr3d_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        
        
class TestSegmentRefine3dMore(TestSegmentRefine3d):
    def remove_additional_files(self):
        projection_files = glob('projection_stack*hdf')
        volume_references = glob('{0}*hdf'.format(os.path.splitext(self.test_reference_volume)[0]))
         
        for each_file in (projection_files + volume_references):
            os.remove(each_file)
        
    def do_test_case_sr0(self):
        """
        * Standard single CPU segmentrefine3d run including update refinement db
        """
        self.perform_iterative_projection_matching_and_3d_reconstruction()
               
        self.check_average_peak_value(1300)
        DataBaseUpdate().update_refinement_db('refinement{0:03}.db'.format(self.iteration_count), 'ref.db')
        os.remove('ref.db')
   
           
    def do_test_case_sr2(self):
        """
        * Segmentrefine3d test run with apolar helix (D2 - symmetry)
        """
        self.prepare_apolar_helix = True
        os.remove(os.path.pardir + os.sep + 'spring.db')
        self.helix_start = 2
        self.generate_input_stack_from_helix()
        self.feature_set.parameters['Helix polarity']='apolar'
        self.feature_set.parameters['HR - High resolution aim']=True
        self.feature_set.parameters['MaxR - Maximum resolution aim']=True
           
        super(TestSegmentRefine3d, self).__init__(self.feature_set)
        self.perform_iterative_projection_matching_and_3d_reconstruction()
        self.check_average_peak_value(1300)
           
           
    def do_test_case_sr3(self):
        """
        * Segmentrefine3d test run with left-handed helical symmetry
        and particular included classes
        """
        self.feature_set.parameters['Helical symmetry in Angstrom or degrees']=((self.helical_rise,
        -self.helical_rotation))
           
        self.feature_set.parameters['Classes select option'] = True
        self.feature_set.parameters['Include or exclude classes'] = 'include'
        self.feature_set.parameters['Classes list'] = '0,1,3,4,5,6,8,9,11,12'
           
        self.feature_set.parameters['3D CTF correction']=True
        self.feature_set.parameters['3D CTF correction intensity']='high'
           
        super(TestSegmentRefine3d, self).__init__(self.feature_set)
        self.perform_iterative_projection_matching_and_3d_reconstruction()
        self.check_average_peak_value(1200)
           
   
    def do_test_case_sr4(self):
        """
        * Segmentrefine3d test run with small image alignment size
        """
        self.feature_set.parameters['Force helical continuity']=False
        self.feature_set.parameters['Image alignment size in Angstrom']=180
        self.feature_set.parameters['Independent half-set refinement']=True
        super(TestSegmentRefine3d, self).__init__(self.feature_set)
        self.perform_iterative_projection_matching_and_3d_reconstruction()
           
        self.check_average_peak_value(650)
          
          
    def do_test_case_sr5(self):
        """
        * Segmentrefine3d test run without assumption of symmetry and attempt to enforce even phi angles
        """
        self.feature_set.parameters['Symmetrize helix']=False
        self.feature_set.parameters['Enforce even phi option']=True
        super(TestSegmentRefine3d, self).__init__(self.feature_set)
        self.perform_iterative_projection_matching_and_3d_reconstruction()
           
        self.check_average_peak_value(1300)
           
          
    def do_test_case_sr6(self):
        """
        * Segmentrefine3d test run with out-of-plane tilt exclusion
        """
        self.feature_set.parameters['Out-of-plane tilt select option']=True
        self.feature_set.parameters['Include or exclude out-of-plane tilted segments']='include'
        self.feature_set.parameters['Out-of-plane tilt range']=((-4,4))
           
        super(TestSegmentRefine3d, self).__init__(self.feature_set)
        self.perform_iterative_projection_matching_and_3d_reconstruction()
           
        self.check_average_peak_value(1300)
         
         
    def do_test_case_sr7_continue(self):
        """
        * Segmentrefine3d test run with continue refinement option
        """
        self.feature_set.parameters['Number of iterations']=3
        self.feature_set.parameters['MR - Medium resolution aim']=False
         
        super(TestSegmentRefine3d, self).__init__(self.feature_set)
        self.perform_iterative_projection_matching_and_3d_reconstruction()
   
        shutil.copy('test_recvol_100apix_003.hdf', os.pardir)
         
        self.feature_set.parameters['Reference structure option']=False
        self.feature_set.parameters['Continue refinement option']=True
        self.feature_set.parameters['LR - Low resolution aim']=False
        self.feature_set.parameters['MR - Medium resolution aim']=True
         
        super(TestSegmentRefine3d, self).__init__(self.feature_set)
        self.perform_iterative_projection_matching_and_3d_reconstruction()
         
        self.check_average_peak_value(1300)
        os.remove(os.path.join(os.pardir, 'test_recvol_100apix_003.hdf'))
         
         
    def do_test_case_sr8(self):
        """
        * Segmentrefine3d test run with custom filter file option
        """
        self.feature_set.parameters['Custom filter option']=True
           
        super(TestSegmentRefine3d, self).__init__(self.feature_set)
        from spring.tests.segment2d.test_segmentclass import HelixClassPreparation
        HelixClassPreparation().prepare_custom_filter_file(self.custom_filter_file, 
        int(round(self.alignment_size_in_A / self.pixelsize)))
           
        self.perform_iterative_projection_matching_and_3d_reconstruction()
           
        self.check_average_peak_value(1100)
           
        os.remove(self.custom_filter_file)
        

class TestSegmentRefine3dFrames(TestSegmentRefine3d):
    def setup_frames_for_averaging(self):
        from spring.tests.segment2d.test_segment import TestSegmentFrames
        ts2d = TestSegmentFrames()
        ts2d.setup()
        ts2d.do_test_case_seg101()

        shutil.copy('refinement_0-4frames.db', os.path.join(os.pardir, 'refinement006.db'))
        shutil.copy('spring_0-4frames.db', os.path.join(os.pardir, os.pardir, 'spring.db'))
        shutil.copy(ts2d.test_frame_stack, os.path.join(os.pardir, self.input_stack))
        ts2d.teardown()
        
        self.feature_set.parameters['Frame motion correction']=True

        self.feature_set.parameters['Reference structure option']=False
        self.feature_set.parameters['Number of iterations']=3
        self.feature_set.parameters['Continue refinement option']=True
        self.feature_set.parameters['refinement.db file']='refinement006.db'
        self.feature_set.parameters['LR - Low resolution aim']=False
        self.feature_set.parameters['MR - Medium resolution aim']=True
        
 
    def do_test_frame_processing_with_frame_averaging(self):
        """
        * Segmentrefine3d test with frame averaging option
        """
        self.setup_frames_for_averaging()
   
        super(TestSegmentRefine3d, self).__init__(self.feature_set)
        self.perform_iterative_projection_matching_and_3d_reconstruction()
        self.check_average_peak_value(1300)
    

    def do_test_frame_processing_with_frame_averaging_MPI(self):
        """
        * Segmentrefine3d MPI test with frame averaging option
        """
        self.setup_frames_for_averaging()
  
        self.feature_set.parameters['MPI option'] = True
          
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        self.check_average_peak_value(1300)
  
        
class TestSegmentRefine3dUnbending(TestSegmentRefine3d):
    def generate_long_helix(self):
        helix_length = 800
        radius = 4.0
        larger_dimension = 50
        s = model_square(radius, larger_dimension, larger_dimension, helix_length)
        t1 = Transform({'type':'spider', 'psi':33, 'theta':100, 'phi':77, 'scale':1.0})
        small_radius = radius/2.0
        ss = model_square(small_radius, larger_dimension, larger_dimension, helix_length)
        ss.transform(t1)
        vol = s - ss
        
        long_vol = TestSegClassReconstructPreparation().shift_volume_and_helicise(self.pixelsize, 50, self.helical_rise,
        self.helical_rotation, vol)
        
        SegClassReconstruct().project_locally(long_vol, [[0, 82, 270, 0, 0]], 'long_stack.hdf')
        long_image = EMData()
        long_image.read_image('long_stack.hdf')
        os.remove('long_stack.hdf')
        img_size = long_image.get_xsize()
        
        return helix_length, img_size, long_image


    def generate_bent_long_helix(self, helix_length, img_size, long_image):
        self.polynom_curve = [1 / float(helix_length), -1.0, helix_length / 2.0]
        cols, rows, inplane_angles = Segment().compute_bending_path_row_wise(float(img_size), self.polynom_curve, 0)
        coord_y = np.linspace(0, helix_length, 80)
        coord_x = np.polyval(self.polynom_curve, coord_y) #        import matplotlib.pyplot as plt
    #        plt.plot(cols, rows, 'x', coord_x, coord_y, '+')
    #        plt.xlim(0, helix_length)
    #        plt.ylim(0, helix_length)
    #        plt.savefig('test3.png')
        bent_helix = Segment().straighten_segment(long_image, img_size, cols, rows, inplane_angles, mode='bend')
        bent_helix.process_inplace('normalize')
        noise = model_gauss_noise(1, helix_length, helix_length)
        bent_helix += noise
#        bent_helix.write_image('bent_helix.hdf')
        
        return coord_x, coord_y, bent_helix


    def window_segments_from_bent_helix(self, coord_x, coord_y, bent_helix):
        coord_x += 4.0

#        Segment().write_boxfile(coord_x[10:-10], coord_y[10:-10], 100, 'test.box')
        os.remove(self.input_stack)
        for each_id, (each_x, each_y) in enumerate(zip(coord_x, coord_y)):
            segment = Segment().window_segment(bent_helix, each_x, each_y, 60)
            segment.write_image(self.input_stack, each_id)


    def setup_unbending_filament(self):
        helix_length, img_size, long_image = self.generate_long_helix()
        coord_x, coord_y, bent_helix = self.generate_bent_long_helix(helix_length, img_size, long_image)
        trimmed_coord_x = coord_x[10:-10] 
        trimmed_coord_y = coord_y[10:-10] 
        self.window_segments_from_bent_helix(trimmed_coord_x, trimmed_coord_y, bent_helix)
        
        prj_parameters = np.array([ [each_segid * self.helical_rotation, 90.0, 270.0, 0, 0] \
                                   for each_segid in list(range(len(trimmed_coord_x)))])
        
        os.remove(os.path.join(os.pardir, 'spring.db'))
        
        self.prepare_database_for_refinement(prj_parameters, self.pixelsize, ((trimmed_coord_x * self.pixelsize,
        trimmed_coord_y * self.pixelsize)))
        

    def do_test_case_sr10(self):
        """
        * Single CPU: Unbending of curved helix
        """
        self.feature_set.parameters['Unbending option']=True
        super(TestSegmentRefine3d, self).__init__(self.feature_set)
         
        self.setup_unbending_filament()
         
        self.perform_iterative_projection_matching_and_3d_reconstruction()
        self.check_average_peak_value(1100)
         
         
    def do_test_case_sr11(self):
        """
        * Segmentrefine3d: single CPU: Unbending and layer-line filter
        """
        self.feature_set.parameters['Unbending option']=True
        self.feature_set.parameters['Filter layer-lines option']=True
        super(TestSegmentRefine3d, self).__init__(self.feature_set)
         
        self.setup_unbending_filament()
         
        self.perform_iterative_projection_matching_and_3d_reconstruction()
        self.check_average_peak_value(1100)
        
        
class TestSegmentRefine3dMpi(TestSegmentRefine3d):
    pass
    def do_end_to_end_test_sa_inputfile_with_MPI(self):
        """
        * Segmentrefine3d: MPI standard run
        """
        self.feature_set.parameters['MPI option'] = True
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        self.check_average_peak_value(1300)
  
  
class TestSegmentRefine3dMpiMore(TestSegmentRefine3d):
    def do_end_to_end_test_sa_inputfile_with_MPI_continue_refhalf(self):
        """
        * MPI run continue refinement from independent half-set refinement
        """
        self.feature_set.parameters['MR - azimuthal and out-of-plane search restraint in degrees']=((180.0, 180.0))
        self.feature_set.parameters['Independent half-set refinement']=True
        self.feature_set.parameters['MPI option'] = True
             
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
       
        shutil.copy('test_recvol_50apix_006.hdf', os.pardir)
              
        self.feature_set.parameters['Independent half-set refinement']=False
        self.feature_set.parameters['Reference structure option']=True
        self.feature_set.parameters['Reference volume']=os.path.join(os.pardir, 'test_recvol_50apix_006.hdf')
        self.feature_set.parameters['Continue refinement option']=True
        self.feature_set.parameters['refinement.db file']='refinement006.db'
        self.feature_set.parameters['LR - Low resolution aim']=False
        self.feature_set.parameters['MR - Medium resolution aim']=True
              
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        self.check_average_peak_value(1300)
        self.test_iteration_count = 12

        os.remove(os.path.join(os.pardir, 'test_recvol_50apix_006.hdf'))


    def do_end_to_end_test_sa_inputfile_with_MPI_continue_ref(self):
        """
        * MPI run continue refinement option
        """
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of iterations']=3
        self.feature_set.parameters['MR - Medium resolution aim']=False
              
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        
        shutil.copy('test_recvol_100apix_003.hdf', os.pardir)
              
        self.feature_set.parameters['Independent half-set refinement']=True
        self.feature_set.parameters['Reference structure option']=False
        self.feature_set.parameters['Continue refinement option']=True
        self.feature_set.parameters['LR - Low resolution aim']=False
        self.feature_set.parameters['MR - Medium resolution aim']=True
              
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        self.check_average_peak_value(1300)
              
        os.remove(os.path.join(os.pardir, 'test_recvol_100apix_003.hdf'))

               
    def do_end_to_end_test_sa_inputfile_with_MPI_layer_line_filter(self):
        """
        * MPI Test for layer-line filter
        """
        self.feature_set.parameters['Filter layer-lines option']=True
        
        self.feature_set.parameters['MPI option'] = True
                
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        self.check_average_peak_value(1300)
        
          
    def do_end_to_end_test_sa_inputfile_with_MPI_unbending(self):
        """
        * MPI Test for unbending
        """
        self.feature_set.parameters['Unbending option']=True
          
        self.feature_set.parameters['MPI option'] = True
                  
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        self.check_average_peak_value(1400)
                    
             
    def do_end_to_end_test_sa_inputfile_with_MPI_unbending_and_layer(self):
        """
        * MPI Test for unbending and layer-line filter at the same time
        """
        self.feature_set.parameters['Unbending option']=True
        self.feature_set.parameters['Filter layer-lines option']=True
          
        self.feature_set.parameters['MPI option'] = True
                  
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        self.check_average_peak_value(1100)
        
          
    def do_end_to_end_test_sa_inputfile_with_MPI_classes(self):
        """
        * MPI Test for class exclusion
        """
        self.feature_set.parameters['Classes select option'] = True
        self.feature_set.parameters['Include or exclude classes'] = 'include'
        self.feature_set.parameters['Classes list'] = '0,1,3,4,5,6,8,11,12'
               
        self.feature_set.parameters['Out-of-plane tilt select option']=True
        self.feature_set.parameters['Include or exclude out-of-plane tilted segments']='include'
        self.feature_set.parameters['Out-of-plane tilt range']=((-8,4))
               
        self.feature_set.parameters['MPI option'] = True
               
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        self.check_average_peak_value(1300)
             
        
class TestSegmentRefine3dBinAlign(object):
    def setup(self):
        self.translation_step = 0.1
        circle_centered = model_circle(2, 600, 600)
        self.sx = self.sy = 22
        circle_shifted = rot_shift2D(circle_centered, 0, self.sx, self.sy)
        
        self.dec_factor = 6.0
        self.small_circle_shifted = image_decimate(circle_shifted, self.dec_factor)
        self.small_circle_centered = image_decimate(circle_centered, self.dec_factor)
    
    def do_test_aligning_binned_images(self):
        translation_series = np.arange(-10, 10, self.translation_step)
        x_translations, y_translations = np.meshgrid(translation_series, translation_series)
        
        translation_pairs = []
        ccc_values = []
        for each_xtrans_index, each_xtranslation in enumerate(x_translations):
            for each_ytrans_index, each_ytranslation in enumerate(y_translations):
                each_xtranslation = x_translations[each_xtrans_index][each_ytrans_index]
                each_ytranslation = y_translations[each_xtrans_index][each_ytrans_index]
                back_shifted_circle = rot_shift2D(self.small_circle_shifted, 0, each_xtranslation, each_ytranslation)
                translation_pairs.append((each_xtranslation, each_ytranslation))
                ccc_values.append(ccc(back_shifted_circle, self.small_circle_centered))
                
        max_ind = np.argmax(ccc_values)
        dec_shifted_x = self.sx/float(self.dec_factor)
        dec_shifted_y = self.sy/float(self.dec_factor)
        
        sys.stderr.write('{0}\t{1}, {2}\t{3}, {4}'.format(ccc_values[max_ind], translation_pairs[max_ind][0],
        translation_pairs[max_ind][1], dec_shifted_x, dec_shifted_y))
    
        margin = 0.3
        assert -dec_shifted_x - margin < translation_pairs[max_ind][0] < -dec_shifted_x + margin
        assert -dec_shifted_y - margin < translation_pairs[max_ind][1] < -dec_shifted_y + margin
    
    def teardown(self):
        pass

class TestSegmentRefine3dCumShiftAlign(object):
    def setup(self):
        self.img_size = 200
        rect_centered = model_blank(self.img_size - 180, self.img_size - 100, 1, 1)
        self.rect_centered = Util.pad(rect_centered, self.img_size, self.img_size, 1, 0, 0, 0, '0')
        self.sx = 22
        self.sy = 2
        self.rot_angle = 50

        self.rect_shifted_rotated = rot_shift2D(self.rect_centered, self.rot_angle, self.sx, self.sy)

        
        self.x_range = 24
        self.y_range = 3
#        self.x_range = 10
#        self.y_range = 21
        self.step_angle = 1.0
        self.step_x = 1.0
        self.delta_psi = 10
    
        self.polar_interpolation_parameters, ring_weights = SegmentAlign2d().prepare_empty_rings(1, self.img_size/2 - 2, 1)
        
        prj = EMData()
        
        self.reference_rings = [SegmentAlign2d().generate_reference_rings_from_image(self.rect_centered,
        self.polar_interpolation_parameters, ring_weights, self.img_size)]
        
        phi = 0.0
        theta = 90.0
        psi = 270.0
        n1 = np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi))
        n2 = np.sin(np.deg2rad(theta)) * np.sin(np.deg2rad(phi))
        n3 = np.cos(np.deg2rad(theta))
            
        self.reference_rings[0].set_attr_dict({'n1':n1, 'n2':n2, 'n3':n3})
        self.reference_rings[0].set_attr('phi', phi)
        self.reference_rings[0].set_attr('theta', theta)
        self.reference_rings[0].set_attr('psi', psi)
            

    def perform_delta_2d_search(self, previous_shift_x, previous_shift_y, x_range, y_range, rot_angle):
        [ang, sxs, s_ys, mirror, matched_reference_id, peak] = \
        Util.multiref_polar_ali_2d_delta(self.rect_shifted_rotated, self.reference_rings, x_range, y_range, self.step_x,
        'F', self.polar_interpolation_parameters, self.center_x + previous_shift_x, self.center_y + previous_shift_y,
        rot_angle, self.delta_psi)
        
        return sxs, s_ys, ang, mirror, peak
    

    def perform_local_2d_search(self, previous_shift_x, previous_shift_y, x_range, y_range):
        fine_step_angle = np.sin(np.deg2rad(0.05))
        zoom_factor = 5.0
        fine_step_x = self.step_x / zoom_factor
        
        fine_x_range = x_range / zoom_factor
        fine_y_range = y_range / zoom_factor
        
        [ang, sxs, s_ys, mirror, xiref, peak] = Util.multiref_polar_ali_2d_local(self.rect_shifted_rotated,
        self.reference_rings, fine_x_range, fine_y_range, fine_step_x, fine_step_angle, 'F',
        self.polar_interpolation_parameters, self.center_x + previous_shift_x, self.center_y + previous_shift_y)
        
        return sxs, s_ys, ang, mirror, peak
    
    
    def do_test_of_cumulative_alignment(self):
        """
        * Simplest restrained 2D alignment 
        
        For each image the following operations are done:
        #. add dummy values of xform.projection for references and image to be aligned
        #. first coarse search with limited in-plane rotation
        #. convert rotate/shift convention back to shift/rotate convention to update shifts
        #. second fine search with smaller search range but finer search step
        #. convert rotate/shift/convention back to shift/rotate convention to update shifts
        """
        self.center_x = self.center_y = self.rect_shifted_rotated.get_xsize() / 2 
        previous_shift_x = previous_shift_y = 0.0
        transform_projection = Transform({'type':'spider','phi':0.0, 'theta':90.0, 'psi':270.0})
        rot_angle = self.rot_angle 
        for each_iteration_id in list(range(10)):
            self.rect_shifted_rotated.set_attr('xform.projection', transform_projection)
        
            local_x_range = max(1.0, self.x_range / float(each_iteration_id + 1))
            local_y_range = max(1.0, self.y_range / float(each_iteration_id + 1))
            
            sxs, s_ys, ang, mirror, peak = self.perform_delta_2d_search(previous_shift_x, previous_shift_y,
            local_x_range, local_y_range, rot_angle)
            
            angb, sxb, syb, ct = compose_transform2(0.0, sxs, s_ys, 1, -ang, 0.0, 0.0, 1)
            
            local_prev_shift_x = previous_shift_x - sxb
            local_prev_shift_y = previous_shift_y - syb
            
            import sys
            
            sys.stderr.write('\n{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}'.format(local_x_range, local_y_range,
            previous_shift_x, previous_shift_y, ang, mirror, peak, sxb, syb))
            
            sxs, s_ys, ang, mirror, peak = self.perform_local_2d_search(local_prev_shift_x, local_prev_shift_y,
            local_x_range, local_y_range)
            
            angb, sxb, syb, ct = compose_transform2(0.0, sxs, s_ys, 1, -ang, 0.0, 0.0, 1)
            previous_shift_x = local_prev_shift_x - sxb
            previous_shift_y = local_prev_shift_y - syb
            rot_angle = ang
            
#            import sys
#            sys.stderr.write('\n{0}, {1}, {2}, {3}, {4}, {5}, {6}'.format(ang, previous_shift_x, previous_shift_y, mirror, peak, sxb, syb))
        assert -0.1 < syb < 0.1
#        back_rot = Segment().shift_and_rotate_image(self.rect_shifted_rotated, -angb, -previous_shift_x, -previous_shift_y)
        a, b, c = Segment().convert_shift_rotate_to_rotate_shift_order(ang, -previous_shift_x, -previous_shift_y)
        back_rot = rot_shift2D(self.rect_shifted_rotated, a, b, c)
        added = back_rot + 2 * self.rect_centered
        added.write_image('added.hdf')
        
    def teardown(self):
        os.remove('added.hdf')
        
    
class TestEulerPlot():
    def setup(self):

        if random.randint(0, 1):
            self.phi_angles = np.arange(0, 360, 4)
            self.theta_angles = np.linspace(80, 100, 90)
            self.psi_angles = 270 * np.ones(90)
        else:
            from utilities import even_angles
            angles = even_angles()
            self.phi_angles, self.theta_angles, self.psi_angles = zip(*angles)

        self.fig = plt.figure()
    
        self.euler = EulerPlot()


    def do_euler_angle_test_spher_prj(self):
        """
        * Project Euler angles on 2D sphere histogram
        """

        self.fig = self.euler.plot_euler_angles_on_spherical_projection(self.fig, self.phi_angles, self.theta_angles,
        self.psi_angles)
        

    def do_euler_angle_test_scatter_sphere(self):
        """
        * Project Euler angles on 2D sphere scatter
        """
        self.fig = self.euler.plot_euler_angles_on_spherical_projection_scatter(self.fig, self.phi_angles, self.theta_angles,
        self.psi_angles)


    def do_euler_angle_test_polar_plot_scatter(self):
        """
        * Plot Euler angles on polar plot scatter
        """
        self.fig = self.euler.plot_euler_angles_on_polar_plot_scatter(self.fig, self.phi_angles, self.theta_angles,
        self.psi_angles)
    

    def do_euler_angle_test_polar_plot_hist(self):
        """
        * Plot Euler angles on polar plot histogram
        """
        self.fig = self.euler.plot_euler_angles_on_polar_plot_hist(self.fig, self.phi_angles, self.theta_angles,
        self.psi_angles)

    def do_euler_angle_test_plot_on_3dsphere(self):
        """
        * Plot Euler angles on 3D sphere scatter
        """
        self.fig = self.euler.plot_euler_angles_on_sphere(self.fig, self.phi_angles, self.theta_angles, self.psi_angles)
        

    def do_euler_angle_test_plot_phi_theta_scatter(self):
        """
        * Plot Euler angles in a simple xy hexbin scatter
        """
        self.fig = self.euler.plot_euler_angle_scatter(self.fig, self.phi_angles, self.theta_angles)


    def teardown(self):
        self.fig.savefig('test_euler.png')
        os.remove('test_euler.png')
        
        
def main():
    tsr3d = TestSegmentRefine3dMain()
    tsr3d.setup()
    tsr3d.do_test_case_sr1()
        
if __name__ == '__main__':
    main()
