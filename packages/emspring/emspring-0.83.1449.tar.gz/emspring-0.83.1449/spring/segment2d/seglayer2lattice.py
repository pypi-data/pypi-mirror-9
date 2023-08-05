# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to simulate helical diffraction pattern and plot helical lattice from a series of indexed layer lines or \
rise/rotation parameters
"""
from EMAN2 import EMData, EMNumPy
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QApplication, QWidget, QLineEdit, QPushButton, QDoubleSpinBox, QLabel, QSplitter, QFont, \
    QToolTip, QComboBox, QCheckBox
from matplotlib.ticker import MultipleLocator
from scipy import special
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.csgui import NumbersOptionsGuiWindow, QTabWidgetCloseable
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import DiagnosticPlot
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segmentexam import SegmentExam
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from spring.springgui.springdataexplore import SpringCommon, SpringDataExplore, SpringDataExploreDraw
from tabulate import tabulate
import matplotlib.cm as cm
import matplotlib.font_manager as font_manager
import numpy as np
import sys

class SegLayer2LatticePar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'seglayer2lattice'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.seglayer2lattice_features = Features()
        self.feature_set = self.seglayer2lattice_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    

    def define_parameters_and_their_properties(self):

        self.feature_set = self.seglayer2lattice_features.set_input_power_to_analyze(self.feature_set)
        
        self.feature_set = self.seglayer2lattice_features.set_input_power_spectrum(self.feature_set, 
                                                                                   'Analyze power spectrum')
        
        self.feature_set = self.seglayer2lattice_features.set_interactive_vs_batch_mode(self.feature_set)
        self.feature_set = self.seglayer2lattice_features.set_output_plot(self.feature_set, self.progname + '_diag.pdf',
                                                                          'Batch mode')
        
        self.feature_set = self.seglayer2lattice_features.set_pixelsize(self.feature_set)
        self.feature_set = self.seglayer2lattice_features.set_high_pass_filter_option(self.feature_set)
        self.feature_set = self.seglayer2lattice_features.set_low_pass_filter_option(self.feature_set)
        self.feature_set = self.seglayer2lattice_features.set_high_and_low_pass_filter_cutoff(self.feature_set)
        self.feature_set = self.set_layer_bessel_or_symmetry_choice(self.feature_set)
        self.feature_set = self.set_layer_bessel_or_symmetry(self.feature_set)
        self.feature_set = self.seglayer2lattice_features.set_rotational_symmetry(self.feature_set)
        self.feature_set = self.seglayer2lattice_features.set_exact_helix_width(self.feature_set)
        

    def define_program_states(self):
        self.feature_set.properties['Number of lines Logfile']=50
        self.feature_set.program_states['plot_layer_lines_to_power_and_lattice']='Plots assigned layer lines to ' + \
        'helical lattice'


    def set_layer_bessel_or_symmetry(self, feature_set):
        inp8 = 'Layer line/Bessel or rise/rotation pair(s)'
        feature_set.parameters[inp8] = str('(0.03, 2); (0.06, -4); (0.09, 6)')
        feature_set.hints[inp8] = 'List of comma-separated pairs in brackets. Pairs are separated by semicolon. ' + \
        '(Layer line position [1/Angstrom], Bessel order [integer]) or (Helical rise [Angstrom], rotation [degrees])'
        feature_set.properties[inp8] = feature_set.file_properties(1, ['*'], None)
        feature_set.level[inp8]='beginner'
        
        return feature_set
    

    def set_layer_bessel_or_symmetry_choice(self, feature_set):
        inp7 = 'Layer line/Bessel order or helical rise/rotation choice'
        feature_set.parameters[inp7] = str('rise/rotation')
        feature_set.hints[inp7] = 'Choose whether \'layer/bessel\', \'rise/rotation\' or \'pitch/unit_number \' ' + \
        'pairs are given for generating the helical lattice.'
        
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['layer/bessel', 'rise/rotation',
        'pitch/unit_number'], 'QComboBox')
        
        feature_set.level[inp7]='beginner'

        return feature_set
    

class SegLayer2LatticeGui(QWidget):
    def __init__(self, feature_set, parent = None):
        QWidget.__init__(self, parent)
        
        self.feature_set = feature_set
        self.properties = feature_set.properties
        
        self = SpringCommon().setup_spring_page_top(self, feature_set)
        
        self.get_parameters_from_dict()
        self.sym_plot = DiagnosticPlot()

        self.build_figure()

        self.build_controls()
        self.tabWidget = QTabWidgetCloseable()
        
        self.add_tab_with_new_symmetry()
        
        self.layout.addWidget(self.tabWidget, 1, 0, 1, 5)
        
        self.setLayout(self.layout)
        
        self.setMouseTracking(True)
 

    def enterEvent(self, event):
        QToolTip.setFont(QFont('Courier', 8))

        
    def get_parameters_from_dict(self):
        self.seglayer2lattice = SegLayer2Lattice(self.feature_set)
        
        
    def build_figure(self):
        fig1 = self.sym_plot.create_next_figure()
        ax1 = fig1.add_subplot(111)
        fig2 = self.sym_plot.create_next_figure()
        ax2 = fig2.add_subplot(111)
        fig3 = self.sym_plot.create_next_figure()
        ax3 = fig3.add_subplot(111)

        layerline_bessel_pairs = self.seglayer2lattice.get_layer_line_bessel_pairs()
        ax1, ax2 = self.seglayer2lattice.plot_layer_lines_in_power_spectrum(layerline_bessel_pairs, ax1, ax2)

        title = '{0}: ({1})'.format(self.seglayer2lattice.layer_bessel_or_sympair_choice, 
                                  self.seglayer2lattice.layer_sympair_entry.strip('(').strip(')'))
        if self.seglayer2lattice.rot_sym > 1:
                title += ' C{0}'.format(int(self.seglayer2lattice.rot_sym))

        ax1.set_title(title.title())
        ax3 = self.seglayer2lattice.plot_helical_lattice(layerline_bessel_pairs, ax3)

        self.power_canvas = SpringDataExplore(fig1)
        self.bessel_canvas = SpringDataExplore(fig2)
        
        res, orders = zip(*layerline_bessel_pairs)
        res_real = np.around(np.flipud(1 / np.array(res)), decimals=2)
        res = np.flipud(np.around(np.array(res), decimals=5))
        orders = np.flipud(orders)

        self.tool_str = tabulate(zip(res, res_real, orders),
                            headers=['Resolution (1/A)', 'Resolution (A)', 'Bessel order'], 
                            tablefmt='rst')
        
        self.bessel_canvas.main_frame.setToolTip(self.tool_str)
        self.bessel_canvas.setMouseTracking(True)

        self.lattice_canvas = SpringDataExplore(fig3)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter_vert = QSplitter(Qt.Vertical)
            
        self.splitter_vert.addWidget(self.lattice_canvas)
        self.splitter_vert.addWidget(self.bessel_canvas)
        self.splitter.addWidget(self.power_canvas)
        self.splitter.addWidget(self.splitter_vert)

        return self.splitter
        
        
    def build_controls(self):

        choices = ['rise/rotation', 'pitch/unit_number']
        self.pushbutton = QPushButton()
        self.pushbutton.setText('OK')
        self.layout.addWidget(self.pushbutton, 2, 4, 1, 1)
        self.connect(self.pushbutton, SIGNAL('clicked()'), self.open_another_tab)
        if self.seglayer2lattice.layer_bessel_or_sympair_choice in ['layer/bessel']:
            text = NumbersOptionsGuiWindow().convert_angstrom_string('Layer line position (Angstrom^-1)/Bessel order')
            self.label = QLabel()
            self.label.setText(text)
            self.lineedit = QLineEdit()
            self.lineedit.setToolTip('(' + ', '.join(text.split('/')) + '(int)); (LL, BO); ...')
            self.lineedit.setText(self.seglayer2lattice.layer_sympair_entry)
            self.layout.addWidget(self.label, 2, 0, 1, 1)
            self.label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
            
            self.layout.addWidget(self.lineedit, 2, 1, 1, 2)
        elif self.seglayer2lattice.layer_bessel_or_sympair_choice in choices:
            self.inputChoice= QComboBox()
            self.inputChoice.addItems([each_choice.title() for each_choice in choices])
            if self.seglayer2lattice.layer_bessel_or_sympair_choice in ['rise/rotation']:
                text = NumbersOptionsGuiWindow().convert_angstrom_string('Helical rise (Angstrom)/Helical rotation (degrees)')
                self.inputChoice.setCurrentIndex(0)
            elif self.seglayer2lattice.layer_bessel_or_sympair_choice in ['pitch/unit_number']:
                text = NumbersOptionsGuiWindow().convert_angstrom_string('Pitch (Angstrom)/Number of units per turn')
                self.inputChoice.setCurrentIndex(1)
            
            self.inputChoice.setToolTip(text)
            rise, rotation = \
            SegLayer2Lattice().convert_entry_to_rise_rotation_pair(self.seglayer2lattice.layer_sympair_entry)
            
            self.rise_dial = QDoubleSpinBox()
            self.rise_dial.setRange(0, 1000)
            self.rise_dial.setSingleStep(1)
            self.rise_dial.setDecimals(3)
            self.rise_dial.setToolTip(text.split('/')[0])
            self.rise_dial.setValue(rise)
            
            self.rotation_dial = QDoubleSpinBox()
            self.rotation_dial.setRange(0.001, 360)
            self.rotation_dial.setSingleStep(0.001)
            self.rotation_dial.setDecimals(3)
            self.rotation_dial.setToolTip(text.split('/')[1])
            self.rotation_dial.setValue(rotation)
            
            self.rot_sym_check = QCheckBox()
            rot_sym_text = 'Rotational symmetry'
            self.rot_sym_check.setText(rot_sym_text)
            self.rot_sym_check.setToolTip(self.feature_set.hints[rot_sym_text])
            self.rot_sym_dial = QDoubleSpinBox()
            self.rot_sym_dial.setRange(1, 1000)
            self.rot_sym_dial.setSingleStep(1)
            self.rot_sym_dial.setDecimals(0)
            self.rot_sym_dial.setToolTip('Rotational symmetry')
            self.rot_sym_dial.setEnabled(False)

            self.layout.addWidget(self.inputChoice, 2, 0, 1, 1)
            self.layout.addWidget(self.rise_dial, 2, 2, 1, 1)
            self.layout.addWidget(self.rotation_dial, 2, 3, 1, 1)
            
            self.layout.addWidget(self.rot_sym_check, 3, 0, 1, 1)
            self.layout.addWidget(self.rot_sym_dial, 3, 2, 1, 2)
            
            self.connect(self.inputChoice, SIGNAL('currentIndexChanged(int)'), self.changeInputChoice)
            self.connect(self.rot_sym_check, SIGNAL('toggled(bool)'), self.turn_rot_sym_dial_on_or_off)

            if self.seglayer2lattice.rot_sym > 1:
                self.rot_sym_check.setChecked(True)
                self.rot_sym_dial.setValue(self.seglayer2lattice.rot_sym)


    def turn_rot_sym_dial_on_or_off(self, state):
        self.rot_sym_dial.setEnabled(state)


    def changeInputChoice(self, choice):
        if choice == 0:
            self.seglayer2lattice.layer_bessel_or_sympair_choice = 'rise/rotation' 
            text = NumbersOptionsGuiWindow().convert_angstrom_string('Helical rise (Angstrom)/Helical rotation (degrees)')
        if choice == 1:
            self.seglayer2lattice.layer_bessel_or_sympair_choice = 'pitch/unit_number' 
            text = NumbersOptionsGuiWindow().convert_angstrom_string('Pitch (Angstrom)/Number of units per turn')

        self.rise_dial.setToolTip(text.split('/')[0])
        self.rotation_dial.setToolTip(text.split('/')[1])

    
    def open_another_tab(self):
        if self.seglayer2lattice.layer_bessel_or_sympair_choice in ['layer/bessel']:
            self.seglayer2lattice.layer_sympair_entry = str(self.lineedit.text())
        else:
            self.seglayer2lattice.layer_sympair_entry = '({0}, {1})'.format(self.rise_dial.value(),
            self.rotation_dial.value())
            
        if hasattr(self, 'rot_sym_dial'):
            if self.rot_sym_dial.isEnabled():
                self.seglayer2lattice.rot_sym = self.rot_sym_dial.value()
            else:
                self.seglayer2lattice.rot_sym = 1
        else:
            self.seglayer2lattice.rot_sym = 1

        self.build_figure()
        self.add_tab_with_new_symmetry()
        

    def get_title_for_current_tab(self):
        title = self.seglayer2lattice.layer_sympair_entry.strip('(').strip(')')
        if hasattr(self, 'rot_sym_dial'):
            if self.rot_sym_dial.isEnabled():
                title += ' C{0}'.format(int(self.seglayer2lattice.rot_sym))
        title += ' ({0})'.format(self.seglayer2lattice.layer_bessel_or_sympair_choice)

        return title


    def add_tab_with_new_symmetry(self):
        title = self.get_title_for_current_tab()

        self.splitter.setToolTip(title.title())
        self.tabWidget.addTab(self.splitter, title.title())
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.splitter))
        self.tabWidget.setTabToolTip(self.tabWidget.currentIndex(), title.title())

            
class SegLayer2LatticePreparation(object):
    """
    * Class that holds functions for plotting assigned layer lines to helical lattice

    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.power_img = p['Power spectrum input image']
            self.analyze_power = p['Analyze power spectrum']
            self.batch_mode = p['Batch mode']
            self.outfile = p['Diagnostic plot']
            self.pixelsize = p['Pixel size in Angstrom']
            
            self.low_pass_filter_option = p['Low-pass filter option']
            self.high_pass_filter_option = p['High-pass filter option']
            self.high_pass_filter_cutoff = p['High and low-pass filter cutoffs in 1/Angstrom'][0]
            self.low_pass_filter_cutoff = p['High and low-pass filter cutoffs in 1/Angstrom'][1]
            
            if not self.high_pass_filter_option:
                self.high_pass_filter_cutoff = 1/1000.0
            if not self.low_pass_filter_option:
                self.low_pass_filter_cutoff = 1/(2*self.pixelsize)
            
            self.helixwidth = p['Precise helix width in Angstrom']
            self.helix_radius = self.helixwidth / 2.0
            self.layer_bessel_or_sympair_choice = p['Layer line/Bessel order or helical rise/rotation choice']
            self.layer_sympair_entry = p['Layer line/Bessel or rise/rotation pair(s)']
            self.rot_sym = p['Rotational symmetry']
            

    def prepare_layerline_bessel_pairs_from_list(self, layerlines, bessel_orders):
        """
        >>> from spring.segment2d.seglayer2lattice import SegLayer2Lattice
        >>> s = SegLayer2Lattice()
        >>> positions = '0.123, 0.234, 0.345'
        >>> s.prepare_layerline_bessel_pairs_from_list(positions, '-2, 4, 5')
        [(0.123, -2), (0.234, 4), (0.345, 5)]
         >>> s.prepare_layerline_bessel_pairs_from_list(positions, '-2, 4') #doctest: +NORMALIZE_WHITESPACE
         Traceback (most recent call last):
          File '<stdin>', line 1, in <module>
          File 'spring/segment2d/seglayer2lattice.py', line 85, in 
              prepare_layerline_bessel_pairs_from_list
            raise ValueError, error_message
         ValueError: Number of layer line positions does not equal number of 
             assigned Bessel orders. Please revise.
         >>> s.prepare_layerline_bessel_pairs_from_list('0.123', '-2 4') #doctest: +NORMALIZE_WHITESPACE
         Traceback (most recent call last):
          File '<stdin>', line 1, in <module>
          File 'spring/segment2d/seglayer2lattice.py', line 77, in 
              prepare_layerline_bessel_pairs_from_list
            raise ValueError, error_message
         ValueError: No comma-separated list was detected. Please check 
             input of layer line positions.
        """
        layerline_list = bessel_order_list = None
        for separator in [',', ';']:
            if layerlines.find(separator) >= 0:
                layerline_list = layerlines.split(separator)
                layerline_list = [float(each_layer_line) for each_layer_line in layerline_list]
        
            if bessel_orders.find(separator) >= 0:
                bessel_order_list = bessel_orders.split(separator)
                bessel_order_list = [int(each_bessel_order) for each_bessel_order in bessel_order_list]
        
        if layerline_list is None:
            error_message = 'No comma-separated list was detected. Please check input of layer line positions.'
            raise ValueError(error_message)
        
        if bessel_order_list is None:
            error_message = 'No comma-separated list was detected. Please check input of Bessel orders.'
            raise ValueError(error_message)
        
        if len(layerline_list) != len(bessel_order_list):
            error_message = 'Number of layer line positions does not equal number of assigned Bessel orders. Please '+ \
            'revise.'
            raise ValueError(error_message)
            
        if len(layerline_list) == 2 and len(bessel_order_list) == 2:
            self.log.wlog('Only two layer lines entered. This will not result in an unambiguous lattice. ' + \
                          'Recommended minimum number of layer lines is 3.')
            
        layerline_bessel_pairs = list(zip(layerline_list, bessel_order_list))
        
        return layerline_bessel_pairs
            

    def convert_entry_to_rise_rotation_pair(self, entry):
        """
        >>> from spring.segment2d.seglayer2lattice import SegLayer2Lattice
        >>> s = SegLayer2Lattice()
        >>> s.convert_entry_to_rise_rotation_pair('1.408, 22.03')
        (1.408, 22.03)
        """
        stripped_off_entry = entry.strip().strip(')').strip('(')
        for separator in [',', ';']:
            if stripped_off_entry.find(separator) >= 0:
                rise_rotation_pair = stripped_off_entry.split(separator)
                rise_rotation_pair = (float(rise_rotation_pair[0]), float(rise_rotation_pair[1]))
        
        return rise_rotation_pair
    

