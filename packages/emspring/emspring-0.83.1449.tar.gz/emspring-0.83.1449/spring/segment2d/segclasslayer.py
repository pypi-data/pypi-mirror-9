# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to extract amplitudes and phases from desired layer lines of class averages
"""
from EMAN2 import Util, EMData, EMNumPy, periodogram
from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QApplication, QWidget, QComboBox, QStackedWidget, QSplitter, QFont, QToolTip
from collections import OrderedDict, namedtuple
from functools import partial
from matplotlib import cm
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
from scipy import interpolate
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.csgui import QTabWidgetCloseable, NumbersOptionsGuiWindow
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import DiagnosticPlot
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segclassexam import SegClassExam
from spring.segment2d.segmentexam import SegmentExam
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from spring.springgui.springdataexplore import SpringCommon, SpringDataExplore, SpringDataExploreDraw
from tabulate import tabulate
from utilities import model_blank
import numpy as np
import os
import sys

class SegClassLayerPar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'segclasslayer'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.segclasslayer_features = Features()
        self.feature_set = self.segclasslayer_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    

    def define_parameters_and_their_properties(self):
        self.feature_set = self.segclasslayer_features.set_class_avg_stack(self.feature_set)
        self.feature_set = self.segclasslayer_features.set_interactive_vs_batch_mode(self.feature_set)
        self.feature_set = self.segclasslayer_features.set_output_plot(self.feature_set, self.progname + '_diag.pdf',
                                                                       'Batch mode')

        self.feature_set = self.set_class_format_choice(self.feature_set)
        self.feature_set = self.segclasslayer_features.set_pixelsize(self.feature_set)
        self.feature_set = self.segclasslayer_features.set_exact_helix_width(self.feature_set)
        self.feature_set = self.segclasslayer_features.set_power_cutoff(self.feature_set)
        self.feature_set = self.segclasslayer_features.set_class_number_range_to_be_analyzed(self.feature_set)

        self.feature_set = self.set_layer_line_position(self.feature_set)
        self.feature_set = self.set_pad_option(self.feature_set)

    def define_program_states(self):
        self.feature_set.program_states['extract_layerlines']='Extracts layer lines from specified position'
        self.feature_set.program_states['visualize_layerlines']='Visualization of layer lines'


    def set_class_format_choice(self, feature_set):
        inp7 = 'Class format'
        feature_set.parameters[inp7] = str('real')
        feature_set.hints[inp7] = 'Choose whether class average stack is in real or power spectrum format.'
        
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['real', 'power'],
        'QComboBox')
        
        feature_set.level[inp7]='beginner'
        
        return feature_set


    def set_layer_line_position(self, feature_set):
        inp8 = 'Layer line positions'
        feature_set.parameters[inp8] = str('0.1234,0.234')
        feature_set.hints[inp8] = 'List of comma-separated values in reciprocal Angstrom'
        feature_set.properties[inp8] = feature_set.file_properties(1, ['*'], None)
        feature_set.level[inp8]='expert'
        feature_set.relatives[inp8]='Batch mode'
        
        return feature_set
    

    def set_pad_option(self, feature_set):
        inp9 = 'Pad option'
        feature_set.parameters[inp9] = bool(True)
        feature_set.hints[inp9] = 'If layer lines are part of a continuous lattice set, average will be padded so ' + \
        'that layer lines lie exactly on pixel grid'
        feature_set.level[inp9]='expert'
        feature_set.relatives[inp9]='Batch mode'
        
        return feature_set
        
    
class SegClassLayerGui(QWidget):

    def __init__(self, feature_set, parent = None):
        QWidget.__init__(self, parent)
        
        self.feature_set = feature_set
        self.properties = feature_set.properties
        
        self = SpringCommon().setup_spring_page_top(self, feature_set)
        
        self.segclasslayer = SegClassLayer(self.feature_set)
        
        start_cls, end_cls = self.segclasslayer.classno_range
        self.classes = ['{0} - {1:03}'.format(os.path.basename(self.segclasslayer.infile), each_class) \
                        for each_class in list(range(start_cls, end_cls + 1))]
    
        self.stackedComboBox = QComboBox()
        self.stackedComboBox.addItems(self.classes)
        self.layout.addWidget(self.stackedComboBox, 0, 3, 1, 1)
        
        self.nyquist = 1 / (2 * self.segclasslayer.pixelsize)
        self.angstrom_str = NumbersOptionsGuiWindow().convert_angstrom_string('Angstrom')
        
        self.stackedWidget = QStackedWidget()
        class_img = EMData()
        self.class_plot = DiagnosticPlot()
        self.class_data = []
        self.tabwidgets = []
        for each_class in list(range(start_cls, end_cls + 1)):
            self.splitter = QSplitter(Qt.Horizontal)
            self.splitter_vert = QSplitter(Qt.Vertical)
            
            class_fig, class_img, cls_ps_np = self.segclasslayer.prepare_class_img_and_power_spectrum(each_class,
            class_img, self.class_plot)
            
            self.class_img_canvas = SpringDataExplore(class_fig)
            
            dummy_grid = np.array([(-self.nyquist, -self.nyquist), (-self.nyquist, self.nyquist), (self.nyquist,
            self.nyquist), (self.nyquist, -self.nyquist)]).reshape((2,2,2))
            
            self.class_ps_canvas = SpringDataExplore()
            self.class_ps_canvas.on_draw(cls_ps_np, dummy_grid, [''] + ['1/Angstrom']*2, '2d')
            
            self.splitter_vert.addWidget(self.class_img_canvas)
            self.splitter_vert.addWidget(self.class_ps_canvas)
            self.splitter.addWidget(self.splitter_vert)
            
            self.class_ps_canvas.main_frame.setToolTip('Mouse button to display amplitude and phases of ' + \
            'corresponding layer line.')
            
            self.class_ps_canvas.picked_left_point.connect(partial(self.add_new_tab_with_layer_line_profile))
            self.class_ps_canvas.picked_middle_point.connect(partial(self.add_new_tab_with_layer_line_profile))
            
            amp_img, phase_img = self.segclasslayer.prepare_amplitude_and_phase_image(class_img)
            layer_profile = self.segclasslayer.get_amplitude_and_phase_at_position(amp_img, phase_img, 1)
            
            container = self.segclasslayer.make_named_tuple_amp_phase_images()
            max_amp = 1.1 * max(np.append(layer_profile.left_amp, layer_profile.right_amp))
            self.class_data.append(container(amp_img, phase_img, max_amp))
            
            fig = self.prepare_layer_line_profile_plot(self.class_plot, layer_profile, max_amp)
            
            self.layer_canvas = SpringDataExplore(fig)    
            
            self.tabWidget = QTabWidgetCloseable()
            self.tabWidget.addTab(self.layer_canvas, 'Equator')
            self.tabwidgets.append(self.tabWidget)
            self.splitter.addWidget(self.tabWidget)
            self.stackedWidget.addWidget(self.splitter)
        
        self.fourier_dim = amp_img.get_ysize() / 2
        self.connect(self.stackedComboBox, SIGNAL('currentIndexChanged(int)'), self.stackedWidget.setCurrentIndex)
        self.layout.addWidget(self.stackedWidget, 2, 0, 2, 5)
        
        self.setLayout(self.layout)
        
        self.setMouseTracking(True)
 

    def enterEvent(self, event):
        QToolTip.setFont(QFont('Courier', 8))
        

    def add_new_tab_with_layer_line_profile(self, index_pair):
        y_pos = index_pair[1]
        fourier_pixel = int(abs(y_pos - self.fourier_dim)) + 1
        fourier_pix_A = fourier_pixel * self.nyquist / self.fourier_dim 
            
        cur_id = self.stackedComboBox.currentIndex()
        amp_img = self.class_data[cur_id].amp
        phase_img = self.class_data[cur_id].phase
        max_amp = self.class_data[cur_id].max_amp
        
        layer_profile = self.segclasslayer.get_amplitude_and_phase_at_position(amp_img, phase_img,
        fourier_pixel)
        
        fig = self.prepare_layer_line_profile_plot(self.class_plot, layer_profile, max_amp)
        
        self.layer_canvas = SpringDataExplore(fig)    

        besselorder, primarymax, primarymaxwidth = self.segclasslayer.get_bessel_table_quant(self.segclasslayer.helixwidth)

        tool_str = tabulate([['{0}'.format('Bessel order')] + besselorder, 
                             ['{0}'.format('Primary max at 2*Pi*r*R')] + primarymax, 
                             ['{0}'.format('At helix radius (R={0} A)'.format(self.segclasslayer.helixwidth / 2))] + primarymaxwidth],
                            tablefmt='grid')
        
        self.layer_canvas.main_frame.setToolTip(tool_str)

        title = '{0:.04} 1/{1}'.format(fourier_pix_A, self.angstrom_str)
        self.tabwidgets[cur_id].addTab(self.layer_canvas, title)
        self.tabwidgets[cur_id].setCurrentIndex(self.tabwidgets[cur_id].indexOf(self.layer_canvas))
        
        
    def prepare_layer_line_profile_plot(self, class_plot, layer_profile, ampmax=None):
        arrresolution = SegmentExam().make_oneoverres(layer_profile.left_phase, self.segclasslayer.pixelsize)
        fig = class_plot.create_next_figure()
        ax1 = fig.add_subplot(111)
        
        ax1, ax2 = self.segclasslayer.add_amplitude_and_phase_difference_to_plot(layer_profile,
            arrresolution, ax1, ampmax)
        
        self.segclasslayer.add_labels_to_plot(ax1, ax2)
        
        return fig

        
class SegClassLayerExtract(object):
    """
    * Class that holds functions for extracting layer lines including amplitude and phase from class averages

    * __init__ Function to interpret multi-input parameters

    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.infilestack = p['Class average stack']
            self.infile = self.infilestack
            self.batch_mode = p['Batch mode']
            self.outfile = p['Diagnostic plot']
            self.class_format = p['Class format']
            self.pixelsize = p['Pixel size in Angstrom']
            self.helixwidth = p['Precise helix width in Angstrom']
            self.helixwidthpix = int(round(self.helixwidth/self.pixelsize))
            self.rescutoff = p['Power spectrum resolution cutoff in 1/Angstrom']
            self.classno_range = p['Class number range to be analyzed']
            self.layerlines = p['Layer line positions'].split(',')
            self.padoption = p['Pad option']

            self.binfactor = int(round(1/(self.rescutoff*self.pixelsize*2)))

            self.stack = EMData()
            self.stack.read_image(self.infilestack, 0)
            self.segsizepix = self.stack.get_xsize()

            if self.binfactor > 1:
                self.infilestack, self.segsizepix, self.helixwidthpix, self.pixelsize = \
                SegmentExam().apply_binfactor(self.binfactor, self.infilestack, self.segsizepix, self.helixwidthpix,
                self.pixelsize)


    def compute_phase_difference(self, leftph, rightph):
        """
        >>> from spring.segment2d.segclasslayer import SegClassLayer
        >>> s = SegClassLayer()
        >>> s.compute_phase_difference(np.array([50]), np.array([-120]))
        array([ 170.])
        >>> s.compute_phase_difference(np.array([170]), np.array([180]))
        array([-10.])
        >>> s.compute_phase_difference(np.array([-70]), np.array([170]))
        array([ 120.])
        """
        phasediffarr = np.array([])
        
        for each_left, each_right in zip(leftph, rightph):
            phase_diff_plus360 = each_left + 360 - each_right
            phase_diff = each_left - each_right
            phase_diff_minus360 = each_left - each_right - 360
            
            dist = np.array([phase_diff_plus360, phase_diff, phase_diff_minus360])
            
            phasediffarr = np.append(phasediffarr, dist[np.argmin(np.abs(dist))])
            
        return phasediffarr
    
    
    def make_named_tuple_layer_line(self):
        return namedtuple('layer_line', 'left_amp right_amp left_phase right_phase')
    
    
    def center_leftside(self, leftarr, rightarr):
        """
        * Function to flip and center left image side with respect to right image side and complement first pixel

        #. Input: left-side amplitude, right-side amplitude
        #. Output: complemented and mirrored left-side amplitudes
        #. Usage: leftarrflip = center_leftside(leftarr, rightarr)
        """
        # flip left side
        leftarrflip = np.flipud(leftarr)

        leftarrflip = np.delete(leftarrflip, -1)
        leftarrflip = np.insert(leftarrflip, 0, rightarr[0])

        return leftarrflip
    

    def retrieve_ampnphases(self, llampprofile, llphprofile):
        """
        * Function to retrieve amplitude and phases along a layer line of interest

        #. Input: layerline amplitude profile, layerline phase profile
        #. Output: leftamplitude, rightamplitude and phase difference 
        #. Usage: leftamp, rightamp, phasediff = retrieve_ampnphases(llampprofile, llphprofile)
        """

        llampprofilearr = np.copy(EMNumPy.em2numpy(llampprofile))
        llphprofilearr = np.copy(EMNumPy.em2numpy(llphprofile))
        # split in half
        leftamp, rightamp = np.split(llampprofilearr, 2)
        leftph, rightph = np.split(llphprofilearr, 2)

        leftamp = self.center_leftside(leftamp, rightamp)
        leftph = self.center_leftside(leftph, rightph)

        layer = self.make_named_tuple_layer_line()
        
        return layer(leftamp, rightamp, np.rad2deg(leftph), np.rad2deg(rightph))
    

    def prepare_amplitude_and_phase_image(self, avg):
        if self.class_format == 'real':
            fftavg = avg.do_fft()
            amplitude_of_avg = fftavg.get_fft_amplitude()
            phase_of_average = fftavg.get_fft_phase()
        elif self.class_format == 'power':
            avg_np = np.copy(EMNumPy.em2numpy(avg))
            avg_np = np.roll(avg_np, avg.get_xsize() / 2, 0)
            amplitude_of_avg = EMNumPy.numpy2em(np.copy(avg_np))
            phase_of_average = model_blank(avg.get_xsize(), avg.get_ysize(), 1)

        return amplitude_of_avg, phase_of_average


    def get_amplitude_and_phase_at_position(self, amplitude_of_avg, phase_of_average, lineimgpos):
        llampprofile = amplitude_of_avg.get_row(lineimgpos)
        llphprofile = phase_of_average.get_row(lineimgpos)
        layer = self.retrieve_ampnphases(llampprofile, llphprofile)
        
        return layer
    

    def extract_layer_line_amplitude_and_phases(self, avg, layerlinespix):
        amplitude_of_avg, phase_of_average = self.prepare_amplitude_and_phase_image(avg)
        
        layer_profiles = []
        for self.line in layerlinespix:
            # compute pixel position
            lineimgpos = int(self.line)
            
            layer = self.get_amplitude_and_phase_at_position(amplitude_of_avg,
            phase_of_average, lineimgpos)
            
            layer_profiles.append(layer)
            
        return layer_profiles
            

    def pad_avg(self, layerlines, classno):
        """
        * Function to pad average to fit layer lines directly onto pixel row (pads classavg and adjusts segmentsize)

        #. Input: list of layerlines in pixel
        #. Output: list of adjusted layerlines in pixel
        #. Usage: layerlines = pad_avg(layerlines)
        """

        layerorder = np.arange(len(layerlines))
        slope, icept = np.polyfit(layerorder, layerlines, 1)

        if 100 < self.segsizepix < 150:
            uproundedslope = round(slope + 5)
        elif self.segsizepix < 100:
            uproundedslope = round(slope + 10)
        else:
            uproundedslope = round(slope + 1)

        pdsegsizepix = int(round(self.segsizepix*uproundedslope)/slope)

        if (pdsegsizepix)%2 != 0:
            pdsegsizepix = pdsegsizepix + 1

        img = Util.pad(self.avg, pdsegsizepix, pdsegsizepix, 1, 0, 0, 0, '0' )
        newlayerlines = [uproundedslope*(layerorder + 1) for layerorder, line in enumerate(layerlines)]

        self.avg = img
        layerlinespix = newlayerlines
        self.segsizepix = pdsegsizepix

        self.log.ilog('Class {classno} will be padded to {xsize} x {ysize} pixels'.format(classno=classno,
        xsize=pdsegsizepix, ysize=pdsegsizepix))
        
        self.log.ilog('Layer lines are plotted from Fourier pixels:{0}'.format(layerlinespix))

        return layerlinespix
        
        
