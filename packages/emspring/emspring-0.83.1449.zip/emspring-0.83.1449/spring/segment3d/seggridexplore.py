# Author: Carsten Sachse 29-Aug-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to interactively explore grid searches according to different criteria
"""
from EMAN2 import EMData
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QApplication, QWidget, QStackedWidget, QPushButton, QComboBox, QSplitter, QTableWidget, \
    QFileDialog, QGridLayout
from functools import partial
from spring.csinfrastr.csdatabase import SpringDataBase, GridRefineTable, GridTable, grid_base
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.csgui import QTabWidgetCloseable
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import ExtLauncher
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from spring.springgui.springdataexplore import SpringDataExplore, SpringDataExploreTablePane, SpringDataExploreDraw, \
    SpringDataExplore3d, SpringCommon
from sqlalchemy.sql.expression import desc, asc
import numpy as np
import os
import shutil
import sys

class SegGridExplorePar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'       
        self.progname = 'seggridexplore'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.seggridexplore_features = Features()
        self.feature_set = self.seggridexplore_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()


    def define_parameters_and_their_properties(self):
        self.feature_set = self.seggridexplore_features.set_grid_database(self.feature_set, singular=False)
        self.feature_set = self.set_subgrid_merge_option(self.feature_set)
        self.feature_set = self.set_reconstitute_grid(self.feature_set)
        
        self.feature_set = self.seggridexplore_features.set_interactive_vs_batch_mode(self.feature_set)
        self.feature_set = self.set_file_prefix_symmetry_grid(self.feature_set)
        self.feature_set = self.set_parameter_pair_to_be_extracted(self.feature_set)
        
    def define_program_states(self):
        self.feature_set.program_states['extract_desired_em_files']='Extract desired EM files'
        self.program_states['launch_seggridexplore_gui']='Explore different grid combinations interactively'

    
    def set_file_prefix_symmetry_grid(self, feature_set):
        inp9 = 'EM name'
        feature_set.parameters[inp9]='recvol.hdf'
        feature_set.properties[inp9]=feature_set.file_properties(1,['hdf'],'saveFile')
        feature_set.hints[inp9]='Template output name for associated EM files from grid search: accepted image file ' +\
        'formats ({0})'.format(', '.join(feature_set.properties[inp9].ext))
        
        feature_set.level[inp9]='beginner'
        feature_set.relatives[inp9]='Batch mode'
        
        return feature_set
    
    
    def set_parameter_pair_to_be_extracted(self, feature_set):
        inp9 = 'Parameter pair'
        feature_set.parameters[inp9]=((1.408, 22.03))
        feature_set.properties[inp9] = feature_set.Range(-1000, 1000, 0.001)
        feature_set.hints[inp9]='Parameter pair to extract associated EM files.'
        feature_set.relatives[inp9]=(('Batch mode', 'Batch mode'))
        feature_set.level[inp9]='intermediate'
        
        return feature_set
    
    
    def set_subgrid_merge_option(self, feature_set):
        inp8 = 'Subgrid merge option'
        feature_set.parameters[inp8] = False
        feature_set.hints[inp8] = 'Merge subgrids from multiple grid searches. Either these subgrids were ' + \
        'generated using the subgrid option in segrefine3drid or they originate from adjacent grids with the ' + \
        'same grid spacing. Enter subgrids using wildcards * or ?? can be used to specify multiple input files.'
        feature_set.level[inp8]='expert'
        
        return feature_set
    
    
    def set_reconstitute_grid(self, feature_set):
        inp1 = 'Reconstitute Grid'
        feature_set.parameters[inp1]=bool(True)
        feature_set.hints[inp1]='In case subgrids are merged reconstitute entire grid by reproducing directory tree ' + \
        'in one place and generate symbolic links to associated original files.'
        feature_set.relatives[inp1]='Subgrid merge option'
        feature_set.level[inp1]='expert'

        return feature_set
    
    
class SegGridExplorePreparation(object):
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters
            
            self.grid_database = p['Grid database']
            self.infile = self.grid_database
            self.outfile = p['EM name']
            self.batch_mode = p['Batch mode']
            self.parameter_pair = p['Parameter pair']
            self.reconstitute_grid = p['Reconstitute Grid']
            
            self.subgrid_merge = p['Subgrid merge option']
            if self.subgrid_merge:
                self.subgrid_files = Features().convert_list_of_files_from_entry_string(self.grid_database)


class SegGridExploreSupport(object):
    def convert_None2nan(self, x):
        """
        Converts None objects to nan, for use in
        NumPy arrays. Returns an array.
        >>> from spring.segment3d.seggridexplore import SegGridExploreSupport
        >>> SegGridExploreSupport().convert_None2nan(5*[None])
        [nan, nan, nan, nan, nan]
        """
        newlist = []
        for i in x:
            if i is not None:
                newlist.append(i)
            else:
                newlist.append(np.nan)
             
        return newlist
    

    def get_general_grid_parameters(self, grid_file):
        grid_session = SpringDataBase().setup_sqlite_db(grid_base, grid_file)
        grid_combinations = grid_session.query(GridRefineTable).order_by(asc(GridRefineTable.id)).all()
        grid_parameters = grid_session.query(GridTable).filter(GridTable.id == grid_combinations[0].grid_id).first()
        
        return grid_session, grid_combinations, grid_parameters
    

    def get_rises_and_rotations_and_entered_symmetry_grid(self, grid_combinations):
        rise_or_pitches = np.array([each_grid_combination.primary_value for each_grid_combination in grid_combinations])
         
        rotation_or_unit_numbers = np.array([each_grid_combination.secondary_value for each_grid_combination in \
        grid_combinations])
         
        entered_symmetry_grid = SegClassReconstruct().convert_rise_rotation_or_pitch_unitnumber_series_to_grid_of_tuples\
        (np.unique(rise_or_pitches), np.unique(rotation_or_unit_numbers))
 
        return rise_or_pitches, rotation_or_unit_numbers, entered_symmetry_grid


    def get_all_attr_from_search_result(self, all_grid_combinations, db_attr, filtered_attr, grid_data, zlabels, table):
        list_of_val = [getattr(each_grid_combination, db_attr) for each_grid_combination in \
        all_grid_combinations]
        
        if set(list_of_val) != set([None]):
            conv_values = self.convert_None2nan(list_of_val)
            grid_data.append(conv_values)
            
            zlabels += SpringDataBase().get_labels_from_table(table, db_attr)
            filtered_attr += [db_attr]
            
        return grid_data, zlabels, filtered_attr


    def get_common_criterias(self):
        return ['fsc_0143', 'fsc_05', 'xshift_error', 'inplane_error', 'outofplane_error', 'mean_peak', 
                          'amp_corr_quarter_nyquist', 'amp_corr_half_nyquist', 'amp_corr_3quarter_nyquist', 
                          'amp_correlation', 'helical_ccc_error', 'mean_helical_ccc', 
                          'variance', 'asym_unit_count', 'avg_azimuth_sampling', 'dev_azimuth_sampling']
                          
        
    def get_criterias(self):
        additional_criteria = ['phase_residual', 'diff_noise_ccc', 'diff_noise_amp_ccc', 'cross_correlation', 
        'diff_noise_pr','excluded_inplane_ratio', 'excluded_out_of_plane_ratio', 'excluded_total_ratio', 
        'noise_ccc', 'noise_amp_ccc', 'noise_pr']
         
        combined_criteria = self.get_common_criterias() + additional_criteria
        return combined_criteria
    
        
    def get_grid_information_from_database(self, grid_file):
        grid_session, grid_combinations, grid_parameters = self.get_general_grid_parameters(grid_file)
        
        rise_or_pitches, rotation_or_unit_numbers, grid_pairs = \
        self.get_rises_and_rotations_and_entered_symmetry_grid(grid_combinations)
        
        grid_data = []
        zlabels = []
        filtered_attr = []
        for each_attr in self.get_criterias():
            grid_data, zlabels, filtered_attr = self.get_all_attr_from_search_result(grid_combinations, each_attr,
            filtered_attr, grid_data, zlabels, GridRefineTable)
            
        if len(grid_data[0]) < (grid_pairs.shape[0] * grid_pairs.shape[1]):
            msg = 'The provided grid.db contains less data than expected from the grid parameters. ' + \
            'Double-check whether all grid runs finished successfully.'
            raise ValueError(msg)

        grid_data = [np.array(each_grid).reshape((grid_pairs.shape)) for each_grid in grid_data]
        
        files = [each_grid_combination.em_files_2d for each_grid_combination in grid_combinations]
        files_2d = [files for each_grid_data in grid_data]
        files = [each_grid_combination.em_files_3d for each_grid_combination in grid_combinations]
        files_3d = [files for each_grid_data in grid_data]
        
        last_grid = grid_session.query(GridTable).order_by(desc(GridTable.id)).first()
        xlabels = [last_grid.primary_variable for each_grid_data in grid_data]
        ylabels = [last_grid.secondary_variable for each_grid_data in grid_data]
        
        zxy_labels = zip(zlabels, xlabels, ylabels)
        grid_pairs = [grid_pairs for each_grid in grid_data]
        
        hints = SpringDataBase().get_hints_from_grid_table(filtered_attr)
        
        return grid_data, grid_pairs, zxy_labels, files_2d, files_3d, hints
        

class SegGridExploreGuiPane(QWidget):

    def __init__(self, grid, grid_pairs, zxy_labels, files_2d, files_3d, parent = None):
        QWidget.__init__(self, parent)
        
        self.tabWidget = QTabWidgetCloseable()

        self.grid = grid
        self.grid_pairs = grid_pairs
        self.zxy_labels = zxy_labels
        self.files_2d = files_2d
        self.files_3d = files_3d
        
        self.layout = QGridLayout()
        if self.grid.shape[0] == 1 or self.grid.shape[-1] == 1:
            self.add_1d_plot(((0, 0)), self.zxy_labels[1])
        else:
            self.setup_matrix_image_plot()
        
        self.table_matrix = self.prepare_table_matrix_from_symmetry_grid_pairs(self.grid, self.grid_pairs)
        self.table_pane = SpringDataExploreTablePane(self.table_matrix, ['GridID'] + list(self.zxy_labels)) 
        self.table_pane.data_table.primary_id_signal.connect(partial(self.launch_external_viewer_from_index))
        self.table_pane.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_pane.data_table.setToolTip('Open connected data point by clicking on beginning of row.')

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.table_pane)
        self.splitter.addWidget(self.tabWidget)
        
        self.layout.addWidget(self.splitter, 0, 0, 2, 5)
        self.setLayout(self.layout)

        self.external_launcher = ExtLauncher()
        

    def setup_matrix_image_plot(self):
        self.seggridexplore2d_tab = SpringDataExplore()
        self.seggridexplore2d_tab.on_draw(np.array(self.grid), self.grid_pairs, self.zxy_labels, '2d')
        self.seggridexplore2d_tab.picked_left_point.connect(partial(self.launch_external_viewers_from_index_pair))
        self.seggridexplore2d_tab.picked_middle_point.connect(partial(self.add_additional_1d_tab))
        
        self.seggridexplore2d_tab.main_frame.setToolTip('Left mouse button to open associated reprojections and ' + \
        'power spectrum (and reconstruction if provided).\nMiddle mouse button to open 1D profile of associated ' + \
        '{rise_pitch} and {rot_number}.'.format(rise_pitch=self.zxy_labels[1], rot_number=self.zxy_labels[2]))
        
        self.tabWidget.addTab(self.seggridexplore2d_tab, '2D grid')
        self.button3d = QPushButton()
        self.button3d.setText('Explore3d')
        self.connect(self.button3d, SIGNAL('clicked()'), self.add_3d_surface_tab)
        self.pull_down3d = QComboBox()
        self.pull_down3d.addItems(['Visvis (fast)', 'Matplotlib (slow)'])
        
        self.pull_down3d.setToolTip('Choose between fast PyOpenGL (visvis) display with less navigation options ' + \
        'for large data grids or \nslow display with many navigation options for small data grids (matplotlib)')
        
        self.layout.addWidget(self.pull_down3d, 2, 3, 1, 1)
        self.layout.addWidget(self.button3d, 2, 4, 1, 1)


    def get_corresponding_symmetry_pair_from_picked_indices(self, index_pair):
        x_index, y_index = index_pair
        symmetry_pair = self.grid_pairs[int(y_index)][int(x_index)]
#        print index_pair, symmetry_pair
        
        return symmetry_pair, x_index, y_index


    def add_1d_plot(self, index_pair, symmetry_pair):
        self.seggridexplore1d_tab = SpringDataExplore()
        self.seggridexplore1d_tab.on_draw(self.grid, self.grid_pairs, self.zxy_labels, '1d', index_pair)
        
        self.tabWidget.addTab(self.seggridexplore1d_tab, '1D: ' + \
        '{0}'.format(symmetry_pair.__str__().strip(')').strip('(')))
        
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.seggridexplore1d_tab))
        self.seggridexplore1d_tab.picked_left_point.connect(partial(self.launch_external_viewers_from1d))
        self.seggridexplore1d_tab.picked_label.connect(partial(self.define_labels_for_1d_profile))
        self.seggridexplore1d_tab.index_2d.connect(partial(self.define_2d_index_for_1d_profile))


    def add_additional_1d_tab(self, index_pair):
        symmetry_pair, x_index, y_index = self.get_corresponding_symmetry_pair_from_picked_indices(index_pair)
        self.add_1d_plot(index_pair, symmetry_pair)
        
        
    def add_3d_surface_tab(self):
        temp, helical_rotations = list(zip(*self.grid_pairs[0,].tolist()))
        helical_rises, temp = list(zip(*self.grid_pairs[:,0].tolist()))
        
        helical_rotations, helical_rises = np.meshgrid(helical_rotations, helical_rises)
        
        xyz_data = np.hstack([helical_rises.reshape(helical_rises.size, 1), 
                              helical_rotations.reshape(helical_rotations.size, 1), 
                              self.grid.reshape(self.grid.size, 1)])
        
        if str(str(self.pull_down3d.currentText())) == 'Visvis (fast)':
            self.seggridexplore3d_tab = SpringDataExplore3d(xyz_data, self.zxy_labels)
            self.tabWidget.addTab(self.seggridexplore3d_tab, '3D surface (vv)')
            
        elif str(str(self.pull_down3d.currentText())) == 'Matplotlib (slow)':
            self.seggridexplore3d_tab = SpringDataExplore()
            self.seggridexplore3d_tab.on_draw(self.grid, self.grid_pairs, self.zxy_labels, '3d')
            self.tabWidget.addTab(self.seggridexplore3d_tab, '3D surface (mpl)')
            
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.seggridexplore3d_tab))
        
    
    def define_labels_for_1d_profile(self, label):
        self.label = label
#        print label
        
    def define_2d_index_for_1d_profile(self, index_pair):
        self.index_2dpair = index_pair
#        print index_pair
        
        
    def launch_external_viewers_from1d(self, picked_pair_from1d):
#        print(picked_pair_from1d)
        helical_rises, helical_rotations = \
        SpringDataExploreDraw().extract_rise_rotation_from_symmetry_grid(self.grid_pairs)
        
        if self.label == self.zxy_labels[1]:
            previous_rotation_index = self.index_2dpair[0]
            adjusted_rise = picked_pair_from1d[0] 
            
            matched_indices = np.where(np.array(helical_rises) == adjusted_rise)
            
            y_index = matched_indices[0][0]
            x_index = int(previous_rotation_index)
        
        elif self.label == self.zxy_labels[2]:
            previous_rise_index = self.index_2dpair[1]
            adjusted_rotation = picked_pair_from1d[0] 
            
            matched_indices = np.where(np.array(helical_rotations) == adjusted_rotation)
            
            y_index = int(previous_rise_index)
            x_index = matched_indices[0][0]
        
        stack_index = self.get_stack_index_from_rise_and_rotation_index(x_index, y_index)
        
        self.launch_external_viewers(stack_index)
        
        
    def launch_external_viewers(self, index):
        if self.files_2d[index] is not None:
            img = EMData()
                
            if not hasattr(self, 'opened'):
                self.opened = []
            else:
                [os.remove(each_opened) for each_opened in self.opened]
                self.opened = []
            
            for (each_file, stack_id) in self.files_2d[index]:
                if each_file.endswith('hdf'):
                    print each_file, stack_id
                    img.read_image(each_file, stack_id)
                    file_name = '{0}_{1:05}{2}'.format(os.path.splitext(each_file)[0], stack_id, os.path.splitext(each_file)[1])
                    img.write_image(file_name)
                    self.external_launcher.qlaunch_open_file(os.path.abspath(file_name))
                    self.opened.append(file_name)
                else:
                    self.external_launcher.qlaunch_open_file(each_file)
        
        if self.files_3d[index] is not None:
            self.external_launcher.qlaunch_open_file(self.files_3d[index][0])
            
    
    def launch_external_viewer_from_index(self, stack_index):
        self.launch_external_viewers(stack_index)


    def launch_external_viewers_from_index_pair(self, index_pair):
        x_index, y_index = index_pair
        stack_index = self.get_stack_index_from_rise_and_rotation_index(x_index, y_index)
        
        self.launch_external_viewers(stack_index)
        
        
    def get_stack_index_from_rise_and_rotation_index(self, x_index, y_index):
        x_count, y_count = self.grid_pairs.shape
        stack_index = int(x_index + y_count * y_index)
        
        return stack_index
    
    
    def exitApp(self):
        self.close()


    def prepare_table_matrix_from_symmetry_grid_pairs(self, symmetry_grid_np, symmetry_grid_pairs):
    
        sym_id = np.arange(symmetry_grid_np.size)
        symmetry_grid_cc_seq = symmetry_grid_np.ravel()
        rises_seq, rotation_seq = list(zip(*symmetry_grid_pairs.ravel()))
        
        table_matrix = np.vstack([sym_id, symmetry_grid_cc_seq, rises_seq, rotation_seq])
        
        return table_matrix
        

class SegGridExploreGui(SegGridExploreSupport, QWidget):
    def __init__(self, feature_set, parent = None):
        QWidget.__init__(self, parent)
        
        self.feature_set = feature_set
        self.properties = feature_set.properties
#        self.grid_database = self.feature_set.parameters['Grid database']
        self.grid_database = 'grid.db'
        
        self = SpringCommon().setup_spring_page_top(self, feature_set)
        
        self.grids, self.grid_pairs, self.zxy_labels, self.files_2d, self.files_3d, hints = \
        self.get_grid_information_from_database(self.grid_database)
        
        self.stackedPane = QStackedWidget()
        self.currentPaneIndex = 0
        self.panes = []
        for pane_id, each_grid in enumerate(self.grids):
            self.pane = SegGridExploreGuiPane(self.grids[pane_id], self.grid_pairs[pane_id], self.zxy_labels[pane_id],
            self.files_2d[pane_id], self.files_3d[pane_id])
            
            self.stackedPane.addWidget(self.pane)
            self.panes.append(self.pane)
        self.layout.addWidget(self.stackedPane, 1, 0, 2, 5)
        self.stackedPane.setCurrentIndex(self.currentPaneIndex)
        
        self.z_labels = [each_label[0] for each_label in self.zxy_labels ]

        self.pull_down_panes = QComboBox() 
        self.pull_down_panes.addItems(self.z_labels)
        self.pull_down_panes.setToolTip(hints)
        self.connect(self.pull_down_panes, SIGNAL('currentIndexChanged(int)'), self.update_panes)
        self.layout.addWidget(self.pull_down_panes, 0, 3, 1, 1)
        
        self.pull_down_pairs = QComboBox()
        self.items = []
        for each_grid in self.grid_pairs:
            self.items.append([ 'Grid ID:{0}: {1}'.format(each_grid_id, str(each_pair).strip(')').strip('(')) for \
            each_grid_id, each_pair in enumerate(each_grid.ravel())])
            
        self.pull_down_pairs.addItems(self.items[self.currentPaneIndex])
        self.layout.addWidget(self.pull_down_pairs, 3, 3, 1, 1)
        
        self.save_button = QPushButton()
        self.save_button.setText('Save')
        self.save_button.setToolTip('Save associated EM files.')
        self.save_button.setShortcut('Ctrl+S')
        self.connect(self.save_button, SIGNAL('clicked()'), self.saveEmFile)
        
        self.layout.addWidget(self.save_button, 3, 4, 1, 1)
        
        self.setLayout(self.layout)
        
        
    def update_panes(self, value):
        self.currentPaneIndex = value
        self.stackedPane.setCurrentIndex(self.currentPaneIndex)
        
        
    def saveEmFile(self):
        fname = str(QFileDialog.getSaveFileName(self , 'Save EM file', '.', 'Files ({0})'.\
        format('*.' + ' *.'.join(self.properties.values()[1].ext)))) 
        
        index = self.pull_down_pairs.currentIndex()
        files = self.files_2d[self.currentPaneIndex][index]
        img = EMData()
        for each_file_id, (each_file_name, each_stack_id) in enumerate(files):
            img.read_image(each_file_name, each_stack_id)
            img.write_image(os.path.splitext(fname)[0] + '2d' + os.path.splitext(fname)[-1], each_file_id)
            
        volume_name = self.files_3d[self.currentPaneIndex][index][0]
        if volume_name is not None:
            img.read_image(volume_name)
            img.write_image(os.path.splitext(fname)[0] + '3d' + os.path.splitext(fname)[-1])
            
        
class SegGridExploreMerge(SegGridExplorePreparation):

    def perform_simple_additive_merge(self, sorted_subgrid_files):
        merged_session = SpringDataBase().setup_sqlite_db(grid_base, 'grid.db')
        for each_subgrid_id, each_subgrid_file in enumerate(sorted_subgrid_files):
            each_grid = SpringDataBase().setup_sqlite_db(grid_base, each_subgrid_file)
            if each_subgrid_id == 0:
                merged_session = SpringDataBase().copy_all_table_data_from_one_session_to_another_session(GridTable,
                merged_session, each_grid, merge_ids=True)

            merged_session = SpringDataBase().copy_all_table_data_from_one_session_to_another_session(GridRefineTable,
            merged_session, each_grid, merge_ids=True)
        
        merged_session.commit()
        
        return merged_session
    

    def check_whether_seamless_grid_merging_is_possible(self, primary_min, primary_max, primary_inc):
        """
        >>> from spring.segment3d.seggridexplore import SegGridExplore
        >>> s = SegGridExplore()
        >>> s.check_whether_seamless_grid_merging_is_possible([16.25, 16.36], [16.35, 16.45], [0.01])
        >>> s.check_whether_seamless_grid_merging_is_possible([16.25, 16.38], [16.35, 16.45], [0.01])
        Traceback (most recent call last):
          File '/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/doctest.py', line 1254, in __run
            compileflags, 1) in test.globs
          File '<doctest spring.segment3d.seggridexplore.SegGridExploreMerge.check_whether_seamless_grid_merging_is_possible[3]>', line 1, in <module>
            s.check_whether_seamless_grid_merging_is_possible([16.25, 16.38], [16.35, 16.45], [0.01])
          File '/Users/sachse/Documents/en_casa/EMBL/08_python/26_springbox/develop-eggs/spring-dev/spring/segment3d/seggridexplore.py', line 517, in check_whether_seamless_grid_merging_is_possible
            raise ValueError(msg)
        ValueError: You have specified grid datbases to be merged that can not be merged seamlessly without gaps into a continuous grid.

        """
        primary_min = [abs(each_min) for each_min in list(primary_min)]
        primary_max = [abs(each_max) for each_max in list(primary_max)]
        primary_inc = [abs(each_inc) for each_inc in  list(primary_inc)]
        
        primary_min.sort()
        primary_max.sort()
        for each_ext_id, each_max in enumerate(primary_max[:-1]):
            next_min = primary_min[each_ext_id + 1]
            computed_next_min = each_max + primary_inc[0]
            if abs(computed_next_min - next_min) > primary_inc[0]/100.0:
                msg = 'You have specified grid datbases to be merged that can not be merged seamlessly without ' + \
                'gaps into a continuous grid.'
                
                raise ValueError(msg)
            

    def update_new_grid_min_and_max_after_merge(self, primary_min, primary_max, second_min, second_max, merged_session):
        grid = merged_session.query(GridTable).first()
        grid.primary_min = min(primary_min)
        grid.primary_max = max(primary_max)
        grid.second_min = min(second_min)
        grid.second_max = max(second_max)
        merged_session.merge(grid)
        
        merged_session.commit()
        
        return merged_session
    

    def merge_grids_from_files(self, sorted_subgrid_files, primary_min, primary_max, second_min, second_max,
    primary_inc, second_inc, same_increments):
    
        same_max_and_mins = len(primary_min) + len(primary_max) + len(second_min) + len(second_max)
        if same_max_and_mins == 4 and same_increments == 2:
            merged_session = self.perform_simple_additive_merge(sorted_subgrid_files)
        if not same_max_and_mins == 4 and same_increments == 2:
            if 0 in second_inc or 0 in primary_inc:
                pass
            else:
                self.check_whether_seamless_grid_merging_is_possible(primary_min, primary_max, primary_inc)
                self.check_whether_seamless_grid_merging_is_possible(second_min, second_max, second_inc)
            merged_session = self.perform_simple_additive_merge(sorted_subgrid_files)
            merged_session = self.update_new_grid_min_and_max_after_merge(primary_min, primary_max, second_min, 
                second_max, merged_session)
            
            os.rename('grid.db', 'grid_not_sorted.db')
            tmp_session = SpringDataBase().setup_sqlite_db(grid_base, 'grid_not_sorted.db')
            
            grid = tmp_session.query(GridRefineTable).\
            order_by(GridRefineTable.primary_value.asc()).\
            order_by(GridRefineTable.secondary_value.asc()).all()
            
            shutil.copy('grid_not_sorted.db', 'grid.db')
            merged_session = SpringDataBase().setup_sqlite_db(grid_base, 'grid.db')
            columns = SpringDataBase().get_columns_from_table(GridRefineTable)
            for each_grid_id, each_grid_point in enumerate(grid):
                data = SpringDataBase().get_data_from_entry(columns, each_grid_point)
                data['id'] = each_grid_id + 1
                merged_session.merge(GridRefineTable(**data))
            
            merged_session.commit()
            os.remove('grid_not_sorted.db')
            
        return merged_session
    

    def merge_subgrids_into_single_grid_file(self, subgrid_files):
        split_files = [os.path.split(each_file)[-1] for each_file in subgrid_files]
        sorted_subgrid_files = [subgrid_files[each_ind] for each_ind in np.argsort(split_files)]
        
        file_grid_parameters = []
        
        for each_subgrid_file in sorted_subgrid_files:
            each_grid = SpringDataBase().setup_sqlite_db(grid_base, each_subgrid_file)
            grid_entries = each_grid.query(GridTable).first()
            file_grid_parameters.append(grid_entries)
        
        primary_var = set([each_file_grid.primary_variable for each_file_grid in file_grid_parameters])
        secondary_var = set([each_file_grid.secondary_variable for each_file_grid in file_grid_parameters])
        primary_min = set([each_file_grid.primary_min for each_file_grid in file_grid_parameters])
        primary_max = set([each_file_grid.primary_max for each_file_grid in file_grid_parameters])
        second_min = set([each_file_grid.second_min for each_file_grid in file_grid_parameters])
        second_max = set([each_file_grid.second_max for each_file_grid in file_grid_parameters])
        primary_inc = set([each_file_grid.primary_inc for each_file_grid in file_grid_parameters])
        second_inc = set([each_file_grid.second_inc for each_file_grid in file_grid_parameters])
            
        same_variables = len(primary_var) + len(secondary_var)
        same_increments = len(primary_inc) + len(second_inc)
        for each_inc in list(primary_inc) + list(second_inc):
            if each_inc == 0:
                same_variables = 2
                same_increments = 2
        
        entities = []
        if not same_variables == 2:
            entities.append('variables')
        if not same_increments == 2:
            entities.append('increments')
            
        if not same_variables == 2 or not same_increments == 2:
            msg = ''
            for each_entity in entities:
                msg += 'You have specified grid databases to be merged that do not match in their primary or ' + \
                'secondary {0}. This way they cannot be merged. Double-check the specified files. '.format(each_entity)
            raise ValueError(msg)
        
        merged_session = self.merge_grids_from_files(sorted_subgrid_files, primary_min, primary_max, second_min,
        second_max, primary_inc, second_inc, same_increments)
             
        return merged_session
    
    
    def write_symbolic_links_to_have_merged_data_in_one_place(self, grid_session):
        grid_points = grid_session.query(GridRefineTable).all()
        
        for each_grid_point in grid_points:
            for each_entry in each_grid_point.em_files_2d + each_grid_point.em_files_3d: 
                if type(each_entry) is tuple:
                    each_file = each_entry[0]
                else:
                    each_file = each_entry 
                    
                local_dir = os.path.split(os.path.dirname(each_file))[-1]
                if not os.path.isdir(local_dir):
                    os.mkdir(local_dir)
                os.chdir(local_dir)
                os.symlink(os.path.relpath(each_file), os.path.basename(each_file))
                os.chdir(os.pardir)
        
    
class SegGridExplore(SegGridExploreMerge):
    def launch_seggridexplore_gui(self, feature_set):
        self.log.fcttolog()
        app = QApplication(sys.argv)
        gridexplor = SegGridExploreGui(feature_set)
        gridexplor.show()
        app.exec_()

    
    def extract_desired_em_files(self):
        self.log.fcttolog()
        
        grids, grid_pairs, zxy_labels, files_2d, files_3d, hints = \
        SegGridExploreSupport().get_grid_information_from_database(self.grid_database)
        
        vol = EMData()
        for each_index, each_grid_pair in enumerate(grid_pairs[0].ravel()):
            if each_grid_pair == self.parameter_pair:
                vol.read_image(files_3d[0][each_index][0])
                
                outfile = '{0}{1:04}{2}'.format(os.path.splitext(self.outfile)[0], each_index,
                os.path.splitext(self.outfile)[-1])
                
                vol.write_image(outfile)
            self.log.plog(90 * (each_index + 1) / len(grid_pairs[0].ravel()) + 10)
                
                
    def launch_seggridexplore(self):
        if self.subgrid_merge:
            grid_session = self.merge_subgrids_into_single_grid_file(self.subgrid_files)
            if self.reconstitute_grid:
                self.write_symbolic_links_to_have_merged_data_in_one_place(grid_session)
        else:
            shutil.copy(self.grid_database, 'grid.db')
            
        self.log.plog(10)
        if not self.batch_mode:
            self.launch_seggridexplore_gui(self.feature_set)
        else:
            self.extract_desired_em_files()
        
        self.log.endlog(self.feature_set)
        
def main():
    # Option handling
    parset = SegGridExplorePar()
    mergeparset = OptHandler(parset)

    ######## Program
    sseg = SegGridExplore(mergeparset)
    sseg.launch_seggridexplore()

if __name__ == '__main__':
    main()
