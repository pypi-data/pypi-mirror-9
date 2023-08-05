#!/usr/bin/env python
"""
Test module to check segment module
"""
from EMAN2 import EMData, EMUtil, Util, EMAN2Ctf, EMNumPy
from filter import filt_ctf
from fundamentals import fshift, rot_shift2D
from glob import glob
from multiprocessing import cpu_count
import os
import shutil
from spring.csinfrastr.csdatabase import SpringDataBase, base, SegmentTable
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.micprgs.micctfdetermine import MicCtfDetermine
from spring.segment2d.segment import Segment, SegmentPar
from spring.segment2d.segmentexam import SegmentExam
from spring.springgui.spring_launch import DataBaseUpdate
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segmentexam import HelixProjectionPreparation
from spring.tests.segment3d.test_segmentrefine3d import TestSegmentRefine3dMain
from utilities import model_gauss_noise

from nose.tools import raises
from scipy.interpolate.fitpack2 import InterpolatedUnivariateSpline
from scipy.ndimage.interpolation import map_coordinates

import numpy as np


class MicrographHelixPreparation(HelixProjectionPreparation):
    def prepare_ctf_micrograph(self, micrograph_file, avg_defocus, cs, voltage, pixelsize, ampcont, astigmatism,
    astigmatism_angle):
        micrograph = MicrographHelixPreparation().prepare_dummy_helix()
        dimension = micrograph.get_xsize()
        offset = (dimension - 1000) / 2
        micrograph = Util.pad(micrograph, 1000, 1000, 1, offset, offset, 0, '0')
        noise = model_gauss_noise(0.1, 1000, 1000)
        micrograph += noise
        
        ctf = EMAN2Ctf()
                ctf.from_dict({'defocus':avg_defocus * 1e-4, 'cs':cs, 'voltage':voltage, 'apix':pixelsize, 'ampcont':ampcont,
        'bfactor':0.0, 'dfdiff':astigmatism * 1e-4 , 'dfang':astigmatism_angle})
        
        ctf_micrograph = filt_ctf(micrograph, ctf)
        ctf_micrograph.write_image(micrograph_file)
        
    def prepare_helix_coordinate_file(self, filename='test_mic.box'):
        self.segment_size_in_pixel = 100
        self.helix_coordinate_file = filename

        if os.path.exists(filename):
            os.remove(filename)

        if self.helix_coordinate_file.endswith('box'):
            Segment().write_boxfile(self.x_coordinates_array, self.y_coordinates_array, self.segment_size_in_pixel,
            self.helix_coordinate_file)
            
        elif self.helix_coordinate_file.endswith('star'):
            self.prepare_helix_coordinate_bsoft_file(self.x_coordinates_array, self.y_coordinates_array,
            self.segment_size_in_pixel, self.helix_coordinate_file)


    def add_segmented_particle_entry(self, x_coordinates, y_coordinates, segment_size_in_pixel):
        lines = '_particle.select\n'
        angles = np.rad2deg(np.arctan(x_coordinates / y_coordinates))
        for each_index, each_x_coordinate in enumerate(x_coordinates):
            each_y_coordinate = y_coordinates[each_index]
            each_angle = angles[each_index]
            
            particle_coordinate_line = \
            '{id:5}{hel_id:5}{zero:8}{one:8.4f}{x_coord:8.2f}{y_coord:8.2f}{zero:8.2f}{size:8.3f}{size:8.3f}{zero:8.3f}{one:8.4f}{zero:8.4f}{zero:8.4f}{angle:8.2f}{one:8.4f}{hel_id:5}\n'.\
            format(id=each_index + 1, hel_id=1, zero=0, one=1.0, x_coord=each_x_coordinate, y_coord=each_y_coordinate,
            size=segment_size_in_pixel / 2, angle=each_angle)
            
            lines += particle_coordinate_line
        
        end_lines = '\n\nloop_\n'
        lines += end_lines
        
        return lines
    

    def add_filament_entry(self, lines, x_coordinates, y_coordinates):
        more_lines = '_filament.id\n_filament.node_id\n_filament.x\n_filament.y\n_filament.z\n'
        lines += more_lines
        filament_coordinate_line_start = '{hel_id:7}{point_id:7}{x_coord:8.2f}{y_coord:8.2f}{zero:8.2f}\n'.\
        format(hel_id=1, point_id=1, x_coord=x_coordinates[0], y_coord=y_coordinates[0], zero=0.0)
        
        filament_coordinate_line_end = '{hel_id:7}{point_id:7}{x_coord:8.2f}{y_coord:8.2f}{zero:8.2f}\n'.\
        format(hel_id=1, point_id=2, x_coord=x_coordinates[-1], y_coord=y_coordinates[-1], zero=0.0)
        
        lines += filament_coordinate_line_start
        lines += filament_coordinate_line_end
        lines += '\n\n'
        
        return lines
    


    def prepare_bsoft_lines(self, x_coordinates, y_coordinates, segment_size_in_pixel):
        """
        >>> from spring.tests.segment2d.test_segment import MicrographHelixPreparation
        >>> m = MicrographHelixPreparation()
        >>> m.prepare_bsoft_lines(np.arange(1000.0, 1005.0), np.arange(1000.0, 1005.0), 600) #doctest: +NORMALIZE_WHITESPACE
        '_particle.select\\n    
        1    1       0  1.0000 1000.00 1000.00    0.00 300.000 300.000   0.000  1.0000  0.0000  0.0000   45.00  1.0000    1\\n    
        2    1       0  1.0000 1001.00 1001.00    0.00 300.000 300.000   0.000  1.0000  0.0000  0.0000   45.00  1.0000    1\\n    
        3    1       0  1.0000 1002.00 1002.00    0.00 300.000 300.000   0.000  1.0000  0.0000  0.0000   45.00  1.0000    1\\n    
        4    1       0  1.0000 1003.00 1003.00    0.00 300.000 300.000   0.000  1.0000  0.0000  0.0000   45.00  1.0000    1\\n    
        5    1       0  1.0000 1004.00 1004.00    0.00 300.000 300.000   0.000  1.0000  0.0000  0.0000   45.00  1.0000    
        1\\n\\n\\nloop_\\n_filament.id\\n_filament.node_id\\n_filament.x\\n_filament.y\\n_filament.z\\n      
        1      1 1000.00 1000.00    0.00\\n      1      2 1004.00 1004.00    0.00\\n\\n\\n'
        """
        lines = self.add_segmented_particle_entry(x_coordinates, y_coordinates, segment_size_in_pixel)
        lines = self.add_filament_entry(lines, x_coordinates, y_coordinates)
        
        return lines
    

    def prepare_helix_coordinate_bsoft_file(self, x_coordinates, y_coordinates, segment_size_in_pixel, filename):
        
        lines = self.prepare_bsoft_lines(x_coordinates, y_coordinates, segment_size_in_pixel)
        
        bsoft_file = open(filename, 'w')
        bsoft_file.write(lines)
        bsoft_file.close()
        
        return lines
    
        
    def prepare_dummy_helix(self, angle=45, shift_in_angstrom=30):
        self.width_of_helix_in_angstrom = 300
        self.micrograph_size_in_angstrom = 1000
        self.pixelsize = 5
        self.width_of_helix_in_pixel = self.width_of_helix_in_angstrom / self.pixelsize
        self.micrograph_size_in_pixel = self.micrograph_size_in_angstrom / self.pixelsize
        self.segment_size_in_pixels = self.micrograph_size_in_pixel
        self.make_empty_segment()
        self.compute_intersect_sine_waves()
        self.helix_segment_img = self.add_intersects_to_segment_image()
        
        self.helix_micrograph = self.helix_segment_img
        self.shift_in_pixel = shift_in_angstrom / self.pixelsize

        self.helix_micrograph = fshift(self.helix_micrograph, self.shift_in_pixel)
        if angle != 0:
            self.helix_micrograph = rot_shift2D(self.helix_micrograph, angle)

        return self.helix_micrograph


    def prepare_helix_on_micrograph(self):
        """
        * Function to prepare a dummy helix on micrograph
        """
        self.prepare_dummy_helix()
        
        self.add_noise_to_helix_micrograph()
        
        self.micrograph_test_file = 'test_mic.hdf'
        self.test_frame_count = 5
        self.helix_micrograph.write_image(self.micrograph_test_file)
        self.micrograph_test_file = os.path.abspath('test_mic.hdf')

        self.x_coordinates_array = self.y_coordinates_array = np.array([100, 90, 80, 70, 60])
        self.prepare_helix_coordinate_file()
        
        return self.helix_micrograph
    

    def setup_helix_or_particle_dimensions(self):
        self.feature_set.parameters['Segment coordinates'] = self.helix_coordinate_file
        self.feature_set.parameters['Estimated helix width in Angstrom'] = int(1.2 * self.width_of_helix_in_angstrom)
        self.feature_set.parameters['Segment size in Angstrom'] = int(self.segment_size_in_pixel * self.pixelsize)
        self.feature_set.parameters['Step size of segmentation in Angstrom'] = int(50)
        self.feature_set.parameters['Perturb step option'] = False
        self.feature_set.parameters['Rotation option'] = False
        self.feature_set.parameters['Unbending option'] = False
        self.feature_set.parameters['Remove helix ends option'] = False
        
        
    def setup_of_common_non_mpi_parameters(self):
        self.feature_set.parameters['Micrographs'] = self.micrograph_test_file
        self.feature_set.parameters['Image output stack'] = 'test_output_stack.hdf'
        self.feature_set.parameters['Spring database option'] = True
        self.feature_set.parameters['spring.db file'] = os.path.join(os.pardir, 'spring.db')
            
        self.feature_set.parameters['Pixel size in Angstrom'] = float(self.pixelsize)
        self.setup_helix_or_particle_dimensions()
        self.feature_set.parameters['CTF correct option'] = False
        self.feature_set.parameters['CTFFIND or CTFTILT'] = 'ctftilt'
        self.feature_set.parameters['convolve or phase-flip'] = 'phase-flip'  # 'convolve'
        self.feature_set.parameters['Astigmatism correction'] = True
        
        self.feature_set.parameters['Frame processing option'] = False
        self.feature_set.parameters['First and last frame'] = (0, self.test_frame_count - 1)
        self.feature_set.parameters['Refinement.db to process'] = 'refinement.db'

        self.feature_set.parameters['Invert option'] = False
        self.feature_set.parameters['Normalization option'] = True
        self.feature_set.parameters['Row normalization option'] = True
        self.feature_set.parameters['Binning option'] = True
        self.feature_set.parameters['Binning factor'] = 6
        
        self.setup_of_selection_parameters()
        
        
    def setup_of_selection_parameters(self):
        self.feature_set.parameters['Micrographs select option'] = False
        self.feature_set.parameters['Include or exclude micrographs'] = 'include'
        self.feature_set.parameters['Micrographs list'] = '1'
        
        self.feature_set.parameters['Helices select option'] = False
        self.feature_set.parameters['Include or exclude helices'] = 'include'
        self.feature_set.parameters['Helices list'] = '1'
        
        self.feature_set.parameters['Straightness select option'] = False
        self.feature_set.parameters['Include or exclude straight helices'] = 'include'
        self.feature_set.parameters['Persistence length range'] = (0, 80)
        
        self.feature_set.parameters['Defocus select option'] = False
        self.feature_set.parameters['Include or exclude defocus range'] = 'include'
        self.feature_set.parameters['Defocus range'] = (0, 23000)
        
        self.feature_set.parameters['Astigmatism select option'] = False
        self.feature_set.parameters['Include or exclude astigmatic segments'] = 'include'
        self.feature_set.parameters['Astigmatism range'] = (0, 10000)
        

