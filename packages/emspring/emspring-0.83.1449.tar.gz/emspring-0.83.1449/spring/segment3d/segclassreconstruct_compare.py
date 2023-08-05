# Author: Carsten Sachse 12-Jun-2013
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from EMAN2 import EMData, EMNumPy, Util, periodogram
from collections import namedtuple
from fundamentals import mirror
from morphology import binarize
from scipy import special
from spring.particle2d.particlealign2d import ParticleAlign2d
from spring.micprgs.scansplit import Micrograph
from spring.segment2d.segmentexam import SegmentExam
from spring.segment3d.segclassreconstruct_assist import SegClassReconstructAssist
from statistics import ccc
from tabulate import tabulate
from utilities import model_circle, model_blank
import numpy as np
import os


class SegClassReconstructCompareMontage(SegClassReconstructAssist):  
    def normalize_power_spectrum(self, power):
        stat = Micrograph().get_statistics_from_image(power)
        freq, gray_bins = np.histogram(np.copy(EMNumPy.em2numpy(power)), 65535)
        most_frequent = gray_bins[np.argmax(freq)]
        
        power = (power - most_frequent) / stat.sigma
         
        return power
    

    def window_left_half_of_spectrum(self, segment_size, thresholded_class_periodogram):
        if (segment_size) % 2 == 0:
            half_panel_width = segment_size / 2 + 1
        else:
            half_panel_width = segment_size / 2
        offset = int(-segment_size / 4) + 1
        if (half_panel_width + offset) > segment_size / 4:
            offset += 1
        windowed_class_periodogram = Util.window(thresholded_class_periodogram, half_panel_width, segment_size, 1, 
            offset, 0, 0)
        
        montage_width = half_panel_width * 2
        
        return windowed_class_periodogram, montage_width
    

    def prepare_class_avg_periodogram_for_montage(self, class_avg_periodogram, segment_size):
        thresholded_class_periodogram = \
        Micrograph().adjust_gray_values_for_print_and_optimal_display(class_avg_periodogram)
        
        thresholded_class_periodogram = self.normalize_power_spectrum(thresholded_class_periodogram)
        
        windowed_class_periodogram, montage_width = \
        self.window_left_half_of_spectrum(segment_size, thresholded_class_periodogram)
        
        windowed_class_periodogram = Util.pad(windowed_class_periodogram, montage_width, segment_size, 1, 
        -montage_width / 4, 0, 0, '0')
        
        return windowed_class_periodogram


    def montage_class_avg_vs_reprojection_periodogram(self, segment_size, windowed_class_periodogram,
    reprojection_periodogram):
        thresholded_periodogram = \
        Micrograph().adjust_gray_values_for_print_and_optimal_display(reprojection_periodogram)
        
        thresholded_periodogram = self.normalize_power_spectrum(thresholded_periodogram)
        
        windowed_helix_periodogram, montage_width = \
        self.window_left_half_of_spectrum(segment_size, thresholded_periodogram)
        
        windowed_helix_periodogram = mirror(windowed_helix_periodogram)
        
        windowed_helix_periodogram = Util.pad((windowed_helix_periodogram), montage_width, segment_size, 1, 
        montage_width / 4, 0, 0, '0')
        
        class_vs_helix_periodogram_montage = (windowed_class_periodogram + windowed_helix_periodogram) * (-1)
        
        return class_vs_helix_periodogram_montage
    

    def montage_exp_vs_sim_power_spectrum(self, power_spectrum, ideal_power_img):
        """
        >>> from utilities import model_gauss_noise
        >>> power_size = 25
        >>> zero = model_gauss_noise(1, power_size, power_size)
        >>> one = model_gauss_noise(10, power_size, power_size)
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> montage = SegClassReconstruct().montage_exp_vs_sim_power_spectrum(one, zero)
        """
        power_size = power_spectrum.get_xsize()
        prepared_power = self.prepare_class_avg_periodogram_for_montage(power_spectrum, power_size)
        
        montage_side_by_side = self.montage_class_avg_vs_reprojection_periodogram(power_size, prepared_power,
        ideal_power_img)
 
        return montage_side_by_side
 

class SegClassReconstructCompare(SegClassReconstructCompareMontage):  
    def project_through_reference_using_parameters_and_log(self, projection_parameters, alignment_size, prj_ids,
    projection_stack, reference_volume):
        self.project_locally(reference_volume, projection_parameters, projection_stack)
        proj_loginfo = []
        img = EMData()
        img.read_image(projection_stack)
        img_width = img.get_xsize() 
        for each_prj_id, each_projection_parameter in enumerate(projection_parameters):
            each_total_prj_id = prj_ids[each_prj_id]
            proj_loginfo += [[each_total_prj_id, each_prj_id] + each_projection_parameter]
            img.read_image(projection_stack, each_prj_id)
