# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import Util, Transform
from collections import namedtuple
from fundamentals import rot_shift2D, prepi
from scipy import interpolate
from spring.csinfrastr.csdatabase import SpringDataBase, base, CtfMicrographTable, SegmentTable, HelixTable
from spring.csinfrastr.csproductivity import OpenMpi
from spring.segment2d.segment_prep import SegmentPreparationFileRead
from tabulate import tabulate
from utilities import model_blank
import numpy as np
import os
    
                        
class SegmentInterpolation(SegmentPreparationFileRead):
    def make_helixinfo_named_tuple(self):
        helixinfo = namedtuple('helixinfo', 'helix_id micrograph segment_list directory coordinates ' + \
                                            'picked_coordinates inplane_angle curvature')
        
        return helixinfo


    def convert_coordinate_line_to_xy_coordinates(self, each_coordinate_line):
        col = each_coordinate_line.split()
        xcoord = float(col[0])
        ycoord = float(col[1])
        boxsize = float(col[2])
        xcenter = xcoord + boxsize / 2
        ycenter = ycoord + boxsize / 2
        
        return xcenter, ycenter
    

    def compute_cumulative_distances_from_start_of_helix(self, x_coordinates, y_coordinates):
        """
        >>> from spring.segment2d.segment import Segment
        >>> x_coordinates = y_coordinates = np.arange(10)
        >>> s = Segment()
        >>> s.compute_cumulative_distances_from_start_of_helix(x_coordinates, y_coordinates)
        array([  0.        ,   1.41421356,   2.82842712,   4.24264069,
                 5.65685425,   7.07106781,   8.48528137,   9.89949494,
                11.3137085 ,  12.72792206])
        >>> x_coordinates = 10 * np.ones(10)
        >>> y_coordinates = np.arange(10)
        >>> s.compute_cumulative_distances_from_start_of_helix(x_coordinates, y_coordinates)
        array([ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9.])
        """
        previous_x_coord = np.roll(np.array(x_coordinates), 1)
        previous_y_coord = np.roll(np.array(y_coordinates), 1)
        distances = np.sqrt((x_coordinates - previous_x_coord)**2 + (y_coordinates - previous_y_coord)**2)
        distances[0] = 0
        distances_from_start = np.cumsum(distances)
        
        return distances_from_start


    def enter_helixinfo_into_helices_and_write_boxfiles(self, helices, micfile, overlap, helixfile, interpolated_xcoord,
    interpolated_ycoord, ipangle, curvature, picked_coordinates, int_xy_coordinates):
        helixinfo = self.make_helixinfo_named_tuple()
        total_helix_number = len(helices) + 1

        helices.append(helixinfo(total_helix_number, micfile, helixfile, overlap, int_xy_coordinates,
        picked_coordinates, ipangle, curvature))

        interpolated_xcoord, interpolated_ycoord = zip(*int_xy_coordinates)

        self.write_boxfile(np.array(interpolated_xcoord), np.array(interpolated_ycoord), self.segsizepix,
        filename=helixfile)

        data = zip([total_helix_number] + (len(int_xy_coordinates) - 1) * [None], 
            [os.path.basename(helixfile)] + (len(int_xy_coordinates) - 1) * [None], 
            interpolated_xcoord, interpolated_ycoord)
        log_info = '\n' + tabulate(data, ['helix_id', 'helix_file', 'x-coordinate', 'y-coordinate'])
        self.log.ilog(log_info)
        
        return helices


    def perform_interpolation_perturbation_removal_if_required(self, helices, segfile, stepsize, pixelsize, helixwidth,
    micfile, overlap, helixfile, x_coordinates, y_coordinates):
        
        if self.frame_option:
            interpolated_xcoord, interpolated_ycoord, ipangle, curvature = \
            self.interpolate_coordinates(np.array(x_coordinates), np.array(y_coordinates), pixelsize, stepsize, helixwidth,
            segfile, new_stepsize=False)
        
            helices = self.enter_helixinfo_into_helices_and_write_boxfiles(helices, micfile, overlap, helixfile,
            interpolated_xcoord, interpolated_ycoord, ipangle, curvature, list(zip(interpolated_xcoord,
            interpolated_ycoord)), list(zip(interpolated_xcoord, interpolated_ycoord)))
        else:
            interpolated_xcoord, interpolated_ycoord, ipangle, curvature = \
            self.interpolate_coordinates(np.array(x_coordinates), np.array(y_coordinates), pixelsize, stepsize, helixwidth,
            segfile, new_stepsize=True)
            
            if self.remove_ends and stepsize != 0:
                remove_end_count = int(round(0.5 * self.segment_size / stepsize))
                
                interpolated_xcoord = interpolated_xcoord[remove_end_count:-remove_end_count]
                interpolated_ycoord = interpolated_ycoord[remove_end_count:-remove_end_count]
                ipangle = ipangle[remove_end_count:-remove_end_count]
                curvature = curvature[remove_end_count:-remove_end_count]
            picked_coordinates = list(zip(interpolated_xcoord, interpolated_ycoord))
            
            if self.perturb_step:
                rand_y_shifts = 0.9 * stepsize / pixelsize * np.array([(np.random.random() - 0.5) for 
                        each_xcoord in interpolated_xcoord[1:-1]])
                centers_x = interpolated_xcoord[:-2]
                centers_y = interpolated_ycoord[:-2]
                hx, hy = self.rotate_coordinates_by_angle(interpolated_xcoord[1:-1], 
                    interpolated_ycoord[1:-1], ipangle[1:-1], centers_x, centers_y)
                hy += rand_y_shifts
                hx, hy = self.rotate_coordinates_by_angle(hx, hy, -ipangle[1:-1], centers_x, centers_y)
                interpolated_xcoord[1:-1] = hx
                interpolated_ycoord[1:-1] = hy
            int_xy_coordinates = list(zip(interpolated_xcoord, interpolated_ycoord))
            
            if len(int_xy_coordinates) >= 3:
                helices = self.enter_helixinfo_into_helices_and_write_boxfiles(helices, micfile, overlap, helixfile,
                interpolated_xcoord, interpolated_ycoord, ipangle, curvature, picked_coordinates, int_xy_coordinates)
            
        return helices
    

    def fill_in_helix_info_from_coordinates(self, helices, segfile, stepsize, pixelsize, helixwidth, micfile, overlap,
    mic_hindex, x_coordinates, y_coordinates):
        helixfile = '{0}{1}{2}_{3:03}{4}box'.format(os.path.abspath(overlap), os.sep,
        os.path.basename(os.path.splitext(segfile)[0]), mic_hindex, os.extsep)

        helix_length = pixelsize * np.sqrt(
            (y_coordinates[-1] - y_coordinates[0]) ** 2 + (x_coordinates[-1] - x_coordinates[0]) ** 2)

        if helix_length < 3 * stepsize:
            log_info = 'Helix from {0} was not further used because length of helix is '.format(helixfile) + \
            'shorter than specified 3 * stepsize ' + \
            '({0} Angstrom < {1} Angstrom). '.format(helix_length, 3 * stepsize) + \
            'No sensible segmentation possible. '

            self.log.ilog(log_info)
        else:
            helices = self.perform_interpolation_perturbation_removal_if_required(helices, segfile, stepsize, pixelsize,
            helixwidth, micfile, overlap, helixfile, x_coordinates, y_coordinates)

        return helices


    def compute_new_coordinates_with_given_stepsize(self, helices, segfile, stepsize, pixelsize, helixwidth, 
        micfile, overlap, helixcoord):
        
        mic_hindex = 0
        for helix in helixcoord:
            xycentercoord = []
            for each_coordinate_line in helix.splitlines():
                xcenter, ycenter = self.convert_coordinate_line_to_xy_coordinates(each_coordinate_line)
                xycentercoord.append((xcenter, ycenter))
                if each_coordinate_line.endswith('-2'):
                    x_coordinates, y_coordinates = list(zip(*xycentercoord))
                    
                    helices = self.fill_in_helix_info_from_coordinates(helices, segfile, stepsize, pixelsize,
                    helixwidth, micfile, overlap, mic_hindex, x_coordinates, y_coordinates)
            
                    mic_hindex += 1

        return helices
    

    def get_picked_coordinates_from_database(self, micfile, db_name, session):
        if session is None:
            session = SpringDataBase().setup_sqlite_db(base, db_name)

        this_mic = session.query(CtfMicrographTable).\
        filter(CtfMicrographTable.micrograph_name.startswith(os.path.basename(os.path.splitext(micfile)[0]))).first()
        
        helices = session.query(HelixTable).filter(HelixTable.mic_id == this_mic.id).order_by(HelixTable.id)
        mic_coord = []
        for each_helix in helices:
            segments = session.query(SegmentTable).\
            filter(SegmentTable.helix_id == each_helix.id).all()

            coordinates = [(each_segment.picked_x_coordinate_A / self.pixelsize, 
            each_segment.picked_y_coordinate_A / self.pixelsize) for each_segment in segments]
            
            mic_coord.append(coordinates)
            
        return session, mic_coord

        
    def get_picked_coordinates_from_file(self, segfile, overlap):
        ifile = open(os.path.abspath(overlap) + os.sep + os.path.basename(segfile), 'r')
        coordinate_lines = ifile.readlines()
        ifile.close()
        if segfile.endswith('box') or segfile.endswith('txt'):
            helixcoord = self.read_coordinate_lines_from_eman_format_and_separate_helices(coordinate_lines)
        elif segfile.endswith('star'):
            helixcoord = \
            self.read_coordinate_lines_from_bsoft_particle_format_and_convert_to_eman_format(coordinate_lines)
            
            if helixcoord == []:
                helixcoord = \
                self.read_coordinate_lines_from_bsoft_filament_format_and_convert_to_eman_format(coordinate_lines)
                
        return helixcoord
    

    def assign_ids_based_on_new_frames(self, inp_stack_ids, inp_mics, mic_coord):
        """
        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> mic_coord = [zip(np.arange(3), np.arange(3)), zip(np.arange(5), np.arange(5))]
        >>> first = s.assign_ids_based_on_new_frames([], list(range(5)), mic_coord)
        >>> first #doctest: +NORMALIZE_WHITESPACE
        [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7,
        0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7]
        >>> s.assign_ids_based_on_new_frames(first, list(range(5)), mic_coord) #doctest: +NORMALIZE_WHITESPACE
        [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 
        0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 
        15, 8, 9, 10, 11, 12, 13, 14, 15, 8, 9, 10, 11, 12, 13, 14, 15, 8, 9, 10, 
        11, 12, 13, 14, 15, 8, 9, 10, 11, 12, 13, 14, 15]
        >>> helices = [1, 2]
        >>> s.assign_ids_based_on_new_frames([], list(range(5)), helices)
        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        """
        all_coord = np.vstack(mic_coord)
        stack_ids = []
        if inp_stack_ids == []:
            max_inp_stack_id = -1
        else:
            max_inp_stack_id = max(inp_stack_ids)

        for each_mic_id, each_inp in enumerate(inp_mics):
            for each_coord_id, each_coord in enumerate(all_coord):
                stack_ids.append(each_coord_id + max_inp_stack_id + 1)
            
        if len(inp_stack_ids) == 0:
            merged_stack_ids = stack_ids
        else:
            merged_stack_ids = inp_stack_ids + stack_ids

        return merged_stack_ids
                    
                
    def single_out(self, pair, stepsize, pixelsize, assigned_multiples):
        """ 
        * Function to single out individual helices from entire micrograph, re-interpolates coordinates\
            according to specified stepsize, 

        #. Input: list of 3-tuples (micrograph file, segment file, overlapping letters), stepsize, pixelsize
        #. Output: list of helices containing micrograph, segment_list, directory, coordinates, inplane_angle
        #. Usage: self.helices = single_out(pair, stepsize, pixelsize)
        """
        self.log.fcttolog()

        helices = []
        session = None
        if assigned_multiples is not None:
            assigned_multiples = dict(assigned_multiples)

        assigned_stack_ids = []
        assigned_helix_ids = []
        for (micfile, segfile, overlap) in pair:
            if segfile.endswith('db'):
                session, mic_coord = self.get_picked_coordinates_from_database(micfile, segfile, session)

                if assigned_multiples is not None:
                    inp_mics = assigned_multiples[micfile]
                else:
                    inp_mics = [micfile]

                assigned_stack_ids = self.assign_ids_based_on_new_frames(assigned_stack_ids, inp_mics, mic_coord)
                assigned_helix_ids = self.assign_ids_based_on_new_frames(assigned_helix_ids, inp_mics, list(range(len(mic_coord))))
                for each_inp_mic in inp_mics:
                    for mic_hindex, each_coord in enumerate(mic_coord):
                        segfile = os.path.splitext(each_inp_mic)[0] + os.extsep + 'box'
                        each_x_coord, each_y_coord = zip(*each_coord)

                        helixfile = '{0}{1}{2}_{3:03}{4}box'.format(os.path.abspath(overlap), os.sep,
                        os.path.basename(os.path.splitext(segfile)[0]), mic_hindex, os.extsep)

                        helices = self.perform_interpolation_perturbation_removal_if_required(helices, segfile,
                        stepsize, pixelsize, self.helixwidth, each_inp_mic, overlap, helixfile, each_x_coord,
                        each_y_coord)
            else:
                helixcoord = self.get_picked_coordinates_from_file(segfile, overlap)
            
                helices = self.compute_new_coordinates_with_given_stepsize(helices, segfile, stepsize,
                pixelsize, self.helixwidth, micfile, overlap, helixcoord)
                
                assigned_stack_ids = None
                                                                                  
        if helices == []:
            msg = 'No helices were segmented because picked helices were too short to be segmented. You ' + \
            'can provide longer helices, choose a shorter step size and/or disable the \'Remove helix ends option \''
            raise ValueError(msg)
            
        return helices, assigned_stack_ids, assigned_helix_ids


    def prepare_segmentation(self):
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        assigned_mics = self.validate_input()
                
        pair = self.assign_reorganize(self.micrograph_files, self.coordinate_files)

        self.helices, assigned_stack_ids, assigned_helix_ids = self.single_out(pair, self.stepsize, self.pixelsize,
        assigned_mics)
        
        return self.helices, assigned_stack_ids, assigned_helix_ids


    def determine_angle_to_rotate_coordinates_to_minimal_slope(self, xcoord, ycoord, helixwidth):
        if np.std(xcoord) < helixwidth/3 or np.std(ycoord) < helixwidth/3:
            if np.std(xcoord) < np.std(ycoord):
                mangle = 90.0
            else: 
                mangle = 0 
        else:
            polyline = np.polyfit((xcoord[0], xcoord[-1]), [ycoord[0], ycoord[-1]], 1)
