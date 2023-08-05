# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import EMData, Util, Transform, EMUtil
from filter import fit_tanh, filt_tanl, filt_table
from fundamentals import rot_shift2D
from random import randint
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segment import Segment
from spring.segment2d.segmentalign2d_prep import SegmentAlign2dPar, SegmentAlign2dPreparation
from spring.segment2d.segmentexam import SegmentExam
from statistics import fsc
from tabulate import tabulate
from utilities import compose_transform2
import numpy as np
import os

        
class SegmentAlign2dImagesToReferences(SegmentAlign2dPreparation):
    def put_random_image_in_reference_image_container(self, reference_stack, assigned_images, each_ref_id,
    alignment_stack_name):
        
        stack_image_count = EMUtil.get_image_count(alignment_stack_name)
        assigned_images[each_ref_id] = []
        random_image_id = randint(0, stack_image_count - 1)
        assigned_images[each_ref_id].append(random_image_id)
        
        random_image = EMData()
        random_image.read_image(alignment_stack_name, random_image_id)
        reference_stack[each_ref_id] = reference_stack[each_ref_id]._replace(odd_average=random_image)
                
        return reference_stack
    

    def compute_average_and_normalize(self, reference_stack, each_ref_id):
        updated_average = reference_stack[each_ref_id].odd_average + reference_stack[each_ref_id].even_average
        
        updated_average /= float(reference_stack[each_ref_id].number_of_images[''])
        reference_stack[each_ref_id] = reference_stack[each_ref_id]._replace(total_average=updated_average) 
        
        return reference_stack
                

    def compute_variance_and_normalize(self, reference_stack, each_ref_id):
        cls_avg = reference_stack[each_ref_id].total_average
        cls_var = reference_stack[each_ref_id].variance
        member_count = reference_stack[each_ref_id].number_of_images['']
        
        var = (cls_var - cls_avg * cls_avg * member_count) / (member_count - 1)
        reference_stack[each_ref_id] = reference_stack[each_ref_id]._replace(variance=var)
        
        return reference_stack
    
    
    def calculate_averages(self, reference_stack, iteration_id, each_ref_id):
        
        frsc = fsc(reference_stack[each_ref_id].odd_average, reference_stack[each_ref_id].even_average, 1.0,
        'drm_it{0:03}_ref{0:04}.dat'.format(iteration_id, each_ref_id))
        
        reference_stack = self.compute_average_and_normalize(reference_stack, each_ref_id)
        reference_stack = self.compute_variance_and_normalize(reference_stack, each_ref_id)
            
        return frsc, reference_stack
    

