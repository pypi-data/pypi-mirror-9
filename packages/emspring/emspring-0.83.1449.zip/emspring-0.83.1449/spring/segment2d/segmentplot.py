# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to plot parameters from segmented helices
"""
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QApplication, QWidget, QStackedWidget, QSplitter, QComboBox
from collections import namedtuple
from matplotlib.font_manager import FontProperties
from spring.csinfrastr.csdatabase import SpringDataBase, base, SegmentTable, HelixTable, CtfMicrographTable
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import DiagnosticPlot
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segmentselect import SegmentSelect
from spring.springgui.springdataexplore import SpringCommon, SpringDataExplore, SpringDataExploreTablePane
from tabulate import tabulate
import numpy as np
import os
import shutil
import sys

class SegmentPlotPar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'segmentplot'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.segmentplot_features = Features()
        self.feature_set = self.segmentplot_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    
    def define_parameters_and_their_properties(self):
        self.feature_set = self.set_inp_spring_path(self.feature_set)
        self.feature_set = self.segmentplot_features.set_interactive_vs_batch_mode(self.feature_set)
        
        self.feature_set = self.segmentplot_features.set_diagnostic_prefix(self.feature_set, 'intermediate', 
        'Batch mode')
        
        self.feature_set = self.set_quantities_to_be_plotted(self.feature_set)
        self.feature_set = self.set_set_size(self.feature_set)
        
        self.feature_set = self.segmentplot_features.set_selection_criteria_from_segment_table(self.feature_set)
        

    def define_program_states(self):

        self.feature_set.program_states['get_quantities_per_set']='Extract desired quantities from spring database'
        self.feature_set.program_states['plot_data_on_figure']='Prepare figures with desired quantities'


    def set_inp_spring_path(self, feature_set):
        inp3 = 'spring.db file'
        feature_set.parameters[inp3]='spring.db'
        feature_set.hints[inp3]='Requires spring.db from segment to plot helix parameters.'
        feature_set.properties[inp3]=feature_set.file_properties(1,['db'],'getFile')
        feature_set.level[inp3]='beginner'
        
        return feature_set
    
    
    def set_quantities_to_be_plotted(self, feature_set):
        inp3 = 'Quantities'
        feature_set.parameters[inp3]=str('coordinates')
        
        feature_set.properties[inp3]=feature_set.choice_properties(2, ['coordinates', 'in-plane_rotation', 'curvature',
        'defocus', 'astigmatism', 'layer-line correlation', 'classes', 'class_models'], 'QComboBox')
        
        feature_set.hints[inp3]=SpringDataBase().get_hints_from_segment_table(feature_set.properties[inp3].choices)  
        feature_set.level[inp3]='beginner'
        
        return feature_set
    
    
    def set_interactive_vs_batch_mode(self, feature_set):
        inp3 = 'Interactive vs. batch mode'
        feature_set.parameters[inp3]='interactive'
        feature_set.hints[inp3]='Choose between interactive (enables quantity per helix view) vs. batch plotting mode.'
        feature_set.properties[inp3]=feature_set.choice_properties(2, ['interactive', 'batch'], 'QComboBox')
        feature_set.level[inp3]='expert'
        
        return feature_set
    
    
    def set_set_size(self, feature_set):
        inp3 = 'Set size'
        feature_set.parameters[inp3]='helix'
        feature_set.hints[inp3]='Choose set size to plot: chosen quantity per \'helix\', \'micrograph\' or \'data_set\'.'
        feature_set.properties[inp3]=feature_set.choice_properties(2, ['helix', 'micrograph', 'data_set'], 'QComboBox')
        feature_set.level[inp3]='expert'
        
        return feature_set
        
    
class SegmentPlotPrepare(object):
    """
    * Class that holds functions for examining segments from micrographs

    * __init__ Function to interpret multi-input parameters

    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.infile = p['spring.db file']
            self.outfile_prefix = p['Diagnostic plot prefix']
            
            self.quantities = p['Quantities']
            self.batch_mode = p['Batch mode']
            self.set_size = p['Set size']

            self = SegmentSelect().define_selection_parameters_from_segment_table(self, p)



    def check_class_values_and_raise_error(self, quantities, y_plot):
        if y_plot[0] is None:
            msg = '{0} entry does not exist in specified spring.db. '.format(quantities) + \
            'Re-run segmentclass including database option to save class information.'
            raise ValueError(msg)


    def check_class_model_values_and_raise_error(self, quantities, y_plot):
        if y_plot[0] is None:
            msg = '{0} entry does not exist in specified spring.db. '.format(quantities) + \
            'Re-run segmentrefine3d or segclassmodel including database option to save class model information.'
            raise ValueError(msg)


    def check_ctf_values_and_raise_error(self, quantities, y_plot):
        if y_plot[0] is None:
            msg = '{0} entry does not exist in specified spring.db. '.format(quantities) + \
            'Re-run micctfdetermine or segment to save CTF-information.'
            raise ValueError(msg)


    def check_layerline_values_and_raise_error(self, quantities, y_plot):
        if y_plot[0] is None:
            msg = '{0} entry does not exist in specified spring.db. '.format(quantities)
            'Re-run segmentexam with the \'Compute layer-line correlation option\'.'
            raise ValueError(msg)


    def check_segmenting_values_and_raise_error(self, quantities, y_plot):
        if y_plot[0] is None:
            msg = '{0} entry does not exist in specified spring.db. Re-run segment to save relevant information.'.\
            format(quantities)
            raise ValueError(msg)


    def get_subset_if_selected(self, plot_sets, attr_selection, attr_in_or_exclude, attr_entries, attr_id):
        if attr_selection:
            attr_list = SegmentSelect().prepare_list_from_comma_separated_input(attr_entries, 'helix')
            if attr_in_or_exclude == 'include':
                plot_sets = [each_set for each_set in plot_sets if getattr(each_set, attr_id) in attr_list]
            elif attr_in_or_exclude == 'exclude':
                plot_sets = [each_set for each_set in plot_sets if getattr(each_set, attr_id) not in attr_list]

        return plot_sets


    def get_plot_set(self, set_size, obj):
        session = SpringDataBase().setup_sqlite_db(base)
        if set_size == 'helix':
            plot_sets = session.query(HelixTable).order_by(HelixTable.id).all()

            plot_sets = self.get_subset_if_selected(plot_sets, obj.mics_selection, obj.mics_in_or_exclude,
            obj.mics_entries, 'mic_id')

            plot_sets = self.get_subset_if_selected(plot_sets, obj.helices_selection, obj.helices_in_or_exclude,
            obj.helices_entries, 'id')
        elif set_size == 'micrograph':
            plot_sets = session.query(CtfMicrographTable).order_by(CtfMicrographTable.id).all()
            if obj.helices_selection:
                helix_sets = session.query(HelixTable).order_by(HelixTable.id).all()
                helix_sets = self.get_subset_if_selected(helix_sets, obj.helices_selection, obj.helices_in_or_exclude,
                obj.helices_entries, 'id')
                mic_ids = list(set([each_helix.mic_id for each_helix in helix_sets]))

                plot_sets = [each_set for each_set in plot_sets if each_set.id in mic_ids]

            plot_sets = self.get_subset_if_selected(plot_sets, obj.mics_selection, obj.mics_in_or_exclude,
            obj.mics_entries, 'id')
        elif set_size == 'data_set':
            plotset_tuple = namedtuple('plot_set', 'id')
            plot_sets = [plotset_tuple('entire')]
            
        return session, plot_sets
    

    def filter_segments_by_helix_and_micrograph_criteria(self, session, obj):
        segments = session.query(SegmentTable).order_by(SegmentTable.stack_id).all()

        included_segments_mics, excluded_mics_count = SegmentSelect().filter_segments_by_entry_string(segments,
        'mic_id', obj.mics_selection, obj.mics_in_or_exclude, obj.mics_entries, 'micrograph')
         
        included_segments_helices, excluded_helix_count = SegmentSelect().filter_segments_by_entry_string(segments,
        'helix_id', obj.helices_selection, obj.helices_in_or_exclude, obj.helices_entries, 'helix')
         
        combined_included_segments = list(set(included_segments_mics).intersection(included_segments_helices))
 
        return combined_included_segments
    

    def prepare_helix_and_coordinates(self, set_size, quantities):
        labels = ['Stack_id']
        if set_size == 'helix' and quantities != 'coordinates':
            labels += SpringDataBase().get_labels_from_table(SegmentTable, 'distance_from_start_A')
        elif quantities == 'coordinates':
            labels += SpringDataBase().get_labels_from_table(SegmentTable, 'x_coordinate_A', 'y_coordinate_A',
            'picked_x_coordinate_A', 'picked_y_coordinate_A')
            
        return labels


    def get_labels_according_to_quantities(self, set_size, quantities):
        """
        >>> from spring.segment2d.segmentplot import SegmentPlot
        >>> SegmentPlot().get_labels_according_to_quantities('helix', 'coordinates') #doctest: +NORMALIZE_WHITESPACE
        ['Stack_id', 'X-Coordinate (Angstrom)', 'Y-Coordinate (Angstrom)', 'Picked X-Coordinate (Angstrom)', 
        'Picked Y-Coordinate (Angstrom)']
        >>> SegmentPlot().get_labels_according_to_quantities('helix', 'curvature') 
        ['Stack_id', 'Distance Along Helix (Angstrom)', 'Curvature', 'Selected Curvature']
        >>> SegmentPlot().get_labels_according_to_quantities('data_set', 'curvature') 
        ['Stack_id', 'Curvature', 'Selected Curvature']
        >>> SegmentPlot().get_labels_according_to_quantities('micrograph', 'astigmatism') 
        ['Stack_id', 'Astigmatism (Angstrom)', 'Selected Astigmatism (Angstrom)']
        """
        labels = self.prepare_helix_and_coordinates(set_size, quantities)
            
        if quantities == 'in-plane_rotation':
            labels += SpringDataBase().get_labels_from_table(SegmentTable, 'inplane_angle')
            labels += ['Selected ' + SpringDataBase().get_labels_from_table(SegmentTable, 'inplane_angle')[0]]
        elif quantities in ['curvature']:
            labels += SpringDataBase().get_labels_from_table(SegmentTable, 'curvature')
            labels += ['Selected ' + SpringDataBase().get_labels_from_table(SegmentTable, 'curvature')[0]]
        elif quantities == 'layer-line correlation':
            labels += SpringDataBase().get_labels_from_table(SegmentTable, 'ccc_layer')
            labels += ['Selected ' + SpringDataBase().get_labels_from_table(SegmentTable, 'ccc_layer')[0]]
        elif quantities == 'defocus':
            labels += SpringDataBase().get_labels_from_table(SegmentTable, 'avg_defocus')
            labels += ['Selected ' + SpringDataBase().get_labels_from_table(SegmentTable, 'avg_defocus')[0]]
        elif quantities == 'astigmatism':
            labels += SpringDataBase().get_labels_from_table(SegmentTable, 'astigmatism')
            labels += ['Selected ' + SpringDataBase().get_labels_from_table(SegmentTable, 'astigmatism')[0]]
        elif quantities == 'classes':
            labels += SpringDataBase().get_labels_from_table(SegmentTable, 'class_id')
            labels += ['Selected ' + SpringDataBase().get_labels_from_table(SegmentTable, 'class_id')[0]]
        elif quantities == 'class_models':
            labels += SpringDataBase().get_labels_from_table(SegmentTable, 'class_model_id')
            labels += ['Selected ' + SpringDataBase().get_labels_from_table(SegmentTable, 'class_model_id')[0]]
        
        return labels
    
    
    def get_segment_ids_according_to_set_size(self, session, set_size, each_plot_set):
        if set_size == 'helix':
            each_helix_segments = session.query(SegmentTable).filter(SegmentTable.helix_id == each_plot_set.id).\
            order_by(SegmentTable.id).all()
        elif set_size == 'micrograph':
            each_helix_segments = session.query(SegmentTable).filter(SegmentTable.mic_id == each_plot_set.id).\
            order_by(SegmentTable.id).all()
        elif set_size == 'data_set':
            each_helix_segments = session.query(SegmentTable).order_by(SegmentTable.id).all()
            
        each_helix_stack_ids = [each_helix_segment.stack_id for each_helix_segment in each_helix_segments]
        
        return each_helix_stack_ids, each_helix_segments
    

    def generate_set_id_label_for_plot_and_filename(self, set_size, each_plot_set):
        if set_size == 'helix':
            each_set_id_label = 'helixid{0:05}_{1}'.format(each_plot_set.id, each_plot_set.helix_name)
        elif set_size == 'micrograph':
            each_set_id_label = 'micid{0:04}_{1}'.format(each_plot_set.id, each_plot_set.micrograph_name)
        elif set_size == 'data_set':
            each_set_id_label = 'dataset_all'
            
        return each_set_id_label
    

    def get_specified_quantities(self, each_plot_set_string, set_size, quantities, xy_quantities, each_helix_stack_ids,
    each_helix_segments, overlapping_segments):

        all_segments_included = np.array([True if each_helix_segment.stack_id in overlapping_segments \
                                         else False for each_helix_segment in each_helix_segments], dtype=bool)

        if quantities == 'coordinates':
            x_coord = np.array([each_helix_segment.x_coordinate_A for each_helix_segment in each_helix_segments])
            y_coord = np.array([each_helix_segment.y_coordinate_A for each_helix_segment in each_helix_segments])
            picked_x_coord = [each_helix_segment.picked_x_coordinate_A for each_helix_segment in each_helix_segments]
            picked_y_coord = [each_helix_segment.picked_y_coordinate_A for each_helix_segment in each_helix_segments]
            self.check_segmenting_values_and_raise_error(quantities, y_coord)
            
            x_coord[all_segments_included == False] = np.nan 
            y_coord[all_segments_included == False] = np.nan 
            xy_quantities.append((each_plot_set_string, np.vstack([each_helix_stack_ids, x_coord, y_coord,
            picked_x_coord, picked_y_coord])))
        else:
            distances = [each_helix_segment.distance_from_start_A for each_helix_segment in each_helix_segments]
            if quantities == 'in-plane_rotation':
                y_plot = [each_helix_segment.inplane_angle for each_helix_segment in each_helix_segments]
                self.check_segmenting_values_and_raise_error(quantities, y_plot)
            elif quantities == 'curvature':
                y_plot = [each_helix_segment.curvature for each_helix_segment in each_helix_segments]
                self.check_segmenting_values_and_raise_error(quantities, y_plot)
            elif quantities == 'defocus':
                y_plot = [each_helix_segment.avg_defocus for each_helix_segment in each_helix_segments]
                self.check_ctf_values_and_raise_error(quantities, y_plot)
            elif quantities == 'astigmatism':
                y_plot = [each_helix_segment.astigmatism for each_helix_segment in each_helix_segments]
                self.check_ctf_values_and_raise_error(quantities, y_plot)
                self.check_ctf_values_and_raise_error(quantities, y_plot)
            elif quantities == 'layer-line correlation':
                y_plot = [each_helix_segment.ccc_layer for each_helix_segment in each_helix_segments]
                self.check_layerline_values_and_raise_error(quantities, y_plot)
            elif quantities == 'classes':
                y_plot = [each_helix_segment.class_id for each_helix_segment in each_helix_segments]
                self.check_class_values_and_raise_error(quantities, y_plot)
            elif quantities == 'class_models':
                y_plot = [each_helix_segment.class_model_id for each_helix_segment in each_helix_segments]
                self.check_class_model_values_and_raise_error(quantities, y_plot)
                
            sel_y_plot = np.array(y_plot, dtype=float)
            if set_size == 'helix':
                sel_y_plot[all_segments_included == False] = np.nan

                xy_quantities.append((each_plot_set_string, np.vstack([each_helix_stack_ids, distances, y_plot,
                sel_y_plot])))
            elif set_size == 'data_set':
                each_helix_stack_ids = np.array(each_helix_stack_ids)
                sel_y_plot = sel_y_plot[all_segments_included == True]
                each_helix_stack_ids = each_helix_stack_ids[all_segments_included == True]
                xy_quantities.append((each_plot_set_string, np.vstack([each_helix_stack_ids, sel_y_plot])))
                
        return xy_quantities
    

    def prepare_log_string(self, labels, xy_quantities):
        msg = ''
        for each_helix, each_quant in xy_quantities:
            msg += ('\n' + tabulate(each_quant.T, labels))
        
        return msg


    def get_quantities_per_set(self, spring_path, quantities):
        self.log.fcttolog()
        shutil.copy(spring_path, 'spring.db')
        
        session, plot_sets = self.get_plot_set(self.set_size, self)

        self.curvature_range, self.ccc_layer_range = SegmentSelect().convert_curvature_ccc_layer_range('spring.db',
        self.straightness_selection, self.curvature_range_perc, self.ccc_layer_selection, self.ccc_layer_range_perc)
        
        combined_included_segments, excluded_segment_counts  = \
        SegmentSelect().filter_non_orientation_parameters_based_on_selection_criteria(self)
        
        labels = self.get_labels_according_to_quantities(self.set_size, quantities)
        xy_quantities = []
        for each_plot_set in plot_sets:
            each_helix_stack_ids, each_helix_segments = self.get_segment_ids_according_to_set_size(session,
            self.set_size, each_plot_set)
            
            if len(set(each_helix_stack_ids).intersection(combined_included_segments)) != 0:
                each_set_id_label = self.generate_set_id_label_for_plot_and_filename(self.set_size, each_plot_set)
                overlapping_segments = list(set(each_helix_stack_ids).intersection(combined_included_segments))
                
                xy_quantities = self.get_specified_quantities(each_set_id_label, self.set_size, quantities,
                xy_quantities, each_helix_stack_ids, each_helix_segments, overlapping_segments)
        
        msg = self.prepare_log_string(labels, xy_quantities)
        
        self.log.ilog('The following quantities have been extracted and will be plotted:\n{0}'.format(msg))
                    
        return labels, xy_quantities
    
    