#            self.log.dlog('xcoord: {0}, ycoord: {1}, polyline: {2}'.format(xcoord, ycoord, polyline[-2]))
            mangle = np.rad2deg(np.arctan(polyline[-2]))

        return mangle


    def rotate_coordinates_by_angle(self, xcoord, ycoord, angle_in_deg, center_x=0, center_y=0):
        """
        * Function to rotate coordinates clockwise by angle_in_deg around origin\
         (in correspondence to EMAN2 convention)

        #. Input: x- and y-array, angle_in_deg to be rotated
        #. Output: rotated x- and y-array
        #. Usage: rotx, roty = rotate_coordinates_by_angle(xcoord, ycoord, angle_in_deg)

        >>> import numpy as np
        >>> np.arange(0, 10)
        array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        >>> np.zeros(10)
        array([ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.])
        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> rot_x, rot_y = s.rotate_coordinates_by_angle(np.arange(10), np.zeros(10), -90.0) 
        >>> np.rint(rot_x)
        array([ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.])
        >>> np.rint(rot_y)
        array([ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9.])
        >>> s.rotate_coordinates_by_angle(np.array([5]), np.array([0]), 180)
        (array([-5.]), array([ -6.12323400e-16]))
        >>> s.rotate_coordinates_by_angle(0, 0, 180, 4, 3)
        (8.0, 6.0)
        """
        c_xcoord = xcoord - center_x
        c_ycoord = ycoord - center_y
        
        angle_in_rad = np.deg2rad(angle_in_deg)
        rotx = np.cos(angle_in_rad)*c_xcoord + np.sin(angle_in_rad)*c_ycoord
        roty = -np.sin(angle_in_rad)*c_xcoord + np.cos(angle_in_rad)*c_ycoord
        
        rotx += center_x
        roty += center_y
        
        return rotx, roty
    
    
    def recalculate_xcoordinate_stepsize_to_perform_interpolation(self, rotated_xcoord, stepsize, new_stepsize):
        if stepsize == 0:
            interpolated_rotated_xcoord = np.linspace(rotated_xcoord.min(), rotated_xcoord.max(), 3)
        elif new_stepsize:
            interpolated_rotated_xcoord = np.arange(rotated_xcoord.min(), rotated_xcoord.max(), stepsize)
        else:
            interpolated_rotated_xcoord = np.linspace(rotated_xcoord.min(), rotated_xcoord.max(), len(rotated_xcoord))

        return interpolated_rotated_xcoord
    

    def perform_interpolation_of_ycoordinates(self, rotated_xcoord, rotated_ycoord, interpolated_rotated_xcoord,
    segfile):

        # spline fit only works for sorted xcoord
        if rotated_xcoord.min() != rotated_xcoord[0]:
            rotated_xcoord = np.flipud(rotated_xcoord)
            rotated_ycoord = np.flipud(rotated_ycoord)

        if 2 <= len(rotated_xcoord) <= 3 or np.std(rotated_ycoord) == 0:
            spline_coefficients = interpolate.splrep(rotated_xcoord, rotated_ycoord, k=1, s=10)
        elif len(rotated_xcoord) >= 4:
            try:
                data_count = len(rotated_ycoord)
                smoothing = max(5, data_count/10)
                spline_coefficients = interpolate.splrep(rotated_xcoord, rotated_ycoord, k=3, s=smoothing)