#             img = Util.window(img, img_width, alignment_size, 1, 0, 0, 0)
            if img_width < alignment_size:
                img = Util.pad(img, alignment_size, alignment_size, 1, 0, 0, 0, 'avg')
            if img_width > alignment_size:
                img = Util.window(img, alignment_size, alignment_size, 1, 0, 0, 0)
                
            img.write_image(projection_stack, each_prj_id)
        
        msg = tabulate(proj_loginfo, ['stack_id', 'local_id', 'phi', 'theta', 'psi', 'x-shift', 'y-shift'])
        self.log.tlog('The volume was projected according to the following parameters:\n{0}'.format(msg))
        
        return projection_stack


    def make_rec_stack_info(self):
        return namedtuple('stack_info', 'file_name reference_vol alignment_size')


    def get_helical_error_string(self):
        return 'helical_ccc_error mean_helical_ccc phase_residual ' + \
        'amp_correlation, amp_corr_quarter_nyquist, amp_corr_half_nyquist, amp_corr_3quarter_nyquist ' + \
        'segment_count asym_unit_count'
    

    def make_helical_error_tuple(self):
        err_tuple = namedtuple('errors_helical', self.get_helical_error_string())
        return err_tuple
        

    def get_quarter_half_3quarter_nyquist_average_from_amp_correlation(self, amp_correlation):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> SegClassReconstruct().get_quarter_half_3quarter_nyquist_average_from_amp_correlation(range(10))
        [0.5, 2.0, 3.0, 4.5]
        """
        vals = [np.mean(amp_correlation[:int(each_ratio*len(amp_correlation))]) for each_ratio in [0.25, 0.5, 0.75, 1.0]]
        
        return vals
    
        
    def compute_amplitude_correlation_between_sim_and_exp_power_spectrum(self, sim_power, exp_power):
        power_size = sim_power.get_xsize()
        max_radius = power_size / 2
        
        amp_cc = []
        for each_radius in range(max_radius):
            outer_circle = model_circle(each_radius + 1, power_size, power_size)
            inner_circle = model_circle(each_radius, power_size, power_size)
            circle = outer_circle - inner_circle
            
            amp_cc.append(ccc(sim_power, exp_power, circle))
            
        return amp_cc
    
        
    def pad_mask_and_compute_power(self, prj, pad_size, rect_mask=None):
        if rect_mask is not None:
            prj *= rect_mask
        pad_prj = Util.pad(prj, pad_size * prj.get_xsize(), pad_size * prj.get_ysize(), 1, 0, 0, 0, '0')
        sim_power = periodogram(pad_prj)

        return sim_power


    def determine_mean_ccc_deviation_within_symmetry_related_views(self, rec_stack, Euler_angles_rec, helixwidthpix,
    measure_phase_residual=False, measure_amp_corr=False, keep_central=False):
        
        reference_volume = EMData()
        reference_volume.read_image(rec_stack.reference_vol)
        
        prj_ids = np.arange(len(Euler_angles_rec))
        sym_ids = Euler_angles_rec[:,0]
        stack_ids = Euler_angles_rec[:,1]
        
        phis = Euler_angles_rec[:,2]
        thetas = Euler_angles_rec[:,3]
        psis = Euler_angles_rec[:,4]
        xx = Euler_angles_rec[:,5]
        yy = Euler_angles_rec[:,6]
        
        prj_Eulers = [[phi, theta, psi, 0.0, 0.0] for (phi, theta, psi) in zip(phis, thetas, psis)]

        projection_stack = os.path.join(os.path.dirname(rec_stack.file_name), 'rec_stack_reproj.hdf')
        
        projection_stack = self.project_through_reference_using_parameters_and_log(prj_Eulers, rec_stack.alignment_size,
        prj_ids, projection_stack, reference_volume)
        
        rect_mask = SegmentExam().make_smooth_rectangular_mask(helixwidthpix, rec_stack.alignment_size, 
        rec_stack.alignment_size, 0.15)

        circle = ParticleAlign2d().make_smooth_circular_mask(int(0.70 * rec_stack.alignment_size), 0,
        rec_stack.alignment_size, 0.15)
 
        rect_mask *= circle
        
        prj = EMData()
        rec_img = EMData()
        
        stdevs = []
        cccs = []
        phase_resid = []
        pad_size = 2
        amp_corrs = np.array([0.0] * (rec_stack.alignment_size * pad_size / 2))
        amp_count = 0
        
        central_prj = []
        central_rec_img = []
        for each_stack_id in np.unique(stack_ids):
            this_sym_ids = np.int64(sym_ids[stack_ids == each_stack_id])
            if np.isscalar(this_sym_ids):
                this_sym_ids = [this_sym_ids]
            stack_id_cccs = []
            for each_prj_id, each_sym_id in enumerate(this_sym_ids):
                rec_img.read_image(rec_stack.file_name, int(each_sym_id))
                prj.read_image(projection_stack, each_prj_id)
                stack_id_cccs.append(ccc(prj, rec_img, rect_mask))
                if measure_phase_residual:
                    phase_resid.append(prj.cmp('phase', rec_img))
                if measure_amp_corr:
                    sim_power = self.pad_mask_and_compute_power(prj, pad_size, rect_mask)
                    exp_power = self.pad_mask_and_compute_power(rec_img, pad_size, rect_mask)

                    pad_img = Util.pad(rec_img * rect_mask, pad_size * rec_stack.alignment_size, 
                    pad_size * rec_stack.alignment_size, 1, 0, 0, 0, 'average')

                    exp_power = periodogram(pad_img)
                    amp_res = self.compute_amplitude_correlation_between_sim_and_exp_power_spectrum(sim_power, exp_power)
                    amp_corrs += amp_res
                    amp_count += 1
#                rec_img *= rect_mask
#                rec_img.append_image('mytest.hdf')
#                prj.append_image('mytest.hdf')
            stdevs.append(np.std(stack_id_cccs))
            cccs += stack_id_cccs
            if keep_central:
                dist = np.sqrt(xx[this_sym_ids] **2 + yy[this_sym_ids] **2)
                central_id = int(this_sym_ids[np.argmin(dist)])
                prj.read_image(projection_stack, central_id)
                central_prj.append(prj.copy())
                rec_img.read_image(rec_stack.file_name, central_id)
                central_rec_img.append(rec_img.copy())
            
        if measure_amp_corr and amp_count !=0:
            amp_corrs /= float(amp_count)

        if measure_phase_residual:
            phase_resid_avg = np.mean(phase_resid)
        else:
            phase_resid_avg = None

        segment_count = len(np.unique(stack_ids))
        asym_unit_count = len(sym_ids)
        err_tuple = self.make_helical_error_tuple()

        quarter, half, three_quarter, full = \
        self.get_quarter_half_3quarter_nyquist_average_from_amp_correlation(amp_corrs)

        mean_error = err_tuple(np.mean(stdevs), np.mean(cccs), phase_resid_avg, full, quarter, half, three_quarter, 
        segment_count, asym_unit_count) 
        
        os.remove(projection_stack)

        return mean_error, central_prj, central_rec_img
    
    
class SegClassReconstructComparePredictLayerLines(SegClassReconstructCompare):

    def get_list_of_bessel_order_maxima(self, order_count):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> SegClassReconstruct().get_list_of_bessel_order_maxima(10)
        array([  0. ,   1.8,   3.1,   4.2,   5.3,   6.4,   7.5,   8.6,   9.6,  10.7])
        """
        arr = np.arange(0, 25, 0.1)
        primarymax = np.array([arr[np.argmax(special.jv(each_order, arr))] for each_order in range(order_count)])
        
        return primarymax
    

    def adjust_bessel_order_if_out_of_plane_not_zero(self, out_of_plane_tilt, layer_line_position,
    assigned_bessel_order, helix_radius, bessel_maxima):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> s = SegClassReconstruct()
        >>> bes = s.get_list_of_bessel_order_maxima(20)
        >>> s.adjust_bessel_order_if_out_of_plane_not_zero(0, 0.1, 3, 180.0, bes) 
        3
        >>> s.adjust_bessel_order_if_out_of_plane_not_zero(3, 0.1, 3, 180.0, bes)
        0
        """
        if out_of_plane_tilt != 0:
            meridional_dist = np.tan(np.deg2rad(out_of_plane_tilt)) * layer_line_position
            pos_prim_point = 2 * np.pi * meridional_dist * helix_radius
            shifted_maxs = bessel_maxima - pos_prim_point
            adjusted_bessel_order = np.argmin(np.abs(shifted_maxs[abs(assigned_bessel_order)] - bessel_maxima))
            if assigned_bessel_order < 0:
                adjusted_bessel_order = -adjusted_bessel_order
        else:
            adjusted_bessel_order = assigned_bessel_order

        return adjusted_bessel_order


    def adjust_reciprocal_layer_line_pitches_by_out_of_plane_angle(self, pitches, out_of_plane_tilt=0):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> s = SegClassReconstruct()
        >>> s.adjust_reciprocal_layer_line_pitches_by_out_of_plane_angle(0.1, 0)
        0.10000000000000001
        >>> s.adjust_reciprocal_layer_line_pitches_by_out_of_plane_angle(0.1, 12)
        0.10223405948650292
        """
        tilt_corrected_pitches = pitches / np.cos(np.deg2rad(out_of_plane_tilt)) 

        return tilt_corrected_pitches


    def generate_layerline_bessel_pairs_from_rise_and_rotation(self, rise_rotation_pair, rot_sym, width_of_helix,
    pixelsize, low_resolution_cutoff, high_resolution_cutoff, out_of_plane_tilt=0.0):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> s = SegClassReconstruct()
        >>> sym = (1.408, 22.03)
        >>> s.generate_layerline_bessel_pairs_from_rise_and_rotation(sym, 1, 180.0, 5.0, 300, 10) #doctest: +NORMALIZE_WHITESPACE
        [(0.086926286509040343, 2), (0.072087658592848908, 18), 
        (0.058298839853086926, -15), (0.043461254291798861, 1), 
        (0.028626227349497609, 17), (0.01483591478250549, -16)]
        >>> s.generate_layerline_bessel_pairs_from_rise_and_rotation(sym, 1, 180.0, 5.0, 300, 10, 3) #doctest: +NORMALIZE_WHITESPACE
        [(0.087045579450445165, 0), (0.072186587802618302, 16), 
        (0.058378846032642748, -13), (0.043520898170190836, 0), 
        (0.028665512438036268, 16), (0.014856274790782758, -16)]
        >>> s.generate_layerline_bessel_pairs_from_rise_and_rotation(sym, 2, 180.0, 5.0, 300, 10, 3) #doctest: +NORMALIZE_WHITESPACE
        [(0.087045579450445165, 0), (0.072186587802618302, 16), 
        (0.014856274790782758, -16)]
        """
        helical_rise = rise_rotation_pair[0]
        helical_rotation = rise_rotation_pair[1]
        pitch_of_helix = helical_rise * 360 / helical_rotation
        
        helix_radius = width_of_helix / 2.0
        maximum_n = int((np.pi * helix_radius)/pixelsize) + 2 
        pitch_grid = np.zeros((maximum_n, maximum_n))
        bessel_grid = np.zeros((maximum_n, maximum_n))
        
        n_combinations = m_combinations = list(range(-maximum_n / 2, maximum_n / 2, 1))
        for n_index, each_n in enumerate(n_combinations):
            n_is_multiple_of_rotational_symmetry = each_n % rot_sym
            if n_is_multiple_of_rotational_symmetry == 0:
                for m_index, each_m in enumerate(m_combinations):
                    layer_line_position = each_n / pitch_of_helix + each_m / helical_rise
                    if layer_line_position == 0:
                        pass
                    else:
                        pitch_grid[n_index][m_index]=1 / layer_line_position
                        bessel_grid[n_index][m_index]=each_n
            
#        img = plt.imshow(pitch_grid, cmap=cm.jet, interpolation='nearest')
#        plt.savefig('test.pdf', dpi=600)
                
        pitch_sequence = pitch_grid.ravel()
        
        bessel_maxima = self.get_list_of_bessel_order_maxima(1000)
        unique_pitches = np.unique(np.round(np.abs(pitch_sequence), 3))
        pitches = []
        orders = []
        for each_unique_pitch in unique_pitches:
            if high_resolution_cutoff < each_unique_pitch < low_resolution_cutoff:
                n_m_indices_of_pitch = np.argwhere(np.round(pitch_grid, 3) == each_unique_pitch)
                
                bessel_orders = np.zeros(len(n_m_indices_of_pitch))
                for each_index, each_n_m_index in enumerate(n_m_indices_of_pitch):
                    each_n_idx, each_m_idx = each_n_m_index
                    bessel_order = bessel_grid[each_n_idx][each_m_idx]
                    bessel_orders[each_index]=bessel_order
                
                if len(n_m_indices_of_pitch) > 0:
                    min_index = np.argmin(np.abs(bessel_orders))
                    assigned_bessel_order = int(bessel_orders[min_index])
                
                    layer_line_position = 1 / each_unique_pitch
                    pitches.append(layer_line_position)
                    
                    adjusted_bessel_order = self.adjust_bessel_order_if_out_of_plane_not_zero(out_of_plane_tilt,
                    layer_line_position, assigned_bessel_order, helix_radius, bessel_maxima)
                    
                    orders.append(adjusted_bessel_order)

        pitches = np.array(pitches)
        
        tilt_corrected_pitches = self.adjust_reciprocal_layer_line_pitches_by_out_of_plane_angle(pitches,
        out_of_plane_tilt)
        
        unique_pitch_bessel_pairs = list(zip(tilt_corrected_pitches, orders))
        
        msg = tabulate(unique_pitch_bessel_pairs, ['layer_line_position', 'bessel_order'])
        self.log.ilog('The following layer_line_position/Bessel pairs have been computed:\n{0}'.\
        format(msg))
        
        return unique_pitch_bessel_pairs
    
            
class SegClassReconstructCompareLayerFilter(SegClassReconstructComparePredictLayerLines):
    def create_single_layer_line(self, linex, linex_fine, bessel_order, layer_line_length):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> b_len = np.pi * 180.0 / 1.2
        >>> ll_len = 50
        >>> b_fine = np.linspace(0, b_len, 100 * ll_len)
        >>> b = np.linspace(0, b_len, ll_len)
        >>> s = SegClassReconstruct()
        >>> ll = s.create_single_layer_line(b, b_fine, 4, ll_len)
        >>> np.round(ll, 2)
        array([ 0.  ,  0.26,  0.18,  0.15,  0.13,  0.11,  0.09,  0.08,  0.06,
                0.04,  0.03,  0.01,  0.  ,  0.01,  0.02,  0.03,  0.04,  0.05,
                0.05,  0.06,  0.06,  0.06,  0.05,  0.05,  0.04,  0.03,  0.02,
                0.01,  0.  ,  0.01,  0.02,  0.02,  0.03,  0.04,  0.04,  0.04,
                0.04,  0.04,  0.04,  0.04,  0.03,  0.03,  0.02,  0.01,  0.01,
                0.  ,  0.01,  0.02,  0.02,  0.03])
        """
        bessel_function = np.abs(special.jv(bessel_order, linex_fine))
        layer_line = np.zeros((layer_line_length))
        for each_pixel, each_val in enumerate(layer_line):
            bessel_index_closest = np.argmin(np.abs(linex_fine - linex[each_pixel]))
            layer_line[each_pixel] += abs(bessel_function[bessel_index_closest])
        
        return layer_line
    

    def prepare_ideal_power_spectrum_from_layer_lines(self, layerline_bessel_pairs, width_of_helix, power_size,
    pixelsize, binary=False):
        if type(power_size) != tuple:
            power_width = power_size
        else:
            power_size, power_width = power_size
        bessel_length = np.pi * width_of_helix / pixelsize
        layer_line_length = power_width / 2
        linex = np.linspace(0, bessel_length, layer_line_length)
        linex_fine = np.linspace(0, bessel_length, 100 * layer_line_length)
        
        ideal_layer_line_power = np.zeros((power_size / 2, layer_line_length))
        for each_layer_line_pair in layerline_bessel_pairs:
            layer_line_position_in_pixel = int(round(each_layer_line_pair[0] * pixelsize * power_size))
            if layer_line_position_in_pixel < power_size / 2:
                bessel_order = abs(each_layer_line_pair[1])
                layer_line = self.create_single_layer_line(linex, linex_fine, bessel_order, layer_line_length)
                ideal_layer_line_power[layer_line_position_in_pixel] += layer_line
                    
        ideal_power = np.hstack((np.fliplr(np.flipud(ideal_layer_line_power)), np.flipud(ideal_layer_line_power)))
        upper_half = np.roll(ideal_power, 1, axis=0)
        lower_half = np.flipud(ideal_power)
        ideal_power = np.vstack((upper_half, lower_half))
        ideal_power_img = EMNumPy.numpy2em(np.copy(ideal_power))
        meridian_solid = model_blank(power_width, 1, 1, 1)
        ideal_power_img.set_row(meridian_solid, power_size / 2)
        
        if binary:
            ideal_power_img = binarize(ideal_power_img, 0.000001)
        
        return ideal_power_img, linex_fine
    

    def filter_image_by_fourier_filter_while_padding(self, image, image_size, padsize, ideal_power_img):
        image = Util.pad(image, padsize, padsize, 1, 0, 0, 0, 'average')
        image = image.filter_by_image(ideal_power_img)
        image = Util.window(image, image_size, image_size, 1, 0, 0, 0)
        
        return image
    

