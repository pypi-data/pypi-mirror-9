# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import EMData, Util, Transform, Vec2f, Reconstructors
from spring.micprgs.scansplit import Micrograph
from spring.segment2d.segment import Segment
from spring.segment3d.segclassreconstruct_prep import SegClassReconstructCylinderMask
from tabulate import tabulate
from utilities import compose_transform2, model_circle, get_sym
import numpy as np


class SegClassReconstructAssist(SegClassReconstructCylinderMask):                
    def compute_transform_with_aligned_helix_segment(self, phi, theta, psi):
        transform = Transform({'type':'spider', 'phi':phi, 'theta':theta, 'psi':psi})
        transform_helical_origin = Transform({'type':'spider', 'phi':0.0, 'theta':90.0, 'psi':270.0})
        transposed_helical_origin = transform_helical_origin.transpose()
        composite_transform = transform * transposed_helical_origin
        RABTeuler = composite_transform.get_rotation('spider')
        
        return RABTeuler


    def compute_helical_inplane_rotation_from_Euler_angles(self, phi, theta, psi):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> SegClassReconstruct().compute_helical_inplane_rotation_from_Euler_angles(180, 90, 270)
        0.0
        >>> SegClassReconstruct().compute_helical_inplane_rotation_from_Euler_angles(0, 90, 270)
        0.0
        >>> SegClassReconstruct().compute_helical_inplane_rotation_from_Euler_angles(33, 90, 334)
        64.00000006504217
        >>> SegClassReconstruct().compute_helical_inplane_rotation_from_Euler_angles(180, 90, 240)
        329.999999554708
        >>> SegClassReconstruct().compute_helical_inplane_rotation_from_Euler_angles(150.0, 94.0, 315)
        45.0
        >>> SegClassReconstruct().compute_helical_inplane_rotation_from_Euler_angles(150.0, 86.0, 315)
        225.0
        >>> SegClassReconstruct().compute_helical_inplane_rotation_from_Euler_angles(170.0, 90.0, 315)
        45.00000000000006
        """
        RABTeuler = self.compute_transform_with_aligned_helix_segment(phi, 90.0, psi)
        RABTphi = RABTeuler['phi']
        RABTpsi = RABTeuler['psi']
        
#        delta_inplane_rotation = (RABTpsi + RABTphi) % 360
        if theta >= 90:
            delta_inplane_rotation = (RABTpsi + RABTphi) % 360
        else:
            delta_inplane_rotation = (RABTpsi + RABTphi + 180) % 360
        
        return delta_inplane_rotation
    

    def compute_point_where_normal_and_parallel_line_intersect(self, shift_x, shift_y, inplane_angle):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> s = SegClassReconstruct()
        >>> s.compute_point_where_normal_and_parallel_line_intersect(3, 1, 0)
        (3.0, -1.8369701987210297e-16)
        >>> s.compute_point_where_normal_and_parallel_line_intersect(3, 1, 45)
        (2.0000000000000004, 2.0)
        >>> s.compute_point_where_normal_and_parallel_line_intersect(3, 1, -45)
        (0.99999999999999978, -0.99999999999999989)
        >>> s.compute_point_where_normal_and_parallel_line_intersect(3, 1, 90)
        (1.7449489701899453e-12, 1.0000000000052349)
        """
        if inplane_angle == 90.0 or inplane_angle == 270.0:
            inplane_angle -= 1e-10
            
        if 90.0 + inplane_angle == 0:
            slope = np.tan(np.deg2rad(360.0))
        else:
            slope = np.tan(np.deg2rad(90.0 + inplane_angle))
            
        t = shift_y - slope * shift_x 
        
        point_x = -t / (1/slope + slope)
        point_y = -point_x / slope 
        
        return point_x, point_y
    
        
    def compute_distances_to_helical_axis(self, shift_x, shift_y, inplane_angle):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> SegClassReconstruct().compute_distances_to_helical_axis(22, 2, 0)
        (-22.0, 2.0000000000000013)
        >>> SegClassReconstruct().compute_distances_to_helical_axis(22, 2, 180)
        (22.0, -2.000000000000004)
        >>> SegClassReconstruct().compute_distances_to_helical_axis(22, 2, 90)
        (-2.0000000000383888, -21.999999999996511)
        >>> SegClassReconstruct().compute_distances_to_helical_axis(3, 1, -45)
        (-1.4142135623730949, 2.8284271247461898)
        >>> SegClassReconstruct().compute_distances_to_helical_axis(3, 1, 45)
        (-2.8284271247461903, -1.4142135623730947)
        >>> SegClassReconstruct().compute_distances_to_helical_axis(22, 2, 20)
        (-21.357277943941323, -5.6450579115928949)
        >>> s = SegClassReconstruct()
        >>> hx, hy = s.compute_distances_to_helical_axis(22, 2, 180)
        >>> SegClassReconstruct().compute_distances_to_helical_axis(hx, hy, 180)
        (22.0, 2.0)
        """
        
        point_x, point_y = self.compute_point_where_normal_and_parallel_line_intersect(shift_x, shift_y, inplane_angle)
        dist_x, dst_y = Segment().rotate_coordinates_by_angle(-point_x, -point_y, inplane_angle)
        
        centered_x = shift_x - point_x
        centered_y = shift_y - point_y
        dst_x, dist_y = Segment().rotate_coordinates_by_angle(centered_x, centered_y, inplane_angle)
        
        return dist_x, dist_y
    
    
    def prepare_symmetry_computation(self, alignment_parameters, each_symmetry_pair, pixelsize, symmetry_views_count):
        helical_rise = each_symmetry_pair[0] / pixelsize
        helical_rotation = each_symmetry_pair[1]
        symmetry_views = np.arange(-symmetry_views_count / 2, symmetry_views_count / 2)
        
        x_norm, y_parallel = self.compute_distances_to_helical_axis(alignment_parameters.x_shift,
        alignment_parameters.y_shift, alignment_parameters.inplane_angle)
        
        if helical_rise != 0:
            multiple_off_center = round(y_parallel / helical_rise)
        else:
            multiple_off_center = 0
            
        symmetry_views += multiple_off_center
        out_of_plane_correction = np.sin(np.deg2rad(alignment_parameters.theta))
        
        return symmetry_views, helical_rotation, out_of_plane_correction, helical_rise

        
    def compute_straight_phi_and_yshift(self, each_symmetry_view, phi, helical_rotation, out_of_plane_correction,
    helical_rise):
        symmetrized_phi = (phi + each_symmetry_view * helical_rotation) % 360
        straight_yshift = out_of_plane_correction * each_symmetry_view * helical_rise
        
        return straight_yshift, symmetrized_phi


    def compute_sx_sy_from_shifts_normal_and_parallel_to_helix_axis_with_inplane_angle(self, helix_shift_x,
    helix_shift_y, inplane_angle):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> hx, hy = SegClassReconstruct().compute_distances_to_helical_axis(3, 1, -45)
        >>> s = SegClassReconstruct()
        >>> s.compute_sx_sy_from_shifts_normal_and_parallel_to_helix_axis_with_inplane_angle(hx, hy, -45)
        (2.9999999999999996, 1.0000000000000002)
        >>> s.compute_sx_sy_from_shifts_normal_and_parallel_to_helix_axis_with_inplane_angle(3, 0, -45)
        (-2.1213203435596428, 2.1213203435596424)
        >>> hx, hy = SegClassReconstruct().compute_distances_to_helical_axis(22, 2, 20)
        >>> s.compute_sx_sy_from_shifts_normal_and_parallel_to_helix_axis_with_inplane_angle(hx, hy, 20)
        (22.0, 2.0)
        """
        point_x, point_y = Segment().rotate_coordinates_by_angle(helix_shift_x, 0, -inplane_angle)
        helix_y_from_point = helix_shift_y - point_y
        sx, sy = Segment().rotate_coordinates_by_angle(-point_x, helix_y_from_point, -inplane_angle, -point_x, -point_y)
        
        return sx, sy
        
    
    def correct_straight_symmetry_parameters_for_in_plane_rotation_and_shifts_old(self, inplane_angle, x_shift, y_shift,
    straight_yshift):
