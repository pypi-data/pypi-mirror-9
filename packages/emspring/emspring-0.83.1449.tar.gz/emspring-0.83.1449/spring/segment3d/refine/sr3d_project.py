# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import EMData, EMUtil
from collections import namedtuple
from fundamentals import rot_shift2D
from morphology import binarize
from spring.csinfrastr.csdatabase import SpringDataBase, refine_base, RefinementCycleTable
from spring.segment2d.segment import Segment
from spring.segment2d.segmentexam import SegmentExam
from spring.segment3d.refine.sr3d_prepare import SegmentRefine3dSymmetry
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from sqlalchemy.sql.expression import desc
from tabulate import tabulate
from utilities import model_blank, model_circle
import numpy as np
import os
import shutil


class SegmentRefine3dPreparationStrategy(SegmentRefine3dSymmetry):
        
    def make_series_info_named_tuple(self):
        bin_info = namedtuple('series_info', 'bin_factor resolution_aim azimuthal_restraint out_of_plane_restraint ' +
        'x_range y_range max_range pixelsize iteration_count') 
        return bin_info
    

    def compute_resolution_ranges_for_binseries(self, bin_series, pixelsize):
#         nyqist_twice_pixs = 2.0 * pixelsize * bin_series
        thrice_pixs = 3.0 * pixelsize * bin_series

