# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to compute 3D reconstruction from a single class average using a range of different helical symmetries
"""
from EMAN2 import EMData, EMNumPy, Transform, Vec2f, Util
from projection import prgs
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from utilities import set_params_proj
import numpy as np
import os
from spring.particle2d.particlealign2d import ParticleAlign2d


class SegClassReconstructPar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'segclassreconstruct'
        self.proginfo = __doc__

        self.code_files = ['segclassreconstruct_prep', 'segclassreconstruct_assist', self.progname, 
        self.progname + '_mpi']

        self.segclassreconstruct_features = Features()
        self.feature_set = self.segclassreconstruct_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()


    def define_parameters_and_their_properties(self):
        self.feature_set = self.segclassreconstruct_features.set_class_avg_stack(self.feature_set)
        self.feature_set = self.set_volume_prefix_symmetry_grid(self.feature_set)
        
        self.feature_set = self.segclassreconstruct_features.set_class_number_to_be_analyzed(self.feature_set)
        
        self.feature_set = \
        self.segclassreconstruct_features.set_helical_symmetry_reconstruction_series(self.feature_set)
        
        self.feature_set = self.segclassreconstruct_features.set_keep_intermediate_files_option(self.feature_set, 
        'Keep 3D reconstruction files. Caution: depending on the size of the helical symmetry grid this can ' + \
        'generate vast amounts of data.')
        
        self.feature_set = self.set_montage_class_reprj_out_stack(self.feature_set)
        self.feature_set = self.set_montage_class_reprj_periodogram_out_stack(self.feature_set)

        self.feature_set = self.segclassreconstruct_features.set_rotational_symmetry(self.feature_set)
        self.feature_set = self.segclassreconstruct_features.set_polar_apolar_helix_choice(self.feature_set)
        self.feature_set = self.segclassreconstruct_features.set_out_of_plane_tilt_angle(self.feature_set)
        
        self.feature_set = self.segclassreconstruct_features.set_volume_size_to_be_reconstructed(self.feature_set)
        self.feature_set = self.set_minimum_image_count_reconstruction(self.feature_set)
        self.feature_set = self.set_local_grid_option(self.feature_set)
        self.feature_set = self.set_center_and_rotation_option(self.feature_set)
        self.feature_set = self.segclassreconstruct_features.set_mpi(self.feature_set)
        self.feature_set = self.segclassreconstruct_features.set_ncpus(self.feature_set)
        self.feature_set = self.segclassreconstruct_features.set_temppath(self.feature_set)


    def define_program_states(self):
        self.feature_set.program_states['prepare_segclassreconstruct']='Prepare 3D reconstruction'
        self.feature_set.program_states['reconstruct_volumes_for_each_symmetry_pair']='Reconstruct_helically ' + \
        'symmetric volumes from class average'
        self.feature_set.program_states['enter_grid_values_in_database']='Enter grid values in database'


    def set_center_and_rotation_option(self, feature_set):
        inp7 = 'Center option'
        feature_set.parameters[inp7] = bool(True)
        feature_set.hints[inp7] = 'Segments are centered and rotationally aligned with respect to their helix axis'
        feature_set.level[inp7]='intermediate'

        return feature_set


#     def set_symgrid_keep_option(self, feature_set):
#         inp15 = 'Keep symmetry grid reconstructions'
#         feature_set.parameters[inp15]=bool(False)
#         feature_set.hints[inp15]='Keep reconstructions that are generated for each symmetry pair - volumes are ' + \
#         'deleted otherwise'
#         
#         return feature_set
    
    
    def set_volume_prefix_symmetry_grid(self, feature_set):
        inp9 = 'Volume name'
        feature_set.parameters[inp9]='recvol.hdf'
        feature_set.properties[inp9]=feature_set.file_properties(1,['hdf'],'saveFile')
        feature_set.hints[inp9]='Output name for volumes of grid search (completion to ' + \
        '\'name_riseXXX_rot_XXX.ext\' or \'name_pitchXXX_unitno_XXX.ext\): accepted image file formats ({0})'.\
        format(', '.join(feature_set.properties[inp9].ext))
        
        feature_set.level[inp9]='beginner'
        
        return feature_set
    
    
    def set_minimum_image_count_reconstruction(self, feature_set):
        inp5 = 'Minimum number of images for 3D reconstruction'
        feature_set.parameters[inp5] = int(8)
        feature_set.hints[inp5] = 'Minimum number of images required for 3D reconstruction. Below this value no ' + \
        '3D reconstruction possible.'
        feature_set.properties[inp5] = feature_set.Range(4, 100, 1)
        feature_set.level[inp5]='expert'

        return feature_set
    
    
    def set_local_grid_option(self, feature_set):
        inp15 = 'Local symmetry grid search'
        feature_set.parameters[inp15]=bool(False)
        feature_set.hints[inp15]='Local symmetry grid search fixes the number of images that are inserted in ' + \
        'each reconstruction'
        feature_set.level[inp15]='expert'
        
        return feature_set
    
    
    def set_montage_class_reprj_out_stack(self, feature_set):
        inp2 = 'Montage stack of class average vs. reprojection images'
        feature_set.parameters[inp2] = 'reprojection_montage.hdf'
        feature_set.properties[inp2] = feature_set.file_properties(1, ['hdf'], 'saveFile')
        feature_set.hints[inp2] = 'Output montage of images from class average vs reprojection stack of 3D ' + \
        'reconstructions: accepted image file formats ({0})'.format(', '.join(feature_set.properties[inp2].ext))
        feature_set.relatives[inp2]='Keep intermediate files'
        feature_set.level[inp2]='intermediate'

        return feature_set
    
    
    def set_montage_class_reprj_periodogram_out_stack(self, feature_set):
        inp2 = 'Montage stack of class average vs. reprojection power spectra'
        feature_set.parameters[inp2] = 'power_montage.hdf'
        feature_set.properties[inp2] = feature_set.file_properties(1, ['hdf'], 'saveFile')
        
        feature_set.hints[inp2] = 'Output montage of power spectra from class average and reprojection stack of ' + \
        '3D reconstructions: accepted image file formats (%s)' % (', '.join(feature_set.properties[inp2].ext))
        
        feature_set.relatives[inp2]='Keep intermediate files'
        feature_set.level[inp2]='intermediate'
        
        return feature_set
    
    
#     def set_generate_surface_slice_views_option(self, feature_set):
#         inp15 = 'Volume slice views'
#         feature_set.parameters[inp15]=bool(False)
#         feature_set.hints[inp15]='Produce stack of volume slice views'
#         
#         return feature_set
#     
# 
#     def set_slice_view_stack(self, feature_set):
#         inp9 = 'Volume slice view stack'
#         feature_set.parameters[inp9]='volume_slice_views.hdf'
#         feature_set.properties[inp9]=feature_set.file_properties(1,['hdf'],'saveFile')
#         feature_set.hints[inp9]='Volume slice view of each symmetry pair reconstruction for visual inspection'
#         feature_set.relatives[inp9]='Volume slice views'
#         
#         return feature_set
#     
#     
#     def set_generate_noise_reprojections_option(self, feature_set):
#         inp15 = 'Noise volumes for normalization'
#         feature_set.parameters[inp15]=bool(True)
#         feature_set.hints[inp15]='Generate pure noise volumes for each symmetry pair that are used to normalize ' + \
#         'similarity comparison'
#         
#         feature_set.level[inp15]='expert'
#         
#         return feature_set
#     
#     
#     def set_noise_image(self, feature_set):
#         inp9 = 'Noise image'
#         feature_set.parameters[inp9]='noise_image.hdf'
#         feature_set.properties[inp9]=feature_set.file_properties(1,['hdf'],'saveFile')
#         feature_set.hints[inp9]='Pure noise image that is used for reconstruction for each symmetry pair and can ' + \
#         'be used later in Seggridcompare to normalize similarity measures'
#         feature_set.relatives[inp9]='Noise volumes for normalization'
#         feature_set.level[inp9]='expert'
#         
#         return feature_set
    
    
class SegClassReconstructPreparation(object):
    """
    * Class that holds functions to insert_image_slices_in_3D_volume helically symmetric volumes
    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.infile = p['Class average stack']
            self.volume_name = p['Volume name']
            self.outfile = self.volume_name
            self.classno = p['Class number to be analyzed']
            self.keep_intermediate_files = p['Keep intermediate files']
            self.montaged_reprojection_stack = p['Montage stack of class average vs. reprojection images']
            self.montaged_power_stack = p['Montage stack of class average vs. reprojection power spectra']
            
            self.pixelsize = p['Pixel size in Angstrom']
            self.helix_inner_width = p['Estimated helix inner and outer diameter in Angstrom'][0]
            self.helixwidth = p['Estimated helix inner and outer diameter in Angstrom'][1]
            self.helix_inner_widthpix = int(round(self.helix_inner_width / self.pixelsize))
            self.helixwidthpix = int(round(self.helixwidth / self.pixelsize))
            
            self.rise_rot_or_pitch_unit_choice = p['Helical rise/rotation or pitch/number of units per turn choice']
            self.helical_rise_or_pitch_range = p['Range of helical rise or pitch search in Angstrom']
            self.helical_rotation_or_unit_range = p['Range of helical rotation in degrees or number of units per ' + \
            'turn search']
            
            self.helical_rise_or_pitch_increment = p['Increments of helical symmetry steps in Angstrom or degrees'][0]
            self.helical_rotation_or_unit_increment = p['Increments of helical symmetry steps in Angstrom or degrees'][1]
            self.rotational_symmetry_start = p['Rotational symmetry']
            self.polar_helix = p['Helix polarity']
            self.out_of_plane_tilt_angle = p['Out-of-plane tilt angle']
            
            self.minimum_image_count_3d = p['Minimum number of images for 3D reconstruction']
            self.percent_reconstruction_size = p['Percent of image reconstruction size']
            self.centeroption=p['Center option']
            self.local_grid_option = p['Local symmetry grid search']
            
            self.mpi_option = p['MPI option']
            self.cpu_count = p['Number of CPUs']
            self.temppath=p['Temporary directory']
    

    def convert_rise_rotation_or_pitch_unitnumber_series_to_grid_of_tuples(self, rise_series, rotation_series):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct                                                                          
        >>> s = SegClassReconstruct()
        >>> s.convert_rise_rotation_or_pitch_unitnumber_series_to_grid_of_tuples(range(2), range(3))
        array([[(0.0, 0.0), (0.0, 1.0), (0.0, 2.0)],
               [(1.0, 0.0), (1.0, 1.0), (1.0, 2.0)]], dtype=object)
        """
        
        symmetry_grid = np.zeros((len(rise_series), len(rotation_series)), dtype=tuple)
        for each_rise_index, each_rise in enumerate(rise_series):
            for each_rotation_index, each_rotation in enumerate(rotation_series):
                symmetry_grid[each_rise_index][each_rotation_index] = (float(each_rise), float(each_rotation))
        
        return symmetry_grid


    def generate_series(self, helical_rise_range, helical_rise_increment):
        rise_count = int(round((max(helical_rise_range) - min(helical_rise_range)) / helical_rise_increment)) + 1
        rise_series = np.linspace(min(helical_rise_range), max(helical_rise_range), rise_count)

        return rise_series.tolist()


    def generate_unique_rise_rotation_or_pitch_unitnumber_arrays(self, helical_rise_range, helical_rise_increment,
    helical_rotation_range, helical_rotation_increment):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct                                                                          
        >>> s = SegClassReconstruct()
        >>> s.generate_unique_rise_rotation_or_pitch_unitnumber_arrays([2,4], 2, [10,30], 10)
        ([2.0, 4.0], [10.0, 20.0, 30.0])
        >>> s.generate_unique_rise_rotation_or_pitch_unitnumber_arrays((275.0, 305.0), 5.0, (3.8, 4.2), 0.1)
        ([275.0, 280.0, 285.0, 290.0, 295.0, 300.0, 305.0], [3.8, 3.9, 4.0, 4.1, 4.2])
        >>> s.generate_unique_rise_rotation_or_pitch_unitnumber_arrays((270.0, 310.0), 5.0, (3.1, 3.7), 0.1) #doctest: +NORMALIZE_WHITESPACE
        ([270.0, 275.0, 280.0, 285.0, 290.0, 295.0, 300.0, 305.0, 310.0], 
        [3.1, 3.2, 3.3000000000000003, 3.4000000000000004, 3.5, 3.6, 3.7])
        """
        if helical_rotation_range[0] != helical_rotation_range[-1] and helical_rotation_increment == 0:
            helical_rotation_range = (helical_rotation_range[0], helical_rotation_range[0])
        if helical_rotation_increment == 0 or helical_rotation_increment is None:
            helical_rotation_increment = 1
        if helical_rise_range[0] != helical_rise_range[-1] and helical_rise_increment == 0:
            helical_rise_range = (helical_rise_range[0], helical_rise_range[0])
        if helical_rise_increment == 0 or helical_rise_increment is None:
            helical_rise_increment = 1
            
        rise_series = self.generate_series(helical_rise_range, helical_rise_increment)
        rotation_series = self.generate_series(helical_rotation_range, helical_rotation_increment)
        
        return rise_series, rotation_series
    

    def generate_rise_rotation_or_pitch_unitnumber_pairs_for_symmetry_grid(self, helical_rise_range, helical_rise_increment,
                                                       helical_rotation_range, helical_rotation_increment):
        """
        * Function to generate pairs of rise and rotation for symmetry grid search
        
        #. Usage: symmetry_grid = generate_rise_rotation_or_pitch_unitnumber_pairs_for_symmetry_grid(helical_rise_range,
        helical_rise_increment, helical_rotation_range, helical_rotation_increment)
                                                                                
        #. Input: helical_rise_range, helical_rotation_range = list of start and end values
        helical_rise_increment, helical_rotation_increment = number of increment
        #. Output: list of symmetry pairs of rise and rotation
        
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct                                                                          
        >>> s = SegClassReconstruct()
        >>> s.generate_rise_rotation_or_pitch_unitnumber_pairs_for_symmetry_grid([2,4], 2, [10,30], 10)
        array([[(2.0, 10.0), (2.0, 20.0), (2.0, 30.0)],
               [(4.0, 10.0), (4.0, 20.0), (4.0, 30.0)]], dtype=object)
               
        >>> s.generate_rise_rotation_or_pitch_unitnumber_pairs_for_symmetry_grid([2,3], 0, [10,20], 2)
        array([[(2.0, 10.0), (2.0, 12.0), (2.0, 14.0), (2.0, 16.0), (2.0, 18.0),
                (2.0, 20.0)]], dtype=object)
                
        >>> s.generate_rise_rotation_or_pitch_unitnumber_pairs_for_symmetry_grid([2,3], 1, [10,10], 0)
        array([[(2.0, 10.0)],
               [(3.0, 10.0)]], dtype=object)
               
        >>> s.generate_rise_rotation_or_pitch_unitnumber_pairs_for_symmetry_grid((275.0, 305.0), 5.0, (3.8, 4.2), 0.1)
        array([[(275.0, 3.8), (275.0, 3.9), (275.0, 4.0), (275.0, 4.1),
                (275.0, 4.2)],
               [(280.0, 3.8), (280.0, 3.9), (280.0, 4.0), (280.0, 4.1),
                (280.0, 4.2)],
               [(285.0, 3.8), (285.0, 3.9), (285.0, 4.0), (285.0, 4.1),
                (285.0, 4.2)],
               [(290.0, 3.8), (290.0, 3.9), (290.0, 4.0), (290.0, 4.1),
                (290.0, 4.2)],
               [(295.0, 3.8), (295.0, 3.9), (295.0, 4.0), (295.0, 4.1),
                (295.0, 4.2)],
               [(300.0, 3.8), (300.0, 3.9), (300.0, 4.0), (300.0, 4.1),
                (300.0, 4.2)],
               [(305.0, 3.8), (305.0, 3.9), (305.0, 4.0), (305.0, 4.1),
                (305.0, 4.2)]], dtype=object)
        """
                                                       
        rise_series, rotation_series = self.generate_unique_rise_rotation_or_pitch_unitnumber_arrays(helical_rise_range,
        helical_rise_increment, helical_rotation_range, helical_rotation_increment)
        
        symmetry_grid = self.convert_rise_rotation_or_pitch_unitnumber_series_to_grid_of_tuples(rise_series,
        rotation_series)
                
        return symmetry_grid
    
    
    def convert_rise_rotation_pair_to_pitch_unit_pair(self, each_rise_rotation_pair):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> s = SegClassReconstruct()
        >>> s.convert_rise_rotation_pair_to_pitch_unit_pair((1.408, 22.03))
        (23.00862460281434, 16.34135270086246)
        >>> s.convert_rise_rotation_pair_to_pitch_unit_pair((1.408, -22.03))
        (-23.00862460281434, -16.34135270086246)
        >>> s.convert_rise_rotation_pair_to_pitch_unit_pair((-1.408, -22.03))
        (23.00862460281434, -16.34135270086246)
        >>> s.convert_rise_rotation_pair_to_pitch_unit_pair((-1.408, 22.03))
        (-23.00862460281434, 16.34135270086246)
        """
        rise = each_rise_rotation_pair[0]
        rotation = each_rise_rotation_pair[1]
        unit_number = 360 / rotation
        pitch = rise * unit_number
        pitch_unit_pair = (pitch, unit_number)
        
        return pitch_unit_pair
    
    
    def convert_pitch_unit_pair_to_rise_rotation_pairs(self, pitch, unit_number):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> s = SegClassReconstruct()
        >>> s.convert_pitch_unit_pair_to_rise_rotation_pairs(23, 16.3333334)
        (1.4081632595585172, 22.040816236568094)
        >>> s.convert_pitch_unit_pair_to_rise_rotation_pairs(-23, -16.3333334)
        (1.4081632595585172, -22.040816236568094)
        >>> s.convert_pitch_unit_pair_to_rise_rotation_pairs(23, -16.3333334)
        (-1.4081632595585172, -22.040816236568094)
        >>> s.convert_pitch_unit_pair_to_rise_rotation_pairs(-23, 16.3333334)
        (-1.4081632595585172, 22.040816236568094)
        """
        rise = pitch / unit_number
        rotation = 360.0 / unit_number
        rise_rotation_pair = (rise, rotation)
        
        return rise_rotation_pair
    
    
    def convert_pitch_unit_grid_to_rise_rotation_grid(self, pitch_unit_grid, shape=None):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct 
        >>> s = SegClassReconstruct()
        >>> p_u_grid = s.generate_rise_rotation_or_pitch_unitnumber_pairs_for_symmetry_grid([10,30], 10, [10,40], 10) 
        >>> s.convert_pitch_unit_grid_to_rise_rotation_grid(p_u_grid)
        array([[(1.0, 36.0), (0.5, 18.0), (0.3333333333333333, 12.0), (0.25, 9.0)],
               [(2.0, 36.0), (1.0, 18.0), (0.6666666666666666, 12.0), (0.5, 9.0)],
               [(3.0, 36.0), (1.5, 18.0), (1.0, 12.0), (0.75, 9.0)]], dtype=object)
        """
        
        rise_rotation_seq = np.zeros(pitch_unit_grid.size, dtype=tuple)
        for each_index, each_pitch_unit_pair in enumerate(pitch_unit_grid.ravel()):
            rise_rotation_pair = self.convert_pitch_unit_pair_to_rise_rotation_pairs(each_pitch_unit_pair[0],
            each_pitch_unit_pair[1])
            
            rise_rotation_seq[each_index]=rise_rotation_pair
            
        if shape is None:
            rise_rotation_grid = rise_rotation_seq.reshape(pitch_unit_grid.shape)
        else:
            rise_rotation_grid = rise_rotation_seq.reshape(shape)
        
        return rise_rotation_grid
    
    
    def get_standard_proj_parameters(self, out_of_plane_tilt_angle):
        phi = 0.0
        corrected_theta = 90.0 + out_of_plane_tilt_angle
        psi = 270.0
        tx = 0.0
        ty = 0.0
        
        return phi, corrected_theta, psi, tx, ty
    
            
    def set_projection_transform_for_helix_azimuth_zero(self, segment, out_of_plane_tilt_angle):
        phi, theta, psi, sx, sy = self.get_standard_proj_parameters(out_of_plane_tilt_angle)
        
        t2 = Transform({'type':'spider', 'phi':phi, 'theta':theta, 'psi':psi})
        t2.set_trans(Vec2f(-sx, -sy))
        segment.set_attr('xform.projection', t2)
        
        return segment
    

    def clear_previous_alignment_parameters_and_copy_class_to_local_directory(self, infile, classno,
    out_of_plane_tilt_angle):
        class_avg = EMData()
        class_avg.read_image(infile, classno)
        class_avg = self.set_projection_transform_for_helix_azimuth_zero(class_avg, out_of_plane_tilt_angle)
        local_input_file = os.path.basename(infile)
        class_avg.write_image(local_input_file)
        
        return local_input_file
    
    
class SegClassReconstructCylinderMask(SegClassReconstructPreparation):

    def make_smooth_cylinder_mask(self, outer_diameter_in_pixel, inner_diameter_in_pixel, segment_size_in_pixel,
    segment_height_in_pixel=None, width_falloff=0.1):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct      
        >>> from EMAN2 import EMNumPy
        >>> cylinder = SegClassReconstruct().make_smooth_cylinder_mask(8,4,10)
        >>> EMNumPy.em2numpy(cylinder)[5]
        array([[  6.85500383e-01,   6.85500383e-01,   6.85500383e-01,
                  6.85500383e-01,   6.85500383e-01,   6.85500383e-01,
                  6.85500383e-01,   6.85500383e-01,   6.85500383e-01,
                  6.85500383e-01],
               [  6.85500383e-01,   6.85500383e-01,   6.85500383e-01,
                  5.27863979e-01,   8.76894474e-01,   1.00000000e+00,
                  8.76894474e-01,   5.27863979e-01,   6.85500383e-01,
                  6.85500383e-01],
               [  6.85500383e-01,   6.85500383e-01,   7.57359564e-01,
                  9.67862368e-01,   9.31746781e-01,   9.18525219e-01,
                  9.31746781e-01,   9.67862368e-01,   7.57359564e-01,
                  6.85500383e-01],
               [  6.85500383e-01,   5.27863979e-01,   9.67862368e-01,
                  8.67420673e-01,   6.90981150e-01,   6.20666146e-01,
                  6.90981150e-01,   8.67420673e-01,   9.67862368e-01,
                  5.27863979e-01],
               [  6.85500383e-01,   8.76894474e-01,   9.31746781e-01,
                  6.90981150e-01,   2.57088304e-01,   5.96046448e-08,
                  2.57088304e-01,   6.90981150e-01,   9.31746781e-01,
                  8.76894474e-01],
               [  6.85500383e-01,   1.00000000e+00,   9.18525219e-01,
                  6.20666146e-01,   5.96046448e-08,   5.96046448e-08,
                  5.96046448e-08,   6.20666146e-01,   9.18525219e-01,
                  1.00000000e+00],
               [  6.85500383e-01,   8.76894474e-01,   9.31746781e-01,
                  6.90981150e-01,   2.57088304e-01,   5.96046448e-08,
                  2.57088304e-01,   6.90981150e-01,   9.31746781e-01,
                  8.76894474e-01],
               [  6.85500383e-01,   5.27863979e-01,   9.67862368e-01,
                  8.67420673e-01,   6.90981150e-01,   6.20666146e-01,
                  6.90981150e-01,   8.67420673e-01,   9.67862368e-01,
                  5.27863979e-01],
               [  6.85500383e-01,   6.85500383e-01,   7.57359564e-01,
                  9.67862368e-01,   9.31746781e-01,   9.18525219e-01,
                  9.31746781e-01,   9.67862368e-01,   7.57359564e-01,
                  6.85500383e-01],
               [  6.85500383e-01,   6.85500383e-01,   6.85500383e-01,
                  5.27863979e-01,   8.76894474e-01,   1.00000000e+00,
                  8.76894474e-01,   5.27863979e-01,   6.85500383e-01,
                  6.85500383e-01]], dtype=float32)
        """ 
        if segment_height_in_pixel is None:
            segment_height_in_pixel = segment_size_in_pixel
            
        vol = np.zeros((segment_height_in_pixel, segment_size_in_pixel, segment_size_in_pixel))
        
        circle_plane = ParticleAlign2d().make_smooth_circular_mask(outer_diameter_in_pixel, inner_diameter_in_pixel,
        segment_size_in_pixel, width_falloff)
        circle_plane_np = np.copy(EMNumPy.em2numpy(circle_plane))
        
        for each_plane in list(range(segment_height_in_pixel)):
            vol[each_plane] = circle_plane_np
            
        cylvol = EMNumPy.numpy2em(np.copy(vol))
        
        return cylvol
    
    
    def prepare_volume_locally(self, vol):
        volsize_x=vol.get_xsize()
        volsize_y=vol.get_ysize()
        volsize_z=vol.get_zsize()
        K = 6
        alpha = 1.75
        
