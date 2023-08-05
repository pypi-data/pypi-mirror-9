# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to examine all excised in-plane rotated segments and compute their collapsed (1D) and 
2D power spectrum and width profile of helices
"""
from EMAN2 import Util, EMData, EMUtil, periodogram, EMNumPy
from filter import filt_gaussl
from fundamentals import image_decimate, fshift
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter
from morphology import threshold_maxval, threshold_to_zero, binarize
from spring.csinfrastr.csdatabase import SpringDataBase, base, SegmentTable, HelixTable
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import DiagnosticPlot, Temporary, OpenMpi
from spring.csinfrastr.csreadinput import OptHandler
from spring.micprgs.scansplit import Micrograph
from spring.segment2d.segmentselect import SegmentSelect
from statistics import add_series, ccc
from tabulate import tabulate
from utilities import model_blank, model_circle
import matplotlib.cm as cm
import numpy as np
import os
import shutil

class SegmentExamPar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'segmentexam'
        self.proginfo = __doc__
        self.code_files = [self.progname, self.progname + '_mpi']

        self.segmentexam_features = Features()
        self.feature_set = self.segmentexam_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    
    def define_parameters_and_their_properties(self):
        self.feature_set = self.segmentexam_features.set_inp_stack(self.feature_set)
        self.feature_set = self.segmentexam_features.set_output_plot(self.feature_set, self.progname + '_diag.pdf')
        
        self.feature_set = self.segmentexam_features.set_output_power_spectrum(self.feature_set)
        self.feature_set = self.segmentexam_features.set_enhance_power_option(self.feature_set)
        self.feature_set = self.segmentexam_features.set_output_enhanced_power_spectrum(self.feature_set)
        self.feature_set = self.segmentexam_features.set_pixelsize(self.feature_set)
        self.feature_set = self.segmentexam_features.set_helix_width(self.feature_set)
        self.feature_set = self.segmentexam_features.set_power_cutoff(self.feature_set)
        self.feature_set = self.set_compute_layer_line_correlation(self.feature_set)
        self.feature_set = self.set_layer_line_region(self.feature_set)
        self.feature_set = self.set_power_spectrum_reference(self.feature_set)
        self.feature_set = self.segmentexam_features.set_input_power_spectrum(self.feature_set,
        'Reference power spectrum', 'expert')
        
        self.feature_set = self.segmentexam_features.set_spring_path_segments(self.feature_set)

        self.feature_set = self.segmentexam_features.set_selection_criteria_from_segment_table(self.feature_set)
        
        self.feature_set = self.segmentexam_features.set_mpi(self.feature_set)
        self.feature_set = self.segmentexam_features.set_ncpus(self.feature_set)
        self.feature_set = self.segmentexam_features.set_temppath(self.feature_set)

    def define_program_states(self):
        self.feature_set.program_states['add_power_spectra_from_verticalized_stack']='Addition of in-plane rotated ' + \
        'power spectra'
        
        self.feature_set.program_states['determine_width']='Determine width of helix by projection along helical axis'
        
        self.feature_set.program_states['visualize_power_avg_and_width_analysis']='Visualization of width and power ' +\
        'spectra'


    def set_compute_layer_line_correlation(self, feature_set):
        inp9 = 'Compute layer-line correlation option'
        feature_set.parameters[inp9] = bool(False)
        feature_set.hints[inp9] = 'Compute layer line correlation of individual power spectra with average power ' + \
        'spectrum and store this correlation value in the Spring database (spring.db).'
        feature_set.level[inp9]='expert'
        
        return feature_set
    
    
    def set_power_spectrum_reference(self, feature_set):
        inp9 = 'Reference power spectrum'
        feature_set.parameters[inp9] = bool(False)
        feature_set.hints[inp9] = 'Choose whether to provide a reference power spectrum for layer-line ' + \
        'correlation. Make sure that the image dimensions agree with the input stack or with the binned input ' + \
        'stack. If not chosen, sum of power spectra from input stack will be used.'
        feature_set.level[inp9]='expert'
        feature_set.relatives[inp9]='Compute layer-line correlation option'
        
        return feature_set
    
    
    def set_layer_line_region(self, feature_set):
        inp7 = 'Layer-line region in 1/Angstrom'
        feature_set.parameters[inp7]=((0.03, 0.035))
        feature_set.hints[inp7]='Layer-line region to correlate individual power spectrum with sum of all power ' + \
        'spectra.'
        feature_set.properties[inp7]=feature_set.Range(0, 1, 0.001)
        feature_set.relatives[inp7]=(('Compute layer-line correlation option', 'Compute layer-line correlation option'))
        feature_set.level[inp7]='expert'
        
        return feature_set


        
class SegmentExamPower(object):
    """
    * Class that holds functions for examining segments from micrographs

    * __init__ Function to interpret multi-input parameters

    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.infilestack = p['Image input stack']
            self.infile=self.infilestack
            self.outfile = p['Diagnostic plot']
            
            self.spring_path = p['spring.db file']
            
            self.power_img = p['Power spectrum output image']
            self.enhanced_power_option = p['Enhanced power spectrum option']
            self.power_enhanced_img = p['Enhanced power spectrum output image']
            self.pixelsize = p['Pixel size in Angstrom']
            self.helixwidth = p['Estimated helix width in Angstrom']
            self.helixwidthpix = int(round(self.helixwidth/self.pixelsize))
            self.rescutoff = p['Power spectrum resolution cutoff in 1/Angstrom']
            
            self.layer_ccc_option = p['Compute layer-line correlation option']
            self.res_ccc_range = p['Layer-line region in 1/Angstrom']
            self.power_reference = p['Reference power spectrum']
            self.power_input = p['Power spectrum input image']

            self = SegmentSelect().define_selection_parameters_from_segment_table(self, p)

            self.mpi_option = p['MPI option']
            self.cpu_count = p['Number of CPUs']
            self.temppath = p['Temporary directory']

            self.binfactor = int(round(1/(self.rescutoff*self.pixelsize*2)))

            self.stack = EMData()
            self.stack.read_image(self.infilestack, 0)
            self.segsizepix = self.stack.get_xsize()


    def bin_image_stack_by_binfactor(self, infilestack, binfactor, image_list=None, binned_stack=None):
        self.log.fcttolog()
        if image_list is None:
            image_list = list(range(EMUtil.get_image_count(infilestack)))
        if binned_stack is None:
            binned_stack = os.path.splitext(os.path.basename(infilestack))[0] + '{0}binned'.format(binfactor) + \
            os.path.splitext(infilestack)[-1]
        
        log_info = 'The following segments were binned by a factor {0} for further analysis and '.format(binfactor) + \
        'saved in {0}.\n(Local_id, Segment_id)\n'.format(binned_stack)
        segment = EMData()
        for each_local_id, each_seg_id in enumerate(image_list):
            segment.read_image(infilestack, each_seg_id)
            if binfactor > 1:
                segment = image_decimate(segment, binfactor, fit_to_fft=False)
            segment.write_image(binned_stack, each_local_id)
            log_info += '({0}, {1}) '.format(each_local_id, each_seg_id)
        
        self.log.ilog(log_info)
        segsizepix = segment.get_xsize()
        
        return binned_stack, segsizepix
    

    def apply_binfactor(self, binfactor, infilestack, segsizepix, helixwidthpix, pixelsize, image_list=None,
    outfile=None):
        """
        * Function to reduce stack and modify pixelsize according to desired binfactor

        #. Input: binfactor, infile stack to be binned, segment size (pixel), helix width (pixel) \
            pixelsize
        #. Output: binned stack, adjusted segment size (pixel), helix width (pixel), pixelsize 
        #. Usage: binned stack, segsizepix, helixwidth, pixelsize = apply_binfactor(binfactor, \
            infilestack, segsizepix, helixwidth, pixelsize)
            
        """

        binned_stack, segsizepix = self.bin_image_stack_by_binfactor(infilestack, binfactor, image_list, outfile)
            
        helixwidthpix = helixwidthpix/binfactor
        pixelsize = pixelsize * binfactor

        return binned_stack, segsizepix, helixwidthpix, pixelsize
    

    def enhance_power(self, avg_periodogram=None, pixelsize=None):
        """
        * Function to visually enhance power spectrum by compensating for decay of amplitude

        #. Input: power spectrum
        #. Output: enhanced power spectrum
        #. Usage: avg_periodogram_enhanced = enhance_power(avg_periodogram)
        
        """
        if avg_periodogram is None: 
            avg_periodogram = self.avg_periodogram
        if pixelsize is None: 
            pixelsize = self.pixelsize

        rotavg = avg_periodogram.rotavg_i()
        segment_size = avg_periodogram.get_xsize()
        mask = model_circle(segment_size/2, segment_size, segment_size)
        stat = Micrograph().get_statistics_from_image(rotavg, mask)
        if pixelsize <= 5:
            avg_periodogram_enhanced = avg_periodogram / (rotavg + 0.001*(stat.max - stat.avg))
        elif 5 < pixelsize < 10:
            avg_periodogram_enhanced = avg_periodogram / (rotavg + 0.01*(stat.max - stat.avg))
        elif pixelsize >= 10:
            avg_periodogram_enhanced = avg_periodogram / rotavg

        return avg_periodogram_enhanced
    

    def collapse_power(self, addpowimg):
        """
        * Function to project powerspectrum onto 1D plot to determine layer line position

        #. Input: power spectrum, segment size (pixel)
        #. Output: collapsed profile
        #. Usage: add1dimg = collapse_power(avg_periodogram)
        
        """
        segsizepix = addpowimg.get_xsize()

        circmask = model_circle(segsizepix - 1, segsizepix, segsizepix)
        maskaddpowimg = circmask * addpowimg
        halfaddpowimg = Util.window(maskaddpowimg, segsizepix, segsizepix/2, 1, 0,segsizepix/4, 0)
        img1dline = EMData()
        self.add1dimg = model_blank( segsizepix/2, 1, 1, 0)
        for eachCol in range(segsizepix/4, segsizepix*3/4, 1):
            img1dline = halfaddpowimg.get_col(eachCol)
            self.add1dimg += img1dline

        return self.add1dimg
    

    def project_helix(self, seg=None):
        """
        * Function to project image along helical axis by adding rows of image

        #. Input: segment
        #. Output: projected profile
        #. Usage: rowsaddimg = project_helix(seg)
        
        """
        if seg is None: 
            seg = self.seg

        number_of_rows = seg.get_ysize()
        self.rowsaddimg = model_blank(seg.get_xsize(), 1, 1, 0)
        for eachRow in range(number_of_rows):
            self.rowsaddimg += seg.get_row(eachRow)

        return self.rowsaddimg
    
    def project_normal_to_helix(self, seg=None):
        """
        * Function to project image perpendicular to helical axis by adding columns of image

        #. Input: segment
        #. Output: projected profile
        #. Usage: columnsaddimg = project_normal_to_helix(seg)
        
        """
        if seg is None: seg = self.seg

        number_of_columns = seg.get_xsize()
        self.columnsaddimg = model_blank(seg.get_ysize(), 1, 1, 0)
        for eachColumn in range(number_of_columns):
            self.columnsaddimg += seg.get_col(eachColumn)

        return self.columnsaddimg