#                weights = 1/np.std(rotated_ycoord)*np.ones(data_count)
#                smoothing = min(5, data_count/10)
#                spline_coefficients = interpolate.splrep(rotated_xcoord, rotated_ycoord, k=3, s=smoothing, w=weights)
            except(ValueError):
                msg = 'Input coordinates could not be used for interpolating new helix path. Please check integrity ' +\
                'of all helix path coordinates in {0}. The helix path must not follow a U-turn, while '.format(segfile)
                'C- and S-paths are accepted. If in doubt simply select helix coordinates again.'
                raise ValueError(msg)
        else:
            errstring = 'Chosen helix {0} too short to segment compute reliable helixpath'.format(segfile)
            self.log.errlog(errstring)
            raise ValueError(errstring)

        interpolated_rotated_ycoord = interpolate.splev(interpolated_rotated_xcoord, spline_coefficients)

        return interpolated_rotated_ycoord
    

    def perform_interpolation_derivative_for_in_plane_angle_rotation(self, interpolated_rotated_xcoord,
    interpolated_rotated_ycoord, rotated_xcoord, rotated_ycoord, segfile):
        # compute first derivative for in-plane rotation angle determination
        if 2 <= len(interpolated_rotated_xcoord) <= 3:
            spline_coefficients_derivative = interpolate.splrep(interpolated_rotated_xcoord,
            interpolated_rotated_ycoord, k=1, s=50)
        elif len(interpolated_rotated_xcoord) >= 4:
            spline_coefficients_derivative = interpolate.splrep(interpolated_rotated_xcoord,
            interpolated_rotated_ycoord, k=3, s=10)
        else:
            errstring = 'Chosen segmentation step in helix {0} too long to compute reliable helixpath'.format(segfile)
            self.log.errlog(errstring)
            raise ValueError(errstring)

        fitted_1st_derivative = interpolate.splev(interpolated_rotated_xcoord, spline_coefficients_derivative, der=1)
        try:
            fitted_2nd_derivative = interpolate.splev(interpolated_rotated_xcoord, spline_coefficients_derivative,
            der=2)
        except:
            fitted_2nd_derivative = np.zeros(fitted_1st_derivative.size)

        # backflip coordinates to original order
        if rotated_xcoord.min() != rotated_xcoord[0]:
            interpolated_rotated_xcoord = np.flipud(interpolated_rotated_xcoord)
            interpolated_rotated_ycoord = np.flipud(interpolated_rotated_ycoord)
            fitted_1st_derivative = np.flipud(fitted_1st_derivative)
            fitted_2nd_derivative = np.flipud(fitted_2nd_derivative)

        return interpolated_rotated_xcoord, interpolated_rotated_ycoord, fitted_1st_derivative, fitted_2nd_derivative
    

    def write_boxfile(self, interpolated_xcoord=None, interpolated_ycoord=None, segsizepix=None, filename=None):
        """
        * Function to write out new boxparameters

        #. Input: interpolated x- and y-array, segment size (pixel), filename
        #. Output: written file filename
        #. Usage: write_boxfile(interpolated_xcoord, interpolated_ycoord, \
        segsizepix, filename)
        """

        interpolated_xcoord = interpolated_xcoord - segsizepix/2
        interpolated_ycoord = interpolated_ycoord - segsizepix/2

        ofile = open(filename, 'a')
        for index, xcoord in enumerate(interpolated_xcoord):
            interpolated_xcoord[index], interpolated_ycoord[index]
            fivecol = 0
            if index == 0:
                fivecol = -1
            elif index == (len(interpolated_xcoord) - 1):
                fivecol = -2
            ofile.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(int(round(interpolated_xcoord[index])),
            int(round(interpolated_ycoord[index])), segsizepix, segsizepix, fivecol))
        ofile.close()
        
        return filename
    

    def compute_persistence_length_m_from_coordinates_A(self, coord_x_A, coord_y_A):
        """
        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> coord_x_A = np.arange(20) 
        >>> coord_y_A = coord_x_A ** 2
        >>> s.compute_persistence_length_m_from_coordinates_A(coord_x_A, coord_y_A)
        5.1463148473997033e-06
        >>> coord_y_A = coord_x_A ** 1
        >>> s.compute_persistence_length_m_from_coordinates_A(coord_x_A, coord_y_A)
        1.0
        """
        length = 1e-10 * np.sqrt((coord_x_A[0] - coord_x_A[-1]) ** 2 + (coord_y_A[0] - coord_y_A[-1]) ** 2)
        contour = 1e-10 * self.compute_cumulative_distances_from_start_of_helix(coord_x_A, coord_y_A)[-1]

        if length < contour:
            pers_length_m = np.min([1, 1 / (-np.log(2 * (length / contour) ** 2 - 1) / contour)])
        else:
            pers_length_m = 1.0

        return pers_length_m


    def interpolate_coordinates(self, xcoord, ycoord, pixelsize, stepsize, helixwidth, segfile, new_stepsize=True):
        """
        * Function to interpolate x and y coordinates according to new stepsize

        #. Input: xarray and yarray of segment coordinates, pixelsize, stepsize \
        and helixwidth in Angstrom
        #. Output: interpolated x and y-array, computed in-plane angle
        #. Usage: interpolated_xcoord, interpolated_ycoord, ipangle = \
        interpolate_coordinates(xcoord, ycoord, pixelsize, stepsize, helixwidth, segfile)

        >>> import numpy as np
        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> i_xcoord, i_ycoord, in_plane_angle, curvature = \
            s.interpolate_coordinates(np.arange(10), np.arange(10), 1, 0.5, 3, 'test.box')
        >>> np.round(i_xcoord, 2)
        array([-0.  ,  0.35,  0.71,  1.06,  1.41,  1.77,  2.12,  2.47,  2.83,
                3.18,  3.54,  3.89,  4.24,  4.6 ,  4.95,  5.3 ,  5.66,  6.01,
                6.36,  6.72,  7.07,  7.42,  7.78,  8.13,  8.49,  8.84])

        >>> np.round(i_ycoord, 2)
        array([ 0.  ,  0.35,  0.71,  1.06,  1.41,  1.77,  2.12,  2.47,  2.83,
                3.18,  3.54,  3.89,  4.24,  4.6 ,  4.95,  5.3 ,  5.66,  6.01,
                6.36,  6.72,  7.07,  7.42,  7.78,  8.13,  8.49,  8.84])
        >>> np.round(in_plane_angle, 2)
        array([ 135.,  135.,  135.,  135.,  135.,  135.,  135.,  135.,  135.,
                135.,  135.,  135.,  135.,  135.,  135.,  135.,  135.,  135.,
                135.,  135.,  135.,  135.,  135.,  135.,  135.,  135.])
                
        >>> interpolated_x_coordinates, interpolated_y_coordinates, in_plane_rotation_angle, curvature = \
                                    Segment().interpolate_coordinates(np.arange(10), 2*np.arange(10), 1, 3, 3, 'test.box')
        >>> np.round(interpolated_x_coordinates, 1)
        array([-0. ,  1.3,  2.7,  4. ,  5.4,  6.7,  8. ])
        
        >>> np.round(interpolated_y_coordinates, 1)
        array([  0. ,   2.7,   5.4,   8. ,  10.7,  13.4,  16.1])
        
        >>> in_plane_rotation_angle
        array([ 153.43494882,  153.43494882,  153.43494882,  153.43494882,
                153.43494882,  153.43494882,  153.43494882])

        >>> # helix parallel to image rows
        ...
        >>> interpolated_x_coordinates, interpolated_y_coordinates, in_plane_rotation_angle, curvature = \
                                    Segment().interpolate_coordinates(np.arange(10), np.zeros(10), 1, 3, 3, 'test.box')
        >>> interpolated_x_coordinates
        array([ 0.,  3.,  6.])
        
        >>> np.round(interpolated_y_coordinates, 2)
        array([ 0.,  0.,  0.])
        
        >>> in_plane_rotation_angle
        array([ 90.,  90.,  90.])
        >>> # helix parallel to image columns
        ...
        >>> interpolated_x_coordinates, interpolated_y_coordinates, in_plane_rotation_angle, curvature = \
                                    Segment().interpolate_coordinates(np.zeros(10), np.arange(10), 10, 20, 30, 'test.box')
        
        >>> np.round(interpolated_y_coordinates, 0)
        array([-0.,  2.,  4.,  6.,  8.])
        
        >>> in_plane_rotation_angle
        array([ 180.,  180.,  180.,  180.,  180.])
        
        >>> np.round(interpolated_x_coordinates, 2)
        array([ 0.,  0.,  0.,  0.,  0.])

        """
        xcoord_A = xcoord * pixelsize
        ycoord_A = ycoord * pixelsize
        
        flat_angle = self.determine_angle_to_rotate_coordinates_to_minimal_slope(xcoord_A, ycoord_A, helixwidth)
        rotated_xcoord, rot_ycoord = self.rotate_coordinates_by_angle(xcoord_A, ycoord_A, flat_angle)
        
        if len(xcoord_A) > 4 and np.std(rot_ycoord) < 100:
            poly = np.polyfit(rotated_xcoord, rot_ycoord, 3)
            rotated_ycoord = np.polyval(poly, rotated_xcoord)
        else:
            rotated_ycoord = rot_ycoord

