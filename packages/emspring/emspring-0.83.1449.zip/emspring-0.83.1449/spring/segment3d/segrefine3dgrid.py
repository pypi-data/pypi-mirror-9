# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to optimize segmentrefine3d reconstruction by varying refinement parameters systematically on a grid
"""

from collections import OrderedDict
from spring.csinfrastr.csdatabase import SpringDataBase, refine_base, RefinementCycleTable, grid_base, GridTable, \
    GridRefineTable
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import OpenMpi
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment3d.refine.sr3d_main import SegmentRefine3d
from spring.segment3d.refine.sr3d_parameters import SegmentRefine3dPar
from spring.segment3d.refine.sr3d_prepare import SegmentRefine3dPreparation
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from sqlalchemy.sql.expression import desc, asc
from tabulate import tabulate
import os
import shutil


class SegRefine3dGridPar(SegmentRefine3dPar):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'       
        self.progname = 'segrefine3dgrid'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.segmentrefine3d_features = Features()
        self.feature_set = self.segmentrefine3d_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()


    def define_parameters_and_their_properties(self):
        super(SegRefine3dGridPar, self).define_input_output_segmentrefine3d()
        self.feature_set = self.set_first_parameter_choice(self.feature_set)
        self.feature_set = self.set_second_parameter_choice(self.feature_set)
        
        self.feature_set = self.set_lower_and_upper_limit_first_parameter(self.feature_set)
        self.feature_set = self.set_lower_and_upper_limit_second_parameter(self.feature_set)
        self.feature_set = self.set_first_and_second_parameter_increment(self.feature_set)
        self.feature_set = self.set_subgrid_option(self.feature_set)
        self.feature_set = self.set_subgrid_details(self.feature_set)
        self.feature_set = self.set_continue_grid_option(self.feature_set)
        self.feature_set = self.set_grid_database(self.feature_set)
        
        super(SegRefine3dGridPar, self).define_segmentrefine3d_parameters()
        
    def define_program_states(self):
        super(SegRefine3dGridPar, self).define_program_states()

    def get_parameters_to_be_varied(self):
        parameter_to_be_varied = ['number_of_iterations', 'high_pass_filter_cutoff', 'low_pass_filter_cutoff', 
                                  'b-factor', 'include_classes', 'exclude_curvature_above', 
                                  'exclude_layer_line_ccc_below', 'exclude_defocus_below', 'exclude_defocus_above', 
                                  'exclude_astigmatism_above', 'exclude_projection_ccc_below', 
                                  'exclude_out_of_plane_tilt_below', 'exclude_out_of_plane_tilt_above', 
                                  'exclude_shift_normal_to_helix_above', 'helical_rise_or_pitch', 
                                  'helical_rotation_or_number_of_units_per_turn', 'helix_start', 
                                  'delta_in_plane_rotation', 'out_of_plane_tilt_search_range', 
                                  'out_of_plane_count', 'azimuthal_count', 'alignment_image_size', 'segmentation_step',
                                  'pixelsize']
        return parameter_to_be_varied


    def set_first_parameter_choice(self, feature_set):
        inp7 = 'First parameter'
        feature_set.parameters[inp7] = str('helical_rise_or_pitch')
        parameters_to_be_varied = self.get_parameters_to_be_varied()
        parameters = ''.join(['\'{0}\'\n'.format(each_parameter) for each_parameter in parameters_to_be_varied])
        feature_set.hints[inp7] = 'Choose parameter to be varied in first dimension: \n{0}'.format(parameters)
        feature_set.properties[inp7] = feature_set.choice_properties(2, parameters_to_be_varied, 'QComboBox')
        feature_set.level[inp7]='beginner'

        return feature_set
    
    
    def set_second_parameter_choice(self, feature_set):
        inp7 = 'Second parameter'
        feature_set.parameters[inp7] = str('helical_rotation_or_number_of_units_per_turn')
        parameters_to_be_varied = self.get_parameters_to_be_varied()
        parameters_to_be_varied.insert(0, 'none')
        parameters = ''.join(['\'{0}\'\n'.format(each_parameter) for each_parameter in parameters_to_be_varied])
        feature_set.hints[inp7] = 'Choose parameter to be varied in second dimension: \n{0}'.format(parameters)
        feature_set.properties[inp7] = feature_set.choice_properties(2, parameters_to_be_varied, 'QComboBox')
        feature_set.level[inp7]='beginner'

        return feature_set
    


    def get_unit_dependence_hint(self):
        return 'Unit dependent on quantity.'

    def set_lower_and_upper_limit_first_parameter(self, feature_set):
        inp8 = 'Lower and upper limit first parameter'
        feature_set.parameters[inp8] = tuple((1.4, 1.9))
        
        feature_set.hints[inp8] = 'Lower and upper limit of first parameter for grid search. ' + \
        self.get_unit_dependence_hint()
        
        feature_set.properties[inp8] = feature_set.Range(-10000000, 10000000, 0.001)
        feature_set.level[inp8]='beginner'
        
        return feature_set

    
    def set_lower_and_upper_limit_second_parameter(self, feature_set):
        inp8 = 'Lower and upper limit second parameter'
        feature_set.parameters[inp8] = tuple((22.0, 24.0))
        
        feature_set.hints[inp8] = 'Lower and upper limit of second parameter for grid search. ' + \
        self.get_unit_dependence_hint()
        
        feature_set.properties[inp8] = feature_set.Range(-10000000, 10000000, 0.001)
        feature_set.level[inp8]='beginner'
        
        return feature_set
    
    
    def set_first_and_second_parameter_increment(self, feature_set):
        inp8 = 'First and second parameter increment'
        feature_set.parameters[inp8] = tuple((0.1, 0.3))
        
        feature_set.hints[inp8] = 'First and second parameter increment for grid search. ' + \
        self.get_unit_dependence_hint()
        
        feature_set.properties[inp8] = feature_set.Range(-1e8, 1e+8, 0.001)
        feature_set.level[inp8]='beginner'
        
        return feature_set
    
    
    def set_subgrid_option(self, feature_set):
        inp8 = 'Subgrid option'
        feature_set.parameters[inp8] = False
        feature_set.hints[inp8] = 'Run subgrids to parallelize expensive grid searches.'
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_subgrid_details(self, feature_set):
        inp8 = 'Part and number of subgrids'
        feature_set.parameters[inp8] = tuple((1, 3))
        feature_set.hints[inp8] = 'E.g. one out of total of three subgrids will be run. This features is thought for '+\
        'parallelization of expensive grid searches.'
        feature_set.properties[inp8] = feature_set.Range(1, 100, 1)
        feature_set.relatives[inp8]=('Subgrid option', 'Subgrid option')
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_continue_grid_option(self, feature_set):
        inp8 = 'Grid continue option'
        feature_set.parameters[inp8] = False
        feature_set.hints[inp8] = 'Continue grid refinement in case of interrupted grid searches.'
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_grid_database(self, feature_set):
        inp8 = 'Grid database'
        feature_set.parameters[inp8] = 'grid.db'
        feature_set.properties[inp8]=feature_set.file_properties(1,['db'],'getFile')
        feature_set.hints[inp8] = 'Continue grid refinement in case of interrupted grid searches.'
        feature_set.relatives[inp8]='Grid continue option'
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
class SegRefine3dGridSetup(SegmentRefine3dPreparation):
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters
            self.define_all_segmentrefine3d_parameters(p)
            
            self.primary_variable = p['First parameter']
            self.secondary_variable = p['Second parameter']
            self.primary_range = p['Lower and upper limit first parameter']
            self.primary_inc, self.second_inc = p['First and second parameter increment']
            self.secondary_range = p['Lower and upper limit second parameter']
            self.subgrid_option = p['Subgrid option']
            self.subgrid = p['Part and number of subgrids']
            self.continue_grid = p['Grid continue option']
            self.grid_database = p['Grid database']
            
        
    def generate_segmentrefine3d_parameters_while_removing_grid_parameters(self, parameters):
        
        segmentrefine3d_params = OrderedDict()
        for each_param in parameters:
            if each_param not in ['First parameter', 'Second parameter', 'Lower and upper limit first parameter',
                                  'Lower and upper limit second parameter', 'First and second parameter increment',
                                  'Subgrid option', 'Part and number of subgrids', 'Grid continue option', 
                                  'Grid database']:
                segmentrefine3d_params[each_param] = parameters[each_param]
            
        return segmentrefine3d_params
    

    def setup_non_refinement_selection_criteria(self, each_grid_point, parameters, index, one_of_both_parameters):
        if one_of_both_parameters == 'include_classes':
            parameters['Classes select option'] = True
            parameters['Include or exclude classes'] = 'include'
            parameters['Classes list'] = each_grid_point[index]
        elif one_of_both_parameters == 'exclude_curvature_above':
            parameters['Straightness select option'] = True
            parameters['Include or exclude straight helices'] = 'include'
            parameters['Persistence length range'] = (0, each_grid_point[index])
        elif one_of_both_parameters == 'exclude_layer_line_ccc_below':
            parameters['Layer line correlation select option'] = True
            parameters['Include or exclude segments based on layer-line correlation'] = 'exclude'
            parameters['Correlation layer line range'] = (0, each_grid_point[index])
        elif one_of_both_parameters == 'exclude_defocus_below':
            parameters['Defocus select option'] = True
            parameters['Include or exclude defocus range'] = 'exclude'
            parameters['Defocus range'] = (0, each_grid_point[index])
        elif one_of_both_parameters == 'exclude_defocus_above':
            parameters['Defocus select option'] = True
            parameters['Include or exclude defocus range'] = 'include'
            parameters['Defocus range'] = (0, each_grid_point[index])
        elif one_of_both_parameters == 'exclude_astigmatism_above':
            parameters['Astigmatism select option'] = True
            parameters['Include or exclude astigmatic segments'] = 'include'
            parameters['Astigmatism range'] = (0, each_grid_point[index])
            
        return parameters
    

    def setup_refinement_selection_criteria(self, each_grid_point, parameters, index, one_of_both_parameters):
        if one_of_both_parameters == 'exclude_projection_ccc_below':
            parameters['Projection correlation select option'] = True
            parameters['Include or exclude segments based on projection correlation'] = 'exclude'
            parameters['Correlation projection range'] = (0, each_grid_point[index])
        elif one_of_both_parameters == 'exclude_out_of_plane_tilt_below':
            parameters['Out-of-plane tilt select option'] = True
            parameters['Include or exclude out-of-plane tilted segments'] = 'exclude'
            parameters['Out-of-plane tilt range'] = (-each_grid_point[index], each_grid_point[index])
        elif one_of_both_parameters == 'exclude_out_of_plane_tilt_above':
            parameters['Out-of-plane tilt select option'] = True
            parameters['Include or exclude out-of-plane tilted segments'] = 'include'
            parameters['Out-of-plane tilt range'] = (-each_grid_point[index], each_grid_point[index])
        elif one_of_both_parameters == 'exclude_shift_normal_to_helix_above':
            parameters['Shift normal to helix select option'] = True
            parameters['Include or exclude segments with shift normal to helix'] = 'include'
            parameters['Shift normal to helix in Angstrom'] = each_grid_point[index]
        
        return parameters
    

    def setup_symmetry_related_parameters(self, each_grid_point, parameters, index, one_of_both_parameters):
        if one_of_both_parameters == 'helical_rise_or_pitch':
            parameters['Helical symmetry in Angstrom or degrees'] = (each_grid_point[index], 
            parameters['Helical symmetry in Angstrom or degrees'][1])
        elif one_of_both_parameters == 'helical_rotation_or_number_of_units_per_turn':
            pitch =  parameters['Helical symmetry in Angstrom or degrees'][0]
            parameters['Helical symmetry in Angstrom or degrees'] = (pitch, each_grid_point[index])
        elif one_of_both_parameters == 'segmentation_step':
            parameters['Step size of segmentation in Angstrom'] = each_grid_point[index]
        elif one_of_both_parameters == 'alignment_image_size':
            parameters['Image alignment size in Angstrom'] = each_grid_point[index]
        elif one_of_both_parameters == 'pixelsize':
            parameters['Pixel size in Angstrom'] = each_grid_point[index]
        
        return parameters
    

    def setup_alignment_related_parameters(self, each_grid_point, parameters, index, one_of_both_parameters):
        if one_of_both_parameters == 'delta_in_plane_rotation':
            parameters['Delta in-plane rotation angle'] = each_grid_point[index]
        elif one_of_both_parameters == 'out_of_plane_tilt_search_range':
            parameters['Out-of-plane tilt angle range'] = (-each_grid_point[index], each_grid_point[index])
        elif one_of_both_parameters == 'out_of_plane_count':
            parameters['Number of projections azimuthal/out-of-plane angle'] = \
            (parameters['Number of projections azimuthal/out-of-plane angle'][0], each_grid_point[index])
        elif one_of_both_parameters == 'azimuthal_count':
            parameters['Number of projections azimuthal/out-of-plane angle'] = \
            (each_grid_point[index], parameters['Number of projections azimuthal/out-of-plane angle'][1])
            
        return parameters
    

    def setup_filter_related_parameters(self, each_grid_point, parameters, index, one_of_both_parameters):
        if one_of_both_parameters == 'number_of_iterations':
            parameters['Number of iteration'] = each_grid_point[index]
        elif one_of_both_parameters == 'high_pass_filter_cutoff':
            parameters['High and low-pass filter cutoffs in 1/Angstrom'] = \
            (each_grid_point[index], parameters['High and low-pass filter cutoffs in 1/Angstrom'][1])
        elif one_of_both_parameters == 'low_pass_filter_cutoff':
            parameters['High and low-pass filter cutoffs in 1/Angstrom'] = \
            (parameters['High and low-pass filter cutoffs in 1/Angstrom'][0], each_grid_point[index])
        elif one_of_both_parameters == 'b-factor':
            parameters['B-Factor'] = each_grid_point[index]
            
        return parameters
    

    def add_grid_point_to_parameter_dictionary(self, first_param, second_param, each_grid_point, parameters):
        """
        >>> from spring.segment3d.segrefine3dgrid import SegRefine3dGrid
        >>> s = SegRefine3dGrid()
        >>> r_p = 'helical_rise_or_pitch'
        >>> params = SegRefine3dGridPar().parameters
        >>> s.add_grid_point_to_parameter_dictionary('b-factor', r_p, [-111, 1.111], params) #doctest: +NORMALIZE_WHITESPACE
        OrderedDict([('Image input stack refinement', 'protein_stack.hdf'), 
        ('Output volume name', 'recvol.hdf'), 
        ('First parameter', 'helical_rise_or_pitch'), ('Second parameter', 
        'helical_rotation_or_number_of_units_per_turn'), 
        ('Lower and upper limit first parameter', (1.4, 1.9)), 
        ('Lower and upper limit second parameter', (22.0, 24.0)), 
        ('First and second parameter increment', (0.1, 0.3)), 
        ('Subgrid option', False), ('Part and number of subgrids', (1, 3)), 
        ('Grid continue option', False), ('Grid database', 'grid.db'), 
        ('Diagnostic plot prefix', 'diagnostic_plot.pdf'), 
        ('Number of iterations', 20), ('Reference structure option', False), 
        ('Reference volume', 'reference_vol.hdf'), ('spring.db file', 
        'spring.db'), ('Continue refinement option', False), 
        ('refinement.db file', 'refinement.db'), ('Assemble refinement strategy', 
        True), ('LR - Low resolution aim', True), 
        ('LR - azimuthal and out-of-plane search restraint in degrees', 
        (180.0, 180.0)), ('LR - X and Y translation range in Angstrom', 
        (50, 23)), ('MR - Medium resolution aim', True), 
        ('MR - azimuthal and out-of-plane search restraint in degrees', 
        (180.0, 180.0)), ('MR - X and Y translation range in Angstrom', 
        (21, 10)), ('HR - High resolution aim', True), 
        ('HR - azimuthal and out-of-plane search restraint in degrees', 
        (20.0, 20.0)), ('HR - X and Y translation range in Angstrom', 
        (14, 7)), ('MaxR - Maximum resolution aim', True), 
        ('MaxR - azimuthal and out-of-plane search restraint in degrees', 
        (2.0, 2.0)), ('MaxR - X and Y translation range in Angstrom', 
        (7, 3.5)), ('Absolute X and Y translation limit in Angstrom', 
        (100, 100)), ('Frame motion correction', False), 
        ('Frame average window size', 3),  ('Frame local averaging distance', 700), 
        ('Independent half-set refinement', False), 
        ('Half-set refinement start', 'medium'), ('High-pass filter option', False), 
        ('Low-pass filter option', True), 
        ('High and low-pass filter cutoffs in 1/Angstrom', 
        (0.001, 0.09)), ('B-Factor', -111), ('Custom filter option', 
        False), ('Custom-built filter file', 'filter_function.dat'), 
        ('Automatic FSC filter', True), ('Filter layer-lines option', False), 
        ('Micrographs select option', False), ('Include or exclude micrographs', 
        'include'), ('Micrographs list', '1-9, 11, 13'), ('Helices select option', 
        False), ('Include or exclude helices', 'include'), ('Helices list', 
        '1-9, 11, 13'), ('Segments select option', False), 
        ('Include or exclude segments', 'include'), ('Segment file', 
        'stackid_file.dat'), ('Classes select option', False), 
        ('Include or exclude classes', 'include'), ('Class type', 'class_id'), 
        ('Classes list', '1-9, 11, 13'),  ('Persistence class option', False), 
        ('Persistence class length in Angstrom', 700), 
        ('Class occupancy threshold', 0.5), ('Straightness select option', False), 
        ('Include or exclude straight helices', 'include'), ('Persistence length range', 
        (80, 100)), ('Layer line correlation select option', False), 
        ('Include or exclude segments based on layer-line correlation', 
        'include'), ('Correlation layer line range', (60, 100)), 
        ('Defocus select option', False), ('Include or exclude defocus range', 
        'include'), ('Defocus range', (10000, 40000)), 
        ('Astigmatism select option', False), 
        ('Include or exclude astigmatic segments', 'include'), 
        ('Astigmatism range', (0, 4000)), 
        ('Projection correlation select option', False), 
        ('Include or exclude segments based on projection correlation', 
        'include'), ('Correlation projection range', (60, 100)), 
        ('Out-of-plane tilt select option', False), 
        ('Include or exclude out-of-plane tilted segments', 'include'), 
        ('Out-of-plane tilt range', (-5, 5)), 
        ('Shift normal to helix select option', False), 
        ('Include or exclude segments with shift normal to helix', 'include'), 
        ('Shift normal to helix in Angstrom', 5.0), ('Keep intermediate files', 
        False), ('Estimated helix inner and outer diameter in Angstrom', (0, 190)), 
        ('Pixel size in Angstrom', 1.163), ('Symmetrize helix', True), 
        ('Helical rise/rotation or pitch/number of units per turn choice', 
        'rise/rotation'), ('Enforce even phi option', False), 
        ('Release cycle even phi', 8), ('Pitch enforce even phi', 8.0), 
        ('Bin cutoff of phi angles', 100), 
        ('Helical symmetry in Angstrom or degrees', (1.111, 22.03)), 
        ('Rotational symmetry', 1), ('Helix polarity', 'polar'), 
        ('Unbending option', False), ('Force helical continuity', True), 
        ('Limit in-plane rotation', True), ('Delta in-plane rotation angle', 
        10.0), ('Out-of-plane tilt angle range', (-12, 12)), 
        ('Number of projections azimuthal/out-of-plane angle', 
        (90, 7)), ('Image alignment size in Angstrom', 700), 
        ('Step size of segmentation in Angstrom', 70), ('3D CTF correction', 
        True), ('3D CTF correction intensity', 'low'), ('MPI option', True), 
        ('Number of CPUs', 8), ('Temporary directory', '/tmp')])
        """
        for index, one_of_both_parameters in enumerate([first_param, second_param]):
            if one_of_both_parameters is not None:
                parameters = self.setup_filter_related_parameters(each_grid_point, parameters, index,
                one_of_both_parameters)
                
                parameters = self.setup_non_refinement_selection_criteria(each_grid_point, parameters, index,
                one_of_both_parameters)
                
                parameters = self.setup_refinement_selection_criteria(each_grid_point, parameters, index,
                one_of_both_parameters)
                
                parameters = self.setup_symmetry_related_parameters(each_grid_point, parameters, index,
                one_of_both_parameters)
                
                parameters = self.setup_alignment_related_parameters(each_grid_point, parameters, index,
                one_of_both_parameters)
        
        return parameters


    def generate_file_name_for_grid_search(self, first_param, second_param, each_grid_point):
        """
        >>> from spring.segment3d.segrefine3dgrid import SegRefine3dGrid
        >>> s = SegRefine3dGrid()
        >>> s.generate_file_name_for_grid_search('b-factor', None, [-200, 3])
        'b-factor_-200'
        >>> sec_par = 'helical_rise_or_pitch'
        >>> s.generate_file_name_for_grid_search('b-factor', sec_par, [-200, 3.344])
        'b-factor_-200_helical_rise_or_pitch_3344'
        """
        if each_grid_point[0] == int(each_grid_point[0]):
            first_grid_point_string = str(int(each_grid_point[0]))
        else:
            first_grid_point_string = ''.join(str(each_grid_point[0]).split('.'))
            
        if each_grid_point[1] == int(each_grid_point[1]):
            second_grid_point_string = str(int(each_grid_point[1]))
        else:
            second_grid_point_string = ''.join(str(each_grid_point[1]).split('.'))
            
        if first_param == second_param or second_param is None:
            run_name = '{0}_{1}'.format(first_param, first_grid_point_string)
        else:
            run_name = '{0}_{1}_{2}_{3}'.format(first_param, first_grid_point_string, second_param,
            second_grid_point_string)
            
        return run_name
    

    def setup_parameters_for_each_grid_point(self, first_param, second_param, each_grid_point, parameters):
        parameters = self.add_grid_point_to_parameter_dictionary(first_param, second_param, each_grid_point, parameters)
        run_name = self.generate_file_name_for_grid_search(first_param, second_param, each_grid_point)
                
        parameter_file = Features().write_parfile(parameters, run_name, tag=False)
        
        return parameter_file, run_name
    
    
class SegRefine3dGrid(SegRefine3dGridSetup):
    
    def split_grid_if_demanded(self, subgrid_option, subgrid, grid_sequence):
        """
        >>> from spring.segment3d.segrefine3dgrid import SegRefine3dGrid
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> s = SegClassReconstruct()
        >>> grid = s.generate_rise_rotation_or_pitch_unitnumber_pairs_for_symmetry_grid((275.0, 305.0), 5.0, (3.8, 4.2), 0.1)
        >>> SegRefine3dGrid().split_grid_if_demanded(True, (1, 6), grid.ravel())
        array([(275.0, 3.8), (275.0, 3.9), (275.0, 4.0), (275.0, 4.1),
               (275.0, 4.2), (280.0, 3.8)], dtype=object)
        >>> SegRefine3dGrid().split_grid_if_demanded(True, (7, 6), grid.ravel())
        Traceback (most recent call last):
          File '/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/doctest.py', line 1254, in __run
            compileflags, 1) in test.globs
          File '<doctest segrefine3dgrid.SegRefine3dGrid.split_grid_if_demanded[5]>', line 1, in <module>
            SegRefine3dGrid().split_grid_if_demanded(True, (7, 6), grid.ravel())
          File 'spring/segment3d/segrefine3dgrid.py', line 430, in split_grid_if_demanded
            raise ValueError(msg)
        ValueError: Part of subgrids must not be larger than entire number of subgrids. Enter part of subgrids < number of subgrids.
        """
        if subgrid_option:
            subgrid_id, subgrid_count = subgrid
            if subgrid_id > subgrid_count:
                msg = 'Part of subgrids must not be larger than entire number of subgrids. Enter part of subgrids < ' +\
                'number of subgrids.'
                raise ValueError(msg)
            grid_sequence = OpenMpi().split_sequence_evenly(grid_sequence, subgrid_count)
            grid_sequence = grid_sequence[subgrid_id - 1]
            
        return grid_sequence
    

    def get_grid_parameters_and_final_grid_entry(self, grid_database, grid_name):
        shutil.copy(grid_database, grid_name)
        
        ref_session = SpringDataBase().setup_sqlite_db(grid_base, grid_name)
        ref_grid = ref_session.query(GridTable).first()
        
        last_ref_cycle = ref_session.query(GridRefineTable).order_by(asc(GridRefineTable.id)).all()
        if last_ref_cycle == []:
            last_ref_cycle_id = 0
        else:
            last_ref_cycle_id = last_ref_cycle[-1].id
            columns = SpringDataBase().get_columns_from_table(GridRefineTable)
            log_str = 'The following grid data was read from the previous grid:'
            for each_cycle in last_ref_cycle:
                col_data = [str(getattr(each_cycle, column)) for column in columns]
                msg = tabulate(zip(columns, col_data))
                log_str += '\ngrid_cycle{0}:\n{1}'.format(each_cycle.id, msg)
            
            self.log.ilog(log_str)
        
        return last_ref_cycle_id, ref_grid
    
    
    def get_grid_database_name(self, subgrid_option):
        if subgrid_option:
            subgrid_id, subgrid_count = self.subgrid
            grid_name = 'grid_{0:02}_{1:02}.db'.format(subgrid_id, subgrid_count)
        else:
            grid_name = 'grid.db'

        return grid_name


    def get_variables_ranges_and_increments(self, grid_name):
        if self.continue_grid:
            last_ref_cycle_id, ref_grid = self.get_grid_parameters_and_final_grid_entry(self.grid_database, grid_name)
            if ref_grid.primary_variable in ['Helical rise in Angstrom', 'Helical pitch in Angstrom']:
                self.rise_rot_or_pitch_unit_choice, primary_variable, secondary_variable = \
                SegClassReconstruct().get_correct_primary_and_secondary_variables_from_database(ref_grid.primary_variable, 
                ref_grid.secondary_variable)
            else:
                primary_variable = ref_grid.primary_variable
                secondary_variable = ref_grid.secondary_variable
            primary_range = ref_grid.primary_min, ref_grid.primary_max
            primary_inc = ref_grid.primary_inc
            secondary_range = ref_grid.second_min, ref_grid.second_max
            second_inc = ref_grid.second_inc
        else:
            last_ref_cycle_id = 0
            if self.secondary_variable == 'helical_rise_or_pitch':
                primary_variable = self.secondary_variable
                primary_range = self.secondary_range
                primary_inc = self.second_inc
                secondary_variable = self.primary_variable
                secondary_range = self.primary_range
                second_inc = self.primary_inc
            else:
                primary_variable = self.primary_variable
                primary_range = self.primary_range
                primary_inc = self.primary_inc
                secondary_variable = self.secondary_variable
                secondary_range = self.secondary_range
                second_inc = self.second_inc

            if primary_variable == secondary_variable or secondary_variable == 'none':
                secondary_variable = None
                secondary_range = (None, None)
                second_inc = None
                secondary_range = self.iteration_count, self.iteration_count
                second_inc = 0

        return primary_range, primary_inc, secondary_range, second_inc, last_ref_cycle_id, primary_variable, \
        secondary_variable


    def setup_grid_sequence(self):
        grid_name = self.get_grid_database_name(self.subgrid_option)
            
        primary_range, primary_inc, secondary_range, second_inc, last_ref_cycle_id, primary_variable, \
        secondary_variable = self.get_variables_ranges_and_increments(grid_name)
            
        grid_sequence = \
        SegClassReconstruct().generate_rise_rotation_or_pitch_unitnumber_pairs_for_symmetry_grid(primary_range,
        primary_inc, secondary_range, second_inc)
            
        grid_sequence = grid_sequence.ravel()
        grid_sequence = self.split_grid_if_demanded(self.subgrid_option, self.subgrid, grid_sequence)
        
        grid_str = [(each_id, each_first, each_second) for each_id, (each_first, each_second) in enumerate(grid_sequence)]
        msg = tabulate(grid_str, ['local_grid_id', primary_variable, secondary_variable])
        self.log.ilog('The following grid combinations will be run:\n{0}'.format(msg))
            
        return grid_sequence, last_ref_cycle_id, primary_variable, secondary_variable, grid_name


    def generate_cmdline_for_each_grid_point(self, parameter_file):
        """
        >>> from spring.segment3d.segrefine3dgrid import SegRefine3dGrid
        >>> s = SegRefine3dGrid()
        >>> s.generate_cmdline_for_each_grid_point('rot_23432_rise_4224.par')
        'segmentrefine3d --d rot_23432_rise_4224 --f rot_23432_rise_4224.par'
        """
        cmdline = 'segmentrefine3d --d {0} --f {1}'.format(os.path.splitext(parameter_file)[0],
        parameter_file)
        
        return cmdline
    

    def make_database_entries(self, run_name, each_grid_point, grid_session, last_cycle, stat_file, reproj_file,
    latest_reconstruction):
        grid_cycle = GridRefineTable()
        rundir_name = os.path.abspath(run_name)
        grid_cycle.dirname = rundir_name
        grid_cycle.primary_value = each_grid_point[0]
        grid_cycle.secondary_value = each_grid_point[1]
        grid_cycle.fsc_0143 = last_cycle.fsc_0143
        grid_cycle.fsc_05 = last_cycle.fsc_05
        grid_cycle.helical_ccc_error = last_cycle.helical_ccc_error
        grid_cycle.mean_helical_ccc = last_cycle.mean_helical_ccc
        grid_cycle.amp_correlation = last_cycle.amp_correlation
        grid_cycle.amp_corr_quarter_nyquist = last_cycle.amp_corr_quarter_nyquist
        grid_cycle.amp_corr_half_nyquist = last_cycle.amp_corr_half_nyquist
        grid_cycle.amp_corr_3quarter_nyquist = last_cycle.amp_corr_3quarter_nyquist
        grid_cycle.variance = last_cycle.variance
        grid_cycle.xshift_error = last_cycle.xshift_error
        grid_cycle.inplane_error = last_cycle.inplane_error
        grid_cycle.outofplane_error = last_cycle.outofplane_error
        grid_cycle.mean_peak = last_cycle.mean_peak
        grid_cycle.excluded_inplane_ratio = last_cycle.excluded_inplane_count / float(last_cycle.segment_count)
        grid_cycle.excluded_out_of_plane_ratio = last_cycle.excluded_out_of_plane_tilt_count / float(last_cycle.segment_count)
        grid_cycle.excluded_total_ratio = last_cycle.total_excluded_count / float(last_cycle.segment_count)
        grid_cycle.asym_unit_count = last_cycle.asym_unit_count
        grid_cycle.avg_azimuth_sampling = last_cycle.avg_azimuth_sampling
        grid_cycle.dev_azimuth_sampling = last_cycle.dev_azimuth_sampling
        grid_cycle.em_files_2d = [(os.path.join(rundir_name, stat_file), 0), (os.path.join(rundir_name, reproj_file), 0)]
        grid_cycle.em_files_3d = [os.path.join(rundir_name, latest_reconstruction)]
        grid_session.add(grid_cycle)
        
        last_grid_entry = grid_session.query(GridTable).order_by(desc(GridTable.id)).first()
        last_grid_entry.completed_grid_id = grid_cycle.id
        
        grid_session.merge(last_grid_entry)
        grid_session.commit()
        
        return grid_cycle
        

    def enter_parameters_in_grid_database(self, primary_variable, secondary_variable, run_name, each_grid_point,
    grid_name, target_cycle_id):
        grid_session = SpringDataBase().setup_sqlite_db(grid_base, grid_name)
                
        ref_db = os.path.join(run_name, 'refinement{0:03}{1}db'.format(target_cycle_id, os.extsep))
        if not os.path.exists(ref_db):
            msg = 'The database file {0} could not be found. This indicates that the refinement '.format(ref_db) + \
            'of the run ({0}) did not complete successfully. Please check the local {1} '.format(run_name, 
            os.path.join(run_name, 'report.log')) + 'file for further error details.'
            raise RuntimeError(msg)
        
        ref_session = SpringDataBase().setup_sqlite_db(refine_base, ref_db)
        
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
        
        stat_file = SegmentRefine3d().generate_diagnostics_statistics_file_name(last_cycle.id, last_cycle.pixelsize,
        self.diagnostic_plot_prefix)
        
        reproj_file = SegmentRefine3d().generate_diagnostics_reprojection_file_name(last_cycle.id, last_cycle.pixelsize,
        self.diagnostic_plot_prefix)
        
        latest_reconstruction = SegmentRefine3d().generate_file_name_with_apix(target_cycle_id, self.outfile_prefix,
        last_cycle.pixelsize)

        this_cycle = self.make_database_entries(run_name, each_grid_point, grid_session, last_cycle, stat_file, reproj_file,
        latest_reconstruction)
        
        columns = SpringDataBase().get_columns_from_table(GridRefineTable)
        log_entries = [str(getattr(this_cycle, each_col)) for each_col in columns]
                                                         
        msg = tabulate(zip(columns, log_entries))

        self.log.ilog('The following parameters have been determined and entered into the database:\n{0}'.format(msg))
        
    
    def enter_variables_into_grid_database(self, primary_variable, secondary_variable, primary_range, secondary_range,
    primary_inc, second_inc, rise_rot_or_pitch_unit_choice):
        primary_db_variable, secondary_db_variable = \
        SegClassReconstruct().get_correct_primary_and_secondary_variables_for_database(rise_rot_or_pitch_unit_choice, 
        secondary_variable)
        
        this_grid_run = SegClassReconstruct().enter_starting_parameters_of_grid_search(primary_db_variable, 
            secondary_db_variable, primary_range, primary_inc, secondary_range, second_inc)
        
        return this_grid_run, primary_db_variable, secondary_db_variable
    

    def prepare_grid_database(self, primary_variable, secondary_variable, primary_range, secondary_range, primary_inc,
    second_inc, grid_name):
        grid_session = SpringDataBase().setup_sqlite_db(grid_base, grid_name)
        this_grid_run, primary_db_variable, secondary_db_variable = self.enter_variables_into_grid_database(primary_variable, 
            secondary_variable, primary_range, secondary_range, primary_inc, second_inc, self.rise_rot_or_pitch_unit_choice)
        
        grid_session.add(this_grid_run)
        grid_session.commit()

        if self.resume_refinement_option:
            cont_ref_session = SpringDataBase().setup_sqlite_db(refine_base, self.refinementdb_path)
            res_cycle = cont_ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
            if res_cycle is None:
                msg = 'Specified refinement.db does not contain any cycles to be continued. ' + \
                'Please, double-check file {0}'.format(self.refinementdb_path)
                raise ValueError(msg)

            target_cycle_id = res_cycle.id + self.iteration_count
        else:
            target_cycle_id = self.iteration_count

        return primary_db_variable, secondary_db_variable, target_cycle_id


    def launch_segmentrefine3d_jobs(self):
        grid_sequence, last_ref_cycle_id, primary_variable, secondary_variable, grid_name = self.setup_grid_sequence()
        
        segmentrefine3d_parameters = \
        self.generate_segmentrefine3d_parameters_while_removing_grid_parameters(self.feature_set.parameters)
        
        primary_db_variable, secondary_db_variable, target_cycle_id = self.prepare_grid_database(primary_variable,
        secondary_variable, self.primary_range, self.secondary_range, self.primary_inc, self.second_inc, grid_name)
            
        for each_grid_id, each_grid_point in enumerate(grid_sequence):
            if each_grid_id >= last_ref_cycle_id:
                parameter_file, run_name = self.setup_parameters_for_each_grid_point(primary_variable, secondary_variable,
                each_grid_point, segmentrefine3d_parameters)
                
                cmdline = self.generate_cmdline_for_each_grid_point(parameter_file)
                self.log.in_progress_log()
                OpenMpi().launch_command(cmdline)
                
                self.enter_parameters_in_grid_database(primary_db_variable, secondary_db_variable, run_name, 
                each_grid_point, grid_name, target_cycle_id)
            
            self.log.plog(100 * (each_grid_id + 1) / len(grid_sequence))
        
        self.log.endlog(self.feature_set)
            
            
def main():
    # Option handling
    parset = SegRefine3dGridPar()
    mergeparset = OptHandler(parset)

    ######## Program
    stack = SegRefine3dGrid(mergeparset)
    stack.launch_segmentrefine3d_jobs()

if __name__ == '__main__':
    main()