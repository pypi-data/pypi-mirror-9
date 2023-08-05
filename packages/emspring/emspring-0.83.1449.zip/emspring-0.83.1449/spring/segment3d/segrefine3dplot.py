# Author: Carsten Sachse 18-Feb-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to plot refinement parameters from segmentrefine3d
"""
from PyQt4.QtGui import QApplication
from spring.csinfrastr.csdatabase import RefinementCycleTable, SpringDataBase, refine_base, SegmentTable, \
    RefinementCycleSegmentTable, RefinementCycleSegmentSubunitTable
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segmentplot import SegmentPlotPar, SegmentPlotGui, SegmentPlot
from spring.segment2d.segmentselect import SegmentSelect
from spring.segment3d.refine.sr3d_main import SegmentRefine3d
from sqlalchemy.sql.expression import desc
import numpy as np
import os
import shutil
import sys

class SegRefine3dPlotPar(SegmentPlotPar):
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'       
        self.progname = 'segrefine3dplot'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.segrefine3dplot_features = Features()
        self.feature_set = self.segrefine3dplot_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    
    def define_parameters_and_their_properties(self):
        self.feature_set = self.segrefine3dplot_features.set_inp_refinement_path(self.feature_set)
        self.feature_set = self.segrefine3dplot_features.set_interactive_vs_batch_mode(self.feature_set)
        self.feature_set = self.segrefine3dplot_features.set_diagnostic_prefix(self.feature_set, 'intermediate', 'Batch mode')
        self.feature_set = self.set_inp_spring_path(self.feature_set)
#        self.feature_set = self.set_refinement_cycle(self.feature_set)
        
        self.feature_set = self.set_ref_quantities_to_be_plotted(self.feature_set)
        self.feature_set = self.set_set_size(self.feature_set)
        
        self.feature_set = self.segrefine3dplot_features.set_micrograph_and_helix_selection_criteria(self.feature_set)
        

    def define_program_states(self):
        self.feature_set.program_states['get_ref_quantities_per_set']='Extract desired refinement quantities from spring database'
        self.feature_set.program_states['plot_data_on_figure']='Prepare figures with desired refined quantities'


    def set_refinement_cycle(self, feature_set):
        inp3 = 'Iteration cycle' 
        feature_set.parameters[inp3] = int(5)
        feature_set.hints[inp3] = 'Iteration cycle to be analyzed.'
        feature_set.properties[inp3] = feature_set.Range(1, 1000, 1)
        feature_set.level[inp3]='intermediate'
        
        return feature_set


    def set_ref_quantities_to_be_plotted(self, feature_set):
        inp3 = 'Refinement quantities'
        feature_set.parameters[inp3]=str('coordinates')
        feature_set.properties[inp3]=feature_set.choice_properties(2, ['coordinates', 'coordinates_subunit', 
        'in-plane_rotation', 'normalized_in-plane_rotation', 'out-of-plane_tilt', 'phi', 'theta', 'psi', 'x_shift', 
        'y_shift', 'shift_perpendicular_to_helix', 'shift_along_helix', 'ccc_peak'], 'QComboBox')
        
        feature_set.hints[inp3]=SpringDataBase().get_hints_from_ref_segment_table(feature_set.properties[inp3].choices)
        feature_set.level[inp3]='beginner'
        
        return feature_set
    
    
class SegRefine3dPlotPreparation(object):
    """
    * Class that holds functions for examining segments from micrographs

    * __init__ Function to interpret multi-input parameters

    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.infile = p['refinement.db file']
            self.outfile_prefix = p['Diagnostic plot prefix']
            self.spring_file = p['spring.db file']
            
            self.quantities = p['Refinement quantities']
            self.batch_mode = p['Batch mode']
            self.set_size = p['Set size']

            self = SegmentSelect().define_mics_and_helices_selection(self, p)


    def check_ref_values_and_raise_error(self, quantities, y_plot):
        if y_plot[0] is None:
            msg = '{0} entry does not exist in specified refinement.db. '.format(quantities) + \
            'Re-run segmentrefine3d to save relevant information.'
            raise ValueError(msg)


    def get_labels_according_to_ref_quantities(self, set_size, quantities):
        """
        >>> from spring.segment3d.segrefine3dplot import SegRefine3dPlot
        >>> SegRefine3dPlot().get_labels_according_to_ref_quantities('helix', 'coordinates') #doctest: +NORMALIZE_WHITESPACE
        ['Stack_id', 'Refined X-Coordinate (Angstrom)', 'Refined Y-Coordinate (Angstrom)', 
        'Picked X-Coordinate (Angstrom)', 'Picked Y-Coordinate (Angstrom)', 
        'Selected refined X-Coordinate (Angstrom)', 'Selected refined Y-Coordinate (Angstrom)']
        >>> SegRefine3dPlot().get_labels_according_to_ref_quantities('helix', 'in-plane_rotation') #doctest: +NORMALIZE_WHITESPACE
        ['Stack_id', 'Distance Along Helix (Angstrom)', 'In-Plane Rotation Angle (Degrees)', 
        'Selected In-Plane Rotation Angle (Degrees)', 'Local Average In-Plane Rotation Angle (Degrees)']
        >>> SegRefine3dPlot().get_labels_according_to_ref_quantities('helix', 'normalized_in-plane_rotation') #doctest: +NORMALIZE_WHITESPACE
        ['Stack_id', 'Distance Along Helix (Angstrom)', 'Normalized In-Plane Rotation Angle (Degrees)', 
        'Selected Normalized In-Plane Rotation Angle (Degrees)']
        >>> SegRefine3dPlot().get_labels_according_to_ref_quantities('helix', 'coordinates_subunit') #doctest: +NORMALIZE_WHITESPACE
        ['Stack_id', 'Refined subunit X-Coordinate (Angstrom)', 'Refined subunit Y-Coordinate (Angstrom)', 
        'Picked X-Coordinate (Angstrom)', 'Picked Y-Coordinate (Angstrom)', 'Selected refined X-Coordinate (Angstrom)', 
        'Selected refined Y-Coordinate (Angstrom)']
        """
        
        labels = ['Stack_id']
        if set_size == 'helix' and not quantities.startswith('coordinates'):
            labels += SpringDataBase().get_labels_from_table(SegmentTable, 'distance_from_start_A')
        elif quantities.startswith('coordinates'):
            coord_labels = SpringDataBase().get_labels_from_table(SegmentTable, 'x_coordinate_A',
            'y_coordinate_A')
            
            if quantities.endswith('coordinates'):
                ref_labels = ['Refined {0}'.format(each_coord_label) for each_coord_label in coord_labels]
            else:
                ref_labels = ['Refined subunit {0}'.format(each_coord_label) for each_coord_label in coord_labels]
            sel_labels = ['Selected refined {0}'.format(each_coord_label) for each_coord_label in coord_labels]
            coord_labels = ['Picked {0}'.format(each_coord_label) for each_coord_label in coord_labels]
            labels += ref_labels + coord_labels + sel_labels
            
        if quantities == 'phi':
            labels += SpringDataBase().get_labels_from_table(RefinementCycleSegmentTable, 'phi')
        elif quantities == 'theta':
            labels += SpringDataBase().get_labels_from_table(RefinementCycleSegmentTable, 'theta')
        elif quantities == 'psi':
            labels += SpringDataBase().get_labels_from_table(RefinementCycleSegmentTable, 'psi')
        elif quantities == 'in-plane_rotation':
            labels += SpringDataBase().get_labels_from_table(RefinementCycleSegmentTable, 'inplane_angle',
            'lavg_inplane_angle')
        elif quantities == 'normalized_in-plane_rotation':
            labels += SpringDataBase().get_labels_from_table(RefinementCycleSegmentTable, 'norm_inplane_angle')
        elif quantities == 'out-of-plane_tilt':
            labels += SpringDataBase().get_labels_from_table(RefinementCycleSegmentTable, 'out_of_plane_angle',
            'lavg_out_of_plane')
        elif quantities == 'x_shift':
            labels += SpringDataBase().get_labels_from_table(RefinementCycleSegmentTable, 'shift_x_A')
        elif quantities == 'y_shift':
            labels += SpringDataBase().get_labels_from_table(RefinementCycleSegmentTable, 'shift_y_A')
        elif quantities == 'shift_perpendicular_to_helix':
            labels += SpringDataBase().get_labels_from_table(RefinementCycleSegmentTable, 'helix_shift_x_A',
            'lavg_helix_shift_x_A')
        elif quantities == 'shift_along_helix':
            labels += SpringDataBase().get_labels_from_table(RefinementCycleSegmentTable, 'helix_shift_y_A')
        elif quantities == 'ccc_peak':
            labels += SpringDataBase().get_labels_from_table(RefinementCycleSegmentTable, 'peak')
            
        if set_size == 'helix' and not quantities.startswith('coordinates'):
            labels += ['Selected {0}'.format(labels[2])]
            
        if set_size == 'helix' and quantities in ['in-plane_rotation', 'out-of-plane_tilt',
        'shift_perpendicular_to_helix']:
            labels = labels[:-2] + [labels[-1]] + [labels[-2]]
            
        return labels
    
    
    def get_refinement_cycle_id(self, infile):
        shutil.copy(infile, os.path.basename(infile))
        
        ref_session = SpringDataBase().setup_sqlite_db(refine_base, os.path.basename(infile))

        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
            
        return ref_session, last_cycle
    