class SegmentPlotVisualize(SegmentPlotPrepare):
    def determine_position_of_point_within_frame(self, frame_bottom_left, frame_top_right, x_quantity, y_quantity,
    x_lim, y_lim):
        """
        >>> from spring.segment2d.segmentplot import SegmentPlot
        >>> s = SegmentPlot()
        >>> x_quant = np.arange(5.0)
        >>> y_quant = np.arange(5.0, 10.0)
        >>> s.determine_position_of_point_within_frame([0.1, 0.2], [0.9, 0.8], x_quant, y_quant, (0.0, 4.0), (5.0, 9.0)) 
        (array([ 0.1,  0.3,  0.5,  0.7,  0.9]), array([ 0.2       ,  0.26666667,  0.33333333,  0.4       ,  0.46666667]))
        """
        x_quantity = np.array(x_quantity)
        y_quantity = np.array(y_quantity)
        
        scaled_x_quant = (x_quantity - x_lim[0]) / x_lim[-1]
        scaled_y_quant = (y_quantity - y_lim[0]) / y_lim[-1]
        
        adjusted_scaled_x_quant = frame_bottom_left[0] + scaled_x_quant * (frame_top_right[0] - frame_bottom_left[0]) 
        adjusted_scaled_y_quant = frame_bottom_left[1] + scaled_y_quant * (frame_top_right[1] - frame_bottom_left[1]) 
        
        return adjusted_scaled_x_quant, adjusted_scaled_y_quant
    
        
    def add_stack_ids_to_upper_x_axis(self, ax1, seg_ids, x_quantity, y_quantity, labels):
        ax11 = ax1.twiny()
        ax11.plot(x_quantity/x_quantity[1], y_quantity, '.', markersize=0.01)
        ax11.set_xlabel('Stack_id along helix', fontsize=8)
        ax1.set_xlim(min(x_quantity), max(x_quantity))
        ax11.set_xlim(min(seg_ids), max(seg_ids))
        if labels[-1].endswith('in-plane rotation angle (degrees)'.title()):
            ax1.set_ylim(0, 360)
            ax11.set_ylim(0, 360)
        elif labels[-1].endswith('out-of-plane rotation angle (degrees)'.title()):
            ax1.set_ylim(-max(abs(y_quantity)), max(abs(y_quantity)))
            ax11.set_ylim(-max(abs(y_quantity)), max(abs(y_quantity)))
        elif min(y_quantity) < max(y_quantity):
            ax1.set_ylim(min(y_quantity), max(y_quantity))
            ax11.set_ylim(min(y_quantity), max(y_quantity))
        
        return ax1, ax11
    

    def add_legend_at_best_location(self, ax1):
        ax1.legend(loc=0, ncol=1, prop=FontProperties(size='small'))
        
        return ax1


    def set_legend_and_xlabel(self, label, ax1):
        ax1 = self.add_legend_at_best_location(ax1)
        ax1.set_xlabel(label, fontsize=8)
        
        return ax1 
    

    def plot_xy_coordinates(self, labels, set_id_label, xy_data, fig):
        ax1 = fig.add_subplot(111)
        ax1.set_aspect('equal')
        ax1.apply_aspect()
        
        if xy_data.shape[0] == 5:
            seg_ids, x_coord, y_coord, picked_x_coord, picked_y_coord = np.split(xy_data.ravel(), xy_data.shape[0])
        elif xy_data.shape[0] == 7:
            seg_ids, x_coord, y_coord, picked_x_coord, picked_y_coord, sel_x_coord, sel_y_coord = \
            np.split(xy_data.ravel(), xy_data.shape[0])
        
        ax1.set_title('{0}{1}'.format(set_id_label[0].capitalize(), set_id_label[1:]))
        ax1.plot(x_coord, y_coord, '.', label=labels[1])
        ax1.plot(picked_x_coord.ravel(), picked_y_coord.ravel(), 'x', label=labels[3])
        if xy_data.shape[0] == 7: 
            ax1.plot(sel_x_coord, sel_y_coord, 'o', markerfacecolor='none', label=labels[5], fillstyle='bottom')
        ax1 = self.set_legend_and_xlabel(labels[1], ax1)
        ax1.set_xticks([min(min(picked_x_coord), min(x_coord)), max(max(picked_x_coord), max(x_coord))])
        ax1.set_yticks([min(min(picked_y_coord), min(y_coord)), max(max(picked_y_coord), max(y_coord))])
        [each_tick.set_fontsize(8) for each_tick in ax1.get_xticklabels() + ax1.get_yticklabels()]
        ax1.set_ylabel(labels[2], fontsize=8)

        return fig
    

    def add_avg_and_stdev_for_label(self, y_quantity):
        y_quantity = np.array(y_quantity)
        y_quantity = y_quantity[(y_quantity > 0) ^ (y_quantity <= 0)]
        avg_stdev = 'Mean: {0:.3}\nstdev: {1:.3}'.format(np.average(y_quantity), np.std(y_quantity))
        
        return avg_stdev
    

    def plot_y_histogram(self, labels, xy_data, set_size, fig):
        seg_ids, y_quantity = np.split(xy_data.ravel(), xy_data.shape[0])
        
        ax1 = fig.add_subplot(111)
        avg_std = self.add_avg_and_stdev_for_label(y_quantity)
        if min(y_quantity) < max(y_quantity):
            ax1.hist(y_quantity, bins=40, label=avg_std)
        [each_tick.set_fontsize(8) for each_tick in ax1.get_xticklabels() + ax1.get_yticklabels()]
        ax1 = self.set_legend_and_xlabel(labels[1], ax1)
        ax1.set_ylabel('Number of segments per {0}'.format(set_size))
        
        return fig


    def make_distance_plot_including_histogram(self, diag_plot, labels, seg_ids, xy_data, set_size, fig, x_quantity,
    y_quantity, sel_y_quantity):
        ax1 = diag_plot.plt.subplot2grid((2, 4), (0, 0), colspan=3, rowspan=2)
        ax1.plot(x_quantity, y_quantity, 'x', label=labels[2])
        if xy_data.shape[0] >= 4:
            ax1.plot(x_quantity, sel_y_quantity, 'o', markerfacecolor='none', label=labels[3])
        ax1.set_xlabel(labels[1], fontsize=8)
        ax1.set_ylabel(labels[2], fontsize=8)
        ax1 = self.set_legend_and_xlabel(labels[1], ax1)
        ax1, ax11 = self.add_stack_ids_to_upper_x_axis(ax1, seg_ids, x_quantity, y_quantity, labels)
        ax2 = diag_plot.plt.subplot2grid((2, 4), (0, 3), colspan=1, rowspan=2)
        if xy_data.shape[0] >= 4:
            avg_std = self.add_avg_and_stdev_for_label(sel_y_quantity)
        else:
            avg_std = self.add_avg_and_stdev_for_label(y_quantity)

        if min(y_quantity) < max(y_quantity):
            ax2.hist(y_quantity, bins=40, orientation='horizontal', label=avg_std)
        ax2.set_xlabel('Number of segments \nper {0}'.format(set_size), fontsize=8)
        ax2 = self.add_legend_at_best_location(ax2)
        ax2.set_ylim(ax1.get_ylim())
        ax2.set_yticks([])
        
        [each_tick.set_fontsize(8) for each_tick in ax1.get_xticklabels() + ax1.get_yticklabels() + \
        ax11.get_xticklabels() + ax2.get_xticklabels()]
        
        return ax1, ax2


    def plot_distance_along_y_including_local_average(self, diag_plot, labels, seg_ids, xy_data, set_size, fig):
        seg_ids, x_quantity, y_quantity, sel_y_quantity, avg_y_quantity = np.split(xy_data.ravel(), xy_data.shape[0])
        
        ax1, ax2 = self.make_distance_plot_including_histogram(diag_plot, labels, seg_ids, xy_data, set_size, fig,
        x_quantity, y_quantity, sel_y_quantity)
        
        ax1.plot(x_quantity, avg_y_quantity, ':', label=labels[-1])
        ax1 = self.add_legend_at_best_location(ax1)
        
        return fig
    
    
    def plot_distance_along_y(self, diag_plot, labels, seg_ids, xy_data, set_size, fig):
        if xy_data.shape[0] == 3:
            seg_ids, x_quantity, y_quantity = np.split(xy_data.ravel(), xy_data.shape[0])
            sel_y_quantity = None
        elif xy_data.shape[0] == 4:
            seg_ids, x_quantity, y_quantity, sel_y_quantity = np.split(xy_data.ravel(), xy_data.shape[0])
        
        self.make_distance_plot_including_histogram(diag_plot, labels, seg_ids, xy_data, set_size, fig, x_quantity,
        y_quantity, sel_y_quantity)
        
        return fig
    

    def choose_subplot_according_to_dimension(self, diag_plot, labels, set_id_label, segid_xy, set_size, fig):
        if segid_xy.shape[0] == 5 and not labels[-1].startswith('Local Average') or segid_xy.shape[0] == 7:
            fig = self.plot_xy_coordinates(labels, set_id_label, segid_xy, fig)
        elif segid_xy.shape[0] == 5 and labels[-1].startswith('Local Average'):
            fig = self.plot_distance_along_y_including_local_average(diag_plot, labels, set_id_label, segid_xy,
            set_size, fig)
        elif segid_xy.shape[0] == 3 or segid_xy.shape[0] == 4:
            fig = self.plot_distance_along_y(diag_plot, labels, set_id_label, segid_xy, set_size, fig)
        elif segid_xy.shape[0] == 2:
            fig = self.plot_y_histogram(labels, segid_xy, set_size, fig)
            
        return fig
            

    def print_progress_statement_if_interactive(self, xy_quantities, batch_mode):
        if not batch_mode:
            progress_statement = '{0} plots are being prepared before they can be browsed interactively.'.\
            format(len(xy_quantities))
            print progress_statement
            self.log.ilog(progress_statement)


    def plot_data_on_figure(self, xy_quantities, labels):
        self.log.fcttolog()
        self.print_progress_statement_if_interactive(xy_quantities, self.batch_mode)
        
        figures = []
        segmentplot_plot = DiagnosticPlot()
        self.log.plog(20)
        for quant_index, (each_set_id_label, each_segid_xy) in enumerate(xy_quantities):
            print each_set_id_label
            fig = segmentplot_plot.create_next_figure()
            
            filename = '{0}_{1}{2}'.format(os.path.splitext(self.outfile_prefix)[0],
            os.path.splitext(each_set_id_label)[0], os.path.splitext(self.outfile_prefix)[-1])
            
            if self.batch_mode:
                fig = segmentplot_plot.add_header_and_footer(self.feature_set, self.infile, filename)
        
            fig = self.choose_subplot_according_to_dimension(segmentplot_plot, labels, each_set_id_label,
            each_segid_xy, self.set_size, fig)
                    
            if self.batch_mode:
                fig.savefig(filename)
            elif not self.batch_mode:
                figures.append(fig)
            self.log.plog(70 * (quant_index + 1) / len(xy_quantities) + 20)
            self.log.ilog('{0}{1} plot was generated.'.format(each_set_id_label[0].capitalize(), each_set_id_label[1:]))
        
        return figures
            
            
