# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import EMNumPy
from PyQt4.QtCore import Qt, SIGNAL, SLOT, QThread
from PyQt4.QtGui import QWidget, QSplitter, QSlider, QGridLayout, QLabel, QPushButton, QDoubleSpinBox, QFileDialog, \
    QComboBox, QStackedWidget, QCheckBox
from collections import namedtuple
from filter import filt_table
from fundamentals import ccfnpl, mirror
from spring.csinfrastr.csdatabase import SpringDataBase, refine_base, RefinementCycleTable
from spring.csinfrastr.csgui import NumbersOptionsGuiWindow
from spring.csinfrastr.csproductivity import ExtLauncher
from spring.segment2d.segmentalign2d import SegmentAlign2d
from spring.segment3d.refine.sr3d_main import SegmentRefine3d
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from spring.springgui.springdataexplore import SpringCommon, SpringDataExplore
from sqlalchemy.sql.expression import desc
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import os


class SegRefine3dInspectCommonOperations(object):
    def convert_helical_symmetry_from_pitch_unit_number_to_rise_rotation(self, rise_or_pitch_choice, helical_symmetry):
        if rise_or_pitch_choice == 'pitch/unit_number':
            pitch, unit_number = helical_symmetry
            helical_symmetry = SegClassReconstruct().convert_pitch_unit_pair_to_rise_rotation_pairs(pitch, unit_number)
        
        return helical_symmetry
    

    def make_volume_collection_named_tuple(self):
        volume_collection = namedtuple('volumes', 'original layer cylinder_mask structural_mask')
        
        return volume_collection


    def apply_bfactor_and_resolution_cutoff(self, vol, bfactor, res_cutoff, pixelsize, fsc_line):
        volume_size = vol.get_xsize()

        filter_coefficients = SegmentAlign2d().prepare_bfactor_coefficients(bfactor, pixelsize, volume_size, res_cutoff)
        if fsc_line is not None:
            filter_coefficients *= np.sqrt(2 * fsc_line / (1 + fsc_line))
        
        vol = filt_table(vol, filter_coefficients.tolist())
        
        return vol
    

    def read_columns_from_text_file(self, fsc_file):
        f = open(fsc_file, 'r')
        fsc_line = []
        for each_row, each_line in enumerate(f.readlines()):
            if each_row == 0 and not each_line.strip().startswith('resolution') or \
            each_row == 1 and not each_line.strip().startswith('----------'):
                msg = 'This is not an FSC file generated from segmentrefine3d. Header is not recognized.'
                raise ValueError(msg)
            elif each_row > 1:
                fsc_line.append(float(each_line.split()[2]))
        
        return fsc_line


    def read_fsc_from_refinement_db(self, fsc_file):
        ref_session = SpringDataBase().setup_sqlite_db(refine_base, fsc_file)
        
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
        
        return last_cycle.fsc


    def read_fsc_line_from_file(self, fsc_file, vol_size):
        if fsc_file.endswith('dat'):
            fsc_line = self.read_columns_from_text_file(fsc_file)
        elif fsc_file.endswith('db'):
            fsc_line = self.read_fsc_from_refinement_db(fsc_file)
        
        fsc_line = np.abs(fsc_line)
        if len(fsc_line) == vol_size / 2 + 1:
            fsc_line = np.array(fsc_line[1:])
        
        if len(fsc_line) != vol_size / 2:
            msg = 'Dimension of volume and number of fsc line values do not agree. Please double check whether ' + \
            'files are from the same cycle of segmentrefine3d.'
            raise ValueError(msg)
        
        return fsc_line

            
    def prepare_long_helix(self, vol, helix_length, helixwidth, pixelsize, helical_symmetry, rotational_symmetry,
    polar_helix):
        xy_size = int(round(1.2 * helixwidth / pixelsize, -1))
        z_size = int(round(helix_length / pixelsize, -1))

        point_symmetry = SegClassReconstruct().determine_point_group_symmetry_from_input(polar_helix, 
        rotational_symmetry)

        vol = SegmentRefine3d().generate_long_helix_volume(vol, xy_size, z_size, helical_symmetry, 
        pixelsize, point_symmetry)
        
        return vol
        