class SegRefine3dPlotDataRetrieval(SegRefine3dPlotPreparation):
    def get_x_and_y_coordinates_from_helix_segments(self, each_helix_segments, each_helix_ref_segments,
    excluded_segments):
        x_coord = np.array([each_helix_segment.picked_x_coordinate_A for each_helix_segment in each_helix_segments])
        y_coord = np.array([each_helix_segment.picked_y_coordinate_A for each_helix_segment in each_helix_segments])
        stack_ids = np.array([each_helix_segment.stack_id for each_helix_segment in each_helix_segments])
        
        ref_stack_ids = np.array([each_helix_ref_segment.stack_id for each_helix_ref_segment in each_helix_ref_segments])

        ref_all_x_shifts = np.zeros(len(stack_ids))
        ref_x_shifts = np.array([each_helix_ref_segment.shift_x_A for each_helix_ref_segment in each_helix_ref_segments])
        ref_all_x_shifts[stack_ids.searchsorted(ref_stack_ids)] = ref_x_shifts
        
        ref_x_coord = x_coord + ref_all_x_shifts

        ref_all_y_shifts = np.zeros(len(stack_ids))
        ref_y_shifts = np.array([each_helix_ref_segment.shift_y_A for each_helix_ref_segment in each_helix_ref_segments])
        ref_all_y_shifts[stack_ids.searchsorted(ref_stack_ids)] = ref_y_shifts
        
        ref_y_coord = y_coord + ref_all_y_shifts
