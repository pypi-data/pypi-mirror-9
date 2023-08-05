# Author: Carsten Sachse 27-Oct-2013
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
""" 
Program to trace helices from micrographs
"""
from EMAN2 import EMUtil, EMData, EMNumPy, Util, periodogram
from fundamentals import window2d, rot_shift2D, ccfn
from scipy import ndimage
from spring.csinfrastr.csfeatures import Features, FeaturesSupport
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import Temporary, OpenMpi, DiagnosticPlot
from spring.csinfrastr.csreadinput import OptHandler
from spring.micprgs.micexam import MicrographExam
from spring.segment2d.segment import Segment
from spring.segment2d.segmentalign2d import SegmentAlign2d
from spring.segment2d.segmentexam import SegmentExam
from tabulate import tabulate
from utilities import model_blank, image_decimate, model_circle
import matplotlib.pyplot as plt
import numpy as np
import os
import scipy.ndimage


class MicHelixTracePar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'michelixtrace'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.mictrace_features = Features()
        self.feature_set = self.mictrace_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    

    def define_parameters_and_their_properties(self):
        self.feature_set = self.mictrace_features.set_inp_multiple_micrographs(self.feature_set)
        self.feature_set = self.mictrace_features.set_output_plot_pattern(self.feature_set, self.progname + \
        '_diag.pdf')
        
        self.feature_set = self.set_helix_reference(self.feature_set)
        self.feature_set = self.mictrace_features.set_pixelsize(self.feature_set)
        self.feature_set = self.mictrace_features.set_power_tile_size(self.feature_set)
        self.feature_set = self.mictrace_features.set_tile_overlap(self.feature_set)
        self.feature_set = self.mictrace_features.set_binning_option(self.feature_set, default=True)
        self.feature_set = self.mictrace_features.set_binning_factor(self.feature_set, binfactor=8)
        self.feature_set = self.set_cc_threshold(self.feature_set)
        self.feature_set = self.set_order_fit(self.feature_set)

        self.feature_set = self.set_exclude_carbon_areas(self.feature_set)
        self.feature_set = self.set_hole_size(self.feature_set)

        self.feature_set = self.mictrace_features.set_mpi(self.feature_set)
        self.feature_set = self.mictrace_features.set_ncpus_scan(self.feature_set)
        self.feature_set = self.mictrace_features.set_temppath(self.feature_set)

    def define_program_states(self):
        self.feature_set.program_states['orient_reference_power_with_overlapping_powers']='Find orientations of ' + \
        'by matching power spectra.'
        self.feature_set.program_states['find_translations_by_projecting']='Find translations by projecting ' + \
        'along helix.'
        self.feature_set.program_states['perform_connected_component_analysis_including_hought']='Extract individual helices ' + \
        'by connected component analysis.'


    def set_helix_reference(self, feature_set):
        inp1 = 'Helix reference'
        feature_set.parameters[inp1] = 'helix_reference.hdf'
        feature_set.properties[inp1] = feature_set.file_properties(1, ['spi', 'hdf', 'img', 'hed'], 'getFile')
        feature_set.hints[inp1] = 'Helix reference: long rectangular straight box of helix to be traced. ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        
        feature_set.level[inp1]='beginner'
        
        return feature_set


    def set_exclude_carbon_areas(self, feature_set):
        inp7 = 'Exclude carbon'
        feature_set.parameters[inp7] = bool(True)
        feature_set.hints[inp7] = 'Choose whether to exclude carbon edge areas of micrograph from helix tracing. '+ \
        'The edge areas will be modeled according to the specified hole diameter below.'
        feature_set.level[inp7]='expert'
        
        return feature_set


    def set_hole_size(self, feature_set):
        inp9 = 'Hole diameter in micrometer'
        feature_set.parameters[inp9] = float(1.3)
        feature_set.hints[inp9] = 'Hole diameter of holey carbon foil is used to estimate edge areas to be excluded ' + \
        'from search.'
        feature_set.properties[inp9] = feature_set.Range(0, 10, 0.1)
        feature_set.relatives[inp9] = 'Exclude carbon'
        feature_set.level[inp9]='expert'
        
        return feature_set


    def set_cc_threshold(self, feature_set):
        inp9 = 'Cross-correlation threshold'
        feature_set.parameters[inp9] = float(0.2)
        feature_set.hints[inp9] = 'Increase threshold if helix tracing too promiscuous. ' + \
        'Otherwise use with caution.'
        feature_set.properties[inp9] = feature_set.Range(0, 1, 0.01)
        feature_set.level[inp9]='expert'
        
        return feature_set


    def set_order_fit(self, feature_set):
        inp9 = 'Order fit'
        feature_set.parameters[inp9] = int(2)
        feature_set.hints[inp9] = 'Order of polynomial fit the coordinates of detected helix (1=linear, ' +\
        '2=quadratic, 3=cubic). Can be used as a further restraint.'
        feature_set.properties[inp9] = feature_set.Range(1, 3, 1)
        feature_set.level[inp9]='expert'
        
        return feature_set