class SegRefine3dInspectGuiSliceView(QWidget, QThread):
    def __init__(self, volume, plane, label, figure_no, parent = None):
        QWidget.__init__(self, parent) 
        QThread.__init__(self, parent) 
        
        self.volume = volume
        self.slice_plane = plane
        self.label = label
        self.figure_no = figure_no
    
        self.layout = QGridLayout()
        
        self.fig = self.build_initial_slice_fig()
        self.canvas = SpringDataExplore(self.fig)
        self.layout.addWidget(self.canvas, 0, 0, 1, 3)
        
        self.setLayout(self.layout)
        
    
    def build_initial_slice_fig(self):
        self.fig = plt.figure(self.figure_no)
        self.ax = self.fig.add_subplot(111)
        self.slice_no_z = self.volume.shape[0]/2
        self.slice = self.ax.imshow(self.volume[:,self.slice_no_z], cmap=cm.jet, origin='upper')
        
        cax = self.fig.add_axes()
        cbar = self.fig.colorbar(self.slice, cax)
        cbar.set_label('Density (normalized)')

        if self.label in ['Radius (Angstrom)', 'Theta (degrees)', 'Z distance (Angstrom)']:
            self.slice.set_clim(self.volume[self.slice_no_z].min(), self.volume[self.slice_no_z].max())
        else:
            self.slice.set_clim(self.volume[:,self.slice_no_z].min(), self.volume[:,self.slice_no_z].max())
#        self.slice = self.ax.imshow(self.volume[self.slice_no_z], interpolation='nearest', cmap=cm.gray, origin='lower')

        return self.fig
    
        
class SegRefine3dInspectGuiSlice(QWidget, QThread):
    def __init__(self, volume, label, figure_no, parent = None):
        QWidget.__init__(self, parent)
        QThread.__init__(self, parent)
    
        self.volume = volume
        self.label = label
        self.figure_no = figure_no
        
        self.build_three_slice_planes()
        self.setLayout(self.layout)
        
    def build_autocorr_volume(self):
        self.auto_volume = np.zeros(self.volume.shape)
        x_count, y_count = self.volume[:,:,0].shape
        for each_x_plane in list(range(x_count)):
            z_slice = EMNumPy.numpy2em(np.copy(self.volume[:,each_x_plane]))