class SegmentPlotGui(QWidget):

    def __init__(self, feature_set, figures, tables, labels, hints = None, parent = None):
        QWidget.__init__(self, parent)
        
        self = SpringCommon().setup_spring_page_top(self, feature_set)
        self.figures = figures
        self.tables = tables
        self.labels = labels
        
        self.graph_items = ['{0}{1}'.format(each_table[0][0].capitalize(), each_table[0][1:]) for each_table in tables]
        
        self.stackedComboBox = QComboBox()
        self.stackedComboBox.addItems(self.graph_items)
        if hints is not None:
            self.stackedComboBox.setToolTip(hints)
        self.layout.addWidget(self.stackedComboBox, 0, 3, 1, 1)
        
        self.stackedWidget = QStackedWidget()
        for each_plot_id, each_figure in enumerate(self.figures):
            self.splitter = QSplitter(Qt.Horizontal)
            self.data_table = SpringDataExploreTablePane(self.tables[each_plot_id][1], self.labels[each_plot_id])
            self.splitter.addWidget(self.data_table)
            self.figure = SpringDataExplore(self.figures[each_plot_id])
            self.splitter.addWidget(self.figure)
            
            self.stackedWidget.addWidget(self.splitter)
        
        self.connect(self.stackedComboBox, SIGNAL('currentIndexChanged(int)'), self.stackedWidget.setCurrentIndex)
        self.layout.addWidget(self.stackedWidget, 2, 0, 2, 5)
        
        self.setLayout(self.layout)
        
            
class SegmentPlot(SegmentPlotVisualize):
        
    def launch_interactive_plot_gui(self, feature_set, figures, tables, labels, hints=None):
        app = QApplication(sys.argv)
        symexplor = SegmentPlotGui(feature_set, figures, tables, labels, hints)
        symexplor.show()
        app.exec_()

        
    def plot_desired_quantities(self):
        labels, xy_quantities = self.get_quantities_per_set(self.infile, self.quantities)
        figures = self.plot_data_on_figure(xy_quantities, labels)
        if not self.batch_mode:
            all_labels = [labels for each_table in xy_quantities]
            self.launch_interactive_plot_gui(self.feature_set, figures, xy_quantities, all_labels)
        
        self.log.endlog(self.feature_set)
        
        
def main():
    # Option handling
    parset = SegmentPlotPar()
    mergeparset = OptHandler(parset)
    ######## Program
    stack = SegmentPlot(mergeparset)
    stack.plot_desired_quantities()

if __name__ == '__main__':
    main()