class SegmentExamMask(SegmentExamPower):

    def limit_width_falloff_to_available_pixels_outside_binary_mask(self, helix_width_in_pixel, helix_height_in_pixel,
    segment_size_in_pixel, width_falloff):
        if (2 * segment_size_in_pixel * width_falloff + helix_width_in_pixel) > segment_size_in_pixel:
            width_falloff = float((segment_size_in_pixel - helix_width_in_pixel) / 2) / segment_size_in_pixel
        if helix_width_in_pixel >= segment_size_in_pixel:
            width_falloff = float((segment_size_in_pixel - helix_height_in_pixel) / 2) / segment_size_in_pixel
            
        return width_falloff
    

    def insure_mirror_symmetry_of_mask_parameters(self, helix_width_in_pixel, helix_height_in_pixel):
        helix_width_is_odd = (helix_width_in_pixel) % 2
        if helix_width_is_odd == 1:
            helix_width_in_pixel += 1
        helix_height_is_odd = (helix_height_in_pixel) % 2
        if helix_height_is_odd:
            helix_height_in_pixel += 1
            
        return helix_width_in_pixel, helix_height_in_pixel


    def make_binary_shape_mask(self, helix_width_in_pixel, helix_height_in_pixel, segment_size_in_pixel):
        if helix_width_in_pixel > segment_size_in_pixel and helix_height_in_pixel < segment_size_in_pixel:
            innermask = model_blank(int(segment_size_in_pixel), int(round(helix_height_in_pixel)), 1, 1)
            error_message = 'Helix is wider than specified segment size. Masking only in helix height.'
            self.log.wlog(error_message)
        elif helix_width_in_pixel > segment_size_in_pixel and helix_height_in_pixel > segment_size_in_pixel:
            innermask = model_blank(int(segment_size_in_pixel), int(round(segment_size_in_pixel)), 1, 1)
            error_message = 'Helix is wider and higher than specified segment size. No effective masking.'
            self.log.wlog(error_message)
        elif helix_width_in_pixel < segment_size_in_pixel and helix_height_in_pixel > segment_size_in_pixel:
            innermask = model_blank(int(helix_width_in_pixel), int(round(segment_size_in_pixel)), 1, 1)
            error_message = 'Helix is higher than specified segment size. Masking only in helix width.'
            self.log.wlog(error_message)
        else:
            innermask = model_blank(int(round(helix_width_in_pixel)), int(round(helix_height_in_pixel)), 1, 1)
        mask = Util.pad(innermask, segment_size_in_pixel, segment_size_in_pixel, 1, 0, 0, 0, '0')
        
        return mask


    def add_smooth_gaussian_falloff_to_edge_of_binary_mask(self, segment_size_in_pixel, width_falloff, binary_mask):