#        if volume_size_too_big_reduce_memory_consumption:
#            npad = 1
#        else:
#            npad = 2
            
        npad = 2
        if volsize_x == volsize_z:
            pad_size = int(volsize_x*npad)
            kbx    = Util.KaiserBessel(alpha, K, volsize_x/2, K/(2.*pad_size), pad_size)
            volft = vol.copy()
            volft.divkbsinh(kbx)
            volft = volft.norm_pad(False, npad)
            volft.do_fft_inplace()
            volft.center_origin_fft()
            volft.fft_shuffle()
            kby = None
            kbz = None
        else:
            padsize_x     = volsize_x*npad
            padsize_y     = volsize_y*npad
            padsize_z     = volsize_z*npad
            # support of the window
            kbx    = Util.KaiserBessel(alpha, K, volsize_x/2, K/(2.*padsize_x), padsize_x)
            kby    = Util.KaiserBessel(alpha, K, volsize_y/2, K/(2.*padsize_y), padsize_y)
            kbz    = Util.KaiserBessel(alpha, K, volsize_z/2, K/(2.*padsize_z), padsize_z)
            volft = vol.copy()
            volft.divkbsinh_rect(kbx,kby,kbz)
            volft = volft.norm_pad(False, npad)
            volft.do_fft_inplace()
            volft.center_origin_fft()
            volft.fft_shuffle()
            
        return  volft, kbx, kby, kbz
            
            
    def project_locally(self, vol, params, stack=None):
        volft, kbx, kby, kbz = self.prepare_volume_locally(vol)
        if stack is None:
            projs = []
        else:
            projs = stack
            
        for each_prj_id, each_param in enumerate(params):
            proj = prgs(volft, kbx, each_param, kby, kbz)
            set_params_proj(proj, [each_param[0], each_param[1], each_param[2], -each_param[3], -each_param[4]])
            proj.set_attr_dict({'active':1, 'ctf_applied':0})
            if stack is None:
                projs.append(proj)
            else:
                proj.write_image(stack, each_prj_id)
        
        return projs