#        ref_x_coord = x_coord + np.array([each_helix_ref_segment.shift_x_A for each_helix_ref_segment in
#        each_helix_ref_segments])
        
#        ref_y_coord = y_coord + np.array([each_helix_ref_segment.shift_y_A for each_helix_ref_segment in
#        each_helix_ref_segments])
        
        sel_x_coord = np.array(np.ma.masked_array(x_coord, mask=excluded_segments).tolist(), dtype=float)
        sel_y_coord = np.array(np.ma.masked_array(y_coord, mask=excluded_segments).tolist(), dtype=float)
        sel_ref_x_coord = np.array(np.ma.masked_array(ref_x_coord, mask=excluded_segments).tolist(), dtype=float)
        sel_ref_y_coord = np.array(np.ma.masked_array(ref_y_coord, mask=excluded_segments).tolist(), dtype=float)
        
        return x_coord, y_coord, ref_x_coord, ref_y_coord, sel_x_coord, sel_y_coord, sel_ref_x_coord, sel_ref_y_coord
    

    def get_refined_quantities_from_segments(self, quantities, each_helix_ref_segments):
        if quantities == 'normalized_in-plane_rotation':
            y_plot = [each_helix_ref_segment.norm_inplane_angle for each_helix_ref_segment in each_helix_ref_segments]
            self.check_ref_values_and_raise_error(quantities, y_plot)
        elif quantities == 'phi':
            y_plot = [each_helix_ref_segment.phi for each_helix_ref_segment in each_helix_ref_segments]
            self.check_ref_values_and_raise_error(quantities, y_plot)
        elif quantities == 'theta':
            y_plot = [each_helix_ref_segment.theta for each_helix_ref_segment in each_helix_ref_segments]
            self.check_ref_values_and_raise_error(quantities, y_plot)
        elif quantities == 'psi':
            y_plot = [each_helix_ref_segment.psi for each_helix_ref_segment in each_helix_ref_segments]
            self.check_ref_values_and_raise_error(quantities, y_plot)
        elif quantities == 'x_shift':
            y_plot = [each_helix_ref_segment.shift_x_A for each_helix_ref_segment in each_helix_ref_segments]
            self.check_ref_values_and_raise_error(quantities, y_plot)
        elif quantities == 'y_shift':
            y_plot = [each_helix_ref_segment.shift_y_A for each_helix_ref_segment in each_helix_ref_segments]
            self.check_ref_values_and_raise_error(quantities, y_plot)
        elif quantities == 'shift_along_helix':
            y_plot = [each_helix_ref_segment.helix_shift_y_A for each_helix_ref_segment in each_helix_ref_segments]
            self.check_ref_values_and_raise_error(quantities, y_plot)
        elif quantities == 'ccc_peak':
            y_plot = [each_helix_ref_segment.peak for each_helix_ref_segment in each_helix_ref_segments]
            self.check_ref_values_and_raise_error(quantities, y_plot)
        else:
            y_plot = None
            
        return y_plot
    
    
    def get_refined_subunit_coordinates(self, session, ref_session, each_helix_ref_segments):
        sub_xcoord = np.array([])
        sub_ycoord = np.array([])
        subunit_stack_ids = np.array([])
        for each_ref_segment in each_helix_ref_segments:
            each_ref_subunits = ref_session.query(RefinementCycleSegmentSubunitTable).\
            filter(RefinementCycleSegmentSubunitTable.ref_seg_id == each_ref_segment.id).all()
        
            each_segment = session.query(SegmentTable).get(each_ref_segment.stack_id + 1)
        
            sub_xcoord = np.append(sub_xcoord, each_segment.picked_x_coordinate_A + \
            np.array([each_subunit.shift_x_A for each_subunit in each_ref_subunits]))
            
            sub_ycoord = np.append(sub_ycoord, each_segment.picked_y_coordinate_A + \
            np.array([each_subunit.shift_y_A for each_subunit in each_ref_subunits]))
        
            subunit_stack_ids = np.append(subunit_stack_ids, np.array([each_ref_segment.stack_id for each_subunit in
            each_ref_subunits]))
            
        return subunit_stack_ids, sub_xcoord, sub_ycoord
    

    def prepare_data_for_table_display(self, each_helix_stack_ids, x_coord, y_coord, sel_ref_x_coord, sel_ref_y_coord,
    each_helix_su_stack_ids, sub_xcoord, sub_ycoord):
    
        filled_x_coord = np.zeros(len(sub_xcoord))
        filled_y_coord = np.zeros(len(sub_ycoord))
        filled_ref_x_coord = np.zeros(len(sub_xcoord))
        filled_ref_y_coord = np.zeros(len(sub_ycoord))
        each_helix_stack_ids = np.array(each_helix_stack_ids)
        for each_unique_stack_id in each_helix_stack_ids:
            filled_x_coord[each_helix_su_stack_ids == each_unique_stack_id] = \
            x_coord[each_helix_stack_ids == each_unique_stack_id]
            
            filled_y_coord[each_helix_su_stack_ids == each_unique_stack_id] = \
            y_coord[each_helix_stack_ids == each_unique_stack_id]
            
            filled_ref_x_coord[each_helix_su_stack_ids == each_unique_stack_id] = \
            sel_ref_x_coord[each_helix_stack_ids == each_unique_stack_id]
            
            filled_ref_y_coord[each_helix_su_stack_ids == each_unique_stack_id] = \
            sel_ref_y_coord[each_helix_stack_ids == each_unique_stack_id]
        
        return each_helix_stack_ids, filled_x_coord, filled_y_coord, filled_ref_x_coord, filled_ref_y_coord


    def add_picked_coordinates_of_exluded_segments(self, each_helix_stack_ids, excluded_segments, x_coord, y_coord,
    each_helix_su_stack_ids, sub_xcoord, sub_ycoord, filled_x_coord, filled_y_coord, filled_ref_x_coord,
    filled_ref_y_coord):
        
        excl_x_coord = np.ma.masked_array(x_coord, mask=np.invert(excluded_segments)).compressed()
        excl_y_coord = np.ma.masked_array(y_coord, mask=np.invert(excluded_segments)).compressed()
        excl_stack_ids = np.ma.masked_array(each_helix_stack_ids, mask=np.invert(excluded_segments)).compressed()
        for each_ex_id, each_ex_refx, each_ex_refy in zip(excl_stack_ids, excl_x_coord, excl_y_coord):
            each_helix_su_stack_ids = np.append(each_helix_su_stack_ids, each_ex_id)
            sub_xcoord = np.append(sub_xcoord, np.nan)
            sub_ycoord = np.append(sub_ycoord, np.nan)
            filled_x_coord = np.append(filled_x_coord, each_ex_refx)
            filled_y_coord = np.append(filled_y_coord, each_ex_refy)
            filled_ref_x_coord = np.append(filled_ref_x_coord, np.nan)
            filled_ref_y_coord = np.append(filled_ref_y_coord, np.nan)
        
        return each_helix_su_stack_ids, sub_xcoord, sub_ycoord, filled_x_coord, filled_y_coord, filled_ref_x_coord, filled_ref_y_coord


    def get_coordinates_from_refinement(self, session, ref_session, each_plot_set_string, quantities, xy_quantities,
    each_helix_stack_ids, each_helix_segments, each_helix_ref_segments, excluded_segments):
    
        x_coord, y_coord, ref_x_coord, ref_y_coord, sel_x_coord, sel_y_coord, sel_ref_x_coord, sel_ref_y_coord = \
        self.get_x_and_y_coordinates_from_helix_segments(each_helix_segments, each_helix_ref_segments,
        excluded_segments)
            
        if quantities == 'coordinates':
            self.check_ref_values_and_raise_error(quantities, y_coord)
            
            xy_quantities.append((each_plot_set_string, np.vstack([each_helix_stack_ids, ref_x_coord, ref_y_coord,
            x_coord, y_coord, sel_ref_x_coord, sel_ref_y_coord])))
            
        elif quantities == 'coordinates_subunit':
            each_helix_su_stack_ids, sub_xcoord, sub_ycoord = self.get_refined_subunit_coordinates(session, ref_session,
            each_helix_ref_segments)
            
            each_helix_stack_ids, filled_x_coord, filled_y_coord, filled_ref_x_coord, filled_ref_y_coord = \
            self.prepare_data_for_table_display(each_helix_stack_ids, x_coord, y_coord, sel_ref_x_coord,
            sel_ref_y_coord, each_helix_su_stack_ids, sub_xcoord, sub_ycoord)
                
            each_helix_su_stack_ids, sub_xcoord, sub_ycoord, filled_x_coord, filled_y_coord, filled_ref_x_coord, \
            filled_ref_y_coord = self.add_picked_coordinates_of_exluded_segments(each_helix_stack_ids,
            excluded_segments, x_coord, y_coord, each_helix_su_stack_ids, sub_xcoord, sub_ycoord, filled_x_coord,
            filled_y_coord, filled_ref_x_coord, filled_ref_y_coord)
                
            xy_quantities.append((each_plot_set_string, np.vstack([each_helix_su_stack_ids, sub_xcoord, sub_ycoord,
            filled_x_coord, filled_y_coord, filled_ref_x_coord, filled_ref_y_coord])))
        return xy_quantities


    def get_refinement_parameters_no_local_averaging(self, each_plot_set_string, set_size, quantities, xy_quantities,
    each_helix_stack_ids, each_helix_ref_segments, excluded_segments, distances):
        
        if quantities in ['phi', 'theta', 'psi', 'x_shift', 'y_shift', 'normalized_in-plane_rotation',
        'shift_along_helix', 'ccc_peak']:
            y_plot = self.get_refined_quantities_from_segments(quantities, each_helix_ref_segments)
            sel_y_plot = np.array(np.ma.masked_array(y_plot, mask=excluded_segments).tolist(), dtype=float)
            if set_size == 'helix':
                xy_quantities.append((each_plot_set_string, np.vstack([each_helix_stack_ids, distances, y_plot,
                sel_y_plot])))
            else:
                xy_quantities.append((each_plot_set_string, np.vstack([each_helix_stack_ids, y_plot])))
                
        return xy_quantities
    

    def get_refinement_parameters_including_local_averaging(self, each_plot_set_string, set_size, quantities,
    xy_quantities, each_helix_stack_ids, each_helix_ref_segments, excluded_segments, each_helix_ref_segment, distances):
        
        if quantities in ['in-plane_rotation', 'out-of-plane_tilt', 'shift_perpendicular_to_helix']:
            if quantities == 'in-plane_rotation':
                y_plot = [each_helix_ref_segment.inplane_angle for each_helix_ref_segment in each_helix_ref_segments]
                
                avg_y_plot = [each_helix_ref_segment.lavg_inplane_angle for each_helix_ref_segment in \
                each_helix_ref_segments]
                
                self.check_ref_values_and_raise_error(quantities, y_plot)
            elif quantities == 'out-of-plane_tilt':
                y_plot = [each_helix_ref_segment.out_of_plane_angle for each_helix_ref_segment in each_helix_ref_segments]
                
                avg_y_plot = [each_helix_ref_segment.lavg_out_of_plane for each_helix_ref_segment in \
                each_helix_ref_segments]
                
                self.check_ref_values_and_raise_error(quantities, y_plot)
            elif quantities == 'shift_perpendicular_to_helix':
                y_plot = [each_helix_ref_segment.helix_shift_x_A for each_helix_ref_segment in each_helix_ref_segments]
                
                avg_y_plot = [each_helix_ref_segment.lavg_helix_shift_x_A for each_helix_ref_segment in \
                each_helix_ref_segments]
                
                self.check_ref_values_and_raise_error(quantities, y_plot)
            sel_y_plot = np.array(np.ma.masked_array(y_plot, mask=excluded_segments).tolist(), dtype=float)
            if set_size == 'helix':
                xy_quantities.append((each_plot_set_string, np.vstack([each_helix_stack_ids, distances, y_plot,
                sel_y_plot, avg_y_plot])))
            else:
                xy_quantities.append((each_plot_set_string, np.vstack([each_helix_stack_ids, y_plot])))
            
        return xy_quantities
    

    def get_refinement_parameters(self, each_plot_set_string, set_size, quantities, xy_quantities, each_helix_stack_ids,
    each_helix_segments, each_helix_ref_segments, excluded_segments, each_helix_ref_segment, distances):
        
        if quantities in ['phi', 'theta', 'psi', 'x_shift', 'y_shift', 'normalized_in-plane_rotation',
        'shift_along_helix', 'ccc_peak', 'in-plane_rotation', 'out-of-plane_tilt', 'shift_perpendicular_to_helix']:
            
            xy_quantities = self.get_refinement_parameters_no_local_averaging(each_plot_set_string, set_size,
            quantities, xy_quantities, each_helix_stack_ids, each_helix_ref_segments, excluded_segments, distances)
            
            xy_quantities = self.get_refinement_parameters_including_local_averaging(each_plot_set_string, set_size,
            quantities, xy_quantities, each_helix_stack_ids, each_helix_ref_segments, excluded_segments,
            each_helix_ref_segment, distances)
        
        return xy_quantities
    

    def get_specified_ref_quantities(self, session, ref_session, each_plot_set_string, set_size, quantities, xy_quantities,
    each_helix_stack_ids, each_helix_segments, each_helix_ref_segments):
    
        ref_stack_ids = np.array([each_helix_ref_segment.stack_id for each_helix_ref_segment in each_helix_ref_segments])
        
        excluded_ref_segments = np.invert([bool(each_helix_ref_segment.selected) for each_helix_ref_segment in \
        each_helix_ref_segments])
        
        helix_stack_ids = np.array(each_helix_stack_ids)
        excluded_segments = np.array(len(each_helix_stack_ids) * [False])
        excluded_segments[helix_stack_ids.searchsorted(ref_stack_ids)] = excluded_ref_segments
        
        xy_quantities = self.get_coordinates_from_refinement(session, ref_session, each_plot_set_string, quantities,
        xy_quantities, each_helix_stack_ids, each_helix_segments, each_helix_ref_segments, excluded_segments)
            
        distances = np.array([each_helix_segment.distance_from_start_A for each_helix_segment in each_helix_segments])
        ref_distances = distances[helix_stack_ids.searchsorted(ref_stack_ids)] 
        
        xy_quantities = self.get_refinement_parameters(each_plot_set_string, set_size, quantities, xy_quantities,
        ref_stack_ids, each_helix_segments, each_helix_ref_segments, excluded_ref_segments,
        each_helix_ref_segment, ref_distances)
                
        return xy_quantities
    

    def get_ref_quantities_per_set(self, spring_path, quantities):
        self.log.fcttolog()
        shutil.copy(spring_path, 'spring.db')
        
        session, plot_sets = SegmentPlot().get_plot_set(self.set_size, self)
        combined_included_segments = SegmentPlot().filter_segments_by_helix_and_micrograph_criteria(session, self)
        
        labels = self.get_labels_according_to_ref_quantities(self.set_size, quantities)
        ref_session, ref_cycle = self.get_refinement_cycle_id(self.infile)
        xy_quantities = []
        for each_plot_set in plot_sets:
            each_helix_seg_ids, each_helix_segments = SegmentPlot().get_segment_ids_according_to_set_size(session,
            self.set_size, each_plot_set)
            
            if len(set(each_helix_seg_ids).intersection(combined_included_segments)) != 0:
                each_set_id_label = SegmentPlot().generate_set_id_label_for_plot_and_filename(self.set_size,
                each_plot_set)
                
                each_helix_ref_segments = SegmentRefine3d().get_all_segments_from_refinement_cycle(ref_session,
                ref_cycle, each_helix_seg_ids)
                
                xy_quantities = self.get_specified_ref_quantities(session, ref_session, each_set_id_label, self.set_size, quantities,
                xy_quantities, each_helix_seg_ids, each_helix_segments, each_helix_ref_segments)
                        
        log_info = SegmentPlot().prepare_log_string(labels, xy_quantities)
                
        self.log.ilog(log_info)
                    
        return labels, xy_quantities
    
    