#            ccfnpl(z_slice, z_slice).write_image('autocorr.hdf', each_x_plane)
            slice_auto = np.copy(EMNumPy.em2numpy(ccfnpl(z_slice, z_slice)))
            
            self.auto_volume[:,each_x_plane]=slice_auto
            
        return self.auto_volume
    
            
    def build_three_slice_planes(self):
        self.layout = QGridLayout()
        self.label_field = QLabel()
        self.label_field.setText(self.label.title)
        self.layout.addWidget(self.label_field, 0, 0, 1, 3)
        
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setGeometry(30, 40, 100, 30)
        self.slider.setValue(50)
        self.slider.valueChanged[int].connect(self.changeSliceNumber)
        self.layout.addWidget(self.slider, 1, 0, 1, 2)
        
        self.minmax_label = QLabel()
        self.minmax_label.setText(' - '.join([str(int(each_label)) for each_label in self.label.z_min_max]))
        self.minmax_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        
        self.layout.addWidget(self.minmax_label, 1, 2, 1, 1)
        self.spinbox = QDoubleSpinBox()
        self.spinbox.valueChanged[float].connect(self.changeSliceNumberSpinBox)
        self.layout.addWidget(self.spinbox, 1, 3, 1, 1)
        
        self.stacked_slice_viewer = QStackedWidget()
        self.x_plane_viewer = SegRefine3dInspectGuiSliceView(self.volume, 0, self.label.label_x, 1 + 10 * self.figure_no)
        self.y_plane_viewer = SegRefine3dInspectGuiSliceView(self.volume, 1, self.label.label_y, 2 + 10 * self.figure_no)
        self.z_plane_viewer = SegRefine3dInspectGuiSliceView(self.volume, 2, self.label.label_z, 0 + 10 * self.figure_no)
        self.auto_volume = self.build_autocorr_volume()
        
        self.x_auto_viewer = SegRefine3dInspectGuiSliceView(self.auto_volume, 0, 'auto' + self.label.label_x, 3 + \
        10 * self.figure_no)
            
        self.stacked_slice_viewer.addWidget(self.x_plane_viewer)
        self.stacked_slice_viewer.addWidget(self.y_plane_viewer)
        self.stacked_slice_viewer.addWidget(self.z_plane_viewer)
        self.stacked_slice_viewer.addWidget(self.x_auto_viewer)
        self.layout.addWidget(self.stacked_slice_viewer, 2, 0, 4, 4)
        
        self.slice_direction = 2
        self.slice_choice = QComboBox()
        
        self.slice_choice.addItems([self.label.label_x, self.label.label_y, self.label.label_z, 'Autocorrelation {' + \
        self.label.label_x + '}'])
        
        self.connect(self.slice_choice, SIGNAL('currentIndexChanged(int)'), self.update_slice_choice)
        self.layout.addWidget(self.slice_choice, 0, 3, 1, 1)
        
        for each_slice in list(range(self.slice_direction)):
            self.update_slice_choice(each_slice)
        self.slice_choice.setCurrentIndex(self.slice_direction)
        
    def update_slice_choice(self, value):
        self.slice_plane = value
        self.set_ticks_and_labels_for_slices()
        self.stacked_slice_viewer.setCurrentIndex(value)
        
    def set_ticks_and_labels_for_slices(self):
        if self.slice_plane == 0:
            x_count, y_count = self.volume[:,:,0].shape
            z_count = self.volume.shape[2]
            x_y_label = [self.label.label_z, self.label.label_y]
            x_min_max, y_min_max  = self.label.z_min_max, self.label.y_min_max
            self.z_min_max = self.label.x_min_max
            self.label_z_text = self.label.label_x
            
            self.x_plane_viewer.canvas.set_adjustable_tick_values(self.x_plane_viewer.ax, x_count, y_count, x_min_max,
            y_min_max)
            
            self.x_plane_viewer.canvas.set_x_and_y_label(self.x_plane_viewer.ax, x_y_label)
            self.x_plane_viewer.slice.axes.figure.canvas.draw()
        elif self.slice_plane == 1:
            x_count, y_count = self.volume[:,0].shape
            z_count = self.volume.shape[1]
            x_y_label = [self.label.label_z, self.label.label_x]
            x_min_max, y_min_max  = self.label.z_min_max, self.label.x_min_max
            self.z_min_max = self.label.y_min_max
            self.label_z_text = self.label.label_y
            
            self.y_plane_viewer.canvas.set_adjustable_tick_values(self.y_plane_viewer.ax, x_count, y_count, x_min_max,
            y_min_max)
            
            self.y_plane_viewer.canvas.set_x_and_y_label(self.y_plane_viewer.ax, x_y_label)
            self.y_plane_viewer.slice.axes.figure.canvas.draw()
        elif self.slice_plane == 2:
            x_count, y_count = self.volume[0].shape
            z_count = self.volume.shape[0]
            x_y_label = [self.label.label_x, self.label.label_y]
            x_min_max, y_min_max  = self.label.x_min_max, self.label.y_min_max
            self.z_min_max = self.label.z_min_max
            self.label_z_text = self.label.label_z
            
            self.z_plane_viewer.canvas.set_adjustable_tick_values(self.z_plane_viewer.ax, x_count, y_count, x_min_max,
            y_min_max)
            
            self.z_plane_viewer.canvas.set_x_and_y_label(self.z_plane_viewer.ax, x_y_label)
            self.z_plane_viewer.slice.axes.figure.canvas.draw()
        if self.slice_plane == 3:
            x_count, y_count = self.volume[:,:,0].shape
            z_count = self.volume.shape[2]
            x_y_label = [self.label.label_z, self.label.label_y]
            x_min_max, y_min_max  = self.label.z_min_max, self.label.y_min_max
            self.z_min_max = self.label.x_min_max
            self.label_z_text = 'Autocorrelation {' + self.label.label_x + '}'
            
            self.x_auto_viewer.canvas.set_adjustable_tick_values(self.x_auto_viewer.ax, x_count, y_count, x_min_max,
            y_min_max)
            
            self.x_auto_viewer.canvas.set_x_and_y_label(self.x_auto_viewer.ax, x_y_label)
            self.x_auto_viewer.slice.axes.figure.canvas.draw()
            
        self.minmax_label.setText(' - '.join([str(int(each_label)) for each_label in self.z_min_max]))
        value = self.slider.value()
        self.spinbox.setValue(self.z_min_max[0] + value/99.0 * (self.z_min_max[1] - self.z_min_max[0]))
        self.changeSliceNumber(value)
        
        self.spinbox.setRange(self.z_min_max[0], self.z_min_max[1])
        step = (self.z_min_max[1] - self.z_min_max[0]) / float(z_count)
        self.spinbox.setSingleStep(step)
        self.spinbox.setDecimals(1)
        
        
    def changeSliceNumberSpinBox(self, value):
        slider_value = int(round(99 * (value - self.z_min_max[0]) / float(self.z_min_max[1] - self.z_min_max[0])))
        self.slider.setValue(slider_value)        
