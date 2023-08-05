# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to align segments from helical specimens with a restrained in-plane rotation of 0 or 180 +/- delta degrees
"""
from EMAN2 import EMData, EMUtil, Util
from alignment import Numrinit, ringwe
from collections import namedtuple, defaultdict
from fundamentals import rot_shift2D
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import OpenMpi, Temporary
from spring.segment2d.segment import Segment
from spring.segment2d.segmentexam import SegmentExam
from tabulate import tabulate
from utilities import model_blank, compose_transform2, get_params2D
import numpy as np
import os


class SegmentAlign2dPar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'segmentalign2d'
        self.proginfo = __doc__
        self.code_files = ['segmentalign2d_prep', self.progname, self.progname + '_mpi']

        self.align2d_features = Features()
        self.feature_set = self.align2d_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    

    def add_mask_dimension_to_features(self):
        self.feature_set = self.align2d_features.set_helix_width_and_height(self.feature_set)
        

    def define_parameters_and_their_properties(self):
        self.feature_set = self.align2d_features.set_inp_stack(self.feature_set)
        self.feature_set = self.align2d_features.set_out_stack(self.feature_set)
        self.feature_set = self.set_iteration_count(self.feature_set)
        
        self.feature_set = self.set_reference_option(self.feature_set)

        self.feature_set = self.align2d_features.set_image_reference_stack(self.feature_set, 'beginner', 
        'Reference option')

        self.feature_set = self.align2d_features.set_reference_update_option(self.feature_set)
        self.feature_set = self.align2d_features.set_reference_output_aligned(self.feature_set)
        self.feature_set = self.align2d_features.set_pixelsize(self.feature_set)
        
        self.add_mask_dimension_to_features()

        self.feature_set = self.set_refinement_option(self.feature_set)
        self.feature_set = self.align2d_features.set_absolute_translation_limit(self.feature_set, 'Local refinement')
        self.feature_set = self.align2d_features.set_internal_binning(self.feature_set)
        self.feature_set = self.align2d_features.set_alignment_rotation_and_translation(self.feature_set)
        
        self.feature_set = self.align2d_features.set_filter_options(self.feature_set)
        self.feature_set = self.set_frc_based_filter_option(self.feature_set)
        
        self.feature_set = self.align2d_features.set_mpi(self.feature_set)
        self.feature_set = self.align2d_features.set_ncpus(self.feature_set)
        self.feature_set = self.align2d_features.set_temppath(self.feature_set)
        

    def set_reference_option(self, feature_set):
        inp14 = 'Reference option'
        feature_set.parameters[inp14] = True
        
        feature_set.hints[inp14] = 'Provide a stack of images as a reference. If not ticked, a simple average of ' +\
        'the provided image stack will be used.'
        
        feature_set.level[inp14]='beginner'
        
        return feature_set
    
        
    def set_iteration_count(self, feature_set):
        inp7 = 'Number of iterations'
        feature_set.parameters[inp7] = int(2)
        feature_set.hints[inp7] = 'Number of iteration cycles of multi-reference alignment. Internally images' + \
        'will be binned to speed up processing.'
        feature_set.properties[inp7] = feature_set.Range(1, 200, 1)
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    
    
    def set_refinement_option(self, feature_set):
        inp14 = 'Local refinement'
        feature_set.parameters[inp14] = False
        
        feature_set.hints[inp14] = 'This option can be used to refine locally around the alignment parameters ' + \
        'stored in the header of the image stack.'
        
        feature_set.level[inp14]='expert'
        
        return feature_set
    
    
    def set_frc_based_filter_option(self, feature_set):
        inp14 = 'Automatic filter option'
        feature_set.parameters[inp14] = bool(True)
        
        feature_set.hints[inp14] = 'Automatic filter design derived from decay of Fourier ring correlation between ' + \
        'images.'
        
        feature_set.level[inp14]='expert'
        
        return feature_set
    

    def define_program_states(self):
        self.feature_set.program_states['prepare_alignment']='Prepare alignment'
        self.feature_set.program_states['prepare_reference_images_for_alignment']='Prepare reference images ' + \
        'for alignment'
        
        self.feature_set.program_states['align_images_to_references']='Aligns images to reference'
        
        self.feature_set.program_states['pass_alignment_parameters_from_reference_groups_to_images']='Apply ' + \
        'alignment parameters to images'

class SegmentAlign2dPreparation(object):
    """
    * Class to prepare iterative alignment of segments
    """

    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            self.p = self.feature_set.parameters

            self.set_given_parameters()
#            self.set_hidden_parameters()
            

    def define_helix_or_particle_dimensions(self):
        self.helixwidth, self.helixheight = self.p['Estimated helix width and height in Angstrom']
        self.helixwidthpix = int(round(self.helixwidth / self.pixelsize))
        self.helixheightpix = int(round(self.helixheight / self.pixelsize))

    def set_given_parameters(self):
        self.alignment_stack_name = self.p['Image input stack']
        self.infile = self.alignment_stack_name
        self.outfile = self.p['Image output stack']
        self.number_of_iterations=self.p['Number of iterations']
        
        self.reference_stack_name = self.p['Image reference stack']
        self.update_references = self.p['Update references']
        self.aligned_averages = self.p['Aligned average stack']
        self.pixelsize = self.p['Pixel size in Angstrom']
        self.reference_option = self.p['Reference option']
        self.define_helix_or_particle_dimensions()
        
        self.binfactor = self.p['Internal binning factor']
        
        self.restrain_inplane_rotation = self.p['Limit in-plane rotation']
        self.delta_psi = self.p['Delta in-plane rotation angle']
        if not self.restrain_inplane_rotation:
            self.delta_psi = 180
        self.x_range_A = self.p['X and Y translation range in Angstrom'][0]
        self.y_range_A = self.p['X and Y translation range in Angstrom'][1]
        
        self.refine_locally = self.p['Local refinement']
        self.x_limit_A, self.y_limit_A = self.p['Absolute X and Y translation limit in Angstrom']
        if not self.refine_locally:
            self.x_limit_A = self.x_range_A
            self.y_limit_A = self.y_range_A
        
        self.low_pass_filter_option = self.p['Low-pass filter option']
        self.high_pass_filter_option = self.p['High-pass filter option']
        self.high_pass_filter_cutoff = self.p['High and low-pass filter cutoffs in 1/Angstrom'][0]
        self.low_pass_filter_cutoff = self.p['High and low-pass filter cutoffs in 1/Angstrom'][1]
        self.custom_filter_option = self.p['Custom filter option']
        self.custom_filter_file = self.p['Custom-built filter file']
        self.bfactor = self.p['B-Factor']
        self.frc_filter_option = self.p['Automatic filter option']
        self.mpi_option = self.p['MPI option']
        self.cpu_count = self.p['Number of CPUs']
        self.temppath = self.p['Temporary directory']
        
        
    def prepare_cosine_falloff(self, image_dimension, start_falloff, falloff_length):
        """
        >>> from spring.segment2d.segmentalign2d import SegmentAlign2d
        >>> SegmentAlign2d().prepare_cosine_falloff(30, 7, 5)
        array([ 1.       ,  1.       ,  1.       ,  1.       ,  1.       ,
                1.       ,  1.       ,  0.9330127,  0.75     ,  0.5      ,
                0.25     ,  0.0669873,  0.       ,  0.       ,  0.       ])
        >>> SegmentAlign2d().prepare_cosine_falloff(50, 21, 10)
        array([ 1.        ,  1.        ,  1.        ,  1.        ,  1.        ,
                1.        ,  1.        ,  1.        ,  1.        ,  1.        ,
                1.        ,  1.        ,  1.        ,  1.        ,  1.        ,
                1.        ,  1.        ,  1.        ,  1.        ,  1.        ,
                1.        ,  0.97974649,  0.92062677,  0.82743037,  0.70770751])

        """
        coeff = np.ones(image_dimension / 2)
        coeff[start_falloff:] = 0.0
        
        falloff = (np.cos(np.linspace(0, 1, falloff_length + 2) * np.pi) + 1) / 2
        
        end_falloff = min(start_falloff + falloff_length, len(coeff))
        diff_length = len(coeff) - (start_falloff + falloff_length)

        if diff_length < 0:
            premature_end = falloff_length + diff_length + 1
            true_falloff = falloff[1:premature_end]
        else: 
            true_falloff = falloff[1:-1]
            
        coeff[start_falloff:end_falloff]=true_falloff
        
        return coeff
    
        
    def prepare_bfactor_coefficients(self, bfactor, pixelsize, image_dimension, cutoff_A=None):
        """
        >>> from spring.segment2d.segmentalign2d import SegmentAlign2d
        >>> SegmentAlign2d().prepare_bfactor_coefficients(0, 1.0, 50)
        array([ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,
                1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.])
        >>> SegmentAlign2d().prepare_bfactor_coefficients(100, 1.0, 50)
        array([ 1.        ,  0.98920796,  0.95752564,  0.90696062,  0.84062374,
                0.76241263,  0.67663385,  0.58761458,  0.49935179,  0.41523683,
                0.33787832,  0.26902956,  0.20961139,  0.15981037,  0.1192258 ,
                0.08703837,  0.06217652,  0.04346276,  0.02972922,  0.0198987 ,
                0.01303291,  0.00835282,  0.00523842,  0.00321471,  0.00193045])
        >>> SegmentAlign2d().prepare_bfactor_coefficients(-100, 1.0, 50)
        array([   1.        ,    1.01090978,    1.04435845,    1.10258371,
                  1.18959286,    1.3116257 ,    1.4779042 ,    1.70179577,
                  2.00259621,    2.40826423,    2.95964534,    3.7170637 ,
                  4.77073318,    6.25741626,    8.38744639,   11.48918606,
                 16.08324067,   23.00820047,   33.63694445,   50.25453012,
                 76.72884995,  119.72006788,  190.89740003,  311.06981145,
                518.01282467])
        >>> SegmentAlign2d().prepare_bfactor_coefficients(0, 1.0, 50, 4.0)
        array([ 1.       ,  1.       ,  1.       ,  1.       ,  1.       ,
                1.       ,  1.       ,  1.       ,  1.       ,  1.       ,
                1.       ,  1.       ,  1.       ,  0.9330127,  0.75     ,
                0.5      ,  0.25     ,  0.0669873,  0.       ,  0.       ,
                0.       ,  0.       ,  0.       ,  0.       ,  0.       ])
        >>> SegmentAlign2d().prepare_bfactor_coefficients(100, 1.0, 50, 4.0)
        array([ 1.        ,  0.98920796,  0.95752564,  0.90696062,  0.84062374,
                0.76241263,  0.67663385,  0.58761458,  0.49935179,  0.41523683,
                0.33787832,  0.26902956,  0.20961139,  0.1491051 ,  0.08941935,
                0.04351918,  0.01554413,  0.00291145,  0.        ,  0.        ,
                0.        ,  0.        ,  0.        ,  0.        ,  0.        ])
        >>> SegmentAlign2d().prepare_bfactor_coefficients(0.0, 5.0, 50, 12)
        array([ 1.       ,  1.       ,  1.       ,  1.       ,  1.       ,
                1.       ,  1.       ,  1.       ,  1.       ,  1.       ,
                1.       ,  1.       ,  1.       ,  1.       ,  1.       ,
                1.       ,  1.       ,  1.       ,  1.       ,  1.       ,
                1.       ,  0.9330127,  0.75     ,  0.5      ,  0.25     ])

        """
        """
        Niko Grigorieff's bfactor.exe::
        
            % bfactor.exe
            Input 3D map?
            circle.spi
              OPENING SPIDER FORMAT FILE....
             B-factor in A^2
            100
             Gauss filter (1) or cosine edge mask (2)?
            
            2
             Cosine edge filter radius in A?
            1
             Width of edge in pixels?
            1
             Pixel size in A?
            1
             Output 3D map?
            new.spi
              OPENING SPIDER FORMAT FILE....
                
                ===========  ================ 
                 Resolution  Weighting Factor
                ===========  ================ 
                      50.00            1.0000
                      25.00            0.9900
                      16.67            0.9608
                      12.50            0.9139
                      10.00            0.8521
                       8.33            0.7788
                       7.14            0.6977
                       6.25            0.6126
                       5.56            0.5273
                       5.00            0.4449
                       4.55            0.3679
                       4.17            0.2982
                       3.85            0.2369
                       3.57            0.1845
                       3.33            0.1409
                       3.12            0.1054
                       2.94            0.0773
                       2.78            0.0556
                       2.63            0.0392
                       2.50            0.0271
                       2.38            0.0183
                       2.27            0.0122
                       2.17            0.0079
                       2.08            0.0050
                       2.00            0.0032
                       1.92            0.0019
                ===========  ================
        
        Niko Grigorieff's bfactor.exe::
        
            % bfactor.exe
             Input 3D map?
            circle.spi
              OPENING SPIDER FORMAT FILE....
             B-factor in A^2
            -100
             Gauss filter (1) or cosine edge mask (2)?
            1
             Gauss filter radius in A?
            1
             Pixel size in A?
            1
             Output 3D map?
            new.spi
              OPENING SPIDER FORMAT FILE....
                
                ===========  ================
                 Resolution  Weighting Factor
                ===========  ================
                      50.00            1.0000
                      25.00            1.0098
                      16.67            1.0400
                      12.50            1.0922
                      10.00            1.1698
                       8.33            1.2776
                       7.14            1.4230
                       6.25            1.6164
                       5.56            1.8724
                       5.00            2.2118
                       4.55            2.6645
                       4.17            3.2733
                       3.85            4.1009
                       3.57            5.2394
                       3.33            6.8264
                       3.12            9.0703
                       2.94           12.2902
                       2.78           16.9828
                       2.63           23.9316
                       2.50           34.3912
                       2.38           50.4004
                       2.27           75.3241
                       2.17          114.8010
                       2.08          178.4306
                       2.00          282.8170
                       1.92          457.1447
                ===========  ================
        """
        one_over_res = SegmentExam().make_oneoverres(np.arange(image_dimension/2), pixelsize)
        fourier_coefficients = np.exp((-bfactor / 4)*one_over_res**2)
        
        if cutoff_A > 2 * pixelsize:
            start_falloff = int(round(image_dimension * pixelsize / float(cutoff_A)))
            falloff_coeff = self.prepare_cosine_falloff(image_dimension, start_falloff, 5)
            fourier_coefficients *= falloff_coeff
        
        return fourier_coefficients
    
    
    def prepare_filter_function(self, high_pass_filter_option, high_pass_filter_cutoff, low_pass_filter_option,
    low_pass_filter_cutoff, pixelsize, image_dimension, filter_falloff = 0.08, custom_filter_option=False,
    custom_filter_file=None, bfactor=0.0):
        """
        * Function to generate a filter function based on hyperbolic tangent \
        (low-pass, high-pass or band-pass filters are possible)
        
        #. Input: high_pass_filter_option, low_pass_filter_option, 
        custom_filter_option: True or False, high_pass_filter_cutoff, 
        low_pass_filter_cutoff: in 1/Angstrom, pixelsize: Angstrom/pixel, 
        image_dimension: pixel, pixelsize, image_dimension: number of pixels
        filter_falloff: percent of pixels that make up smooth filter falloff
        custom_filter_file: recognizes last column as filter coefficient from 
        provided text file
                    
        #. Output: list of filter coefficients as in Fourier pixels
        
        >>> from spring.segment2d.segmentalign2d import SegmentAlign2d
        >>> sa = SegmentAlign2d()
        >>> sa.prepare_filter_function(True, 0.02, True, 0.08, 5, 10, 0.08) #doctest: +NORMALIZE_WHITESPACE
        [8.2287160299010509e-06, 0.99999853615457568, 1.0, 0.99999853615457568, 
        4.1143580149505254e-06]

        >>> sa.prepare_filter_function(True, 0.04, True, 0.06, 5, 50, 0.05) #doctest: +NORMALIZE_WHITESPACE
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.4444668511591772e-11, 
        0.00092821640674234374, 0.99997168174280127, 0.99999999999925493, 1.0, 
        1.0, 1.0, 0.99999999999925493, 0.99997168174280127, 0.00092821640674228822, 
        2.4444668511591772e-11, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        >>> sa.prepare_filter_function(True, 0.04, False, 0.06, 1.5, 50, 0.05, False, None, -100) #doctest: +NORMALIZE_WHITESPACE
        [5.172734356748137e-05, 0.002565400437652817, 0.051660149853613654, 
        0.06479161976119088, 0.06716260031683237, 0.07014331907922618, 
        0.07396474866331282, 0.07875025482159989, 0.08465798862251377, 
        0.09189094570840427, 0.10070853850346509, 0.11144193977503326, 
        0.124514471444123, 0.14046877432184984, 0.16000315768767867, 
        0.18402045973674444, 0.21369406779466352, 0.2505576217346058, 
        0.2966276062917161, 0.3545718989002555, 0.42794293056222643, 
        0.521502262206533, 0.6416753173042158, 0.7971926179830757, 1.0]
        >>> sa.prepare_filter_function(True, 0.04, False, 0.06, 1.5, 50, 0.05, False, None, 100) #doctest: +NORMALIZE_WHITESPACE
        [0.00083194331592229, 0.04086391086268285, 0.7994182049573009, 
        0.9554175714851911, 0.9257214133064412, 0.8864208155253327, 
        0.8406237416314447, 0.7895406073354527, 0.7344436719295907, 
        0.6766338461617276, 0.6173907887659099, 0.5579275104833195, 
        0.4993517885992762, 0.4426359119476192, 0.38859560599099563, 
        0.33787832130766693, 0.29096045886431027, 0.24815259496665634, 
        0.2096113871510978, 0.1753566038791111, 0.14529162554555938, 
        0.11922579924973033, 0.09689717267500671, 0.07799435496458187, 
        0.06217652402211632]
        >>> sa.prepare_filter_function(False, 0.04, False, 0.06, 1.0, 50, 0.05, False, None, 100) #doctest: +NORMALIZE_WHITESPACE
        [1.0, 0.9892079619944574, 0.9575256423365532, 0.9069606178873836, 
        0.8406237433345053, 0.7624126296654683, 0.676633846161729, 
        0.5876145767179657, 0.4993517885992762, 0.4152368286818413, 
        0.33787832130766693, 0.26902955708479037, 0.2096113871510978, 
        0.15981036888569505, 0.11922579924973033, 0.08703836765622351, 
        0.06217652402211632, 0.04346276456589661, 0.02972921638615875, 
        0.01989870361309264, 0.013032907448509368, 0.008352818518081014, 
        0.0052384160278331, 0.0032147124638421238, 0.0019304541362277093]
        """
        
        if low_pass_filter_option is True:
            freq_lowend = low_pass_filter_cutoff*pixelsize + filter_falloff/2
            low_fall_off = filter_falloff
        else:
            freq_lowend = 0.6
            low_fall_off = 1e-14
            
        if high_pass_filter_option is True:
            freq_highend = high_pass_filter_cutoff*pixelsize - filter_falloff/2
            high_fall_off = filter_falloff
        else:
            freq_highend = 0
            high_fall_off = 1e-14
            
        def compute_filter_value(frequency):
            filter_value = 0.5*(np.tanh(np.pi*(frequency + freq_highend)/(high_fall_off*(freq_highend - freq_lowend))) \
                 - np.tanh(np.pi*(frequency - freq_highend)/(high_fall_off*(freq_highend - freq_lowend)))\
                 - np.tanh(np.pi*(frequency + freq_lowend)/(low_fall_off*(freq_highend - freq_lowend))) \
                 + np.tanh(np.pi*(frequency - freq_lowend)/(low_fall_off*(freq_highend - freq_lowend))))
            return filter_value
        
        frequencies = [f for f in np.linspace(0, 0.5, image_dimension/2)]
        filter_function = [compute_filter_value(each_frequency) for each_frequency in frequencies]
        
        if custom_filter_option is True:
            custom_filter_function = self.read_custom_filter_file(custom_filter_file, image_dimension)
            filter_function = np.array(filter_function)*np.array(custom_filter_function)
        
        if bfactor != 0:
            fourier_coefficients = self.prepare_bfactor_coefficients(bfactor, pixelsize, image_dimension)
            filter_function = filter_function * fourier_coefficients / np.max(fourier_coefficients)
        
        if type(filter_function) != list:
            filter_function = filter_function.tolist()
            
        log_pairs = list(zip(frequencies, filter_function))
        msg = tabulate(log_pairs, ['normalized spatial frequencies', 'filter coefficients'])
        log_info = 'The following filter coefficients have been computed:\n{0}'.format(msg)
            
        self.log.ilog(log_info)
        
        return filter_function
    
    
    def read_custom_filter_file(self, custom_filter_file=None, image_dimension=None):
        """
        * Function to read Fourier coefficients from text file
        """
        if custom_filter_file is None: 
            custom_filter_file = self.custom_filter_file
        if image_dimension is None: 
            image_dimension = self.image_dimension
        
        ffile = open(custom_filter_file, 'r')
        filterrows = ffile.readlines()
        ffile.close()
        
        custom_filter_function = []
        for each_line in filterrows:
            if not each_line.startswith('#') or not each_line.startswith(';'):
                filter_pair = each_line.split()
                error = 'Last column entry filter coefficient could not be interpreted'
                try:
                    error += ' as a number' 
                    filter_coefficient = float(filter_pair[-1].strip())
                except:
                    raise ValueError(error)
                if filter_coefficient < 0 or filter_coefficient > 1:
                    error += ' between 0 and 1.' 
                custom_filter_function.append(filter_coefficient)
            
        if image_dimension/2 != len(custom_filter_function):
            error = """Filter file could not be interpreted. Number of detected rows does not match 
            image dimensions, i.e. Filter file should have 'image dimension/2' x 'frequency, 
            Fourier coefficient' value pairs"""
            raise ValueError(error)
        
        return custom_filter_function
        

    def log_mask_dimensions(self):
        
        return self.log.ilog('Maskfile                    : %s' % ('rectangle of {0} x {1} pixels'.\
        format(self.helixwidthpix, self.helixheightpix)))


    def prepare_mask(self, helixwidthpix, helixheightpix, image_dimension):
        mask = SegmentExam().make_smooth_rectangular_mask(helixwidthpix, helixheightpix, image_dimension)
        
        return mask
        
        
    def prepare_empty_rings(self, first_ring, last_ring, ring_step, full_circle_mode='F'):
        polar_interpolation_parameters = Numrinit(first_ring, last_ring, ring_step, full_circle_mode)
        
        ring_weights = ringwe(polar_interpolation_parameters, full_circle_mode)
        
        return polar_interpolation_parameters, ring_weights
        
        
    def center_and_rotate_image(self, ref_center, file_name, file_info, search_range_pix, delta_psi, y_align=False):
        img = EMData()
        img.read_image(file_name, file_info[0])
        segment_size = img.get_xsize()
        
        mask = SegmentExam().make_smooth_rectangular_mask(self.helixwidthpix, self.helixheightpix, segment_size)
        polar_interpolation_parameters, ring_weights = self.prepare_empty_rings(1, segment_size / 2 - 2, 1)
        
        cimage = self.generate_reference_rings_from_image(ref_center, polar_interpolation_parameters,
        ring_weights, segment_size)
        
        reference_rings = [cimage]
        
        centered_file = os.path.join(self.tempdir, os.path.basename(file_name))
        x_range = search_range_pix
        if not y_align:
            y_range = 0
        else: 
            y_range = x_range
            
        step_x = 0.3
        full_circle_mode = 'F'
        center_x = center_y = segment_size / 2 + 1
        previous_shift_x = previous_shift_y = previous_inplane_angle = 0.0
        
        for each_index, each_image in enumerate(file_info):
            img.read_image(file_name, each_image)
            img *= mask
            
            [inplane_angle, sxst, syst, mirror, matched_reference_id, peak] = Util.multiref_polar_ali_2d_delta(img,
            reference_rings, x_range, y_range, step_x, full_circle_mode, polar_interpolation_parameters, center_x -
            previous_shift_x, center_y - previous_shift_y, previous_inplane_angle, delta_psi)
            
            angb, sxb, syb, ct = compose_transform2(0.0, sxst, syst, 1, -inplane_angle, 0.0, 0.0, 1)
            shift_x = previous_shift_x - sxb
            shift_y = previous_shift_y - syb
            
            centered_img = rot_shift2D(img, inplane_angle, shift_x, shift_y)
            centered_img.write_image(centered_file, each_index)
            
        return centered_file


    def prepare_reference_stack(self, reference_stack_name):
        blank_image = EMData()
        blank_image.read_image(reference_stack_name, 0)
        
        blank_image.to_zero()
        
        reference_stack = []
        reference_features = namedtuple('reference_features', 
        'odd_average even_average total_average variance number_of_images')
        
        references_image_count = EMUtil.get_image_count(reference_stack_name)
        ref_image = EMData()
        for each_ref_id in list(range(references_image_count)):
            ref_image.read_image(reference_stack_name, each_ref_id)
            number_of_images = defaultdict(int)
            
            reference_imgs = reference_features(blank_image.copy(), blank_image.copy(), ref_image.copy(),
            blank_image.copy(), number_of_images)
            
            reference_stack.append(reference_imgs)
        
        return reference_stack


    def average_stack(self, stack, img_info, align=False):
        img = EMData()
        img.read_image(stack)
        
        avg = model_blank(img.get_xsize(), img.get_ysize(), 1, 0)
        for each_image in img_info:
            img.read_image(stack, each_image)
            if align and img.has_attr('xform.align2d'):
                t = img.get_attr('xform.align2d')
                d = t.get_params('2D')
                img = rot_shift2D(img, d['alpha'], d['tx'], d['ty'])
                
            avg += img
            
        avg /= len(img_info)
        
        return avg
        

    def center_reference_images_by_alignment_to_avg(self, file_info, ref_center):
        search_range_pix = int(50 / self.pixelsize)
        
        self.reference_stack_name = \
        self.center_and_rotate_image(ref_center, self.reference_stack_name, file_info, search_range_pix, self.delta_psi)
        
        return self.reference_stack_name

    
    def get_image_list_named_tuple(self):
        return namedtuple('alignments', 'stack_id local_id ref_id shift_x shift_y inplane_angle peak mirror')
    

    def get_image_alignments_from_stack(self, alignment_stack_name):
        stack_image_count = EMUtil.get_image_count(alignment_stack_name)
        image_nt = self.get_image_list_named_tuple()
        img = EMData()
        images_info = []
        for each_local_id, each_image_id in enumerate(list(range(stack_image_count))):
            img.read_image(alignment_stack_name, each_image_id)
            if img.has_attr('xform.align2d') and self.refine_locally:
                inplane_angle, shift_x, shift_y, mirror, scale = get_params2D(img)
                
                inplane_angle, shift_x, shift_y = Segment().convert_rotate_shift_to_shift_rotate_order(inplane_angle,
                shift_x, shift_y)
                
                image_info = image_nt(each_image_id, each_local_id, 0, -shift_x * self.pixelsize, 
                    -shift_y * self.pixelsize, inplane_angle, 0, mirror)
            else:
                image_info = image_nt(each_image_id, each_local_id, 0, 0, 0, 0, 0, 0)
            images_info.append(image_info)
        
        return images_info, img.get_xsize()


    def compute_binfactor_for_desired_resolution(self, desired_resolution, pixelsize):
        """
        >>> from spring.segment2d.segmentalign2d import SegmentAlign2d
        >>> s = SegmentAlign2d()
        >>> resolutions = np.array([24.0, 12.0, 7.0, 3.0])
        >>> s.compute_binfactor_for_desired_resolution(resolutions, 2.4)
        array([3, 2, 1])
        >>> s.compute_binfactor_for_desired_resolution(resolutions, 1.2)
        array([7, 3, 2, 1])
        >>> s.compute_binfactor_for_desired_resolution(resolutions, 1.372)
        array([6, 3, 2, 1])
        """
        binfactor = np.array(np.round(desired_resolution / (3 * pixelsize)), dtype=int)
        binfactor = binfactor[binfactor >= 1]
        
        return binfactor
    

    def get_align_info_nt(self):
        align_info = namedtuple('align_info', 'iteration_id pixelsize binfactor')

        return align_info


    def define_flow_of_alignment(self, pixelsize, binfactor, iteration_count, range_A):
        """
        >>> from spring.segment2d.segmentalign2d import SegmentAlign2d
        >>> SegmentAlign2d().define_flow_of_alignment(1.2, 2, 2, 50) #doctest: +NORMALIZE_WHITESPACE
        [align_info(iteration_id=0, pixelsize=8.4000000000000004, binfactor=7), 
        align_info(iteration_id=1, pixelsize=8.4000000000000004, binfactor=7), 
        align_info(iteration_id=0, pixelsize=3.5999999999999996, binfactor=3), 
        align_info(iteration_id=1, pixelsize=3.5999999999999996, binfactor=3), 
        align_info(iteration_id=0, pixelsize=2.3999999999999999, binfactor=2), 
        align_info(iteration_id=1, pixelsize=2.3999999999999999, binfactor=2)]
        
        >>> SegmentAlign2d().define_flow_of_alignment(5.0, 2, 5, 50) #doctest: +NORMALIZE_WHITESPACE
        [align_info(iteration_id=0, pixelsize=10.0, binfactor=2), 
        align_info(iteration_id=1, pixelsize=10.0, binfactor=2), 
        align_info(iteration_id=2, pixelsize=10.0, binfactor=2), 
        align_info(iteration_id=3, pixelsize=10.0, binfactor=2), 
        align_info(iteration_id=4, pixelsize=10.0, binfactor=2)]
        
        >>> SegmentAlign2d().define_flow_of_alignment(5.0, 1, 5, 50) #doctest: +NORMALIZE_WHITESPACE
        [align_info(iteration_id=0, pixelsize=10.0, binfactor=2), 
        align_info(iteration_id=1, pixelsize=10.0, binfactor=2), 
        align_info(iteration_id=2, pixelsize=10.0, binfactor=2), 
        align_info(iteration_id=3, pixelsize=10.0, binfactor=2), 
        align_info(iteration_id=4, pixelsize=10.0, binfactor=2), 
        align_info(iteration_id=0, pixelsize=5.0, binfactor=1), 
        align_info(iteration_id=1, pixelsize=5.0, binfactor=1), 
        align_info(iteration_id=2, pixelsize=5.0, binfactor=1), 
        align_info(iteration_id=3, pixelsize=5.0, binfactor=1), 
        align_info(iteration_id=4, pixelsize=5.0, binfactor=1)]
        """
        align_info = self.get_align_info_nt()
        
        alignment_info = []
        bin_factor_series = self.compute_binfactor_for_desired_resolution(np.array([24.0, 12.0, 7.0, 3.0]), pixelsize)
        bin_factor_series = bin_factor_series[bin_factor_series >= binfactor]
        
        for each_bin_factor in bin_factor_series:
            for each_iteration in list(range(iteration_count)):
                alignment_info.append(align_info(each_iteration, each_bin_factor * pixelsize, each_bin_factor))
        
        self.log.ilog('The following flow of alignment has been determined: {0}'.format(alignment_info.__str__()))
        
        return alignment_info
    
    
    def prepare_alignment(self):
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        self.tempdir = Temporary().mktmpdir(self.temppath)
            
        self.log.fcttolog()
        
        images_info, self.image_dimension = self.get_image_alignments_from_stack(self.alignment_stack_name)
        
        if not self.reference_option:
            image_ids = [each_image.local_id for each_image in images_info]
            ref_center = self.average_stack(self.alignment_stack_name, image_ids, align=True)
            ref_center.write_image('average.hdf')
        
            self.reference_stack_name = 'average.hdf'
            
        alignment_info = self.define_flow_of_alignment(self.pixelsize, self.binfactor, self.number_of_iterations,
        max(self.x_range_A, self.y_range_A))
        
        self.log.plog(10)
        
        return alignment_info, images_info
        