#        """
#        >>> from spring.segment2d.segmentexam import SegmentExam
#        >>> circ = model_circle(3, 20, 20)
#        >>> mask = SegmentExam().add_smooth_gaussian_falloff_to_edge_of_binary_mask(20, 0.1, circ)
#        >>> np.copy(EMNumPy.em2numpy(mask.get_row(10)))
#        """
        gauss_edge_width = max(1, int(round(segment_size_in_pixel * width_falloff)))
        kernel_width = gauss_edge_width * 2
        kernel_width_is_even = kernel_width % 2
        if kernel_width_is_even == 0:
            kernel_width += 1
        smooth_mask = filt_gaussl(binary_mask, 1/(2*np.pi*gauss_edge_width))
        smooth_mask += binary_mask
        try:
            smooth_mask = threshold_to_zero(smooth_mask, 0.075)
            smooth_mask = threshold_maxval(smooth_mask, 0.5)
        except RuntimeError:
            pass
        smooth_mask = smooth_mask * 2
        
        return smooth_mask
    

    def generate_falloff_line(self, segment_size_in_pixel, width_falloff):
        """
        >>> from spring.segment2d.segmentexam import SegmentExam
        >>> s = SegmentExam()
        >>> s.generate_falloff_line(20, 0.5)
        (array([ 1.        ,  0.97488286,  0.90205491,  0.78883309,  0.64659262,
                0.48962419,  0.33369821,  0.19448033,  0.08595758,  0.01903308]), 10)
        >>> s.generate_falloff_line(20, 0)
        (array([], dtype=float64), 0)
        """
        if width_falloff > 0:
            falloff_len = max(2, int(width_falloff * segment_size_in_pixel))
        else:
            falloff_len = 0

        falloff_line = 0.5 * np.cos(np.arange(falloff_len) / (falloff_len / 10.0 * np.pi)) + 0.5
        
        return falloff_line, falloff_len


    def generate_falloff_line_old(self, segment_size_in_pixel, width_falloff):
        falloff_len = int(width_falloff * segment_size_in_pixel)
        falloff_line = 0.5 * np.cos(np.arange(falloff_len) / (falloff_len / 10.0 * np.pi)) + 0.5
        
        return falloff_line, falloff_len


    def generate_two_dee_cosine_falloff(self, falloff_line, max_dim):
        
        cos_field = np.zeros((len(falloff_line), max_dim))
        for every_row in np.arange(max_dim):
            cos_field[:,int(every_row)] = falloff_line
            
        return cos_field
    

    def generate_rectangular_mask_with_linear_falloffs(self, helix_width_in_pixel, helix_height_in_pixel,
    segment_size_in_pixel, width_falloff):
        falloff_line, falloff_len = self.generate_falloff_line(segment_size_in_pixel, width_falloff)
        
        cos_field = self.generate_two_dee_cosine_falloff(falloff_line, helix_height_in_pixel)
        rect = np.ones((helix_width_in_pixel, helix_height_in_pixel))
        mask = np.vstack([np.flipud(cos_field), rect, cos_field])
        mask = np.rot90(mask)
        
        cos_field = self.generate_two_dee_cosine_falloff(falloff_line, helix_width_in_pixel + 2 * falloff_len)
        mask_both = np.vstack([np.flipud(cos_field), mask, cos_field])
        
        return falloff_line, mask_both
    

    def generate_radial_falloff_gradient(self, falloff_line):
        falloff_len = len(falloff_line)
        img_dim = 2 * falloff_len
        img = model_blank(img_dim, img_dim)
        for each_radius, each_row in enumerate((falloff_line[:-1])):
            inner_circle = model_circle(each_radius, img_dim, img_dim)
            outer_circle = model_circle(each_radius + 1, img_dim, img_dim)
            ring = outer_circle - inner_circle
            img += (ring * each_row)
            
        square = np.copy(EMNumPy.em2numpy(img))
        
        upper_row, lower_row = np.hsplit(square, 2)
        third_quad, fourth_quadrant = np.vsplit(lower_row, 2)
        
        fourth_quadrant = fourth_quadrant[1:falloff_len, 1:falloff_len] 
        fq_range = fourth_quadrant.max() - fourth_quadrant.min()
        if fq_range != 0:
            fourth_quadrant = (fourth_quadrant - fourth_quadrant.min()) / (fourth_quadrant.max() - fourth_quadrant.min())
        else:
            fourth_quadrant = fourth_quadrant - fourth_quadrant.min()
        
        return fourth_quadrant
        
        
    def insert_radial_falloff_gradient_into_corners_of_rectangular_mask(self, radial_quadrant, falloff_line, rect_mask):
        falloff_len = len(falloff_line)
        rows, cols = np.shape(rect_mask)
        rect_mask[0:falloff_len - 1, 0:falloff_len - 1]=np.fliplr(np.flipud(radial_quadrant))
        rect_mask[rows - falloff_len + 1:rows, 0:falloff_len - 1]=np.fliplr(radial_quadrant)
        
        rect_mask[0:falloff_len - 1, cols - falloff_len + 1:cols]=np.flipud(radial_quadrant)
        rect_mask[rows - falloff_len + 1:rows, cols - falloff_len + 1:cols]=(radial_quadrant)
        
        central_row = rows / 2
        rect_mask[rows - falloff_len] = rect_mask[central_row]
        rect_mask[falloff_len - 1] = rect_mask[central_row]
        
        emmask = EMNumPy.numpy2em(np.copy(rect_mask))
        
        return emmask
    

    def pad_image_to_current_size(self, emmask, current_xsize, current_ysize):
        emmask = Util.pad(emmask, current_xsize, current_ysize, 1, 0, 0, 0, '0')
        return emmask


    def window_image_to_current_sizes(self, emmask, current_xsize, current_ysize):
        emmask = Util.window(emmask, current_xsize, current_ysize, 1, 0, 0, 0)
        return emmask

    def resize_mask_to_segment_dimensions(self, emmask, segment_size):
        current_xsize = emmask.get_xsize()
        current_ysize = emmask.get_ysize()
        
        if current_xsize < segment_size:
            current_xsize = segment_size
            emmask = self.pad_image_to_current_size(emmask, current_xsize, current_ysize)
        if current_ysize < segment_size:
            current_ysize = segment_size
            emmask = self.pad_image_to_current_size(emmask, current_xsize, current_ysize)
        if current_xsize > segment_size:
            current_xsize = segment_size
            emmask = self.window_image_to_current_sizes(emmask, current_xsize, current_ysize)
        if current_ysize > segment_size:
            current_ysize = segment_size
            emmask = self.window_image_to_current_sizes(emmask, current_xsize, current_ysize)
            
