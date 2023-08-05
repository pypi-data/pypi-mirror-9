#!/usr/bin/env python
# Author: Carsten Sachse 21-Sep-2010
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
* Several classes to define features of programs
"""
from collections import namedtuple
from glob import glob
from multiprocessing import cpu_count
from spring.csinfrastr.cslogger import GetMetaData
from collections import OrderedDict
import os
import time

class FeaturesSupport(object):

    def add_file_extensions_in_comma_separated_string(self, feature_set, inp3):
        return ', {0}'.format(os.extsep).join(feature_set.properties[inp3].ext)

    def add_accepted_file_formats_to_hint(self, feature_set, inp3):
        return 'accepted file formats ({0}).'.\
        format(self.add_file_extensions_in_comma_separated_string(feature_set, inp3))


    def get_diagnostic_output_formats_for_matplotlib(self):
        return ['pdf', 'png', 'bmp', 'emf', 'eps', 'gif', 'jpeg', 'jpg', 'ps', 'raw', 'rgba', 'svg', 'svgz', 'tif',
        'tiff']


    def get_input_micrograph_formats(self):
        return ['tif', 'mrc', 'mrcs', 'spi', 'hdf', 'img', 'hed']
    

    def get_cpu_hint(self):
        return 'Number of processors to be used.'

class FeaturesBinning(object):

    def get_binning_hint(self, image):
        if image in ['micrograph']:
            hint_txt = 'Micrograph is '
        if image in ['segments']:
            hint_txt = 'Segments are '
            
        hint_txt += 'reduced in size by binning'
        
        return hint_txt
    

    def set_binning_option(self, feature_set, default=False, image='micrograph'):
        inp15 = 'Binning option'
        feature_set.parameters[inp15]=bool(default)
        feature_set.hints[inp15]=self.get_binning_hint(image) + '.'
        feature_set.level[inp15]='intermediate'
        
        return feature_set
        
        
    def set_binning_factor(self, feature_set, binfactor=6, image='micrograph'):
        inp16 = 'Binning factor'
        feature_set.parameters[inp16]=int(binfactor)
        feature_set.hints[inp16]=self.get_binning_hint(image) + ' factor.'
        feature_set.properties[inp16]=feature_set.Range(1,20,1)
        feature_set.relatives[inp16]='Binning option'
        feature_set.level[inp16]='intermediate'
        
        return feature_set
    
    
    def set_internal_binning(self, feature_set):
        inp9 = 'Internal binning factor'
        feature_set.parameters[inp9]=2
        feature_set.hints[inp9]='In order to speed up alignments images can be optionally binned.'
        feature_set.properties[inp9]=feature_set.Range(1,20,1)
        feature_set.level[inp9]='intermediate'
        
        return feature_set
    
    
class FeaturesFilter(object):
    def set_high_pass_filter_option(self, feature_set):
        inp15 = 'High-pass filter option'
        feature_set.parameters[inp15] = bool(False)
        feature_set.hints[inp15] = 'Option to high-pass filter images before alignment or band-pass filter in ' + \
        'combination with low-pass filter.'
        feature_set.level[inp15]='intermediate'
        
        return feature_set
    

    def set_low_pass_filter_option(self, feature_set):
        inp10 = 'Low-pass filter option'
        feature_set.parameters[inp10] = bool(True)
        feature_set.hints[inp10] = 'Option to low-pass filter images before alignment or band-pass filter in ' + \
        'combination with high-pass filter.'
        feature_set.level[inp10]='intermediate'

        return feature_set
    
    
    def set_high_and_low_pass_filter_cutoff(self, feature_set):
        inp11 = 'High and low-pass filter cutoffs in 1/Angstrom'
        feature_set.parameters[inp11] = tuple((0.001, 0.09))
        feature_set.hints[inp11] = 'Filter design for high- and low-pass filter with cutoffs in 1/Angstrom. ' + \
        'Maximum spatial frequency is 1/(2*pixelsize).'
        feature_set.properties[inp11] = feature_set.Range(0, 1, 0.001)
        feature_set.relatives[inp11] = ('Low-pass filter option', 'High-pass filter option')
        feature_set.level[inp11]='intermediate'

        return feature_set
    

    def set_custom_filter_option(self, feature_set):
        inp12 = 'Custom filter option'
        feature_set.parameters[inp12] = bool(False)
        feature_set.hints[inp12] = 'Option to custom filter images before alignment.'
        feature_set.level[inp12]='expert'

        return feature_set
    
    
    def set_custom_build_filter_file(self, feature_set):
        inp13 = 'Custom-built filter file'
        feature_set.parameters[inp13] = 'filter_function.dat'
        feature_set.properties[inp13] = feature_set.file_properties(1, ['txt', 'dat'], 'getFile')
        feature_set.hints[inp13] = 'Custom-built filter function with two columns (normalized spatial frequency ' + \
        '0 - 0.5, Fourier filter coefficients between 0 - 1): ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp13) 
        
        feature_set.relatives[inp13] = 'Custom filter option'
        feature_set.level[inp13]='expert'

        return feature_set
    
    
    def set_bfactor_on_images(self, feature_set):
        inp10 = 'B-Factor'
        feature_set.parameters[inp10] = int(0)
        feature_set.properties[inp10]=feature_set.Range(-50000, 50000, 10)
        feature_set.hints[inp10] = 'B-Factor in 1/Angstrom^2 to be applied to images. Zero no modulation of ' + \
        'frequencies. Negative B-factors enhance high-resolution frequencies. Positive B-factors dampen ' + \
        'high-resolution frequencies.'
        feature_set.level[inp10]='expert'

        return feature_set


    def set_layer_line_filter_option(self, feature_set):
        inp5 = 'Filter layer-lines option'
        feature_set.parameters[inp5]=bool(False)
        feature_set.hints[inp5]='Tick if reference is to be filtered iteratively by layer-line mask based on ' + \
        'symmetry parameters.'
        feature_set.level[inp5]='experimental'
        
        return feature_set
    
    
    def set_filter_options(self, feature_set):
        feature_set = self.set_high_pass_filter_option(feature_set)
        feature_set = self.set_low_pass_filter_option(feature_set)
        feature_set = self.set_high_and_low_pass_filter_cutoff(feature_set)
        feature_set = self.set_bfactor_on_images(feature_set)
        feature_set = self.set_custom_filter_option(feature_set)
        feature_set = self.set_custom_build_filter_file(feature_set)
        
        return feature_set
    

class FeaturesAlign(object):
    def set_alignment_pixel_step(self, feature_set):
        inp6 = 'Step size of alignment in pixels'
        feature_set.parameters[inp6] = int(1)
        feature_set.hints[inp6] = 'Alignment search is performed every ...th pixel, higher numbers speed up the ' + \
        'procedure at the cost of alignment accuracy.'
        feature_set.properties[inp6] = feature_set.Range(1, 50, 1)
        feature_set.level[inp6]='expert'
        
        return feature_set


    def set_restrain_in_plane_angular_search_option(self, feature_set):
        inp15 = 'Limit in-plane rotation'
        feature_set.parameters[inp15]=bool(True)
        feature_set.hints[inp15]='Restricts in-plane rotation alignment.'
        feature_set.level[inp15]='intermediate'
        
        return feature_set
    
        
    def set_delta_in_plane_angular_search(self, feature_set):
        inp7 = 'Delta in-plane rotation angle'
        feature_set.parameters[inp7] = 10.0
        feature_set.hints[inp7] = 'Rotational alignment is being performed within +/- delta angle from 0 and 180 ' + \
        'degrees (delta=0 means only 0/180 are checked, delta=180 means no rotational restraint).'
        feature_set.properties[inp7] = feature_set.Range(0.0, 180.0, 1)
        feature_set.relatives[inp7] = 'Limit in-plane rotation'
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    

    def set_x_y_translation(self, feature_set):
        inp8 = 'X and Y translation range in Angstrom'
        feature_set.parameters[inp8]=tuple((50, 50))
        feature_set.hints[inp8]='Translational range of alignment search perpendicular and along helix axis (X: ' + \
        'off-center helical axis, Y: (minimum y-range=helical rise/2).'
        feature_set.properties[inp8]=feature_set.Range(0, 1000, 1)
        feature_set.level[inp8]='intermediate'
        
        return feature_set
    
        
    def set_alignment_rotation_and_translation(self, feature_set):
        feature_set = self.set_restrain_in_plane_angular_search_option(feature_set)
        feature_set = self.set_delta_in_plane_angular_search(feature_set)
        feature_set = self.set_x_y_translation(feature_set)
        
        return feature_set


    def set_absolute_translation_limit(self, feature_set, relative=None):
        inp8 = 'Absolute X and Y translation limit in Angstrom'
        feature_set.parameters[inp8]=tuple((100, 100))
        feature_set.hints[inp8]='Absolute translation limit of alignment search in Angstrom perpendicular ' + \
        'and along helix axis from center of segment. This is useful because iterative alignments tend to move ' + \
        'the helix axis in y-direction.' 
        feature_set.properties[inp8]=feature_set.Range(1, 1000, 1)
        if relative is not None:
            feature_set.relatives[inp8] = (relative, relative)
        feature_set.level[inp8]='intermediate'
        
        return feature_set
    
    
    def set_center_and_rotation_option(self, feature_set):
        inp7 = 'Center option'
        feature_set.parameters[inp7] = bool(True)
        feature_set.hints[inp7] = 'Class averages are centered and rotationally aligned with respect to their helix ' +\
        'axis.'
        feature_set.level[inp7]='expert'

        return feature_set
    

class FeaturesHelix(object):
    def set_pixelsize(self, feature_set):
        inp7 = 'Pixel size in Angstrom'
        feature_set.parameters[inp7]=float(1.163)
        feature_set.hints[inp7]='Pixel size is an imaging parameter.'
        feature_set.properties[inp7]=feature_set.Range(0.001, 100, 0.001)
        feature_set.level[inp7]='beginner'
        
        return feature_set


    def set_helix_width(self, feature_set):
        inp5 = 'Estimated helix width in Angstrom'
        feature_set.parameters[inp5]=int(200)
        feature_set.hints[inp5]='Generous width measure of helix required for rectangular mask.'
        feature_set.properties[inp5]=feature_set.Range(0,1500,10)
        feature_set.level[inp5]='beginner'
        
        return feature_set
    

    def set_helix_width_and_height(self, feature_set):
        inp5 = 'Estimated helix width and height in Angstrom'
        feature_set.parameters[inp5]=((200, 600))
        feature_set.hints[inp5]='Generous width and height measure of helix required for rectangular mask.'
        feature_set.properties[inp5]=feature_set.Range(20,1500,10)
        feature_set.level[inp5]='beginner'
        
        return feature_set
     
     
    def set_exact_helix_width(self, feature_set):
        inp5 = 'Precise helix width in Angstrom'
        feature_set.parameters[inp5]=int(180)
        feature_set.hints[inp5]='Precise width of helix for layer line interpretation.'
        feature_set.properties[inp5]=feature_set.Range(20,1500,10)
        feature_set.level[inp5]='beginner'
        
        return feature_set
    

    def set_helix_inner_outer_diameter(self, feature_set):
        inp5 = 'Estimated helix inner and outer diameter in Angstrom'
        feature_set.parameters[inp5]=tuple((int(0), int(190)))
        feature_set.hints[inp5]='Generous inner and outer diameter of helix required for cylindrical mask in Angstrom.'
        feature_set.properties[inp5]=feature_set.Range(0,1500,10)
        feature_set.level[inp5]='beginner'
        
        return feature_set


    def set_power_cutoff(self, feature_set):
        inp6 = 'Power spectrum resolution cutoff in 1/Angstrom'
        feature_set.parameters[inp6]=float(0.15)
        feature_set.hints[inp6]='Images are binned to obtain a suitable power spectrum.'
        feature_set.properties[inp6]=feature_set.Range(0,1,0.01)
        feature_set.level[inp6]='expert'
        
        return feature_set


class FeaturesHelixSymmetry(FeaturesHelix):
    def set_rise_rotation_or_pitch_unitnumber_choice(self, feature_set):
        inp7 = 'Helical rise/rotation or pitch/number of units per turn choice'
        feature_set.parameters[inp7] = str('rise/rotation')
        feature_set.hints[inp7] = 'Choose whether helical \'rise/rotation\' or \'pitch/unit_number\' of units per ' + \
        'turn pairs are given for generating the helical lattice.'
        
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['rise/rotation', 'pitch/unit_number'],
        'QComboBox')
        
        feature_set.level[inp7]='beginner'

        return feature_set
    
    
    def set_helical_rise_search_range(self, feature_set):
        inp6 = 'Range of helical rise or pitch search in Angstrom'
        feature_set.parameters[inp6] = tuple((1.0, 10.0))
        feature_set.hints[inp6] = 'Helical rise or pitch (Angstrom) range (from ... to ...) to be reconstructed.'
        feature_set.properties[inp6] = feature_set.Range(0, 1000, 0.0001)
        feature_set.level[inp6]='beginner'
        
        return feature_set


    def set_helical_rotation_search_range(self, feature_set):
        inp7 = 'Range of helical rotation in degrees or number of units per turn search'
        feature_set.parameters[inp7] = tuple((1.0, 300.0))
        feature_set.hints[inp7] = 'Helical rotation (degrees) or \'number of units per turn\' range (from ... to ' + \
        '...) to be reconstructed.'
        feature_set.properties[inp7] = feature_set.Range(-360, 360, 0.0001)
        feature_set.level[inp7]='beginner'
        
        return feature_set


    def set_increment_helical_symmetry_search(self, feature_set):
        inp8 = 'Increments of helical symmetry steps in Angstrom or degrees'
        feature_set.parameters[inp8] = tuple((1.0, 0.1))
        feature_set.hints[inp8] = 'Helical rise (Angstrom) and rotation (degrees) increments to be reconstructed.'
        feature_set.properties[inp8] = feature_set.Range(0, 100, 0.001)
        feature_set.level[inp8]='beginner'
        
        return feature_set


    def defined_shared_helical_symmetry_value_range_and_level(self, feature_set, inp8):
        feature_set.properties[inp8] = feature_set.Range(-1000, 1000, 0.001)
        feature_set.level[inp8] = 'beginner'
        
        return feature_set


    def set_helical_symmetry(self, feature_set):
        inp8 = 'Helical symmetry in Angstrom or degrees'
        feature_set.parameters[inp8] = tuple((1.408, 22.03))
        feature_set.hints[inp8] = 'Helical rise/pitch (Angstrom) and rotation (degrees)/number of units per turn ' + \
        'to be imposed to 3D reconstruction.'
        feature_set = self.defined_shared_helical_symmetry_value_range_and_level(feature_set, inp8)
        
        return feature_set


    def set_rotational_symmetry(self, feature_set):
        inp7 = 'Rotational symmetry'
        feature_set.parameters[inp7] = int(1)
        feature_set.hints[inp7] = 'Additional x-fold rotational symmetry or x-number of helix start.'
        feature_set.properties[inp7] = feature_set.Range(1, 100, 1)
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    

    def set_polar_apolar_helix_choice(self, feature_set):
        inp7 = 'Helix polarity'
        feature_set.parameters[inp7] = str('polar')
        feature_set.hints[inp7] = 'Choose whether helix is \'polar\' or \'apolar\'. Polar helices have different ' + \
        'ends at the top and bottom. Only the predominant direction within a helix will be used for the ' + \
        'reconstruction. In apolar helices they are related by 180 degree rotation. Thus each segment can be ' + \
        'inserted twice in the 3D reconstruction in opposite directions.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['polar', 'apolar'], 'QComboBox')
        feature_set.level[inp7]='intermediate'

        return feature_set
    

class FeaturesHelix3dReconstruction(FeaturesHelixSymmetry):
    def set_volume_size_to_be_reconstructed(self, feature_set):
        inp5 = 'Percent of image reconstruction size'
        feature_set.parameters[inp5] = int(50)
        feature_set.hints[inp5] = 'Percent of image dimension to be used for helical reconstruction, i.e. number ' + \
        'of views inserted in reconstruction = (100 - percent)*imagesize in Angstrom / helical rise)'
        
        feature_set.properties[inp5] = feature_set.Range(10, 100, 1)
        feature_set.level[inp5]='expert'

        return feature_set


    def set_helical_symmetry_option(self, feature_set):
        inp5 = 'Symmetrize helix'
        feature_set.parameters[inp5]=bool(True)
        feature_set.hints[inp5]='Tick to impose helical symmetry. Symmetry-related views are incorporated into ' + \
        'final reconstruction.'
        feature_set.level[inp5]='beginner'
        
        return feature_set
    
    
    def set_helical_symmetry_reconstruction(self, feature_set, turn_on=False):
        feature_set = self.set_helix_inner_outer_diameter(feature_set)
        feature_set = self.set_pixelsize(feature_set)
        if turn_on:
            feature_set = self.set_helical_symmetry_option(feature_set)
        feature_set = self.set_rise_rotation_or_pitch_unitnumber_choice(feature_set)
        
        return feature_set
    
    
    def set_helical_symmetry_reconstruction_series(self, feature_set):
        feature_set = self.set_helical_symmetry_reconstruction(feature_set)
        feature_set = self.set_helical_rise_search_range(feature_set)
        feature_set = self.set_helical_rotation_search_range(feature_set)
        feature_set = self.set_increment_helical_symmetry_search(feature_set)
        
        return feature_set



    def set_out_of_plane_tilt_angle(self, feature_set):

        inp7 = 'Out-of-plane tilt angle'
        feature_set.parameters[inp7] = int(0)
        feature_set.hints[inp7] = 'Out-of-plane tilt angle in degrees (0=no out-of-plane tilt) of class average ' + \
        'view used for 3D reconstruction.'
        feature_set.properties[inp7] = feature_set.Range(-40, 40, 1)
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    
    
    def set_out_of_plane_tilt_angle_range(self, feature_set):

        inp7 = 'Out-of-plane tilt angle range'
        feature_set.parameters[inp7] = ((-12, 12))
        feature_set.hints[inp7] = 'Expected out-of-plane tilt angle in degrees (0=no out-of-plane tilt) of helices ' + \
        'used for 3D reconstruction.'
        feature_set.properties[inp7] = feature_set.Range(-40, 40, 1)
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    
    
    def set_angular_projection_count(self, feature_set):
        inp7 = 'Number of projections azimuthal/out-of-plane angle'
        feature_set.parameters[inp7] = ((90, 7))
        feature_set.hints[inp7] = 'Number of projections (e.g. 90 azimuthal projections per 360 degrees ' + \
        '- projection every four degrees, out-of-plane tilt 7 projections from -12 to 12 ' + \
        'degrees to be searched for 3D reconstruction. High- and maximum resolution reconstructions will be further ' +\
        'refined by 5 * number of specified azimuthal and out-of-plane angles.'
        feature_set.properties[inp7] = feature_set.Range(1, 1000, 1)
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    

    def set_keep_intermediate_files_option(self, feature_set, hinttxt=None):
        inp15 = 'Keep intermediate files'
        feature_set.parameters[inp15]=bool(False)
        if hinttxt is None:
            hinttxt ='Keep intermediate projection and diagnostic images (power spectra ' + \
            'and reprojections) which are iteratively generated - EM image stacks are deleted otherwise.'
        feature_set.hints[inp15]=hinttxt
        
        feature_set.level[inp15]='intermediate'
        
        return feature_set
    

class FeaturesParticle(object):
    def set_particle_inner_and_outer_diameter(self, feature_set):
        inp5 = 'Estimated inner and outer particle diameter in Angstrom'
        feature_set.parameters[inp5]=((0, 160))
        feature_set.hints[inp5]='Generous inner and outer diameter measure of particle in Angstrom required for 2D ' + \
        'circular mask (inner diameter > 0 is very rare).'
        feature_set.properties[inp5]=feature_set.Range(0,1500,10)
        feature_set.level[inp5]='beginner'
        
        return feature_set
    
    
class FeaturesPower(object):
    def set_power_tile_size(self, feature_set, size=1800, power_of_2_hint=False):
        inp4 = 'Tile size power spectrum in Angstrom'
        feature_set.parameters[inp4] = int(size)
        feature_set.hints[inp4] = 'Tile size to be used for analysis.'
        if power_of_2_hint:
            feature_set.hints[inp4]+=' It will be internally converted to nearest power-of-two pixel dimensions.'
        feature_set.properties[inp4] = feature_set.Range(1, 10000, 1)
        feature_set.level[inp4]='expert'
        
        return feature_set


    def set_tile_overlap(self, feature_set):
        inp5 = 'Tile overlap in percent'
        feature_set.parameters[inp5] = int(50)
        feature_set.hints[inp5] = 'Overlap influences degree of averaging.'
        feature_set.properties[inp5] = feature_set.Range(0, 90, 1)
        feature_set.level[inp5]='expert'
        
        return feature_set


    def set_input_power_to_analyze(self, feature_set):
        inp1 = 'Analyze power spectrum'
        feature_set.parameters[inp1]=bool(True)
        feature_set.hints[inp1]='Option to analyze experimental power spectrum.'
        feature_set.level[inp1]='beginner'
        
        return feature_set
    
        
    def set_input_power_spectrum(self, feature_set, related=None, level='beginner'):
        inp1 = 'Power spectrum input image'
        feature_set.parameters[inp1]='power.hdf'
        feature_set.properties[inp1]=feature_set.file_properties(1,['hdf'],'getFile')
        feature_set.hints[inp1]='Input power spectrum image: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        feature_set.level[inp1]=level
        if related is not None:
            feature_set.relatives[inp1]=related
        
        return feature_set
    
    
    def set_output_power_spectrum(self, feature_set):
        inp1 = 'Power spectrum output image'
        feature_set.parameters[inp1]='power.hdf'
        feature_set.properties[inp1]=feature_set.file_properties(1,['hdf'],'saveFile')
        feature_set.hints[inp1]='Output power spectrum image: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        
        feature_set.level[inp1]='beginner'
        
        return feature_set
    
    
    def set_output_enhanced_power_spectrum(self, feature_set):
        inp1 = 'Enhanced power spectrum output image'
        feature_set.parameters[inp1]='power_enhanced.hdf'
        feature_set.properties[inp1]=feature_set.file_properties(1,['hdf'],'saveFile')
        feature_set.hints[inp1]='Output enhanced power spectrum image (compensated for decay of amplitudes): ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        
        feature_set.relatives[inp1]='Enhanced power spectrum option'
        feature_set.level[inp1]='expert'
        
        return feature_set
    
    
    def set_enhance_power_option(self, feature_set):
        inp10 = 'Enhanced power spectrum option'
        feature_set.parameters[inp10] = bool(True)
        feature_set.hints[inp10] = 'Option to enhance power spectrum to compensate for decay of amplitudes.'
        feature_set.level[inp10]='expert'

        return feature_set
        

class FeaturesMicrograph(object):

    def set_inp_micrograph(self, feature_set):
        inp1 = 'Micrograph'
        feature_set.parameters[inp1]='cs_scan034.tif'
        feature_set.properties[inp1]=feature_set.file_properties(1, 
        FeaturesSupport().get_input_micrograph_formats(),'getFile')
        
        feature_set.hints[inp1]='Input micrograph: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        
        feature_set.level[inp1]='beginner'
        
        return feature_set
    

    def set_inp_multiple_micrographs(self, feature_set):
        inp1 = 'Micrographs'
        feature_set.parameters[inp1]='cs_scan034.tif'
        
        feature_set.properties[inp1]=feature_set.file_properties(10, FeaturesSupport().get_input_micrograph_formats(), 
        'getFiles')
        
        feature_set.hints[inp1]='Input micrographs: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        
        feature_set.level[inp1]='beginner'

        return feature_set
    
    
class FeaturesInteractive(object):
    def set_interactive_vs_batch_mode(self, feature_set):
        inp3 = 'Batch mode'
        feature_set.parameters[inp3]=bool(False)
        feature_set.hints[inp3]='Batch mode for plot. Otherwise interactive.'
        feature_set.level[inp3]='beginner'
        
        return feature_set
    
    
class FeaturesMpi(object):
    def set_mpi(self, feature_set):
        inp15 = 'MPI option'
        feature_set.parameters[inp15]=bool(True)
        feature_set.hints[inp15]='OpenMPI installed (mpirun).'
        feature_set.level[inp15]='intermediate'
        
        return feature_set


    def set_ncpus(self, feature_set):
        inp9 = 'Number of CPUs'
        feature_set.parameters[inp9]=cpu_count()
        feature_set.hints[inp9]=FeaturesSupport().get_cpu_hint()
        feature_set.properties[inp9]=feature_set.Range(1,1000,1)
        feature_set.relatives[inp9]='MPI option'
        feature_set.level[inp9]='intermediate'
        
        return feature_set
        
        
    def set_ncpus_scan(self, feature_set):
        inp9 = 'Number of CPUs'
        feature_set.parameters[inp9]=2
        feature_set.hints[inp9]=FeaturesSupport().get_cpu_hint() + ' Maximum number corresponds directly to number ' + \
        'of input scans, i.e. no gain in performance if single input micrograph chosen.'
        feature_set.properties[inp9]=feature_set.Range(1,300,1)
        feature_set.relatives[inp9]='MPI option'
        feature_set.level[inp9]='intermediate'
        
        return feature_set
        

class FeaturesSelectionAssist(object):
    def define_option(self, option_name, feature_set):
        inp7 = '{0} select option'.format(option_name.title())
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Choose whether to select any particular {0}.'.format(option_name)
        feature_set.level[inp7]='expert'
        
        return feature_set
        

    def define_include_and_exclude(self, option_name, feature_set):
        inp7 = 'Include or exclude {0}'.format(option_name)
        feature_set.parameters[inp7] = str('include')
        feature_set.hints[inp7] = 'Choose whether to \'include\' or \'exclude\' specified {0}.'.format(option_name)
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['include', 'exclude'], 'QComboBox')
        feature_set.relatives[inp7] = '{0} select option'.format(option_name.title())
        feature_set.level[inp7]='expert'
        
        return feature_set
    

    def define_stringlist(self, option_name_plural, option_name_singular, feature_set, start=1):
        inp8 = '{0} list'.format(option_name_plural.title())
        feature_set.parameters[inp8] = str('1-9, 11, 13')
        feature_set.hints[inp8] = 'List of comma-separated {0} ids, e.g. \'1-10, 12, 14\' (1st {0} is {1}).'.\
        format(option_name_singular, start)
        feature_set.properties[inp8] = feature_set.file_properties(1, ['*'], None)
        feature_set.relatives[inp8] = '{0} select option'.format(option_name_plural.title())
        feature_set.level[inp8]='expert'
        
        return feature_set
    

class FeaturesSelection(FeaturesSelectionAssist):

    def set_in_or_exclude_segments_option(self, feature_set):
        self.define_option('segments', feature_set)
        
        return feature_set
    

    def set_in_or_exclude_segments(self, feature_set):
        feature_set = self.define_include_and_exclude('segments', feature_set)
        
        return feature_set


    def set_segments_from_segment_file_to_be_in_or_excluded(self, feature_set):
        inp8 = 'Segment file'
        feature_set.parameters[inp8] = 'stackid_file.dat'
        feature_set.hints[inp8] = 'File with single column of stack_ids.'
        feature_set.properties[inp8]=feature_set.file_properties(2,['dat', 'txt'],'getFile')
        feature_set.relatives[inp8] = 'Segments select option'
        feature_set.level[inp8]='expert'
         
        return feature_set
    
        
        return feature_set


    def set_in_or_exclude_classes_option(self, feature_set):
        self.define_option('classes', feature_set)
        
        return feature_set
    

    def set_in_or_exclude_classes(self, feature_set):
        feature_set = self.define_include_and_exclude('classes', feature_set)
        
        return feature_set


    def set_classes_to_be_in_or_excluded(self, feature_set):
        feature_set = self.define_stringlist('classes', 'class', feature_set, start=0)
        
        return feature_set


    def set_class_type(self, feature_set):
        inp7 = 'Class type'
        feature_set.parameters[inp7] = str('class_id')
        feature_set.hints[inp7] = 'Choose class type either \'class_id\' based on segmentclass assignments or ' + \
        '\'class_model_id\' based on segmultirefine3d/segclassmodel assigments.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['class_id', 'class_model_id'], 'QComboBox')
        feature_set.relatives[inp7] = 'Classes select option'
        feature_set.level[inp7]='expert'
        
        return feature_set

    
    def set_persistence_class_selection_option(self, feature_set):
        inp7 = 'Persistence class option'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Choose whether to select segments from classes based on class assignments of '+ \
        'neighboring segments.'
        feature_set.level[inp7]='expert'
        
        return feature_set
    

    def set_persistence_class_length(self, feature_set):
        inp8 = 'Persistence class length in Angstrom'
        feature_set.parameters[inp8] = 700
        feature_set.hints[inp8] = 'Length of helix window that will be used to average the class memberships of segments.'
        feature_set.properties[inp8] = feature_set.Range(1,5000,10)
        feature_set.relatives[inp8] = 'Persistence class option'
        feature_set.level[inp8]='expert'
         
        return feature_set
    
    
    def set_persistence_class_occupancy(self, feature_set):
        inp8 = 'Class occupancy threshold'
        feature_set.parameters[inp8] = 0.5
        feature_set.hints[inp8] = 'Class occupancy threshold of segments (between 0 and 1) that belong to specified subset ' + \
        'of classes within persistence length. Segments that have a lower occupancy will be excluded.'
        feature_set.properties[inp8] = feature_set.Range(0,1,0.1)
        feature_set.relatives[inp8] = 'Persistence class option'
        feature_set.level[inp8]='expert'
         
        return feature_set
    
    
    def set_in_or_exclude_helices_option(self, feature_set):
        feature_set = self.define_option('helices', feature_set)
        
        return feature_set
    

    def set_in_or_exclude_helices(self, feature_set):
        feature_set = self.define_include_and_exclude('helices', feature_set)
        
        return feature_set

    
    def set_helices_to_be_in_or_excluded(self, feature_set):
        feature_set = self.define_stringlist('helices', 'helix', feature_set)
        
        return feature_set
    
    
    def set_in_or_exclude_micrographs_option(self, feature_set):
        feature_set = self.define_option('micrographs', feature_set)
        
        return feature_set
    

    def set_in_or_exclude_micrographs(self, feature_set):
        feature_set = self.define_include_and_exclude('micrographs', feature_set)
        
        return feature_set
    
    
    def set_micrographs_to_be_in_or_excluded(self, feature_set):
        feature_set = self.define_stringlist('micrographs', 'micrograph', feature_set)
        
        return feature_set
    
    
    def set_in_or_exclude_curvature_option(self, feature_set):
        inp7 = 'Straightness select option'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Choose whether to select any helices based on straightness.'
        feature_set.level[inp7]='expert'
        
        return feature_set
    

    def set_in_or_exclude_curvature(self, feature_set):
        inp7 = 'Include or exclude straight helices'
        feature_set.parameters[inp7] = str('include')
        feature_set.hints[inp7] = 'Choose whether to \'include\' or \'exclude\' helices of specified persistence length.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['include', 'exclude'], 'QComboBox')
        feature_set.relatives[inp7] = 'Straightness select option'
        feature_set.level[inp7]='expert'
        
        return feature_set


    def get_percent_distribution_hint(self):
        txt='i.e. upper 10 percent of distribution is expressed as 90 - 100 percent range, ' + \
        'lower 20 percent is expressed as 0 - 20 percent etc. '
        return txt 


    def set_curvature_to_be_in_or_excluded(self, feature_set):
        inp8 = 'Persistence length range'
        feature_set.parameters[inp8]=((80, 100))
        feature_set.hints[inp8] = 'Range of persistence length in perecent, ' + self.get_percent_distribution_hint()
        '90 - 100 % corresponds to most straight helices. ' + \
        'Values from database are stored in m, e.g. \'0-0.0001\' (persistence length is: ' + \
        'calculated as p = -ln(2 * (end_to_end_distance / contour_length) ** 2 - 1) / contour_length)), i.e. short ' +\
        'persistence lengths of 1e-9 m are very flexible, 1 m corresponds ' + \
        'to an extremely straight helix (TMV, amyloid beta filaments and DNA have 2.9e-3, 3e-4 and 1e-7 m). ' + \
        'Due to the alignment error of the segments this value may not be absolutely comparable to determined ' + \
        'persistence lengths but still be valid as a relative measure of straightness.'
        feature_set.properties[inp8]=feature_set.Range(0,100,1)
        feature_set.relatives[inp8]=(('Straightness select option', 'Straightness select option'))
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_defocus_option(self, feature_set):
        inp7 = 'Defocus select option'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Choose whether to select any segments based on defocus.'
        feature_set.level[inp7]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_defocus(self, feature_set):
        inp7 = 'Include or exclude defocus range'
        feature_set.parameters[inp7] = str('include')
        feature_set.hints[inp7] = 'Choose whether to \'include\' or \'exclude\' segments of specified defocus.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['include', 'exclude'], 'QComboBox')
        feature_set.relatives[inp7] = 'Defocus select option'
        feature_set.level[inp7]='expert'
        
        return feature_set


    def set_defocus_to_be_in_or_excluded(self, feature_set):
        inp8 = 'Defocus range'
        feature_set.parameters[inp8] = ((10000, 40000))
        feature_set.hints[inp8] = 'Range of defocus in Angstrom, e.g. \'10000-40000\''
        feature_set.properties[inp8] = feature_set.Range(0, 100000, 100)
        feature_set.relatives[inp8] = (('Defocus select option', 'Defocus select option'))
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_astigmatism_option(self, feature_set):
        inp7 = 'Astigmatism select option'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Choose whether to select any segments based on astigmatism.'
        feature_set.level[inp7]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_astigmatism(self, feature_set):
        inp7 = 'Include or exclude astigmatic segments'
        feature_set.parameters[inp7] = str('include')
        feature_set.hints[inp7] = 'Choose whether to \'include\' or \'exclude\' segments of specified astigmatism ' + \
        'amplitude in Angstrom.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['include', 'exclude'], 'QComboBox')
        feature_set.relatives[inp7] = 'Astigmatism select option'
        feature_set.level[inp7]='expert'
        
        return feature_set


    def set_astigmatism_to_be_in_or_excluded(self, feature_set):
        inp8 = 'Astigmatism range'
        feature_set.parameters[inp8] = ((0, 4000))
        feature_set.hints[inp8] = 'Range of astigmatism amplitude (difference between defocus one and two) in ' + \
        ' Angstrom, e.g. \'0-4000\'.'
        feature_set.properties[inp8] = feature_set.Range(0, 100000, 100)
        feature_set.relatives[inp8] = (('Astigmatism select option', 'Astigmatism select option'))
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_prj_ccc_option(self, feature_set):
        inp7 = 'Projection correlation select option'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Choose whether to select any segments based on matched cross-correlation ' + \
        'coefficient.'
        feature_set.level[inp7]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_ccc_prj_match(self, feature_set):
        inp7 = 'Include or exclude segments based on projection correlation'
        feature_set.parameters[inp7] = str('include')
        feature_set.hints[inp7] = 'Choose whether to \'include\' or \'exclude\' segments of specified cross ' + \
        'correlation coefficient with projection.' 
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['include', 'exclude'], 'QComboBox')
        feature_set.relatives[inp7] = 'Projection correlation select option'
        feature_set.level[inp7]='expert'
        
        return feature_set


    def set_ccc_prj_match_to_be_in_or_excluded(self, feature_set):
        inp8 = 'Correlation projection range'
        feature_set.parameters[inp8] = ((60, 100))
        feature_set.hints[inp8] = 'Range of cross-correlation peak between matched projection and segment in percent, ' + \
        self.get_percent_distribution_hint() + 'Values are stored as peak values depending on the pixel dimension, ' + \
        'e.g. 1220.'
        feature_set.properties[inp8] = feature_set.Range(0, 100, 1)
        feature_set.relatives[inp8] = (('Projection correlation select option', 'Projection correlation select option'))
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_layer_ccc_option(self, feature_set):
        inp7 = 'Layer line correlation select option'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Choose whether to select any segments based on layer-line cross-correlation ' + \
        'coefficient.'
        feature_set.level[inp7]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_ccc_layer(self, feature_set):
        inp7 = 'Include or exclude segments based on layer-line correlation'
        feature_set.parameters[inp7] = str('include')
        feature_set.hints[inp7] = 'Choose whether to \'include\' or \'exclude\' segments of specified cross ' + \
        'correlation coefficient with layer lines.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['include', 'exclude'], 'QComboBox')
        feature_set.relatives[inp7] = 'Layer line correlation select option'
        feature_set.level[inp7]='expert'
        
        return feature_set


    def set_ccc_layer_to_be_in_or_excluded(self, feature_set):
        inp8 = 'Correlation layer line range'
        feature_set.parameters[inp8] = ((60, 100))
        feature_set.hints[inp8] = 'Range of cross-correlation between layer lines of power spectrum average and ' + \
        'segment in percent. ' + self.get_percent_distribution_hint() + 'Values in database are stored as ' + \
        'cross correlation coefficient, e.g. \'0.5 - 1.0\'.'
        feature_set.properties[inp8] = feature_set.Range(0, 100, 1)
        feature_set.relatives[inp8] = (('Layer line correlation select option', 'Layer line correlation select option'))
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_out_of_plane_option(self, feature_set):
        inp7 = 'Out-of-plane tilt select option'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Choose whether to select any segments based on out-of-plane tilt angle.'
        feature_set.level[inp7]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_out_of_plane_tilt(self, feature_set):
        inp7 = 'Include or exclude out-of-plane tilted segments'
        feature_set.parameters[inp7] = str('include')
        feature_set.hints[inp7] = 'Choose whether to \'include\' or \'exclude\' segments of specified out-of-plane ' + \
        'tilt angle.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['include', 'exclude'], 'QComboBox')
        feature_set.relatives[inp7] = 'Out-of-plane tilt select option'
        feature_set.level[inp7]='expert'
        
        return feature_set


    def set_out_of_plane_tilt_to_be_in_or_excluded(self, feature_set):
        inp8 = 'Out-of-plane tilt range'
        feature_set.parameters[inp8] = ((-5, 5))
        feature_set.hints[inp8] = 'Range of out-of-plane tilt in degrees, e.g. \'-10 - 10 degrees\'.'
        feature_set.properties[inp8] = feature_set.Range(-50, 50, 0.5)
        feature_set.relatives[inp8] = (('Out-of-plane tilt select option', 'Out-of-plane tilt select option'))
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_helix_shift_x_option(self, feature_set):
        inp7 = 'Shift normal to helix select option'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Choose whether to select any segments based on forward shift difference normal ' + \
        'to helix. This parameter tends to correlate with resolution.'
        feature_set.level[inp7]='expert'
        
        return feature_set
    
    
    def set_in_or_exclude_helix_shift_x(self, feature_set):
        inp7 = 'Include or exclude segments with shift normal to helix'
        feature_set.parameters[inp7] = str('include')
        feature_set.hints[inp7] = 'Choose whether to \'include\' or \'exclude\' segments of specified foward ' + \
        'shift difference normal to helix. \'include\' and 5 Angstrom  will select for segments with a ' + \
        'smaller forward difference. \'exclude\' and 5 Angstrom will select for segments with a larger forward ' + \
        'difference than 5 Angstrom.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['include', 'exclude'], 'QComboBox')
        feature_set.relatives[inp7] = 'Shift normal to helix select option'
        feature_set.level[inp7]='expert'
        
        return feature_set


    def set_helix_shift_x_to_be_in_or_excluded(self, feature_set):
        inp8 = 'Shift normal to helix in Angstrom'
        feature_set.parameters[inp8] = float(5.0)
        feature_set.hints[inp8] = 'Shift normal to helix in Angstrom, e.g. \'5\'.'
        feature_set.properties[inp8] = feature_set.Range(0, 50, 0.5)
        feature_set.relatives[inp8] = 'Shift normal to helix select option'
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_micrograph_and_helix_selection_criteria(self, feature_set):
        feature_set = self.set_in_or_exclude_micrographs_option(feature_set)
        feature_set = self.set_in_or_exclude_micrographs(feature_set)
        feature_set = self.set_micrographs_to_be_in_or_excluded(feature_set)
         
        feature_set = self.set_in_or_exclude_helices_option(feature_set)
        feature_set = self.set_in_or_exclude_helices(feature_set)
        feature_set = self.set_helices_to_be_in_or_excluded(feature_set)
         
        return feature_set
    

    def set_defocus_and_astigmatism_selection_criteria(self, feature_set):
        feature_set = self.set_in_or_exclude_defocus_option(feature_set)
        feature_set = self.set_in_or_exclude_defocus(feature_set)
        feature_set = self.set_defocus_to_be_in_or_excluded(feature_set)

        feature_set = self.set_in_or_exclude_astigmatism_option(feature_set)
        feature_set = self.set_in_or_exclude_astigmatism(feature_set)
        feature_set = self.set_astigmatism_to_be_in_or_excluded(feature_set)

        return feature_set


    def set_curvature_selection_criteria(self, feature_set):
        feature_set = self.set_in_or_exclude_curvature_option(feature_set)
        feature_set = self.set_in_or_exclude_curvature(feature_set)
        feature_set = self.set_curvature_to_be_in_or_excluded(feature_set)

        return feature_set


    def set_selection_criteria_from_segment_table(self, feature_set):
        feature_set = self.set_micrograph_and_helix_selection_criteria(feature_set)
        
        feature_set = self.set_in_or_exclude_segments_option(feature_set)
        feature_set = self.set_in_or_exclude_segments(feature_set)
        feature_set = self.set_segments_from_segment_file_to_be_in_or_excluded(feature_set)

        feature_set = self.set_in_or_exclude_classes_option(feature_set)
        feature_set = self.set_in_or_exclude_classes(feature_set)
        feature_set = self.set_class_type(feature_set)
        feature_set = self.set_classes_to_be_in_or_excluded(feature_set)
        
        feature_set = self.set_persistence_class_selection_option(feature_set)
        feature_set = self.set_persistence_class_length(feature_set)
        feature_set = self.set_persistence_class_occupancy(feature_set)

        feature_set = self.set_curvature_selection_criteria(feature_set)
        
        feature_set = self.set_in_or_exclude_layer_ccc_option(feature_set)
        feature_set = self.set_in_or_exclude_ccc_layer(feature_set)
        feature_set = self.set_ccc_layer_to_be_in_or_excluded(feature_set)
        
        feature_set = self.set_defocus_and_astigmatism_selection_criteria(feature_set)
        
        return feature_set
    
    
    def set_selection_criteria_from_refined_segments_table(self, feature_set):
        feature_set = self.set_in_or_exclude_prj_ccc_option(feature_set)
        feature_set = self.set_in_or_exclude_ccc_prj_match(feature_set)
        feature_set = self.set_ccc_prj_match_to_be_in_or_excluded(feature_set)
        
        feature_set = self.set_in_or_exclude_out_of_plane_option(feature_set)
        feature_set = self.set_in_or_exclude_out_of_plane_tilt(feature_set)
        feature_set = self.set_out_of_plane_tilt_to_be_in_or_excluded(feature_set)
        
        feature_set = self.set_in_or_exclude_helix_shift_x_option(feature_set)
        feature_set = self.set_in_or_exclude_helix_shift_x(feature_set)
        feature_set = self.set_helix_shift_x_to_be_in_or_excluded(feature_set)
        
        return feature_set
    
    
    def set_database_selected(self, feature_set):
        inp1 = 'Selected database'
        feature_set.parameters[inp1] = 'spring_selected.db'
        feature_set.properties[inp1] = feature_set.file_properties(1, ['db'], 'saveFile')
        feature_set.hints[inp1] = 'Segment in this database will be reduced to selected properties. This database ' + \
        'can be used for selected refinement together with the selected output image stack.'
        feature_set.level[inp1]='beginner'
        
        return feature_set
    

class FeaturesStack(object):
    def set_inp_stack(self, feature_set):
        inp1 = 'Image input stack'
        feature_set.parameters[inp1]='protein_stack.hdf'
        feature_set.properties[inp1]=feature_set.file_properties(1,['hdf'],'getFile')
        feature_set.hints[inp1]='Input stack: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        
        feature_set.level[inp1]='beginner'
        
        return feature_set
        
        
    def set_class_avg_stack(self, feature_set):
        inp1 = 'Class average stack'
        feature_set.parameters[inp1] = 'avgerages.hdf'
        feature_set.properties[inp1] = feature_set.file_properties(1, ['hdf'], 'getFile')
        feature_set.hints[inp1] = 'Class average stack: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        
        feature_set.level[inp1]='beginner'
        
        return feature_set


    def set_class_number_to_be_analyzed(self, feature_set):
        inp7 = 'Class number to be analyzed'
        feature_set.parameters[inp7] = int(3)
        feature_set.hints[inp7] = 'Class number to be analyzed (1st class is 0).'
        feature_set.properties[inp7] = feature_set.Range(0, 2000, 1)
        feature_set.level[inp7]='beginner'

        return feature_set
    
    
    def set_class_number_range_to_be_analyzed(self, feature_set):
        inp7 = 'Class number range to be analyzed'
        feature_set.parameters[inp7] = tuple((int(3), int(5)))
        feature_set.hints[inp7] = 'Class number range to be analyzed (1st class is 0).'
        feature_set.properties[inp7] = feature_set.Range(0, 2000, 1)
        feature_set.level[inp7]='beginner'

        return feature_set
    
    
    def set_out_stack(self, feature_set):
        inp1 = 'Image output stack'
        feature_set.parameters[inp1]='protein_stack.hdf'
        feature_set.properties[inp1]=feature_set.file_properties(1,['hdf'],'saveFile')
        feature_set.hints[inp1]='Output stack: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        
        feature_set.level[inp1]='beginner'
        
        return feature_set


    def set_reference_option(self, feature_set):
        inp5 = 'Reference image option'
        feature_set.parameters[inp5]=bool(False)
        feature_set.hints[inp5]='If reference stack desired to continue classification.'
        feature_set.level[inp5]='intermediate'
        
        return feature_set
    
    
    def set_image_reference_stack(self, feature_set, current_level='beginner', relative=None):
        inp1 = 'Image reference stack'
        feature_set.parameters[inp1] = 'protein_reference_stack.hdf'
        feature_set.properties[inp1] = feature_set.file_properties(1, ['spi', 'hdf', 'img', 'hed'], 'getFile')
        feature_set.hints[inp1] = 'Input reference stack: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        
        feature_set.level[inp1]=current_level
        if relative is not None:
            feature_set.relatives[inp1]=relative
        
        return feature_set


    def set_reference_update_option(self, feature_set):
        inp1 = 'Update references'
        feature_set.parameters[inp1] = True
        feature_set.hints[inp1] = 'Check if references should be updated for every iteration. This is useful if ' + \
        'you have a high ratio of images / references and you expect to improve your references. In case you ' + \
        'simply want to match or assign having a low images / references ratio you should turn it off.'
        
        feature_set.level[inp1]='beginner'
        
        return feature_set
    
    
    def set_reference_output_aligned(self, feature_set):
        inp1 = 'Aligned average stack'
        feature_set.parameters[inp1] = 'protein_reference_aligned.hdf'
        feature_set.properties[inp1] = feature_set.file_properties(1, ['spi', 'hdf', 'img', 'hed'], 'saveFile')
        feature_set.hints[inp1] = 'Output aligned reference stack: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        
        feature_set.level[inp1]='beginner'
        feature_set.relatives[inp1]='Update references'
        
        return feature_set
    
    
class FeaturesDatabase(object):
    def set_spring_db_option(self, feature_set, current_level='intermediate', default=True, relative=None):
        inp6 = 'Spring database option'
        feature_set.parameters[inp6] = bool(default)
        feature_set.hints[inp6] = 'If checked will read previous spring.db (Sqlite-compatible database) otherwise ' + \
        'will create new one.'
        feature_set.level[inp6]=current_level
        if relative is not None:
            feature_set.relatives[inp6]=relative 
        
        return feature_set

    
    def set_spring_path(self, feature_set, current_level='intermediate', relative='Spring database option'):
        inp3 = 'spring.db file'
        feature_set.parameters[inp3]='spring.db'
        feature_set.hints[inp3]='Program requires a previously generated spring.db and writes an updated spring.db ' + \
        'database in the working directory.'
        feature_set.properties[inp3]=feature_set.file_properties(1,['db'],'getFile')
        feature_set.relatives[inp3]=relative
        feature_set.level[inp3]=current_level
        
        return feature_set
    

    def set_spring_path_segments(self, feature_set):
        inp3 = 'spring.db file'
        feature_set.parameters[inp3]='spring.db'
        feature_set.hints[inp3]='Program requires a combined spring.db from segment (and optional: ' + \
        'micctfdetermine). An updated spring.db will be created in the working directory.'
        feature_set.properties[inp3]=feature_set.file_properties(1,['db'],'getFile')
        feature_set.level[inp3]='beginner'
        
        return feature_set
    
    
    def set_inp_refinement_path(self, feature_set):
        inp3 = 'refinement.db file'
        feature_set.parameters[inp3]='refinement.db'
        feature_set.hints[inp3]='Requires refinement.db from segmentrefine3d to extract refinment parameters.'
        feature_set.properties[inp3]=feature_set.file_properties(1,['db'],'getFile')
        feature_set.level[inp3]='beginner'
        
        return feature_set
    
    
    def set_grid_database(self, feature_set, singular=True):
        inp9 = 'Grid database'
        feature_set.parameters[inp9]='grid.db'
        if singular:
            file_attr = 'getFile'
        else:
            file_attr = 'getFiles'
        feature_set.properties[inp9]=feature_set.file_properties(1,['db'], file_attr)
        feature_set.hints[inp9]='Grid database with associated metadata from segclassreconstruct or segrefine3dgrid: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp9)
        
        feature_set.level[inp9]='beginner'
        
        return feature_set
    
    
    def set_continue_refinement_option(self, feature_set):
        inp5 = 'Continue refinement option'
        feature_set.parameters[inp5]=bool(False)
        feature_set.hints[inp5]='To continue previous refinement and use final alignment parameters as ' + \
        'starting point. In case no reference structure is provided, it will re-create the final 3D reconstruction ' + \
        'without the projection matching step. When a reference structure is provided, it will perform ' + \
        'projection matching and 3D reconstruction.'
        feature_set.level[inp5]='intermediate'
        
        return feature_set
    
    
    def set_refinementdb_path(self, feature_set):
        inp3 = 'refinement.db file'
        feature_set.parameters[inp3]='refinement.db'
        feature_set.hints[inp3]='Program requires a refinement.db from previous segmentrefine3d. An updated ' + \
        'refinement.db will be created in the working directory.'
        feature_set.properties[inp3]=feature_set.file_properties(1,['db'],'getFile')
        feature_set.relatives[inp3]='Continue refinement option'
        feature_set.level[inp3]='intermediate'
        
        return feature_set
    
    
class FeaturesConvert(object):
    def convert_list_of_numbers_from_entry_string(self, entry, entry_type=int):
        """
        >>> from spring.csinfrastr.csfeatures import Features
        >>> f = Features()
        >>> f.convert_list_of_numbers_from_entry_string('1, 1, 10')
        [1, 1, 10]
        >>> f.convert_list_of_numbers_from_entry_string('1, 1, a', entry_type=float)
        Traceback (most recent call last):
            ...
        ValueError: Entry 'a' could not be interpreted with expected number: <type 'float'>
        """
        converted = []
        for each_entry in entry.split(','):
            try:
                converted.append(entry_type(each_entry.strip()))
            except:
                msg = 'Entry \'{0}\' could not be interpreted with expected number: {1}'.format(each_entry.strip(),
                entry_type)

                raise ValueError(msg)

        return converted
        

    def convert_list_of_specific_strings_from_entry_string(self, entry, quantities=['polar', 'apolar']):
        """
        >>> from spring.csinfrastr.csfeatures import Features
        >>> f = Features()
        >>> f.convert_list_of_specific_strings_from_entry_string('polar, apolar, polar')
        ['polar', 'apolar', 'polar']
        >>> f.convert_list_of_specific_strings_from_entry_string('opolar, apolar, polar')
        Traceback (most recent call last):
            ...
        ValueError: Entry 'opolar' could not be matched with expected: polar, apolar
        """
        converted = []
        for each_entry in entry.split(','):
            if each_entry.strip() in quantities:
                converted.append(each_entry.strip())
            else:
                msg = 'Entry \'{0}\' could not be matched with expected: {1}'.format(each_entry.strip(), 
                ", ".join(quantities))
                raise ValueError(msg)
        
        return converted

    def convert_list_of_data_pairs_from_entry_string(self, entry, quantities=('Layer line position (1/Angstrom)', 
        'Bessel order')):
        """
        >>> from spring.csinfrastr.csfeatures import Features
        >>> f = Features()
        >>> first = '(0.1, -2)'
        >>> entry = first + '; (0.2, 4); (0.3, -6)'
        >>> f.convert_list_of_data_pairs_from_entry_string(first)
        [(0.1, -2)]
        >>> f.convert_list_of_data_pairs_from_entry_string('(10, 50);(20, 80);(30, 30)')
        [(10.0, 50), (20.0, 80), (30.0, 30)]
        >>> f.convert_list_of_data_pairs_from_entry_string(entry)
        [(0.1, -2), (0.2, 4), (0.3, -6)]
        >>> wrong_entry = first + '; (0.2, 4); (0.3, -6g)'
        >>> f.convert_list_of_data_pairs_from_entry_string(wrong_entry) #doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        ValueError: No pairs with comma-separated numbers could be found. 
            Please comply with input format: (Layer line position (1/Angstrom), 
            Bessel order), e.g. '(0.1, -2); (0.2, -3)'
        """
        first_q, second_q = quantities
        error_message = 'No pairs with comma-separated numbers could be found. Please comply with input format: ' + \
        '({0}, {1}), e.g. \'(0.1, -2); (0.2, -3)\''.format(first_q, second_q)

        if entry.find(',') >= 0:
            pass
        else:
            raise ValueError(error_message)
            
        layerline_bessel_pair = []
        isolated_pairs = entry.split(';')
        try:
            for each_pair in isolated_pairs:
                pair = each_pair.strip().strip(')').strip('(')
                layerline_str, bessel_str = pair.split(',')
                if second_q == 'Bessel order':
                    layerline_bessel_pair.append((float(layerline_str), int(bessel_str)))
                else:
                    layerline_bessel_pair.append((float(layerline_str), float(bessel_str)))
        except:
            raise ValueError(error_message)
            
        return layerline_bessel_pair
            
        
    def convert_list_of_files_from_entry_string(self, inputfiles):
        if inputfiles.find('?') >= 0 or inputfiles.find('*') >= 0 or glob(inputfiles) != []:
            inputlist = glob(inputfiles) 
            inputlist.sort()
        elif inputfiles.find(',') >= 0 :
            inputlist = inputfiles.split(',')
        elif inputfiles.find(';') >= 0 :
            inputlist = inputfiles.split(';')
        else:
            inputlist = [inputfiles]
 
        def getabsfilename(infile):
            try:
                absfile = os.path.abspath(infile)
            except OSError:
                errstring = 'File {0} does not exist'.format(infile)
                raise IOError(errstring)
            return absfile

        inputabslist = [ getabsfilename(infile.strip()) for infile in inputlist]

        return inputabslist
    
    
class Features(FeaturesBinning, FeaturesFilter, FeaturesAlign, FeaturesHelix3dReconstruction, FeaturesMicrograph,
FeaturesParticle, FeaturesPower, FeaturesInteractive, FeaturesMpi, FeaturesSelection, FeaturesStack, FeaturesDatabase,
FeaturesConvert):
    """
    * Class that initiates ...Par classes
    """
    def setup(self, sett):
        """
        * Function to set up dictionaries for each program, including parameter, help, range and status information

        """

        # define default input dictionary p, help dictionary h, range dictionary r, status dictionary s
        sett.parameters = OrderedDict()
        sett.hints = OrderedDict()
        sett.properties = OrderedDict() 
        sett.relatives = OrderedDict()
        sett.level = OrderedDict()
        sett.program_states = OrderedDict()
        sett.Range = namedtuple('Range', 'minimum maximum step')
        sett.file_properties = namedtuple('file_properties', 'number ext ftype')
        sett.choice_properties = namedtuple('choice_properties', 'number choices ctype')

        # retrieve metadata from EGG
        sett.eggmeta = GetMetaData(sett.package).release_meta()
        sett.version = sett.eggmeta['Version']

        return sett

    def reduce_features_to_parameters_for_mpi(self, parameters):
        self.parameters = parameters
        
        return self
    


    def get_parameters_in_string(self, parameters):
        par_string = ''
        for name in parameters:
            if parameters[name] is not None:
                par_string += '%-40s = %s\n' % (name, parameters[name])
        
        return par_string

    def write_parameters_in_file(self, parameters, prgparfile):
        parfile = open(prgparfile, 'w')
        
        par_string = self.get_parameters_in_string(parameters)
        
        parfile.write(par_string)
        parfile.close()


    def get_submission_script_str(self, program, parameters):
        header = """\