#        sys.stderr.write('Changed {0}'.format(slider_value))
    
    def changeSliceNumber(self, value):
#        sys.stderr.write('Changed {0}'.format(value))
        if self.slice_plane == 0:
            self.slider_value_x = value
            self.slice_no_x = int(value/100.0 * self.volume.shape[1])
            self.x_plane_viewer.slice.set_data(self.volume[:,self.slice_no_x])
            self.x_plane_viewer.slice.axes.figure.canvas.draw()
        elif self.slice_plane == 1:
            self.slider_value_y = value
            self.slice_no_y = int(value/100.0 * self.volume.shape[2])
            self.y_plane_viewer.slice.set_data(self.volume[:,:,self.slice_no_y])
            self.y_plane_viewer.slice.axes.figure.canvas.draw()
        elif self.slice_plane == 2:
            self.slider_value_z = value
            self.slice_no_z = int(value/100.0 * self.volume.shape[0])
            self.z_plane_viewer.slice.set_data(self.volume[self.slice_no_z])
            self.z_plane_viewer.slice.axes.figure.canvas.draw()
        if self.slice_plane == 3:
            self.slider_value_x = value
            self.slice_no_x = int(value/100.0 * self.volume.shape[1])
            self.x_auto_viewer.slice.set_data(self.auto_volume[:,self.slice_no_x])
            self.x_auto_viewer.slice.axes.figure.canvas.draw()
        
        self.spinbox.setValue(self.z_min_max[0] + value/99.0 * (self.z_min_max[1] - self.z_min_max[0]))
        
    def update_volume_and_views(self, volume):
        self.volume = volume
        
        self.x_plane_viewer.slice.set_data(self.volume[:,self.slice_no_x])
        self.x_plane_viewer.slice.set_clim(0, self.volume.max())
        self.x_plane_viewer.slice.axes.figure.canvas.draw()
        
        self.y_plane_viewer.slice.set_data(self.volume[:,:,self.slice_no_y])
        self.y_plane_viewer.slice.set_clim(0, self.volume.max())
        self.y_plane_viewer.slice.axes.figure.canvas.draw()
        
        self.z_plane_viewer.slice.set_data(self.volume[self.slice_no_z])
        self.z_plane_viewer.slice.set_clim(0, self.volume.max())
        self.z_plane_viewer.slice.axes.figure.canvas.draw()
            
            