#        emmask.write_image('test.hdf')
        
        return emmask
    
    
    def make_smooth_rectangular_mask(self, helix_width_in_pixel, helix_height_in_pixel, segment_size_in_pixel,
    width_falloff=0.1):
        """
        >>> from spring.segment2d.segmentexam import SegmentExam
        >>> helixmask = SegmentExam().make_smooth_rectangular_mask(13, 30, 40)
        >>> mask_row = helixmask.get_row(20)
        >>> EMNumPy.em2numpy(mask_row)
        array([ 0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
                0.        ,  0.        ,  0.        ,  0.        ,  0.        ,
                0.13561368,  0.4896242 ,  0.84986573,  1.        ,  1.        ,
                1.        ,  1.        ,  1.        ,  1.        ,  1.        ,
                1.        ,  1.        ,  1.        ,  1.        ,  1.        ,
                1.        ,  1.        ,  1.        ,  0.84986573,  0.4896242 ,
                0.13561368,  0.        ,  0.        ,  0.        ,  0.        ,
                0.        ,  0.        ,  0.        ,  0.        ,  0.        ], dtype=float32)
        >>> helixmask = SegmentExam().make_smooth_rectangular_mask(20, 20, 40, 0)
        >>> mask_row = helixmask.get_row(20)
        >>> EMNumPy.em2numpy(mask_row)
        array([ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  1.,  1.,  1.,
                1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,
                1.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.], dtype=float32)
        """
    
        if helix_height_in_pixel is None:
            helix_height_in_pixel = segment_size_in_pixel
            
        falloff_line, rect_mask = self.generate_rectangular_mask_with_linear_falloffs(int(helix_width_in_pixel),
        int(helix_height_in_pixel), segment_size_in_pixel, width_falloff)
        
        if width_falloff > 0:
            radial_quadrant = self.generate_radial_falloff_gradient(falloff_line)
        
            emmask = self.insert_radial_falloff_gradient_into_corners_of_rectangular_mask(radial_quadrant, falloff_line,
            rect_mask)
        else:
            emmask = EMNumPy.numpy2em(np.copy(rect_mask))
        
        resized_mask = self.resize_mask_to_segment_dimensions(emmask, segment_size_in_pixel)
        
        return resized_mask
        
            
    def make_rectangle_with_rounded_edges(self, size, width, height, corner_radius):
        
        if not size > width + 2 * corner_radius or not size > height + 2 * corner_radius:
            corner_radius = 0
        first_rec = self.make_binary_shape_mask(width - 2 * corner_radius, height, size) 
        second_rec = self.make_binary_shape_mask(width, height - 2 * corner_radius, size)
        
        center_x = width / 2 - corner_radius
        center_y = height / 2 - corner_radius
        
        rectangle = first_rec + second_rec
        if size > width + 2 * corner_radius and size > height + 2 * corner_radius:
            for each_x, each_y in [(center_x, center_y), (-center_x, center_y), (center_x, -center_y), (-center_x, -center_y)]:
                circ = model_circle(corner_radius, size, size)
                shifted = fshift(circ, each_x, each_y)
                rectangle += shifted
        
        rectangle = binarize(rectangle, 0.001)
        
        return rectangle
            
        
    def make_smooth_rectangular_mask_old(self, helix_width_in_pixel=None, helix_height_in_pixel=None,
    segment_size_in_pixel=None, width_falloff=0.1):
        """
        * Function to generate smooth rectangular mask for helix

        #. Input: helix width (pixel), helix height (pixel), segment size (pixel), width_falloff (percent)
        #. Output: rectangular smooth helix mask
        #. Usage: helixmask = make_smooth_rectangular_mask_old(helixwidthpix, helixheightpix, segsizepix, width_falloff)

        >>> from EMAN2 import EMNumPy
        >>> from spring.segment2d.segmentexam import SegmentExam
        >>> helixmask = SegmentExam().make_smooth_rectangular_mask_old(3, 8, 10)
        >>> mask_row = helixmask.get_row(6)
        >>> EMNumPy.em2numpy(mask_row)
        array([ 0.        ,  0.        ,  0.44859728,  1.        ,  1.        ,
                1.        ,  1.        ,  0.4485974 ,  0.        ,  0.        ], dtype=float32)
        
        >>> helixmask = SegmentExam().make_smooth_rectangular_mask_old(4, 8, 10)
        >>> mask_row = helixmask.get_row(6)
        >>> EMNumPy.em2numpy(mask_row)
        array([ 0.        ,  0.        ,  0.44859728,  1.        ,  1.        ,
                1.        ,  1.        ,  0.4485974 ,  0.        ,  0.        ], dtype=float32)
        
        >>> mask_col = helixmask.get_col(5)
        >>> EMNumPy.em2numpy(mask_col)
        array([ 0.52295566,  1.        ,  1.        ,  1.        ,  1.        ,
                1.        ,  1.        ,  1.        ,  1.        ,  0.52295554], dtype=float32)
        >>> EMNumPy.em2numpy(helixmask)
        array([[ 0.        ,  0.        ,  0.06597386,  0.3522006 ,  0.52295566,
                 0.52295566,  0.3522006 ,  0.06597386,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.27333945,  1.        ,  1.        ,
                 1.        ,  1.        ,  0.27333945,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.41630986,  1.        ,  1.        ,
                 1.        ,  1.        ,  0.41630986,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.44859722,  1.        ,  1.        ,
                 1.        ,  1.        ,  0.44859722,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.45131591,  1.        ,  1.        ,
                 1.        ,  1.        ,  0.45131603,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.45131591,  1.        ,  1.        ,
                 1.        ,  1.        ,  0.45131591,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.44859728,  1.        ,  1.        ,
                 1.        ,  1.        ,  0.4485974 ,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.41630974,  1.        ,  1.        ,
                 1.        ,  1.        ,  0.41630974,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.27333945,  1.        ,  1.        ,
                 1.        ,  1.        ,  0.27333951,  0.        ,  0.        ],
               [ 0.        ,  0.        ,  0.06597374,  0.35220054,  0.52295542,
                 0.52295554,  0.35220054,  0.06597385,  0.        ,  0.        ]], dtype=float32)
        >>> helixmask = SegmentExam().make_smooth_rectangular_mask_old(3, 12, 16 , 0.4)
        >>> mask_row = helixmask.get_row(8)
        >>> EMNumPy.em2numpy(mask_row)
        array([ 0.19578975,  0.20234054,  0.21444666,  0.23026752,  0.24739641,
                0.26322556,  1.        ,  1.        ,  1.        ,  1.        ,
                0.26322556,  0.24739641,  0.23026752,  0.21444666,  0.20234054,
                0.19578975], dtype=float32)
        >>> helixmask = SegmentExam().make_smooth_rectangular_mask_old(3, 12, 16 , 0.6)
        >>> mask_row = helixmask.get_row(8)
        >>> EMNumPy.em2numpy(mask_row)
        array([ 0.19578975,  0.20234054,  0.21444666,  0.23026752,  0.24739641,
                0.26322556,  1.        ,  1.        ,  1.        ,  1.        ,
                0.26322556,  0.24739641,  0.23026752,  0.21444666,  0.20234054,
                0.19578975], dtype=float32)
        >>> helixmask = SegmentExam().make_smooth_rectangular_mask_old(15, 12, 16 , 0.6)
        >>> mask_col = helixmask.get_col(8)
        >>> EMNumPy.em2numpy(mask_col)
        array([ 0.50495636,  0.72750413,  1.        ,  1.        ,  1.        ,
                1.        ,  1.        ,  1.        ,  1.        ,  1.        ,
                1.        ,  1.        ,  1.        ,  1.        ,  0.72750401,
                0.50495636], dtype=float32)
        >>> mask_row = helixmask.get_row(8)
        >>> EMNumPy.em2numpy(mask_row)
        array([ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,
                1.,  1.,  1.], dtype=float32)
 
        >>> helixmask = SegmentExam().make_smooth_rectangular_mask_old(19, 12, 16 , 0)
        >>> mask_col = helixmask.get_col(8)
        >>> EMNumPy.em2numpy(mask_col)
        array([ 0.,  0.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,
                1.,  0.,  0.], dtype=float32)

        >>> helixmask = SegmentExam().make_smooth_rectangular_mask_old(12, 19, 16 , 0)
        >>> mask_row = helixmask.get_row(8)
        >>> EMNumPy.em2numpy(mask_row)
        array([ 0.,  0.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,
                1.,  0.,  0.], dtype=float32)
 
        >>> helixmask = SegmentExam().make_smooth_rectangular_mask_old(19, 19, 16 , 0.4)
        >>> mask_row = helixmask.get_row(8)
        >>> EMNumPy.em2numpy(mask_row)
        array([ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,
                1.,  1.,  1.], dtype=float32)
 
        """
        if helix_width_in_pixel is None: 
            helix_width_in_pixel = self.helixwidthpix
        if segment_size_in_pixel is None: 
            segment_size_in_pixel = self.segsizepix
        if helix_height_in_pixel is None: 
            helix_height_in_pixel = segment_size_in_pixel * 0.95

        helix_width_in_pixel, helix_height_in_pixel = \
        self.insure_mirror_symmetry_of_mask_parameters(helix_width_in_pixel, helix_height_in_pixel)
        
        adjusted_width_falloff = self.limit_width_falloff_to_available_pixels_outside_binary_mask(helix_width_in_pixel,
        helix_height_in_pixel, segment_size_in_pixel, width_falloff)
        
        binary_mask = self.make_binary_shape_mask(helix_width_in_pixel, helix_height_in_pixel, segment_size_in_pixel)
        
        if width_falloff > 0 and adjusted_width_falloff > 0:
            self.helixmask = self.add_smooth_gaussian_falloff_to_edge_of_binary_mask(segment_size_in_pixel,
            adjusted_width_falloff, binary_mask)
        else:
            self.helixmask = binary_mask

        return self.helixmask
    