class TestSegmentComparison(MicrographHelixPreparation, Segment):
#     def compare_centered_segments(self):
#         linear_fit_dummy = np.polyfit(self.x_coordinates_array, self.y_coordinates_array, 1)
# 
#         self.get_centered_coordinates()
#         linear_fit_centered = np.polyfit(self.centered_x_coordinates_array, self.centered_y_coordinates_array, 1)
#         distance_between_old_and_new_coordinates = abs(linear_fit_centered[1] - linear_fit_dummy[1])*np.sin(np.pi/4)
# #        sys.stderr.write('{0}{1}{2}'.format(linear_fit_dummy, linear_fit_centered, distance_between_old_and_new_coordinates))
#         sys.stderr.write('{0}<{1}<{2}'.format(self.shift_in_pixel - 0.8, distance_between_old_and_new_coordinates,
#         self.shift_in_pixel + 0.8))
#         assert self.shift_in_pixel - 0.8 < distance_between_old_and_new_coordinates < self.shift_in_pixel + 0.8
# 
#     def get_centered_coordinates(self):
#         self.centered_x_coordinates_array, self.centered_y_coordinates_array = \
#                         list(zip(*self.helices[0].coordinates))

    def check_number_of_segments_equals_one(self):
        number_of_segments = EMUtil.get_image_count('test_output_stack.hdf')
        assert number_of_segments == 1