class SegmentAlign2dAlign(SegmentAlign2dImagesToReferences):
    def low_pass_filter_reference_according_to_frc(self, total_average, frc_line):
        """
        * Function to filter low-resolution reference image with a hyperbolic tangent that was fitted \
        against fourier ring correlation
         
        Prepare the reference in 2D alignment, i.e., low-pass filter and center.
        Input: list ref_data
        2 - raw average
        3 - fsc result
        Output: filtered, centered, and masked reference image
        apply filtration (FRC) to reference image:
        
        """
        frequency_cutoff, filter_falloff_width = fit_tanh(frc_line)
        filter_falloff_width = min(filter_falloff_width, 0.12)
        frequency_cutoff = max(min(0.4,frequency_cutoff),0.2)
        msg = 'Tangent filter:  cut-off frequency = %10.3f  fall-off = %10.3f' \
                                        %(frequency_cutoff, filter_falloff_width)
        self.log.ilog(msg)
        
        tanl_filtered_reference = filt_tanl(total_average, frequency_cutoff, filter_falloff_width)
        
        return  tanl_filtered_reference


    def generate_reference_rings_from_image(self, reference_image, polar_interpolation_parameters, ring_weights,
    image_dimension, full_circle_mode='F'):
        center_x = image_dimension / 2 + 1
        center_y = center_x

        cimage = Util.Polar2Dm(reference_image, center_x, center_y, polar_interpolation_parameters, full_circle_mode)
        Util.Normalize_ring(cimage, polar_interpolation_parameters)
        Util.Frngs(cimage, polar_interpolation_parameters)
        Util.Applyws(cimage, polar_interpolation_parameters, ring_weights)
        
        return cimage


    def make_rings_and_prepare_cimage_header(self, image_dimension, polar_interpolation_parameters, ring_weights,
    reference_image):
        cimage = self.generate_reference_rings_from_image(reference_image, polar_interpolation_parameters, ring_weights,
        image_dimension)

        phi = 0
        theta = 90.0
        psi = 270.0
        n1 = np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi))
        n2 = np.sin(np.deg2rad(theta)) * np.sin(np.deg2rad(phi))
        n3 = np.cos(np.deg2rad(theta))
        cimage.set_attr_dict({'n1':n1, 'n2':n2, 'n3':n3})
        cimage.set_attr('phi', phi)
        cimage.set_attr('theta', theta)
        cimage.set_attr('psi', psi)

        return cimage


    def prepare_reference_images_for_alignment(self, mask, reference_stack):
        self.log.fcttolog()
        ringref = []
        references_image_count = len(reference_stack)
        
        image_dimension = mask.get_xsize()
        
        self.log.dlog('Mask pixel dimensions: {0} and reference pixel dimensions: {1}'.format(image_dimension,
        reference_stack[0].total_average.get_xsize()))
                      
        polar_interpolation_parameters, ring_weights = self.prepare_empty_rings(1, image_dimension / 2 - 2, 1)
        
        for each_ref_id in list(range(references_image_count)):
            reference_stack[each_ref_id].total_average.process_inplace('normalize.mask', {'mask':mask,
            'no_sigma':1})
            
            reference_image = reference_stack[each_ref_id].total_average * mask
            
            cimage = self.make_rings_and_prepare_cimage_header(image_dimension, polar_interpolation_parameters,
            ring_weights, reference_image)
            
            ringref.append(cimage) 

            reference_stack[each_ref_id].odd_average.to_zero()
            reference_stack[each_ref_id].even_average.to_zero()
            reference_stack[each_ref_id].total_average.to_zero()
            reference_stack[each_ref_id].variance.to_zero()
            reference_stack[each_ref_id].number_of_images[''] = 0
            
        return ringref, polar_interpolation_parameters, ring_weights, reference_stack
    

    def define_parameters_for_alignment(self, alignment_stack_name, alignment_info, ringref):
        references_image_count = len(ringref)
        assigned_images = [[] for each_reference_img in list(range(references_image_count))]
        align_img = EMData()
        align_img.read_image(alignment_stack_name)
        center_x = center_y = align_img.get_xsize() / 2 + 1
        determined_params = []
        image_nt = self.get_image_list_named_tuple()
        dummy_transform = Transform({'type':'spider', 'phi':0.0, 'theta':90.0, 'psi':270.0})
        x_range = self.x_range_A / (7.0 * self.pixelsize)
        y_range = self.y_range_A / (7.0 * self.pixelsize)
        x_limit = self.x_limit_A / alignment_info.pixelsize
        y_limit = self.y_limit_A / alignment_info.pixelsize
        translation_step = 1
        
        return align_img, (x_range, y_range), (x_limit, y_limit), translation_step, center_x, center_y, dummy_transform,\
        image_nt, determined_params, assigned_images


    def limit_search_range_based_on_previous_alignment(self, local_prev_shift_x, x_limit, fine_x_range):
        """
        >>> from spring.segment2d.segmentalign2d import SegmentAlign2d
        >>> s = SegmentAlign2d()
        >>> s.limit_search_range_based_on_previous_alignment(2.75, 3, 0.5)
        2.5
        >>> s.limit_search_range_based_on_previous_alignment(2.25, 3, 0.5)
        2.25
        >>> s.limit_search_range_based_on_previous_alignment(-2.75, 3, 0.5)
        -2.5
        >>> s.limit_search_range_based_on_previous_alignment(2.05, 3, 3)
        0
        >>> s.limit_search_range_based_on_previous_alignment(2.05, 5, 3)
        2
        """
        x_range_border = x_limit - fine_x_range
        if local_prev_shift_x > x_range_border:
            local_prev_shift_x = x_range_border
        elif local_prev_shift_x < -x_range_border:
            local_prev_shift_x = -x_range_border

        return local_prev_shift_x


    def perform_coarse_restrained_alignment(self, alignment_stack_name, ringref, polar_interpolation_parameters,
    alignment_info, refine_locally, full_circle_mode, align_img, search_ranges, search_limits, translation_step,
    center_x, center_y, each_image):
    
        x_range, y_range = search_ranges
        x_limit, y_limit = search_limits
        align_img.read_image(alignment_stack_name, each_image.local_id)
        shift_x, shift_y = each_image.shift_x / alignment_info.pixelsize, each_image.shift_y / alignment_info.pixelsize
        
        shift_x = self.limit_search_range_based_on_previous_alignment(shift_x, x_limit, x_range)
        shift_y = self.limit_search_range_based_on_previous_alignment(shift_y, y_limit, y_range)
            
        if refine_locally:
            sxb = 0.0
            syb = 0.0
        else:
            [angt, sxst, syst, mirror, xiref, peakt] = Util.multiref_polar_ali_2d_delta(align_img, ringref, x_range,
            y_range, translation_step, full_circle_mode, polar_interpolation_parameters, center_x + shift_x, 
            center_y + shift_y, each_image.inplane_angle, self.delta_psi)
            
            angb, sxb, syb, ct = compose_transform2(0.0, sxst, syst, 1, -angt, 0.0, 0.0, 1)
            
        local_prev_shift_x = shift_x - sxb
        local_prev_shift_y = shift_y - syb
        
        return local_prev_shift_x, local_prev_shift_y


    def perform_fine_alignment(self, ringref, polar_interpolation_parameters, alignment_info, full_circle_mode,
    align_img, search_ranges, search_limits, translation_step, center_x, center_y, dummy_transform, image_nt,
    determined_params, each_image, local_prev_shift_x, local_prev_shift_y):
        x_range, y_range = search_ranges
        x_limit, y_limit = search_limits
    
        zoom_factor = 5.0
        step_angle = 0.05
        fine_step_angle = np.sin(np.deg2rad(step_angle / zoom_factor))
        fine_x_range = x_range / zoom_factor
        fine_y_range = y_range / zoom_factor
        align_img.set_attr('xform.projection', dummy_transform)
        
        local_prev_shift_x = self.limit_search_range_based_on_previous_alignment(local_prev_shift_x, x_limit,
        fine_x_range)
            
        local_prev_shift_y = self.limit_search_range_based_on_previous_alignment(local_prev_shift_y, y_limit,
        fine_y_range)
            
        [angt, sxst, syst, mirror, xref, peakt] = Util.multiref_polar_ali_2d_local(align_img, ringref, fine_x_range,
        fine_y_range, translation_step / zoom_factor, fine_step_angle, full_circle_mode, polar_interpolation_parameters,
        center_x + local_prev_shift_x, center_y + local_prev_shift_y)
        
        matched_reference = int(xref)
        
        angb, sxb, syb, ct = compose_transform2(0.0, sxst, syst, 1, -angt, 0.0, 0.0, 1)
        refined_shift_x = local_prev_shift_x - sxb
        refined_shift_y = local_prev_shift_y - syb
        
        new_params = image_nt(each_image.stack_id, each_image.local_id, matched_reference, refined_shift_x *
        alignment_info.pixelsize, refined_shift_y * alignment_info.pixelsize, angt, peakt, mirror)
        
        determined_params.append(new_params)
        
        return angt, refined_shift_x, refined_shift_y, mirror, matched_reference, determined_params


    def determine_odd_and_even_average_including_variance(self, align_img, reference_stack, assigned_images, each_image,
    angt, refined_shift_x, refined_shift_y, mirror, matched_reference):
        alphan, sxn, syn = Segment().convert_shift_rotate_to_rotate_shift_order(angt, -refined_shift_x, -refined_shift_y)
        
        img_align_params_applied = rot_shift2D(align_img, alphan, sxn, syn, mirror)
        
        odd = each_image.stack_id % 2
        if odd:
            Util.add_img(reference_stack[matched_reference].odd_average, img_align_params_applied)
        elif not odd:
            Util.add_img(reference_stack[matched_reference].even_average, img_align_params_applied)
            
        Util.add_img2(reference_stack[matched_reference].variance, img_align_params_applied)
        assigned_images[matched_reference].append(each_image.stack_id)
        reference_stack[matched_reference].number_of_images[''] += 1

        return reference_stack
    

    def log_alignment_params(self, previous_params, determined_params):
        """
        >>> from spring.segment2d.segmentalign2d import SegmentAlign2d
        >>> s = SegmentAlign2d()
        >>> param_nt = s.get_image_list_named_tuple()
        >>> a = b = [param_nt(1, 1, 3, 0, 0, 0, 0, 1)]
        >>> SegmentAlign2d().log_alignment_params(a, b)
        u'  stack_id    local_id    ref_id    shift_x    shift_y    inplane_angle    peak    mirror  cycle\\n----------  ----------  --------  ---------  ---------  ---------------  ------  --------  ----------\\n         1           1         3          0          0                0       0         1  previous\\n         1           1         3          0          0                0       0         1  determined'
        """
        log_info = []
        for each_prev_param, each_det_param in zip(previous_params, determined_params):
            log_info += [list(each_prev_param) + ['previous']]
            log_info += [list(each_det_param) + ['determined']]
            
        msg = tabulate(log_info, list(each_prev_param._fields) + ['cycle'])
        self.log.tlog('The following alignment parameters were determined:\n{0}'.format(msg))
        
        return msg
            
        
    def align_images_to_references(self, alignment_stack_name, reference_stack, previous_params, ringref,
    polar_interpolation_parameters, ring_weights, alignment_info, refine_locally=True, full_circle_mode='F'):
        self.log.fcttolog()
        self.log.in_progress_log()
        
        align_img, search_ranges, search_limits, translation_step, center_x, center_y, dummy_transform, image_nt, determined_params,\
        assigned_images = self.define_parameters_for_alignment(alignment_stack_name, alignment_info, ringref)
        
        for each_image in previous_params:
            local_prev_shift_x, local_prev_shift_y = self.perform_coarse_restrained_alignment(alignment_stack_name,
            ringref, polar_interpolation_parameters, alignment_info, refine_locally, full_circle_mode, align_img,
            search_ranges, search_limits, translation_step, center_x, center_y, each_image)
            
            angt, refined_shift_x, refined_shift_y, mirror, matched_reference, determined_params = \
            self.perform_fine_alignment(ringref, polar_interpolation_parameters, alignment_info, full_circle_mode,
            align_img, search_ranges, search_limits, translation_step, center_x, center_y, dummy_transform, image_nt,
            determined_params, each_image, local_prev_shift_x, local_prev_shift_y)
            
            reference_stack = self.determine_odd_and_even_average_including_variance(align_img, reference_stack,
            assigned_images, each_image, angt, refined_shift_x, refined_shift_y, mirror, matched_reference)
        
        self.log_alignment_params(previous_params, determined_params)
        
        return assigned_images, determined_params, reference_stack
    