class SegClassLayerGuiSupport(SegClassLayerExtract):
    def make_named_tuple_amp_phase_images(self):
        return namedtuple('image', 'amp phase max_amp')
    
    
    def prepare_class_img_and_power_spectrum(self, each_class, class_img, class_plot):
        class_img.read_image(self.infilestack, each_class)
        class_img_np = np.copy(EMNumPy.em2numpy(class_img))
        segment_size = class_img.get_xsize()
        
        fig = class_plot.create_next_figure()
        ax1 = fig.add_subplot(111)
        ax1.imshow(class_img_np, cmap=cm.gray, interpolation='nearest')
        
        img_dim_half = self.pixelsize * segment_size / 2 
        
        ax1 = SpringDataExploreDraw().set_adjustable_tick_values(ax1, class_img.get_ysize(), class_img.get_xsize(),
        (-img_dim_half, img_dim_half), (-img_dim_half, img_dim_half))
        
        [t.set_fontsize(6) for t in ax1.get_xticklabels() + ax1.get_yticklabels()]
        
        ax1.set_xlabel('Angstrom', fontsize=8)
        ax1.set_ylabel('Angstrom', fontsize=8)
        
        if self.class_format == 'real':
            helixmask = SegmentExam().make_smooth_rectangular_mask(self.helixwidthpix, segment_size * 0.8,
            segment_size, 0.15)
            
            padsize = 4
            class_img = Util.pad(class_img * helixmask, padsize * segment_size, padsize * segment_size, 1, 0, 0, 0, '0')
            
            cls_ps = periodogram(class_img)
            cls_ps.process_inplace('normalize')
            cls_ps_np = np.copy(EMNumPy.em2numpy(cls_ps))
        elif self.class_format == 'power':
            cls_ps_np = np.copy(class_img_np)
        
        return fig, class_img, cls_ps_np 
    