class SegmentExamWidth(SegmentExamMask):
    def find_local_extrema(self, fits, target='maxima', window=None):
        """
        Function from [SciPy-user] mailing list 'Finding local minima of greater than a given depth'

        #. Input: 1D/2D array of data and window size for minimum filter
        #. Output: ordered indices and minimum values
        #. Usage: ind, minima = find_local_extrema(array, target, window)
        
        """

        if window is None: 
            window=int(0.1*len(fits))

        fits = np.asarray(fits)
        if target == 'minima':
            from scipy.ndimage import minimum_filter
            minfits = minimum_filter(fits, size=window, mode='wrap')
        elif target == 'maxima':
            from scipy.ndimage import maximum_filter
            minfits = maximum_filter(fits, size=window, mode='wrap')

        minima_mask = fits == minfits
        good_indices = np.arange(len(fits))[minima_mask]
        good_fits = fits[minima_mask]
        order = good_fits.argsort()

        return good_indices[order], good_fits[order]

    def measure_peakdist(self, rowsaddimg=None, segsizepix=None, pixelsize=None):
        """
        * Function to measure distance between two symmetrical peaks of 1D helix width projection

        #. Input: rowsaddimg = projection to be measured, segsizepix = segment size (pixel), pixelsize
        #. Output: width of helix in Angstrom
        #. Usage: width = measure_peakdist(rowsaddimg, segsizepix, pixelsize)
        
        """
        from scipy import interpolate

        if rowsaddimg is None: rowsaddimg = self.rowsaddimg
        if segsizepix is None: segsizepix = self.segsizepix
        if pixelsize is None: pixelsize = self.pixelsize

        rowsaddimgnp = EMNumPy.em2numpy(rowsaddimg)
        rowsaddimgcp = np.copy(rowsaddimgnp)

        while True:
            try:
                img1dlineleft, img1dlineright = np.hsplit(rowsaddimgcp, 2)
                break
            except ValueError:
                rowsaddimgcp = np.append(rowsaddimgcp, max(rowsaddimgcp))

        img1dlineleft = np.flipud(img1dlineleft)

        cols = np.arange(0, len(img1dlineleft))
        colspol = np.arange(0, len(cols), 0.01)
        t = interpolate.splrep(cols, img1dlineleft, k=3, s=0)
        img1dlineleftpol = interpolate.splev(colspol, t)

        t = interpolate.splrep(cols, img1dlineright, k=3, s=0)
        img1dlinerightpol = interpolate.splev(colspol, t)

        ind, minima = self.find_local_extrema(img1dlineleftpol, target='minima')
        leftmin = colspol[ind[0]]
        # loop until value is significantly away from center of image
        it = iter(ind)
        while (leftmin < 0.2*self.helixwidthpix):
            try:
                leftmin = colspol[next(it)]
            except:
                break

        # sort according to real for display purposes
        ind, minima = self.find_local_extrema(img1dlinerightpol, target='minima')
        rightmin = colspol[ind[0]]
        it = iter(ind)
        while (rightmin < 0.2*self.helixwidthpix):
            try:
                rightmin = colspol[next(it)]
            except:
                break

#        self.log.dlog('min1: {0}, min2: {1}'.format(leftmin, rightmin))
        width = (rightmin + leftmin)*pixelsize

        return width
    

class SegmentExamLayerCorrelation(SegmentExamWidth):
    def compute_radii_for_fourier_mask(self, layer_line_region, segment_size, pixelsize):
        """
        >>> from spring.segment2d.segmentexam import SegmentExam
        >>> SegmentExam().compute_radii_for_fourier_mask(((0.1, 0.2)), 100, 2.5) 
        array([ 25.,  50.])
        """
        radii_pixel = np.array(layer_line_region) * pixelsize * segment_size
        radii_pixel = np.round(radii_pixel)
        
        return radii_pixel
        
    def generate_series_of_circular_masks_from_radii(self, radii_pixel, segment_size):
        masks = []
        for each_radius in np.arange(radii_pixel[0], radii_pixel[-1]):
            outer = model_circle(each_radius, segment_size, segment_size)
            inner = model_circle(each_radius - 1, segment_size, segment_size)
            
            ring = outer - inner
            masks.append(ring)
            
        return masks
    
            
    def compute_power_correlations_with_rings(self, avg_periodogram, masked_power, masks, segment_ids):
        power = EMData()
        correlations = []
        log_info = []
        for each_local_seg_id, each_stack_id in enumerate(segment_ids):
            power.read_image(masked_power, each_local_seg_id)
            
            correlation_of_one = [ccc(avg_periodogram, power, each_ring) for each_ring in masks]
            mean_ccc = np.mean(correlation_of_one)
            correlations.append(mean_ccc)
            log_info += [[each_stack_id, each_local_seg_id, mean_ccc]]

        msg = tabulate(log_info, ['stack_id', 'local_id', 'ccc'])

        self.log.ilog('The amplitudes of the following segments correlate with the avaraged power' + \
        'spectrum.\n{0}'.format(msg))
        
        return correlations
    
            
    def enter_correlation_values_in_database(self, correlations, segment_ids):
        session = SpringDataBase().setup_sqlite_db(base)
        
        for each_id, each_stack_id in enumerate(segment_ids):
            each_segment = session.query(SegmentTable).get(each_stack_id + 1)
            each_segment.ccc_layer = correlations[each_id]
            session.merge(each_segment)
            
        helices = session.query(HelixTable).all()
        for each_helix in helices:
            cc_per_helix = session.query(SegmentTable.ccc_layer).filter(SegmentTable.helix_id == HelixTable.id)
            avg_ccc_layer = np.mean([each_cc for each_cc in cc_per_helix])
            
            each_helix.avg_ccc_layer = avg_ccc_layer
            each_helix.ccc_layer_position_start = self.res_ccc_range[0]
            each_helix.ccc_layer_position_end = self.res_ccc_range[1]
            session.merge(each_helix)
            
        session.commit()
        