#     def compute_difference_between_centered_and_uncentered(self):
#         self.get_centered_coordinates()
#         self.avg_difference_x = abs(np.mean(self.centered_x_coordinates_array) - np.mean(self.x_coordinates_array))
#         self.avg_difference_y = abs(np.mean(self.centered_y_coordinates_array) - np.mean(self.y_coordinates_array))


class TestSegment(TestSegmentComparison):
    def setup_no_helix_generation(self):
        self.feature_set = SegmentPar()
        self.setup_of_common_non_mpi_parameters()
        self.cpu_count = min(8, cpu_count())
        self.feature_set.parameters['MPI option'] = False
        self.feature_set.parameters['Number of CPUs'] = self.cpu_count
        super(TestSegment, self).__init__(self.feature_set)
        

    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.prepare_helix_on_micrograph()
        self.setup_no_helix_generation()
        
#        self.tscd = TestMicCtfDetermine()
#        self.tscd.setup()
#        self.tscd.do_test_case_scd1()
        
#        os.rename('spring.db', os.path.join(os.path.pardir, 'spring.db'))
        
        self.session = SpringDataBase().setup_sqlite_db(base, os.path.join(os.pardir, 'spring.db'))
        self.session.commit()
        self.session.close()

        
    def prepare_spring_database_ctf_entries(self):
        self.pixelsize = 5.0
        self.avg_defocus = 40000.0
        self.voltage = 200
        self.cs = 2.0
        self.ampcont = 0.1
        self.astigmatism = 5000.0
        self.astigmatism_angle = 33.0
        
        ctf_params = MicCtfDetermine().make_ctf_parameter_named_tuple()
        ctf_parameters = ctf_params._make([self.voltage, self.cs, self.ampcont, self.pixelsize])
        
        ctffind_params = MicCtfDetermine().make_ctffind_parameters_named_tuple()
        ctffind_parameters = ctffind_params._make([35000, 45000, 33.0, 10000])
        
        ctftilt_params = MicCtfDetermine().make_ctftilt_parameters_named_tuple()
        ctftilt_parameters = ctftilt_params._make([36000, 44000, 30.0, 0, 0, 10000, 300, 300])
        
        session = SpringDataBase().setup_sqlite_db(base, os.path.join(os.pardir, 'spring.db'))
        
        session = MicCtfDetermine().enter_ctffind_values_in_database(session, os.path.abspath(self.micrograph_test_file),
        self.pixelsize, ctf_parameters, ctffind_parameters)
        
        session = MicCtfDetermine().enter_ctftilt_values_in_database(session, os.path.abspath(self.micrograph_test_file),
        self.pixelsize, ctftilt_parameters)
        
        session.commit()
        session.close()
        
        
    def remove_coordfile_micrographdir_and_linkfiles(self, helix_coordinate_file, micrograph_test_file):
        os.remove(helix_coordinate_file)
        os.remove('test_output_stack.hdf')
        micrograph_directory = micrograph_test_file.split(os.extsep)[0]
        files_in_dir = glob('{0}{1}*'.format(micrograph_directory, os.sep))
        for each_file in files_in_dir:
            os.remove(each_file)
        os.rmdir(micrograph_directory)
        

    def teardown(self):
        database_file = os.path.join(os.path.pardir, 'spring.db')
        os.remove(database_file)
        try:
            os.remove(os.path.basename(database_file))
            os.remove(self.micrograph_test_file)
        except:
            comment = 'This is only relevant for running test_segmentctfapply'
         
        os.remove('test_output_stack-6xbin.hdf')
         
        self.remove_coordfile_micrographdir_and_linkfiles(self.helix_coordinate_file, self.micrograph_test_file)
 
        self.testingdir.remove()
        