class SegmentAlign2dPostAlign(SegmentAlign2dAlign):
    def filter_references_if_requested(self, reference_stack, frc_line, each_ref_id):
        if self.low_pass_filter_option or self.high_pass_filter_option or self.custom_filter_option is True \
        or self.bfactor != 0:
            filter_coefficients = self.prepare_filter_function(self.high_pass_filter_option,
            self.high_pass_filter_cutoff, self.low_pass_filter_option, self.low_pass_filter_cutoff,
            self.pixelsize, self.image_dimension, 0.08, self.custom_filter_option, self.custom_filter_file,
            self.bfactor)
            
            filtered_average = filt_table(reference_stack[each_ref_id].total_average, filter_coefficients)
            reference_stack[each_ref_id] = reference_stack[each_ref_id]._replace(total_average=filtered_average)
            
        if self.frc_filter_option is True and frc_line is not None:
            updated_average = \
            self.low_pass_filter_reference_according_to_frc(reference_stack[each_ref_id].total_average, frc_line)
            
            reference_stack[each_ref_id] = reference_stack[each_ref_id]._replace(total_average=updated_average)
        
        return reference_stack
            

    def pass_alignment_parameters_from_reference_groups_to_images(self, reference_stack, alignment_info,
    assigned_images, mask, alignment_stack_name, reference_aligned):
        self.log.fcttolog()
        similarity_criterion = 0.0
    
        references_image_count = len(reference_stack)
        log_info = []
        for each_ref_id in list(range(references_image_count)):
            log_info += [[each_ref_id, reference_stack[each_ref_id].number_of_images['']]]
            
            if reference_stack[each_ref_id].number_of_images[''] <= 3: 
                reference_stack = self.put_random_image_in_reference_image_container(reference_stack, assigned_images,
                each_ref_id, alignment_stack_name)
                frc_line = None
            else:
                if self.update_references:
                    frc_line, reference_stack = self.calculate_averages(reference_stack, alignment_info.iteration_id,
                    each_ref_id)
        
            reference_stack[each_ref_id].total_average.set_attr('ave_n',
            reference_stack[each_ref_id].number_of_images[''])
            
            members = assigned_images[each_ref_id]
            reference_stack[each_ref_id].total_average.set_attr('members', members)
            
            if self.update_references:
                self.write_aligned_unfiltered_averages_and_variances(reference_stack, reference_aligned, each_ref_id)
            
                reference_stack = self.filter_references_if_requested(reference_stack, frc_line, each_ref_id)
                    
                new_reference_image = 'aqm{0:03}.hdf'.format(alignment_info.iteration_id)
                reference_stack[each_ref_id].total_average.write_image(new_reference_image, each_ref_id)
            
            similarity_criterion += reference_stack[each_ref_id].total_average.cmp(
                        'dot', reference_stack[each_ref_id].total_average, {'negative':0, 'mask':mask})
            
        msg = tabulate(log_info, ['reference_group', 'particle_count'])
        self.log.tlog('The following references have matched the number of the images:\n{0}'.format(msg))
        
        return similarity_criterion, reference_stack


    def generate_temp_bin_name(self, tempdir, stack_name, spec='ali'):
        temp_alignment_stack = os.path.join(tempdir,
        '{0}binned{1}{2}'.format(os.path.splitext(os.path.basename(stack_name))[0], spec, os.path.splitext(stack_name)[-1]))
        
        return temp_alignment_stack
    

    def write_out_aligned_averages_and_adapt_scales_from_previous_cycle(self, reference_stack_name, reference_stack,
    segsizepix, previous_binfactor, current_binfactor):
        
        scale_factor = previous_binfactor / float(current_binfactor)
        for each_ref_id, each_ref in enumerate(reference_stack):
            img = each_ref.total_average.copy()
            if scale_factor > 1:
                img = Util.pad(img, segsizepix, segsizepix, 1, 0, 0, 0)
            elif scale_factor < 1:
                img = Util.window(img, segsizepix, segsizepix, 1, 0, 0, 0)
            
            if scale_factor != 1:
                img.scale(scale_factor)
            img.write_image(reference_stack_name, each_ref_id)
        
        if scale_factor > 1:
            self.log.dlog('References were padded to {0} pixel dimensions'.format(segsizepix))
        elif scale_factor > 1:
            self.log.dlog('References were windowed to {0} pixel dimensions'.format(segsizepix))
        else:
            self.log.dlog('References are of {0} pixel dimensions'.format(segsizepix))
            
        return reference_stack_name
        
            
