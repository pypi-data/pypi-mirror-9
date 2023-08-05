#!/usr/bin/env python
"""
Test module to check micctfdetermine
"""
from glob import glob
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.micprgs.micctfdetermine import MicCtfDetermine, MicCtfDeterminePar
from spring.segment2d.segmentctfapply import SegmentCtfApply
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segment import MicrographHelixPreparation
import numpy as np
import os
import shutil
import sys


class TestMicCtfDeterminePreparation(object):

    def setup_of_common_non_mpi_parameters(self):
        self.feature_set = MicCtfDeterminePar()
        self.pixelsize = 5.0
        self.avg_defocus=40000
        self.voltage=200
        self.cs=2.0
        self.ampcont=0.1
        self.astigmatism=5000
        self.astigmatism_angle=33.0
        
        self.micrograph_file = 'test_mic.hdf'
        self.diagnostic_output = 'test_output.pdf'
        
        MicrographHelixPreparation().prepare_ctf_micrograph(self.micrograph_file, self.avg_defocus, self.cs,
        self.voltage, self.pixelsize, self.ampcont, self.astigmatism, self.astigmatism_angle)

        self.feature_set.parameters['Micrographs']='test_mic.hdf'
        self.feature_set.parameters['Diagnostic plot pattern']=self.diagnostic_output
        
        self.feature_set.parameters['Spring database option']=False
        self.feature_set.parameters['spring.db file']=os.pardir + os.sep + 'spring.db'
        self.feature_set.parameters['Continue spring.db option']=False
            
        self.pardir = os.path.pardir
            
        self.feature_set.parameters['Pixel size in Angstrom'] = self.pixelsize
        self.feature_set.parameters['Spherical aberration'] = self.cs
        self.feature_set.parameters['Electron voltage in kV'] = self.voltage
        self.feature_set.parameters['Amplitude contrast'] = self.ampcont
        self.feature_set.parameters['Tile size power spectrum in Angstrom'] = 640
        self.feature_set.parameters['Range of defocus in Angstrom'] =((self.avg_defocus - 5000, self.avg_defocus + 5000))
        self.feature_set.parameters['Defocus search step size'] = 500
        self.feature_set.parameters['Astigmatism search restraint in Angstrom']=6000
        self.feature_set.parameters['Resolution search range in Angstrom']= ((300.0, 10.0))
        self.feature_set.parameters['CTFTILT refine option']=True
        self.feature_set.parameters['Local defocus search range'] = 5000
        self.feature_set.parameters['Expected tilt and tilt search range in degrees']= ((0, 10))

        self.feature_set.parameters['Binning option'] = False
        self.feature_set.parameters['Binning factor'] = 1
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
            
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)
        
class TestMicCtfDetermine(TestMicCtfDeterminePreparation, MicCtfDetermine):

    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()
        self.setup_of_common_non_mpi_parameters()
        super(TestMicCtfDetermine, self).__init__(self.feature_set)
        

    def check_avg_defocus(self):
        defocus1 = self.ctftilt_parameters.defocus1
        defocus2 = self.ctftilt_parameters.defocus2
        determined_defocus = round(defocus1 + defocus2) / 2
        sys.stderr.write('\n{avg_def} = {det_def} '.format(avg_def=self.avg_defocus, det_def=determined_defocus))
        assert self.avg_defocus == round(determined_defocus, -3)
        return defocus1, defocus2


    def check_astigmatism_and_astigmation_angle(self):
        defocus1 = self.ctftilt_parameters.defocus1
        defocus2 = self.ctftilt_parameters.defocus2
        
        astigmation_angle = self.ctftilt_parameters.astigmation_angle
        
        determined_defocus, determined_astigmatism, determined_astig_angle = \
        SegmentCtfApply().convert_mrc_defocus_to_sparx_defocus(defocus1, defocus2, astigmation_angle)
        
        sys.stderr.write('\n{avg_def} = {det_def} '.format(avg_def=self.avg_defocus, det_def=determined_defocus))
        assert self.avg_defocus == round(determined_defocus, -3)
        sys.stderr.write('\n{astig} = {det_astig} '.format(astig=self.astigmatism, det_astig=determined_astigmatism))
        assert self.astigmatism == round(determined_astigmatism, -3)
        
        sys.stderr.write('\n{a_angle} = {det_a_angle} '.format(a_angle=self.astigmatism_angle,
        det_a_angle=determined_astig_angle))
        
        assert self.astigmatism_angle == round(determined_astig_angle, -1)


    def check_tilt_angle(self):
        determined_tilt_angle = self.ctftilt_parameters.tilt_angle
        
        sys.stderr.write('\n{exp_angle} = {tilt_angle} '.format(exp_angle=self.expected_tilt_angle,
        tilt_angle=determined_tilt_angle))
        
        assert self.expected_tilt_angle == round(determined_tilt_angle)

    def check_that_parameters_were_correctly_detemined(self):
        defocus1, defocus2 = self.check_avg_defocus()
        self.check_astigmatism_and_astigmation_angle(defocus1, defocus2)
        self.check_tilt_angle()

    def teardown(self):
        database_file = 'spring.db'
        assert os.path.isfile(database_file)
        os.remove(database_file)
        os.remove(self.micrograph_file)
        
        logfiles = glob('test*{sep}log'.format(sep=os.extsep))
        diag_files = glob('test*{sep}pdf'.format(sep=os.extsep))
        for each_file in logfiles + diag_files:
            os.remove(each_file)
            
        self.testingdir.remove()


class TestMicCtfDetermineMain(TestMicCtfDetermine):
    def do_test_case_scd1(self):
        self.determine_ctf()


class TestMicCtfDetermineMore(TestMicCtfDetermine):
    def do_test_case_scd2(self):
        self.feature_set.parameters['CTFTILT refine option']=False
        super(TestMicCtfDetermine, self).__init__(self.feature_set)
            
        self.determine_ctf()
    
    def do_test_case_scd3(self):
        astigmation_angles = np.linspace(20, 160, 8)
        for each_angle in astigmation_angles:
            self.astigmatism_angle = each_angle
            
            MicrographHelixPreparation().prepare_ctf_micrograph(self.micrograph_file, self.avg_defocus, self.cs,
            self.voltage, self.pixelsize, self.ampcont, self.astigmatism, self.astigmatism_angle)
            
            if os.path.exists('spring.db'):
                os.remove('spring.db')
            self.determine_ctf()
            self.check_astigmatism_and_astigmation_angle()

        
class TestMicCtfDetermineEndtoEnd(TestMicCtfDetermine):
    def do_end_to_end_test_scd_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        self.pardir = os.path.curdir
 
    def do_end_to_end_test_scd_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        self.pardir = os.path.curdir
        
class TestMicCtfDetermineMpi(TestMicCtfDetermine):
    def do_end_to_end_test_sa_inputfile_with_MPI(self):
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        self.feature_set.parameters['Micrographs']='test_mi?.hdf'
        shutil.copy(self.micrograph_file, 'test_mi1.hdf')
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        os.remove('test_mi1.hdf')
        self.pardir = os.path.curdir

    def do_end_to_end_test_sa_inputfile_no_CTFTILT_with_MPI(self):
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        self.feature_set.parameters['CTFTILT refine option']=False
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        self.pardir = os.path.curdir
        
def main():
    trc = TestMicCtfDetermineMain()
    trc.setup()
    trc.do_test_case_scd1()
        
if __name__ == '__main__':
    main()