class TestSegmentMain(TestSegment):
    def do_test_case_seg1(self):
        """
        Segment test box files that contain a set of overlapping boxes
        """
        self.segment()


class TestSegmentMore(TestSegment):
    def do_test_case_seg0(self):
        """
        Segment test box files that contain a set of overlapping boxes including segment database update
        """
        self.segment()
        DataBaseUpdate().update_spring_db('spring.db', 'spring_up.db')
        os.remove('spring_up.db')
 
 
    def do_test_case_seg2(self):
        """
        Segment test box files that contain only start and end point of helix
        """
        self.x_coordinates_array = self.y_coordinates_array = np.array([100, 60])
        self.prepare_helix_coordinate_file()
        self.segment()
          
 
    def do_test_case_seg3(self):
        """
        Segment test box files with a segmentation stepsize of 0
        """
        self.feature_set.parameters['Step size of segmentation in Angstrom'] = 0
        super(TestSegment, self).__init__(self.feature_set)
        self.x_coordinates_array = self.y_coordinates_array = np.array([100, 60])
        self.prepare_helix_coordinate_file()
        self.segment()
        self.check_number_of_segments_equals_one()
 
 
    def do_test_case_seg4(self):
        """
        Segment test box files that are aligned with micrograph columnns
        """
        self.helix_micrograph = rot_shift2D(self.helix_micrograph, -45)
        self.helix_micrograph.write_image(self.micrograph_test_file)
        self.x_coordinates_array = np.array([100, 100, 100, 100, 100])
        self.y_coordinates_array = np.array([100, 90, 80, 70, 60])
        self.prepare_helix_coordinate_file()
        self.segment()
          
  
    def do_test_case_seg5(self):
        """
        Segment test box files that are aligned with micrograph rows
        """
        self.helix_micrograph = rot_shift2D(self.helix_micrograph, 45)
        self.helix_micrograph.write_image(self.micrograph_test_file)
        self.x_coordinates_array = np.array([100, 90, 80, 70, 60])
        self.y_coordinates_array = np.array([100, 100, 100, 100, 100])
        self.prepare_helix_coordinate_file()
        self.segment()
          
  
    def do_test_case_seg6(self):
        """
        Segment test bsoft star files that contain a set of overlapping boxes
        """
        self.x_coordinates_array = self.y_coordinates_array = np.array([100, 90, 80, 70, 60])
        self.star_filename = 'test_mic.star'
        self.prepare_helix_coordinate_file(self.star_filename)
        self.feature_set.parameters['Segment coordinates'] = self.star_filename
        super(TestSegment, self).__init__(self.feature_set)
          
        current_directory = os.path.abspath(os.curdir)
        self.directory = 'test_segmentdir'
        os.mkdir(self.directory)
        os.chdir(self.directory)
        self.segment()
        os.chdir(current_directory)
        EndToEndTest().cleanup_working_directory(self.directory)
          
        os.remove('test_mic.box')
          
    def do_test_case_seg7(self):
        """
        Segment test bsoft star filament coordinates that contain a set of overlapping boxes
        """
        self.x_coordinates_array = self.y_coordinates_array = np.array([100, 90, 80, 70, 60])
        self.star_filename = self.helix_coordinate_file = 'test_mic.star'
        filament_lines = self.add_filament_entry('', self.x_coordinates_array, self.y_coordinates_array)
        coord_file = open(self.star_filename, 'w')
        coord_file.write(filament_lines)
        coord_file.close()
          
        self.feature_set.parameters['Segment coordinates'] = self.star_filename
        super(TestSegment, self).__init__(self.feature_set)
          
        current_directory = os.path.abspath(os.curdir)
        self.directory = 'test_segmentdir'
        os.mkdir(self.directory)
        os.chdir(self.directory)
        self.segment()
        os.chdir(current_directory)
        EndToEndTest().cleanup_working_directory(self.directory)
          
        os.remove('test_mic.box')
  
  
    def do_test_case_seg8(self):
        """
        Segment test Remove helix ends true
        """
        self.feature_set.parameters['Remove helix ends option'] = True
        self.feature_set.parameters['Spring database option'] = False
        self.feature_set.parameters['spring.db file'] = ''
        super(TestSegment, self).__init__(self.feature_set)
          
        self.x_coordinates_array = self.y_coordinates_array = np.arange(150, 0, -10)
        self.prepare_helix_coordinate_file()
        self.segment()
          
          
    def do_test_case_seg9(self):
        """
        Segment test Perturb step option
        """
        self.feature_set.parameters['Perturb step option'] = True
        super(TestSegment, self).__init__(self.feature_set)
          
        self.segment()
          
          
    @raises(ValueError)
    def do_test_case_impossible_seg10(self):
        """
        Segment test to raise error in case no CTF info available
        """
        self.feature_set.parameters['CTF correct option'] = True
        super(TestSegment, self).__init__(self.feature_set)
          
        for each_file in ['test_output_stack.hdf', 'test_output_stack-6xbin.hdf']:
            dummy = open(each_file, 'w')
            dummy.close()
              
        self.segment()
 
         
    def do_test_case_seg99(self):
        """
        Segment test reading coordinates from spring.db including helix selection and rotation option
        """
        self.segment()
        os.rename('spring.db', 'spring_inp.db')
        self.feature_set.parameters['Segment coordinates'] = 'spring_inp.db'
        self.feature_set.parameters['Helices select option'] = True
        self.feature_set.parameters['Rotation option'] = True
        super(TestSegment, self).__init__(self.feature_set)
        self.segment()
        os.remove('spring_inp.db')


