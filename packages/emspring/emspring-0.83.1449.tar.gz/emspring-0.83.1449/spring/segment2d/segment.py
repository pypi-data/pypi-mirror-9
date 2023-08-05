# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import Util, EMData, EMUtil, EMNumPy
from collections import namedtuple
from filter import filt_gaussl
from fundamentals import rot_shift2D, image_decimate, fshift
from morphology import threshold
from scipy import interpolate
from spring.csinfrastr.csdatabase import SpringDataBase, base, CtfMicrographTable, HelixTable, SegmentTable, \
    CtfFindMicrographTable, CtfTiltMicrographTable, refine_base, RefinementCycleSegmentTable, RefinementCycleTable, \
    RefinementCycleHelixTable
from spring.csinfrastr.csreadinput import OptHandler
from spring.micprgs.scansplit import Micrograph
from spring.segment2d.segment_int import SegmentStraighten
from spring.segment2d.segment_prep import SegmentPar
from spring.segment2d.segmentctfapply import SegmentCtfApply
from spring.segment2d.segmentexam import SegmentExam
from spring.segment2d.segmentselect import SegmentSelect
from tabulate import tabulate
import numpy as np
import os
import shutil
    
                        
class SegmentCut(SegmentStraighten):
    def compute_new_micsize_if_coordinates_at_edges(self, xcoord, ycoord, segsizepix, mic_xsize, mic_ysize):
        """
        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> s.compute_new_micsize_if_coordinates_at_edges(10, 10, 30, 2000, 4000)
        (2012, 4012, -990, -1990)
        >>> s.compute_new_micsize_if_coordinates_at_edges(1995, 3995, 30, 2000, 4000)
        (2022, 4022, 995, 1995)
        >>> s.compute_new_micsize_if_coordinates_at_edges(-10, 10, 30, 2000, 4000)
        (2052, 4012, -1010, -1990)
        >>> s.compute_new_micsize_if_coordinates_at_edges(2005, 4005, 30, 2000, 4000)
        (2042, 4042, 1005, 2005)
        >>> s.compute_new_micsize_if_coordinates_at_edges(13463, 1924, 1216, 10880, 14035)
        (17264, 14035, 8023, -5093)
        """
        x_distance_from_edge = int(min((xcoord, mic_xsize - xcoord)))
        y_distance_from_edge = int(min((ycoord, mic_ysize - ycoord)))
        xoffcenter = int(round(xcoord)) - mic_xsize / 2
        yoffcenter = int(round(ycoord)) - mic_ysize / 2
        if x_distance_from_edge <= segsizepix / 2 or y_distance_from_edge <= segsizepix / 2:
            if x_distance_from_edge <= segsizepix / 2:
                mic_xsize = int(mic_xsize + (segsizepix - 2 * (x_distance_from_edge - 1)))
            if y_distance_from_edge <= segsizepix / 2:
                mic_ysize = int(mic_ysize + (segsizepix - 2 * (y_distance_from_edge - 1)))
                
        return mic_xsize, mic_ysize, xoffcenter, yoffcenter
    

    def window_segment(self, micrograph, xcoord, ycoord, segsizepix):
        """
        * Function to window segment from image part of cut_segments

        #. Input: x and y coordinates, segment size (pixel)
        #. Output: windowed segment
        #. Usage: im_out = window_segment(micrograph_img, xcoord, ycoord, segsizepix)
        
        """

        mic_xsize = micrograph.get_xsize()
        mic_ysize = micrograph.get_ysize()
        
        new_mic_xsize, new_mic_ysize, xoffcenter, yoffcenter = self.compute_new_micsize_if_coordinates_at_edges(xcoord,
        ycoord, segsizepix, mic_xsize, mic_ysize)
        
        if new_mic_xsize > mic_xsize or new_mic_ysize > mic_ysize:
            micrograph = Util.pad(micrograph, new_mic_xsize, new_mic_ysize, 1, 0, 0, 0, 'average')
        im_out = Util.window(micrograph, segsizepix, segsizepix, 1, xoffcenter, yoffcenter, 0)

        return im_out
    

    def invert(self, img=None):
        """
        * Function to invert segment image densities for cryo data (protein=white)

        #. Input: segment image
        #. Output: inverted image segment
        #. Usage: im_out = normalize(img)
        
        """
        if img is None: 
            img = self.im_out

        im_out = img*(-1)
        return im_out

    def normalize(self, img=None):
        """
        * Function to normalize segment to image densities of average 0 and \
        standard deviation of 1 and truncate dark spots

        #. Input: segment image
        #. Output: normalized image segment
        #. Usage: im_out = normalize(img)
        
        """
        if img is None: 
            img = self.im_out

        img.process_inplace('normalize')
        # clear dark spots to average
        im_out = threshold(img, -3.75)

        return im_out

    def verticalize_segment(self, im_out=None, ipangle=None):
        """
        * Function to align helix axis to perpendicular image rows, includes additional windowing\
            to get rid of rotation artefacts at edges

        #. Input: image, angle to be rotated
        #. Output: written rtstack file
        #. Usage: verticalize_segment(im_out, ipangle)
        """
        if im_out is None: 
            im_out = self.im_out
        if ipangle is None: 
            ipangle = self.ipangle
        
        im_outrt = rot_shift2D(im_out, ipangle, 0, 0)#, interpolation_method='gridding')

        im_outrt = Util.window(im_outrt, self.segsizepix, self.segsizepix, 1, 0, 0, 0)
        
        return im_outrt
    
                
    def minimize_xposition(self, rowsaddimg=None, xshift=None):
        """
        * Function to center helix axis due to 2fold symmetry of projection

        #. Input: 1D helix projection
        #. Output: image shift required for centering perpendicular to helix axis
        #. Usage: centerx = minimize_xposition(rowsaddimg)
        
        """
        if rowsaddimg is None: 
            rowsaddimg = self.rowsaddimg

        # assume a rough centering cut out 1/6 at either sides
        symimgpars = []
        xshifts = np.arange(-xshift, xshift, 0.3)
