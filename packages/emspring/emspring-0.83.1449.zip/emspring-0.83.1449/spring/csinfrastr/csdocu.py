#!/usr/bin/env python
# Author: Carsten Sachse 3-Jan-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Module to generate rst files for sphinx documentation
"""
from EMAN2 import EMData, EMUtil, EMNumPy, Util
from glob import glob
import os
import shutil
from spring.csinfrastr.csproductivity import Support
import subprocess
import sys

import numpy as np


class GalleryTestSetup(object):
    def prepare_tests_in_new_directory(self):
        os.mkdir(self.program)
        os.chdir(self.program)

    def convert_wildcards_if_present_to_correct_filename(self, filename):
        if '?' in filename or '*' in filename:
            filename = glob(filename)[0]
            
        return filename

    def copy_input_and_output_files_to_images(self):
        self.infile = list(self.parameters.values())[0]
        self.outfile = list(self.parameters.values())[1]
        self.infile = self.convert_wildcards_if_present_to_correct_filename(self.infile)
        self.outfile = self.convert_wildcards_if_present_to_correct_filename(self.outfile)

class GalleryTestsScan(object):
    def perform_test_scansplit(self):
        from spring.tests.micprgs.test_scansplit import TestScanSplitMain
        self.test = TestScanSplitMain()
        self.test.setup()
        self.test.do_test_case_ss1()

    def perform_test_micexam(self):
        from spring.tests.micprgs.test_micexam import TestMicrographExamMain
        self.test = TestMicrographExamMain()
        self.test.setup()
        self.test.do_test_case_se1()
        
    def perform_test_michelixtrace(self):
        from spring.tests.micprgs.test_michelixtrace import TestMicHelixTraceMain
        self.test = TestMicHelixTraceMain()
        self.test.setup()
        self.test.do_test_case_mt1()
        
    def perform_test_micctfdetermine(self):
        from spring.tests.micprgs.test_micctfdetermine import TestMicCtfDetermineMain
        self.test = TestMicCtfDetermineMain()
        self.test.setup()
        self.test.do_test_case_scd1()
        
    def perform_test_scanrowcolcorr(self):
        from spring.tests.micprgs.test_scanrowcolcorr import TestScanRowColCorrMain
        self.test = TestScanRowColCorrMain()
        self.test.setup()
        self.test.do_test_case_rcc1()

    def perform_test_scandotfit(self):
        from spring.tests.micprgs.test_scandotfit import TestScanDotFitMain
        self.test = TestScanDotFitMain()
        self.test.setup()
        self.test.do_test_case_df1()

    def perform_test_scanlinefit(self):
        from spring.tests.micprgs.test_scanlinefit import TestScanLineFitMain
        self.test = TestScanLineFitMain()
        self.test.setup()
        self.test.do_test_case_lf1()

class GalleryTestsSegment2d(object):
    def perform_test_seglayer2lattice(self):
        from spring.tests.segment2d.test_seglayer2lattice import TestSegLayer2LatticeMain
        self.test = TestSegLayer2LatticeMain()
        self.test.setup()
        self.test.do_test_case_sl2l_1()
        
        key_infile = list(self.test.feature_set.parameters.keys())[0]
        self.test.feature_set.parameters[key_infile] = 'test_power.hdf'
        self.copy_file_to_output('seglayer2lattice.png') 
        
    def perform_test_segmentalign2d(self):
        from spring.tests.segment2d.test_segmentalign2d import TestSegmentAlign2dMain
        self.test = TestSegmentAlign2dMain()
        self.test.setup()
        self.test.do_test_case_sa1()
        
    def perform_test_segment(self):
        from spring.tests.segment2d.test_segment import TestSegmentMain
        self.test = TestSegmentMain()
        self.test.setup()
        self.test.do_test_case_seg1()

    def perform_test_segmentexam(self):
        from spring.tests.segment2d.test_segmentexam import TestSegmentExamMain
        self.test = TestSegmentExamMain()
        self.test.setup()
        self.test.do_test_case_se1()

    def perform_test_segmentclass(self):
        from spring.tests.segment2d.test_segmentclass import TestSegmentClassMain
        self.test = TestSegmentClassMain()
        self.test.setup()
        self.test.do_test_case_sc1()

    def perform_test_segclassexam(self):
        from spring.tests.segment2d.test_segclassexam import TestSegClassExamMain
        self.test = TestSegClassExamMain()
        self.test.setup()
        self.test.do_test_case_sce1()

    def perform_test_segclasslayer(self):
        from spring.tests.segment2d.test_segclasslayer import TestSegClassLayerMain
        self.test = TestSegClassLayerMain()
        self.test.setup()
        self.test.do_test_case_scl1()
        self.copy_file_to_output('segclasslayer.png') 
        
    def perform_test_segmentselect(self):
        from spring.tests.segment2d.test_segmentselect import TestSegmentSelectMain
        self.test = TestSegmentSelectMain()
        self.test.setup()
        self.test.do_test_case_scex1()

    def copy_file_to_output(self, outfile):
        key_outfile = list(self.test.feature_set.parameters.keys())[1]
        self.test.feature_set.parameters[key_outfile] = outfile
        shutil.copy(os.path.join(os.pardir, os.pardir, 'screenshots', outfile), outfile)

    def perform_test_segmentplot(self):
        from spring.tests.segment2d.test_segmentplot import TestSegmentPlotMain
        self.test = TestSegmentPlotMain()
        self.test.setup()
        self.test.do_test_case_sp1()
        self.copy_file_to_output('segmentplot.png') 

class GalleryTestsSegment3d(object):
    def perform_test_segrefine3dcyclexplore(self):
        from spring.tests.segment3d.test_segrefine3dcyclexplore import TestSegRefine3dCycleExploreMain
        self.test = TestSegRefine3dCycleExploreMain()
        self.test.setup()
        
        self.test.do_test_case_sr3dce1()
        os.chdir(os.pardir)
        self.copy_file_to_output('segrefine3dcyclexplore.png') 

    def perform_test_segrefine3dinspect(self):
        from spring.tests.segment3d.test_segrefine3dinspect import TestSegRefine3dInspectMain
        self.test = TestSegRefine3dInspectMain()
        self.test.setup()
        self.test.do_test_case_sr3di1()
        self.copy_file_to_output('segrefine3dinspect.png') 

    def perform_test_segrefine3dplot(self):
        from spring.tests.segment3d.test_segrefine3dplot import TestSegRefine3dPlotMain
        self.test = TestSegRefine3dPlotMain()
        self.test.setup()
        
        self.test.do_test_case_sr3dp1()
        os.chdir(os.pardir)
        self.copy_file_to_output('segrefine3dplot.png') 

    def perform_test_segmentrefine3d(self):
        from spring.tests.segment3d.test_segmentrefine3d import TestSegmentRefine3dMain
        self.test = TestSegmentRefine3dMain()
        self.test.setup()
        self.test.do_test_case_sr1()
        if self.program == 'segrefine3dgrid':
            from spring.tests.segment3d.test_segrefine3dgrid import TestSegRefine3dGridMain
            self.test = TestSegRefine3dGridMain()
            self.test.setup()
            
            os.chdir(os.pardir)
            files = glob('{0}/*'.format(self.test.testingdir.testdir))
            [os.rename(each_file, os.path.basename(each_file)) for each_file in files]
            os.rmdir(self.test.testingdir.testdir)

        
    def perform_test_segmentctfapply(self):
        from spring.tests.segment2d.test_segmentctfapply import TestSegmentCtfApplyMain
        self.test = TestSegmentCtfApplyMain()
        self.test.setup()
        self.test.do_test_case_sca1()
        
    def perform_test_seggridexplore(self):
        from spring.tests.segment3d.test_seggridexplore import TestSegGridExploreMain
        self.test = TestSegGridExploreMain()
        self.test.setup()
        
        self.test.do_test_sgx1()
        os.chdir(os.pardir)
        self.copy_file_to_output('seggridexplore.png') 
        
        
    def perform_test_segclassreconstruct(self):
        from spring.tests.segment3d.test_segclassreconstruct import TestSegClassReconstructMain
        self.test = TestSegClassReconstructMain()
        self.test.setup()
        self.test.do_test_case_cr1()
        
        
    def perform_test_segclassmodel(self):
        from spring.tests.segment3d.test_segclassmodel import TestSegClassModelMain
        self.test = TestSegClassModelMain()
        self.test.setup()
        self.test.do_test_case_scm1()
        
        
    def perform_test_segmultirefine3d(self):
        from spring.tests.segment3d.test_segmultirefine3d import TestSegMultiRefine3dMain
        self.test = TestSegMultiRefine3dMain()
        self.test.setup()
        self.test.do_test_case_smr3d1()
        key_infile = list(self.test.feature_set.parameters.keys())[1]
        self.test.feature_set.parameters[key_infile] = 'test_recvol.hdf'
        
        
class GalleryTests(GalleryTestSetup, GalleryTestsScan, GalleryTestsSegment2d, GalleryTestsSegment3d):
    """
    * Class to perform test procedures
    """
    def perform_test_particleclass(self):
        from spring.tests.particle2d.test_particleclass import TestParticleClass
        self.test = TestParticleClass()
        self.test.setup()
        self.test.do_test_case_pc1()
        
    def perform_test_cleanup(self):
        if self.program in ['segrefine3dgrid']:
            testing_dir = os.path.join(self.current_directory, self.program, 'test_segmentrefine3d')
            to_be_deleted = os.listdir(testing_dir)
            [os.remove(each_file) for each_file in to_be_deleted]
            os.rmdir(testing_dir)
        else:
            self.test.teardown()

class GalleryBrowserFiles(object):
    """
    * Class that holds functions for rst file write
    """
    def open_gallery_rst_file(self):
        if not os.path.isdir('programs'):
            os.mkdir('programs')
        self.rst_file = open(os.path.join('programs', 'gallery' + os.extsep + 'rst'), 'w')
        self.rst_file.write('.. _gallery:\n\n')
        self.rst_file.write('Gallery\n' + 40*'=' + '\n')

        if not os.path.isdir('gallery_images'):
            os.mkdir('gallery_images')
            
    def convert_file_for_webbrowser(self, filename):
        if self.program in ['segrefine3dgrid']:
            self.filename = os.path.join(self.current_directory, self.program, 'test_segmentrefine3d',
            os.path.basename(filename))
        else:
            self.filename = os.path.join(self.current_directory, self.program, self.test.testingdir.testdir,
            os.path.basename(filename))

        self.filename_extension = self.filename.split(os.extsep)[-1]
        self.in_or_outputtype = next(self.fileit)        
        if self.filename_extension in ['hdf', 'spi', 'img', 'hed', 'mrc', 'tif']:
            self.combine_EMData_to_img()
            self.write_img_to_png()
        elif self.filename_extension in ['png', 'pdf']:
            self.copy_png_to_png()
        return self.converted_file

    def combine_EMData_to_img(self, filename=None):
        """
        >>> import numpy as np
        >>> imgarr = np.array([[ 0.,  0.,  1.,  1.],
        ...                    [ 0.,  0.,  1.,  0.],
        ...                    [ 0.,  1.,  1.,  0.],
        ...                    [ 1.,  1.,  0.,  0.]])
        >>> from EMAN2 import EMNumPy
        >>> from spring.csinfrastr.csdocu import GalleryBrowserFiles
        >>> filename = 'test_stack.hdf'
        >>> def setup_and_merge_stack_with_image_number(imgarr, number):
        ...     for image_number in range(number):
        ...         EMNumPy.numpy2em(imgarr).write_image(filename, image_number)
        ...     img = GalleryBrowserFiles().combine_EMData_to_img(filename)
        ...     os.remove(filename)
        ...     return np.copy(EMNumPy.em2numpy(img))
        >>> setup_and_merge_stack_with_image_number(imgarr, 6)
        array([[ 0.,  0.,  1.,  1.,  0.,  0.,  1.,  1.],
               [ 0.,  0.,  1.,  0.,  0.,  0.,  1.,  0.],
               [ 0.,  1.,  1.,  0.,  0.,  1.,  1.,  0.],
               [ 1.,  1.,  0.,  0.,  1.,  1.,  0.,  0.],
               [ 0.,  0.,  1.,  1.,  0.,  0.,  1.,  1.],
               [ 0.,  0.,  1.,  0.,  0.,  0.,  1.,  0.],
               [ 0.,  1.,  1.,  0.,  0.,  1.,  1.,  0.],
               [ 1.,  1.,  0.,  0.,  1.,  1.,  0.,  0.],
               [ 0.,  0.,  1.,  1.,  0.,  0.,  1.,  1.],
               [ 0.,  0.,  1.,  0.,  0.,  0.,  1.,  0.],
               [ 0.,  1.,  1.,  0.,  0.,  1.,  1.,  0.],
               [ 1.,  1.,  0.,  0.,  1.,  1.,  0.,  0.]], dtype=float32)
        >>> imgarr = np.array([0])
        >>> setup_and_merge_stack_with_image_number(imgarr, 2).shape
        (2,)
        >>> setup_and_merge_stack_with_image_number(imgarr, 6).shape
        (3, 2)
        >>> setup_and_merge_stack_with_image_number(imgarr, 12).shape
        (3, 4)
        >>> setup_and_merge_stack_with_image_number(imgarr, 25).shape
        (3, 4)
        """
        if filename is None: filename = self.filename
        self.filename = filename

        self.img = EMData()
        self.number_of_images_on_stack = EMUtil.get_image_count(self.filename)
        if  self.number_of_images_on_stack == 1:
            self.img.read_image(self.filename)
        elif 1 < self.number_of_images_on_stack <= 12:
            self.increment = 1
            self.tile_ten_images_to_montage()
        elif self.number_of_images_on_stack > 12:
            self.increment = int(self.number_of_images_on_stack/12)
            self.number_of_images_on_stack = 12
            self.tile_ten_images_to_montage()

        return self.img

    def copy_png_to_png(self):
        self.converted_file = '{0}{1}gallery_images{2}{3}_{4}{5}{6}'.format(self.current_directory, os.sep, os.sep,
        self.program, self.in_or_outputtype, os.extsep, self.filename_extension)
        
        if not os.path.isfile(self.filename):
            files = glob('{0}*{1}'.format(os.path.splitext(self.filename)[0], os.path.splitext(self.filename)[-1]))
            shutil.copy(files[0], self.converted_file) 
        else:
            shutil.copy(self.filename, self.converted_file) 

    def tile_ten_images_to_montage(self):

        if self.number_of_images_on_stack >= 6:
            column_count = int(self.number_of_images_on_stack/3)
            row_count = int(self.number_of_images_on_stack/(column_count))
        else:
            row_count = 1
            column_count = self.number_of_images_on_stack
        images = {}
        horizontal_stacks = {}
        image_number = 0
        self.img.read_image(self.filename, 0)
        padsize_x_to_include_border = int(1.1*self.img.get_xsize())
        padsize_y_to_include_border = int(1.1*self.img.get_ysize())
        for row_number in range(row_count):
            for column_number in range(column_count):
                new_image_number = image_number*self.increment
                self.img.read_image(self.filename, new_image_number)
                padimg = Util.pad(self.img, padsize_x_to_include_border, padsize_y_to_include_border, 1, 0, 0, 0, '0')
                images['column{0}'.format(column_number)] = np.copy(EMNumPy.em2numpy(padimg))
                image_number += 1
            horizontal_stacks['row{0}'.format(row_number)] = \
            np.hstack([images['column{0}'.format(column_number)] for column_number in range(column_count)])
            
        if column_count >= 1:
            vertical_stack = np.vstack([horizontal_stacks['row{0}'.format(row_number)] 
                                        for row_number in range(row_count)])
        elif column_count == 1:
            vertical_stack = horizontal_stacks['row0']

        self.img = EMNumPy.numpy2em(np.copy(vertical_stack))

    def write_img_to_png(self):
        self.converted_file = '{0}{1}gallery_images{2}{3}_{4}{5}png'.format(self.current_directory, os.sep, os.sep,
        self.program, self.in_or_outputtype, os.extsep)
        
        self.img.write_image(self.converted_file)

    def add_program_header(self):
        header_referenced = """
        \n:ref:`{program}`\n{underline}
        \n.. automodule:: {first_code}
        """.format(program = self.program, underline=(len(self.program) + 7) * '^', 
        first_code=self.test.feature_set.code_files[0])

        self.rst_file.write(header_referenced)

    def add_images_to_gallery(self):
        relative_infile = os.path.join(os.pardir, 'gallery_images', os.path.basename(self.browser_infile))
        
        relative_outfile = os.path.join(os.pardir, 'gallery_images', os.path.basename(self.browser_outfile))
        
#         relative_infile = '{pardir}{separator}gallery_images{separator}{basename_infile}'.format(pardir=os.pardir, 
#         separator=os.sep, basename_infile=os.path.basename(self.browser_infile))
#         
#         relative_outfile = '{pardir}{separator}gallery_images{separator}{basename_outfile}'.format(pardir=os.pardir, 
#         separator=os.sep, basename_outfile=os.path.basename(self.browser_outfile))
        
        basename_infile = os.path.basename(self.browser_infile)
        basename_outfile = os.path.basename(self.browser_outfile)
        basename_infile_border='|{0}|'.format(os.path.basename(self.browser_infile))
        basename_outfile_border='|{0}|'.format(os.path.basename(self.browser_outfile))

        out = list(self.parameters.keys())[1]
        if out == 'Batch mode':
            out = 'Interactive screenshot'
            
        figure_table = """
        +{horizontal_border:<49}+{horizontal_border:<49}+
        {vert_border} {basename_infile_border:<49}{vert_border} {basename_outfile_border:<49}{vert_border}
        +{horizontal_border:<49}+{horizontal_border:<49}+
        {vert_border:<2}Input: {input_parameter:<42}{vert_border:<2}Output: {output_parameter:<41}{vert_border}
        +{horizontal_border:<49}+{horizontal_border:<49}+
        
        .. {basename_infile_border} image:: {relative_infile}
            :alt: tree
            :width: 4 cm
            :target: {pardir}{separator}_images{separator}{basename_infile}
            
        .. {basename_outfile_border} image:: {relative_outfile}
            :alt: tree
            :width: 4 cm
            :target: {pardir}{separator}_images{separator}{basename_outfile}

        """.format(basename_infile = basename_infile, basename_outfile=basename_outfile,
        basename_infile_border = basename_infile_border, basename_outfile_border=basename_outfile_border,
        relative_infile=relative_infile, relative_outfile=relative_outfile,
        input_parameter=list(self.parameters.keys())[0], output_parameter=out,
        horizontal_border=50 * '-', vert_border='|', separator=os.sep, pardir=os.pardir)

        self.rst_file.write(figure_table)

class Gallery(GalleryTests, GalleryBrowserFiles):
    """
    * Class to generate gallery from input and output of each individual program
    """

    def __init__(self):
        self.open_gallery_rst_file()
        self.current_directory = os.path.abspath(os.curdir)
         
        self.prgms_dir = 'programs'
        if not os.path.isdir(self.prgms_dir):
            os.mkdir(self.prgms_dir)
        self.run_segment3d_tests()
        self.run_segment2d_tests()
        
        self.run_micprgs_tests()
        
#        self.write_updated_changelog()

    def run_test(self, program):
        self.program = program
        self.prepare_tests_in_new_directory()

        self.perform_test_program()
        self.copy_input_and_output_files_to_images()
        os.chdir(os.path.join(self.current_directory, 'gallery_images'))

        self.fileit = iter(['input', 'output'])
        self.browser_infile = self.convert_file_for_webbrowser(self.infile)
        self.browser_outfile = self.convert_file_for_webbrowser(self.outfile)

        self.add_program_header()
        self.add_images_to_gallery()
        if self.program in ['segrefine3dplot', 'segrefine3dcyclexplore']:
            os.chdir(os.path.join(self.current_directory, self.program, self.test.testingdir.testdir,
            'test_segmentrefine3d'))
        elif self.program in ['segrefine3dgrid']:
            os.chdir(os.path.join(self.current_directory, self.program, 'test_segmentrefine3d'))
        elif self.program in ['seggridexplore']:
            os.chdir(os.path.join(self.current_directory, self.program, self.test.testingdir.testdir,
            'test_segclassreconstruct'))
        else:
            os.chdir(os.path.join(self.current_directory, self.program, self.test.testingdir.testdir))

        self.perform_test_cleanup()
        os.chdir(self.current_directory)
        self.write_program_rst_file()
        additional_files = glob('{0}*'.format(os.path.join(self.current_directory, self.program) + os.sep))
        for each_file in additional_files:
            os.remove(each_file)
        os.rmdir(os.path.join(self.current_directory,self.program))


    def run_segment2d_tests(self):
        self.rst_file.write('\nSpring2d' + '\n' + len('Spring2d')*'-' + '\n')
        self.run_test('segment')
        self.run_test('segmentexam')
        self.run_test('segmentclass')
        self.run_test('segmentalign2d')
        self.run_test('segclassexam')
        self.run_test('segclasslayer')
        self.run_test('seglayer2lattice')
        self.run_test('segmentplot')


    def run_segment3d_tests(self):
        self.rst_file.write('\nSpring3d' + '\n' + len('Spring3d')*'-' + '\n')
        self.run_test('segmentrefine3d')
        self.run_test('segrefine3dinspect')
        self.run_test('segrefine3dgrid')
        self.run_test('seggridexplore')
        self.run_test('segmultirefine3d')
        self.run_test('segclassreconstruct')
        self.run_test('segrefine3dplot')
        self.run_test('segrefine3dcyclexplore')
        self.run_test('segclassmodel')


    def run_micprgs_tests(self):
        self.rst_file.write('\nSpringmicrograph' + '\n' + len('Springmicrograph')*'-' + '\n')
        self.run_test('scansplit')
        self.run_test('micexam')
        self.run_test('michelixtrace')
        self.run_test('micctfdetermine')
        self.run_test('scanrowcolcorr')
        self.run_test('scandotfit')
        self.run_test('scanlinefit')

    def write_updated_changelog(self):
        changelog = open('changelog.rst', 'w')
        changelog_header = """.. _changelog:
        \nChangelog\n=========\n
        """
        changelog.write(changelog_header)
        
        proc = subprocess.Popen(['hg', 'log', '--style=changelog', sys.argv[0]], shell=False,
                                stdout=subprocess.PIPE)
        changelog.write(proc.communicate()[0])
        changelog.close()
    
    def perform_test_program(self):
        if self.program == 'segment':
            self.perform_test_segment()
        elif self.program == 'segmentexam':
            self.perform_test_segmentexam()
        elif self.program == 'segmentclass':
            self.perform_test_segmentclass()
        elif self.program == 'segclassexam':
            self.perform_test_segclassexam()
        elif self.program == 'segmentalign2d':
            self.perform_test_segmentalign2d()
        elif self.program == 'segclasslayer':
            self.perform_test_segclasslayer()
        elif self.program == 'seglayer2lattice':
            self.perform_test_seglayer2lattice()
        elif self.program == 'segmentselect':
            self.perform_test_segmentselect()
        elif self.program == 'segmentplot':
            self.perform_test_segmentplot()
            
        elif self.program == 'segmentrefine3d':
            self.perform_test_segmentrefine3d()
        elif self.program == 'segrefine3dgrid':
            self.perform_test_segmentrefine3d()
        elif self.program == 'segrefine3dinspect':
            self.perform_test_segrefine3dinspect()
        elif self.program == 'segrefine3dcyclexplore':
            self.perform_test_segrefine3dcyclexplore()
        elif self.program == 'segrefine3dplot':
            self.perform_test_segrefine3dplot()
        elif self.program == 'segmentctfapply':
            self.perform_test_segmentctfapply()
        elif self.program == 'segclassreconstruct':
            self.perform_test_segclassreconstruct()
        elif self.program == 'segclassmodel':
            self.perform_test_segclassmodel()
        elif self.program == 'segmultirefine3d':
            self.perform_test_segmultirefine3d()
        elif self.program == 'seggridexplore':
            self.perform_test_seggridexplore()
        elif self.program == 'particleclass':
            self.perform_test_particleclass()
            
        elif self.program == 'scansplit':
            self.perform_test_scansplit()
        elif self.program == 'micexam':
            self.perform_test_micexam()
        elif self.program == 'michelixtrace':
            self.perform_test_michelixtrace()
        elif self.program == 'micctfdetermine':
            self.perform_test_micctfdetermine()
        elif self.program == 'scanrowcolcorr':
            self.perform_test_scanrowcolcorr()
        elif self.program == 'scandotfit':
            self.perform_test_scandotfit()
        elif self.program == 'scanlinefit':
            self.perform_test_scanlinefit()

        self.parameters = self.test.feature_set.parameters


    def write_program_rst_file(self):
        command_line = '{0} --print_rst {1} {2}'.format(self.program, self.browser_infile, self.browser_outfile)
        print(command_line)
        subprocess.call(command_line.split())
        
        rst_file = self.program + os.extsep + 'rst'
        os.rename(rst_file, os.path.join(self.prgms_dir, rst_file))
        prg_name_file = self.program + '_functions' + os.extsep + 'rst'
        os.rename(prg_name_file, os.path.join(self.prgms_dir, prg_name_file))
        
        
class RecordRst(GalleryBrowserFiles):
    """
    Class that holds functions required for rst file generation and sphinx build generation
    """
    def __init__(self, parset):
        """
        Initialize rstfile for further modification
        """
        self.progname = parset.progname
        self.proginfo = parset.proginfo
        self.parameters = parset.parameters
        self.level = parset.level
        self.program_states = parset.program_states
        self.hints = parset.hints
        self.properties = parset.properties
        self.parser = parset.parser
        self.code_files = parset.code_files
        options  = self.parser.parse_args()
        self.args = options.input_output

        self.rst_file = open(self.progname + '.rst', 'w')

        self.mkintrorst()
        if len(self.args) == 2:
            self.add_input_output_table()
        
        levels = Support().define_levels_beginner_intermediate_expert()
        for self.this_level in ['beginner', 'intermediate', 'expert']:
            self.this_levels = levels[self.this_level]
            self.inputrst()
            self.write_sample_parameter_file()
            
        self.cmdlineoptrst()
        self.programstr()
        self.generate_functions_file()

        sys.exit()

    def mkintrorst(self):
        """
        Brief program description at the top of the page
        """
        self.rst_file.write('.. _'+ self.progname + ':\n\n')
        self.rst_file.write(self.progname.capitalize() + '\n' + len(self.progname)*'-' + '\n')
#        self.rst_file.write('\n.. automodule:: %s\n' %(self.progname))
        self.rst_file.write('\n{0}\n'.format(self.proginfo))

    def add_input_output_table(self):
        self.browser_infile = self.args[0]
        self.browser_outfile = self.args[1]
        self.program = self.progname
        self.add_images_to_gallery()


    def print_help_message_with_indentation(self):
        this_file = open('thisfile.txt', 'w')
        self.parser.print_help(this_file)
        this_file.close()
        written_file = open('thisfile.txt', 'r')
        indented_string = ''
        for each_line in written_file.readlines():
            indented_string += '    {0}'.format(each_line)
        
        written_file.close()
        os.remove('thisfile.txt')
        self.rst_file.write(indented_string)
        self.rst_file.close()

    def cmdlineoptrst(self):
        self.rst_file.write('\n.. _using_%s_on_cmdline:\n' %self.progname)
        self.rst_file.write('\nCommand line options' + '\n' + 23*'~' + '\n')
        self.rst_file.write('\nWhen invoking ' + self.progname + ', you may specify any of these options::\n\n')

        self.print_help_message_with_indentation()

        # add tabs to 'Usage' lines for correct cmdline formatting
        rfile = open(self.progname + '.rst', 'r')  # r for reading
        lines = rfile.readlines()
        rfile.close()
        
        self.rst_file = open(self.progname + '.rst', 'w')
        for line in lines:
            if line.strip().startswith('Usage:'):
                self.rst_file.write('    ' + line)
            elif line.strip().startswith('Options:'):
                self.rst_file.write(line.strip() + ':\n\n')
            else:
                self.rst_file.write(line)
                

    def inputrst(self):
        self.rst_file.write('\n\n.. _making_a_{0}_table_for_{1}:\n\n'.format(self.progname, self.this_level))
        heading = 'parameters'
        if self.this_level not in ['beginner']:
            heading = 'additional ' + heading + ' ({0} level)'.format(self.this_level) 
        self.rst_file.write(heading.capitalize() + '\n' + 45 * '~' + '\n\n')
        self.rst_file.write('.. tabularcolumns:: |p{4cm}|p{2.5cm}|p{9cm}|\n\n')
        self.rst_file.write('%-80s %-80s %s\n' %(78*'=', 78*'=', 100*'='))
        self.rst_file.write('%-80s %-80s %s\n' %('Parameter', 'Example (default)', 'Description'))
        self.rst_file.write('%-80s %-80s %s\n' %(78*'=', 78*'=', 100*'='))
        for name in self.hints:
            if self.level[name] == self.this_level:
                if type(self.parameters[name]) in [int, float, tuple]:
                    if self.hints[name].endswith('.'):
                        hint_str = self.hints[name][:-1]
                    else:
                        hint_str = self.hints[name]
                    helpstr = hint_str + \
                    ' (accepted values min=%g, max=%g).' %(self.properties[name].minimum, self.properties[name].maximum)
                else:
                    helpstr = self.hints[name]
                    if helpstr.find('\n'):
                        helpstr = '; '.join(helpstr.split('\n'))
                self.rst_file.write('%-80s %-80s %s\n' % (name, self.parameters[name], helpstr))
        self.rst_file.write('%-80s %-80s %s\n\n' %(78*'=', 78*'=', 100*'='))


    def write_sample_parameter_file(self):
        self.rst_file.write('\n\n.. _{0}_parameter_file_for_{1}:'.format(self.progname, self.this_level))
        heading = '\n\nSample parameter file'
        if self.this_level not in ['beginner']:
            heading = heading + ' ({0} level)'.format(self.this_level)
        self.rst_file.write(heading + '\n')
        self.rst_file.write('%-60s\n' %(58*'~'))
        self.rst_file.write('\nYou may run the program in the command line by providing the parameters via a text file::')
        self.rst_file.write('\n\n    %s --f parameterfile.txt\n' %self.progname)
        self.rst_file.write('\nWhere the format of the parameters is::\n\n')
        for name in self.parameters:
            if self.level[name] in self.this_levels:
                self.rst_file.write('    %-40s = %s\n' % (name, self.parameters[name]))


    def programstr(self):
        self.rst_file.write(2*'\n' + 'Program flow\n' + 20*'~' + '\n')
        for state in self.program_states:
            self.rst_file.write('#. {0}: {1}\n'.format(state, self.program_states[state]))
        self.rst_file.write(2*'\n' + 'Functions\n' + 20*'~' + '\n')
        self.rst_file.write('\n.. toctree::\n')
        self.rst_file.write('   :maxdepth: 1\n')
        self.codefile_name = '{0}_functions{1}rst'.format(self.progname, os.extsep)
        self.rst_file.write('\n   {0}'.format(os.path.splitext(self.codefile_name)[0]))
        self.rst_file.close()

    def generate_functions_file(self):
        self.code_file = open(self.codefile_name, 'w')
        self.code_file.write('.. _{0}:\n'.format(os.path.splitext(self.codefile_name)[0]))
        self.code_file.write('\nDocumented functions with links to source\n' + 45 * '~' + '\n')
        for each_file in self.code_files:
            self.code_file.write('\n.. automodule:: {0}\n'.format(each_file))
            self.code_file.write('    :members:\n')
            self.code_file.write('    :undoc-members:\n\n')
        
        self.code_file.close()

def main():
    gal = Gallery()
        
if __name__ == '__main__':
    main()
