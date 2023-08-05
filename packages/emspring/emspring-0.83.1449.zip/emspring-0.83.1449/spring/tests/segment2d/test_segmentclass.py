#!/usr/bin/env python
"""
Test module to check segmentclass
"""
from EMAN2 import EMData, EMUtil
from fundamentals import rot_shift2D
from glob import glob
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment2d.segmentclass import SegmentClass, SegmentClassPar
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segmentexam import HelixProjectionPreparation
import numpy as np
import os
import random
import shutil


class HelixClassPreparation(HelixProjectionPreparation):
    def shift_segments(self):
        img = EMData()
        
        for each_img_id in list(range(EMUtil.get_image_count('test_segments.hdf'))):
            img.read_image('test_segments.hdf', each_img_id)
            img = rot_shift2D(img, 0, random.randrange(-5, 5), 0)
            img.write_image('test_segments.hdf', each_img_id)
            
            
    def prepare_helix_classes(self):
        """
        * Function to generate a projection of 4 classes
        """
        self.number_of_classes = 3
        for class_helix in range(self.number_of_classes):
            self.width_of_helix_in_angstrom = 250 + 100 * class_helix
            self.prepare_helix_projection()
            self.shift_segments()
        

    def prepare_custom_filter_file(self, custom_filter_file, dimension, binfactor=1):
        number_of_frequencies = (dimension/2)/binfactor
#        number_of_frequencies = (self.helix_micrograph.get_xsize()/2)/binfactor
        frequencies = np.linspace(0, 0.5, number_of_frequencies)
        ffile = open(custom_filter_file, 'w')
        for each_frequency in frequencies:
            filter_coefficient = np.sin(np.degrees(each_frequency))
            if filter_coefficient > 1:
                filter_coefficient = 1
            elif filter_coefficient < 0:
                filter_coefficient = 0
            
            ffile.write('{0}\t{1}\n'.format(each_frequency, filter_coefficient))
        
        ffile.close()


    def setup_helix_or_particle_dimensions(self):
        self.feature_set.parameters['Estimated helix width and height in Angstrom'] = ((self.width_of_helix_in_angstrom,
        int(1.5 * self.width_of_helix_in_angstrom)))

    def setup_common_non_mpi_parameters(self):
        self.prepare_helix_classes()
        self.custom_filter_file = 'test_filter_file.dat'
        self.test_bin_factor = 2
        self.prepare_custom_filter_file(self.custom_filter_file, self.test_bin_factor)
        self.logfile, self.directory = EndToEndTest().define_logfile_and_directory(self.feature_set.progname)
        self.feature_set.logfile = self.logfile
        self.feature_set.parameters['Image input stack'] = 'test_segments.hdf'
        self.feature_set.parameters['Class average stack'] = 'test_averages.hdf'
        
        self.feature_set.parameters['Spring database option']=False
        self.feature_set.parameters['Database prepare option']=False
        self.feature_set.parameters['spring.db file']=os.path.join(os.pardir, 'spring.db')
            
        self.feature_set.parameters['Reference image option']=False
        self.feature_set.parameters['Image reference stack']='test_ref_segments.hdf'
        self.feature_set.parameters['Class variance stack'] = 'test_variances.hdf'
        self.feature_set.parameters['Eigenimage stack'] = 'test_eigenimages.hdf'
        self.feature_set.parameters['Pixel size in Angstrom'] = float(self.pixelsize)
        self.setup_helix_or_particle_dimensions()
        self.feature_set.parameters['Binning option'] = True
        self.feature_set.parameters['Binning factor'] = self.test_bin_factor
        self.feature_set.parameters['Number of classes'] = int(self.number_of_classes)
        self.feature_set.parameters['Number of iterations'] = int(3)
        self.feature_set.parameters['Keep intermediate files']=False
        
        self.feature_set.parameters['Limit in-plane rotation'] = True
        self.feature_set.parameters['Delta in-plane rotation angle'] = 10.0
        self.feature_set.parameters['X and Y translation range in Angstrom'] = (20, 15)
        self.feature_set.parameters['High-pass filter option'] = False
        self.feature_set.parameters['Low-pass filter option'] = False
        self.feature_set.parameters['High and low-pass filter cutoffs in 1/Angstrom'] = (0.01, 0.06)
        self.feature_set.parameters['Custom filter option'] = False
        self.feature_set.parameters['Custom-built filter file'] = self.custom_filter_file
        self.feature_set.parameters['Automatic filter option'] = False
        self.feature_set.parameters['B-Factor']=0
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)


class TestSegmentClassClear(object):
    def clear_segment_files(self):
        segment_files = glob('test_segments*.hdf')
        for segment_file in segment_files:
            os.remove(segment_file)
        pass

    def clear_logfiles(self):
        try:
            os.remove(os.path.join(os.pardir, self.logfile))
        except:
            pass
        
        logfiles = glob('logfile*')
        for logfile in logfiles:
            os.remove(logfile)

    def clear_directories_including_content(self):
        directories = ['sxk_means*', 'segmentalign*', 'particlealign*']
        
        for directory in directories:
            cluster_directory_list = glob(directory)
            for cluster_directory in cluster_directory_list:
                all_files_in_directory = os.listdir(cluster_directory)
                for each_file in all_files_in_directory:
                    os.remove(os.path.join(cluster_directory, each_file))
                os.rmdir(cluster_directory)


    def teardown_segmentclass(self):
        self.clear_segment_files()
        os.remove(self.custom_filter_file)
        os.remove('spring.db')
        os.remove('test_averages.hdf')
        os.remove('test_variances.hdf')
        os.remove('test_eigenimages.hdf')
        self.clear_logfiles()
        self.clear_directories_including_content()


class TestSegmentClass(HelixClassPreparation, SegmentClass, TestSegmentClassClear):

    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = SegmentClassPar()
        self.setup_common_non_mpi_parameters()
        
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())

        super(TestSegmentClass, self).__init__(self.feature_set)


    def teardown(self):
        self.teardown_segmentclass()
        
        self.testingdir.remove()


class TestSegmentClassMain(TestSegmentClass):
    def do_test_case_sc1(self):
        """
        * Standard single-CPU segmentclass test
        """
        self.classify()


class TestSegmentClassMore(TestSegmentClass):
    def do_test_case_sc2_reference_image(self):
        """
        * Segmentclass: Test reference image option
        """
        self.feature_set.parameters['Reference image option']=True

        shutil.copy('test_segments.hdf', 'test_ref_segments.hdf')
        super(TestSegmentClass, self).__init__(self.feature_set)
        self.classify()
        os.remove('test_ref_segments.hdf')
        os.remove('test_ref_segments2binned.hdf')

    
    def do_test_case_sc3_single_iteration(self):
        """
        * Segmentclass single iteration
        """
        self.feature_set.parameters['Number of iterations'] = 0

        super(TestSegmentClass, self).__init__(self.feature_set)
        self.classify()
        

class TestSegmentClassEndToEnd(TestSegmentClass):
    def do_end_to_end_test_sc_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_sc_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)

class TestSegmentClassMpi(TestSegmentClass):
    def do_end_to_end_test_sc_inputfile_MPI(self):

        self.feature_set.parameters['MPI option']=True
#        self.feature_set.parameters['Number of CPUs']=2
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)


def main():
    tsce = TestSegmentClassMain()
    tsce.setup()
    tsce.do_test_case_sc1()
        
if __name__ == '__main__':
    main()