class SegLayer2LatticePlot(SegLayer2LatticePreparation):
    def generate_lattice_line(self, pitch_bessel_pair, lines_count):
        
        pitch = 1/(pitch_bessel_pair[0])
        bessel_order = pitch_bessel_pair[1]
        
        total_lattice_line = []
        
        linex = np.array([0, 360])
        linexx = np.arange(0, 361, 1)
        if bessel_order > 0:
            liney = [0, bessel_order * pitch]
        elif bessel_order < 0:
            liney = [abs(bessel_order) * pitch, 0]
        elif bessel_order == 0:
            liney = [0, 0]
                    
        polyvar = np.polyfit(linex, liney, 1)
        first_lattice_line = np.polyval(polyvar, linexx)
        
        for each_lattice_line in range(-lines_count/2, lines_count, 1):
            lattice_line = first_lattice_line + each_lattice_line * pitch

#            sys.stderr.write('\nbesselorder:{0}\neach_bessel_order:{1}'.format(bessel_order, each_lattice_line))
#            sys.stderr.write('\nlinex:{0}\nliney:{1}'.format(linex.__str__(), liney.__str__()))
            
            total_lattice_line.append(list(zip(linexx, lattice_line)))
        
        return total_lattice_line
    
    
    def determine_number_of_lattice_lines_required_for_plot(self, layerline_bessel_pairs):
        """
        >>> from spring.segment2d.seglayer2lattice import SegLayer2Lattice
        >>> s = SegLayer2Lattice()
        >>> s.determine_number_of_lattice_lines_required_for_plot([(0.123, -2), (0.234, 4), (0.35, 5)])
        84
        """
        
        layer_line_positions, bessel_orders = list(zip(*layerline_bessel_pairs))
        abs_bessel_orders = [abs(each_bessel_order) for each_bessel_order in bessel_orders]
        lines_count = 2 * int(3 / min(layer_line_positions)) / (1 / max(layer_line_positions)) * max(abs_bessel_orders)
        
        return int(round(lines_count))


    def include_lattice_lines_in_plot(self, layerline_bessel_pairs, ax1, lines_count):
        lattice_lines = []
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        if len(layerline_bessel_pairs) > len(colors):
            colors = int(len(layerline_bessel_pairs)/len(colors) + 1)*colors
            
        maximum_pitch = 0
        layer_line_positions, bessel_orders = list(zip(*layerline_bessel_pairs))
        min_pitch_ind = np.argmax(layer_line_positions)
        
        for each_layer_line_number, each_pitch_bessel_pair in enumerate(layerline_bessel_pairs):
            lattice_line = self.generate_lattice_line(each_pitch_bessel_pair, lines_count)
            each_pitch, each_bessel = each_pitch_bessel_pair
            lattice_lines.append(lattice_line)
            self.log.ilog('Layer line/Bessel order pair: {0} plotted'.format(each_pitch_bessel_pair.__str__()))
            for each_line_number, each_line in enumerate(lattice_line):
                linexx, latttice_line = list(zip(*each_line))
                if each_line_number == 0:
                    ax1.plot(linexx, latttice_line, linewidth=.2, color=colors[each_layer_line_number], 
                    label='Pitch: {0} Angstrom, Bessel order: {1}'.format(round(1 / each_pitch, 2), 
                                                                          each_bessel))
                else:
                    ax1.plot(linexx, latttice_line, linewidth=.2, color=colors[each_layer_line_number])
                if each_layer_line_number == min_pitch_ind:
                    pitch_x = np.linspace(0, 360, 30)
                    pitch_line = [each_line_number / each_pitch for each_pitchi in range(len(pitch_x))]
                    
                    ax1.plot(pitch_x, pitch_line, linewidth=.1, linestyle='dashed',
                    color=colors[each_layer_line_number])
            
            if 1 / each_pitch_bessel_pair[0] > maximum_pitch:
                maximum_pitch = 1 / each_pitch_bessel_pair[0]
        
        return maximum_pitch


    def set_up_general_lattice_plot_properties(self, ax, maximum_pitch):
        ax.legend(loc='upper center', prop=font_manager.FontProperties(size=5))
        ax.set_xlim(0, 360)
        ax.grid(True) 
        ax.yaxis.set_major_locator(MultipleLocator(20))
        ax.yaxis.set_minor_locator(MultipleLocator(10))
        ax.xaxis.set_major_locator(MultipleLocator(45))
        ax.xaxis.set_minor_locator(MultipleLocator(22.5))
        ax.set_xlabel('Angle (degrees)', fontsize=8)
        ax.set_ylabel('Distance (Angstrom)', fontsize=8)
        ax.set_ylim(0, 2 * maximum_pitch)
        
        for t in ax.get_xticklabels(): 
            t.set_fontsize(6)
        for t in ax.get_yticklabels(): 
            t.set_fontsize(6)

        return ax

    
    def limit_to_a_maximum_of_ten_for_display(self, layerline_bessel_pairs):
        pitches, orders = zip(*layerline_bessel_pairs)
        min_indices = np.argsort(np.abs(orders)).tolist()
        
        limit_ll_bessel_pairs = [layerline_bessel_pairs[each_min_order] for each_index, each_min_order in \
        enumerate(min_indices) if each_index < 10]
                
        return limit_ll_bessel_pairs
                
        
    def filter_layer_line_bessel_pairs_to_10A_and_150A_resolution(self, layerline_bessel_pairs):
        
        filtered_pairs = [layerline_bessel_pairs[each_index] for each_index, (each_pitch, each_bessel_order) in \
        enumerate(layerline_bessel_pairs) if 10 < 1/each_pitch < 150]
        
        return filtered_pairs
    

    def plot_helical_lattice(self, layerline_bessel_pairs, ax2):
        layerline_bessel_pairs = self.filter_layer_line_bessel_pairs_to_10A_and_150A_resolution(layerline_bessel_pairs)
        layerline_bessel_pairs = self.limit_to_a_maximum_of_ten_for_display(layerline_bessel_pairs)
        lines_count = self.determine_number_of_lattice_lines_required_for_plot(layerline_bessel_pairs)
        maximum_pitch = self.include_lattice_lines_in_plot(layerline_bessel_pairs, ax2, lines_count)
        self.set_up_general_lattice_plot_properties(ax2, maximum_pitch)

        return ax2