class TestSegmentFrames(TestSegment):

    def setup_of_databases_for_frame_processing_from_segmentrefine3d(self):
        self.segment()
        os.remove('spring.db')
        tsr3d = TestSegmentRefine3dMain()
        tsr3d.setup()
        tsr3d.do_test_case_sr1()

        helix_list = [int(each_val) for each_val in self.feature_set.parameters['Helices list'].split(',')]
        session = SpringDataBase().setup_sqlite_db(base, 'spring.db')
        sel_segments = session.query(SegmentTable).filter(SegmentTable.helix_id.in_(helix_list)).all()
        stack_ids = [each_segment.stack_id for each_segment in sel_segments]

        img = EMData()
        self.test_frame_stack = os.path.abspath(os.path.join(os.pardir, tsr3d.input_stack)) 
        for each_frame in list(range(self.test_frame_count)):
            for each_stack_id in stack_ids:
                img.read_image(tsr3d.input_stack, each_stack_id)
                img.append_image(self.test_frame_stack)

        shutil.copy('spring.db', os.path.join(os.pardir, os.pardir, 'spring.db'))
        os.rename('refinement006.db', os.path.join(os.pardir, 'refinement006.db'))
        tsr3d.teardown()
        
        return tsr3d


    def do_test_case_seg100(self):
        """
        Segment test frame processing of spring.db/refinement.db entries
        """
        self.setup_of_databases_for_frame_processing_from_segmentrefine3d()
      
        mics = ['test_mic_{0:03}.hdf'.format(each_time) for each_time in list(range(5))]
        [shutil.copy('test_mic.hdf', each_mic) for each_mic in mics]
            
        self.feature_set.parameters['Micrographs'] = 'test_mic_???.hdf'
        self.feature_set.parameters['Segment coordinates'] = os.path.join(os.pardir, 'spring.db')
        self.feature_set.parameters['Frame processing option']=True
        self.feature_set.parameters['Refinement.db to process']='refinement006.db'
        super(TestSegment, self).__init__(self.feature_set)
        self.segment()
                    
        os.rename(self.spring_db_frames, os.path.join(os.pardir, 'spring.db'))
        [os.remove(each_file) for each_file in [self.ref_db_frames] + mics ]
      
        
    def create_mic_mrc_stack(self, mic, file_name=None):
        img = EMData()
        img.read_image(mic)
        img_np = EMNumPy.em2numpy(img.copy())
        
        vol_np = np.zeros((self.test_frame_count, img.get_xsize(), img.get_ysize()))
        for each_plane in range(self.test_frame_count):
            vol_np[each_plane] = img_np
            
        stack = EMNumPy.numpy2em(np.copy(vol_np))
        if file_name is None:
            mrc_stack = os.path.splitext(mic)[0] + os.extsep + 'mrcs'
        else:
            mrc_stack = file_name
        stack.write_image(mrc_stack[:-1])
        
        os.rename(mrc_stack[:-1], mrc_stack)

        return mrc_stack


    def do_test_case_seg101(self):
        """
        Segment test frame processing with mrcs (mrc-stack file) of spring.db/refinement.db entries
        """
        tsr3d = self.setup_of_databases_for_frame_processing_from_segmentrefine3d()

        fake_mrc_stack = self.create_mic_mrc_stack('test_mic.hdf')
        os.mkdir(tsr3d.testingdir.testdir)
        os.rename(fake_mrc_stack, os.path.join(tsr3d.testingdir.testdir, fake_mrc_stack))

        self.feature_set.parameters['Micrographs'] = os.path.join(tsr3d.testingdir.testdir, fake_mrc_stack)
        self.feature_set.parameters['Segment coordinates'] = os.path.join(os.pardir, 'spring.db')
        self.feature_set.parameters['Frame processing option'] = True
        self.feature_set.parameters['Refinement.db to process'] = 'refinement006.db'
 
        self.feature_set.parameters['Helices select option'] = True
 
        super(TestSegment, self).__init__(self.feature_set)
        self.segment()
         
        shutil.copy(self.spring_db_frames, os.path.join(os.pardir, 'spring.db'))
        os.remove(os.path.join(tsr3d.testingdir.testdir, fake_mrc_stack))
        shutil.rmtree(tsr3d.testingdir.testdir)
 