class MicHelixTrace(object):
    """
    * Class that holds functions for examining micrograph quality

    * __init__ Function to read in the entered parameter dictionary and load micrograph

    #. Usage: MicrographExam(pardict)
    #. Input: pardict = OrderedDict of program parameters
    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.infile=p['Micrographs']
            self.outfile=p['Diagnostic plot pattern']

            self.micrograph_files = Features().convert_list_of_files_from_entry_string(self.infile)
            self.reference_file = p['Helix reference']
            
            self.ori_pixelsize = p['Pixel size in Angstrom']
            self.tile_size_A = p['Tile size power spectrum in Angstrom']
            self.tile_overlap = p['Tile overlap in percent']
            self.exclude_carbon = p['Exclude carbon']
            self.hole_size = p['Hole diameter in micrometer']
            self.hole_size_A = self.hole_size * 1e+4
            self.binoption = p['Binning option']
            self.binfactor = p['Binning factor']
            if self.binfactor == 1 and self.binoption is True:
                self.binoption = False
            
            self.cc_threshold = p['Cross-correlation threshold']
            self.order_fit = p['Order fit']
            
            self.temppath=p['Temporary directory']
            self.mpi_option = p['MPI option']
            self.cpu_count = p['Number of CPUs']


    def prepare_power_from_reference(self, reference_file):
        reference = EMData()
        reference.read_image(reference_file)
        reference.process_inplace('normalize')
        
        if self.binoption:
            reference = image_decimate(reference, self.binfactor, fit_to_fft=False)
            pixelsize = self.ori_pixelsize * float(self.binfactor)
        else:
            pixelsize = self.ori_pixelsize 

        overlap_percent = 90.0
        step_size = int(reference.get_ysize() * (100.0 - overlap_percent) / 100.0)
        tile_size_pix = int(self.tile_size_A / pixelsize)
        tile_size_pix = Segment().determine_boxsize_closest_to_fast_values(tile_size_pix)
        ref_size = reference.get_ysize()
        
        if ref_size < tile_size_pix:
            msg = 'Chosen reference size ({0} Angstrom) is smaller than specified '.format(int(ref_size * pixelsize)) + \
            'tile size of {0} Angstrom. Please increase reference or decrease tile size.'.format(self.tile_size_A)
            raise ValueError(msg)

        y_positions = np.arange(0, reference.get_ysize() - tile_size_pix, step_size)
        
        if reference.get_xsize() < tile_size_pix:
            reference = Util.pad(reference, tile_size_pix, ref_size, 1, 0, 0, 0, 'average')
        if reference.get_xsize() > tile_size_pix:
            reference = Util.window(reference, tile_size_pix, ref_size, 1, 0, 0, 0)

        if len(y_positions) > 0:
            reference_pw = model_blank(tile_size_pix, tile_size_pix)
            for each_y in y_positions:
                wi_ref = window2d(reference, tile_size_pix, tile_size_pix, 'l', 0, int(each_y))
                reference_pw += periodogram(wi_ref)
        else:
            wi_ref = Util.window(reference, tile_size_pix, tile_size_pix, 1, 0, 0, 0)
            reference_pw = periodogram(wi_ref)

        circle_mask = -1 * model_circle(3, tile_size_pix, tile_size_pix) + 1
        reference_pw *= circle_mask
        
        ref_profile = SegmentExam().project_helix(reference)

        return reference_pw, ref_profile, tile_size_pix


    def compute_step_size(self, tile_size, overlap):
        step = int(tile_size - tile_size * overlap / 100.0)
        return step


    def determine_xy_center_grid(self, tile_size, overlap, x_size, y_size):
        """
        >>> from spring.micprgs.michelixtrace import MicHelixTrace
        >>> MicHelixTrace().determine_xy_center_grid(15, 50, 50, 100)
        array([[(7, 7), (7, 14), (7, 21), (7, 28), (7, 35), (7, 42), (7, 49),
                (7, 56), (7, 63), (7, 70), (7, 77), (7, 84), (7, 91)],
               [(14, 7), (14, 14), (14, 21), (14, 28), (14, 35), (14, 42),
                (14, 49), (14, 56), (14, 63), (14, 70), (14, 77), (14, 84),
                (14, 91)],
               [(21, 7), (21, 14), (21, 21), (21, 28), (21, 35), (21, 42),
                (21, 49), (21, 56), (21, 63), (21, 70), (21, 77), (21, 84),
                (21, 91)],
               [(28, 7), (28, 14), (28, 21), (28, 28), (28, 35), (28, 42),
                (28, 49), (28, 56), (28, 63), (28, 70), (28, 77), (28, 84),
                (28, 91)],
               [(35, 7), (35, 14), (35, 21), (35, 28), (35, 35), (35, 42),
                (35, 49), (35, 56), (35, 63), (35, 70), (35, 77), (35, 84),
                (35, 91)],
               [(42, 7), (42, 14), (42, 21), (42, 28), (42, 35), (42, 42),
                (42, 49), (42, 56), (42, 63), (42, 70), (42, 77), (42, 84),
                (42, 91)]], dtype=object)

        """
        edge_x0 = edge_y0 = tile_size / 2
        edge_x1 = x_size - edge_x0
        edge_y1 = y_size - edge_y0

        step = self.compute_step_size(tile_size, overlap)

        x_array = np.arange(edge_x0, edge_x1, step)
        y_array = np.arange(edge_y0, edge_y1, step)
        
        xy_center_grid = np.zeros((x_array.size, y_array.size), dtype=tuple)
        for each_x_id, each_x in enumerate(x_array):
            for each_y_id, each_y in enumerate(y_array):
                xy_center_grid[each_x_id][each_y_id]=((int(each_x), int(each_y)))

        return xy_center_grid


    def generate_stack_of_overlapping_images_powers(self, mic, tile_size, overlap):
        
        x_size = mic.get_xsize()
        y_size = mic.get_ysize()

        xy_center_grid = self.determine_xy_center_grid(tile_size, overlap, x_size, y_size)

        xy_table = tabulate(xy_center_grid.ravel(), ['x_coordinate', 'y_coordinate'])
        self.log.ilog('The following x, y coordinates are the centers of the tiles of ' + \
        'the binned micrograph:\n{0}'.format(xy_table))
         
        pw_stack = os.path.join(self.tempdir, 'pw_stack.hdf')
        img_stack = os.path.join(self.tempdir, 'img_stack.hdf')
        circle = -1 * model_circle(3, tile_size, tile_size) + 1
        for each_id, (each_x, each_y) in enumerate(xy_center_grid.ravel()):
            upper_x = each_x - tile_size / 2
            upper_y = each_y - tile_size / 2
            img = window2d(mic, tile_size, tile_size, "l", upper_x, upper_y)
            pw = periodogram(img) * circle
            img.write_image(img_stack, each_id)
            pw.write_image(pw_stack, each_id)
            
        return img_stack, pw_stack, xy_center_grid

    
    def orient_reference_power_with_overlapping_powers(self, pw_stack, ref_power, xy_center_grid):
        self.log.fcttolog()

        image_dimension = ref_power.get_xsize()
        polar_interpolation_parameters, ring_weights = SegmentAlign2d().prepare_empty_rings(1, image_dimension / 2 - 2, 1)
        
        cimage = SegmentAlign2d().make_rings_and_prepare_cimage_header(image_dimension, polar_interpolation_parameters,
        ring_weights, ref_power)
        
        x_range = y_range = 0.0
        translation_step = 1.0
        shift_x = shift_y = 0
        center_x = center_y = image_dimension / 2 + 1
        full_circle_mode = 'F'
        pw_img_count = EMUtil.get_image_count(pw_stack)

        pw_img = EMData()
        angles = []
        peaks = []
        for each_pw_id in list(range(pw_img_count)):
            pw_img.read_image(pw_stack, each_pw_id)
            
            [angt, sxst, syst, mirror, xiref, peakt] = Util.multiref_polar_ali_2d(pw_img, [cimage], x_range,
            y_range, translation_step, full_circle_mode, polar_interpolation_parameters, center_x + shift_x, 
            center_y + shift_y)
            
            angles.append(angt)
            peaks.append(peakt)
            
        angles = np.array(angles).reshape(xy_center_grid.shape)
        peaks = np.array(peaks).reshape(xy_center_grid.shape)

        angle_table = tabulate(angles)
        peaks_table = tabulate(peaks)
        
        self.log.ilog('The following angles were assigned to the tiles:\n{0}'.format(angle_table))
        self.log.ilog('The following peaks were found for the tiles:\n{0}'.format(peaks_table))

        return angles


    def find_translations_by_projecting(self, angles, xy_centers, img_stack, ref_profile, overlap_pix, mic):
        self.log.fcttolog()

        img = EMData()
        image_dimension = ref_profile.get_xsize()

        fl_centers = xy_centers.ravel()
        rhos = np.zeros(fl_centers.shape)
        thetas = np.zeros(fl_centers.shape)
        circle = model_circle(image_dimension / 2, image_dimension, image_dimension)
        cross_corr = []
        for each_id, each_angle in enumerate(angles.ravel()):
            img.read_image(img_stack, each_id)

            img = rot_shift2D(circle * img, each_angle)
        
            each_profile = SegmentExam().project_helix(img)
            cc_profile = ccfn(each_profile, ref_profile, center=False)
            
            cc_prof_np = np.copy(EMNumPy.em2numpy(cc_profile))
            
            max_shift = np.argmax(cc_prof_np)
            cross_corr.append(cc_prof_np[max_shift])
            if cc_prof_np[max_shift] > 0.0:
                if max_shift > image_dimension / 2:
                    max_shift -= image_dimension
                
                if abs(max_shift) < overlap_pix / 2:
                    x_coord = fl_centers[each_id][0]
                    y_coord = fl_centers[each_id][1]
                    rhos[each_id] = x_coord * np.cos(np.deg2rad(each_angle)) + \
                    y_coord * np.sin(np.deg2rad(each_angle)) + max_shift
        
                    thetas[each_id] = each_angle
                    
        rhos = rhos.reshape(angles.shape)
        thetas = thetas.reshape(angles.shape)
        cross_corr = np.array(cross_corr).reshape(angles.shape)
        
        table_rhos = tabulate(rhos)
        table_thetas = tabulate(thetas)
        self.log.ilog('Lines were determined according to equation: rho = x * cos(theta) + y * sin(theta).')
        self.log.ilog('The following rhos were determined:\n{0}'.format(table_rhos))
        self.log.ilog('The following thetas were determined:\n{0}'.format(table_thetas))

        return rhos, thetas, cross_corr


    def build_binary_image_of_segmented_helices(self, rhos, thetas, cross_corr, xy_center_grid, mic, tilesize,
    overlap_percent, cc_threshold):
        x_size, y_size = mic.get_xsize(), mic.get_ysize()
        overlap_cc = np.zeros((y_size, x_size))
        
        fl_rhos = rhos.ravel()
        fl_thetas = thetas.ravel()
        fl_cc = cross_corr.ravel()
        for each_id, (each_x, each_y) in enumerate(xy_center_grid.ravel()):
            lower_x = each_x - tilesize / 2
            upper_x = min(x_size, each_x + tilesize / 2)
            
            lower_y = each_y - tilesize / 2
            upper_y = min(y_size, each_y + tilesize / 2)
            
            each_angle = fl_thetas[each_id]
            
            point_count = tilesize
            if 45 <= each_angle < 135 or 225 <= each_angle < 315:
                xx = np.linspace(lower_x, upper_x, point_count)
                yy = (fl_rhos[each_id] - xx * np.cos(np.deg2rad(each_angle))) / np.sin(np.deg2rad(each_angle))

                yyy = yy[(lower_y <= yy) & (yy < upper_y)]
                xxx = xx[(lower_y <= yy) & (yy < upper_y)]
            else:
                yy = np.linspace(lower_y, upper_y, point_count)
                xx = (fl_rhos[each_id] - yy * np.sin(np.deg2rad(each_angle))) / np.cos(np.deg2rad(each_angle))
            
                yyy = yy[(lower_x <= xx) & (xx < upper_x)]
                xxx = xx[(lower_x <= xx) & (xx < upper_x)]
            
            for each_xx, each_yy in zip(xxx, yyy):
#                 overlap_cc[int(each_yy)][int(each_xx)] += 1#fl_cc[each_id]
                overlap_cc[int(each_yy) - 1:int(each_yy) + 2, int(each_xx) - 1:int(each_xx) + 2] += 1#fl_cc[each_id]

#         overlap_cc = scipy.ndimage.gaussian_filter(overlap_cc, 3)
        overlap_count = tilesize / float(self.compute_step_size(tilesize, overlap_percent))
        overlap_cc /= overlap_count * 16.0 

        histogram_bin = np.histogram(overlap_cc)
        table_cc = tabulate([np.append('cc_bin', histogram_bin[1]), np.append('pixel_count', histogram_bin[0])])

        cc_summary = tabulate([[np.min(overlap_cc), np.max(overlap_cc), np.average(overlap_cc), np.std(overlap_cc)]], 
                              ['min', 'max', 'average', 'stdev'])

        self.log.ilog('The following weighted cross correlations were determined:\n{0}'.format(table_cc))
        self.log.ilog('Cross correlation summary:\n{0}'.format(cc_summary))

        binary = np.copy(overlap_cc)
        binary[binary < cc_threshold] = 0 
        binary[binary > 0] = 1 

        return binary, overlap_cc


    def perform_hough_transform(self, img, angles=None):
        """Perform the straight line Hough transform.
    
        Input:
          img - a boolean array
          angles - in degrees
    
        Output:
          H - the Hough transform coefficients
          distances
          angles
        
        """
        itype = np.uint16 # See ticket 225
    
        if img.ndim != 2:
            raise ValueError("Input must be a two-dimensional array")
    
        img = img.astype(bool)
        
        if not angles:
            angles = np.linspace(-90, 90, 180)
    
        d = np.ceil(np.hypot(*img.shape))
        nr_bins = 2*d - 1
        bins = np.linspace(-d,d,nr_bins)
        theta = angles / 180. * np.pi
        out = np.zeros((nr_bins,len(theta)), dtype=itype)
    
        rows,cols = img.shape
        x,y = np.mgrid[:rows,:cols]
    
        for i,(cT,sT) in enumerate(zip(np.cos(theta), np.sin(theta))):
            rho = np.round_(cT*x[img] + sT*y[img]) - bins[0] + 1
            rho = rho.astype(itype)
            rho[(rho < 0) | (rho > nr_bins)] = 0
            bc = np.bincount(rho.flat)[1:]
            out[:len(bc),i] = bc
    
        return out, angles, bins


    def get_local_maxima1d(self, data, neighborhood_size=5):
        threshold = np.mean(data) + 3 * np.std(data)
        data_max = ndimage.filters.maximum_filter(data, neighborhood_size)
        maxima = (data == data_max)
        data_min = ndimage.filters.minimum_filter(data, neighborhood_size)
        diff = ((data_max - data_min) > threshold)
        maxima[diff == 0] = 0
        
        labeled, num_objects = ndimage.label(maxima)
        slices = ndimage.find_objects(labeled)
        x = []
        for dx in slices:
            x_center = (dx[0].start + dx[0].stop - 1)/2
            x.append(x_center)
        
        return x
    

    def get_local_maxima(self, data, neighborhood_size=5):
        threshold = np.mean(data) + 3 * np.std(data)
        data_max = ndimage.filters.maximum_filter(data, neighborhood_size)
        maxima = (data == data_max)
        data_min = ndimage.filters.minimum_filter(data, neighborhood_size)
        diff = ((data_max - data_min) > threshold)
        maxima[diff == 0] = 0
        
        labeled, num_objects = ndimage.label(maxima)
        slices = ndimage.find_objects(labeled)
        x, y = [], []
        for dy,dx in slices:
            x_center = (dx.start + dx.stop - 1)/2
            x.append(x_center)
            y_center = (dy.start + dy.stop - 1)/2    
            y.append(y_center)
        
        return x, y
    

    def compute_normal_distance_point_to_line(self, p, seg, testSegmentEnds=False):
        """
        Minimum Distance between a Point and a Line
        Written by Paul Bourke,    October 1988
        http://astronomy.swin.edu.au/~pbourke/geometry/pointline/
        """
        y3,x3 = p
        (y1,x1),(y2,x2) = seg
    
        dx21 = (x2-x1)
        dy21 = (y2-y1)
        
        lensq21 = dx21*dx21 + dy21*dy21
        if lensq21 == 0:
            #20080821 raise ValueError, "zero length line segment"
            dy = y3-y1 
            dx = x3-x1 
            return np.sqrt( dx*dx + dy*dy )  # return point to point distance
    
        u = (x3-x1)*dx21 + (y3-y1)*dy21
        u = u / float(lensq21)
    
    
        x = x1+ u * dx21
        y = y1+ u * dy21    
    
        if testSegmentEnds:
            if u < 0:
                x,y = x1,y1
            elif u >1:
                x,y = x2,y2
        
        dx30 = x3-x
        dy30 = y3-y
    
        return np.sqrt( dx30*dx30 + dy30*dy30 )


    def compute_global_rho_in_label_area(self, start_x, stop_x, start_y, stop_y, rho, theta):
        if -45 <= theta < 45:
            yy = np.linspace(0, stop_y - start_y, 2)
            xx = (rho - yy * np.sin(np.deg2rad(theta))) / np.cos(np.deg2rad(theta))
        else:
            xx = np.linspace(0, stop_x - start_x, 2)
            yy = (rho - xx * np.cos(np.deg2rad(theta))) / np.sin(np.deg2rad(theta))
        total_rho = self.compute_normal_distance_point_to_line((0, 0), zip(xx + start_x, yy + start_y))

        return total_rho


    def compute_rho_theta_map_from_label_area_by_going_through_each_thresholded_point_in_tiles(self, label_im, slice_x,
    slice_y, each_feature, x_size, y_size):
        label_area = label_im[slice_x, slice_y]
        binary_label = np.zeros((x_size, y_size))
        binary_label[np.where(label_area == each_feature)] = 1 
        rho_map = np.zeros((x_size, y_size))
        theta_map = np.zeros((x_size, y_size))

        x, y = np.where(label_area == each_feature)

        angles = np.linspace(-90, 90, 180)
        diagonal = np.sqrt(x_size ** 2 + y_size ** 2)
        diagonal_line = np.arange(0, diagonal)
        rho_theta_map = np.zeros((len(angles), int(diagonal)))
        for each_x, each_y in zip(x, y):
            window_size = 7
            start_x = max(0, each_x - window_size / 2)
            stop_x = min(slice_x.stop - 1, each_x + window_size / 2 + 1)
            start_y = max(0, each_y - window_size / 2)
            stop_y = min(slice_y.stop - 1, each_y + window_size / 2 + 1)

            tile = binary_label[start_x:stop_x, start_y:stop_y]
        
            if tile.size > 0:
                out, thetas, rhos = self.perform_hough_transform(tile)

                ind = np.argwhere(out == np.max(out))
            
                rho = rhos[ind[0][0]]
                theta = thetas[ind[0][1]]

                total_rho = self.compute_global_rho_in_label_area(start_x, stop_x, start_y, stop_y, rho, theta)
                rho_map[each_x][each_y] = total_rho
                theta_map[each_x][each_y] = theta
                
                rho_theta_map[int(round(theta + 90))][int(round(total_rho))] += 1

        return angles, diagonal_line, rho_theta_map, theta_map, rho_map

                
    def segment_helix_coordinates_based_on_rho_theta_map(self, order_fit, step, single_helices, slice_x, slice_y,
    x_size, y_size, angles, diagonal_line, rho_theta_map, theta_map, rho_map):

        rho_theta_map_filt = scipy.ndimage.gaussian_filter(rho_theta_map, 3)
        max_rho, max_theta = self.get_local_maxima(rho_theta_map_filt, neighborhood_size=20)
        for each_max_rho, each_max_theta in zip(max_rho, max_theta):
            highest_theta = angles[int(each_max_theta)]
            thres_map_theta = np.zeros(theta_map.shape)
            thres_map_theta[(highest_theta - 10 < theta_map) & (theta_map < highest_theta + 10)] = 1
            highest_rho = diagonal_line[int(round(each_max_rho))]
            thres_map_rho = np.zeros(theta_map.shape)
            thres_map_rho[(highest_rho - 10 < rho_map) & (rho_map < highest_rho + 10)] = 1
            thres_map = thres_map_rho + thres_map_theta
            each_x, each_y = np.where(thres_map == 2)
            if len(each_x) > 0:
                diff_x = abs(each_x[-1] - each_x[0])
                diff_y = abs(each_y[-1] - each_y[0])
                coord_count = int(np.sqrt(diff_x ** 2 + diff_y ** 2) / float(0.5 * step))
                if diff_x >= diff_y:
                    fitt = np.polyfit(each_x, each_y, order_fit)
                    fine_x_coord = np.linspace(each_x[0], each_x[-1] - 1, coord_count)
                    fine_y_coord = np.polyval(fitt, fine_x_coord)
                    fine_xx_coord = fine_x_coord[fine_y_coord < y_size]
                    fine_yy_coord = fine_y_coord[fine_y_coord < y_size]
                else:
                    fitt = np.polyfit(each_y, each_x, order_fit)
                    fine_y_coord = np.linspace(each_y[0], each_y[-1] - 1, coord_count)
                    fine_x_coord = np.polyval(fitt, fine_y_coord)
                    fine_xx_coord = fine_x_coord[fine_x_coord < x_size]
                    fine_yy_coord = fine_y_coord[fine_x_coord < x_size]
                if len(fine_xx_coord) >= 2:
                    single_helices.append((fine_yy_coord + np.float(slice_y.start), fine_xx_coord + np.float(slice_x.start)))
            
        return single_helices


    def perform_connected_component_analysis_including_hought(self, binary, tilesize, overlap, order_fit):
        self.log.fcttolog()
        step = self.compute_step_size(tilesize, overlap)

        label_im, label_count = scipy.ndimage.label(binary)

        single_helices = []
        for each_feature in list(range(1, label_count + 1)):
            
            slice_x, slice_y = ndimage.find_objects(label_im == each_feature)[0]
            x_size = int(slice_x.stop - slice_x.start)
            y_size = int(slice_y.stop - slice_y.start)
            
            length = np.sqrt(x_size ** 2 + y_size ** 2) 
            if length > tilesize / 2:
                
                angles, diagonal_line, rho_theta_map, theta_map, rho_map = \
                self.compute_rho_theta_map_from_label_area_by_going_through_each_thresholded_point_in_tiles(label_im,
                slice_x, slice_y, each_feature, x_size, y_size)

                single_helices = self.segment_helix_coordinates_based_on_rho_theta_map(order_fit, step, single_helices,
                slice_x, slice_y, x_size, y_size, angles, diagonal_line, rho_theta_map, theta_map, rho_map)
  
#                     for each_fine_x, each_fine_y in zip(fine_xx_coord, fine_yy_coord):
#                         binary_hel[int(round(each_fine_x))][int(round(each_fine_y))]=1

#                 plt.clf()
#                 f, (ax4, ax1, ax2, ax3) = plt.subplots(4)
#                 ax4.imshow(binary_label, origin='lower')
#                 ax1.imshow(rho_theta_map_filt, origin='lower')
#                 ax2.imshow(thres_map, origin='lower')
#                 ax3.imshow(rho_map, origin='lower')
#                 plt.savefig('plot{0:02}.pdf'.format(each_feature))

#                 yy = np.linspace(0, y_size, coord_count)
#                 xx = (rho - yy * np.sin(np.deg2rad(theta))) / np.cos(np.deg2rad(theta))
#                 
#                 xxx = xx[(0 < xx) & (xx < x_size)]
#                 yyy = yy[(0 < xx) & (xx < x_size)]

        return single_helices
    

    def compute_cross_product_z_direction_with_respect_to_closest_vector(self, my_pt, each_x, each_y):
        dist = np.sqrt((my_pt[0] - each_x) ** 2 + (my_pt[1] - each_y) ** 2)
        arg_min = np.argmin(dist)
        if arg_min == len(each_x) - 1:
            arg_min -= 1
        clst_pt = each_x[arg_min], each_y[arg_min]
        sec_cls_pt = each_x[arg_min + 1], each_y[arg_min + 1]
        fst_vec = np.array([clst_pt[0] - my_pt[0], clst_pt[1] - my_pt[1], 0])
        sec_vec = np.array([sec_cls_pt[0] - my_pt[0], sec_cls_pt[1] - my_pt[1], 0])
        direction_z = np.cross(fst_vec, sec_vec)[2]

        return direction_z


    def compute_side_of_point_with_respect_to_closest_vector(self, my_pt, each_x, each_y):
        """
        >>> from spring.micprgs.michelixtrace import MicHelixTrace
        >>> m = MicHelixTrace()
        >>> x = np.arange(-30,30)
        >>> m.compute_side_of_point_with_respect_to_closest_vector([3, 4], x, x**2)
        'right'
        >>> m.compute_side_of_point_with_respect_to_closest_vector([2, 4], x, x**2)
        'intersect'
        >>> m.compute_side_of_point_with_respect_to_closest_vector([1, 4], x, x**2)
        'left'
        """
        direction_z = self.compute_cross_product_z_direction_with_respect_to_closest_vector(my_pt, each_x, each_y)

        if direction_z > 0:
            side = 'left'
        elif direction_z < 0:
            side = 'right'
        elif direction_z == 0:
            side = 'intersect'
    
        return side


    def solve_quadratic_equation(self, a, b, c=None):
        """
        x^2 + ax + b = 0  (or ax^2 + bx + c = 0)
        By substituting x = y-t and t = a/2, the equation reduces to 
            y^2 + (b-t^2) = 0 
        which has easy solution
            y = +/- sqrt(t^2-b)
        >>> from spring.micprgs.michelixtrace import MicHelixTrace
        >>> m = MicHelixTrace()
        >>> m.solve_quadratic_equation(1, 4, 4)
        (-2.0, -2.0)
        """
        disc = b ** 2 - 4.0 * a * c
        if disc >= 0:
            x1 = (-b - np.sqrt(disc)) / (2.0 * a)
            x2 = (-b + np.sqrt(disc)) / (2.0 * a)
        else:
            x1 = None
            x2 = None
            
        return x1, x2


    def determine_intersection_points_of_two_circles(self, radius_a, radius_b, center_x_a, center_x_b, center_y_a,
    center_y_b):
        """
        >>> from spring.micprgs.michelixtrace import MicHelixTrace
        >>> m = MicHelixTrace()
        >>> m.determine_intersection_points_of_two_circles(3, 4, 2, 1, 3, -1)
        ((-0.95616670564347328, 2.489041676410868), (4.3679314115258263, 1.1580171471185434))
        """
        diff_x_cntrs = center_x_b - center_x_a                          
        diff_y_cntrs = center_y_b - center_y_a                          
        dist_cntrs = np.sqrt(diff_x_cntrs ** 2 + diff_y_cntrs ** 2)                
        dist_cntr_line = (dist_cntrs ** 2 + radius_a ** 2 - radius_b ** 2) / float(2 * dist_cntrs)       

        x1 = center_x_a + diff_x_cntrs * dist_cntr_line / dist_cntrs + \
        (diff_y_cntrs/dist_cntrs) * np.sqrt(radius_a ** 2 - dist_cntr_line ** 2)

        y1 = center_y_a + diff_y_cntrs * dist_cntr_line / dist_cntrs - \
        (diff_x_cntrs/dist_cntrs) * np.sqrt(radius_a ** 2 - dist_cntr_line ** 2)
        
        x2 = center_x_a + diff_x_cntrs * dist_cntr_line / dist_cntrs - \
        (diff_y_cntrs/dist_cntrs) * np.sqrt(radius_a ** 2 - dist_cntr_line ** 2)

        y2 = center_y_a + diff_y_cntrs * dist_cntr_line / dist_cntrs + \
        (diff_x_cntrs/dist_cntrs) * np.sqrt(radius_a ** 2 - dist_cntr_line ** 2)
        
        return (x1, y1), (x2, y2)


    def determine_left_right_filters_from_centers(self, x_size, y_size, radius, centers):
        center_x_a, center_y_a = centers[0]
        center_x_b, center_y_b = centers[-1]
        inters_pt1, inters_pt2 = self.determine_intersection_points_of_two_circles(radius, radius, center_x_a, 
            center_x_b, center_y_a, center_y_b)
        if 0 <= inters_pt1[0] < y_size and 0 <= inters_pt1[1] < x_size:
            inters_on_mic = inters_pt1
        elif 0 <= inters_pt2[0] < y_size and 0 <= inters_pt2[1] < x_size:
            inters_on_mic = inters_pt2
        else:
            inters_on_mic = (0,0)
        left_x, left_y = inters_on_mic
        right_x, right_y = y_size - left_x, x_size - left_y

        return left_x, right_x, left_y, right_y


    def filter_overlapping_circles(self, circles, left_x, left_y, right_x, right_y, scan):

        circle_x = np.array([])
        circle_y = np.array([])
        for each_quarter, (xx, yy) in enumerate(circles):
            odd = (each_quarter) % 2
            if scan:
                xxx = np.copy(xx)
                yyy = np.copy(yy)
            else:
                if odd:
                    xxx = xx[(left_x <= xx) & (xx < right_x)]
                    yyy = yy[(left_x <= xx) & (xx < right_x)]
                else:
                    xxx = xx[(left_y <= yy) & (yy < right_y)]
                    yyy = yy[(left_y <= yy) & (yy < right_y)]
                
            circle_x = np.append(circle_x, xxx)
            circle_y = np.append(circle_y, yyy)
            
        return circle_x, circle_y


    def generate_continuous_edges_to_be_excluded(self, pixelsize, x_size, y_size, hole_size):
        x_y_ratio = min(x_size, y_size) / float(max(x_size, y_size))
        if x_y_ratio < .8 and max(x_size, y_size) * pixelsize > 0.9 * hole_size:
            scan = True
            ends_width = 1300.0
        else:
            scan = False
            ends_width = 800.0

        radius = hole_size / (2 * pixelsize)
        x = np.arange(-radius, radius)
        y = np.arange(-radius, radius)
        ends_x_ratio = ends_width / (x_size * pixelsize)
        ends_y_ratio = ends_width / (y_size * pixelsize)

        circles = []
        centers = []
        for each_quarter in list(range(4)):
            odd = (each_quarter) % 2
            xx = None
            if odd:
                center_x = y_size / 2
                xx = np.copy(x) + center_x
                yy = np.sqrt(radius ** 2 - x ** 2)
                if each_quarter == 1:
                    center_y = x_size * (1 - ends_x_ratio) - radius
                    yy = yy + center_y
                elif each_quarter == 3:
                    center_y = x_size * ends_x_ratio + radius
                    yy = -yy + center_y
            elif not scan:
                xx = -np.sqrt(radius ** 2 - y ** 2)
                center_y = x_size / 2
                yy = np.copy(y) + center_y
                if each_quarter == 0:
                    center_x = y_size * ends_y_ratio + radius
                    xx = xx + center_x
                elif each_quarter == 2:
                    center_x = y_size * (1 - ends_y_ratio) - radius
                    xx = -xx + center_x
            if each_quarter in [2, 3] and xx is not None:
                xx = np.flipud(xx)
                yy = np.flipud(yy)
            if xx is not None:
                circles.append((xx, yy))
                centers.append((center_x, center_y))
        
        left_x, right_x, left_y, right_y = self.determine_left_right_filters_from_centers(x_size, y_size, radius, centers)
        
        circle_x, circle_y = self.filter_overlapping_circles(circles, left_x, left_y, right_x, right_y, scan)
        
        return circle_x, circle_y


    def remove_helices_at_edges(self, helices, mic, pixelsize, hole_size):

        mic_np = np.copy(EMNumPy.em2numpy(mic))
        x_size, y_size = mic_np.shape
        
        circle_x, circle_y = self.generate_continuous_edges_to_be_excluded(pixelsize, x_size, y_size, hole_size) 

#         plt.imshow(mic_np, cmap=plt.cm.gray, origin='lower', interpolation='nearest')
#         plt.plot(circle_x, circle_y, '.')
#         plt.legend(loc=0)
#         plt.savefig('test.pdf')
          
        filtered_hels = []
        for each_xcoord, each_ycoord in helices:
            start = each_xcoord[0], each_ycoord[0]
            end = each_xcoord[-1], each_ycoord[-1]
            
            start_z_dir = self.compute_side_of_point_with_respect_to_closest_vector(start, circle_x, circle_y)
            end_z_dir = self.compute_side_of_point_with_respect_to_closest_vector(end, circle_x, circle_y)

            if start_z_dir == 'left' and end_z_dir == 'left':
                pass
            else:
                filtered_hels.append((each_xcoord, each_ycoord))

        return filtered_hels


#     def separate_intersecting_helix(self, each_x, each_y):
#         
#         diff_x = abs(each_x[-1] - each_x[0])
#         diff_y = abs(each_y[-1] - each_y[0])
#         
#         if diff_x >= diff_y:
#             fitt = np.polyfit(each_x, each_y, 1)
#             line_x = np.linspace(each_x[0], each_x[-1], 2)
#             line_y = np.polyval(fitt, line_x)
#         else:
#             fitt = np.polyfit(each_y, each_x, 1)
#             line_y = np.linspace(each_y[0], each_y[-1], 2)
#             line_x = np.polyval(fitt, line_y)
#             
#         distances = self.compute_dist_point_to_line(each_x, each_y, line_x, line_y)
#         if max(distances) < 200:
#             break


#     def compute_dist_point_to_line(self, point_x, point_y, line_x, line_y):
#         """
#         >>> from spring.micprgs.michelixtrace import MicHelixTrace
#         >>> m = MicHelixTrace()
#         >>> m.compute_dist_point_to_line(1.0, 0.0, [-1.0, 2.0], [-1.0, 2.0])
#         0.70710678118654757
#         >>> m.compute_dist_point_to_line(np.arange(10), np.arange(10) + 0.5, [-1.0, 2.0], [-1.0, 2.0])
#         array([ 0.35355339,  0.35355339,  0.35355339,  0.35355339,  0.35355339,
#                 0.35355339,  0.35355339,  0.35355339,  0.35355339,  0.35355339])
#         >>> m.compute_dist_point_to_line(np.arange(10), np.arange(10), [-1.0, 2.0], [-1.0, 2.0])
#         array([ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.])
#         """
#         x1, x2 = line_x
#         y1, y2 = line_y
#     
#         dx21 = x2 - x1
#         dy21 = y2 - y1
#         
#         lensq21 = dx21 * dx21 + dy21 * dy21
#         if lensq21 == 0:
#             #20080821 raise ValueError, "zero length line segment"
#             dy = point_y - y1 
#             dx = point_x - x1 
#             return np.sqrt( dx * dx + dy * dy )  # return point to point distance
#     
#         u = (point_x - x1) * dx21 + (point_y - y1) * dy21
#         u = u / float(lensq21)
#     
#     
#         x = x1 + u * dx21
#         y = y1 + u * dy21    
#     
#         dx30 = point_x - x
#         dy30 = point_y - y
#     
#         return np.sqrt( dx30*dx30 + dy30*dy30 )


    def remove_overlapping_helices_found(self, helices, shape):
        """
        >>> from spring.micprgs.michelixtrace import MicHelixTrace
        >>> m = MicHelixTrace()
        >>> helix_1 = [np.arange(13), np.ones(13)* 16]
        >>> helix_2 = [np.arange(10), np.arange(10)]
        >>> helix_3 = [np.arange(5), np.arange(5)]
        >>> m.remove_overlapping_helices_found([helix_1, helix_2, helix_3], (20, 20))
        [[array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12]), array([ 16.,  16.,  16.,  16.,  16.,  16.,  16.,  16.,  16.,  16.,  16.,
                16.,  16.])], [array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])]]
        """
        
        lengths = [np.sqrt((each_x[-1] - each_x[0]) ** 2 + (each_y[-1] - each_y[0]) ** 2) \
                   for each_x, each_y in helices]

        sorted_helices = [helices[each_helix_id] for each_helix_id in np.argsort(lengths)]
            
        binaries = []
        for each_x_arr, each_y_arr in sorted_helices: 
            binary = np.zeros(shape)
            for each_x, each_y in zip(each_x_arr, each_y_arr):
                window_size = 5
                start_x = each_x - window_size / 2 
                stop_x = each_x + window_size / 2 + 1
                start_y = each_y - window_size / 2 
                stop_y = each_y + window_size / 2 + 1
                binary[start_x:stop_x, start_y:stop_y]=1
            binaries.append(binary)
        
        filtered_helices = []
        for each_helix_id, each_helix in enumerate(sorted_helices):
            all_helices = np.zeros(shape)
            for each_bin_id, each_binary in enumerate(binaries):
                if each_helix_id != each_bin_id:
                    all_helices += each_binary

            all_helices[all_helices > 0] = 1
            overlap = all_helices + binaries[each_helix_id]
            if np.max(overlap) <= 1:
                filtered_helices.append(each_helix)
            else:
                binaries[each_helix_id]=np.zeros(shape)
            
        return filtered_helices


    def write_boxfiles(self, single_helices, tilesize, each_mic):
        
        each_box = os.path.splitext(os.path.basename(each_mic))[0] + os.extsep + 'box'
        for each_xcoord, each_ycoord in single_helices:
            if self.binoption:
                xcoord = each_xcoord * self.binfactor 
                ycoord = each_ycoord * self.binfactor 
            else:
                xcoord = each_xcoord
                ycoord = each_ycoord

            Segment().write_boxfile(xcoord, ycoord, tilesize, each_box)


    def remove_ticks_and_scale_correctly(self, ax3, mic_np):
        ax3.set_xticks([])
        ax3.set_yticks([])
        ax3.set_xlim([0, mic_np.shape[1]])
        ax3.set_ylim([0, mic_np.shape[0]])
        
        return ax3 


    def visualize_traces_in_diagnostic_plot(self, infile, outfile, overlap_cc, binary, helices, mic):
        
        mic_np = np.copy(EMNumPy.em2numpy(mic))

        michelixtrace_plot = DiagnosticPlot()
        self.fig = michelixtrace_plot.add_header_and_footer(self.feature_set, infile, outfile)

        ax1 = michelixtrace_plot.plt.subplot2grid((2,2), (0,0), colspan=1, rowspan=1)
        ax2 = michelixtrace_plot.plt.subplot2grid((2,2), (1,0), colspan=1, rowspan=1)
        ax3 = michelixtrace_plot.plt.subplot2grid((2,2), (0,1), colspan=1, rowspan=2)

        cc_im = ax1.imshow(overlap_cc, cmap=plt.cm.jet, origin='lower', interpolation='nearest')
        ax1 = self.remove_ticks_and_scale_correctly(ax1, mic_np)
        ax1.set_title('Overlapping cross correlation', fontsize=8)
        cax = self.fig.add_axes([0.08, 0.65, 0.01, 0.25])
        cbar = self.fig.colorbar(cc_im, cax)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(5)

        ax2.set_title('Thresholded at {0}'.format(self.cc_threshold), fontsize=8)
        ax2.imshow(-1 * binary, cmap=plt.cm.gray, origin='lower', interpolation='nearest')
        ax2 = self.remove_ticks_and_scale_correctly(ax2, mic_np)