class SegmentExamVisualize(SegmentExamLayerCorrelation):
    def split_quarters(self, addpowimgenh=None):
        """
        * Function to split enhanced power spectrum (EMData object) into lower right quarter

        #. Input: avg_periodogram_enhanced = added power spectrum, segment size (pixel)
        #. Output: lower right quarter
        #. Usage: addpowimgenh1st = split_quarters(avg_periodogram_enhanced)
        
        """
        if addpowimgenh is None: addpowimgenh = self.avg_periodogram_enhanced
        segsizepix  = addpowimgenh.get_xsize()

        addpowimgenh1st = Util.window(addpowimgenh, segsizepix/2, segsizepix/2, 1, segsizepix/4, segsizepix/4, 0)

        return addpowimgenh1st
    

    def setup_fourxtwo(self, figno=None):
        """
        * Function to setup 4 x 2 subplot grid for diagnostic output

        #. Input: figno = figure number
        #. Output: figure
        #. Usage figure = setupfourxtwo(figno)
        
        """
        segmentexam_plot = DiagnosticPlot()
        if len(self.feature_set.parameters) < 15:
            self.fig = segmentexam_plot.add_header_and_footer(self.feature_set)
        else:    
            self.fig = segmentexam_plot.fig
        
        self.ax1 = segmentexam_plot.plt.subplot2grid((2,4), (0,0), colspan=1, rowspan=1)
        self.ax2 = segmentexam_plot.plt.subplot2grid((2,4), (1,0), colspan=1, rowspan=1)
        self.ax3 = segmentexam_plot.plt.subplot2grid((2,4), (0,1), colspan=1, rowspan=1)
        self.ax4 = segmentexam_plot.plt.subplot2grid((2,4), (1,1), colspan=1, rowspan=1)
        self.ax5 = segmentexam_plot.plt.subplot2grid((2,4), (0,2), colspan=1, rowspan=1)
        self.ax6 = segmentexam_plot.plt.subplot2grid((2,4), (1,2), colspan=1, rowspan=1)
        self.ax7 = segmentexam_plot.plt.subplot2grid((2,4), (0,3), colspan=1, rowspan=1)
        self.ax8 = segmentexam_plot.plt.subplot2grid((2,4), (1,3), colspan=1, rowspan=1)

        subplot_collection = [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6, self.ax7, self.ax8]
        subplot_collection = segmentexam_plot.set_fontsize_to_all_ticklabels_of_subplots(subplot_collection)

        return self.fig


    def display_average_and_variance(self, twodavg=None, twodvar=None):
        """
        * Function to add average and variance images to diagnostic output plot

        #. Input: 2D average, 2d variance
        #. Output: subplot ax1, subplot ax3
        #. Usage: ax1, ax3 = display_average_and_variance(twodavg, twodvar)
        
        """
        if twodavg is None: twodavg = self.twodavg
        if twodvar is None: twodvar = self.twodvar

        twodavg = Micrograph().adjust_gray_values_for_print_and_optimal_display(twodavg)
        arrtwodavg = np.copy(EMNumPy.em2numpy(twodavg))

        # ax1: 2D average of width
        self.ax1.set_title('Average of segments', fontsize=8)
        self.ax1.set_xticks([])
        self.ax1.set_yticks([])
        self.ax1.imshow(arrtwodavg, cmap=cm.gray, interpolation='nearest')
        self.log.ilog('Avarage image included in montage')