class SegClassReconstructCompareVisual(SegClassReconstructCompareLayerFilter):  
    def determine_pixel_width_of_helix_for_display(self, segment_size, helixwidthpix):
        display_width = max(segment_size / 2, int(2.2 * helixwidthpix + 1))
        
        return display_width
     
     
    def prepare_class_avg_for_montage(self, class_avg, segment_size, helixwidthpix):
        display_width = self.determine_pixel_width_of_helix_for_display(segment_size, helixwidthpix)
        
        if display_width < segment_size:
            windowed_class_avg = Util.window(class_avg, display_width, segment_size, 1, 0, 0, 0)
        else:
            windowed_class_avg = class_avg.copy()
            
        windowed_class_avg.process_inplace('normalize')
        
        windowed_class_avg = Util.pad(windowed_class_avg, 2 * display_width, segment_size, 1, -display_width / 2, 0, 0,
        'average')
        
        return windowed_class_avg


    def montage_class_avg_vs_reprojection(self, segment_size, helixwidthpix, windowed_class_avg, symmetry_reprojection):
        thresholded_sym_reprojection = \
        Micrograph().adjust_gray_values_for_print_and_optimal_display(symmetry_reprojection)
        
        display_width = self.determine_pixel_width_of_helix_for_display(segment_size, helixwidthpix)
        if display_width < segment_size:
            windowed_helix = Util.window(thresholded_sym_reprojection, display_width, segment_size, 1, 0, 0, 0)
        else:
            windowed_helix = thresholded_sym_reprojection.copy()
            
        windowed_helix.process_inplace('normalize')
        windowed_helix = Util.pad(windowed_helix, 2 * display_width, segment_size, 1, display_width / 2, 0, 0)
        class_vs_helix_montage = windowed_class_avg + windowed_helix
        
        return class_vs_helix_montage


    def set_header_with_helical_parameters(self, each_rise_rotation_pair, segment, point_symmetry=None):
        decimal_place = 5
        
        rise_rotation_pair = '({0}, {1})'.format(round(each_rise_rotation_pair[0], decimal_place),
        round(each_rise_rotation_pair[1], decimal_place))
        
        segment.set_attr('rise/rotation', rise_rotation_pair)
        
        if each_rise_rotation_pair[1] != 0:
            each_pitch_unit_pair = self.convert_rise_rotation_pair_to_pitch_unit_pair(each_rise_rotation_pair)
        
            pitch_unit_pair = '({0}, {1})'.format(round(each_pitch_unit_pair[0], decimal_place),
            round(each_pitch_unit_pair[1], decimal_place))
        
            segment.set_attr('pitch/unit_number', pitch_unit_pair)
        if point_symmetry is not None:
            segment.set_attr('point_sym', point_symmetry)
        
        return segment
    

    def write_out_side_by_side_display_of_images_and_power_spectra(self, class_avg, reproj, img_id, montage_reprj,
    montage_power, each_rise_rotation_pair):
        
        segment_size = reproj.get_xsize()
        rect_mask = SegmentExam().make_smooth_rectangular_mask(self.helixwidthpix, segment_size, segment_size, 0.15)
        circle = ParticleAlign2d().make_smooth_circular_mask(int(0.70 * segment_size), 0, segment_size, 0.15)
        rect_mask *= circle

        windowed_class_avg = self.prepare_class_avg_for_montage(class_avg * rect_mask, segment_size, self.helixwidthpix)
        
        montage_real = self.montage_class_avg_vs_reprojection(segment_size, self.helixwidthpix, windowed_class_avg,
        reproj * rect_mask)
        
        montage_real = self.set_header_with_helical_parameters(each_rise_rotation_pair, montage_real)
        montage_real.write_image(montage_reprj, img_id)

        pad_size = 3
        sim_power = self.pad_mask_and_compute_power(reproj, pad_size, rect_mask)
        exp_power = self.pad_mask_and_compute_power(class_avg, pad_size, rect_mask)
        montage_fourier = self.montage_exp_vs_sim_power_spectrum(exp_power, sim_power)

        montage_fourier = self.set_header_with_helical_parameters(each_rise_rotation_pair, montage_fourier)
        montage_fourier.write_image(montage_power, img_id)