#         ax1.colorbar()
#         ax2.hist(binary)

        ax3.imshow(mic_np, cmap=plt.cm.gray, origin='lower', interpolation='nearest')
        for each_xcoord, each_ycoord in helices:
            ax3.plot(each_xcoord, each_ycoord, 'o', markersize=1)

        ax3 = self.remove_ticks_and_scale_correctly(ax3, mic_np)
        
        self.fig.savefig(outfile, dpi=600)

        return outfile


    def trace_helices_in_micrographs(self, micrograph_files, outfiles):
        ref_power, ref_profile, tilesize_pix = self.prepare_power_from_reference(self.reference_file)
        for each_mic, each_outfile in zip(micrograph_files, outfiles):
            each_mic, pixelsize, tilesize_bin = MicrographExam().bin_micrograph(each_mic, self.binoption,
            self.binfactor, self.ori_pixelsize, self.tile_size_A, self.tempdir)

            mic = EMData()
            mic.read_image(each_mic)
            mic.process_inplace('normalize')

            img_stack, pw_stack, xy_center_grid = self.generate_stack_of_overlapping_images_powers(mic, tilesize_pix, 
            self.tile_overlap)

            angles = self.orient_reference_power_with_overlapping_powers(pw_stack, ref_power, xy_center_grid)
            overlap_pix = int(round(self.tile_overlap * self.tile_size_A / pixelsize))
            rhos, thetas, cross_corr = self.find_translations_by_projecting(angles, xy_center_grid, img_stack, 
            ref_profile, overlap_pix, mic)

            binary, overlap_cc = self.build_binary_image_of_segmented_helices(rhos, thetas, cross_corr, xy_center_grid,
            mic, tilesize_pix, self.tile_overlap, self.cc_threshold)

            single_helices = self.perform_connected_component_analysis_including_hought(binary, tilesize_pix,
            self.tile_overlap, self.order_fit)
 
            if self.exclude_carbon:
                single_helices = self.remove_helices_at_edges(single_helices, mic, pixelsize, self.hole_size_A)
             
            single_helices = self.remove_overlapping_helices_found(single_helices, binary.shape)
            self.visualize_traces_in_diagnostic_plot(each_mic, each_outfile, overlap_cc, binary, single_helices, mic)

            self.write_boxfiles(single_helices, tilesize_pix, each_mic)

            os.remove(img_stack)
            os.remove(pw_stack)
            if self.binoption:
                os.remove(each_mic)

    def trace_helices(self):

        if len(self.micrograph_files) < self.cpu_count:
            self.cpu_count = len(self.micrograph_files)
            self.feature_set.parameters['Number of CPUs']=self.cpu_count
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        self.tempdir = Temporary().mktmpdir(self.temppath)
        
        outfiles = Features().rename_series_of_output_files(self.micrograph_files, self.outfile)

        self.trace_helices_in_micrographs(self.micrograph_files, outfiles)

        os.rmdir(self.tempdir)
        self.log.endlog(self.feature_set)
        
def main():
    # Option handling
    parset = MicHelixTracePar()
    mergeparset = OptHandler(parset)

    ######## Program
    micrograph = MicHelixTrace(mergeparset)
    micrograph.trace_helices()

if __name__ == '__main__':
    main()
