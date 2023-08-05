# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import EMData, Util, Transform
from collections import namedtuple
from spring.csinfrastr.csdatabase import SpringDataBase, base, SegmentTable, RefinementCycleSegmentTable
from spring.segment2d.segment import Segment
from spring.segment2d.segmentalign2d import SegmentAlign2d
from spring.segment2d.segmentselect import SegmentSelect
from spring.segment3d.refine.sr3d_project import SegmentRefine3dProjectionLayerLineFilter
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from sqlalchemy.sql.expression import asc
from tabulate import tabulate
from utilities import compose_transform2
import numpy as np
import os
import sys


class SegmentRefine3dAlignMatch(SegmentRefine3dProjectionLayerLineFilter):
    def prepare_segment_for_alignment(self, masked_segment_stack, previous_params, segment_size, each_info,
    limit_search_ranges=True):
        segment = EMData()
        segment.read_image(masked_segment_stack, previous_params.local_id)

        if limit_search_ranges:
            x_distance, y_distance = SegClassReconstruct().compute_distances_to_helical_axis(previous_params.shift_x,
            previous_params.shift_y, previous_params.inplane_angle)
                 
            x_range = float(min(max(0, self.x_limit_A / each_info.pixelsize - abs(x_distance)), each_info.x_range))
            y_range = float(min(max(0, self.y_limit_A / each_info.pixelsize - abs(y_distance)), each_info.y_range))
        else:
            x_range = each_info.x_range
            y_range = each_info.y_range

        segment = Segment().shift_and_rotate_image(segment, previous_params.inplane_angle, previous_params.shift_x,
        previous_params.shift_y)
        
        center_x = center_y = segment_size / 2 + 1
        
        return segment, center_x, center_y, x_range, y_range
    

    def convert_Euler_angles_to_mirrored_sparx(self, phi, theta, psi):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> phi, theta, psi = s.convert_Euler_angles_from_mirrored_sparx(90, 90, 270)
        >>> s.convert_Euler_angles_to_mirrored_sparx(phi, theta, psi)
        (90.0, 90.0, 270.0)
        """
        mirrored_phi = (phi - 540.0) % 360
        mirrored_theta = (180.0 - theta) % 360
        mirrored_psi = (540.0 - psi) % 360
        
        return mirrored_phi, mirrored_theta, mirrored_psi
    

    def convert_Euler_angles_from_mirrored_sparx(self, phi, theta, psi):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.convert_Euler_angles_from_mirrored_sparx(90, 90, 270)
        (270.0, 90.0, 270.0)
        >>> s.convert_Euler_angles_from_mirrored_sparx(np.linspace(0, 360, 2), np.linspace(82, 98, 2), 270 * np.ones(2))
        (array([ 180.,  180.]), array([ 98.,  82.]), array([ 270.,  270.]))
        """
        mirrored_phi = (phi + 540.0) % 360
        mirrored_theta = (180.0 - theta) % 360
        mirrored_psi = (540.0 - psi) % 360
        
        return mirrored_phi, mirrored_theta, mirrored_psi
    

    def combine_determined_parameters_to_final_five(self, previous_params, reference_rings, projection_parameters, ang,
    sxs, s_ys, mirror, matched_reference_id, peak):
        """
        Function to convert (in-plane rotation and shifts) to (shifts and rotation)
        if mirror parameters have been found, adjust Euler angles    
        """
        peak = abs(peak)
        matched_reference_id = int(matched_reference_id)
        model = projection_parameters[matched_reference_id].model_id
        if matched_reference_id > -1:
            angb, sxb, syb, ct = compose_transform2(0.0, sxs, s_ys, 1, -ang, 0.0, 0.0, 1)
            inplane_angle = (ang) % 360
            if mirror:
                phi, theta, psi = \
                self.convert_Euler_angles_from_mirrored_sparx(projection_parameters[matched_reference_id].phi,
                projection_parameters[matched_reference_id].theta, projection_parameters[matched_reference_id].psi +
                angb)
            else:
                phi = projection_parameters[matched_reference_id].phi
                theta = projection_parameters[matched_reference_id].theta
                psi = (projection_parameters[matched_reference_id].psi + angb) % 360
            s2x = (sxb + previous_params.shift_x)
            s2y = (syb + previous_params.shift_y)
        else:
            phi = theta = psi = s2x = s2y = t1 = 0.0
            peak = -1.0e23

        return model, phi, theta, psi, s2x, s2y, inplane_angle, peak


    def find_inplane_to_match(self, phiA,thetaA,phiB,thetaB,psiA=0,psiB=0):
        """Find the z rotation such that
            ZA  RA is as close as possible to RB
                this maximizes trace of ( RB^T ZA RA) = trace(ZA RA RB^T)
        """
    
        RA   = Transform({'type': 'spider', 'phi': phiA, 'theta': thetaA, 'psi': psiA})
        RB   = Transform({'type': 'spider', 'phi': phiB, 'theta': thetaB, 'psi': psiB})
        RBT  = RB.transpose()
        RABT = RA * RBT
    
        RABTeuler = RABT.get_rotation('spider')
        RABTphi   = RABTeuler['phi']
        RABTtheta = RABTeuler['theta']
        RABTpsi   = RABTeuler['psi']
    
        return (-RABTpsi-RABTphi),RABTtheta
    

    def filter_angle_ids_according_to_search_restraint(self, phis, phi_ids, each_phi, phi_restraint,
    max_angle=360.0):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.filter_angle_ids_according_to_search_restraint(np.arange(0, \
360.0, 10), np.arange(36), 55.0, 80.0)
        array([  0.,   1.,   2.,   3.,   4.,   5.,   6.,   7.,   8.,   9.,  10.,
                11.,  12.,  13.,  34.,  35.])
                
        >>> s.filter_angle_ids_according_to_search_restraint(np.arange(0, \
360.0, 10), np.arange(36), 335.0, 80.0)
        array([  0.,   1.,   2.,   3.,   4.,   5.,  26.,  27.,  28.,  29.,  30.,
                31.,  32.,  33.,  34.,  35.])
                
        >>> s.filter_angle_ids_according_to_search_restraint(np.arange(0, \
360.0, 10), np.arange(36), 135.0, 80.0)
        array([  6.,   7.,   8.,   9.,  10.,  11.,  12.,  13.,  14.,  15.,  16.,
                17.,  18.,  19.,  20.,  21.])
                
        >>> s.filter_angle_ids_according_to_search_restraint(np.arange(82, \
99), np.arange(34), 82.0, 3.0)
        array([ 0.,  1.,  2.])
        """
        lower_bound = (each_phi - phi_restraint) 
        higher_bound = (each_phi + phi_restraint) 
        filtered_ids = phi_ids[(lower_bound < phis) & (phis < higher_bound)]
        
        add_low_filtered = np.array([])
        add_high_filtered = np.array([])
            
        if lower_bound != (lower_bound) % max_angle:
            add_low_filtered = phi_ids[((lower_bound) % max_angle < phis)] 
        if higher_bound != (higher_bound) % max_angle:
            add_high_filtered = phi_ids[((higher_bound) % max_angle > phis)] 
        
        filtered_ids = np.append(filtered_ids, add_low_filtered)
        filtered_ids = np.append(filtered_ids, add_high_filtered)
        filtered_ids = np.sort(np.unique(filtered_ids))
        
        return filtered_ids
        

    def compute_distance(self, this_phi, this_theta, phis, thetas):
        distances = np.sqrt((phis - this_phi) ** 2 + (thetas - this_theta) ** 2)
        
        return distances 
        

    def get_closest_projection_from_projection_list(self, this_phi, this_theta, phis, thetas, ids):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> phis = np.arange(10, 90, 10)
        >>> thetas = np.array(8 * [90.0])
        >>> ids = np.arange(len(phis))
        >>> s.get_closest_projection_from_projection_list(350, 90, phis, thetas, ids)
        (0, 10, 90.0)
        
        >>> phis = np.array(8 * np.arange(10, 90, 10).tolist())
        >>> thetas = np.array([each_theta for each_theta in np.arange(82, 98, 2) for each_time in range(8)])
        >>> ids = np.arange(len(phis))
        >>> s.get_closest_projection_from_projection_list(350, 98, phis, thetas, ids)
        (56, 10, 96)
        """
        distances = self.compute_distance(this_phi, this_theta, phis, thetas)
        distances = np.append(distances, self.compute_distance(this_phi + 360.0, this_theta, phis, thetas))
        distances = np.append(distances, self.compute_distance(this_phi - 360.0, this_theta, phis, thetas))
        
        ids = np.append(ids, np.append(ids, ids))
        closest_index = np.argmin(distances)
        closest_id = ids[closest_index]
        closest_phi = phis[closest_id]
        closest_theta = thetas[closest_id]
        
        return closest_id, closest_phi, closest_theta
    
        
    def select_reference_rings_according_to_angular_restraints(self, reference_rings, each_info, projection_parameters,
    each_proj_parameter):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> ref_rings = ['first_ring', 'second_ring']
        >>> restraint_tuple = s.get_restraint_tuple()
        >>> info = restraint_tuple(20, 20, 5, 5, 5)
        >>> proj_tuple = s.get_prj_params_named_tuple()
        >>> proj_params = [proj_tuple(0, 0, 0, 90, 270, 0, 0), proj_tuple(1, 0, 350, 90, 270, 0, 0)]
        >>> last_param = proj_tuple(0, 0, 0, 90, 270, 0, 0)
        >>> s.select_reference_rings_according_to_angular_restraints(ref_rings, info, proj_params, last_param) #doctest: +NORMALIZE_WHITESPACE
        (['first_ring', 'second_ring'], 
        [prj_parameters(id=0, model_id=0, phi=0, theta=90, psi=270, shift_x=0, shift_y=0), 
        prj_parameters(id=1, model_id=0, phi=350, theta=90, psi=270, shift_x=0, shift_y=0)], 
        ('340.00 - 20.00', '90.00 - 90.00'))
        
        >>> proj_params = [proj_tuple(0, 0, 0, 60, 270, 0, 0), proj_tuple(1, 0, 0, 90, 270, 0, 0)]
        >>> s.select_reference_rings_according_to_angular_restraints(ref_rings, info, proj_params, last_param) #doctest: +NORMALIZE_WHITESPACE
        (['second_ring'], 
        [prj_parameters(id=1, model_id=0, phi=0, theta=90, psi=270, shift_x=0, shift_y=0)], 
        ('340.00 - 20.00', '70.00 - 110.00'))
        
        >>> proj_params = [proj_tuple(0, 0, 0, 60, 270, 0, 0), proj_tuple(1, 0, 330, 90, 270, 0, 0)]
        >>> s.select_reference_rings_according_to_angular_restraints(ref_rings, info, proj_params, last_param) #doctest: +NORMALIZE_WHITESPACE
        (['first_ring'], 
        [prj_parameters(id=0, model_id=0, phi=0, theta=60, psi=270, shift_x=0, shift_y=0)], 
        ('340.00 - 20.00', '70.00 - 110.00'))
        
        >>> proj_params = [proj_tuple(0, 1, 0, 90, 270, 0, 0), proj_tuple(1, 0, 350, 90, 270, 0, 0)]
        >>> s.select_reference_rings_according_to_angular_restraints(ref_rings, info, proj_params, last_param) #doctest: +NORMALIZE_WHITESPACE
        (['second_ring'], 
        [prj_parameters(id=1, model_id=0, phi=350, theta=90, psi=270, shift_x=0, shift_y=0)], 
        ('340.00 - 20.00', '90.00 - 90.00'))
        """
        
        if each_info.azimuthal_restraint == 180.0 and each_info.out_of_plane_restraint == 180.0:
            selected_reference_rings = reference_rings
            selected_projection_parameters = projection_parameters
            selected_log_info = (None, None)
        else:
            phis = np.array([each_prj.phi for each_prj in projection_parameters])# if each_proj_parameter.model_id == each_prj.model_id])
            thetas = np.array([each_prj.theta for each_prj in projection_parameters])# if each_proj_parameter.model_id == each_prj.model_id])
            psis = np.array([each_prj.psi for each_prj in projection_parameters])# if each_proj_parameter.model_id == each_prj.model_id])
            model_ids = np.array([each_prj.model_id for each_prj in projection_parameters])# if each_proj_parameter.model_id == each_prj.model_id])
            
            mirr_phis, mirr_thetas, mirr_psis = self.convert_Euler_angles_to_mirrored_sparx(phis, thetas, psis)
            prj_ids = np.append(np.arange(len(phis)), np.arange(len(mirr_phis)))
            phis = np.append(phis, mirr_phis)
            thetas = np.append(thetas, mirr_thetas)
            model_ids = np.append(model_ids, model_ids)
            
            filtered_phi_ids = self.filter_angle_ids_according_to_search_restraint(phis, prj_ids, 
            each_proj_parameter.phi, each_info.azimuthal_restraint)
            
            filtered_theta_ids = self.filter_angle_ids_according_to_search_restraint(thetas, prj_ids,
            each_proj_parameter.theta, each_info.out_of_plane_restraint)
            
            filtered_model_ids = prj_ids[model_ids == each_proj_parameter.model_id]
            
            filtered_prj_ids = np.intersect1d(filtered_phi_ids, np.intersect1d(filtered_theta_ids, filtered_model_ids))
            
            if reference_rings is not None:
                selected_reference_rings = [reference_rings[int(each_selected_prj)] for each_selected_prj in
                filtered_prj_ids]
            else:
                selected_reference_rings = None
            
            selected_projection_parameters = [projection_parameters[int(each_selected_prj)] for each_selected_prj in
            filtered_prj_ids]
        
            if selected_projection_parameters == []:
                filtered_phis = phis[model_ids == each_proj_parameter.model_id]
                filtered_thetas = thetas[model_ids == each_proj_parameter.model_id]
                closest_id, closest_phi, closest_theta = \
                self.get_closest_projection_from_projection_list(each_proj_parameter.phi, each_proj_parameter.theta,
                filtered_phis, filtered_thetas, filtered_model_ids)
                
                selected_projection_parameters = [projection_parameters[closest_id]]
                if reference_rings is not None:
                    selected_reference_rings = [reference_rings[closest_id]]
                
            selected_phi_str = '{0:.2f} - {1:.2f}'.format((each_proj_parameter.phi - each_info.azimuthal_restraint) % 360,
                                                   (each_proj_parameter.phi + each_info.azimuthal_restraint) % 360)
            
            selected_theta_str = '{0:.2f} - {1:.2f}'.\
            format(max(np.min(thetas), (each_proj_parameter.theta - each_info.out_of_plane_restraint) % 360),
            (min(np.max(thetas), (each_proj_parameter.theta + each_info.out_of_plane_restraint) % 360)))
            
            selected_log_info = (selected_phi_str, selected_theta_str)
            
        return selected_reference_rings, selected_projection_parameters, selected_log_info
        
        
    def match_each_image_against_all_projections_with_delta_in_plane_restraint(self, masked_segment_stack,
    previous_params, reference_rings, projection_parameters, each_info, step_x, delta_psi,
    polar_interpolation_parameters, segment_size, full_circle_mode='F'):
        
        segment, center_x, center_y, x_range, y_range = self.prepare_segment_for_alignment(masked_segment_stack,
        previous_params, segment_size, each_info)
        
        [ang, sxs, s_ys, mirror, matched_reference_id, peak] = Util.multiref_polar_ali_2d_delta(segment,
        reference_rings, x_range, y_range, step_x, full_circle_mode, polar_interpolation_parameters, 
        center_x, center_y, 0.0, delta_psi)
        
        model, phi, theta, psi, s2x, s2y, inplane_angle, peak = \
        self.combine_determined_parameters_to_final_five(previous_params, reference_rings, projection_parameters, 
        ang + previous_params.inplane_angle, sxs, s_ys, mirror, matched_reference_id, peak)
        
        return [model, phi, theta, psi, s2x, s2y, inplane_angle, peak, mirror]
    

    def refine_each_image_against_projections_including_delta_inplane_restraint(self, masked_segment_stack,
    previous_params, reference_rings, projection_parameters, each_info, step_x, step_angle, delta_psi,
    polar_interpolation_parameters, segment_size, full_circle_mode='F'):
        
        segment, center_x, center_y, x_range, y_range = self.prepare_segment_for_alignment(masked_segment_stack,
        previous_params, segment_size, each_info)
    
        transform_projection = Transform({'type':'spider','phi':previous_params.phi,'theta':previous_params.theta,'psi':
        (270.0)%360})
        
        segment.set_attr('xform.projection', transform_projection)
        
        [ang, sxs, s_ys, mirror, matched_reference_id, peak] = Util.multiref_polar_ali_2d_local(segment,
        reference_rings, x_range, y_range, float(step_x), step_angle, full_circle_mode,
        polar_interpolation_parameters, center_x, center_y)
        
        model, phi, theta, psi, s2x, s2y, inplane_angle, peak = \
        self.combine_determined_parameters_to_final_five(previous_params, reference_rings, projection_parameters, 
        ang + previous_params.inplane_angle, sxs, s_ys, mirror, matched_reference_id, peak)
        
        return [model, phi, theta, psi, s2x, s2y, inplane_angle, peak, mirror]
    
    
class SegmentRefine3dAlign(SegmentRefine3dAlignMatch):
    def set_euler_angles_to_reference_rings(self, reference_rings, reference_angles):

        for each_ref_id, each_ref_angle in enumerate(reference_angles):
            n1 = np.sin(np.deg2rad(each_ref_angle.theta)) * np.cos(np.deg2rad(each_ref_angle.phi))
            n2 = np.sin(np.deg2rad(each_ref_angle.theta)) * np.sin(np.deg2rad(each_ref_angle.phi))
            n3 = np.cos(np.deg2rad(each_ref_angle.theta))
            reference_rings[each_ref_id].set_attr_dict({'n1':n1, 'n2':n2, 'n3':n3})
            reference_rings[each_ref_id].set_attr('phi', each_ref_angle.phi)
            reference_rings[each_ref_id].set_attr('theta', each_ref_angle.theta)
            reference_rings[each_ref_id].set_attr('psi', each_ref_angle.psi)

        return reference_rings
    
    
    def prepare_reference_rings_from_projections(self, projection_stack, projection_parameters, alignment_size,
    max_range):
        first_ring = 1
        last_ring = max(int(alignment_size * 0.75 / 2), alignment_size / 2 - int(np.sqrt(2) * max_range))
        ring_step = 1
        
        polar_interpolation_parameters, ring_weights = SegmentAlign2d().prepare_empty_rings(first_ring, last_ring,
        ring_step)
        
        prj = EMData()
        reference_rings = []
        for each_prj in projection_parameters:
            prj.read_image(projection_stack, each_prj.id)
            
            cimage = SegmentAlign2d().generate_reference_rings_from_image(prj, polar_interpolation_parameters,
            ring_weights, alignment_size)
            
            reference_rings.append(cimage)

        reference_rings = self.set_euler_angles_to_reference_rings(reference_rings, projection_parameters)

        return reference_rings, polar_interpolation_parameters
    
    
    def make_named_tuple_of_orientation_parameters(self):
        orientation_parameters = namedtuple('orientation', 'stack_id local_id model_id phi theta psi shift_x ' + \
        'shift_y inplane_angle peak mirror rank_id')
        
        return orientation_parameters
    

    def get_masking_parameters(self, masking_parameters, mask_params, each_segment, pixelsize):
        if each_segment.lavg_inplane_angle is not None:
            inplane_angle = each_segment.lavg_inplane_angle
            shift_x_A = each_segment.lavg_helix_shift_x_A
        else:
            inplane_angle = each_segment.inplane_angle
            shift_x_A = each_segment.shift_x_A

        mask_params.append(masking_parameters(each_segment.stack_id, each_segment.stack_id, inplane_angle, shift_x_A /
        pixelsize, abs(each_segment.theta - 90.0)))
        
        return mask_params
    

    def make_named_tuple_of_masking_parameters(self):
        masking_parameters = namedtuple('mask', 'stack_id local_id lavg_inplane_angle lavg_helix_shift_x ' +
        'out_of_plane_tilt')
        
        return masking_parameters
    

    def compute_optimum_phi_and_index_closest_to_one_of_prj_phis(self, multiples, phis, prj_phis):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> mult = np.array([0, 1, 2]) 
        >>> phis = np.array([325, 97, 355])
        >>> prj_phis = np.array([0, 90, 180, 270])
        >>> s.compute_optimum_phi_and_index_closest_to_one_of_prj_phis(mult, phis, prj_phis)
        (355, 2)
        """
        ang_distances = [np.min(np.abs(phis - each_prj_phi)) for each_prj_phi in prj_phis]
        ang_distances += [np.min(np.abs(phis - each_prj_phi + 360)) for each_prj_phi in prj_phis]
        ang_distances += [np.min(np.abs(phis - each_prj_phi - 360)) for each_prj_phi in prj_phis]
        