class SegRefine3dPlotVisualize(SegRefine3dPlotDataRetrieval):
    def plot_ref_data_on_figure(self, xy_quantities, quantities, labels):
        segplot = SegmentPlot()
        segplot.feature_set = self.feature_set
        segplot.batch_mode = self.batch_mode
        segplot.infile = self.infile
        segplot.outfile_prefix = self.outfile_prefix
        segplot.set_size = self.set_size
        
        figures = segplot.plot_data_on_figure(xy_quantities, labels)

        return figures, segplot
            
            
class SegRefine3dPlot(SegRefine3dPlotVisualize):
        
    def launch_interactive_plot_gui(self, figures, tables, labels):
        labels = [labels for each_table in tables]
        app = QApplication(sys.argv)
        symexplor = SegmentPlotGui(self.feature_set, figures, tables, labels)
        symexplor.show()
        app.exec_()

        
    def plot_desired_ref_quantities(self):
        labels, xy_quantities = self.get_ref_quantities_per_set(self.spring_file, self.quantities)
        self.log.plog(10)
        figures, segplot = self.plot_ref_data_on_figure(xy_quantities, self.quantities, labels)
        if not self.batch_mode:
            all_labels = [labels for each_table in xy_quantities]
            segplot.launch_interactive_plot_gui(self.feature_set, figures, xy_quantities, all_labels)
        
        self.log.endlog(self.feature_set)
        
        
def main():
    # Option handling
    parset = SegRefine3dPlotPar()
    mergeparset = OptHandler(parset)
    ######## Program
    stack = SegRefine3dPlot(mergeparset)
    stack.plot_desired_ref_quantities()

if __name__ == '__main__':
    main()