class TestSegmentMoreStraight(TestSegment):
    def do_test_case_seg8_with_straightening_option(self):
        self.feature_set.parameters['Unbending option'] = True
        super(TestSegment, self).__init__(self.feature_set)
        
        helix = MicrographHelixPreparation().prepare_dummy_helix(0, 0)
        self.helix_micrograph = TestSegmentStraight().prepare_bent_helix(helix)
        self.helix_micrograph = rot_shift2D(self.helix_micrograph, -45)
        self.helix_micrograph.write_image(self.micrograph_test_file)
        
        self.x_coordinates_array = np.array([32, 36, 42, 49, 58, 66, 76, 88, 100]) + 50
        self.y_coordinates_array = np.array([90, 77, 66, 56, 47, 38, 32, 25, 20]) + 50
        self.prepare_helix_coordinate_file()
        self.segment()
        

class TestSegmentCtf(TestSegment):
    def do_test_case_seg10(self):
        """
        Segment test CTF correction with box files that contain a set of overlapping boxes
        """
        self.feature_set.parameters['CTF correct option'] = True
        super(TestSegment, self).__init__(self.feature_set)
        
        self.prepare_spring_database_ctf_entries()

        self.segment()
        

class TestSegmentEndToEnd(TestSegment):
    def do_end_to_end_test_seg_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_seg_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)