#        twodvar = Micrograph().adjust_gray_values_for_print_and_optimal_display(twodvar)
        self.arrtwodvar = np.copy(EMNumPy.em2numpy(twodvar))
        # ax3 variance image
        self.ax3.set_title('Variance of segments', fontsize=8)
        self.ax3.set_xticks([])
        self.ax3.set_yticks([])
        self.ax3.imshow(self.arrtwodvar, cmap=cm.gray, interpolation='nearest')
        self.log.ilog('Variance image included in montage')

        return self.ax1, self.ax3
    

    def add_width_profile_from_avg_and_var(self, widthavg, widthvar, pixelsize, axx, quantity='width'):
        widthavgline = np.copy(EMNumPy.em2numpy(widthavg))
        widthvarline = np.copy(EMNumPy.em2numpy(widthvar))
        distance = self.measure_peakdist(widthavg, len(widthavgline), pixelsize)
        
        Angstrom = self.pixelsize * np.arange(len(widthavgline))
        table_data = [[each_ang, each_avg, each_var] for each_ang, each_avg, each_var in zip(Angstrom, widthavgline, widthvarline)]

        msg = tabulate(table_data, ['{0} (Angstrom)'.format(quantity.title()),'Intensity average', 'Intensity variance'])
        self.log.ilog('The following average/variance {0} profile was determined:\n{1}'.format(quantity, msg))
        
        axx.set_yticks([])
        axx.set_xlabel('Length (Angstrom)', fontsize=8)
        axx.set_ylabel('Image density', fontsize=8)
        axx.grid(True)
        axxtwin = axx.twinx()
        width_in_angstrom = (np.arange(len(widthavgline)) - len(widthavgline) / 2) * pixelsize
        axx.plot(width_in_angstrom, widthavgline, linewidth=.5, label='Average', color='r')
        axxtwin.plot(width_in_angstrom, widthvarline, linewidth=.5, label='Variance', color='b')
        axx.set_xlim(min(width_in_angstrom), max(width_in_angstrom))
        axx.set_ylim(min(widthavgline), 1.2 * max(widthavgline))
        axxtwin.set_ylim(min(widthvarline), 1.2 * max(widthvarline))
        axxtwin.set_yticks([])
        axx.text(0.5, max(widthavgline), 'Distance: %d A' % (distance), fontsize=5)
        axxtwin.legend(loc=3, prop=font_manager.FontProperties(size=5))
        axx.legend(loc=4, prop=font_manager.FontProperties(size=5))
        
        return axx


    def add_width_histogram_next_to_width_profile(self, widths):
        self.ax4.set_title('Helix width distribution', fontsize=8)
        nobins = self.helixwidth / 10
        self.ax4.hist(widths, nobins, facecolor='green', rwidth=1)
        self.ax4.set_xlim(0, 1.5 * self.helixwidth)
        self.ax4.set_ylabel('Number of segments', fontsize=8)
        self.ax4.set_xlabel('Width (Angstrom)', fontsize=8)
        self.ax4.grid(True)

    def visualize_widthprofile_and_histogram(self, widths=None, widthavg=None, widthvar=None, pixelsize=None):
        """
        * Function to add width profile to diagnostic output plot

        Input: widths = list of widths, widthavg = average of width, widthvar = variance of width, \
            pixelsize
        Output: subplot ax2, ax4
        Usage: ax2, ax4 = visualize_widthprofile_and_histogram(widths, widthavg, widthvar, pixelsize)
        
        """
        if widths is None: widths = self.widths
        if widthavg is None: widthavg = self.widthavg
        if widthvar is None: widthvar = self.widthvar
        if pixelsize is None: pixelsize = self.pixelsize

        self.ax2.set_title('Helix width profile', fontsize=8)
        self.ax2 = self.add_width_profile_from_avg_and_var(widthavg, widthvar, pixelsize, self.ax2)
        self.log.ilog('Width profile of average segment included in montage')
        self.add_width_histogram_next_to_width_profile(widths)

        return self.ax2, self.ax4

    def display_power_spectra_enhanced_and_collapsed(self, avg_periodogram=None, avg_periodogram_enhanced=None,
    avg_collapsed_power_line=None, avg_collapsed_line_enhanced=None):
        """
        * Function to visualize power spectra: sum of power spectra, enhanced sum and their collapsed 1D profile

        #. Input: avg_periodogram = sum of power spectra (img), avg_periodogram_enhanced = enhanced sum \
            of power spectra, avg_collapsed_power_line = collapsed profile of power spectrum (img), \
            avg_collapsed_line_enhanced = collapsed profile of enhanced power spectrum
        #. Output: subplots ax5, ax6, ax7, ax8
        #. Usage: ax5, ax6, ax7, ax8 = display_power_spectra_enhanced_and_collapsed(avg_periodogram, 
            avg_periodogram_enhanced, avg_collapsed_power_line, avg_collapsed_line_enhanced)
        
        """

        if avg_periodogram is None: 
            avg_periodogram = self.avg_periodogram
        if avg_periodogram_enhanced is None: 
            avg_periodogram_enhanced = self.avg_periodogram_enhanced
        if avg_collapsed_power_line is None: 
            avg_collapsed_power_line = self.avg_collapsed_power_line
        if avg_collapsed_line_enhanced is None: 
            avg_collapsed_line_enhanced = self.avg_collapsed_line_enhanced

        # ax5: 2D avaraged power spectrum
        self.ax5.set_title('Averaged powerspectrum', fontsize=8)

        def fourier_pix(x, pos):
            resol = abs(int(x - avg_periodogram.get_xsize() / 2))
            return resol

        formatter_x = FuncFormatter(fourier_pix)
        self.ax5.xaxis.set_major_formatter(formatter_x)
        self.ax5.yaxis.set_major_formatter(formatter_x)

        self.ax5.set_xlabel('Fourier pixel', fontsize=8)

        avg_periodogram = Micrograph().adjust_gray_values_for_print_and_optimal_display(avg_periodogram)
        self.arraddpowimg = np.copy(EMNumPy.em2numpy(avg_periodogram))
        img = self.ax5.imshow(self.arraddpowimg, cmap=cm.hot, interpolation='nearest')

        # colorbar
        cax = self.fig.add_axes([0.93, 0.6, 0.01, 0.25])
        cbar = self.fig.colorbar(img, cax)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(5)

        self.log.ilog('Averaged power spectrum added')

        # ax7: 2D avaraged enhanced power spectrum
        self.ax7.set_title('Enhanced \n(B-factor compensated)', fontsize=8)

        def res(x, pos):
            resol = '{0:.3f}'.format(
                    self.nyquist_frequency * (x - avg_periodogram.get_xsize() / 2)  / float(avg_periodogram.get_xsize() / 2)) 
            return resol

        formatter_x = FuncFormatter(res)
        self.ax7.xaxis.set_major_formatter(formatter_x)
        self.ax7.yaxis.set_major_formatter(formatter_x)
        self.ax7.set_xlabel('Resolution (1/Angstrom)', fontsize=8)

        avg_periodogram_enhanced = \
        Micrograph().adjust_gray_values_for_print_and_optimal_display(avg_periodogram_enhanced)
        
        self.arraddpowimgenh = np.copy(EMNumPy.em2numpy(avg_periodogram_enhanced))
        self.ax7.imshow(self.arraddpowimgenh, cmap=cm.hot, interpolation='nearest')
        self.log.ilog('Averaged enhanced power spectrum added')

        addpowimgenh1st = self.split_quarters(avg_periodogram_enhanced)
        # ax6: first quarter
        self.ax6.set_title('Lower right quadrant', fontsize=8)
        
        self.arraddcolline = np.copy(EMNumPy.em2numpy(avg_collapsed_power_line))
        self.arraddcollineenh = np.copy(EMNumPy.em2numpy(avg_collapsed_line_enhanced))
        self.make_oneoverres(self.arraddcolline)

        def res(x, pos):
            resol = '{0:.3f}'.format(self.nyquist_frequency * x / float(len(self.arraddcolline))) 
            return resol

        formatter_x = FuncFormatter(res)
        self.ax6.xaxis.set_major_formatter(formatter_x)
        self.ax6.yaxis.set_major_formatter(formatter_x)
        self.ax6.set_xlabel('Resolution (1/Angstrom)', fontsize=8)

        self.arraddpowimgenh1st = np.copy(EMNumPy.em2numpy(addpowimgenh1st))
        self.ax6.imshow(self.arraddpowimgenh1st, cmap=cm.hot, interpolation='nearest')
        self.log.ilog('Upper left quadrant added.')

        # ax8: 1D collapsed power spectrum
        self.ax8.set_title('Collapsed powerspectrum', fontsize=8)

        self.ax8twin = self.ax8.twinx()
        self.ax8twin.plot(self.arrresolution, self.arraddcolline, linewidth = .5, color='b', label='collapsed')
        self.ax8.plot(self.arrresolution, self.arraddcollineenh, linewidth = .5, color='r', label='enhanced')
        self.ax8twin.set_yticks([])
        self.ax8.legend(loc=1, prop=font_manager.FontProperties(size='x-small'))
        self.ax8.set_xlabel('Resolution (1/Angstrom)', fontsize=8)
        self.ax8.set_yticks([])
        self.ax8.set_xlim(0, max(self.arrresolution))
        self.ax8twin.set_xlim(0, max(self.arrresolution))
        self.ax8.grid(True)

        table_data = [[each_res, each_col, each_colen]
                       for each_res, each_col, each_colen in zip(self.arrresolution, self.arraddcolline, self.arraddcollineenh)]
        
        msg = tabulate(table_data, ['Resolution (1/Angstrom)', 'Intensity', 'Intensity (enhanced)'])
        self.log.ilog('The following collapsed power spectrum profile was determined:\n{0}'.format(msg))

        return self.ax5, self.ax6, self.ax7, self.ax8

    def make_oneoverres(self, arr=None, pixelsize=None):
        """
        * Function to generate an array of resolution in reciprocal Angstrom

        #. Input: array, pixelsize
        #. Output: array of reciprocal resolution (1/Angstrom)
        #. Usage: arrresolution = make_overoverres(arr, pixelsize)
        
        >>> from spring.segment2d.segmentexam import SegmentExam
        >>> SegmentExam().make_oneoverres(range(10), 10)
        array([ 0.        ,  0.00555556,  0.01111111,  0.01666667,  0.02222222,
                0.02777778,  0.03333333,  0.03888889,  0.04444444,  0.05      ])
        >>> SegmentExam().make_oneoverres(range(25), 1)
        array([ 0.        ,  0.02083333,  0.04166667,  0.0625    ,  0.08333333,
                0.10416667,  0.125     ,  0.14583333,  0.16666667,  0.1875    ,
                0.20833333,  0.22916667,  0.25      ,  0.27083333,  0.29166667,
                0.3125    ,  0.33333333,  0.35416667,  0.375     ,  0.39583333,
                0.41666667,  0.4375    ,  0.45833333,  0.47916667,  0.5       ])
        >>> 1/SegmentExam().make_oneoverres(range(25), 1)
        array([         inf,  48.        ,  24.        ,  16.        ,
                12.        ,   9.6       ,   8.        ,   6.85714286,
                 6.        ,   5.33333333,   4.8       ,   4.36363636,
                 4.        ,   3.69230769,   3.42857143,   3.2       ,
                 3.        ,   2.82352941,   2.66666667,   2.52631579,
                 2.4       ,   2.28571429,   2.18181818,   2.08695652,   2.        ])
        """
        if arr is None: arr = self.arraddcolline
        if pixelsize is None: pixelsize = self.pixelsize

        self.nyquist_frequency = 1/(float(pixelsize)*2)
        self.arrresolution = np.linspace(0, self.nyquist_frequency, len(arr))

        return self.arrresolution

    def cleanup(self, *files):
        """
        * Function to clean up intermediate image files

        Input: arbitrary number of files
        Ouput: None
        Usage: cleanup(thisfile, anotherfile)
        """
        for rmfile in files:
            if os.path.isfile(rmfile):
                os.remove(rmfile)
                self.log.ilog('Intermediate file {0} was removed'.format(rmfile))