class SegRefine3dInspectGuiItems(object):

    def build_original_volume_display(self):
        self.cartesian_window_ori = SegRefine3dInspectGuiSlice(self.current_vol, self.cart_label, 0)
        self.cylindrical_window_ori = SegRefine3dInspectGuiSlice(self.current_cyl_vol, self.cyl_label, 1)
        self.splitter_ori = QSplitter(Qt.Horizontal)
        self.splitter_ori.addWidget(self.cartesian_window_ori)
        self.splitter_ori.addWidget(self.cylindrical_window_ori)
        
        
    def build_mirror_check(self):
        self.mirror_check = QCheckBox()
        swap_handedness = 'Swap handedness'
        self.mirror_check.setText(swap_handedness)
        self.mirror_check.setToolTip(self.feature_set.hints[swap_handedness])
        self.layout.addWidget(self.mirror_check, 3, 0, 1, 1)
        self.connect(self.mirror_check, SIGNAL('toggled(bool)'), self.update_current_volume_with_mirror)
        
    
    def build_sn_weighting_check(self):
        if self.feature_set.parameters['Signal-to-noise weighting']:
            self.sn_weighting_check = QCheckBox()
            sn_weighting = 'Signal-to-noise weighting'
            self.sn_weighting_check.setText(sn_weighting)
            self.sn_weighting_check.setToolTip(self.feature_set.hints[sn_weighting])
            self.layout.addWidget(self.sn_weighting_check, 4, 3, 1, 1)
            self.connect(self.sn_weighting_check, SIGNAL('toggled(bool)'), self.update_current_fsc_line)
            
            self.fsc_line_read = \
            SegRefine3dInspectCommonOperations().read_fsc_line_from_file(self.feature_set.parameters['FSC curve'],
            self.current_vol_ref.get_xsize())
            self.fsc_line = self.fsc_line_read

        else:
            self.fsc_line_read = None
            self.fsc_line = None
    
    
    def build_bfactor_and_cutoff_dials(self):
        bfactor_res = 'B-factor and resolution cutoff'
        
        self.bfactor_check = QCheckBox()
        self.layout.addWidget(self.bfactor_check, 4, 0, 1, 1)
        self.bfactor_check.setText('{0}'.format(bfactor_res))

        self.bfactor_dial = QDoubleSpinBox()
        bfact_cutoff_tip = '{0} Confirm entry by pressing enter.'.format(self.feature_set.hints[bfactor_res])
        self.bfactor_dial.setToolTip(bfact_cutoff_tip)
        self = NumbersOptionsGuiWindow().compute_number_of_digits_from_properties(self, bfactor_res)
        self.bfactor_dial.setRange(self.properties[bfactor_res].minimum, self.properties[bfactor_res].maximum)
        self.bfactor_dial.setSingleStep(25)
        self.bfactor_dial.setDecimals(self.digits)
        self.bfactor_dial.setValue(self.feature_set.parameters[bfactor_res][0])
        self.connect(self.bfactor_dial, SIGNAL('editingFinished()'), self.activateOrInactivateBfactor)
        self.bfactor_dial.setEnabled(False)
        self.layout.addWidget(self.bfactor_dial, 4, 1, 1, 1)
        
        self.cutoff_dial = QDoubleSpinBox()
        self.cutoff_dial.setToolTip(bfact_cutoff_tip)
        self.cutoff_dial.setRange(0, self.properties[bfactor_res].maximum)
        self.cutoff_dial.setSingleStep(1)
        self.cutoff_dial.setDecimals(1)
        self.cutoff_dial.setValue(self.feature_set.parameters[bfactor_res][1])
        self.connect(self.cutoff_dial, SIGNAL('editingFinished()'), self.activateOrInactivateBfactor)
        self.cutoff_dial.setEnabled(False)
        self.layout.addWidget(self.cutoff_dial, 4, 2, 1, 1)

        self.connect(self.bfactor_check, SIGNAL('toggled(bool)'), self.cutoff_dial, SLOT('setEnabled(bool)'))
        self.connect(self.bfactor_check, SIGNAL('toggled(bool)'), self.bfactor_dial, SLOT('setEnabled(bool)'))
        self.connect(self.bfactor_check, SIGNAL('toggled(bool)'), self.activateOrInactivateBfactor)
        
        
    def build_structural_mask_choice(self):
        self.mask_choice = QComboBox()
        mask_type = 'Mask type'
        self.mask_label = QLabel()
        self.mask_label.setText(mask_type)
        items = ['None'] + \
        [each_choice.capitalize() for each_choice in self.feature_set.properties[mask_type].choices]
        self.mask_choice.addItems(items)
        self.mask_choice.setToolTip(self.feature_set.hints[mask_type])
        self.layout.addWidget(self.mask_label, 6, 0, 1, 1)
        self.layout.addWidget(self.mask_choice, 6, 1, 1, 1)
        self.connect(self.mask_choice, SIGNAL('currentIndexChanged(int)'), self.setCurrentDisplay)
        
        self.item_choice = dict([(each_item, each_index) for each_index, each_item in enumerate(items)])
    
        
    def build_layer_line_filter_check(self):
        self.layer_line_check = QCheckBox()
        layer_line_filter = 'Layer-line Fourier filter'
        self.layer_line_check.setText(layer_line_filter)
        self.layer_line_check.setToolTip(self.feature_set.hints[layer_line_filter])
        self.layout.addWidget(self.layer_line_check, 5, 0, 1, 1)
        self.connect(self.layer_line_check, SIGNAL('toggled(bool)'), self.setCurrentDisplay)
        
    
    def build_long_helix_buttons(self):
        self.helix_length_dial = QDoubleSpinBox()
        length = 'Helix length in Angstrom'
        self.helix_length_dial.setToolTip(self.feature_set.hints[length])
        self = NumbersOptionsGuiWindow().compute_number_of_digits_from_properties(self, length)
        self.helix_length_dial.setRange(self.properties[length].minimum, self.properties[length].maximum)
        self.helix_length_dial.setValue(self.feature_set.parameters[length])
        self.helix_length_dial.setSingleStep(self.properties[length].step)
        self.helix_length_dial.setDecimals(self.digits)
        self.helix_length_dial.setEnabled(False)
        self.layout.addWidget(self.helix_length_dial, 5, 4, 1, 1)
        
        self.long_helix_tick = QCheckBox()
        long_helix = 'Long helix'
        self.long_helix_tick.setText(long_helix)
        self.long_helix_tick.setToolTip(self.feature_set.hints[long_helix])
        self.connect(self.long_helix_tick, SIGNAL('toggled(bool)'), self.helix_length_dial, SLOT('setEnabled(bool)'))
        self.layout.addWidget(self.long_helix_tick, 5, 3, 1, 1)
        
        
    def build_open_button(self):
        self.open_button = QPushButton()
        self.open_button.setText('Open')
        self.open_button.setToolTip('Open volume in 3D viewer.')
        self.open_button.setShortcut('Ctrl+O')
        self.connect(self.open_button, SIGNAL('clicked()'), self.openVolume)
        self.layout.addWidget(self.open_button, 6, 3, 1, 1)
        

    def build_save_button(self):
        self.save_button = QPushButton()
        self.save_button.setText('Save')
        self.save_button.setToolTip('Save volume in current masked and filtered state.')
        self.save_button.setShortcut('Ctrl+S')
        self.connect(self.save_button, SIGNAL('clicked()'), self.saveVolume)
        self.layout.addWidget(self.save_button, 6, 4, 1, 1)
        