#        self.log.ilog('Coordinates are rotated by {0} degrees'.format(np.degrees(flat_angle)))

        interpolated_rotated_xcoord = self.recalculate_xcoordinate_stepsize_to_perform_interpolation(rotated_xcoord,
        stepsize, new_stepsize)
        
        interpolated_rotated_ycoord = self.perform_interpolation_of_ycoordinates(rotated_xcoord, rotated_ycoord,
        interpolated_rotated_xcoord, segfile)
        
        interpolated_rotated_xcoord, interpolated_rotated_ycoord, fitted_1st_derivative, fitted_2nd_derivative = \
        self.perform_interpolation_derivative_for_in_plane_angle_rotation(interpolated_rotated_xcoord,
        interpolated_rotated_ycoord, rotated_xcoord, rotated_ycoord, segfile)
        
        # backrotate coordinates
        interpolated_xcoord_A, interpolated_ycoord_A = self.rotate_coordinates_by_angle(interpolated_rotated_xcoord,
        interpolated_rotated_ycoord, -flat_angle)
        
        ipangle = 90 + np.rad2deg(np.arctan(fitted_1st_derivative)) + flat_angle
        pers_length = self.compute_persistence_length_m_from_coordinates_A(interpolated_xcoord_A, interpolated_ycoord_A)
        curvature = len(interpolated_rotated_xcoord) * [pers_length]

        interpolated_xcoord = interpolated_xcoord_A / pixelsize
        interpolated_ycoord = interpolated_ycoord_A / pixelsize
        
        return interpolated_xcoord, interpolated_ycoord, ipangle, curvature
    
    