#        pixels = np.arange(0, rowsaddimg.get_xsize())
        for shift in xshifts:
            # shift array
            shiftedline = fshift(rowsaddimg, shift)
            arrrowsaddimg = np.copy(EMNumPy.em2numpy(shiftedline))
            
            sp = np.fft.fft(arrrowsaddimg)
       
            # return a flattened array
            sp = sp.ravel()
       
            # compute symimgpar
            i1 = sp.imag**2
            i2 = sp.imag**2 + sp.real**2
            symimgpar = np.sqrt(i1.sum())/np.sqrt(i2.sum())

            symimgpars.append(symimgpar)

        # increase accuracy by a factor of 50 by interpolation
        xshifts_fine = np.arange(-xshift, xshift, 0.01)
        t = interpolate.splrep(xshifts, symimgpars, k=3, s=0)
        symimg_interpolated = interpolate.splev(xshifts_fine, t)

        sorted_indices, minima = SegmentExam().find_local_extrema(symimg_interpolated, target='minima')
        # sort according to real for display purposes
        centerx = xshifts_fine[sorted_indices[0]]
        symimg_par = symimg_interpolated[sorted_indices[0]]

        return centerx, symimg_par
    

    def center_xycoordinates(self, xcoord=None, ycoord=None, centerx=None, ipangle=None):
        """
        * Function to apply shift perpedicular to helix to xy coordinates

        #. Input: x and y coordinates, x-shift (pixel), in-plane rotation angle
        #. Output: centered x and y coordinates
        #. Usage: newxcoord, newycoord = center_xycoordinates(xcoor, ycoord, centerx, ipangle)

        >>> import numpy as np
        >>> from spring.segment2d.segment import Segment
        >>> # helix oriented along image columns
        ...
        >>> s = Segment()
        >>> x, y = s.center_xycoordinates(np.zeros(10), np.arange(10), 1, 0)
        >>> x 
        array([-1., -1., -1., -1., -1., -1., -1., -1., -1., -1.])
        >>> y
        array([ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9.])
        >>> # helix oriented along image rows
        ...
        >>> x = np.arange(10)
        >>> y = np.zeros(10)
        >>> s_xcoord, s_ycoord = s.center_xycoordinates(x, y, 1, 90)
        >>> s_xcoord
        array([ -6.12323400e-17,   1.00000000e+00,   2.00000000e+00,
                 3.00000000e+00,   4.00000000e+00,   5.00000000e+00,
                 6.00000000e+00,   7.00000000e+00,   8.00000000e+00,
                 9.00000000e+00])
        >>> s_ycoord
        array([-1., -1., -1., -1., -1., -1., -1., -1., -1., -1.])
        >>> # helix oriented by 45 degrees
        ...
        >>> y = x
        >>> s_xcoord, s_ycoord = s.center_xycoordinates(x, y, 1, -45)
        >>> s_xcoord
        array([-0.70710678,  0.29289322,  1.29289322,  2.29289322,  3.29289322,
                4.29289322,  5.29289322,  6.29289322,  7.29289322,  8.29289322])
        >>> s_ycoord
        array([ 0.70710678,  1.70710678,  2.70710678,  3.70710678,  4.70710678,
                5.70710678,  6.70710678,  7.70710678,  8.70710678,  9.70710678])
        >>> # helix oriented by -45 degrees
        ...
        >>> s_xcoord, s_ycoord = s.center_xycoordinates(x, np.flipud(x), 1, 45)
        >>> s_xcoord
        array([-0.70710678,  0.29289322,  1.29289322,  2.29289322,  3.29289322,
                4.29289322,  5.29289322,  6.29289322,  7.29289322,  8.29289322])
        >>> s_ycoord
        array([ 8.29289322,  7.29289322,  6.29289322,  5.29289322,  4.29289322,
                3.29289322,  2.29289322,  1.29289322,  0.29289322, -0.70710678])

        """
        if xcoord is None: xcoord = self.xcoord
        if ycoord is None: ycoord = self.ycoord
        if centerx is None: centerx = self.centerx
        if ipangle is None: ipangle = self.ipangle

        rotx = centerx*np.cos(np.radians(ipangle))
        roty = centerx*np.sin(np.radians(ipangle))