class SegRefine3dInspectGui(QWidget, SegRefine3dInspectGuiItems):

    def __init__(self, feature_set, em_volumes, parent = None):
        QWidget.__init__(self, parent)
        
        self.em_volumes = em_volumes
        self.cart_volumes = self.make_cart_volumes()
        self.current_vol_ref = self.em_volumes.original
        self.current_vol = np.copy(EMNumPy.em2numpy(self.em_volumes.original))
        
        self.current_cyl_vol, self.r, self.theta = SegmentRefine3d().reproject_volume_into_cylinder(self.current_vol)
        
        self.feature_set = feature_set
        self.properties = feature_set.properties
        self = SpringCommon().setup_spring_page_top(self, self.feature_set)
        
        self.get_parameters_from_dict()
        self.make_labels()
        self.build_original_volume_display()
        
        self.layout.addWidget(self.splitter_ori, 2, 0, 2, 5)
        
        self.build_mirror_check()
        self.build_bfactor_and_cutoff_dials()
        self.build_layer_line_filter_check()
        self.build_structural_mask_choice()
        self.build_sn_weighting_check()

        self.build_open_button()
        self.build_long_helix_buttons()
        self.build_save_button()
        self.setLayout(self.layout)
        
        self.external_launcher = ExtLauncher()

        self.setCurrentDisplay()
        
        self.set_values_from_parameters()

    def make_cart_volumes(self):
        self.volume_collection = SegRefine3dInspectCommonOperations().make_volume_collection_named_tuple()
        np_vols = [np.copy(EMNumPy.em2numpy(each_volume)) for each_volume in list(self.em_volumes)]
        self.cart_volumes = self.volume_collection._make(np_vols)
        
        return self.cart_volumes
        

    def get_parameters_from_dict(self):
        self.pixelsize = self.feature_set.parameters['Pixel size in Angstrom']
        self.helixwidth = self.feature_set.parameters['Estimated helix inner and outer diameter in Angstrom'][1]
        rise_or_pitch_choice = self.feature_set.parameters['Helical rise/rotation or pitch/number of units per turn choice']
        self.helical_symmetry = self.feature_set.parameters['Helical symmetry in Angstrom or degrees']
        self.rotational_symmetry = self.feature_set.parameters['Rotational symmetry']
        self.polar_helix = self.feature_set.parameters['Helix polarity']
        
        self.helical_symmetry = \
        SegRefine3dInspectCommonOperations().convert_helical_symmetry_from_pitch_unit_number_to_rise_rotation(
        rise_or_pitch_choice, self.helical_symmetry)


    def make_labels(self):
        label_collection = namedtuple('label', 'title label_x label_y label_z quantities x_min_max y_min_max z_min_max')
        distance = 'distance (Angstrom)'
        self.bfactor = 0.0
        self.res_cutoff_A = 0.0
        
        self.cart_label = label_collection('Cartesian image slices', 'X ' + distance, 'Y ' + distance, 'Z ' + distance, 
        ['x', 'y', 'z'], 
        [-self.pixelsize * self.cart_volumes[0].shape[1]/2, self.pixelsize * self.cart_volumes[0].shape[1]/2],
        [-self.pixelsize * self.cart_volumes[0].shape[2]/2, self.pixelsize * self.cart_volumes[0].shape[2]/2],
        [-self.pixelsize * self.cart_volumes[0].shape[0]/2, self.pixelsize * self.cart_volumes[0].shape[0]/2])
        
        self.cyl_label = label_collection('Cylindrical image slices', 'Radius (Angstrom)', 'Theta (degrees)', 
        'Z ' + distance, ['r', 'theta', 'z'],
        [self.pixelsize * self.r.min(), self.pixelsize * self.r.max()], 
#        [-180.0, 180.0], 
#        [np.rad2deg(self.theta.min()), np.rad2deg(self.theta.max())], 
        [np.rad2deg(self.theta.min()), 180.0], 
        [-self.pixelsize * self.cart_volumes[0].shape[0]/2, self.pixelsize * self.cart_volumes[0].shape[0]/2])
            

    def mirror_numpy_volume(self):
        current_vol = EMNumPy.numpy2em(np.copy(self.current_vol))
        current_vol = mirror(current_vol)
        self.current_vol = np.copy(EMNumPy.em2numpy(current_vol))
        

    def update_current_fsc_line(self):
        if self.sn_weighting_check.isChecked():
            self.fsc_line = self.fsc_line_read
        else:
            self.fsc_line = None

        self.setCurrentDisplay()


    def update_current_volume_with_mirror(self):
        self.mirror_numpy_volume()
        
        rise, rotation = self.helical_symmetry
        self.helical_symmetry = (rise, -rotation)
        
        self.current_cyl_vol, self.r, self.theta = \
        SegmentRefine3d().reproject_volume_into_cylinder(self.current_vol)
        
        self.update_views_of_volumes()
        
        
    def update_volume_to_numpy_and_cylinder_projection(self):
        self.current_vol = np.copy(EMNumPy.em2numpy(self.current_vol_ref))
        if self.mirror_check.isChecked():
            self.mirror_numpy_volume()
        
        self.current_cyl_vol, self.r, self.theta = \
        SegmentRefine3d().reproject_volume_into_cylinder(self.current_vol)
        
        self.update_views_of_volumes()
        

    def update_views_of_volumes(self):
        self.cartesian_window_ori.update_volume_and_views(self.current_vol)
        self.cylindrical_window_ori.update_volume_and_views(self.current_cyl_vol)
        
        
    def setCurrentDisplay(self):
        if self.layer_line_check.checkState() == 0:
            self.current_vol_ref = self.em_volumes.original
        elif self.layer_line_check.checkState() == 2:
            self.current_vol_ref = self.em_volumes.layer
        
        self.current_vol_ref = \
        SegRefine3dInspectCommonOperations().apply_bfactor_and_resolution_cutoff(self.current_vol_ref, self.bfactor,
        self.res_cutoff_A, self.pixelsize, self.fsc_line)
        
        if self.mask_choice.currentIndex() == 1:
            self.current_vol_ref *= self.em_volumes.cylinder_mask 
        elif self.mask_choice.currentIndex() == 2:
            self.current_vol_ref *= self.em_volumes.structural_mask 
            
        self.current_vol_ref.process_inplace('normalize')
        self.update_volume_to_numpy_and_cylinder_projection()
        

    def set_values_from_parameters(self):
        if self.feature_set.parameters['Swap handedness']:
            self.mirror_check.setChecked(True)
        if self.feature_set.parameters['B-factor']:
            self.bfactor_check.setChecked(True)
        if self.feature_set.parameters['Signal-to-noise weighting']:
            self.sn_weighting_check.setChecked(True)
        if self.feature_set.parameters['Layer-line Fourier filter']:
            self.layer_line_check.setChecked(True)
        if self.feature_set.parameters['Long helix']:
            self.long_helix_tick.setChecked(True)
        self.mask_choice.setCurrentIndex(self.item_choice[self.feature_set.parameters['Mask type'].capitalize()])


    def activateOrInactivateBfactor(self):
        if self.bfactor != self.bfactor_dial.value() or self.res_cutoff_A != self.cutoff_dial.value():
            if self.bfactor_check.checkState() == 2:
                self.bfactor = self.bfactor_dial.value()
                self.res_cutoff_A = self.cutoff_dial.value()
            self.setCurrentDisplay()
        elif self.bfactor_check.checkState() == 0:
            self.bfactor = 0.0
            self.res_cutoff_A = 0.0
            self.setCurrentDisplay()
        elif self.bfactor == self.bfactor_dial.value() and self.res_cutoff_A == self.cutoff_dial.value():
            pass 
        

    def get_cur_volume_and_write_out(self, fname):
        if fname != '':
            vol = EMNumPy.numpy2em(np.copy(self.current_vol))
            vol = SegClassReconstruct().set_isotropic_pixelsize_in_volume(self.pixelsize, vol)
            if self.long_helix_tick.isChecked():
                length = self.helix_length_dial.value()

                vol = SegRefine3dInspectCommonOperations().prepare_long_helix(vol, length, self.helixwidth,
                self.pixelsize, self.helical_symmetry, self.rotational_symmetry, self.polar_helix)

                vol.process_inplace('normalize')
            vol.write_image(fname)


    def saveVolume(self):
        fname = str(QFileDialog.getSaveFileName(self , 'Save volume', '.', 'Files ({0})'.\
        format('*.' + ' *.'.join(self.properties.values()[0].ext)))) 
        
        self.get_cur_volume_and_write_out(fname)
        

    def openVolume(self):
        cur_bfactor = self.bfactor_dial.value()
        cur_res = self.cutoff_dial.value()
        cur_res_str = 'd'.join(cur_res.__str__().split('.'))
        
        fname = 'recvol_{0}Bfac_{1}A.hdf'.format(abs(int(cur_bfactor)), cur_res_str)
        self.get_cur_volume_and_write_out(fname)
        self.external_launcher.qlaunch_open_file(os.path.abspath(fname))