#        x_contribution, y_contribution = self.compute_sx_sy_from_shifts_normal_and_parallel_to_helix_axis_with_inplane_angle(0.0, straight_yshift, inplane_angle)

        new_rot, x_contribution, y_contribution, scale = compose_transform2(0.0, 0, straight_yshift, 1.0, inplane_angle,
        0.0, 0.0, 1.0)
        
        total_symmetrized_xshift = x_contribution + x_shift
        total_symmetrized_yshift = y_contribution + y_shift
        
        return total_symmetrized_xshift, total_symmetrized_yshift
    
    
    def correct_straight_symmetry_parameters_for_in_plane_rotation_and_shifts(self, inplane_angle, x_shift, y_shift,
    straight_yshift):
        
        x_norm, y_parallel = self.compute_distances_to_helical_axis(x_shift, y_shift, inplane_angle)
        
        total_symmetrized_xshift, total_symmetrized_yshift = \
        self.compute_sx_sy_from_shifts_normal_and_parallel_to_helix_axis_with_inplane_angle(x_norm, y_parallel + \
        straight_yshift, inplane_angle)
        
        return -total_symmetrized_xshift, -total_symmetrized_yshift
    

    def compute_helical_symmetry_related_views(self, alignment_parameters, each_symmetry_pair, pixelsize,
    symmetry_views_count):
        """
        #. positive y-shift for straight helix
        #. negative y-shift for straight helix
        #. negative y-shift including x-shift with flipped helix
        #. helix perpendicular to 'straight'
        #. id3 but respective x and y shifts swapped
        #. test angle of 45 degrees
        #. test angle of 60 degrees
        #. Out-of-plane tilt will affect helical rise in image plane:
        #. If straight y-shift is smaller than helical rise, no action need to taken
        #. If straight y-shift is larger than half helical rise will be reduced:
        
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> s = SegClassReconstruct()
        >>> rec_parameters = s.make_named_tuple_for_reconstruction()
        >>> r_info = rec_parameters(0, 0, 0, 90, 270, 0, 0, 0.0, 0, 22)
        >>> s.compute_helical_symmetry_related_views(r_info, (10, 50), 10, 10)
        (array([[   0.,  110.,   90.,  270.,   -0.,    5.,    0.,   22.],
               [   0.,  160.,   90.,  270.,   -0.,    4.,    0.,   22.],
               [   0.,  210.,   90.,  270.,   -0.,    3.,    0.,   22.],
               [   0.,  260.,   90.,  270.,   -0.,    2.,    0.,   22.],
               [   0.,  310.,   90.,  270.,   -0.,    1.,    0.,   22.],
               [   0.,    0.,   90.,  270.,   -0.,   -0.,    0.,   22.],
               [   0.,   50.,   90.,  270.,   -0.,   -1.,    0.,   22.],
               [   0.,  100.,   90.,  270.,   -0.,   -2.,    0.,   22.],
               [   0.,  150.,   90.,  270.,   -0.,   -3.,    0.,   22.],
               [   0.,  200.,   90.,  270.,   -0.,   -4.,    0.,   22.]]), 0.0)

        >>> r_info = rec_parameters(0, 0, 0, 90, 270, 0.5, 3.0, 0.0, 0, 22)
        >>> s.compute_helical_symmetry_related_views(r_info, (10, 50), 10, 10)
        (array([[   0. ,  260. ,   90. ,  270. ,    0.5,    5. ,    0. ,   22. ],
               [   0. ,  310. ,   90. ,  270. ,    0.5,    4. ,    0. ,   22. ],
               [   0. ,    0. ,   90. ,  270. ,    0.5,    3. ,    0. ,   22. ],
               [   0. ,   50. ,   90. ,  270. ,    0.5,    2. ,    0. ,   22. ],
               [   0. ,  100. ,   90. ,  270. ,    0.5,    1. ,    0. ,   22. ],
               [   0. ,  150. ,   90. ,  270. ,    0.5,   -0. ,    0. ,   22. ],
               [   0. ,  200. ,   90. ,  270. ,    0.5,   -1. ,    0. ,   22. ],
               [   0. ,  250. ,   90. ,  270. ,    0.5,   -2. ,    0. ,   22. ],
               [   0. ,  300. ,   90. ,  270. ,    0.5,   -3. ,    0. ,   22. ],
               [   0. ,  350. ,   90. ,  270. ,    0.5,   -4. ,    0. ,   22. ]]), 0.0)

        >>> r_info = rec_parameters(0, 0, 0, 90, 270, 0, 0, 0.0, 0, 22)
        >>> s.compute_helical_symmetry_related_views(r_info, (10, 50), 10, 2)
        (array([[   0.,  310.,   90.,  270.,   -0.,    1.,    0.,   22.],
               [   0.,    0.,   90.,  270.,   -0.,   -0.,    0.,   22.]]), 0.0)
              
        >>> r_info = rec_parameters(3, 3, 0, 90, 90, 2.5, -3.5, 180.0, 0, 22)
        >>> s.compute_helical_symmetry_related_views(r_info, (10, 50), 10, 10)
        (array([[   3. ,  260. ,   90. ,   90. ,    2.5,   -5.5,    0. ,   22. ],
               [   3. ,  310. ,   90. ,   90. ,    2.5,   -4.5,    0. ,   22. ],
               [   3. ,    0. ,   90. ,   90. ,    2.5,   -3.5,    0. ,   22. ],
               [   3. ,   50. ,   90. ,   90. ,    2.5,   -2.5,    0. ,   22. ],
               [   3. ,  100. ,   90. ,   90. ,    2.5,   -1.5,    0. ,   22. ],
               [   3. ,  150. ,   90. ,   90. ,    2.5,   -0.5,    0. ,   22. ],
               [   3. ,  200. ,   90. ,   90. ,    2.5,    0.5,    0. ,   22. ],
               [   3. ,  250. ,   90. ,   90. ,    2.5,    1.5,    0. ,   22. ],
               [   3. ,  300. ,   90. ,   90. ,    2.5,    2.5,    0. ,   22. ],
               [   3. ,  350. ,   90. ,   90. ,    2.5,    3.5,    0. ,   22. ]]), 180.0)

        >>> r_info = rec_parameters(2, 2, 0, 90, 180, 2.5, -3.5, 270.0, 0, 22)
        >>> s.compute_helical_symmetry_related_views(r_info, (10, 50), 10, 10)
        (array([[   2. ,  260. ,   90. ,  180. ,    4.5,   -3.5,    0. ,   22. ],
               [   2. ,  310. ,   90. ,  180. ,    3.5,   -3.5,    0. ,   22. ],
               [   2. ,    0. ,   90. ,  180. ,    2.5,   -3.5,    0. ,   22. ],
               [   2. ,   50. ,   90. ,  180. ,    1.5,   -3.5,    0. ,   22. ],
               [   2. ,  100. ,   90. ,  180. ,    0.5,   -3.5,    0. ,   22. ],
               [   2. ,  150. ,   90. ,  180. ,   -0.5,   -3.5,    0. ,   22. ],
               [   2. ,  200. ,   90. ,  180. ,   -1.5,   -3.5,    0. ,   22. ],
               [   2. ,  250. ,   90. ,  180. ,   -2.5,   -3.5,    0. ,   22. ],
               [   2. ,  300. ,   90. ,  180. ,   -3.5,   -3.5,    0. ,   22. ],
               [   2. ,  350. ,   90. ,  180. ,   -4.5,   -3.5,    0. ,   22. ]]), 270.0)

        >>> r_info = rec_parameters(4, 4, 0, 90, 180, -2.5, 3.5, 270.0, 0, 22)
        >>> s.compute_helical_symmetry_related_views(r_info, (10, 50), 10, 10)
        (array([[   4. ,  320. ,   90. ,  180. ,    5.5,    3.5,    0. ,   22. ],
               [   4. ,   10. ,   90. ,  180. ,    4.5,    3.5,    0. ,   22. ],
               [   4. ,   60. ,   90. ,  180. ,    3.5,    3.5,    0. ,   22. ],
               [   4. ,  110. ,   90. ,  180. ,    2.5,    3.5,    0. ,   22. ],
               [   4. ,  160. ,   90. ,  180. ,    1.5,    3.5,    0. ,   22. ],
               [   4. ,  210. ,   90. ,  180. ,    0.5,    3.5,    0. ,   22. ],
               [   4. ,  260. ,   90. ,  180. ,   -0.5,    3.5,    0. ,   22. ],
               [   4. ,  310. ,   90. ,  180. ,   -1.5,    3.5,    0. ,   22. ],
               [   4. ,    0. ,   90. ,  180. ,   -2.5,    3.5,    0. ,   22. ],
               [   4. ,   50. ,   90. ,  180. ,   -3.5,    3.5,    0. ,   22. ]]), 270.0)

        >>> r_info = rec_parameters(5, 5, 0, 90, 45, 1.0, 1.0, 135.0, 0, 22)
        >>> s.compute_helical_symmetry_related_views(r_info, (10, 50), 10, 10)
        (array([[  5.00000000e+00,   6.00000000e+01,   9.00000000e+01,
                  4.50000000e+01,  -3.24264069e+00,  -3.24264069e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  5.00000000e+00,   1.10000000e+02,   9.00000000e+01,
                  4.50000000e+01,  -2.53553391e+00,  -2.53553391e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  5.00000000e+00,   1.60000000e+02,   9.00000000e+01,
                  4.50000000e+01,  -1.82842712e+00,  -1.82842712e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  5.00000000e+00,   2.10000000e+02,   9.00000000e+01,
                  4.50000000e+01,  -1.12132034e+00,  -1.12132034e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  5.00000000e+00,   2.60000000e+02,   9.00000000e+01,
                  4.50000000e+01,  -4.14213562e-01,  -4.14213562e-01,
                  0.00000000e+00,   2.20000000e+01],
               [  5.00000000e+00,   3.10000000e+02,   9.00000000e+01,
                  4.50000000e+01,   2.92893219e-01,   2.92893219e-01,
                  0.00000000e+00,   2.20000000e+01],
               [  5.00000000e+00,   0.00000000e+00,   9.00000000e+01,
                  4.50000000e+01,   1.00000000e+00,   1.00000000e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  5.00000000e+00,   5.00000000e+01,   9.00000000e+01,
                  4.50000000e+01,   1.70710678e+00,   1.70710678e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  5.00000000e+00,   1.00000000e+02,   9.00000000e+01,
                  4.50000000e+01,   2.41421356e+00,   2.41421356e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  5.00000000e+00,   1.50000000e+02,   9.00000000e+01,
                  4.50000000e+01,   3.12132034e+00,   3.12132034e+00,
                  0.00000000e+00,   2.20000000e+01]]), 135.0)
        
        >>> r_info = rec_parameters(6, 3, 0, 90, 60, 1, 1, 150.0, 0, 22)
        >>> s.compute_helical_symmetry_related_views(r_info, (10, 50), 10, 10)
        (array([[  6.00000000e+00,   6.00000000e+01,   9.00000000e+01,
                  6.00000000e+01,  -2.00000000e+00,  -4.19615242e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.10000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -1.50000000e+00,  -3.33012702e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.60000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -1.00000000e+00,  -2.46410162e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   2.10000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -5.00000000e-01,  -1.59807621e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   2.60000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -3.33066907e-16,  -7.32050808e-01,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   3.10000000e+02,   9.00000000e+01,
                  6.00000000e+01,   5.00000000e-01,   1.33974596e-01,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   0.00000000e+00,   9.00000000e+01,
                  6.00000000e+01,   1.00000000e+00,   1.00000000e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   5.00000000e+01,   9.00000000e+01,
                  6.00000000e+01,   1.50000000e+00,   1.86602540e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.00000000e+02,   9.00000000e+01,
                  6.00000000e+01,   2.00000000e+00,   2.73205081e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.50000000e+02,   9.00000000e+01,
                  6.00000000e+01,   2.50000000e+00,   3.59807621e+00,
                  0.00000000e+00,   2.20000000e+01]]), 150.0)
                  
        >>> s.compute_helical_symmetry_related_views(r_info, (10, 50), 10, 10)
        (array([[  6.00000000e+00,   6.00000000e+01,   9.00000000e+01,
                  6.00000000e+01,  -2.00000000e+00,  -4.19615242e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.10000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -1.50000000e+00,  -3.33012702e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.60000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -1.00000000e+00,  -2.46410162e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   2.10000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -5.00000000e-01,  -1.59807621e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   2.60000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -3.33066907e-16,  -7.32050808e-01,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   3.10000000e+02,   9.00000000e+01,
                  6.00000000e+01,   5.00000000e-01,   1.33974596e-01,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   0.00000000e+00,   9.00000000e+01,
                  6.00000000e+01,   1.00000000e+00,   1.00000000e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   5.00000000e+01,   9.00000000e+01,
                  6.00000000e+01,   1.50000000e+00,   1.86602540e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.00000000e+02,   9.00000000e+01,
                  6.00000000e+01,   2.00000000e+00,   2.73205081e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.50000000e+02,   9.00000000e+01,
                  6.00000000e+01,   2.50000000e+00,   3.59807621e+00,
                  0.00000000e+00,   2.20000000e+01]]), 150.0)
                  
        >>> s.compute_helical_symmetry_related_views(r_info, (10, 50), 10, 10)
        (array([[  6.00000000e+00,   6.00000000e+01,   9.00000000e+01,
                  6.00000000e+01,  -2.00000000e+00,  -4.19615242e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.10000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -1.50000000e+00,  -3.33012702e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.60000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -1.00000000e+00,  -2.46410162e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   2.10000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -5.00000000e-01,  -1.59807621e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   2.60000000e+02,   9.00000000e+01,
                  6.00000000e+01,  -3.33066907e-16,  -7.32050808e-01,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   3.10000000e+02,   9.00000000e+01,
                  6.00000000e+01,   5.00000000e-01,   1.33974596e-01,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   0.00000000e+00,   9.00000000e+01,
                  6.00000000e+01,   1.00000000e+00,   1.00000000e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   5.00000000e+01,   9.00000000e+01,
                  6.00000000e+01,   1.50000000e+00,   1.86602540e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.00000000e+02,   9.00000000e+01,
                  6.00000000e+01,   2.00000000e+00,   2.73205081e+00,
                  0.00000000e+00,   2.20000000e+01],
               [  6.00000000e+00,   1.50000000e+02,   9.00000000e+01,
                  6.00000000e+01,   2.50000000e+00,   3.59807621e+00,
                  0.00000000e+00,   2.20000000e+01]]), 150.0)
        
        """
        symmetry_alignment_parameters = []
        symmetry_views, helical_rotation, out_of_plane_correction, helical_rise = \
            self.prepare_symmetry_computation(alignment_parameters, each_symmetry_pair, pixelsize, symmetry_views_count)
        
        for each_symmetry_related_view in symmetry_views:
            straight_yshift, symmetrized_phi = self.compute_straight_phi_and_yshift(each_symmetry_related_view,
            alignment_parameters.phi, helical_rotation, out_of_plane_correction, helical_rise)
            
            total_symmetrized_xshift, total_symmetrized_yshift = \
            self.correct_straight_symmetry_parameters_for_in_plane_rotation_and_shifts(
            alignment_parameters.inplane_angle, -alignment_parameters.x_shift, -alignment_parameters.y_shift, 
            straight_yshift)
            
            symmetry_alignment_parameters.append(np.array([alignment_parameters.stack_id, symmetrized_phi,
            alignment_parameters.theta, alignment_parameters.psi, total_symmetrized_xshift, total_symmetrized_yshift,
            alignment_parameters.mirror, alignment_parameters.seg_ref_id], dtype=float))
            
        symmetry_alignment_parameters = np.vstack(symmetry_alignment_parameters)
        
        return symmetry_alignment_parameters, alignment_parameters.inplane_angle
    
    
    def setup_reconstructor(self, imgsize):
        fftvol = EMData()
        weight = EMData()
        #ds.humanize_bytes(s.compute_byte_size_of_image_stack(4 * 200,4 * 200,4 * 200)) = 1.91 GB
        if 0 < imgsize <= 200:
            npad = 4
        # ds.humanize_bytes(s.compute_byte_size_of_image_stack(3 * 267,3 * 267,3 * 267)) = 1.91GB
        elif 200 < imgsize <= 267:
            npad = 3
        #ds.humanize_bytes(s.compute_byte_size_of_image_stack(2 * 400,2 * 400,2 * 400)) = 1.91 GB
        elif 267 < imgsize <= 400:
            npad = 2
        elif imgsize > 400: 
            npad = 1.5
        params = {'size':imgsize, 'npad':npad, 'symmetry':'c1', 'fftvol':fftvol, 'weight':weight}
        r = Reconstructors.get('nn4', params)
        r.setup()
        
        return r, fftvol, weight
    

    def setup_transform_with_reduced_alignment_parameters(self, each_phi, each_theta, each_psi, each_x, each_y):
        transform_projection = Transform({'type':'spider', 'phi':each_phi, 'theta':each_theta, 'psi':each_psi})
        transform_projection.set_trans(Vec2f(-each_x, -each_y))
        
        return transform_projection
    

    def get_symmetry_transformations(self, point_symmetry):
        angs = get_sym(point_symmetry)
        
        sym_transformations = [Transform({'type':'spider', 'phi':each_phi, 'theta':each_theta, 'psi':each_psi}) for \
        each_phi, each_theta, each_psi in angs]
        
        return sym_transformations


    def get_Euler_angles_after_transformation(self, each_phi, each_theta, each_psi, each_x, each_y, each_sym_transform):
        current_transform = Transform({'type':'spider', 'phi':each_phi, 'theta':each_theta, 'psi':each_psi, 
                                       'tx': each_x, 'ty': each_y})
        transform_projection = current_transform * each_sym_transform
        trans = transform_projection.get_params('spider')
        
        return transform_projection, trans['phi'], trans['theta'], trans['psi'], trans['tx'], trans['ty']
    
    
    def compute_point_group_symmetry_related_views(self, sym_transformations, align_params, inplane=False):
        symmetry_alignment_parameters = []
        for (each_stack_id, each_phi, each_theta, each_psi, each_x, each_y, each_mirror, each_ref_id) in align_params:
            for each_sym_transform in sym_transformations:
                if inplane:
                    each_psi = 270.0
                transform_projection, trans_phi, trans_theta, trans_psi, trans_x, trans_y = \
                self.get_Euler_angles_after_transformation(each_phi, each_theta, each_psi, each_x, each_y, 
                each_sym_transform)
                
                symmetry_alignment_parameters.append(np.array([each_stack_id, trans_phi, trans_theta, trans_psi, trans_x,
                trans_y, each_mirror, each_ref_id], dtype=float))
        symmetry_alignment_parameters = np.vstack(symmetry_alignment_parameters)
        
        return symmetry_alignment_parameters
        

    def convert_alignment_parameters_to_symmetry_alignment_parameters(self, each_param):
        sym_align_parameters = np.vstack([[each_param.stack_id, each_param.phi, each_param.theta, each_param.psi,
        each_param.x_shift, each_param.y_shift, each_param.mirror, each_param.seg_ref_id]])
        
        return sym_align_parameters, each_param.inplane_angle
    

    def compute_all_symmetry_related_views(self, each_symmetry_pair, pixelsize, symmetry_views_count, point_symmetry,
    each_alignment_parameters):
        """
        >>> from spring.segment3d.segclassreconstruct import SegClassReconstruct
        >>> s = SegClassReconstruct()
        >>> rec_parameters = s.make_named_tuple_for_reconstruction()
        >>> r_info = rec_parameters(0, 0, 0, 90, 270, 0, 0, 0.0, 0, 22)
        >>> a, b, c = s.compute_all_symmetry_related_views((1.408, 22.03), 1.2, 2, 'c2', r_info)
        >>> a
        array([[   0.        ,  337.97000087,   90.        ,  270.        ,
                   0.        ,    1.17333329,    0.        ,   22.        ],
               [   0.        ,  157.97000087,   90.        ,  270.        ,
                   0.        ,    1.17333329,    0.        ,   22.        ],
               [   0.        ,    0.        ,   90.        ,  270.        ,
                   0.        ,    0.        ,    0.        ,   22.        ],
               [   0.        ,  180.        ,   90.        ,  270.        ,
                   0.        ,    0.        ,    0.        ,   22.        ]])
        """
        sym_transformations = self.get_symmetry_transformations(point_symmetry)
        
        helical_rise, helical_rotation = each_symmetry_pair
        if helical_rise == 0 and helical_rotation == 0:
            sym_align_params, inplane_angle = \
            self.convert_alignment_parameters_to_symmetry_alignment_parameters(each_alignment_parameters)
        else:
            sym_align_params, inplane_angle = self.compute_helical_symmetry_related_views(each_alignment_parameters,
            each_symmetry_pair, pixelsize, symmetry_views_count)
            
        log_sym_align_params = self.compute_point_group_symmetry_related_views(sym_transformations, sym_align_params)

        sym_align_params = self.compute_point_group_symmetry_related_views(sym_transformations, sym_align_params,
        inplane=True)
    
        return sym_align_params, inplane_angle, log_sym_align_params
    

    def compute_and_write_symmetry_related_views(self, rec_volume, image_stack, alignment_parameters,
    each_symmetry_pair, pixelsize, symmetry_views_count, trimmed_image_size, rec_stack, point_symmetry='c1', 
    mode='BP 3F'):
        
        if mode == 'BP RP':
            mask2d = model_circle(trimmed_image_size/2 - 2, trimmed_image_size, trimmed_image_size)  # SIRT works for squares only!
            mask2d = 1.0 - mask2d  # invert the mask to get average in corners
        total_symmetry_alignment_parameters = []
        Euler_angles_rec = []
        
        symmetry_image_single = EMData()
        symmetry_rec_loginfo = []
        rec_img_id = -1
        for each_alignment_parameters in alignment_parameters:
            each_stack_id = int(each_alignment_parameters[0])
            each_local_id = each_alignment_parameters[1]
            symmetry_image_single.read_image(image_stack, each_local_id)
            
            sym_align_params, inplane_angle, log_sym_align_params = \
            self.compute_all_symmetry_related_views(each_symmetry_pair, pixelsize, symmetry_views_count, point_symmetry,
            each_alignment_parameters)
            
            for each_sym_id, (each_stack_id, each_phi, each_theta, each_psi, each_x, each_y, each_mirror, each_ref_id) \
            in enumerate(sym_align_params):
                symmetry_image = symmetry_image_single.copy()
                
                trans_symmetry_image = Segment().shift_and_rotate_image_gridding(symmetry_image, inplane_angle,
                each_x, each_y)
                
                transform_projection = Transform({'type':'spider', 'phi':each_phi, 'theta':each_theta, 'psi':each_psi,
                'tx':0.0, 'ty':0.0})
                
                if rec_stack is not None:
                    rec_image = Util.window(trans_symmetry_image, rec_stack.alignment_size, rec_stack.alignment_size, 
                                            1, 0, 0, 0)
                    rec_img_id += 1
                    rec_image.write_image(rec_stack.file_name, rec_img_id)
                    