#        self.log.dlog('modified x: {0} modified y: {1} inplane-angle: {2}'.format(rotx, roty, ipangle))
        self.newxcoord = xcoord - rotx
        self.newycoord = ycoord - roty

        return self.newxcoord, self.newycoord


    def center_segments(self, helices, rtimgstack, mask_width):
        """
        * Function to center helix axis 

        #. Input: in-plane rotated image stack
        #. Output: re-cut segment stack
        #. Usage: center_segments(rtimgstack, mask_width)
        
        """
        self.log.fcttolog()
        each_image_index = 0
        segment = EMData()

        log_info = []
        for each_helix_id, each_helix in enumerate(helices):
            for each_seg_id, each_helix_coordinate in enumerate(each_helix.coordinates):
                if (self.stepsize == 0 and each_seg_id == 0) or \
                (self.stepsize == 0 and each_seg_id == len(each_helix_coordinate) - 1):
                    pass
                else:
                    segment.read_image(rtimgstack, each_image_index)
                    filter_radius = self.pixelsize/float(max(self.helixwidth/4, 40.0))
                    segment = filt_gaussl(segment, filter_radius)
                    
                    self.helixmask = SegmentExam().make_smooth_rectangular_mask(mask_width, self.segsizepix * 0.8,
                    self.segsizepix)
                    
                    segment *= self.helixmask
                    rowsaddimg = SegmentExam().project_helix(segment)
                    centerx, symimg_par = self.minimize_xposition(rowsaddimg, 0.35*self.helixwidthpix)
                    
                    xcoord, ycoord = each_helix_coordinate
                    
                    centered_x, centered_y = self.center_xycoordinates(xcoord, ycoord, centerx,
                    each_helix.inplane_angle[each_seg_id])
                    
                    each_helix.coordinates[each_seg_id] = (centered_x, centered_y)
                    each_image_index = each_image_index + 1
                    
                    log_info += [[each_seg_id, each_helix.helix_id, centered_x, symimg_par, xcoord, ycoord,
                    centered_x, centered_y, each_helix.picked_coordinates[each_seg_id][0],
                    each_helix.picked_coordinates[each_seg_id][1]]]

            xs, ys = list(zip(*each_helix.coordinates))
            each_helix_x_coordinates = np.array(xs)
            each_helix_y_coordinates = np.array(ys)
            
            self.write_boxfile(each_helix_x_coordinates, each_helix_y_coordinates, self.segsizepix,
            filename=each_helix.segment_list)
            
            helices[each_helix_id] = each_helix._replace(coordinates=zip(each_helix_x_coordinates,
            each_helix_y_coordinates))

        header = ['segment_id', 'helix_id', 'center_x', 'minimizer', 'previous_xy', 'centered_xy', 'picked_xy']
        msg = tabulate(log_info, header)
        self.log.ilog('The following segments were centered:\n{0}'.format(msg))
        
        return helices


    def make_segment_info_named_tuple(self):
        segment_info = namedtuple('segment_info', 'mic_id x_coordinate_A y_coordinate_A')
        return segment_info

    
    def pre_loop_setup(self):
        each_image_index = 0
        log_info = []
        ctf_info = []
        micrograph_img = EMData()
        matched_mic_find = None
        micrograph_name = ''

        return micrograph_img, matched_mic_find, micrograph_name, log_info, ctf_info, each_image_index


    def get_mic_slice_from_mrc_stack(self, micrograph_name):
        vol = EMData()
        prefix, no_ending = micrograph_name.split('@')
        stack_no, ext = os.path.splitext(no_ending)
        stack_name = prefix + ext
        vol.read_image(stack_name)
        micrograph_img = Util.window(vol, vol.get_xsize(), vol.get_ysize(), 1, 0, 0, -(vol.get_zsize() / 2) + int(stack_no))

        return micrograph_img


    def read_micrograph_and_get_ctf_info(self, micrograph_img, matched_mic_find, micrograph_name, session, each_helix):
        if micrograph_name != each_helix.micrograph:
            micrograph_name = each_helix.micrograph
            if '@' not in micrograph_name:
                micrograph_img, mic_xsize, mic_ysize = Micrograph().readmic(micrograph_name)
            elif '@' in micrograph_name:
                micrograph_img = self.get_mic_slice_from_mrc_stack(micrograph_name)

            if self.ctfcorrect_option:
                if not self.spring_db_option:
                    msg = 'CTF correction requested without specifying a spring database file. Please run ' + \
                    'micctfdetermine to generate spring.db file that contains the relevant CTF information.'
                    raise ValueError(msg)
                else:
                    matched_mic_find = SegmentCtfApply().get_micrograph_from_database_by_micname(session,
                    micrograph_name, self.spring_path)
            if self.row_normalization:
                for each_row in list(range(micrograph_img.get_xsize())):
                    row = micrograph_img.get_row(each_row)
                    row.process_inplace('normalize')
                    micrograph_img.set_row(row, each_row)
            
        return micrograph_img, matched_mic_find, micrograph_name
    

    def window_segment_and_invert_normalize_and_ctf_correct(self, session, large_segsizepix, each_helix, micrograph_img,
    matched_mic_find, xcoord, ycoord, ctf_info, each_image_index):
        windowed_segment = self.window_segment(micrograph_img, xcoord, ycoord, large_segsizepix)
        if self.invertoption == True:
            windowed_segment = self.invert(windowed_segment)
        if self.normoption == True:
            windowed_segment = self.normalize(windowed_segment)
        if self.ctfcorrect_option:
            segment_info = self.make_segment_info_named_tuple()
            each_segment = segment_info._make([matched_mic_find.id, xcoord * self.pixelsize, ycoord * self.pixelsize])
            
            ctf_params, avg_defocus, astigmatism, astig_angle = \
            SegmentCtfApply().get_ctfparameters_from_database(self.ctffind_or_ctftilt_choice, self.astigmatism_option,
            self.pixelsize, session, each_segment, matched_mic_find, self.spring_path)
            
            windowed_segment = \
            SegmentCtfApply().filter_image_by_ctf_convolve_or_phaseflip(self.convolve_or_phaseflip_choice,
            windowed_segment, ctf_params)
            
            ctf_info += [[each_image_index, each_helix.helix_id, matched_mic_find.micrograph_name] + \
            [each_ctf for each_ctf in ctf_params]]
            
        return windowed_segment, ctf_info


    def rotate_and_unbend_segment_if_required(self, imgstack, each_image_index, large_segsizepix,
    each_helix, each_segment_index, coordpair, windowed_segment):
        inplane_angle = each_helix.inplane_angle[each_segment_index]
        if not self.unbending:
            segment_rotated = self.verticalize_segment(windowed_segment, inplane_angle)
            polyfit = None
        else:
            cut_coord_pair = round(coordpair[0]), round(coordpair[1])
            if each_segment_index * self.stepsize < 0.8 * float(self.window_size) or \
            (len(each_helix.coordinates) - each_segment_index) * self.stepsize < 0.8 * float(self.window_size):
                straightened_segment, polyfit, central_ip_angle = \
                self.unbend_segment_using_coordinates(windowed_segment, large_segsizepix, each_helix.coordinates,
                coordpair, cut_coord_pair, inplane_angle, 0.0)
            else:
                straightened_segment, polyfit, central_ip_angle = \
                self.unbend_segment_using_coordinates(windowed_segment, large_segsizepix, each_helix.coordinates,
                coordpair, cut_coord_pair, inplane_angle)
            segment_rotated = Util.window(straightened_segment, self.segsizepix, self.segsizepix, 1, 0, 0, 0)
            
        if self.unbending or self.rotoption:
            segment_rotated.write_image(imgstack, each_image_index)
        else:
            windowed_segment = Util.window(windowed_segment, self.segsizepix, self.segsizepix, 1, 0, 0, 0)
            windowed_segment.write_image(imgstack, each_image_index)

        return polyfit


    def get_ctfinfo_header(self):
        ctf_info = ['Local_id', 'helix_id', 'micrograph', 'avg_defocus(microm)', 'Cs(mm)', 'voltage(kV)', 'pixelsize', 
        'bfactor', 'amp_contrast', 'astigmatism', 'astig_angle']
        
        return ctf_info
    

    def get_log_info_header(self):
        return ['Local_id', 'helix_id', 'micrograph', 'x_coordinate', 'y_coordinate', 'normalization', 
            'contrast_inversion', 'rotation', 'unbending', 'polynomial']


    def cut_segments(self, helices=None, imgstack=None):
        """
        * Function to cut segments from helices dictionary including micrograph\
         information, 

        #. Input: helix dictionary containing: micrograph, segment_list, \
            directory, coordinates, in-plane angle; outfilestack
        #. Output: written stack
        #. Usage: cut_segments(helices, outfile)
        
        """
        self.log.fcttolog()

        session = None
        if self.spring_db_option:
            session = SpringDataBase().setup_sqlite_db(base, self.spring_path)
        if self.spring_db_option and self.frame_option:
            session = SpringDataBase().setup_sqlite_db(base, self.spring_db_frames)

        large_segsizepix = int(np.sqrt(2) * self.window_sizepix)
        
        micrograph_img, matched_mic_find, micrograph_name, log_info, ctf_info, each_image_index = \
        self.pre_loop_setup()
        
        for each_helix_id, each_helix in enumerate(helices):
            micrograph_img, matched_mic_find, micrograph_name = self.read_micrograph_and_get_ctf_info(micrograph_img,
            matched_mic_find, micrograph_name, session, each_helix)
            
            for each_segment_index, coordpair in enumerate(each_helix.coordinates):
                xcoord, ycoord = coordpair
                if (self.stepsize == 0 and each_segment_index == 0) or \
                (self.stepsize == 0 and each_segment_index == len(each_helix.coordinates) - 1):
                    pass
                else:
                    windowed_segment, ctf_info = self.window_segment_and_invert_normalize_and_ctf_correct(session,
                    large_segsizepix, each_helix, micrograph_img, matched_mic_find, xcoord, ycoord,
                    ctf_info, each_image_index)
                    
                    polyfit = self.rotate_and_unbend_segment_if_required(imgstack, each_image_index,
                    large_segsizepix, each_helix, each_segment_index, coordpair, windowed_segment)
                    
                    log_info += [[each_image_index, each_helix.helix_id, os.path.basename(micrograph_name), xcoord,
                    ycoord, self.normoption, self.invertoption, self.rotoption, self.unbending, polyfit.__str__()]]
                    
                    each_image_index = each_image_index + 1
            self.log.plog(10.0 + (each_helix_id + 1) * 70.0 / float(len(helices)))
        msg = tabulate(log_info, self.get_log_info_header())
        if self.ctfcorrect_option:
            msg += '\n' + tabulate(ctf_info, self.get_ctfinfo_header())
        self.log.ilog('The following segments have been windowed:\n{0}'.format(msg))
                    
        return helices
    
    
    def compare_centered_coordinates_with_picked_coordinates_and_smooth_path(self, helices):
        for each_helix_id, each_helix in enumerate(helices):
            x_coord, y_coord = zip(*each_helix.coordinates)
            x_coord = np.array(x_coord)
            y_coord = np.array(y_coord)
            
            picked_x_coord, picked_y_coord = zip(*each_helix.picked_coordinates)
            
            shifted_x = x_coord - np.array(picked_x_coord)
            shifted_y = y_coord - np.array(picked_y_coord)
            
            shifts_x_helix, shifts_y_helix = self.rotate_coordinates_by_angle(shifted_x, shifted_y,
            np.average(each_helix.inplane_angle))
            
            excessive_shift_indices = np.where(np.abs(shifts_x_helix) > 0.35*self.helixwidthpix)
            for each_shift_index in excessive_shift_indices[0]:
                x_coord[each_shift_index] = picked_x_coord[each_shift_index]
                y_coord[each_shift_index] = picked_y_coord[each_shift_index]
            
            interpolated_xcoord, interpolated_ycoord, ipangle, curvature = \
            self.interpolate_coordinates(np.array(x_coord), np.array(y_coord), self.pixelsize, self.stepsize,
            self.helixwidth, each_helix.segment_list, new_stepsize=False)
            
            helices[each_helix_id] = helices[each_helix_id]._replace(coordinates=zip(interpolated_xcoord,
            interpolated_ycoord))
            
            helices[each_helix_id] = helices[each_helix_id]._replace(inplane_angle=ipangle)
            helices[each_helix_id] = helices[each_helix_id]._replace(curvature=curvature)
        
        return helices
            