class SegClassLayer(SegClassLayerGuiSupport):
    def add_amplitude_and_phase_difference_to_plot(self, layer_profile, arrresolution, ax1, ampmax=None):
        ax1.plot(arrresolution, layer_profile.left_amp, label='Left quadrant')
        ax1.plot(arrresolution, layer_profile.right_amp, label='Right quadrant amplitudes')
        if ampmax is not None:
            ax1.set_ylim(0, ampmax)
        ax1.set_xlim(arrresolution[0], arrresolution[-1])
        ax1.set_yticks([])
        
        ax2 = ax1.twinx()
        ax2.set_xlim(arrresolution[0], arrresolution[-1])
        ax2.set_ylim(-190, 230)
        
        phase_diff = self.compute_phase_difference(layer_profile.left_phase, layer_profile.right_phase)
        ax2.plot(arrresolution, phase_diff, 'r.', label='Phase difference left/right')
        
        ax2.fill([0,arrresolution[-1], arrresolution[-1], 0], [-90,-90, 90, 90], 'grey', alpha=0.05, 
        label='Even Bessel order')
#        ax2.plot(arrresolution, layer_profile.left_phase, '.', label='phase left')
#        ax2.plot(arrresolution, layer_profile.right_phase, 'x', label='phase right')
        ax2.set_yticks([-180, -90, 0, 90, 180])
        [t.set_fontsize(6) for t in ax1.get_xticklabels() + ax1.get_yticklabels() + ax2.get_yticklabels()]
        
        return ax1, ax2
    

    def determine_first_maxima_computationally(self, layer_profile, ax1):
        finestep = (self.arrresolution[1] - self.arrresolution[0]) / 100
        resarrpol = np.arange(self.arrresolution[0], self.arrresolution[-1], finestep)
        
        t = interpolate.splrep(self.arrresolution, layer_profile.left_amp, k=3, s=0)
        leftamppol = interpolate.splev(resarrpol, t)
        ind, val = SegmentExam().find_local_extrema(leftamppol)
        leftmax = resarrpol[ind[-1]]
        leftmaxval = val[-1]
        ax1.text(leftmax, 0.2 * leftmaxval, 'Max {0:.4}'.format(leftmax), fontsize=6)
        
        t = interpolate.splrep(self.arrresolution, layer_profile.right_amp, k=3, s=0)
        rightamppol = interpolate.splev(resarrpol, t)
        ind, val = SegmentExam().find_local_extrema(rightamppol)
        rightmax = resarrpol[ind[-1]]
        ax1.text(rightmax, 0.4 * leftmaxval, 'Max {0:.4}'.format(rightmax), fontsize=6)
        

    def add_labels_to_plot(self, ax1, ax2):
        ax1.set_xlabel('Resolution in 1/Angstrom', fontsize=8)
        ax1.set_ylabel('LL amplitudes', fontsize=8)
        ax1.legend(loc='upper left', ncol=1, prop=FontProperties(size='x-small'))
        
        ax2.set_ylabel('LL phase difference (degrees)', fontsize=8)
        ax2.legend(loc='upper right', ncol=1, prop=FontProperties(size='x-small'))
        
        return ax1, ax2
    

    def plot_individual_layer_lines(self, diag_plot, layerlines, layer_profiles):
        plots = OrderedDict()
        for self.order, line in enumerate(layerlines):
            llplot = 'plot{0}'.format(self.order)
            plots[llplot] = diag_plot.plt.subplot2grid((len(layerlines) + 1, 1), (self.order, 0), colspan=1, rowspan=1)
            # plot figure
            plots[llplot].set_title('{order}. layer line ({res} 1/Angstrom)'.format(order=self.order, res=line),
            fontsize=9)
            
            llplottwin = 'plot{0}twin'.format(self.order)
            plots[llplot], plots[llplottwin] = self.add_amplitude_and_phase_difference_to_plot(layer_profiles[self.order],
            self.arrresolution, plots[llplot])
            
            self.determine_first_maxima_computationally(layer_profiles[self.order], plots[llplot])
            
            plots[llplottwin].minorticks_on()
            plots[llplottwin].grid(True)
            self.log.ilog('Layer line {order} was visualized left and right quadrant amplitudes and phase ' + \
            'difference'.format(order=self.order))
            # last plot
            if self.order == (len(layerlines) - 1):
                self.add_labels_to_plot(plots[llplot], plots[llplottwin])
                
                tbl = diag_plot.plt.subplot2grid((len(self.layerlines) + 1,1), (self.order + 1,0), colspan=1, rowspan=1,
                frameon=False)
        
                self.add_besseltable(diag_plot, tbl)
                self.log.ilog('Final Bessel order lookup table added')
                
        return diag_plot
    

    def determine_max(self):
        """
        * Function to determine maximum of layer line
        """
        ind1 = np.lexsort((self.arrresolution, self.leftamp[self.order]))
        ind2 = np.lexsort((self.arrresolution, self.rightamp[self.order]))
        if self.leftamp[self.order][ind1[-1]] > self.rightamp[self.order][ind2[-1]]:
            self.maxx = self.arrresolution[ind1[-1]]
            self.maxy = self.leftamp[self.order][ind1[-1]]
        else:
            self.maxx = self.arrresolution[ind2[-1]]
            self.maxy = self.rightamp[self.order][ind2[-1]]

        return self.maxx, self.maxy


    def get_bessel_table_quant(self, helixwidth):
        """
        >>> from spring.segment2d.segclasslayer import SegClassLayer
        >>> s = SegClassLayer()
        >>> s.get_bessel_table_quant(100) #doctest: +NORMALIZE_WHITESPACE
        ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 
        [0.0, 1.8, 3.1, 4.2, 5.3, 6.4, 7.5, 8.6, 9.6, 10.7, 11.8, 12.8, 13.9, 
        14.9, 16.0, 17.0, 18.1, 19.1, 20.1, 21.2], [0.0, 0.006, 0.01, 0.013, 
        0.017, 0.02, 0.024, 0.027, 0.031, 0.034, 0.038, 0.041, 0.044, 0.047, 
        0.051, 0.054, 0.058, 0.061, 0.064, 0.067])
        """
        primarymax = SegClassReconstruct().get_list_of_bessel_order_maxima(20)
        primarymax = np.around(primarymax, decimals=1)

        primarymaxwidth = primarymax / (2 * np.pi * helixwidth / 2.0)
        primarymaxwidth = np.around(primarymaxwidth, decimals=3)

        besselorder = np.arange(len(primarymax), dtype=int)

        return besselorder.tolist(), primarymax.tolist(), primarymaxwidth.tolist()


    def add_besseltable(self, diag_plot, tbl, helixwidth=None):
        """
        * Function to add Bessel order look-up table to printout

        #. Input: helix width in Angstrom
        #. Output: table with Bessel order and their corroesponding primary maximum and expected \
            maximum for helix width
        #. Usage: add_besseltable(helixwidth)
        """
        if helixwidth is None: helixwidth = self.helixwidth

        besselorder, primarymax, primarymaxwidth = self.get_bessel_table_quant(helixwidth)

        tbl.set_title('Bessel order look-up table (from Stewart 1988)', fontsize=10)
        tbl.xaxis.set_visible(False)
        tbl.yaxis.set_visible(False)
        
        rowLabels = ['Bessel order', 
        'Primary maximum at 2*Pi*r*R', 'at helix radius \nof R={width} Angstrom'.format(width=helixwidth/2)]
        
        cellText = np.row_stack((besselorder, primarymax, primarymaxwidth))

        the_table = diag_plot.plt.table(cellText=cellText, rowLabels=rowLabels, loc='center')
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(4)


    def extract_layerlines(self, infilestack, classno):
        self.log.fcttolog()

        self.avg = EMData()
        self.avg.read_image(infilestack, classno)

        layerlines = np.array([float(line.strip()) for line in self.layerlines])
        layerlinespix = np.round(self.pixelsize*self.segsizepix*layerlines)

        if self.padoption is True:
            layerlinespix = self.pad_avg(layerlinespix, classno)

        layer_profiles = self.extract_layer_line_amplitude_and_phases(self.avg, layerlinespix)

        return layerlines, layer_profiles
        
        
    def visualize_layerlines(self, figno, layerlines, layer_profiles):
        """
        * Function to visualize layer lines

        #. Input: figurenumber, list of layerlines (1/Angstrom), list of left-side centered amplitude \
            arrays, list of right-side centered amplitude arrays, list of phasedifference arrays
        #. Output: figure with stacked amplitude profile and phase difference plots
        #. Usage: figure = visualize_layerlines(figno, layerlines, leftamp, rightamp, phasediff)
        """
        self.log.fcttolog()
        layerline_plot = DiagnosticPlot()
        layerline_plot.plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.65)
        