class TestSegmentMpi(TestSegment):
    def do_end_to_end_test_seg_inputfile_with_MPI(self):
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs'] = min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)


class TestSegmentStraightPreparation(object):

    def prepare_bent_helix(self, helix_img):
        img_size = helix_img.get_xsize()
        self.polynom_curve = [1 / 200.0, -1.0, 150.0]
        cols, rows, inplane_angles = self.compute_bending_path_row_wise(float(img_size), self.polynom_curve, 0)
        
        bent_helix = self.straighten_segment(helix_img, img_size, cols, rows, inplane_angles, mode='bend')
        
        return bent_helix
        
        
class TestSegmentStraight(TestSegmentStraightPreparation, Segment):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.bent_helix_name = 'test_helix_bent.hdf'
        self.straightened_helix_name = 'test_helix_straightened.hdf'
        helix = MicrographHelixPreparation().prepare_dummy_helix(0, 0)
        helix.write_image('test_helix.hdf')
        
        self.bent_helix = self.prepare_bent_helix(helix)
        self.bent_helix.write_image(self.bent_helix_name)
        
    def do_test_case_straightening_with_verticalized_helix(self):
        img_size = self.bent_helix.get_xsize()
        cols, rows, inplane_angles = self.compute_bending_path_row_wise(float(img_size), self.polynom_curve, 0)
    
        self.straightened_helix = self.straighten_segment(self.bent_helix, img_size, cols, rows, inplane_angles)
        self.straightened_helix.write_image(self.straightened_helix_name)
         
    def do_test_case_straightening_with_45deg_helix(self):
        angle = 45
        x_offset = 45.4
        y_offset = -15.1
        self.bent_helix = rot_shift2D(self.bent_helix, -angle, x_offset, y_offset)
        self.bent_helix.write_image(self.bent_helix_name)
        
        img_size = self.bent_helix.get_xsize()
        cols, rows, inplane_angles = self.compute_bending_path_row_wise(float(img_size), self.polynom_curve, angle)
        cols += x_offset
        rows += y_offset
        
        self.straightened_helix = self.straighten_segment(self.bent_helix, img_size, cols, rows, inplane_angles,
        'straighten')
        
        self.straightened_helix.write_image(self.straightened_helix_name)

        
    def teardown(self):
        os.remove('test_helix.hdf')

        os.remove(self.straightened_helix_name)
        os.remove(self.bent_helix_name)
    
        self.testingdir.remove()