class SegmentStraighten(SegmentInterpolation):
    def select_coordinates_within_segment_dimensions(self, coordinates, current_center, segment_size_pix):
        """
        >>> from spring.segment2d.segment import Segment
        >>> Segment().select_coordinates_within_segment_dimensions(zip(np.arange(20.), np.arange(20., 40.)), (10, 30), 10.0)
        (array([  6.,   7.,   8.,   9.,  10.,  11.,  12.,  13.,  14.]), array([ 26.,  27.,  28.,  29.,  30.,  31.,  32.,  33.,  34.]))
        """
        x_coordinates, y_coordinates = list(zip(*coordinates))
        x_coordinates = np.array(x_coordinates)
        y_coordinates = np.array(y_coordinates)
        
        x_center, y_center = current_center
        x_left_corner = x_center - segment_size_pix/2 
        y_left_corner = y_center - segment_size_pix/2
        x_right_corner = x_center + segment_size_pix/2
        y_right_corner = y_center + segment_size_pix/2
        
        x_indices = np.arange(x_coordinates.size)
        y_indices = np.arange(y_coordinates.size)
        within_xlimits = x_indices[(x_coordinates > x_left_corner) & (x_coordinates < x_right_corner)]
        within_ylimits = y_indices[(y_coordinates > y_left_corner) & (y_coordinates < y_right_corner)]
        
        within_x_and_y = np.intersect1d(within_xlimits, within_ylimits)
        
        filtered_x = np.array([x_coordinates[each_index] for each_index in within_x_and_y])
        filtered_y = np.array([y_coordinates[each_index] for each_index in within_x_and_y])
        
        return filtered_x, filtered_y
        
    
    def compute_bending_path_row_wise(self, length, polyfit, angle):
        """
        >>> from spring.segment2d.segment import Segment
        >>> Segment().compute_bending_path_row_wise(20.0, [1/20.0, -1.0, 15.0], 0)
        (array([ 15.  ,  14.05,  13.2 ,  12.45,  11.8 ,  11.25,  10.8 ,  10.45,
                10.2 ,  10.05,  10.  ,  10.05,  10.2 ,  10.45,  10.8 ,  11.25,
                11.8 ,  12.45,  13.2 ,  14.05]), array([  0.,   1.,   2.,   3.,   4.,   5.,   6.,   7.,   8.,   9.,  10.,
                11.,  12.,  13.,  14.,  15.,  16.,  17.,  18.,  19.]), array([ 315.        ,  318.0127875 ,  321.34019175,  325.0079798 ,
                329.03624347,  333.43494882,  338.19859051,  343.30075577,
                348.69006753,  354.28940686,  360.        ,    5.71059314,
                 11.30993247,   16.69924423,   21.80140949,   26.56505118,
                 30.96375653,   34.9920202 ,   38.65980825,   41.9872125 ]))

        >>> Segment().compute_bending_path_row_wise(20.0, [1/20.0, -1.0, 15.0], 90)
        (array([ 20.,  19.,  18.,  17.,  16.,  15.,  14.,  13.,  12.,  11.,  10.,
                 9.,   8.,   7.,   6.,   5.,   4.,   3.,   2.,   1.]), array([ 15.  ,  14.05,  13.2 ,  12.45,  11.8 ,  11.25,  10.8 ,  10.45,
                10.2 ,  10.05,  10.  ,  10.05,  10.2 ,  10.45,  10.8 ,  11.25,
                11.8 ,  12.45,  13.2 ,  14.05]), array([ 225.        ,  228.0127875 ,  231.34019175,  235.0079798 ,
                239.03624347,  243.43494882,  248.19859051,  253.30075577,
                258.69006753,  264.28940686,  270.        ,  275.71059314,
                281.30993247,  286.69924423,  291.80140949,  296.56505118,
                300.96375653,  304.9920202 ,  308.65980825,  311.9872125 ]))
        """
        straight_rows = np.arange(float(length))
        straight_cols = np.polyval(polyfit, straight_rows)
        
        spline_coefficients = interpolate.splrep(straight_rows, straight_cols, k=3, s=10)
        fitted_first_derivative = interpolate.splev(straight_rows, spline_coefficients, der=1)

        inplane_angles = (np.rad2deg(np.arctan(fitted_first_derivative)) - angle)%360
        
        cols, rows = self.rotate_coordinates_by_angle(straight_cols, straight_rows, -angle, center_x=length/2,
        center_y=length/2)
        
        return cols, rows, inplane_angles
    
    
    def shift_and_rotate_image_linear(self, image, inplane_angle, each_x, each_y):
        t_shift = Transform({'type':'SPIDER', 'psi':0.0, 'tx':each_x, 'ty':each_y, 'scale':1.0})
        t_rot = Transform({'type':'SPIDER', 'psi':inplane_angle, 'tx':0.0, 'ty':0.0, 'scale':1.0})
        composite_transform = t_rot * t_shift
        trans_rot_image = image.rot_scale_trans_background(composite_transform)
        
        return trans_rot_image
    
    
    def convert_rotate_shift_to_shift_rotate_order(self, inplane_angle, each_x, each_y):
        """
        >>> from spring.segment2d.segment import Segment
        >>> a, b, c = Segment().convert_shift_rotate_to_rotate_shift_order(50,22,2)
        >>> Segment().convert_rotate_shift_to_shift_rotate_order(a, b, c)
        (49.99999868188684, 22.0, 2.0)
        """
        psi, tx, ty = self.convert_shift_rotate_to_rotate_shift_order(-inplane_angle, each_x, each_y)
        
        return (-psi) % 360, tx, ty


    def convert_shift_rotate_to_rotate_shift_order(self, inplane_angle, each_x, each_y):
        """
        >>> from spring.segment2d.segment import Segment
        >>> Segment().convert_shift_rotate_to_rotate_shift_order(50,22,2)
        (49.99999868188683, 15.673417091369629, -15.567402839660645)
        """
        t_shift = Transform({'type':'SPIDER', 'psi':0.0, 'tx':each_x, 'ty':each_y, 'scale':1.0})
        t_rot = Transform({'type':'SPIDER', 'psi':inplane_angle, 'tx':0.0, 'ty':0.0, 'scale':1.0})
        composite_transform = t_rot * t_shift
        t = composite_transform.get_params('spider')

        return t['psi'], t['tx'], t['ty']


    def shift_and_rotate_image(self, image, inplane_angle, each_x, each_y):
        angle, tx, ty = self.convert_shift_rotate_to_rotate_shift_order(inplane_angle, each_x, each_y)
        trans_rot_image = image.rot_scale_trans2D_background(angle, tx, ty, 1.0)
        
        return trans_rot_image
    
    
    def shift_and_rotate_image_gridding(self, image, inplane_angle, each_x, each_y):
        trans_rot_image, kb = prepi(image)
        angle, tx, ty = self.convert_shift_rotate_to_rotate_shift_order(inplane_angle, each_x, each_y)
        trans_rot_image = trans_rot_image.rot_scale_conv_new_background(np.deg2rad(angle), tx, ty, kb, 1.0)
        
        return trans_rot_image
    
    
    def straighten_segment(self, helix_img, img_size, cols, rows, inplane_angles, mode='straighten'):
        if mode == 'bend':
            pd_img_size = 2*img_size
        else:
            pd_img_size = int(1.2*img_size)
        helix_pd = Util.pad(helix_img, pd_img_size, pd_img_size, 1, 0, 0, 0, '0')
            
        bent_helix = model_blank(img_size, img_size)
        for each_index, each_row in enumerate(rows):
            each_col = cols[each_index]
            each_angle = inplane_angles[each_index]
            if mode == 'bend':
                helix_wi = Util.window(helix_pd, img_size, img_size, 1, 0, int(each_row - img_size/2), 0)
                helix_rot = rot_shift2D(helix_wi, each_angle, (each_col - img_size/2), 0)
            elif mode == 'straighten':
                helix_rot = self.shift_and_rotate_image(helix_pd, -each_angle, -(each_col - img_size/2), 
                                                        -(each_row - img_size/2))
                
                helix_rot = Util.window(helix_rot, img_size, img_size, 1, 0, 0, 0)
            bent_row = helix_rot.get_row(img_size / 2)
            bent_helix.set_row(bent_row, each_index)
        
        return bent_helix
    
    
    def compute_rotated_helix_path_on_segment_locally(self, current_coordinates, cut_coordinates, current_inplane_angle,
    large_segsizepix, filtered_x, filtered_y):
        """
        >>> from spring.segment2d.segment import Segment
        >>> Segment().compute_rotated_helix_path_on_segment_locally((17.0, 87.0), (17, 87), 180.0, 10.0, np.arange(10, 20), np.arange(80, 90))
        (array([ 12.,  11.,  10.,   9.,   8.,   7.,   6.,   5.,   4.,   3.]), array([ 12.,  11.,  10.,   9.,   8.,   7.,   6.,   5.,   4.,   3.]))
        """
        center_x, center_y = current_coordinates
        cut_center_x, cut_center_y = cut_coordinates
        local_x = filtered_x - cut_center_x + large_segsizepix / 2
        local_y = filtered_y - cut_center_y + large_segsizepix / 2
        x_offset = center_x - cut_center_x
        y_offset = center_y - cut_center_y
        
        rot_local_x, rot_local_y = self.rotate_coordinates_by_angle(local_x, local_y, current_inplane_angle,
        large_segsizepix / 2 + x_offset, large_segsizepix / 2 + y_offset)
        
        return rot_local_x, rot_local_y
    


    def set_polyfit_variable(self, large_segsizepix, current_inplane_angle, second_order_fit):
        first_order_from_ip_angle = np.tan(np.deg2rad(-current_inplane_angle - 90))
        zero_order = large_segsizepix / 2 - (first_order_from_ip_angle * large_segsizepix / 2)
        polyfit = [second_order_fit, first_order_from_ip_angle, zero_order]
        return polyfit

    def fit_square_function_path_of_coordinates(self, large_segsizepix, helix_coordinates, current_coordinates,
    cut_coordinates, current_inplane_angle, second_order_fit=None):
        filtered_x, filtered_y = self.select_coordinates_within_segment_dimensions(helix_coordinates,
        current_coordinates, 1.5 * large_segsizepix)
        
        rot_local_x, rot_local_y = self.compute_rotated_helix_path_on_segment_locally(current_coordinates,
        cut_coordinates, current_inplane_angle, large_segsizepix, filtered_x, filtered_y)
        
        if second_order_fit is None:
            if rot_local_y != []:
                polyfit = np.polyfit(rot_local_y, rot_local_x, 2)
            else:
                polyfit = self.set_polyfit_variable(large_segsizepix, current_inplane_angle, second_order_fit=0)
        elif second_order_fit is not None:
            corrected_local_x = rot_local_x - (second_order_fit * rot_local_y**2)
            if rot_local_y != [] or corrected_local_x != []:
                polyfit = np.polyfit(rot_local_y, corrected_local_x, 1)
                polyfit = np.insert(polyfit, 0, second_order_fit)
            else:
                polyfit = self.set_polyfit_variable(large_segsizepix, current_inplane_angle, second_order_fit)
            
        return polyfit, filtered_x, filtered_y


    def unbend_segment_using_coordinates(self, segment, large_segsizepix, helix_coordinates, current_coordinates,
    cut_coordinates, current_inplane_angle, second_order_fit=None):
        polyfit, filtered_x, filtered_y = self.fit_square_function_path_of_coordinates(large_segsizepix,
        helix_coordinates, current_coordinates, cut_coordinates, current_inplane_angle, second_order_fit)
        
        cols, rows, inplane_angles = self.compute_bending_path_row_wise(large_segsizepix, polyfit,
        current_inplane_angle)
        
        straightened_segment = self.straighten_segment(segment, large_segsizepix, cols, rows, inplane_angles)
        central_inplane_angle = inplane_angles[len(inplane_angles)/2]
        
        return straightened_segment, polyfit, central_inplane_angle
        