class SegmentDatabase(SegmentCut):
            
    def remove_all_previous_entries(self, session, column_name):
#        if session.query(column_name).count > 0:
        column = session.query(column_name).all()
        for each_item in column:
            session.delete(each_item)
        
        return session
    

    def enter_parameters_into_helix_table(self, session, each_helix, current_mic):
        matched_helix_id = session.query(HelixTable.id).\
        filter(HelixTable.helix_name == os.path.basename(each_helix.segment_list)).first()
        
        if matched_helix_id is not None:
            helix = session.query(HelixTable).get(matched_helix_id)
        else:
            helix = HelixTable()
            helix.helix_name = os.path.basename(each_helix.segment_list)
        helix.micrographs = current_mic
        helix.dirname = os.path.dirname(each_helix.segment_list)
        helix.avg_inplane_angle = sum(each_helix.inplane_angle) / float(len(each_helix.inplane_angle))
        helix.avg_curvature = sum(each_helix.curvature) / float(len(each_helix.curvature))
        if self.stepsize != 0 and self.averaging_option:
            window_size = int(self.averaging_distance / self.stepsize)
            lavg_inplane_angles = SegmentSelect().compute_local_average_from_measurements(each_helix.inplane_angle, window_size)
            lavg_curvatures = SegmentSelect().compute_local_average_from_measurements(each_helix.curvature, window_size)
            helix.lavg_distance_A = self.averaging_distance
        else:
            lavg_inplane_angles = each_helix.inplane_angle
            lavg_curvatures = each_helix.curvature
            helix.lavg_distance_A = 0
        previous_segment_ids_from_helix = session.query(SegmentTable).filter(SegmentTable.helix_id == helix.id).all()
        for each_previous_segment in previous_segment_ids_from_helix:
            session.delete(each_previous_segment)
        
        x_coordinates, y_coordinates = list(zip(*each_helix.coordinates))
        distances = self.compute_cumulative_distances_from_start_of_helix(x_coordinates, y_coordinates) * self.pixelsize
        helix.length = distances[-1]
        session.add(helix)
        
        return session, helix, distances, lavg_inplane_angles, lavg_curvatures
    

    def round_and_calculate_coordinate_in_Angstrom(self, each_helix_coordinate, pixelsize):
        coordinate_A = round(each_helix_coordinate) * pixelsize
        
        return coordinate_A
    

    def enter_parameters_into_segment_table(self, session, stack_id, each_helix, current_mic, helix, distances,
    lavg_inplane_angles, lavg_curvatures):
        if self.ctfcorrect_option:
            matched_mic_find = SegmentCtfApply().get_micrograph_from_database_by_micname(session, each_helix.micrograph,
            self.spring_path)
        for each_segment_index, each_helix_coordinate in enumerate(each_helix.coordinates):
            if self.stepsize == 0 and each_segment_index == 0 or self.stepsize != 0:
                segment = SegmentTable()
                segment.helices = helix
                segment.micrographs = current_mic
                segment.stack_id = stack_id
                x_coordinate = self.round_and_calculate_coordinate_in_Angstrom(each_helix_coordinate[0], self.pixelsize)
                y_coordinate = self.round_and_calculate_coordinate_in_Angstrom(each_helix_coordinate[1], self.pixelsize)
                segment.x_coordinate_A = x_coordinate
                segment.y_coordinate_A = y_coordinate
                
                picked_x_coordinate = \
                self.round_and_calculate_coordinate_in_Angstrom(each_helix.picked_coordinates[each_segment_index][0],
                self.pixelsize)
                
                picked_y_coordinate = \
                self.round_and_calculate_coordinate_in_Angstrom(each_helix.picked_coordinates[each_segment_index][1],
                self.pixelsize)
                
                segment.picked_x_coordinate_A = picked_x_coordinate
                segment.picked_y_coordinate_A = picked_y_coordinate
                segment.distance_from_start_A = distances[each_segment_index]
                segment.inplane_angle = each_helix.inplane_angle[each_segment_index]
                segment.curvature = each_helix.curvature[each_segment_index]
                segment.lavg_inplane_angle = lavg_inplane_angles[each_segment_index]
                segment.lavg_curvature = lavg_curvatures[each_segment_index]

                segment_info = self.make_segment_info_named_tuple()
                each_segment = segment_info._make([current_mic.id, x_coordinate, y_coordinate])
                if self.ctfcorrect_option:
                    ctf_params, avg_defocus, astigmatism, astig_angle = \
                    SegmentCtfApply().get_ctfparameters_from_database(self.ctffind_or_ctftilt_choice,
                    self.astigmatism_option, self.pixelsize, session, each_segment, matched_mic_find, self.spring_path)
                    
                    session, segment = \
                    SegmentCtfApply().update_ctfparameters_in_database(self.ctffind_or_ctftilt_choice,
                    self.convolve_or_phaseflip_choice, self.astigmatism_option, session, segment, avg_defocus,
                    astigmatism, astig_angle)

                if len(each_helix.coordinates) >= 3 and self.stepsize != 0:
                    polyfit, filtered_x, filtered_y = self.fit_square_function_path_of_coordinates(self.segsizepix *\
                    1.5, each_helix.coordinates, each_helix_coordinate, each_helix_coordinate,
                    each_helix.inplane_angle[each_segment_index])
                    
                    segment.second_order_fit = polyfit[0] * self.pixelsize
                else:
                    segment.second_order_fit = 0
                session.add(segment)
                stack_id += 1
        
        return session, stack_id
    

    def enter_helix_info_into_segments_and_helix_tables(self, helices, session):
        stack_id = 0
        for each_helix in helices:
            matched_mic_id = session.query(CtfMicrographTable.id).\
            filter(CtfMicrographTable.micrograph_name == os.path.basename(each_helix.micrograph)).first()

            if matched_mic_id is not None:
                current_mic = session.query(CtfMicrographTable).get(matched_mic_id)
            else:
                current_mic = CtfMicrographTable()
                current_mic.dirname = os.path.dirname(each_helix.micrograph)
                current_mic.micrograph_name = os.path.basename(each_helix.micrograph)
                current_mic.pixelsize = self.pixelsize
                session.add(current_mic)
            session, helix, distances, lavg_inplane_angles, lavg_curvatures = \
            self.enter_parameters_into_helix_table(session, each_helix, current_mic)

            session, stack_id = self.enter_parameters_into_segment_table(session, stack_id, each_helix, current_mic, 
            helix, distances, lavg_inplane_angles, lavg_curvatures)
        
        session.commit()

        return session
    

    def copy_micrograph_info_on_ctffind_and_ctftilt(self, assigned_mics, source_session, new_session):

        mic_columns = SpringDataBase().get_columns_from_table(CtfMicrographTable)
        find_columns = SpringDataBase().get_columns_from_table(CtfFindMicrographTable)
        tilt_columns = SpringDataBase().get_columns_from_table(CtfTiltMicrographTable)

        for each_mic, each_inp_mics in assigned_mics:
            matched_mic = source_session.query(CtfMicrographTable).\
            filter(CtfMicrographTable.micrograph_name.startswith(os.path.basename(os.path.splitext(each_mic)[0]))).first()

            matched_mic_find = source_session.query(CtfFindMicrographTable).get(matched_mic.id)
            mic_data = SpringDataBase().get_data_from_entry(mic_columns, matched_mic)
            if matched_mic_find is not None:
                find_data = SpringDataBase().get_data_from_entry(find_columns, matched_mic_find)

            matched_mic_tilt = source_session.query(CtfTiltMicrographTable).get(matched_mic.id)
            if matched_mic_tilt is not None:
                tilt_data = SpringDataBase().get_data_from_entry(tilt_columns, matched_mic_tilt)
            for each_inp in each_inp_mics:
                new_mic = CtfMicrographTable()
                [setattr(new_mic, each_col, mic_data[each_col]) for each_col in mic_columns if each_col != 'id']
                new_mic.micrograph_name = os.path.basename(each_inp)

                if matched_mic_find is not None:
                    new_find_mic = CtfFindMicrographTable()
                    [setattr(new_find_mic, each_col, find_data[each_col]) for each_col in find_columns if each_col != 'id']
                    new_find_mic.micrograph_name = os.path.basename(each_inp)
                    new_find_mic.ctf_micrographs = new_mic
                    
                    new_session.add(new_find_mic)

                if matched_mic_tilt is not None:
                    new_tilt_mic = CtfTiltMicrographTable()
                    [setattr(new_tilt_mic, each_col, tilt_data[each_col]) for each_col in tilt_columns if each_col != 'id']
                    new_tilt_mic.ctf_micrographs = new_mic
                    
                    new_session.add(new_tilt_mic)
                else:
                    new_session.add(new_mic)
        
        new_session.commit()
        
        return new_session


    def copy_and_duplicate_refined_segment_entries_to_new_database(self, assigned_stack_ids, ref_source_session,
    new_ref_session):

        ref_columns = SpringDataBase().get_columns_from_table(RefinementCycleSegmentTable)
        for each_related_stack_id, each_stack_id in enumerate(assigned_stack_ids):
            each_ref_entry = ref_source_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.stack_id == int(each_stack_id)).first()
            ref_data = SpringDataBase().get_data_from_entry(ref_columns, each_ref_entry)
            if ref_data is not None:
                ref_data['id'] = None
                ref_data['stack_id'] = each_related_stack_id
                new_ref_session.add(RefinementCycleSegmentTable(**ref_data))
        
        new_ref_session.commit()
        
        return new_ref_session


    def copy_and_duplicate_refined_helix_entries_to_new_database(self, assigned_helix_ids, ref_source_session,
    new_ref_session):
        hel_columns = SpringDataBase().get_columns_from_table(RefinementCycleHelixTable)
        for each_updated_hel_id, each_helix_id in enumerate(assigned_helix_ids):
            each_ref_entry = ref_source_session.query(RefinementCycleHelixTable).\
            filter(RefinementCycleHelixTable.helix_id == int(each_helix_id + 1)).first()

            hel_data = SpringDataBase().get_data_from_entry(hel_columns, each_ref_entry)
            if hel_data is not None:
                hel_data['id'] = None
                hel_data['helix_id']= each_updated_hel_id + 1
                new_ref_session.add(RefinementCycleHelixTable(**hel_data))
        
        new_ref_session.commit()
        
        return new_ref_session


    def copy_refinement_info_into_new_refinement_database(self, assigned_stack_ids, assigned_helix_ids):
        ref_source_session = SpringDataBase().setup_sqlite_db(refine_base, self.ref_db)
        new_ref_session = SpringDataBase().setup_sqlite_db(refine_base, self.ref_db_frames)

        new_ref_session = self.copy_and_duplicate_refined_segment_entries_to_new_database(assigned_stack_ids,
        ref_source_session, new_ref_session)

        new_ref_session = self.copy_and_duplicate_refined_helix_entries_to_new_database(assigned_helix_ids,
        ref_source_session, new_ref_session)

        new_ref_session = SpringDataBase().copy_all_table_data_from_one_session_to_another_session(RefinementCycleTable, 
        new_ref_session, ref_source_session)


    def enter_helix_parameters_in_database(self, helices, assigned_stack_ids, assigned_helix_ids):
        if not self.frame_option:
            if self.spring_db_option:
                shutil.copy(self.spring_path, 'spring.db')
            session = SpringDataBase().setup_sqlite_db(base)
            
            if self.spring_db_option:
                session = SpringDataBase().remove_all_previous_entries(session, SegmentTable)
                session = SpringDataBase().remove_all_previous_entries(session, HelixTable)
                    
            session = self.enter_helix_info_into_segments_and_helix_tables(helices, session)
        
        if self.frame_option:
            new_session = SpringDataBase().setup_sqlite_db(base, self.spring_db_frames)

            new_session = self.enter_helix_info_into_segments_and_helix_tables(helices, new_session)
        
            self.copy_refinement_info_into_new_refinement_database(assigned_stack_ids, assigned_helix_ids)
        