class SegmentAlign2d(SegmentAlign2dPostAlign):
    
    def define_previous_params_and_refine_locally(self, images_info, determined_params, previous_binfactor, align_id,
    each_info):
        if align_id == 0:
            previous_params = images_info
        else:
            previous_params = determined_params
            
        if previous_binfactor != each_info.binfactor:
            refine_locally = False
        else:
            refine_locally = True
            
        return previous_params, refine_locally
    

    def bin_references_and_images(self, alignment_stack_name, reference_stack_name, reference_stack, alignment_info,
    image_ids, align_id, previous_binfactor):
        segsizepix = self.image_dimension
        
        temp_alignment_stack = self.generate_temp_bin_name(self.tempdir, alignment_stack_name)
        
        if previous_binfactor != alignment_info.binfactor:
            temp_alignment_stack, segsizepix, helixwidthpix, pixelsize = \
            SegmentExam().apply_binfactor(alignment_info.binfactor, alignment_stack_name, segsizepix, self.helixwidthpix,
            self.pixelsize, image_ids, temp_alignment_stack)
        
        temp_reference_stack = self.generate_temp_bin_name(self.tempdir, reference_stack_name, 'ref')
        if align_id == 0 or not self.update_references:
            ref_img_list = list(range(EMUtil.get_image_count(reference_stack_name)))
            temp_reference_stack, segsizepix, helixwidthpix, pixelsize = \
            SegmentExam().apply_binfactor(alignment_info.binfactor, reference_stack_name, segsizepix, self.helixwidthpix,
            self.pixelsize, ref_img_list, temp_reference_stack)
        else:
            image = EMData()
            image.read_image(temp_alignment_stack)
            segsizepix = image.get_xsize()
            
            temp_reference_stack = \
            self.write_out_aligned_averages_and_adapt_scales_from_previous_cycle(temp_reference_stack, reference_stack,
            segsizepix, previous_binfactor, alignment_info.binfactor)
        
        reference_stack = self.prepare_reference_stack(temp_reference_stack)
        
        helixwidthpix = int(self.helixwidthpix / float(alignment_info.binfactor))
        helixheightpix = int(self.helixheightpix / float(alignment_info.binfactor))
        bin_mask = self.prepare_mask(helixwidthpix, helixheightpix, segsizepix)
        
        self.log.dlog('Internal mask prepared: segmentsize {0}: width x height {1} x {2} pixels. (Align_id {3})'.\
        format(segsizepix, helixwidthpix, helixheightpix, align_id))
        
        return temp_alignment_stack, reference_stack, bin_mask
    

    def write_aligned_unfiltered_averages_and_variances(self, reference_stack, reference_aligned, each_ref_id):
        new_variance_image_stack = '{0}_var{1}'.format(os.path.splitext(reference_aligned)[0],
        os.path.splitext(reference_aligned)[-1])
        
        reference_stack[each_ref_id].total_average.write_image(reference_aligned, each_ref_id)
        reference_stack[each_ref_id].variance.write_image(new_variance_image_stack, each_ref_id)


    def generate_aligned_output_file_and_update_header_of_input(self, each_image, determined_params):
        img = EMData()
        for each_image in determined_params:
            img.read_image(self.infile, each_image.stack_id)
            refined_shift_x = each_image.shift_x / self.pixelsize
            refined_shift_y = each_image.shift_y / self.pixelsize
            
            alphan, sxn, syn = Segment().convert_shift_rotate_to_rotate_shift_order(each_image.inplane_angle, 
            -refined_shift_x, -refined_shift_y)
            
            align_img = rot_shift2D(img, alphan, sxn, syn, each_image.mirror)
            align_img.del_attr('xform.align2d')
            align_img.set_attr('active', 1)
            align_img.write_image(self.outfile, each_image.stack_id)

            trans_2d = Transform({'type':'2d', 'alpha':alphan, 'tx':sxn, 'ty':syn, 'mirror':int(each_image.mirror)})
            img.set_attr('xform.align2d', trans_2d)
            img.set_attr('assign', each_image.ref_id)
            img.write_image(self.infile, each_image.stack_id)
            

    def cleanup_segmentalign2d(self):
        os.remove(self.generate_temp_bin_name(self.tempdir, self.alignment_stack_name))
        os.remove(self.generate_temp_bin_name(self.tempdir, self.reference_stack_name, 'ref'))
        os.rmdir(self.tempdir)


    def perform_iterative_alignment(self, alignment_info, images_info):
        image_ids = [each_image.stack_id for each_image in images_info]
        
        determined_params = None
        previous_binfactor = 0
        reference_stack = None
        
        for align_id, each_info in enumerate(alignment_info):
            
            previous_params, refine_locally = self.define_previous_params_and_refine_locally(images_info,
            determined_params, previous_binfactor, align_id, each_info)
                
            alignment_stack_name, reference_stack, bin_mask = \
            self.bin_references_and_images(self.alignment_stack_name, self.reference_stack_name, reference_stack,
            each_info, image_ids, align_id, previous_binfactor)
            
            ringref, polar_interpolation_parameters, ring_weights, reference_stack = \
            self.prepare_reference_images_for_alignment(bin_mask, reference_stack)
            
            self.log.plog(80 * (align_id + 0.5) / len(alignment_info) + 10)
            
            assigned_images, determined_params, reference_stack = \
            self.align_images_to_references(alignment_stack_name, reference_stack, previous_params, ringref,
            polar_interpolation_parameters, ring_weights, each_info, refine_locally)
            
            similarity_criterion, reference_stack = \
            self.pass_alignment_parameters_from_reference_groups_to_images(reference_stack, each_info, assigned_images,
            bin_mask, alignment_stack_name, self.aligned_averages)
            
            msg = 'ITERATION #{0}        criterion = {1}'.format(each_info.iteration_id, similarity_criterion)
            self.log.tlog(msg)
 
            self.log.plog(80 * (align_id + 1) / len(alignment_info) + 10)
            previous_binfactor = each_info.binfactor
            
        self.generate_aligned_output_file_and_update_header_of_input(each_image, determined_params)
            
        self.log.ilog('Alignment parameters were applied to new output file {0}.'.format(self.outfile))
        
        self.cleanup_segmentalign2d()
        if not self.reference_option:
            os.remove(self.reference_stack_name)
        self.log.endlog(self.feature_set)
        
        
    def perform_segmentalign2d(self):
        alignment_info, images_info = self.prepare_alignment()
        self.perform_iterative_alignment(alignment_info, images_info)
        
        
def main():
    # Option handling
    parset = SegmentAlign2dPar()
    mergeparset = OptHandler(parset)

    ######## Program
    stack = SegmentAlign2d(mergeparset)
    stack.perform_segmentalign2d()


if __name__ == '__main__':
    main()