#         res_avg = (nyqist_twice_pixs + thrice_pixs) / 2.0
        res_avg = thrice_pixs
        
        return res_avg


    def set_res_expectation(self):
        low_res = 24.0#sum([40.0, 20.0]) / 2.0
        medium_res = 12.0#sum([20.0, 10.0]) / 2.0
        high_res = 7.0#sum([10.0, 6.0]) / 2.0
        max_res = 3.0#sum([6.0, 0.0]) / 2.0
        
        return [low_res, medium_res, high_res, max_res]
        

    def get_closest_binfactors(self, pixel_res, bin_series):
        
        res_avg = self.set_res_expectation()
        binfactors = [bin_series[np.argmin(np.abs(pixel_res - each_res))] for each_res in res_avg]
        
        return binfactors
    

    def determine_res_ranges_and_binfactors_to_be_used(self, pixelsize, resolution_aim):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> res_aim = {'low': True, 'medium': True, 'high': True, 'max': False}
        >>> s.determine_res_ranges_and_binfactors_to_be_used(1.78, res_aim)
        {'high': 1, 'medium': 2, 'low': 4}
        """
        bin_series = np.arange(1, 30)
        
        pixel_res = self.compute_resolution_ranges_for_binseries(bin_series, pixelsize)
        
        closest_binfactors = self.get_closest_binfactors(pixel_res, bin_series)
        
        selected_binfactors = {}
        for each_id, each_aim in enumerate(['low', 'medium', 'high', 'max']):
            if resolution_aim[each_aim]:
                selected_binfactors[each_aim]=closest_binfactors[each_id]
        
        return selected_binfactors

        
    def get_and_distribute_total_iteration_count(self, total_iteration_count, aims):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> dd = {'low': True, 'medium': True, 'high': True, 'max': False}
        >>> s.get_and_distribute_total_iteration_count(14, dd)
        {'high': 4, 'medium': 5, 'low': 5}
        >>> s.get_and_distribute_total_iteration_count(7, dd)
        {'high': 2, 'medium': 2, 'low': 3}
        """
        selected_keys = [each_aim for each_aim in ['low', 'medium', 'high', 'max'] if aims[each_aim]]
        count, rest = divmod(total_iteration_count, len(selected_keys))

        selected_counts = [count] * len(selected_keys)
        for each_rest in list(range(rest)):
            selected_counts[each_rest] += 1
        
        selected_counts = dict(zip(selected_keys, selected_counts))

        return selected_counts


    def define_series_of_search_steps(self, pixelsize, refine_strategy, low_resolution, medium_resolution,
    high_resolution, max_resolution, total_iteration_count):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> low_res = (False, (180.0, 180.0), (30, 20))
        >>> medium_res = (True, (180.0, 180.0), (20, 10))
        >>> high_res = (True, (20.0, 10.0), (10, 5)) 
        >>> max_res = (False, (2.0, 2.0), (5, 2.5))
        >>> p = 1.372, True, low_res, medium_res, high_res, max_res, 10
        >>> s.define_series_of_search_steps(p[0], p[1], p[2], p[3], p[4], p[5], p[6]) #doctest: +NORMALIZE_WHITESPACE
        ([series_info(bin_factor=3, resolution_aim='medium', 
        azimuthal_restraint=180.0, out_of_plane_restraint=180.0, 
        x_range=4.8590864917395526, y_range=2.4295432458697763, 
        max_range=4.8590864917395526, pixelsize=4.1160000000000005, 
        iteration_count=5), series_info(bin_factor=2, resolution_aim='high', 
        azimuthal_restraint=20.0, out_of_plane_restraint=10.0, x_range=3.6443148688046643, 
        y_range=1.8221574344023321, max_range=7.2886297376093285, 
        pixelsize=2.7440000000000002, iteration_count=5)], 10)
        
        >>> low_res = (True, (180.0, 180.0), (30, 20))
        >>> medium_res = (True, (180.0, 180.0), (20, 10))
        >>> high_res = (True, (20.0, 10.0), (10, 5)) 
        >>> max_res = (True, (2.0, 2.0), (5, 2.5))
        >>> p = 1.2, True, low_res, medium_res, high_res, max_res, 18
        >>> s.define_series_of_search_steps(p[0], p[1], p[2], p[3], p[4], p[5], p[6]) #doctest: +NORMALIZE_WHITESPACE
        ([series_info(bin_factor=7, resolution_aim='low',
        azimuthal_restraint=180.0, out_of_plane_restraint=180.0,
        x_range=3.5714285714285712, y_range=2.3809523809523809,
        max_range=3.5714285714285712, pixelsize=8.4000000000000004,
        iteration_count=5), series_info(bin_factor=3, resolution_aim='medium',
        azimuthal_restraint=180.0, out_of_plane_restraint=180.0,
        x_range=5.5555555555555562, y_range=2.7777777777777781,
        max_range=8.3333333333333339, pixelsize=3.5999999999999996,
        iteration_count=5), series_info(bin_factor=2, resolution_aim='high',
        azimuthal_restraint=20.0, out_of_plane_restraint=10.0,
        x_range=4.166666666666667, y_range=2.0833333333333335, max_range=12.5,
        pixelsize=2.3999999999999999, iteration_count=4),
        series_info(bin_factor=1, resolution_aim='max', azimuthal_restraint=2.0,
        out_of_plane_restraint=2.0, x_range=4.166666666666667,
        y_range=2.0833333333333335, max_range=25.0, pixelsize=1.2,
        iteration_count=4)], 18)
        
        >>> low_res  = (True, (180.0, 180.0), (30, 20))
        >>> medium_res = (True,(180.0, 180.0), (20, 10))
        >>> high_res = (False, (20.0, 10.0), (10, 5))
        >>> max_res = (False, (2.0, 2.0), (5, 2.5))
        >>> p = 1.2, True, low_res, medium_res, high_res, max_res, 13
        >>> s.define_series_of_search_steps(p[0], p[1], p[2], p[3], p[4], p[5], p[6]) #doctest: +NORMALIZE_WHITESPACE
        ([series_info(bin_factor=7, resolution_aim='low',
        azimuthal_restraint=180.0, out_of_plane_restraint=180.0,
        x_range=3.5714285714285712, y_range=2.3809523809523809,
        max_range=3.5714285714285712, pixelsize=8.4000000000000004,
        iteration_count=7), series_info(bin_factor=3, resolution_aim='medium',
        azimuthal_restraint=180.0, out_of_plane_restraint=180.0,
        x_range=5.5555555555555562, y_range=2.7777777777777781,
        max_range=8.3333333333333339, pixelsize=3.5999999999999996,
        iteration_count=6)], 13)
        
        >>> low_res = (False, (180.0, 180.0), (30, 20))
        >>> medium_res = (False, (180.0, 180.0), (20, 10))
        >>> high_res = (False, (20.0, 10.0), (10, 5))
        >>> max_res = (True, (2.0, 2.0), (5, 2.5))
        >>> p = 1.2, True, low_res, medium_res, high_res, max_res, 7
        >>> s.define_series_of_search_steps(p[0], p[1], p[2], p[3], p[4], p[5], p[6]) #doctest: +NORMALIZE_WHITESPACE
        ([series_info(bin_factor=1, resolution_aim='max',
        azimuthal_restraint=2.0, out_of_plane_restraint=2.0,
        x_range=4.166666666666667, y_range=2.0833333333333335,
        max_range=4.166666666666667, pixelsize=1.2, iteration_count=7)], 7)
        
        >>> low_res = (False, (180.0, 180.0), (30, 20))
        >>> medium_res = (True, (180.0, 180.0), (20, 10))
        >>> high_res = (True, (10.0, 5.0), (10.0, 5.0))
        >>> max_res = (False, (2.0, 2.0), (5, 2.5))
        >>> p = 1.2, True, low_res, medium_res, high_res, max_res, 7
        >>> s.define_series_of_search_steps(p[0], p[1], p[2], p[3], p[4], p[5], p[6]) #doctest: +NORMALIZE_WHITESPACE
        ([series_info(bin_factor=3, resolution_aim='medium',
        azimuthal_restraint=180.0, out_of_plane_restraint=180.0,
        x_range=5.5555555555555562, y_range=2.7777777777777781,
        max_range=5.5555555555555562, pixelsize=3.5999999999999996,
        iteration_count=4), series_info(bin_factor=2, resolution_aim='high',
        azimuthal_restraint=10.0, out_of_plane_restraint=5.0,
        x_range=4.166666666666667, y_range=2.0833333333333335,
        max_range=8.3333333333333339, pixelsize=2.3999999999999999,
        iteration_count=3)], 7)
        
        >>> low_res = (True, (180.0, 180.0), (30, 20))
        >>> medium_res = (True, (180.0, 180.0), (20, 10))
        >>> high_res = (True, (20.0, 10.0), (10, 5))
        >>> max_res = (True, (2.0, 2.0), (5, 2.5))
        >>> p = 1.2, True, low_res, medium_res, high_res, max_res, 3
        >>> s.define_series_of_search_steps(p[0], p[1], p[2], p[3], p[4], p[5], p[6]) #doctest: +NORMALIZE_WHITESPACE
        ([series_info(bin_factor=7, resolution_aim='low',
        azimuthal_restraint=180.0, out_of_plane_restraint=180.0,
        x_range=3.5714285714285712, y_range=2.3809523809523809,
        max_range=3.5714285714285712, pixelsize=8.4000000000000004,
        iteration_count=1), series_info(bin_factor=3, resolution_aim='medium',
        azimuthal_restraint=180.0, out_of_plane_restraint=180.0,
        x_range=5.5555555555555562, y_range=2.7777777777777781,
        max_range=8.3333333333333339, pixelsize=3.5999999999999996,
        iteration_count=1), series_info(bin_factor=2, resolution_aim='high',
        azimuthal_restraint=20.0, out_of_plane_restraint=10.0,
        x_range=4.166666666666667, y_range=2.0833333333333335, max_range=12.5,
        pixelsize=2.3999999999999999, iteration_count=1),
        series_info(bin_factor=1, resolution_aim='max', azimuthal_restraint=2.0,
        out_of_plane_restraint=2.0, x_range=4.166666666666667,
        y_range=2.0833333333333335, max_range=25.0, pixelsize=1.2,
        iteration_count=1)], 4)
        
        >>> low_res = (False, (180.0, 180.0), (30, 20))
        >>> medium_res = (False, (180.0, 180.0), (20, 10))
        >>> high_res = (False, (10.0, 5.0), (10.0, 5.0))
        >>> max_res = (False, (2.0, 2.0), (5, 2.5))
        >>> p = 3.5, True, low_res, medium_res, high_res, max_res, 3
        >>> s.define_series_of_search_steps(p[0], p[1], p[2], p[3], p[4], p[5], p[6]) #doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
          File '/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/doctest.py', line 1254, in __run
            compileflags, 1) in test.globs
          File '<doctest segmentrefine3d_prj_algn.SegmentRefine3dAlign.define_series_of_search_steps[9]>', line 1, in
          <module>
            s.define_series_of_search_steps(1.2, True, False, False, False, False)
          File 'spring/segment3d/segmentrefine3d_prj_algn.py', line 975, in define_series_of_search_steps
            raise ValueError, error_msg
        ValueError: You have specified to assemble a refinement strategy without any resolution aim. Please, specify at
        least one resolution range you are targeting.
        >>> low_res = (True, (180.0, 180.0), (30, 20))
        >>> medium_res = (True, (180.0, 180.0), (20, 10))
        >>> high_res = (True, (180.0, 20.0), (10.0, 5.0))
        >>> max_res = (False, (2.0, 2.0), (5, 2.5))
        >>> p = 1.78, True, low_res, medium_res, high_res, max_res, 15
        >>> s.define_series_of_search_steps(p[0], p[1], p[2], p[3], p[4], p[5], p[6]) #doctest: +NORMALIZE_WHITESPACE
        ([series_info(bin_factor=4, resolution_aim='low', 
        azimuthal_restraint=180.0, out_of_plane_restraint=180.0, 
        x_range=4.213483146067416, y_range=2.8089887640449436, 
        max_range=4.213483146067416, pixelsize=7.1200000000000001, 
        iteration_count=5), series_info(bin_factor=2, 
        resolution_aim='medium', azimuthal_restraint=180.0, 
        out_of_plane_restraint=180.0, x_range=5.6179775280898872, 
        y_range=2.8089887640449436, max_range=8.4269662921348321, 
        pixelsize=3.5600000000000001, iteration_count=5), 
        series_info(bin_factor=1, resolution_aim='high', 
        azimuthal_restraint=180.0, out_of_plane_restraint=20.0, 
        x_range=5.6179775280898872, y_range=2.8089887640449436, 
        max_range=16.853932584269664, pixelsize=1.78, 
        iteration_count=5)], 15)
        """

        (low_resolution_aim, low_res_ang_range, (low_res_x_range, low_res_y_range)) = low_resolution 
        (medium_resolution_aim, medium_res_ang_range, (medium_res_x_range, medium_res_y_range)) = medium_resolution
        (high_resolution_aim, high_res_ang_range, (high_res_x_range, high_res_y_range)) = high_resolution
        (max_resolution_aim, max_res_ang_range, (max_res_x_range, max_res_y_range)) = max_resolution
        
        aims = {'low': low_resolution_aim, 
                'medium': medium_resolution_aim, 
                'high': high_resolution_aim, 
                'max': max_resolution_aim}

        azimuthal_series = {'low': low_res_ang_range[0], 
                            'medium': medium_res_ang_range[0], 
                            'high': high_res_ang_range[0],
                            'max': max_res_ang_range[0]}
        
        out_of_plane_series = {'low': low_res_ang_range[1], 
                               'medium': medium_res_ang_range[1], 
                               'high': high_res_ang_range[1],
                               'max': max_res_ang_range[1]}
        
        x_ranges_A = {'low': low_res_x_range, 
                      'medium': medium_res_x_range, 
                      'high': high_res_x_range, 
                      'max': max_res_x_range}

        y_ranges_A = {'low': low_res_y_range, 
                      'medium': medium_res_y_range, 
                      'high': high_res_y_range, 
                      'max': max_res_y_range}
        
        selected_binfactors = self.determine_res_ranges_and_binfactors_to_be_used(pixelsize, aims)
        
        total_iteration_count = max(total_iteration_count, len(selected_binfactors))
            
        if len(selected_binfactors) == 0 and refine_strategy:
            error_msg = 'You have specified to assemble a refinement strategy without any resolution aim. Please, ' +\
            'specify at least one resolution range you are targeting.'
            
            raise ValueError, error_msg
        
        
        max_range_A = max([max(x_ranges_A[each_aim], y_ranges_A[each_aim]) for each_aim in selected_binfactors.keys()])

        selected_counts = self.get_and_distribute_total_iteration_count(total_iteration_count, aims)

        bin_info = self.make_series_info_named_tuple()
        info_series = []
        for each_aim in ['low', 'medium', 'high', 'max']:
            if aims[each_aim]:
                each_pixelsize = (selected_binfactors[each_aim] * pixelsize)
                info_series.append(bin_info(selected_binfactors[each_aim],
                                            each_aim, 
                                            azimuthal_series[each_aim],
                                            out_of_plane_series[each_aim],
                                            x_ranges_A[each_aim] / each_pixelsize,
                                            y_ranges_A[each_aim] / each_pixelsize,
                                            max_range_A / each_pixelsize,
                                            each_pixelsize,
                                            selected_counts[each_aim]
                                            ))
        
        return info_series, total_iteration_count
        
        
class SegmentRefine3dProjection(SegmentRefine3dPreparationStrategy):
    def generate_thetas_evenly_dependent_on_cos_of_out_of_plane_angle(self, thetas):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.generate_thetas_evenly_dependent_on_cos_of_out_of_plane_angle(\
np.arange(78, 106, 4, dtype=float)) 
        array([  78.        ,   80.20802669,   83.08024783,   90.        ,
                 96.91975217,   99.79197331,  102.        ])
        >>> s.generate_thetas_evenly_dependent_on_cos_of_out_of_plane_angle(\
np.arange(78, 106, 2, dtype=float)) 
        array([  78.        ,   79.0488977 ,   80.20802669,   81.52248781,
                 83.08024783,   85.10848412,   90.        ,   95.28021705,
                 97.47000184,   99.15209489,  100.5716871 ,  101.82371539,
                102.95685186,  104.        ])
        """
        thetas_gt_90 = thetas[thetas > 90.0] - 90.0
        cos_even_space = np.linspace(np.cos(np.deg2rad(np.max(thetas_gt_90))), 1, len(thetas_gt_90) + 1 )
        even_thetas_gt_90 = np.rad2deg(np.arccos(cos_even_space)) 
        
        thetas_le_90 = thetas[thetas <= 90.0] - 90.0
        cos_even_space = np.linspace(np.cos(np.deg2rad(np.min(thetas_le_90))), 1, len(thetas_le_90))
        even_thetas_le_90 = np.rad2deg(np.arccos(cos_even_space)) 

        first = even_thetas_gt_90 
        second = -even_thetas_le_90
        unique_thetas = np.sort(np.unique(np.append(first, second))) + 90.0
        
        assert len(thetas) == len(unique_thetas)
        
        return unique_thetas
    
                                     
    def generate_phis_evenly_across_asymmetric_unit_and_distribute_over_360(self, helical_rotation, azimuth_view_count):
        """
        * Function contributed by Ambroise Desfosses (May 2012)
        
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.generate_phis_evenly_across_asymmetric_unit_and_distribute_over_360(22.04, 6)
        array([   0.        ,   25.71333333,   51.42666667,   77.14      ,
                102.85333333,  128.56666667])
        >>> s.generate_phis_evenly_across_asymmetric_unit_and_distribute_over_360(-22.04, 6)
        array([   0.        ,   25.71333333,   51.42666667,   77.14      ,
                102.85333333,  128.56666667])
        """
        views_asym_unit = np.arange(azimuth_view_count) * abs(helical_rotation) / azimuth_view_count
        multiples_rot = abs(helical_rotation) * np.arange(int(360.0 / abs(helical_rotation) + 0.5))
        all_multiples_rot = multiples_rot.tolist() * views_asym_unit.size
        phis = [each_view + all_multiples_rot[each_index] for each_index, each_view in enumerate(views_asym_unit)]
        phis.sort()
        
        return np.array(phis)
    
            
    def generate_Euler_angles_for_projection(self, azimuthal_count, out_of_plane_range, out_of_plane_count,
    helical_rotation):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.generate_Euler_angles_for_projection(4, [0, 0], 0, 22.04) #doctest: +NORMALIZE_WHITESPACE
        [[0.0, 90.0, 270.0, 0.0, 0.0], [27.549999999999997, 90.0, 270.0, 0.0,
        0.0], [55.099999999999994, 90.0, 270.0, 0.0, 0.0], [82.65,
        90.0, 270.0, 0.0, 0.0]]
        
        >>> s.generate_Euler_angles_for_projection(4, [-8, 8], 3, 22.04) #doctest: +NORMALIZE_WHITESPACE
        [[0.0, 82.0, 270.0, 0.0, 0.0], [27.549999999999997, 82.0, 270.0, 0.0, 0.0], 
        [55.099999999999994, 82.0, 270.0, 0.0, 0.0], [82.65, 82.0, 270.0, 0.0, 0.0], 
        [0.0, 90.0, 270.0, 0.0, 0.0], [27.549999999999997, 90.0, 270.0, 0.0, 0.0], 
        [55.099999999999994, 90.0, 270.0, 0.0, 0.0], [82.65, 90.0, 270.0, 0.0, 0.0], 
        [0.0, 98.0, 270.0, 0.0, 0.0], [27.549999999999997, 98.0, 270.0, 0.0, 0.0], 
        [55.099999999999994, 98.0, 270.0, 0.0, 0.0], [82.65, 98.0, 270.0, 0.0, 0.0]]

        >>> s.generate_Euler_angles_for_projection(2, [-8, 8], 3, 22.04) #doctest: +NORMALIZE_WHITESPACE
        [[0.0, 82.0, 270.0, 0.0, 0.0], 
        [33.06, 82.0, 270.0, 0.0, 0.0], 
        [0.0, 90.0, 270.0, 0.0, 0.0], 
        [33.06, 90.0, 270.0, 0.0, 0.0], 
        [0.0, 98.0, 270.0, 0.0, 0.0], 
        [33.06, 98.0, 270.0, 0.0, 0.0]]
        
        >>> s.generate_Euler_angles_for_projection(4, [-8, -8], 0, 22.04) #doctest: +NORMALIZE_WHITESPACE
        [[0.0, 82.0, 270.0, 0.0, 0.0], [27.549999999999997, 82.0, 270.0, 0.0,
        0.0], [55.099999999999994, 82.0, 270.0, 0.0, 0.0], [82.65,
        82.0, 270.0, 0.0, 0.0]]
        
        >>> s.generate_Euler_angles_for_projection(4, [0, 0], 0, 0) #doctest: +NORMALIZE_WHITESPACE 
        [[0.0, 90.0, 270.0, 0.0, 0.0], [90.0, 90.0, 270.0, 0.0, 0.0], [180.0,
        90.0, 270.0, 0.0, 0.0], [270.0, 90.0, 270.0, 0.0, 0.0]]
        
        >>> s.generate_Euler_angles_for_projection(4, [-12, 12], 1, 58) #doctest: +NORMALIZE_WHITESPACE 
        [[0.0, 90.0, 270.0, 0.0, 0.0], [72.0, 90.0, 270.0, 0.0, 0.0], 
        [145.0, 90.0, 270.0, 0.0, 0.0], [217.0, 90.0, 270.0, 0.0, 0.0]]
        """
        if out_of_plane_range[0] == 0 and out_of_plane_range[1] == 0:
            out_of_plane_count = 1
        if out_of_plane_range[0] == out_of_plane_range[1] and out_of_plane_count == 0:
            out_of_plane_count = 1
        if out_of_plane_count == 0:
            out_of_plane_count = 1
            
        if out_of_plane_count == 1:
            out_of_plane_range = 2 * [float(np.mean(out_of_plane_range))]

        theta_angles = 90.0 + np.linspace(min(out_of_plane_range), max(out_of_plane_range), out_of_plane_count)
#         if min(out_of_plane_range) != max(out_of_plane_range):
#             theta_angles = self.generate_thetas_evenly_dependent_on_cos_of_out_of_plane_angle(theta_angles)
            
        if helical_rotation != 0:
            phi_angles = self.generate_phis_evenly_across_asymmetric_unit_and_distribute_over_360(helical_rotation,
            azimuthal_count)
        else:
            phi_angles = np.linspace(0.0, 360.0, azimuthal_count, endpoint=False)
            
        shifts = 0.0
        psi = 270.0
        parameter_list = []
        for each_theta in theta_angles:
            for each_phi in phi_angles:
                parameter_list.append([float(each_phi), float(each_theta), psi, shifts, shifts])
                    
        return parameter_list
            
    
    def collect_prj_params_and_update_reference_info(self, updated_ref_files, each_reference, projection_stack,
    projection_parameters, fine_projection_stack, fine_projection_parameters, merged_prj_params, merged_fine_prj_params):
        projection_parameters = [[each_reference.model_id] + each_prj for each_prj in projection_parameters]
        merged_prj_params += projection_parameters
        if fine_projection_parameters is not None:
            fine_projection_parameters = [[each_reference.model_id] + each_prj for each_prj in fine_projection_parameters]
            merged_fine_prj_params += fine_projection_parameters
        else:
            merged_fine_prj_params = fine_projection_parameters
        each_reference = each_reference._replace(prj_stack=projection_stack)
        each_reference = each_reference._replace(fine_prj_stack=fine_projection_stack)
        updated_ref_files.append(each_reference)

        return updated_ref_files, merged_prj_params, merged_fine_prj_params


    def merge_prj_ref_stacks_into_single_prj_stack(self, updated_ref_files, prj_attr):
        prj = EMData()
        for each_reference in updated_ref_files:
            if each_reference.model_id == 0:
                merged_prj_stack = getattr(each_reference, prj_attr)
            elif each_reference.model_id > 0:
                if getattr(each_reference, prj_attr) is not None:
                    if getattr(each_reference, prj_attr).startswith(self.tempdir):
                        prj_img_count = EMUtil.get_image_count(getattr(each_reference, prj_attr))
                        for each_img in list(range(prj_img_count)):
                            prj.read_image(getattr(each_reference, prj_attr), each_img)
                            prj.append_image(merged_prj_stack)
                        
                        os.remove(getattr(each_reference, prj_attr))
        
        return merged_prj_stack


    def write_out_reference_and_get_prj_prefix_depending_on_number_of_models(self, reference_files, ref_cycle_id,
    each_iteration_number, each_reference, reference_volume):
        if len(reference_files) > 1:
            prj_prefix = 'projection_stack_mod{0:03}_'.format(each_reference.model_id)

            each_reference = self.write_out_reference_volume(each_reference, each_iteration_number, ref_cycle_id,
            reference_volume, each_reference.model_id)
        else:
            prj_prefix = 'projection_stack'
            each_reference = self.write_out_reference_volume(each_reference, each_iteration_number, ref_cycle_id, 
            reference_volume)

        return each_reference, prj_prefix


    def copy_image_stack_to_new_stack(self, projection_stack, local_projection_stack):
        img_count = EMUtil.get_image_count(projection_stack)
        img = EMData()
        for each_img in list(range(img_count)):
            img.read_image(projection_stack, each_img)
            img.write_image(local_projection_stack, each_img)
    

    def copy_image_stack_to_new_stack_shutil(self, projection_stack, local_projection_stack):
        shutil.copy(projection_stack, local_projection_stack)
        
        
    def generate_projection_stack(self, resolution_aim, cycle_number, reference_volume, pixelinfo,
    azimuthal_angle_count, out_of_plane_tilt_angle_count, projection_stack, helical_symmetry, rotational_sym):
    
        projection_parameters = self.generate_Euler_angles_for_projection(azimuthal_angle_count,
        self.out_of_plane_tilt_angle_range, out_of_plane_tilt_angle_count, helical_symmetry[1])
        
        prj_ids = list(range(len(projection_parameters)))
        
        projection_stack = \
        SegClassReconstruct().project_through_reference_using_parameters_and_log(projection_parameters,
        pixelinfo.alignment_size, prj_ids, projection_stack, reference_volume)
        
        self.filter_layer_lines_if_demanded(resolution_aim, projection_parameters, prj_ids, projection_stack,
        pixelinfo, helical_symmetry, rotational_sym)
        
        local_projection_stack = os.path.join(self.tempdir, projection_stack)
        
        self.copy_image_stack_to_new_stack(projection_stack, local_projection_stack)
        self.remove_intermediate_files_if_desired(projection_stack)

        return local_projection_stack, projection_parameters


    def project_through_reference_volume_in_helical_perspectives(self, resolution_aim, cycle_number,
    reference_volume_file, pixelinfo, helical_symmetry, rotational_sym, prj_prefix='projection_stack'):
        self.log.fcttolog()
        self.log.in_progress_log()
        
        reference_volume = EMData()
        reference_volume.read_image(reference_volume_file)
        
        projection_stack = '{0}{1:03}.hdf'.format(prj_prefix, cycle_number)
        if hasattr(self, 'comm'):
            projection_stack, projection_parameters = self.generate_projection_stack_mpi(resolution_aim, cycle_number,
            reference_volume, pixelinfo, self.azimuthal_angle_count, self.out_of_plane_tilt_angle_count,
            projection_stack, helical_symmetry, rotational_sym)
        else:
            projection_stack, projection_parameters = self.generate_projection_stack(resolution_aim, cycle_number,
            reference_volume, pixelinfo, self.azimuthal_angle_count, self.out_of_plane_tilt_angle_count,
            projection_stack, helical_symmetry, rotational_sym)
        
        fine_projection_stack = '{0}_fine{1:03}.hdf'.format(prj_prefix, cycle_number)
        if resolution_aim in ['high', 'max'] and hasattr(self, 'comm'):
            fine_projection_stack, fine_projection_parameters = self.generate_projection_stack_mpi(resolution_aim,
            cycle_number, reference_volume, pixelinfo, 5 * self.azimuthal_angle_count, 
            5 * self.out_of_plane_tilt_angle_count, fine_projection_stack, helical_symmetry, rotational_sym)
        elif resolution_aim in ['high', 'max'] and not hasattr(self, 'comm'):
            fine_projection_stack, fine_projection_parameters = self.generate_projection_stack(resolution_aim,
            cycle_number, reference_volume, pixelinfo, 5 * self.azimuthal_angle_count,
            5 * self.out_of_plane_tilt_angle_count, fine_projection_stack, helical_symmetry, rotational_sym)
        else:
            fine_projection_stack = None
            fine_projection_parameters = None
        
        return projection_stack, projection_parameters, fine_projection_stack, fine_projection_parameters
    

class SegmentRefine3dProjectionLayerLineFilter(SegmentRefine3dProjection):
    def convert_reciprocal_Angstrom_to_Fourier_pixel_position_in_power_spectrum(self, pixelsize, powersize,
    reciprocal_Angstrom):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.convert_reciprocal_Angstrom_to_Fourier_pixel_position_in_power_\
spectrum(2.0, 200, 0.25)
        100
        >>> s.convert_reciprocal_Angstrom_to_Fourier_pixel_position_in_power_\
spectrum(2.0, 200, 0.05)
        20
        """
        Fourier_pixel = int(round(reciprocal_Angstrom * powersize * pixelsize))
        
        return Fourier_pixel


    def convert_Fouier_pixel_to_reciprocal_Angstrom(self, pixelsize, powersize, Fourier_pixel):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.convert_Fouier_pixel_to_reciprocal_Angstrom(2.0, 200, 100)
        0.25
        >>> s.convert_Fouier_pixel_to_reciprocal_Angstrom(2.0, 200, 20)
        0.05
        """
        reciprocal_Angstrom = Fourier_pixel / float(powersize * pixelsize)
        
        return reciprocal_Angstrom
        

    def determine_Fourier_pixel_position_of_highest_resolution_layer_line(self, helical_symmetry, rotational_sym,
    helixwidth, pixelsize, powersize, tilt):
        min_layerline_bessel_pairs = \
        SegClassReconstruct().generate_layerline_bessel_pairs_from_rise_and_rotation(helical_symmetry, rotational_sym,
        helixwidth, pixelsize, 300.0, 2 * pixelsize, tilt)

        min_ll, min_bessel = zip(*min_layerline_bessel_pairs) 
        max_pixel = \
        self.convert_reciprocal_Angstrom_to_Fourier_pixel_position_in_power_spectrum(pixelsize, powersize,
        np.max(min_ll))
        
        return max_pixel
    

    def compute_corresponding_tilts_from_Fourier_pixel_series(self, no_tilt_pixel, tilted_series):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.compute_corresponding_tilts_from_Fourier_pixel_series(200, 201)
        5.7176796852519809
        """
        tilts = np.rad2deg(np.arccos(no_tilt_pixel / np.array(tilted_series, dtype=float)))
        
        return tilts
    

    def blur_ideal_power_spectrum_by_even_out_of_plane_variation(self, helical_symmetry, rotational_sym, helixwidth,
    pixelsize, powersize, each_unique_tilt, out_of_plane_blur, no_tilt_pixel):
        min_tilt = max(abs(each_unique_tilt) - out_of_plane_blur, 0)
        
        min_pixel = self.determine_Fourier_pixel_position_of_highest_resolution_layer_line(helical_symmetry,
        rotational_sym, helixwidth, pixelsize, powersize, min_tilt)
        
        max_tilt = abs(each_unique_tilt + out_of_plane_blur)
        
        max_pixel = self.determine_Fourier_pixel_position_of_highest_resolution_layer_line(helical_symmetry,
        rotational_sym, helixwidth, pixelsize, powersize, max_tilt)
        
        pixel_series = np.arange(min(min_pixel, max_pixel), max(min_pixel, max_pixel) + 1)
        tilts = self.compute_corresponding_tilts_from_Fourier_pixel_series(no_tilt_pixel, pixel_series)
        ideal_power_img = model_blank(powersize, powersize)
        for each_tilt in tilts:
            layerline_bessel_pairs =\
            SegClassReconstruct().generate_layerline_bessel_pairs_from_rise_and_rotation(helical_symmetry,
            rotational_sym, helixwidth, pixelsize, 300.0, 2 * pixelsize, each_tilt)
            
            tilt_power_img, linex_fine =\
            SegClassReconstruct().prepare_ideal_power_spectrum_from_layer_lines(layerline_bessel_pairs, helixwidth,
                powersize, pixelsize, binary=True)
            
            ideal_power_img += tilt_power_img
        ideal_power_img /= len(tilts)
        
        return ideal_power_img
    

    def generate_binary_layer_line_filter_for_different_out_of_plane_tilt_angles(self, tilts, helical_symmetry,
    rotational_sym, helixwidth, pixelsize, powersize, binary=True, out_of_plane_blur=None):
        ideal_power_imgs = []
        if out_of_plane_blur is not None:
            no_tilt_pixel = self.determine_Fourier_pixel_position_of_highest_resolution_layer_line(helical_symmetry,
            rotational_sym, helixwidth, pixelsize, powersize, 0.0)
        for each_unique_tilt in tilts:
            if out_of_plane_blur is not None:
                ideal_power_img = self.blur_ideal_power_spectrum_by_even_out_of_plane_variation(helical_symmetry,
                rotational_sym, helixwidth, pixelsize, powersize, each_unique_tilt, out_of_plane_blur, no_tilt_pixel)
                
                if binary is True:
                    ideal_power_img = binarize(ideal_power_img, 1e-14)
            else:
                layerline_bessel_pairs =\
                SegClassReconstruct().generate_layerline_bessel_pairs_from_rise_and_rotation(helical_symmetry,
                rotational_sym, helixwidth, pixelsize,300.0, 2 * pixelsize, each_unique_tilt)
                
                ideal_power_img, linex_fine =\
                SegClassReconstruct().prepare_ideal_power_spectrum_from_layer_lines(layerline_bessel_pairs, helixwidth,
                powersize, pixelsize, binary=True)
            ideal_power_imgs.append(ideal_power_img)
            
        return ideal_power_imgs
            

    def get_maximum_pixel_displacement_by_inplane_rotation_at_edge(self, inplane_blur, powersize, pixel_pos):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.get_maximum_pixel_displacement_by_inplane_rotation_at_edge(5, 200, 80)
        8
        >>> s.get_maximum_pixel_displacement_by_inplane_rotation_at_edge(-5, 200, 80)
        -9
        >>> s.get_maximum_pixel_displacement_by_inplane_rotation_at_edge(-0.3, 200, 80)
        0
        """
        rot_x, rot_y = Segment().rotate_coordinates_by_angle(0.0, pixel_pos, -inplane_blur)
        slope = np.tan(np.deg2rad(inplane_blur))
        intercept = rot_y - slope * rot_x
        y_height = slope * (- powersize / 2) + intercept
        y_difference = int(pixel_pos - y_height)
        
        return y_difference
    

    def generate_power_spectrum_average_by_inplane_angle_blurring(self, power_spectrum, inplane_blur, helical_symmetry,
    rotational_sym, helixwidth, pixelsize, binary=True):
        powersize = power_spectrum.get_ysize()
        
        pixel_pos = self.determine_Fourier_pixel_position_of_highest_resolution_layer_line(helical_symmetry,
        rotational_sym, helixwidth, pixelsize, powersize, 0.0)
        
        min_pix = self.get_maximum_pixel_displacement_by_inplane_rotation_at_edge(-inplane_blur, powersize, pixel_pos)
        max_pix = self.get_maximum_pixel_displacement_by_inplane_rotation_at_edge(inplane_blur, powersize, pixel_pos)
        
        inplane_angles = np.arange(min(min_pix, max_pix) - 1, max(min_pix, max_pix) + 2)
        
        blurred_power = model_blank(powersize, powersize, 1, 0)
        for each_angle in inplane_angles:
            rot_power = rot_shift2D(power_spectrum, float(each_angle))
            if binary is True:
                rot_power = binarize(rot_power, 0.1)
            blurred_power += rot_power
        
        blurred_power /= len(inplane_angles)
            
        return blurred_power
        
    
    def get_padsize_and_unique_tilts(self, alignment_size, projection_parameters):
        padsize = 4 * alignment_size
        theta = np.array(projection_parameters)[:,1]
        unique_tilts = np.unique(np.abs(theta - 90.0))
        
        return padsize, unique_tilts
    
        
    def compute_angular_blur_based_on_Crowther_criterion(self, ref_cycle_id, outer_diameter, pixelsize):
        if os.path.exists('refinement{0:03}.db'.format(ref_cycle_id)):
            temp_ref_db = self.copy_ref_db_to_tempdir(ref_cycle_id)
            ref_session = SpringDataBase().setup_sqlite_db(refine_base, temp_ref_db)
            last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
            ref_session.close()
            os.remove(temp_ref_db)
        else:
            last_cycle = None
        
        if last_cycle is not None:
            angular_blur = last_cycle.fsc_05 / np.deg2rad(outer_diameter / 2.0)
        else:
            angular_blur = pixelsize * 4.0 / np.deg2rad(outer_diameter / 2.0)
        
        return angular_blur
            
            
    def apply_inplane_blurring_to_set_of_power_spectra(self, ideal_power_imgs, helical_symmetry, rotational_sym,
    helixwidth, pixelsize, angular_blur, binary=True):
        if angular_blur is not None:
            blurred_powers = []
            power_size = ideal_power_imgs[0].get_ysize() 
            circle = model_circle(power_size /2, power_size, power_size)
            for each_power in ideal_power_imgs:
                
                blurred_power = self.generate_power_spectrum_average_by_inplane_angle_blurring(each_power, angular_blur
                / 5.0, helical_symmetry, rotational_sym, helixwidth, pixelsize)
                
                if binary:
#                    blurred_power = -1 * binarize(-1 * blurred_power, 0.0) + 1
                    blurred_power = binarize(blurred_power, 1e-14)
                blurred_power *= circle
                blurred_powers.append(blurred_power)
            
            ideal_power_imgs = blurred_powers

        return ideal_power_imgs


    def generate_binary_layer_line_filters_including_angular_blur(self, projection_parameters, pixelinfo,
    helical_symmetry, rotational_sym, angular_blur=None):
        padsize, unique_tilts = self.get_padsize_and_unique_tilts(pixelinfo.alignment_size, projection_parameters)
        
        ideal_power_imgs = self.generate_binary_layer_line_filter_for_different_out_of_plane_tilt_angles(unique_tilts,
        helical_symmetry, rotational_sym, self.helixwidth, pixelinfo.pixelsize, padsize, binary=True,
        out_of_plane_blur=angular_blur)
        
        ideal_power_imgs = self.apply_inplane_blurring_to_set_of_power_spectra(ideal_power_imgs, helical_symmetry,
        rotational_sym, self.helixwidth, pixelinfo.pixelsize, angular_blur)
            
        return unique_tilts, padsize, ideal_power_imgs


    def filter_projections_using_provided_layer_line_filters(self, projection_parameters, prj_ids, projection_stack,
    unique_tilts, padsize, ideal_power_imgs, pixelinfo):
        projection = EMData()
        
        rectangular_mask = SegmentExam().make_smooth_rectangular_mask(pixelinfo.helixwidthpix, pixelinfo.helix_heightpix,
        pixelinfo.alignment_size)
        
        filter_loginfo = []
        for each_local_prj_id, each_parameter in enumerate(projection_parameters):
            each_theta = each_parameter[1]
            each_total_prj_id = prj_ids[each_local_prj_id]
            tilt_index = np.where(unique_tilts == abs(each_theta - 90.0))
            projection.read_image(projection_stack, each_local_prj_id)
            
            projection = SegClassReconstruct().filter_image_by_fourier_filter_while_padding(projection,
            pixelinfo.alignment_size, padsize, ideal_power_imgs[tilt_index[0][0]])
            
            projection *= rectangular_mask
            projection.write_image(projection_stack, each_local_prj_id)
            filter_loginfo += [[each_total_prj_id, each_local_prj_id, each_theta - 90]]
        
        header = ['stack_id',  'local_id', 'out-of-plane tilt']
        msg = tabulate(filter_loginfo, header)
        self.log.tlog('The following projection images were filtered with a layer-line based' +
        'filter:\n{0}'.format(msg))


    def filter_layer_lines_if_demanded(self, resolution_aim, projection_parameters, prj_ids, projection_stack,
    pixelinfo, helical_symmetry, rotational_sym):
        if self.layer_line_filter:# and resolution_aim in ['high', 'max']:
            
            unique_tilts, padsize, ideal_power_imgs = \
            self.generate_binary_layer_line_filters_including_angular_blur(projection_parameters, pixelinfo,
            helical_symmetry, rotational_sym)
            
            self.filter_projections_using_provided_layer_line_filters(projection_parameters, prj_ids, projection_stack,
            unique_tilts, padsize, ideal_power_imgs, pixelinfo)
            