class SegmentExam(SegmentExamVisualize):


    def collapse_periodograms(self, avg_periodogram, avg_periodogram_enhanced):
        avg_collapsed_power_line = self.collapse_power(avg_periodogram)
        
        avg_collapsed_line_enhanced = self.collapse_power(avg_periodogram_enhanced)
        
        return avg_collapsed_power_line, avg_collapsed_line_enhanced
    

    def write_avg_periodograms(self, avg_periodogram, power_img, power_enhanced_img):
        avg_periodogram.write_image(power_img)
        avg_periodogram_enhanced = self.enhance_power(avg_periodogram, self.pixelsize)
        avg_periodogram_enhanced.write_image(power_enhanced_img)
            
        return avg_periodogram_enhanced
    

    def add_power_spectra_from_verticalized_stack(self, infilestack, segment_ids, helixwidth=None,
    masked_infilestack=None, power_infilestack=None, padsize=4):
        """
        * Function to compute sum of in-planed rotated segments 
        """
        self.log.fcttolog()
        self.log.in_progress_log()
        segment = EMData()
        segment.read_image(infilestack)
        segment_size = segment.get_xsize()
        avg_periodogram = model_blank(padsize * segment_size, padsize * segment_size, 1, 0)

        if helixwidth is None:
            helixwidth = segment_size
        helixmask = self.make_smooth_rectangular_mask(helixwidth, segment_size * 0.6, segment_size, 0.15)
        log_info = 'The following segments are fourier-transformed and their amplitudes averaged.' + \
        '\n(Local_id, Segment_id)\n'
        for each_local_seg_id, each_seg_id in enumerate(segment_ids):
            segment.read_image(infilestack, each_local_seg_id)
            segment *= helixmask
            if masked_infilestack is not None:
                segment.write_image(masked_infilestack, each_local_seg_id)
            log_info += '({0}, {1}) '.format(each_local_seg_id, each_seg_id)
            if padsize > 1:
                segment = Util.pad(segment, padsize * segment_size, padsize * segment_size, 1, 0, 0, 0, '0')
            ps = periodogram(segment)
            avg_periodogram += ps
            if power_infilestack is not None:
                ps.write_image(power_infilestack, each_local_seg_id)
        self.log.ilog(log_info)

        return avg_periodogram
    

    def compute_avg_and_var_of_width_and_image(self, infilestack, temp_rowsadd):
        widthavg, widthvar = add_series(temp_rowsadd)
        twodavg, twodvar = add_series(infilestack)
        os.remove(temp_rowsadd)
        
        return widthavg, widthvar, twodavg, twodvar
    

    def determine_width(self, infilestack, segsizepix, segment_ids):
        """
        * Function to project width profile of segments

        #. Input: stackfile, segment size (pixel)
        #. Output: width average profile, width variance profile, measured width list
        #. Usage: widthavg, widthvar, widths = determine_width(infilestack, segsizepix)
        """

        self.log.fcttolog()
        widths = []
        
        segment = EMData()
        temp_rowsadd = os.path.join(self.tempdir,'rowsaddimg.hdf')
        
        log_info = []
        for each_local_seg_id, each_stack_id in enumerate(segment_ids):
            segment.read_image(infilestack, each_local_seg_id)
            rowsaddimg = self.project_helix(segment)
            rowsaddimg.write_image(temp_rowsadd, each_local_seg_id)

            width = self.measure_peakdist(rowsaddimg, self.segsizepix, self.pixelsize)
            widths.append(width)
            log_info += [[each_stack_id, each_local_seg_id, width]]

        msg = tabulate(log_info, ['stack_id', 'local_id', 'width (Angstrom)'])
        self.log.ilog('The following segments were projected and their width is measured:\n{0}'.format(msg))

        return temp_rowsadd, widths
    

    def correlate_layer_lines_of_average_power_with_individual_segments(self, avg_periodogram, masked_power,
    segment_ids):
        segment = EMData()
        segment.read_image(masked_power)
        segment_size = segment.get_xsize()
        
        if self.power_reference:
            ref_periodogram = EMData()
            ref_periodogram.read_image(self.power_input)
            
            if avg_periodogram.get_xsize() != ref_periodogram.get_xsize():
                msg = 'The provided reference power spectrum does not have the same size as the power spectra of ' + \
                'the segments ({0} vs. {1} '.format(ref_periodogram.get_xsize(), avg_periodogram.get_xsize()) + \
                'pixels). Double-check the origin of the reference power spectrum. Was it generated using ' + \
                '{0} with the same processing options, e.g. \'Power spectrum '.format(self.feature_set.progname) + \
                'resolution cutoff in 1/Angstrom\'?'
                raise ValueError(msg)
            cc_periodogram = ref_periodogram
        else:
            cc_periodogram = avg_periodogram

        fourier_radii = self.compute_radii_for_fourier_mask(self.res_ccc_range, segment_size, self.pixelsize)
        masks = self.generate_series_of_circular_masks_from_radii(fourier_radii, segment_size)
        correlations = self.compute_power_correlations_with_rings(cc_periodogram, masked_power, masks, segment_ids)
        
        return correlations
        

    def visualize_power_avg_and_width_analysis(self, widthavg, widthvar, widths, twodavg, twodvar, avg_periodogram,
    avg_periodogram_enhanced, avg_collapsed_power_line, avg_collapsed_line_enhanced):
        """
        * Function to combine output of width and power spectra analysis into single summary sheet

        """
            
        self.log.fcttolog()

        self.setup_fourxtwo()

        self.display_average_and_variance(twodavg, twodvar)
        self.visualize_widthprofile_and_histogram(widths, widthavg, widthvar, self.pixelsize)
        
        self.display_power_spectra_enhanced_and_collapsed(avg_periodogram, avg_periodogram_enhanced,
        avg_collapsed_power_line, avg_collapsed_line_enhanced)

        self.fig.savefig(self.outfile)
        
        return self.fig
    

    def copy_database_and_filter_segment_ids(self):
        shutil.copy(self.spring_path, 'spring.db')

        self.curvature_range, self.ccc_layer_range = SegmentSelect().convert_curvature_ccc_layer_range('spring.db',
        self.straightness_selection, self.curvature_range_perc, self.ccc_layer_selection, self.ccc_layer_range_perc)
        
        segment_ids, excluded_segment_counts = \
        SegmentSelect().filter_non_orientation_parameters_based_on_selection_criteria(self)

        return segment_ids


    def add_up_power_spectra(self):
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        self.tempdir = Temporary().mktmpdir(self.temppath)
        
        self.infilestack, self.segsizepix, self.helixwidthpix, self.pixelsize = \
        self.apply_binfactor(self.binfactor, self.infilestack, self.segsizepix, self.helixwidthpix, self.pixelsize)
        
        self.log.plog(10)

        segment_ids = self.copy_database_and_filter_segment_ids()

        masked_infilestack = os.path.join(self.tempdir, 'infilestack-masked.hdf')
        power_infilestack = os.path.join(self.tempdir, 'infilestack-power.hdf')
        
        avg_periodogram = self.add_power_spectra_from_verticalized_stack(self.infilestack, segment_ids,
        self.helixwidthpix, masked_infilestack, power_infilestack)
        
        self.log.plog(40)
        avg_periodogram_enhanced = self.write_avg_periodograms(avg_periodogram, self.power_img, self.power_enhanced_img)
        
        avg_collapsed_power_line, avg_collapsed_line_enhanced = self.collapse_periodograms(avg_periodogram,
        avg_periodogram_enhanced)
        
        self.log.plog(60)
                     
        if self.layer_ccc_option:
            correlations = self.correlate_layer_lines_of_average_power_with_individual_segments(avg_periodogram,
            power_infilestack, segment_ids)
            
            self.enter_correlation_values_in_database(correlations, segment_ids)
        os.remove(power_infilestack)
            
        temp_rowsadd, self.widths = self.determine_width(masked_infilestack, self.segsizepix, segment_ids)
        
        widthavg, widthvar, twodavg, twodvar = self.compute_avg_and_var_of_width_and_image(masked_infilestack,
        temp_rowsadd)
        
        self.log.plog(80)
        
        os.remove(masked_infilestack)
        
        self.visualize_power_avg_and_width_analysis(widthavg, widthvar, self.widths, twodavg, twodvar, avg_periodogram,
        avg_periodogram_enhanced, avg_collapsed_power_line, avg_collapsed_line_enhanced)
        
        self.log.plog(90)
        
        self.cleanup(self.infilestack)
            
        os.rmdir(self.tempdir)
        self.log.endlog(self.feature_set)
        
        
def main():
    # Option handling
    parset = SegmentExamPar()
    mergeparset = OptHandler(parset)
    ######## Program
    stack = SegmentExam(mergeparset)
    stack.add_up_power_spectra()

if __name__ == '__main__':
    main()