class Segment(SegmentDatabase):
    def binstack(self, imgstack=None, binned_imgstack=None, binfactor=None):
        """
        * Function to bin image stack by factor

        #. Input: image stack to be binned, bining factor (1 = no binning)
        #. Output: binned stack
        #. Usage: binnedimgstack = binstack(imgstack, binfactor)
        
        """
        self.log.fcttolog()

        if imgstack is None: 
            imgstack = self.imgstack
        if binfactor is None: 
            binfactor = self.binfactor

        if binfactor < 2:
            self.log.errlog('Bin factor of {0} too low, binning is not required'.format(binfactor))
        else:
            segment = EMData()
            noimgstack = EMUtil.get_image_count(imgstack)
            for each_segment_index in range(noimgstack):
                segment.read_image(imgstack, each_segment_index)
                decsegment = image_decimate(segment, binfactor)
                decsegment.write_image(binned_imgstack, each_segment_index)
            self.log.ilog('{0} images from {1} were binned by a factor of {2}'.format(noimgstack, imgstack, binfactor))

        return binned_imgstack

    def segment(self):
        self.helices, assigned_stack_ids, assigned_helix_ids = self.prepare_segmentation()
        self.log.plog(10)
        
        imgstack = self.outfile
        self.helices = self.cut_segments(self.helices, imgstack)

        self.log.plog(80)

        self.enter_helix_parameters_in_database(self.helices, assigned_stack_ids, assigned_helix_ids)
        if self.binoption is True: 
            binned_imgstack = '{0}-{1}xbin{2}'.format(os.path.splitext(imgstack)[0], self.binfactor,
            os.path.splitext(imgstack)[-1])
            
            self.binstack(imgstack, binned_imgstack, self.binfactor)

        self.log.endlog(self.feature_set)
        
        return self.outfile

def main():
    # Option handling
    parset = SegmentPar()
    mergeparset = OptHandler(parset)
 
    ######## Program
    mic = Segment(mergeparset)
    mic.segment()

if __name__ == '__main__':
    main()