class TestSegmentWarping(object):
    def setup(self):
        img_size = 40.0
        self.linex = np.ones(img_size) * img_size / 2.0
        self.liney = np.arange(0.0, img_size)
        
        parabola_xx = np.linspace(-(img_size / 2), (img_size / 2), img_size) 
        parabola_yy = 0.02 * (parabola_xx) ** 2 + img_size / 2.0
        
        parabola_xx += img_size / 2.0
        
        self.parabola_x, self.parabola_y = Segment().rotate_coordinates_by_angle(parabola_xx, parabola_yy, 270.0,
        img_size / 2.0, img_size / 2.0)

    
    def start_from_center_and_determine_arc_length(self, linex, liney):
        
        first_half_x = linex[:len(linex) / 2] 
        first_half_y = liney[:len(liney) / 2] 
        
        distances = Segment().compute_cumulative_distances_from_start_of_helix(first_half_x, first_half_y)
        
        return distances
    
    
    def interpolate_xy_finely(self, xcoord, ycoord, angle):
        rotx, roty = Segment().rotate_coordinates_by_angle(xcoord, ycoord, angle, xcoord[0], ycoord[0])
        
        rotx_int = np.linspace(rotx[0], rotx[-1], 100 * len(rotx))
        spline = InterpolatedUnivariateSpline(rotx, roty, k=1)
        roty_int = spline(rotx_int)
        
        xcoord_int, ycoord_int = Segment().rotate_coordinates_by_angle(rotx_int, roty_int, -angle,
        xcoord[0], ycoord[0])
        
        return xcoord_int, ycoord_int
    
        
    def do_test_arc_length(self):
        
        rounded_target_x = np.round(self.parabola_x)
        rounded_target_y = np.round(self.parabola_y)
        
        fine_x, fine_y = self.interpolate_xy_finely(self.linex, self.liney, 270.0)
        
        line_distances = self.start_from_center_and_determine_arc_length(fine_x, fine_y)
        parabola_distances = self.start_from_center_and_determine_arc_length(rounded_target_x, rounded_target_y)
        
        source_coord_x = []
        source_coord_y = []
        for each_target_dist in parabola_distances:
            min_ind = np.argmin(np.abs(line_distances - each_target_dist))
            source_coord_x.append(fine_x[min_ind])
            source_coord_y.append(fine_y[min_ind])
        
        
class TestSegmentMapping(object):
    def setup(self):
        self.img_size = 40.0
        self.linex = np.ones(self.img_size) * self.img_size / 2.0
        self.liney = np.arange(0.0, self.img_size)
        
        self.parabola_y = np.linspace(-(self.img_size / 2), (self.img_size / 2), self.img_size) 
        self.parabola_x = 0.02 * (self.parabola_y) ** 2 + self.img_size / 2.0
        
        self.parabola_y += self.img_size / 2.0
        
        
    def insert_x_y_into_image(self, img_size, x_arr, y_arr, map_axis):
        img = np.zeros((img_size, img_size))
        
        for (each_x, each_y) in zip(x_arr, y_arr):
            if int(each_x) < img_size and int(each_y) < img_size:
                img[int(each_y)][int(each_x)] = 1.0
        
        return img
    
            
    def generate_complete_xmap(self):
        complete_y_map = np.vstack([each_col * np.ones(self.img_size) for each_col in np.arange(self.img_size)])
        complete_y_map = np.swapaxes(complete_y_map, 0, 1)
        
        return complete_y_map
    

    def generate_complete_map(self, map_y_img):
        complete_y_map = np.zeros((self.img_size, self.img_size))
        for each_col_id, each_col in enumerate(np.arange(-self.img_size / 2, self.img_size / 2)):
            complete_y_map += np.roll(map_y_img * each_col_id, int(each_col), axis=1)
        
        return complete_y_map


    def do_test_mapping(self):
        map_y_img = self.insert_x_y_into_image(self.img_size, self.parabola_x, self.parabola_y, self.linex)
        
        source_y_map = self.generate_complete_map(map_y_img)
        source_x_map = self.generate_complete_xmap()
            
        helix = SegmentExam().make_smooth_rectangular_mask(3, 40, 40)
        
        helix_arr = np.copy(EMNumPy.em2numpy(helix))
        
        
        zi = map_coordinates(helix_arr, [source_x_map, source_y_map], order=3)
        output = zi.reshape(helix_arr.shape)
    
def main():
    tseg = TestSegmentMain()
    tseg.setup()
    tseg.do_test_case_seg1()
        
if __name__ == '__main__':
    main()