class SegLayer2LatticeMontage(SegLayer2LatticePlot):
    def histeq(self, em_img, nbr_bins=65535):
        im = np.copy(EMNumPy.em2numpy(em_img))
        #get image histogram
        imhist,bins = np.histogram(im.flatten(),nbr_bins,normed=True)
        cdf = imhist.cumsum() #cumulative distribution function
        cdf = cdf / cdf[-1] #normalize
         
        #use linear interpolation of cdf to find new pixel values
        im2 = np.interp(im.flatten(),bins[:-1], cdf)
        em_hist_img = EMNumPy.numpy2em(im2.reshape(im.shape))
         
        return em_hist_img
     
  
class SegLayer2Lattice(SegLayer2LatticeMontage):
    def compute_layer_line_bessel_pairs(self, layer_bessel_or_sympair_choice, layer_sympair_entry, helixwidth,
    pixelsize, high_res_cutoff, low_res_cutoff, rotational_sym):
        if layer_bessel_or_sympair_choice in ['rise/rotation', 'pitch/unit_number']:
            sym_numbers = self.convert_entry_to_rise_rotation_pair(layer_sympair_entry)
            
            if layer_bessel_or_sympair_choice in ['pitch/unit_number']:
                pitch, unit_number = sym_numbers
                
                rise_rotation_pair = SegClassReconstruct().convert_pitch_unit_pair_to_rise_rotation_pairs(pitch,
                unit_number)
            else:
                rise_rotation_pair = sym_numbers
            
            layerline_bessel_pairs = \
            SegClassReconstruct().generate_layerline_bessel_pairs_from_rise_and_rotation(rise_rotation_pair,
            rotational_sym, helixwidth, pixelsize, 1 / high_res_cutoff, 1 / low_res_cutoff, out_of_plane_tilt=0)
        elif layer_bessel_or_sympair_choice in ['layer/bessel']:
            layerline_bessel_pairs = Features().convert_list_of_data_pairs_from_entry_string(layer_sympair_entry)
            
        return layerline_bessel_pairs
    

    def format_ticklabels_to_six_and_xlabel_to_eight(self, ax2):
        [t.set_fontsize(6) for t in ax2.get_xticklabels() + ax2.get_yticklabels()]
        
        ax2.set_xlabel('1/Angstrom', fontsize=8)
        
        return ax2
        

    def format_second_layer_line_plot(self, ax2, line):
        ax2.set_xlim(0, max(line))
        ax2.set_yticks([])
        ax2 = self.format_ticklabels_to_six_and_xlabel_to_eight(ax2)
        
        return ax2
    

    def get_layer_line_bessel_pairs(self):
        layerline_bessel_pairs = self.compute_layer_line_bessel_pairs(self.layer_bessel_or_sympair_choice,
        self.layer_sympair_entry, self.helixwidth, self.pixelsize, self.high_pass_filter_cutoff,
        self.low_pass_filter_cutoff, self.rot_sym)

        return layerline_bessel_pairs


    def prepare_layer_line_plot(self, layerline_bessel_pairs, ax2, linex_fine):
        reciprocal_angstrom_fine = SegmentExam().make_oneoverres(linex_fine, self.pixelsize)
        for each_layer_line_pair in layerline_bessel_pairs:
            bessel_order = abs(each_layer_line_pair[1])
            bessel_function = np.abs(special.jv(bessel_order, linex_fine))
            ax2.plot(reciprocal_angstrom_fine, bessel_function)
        
        return reciprocal_angstrom_fine, ax2


    def plot_layer_lines_in_power_spectrum(self, layerline_bessel_pairs, ax1, ax2):
        if self.analyze_power:
            power_spectrum = EMData()
            power_spectrum.read_image(self.power_img, 0)
        
            power_size = power_spectrum.get_xsize()
        else:
            power_size = 200
        
        ideal_power_img, linex_fine = \
        SegClassReconstruct().prepare_ideal_power_spectrum_from_layer_lines(layerline_bessel_pairs, self.helix_radius,
        power_size, self.pixelsize)
        
