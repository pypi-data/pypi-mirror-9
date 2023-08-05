# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to iteratively refine 3D structure of helical specimens from segment stacks
"""
from spring.csinfrastr.csfeatures import Features
from spring.segment2d.segment import SegmentPar
from spring.segment2d.segmentselect import SegmentSelect
from spring.segment3d.segclassreconstruct import SegClassReconstruct


class SegmentRefine3dParPreparation(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'       
        self.progname = 'segmentrefine3d'
        self.proginfo = __doc__
        
        self.code_files = ['sr3d_parameters', 'sr3d_prepare', 'sr3d_project', 'sr3d_align', 'sr3d_select', 
                           'segmentselect', 'sr3d_reconstruct', 'sr3d_diagnostics', 'sr3d_main', 'sr3d_mpi']

        self.segmentrefine3d_features = Features()
        self.feature_set = self.segmentrefine3d_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()


    def define_input_output_segmentrefine3d(self):
        self.feature_set = self.set_inp_refinement_stack(self.feature_set)
        self.feature_set = self.set_volume_prefix_refined_structure(self.feature_set)



    def define_segmentrefine3d_parameters(self):
        self.feature_set = self.segmentrefine3d_features.set_diagnostic_prefix(self.feature_set)
        self.feature_set = self.set_iteration_count(self.feature_set)
        self.feature_set = self.set_reference_volume_option(self.feature_set)
        self.feature_set = self.set_reference_volume(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_spring_path_segments(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_continue_refinement_option(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_refinementdb_path(self.feature_set)
        self.set_refinement_strategy_options()
        self.feature_set = self.set_halfset_refinement_option(self.feature_set)
        self.feature_set = self.set_halfset_start(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_filter_options(self.feature_set)
        self.feature_set = self.set_fsc_based_filter_option(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_layer_line_filter_option(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_selection_criteria_from_segment_table(self.feature_set)
        
        self.feature_set = \
        self.segmentrefine3d_features.set_selection_criteria_from_refined_segments_table(self.feature_set)
        
        self.feature_set = self.segmentrefine3d_features.set_keep_intermediate_files_option(self.feature_set)
        
        self.feature_set = self.segmentrefine3d_features.set_helical_symmetry_reconstruction(self.feature_set,
        turn_on=True)
        self.feature_set = self.set_enforce_even_phi_distribution(self.feature_set)
        self.feature_set = self.set_release_cycle_even_phi(self.feature_set)
        self.feature_set = self.set_enforce_pitch_even_phi(self.feature_set)
        self.feature_set = self.set_bin_cutff_enforce_pitch_even_phi(self.feature_set)
        
        self.set_helical_symmetry_parameters()
        self.feature_set = SegmentPar().set_straightening_option(self.feature_set)
        self.feature_set = self.set_helical_continuity_option(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_restrain_in_plane_angular_search_option(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_delta_in_plane_angular_search(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_out_of_plane_tilt_angle_range(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_angular_projection_count(self.feature_set)
        self.feature_set = self.set_image_size_to_be_aligned(self.feature_set)
        self.feature_set = SegmentPar().set_segmentation_step(self.feature_set)
        self.feature_set = self.set_3dctf_correction_option(self.feature_set)
        self.feature_set = self.set_3dctf_correction_intensity_option(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_mpi(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_ncpus(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_temppath(self.feature_set)


    def set_helical_symmetry_parameters(self):
        self.feature_set = self.segmentrefine3d_features.set_helical_symmetry(self.feature_set)
        self.feature_set.relatives['Helical rise/rotation or pitch/number of units per turn choice']='Symmetrize helix'
        self.feature_set.relatives['Helical symmetry in Angstrom or degrees']=(('Symmetrize helix', 'Symmetrize helix'))
        self.feature_set = self.segmentrefine3d_features.set_rotational_symmetry(self.feature_set)
        self.feature_set = self.segmentrefine3d_features.set_polar_apolar_helix_choice(self.feature_set)
        

    def define_parameters_and_their_properties(self):
        self.define_input_output_segmentrefine3d()
        self.define_segmentrefine3d_parameters()


    def define_program_states(self):
        self.feature_set.program_states['project_through_reference_volume_in_helical_perspectives']='Projection ' + \
        'through reference volume'
        
        self.feature_set.program_states['window_and_mask_input_stack']='Window and mask image stack for alignment'
        
        self.feature_set.program_states['unbend_window_and_mask_input_stack']='Unbend and window image stack for ' + \
        'alignment and reconstruction'
        
        self.feature_set.program_states['perform_coarse_and_fine_projection_matching']='Projection matching of ' + \
        'references against image stack'
        
        self.feature_set.program_states['select_segments_based_on_specified_criteria']='Select segments according ' + \
        'to specified criteria'
        
        self.feature_set.program_states['apply_orientation_parameters_and_reconstruct_imposing_helical_symmetry']= \
        'Reconstruct 3D volume from images using orientation parameters and helical symmetry'
        
        self.feature_set.program_states['evaluate_alignment_parameters_and_summarize_in_plot']='Evaluate alignment ' + \
        'parameters and summarize in diagnostic plot'


    def set_inp_refinement_stack(self, feature_set):
        inp1 = 'Image input stack refinement'
        feature_set.parameters[inp1]='protein_stack.hdf'
        feature_set.properties[inp1]=feature_set.file_properties(1,['hdf'],'getFile')
        
        feature_set.hints[inp1]='Input stack should have CTF applied and prepared: accepted image file formats ' + \
        '({0}).'.format(', '.join(feature_set.properties[inp1].ext))
        
        feature_set.level[inp1]='beginner'
        
        return feature_set
    
        
    def set_volume_prefix_refined_structure(self, feature_set):
        inp9 = 'Output volume name'
        feature_set.parameters[inp9]='recvol.hdf'
        feature_set.properties[inp9]=feature_set.file_properties(1,['hdf'],'saveFile')
        
        feature_set.hints[inp9]='Output name for volumes of iterative structure refinement (completion to ' + \
        '\'prefix_XXX.ext\'): accepted image file formats ({0}).'.format(', '.join(feature_set.properties[inp9].ext))
        
        feature_set.level[inp9]='beginner'
        
        return feature_set
    
    
    def set_iteration_count(self, feature_set):
        inp7 = 'Number of iterations'
        feature_set.parameters[inp7] = int(20)
        feature_set.hints[inp7] = 'Number of iteration cycles of projection, alignment and 3D reconstruction.'
        feature_set.properties[inp7] = feature_set.Range(1, 200, 1)
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    
    
    def set_helical_continuity_option(self, feature_set):
        inp5 = 'Force helical continuity'
        feature_set.parameters[inp5]=bool(True)
        feature_set.hints[inp5]='Tick to enforce helical continuity of segments. This way segments are removed  ' +\
        'when polarity flips within helix. Running averages of in-plane rotation, shifts perpendicular ' +\
        'to helix axis and out-of-plane angles are computed and monitored. Forward differences and polarity ' + \
        'distribution are given in statistical evaluation.'
        feature_set.level[inp5]='intermediate'
        
        return feature_set
    
    
    def set_reference_volume_option(self, feature_set):
        inp5 = 'Reference structure option'
        feature_set.parameters[inp5]=bool(False)
        feature_set.hints[inp5]='Tick if reference available - otherwise uses cylinder with diameter specifications ' +\
        'below.'
        feature_set.level[inp5]='intermediate'
        
        return feature_set
    

    def set_relatives_and_level(self, feature_set, inp9):
        feature_set.relatives[inp9] = 'Reference structure option'
        feature_set.level[inp9] = 'intermediate'

        return feature_set
    
    
    def set_reference_volume(self, feature_set):
        inp9 = 'Reference volume'
        feature_set.parameters[inp9]='reference_vol.hdf'
        feature_set.properties[inp9]=feature_set.file_properties(1,['hdf'],'getFile')
        feature_set.hints[inp9]='Reference to be used for 3D structure refinement: accepted image file formats ' + \
        '({0}).'.format(', '.join(feature_set.properties[inp9].ext))
        feature_set = self.set_relatives_and_level(feature_set, inp9)
        
        return feature_set
    
    
    def set_image_size_to_be_aligned(self, feature_set):
        inp5 = 'Image alignment size in Angstrom'
        feature_set.parameters[inp5] = int(700)
        feature_set.hints[inp5] = 'Image dimension to be used for alignment in Angstrom, i.e. the larger, the more ' + \
        'signal is available for alignment but less compensation of structural flexibility is possible.'
        feature_set.properties[inp5] = feature_set.Range(10, 5000, 1)
        feature_set.level[inp5]='beginner'
        
        return feature_set

        
    def set_3dctf_correction_option(self, feature_set):
        inp5 = '3D CTF correction'
        feature_set.parameters[inp5]=bool(True)
        feature_set.hints[inp5]='Tick to perform 3D CTF correction by dividing through the average of all CTFs ' + \
        'squared. Only applied in case segments were convolved by CTF. Therefore, if segments were phase-flipped ' + \
        'no 3D CTF correction will be performed.'
        feature_set.level[inp5]='expert'
        
        return feature_set
    
        
    def set_3dctf_correction_intensity_option(self, feature_set):
        inp5 = '3D CTF correction intensity'
        feature_set.parameters[inp5]=str('low')
        feature_set.hints[inp5]='Wiener filter constant as percent of Fourier amplitude. None - No 3D CTF ' + \
        'correction. High - 40, 20, 10, 5. Medium - 20, 10, 5, 2. Low - 10, 5, 2, 1. (percent for low-, medium-, ' + \
        'high- and maximum resolution refinement).'
        feature_set.properties[inp5] = feature_set.choice_properties(2, ['low', 'medium', 'high'], 'QComboBox')
        feature_set.level[inp5]='expert'
        feature_set.relatives[inp5]='3D CTF correction'
        
        return feature_set
    
    
    def set_enforce_even_phi_distribution(self, feature_set):
        inp5 = 'Enforce even phi option'
        feature_set.parameters[inp5]=bool(False)
        feature_set.hints[inp5]='Tick if you want to enforce an even azimuthal angular distribution by analyzing and '+\
        'restraining the phi angle distribution. First, it randomizes phi angles. Second, it removes excessive phi ' +\
        'angles to achieve an even distribution. At last, it releases the restraint after specified cycle below. ' +\
        'This option has a stabilizing effect on the reconstruction in particular when \'Symmetrize helix\' is not used.'
        feature_set.level[inp5]='experimental'
        
        return feature_set
    
    
    def set_release_cycle_even_phi(self, feature_set):
        inp7 = 'Release cycle even phi'
        feature_set.parameters[inp7] = int(8)
        feature_set.hints[inp7] = 'Iteration cycle number when even phi angle enforcement should be released.'
        feature_set.properties[inp7] = feature_set.Range(4, 200, 1)
        feature_set.relatives[inp7]='Enforce even phi option'
        feature_set.level[inp7]='experimental'
        
        return feature_set
    
    
    def set_enforce_pitch_even_phi(self, feature_set):
        inp7 = 'Pitch enforce even phi'
        feature_set.parameters[inp7] = float(8)
        feature_set.hints[inp7] = 'Pitch in Angstrom for even phi enforcement. Pitch of 0 will result in rotational '+\
        'blur.'
        feature_set.properties[inp7] = feature_set.Range(0, 20000, 10)
        feature_set.relatives[inp7]='Enforce even phi option'
        feature_set.level[inp7]='experimental'
        
        return feature_set
    
    
    def set_bin_cutff_enforce_pitch_even_phi(self, feature_set):
        inp7 = 'Bin cutoff of phi angles'
        feature_set.parameters[inp7] = int(100)
        feature_set.hints[inp7] = 'Number of segments per phi bin that are cut off to enforce an even phi distribution.'
        feature_set.properties[inp7] = feature_set.Range(0, 1000000, 10)
        feature_set.relatives[inp7]='Enforce even phi option'
        feature_set.level[inp7]='experimental'
        
        return feature_set
    
    
    def set_fsc_based_filter_option(self, feature_set):
        inp14 = 'Automatic FSC filter'
        feature_set.parameters[inp14] = bool(True)
        
        feature_set.hints[inp14] = 'Automatic filter design derived from square root of Fourier Shell Correlation ' + \
        '(FSC) between reconstructions from half data sets.'
        
        feature_set.level[inp14]='expert'
        
        return feature_set
    
        
class SegmentRefine3dPar(SegmentRefine3dParPreparation):
    def set_resolution_aim_choice(self, feature_set):
        inp7 = 'Resolution aim'
        feature_set.parameters[inp7] = str('medium')
        feature_set.hints[inp7] = 'Choose whether \'low\'(>30 Angstrom) or \'medium\' (10 < x < 20 Angstrom) or ' + \
        '\'high\' (<10 Angstrom) resolution of refinement is expected. Consequences for CTF correction and ' + \
        'symmetrization.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['low', 'medium', 'high'], 'QComboBox')

        return feature_set
    
    
    def set_refinement_strategy(self, feature_set):
        inp7 = 'Assemble refinement strategy'
        feature_set.parameters[inp7] = bool(True)
        feature_set.hints[inp7] = 'Assemble refinement strategy according to resolution aims. If not ticked ' +\
        'it will perform refinement from low to maximum resolution. For a lower resolution aim, data will be binned ' +\
        'and refinement consequently converges and refines quicker. Subsequently, such refinements can be used as a ' +\
        'starting point for later higher-resolution reconstructions.'
        feature_set.level[inp7]='intermediate'

        return feature_set


    def add_custom_refinement_strategy_as_relative(self, feature_set, current_parameter):
        feature_set.relatives[current_parameter] = 'Assemble refinement strategy'

    def set_low_resolution_aim(self, feature_set):
        inp7 = 'LR - Low resolution aim'
        feature_set.parameters[inp7] = bool(True)
        feature_set.hints[inp7] = 'Select if your resolution aim is \'low\'(>20 Angstrom). Data will be binned ' + \
        'internally to speed up refinement. Volumes are symmetrized in 3D.'
        self.add_custom_refinement_strategy_as_relative(feature_set, inp7)
        feature_set.level[inp7]='intermediate'

        return feature_set
    
    
    def get_restraint_phrase(self):
        return 'projection matching search of azimuthal and out-of-plane angles within specified limits of ' + \
            'previous angle. 0 degrees = fixed, i.e. only previous projection will be searched. 360 degrees = no ' + \
            'restraints, i.e. all projections are searched.'
    
    
    def get_translation_range_phrase(self):
        return 'translational range of alignment search perpendicular and along helix axis (X: off-center helical ' + \
            'axis, Y: (minimum y-range=helical rise/2).'


    def get_translational_range_title(self):
        return '- X and Y translation range in Angstrom'


    def set_low_resolution_trans_range(self, feature_set):
        inp8 = 'LR ' + self.get_translational_range_title()
        feature_set.parameters[inp8]=tuple((50, 23))
        feature_set.hints[inp8]='Low resolution ' + self.get_translation_range_phrase()
        feature_set.properties[inp8]=feature_set.Range(0, 1000, 1)
        feature_set.relatives[inp8] = (('LR - Low resolution aim', 'LR - Low resolution aim'))
        feature_set.level[inp8]='expert'
        
        return feature_set
    

    def get_angular_restraint_title(self):
        return '- azimuthal and out-of-plane search restraint in degrees'
    

    def set_low_resolution_angular_restraint(self, feature_set):
        inp7 = 'LR ' + self.get_angular_restraint_title()
        feature_set.parameters[inp7] = tuple((180.0, 180.0))
        feature_set.hints[inp7] = 'Restrain low-resolution ' + self.get_restraint_phrase() 
        feature_set.properties[inp7] = feature_set.Range(0, 180, 0.1)
        feature_set.relatives[inp7] = (('LR - Low resolution aim', 'LR - Low resolution aim'))
        feature_set.level[inp7]='expert'

        return feature_set
    
    
    def set_medium_resolution_aim(self, feature_set):
        inp7 = 'MR - Medium resolution aim'
        feature_set.parameters[inp7] = bool(True)
        feature_set.hints[inp7] = 'Select if your resolution aim is \'medium\'(10 - 20 Angstrom). Data will be ' + \
        'binned to maximum spatial resolution of 10 Angstrom. Volumes are symmetrized in 3D.'
        self.add_custom_refinement_strategy_as_relative(feature_set, inp7)
        feature_set.level[inp7]='intermediate'

        return feature_set

    
    def set_medium_resolution_angular_restraint(self, feature_set):
        inp7 = 'MR ' + self.get_angular_restraint_title()
        feature_set.parameters[inp7] = tuple((180.0, 180.0))
        feature_set.hints[inp7] = 'Restrain medium-resolution ' + self.get_restraint_phrase()
        feature_set.properties[inp7] = feature_set.Range(0, 180, 0.1)
        feature_set.relatives[inp7] = (('MR - Medium resolution aim', 'MR - Medium resolution aim'))
        feature_set.level[inp7]='expert'

        return feature_set
    
    
    def set_medium_resolution_trans_range(self, feature_set):
        inp8 = 'MR ' + self.get_translational_range_title()
        feature_set.parameters[inp8]=tuple((21, 10))
        feature_set.hints[inp8]='Medium resolution ' + self.get_translation_range_phrase()
        feature_set.properties[inp8]=feature_set.Range(0, 1000, 1)
        feature_set.relatives[inp8] = (('MR - Medium resolution aim', 'MR - Medium resolution aim'))
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_high_resolution_aim(self, feature_set):
        inp7 = 'HR - High resolution aim'
        feature_set.parameters[inp7] = bool(True)
        feature_set.hints[inp7] = 'Select if your resolution aim is \'high\'(5 - 10 Angstrom). Data will be binned ' + \
        'internally to maximum spatial resolution of 5 Angstrom.'
        self.add_custom_refinement_strategy_as_relative(feature_set, inp7)
        feature_set.level[inp7]='intermediate'

        return feature_set

    
    def set_high_resolution_angular_restraint(self, feature_set):
        inp7 = 'HR ' + self.get_angular_restraint_title()
        feature_set.parameters[inp7] = tuple((20.0, 20.0))
        feature_set.hints[inp7] = 'Restrain high-resolution ' + self.get_restraint_phrase()
        feature_set.properties[inp7] = feature_set.Range(0, 180, 0.1)
        feature_set.relatives[inp7] = (('HR - High resolution aim', 'HR - High resolution aim'))
        feature_set.level[inp7]='expert'

        return feature_set
    
    
    def set_high_resolution_trans_range(self, feature_set):
        inp8 = 'HR ' + self.get_translational_range_title()
        feature_set.parameters[inp8]=tuple((14, 7))
        feature_set.hints[inp8]='High resolution ' + self.get_translation_range_phrase()
        feature_set.properties[inp8]=feature_set.Range(0, 1000, 1)
        feature_set.relatives[inp8] = (('HR - High resolution aim', 'HR - High resolution aim'))
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_maximum_resolution_aim(self, feature_set):
        inp7 = 'MaxR - Maximum resolution aim'
        feature_set.parameters[inp7] = bool(True)
        feature_set.hints[inp7] = 'Select if your resolution aim is your maximum spatial frequency. Data will not ' + \
        'be binned and is limited by pixelsize. As a result, this refinement is very slow.'
        self.add_custom_refinement_strategy_as_relative(feature_set, inp7)
        feature_set.level[inp7]='intermediate'

        return feature_set


    def set_maximum_resolution_angular_restraint(self, feature_set):
        inp7 = 'MaxR ' + self.get_angular_restraint_title()
        feature_set.parameters[inp7] = tuple((2.0, 2.0))
        feature_set.hints[inp7] = 'Restrain maximum-resolution ' + self.get_restraint_phrase()
        feature_set.properties[inp7] = feature_set.Range(0, 180, 0.1)
        feature_set.relatives[inp7] = (('MaxR - Maximum resolution aim', 'MaxR - Maximum resolution aim'))
        feature_set.level[inp7]='expert'

        return feature_set
    
    
    def set_max_resolution_trans_range(self, feature_set):
        inp8 = 'MaxR ' + self.get_translational_range_title()
        feature_set.parameters[inp8]=tuple((7, 3.5))
        feature_set.hints[inp8]='Maximum resolution ' + self.get_translation_range_phrase()
        feature_set.properties[inp8]=feature_set.Range(0, 1000, 1)
        feature_set.relatives[inp8] = (('MaxR - Maximum resolution aim', 'MaxR - Maximum resolution aim'))
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_refinement_strategy_options(self):
        self.feature_set = self.set_refinement_strategy(self.feature_set)
        
        self.feature_set = self.set_low_resolution_aim(self.feature_set)
        self.feature_set = self.set_low_resolution_angular_restraint(self.feature_set)
        self.feature_set = self.set_low_resolution_trans_range(self.feature_set)
        
        self.feature_set = self.set_medium_resolution_aim(self.feature_set)
        self.feature_set = self.set_medium_resolution_angular_restraint(self.feature_set)
        self.feature_set = self.set_medium_resolution_trans_range(self.feature_set)
        
        self.feature_set = self.set_high_resolution_aim(self.feature_set)
        self.feature_set = self.set_high_resolution_angular_restraint(self.feature_set)
        self.feature_set = self.set_high_resolution_trans_range(self.feature_set)
        
        self.feature_set = self.set_maximum_resolution_aim(self.feature_set)
        self.feature_set = self.set_maximum_resolution_angular_restraint(self.feature_set)
        self.feature_set = self.set_max_resolution_trans_range(self.feature_set)
        
        self.feature_set = self.segmentrefine3d_features.set_absolute_translation_limit(self.feature_set)
        
        self.feature_set = self.set_frame_motion_correction(self.feature_set)
        self.feature_set = self.set_frame_averaging_size(self.feature_set)
        self.feature_set = self.set_local_averaging_size(self.feature_set)


    def set_halfset_refinement_option(self, feature_set):
        inp7 = 'Independent half-set refinement'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Independent half-set refinement from two halves of the data set that are .' + \
        'kept separate for multiple cycles. Sometimes referred to \'gold standard refinement\'. Here, helices ' + \
        'are divided into odd and even data sets.'
        feature_set.level[inp7]='intermediate'
        
        return feature_set

        
    def set_halfset_start(self, feature_set):
        inp7 = 'Half-set refinement start'
        feature_set.parameters[inp7] = str('medium')
        feature_set.hints[inp7] = 'Choose when to start independent half-set refinement. At least, a ' + \
        'low resolution refinement is critical to compute reliable FSC curves without an additional alignment ' + \
        'step.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['medium', 'high', 'max'], 'QComboBox')
        feature_set.level[inp7]='intermediate'
        
        return feature_set
        

    def set_frame_motion_correction(self, feature_set): 
        inp7 = 'Frame motion correction'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Segment-based motion correction to correct for beam-induced movement.'
        feature_set.level[inp7]='expert'
        
        return feature_set


    def set_frame_averaging_size(self, feature_set): 
        inp8 = 'Frame average window size'
        feature_set.parameters[inp8]=int(3)
        feature_set.hints[inp8]='Size of window of number of frames used for running average frame processing. ' + \
        '1 means no additional frame averaging, 3 corresponds to +/-1 average. Only odd values will be considered. ' + \
        'Even values will be rounded to the next higher odd one, e.g. 4 to 5.'
        feature_set.properties[inp8]=feature_set.Range(0, 1000, 1)
        feature_set.relatives[inp8] = 'Frame motion correction'
        feature_set.level[inp8]='expert'
        
        return feature_set


    def set_local_averaging_size(self, feature_set): 
        inp8 = 'Frame local averaging distance'
        feature_set.parameters[inp8]=int(700)
        feature_set.hints[inp8]='Distance in Angstrom used for local average frame processing. ' + \
        'Movement of segments between frames will be averaged over neighboring segments of this distance within ' + \
        'helix. 0 means no local averaging. '
        feature_set.properties[inp8]=feature_set.Range(0, 10000, 1)
        feature_set.relatives[inp8] = 'Frame motion correction'
        feature_set.level[inp8]='expert'
        
        return feature_set


class SegmentRefine3dReadParameters(object):
    def define_input_output_iteration(self, p):
        self.infile = p['Image input stack refinement']
        self.outfile_prefix = p['Output volume name']
        
        self.diagnostic_plot_prefix = p['Diagnostic plot prefix']
        self.spring_path = p['spring.db file']
        self.resume_refinement_option = p['Continue refinement option']
        self.refinementdb_path = p['refinement.db file']
            
        self.iteration_count = p['Number of iterations']
        self.reference_option = p['Reference structure option']
        if p.has_key('Reference volume'):
            self.reference_volume_file = p['Reference volume']
            self.references = [self.reference_volume_file]
        else:
            self.references = Features().convert_list_of_files_from_entry_string(p['Reference volumes'])

        self.keep_intermediate_files = p['Keep intermediate files']
        

    def define_helical_symmetry_parameters(self, p):
        self.ori_pixelsize = float(p['Pixel size in Angstrom'])
        self.helix_inner_width, self.helixwidth = p['Estimated helix inner and outer diameter in Angstrom']
        self.rise_rot_or_pitch_unit_choice = p['Helical rise/rotation or pitch/number of units per turn choice']
        if p.has_key('Helix polarity'):
            self.polar_helices = [p['Helix polarity']]
        else:
            self.polar_helices = Features().convert_list_of_specific_strings_from_entry_string(p['Helix polarities'])

        self.helix_symmetrization = p['Symmetrize helix']
        self.enforce_even_phi = p['Enforce even phi option']
        self.release_cycle = p['Release cycle even phi']
        self.pitch_enforce = p['Pitch enforce even phi']
        self.bin_cutoff_enforce = p['Bin cutoff of phi angles']
        
        if p.has_key('Helical symmetry in Angstrom or degrees'):
            if self.helix_symmetrization:
                helical_symmetry = p['Helical symmetry in Angstrom or degrees']
            else:
                helical_symmetry = ((0.0, 0.0))
    
            if self.rise_rot_or_pitch_unit_choice in ['rise/rotation'] or not self.helix_symmetrization:
                self.helical_symmetries = [helical_symmetry]
            elif self.rise_rot_or_pitch_unit_choice in ['pitch/unit_number'] and self.helix_symmetrization:
                self.helical_symmetries = \
                [SegClassReconstruct().convert_pitch_unit_pair_to_rise_rotation_pairs(helical_symmetry[0],
                helical_symmetry[1])]
        else:
            hel_sym_entry = p['Helical symmetries in Angstrom or degrees']
            helical_symmetries = Features().convert_list_of_data_pairs_from_entry_string(hel_sym_entry, 
            ('Helical rise/pitch in Angstrom', 'Helical rotation/unit_number'))

            self.helical_symmetries = []
            for each_sym in helical_symmetries:
                if not self.helix_symmetrization:
                    each_sym = ((0.0, 0.0))
                elif self.rise_rot_or_pitch_unit_choice in ['pitch/unit_number'] and self.helix_symmetrization:
                    each_sym = \
                    SegClassReconstruct().convert_pitch_unit_pair_to_rise_rotation_pairs(each_sym[0], each_sym[1])
                self.helical_symmetries.append(each_sym)
            
        self.unbending = p['Unbending option']


    def define_alignment_parameters(self, p):
        self.force_hel_continue = p['Force helical continuity']
        self.restrain_in_plane_rotation = p['Limit in-plane rotation']
        self.delta_in_plane_rotation = p['Delta in-plane rotation angle']
        self.out_of_plane_tilt_angle_range = p['Out-of-plane tilt angle range']
        
        self.azimuthal_angle_count, self.out_of_plane_tilt_angle_count = p['Number of projections azimuthal/' + \
                                                                           'out-of-plane angle']

        
    def define_refinement_strategy_options(self, p):
        self.refine_strategy = p['Assemble refinement strategy']
        self.low_resolution_aim = p['LR - Low resolution aim']
        self.low_resolution_ang_range = p['LR - azimuthal and out-of-plane search restraint in degrees']
        self.low_resolution_trans_range = p['LR - X and Y translation range in Angstrom']
        
        self.medium_resolution_aim = p['MR - Medium resolution aim']
        self.medium_resolution_ang_range = p['MR - azimuthal and out-of-plane search restraint in degrees']
        self.medium_resolution_trans_range = p['MR - X and Y translation range in Angstrom']
        
        self.high_resolution_aim = p['HR - High resolution aim']
        self.high_resolution_ang_range = p['HR - azimuthal and out-of-plane search restraint in degrees']
        self.high_resolution_trans_range = p['MR - X and Y translation range in Angstrom']
        
        self.max_resolution_aim = p['MaxR - Maximum resolution aim']
        self.max_resolution_ang_range = p['MaxR - azimuthal and out-of-plane search restraint in degrees']
        self.max_resolution_trans_range = p['MaxR - X and Y translation range in Angstrom']
        
        self.x_limit_A, self.y_limit_A = p['Absolute X and Y translation limit in Angstrom']
        self.halfset_refinement = p['Independent half-set refinement']
        self.halfset_start = p['Half-set refinement start']
        self.fsc_split = False
        
        self.frame_motion_corr = p['Frame motion correction']
        self.frame_avg_window_entry = p['Frame average window size']
        if self.frame_avg_window_entry % 2 == 0:
            self.frame_avg_window = self.frame_avg_window_entry / 2 * 2 + 1
        else:
            self.frame_avg_window = self.frame_avg_window_entry 
            
        self.frame_local_avg_dstnce = p['Frame local averaging distance']


    def define_selection_parameters(self, p):
        self = SegmentSelect().define_selection_parameters_from_segment_table(self, p)
        
        self.ccc_proj_selection = p['Projection correlation select option']
        self.ccc_proj_in_or_exclude = p['Include or exclude segments based on projection correlation']
        self.ccc_proj_range = p['Correlation projection range']
        
        self.out_of_plane_selection = p['Out-of-plane tilt select option']
        self.out_of_plane_in_or_exclude = p['Include or exclude out-of-plane tilted segments']
        self.out_of_plane_in_or_ex_range = p['Out-of-plane tilt range']
        
        self.helix_shift_x_selection = p['Shift normal to helix select option']
        self.helix_shift_x_in_or_exclude = p['Include or exclude segments with shift normal to helix']
        self.helix_shift_x_in_or_ex_cutoff = p['Shift normal to helix in Angstrom']
        

    def define_filter_parameters(self, p):
        self.high_pass_filter_option = p['High-pass filter option']
        self.low_pass_filter_option = p['Low-pass filter option']
        self.high_pass_filter_cutoff, self.low_pass_filter_cutoff = p['High and low-pass filter cutoffs in 1/Angstrom']
        self.custom_filter_option = p['Custom filter option']
        self.custom_filter_file = p['Custom-built filter file']
        self.fsc_filter = ['Automatic FSC filter']
        self.bfactor = p['B-Factor']
        
        if p.has_key('Filter layer-lines option'):
            self.layer_line_filter = p['Filter layer-lines option']
        else:
            self.layer_line_filter = False


    def define_reconstruction_parameters(self, p):
        if p.has_key('Rotational symmetry'):
            self.rotational_symmetry_starts = [p['Rotational symmetry']]
        else:
            self.rotational_symmetry_starts = \
            Features().convert_list_of_numbers_from_entry_string(p['Rotational symmetries'])
        
        self.alignment_size_in_A = p['Image alignment size in Angstrom']
        self.stepsize = p['Step size of segmentation in Angstrom']
        self.ctf_correction = p['3D CTF correction']
        self.ctf_correction_type = p['3D CTF correction intensity'].lower()


    def define_mpi_parameters(self, p):
        self.mpi_option = p['MPI option']
        self.cpu_count = p['Number of CPUs']
        self.temppath = p['Temporary directory']