#!/usr/bin/env python

import subprocess
import time
import os

if 'PBS_O_WORKDIR' in os.environ:
    os.chdir(os.environ['PBS_O_WORKDIR'])

program = '{0}'
par_file_content = \'\'\'
""".format(program)

        par_string = self.get_parameters_in_string(parameters) + '\'\'\''
        
        launch_lines = """\

dir_name = '{prg}_{zeit}_{pid}'.format(prg=os.path.split(program)[-1], zeit=time.strftime('%d_%b_%Y_%H_%M_%S'), \
pid=os.getpid())

par_file_name = '{dir_name}.par'.format(dir_name=dir_name)
f = open(par_file_name, 'w')
f.write(par_file_content)
f.close()

command_line = '{prg} --f {par_file} --d {dir_name}'.format(prg=program, par_file=par_file_name, dir_name=dir_name)
print command_line

subprocess.call(command_line.split())
os.rename(par_file_name, dir_name + os.sep + 'parameters.par')
"""
        return header + par_string + launch_lines

        
    def write_parfile(self, parameters=None, program=None, tag=True):

        if program is None:
            prgparfile = 'parfile_{0}.par'.format(os.getpid())
        else:
            prgparfile = '{prg}_{zeit}_{id}.par'.format(prg=program, zeit=time.strftime('%d_%b_%Y_%H_%M_%S'),
            id=os.getpid())
        if not tag:
            prgparfile = '{prg}.par'.format(prg=program) 
            
        self.write_parameters_in_file(parameters, prgparfile)

        return prgparfile


    def rename_series_of_output_files(self, micrograph_files, outfile):
        """
        >>> from spring.csinfrastr.csfeatures import Features
        >>> f = Features()
        >>> f.rename_series_of_output_files(['test0.mrc'], 'dp.pdf')
        ['dp.pdf']
        >>> f.rename_series_of_output_files(['test0.mrc','test1.mrc'], 'dp.pdf')
        ['dp_test0.pdf', 'dp_test1.pdf']
        """
        if len(micrograph_files) == 1:
            outfiles = [outfile]
        else:
            outfiles = [os.path.splitext(os.path.basename(outfile))[0] + '_' +
            os.path.splitext(os.path.basename(each_micrograph_file))[0] + os.path.splitext(outfile)[-1] for
            each_micrograph_file in micrograph_files]
            
        return outfiles
    

    def set_output_plot(self, feature_set, output, related=None):
        inp2 = 'Diagnostic plot'
        feature_set.parameters[inp2]=str(output)
        
        feature_set.properties[inp2]=feature_set.file_properties(1,
        FeaturesSupport().get_diagnostic_output_formats_for_matplotlib(), 'saveFile')
        
        feature_set.hints[inp2]='Output diagnostic plot: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp2)
        
        feature_set.level[inp2]='beginner'
        if related is not None:
            feature_set.relatives[inp2]=related
        
        return feature_set
    
    
    def set_output_plot_pattern(self, feature_set, output):
        inp2 = 'Diagnostic plot pattern'
        feature_set.parameters[inp2]=str(output)
        
        feature_set.properties[inp2]=feature_set.file_properties(1, 
        FeaturesSupport().get_diagnostic_output_formats_for_matplotlib(), 'saveFile')
        
        feature_set.hints[inp2]='If single input micrograph: name of diagnostic plot file. In case of multiple ' + \
        'input micrographs suffix to be attached to corresponding input micrograph. Output: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp2)
        
        feature_set.level[inp2]='beginner'
        
        return feature_set
    
    
    def set_diagnostic_prefix(self, feature_set, level='beginner', related=None):
        inp3 = 'Diagnostic plot prefix'
        feature_set.parameters[inp3]='diagnostic_plot.pdf'
        feature_set.properties[inp3]=feature_set.file_properties(1, 
        FeaturesSupport().get_diagnostic_output_formats_for_matplotlib(), 'saveFile')
        
        feature_set.hints[inp3]='Output name for diagnostic plots of iterative structure refinement (completion ' + \
        'to \'prefix_XXX.ext\'): ' + FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp3) 
        feature_set.level[inp3]=level
        if related is not None:
            feature_set.relatives[inp3]=related
        
        return feature_set
    
    
    def set_temppath(self, feature_set):
        inp3 = 'Temporary directory'
        feature_set.parameters[inp3]='/tmp'
        feature_set.hints[inp3]='Temporary directory should have fast read and write access.'
        feature_set.properties[inp3]=feature_set.file_properties(1,['*'],'getDir')
        feature_set.level[inp3]='intermediate'
        
        return feature_set


    def set_scanner_step_size(self, feature_set):
        inp3 = 'Scanner step size in micrometer' 
        feature_set.parameters[inp3] = float(7.0)
        feature_set.hints[inp3] = 'Characteristic resolution or step size of scanner in micrometer.'
        feature_set.properties[inp3] = feature_set.Range(1, 1000, 1)
        feature_set.level[inp3] = 'intermediate'
        
        return feature_set