#        ideal_power_img.write_image('ideal_power.hdf')
        
        if self.analyze_power:
            montage_side_by_side = SegClassReconstruct().montage_exp_vs_sim_power_spectrum(power_spectrum,
            ideal_power_img)
        else:
            montage_side_by_side = ideal_power_img
            
        montage = np.copy(EMNumPy.em2numpy(montage_side_by_side))
        
        ax1.imshow(montage, cmap=cm.jet, interpolation='nearest')
        
        nyquist = 1 / (2 * self.pixelsize)
        
        ax1 = SpringDataExploreDraw().set_adjustable_tick_values(ax1, montage_side_by_side.get_ysize(),
        montage_side_by_side.get_xsize(), (-nyquist, nyquist), (-nyquist, nyquist))
        
        ax1 = self.format_ticklabels_to_six_and_xlabel_to_eight(ax1)
        ax1.set_ylabel('1/Angstrom', fontsize=8)
        
        reciprocal_angstrom_fine, ax2 = self.prepare_layer_line_plot(layerline_bessel_pairs, ax2, linex_fine)
        ax2 = self.format_second_layer_line_plot(ax2, reciprocal_angstrom_fine)

        return ax1, ax2
        
        
    def print_seglayer2lattice(self):
        layerline_bessel_pairs = self.get_layer_line_bessel_pairs()
        
        self.log.plog(10)

        lattice_plot = DiagnosticPlot()
        
        ax1 = lattice_plot.plt.subplot2grid((2,2), (0,0), colspan=1, rowspan=1)
        ax2 = lattice_plot.plt.subplot2grid((2,2), (1,0), colspan=1, rowspan=1)
        ax3 = lattice_plot.plt.subplot2grid((2,2), (0,1), colspan=1, rowspan=2)
        
        if self.analyze_power:
            plot_title = 'Experimental vs. theoretical power spectrum' 
        else:
            plot_title = 'Theoretical power spectrum' 
            
        ax1.set_title(plot_title, fontsize=8)
        
        self.log.plog(40)
        ax1, ax2 = self.plot_layer_lines_in_power_spectrum(layerline_bessel_pairs, ax1, ax2)
        ax3 = self.plot_helical_lattice(layerline_bessel_pairs, ax3)
        self.log.plog(90)
        
        lattice_plot.fig.savefig(self.outfile, dpi=600)
        
        return lattice_plot.fig
        
        
    def launch_seglayer2lattice_gui(self, feature_set):
        self.log.fcttolog()
        app = QApplication(sys.argv)
        gridexplor = SegLayer2LatticeGui(feature_set)
        gridexplor.show()
        app.exec_()
        

    def plot_layer_lines_to_power_and_lattice(self):
        self.log.fcttolog()
        
        if self.batch_mode:
            self.print_seglayer2lattice()
        else:
            self.launch_seglayer2lattice_gui(self.feature_set)
        
        self.log.endlog(self.feature_set)
        
def main():
    # Option handling
    parset = SegLayer2LatticePar()
    mergeparset = OptHandler(parset)

    ######## Program
    layer_lines = SegLayer2Lattice(mergeparset)
    layer_lines.plot_layer_lines_to_power_and_lattice()

if __name__ == '__main__':
    main()