#        self.fig = layerline_plot.add_header_and_footer(self.feature_set)

        self.arrresolution = SegmentExam().make_oneoverres(layer_profiles[0].left_phase, self.pixelsize)
 
        layerline_plot = self.plot_individual_layer_lines(layerline_plot, layerlines, layer_profiles)

        return layerline_plot.fig


    def print_layerlines_as_requested(self):
        if os.path.splitext(self.outfile)[-1].endswith('pdf'):
            self.pdf = PdfPages(self.outfile)
        self.classno_range = SegClassExam().check_maximum_class_number(self.infilestack, self.classno_range)
        classno_start, classno_end = self.classno_range
        self.log.plog(10)
        
        classes_iter = list(range(classno_start, classno_end + 1))
        for each_class_index in classes_iter:
            if len(classes_iter) > 1:
                plot_file, self.feature_set = SegClassExam().rename_plot_title_for_multiple_classes(self.infile, 
                self.outfile, classno_start, classno_end, each_class_index, self.feature_set)
            else:
                plot_file = self.outfile
            
            layerlines, layer_profiles = self.extract_layerlines(self.infilestack, each_class_index)
            self.fig = self.visualize_layerlines(each_class_index, layerlines, layer_profiles)
            
            if os.path.splitext(self.outfile)[-1].endswith('pdf'):
                self.pdf.savefig(self.fig)
            elif not os.path.splitext(self.outfile)[-1].endswith('pdf') and classno_end != classno_start:
                self.fig.savefig(plot_file, dpi=600)
            else:
                self.fig.savefig(self.outfile, dpi=600)
            self.log.plog(100 * (each_class_index + 1) / (classno_end + 1))
        
        if os.path.splitext(self.outfile)[-1].endswith('pdf'):
            self.pdf.close()


    def launch_segclasslayer_gui(self, feature_set):
        self.log.fcttolog()
        app = QApplication(sys.argv)
        gridexplor = SegClassLayerGui(feature_set)
        gridexplor.show()
        app.exec_()
        

    def extract_and_visualize_layer_lines(self):
        if self.batch_mode:
            self.print_layerlines_as_requested()
        else:
            self.launch_segclasslayer_gui(self.feature_set)
            
        self.log.endlog(self.feature_set)
        
def main():
    # Option handling
    parset = SegClassLayerPar()
    mergeparset = OptHandler(parset)

    ######## Program
    stack = SegClassLayer(mergeparset)
    stack.extract_and_visualize_layer_lines()

if __name__ == '__main__':
    main()