#        min_ang_dist = np.min(ang_distances)
        
        closest_prj_indices = [np.argmin(np.abs(phis - each_prj_phi)) for each_prj_phi in prj_phis]
        closest_prj_indices += [np.argmin(np.abs(phis - each_prj_phi + 360)) for each_prj_phi in prj_phis]
        closest_prj_indices += [np.argmin(np.abs(phis - each_prj_phi - 360)) for each_prj_phi in prj_phis]
        closest_index = closest_prj_indices[np.argmin(ang_distances)]
        closest_phi = phis[closest_index]
        closest_multiple = multiples[closest_index]
        
        return closest_phi, closest_multiple
    
        
    def reduce_y_shifts_and_phis_to_half_stepsize(self, orientation_result, helix_y_shifts, helical_symmetry,
    projection_parameters, stepsize):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> n_phi = namedtuple('orient', 'phi')
        >>> o_rslt = [n_phi(5), n_phi(87), n_phi(330), n_phi(350)]
        >>> y_shifts = np.array([1, 2, 4, 5])
        >>> prj_params = [[0], [90], [180], [270]]
        >>> s = SegmentRefine3d()
        >>> s.reduce_y_shifts_and_phis_to_half_stepsize(o_rslt, y_shifts, (1, 10), prj_params, 10) 
        (array([ 1.,  2., -2., -3.]), array([   5.,   87.,  270.,  270.]))
        >>> s.reduce_y_shifts_and_phis_to_half_stepsize(o_rslt, y_shifts, (0, 10), prj_params, 10) 
        (array([ 1.,  2.,  4.,  5.]), array([   5.,   87.,  330.,  350.]))
        """
        helical_rise, helical_rotation = helical_symmetry
        phis = np.array([each_result.phi for each_result in orientation_result])
        if helical_rise != 0:
            multiples = np.round(helix_y_shifts / helical_rise)
        else:
            multiples = np.zeros(len(helix_y_shifts))
        close_to_0_ys = helix_y_shifts - helical_rise * multiples
        close_to_0_phis = (phis - multiples * helical_rotation) %360
        prj_phis = np.unique([each_prj[0] for each_prj in projection_parameters])
        
        if helical_rise != 0:
            stepsize_multiple = np.round(stepsize / helical_rise)
            multiples_to_test = np.arange(stepsize_multiple) - stepsize_multiple / 2
        
            optimum_multiples = np.array([])
            for each_stack_id, each_multiple in enumerate(multiples):
                each_phi = close_to_0_phis[each_stack_id]
                phis_to_test = (each_phi + multiples_to_test * helical_rotation) %360
                
                optimum_phi, optimum_multiple = \
                self.compute_optimum_phi_and_index_closest_to_one_of_prj_phis(multiples_to_test, phis_to_test, prj_phis)
                
                optimum_multiples = np.append(optimum_multiples, optimum_multiple)
        else:
            optimum_multiples = 0
                
        reduced_y_shifts = close_to_0_ys + helical_rise * optimum_multiples
        reduced_phis = (close_to_0_phis + optimum_multiples * helical_rotation) %360

        return reduced_y_shifts, reduced_phis
    

    def enter_orientation_parameters(self, orientation_parameters, phi, psi, x_shift, y_shift, each_segment,
    inplane_angle, pixelsize, model_id=None):
        if model_id is None:
            model_id = each_segment.model_id
        fitted_param = orientation_parameters(each_segment.stack_id, each_segment.stack_id, model_id, phi,
        each_segment.theta, psi, x_shift / pixelsize, y_shift / pixelsize, inplane_angle, each_segment.peak,
        each_segment.mirror, None)
        
        return fitted_param
    

    def setup_parameter_containers(self):
        previous_params = []
        mask_params = []
        orientation_parameters = self.make_named_tuple_of_orientation_parameters()
        masking_parameters = self.make_named_tuple_of_masking_parameters()

        return orientation_parameters, previous_params, mask_params, masking_parameters


    def get_helically_related_parameters_for_first_refinement_cycle(self, temp_db, each_info,
    included_nonorientation_segments):
        orientation_parameters, previous_params, mask_params, masking_parameters = self.setup_parameter_containers()
        
        session = SpringDataBase().setup_sqlite_db(base, temp_db)
        orientation_results = session.query(SegmentTable).order_by(asc(SegmentTable.id)).all()
        session.close()
        os.remove(temp_db)

        segment_count = len(orientation_results)
#         helix_x_shifts = np.zeros(segment_count)
        helix_x_shifts = 2.0 * np.random.randn(segment_count)
        inplane_angles = np.array([each_segment.inplane_angle for each_segment in orientation_results])
        thetas = np.int64(90 + 4 * np.random.randn(segment_count))

        if len(self.helical_symmetries) > 1:
            azimuthal_increment = 360.0 / self.azimuthal_angle_count
            linear_phis = (np.arange(0, segment_count * azimuthal_increment, azimuthal_increment)) % 360
            phis = linear_phis[np.random.randint(0, segment_count, segment_count)]
            helix_y_shifts = 10.0 * np.random.randn(segment_count)
            model_ids = np.random.randint(0, len(self.helical_symmetries), segment_count)
        else:
            rise, rotation = self.helical_symmetries[0]
            distances_along_helix = self.stepsize * np.arange(segment_count)
            multiples_of_rise = np.int64(distances_along_helix / rise)
            phis = (multiples_of_rise * rotation) % 360
            helix_y_shifts = distances_along_helix - multiples_of_rise * rise
            model_ids = np.zeros(segment_count)

        sx, sy = SegClassReconstruct().compute_sx_sy_from_shifts_normal_and_parallel_to_helix_axis_with_inplane_angle(
        helix_x_shifts / each_info.pixelsize, helix_y_shifts / each_info.pixelsize, inplane_angles)

        for local_id, each_result in enumerate(orientation_results):
            if not self.unbending:
                psi = (-(each_result.inplane_angle + 270)) % 360
            elif self.unbending:
                psi = 270.0

            if each_result.stack_id in included_nonorientation_segments:
                ten_params = orientation_parameters(each_result.stack_id, local_id, int(model_ids[local_id]),
                phis[local_id], thetas[local_id], psi, sx[local_id], sy[local_id], each_result.inplane_angle, 0, 0, None)

                previous_params.append(ten_params)
                mask_params.append(masking_parameters(each_result.stack_id, local_id, each_result.inplane_angle, 0, 0))
        
        return previous_params, mask_params


    def get_zero_parameters_for_initial_stages_of_refinement(self, temp_db, included_nonorientation_segments):
        orientation_parameters, previous_params, mask_params, masking_parameters = self.setup_parameter_containers()
        
        session = SpringDataBase().setup_sqlite_db(base, temp_db)
        orientation_results = session.query(SegmentTable).order_by(asc(SegmentTable.id)).all()
        session.close()
        os.remove(temp_db)

        for local_id, each_result in enumerate(orientation_results):
            if not self.unbending:
                psi = (-(each_result.inplane_angle + 270)) % 360
            elif self.unbending:
                psi = 270.0

            if each_result.stack_id in included_nonorientation_segments:
                ten_params = orientation_parameters(each_result.stack_id, local_id, None, 0, 90, psi, 0, 0, 
                    each_result.inplane_angle, 0, 0, None)
                previous_params.append(ten_params)
                mask_params.append(masking_parameters(each_result.stack_id, local_id, each_result.inplane_angle, 0, 0))
        
        return previous_params, mask_params


    def get_refined_parameters_for_advanced_stages_of_refinement(self, each_info, reference_files,
    included_nonorientation_segments, temp_ref_db, last_cycle, ref_session):
        orientation_parameters, previous_params, mask_params, masking_parameters = self.setup_parameter_containers()

        if len(reference_files) > 1:
            model_id = None
        else:
            model_id = 0

        orientation_results = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
        order_by(asc(RefinementCycleSegmentTable.stack_id)).all()

        ref_session.close()
        os.remove(temp_ref_db)

        for each_segment in orientation_results:
            if each_segment.stack_id in included_nonorientation_segments:
                if self.unbending:
                    ten_params = self.enter_orientation_parameters(orientation_parameters, 
                        each_segment.phi, 270.0, each_segment.unbent_shift_x_A, each_segment.unbent_shift_y_A, 
                        each_segment, each_segment.unbent_ip_angle, each_info.pixelsize, model_id)
                else:
                    ten_params = self.enter_orientation_parameters(orientation_parameters, 
                        each_segment.phi, each_segment.psi, each_segment.shift_x_A, each_segment.shift_y_A, 
                        each_segment, each_segment.inplane_angle, each_info.pixelsize, model_id)
                previous_params.append(ten_params)

                mask_params = self.get_masking_parameters(masking_parameters, mask_params, each_segment, 
                each_info.pixelsize)
        
        return previous_params, mask_params


    def prepare_previous_parameters_either_from_inplane_angle_or_from_previous_cycle(self, each_info, info_series,
    ref_cycle_id, each_iteration_number, reference_files):
        temp_db = self.copy_spring_db_to_tempdir()

        included_nonorientation_segments, excluded_non_orientation_counts = \
        SegmentSelect().filter_non_orientation_parameters_based_on_selection_criteria(self, temp_db,
        keep_helices_together=True)
        
        prev_ref_cycle_id = ref_cycle_id - 1
        refine_db = 'refinement{0:03}.db'.format(prev_ref_cycle_id)
        if self.resume_refinement_option and not os.path.exists(refine_db):
            refine_db = 'refinement{0:03}.db'.format(prev_ref_cycle_id)
            assert os.path.exists(refine_db)
        
        if os.path.exists(refine_db):
            temp_ref_db = self.copy_ref_db_to_tempdir(prev_ref_cycle_id)
            last_cycle, ref_session = self.get_last_cycle_from_refinement_database(temp_ref_db)
        else:
            last_cycle = None
            
#         if ref_cycle_id == 1 and not self.unbending and not self.reference_option:
#             previous_params, mask_params = self.get_helically_related_parameters_for_first_refinement_cycle(temp_db,
#             each_info, included_nonorientation_segments)
        if each_info.bin_factor == info_series[0].bin_factor and not self.resume_refinement_option:
            previous_params, mask_params = self.get_zero_parameters_for_initial_stages_of_refinement(temp_db,
            included_nonorientation_segments)
        elif last_cycle is not None:
            previous_params, mask_params = self.get_refined_parameters_for_advanced_stages_of_refinement(each_info,
            reference_files, included_nonorientation_segments, temp_ref_db,
            last_cycle, ref_session)
                
        temp_prev_ref_db = os.path.join(self.tempdir, 'refinement{0:03}.db'.format(prev_ref_cycle_id))
        if os.path.exists(temp_prev_ref_db):
            os.remove(temp_prev_ref_db)
            
        return previous_params, mask_params
    
    
    def find_maximum_cross_correlation_for_local_in_plane_angle(self, masked_segment_stack, step_x, each_info,
    reference_rings, projection_parameters, polar_interpolation_parameters, previous_params, alignment_size):
        coarse_determined_params = []
        orientation_parameters = self.make_named_tuple_of_orientation_parameters()
        coarse_align_loginfo = []
        for each_first_params in previous_params:
            
            selected_ref_rings, selected_prj_params, selected_log_info = \
            self.select_reference_rings_according_to_angular_restraints(reference_rings, each_info,
            projection_parameters, each_first_params)
            
            segment_params = \
            self.match_each_image_against_all_projections_with_delta_in_plane_restraint(masked_segment_stack,
            each_first_params, selected_ref_rings, selected_prj_params, each_info, step_x, self.delta_in_plane_rotation,
            polar_interpolation_parameters, alignment_size)
            
            segment_params.insert(0, each_first_params.stack_id)
            segment_params.insert(1, each_first_params.local_id)
            segment_params.append(each_first_params.rank_id)
            ref_orientation_param = orientation_parameters._make(segment_params)
            coarse_determined_params.append(ref_orientation_param)
            
            coarse_align_loginfo += [[each_first_params.stack_id, each_first_params.local_id, each_first_params.model_id,
            each_first_params.phi, each_first_params.theta, each_first_params.psi, each_first_params.shift_x,
            each_first_params.shift_y, each_first_params.inplane_angle, each_first_params.peak,
            each_first_params.mirror, None, None, 'previous']]
            
            coarse_align_loginfo += [[ref_orientation_param.stack_id, ref_orientation_param.local_id,
            ref_orientation_param.model_id, ref_orientation_param.phi, ref_orientation_param.theta,
            ref_orientation_param.psi, ref_orientation_param.shift_x, ref_orientation_param.shift_y,
            ref_orientation_param.inplane_angle, ref_orientation_param.peak, ref_orientation_param.mirror,
            selected_log_info[0], selected_log_info[1], 'current']]
        
        msg = tabulate(coarse_align_loginfo, list(orientation_parameters._fields)[:-1] + ['phi_range', 'theta_range', 'cycle'])
        self.log.tlog('The following alignment parameters were determined:\n{0}'.format(msg))
        
        return coarse_determined_params


    def get_restraint_tuple(self):
        restraint_tuple = namedtuple('restraints', 'azimuthal_restraint out_of_plane_restraint x_range y_range pixelsize')
        
        return restraint_tuple
    

    def refine_local_inplane_angle(self, masked_segment_stack, step_x, each_info, x_range, y_range,
    delta_in_plane_rotation, step_angle, reference_rings, projection_parameters, polar_interpolation_parameters,
    coarse_determined_params, fine_projection_stack, alignment_size):
        ref_orientation_params = []
        restraint_tuple = self.get_restraint_tuple()
        tilt_range = 1.2 * abs(self.out_of_plane_tilt_angle_range[-1] - self.out_of_plane_tilt_angle_range[0]) 
        
        restraint_info = restraint_tuple(1.2 * 360.0 / self.azimuthal_angle_count, tilt_range /
        self.out_of_plane_tilt_angle_count, x_range, y_range, each_info.pixelsize)
        
        orientation_parameters = self.make_named_tuple_of_orientation_parameters()
        ref_align_loginfo = []
        for each_previous_params in coarse_determined_params:
            selected_ref_rings, selected_prj_params, selected_log_info = \
            self.select_reference_rings_according_to_angular_restraints(reference_rings, restraint_info,
            projection_parameters, each_previous_params)
            
            if fine_projection_stack is not None:
                selected_ref_rings, polar_interpolation_parameters = \
                self.prepare_reference_rings_from_projections(fine_projection_stack, selected_prj_params,
                alignment_size, each_info.max_range)
            
            segment_params = \
            self.refine_each_image_against_projections_including_delta_inplane_restraint(masked_segment_stack,
            each_previous_params, selected_ref_rings, selected_prj_params, restraint_info, step_x,
            step_angle, delta_in_plane_rotation, polar_interpolation_parameters, alignment_size)
                
            segment_params.insert(0, each_previous_params.stack_id)
            segment_params.insert(1, each_previous_params.local_id)
            
            if hasattr(self, 'rank'):
                segment_params.append(self.rank)
            else:
                segment_params.append(None)
            
            ref_align_loginfo += [list(each_previous_params)[:-1] + [None, None, 'coarse']]
            ref_align_loginfo += [segment_params[:-1] + [selected_log_info[0], selected_log_info[1], 'fine']]
            
            segment_params = orientation_parameters._make(segment_params)
            ref_orientation_params.append(segment_params)
        
        msg = tabulate(ref_align_loginfo, list(each_previous_params._fields)[:-1] + ['phi_range', 'theta_range', 'align type'])
        self.log.tlog('The following refined parameters were determined for in-plane ' + \
        'angles:\n{0}'.format(msg))
        
        return ref_orientation_params
    

    def convert_coarse_into_fine_parameters(self, coarse_params):
        fine_params = []
        for each_param in coarse_params:
            params = list(each_param)[:-1]
            if hasattr(self, 'comm'):
                params.append(self.rank)
            elif not hasattr(self, 'comm'):
                params.append(None)
            fine_params.append(params)
        
        return fine_params
    
        
    def get_prj_params_named_tuple(self):
        prj_named_tuple = namedtuple('prj_parameters', 'id model_id phi theta psi shift_x shift_y')

        return prj_named_tuple


    def get_prj_stack_name_with_ending(self, projection_stack, ending):
        azimuthal_prj_stack = os.path.splitext(projection_stack)[0] + ending + \
        os.path.splitext(projection_stack)[-1]
        
        return azimuthal_prj_stack


    def copy_out_angular_series(self, projection_stack, azimuthal_prj_stack, azimuthal_angles):
        img = EMData()
        for each_azimuth_id, each_azimuth in enumerate(azimuthal_angles):
            img.read_image(projection_stack, each_azimuth.id)
            img.write_image(azimuthal_prj_stack, each_azimuth_id)
            
        return azimuthal_prj_stack


    def get_azimuthal_angles_from_prj_params(self, projection_parameters, model_id=None, unique_angle='theta'):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> proj_params = s.generate_Euler_angles_for_projection(4, [-8, 8], 3, 22.04) 
        >>> proj_params = [[0]+ each_p for each_p in proj_params]
        >>> proj_tuples = s.convert_list_of_projection_parameters_to_prj_tuples(proj_params)
        >>> s.get_azimuthal_angles_from_prj_params(proj_tuples) #doctest: +NORMALIZE_WHITESPACE
        [prj_parameters(id=4, model_id=0, phi=0.0, theta=90.0, psi=270.0, shift_x=0.0, shift_y=0.0), 
        prj_parameters(id=5, model_id=0, phi=27.549999999999997, theta=90.0, psi=270.0, shift_x=0.0, shift_y=0.0), 
        prj_parameters(id=6, model_id=0, phi=55.099999999999994, theta=90.0, psi=270.0, shift_x=0.0, shift_y=0.0), 
        prj_parameters(id=7, model_id=0, phi=82.65, theta=90.0, psi=270.0, shift_x=0.0, shift_y=0.0)]
        >>> s.get_azimuthal_angles_from_prj_params(proj_tuples, 0) #doctest: +NORMALIZE_WHITESPACE
        [prj_parameters(id=4, model_id=0, phi=0.0, theta=90.0, psi=270.0, shift_x=0.0, shift_y=0.0), 
        prj_parameters(id=5, model_id=0, phi=27.549999999999997, theta=90.0, psi=270.0, shift_x=0.0, shift_y=0.0), 
        prj_parameters(id=6, model_id=0, phi=55.099999999999994, theta=90.0, psi=270.0, shift_x=0.0, shift_y=0.0), 
        prj_parameters(id=7, model_id=0, phi=82.65, theta=90.0, psi=270.0, shift_x=0.0, shift_y=0.0)]
        >>> s.get_azimuthal_angles_from_prj_params(proj_tuples, 1)
        []
        """
        if model_id is None:
            un_thetas = np.unique([getattr(each_param, unique_angle) for each_param in projection_parameters])
            theta_closest_to_avg = np.argmin(np.abs(un_thetas - np.average(un_thetas)))

            azimuthal_angles = [each_param for each_param in projection_parameters \
                                if getattr(each_param, unique_angle) == un_thetas[theta_closest_to_avg]]
        else:
            un_thetas = np.unique([each_param.theta for each_param in projection_parameters
                                   if each_param.model_id == model_id])

            if len(un_thetas) > 0: 
                theta_closest_to_avg = np.argmin(np.abs(un_thetas - np.average(un_thetas)))
    
                azimuthal_angles = [each_param for each_param in projection_parameters \
                                    if getattr(each_param, unique_angle) == un_thetas[theta_closest_to_avg] and \
                                    each_param.model_id == model_id]
            else:
                azimuthal_angles = []

        return azimuthal_angles


    def get_out_of_plane_angles_from_prj_params(self, projection_parameters, model_id=None):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> proj_params = s.generate_Euler_angles_for_projection(4, [-8, 8], 3, 22.04) 
        >>> proj_params = [[0]+ each_p for each_p in proj_params]
        >>> proj_tuples = s.convert_list_of_projection_parameters_to_prj_tuples(proj_params)
        >>> s.get_out_of_plane_angles_from_prj_params(proj_tuples) #doctest: +NORMALIZE_WHITESPACE
        [prj_parameters(id=2, model_id=0, phi=55.099999999999994, theta=82.0, psi=270.0, shift_x=0.0, shift_y=0.0), 
        prj_parameters(id=6, model_id=0, phi=55.099999999999994, theta=90.0, psi=270.0, shift_x=0.0, shift_y=0.0), 
        prj_parameters(id=10, model_id=0, phi=55.099999999999994, theta=98.0, psi=270.0, shift_x=0.0, shift_y=0.0)]
        >>> s.get_out_of_plane_angles_from_prj_params(proj_tuples, 1)
        []
        """
        out_of_plane_angles = self.get_azimuthal_angles_from_prj_params(projection_parameters,model_id=model_id,
        unique_angle='phi')

        return out_of_plane_angles


    def remove_projection_stacks_and_copy_out_azimuthal_and_out_of_plane_series(self, prj_info):
        if hasattr(self, 'comm'):
            self.comm.barrier()
        if prj_info.projection_stack.startswith(self.tempdir):
            azimuthal_angles = self.get_azimuthal_angles_from_prj_params(prj_info.projection_parameters)
            out_of_plane_angles = self.get_out_of_plane_angles_from_prj_params(prj_info.projection_parameters)
            azimuthal_prj_stack = self.get_prj_stack_name_with_ending(prj_info.projection_stack, ending='az')
            out_of_plane_prj_stack = self.get_prj_stack_name_with_ending(prj_info.projection_stack, ending='out')

            if prj_info.fine_projection_stack is None:
                self.copy_out_angular_series(prj_info.projection_stack, azimuthal_prj_stack, azimuthal_angles)
                self.copy_out_angular_series(prj_info.projection_stack, out_of_plane_prj_stack, out_of_plane_angles)
            elif prj_info.fine_projection_stack is not None:
                self.copy_out_angular_series(prj_info.fine_projection_stack, azimuthal_prj_stack, azimuthal_angles)
                self.copy_out_angular_series(prj_info.fine_projection_stack, out_of_plane_prj_stack, out_of_plane_angles)
                os.remove(prj_info.fine_projection_stack)

            os.remove(prj_info.projection_stack)


    def convert_list_of_projection_parameters_to_prj_tuples(self, projection_parameters):
        prj_named_tuple = self.get_prj_params_named_tuple()
        
        prj_tuples = [ prj_named_tuple._make([each_prj_id] + each_prj_param) \
                      for each_prj_id, each_prj_param in enumerate(projection_parameters) ]

        return prj_tuples


    def perform_coarse_and_fine_projection_matching(self, each_info, masked_segment_stack, prj_info, previous_params,
    alignment_size):
        
        self.log.fcttolog()
        self.log.in_progress_log()

        prj_tuples = self.convert_list_of_projection_parameters_to_prj_tuples(prj_info.projection_parameters)
        prj_info = prj_info._replace(projection_parameters = prj_tuples)

        step_x = 1.0
        step_angle = 0.05
        zoom_refinement_factor = 5.0
        
        reference_rings, polar_interpolation_parameters = \
        self.prepare_reference_rings_from_projections(prj_info.projection_stack, prj_info.projection_parameters,
        alignment_size, each_info.max_range)
        
        coarse_determined_params = self.find_maximum_cross_correlation_for_local_in_plane_angle(masked_segment_stack,
        step_x, each_info, reference_rings, prj_info.projection_parameters, polar_interpolation_parameters,
        previous_params, alignment_size)
        
        fine_x_search_range = each_info.x_range / zoom_refinement_factor
        fine_y_search_range = each_info.y_range / zoom_refinement_factor
        fine_step_angle = np.sin(np.deg2rad(step_angle / zoom_refinement_factor))
        
        if prj_info.fine_projection_stack is not None:
            prj_tuples = self.convert_list_of_projection_parameters_to_prj_tuples(prj_info.fine_projection_parameters)
            prj_info = prj_info._replace(projection_parameters = prj_tuples)

            reference_rings = None
            polar_interpolation_parameters = None
        
        refined_orientation_parameters = self.refine_local_inplane_angle(masked_segment_stack,
        step_x / zoom_refinement_factor, each_info, fine_x_search_range, fine_y_search_range,
        self.delta_in_plane_rotation / zoom_refinement_factor, fine_step_angle, reference_rings, 
        prj_info.projection_parameters, polar_interpolation_parameters, coarse_determined_params, 
        prj_info.fine_projection_stack, alignment_size)
        
        self.remove_projection_stacks_and_copy_out_azimuthal_and_out_of_plane_series(prj_info)
            
        return refined_orientation_parameters, step_x, prj_info
    