#                trans_symmetry_image.append_image('test_rec.hdf')
                symmetry_image = Util.window(trans_symmetry_image, trimmed_image_size, trimmed_image_size, 1, 0, 0, 0)
                symmetry_image.set_attr('xform.projection', transform_projection)
                
                if mode == 'BP 3F':
                    rec_volume.insert_slice(symmetry_image, transform_projection)
                elif mode == 'BP RP':
                    stat = Micrograph().get_statistics_from_image(symmetry_image, mask2d)
                    symmetry_image = symmetry_image - stat.avg    #subtract the background average in the corners
                    
                    myparams = {'transform':transform_projection, 'anglelist':[each_phi, each_theta, each_psi],
                    'radius':(trimmed_image_size/2 - 2)}
                    
                    rec_volume += symmetry_image.backproject('chao', myparams)
                log_psi = log_sym_align_params[each_sym_id][3]
                symmetry_rec_loginfo += [[each_stack_id, each_phi, each_theta, log_psi, each_x, each_y]]
                
                total_symmetry_alignment_parameters.append(np.array([each_stack_id, each_phi, each_theta, log_psi,
                each_x, each_y, each_mirror, each_ref_id], dtype=float))
                
                Euler_angles_rec.append(np.array([rec_img_id, each_stack_id, each_phi, each_theta, each_psi, each_x,
                each_y, inplane_angle]))
                
        total_symmetry_alignment_parameters = np.vstack(total_symmetry_alignment_parameters)
        Euler_angles_rec = np.vstack(Euler_angles_rec)
        
        symmetry_rec_loginfo = tabulate(symmetry_rec_loginfo, ['stack_id', 'phi', 'theta', 'psi', 'x-shift', 'y-shift'])

        return rec_volume, total_symmetry_alignment_parameters, symmetry_rec_loginfo, Euler_angles_rec
    
    
    def project_from_volume_and_backproject(self, alignment_parameters, trimmed_image_size, xvol,
    pxvol):
        for each_image_parameters in alignment_parameters:
            for (each_stack_id, each_phi, each_theta, each_psi, each_x, each_y, each_ref_id) in each_image_parameters:
                
                transform_projection = \
                self.setup_transform_with_reduced_alignment_parameters(trimmed_image_size, each_phi,
                each_theta, each_psi, each_x, each_y)
                
                myparams = {'transform':transform_projection, 'anglelist':[each_phi, each_theta, each_psi],
                'radius':(trimmed_image_size/2 - 2)}
                
                data = xvol.project('chao', myparams) 
                pxvol += data.backproject('chao', myparams)
        
        return pxvol
    