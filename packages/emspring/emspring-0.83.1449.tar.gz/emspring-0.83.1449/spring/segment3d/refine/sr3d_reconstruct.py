# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import EMData, Util, EMNumPy
from collections import namedtuple
from filter import filt_table
from fundamentals import fft
import gc
from morphology import erosion
import os
import shutil
from spring.csinfrastr.csdatabase import SpringDataBase, refine_base, base, RefinementCycleTable, \
    RefinementCycleSegmentTable, RefinementCycleSegmentSubunitTable, SubunitTable, SegmentTable, HelixTable
from spring.csinfrastr.csproductivity import DiskSpace, Support, OpenMpi
from spring.micprgs.scansplit import Micrograph
from spring.segment2d.segment import Segment
from spring.segment2d.segmentalign2d import SegmentAlign2d
from spring.segment2d.segmentexam import SegmentExam
from spring.segment3d.refine.sr3d_select import SegmentRefine3dParameterAveraging
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from statistics import fsc
from utilities import model_circle, model_blank

from matplotlib import cm
import scipy.interpolate
import scipy.ndimage
from sqlalchemy.sql.expression import desc
from tabulate import tabulate

import matplotlib.pyplot as plt
import numpy as np


class SegmentRefine3dCylindrical(SegmentRefine3dParameterAveraging):
    def assemble_image_plane(self, bessel_line):
        bessel_length = np.shape(bessel_line)[0]
        polar_img_plane = np.zeros((bessel_length, bessel_length))
        
        for each_y_line in list(range(bessel_length)):
            polar_img_plane[:,each_y_line]=bessel_line
        
        img_plane = self.reproject_polar_into_image(polar_img_plane)
        
        return img_plane
    
        
    def build_3d_layer_line_mask_half_as_wide_as_high(self, image_slice):
        row_count, col_count = np.shape(image_slice)
        vol = np.zeros((row_count, col_count / 2, col_count / 2))
        
        for each_row in list(range(row_count)):
            bessel_line = image_slice[each_row][-col_count/2:]
            image_plane = self.assemble_image_plane(bessel_line)
            vol[each_row]=image_plane
        
        return vol
        
    
    def index_coords(self, data, origin=None):
        """Creates x & y coords for the indicies in a numpy array 'data'.
        'origin' defaults to the center of the image. Specify origin=(0,0)
        to set the origin to the lower left corner of the image."""
        ny, nx = data.shape[:2]
        if origin is None:
            origin_x, origin_y = nx // 2, ny // 2
        else:
            origin_x, origin_y = origin
        x, y = np.meshgrid(np.arange(nx), np.arange(ny))
        x -= origin_x
        y -= origin_y
        return x, y
    
    def cart2polar(self, x, y):
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        return r, theta
    
    def polar2cart(self, r, theta):
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return x, y
    
    
    def map_new_coordinates(self, data, ny, nx, xi, yi):
        zi = np.array([scipy.ndimage.map_coordinates(data, np.array([xi, yi]), order=3)])
        output = zi.reshape((nx, ny))
        return output

    def reproject_image_into_polar(self, data, origin=None):
        """Reprojects a 3D numpy array ('data') into a polar coordinate system.
        'origin' is a tuple of (x0, y0) and defaults to the center of the image."""
        ny, nx = data.shape[:2]
        if origin is None:
            origin = (nx//2, ny//2)
    
        # Determine that the min and max r and theta coords will be...
        x, y = self.index_coords(data, origin=origin)
        r, theta = self.cart2polar(x, y)
    
        # Make a regular (in polar space) grid based on the min and max r & theta
        r_i = np.linspace(r.min(), r.max(), nx)
        theta_i = np.linspace(theta.min(), theta.max(), ny)
        theta_grid, r_grid = np.meshgrid(theta_i, r_i)
    
        # Project the r and theta grid back into pixel coordinates
        xi, yi = self.polar2cart(r_grid, theta_grid)
        xi += origin[0] # We need to shift the origin back to 
        yi += origin[1] # back to the lower-left corner...
        xi, yi = xi.flatten(), yi.flatten()
#        coords = np.vstack((xi, yi)) # (map_coordinates requires a 2xn array)
    
        # Reproject each band individually and the restack
        # (uses less memory than reprojection the 3-dimensional array in one step)
        output = self.map_new_coordinates(data, ny, nx, xi, yi)
        
        return output, r_i, theta_i
    
    def reproject_polar_into_image(self, data, origin=None):
        ny, nx = data.shape[:2]
        if origin is None:
            origin = (nx//2, ny//2)
    
        x, y = self.index_coords(data, origin)
        new_r = np.sqrt(x**2 + y**2) 
        new_t = np.arctan2(x, y)
    
        radii = np.linspace(new_r.min(), new_r.max(), nx)
        thetas = np.linspace(new_t.min(), new_t.max(), ny)
    
        ir = scipy.interpolate.interp1d(radii, np.arange(len(radii)), bounds_error=False)
        it = scipy.interpolate.interp1d(thetas, np.arange(len(thetas)))
    
        new_ir = ir(new_r.ravel())
        new_it = it(new_t.ravel())
    
        output = self.map_new_coordinates(data, ny, nx, new_ir, new_it)
        
        return output
                                
    def reproject_volume_into_cylinder(self, data, origin=None):
        cyl_volume = np.zeros(data.shape)
        for each_index, each_zslice in enumerate(data):
            polar_zslice, r, theta = self.reproject_image_into_polar(each_zslice)
            cyl_volume[each_index]=polar_zslice
            
        return cyl_volume, r, theta
        
        
    def plot_polar_image(self, data, origin=None):
        """Plots an image reprojected into polar coordinates with the origin
        at 'origin' (a tuple of (x0, y0), defaults to the center of the image)"""
        polar_grid, r, theta = self.reproject_image_into_polar(data, origin)
        plt.figure()
        # extent is import to display grid with correct scale
        
        plt.imshow(polar_grid, cmap=cm.gray, interpolation='nearest', extent=(theta.min(), theta.max(), r.max(),
        r.min()))
        
        plt.axis('auto')
        plt.ylim(plt.ylim()[::-1])
        plt.xlabel('Theta Coordinate (radians)')
        plt.ylabel('R Coordinate (pixels)')
        plt.title('Image in Polar Coordinates')
        

    def filter_volume_by_fourier_filter_while_padding(self, vol, volsize, padsize_along_z, layer_mask):
        padded_vol = Util.pad(vol, padsize_along_z, padsize_along_z, padsize_along_z, 0, 0, 0, 'average')
        filtered_vol = padded_vol.filter_by_image(layer_mask)
        filtered_vol = Util.window(filtered_vol, volsize, volsize, volsize, 0, 0, 0)
        return filtered_vol
        

    def generate_and_apply_layerline_filter(self, vol, pixelsize, helical_symmetry, rotational_sym, helixwidth):
        volsize = vol.get_xsize()
        padsize_along_z = volsize * 2
        
        layerline_bessel_pairs = \
        SegClassReconstruct().generate_layerline_bessel_pairs_from_rise_and_rotation(helical_symmetry, rotational_sym,
        helixwidth, pixelsize, 300.0, 2 * pixelsize)
        
        ideal_power_img, linex_fine = \
        SegClassReconstruct().prepare_ideal_power_spectrum_from_layer_lines(layerline_bessel_pairs, helixwidth,
        ((padsize_along_z, 2 * padsize_along_z)), pixelsize, binary=True)
        
        power_vol_np = self.build_3d_layer_line_mask_half_as_wide_as_high(np.copy(EMNumPy.em2numpy(ideal_power_img)))
        layer_filter = EMNumPy.numpy2em(np.copy(power_vol_np)) 
        filtered_vol = self.filter_volume_by_fourier_filter_while_padding(vol, volsize, padsize_along_z, layer_filter)
        
        return filtered_vol, layer_filter
    

class SegmentRefine3dReconstruction(SegmentRefine3dCylindrical):

    def enter_asymmetric_unit_parameters_in_database(self, ref_session, symmetry_alignment_parameters, pixelsize):
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
        
        for each_stack_id, each_phi, each_theta, each_psi, each_xshift, each_yshift, each_mirror, each_ref_id in \
        symmetry_alignment_parameters:
            
            each_subunit = RefinementCycleSegmentSubunitTable()
            each_subunit.stack_id = each_stack_id
            each_subunit.phi = each_phi
            each_subunit.theta = each_theta
            each_subunit.psi = each_psi
            each_subunit.shift_x_A = each_xshift * pixelsize
            each_subunit.shift_y_A = each_yshift * pixelsize
            each_subunit.ref_seg_id = each_ref_id
            each_subunit.ref_cycle_id = last_cycle.id

            each_subunit.refined_segments = ref_session.query(RefinementCycleSegmentTable).get(int(each_ref_id))
            
            ref_session.add(each_subunit)
            
        return ref_session, last_cycle
    
    
    def check_whether_adjacent_values_are_closer_to_cutoff_value(self, value, fsc_line, first_value_id):
        adjacent_vals = np.array([fsc_line[first_value_id], fsc_line[first_value_id - 1]])
        closest_id = np.argmin(np.abs(adjacent_vals - value))

        return first_value_id - closest_id


    def get_resolution_closest_to_value(self, value, fsc_line, resolution):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> fsc_line = (np.cos(np.linspace(0, 2 * np.pi, 30)) + 1) / 2
        >>> res = SegmentExam().make_oneoverres(fsc_line, 3.489)
        >>> s = SegmentRefine3d()
        >>> s.get_resolution_closest_to_value(0.5, fsc_line, res)
        28.908857142857148
        >>> s.get_resolution_closest_to_value(0.5, np.ones(30), res)
        6.9779999999999998
        >>> fsc_line = np.append(-1 /  np.arange(10.0) + 1, [0.4, 0.2, 0.])
        >>> res = SegmentExam().make_oneoverres(fsc_line, 3.489)
        >>> s.get_resolution_closest_to_value(0.5, fsc_line, res)
        8.3736000000000015
        >>> fsc_line = [1.0, 0.9640229344367981, 0.9330880641937256, 0.6869177222251892, 0.5881993174552917, 0.6750558614730835, 0.5739578008651733, 0.2881937623023987, 0.3714075982570648, 0.5021396279335022, 0.13414639234542847, 0.2937462329864502]
        >>> res = SegmentExam().make_oneoverres(fsc_line, 3.489)
        >>> s.get_resolution_closest_to_value(0.143, fsc_line, res)
        6.9779999999999998
        """
        fsc_line_arr = np.array(fsc_line)
        first_value = np.where(fsc_line_arr < value)[0]
        
        if len(first_value) >= 5:
            if first_value[0] > 5:
                closest_id = self.check_whether_adjacent_values_are_closer_to_cutoff_value(value, fsc_line, first_value[0])
                determined_res = 1 / resolution[closest_id]
            else:
                id = 0
                while first_value[id] <= 5:
                    id += 1
                closest_id = self.check_whether_adjacent_values_are_closer_to_cutoff_value(value, fsc_line, first_value[id])
                determined_res = 1 / resolution[closest_id]
        else:
            determined_res = 1 / max(resolution)
        
        return determined_res
    
    
    def enter_fsc_values_in_database(self, ref_session, fsc_line, amp_cc, variance, mean_error, pixelsize):
        resolution = SegmentExam().make_oneoverres(fsc_line, pixelsize)
        
        last_cycle = ref_session.query(RefinementCycleTable).order_by(desc(RefinementCycleTable.id)).first()
        last_cycle.fsc_0143 = self.get_resolution_closest_to_value(0.143, fsc_line, resolution)
        last_cycle.fsc_05 = self.get_resolution_closest_to_value(0.5, fsc_line, resolution)
        last_cycle.fsc = fsc_line
        last_cycle.fsc_split = False
        last_cycle.amp_cc_line = amp_cc
        last_cycle.helical_ccc_error = mean_error.helical_ccc_error
        last_cycle.mean_helical_ccc = mean_error.mean_helical_ccc
        
        quarter, half, three_quarter, full = \
        SegClassReconstruct().get_quarter_half_3quarter_nyquist_average_from_amp_correlation(amp_cc)

        last_cycle.amp_corr_quarter_nyquist = quarter
        last_cycle.amp_corr_half_nyquist = half
        last_cycle.amp_corr_3quarter_nyquist = three_quarter
        last_cycle.amp_correlation = full
        last_cycle.variance = variance
        
        ref_session.merge(last_cycle)
        
        return ref_session
    
    
    def update_persistence_length_in_spring_db(self):
        temp_db = self.copy_spring_db_to_tempdir()
        session = SpringDataBase().setup_sqlite_db(base, temp_db)
        
        helices = session.query(HelixTable).all()
        for each_helix in helices:
            segments = session.query(SegmentTable).filter(SegmentTable.helix_id == each_helix.id).all()
        
            coord_x = np.array([each_segment.x_coordinate_A for each_segment in segments]) 
            coord_y = np.array([each_segment.y_coordinate_A for each_segment in segments]) 

            pers_length = Segment().compute_persistence_length_m_from_coordinates_A(coord_x, coord_y)
        
            each_helix.avg_curvature = pers_length
            session.merge(each_helix)
        
            for each_segment in segments:
                each_segment.curvature = pers_length
                each_segment.lavg_curvature = pers_length
                session.merge(each_segment)
            
        session.commit()
        
        session.close()
        shutil.copy(temp_db, 'spring.db')
        os.remove(temp_db)


    def update_segment_subunits_database_with_final_refinement_parameters(self, ref_session, last_cycle, is_last_cycle):
        temp_db = self.copy_spring_db_to_tempdir()
        session = SpringDataBase().setup_sqlite_db(base, temp_db)
        
        refined_subunits = ref_session.query(RefinementCycleSegmentSubunitTable).\
        filter(RefinementCycleSegmentSubunitTable.ref_cycle_id == last_cycle.id).all()
        
        session.query(SubunitTable).delete()
                
        for each_refined_subunit in refined_subunits:
            each_subunit = SubunitTable()
            each_segment = session.query(SegmentTable).get(each_refined_subunit.stack_id + 1)
            each_subunit.ref_cycle_id = last_cycle.id 
            each_subunit.x_coordinate_A = each_segment.picked_x_coordinate_A + each_refined_subunit.shift_x_A 
            each_subunit.y_coordinate_A = each_segment.picked_y_coordinate_A + each_refined_subunit.shift_y_A 
            each_subunit.psi = each_refined_subunit.psi
            each_subunit.theta = each_refined_subunit.theta
            each_subunit.phi = each_refined_subunit.phi
            each_subunit.segments = each_segment
                
            session.add(each_subunit)
        
        session.commit()
        
        ref_segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).all()
        for each_ref_segment in ref_segments:
            each_segment = session.query(SegmentTable).get(each_ref_segment.stack_id + 1)
            each_segment.x_coordinate_A = each_segment.picked_x_coordinate_A + each_ref_segment.shift_x_A
            each_segment.y_coordinate_A = each_segment.picked_y_coordinate_A + each_ref_segment.shift_y_A
            each_segment.psi = each_ref_segment.psi
            each_segment.theta = each_ref_segment.theta
            each_segment.phi = each_ref_segment.phi
            
            if self.classes_selection and self.class_type == 'class_model_id' and not is_last_cycle:
                pass
            else:
                each_segment.class_model_id = each_ref_segment.model_id
             
            session.merge(each_segment)
         
        session.commit()
        
        session.close()
        shutil.copy(temp_db, 'spring.db')
        os.remove(temp_db)


    def enter_additional_ref_parameters_in_database(self, ref_cycle_id, symmetry_alignment_parameters, fsc_line,
    amp_cc, variance, helical_error, pixelsize, each_reference, is_last_cycle):
        
        if self.unbending:
            symmetry_views_count = self.get_symmetry_views_count_from_stepsize(each_reference.helical_symmetry,
            self.stepsize)

            symmetry_alignment_parameters = []
            
            alignment_parameters = self.prepare_refined_alignment_parameters_from_database(ref_cycle_id, pixelsize,
            False, [each_reference])
            
            sym_transformations = SegClassReconstruct().get_symmetry_transformations(each_reference.point_symmetry)
            for each_alignment_parameter in alignment_parameters[0]:
                
                sym_alignment_parameters, inplane_angle = \
                SegClassReconstruct().compute_helical_symmetry_related_views(each_alignment_parameter,
                each_reference.helical_symmetry, pixelsize, symmetry_views_count)
                
                for (each_stack_id, each_phi, each_theta, each_psi, each_x, each_y, each_mirror, each_ref_id) in \
                sym_alignment_parameters:
                    
                    for each_sym_transform in sym_transformations:
                        trans, trans_phi, trans_theta, trans_psi, trans_x, trans_y = \
                        SegClassReconstruct().get_Euler_angles_after_transformation(each_phi, each_theta, each_psi,
                        each_x, each_y, each_sym_transform)
                        
                        symmetry_alignment_parameters.append(np.array([each_stack_id, trans_phi, trans_theta, trans_psi,
                        trans_x, trans_y, each_mirror, each_ref_id], dtype=float))
                        
            symmetry_alignment_parameters = np.vstack(symmetry_alignment_parameters)
            
        temp_ref_db = self.copy_ref_db_to_tempdir(ref_cycle_id)
        ref_session = SpringDataBase().setup_sqlite_db(refine_base, temp_ref_db)
        
        ref_session, last_cycle = self.enter_asymmetric_unit_parameters_in_database(ref_session,
        symmetry_alignment_parameters, pixelsize)
        
        ref_session = self.enter_fsc_values_in_database(ref_session, fsc_line, amp_cc, variance, helical_error, pixelsize)
        ref_session.commit()
        
        if each_reference.model_id == 0:
            self.update_segment_subunits_database_with_final_refinement_parameters(ref_session, last_cycle,
            is_last_cycle)
        
        ref_session.close()
        shutil.copy(temp_ref_db, 'refinement{0:03}.db'.format(ref_cycle_id))
        os.remove(temp_ref_db)

    
    def generate_file_name_with_apix(self, each_iteration_number, outfile_prefix, pixelsize):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> SegmentRefine3d().generate_file_name_with_apix(3, 'test_rec.hdf', 4.55)
        'test_rec_455apix_003.hdf'
        """
        str_pixelsize = ''.join([each_part[:3] for each_part in str(pixelsize).split('.')])
        
        latest_reconstruction = '{prefix}_{apix}apix_{iter:03}{ext}'.format(prefix=os.path.splitext(outfile_prefix)[0],
        apix=str_pixelsize, iter=each_iteration_number, ext=os.path.splitext(outfile_prefix)[-1])
        
        return latest_reconstruction
    

    def write_out_fsc_line(self, fsc_lines, pixelsize, fsc_prefix, each_iteration):
        fsc_name = self.generate_file_name_with_apix(each_iteration, fsc_prefix, pixelsize)
        
        fsc_file = open(fsc_name, 'w')
        resolution = SegmentExam().make_oneoverres(fsc_lines[0], pixelsize)
        
        msg = tabulate(zip(resolution.tolist(), fsc_lines.unmasked, fsc_lines.cylinder_masked,
        fsc_lines.structure_masked, fsc_lines.layer_line_filtered),
                       ['resolution (1/Angstrom)'] + list(fsc_lines._fields))

        fsc_file.write(msg)
#         
        fsc_file.close()
        
        return fsc_name
        
        
    def get_symmetry_views_count_from_stepsize(self, helical_symmetry, stepsize):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> SegmentRefine3d().get_symmetry_views_count_from_stepsize((1.408, 22.03), 70)
        50
        """
        helical_rise, helical_rotation = helical_symmetry
        if helical_rise != 0:
            symmetry_views_count = int(round(float(stepsize) / helical_rise))
        elif helical_rise == 0 and helical_rotation == 0:
            symmetry_views_count = 1
        elif helical_rotation == 0:
            symmetry_views_count = int(round(360.0 / helical_rotation))

        return symmetry_views_count


    def prepare_helical_reconstruction_using_Fourier_interpolation(self, large_input_stack, alignment_parameters,
    helical_symmetry, stepsize, pixelsize, reconstruction_size, rec_stack, point_symmetry):
    
        symmetry_views_count = self.get_symmetry_views_count_from_stepsize(helical_symmetry, stepsize)
        
        gc.collect()
        
        rec_volume, fftvol, weight = SegClassReconstruct().setup_reconstructor(reconstruction_size)
        
        rec_volume, symmetry_alignment_parameters, symmetry_rec_loginfo, Euler_angles_rec = \
        SegClassReconstruct().compute_and_write_symmetry_related_views(rec_volume, large_input_stack,
        alignment_parameters, helical_symmetry, pixelsize, symmetry_views_count, reconstruction_size, rec_stack,
        point_symmetry)
        
        return rec_volume, fftvol, weight, symmetry_alignment_parameters, symmetry_rec_loginfo, Euler_angles_rec
    
    
    def finish_Fourier_interpolation_reconstruction(self, r, fftvol, weight):
        vol = r.finish(True)
        
        return fftvol
    
        
class SegmentRefine3dVolume(SegmentRefine3dReconstruction):
    def compute_3dreconstruction_by_Fourier_interpolation(self, large_input_stack, pixelsize, helical_symmetry,
    stepsize, reconstruction_size, rec_stack, point_symmetry, alignment_parameters):
        r, fftvol, weight, symmetry_alignment_parameters, symmetry_rec_loginfo, Euler_angles_rec = \
        self.prepare_helical_reconstruction_using_Fourier_interpolation(large_input_stack, alignment_parameters,
        helical_symmetry, stepsize, pixelsize, reconstruction_size, rec_stack, point_symmetry)
        
        uncorrected_reconstruction = self.finish_Fourier_interpolation_reconstruction(r, fftvol, weight)

        return uncorrected_reconstruction, symmetry_alignment_parameters, symmetry_rec_loginfo, Euler_angles_rec
    
    
    def launch_3dreconstruction_by_SIRT(self, large_input_stack, pixelsize, helical_symmetry, stepsize,
    reconstruction_size, rec_stack, point_symmetry, alignment_parameters, mask3d, maxit=40, lam=1.0e-4, tol=0.0):
        
        xvol = EMData()
        xvol.set_size(reconstruction_size, reconstruction_size, reconstruction_size)
        xvol.to_zero()
        
        pxvol = xvol.copy()
    
        old_rnorm = 1.0e+20
        rec_string = []
        
        symmetry_views_count = self.get_symmetry_views_count_from_stepsize(helical_symmetry, stepsize)
        
        align_stack = self.get_alignment_stack_name(self.tmpdir)
        interrupted = False
        for each_iteration in list(range(maxit)):
            if (each_iteration == 0):
                first_vol = EMData()
                first_vol.set_size(reconstruction_size, reconstruction_size, reconstruction_size)
                first_vol.to_zero()
            
                first_vol, symmetry_alignment_parameters, symmetry_rec_loginfo = \
                SegClassReconstruct().compute_and_write_symmetry_related_views(first_vol, large_input_stack,
                alignment_parameters, helical_symmetry, pixelsize, symmetry_views_count, reconstruction_size,
                rec_stack, align_stack, point_symmetry, mode='BP RP')
                
                bnorm = np.sqrt(first_vol.cmp('dot', first_vol, {'mask':mask3d,'negative':0}))
                grad  = first_vol
            else:
                pxvol.to_zero() 
                
                pxvol = SegClassReconstruct().project_from_volume_and_backproject(symmetry_alignment_parameters,
                reconstruction_size, xvol, pxvol)
                
                grad  = first_vol - pxvol
    
            rnorm = np.sqrt(grad.cmp('dot', grad, {'mask':mask3d, 'negative':0}))
            rec_string += [[each_iteration, rnorm, rnorm/bnorm]]
            if each_iteration != 0 and rnorm < tol or rnorm > old_rnorm: 
                
                self.log.tlog('SIRT iterations interrupted at lambda: {0}, tolerance {1}.\n'.format(lam, tol) + \
                'Iteration:{0}, Rnorm:{1}, Old_Rnorm:{2}'.format(each_iteration, rnorm, old_rnorm))
                
                interrupted = True
                break
            old_rnorm = rnorm
            xvol = xvol + lam*grad
    
        if not interrupted:
            msg = tabulate(rec_string, ['iteration,' 'rnorm', 'rnorm:prev_rnorm ratio'])
            self.log.ilog('The SIRT alogorhithm has computed the following parameters per iteration:\n{0}'.format(msg))
        
        return  xvol, symmetry_alignment_parameters, symmetry_rec_loginfo, interrupted
    

    def compute_3dreconstruction_by_SIRT(self, large_input_stack, pixelsize, helical_symmetry, stepsize,
    reconstruction_size, rec_stack, point_symmetry, alignment_parameters, lam):
    
        interrupted = True
        iteration_count = 20
        mask3d = model_circle(reconstruction_size/2 - 2, reconstruction_size, reconstruction_size, reconstruction_size) 
        while interrupted:
            
            uncorrected_reconstruction, symmetry_alignment_parameters, symmetry_rec_loginfo, interrupted = \
            self.launch_3dreconstruction_by_SIRT(large_input_stack, pixelsize, helical_symmetry, stepsize,
            reconstruction_size, rec_stack, point_symmetry, alignment_parameters, mask3d, iteration_count, lam)
            
            if interrupted:
                lam = lam/2
            
        return  uncorrected_reconstruction, symmetry_alignment_parameters, symmetry_rec_loginfo, lam
        
    
    def determine_percent_amplitude_for_Wiener_filter_constant(self, ctf_correction_type, pixelsize):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.determine_percent_amplitude_for_Wiener_filter_constant('low', 1.2)
        0.0096806219999999998
        >>> [s.determine_percent_amplitude_for_Wiener_filter_constant('low', e_apix) for e_apix in range(1, 8, 2)]
        [0.0065348700000000016, 0.037992390000000001, 0.069449910000000017, 0.10090743000000001]
        >>> [s.determine_percent_amplitude_for_Wiener_filter_constant('high', e_apix) for e_apix in range(1, 8, 2)]
        [0.032674350000000005, 0.18996194999999999, 0.34724955000000007, 0.50453714999999999]
        >>> [s.determine_percent_amplitude_for_Wiener_filter_constant('medium', e_apix) for e_apix in range(1, 8, 2)]
        [0.016337175000000002, 0.094980974999999995, 0.17362477500000004, 0.25226857499999999]
        """
        amp_factor = {'high': 5, 
                      'medium': 2.5,
                      'low': 1}
        
        if pixelsize < 0.6:
            percent_amp = amp_factor[ctf_correction_type] * abs(np.polyval([0.01572876, -0.00919389], 0.6))
        else:
            percent_amp = amp_factor[ctf_correction_type] * abs(np.polyval([0.01572876, -0.00919389], pixelsize))

        return percent_amp
    

    def perform_ctf_correction_on_volume(self, ctf_correction_type, vol, avg_ctf_squared_file, pixelsize):
        avg_ctf_squared_volume = EMData()
        avg_ctf_squared_volume.read_image(avg_ctf_squared_file)
        
        stat = Micrograph().get_statistics_from_image(avg_ctf_squared_volume)
        percent_amp = self.determine_percent_amplitude_for_Wiener_filter_constant(ctf_correction_type, pixelsize)
        wiener_filter_constant = percent_amp * stat.max
        
        ctf_corrected_vol = fft( fft(vol) / (wiener_filter_constant + avg_ctf_squared_volume))
        self.log.ilog('Reconstruction was divided by 3D-CTF squared with Wiener filter constant of ' + \
        '{0} ({1:.3} % of maximum Fourier amplitude).'.format(wiener_filter_constant, percent_amp * 100))
        
        return  ctf_corrected_vol
    
        
    def perform_ctf_correction_and_volume_symmetrization(self, resolution_aim, uncorrected_reconstruction,
    ctf3d_avg_squared, pixelsize, each_reference):
        if self.ctf_correction:
            reconstruction = self.perform_ctf_correction_on_volume(self.ctf_correction_type, uncorrected_reconstruction,
            ctf3d_avg_squared, pixelsize)
            
        else:
            reconstruction = uncorrected_reconstruction
            
        if resolution_aim in ['low', 'medium']:
            reconstruction = self.generate_long_helix_volume(reconstruction, reconstruction.get_xsize(),
            reconstruction.get_zsize(), each_reference.helical_symmetry, pixelsize, each_reference.point_symmetry)

#             reconstruction = self.symmetrize_volume(reconstruction, pixelsize,
#             each_reference.helical_symmetry, each_reference.point_symmetry, self.helixwidth)
            
        return reconstruction
    
    
    def perform_volume_operations_ctf_and_symmetrization(self, resolution_aim, uncorrected_reconstruction,
    ctf3d_avg_squared, pixelsize, each_reference):
        reconstruction = self.perform_ctf_correction_and_volume_symmetrization(resolution_aim,
        uncorrected_reconstruction, ctf3d_avg_squared, pixelsize, each_reference)
        
        return reconstruction
    

class SegmentRefine3dFsc(SegmentRefine3dVolume):
    def if_no_selected_images_left_abort_refinement(self):
        msg = 'No reconstruction possible because no images left after selection. Turn off selection or ' + \
        'lower the thresholds in the non-orientation selection criteria and/or turn off orientation-based ' + \
        'selection criteria.'

        raise ValueError(msg)


    def make_fsc_line_named_tuple(self):
        fsc_named_tuple = namedtuple('fsc_curves', 'unmasked cylinder_masked structure_masked layer_line_filtered')
        
        return fsc_named_tuple
    
        
    def normalize_and_scale_volumes_including_mask_and_compute_fsc(self, first_rec, second_rec, mask=None):
        if mask is not None:
            mask_eroded = mask.copy()
            mask_eroded = Util.sub_img(mask_eroded, erosion(mask_eroded))
        else:
            mask_eroded=None

        stat_rec1 = Micrograph().get_statistics_from_image(first_rec, mask_eroded)
        stat_rec2 = Micrograph().get_statistics_from_image(second_rec, mask_eroded)
            
        if stat_rec1.sigma != 0:
            first_rec_norm = (first_rec - stat_rec1.avg) / stat_rec1.sigma
        else:
            first_rec_norm = first_rec.copy()

        if stat_rec2.sigma != 0:
            second_rec_norm = (second_rec - stat_rec2.avg) / stat_rec2.sigma
        else:
            second_rec_norm = second_rec.copy()

        if mask is not None:
            first_rec_norm = mask * first_rec_norm
            second_rec_norm = mask * second_rec_norm
        freq, fsc_line, n = fsc(first_rec_norm, second_rec_norm)
        
        return np.array(fsc_line)


    def build_smooth_mask_with_top_and_bottom_cut(self, reconstruction_size, percent=60):
        fsc_rec_mask = SegmentExam().make_smooth_rectangular_mask(
        percent / 100.0 * reconstruction_size, reconstruction_size, reconstruction_size)

        fsc_rec_np = np.copy(EMNumPy.em2numpy(fsc_rec_mask))
        vol = np.zeros((reconstruction_size, reconstruction_size, reconstruction_size))
        for each_plane in list(range(reconstruction_size)):
            vol[each_plane] = fsc_rec_np
        
        vol = vol.transpose()
        top_bottom_cut = EMNumPy.numpy2em(np.copy(vol))

        return top_bottom_cut


    def compute_fsc_of_raw_reconstruction_halves(self, first_rec, second_rec, top_bottom_cut):
        fsc_line_raw = self.normalize_and_scale_volumes_including_mask_and_compute_fsc(first_rec, second_rec,
        top_bottom_cut)
        
        return fsc_line_raw


    def compute_fsc_of_cylinder_masked_reconstruction_halves(self, first_rec, second_rec, top_bottom_cut,
    pixelinfo):
            
        fsc_mask_vol = SegClassReconstruct().make_smooth_cylinder_mask(pixelinfo.helixwidthpix,
        pixelinfo.helix_inner_widthpix, pixelinfo.reconstruction_size, width_falloff=0.03)
            
        fsc_cylinder_masked = self.normalize_and_scale_volumes_including_mask_and_compute_fsc(first_rec, second_rec,
        fsc_mask_vol * top_bottom_cut)
        
        return fsc_mask_vol, fsc_cylinder_masked


    def compute_Fourier_radius(self, res_cutoff, pixelsize, dim):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.compute_Fourier_radius(20, 5, 100)
        25
        >>> s.compute_Fourier_radius(40, 5, 100)
        13
        >>> s.compute_Fourier_radius(11, 5, 100)
        45
        """
        return int(round(dim * (pixelsize) / float(res_cutoff)))


    def randomize_quant_beyond_circle(self, F_phase, circ_np, amp=False):
        Frand_phase = np.random.rand(F_phase.shape[0], F_phase.shape[1], F_phase.shape[2])
        if amp:
            Frand_phase = np.exp(Frand_phase)
        Frand_phase = (F_phase.max() - F_phase.min()) * Frand_phase + F_phase.min()
        F_phase[circ_np == 0.0] = 0.0
        Frand_phase[circ_np == 1.0] = 0.0
        Fnew_phase = Frand_phase + F_phase

        return Fnew_phase


    def generate_structure_with_phases_randomized(self, vol, res_cutoff, pixelsize):
        F_radius = self.compute_Fourier_radius(res_cutoff, pixelsize, vol.get_xsize())
        vol_np = np.copy(EMNumPy.em2numpy(vol))
        
        # Fourier transform n-dimensional array
        cyl_fft = np.fft.fftn(vol_np)
        # convert from complex numbers to amp and phases
        centered_fft = np.fft.fftshift(cyl_fft)
        F_amp = np.abs(centered_fft)
        F_phase = np.angle(centered_fft)
        
        circ_np = np.copy(EMNumPy.em2numpy(model_circle(F_radius, F_phase.shape[0], F_phase.shape[1], F_phase.shape[2])))
        Fnew_phase = self.randomize_quant_beyond_circle(F_phase, circ_np)
#         circ_np = np.copy(EMNumPy.em2numpy(model_circle(23 * F_radius, F_phase.shape[0], F_phase.shape[1], F_phase.shape[2])))
#         Fnew_amp = self.randomize_quant_beyond_circle(F_amp, circ_np, amp=True)
        
        # back to the complex representation
        Fnew = F_amp * np.exp(1j * Fnew_phase)
        fnew = np.fft.ifftn(np.fft.ifftshift(Fnew))
        
        vol_phase_rand = EMNumPy.numpy2em(np.real(fnew))
        
        return vol_phase_rand, F_radius
        
        
    def compute_fsc_of_structure_masked_reconstruction_halves(self, first_rec, second_rec, uncorrected_reconstruction,
    pixelinfo, top_bottom_cut, res=None):
            
        if res is not None:
            filter_coefficients = SegmentAlign2d().prepare_filter_function(False, 0.1, True, 1 / (res + 10),
            pixelinfo.pixelsize, uncorrected_reconstruction.get_xsize(), 0.08, False, 'blank', 0)
         
            filt_rec = filt_table(uncorrected_reconstruction, filter_coefficients)
        else:
            filt_rec = uncorrected_reconstruction

        fsc_mask_vol = self.build_structural_mask_from_volume(filt_rec, pixelinfo.helixwidthpix,
        pixelinfo.helix_inner_widthpix, pixelinfo.pixelsize, sigma_factor=1.5)
         
        fsc_mask_vol = filt_table(fsc_mask_vol, filter_coefficients)
            
        fsc_line_real = self.normalize_and_scale_volumes_including_mask_and_compute_fsc(first_rec, second_rec,
        fsc_mask_vol * top_bottom_cut)
        
        return fsc_mask_vol, fsc_line_real


    def compute_fsc_of_layer_line_filtered_reconstruction_halves(self, reconstruction_size, first_rec_norm,
    second_rec_norm, fsc_mask_vol, pixelinfo, helical_symmetry, rotational_sym):
        first_rec_filtered, layer_filter = self.generate_and_apply_layerline_filter(first_rec_norm, pixelinfo.pixelsize,
        helical_symmetry, pixelinfo.helixwidthpix * pixelinfo.pixelsize, rotational_sym)
        
        second_rec_filtered = self.filter_volume_by_fourier_filter_while_padding(second_rec_norm, reconstruction_size, 
        2 * reconstruction_size, layer_filter)
        
        fsc_line_fourier = self.normalize_and_scale_volumes_including_mask_and_compute_fsc(first_rec_filtered,
        second_rec_filtered, fsc_mask_vol)
        
        return fsc_line_fourier


    def compute_fsc_on_volumes_from_half_the_dataset(self, resolution_aim, first_rec, second_rec, pixelinfo,
    helical_symmetry, rotational_sym):
        reconstruction_size = pixelinfo.reconstruction_size
        if reconstruction_size < first_rec.get_xsize():
            first_rec = Util.window(first_rec, reconstruction_size, reconstruction_size, reconstruction_size, 0, 0, 0)
            second_rec = Util.window(second_rec, reconstruction_size, reconstruction_size, reconstruction_size, 0, 0, 0)
            
        uncorrected_reconstruction = first_rec + second_rec
        
        top_bottom_cut = self.build_smooth_mask_with_top_and_bottom_cut(reconstruction_size)

        fsc_line_unmasked = self.compute_fsc_of_raw_reconstruction_halves(first_rec, second_rec, top_bottom_cut)
        uncorrected_reconstruction *= top_bottom_cut

        fsc_mask_vol, fsc_cylinder_masked = self.compute_fsc_of_cylinder_masked_reconstruction_halves(first_rec,
        second_rec, top_bottom_cut, pixelinfo)
        
        resolution = SegmentExam().make_oneoverres(fsc_cylinder_masked, pixelinfo.pixelsize)
        
        cyl_resolution = self.get_resolution_closest_to_value(0.75, fsc_cylinder_masked, resolution)
        if cyl_resolution < 12:
            fsc_mask_vol, fsc_structure_masked = \
            self.compute_fsc_of_structure_masked_reconstruction_halves(first_rec, second_rec,
            uncorrected_reconstruction, pixelinfo, top_bottom_cut, cyl_resolution)

            first_rec_rand, F_radius = self.generate_structure_with_phases_randomized(first_rec, cyl_resolution,
            pixelinfo.pixelsize)

            fsc_structure_rand = self.normalize_and_scale_volumes_including_mask_and_compute_fsc(first_rec_rand,
            second_rec, fsc_mask_vol * top_bottom_cut)
            
            fsc_structure_true = (fsc_structure_masked[F_radius:] - fsc_structure_rand[F_radius:]) / \
            (1 - fsc_structure_rand[F_radius:])
            
            fsc_structure_true = np.append(fsc_structure_masked[:F_radius], fsc_structure_true)
        else:
            fsc_structure_true = [None] * len(fsc_cylinder_masked)
        
        helical_rise, helical_rotation = helical_symmetry
        if helical_rise != 0 and self.layer_line_filter:
            fsc_layer_line_filtered = self.compute_fsc_of_layer_line_filtered_reconstruction_halves(reconstruction_size,
            first_rec, second_rec, fsc_mask_vol, pixelinfo, helical_symmetry, rotational_sym)
        else:
            fsc_layer_line_filtered = [None] * len(fsc_line_unmasked)
        
        fsc_named_tuple = self.make_fsc_line_named_tuple()
        fsc_lines = fsc_named_tuple(fsc_line_unmasked, fsc_cylinder_masked, fsc_structure_true, fsc_layer_line_filtered)
        
        return uncorrected_reconstruction, fsc_lines
    
    
    def merge_list_of_helical_errors(self, helical_error):
        err_tuple = SegClassReconstruct().make_helical_error_tuple()
        helical_error = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(helical_error, err_tuple)

        helical_ccc_errors = [each_rank.helical_ccc_error for each_rank in helical_error]
        mean_helical_cccs = [each_rank.mean_helical_ccc for each_rank in helical_error]
        segment_counts = [each_rank.segment_count for each_rank in helical_error]
        asym_unit_counts = [each_rank.asym_unit_count for each_rank in helical_error]

        if sum(asym_unit_counts) > 0:
            mean_helical_ccc = np.average(mean_helical_cccs, weights=asym_unit_counts)
            helical_ccc_error = np.average(helical_ccc_errors, weights=segment_counts)
        else:
            mean_helical_ccc = None
            helical_ccc_error = None
        helical_error = err_tuple(helical_ccc_error, mean_helical_ccc, None, None, None, None, None, 
        sum(segment_counts), sum(asym_unit_counts))

        return helical_error


    def prepare_empty_helical_error(self):
        err_tuple = SegClassReconstruct().make_helical_error_tuple()
        helical_error = err_tuple(0, 1, 0, 0, 0, 0, 0, 0, 0)

        return helical_error


    def perform_mean_ccc_evaluation_of_images_with_symmetry_related_projections(self, rec_stack, alignment_parameters,
    Euler_angles_rec, helixwidthpix):
        if hasattr(self, 'comm'):
            local_job_count, this_node, unique_nodes = OpenMpi().get_job_current_count_on_this_node(self.comm)
        else:
            local_job_count = 1
        
        if len(alignment_parameters) > 0:
            ds = DiskSpace(self.temppath)
            byte_size = int(Support().compute_byte_size_of_image_stack(rec_stack.alignment_size,
            rec_stack.alignment_size, 2 * len(Euler_angles_rec)))

            split_count = int(byte_size * local_job_count / ds.bytes_free()) + 1

            Euler_angles_rec_split = OpenMpi().split_sequence_evenly(Euler_angles_rec, split_count)
            helical_errors = []
            for each_Euler_angles_rec in Euler_angles_rec_split: 
                helical_error, dummy, dummy = \
                SegClassReconstruct().determine_mean_ccc_deviation_within_symmetry_related_views(rec_stack,
                each_Euler_angles_rec, helixwidthpix)
                helical_errors.append(helical_error)
             
            os.remove(rec_stack.file_name)
 
            helical_error = self.merge_list_of_helical_errors(helical_errors)
        else:
            helical_error = self.prepare_empty_helical_error()

        return helical_error


    def log_helical_error(self, helical_error):
        msg = tabulate(zip(['mean helical cross correlation', 'mean helical ccc error (stdev)'], 
                           [helical_error.mean_helical_ccc, helical_error.helical_ccc_error]))

        self.log.ilog('For this iteration: the following helical CCC statistics of asymmetric units with ' + \
            'their reprojections were determined:\n{0}'.format(msg))
        

    def apply_orientation_parameters_and_reconstruct_imposing_helical_symmetry(self, alignment_parameters, ref_cycle_id,
    resolution_aim, large_input_stack, ctf3d_avg_squared, pixelinfo, each_reference, stepsize, rec_stack, lambda_sirt,
    unbending, rank=None, split_reconstruction=True):
        mpi = rank
        self.log.fcttolog()
        self.log.in_progress_log()
        
        mode = 'BP 3F'
        if split_reconstruction or mpi is None:
            split_align_params = [alignment_parameters[:len(alignment_parameters)/2],
            alignment_parameters[len(alignment_parameters)/2:]]
            
            for each_rec_id, each_half_params in enumerate(split_align_params):
                if mode == 'BP 3F':
                    uncorrected_reconstruction, symmetry_alignment_parameters, symmetry_rec_loginfo, Euler_angles_rec =\
                    self.compute_3dreconstruction_by_Fourier_interpolation(large_input_stack, pixelinfo.pixelsize,
                    each_reference.helical_symmetry, stepsize, pixelinfo.reconstruction_size, rec_stack,
                    each_reference.point_symmetry, each_half_params)
                    
                elif mode == 'BP RP':
                    uncorrected_reconstruction, symmetry_alignment_parameters, symmetry_rec_loginfo, lambda_sirt = \
                    self.compute_3dreconstruction_by_SIRT(large_input_stack, pixelinfo.pixelsize,
                    each_reference.helical_symmetry, stepsize, pixelinfo.reconstruction_size, rec_stack,
                    each_reference.point_symmetry, each_half_params, lambda_sirt)
                    
                if each_rec_id == 0:
                    first_rec = uncorrected_reconstruction
                    
                    symmetry_alignment_parameters_first = \
                    SegClassReconstruct().log_and_stack_alignment_parameters_into_numpy_array(each_half_params,
                    symmetry_alignment_parameters, symmetry_rec_loginfo)
                    
                elif each_rec_id == 1:
                    second_rec = uncorrected_reconstruction
                    
                    symmetry_alignment_parameters_second = \
                    SegClassReconstruct().log_and_stack_alignment_parameters_into_numpy_array(each_half_params,
                    symmetry_alignment_parameters, symmetry_rec_loginfo)
                
            symmetry_alignment_parameters = np.vstack([symmetry_alignment_parameters_first,
            symmetry_alignment_parameters_second])
        
            if first_rec is not None and second_rec is not None:
                uncorrected_reconstruction, fsc_lines = \
                self.compute_fsc_on_volumes_from_half_the_dataset(resolution_aim, first_rec, second_rec,
                pixelinfo, each_reference.helical_symmetry, each_reference.rotational_symmetry)
                if self.keep_intermediate_files:
                    first_rec.write_image('rec_fsc_even.hdf')
                    second_rec.write_image('rec_fsc_odd.hdf')
            else:
                uncorrected_reconstruction = None
                fsc_lines = None
        else:
            if mode == 'BP 3F':
                if alignment_parameters != []:
                    uncorrected_reconstruction, symmetry_alignment_parameters, symmetry_rec_loginfo, Euler_angles_rec = \
                    self.compute_3dreconstruction_by_Fourier_interpolation(large_input_stack, pixelinfo.pixelsize,
                    each_reference.helical_symmetry, stepsize, pixelinfo.reconstruction_size, rec_stack, 
                    each_reference.point_symmetry, alignment_parameters)
                else:
                    uncorrected_reconstruction = model_blank(pixelinfo.reconstruction_size,
                    pixelinfo.reconstruction_size, pixelinfo.reconstruction_size, 0)
                    
                    Euler_angles_rec = []
                    symmetry_alignment_parameters = []
                    symmetry_rec_loginfo = ''
            elif mode == 'BP RP':
                uncorrected_reconstruction, symmetry_alignment_parameters, symmetry_rec_loginfo, lambda_sirt = \
                self.compute_3dreconstruction_by_SIRT(large_input_stack, pixelinfo.pixelsize,
                each_reference.helical_symmetry, stepsize, pixelinfo.reconstruction_size, rec_stack,
                each_reference.point_symmetry, alignment_parameters, lambda_sirt)
                
            fsc_lines = None
            
            symmetry_alignment_parameters = \
            SegClassReconstruct().log_and_stack_alignment_parameters_into_numpy_array(alignment_parameters,
            symmetry_alignment_parameters, symmetry_rec_loginfo)
        
        return uncorrected_reconstruction, alignment_parameters, symmetry_alignment_parameters, fsc_lines, lambda_sirt,\
            Euler_angles_rec
    