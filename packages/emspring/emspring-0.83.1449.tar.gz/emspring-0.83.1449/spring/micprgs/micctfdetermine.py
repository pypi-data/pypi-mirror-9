# Author: Carsten Sachse 09-Aug-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to determine CTF parameters from a set of micrographs using CTFFIND and CTFTILT (Mindell and Grigorieff JSB, \
2003)
"""
from EMAN2 import EMData, EMNumPy
from collections import namedtuple
from spring.csinfrastr.csdatabase import CtfMicrographTable, CtfFindMicrographTable, CtfTiltMicrographTable, base, \
    SpringDataBase
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import DiagnosticPlot, Temporary, OpenMpi
from spring.csinfrastr.csreadinput import OptHandler
from spring.micprgs.micexam import MicrographExam
from tabulate import tabulate
import matplotlib.cm as cm
import numpy as np
import os
import shutil
import subprocess

class MicCtfDeterminePar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'micctfdetermine'
        self.proginfo = __doc__
        self.code_files = [self.progname, self.progname + '_mpi']

        self.micctfdetermine_features = Features()
        self.feature_set = self.micctfdetermine_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()


    def define_parameters_and_their_properties(self):

        self.feature_set = self.micctfdetermine_features.set_inp_multiple_micrographs(self.feature_set)
        self.feature_set = self.micctfdetermine_features.set_output_plot_pattern(self.feature_set, self.progname + \
        '_diag.pdf')
        
        self.feature_set = self.micctfdetermine_features.set_spring_db_option(self.feature_set, 'expert', False)
        self.feature_set = self.micctfdetermine_features.set_spring_path(self.feature_set, 'expert')
        self.feature_set = self.set_spring_db_continue_option(self.feature_set)
        
        self.feature_set = self.set_spherical_aberration(self.feature_set)
        self.feature_set = self.set_electron_voltage(self.feature_set)
        self.feature_set = self.set_amplitude_contrast(self.feature_set)
        self.feature_set = self.micctfdetermine_features.set_pixelsize(self.feature_set)
        self.feature_set = self.set_defocus_range(self.feature_set)
        self.feature_set = self.set_defocus_search_step_size(self.feature_set)
        self.feature_set = self.set_astigmatism_restraint(self.feature_set)
        self.feature_set = self.micctfdetermine_features.set_power_tile_size(self.feature_set, 600, power_of_2_hint=True)
        self.feature_set = self.set_resolution_range(self.feature_set)
        self.feature_set = self.set_ctftilt_option(self.feature_set)
        self.feature_set = self.set_ctftilt_search_range(self.feature_set)
        self.feature_set = self.set_tilt_range(self.feature_set)
    
        self.feature_set = self.micctfdetermine_features.set_binning_option(self.feature_set, default=True)
        self.feature_set = self.micctfdetermine_features.set_binning_factor(self.feature_set, binfactor=2)
        
        self.feature_set = self.micctfdetermine_features.set_mpi(self.feature_set)
        self.feature_set = self.micctfdetermine_features.set_ncpus_scan(self.feature_set)
        self.feature_set = self.micctfdetermine_features.set_temppath(self.feature_set)
    
    def define_program_states(self):
        # status dictionary
        self.feature_set.program_states['prepare_micrograph_for_ctffind']='Prepare micrographs for CTFFIND.'
        self.feature_set.program_states['run_ctffind_for_first_defocus_estimation']='Runs CTFFIND on micrographs to ' +\
        'determine defocus'
        self.feature_set.program_states['run_ctftilt_to_refine_defocus_parameters']='Runs CTFTILT on micrographs to ' +\
        'refine local defocus'
        self.feature_set.program_states['assemble_diagnostic_plot']='Assembles summarized diagnostic plot of ' +\
        'micrograph.'

    
    def set_spring_db_continue_option(self, feature_set):
        inp6 = 'Continue spring.db option'
        feature_set.parameters[inp6] = bool(False)
        feature_set.hints[inp6] = 'Continue spring.db without re-computing previously determined CTF of micrographs. '+\
        'Do not tick in case you want to update the Ctf results of the micrographs in the provided database.'
        feature_set.relatives[inp6]='Spring database option'
        feature_set.level[inp6]='expert'
        
        return feature_set
    

    def set_spherical_aberration(self, feature_set):
        inp6 = 'Spherical aberration'
        feature_set.parameters[inp6]=float(2.0)
        feature_set.hints[inp6]= 'Spherical aberration - property of your electron microscope.'
        feature_set.properties[inp6]=feature_set.Range(0,10,0.01)
        feature_set.level[inp6]='beginner'
        
        return feature_set

        
    def set_electron_voltage(self, feature_set):
        inp6 = 'Electron voltage in kV'
        feature_set.parameters[inp6]=int(200)
        feature_set.hints[inp6]= 'Electron beam voltage of your microscope in kV.'
        feature_set.properties[inp6]=feature_set.Range(0, 1000, 10)
        feature_set.level[inp6]='beginner'
        
        return feature_set


    def set_amplitude_contrast(self, feature_set):
        inp6 = 'Amplitude contrast'
        feature_set.parameters[inp6]=float(0.1)
        feature_set.hints[inp6]= 'Amplitude contrast (between 0 and 1). For cryo data ranges from 0.07 to 0.14 and ' +\
        'negative stain from 0.1 - 0.4 have been reported.'
        feature_set.properties[inp6]=feature_set.Range(0, 1, 0.01)
        feature_set.level[inp6]='expert'
        
        return feature_set
    
    
    def set_defocus_range(self, feature_set):
        inp7 = 'Range of defocus in Angstrom'
        feature_set.parameters[inp7] = tuple(( int(10000), int(45000) ))
        feature_set.hints[inp7] = 'Images were taken at this defocus range in Angstrom. Positive values for ' +\
        'underfocus. FEI microscopes tend to have an offset to the theoretical values of 6000 Angstrom.'
        feature_set.properties[inp7] = feature_set.Range(0, 100000, 1000)
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    
    
    def set_astigmatism_restraint(self, feature_set):
        inp7 = 'Astigmatism search restraint in Angstrom'
        feature_set.parameters[inp7] = int(2000)
        feature_set.hints[inp7] = 'Astigmatism in Angstrom. This is useful in case Thon rings are not well visible.'
        feature_set.properties[inp7] = feature_set.Range(0, 50000, 100)
        feature_set.level[inp7]='expert'
        
        return feature_set
    
    
    def set_defocus_search_step_size(self, feature_set):
        inp6 = 'Defocus search step size'
        feature_set.parameters[inp6]=int(300)
        feature_set.hints[inp6]= 'Choose defocus search step size. Smaller step size will result in slower search.'
        feature_set.properties[inp6]=feature_set.Range(0, 5000, 100)
        feature_set.level[inp6]='expert'
        
        return feature_set

        
    def set_resolution_range(self, feature_set):
        inp7 = 'Resolution search range in Angstrom'
        feature_set.parameters[inp7] = tuple(( float(200), float(6) ))
        feature_set.hints[inp7] = 'Maximum and minimum resolution rings to be included in CTF determination.'
        feature_set.properties[inp7] = feature_set.Range(0, 100000, 1)
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    
    
    def set_ctftilt_option(self, feature_set):
        inp6 = 'CTFTILT refine option'
        feature_set.parameters[inp6] = bool(True)
        feature_set.hints[inp6] = 'Use CTFTILT to refine defocus by assuming a defocus gradient across the micrograph.'
        feature_set.level[inp6]='expert'
        
        return feature_set


    def set_ctftilt_search_range(self, feature_set):
        inp6 = 'Local defocus search range'
        feature_set.parameters[inp6]=int(3000)
        feature_set.hints[inp6]= 'Using the given search range for CTFTILT to refine locally around CTFFIND maximum.' 
        feature_set.properties[inp6]=feature_set.Range(0, 20000, 100)
        feature_set.relatives[inp6]='CTFTILT refine option'
        feature_set.level[inp6]='expert'
        
        return feature_set


    def set_tilt_range(self, feature_set):
        inp7 = 'Expected tilt and tilt search range in degrees'
        feature_set.parameters[inp7] = tuple(( int(0), int(8) ))
        feature_set.hints[inp7] = 'Minimum and maximum micrograph tilt to be searched in CTFTILT determination.'
        feature_set.properties[inp7] = feature_set.Range(0, 80, 1)
        feature_set.relatives[inp7]=('CTFTILT refine option', 'CTFTILT refine option')
        feature_set.level[inp7]='expert'
        
        return feature_set
    
    
class MicCtfDeterminePreparation(object):
    """
    * Class that holds all functions required for splitting micrographs 

    * __init__ Function to read in the entered parameter dictionary, load micrograph and initialize \
                    unique temporary directory

    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None: 
            self.feature_set = parset
            p = self.feature_set.parameters
            self.infile=p['Micrographs']
            self.micrograph_files = Features().convert_list_of_files_from_entry_string(self.infile)
            self.outfile=p['Diagnostic plot pattern']
            
            self.spring_db_option = p['Spring database option']
            self.spring_path = p['spring.db file']
            self.continue_spring_db = p['Continue spring.db option']
            
            self.ori_pixelsize=p['Pixel size in Angstrom']
            self.spherical_aberration=p['Spherical aberration']
            self.voltage=p['Electron voltage in kV']
            self.amplitude_contrast=p['Amplitude contrast']
            self.tile_size_A = p['Tile size power spectrum in Angstrom']
            self.minimum_defocus, self.maximum_defocus = p['Range of defocus in Angstrom']
            self.defocus_step = p['Defocus search step size']
            self.astigmatism_restraint = p['Astigmatism search restraint in Angstrom']
            self.maximum_resolution, self.minimum_resolution = p['Resolution search range in Angstrom']
            self.ctftilt_option = p['CTFTILT refine option']
            self.local_defocus_range=p['Local defocus search range']
            self.expected_tilt_angle, self.tilt_range = p['Expected tilt and tilt search range in degrees']

            self.binoption=p['Binning option']
            self.binfactor=p['Binning factor']
            if self.binfactor == 1 and self.binoption is True:
                self.binoption = False

            self.mpi_option = p['MPI option']
            self.cpu_count = p['Number of CPUs']
            self.temppath=p['Temporary directory']


    def convert_to_mrc_if_required(self, non_mrc_micrograph):
        micrograph = EMData()
        micrograph.read_image(non_mrc_micrograph)
        micrograph.del_attr('ctf')
        
        mrc_micrograph = '{tmpdir}{body}{sep}mrc'.format(tmpdir=self.tempdir,
        body=os.path.splitext(os.path.basename(non_mrc_micrograph))[0], sep=os.extsep)
        
        micrograph.write_image(mrc_micrograph)
        
        return mrc_micrograph
        
        
class MicCtfDetermineFind(MicCtfDeterminePreparation):
    def start_program_and_capture_output(self, diagnostic_power_montage, ctffind_or_ctftilt_exe, script,
    ctffind_or_ctftilt_report_file):
        ctftilt_log = open(ctffind_or_ctftilt_report_file, 'w')
        try:
            os.environ['NCPUS']='1'
            ctftilt_process = subprocess.Popen(ctffind_or_ctftilt_exe, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            shell=True)
            
            log_stdout, log_stderr = ctftilt_process.communicate(input=script)
            ctftilt_process.wait()
        except:
            error_message = '{prg} could not be launched. Please, check the existence of {prg} and your PATH variable.'\
            .format(prg=ctffind_or_ctftilt_exe[0])
            
            raise ValueError(error_message)
        ctftilt_log.write(log_stdout.__str__())
        if log_stderr is not None:
            ctftilt_log.write(log_stderr.__str__())
        ctftilt_log.close()
        OpenMpi().check_expected_output_file(ctffind_or_ctftilt_exe[0], diagnostic_power_montage)


    def determine_closest_power_of_two(self, tilesize):
        """
        >>> from spring.micprgs.micctfdetermine import MicCtfDetermine
        >>> MicCtfDetermine().determine_closest_power_of_two(100)
        128
        >>> MicCtfDetermine().determine_closest_power_of_two(78)
        64
        """
        powers = 2 ** np.arange(20)
        closest = np.argmin(np.abs(tilesize - powers))
        
        return powers[closest]
    
    
    def launch_ctffind(self, micrograph_file):
        magnification = 59000.0
        
        find_power_montage = self.tempdir + 'ctffind_power{0}.mrc'.format(os.getpid())
#        find_power_montage = os.path.splitext(micrograph_file)[0] + 'find_power{0}.mrc'
        ctffind_exe = ['ctffind3_mp.exe', ' <<eof']
        
        tile_size_power_2 = self.determine_closest_power_of_two(self.tile_size)
        script = """{mic}\n{pow}\n{cs}, {ht}, {ampcnst}, {mag}, {scanstep}\n{box}, {resmax}, {resmin}, {dfmin}, {dfmax},
        {fstep}, {rastig}\neof""".format(mic=micrograph_file, pow=find_power_montage, cs=self.spherical_aberration,
        ht=self.voltage, ampcnst=self.amplitude_contrast, mag=magnification, scanstep=(self.pixelsize * magnification *\
        1e-4), box=tile_size_power_2, resmax=self.maximum_resolution, resmin=self.minimum_resolution,
        dfmin=self.minimum_defocus, dfmax=self.maximum_defocus, fstep=self.defocus_step, 
        rastig=self.astigmatism_restraint)
        
        ctffind_report_file = '{dir}{sep}{body}_ctffind{extsep}log'.format(dir=os.path.abspath(os.curdir), sep=os.sep,
        body=os.path.splitext(os.path.basename(micrograph_file))[0], extsep=os.extsep)
        
        self.start_program_and_capture_output(find_power_montage, ctffind_exe, script, ctffind_report_file)
        
        return ctffind_report_file, find_power_montage
    

    def analyze_ctffind_report_file(self, report_file):
        ctffind_output = open(report_file)
        ctffind_lines = ctffind_output.readlines()
        ctffind_output.close
        
        found = False
        for each_line in ctffind_lines:
            if each_line.find('Final Values') > 0: 
                
                extracted_values = each_line.split()
                defocus1 = float(extracted_values[0])
                defocus2 = float(extracted_values[1])
                astigmation_angle = float(extracted_values[2])
                cross_correlation = float(extracted_values[3])
                
                found = True
                
        if not found:
            error_message = 'CTFFIND did not finish successfully. Please check {0} logfile for details.'.\
            format(report_file)
            
            raise ValueError(error_message)
        
        return defocus1, defocus2, astigmation_angle, cross_correlation
        

    def update_determined_ctffind_values_for_micrograph(self, current_mic, ctffind_parameters, pixelsize):
        current_mic.pixelsize = pixelsize
        current_mic.defocus_avg = sum([ctffind_parameters.defocus1, ctffind_parameters.defocus2]) / 2
        current_mic.defocus1 = ctffind_parameters.defocus1
        current_mic.defocus2 = ctffind_parameters.defocus2
        current_mic.astigmation_angle = ctffind_parameters.astigmation_angle
        current_mic.cc_score = ctffind_parameters.cc_score
        
        return current_mic
    

    def make_new_micrograph_entry_with_ctffind_parameters(self, micrograph_file, ori_pixelsize, ctf_parameters,
    ctffind_parameters):
        current_mic = CtfMicrographTable()
        current_mic.dirname = os.path.dirname(micrograph_file)
        current_mic.micrograph_name = os.path.basename(micrograph_file)
        current_mic.voltage = ctf_parameters.voltage
        current_mic.spherical_aberration = ctf_parameters.spherical_aberration
        current_mic.amplitude_contrast = ctf_parameters.amplitude_contrast
        current_mic.ctffind_determined = True
        current_mic.pixelsize = ori_pixelsize
        current_mic_find = CtfFindMicrographTable()
        current_mic_find.dirname = os.path.dirname(micrograph_file)
        current_mic_find.micrograph_name = os.path.basename(micrograph_file)
        current_mic_find.pixelsize = ctf_parameters.pixelsize
        current_mic_find.ctf_micrographs = current_mic
        
        current_mic_find = self.update_determined_ctffind_values_for_micrograph(current_mic_find, ctffind_parameters,
        ctf_parameters.pixelsize)
        
        current_mic_tilt = CtfTiltMicrographTable()
        current_mic_tilt.ctf_micrographs = current_mic
        
        return current_mic_find, current_mic_tilt
    

    def query_micrograph_name_in_database(self, session, micrograph_file):
        matched_mic = session.query(CtfFindMicrographTable).\
        filter(CtfFindMicrographTable.micrograph_name == os.path.basename(micrograph_file)).first()
        
        return matched_mic


    def enter_ctffind_values_in_database(self, session, micrograph_file, ori_pixelsize, ctf_parameters,
    ctffind_parameters):
        
        matched_mic = self.query_micrograph_name_in_database(session, micrograph_file)
        
        if matched_mic is not None:
#            matched_mic = self.session.query(CtfFindMicrographTable).get(matched_mic_id)
            matched_mic.pixelsize = ctf_parameters.pixelsize
            
            matched_mic = self.update_determined_ctffind_values_for_micrograph(matched_mic, ctffind_parameters,
            ctf_parameters.pixelsize)
            
            session.merge(matched_mic)
        else:
            current_mic_find, current_mic_tilt = self.make_new_micrograph_entry_with_ctffind_parameters(micrograph_file,
            ori_pixelsize, ctf_parameters, ctffind_parameters)
            
            session.add(current_mic_find)
            session.add(current_mic_tilt)
        
        return session
        

    def make_ctffind_parameters_named_tuple(self):
        ctffind_parameters = namedtuple('ctffind', 'defocus1 defocus2 astigmation_angle cc_score')
        
        return ctffind_parameters
    

    def run_ctffind_for_first_defocus_estimation(self, micrograph_file):
        self.log.fcttolog()
    
        ctffind_report_file, find_power_montage = self.launch_ctffind(micrograph_file)
        
        self.defocus1, self.defocus2, astigmation_angle, cc_score = \
        self.analyze_ctffind_report_file(ctffind_report_file)
        
        ctffind_parameters = self.make_ctffind_parameters_named_tuple()
        ctffind_parameters = ctffind_parameters._make([self.defocus1, self.defocus2, astigmation_angle, cc_score])

        return ctffind_parameters, ctffind_report_file, find_power_montage
    
    
class MicCtfDetermineTilt(MicCtfDetermineFind):
    def launch_ctftilt(self, micrograph_file, found_defocus):
        magnification = 59000.0
        
        current_dir = os.path.abspath(os.curdir)
        os.chdir(os.path.abspath(os.path.dirname(micrograph_file)))
#        tilt_power_montage = os.path.splitext(micrograph_file)[0] + '_tilt_power.mrc'
        tilt_power_montage = self.tempdir + 'ctftilt_power{0}.mrc'.format(os.getpid())
        ctftilt_exe = ['ctftilt_mp.exe', ' <<eof']
        
        tile_size_power_2 = self.determine_closest_power_of_two(self.tile_size)
        script = """{mic}\n{pow}\n{cs}, {ht}, {ampcnst}, {mag}, {scanstep}, 1\n{box}, {resmax}, {resmin}, {dfmin},
        {dfmax}, {fstep}, {rastig}, {tangle}, {trange}\neof""".format(mic=os.path.basename(micrograph_file),
        pow=tilt_power_montage, cs=self.spherical_aberration, ht=self.voltage, box=tile_size_power_2,
        resmax=self.maximum_resolution, ampcnst=self.amplitude_contrast, mag=magnification, scanstep=self.pixelsize *\
        magnification * 1e-4, resmin=self.minimum_resolution, dfmin=found_defocus - self.local_defocus_range,
        dfmax=found_defocus + self.local_defocus_range, fstep=self.defocus_step, rastig=self.astigmatism_restraint, 
        tangle=self.expected_tilt_angle, trange=self.tilt_range)
        
        ctftilt_report_file = '{dir}{sep}{body}_ctftilt{extsep}log'.format(dir=current_dir, sep=os.sep,
        body=os.path.splitext(os.path.basename(micrograph_file))[0], extsep=os.extsep)
        
        self.start_program_and_capture_output(tilt_power_montage, ctftilt_exe, script, ctftilt_report_file)
        
        os.chdir(current_dir)
        
        return ctftilt_report_file, tilt_power_montage
    
        
    def make_ctftilt_parameters_named_tuple(self):
        ctftilt_params = namedtuple('ctftilt', 'defocus1 defocus2 astigmation_angle tilt_axis tilt_angle ' +\
        'cross_correlation center_x center_y')

        return ctftilt_params


    def analyze_ctftilt_report_file(self, report_file):
        ctftilt_output = open(report_file)
        ctftilt_lines = ctftilt_output.readlines()
        ctftilt_output.close
        
        ctftilt_params = self.make_ctftilt_parameters_named_tuple()
        ctftilts = []
        found = False
        for each_line in ctftilt_lines:
            if each_line.find('Final Values') > 0: 
                extracted_values = each_line.split()
                ctftilts.append(float(extracted_values[0]))
                ctftilts.append(float(extracted_values[1]))
                ctftilts.append(float(extracted_values[2]))
                ctftilts.append(float(extracted_values[3]))
                ctftilts.append(float(extracted_values[4]))
                ctftilts.append(float(extracted_values[5]))
                
            if each_line.find('CENTER_X') > 0: 
                ctftilts.append(float(each_line.split()[4]))
            if each_line.find('CENTER_Y') > 0: 
                ctftilts.append(float(each_line.split()[4]))
                found = True
                
        if not found:
            error_message = 'CTFTILT did not finish successfully. Please check {0} logfile for details.'.\
            format(report_file)
            
            raise ValueError(error_message)

        ctftilt_parameters = ctftilt_params._make(ctftilts)
            
        return ctftilt_parameters
    
        
    def enter_additional_ctftilt_parameters(self, current_mic, ctftilt_parameters):
        
        current_mic.type = 'CtfTiltMicrographs'
        current_mic.tilt_angle = ctftilt_parameters.tilt_angle
        current_mic.tilt_axis = ctftilt_parameters.tilt_axis
        current_mic.center_x = ctftilt_parameters.center_x
        current_mic.center_y = ctftilt_parameters.center_y
        
        return current_mic
    
        
    def update_determined_ctftilt_values_for_micrograph(self, current_mic, pixelsize, ctftilt_parameters):
        ctffind_equivalents = namedtuple('cttffinds', 'defocus1 defocus2 astigmation_angle cc_score')
        
        ctffind_equivalents_params = ctffind_equivalents._make([ctftilt_parameters.defocus1,
        ctftilt_parameters.defocus2, ctftilt_parameters.astigmation_angle, ctftilt_parameters.cross_correlation])
        
        current_mic = self.update_determined_ctffind_values_for_micrograph(current_mic, ctffind_equivalents_params,
        pixelsize)
        
        return current_mic
        
        
    def enter_ctftilt_values_in_database(self, session, micrograph_file, pixelsize, ctftilt_parameters):
        
        matched_mic_id = session.query(CtfFindMicrographTable.id).\
        filter(CtfFindMicrographTable.micrograph_name == os.path.basename(micrograph_file)).first()
        
        if matched_mic_id is not None:
            matched_mic = session.query(CtfMicrographTable).get(matched_mic_id)
            matched_mic.ctftilt_determined = True
            session.merge(matched_mic)
            matched_mic_tilt = session.query(CtfTiltMicrographTable).get(matched_mic_id)
            
            matched_mic_tilt = self.update_determined_ctftilt_values_for_micrograph(matched_mic_tilt, pixelsize,
            ctftilt_parameters)
            
            matched_mic_tilt = self.enter_additional_ctftilt_parameters(matched_mic_tilt, ctftilt_parameters)
            matched_mic_tilt = session.merge(matched_mic_tilt)
        
        return session
            
            
    def run_ctftilt_to_refine_defocus_parameters(self, micrograph_file, found_defocus):
        self.log.fcttolog()
        
        ctftilt_report_file, tilt_power_montage = self.launch_ctftilt(micrograph_file, found_defocus)
        ctftilt_parameters = self.analyze_ctftilt_report_file(ctftilt_report_file)
        
        return ctftilt_parameters, ctftilt_report_file, tilt_power_montage
    
    
class MicCtfDetermineDiagnosticPlot(MicCtfDetermineTilt):

    def add_montage_images(self, find_power_montage, subplot):
        if find_power_montage is not None:
            montage = EMData()
            montage.read_image(find_power_montage)
            montage_np = np.copy(EMNumPy.em2numpy(montage))
            subplot.imshow(montage_np, cmap=cm.gray, interpolation='nearest')
        
        subplot.set_xticks([])
        subplot.set_yticks([])

        return subplot


    def add_final_values_from_ctffind_or_ctftilt_report_files(self, ctffind_report, subplot):
        if ctffind_report is not None:
            ctffind_output = open(ctffind_report)
            ctffind_lines = ctffind_output.readlines()
            ctffind_output.close
        else:
            ctffind_lines = []
        
        found_tilt_line = None
        printed_text = ''
        for each_line in ctffind_lines:
            if each_line.find('DFMID') > 0: 
                printed_text += each_line
            if each_line.find('Final Values') > 0: 
                printed_text += each_line
            if each_line.find('EQUATION FOR CALCULATING DEFOCUS DFL1,DFL2 AT LOCATION NX,NY') > 0: 
                found_tilt_line = True
            if found_tilt_line:
                printed_text += each_line
        
        subplot.text(0.5, 0.5, printed_text, horizontalalignment='center', verticalalignment='center', 
                     transform = subplot.transAxes, fontsize=3)
        subplot.set_yticks([])
        subplot.set_xticks([])
        
        return subplot
        
        
    def assemble_diagnostic_plot(self, find_power_montage, ctffind_report_file, tilt_power_montage, ctftilt_report_file,
    infile, outfile):
        self.log.fcttolog()

        micctfdetermine_plot = DiagnosticPlot()
        self.fig = micctfdetermine_plot.add_header_and_footer(self.feature_set, infile, outfile)
        ax1 = micctfdetermine_plot.plt.subplot2grid((2,3), (0,0), colspan=1, rowspan=1)
        ax2 = micctfdetermine_plot.plt.subplot2grid((2,3), (1,0), colspan=1, rowspan=1)
        ax3 = micctfdetermine_plot.plt.subplot2grid((2,3), (0,1), colspan=1, rowspan=2)
        ax4 = micctfdetermine_plot.plt.subplot2grid((2,3), (0,2), colspan=1, rowspan=2)
        
        added_statement = 'added to diagnostic output plot.\n'
        log_statement = 'Diagnostics for {0}:\n'.format(infile)
        ax1.set_title('CTFFIND power montage', fontsize=8)
        self.add_montage_images(find_power_montage, ax1)
        log_statement += 'CTFFIND montage {0}'.format(added_statement)
        
        ax2.set_title('CTFTILT power montage', fontsize=8)
        self.add_montage_images(tilt_power_montage, ax2)
        log_statement += 'CTFTILT montage {0}'.format(added_statement)
        
        ax3.set_title('CTFFIND report', fontsize=8)
        self.add_final_values_from_ctffind_or_ctftilt_report_files(ctffind_report_file, ax3)
        log_statement += 'Essential CTFFIND report output {0}'.format(added_statement)
        
        ax4.set_title('CTFTILT report', fontsize=8)
        self.add_final_values_from_ctffind_or_ctftilt_report_files(ctftilt_report_file, ax4)
        log_statement += 'Essential CTFTILT report output {0}'.format(added_statement)
        
        self.log.ilog(log_statement)
        
        self.fig.savefig(outfile, dpi=600)
        
    
class MicCtfDetermine(MicCtfDetermineDiagnosticPlot):

    def prepare_micrograph_for_ctffind(self, each_micrograph_file):
        self.log.fcttolog()
        
        each_micrograph_file, self.pixelsize, self.tile_size = MicrographExam().bin_micrograph(each_micrograph_file,
        self.binoption, self.binfactor, self.ori_pixelsize, self.tile_size_A, self.tempdir)
        
        if not each_micrograph_file.endswith('mrc'):
            each_micrograph_file = self.convert_to_mrc_if_required(each_micrograph_file)
            
        self.log.ilog('{0} will be used for further CTF determination.'.format(each_micrograph_file))
        
        return each_micrograph_file


    def make_empty_ctftilt_parameters(self):
        np_ctftilt = self.make_ctftilt_parameters_named_tuple()
        ctftilt_parameters = np_ctftilt._make(8 * [None])

        return ctftilt_parameters


    def run_ctffind_and_ctftilt_for_each_micrograph(self, micrograph_files, outfiles, each_micrograph_index,
    each_micrograph_file):
        
        each_micrograph_file = self.prepare_micrograph_for_ctffind(each_micrograph_file)
        
        ctffind_parameters, ctffind_report_file, find_power_montage = \
        self.run_ctffind_for_first_defocus_estimation(each_micrograph_file)
        
        self.log.plog(90 * (each_micrograph_index + 0.4) / len(micrograph_files) + 10)
        if self.ctftilt_option:
            ctftilt_parameters, ctftilt_report_file, tilt_power_montage = \
            self.run_ctftilt_to_refine_defocus_parameters(each_micrograph_file, (ctffind_parameters.defocus1 +
            ctffind_parameters.defocus2) / 2)
            
            self.log.plog(90 * (each_micrograph_index + 0.8) / len(micrograph_files) + 10)
        else:
            tilt_power_montage = None
            ctftilt_report_file = None
            ctftilt_parameters = self.make_empty_ctftilt_parameters()
            
        self.assemble_diagnostic_plot(find_power_montage, ctffind_report_file, tilt_power_montage, ctftilt_report_file,
        os.path.basename(each_micrograph_file), outfiles[each_micrograph_index])
        
        os.remove(find_power_montage)
        if tilt_power_montage is not None:
            os.remove(tilt_power_montage)
        if not micrograph_files[each_micrograph_index].endswith('mrc') or self.binoption:
            os.remove(each_micrograph_file)

        self.log.plog(90 * (each_micrograph_index + 1) / len(micrograph_files) + 10)
        
        return ctffind_parameters, ctftilt_parameters


    def filter_previously_determined_micrographs(self, session, micrograph_files):
        if self.spring_db_option and self.continue_spring_db:
            micrograph_queries = [self.query_micrograph_name_in_database(session, each_micrograph_file)
            for each_micrograph_file in micrograph_files]
        
            filt_micrograph_files = [micrograph_files[each_index] 
            for each_index, each_micrograph_query in enumerate(micrograph_queries) if each_micrograph_query is None]
        else:
            filt_micrograph_files = micrograph_files
        
        return filt_micrograph_files
        
        
    def setup_database_and_ctfinfo(self, micrograph_files):
        session = SpringDataBase().setup_sqlite_db(base)
        ctf_params = self.make_ctf_parameter_named_tuple()
        ctf_parameters = ctf_params._make([self.voltage, self.spherical_aberration, self.amplitude_contrast, 
                self.ori_pixelsize * self.binfactor])
        
        micrograph_files = self.filter_previously_determined_micrographs(session, micrograph_files)
        
        return session, ctf_parameters, micrograph_files
    

    def run_ctffind_and_ctftilt_for_given_micrographs(self, micrograph_files, outfiles):
        if self.spring_db_option:
            shutil.copy(self.spring_path, 'spring.db')
        session, ctf_parameters, micrograph_files = self.setup_database_and_ctfinfo(micrograph_files)
        
        self.log.plog(10)
        
        ctffind_params = []
        ctftilt_params = []
        for each_micrograph_index, each_micrograph_file in enumerate(micrograph_files):
            ctffind_parameters, ctftilt_parameters = self.run_ctffind_and_ctftilt_for_each_micrograph(micrograph_files, outfiles,
            each_micrograph_index, each_micrograph_file)
            
            session = self.enter_ctffind_values_in_database(session, each_micrograph_file, self.ori_pixelsize,
            ctf_parameters, ctffind_parameters)
            
            if ctftilt_parameters.defocus1 is not None:
                session = self.enter_ctftilt_values_in_database(session, each_micrograph_file, ctf_parameters.pixelsize,
                ctftilt_parameters)
                self.ctftilt_parameters = ctftilt_parameters
        
            ctffind_params.append([os.path.basename(each_micrograph_file)] + list(ctffind_parameters))
            ctftilt_params.append([os.path.basename(each_micrograph_file)] + list(ctftilt_parameters))
            session.commit()
        
        msg = tabulate(ctffind_params, ['micrograph'] + list(ctffind_parameters._fields))
        self.log.ilog('The following microscope parameters have been determined by CTFFIND:\n{0}'.format(msg))

        if self.ctftilt_option:
            msg = tabulate(ctftilt_params, ['micrograph'] + list(ctftilt_parameters._fields))
            self.log.ilog('The following microscope parameters have been refined by CTFTILT:\n{0}'.format(msg))


    def make_ctf_parameter_named_tuple(self):
        ctf_params = namedtuple('ctf_info', 'voltage spherical_aberration amplitude_contrast pixelsize')
    
        return ctf_params
    

    def enter_ctffind_and_ctftilt_values_in_database(self, micrograph_files, ctffind_parameters, ctftilt_parameters):
        session, ctf_parameters = self.setup_database_and_ctfinfo()
        
        for each_mic_id, each_micrograph_file in enumerate(micrograph_files):
            session = self.enter_ctffind_values_in_database(session, each_micrograph_file, self.ori_pixelsize,
            ctf_parameters, ctffind_parameters[each_mic_id])
            
            if ctftilt_parameters[each_mic_id].defocus1 is not None:
                session = self.enter_ctftilt_values_in_database(session, each_micrograph_file, ctf_parameters.pixelsize,
                ctftilt_parameters[each_mic_id])
        
        self.log.ilog('CTFFIND and CTFTILT parameters added to spring.db.')
        session.commit()
        session.close()
        

    def determine_ctf(self):
        if len(self.micrograph_files) < self.cpu_count:
            self.cpu_count = max(1, len(self.micrograph_files))
            self.feature_set.parameters['Number of CPUs']=self.cpu_count
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        self.tempdir = Temporary().mktmpdir(self.temppath)
        
        outfiles = Features().rename_series_of_output_files(self.micrograph_files, self.outfile)
        
        self.run_ctffind_and_ctftilt_for_given_micrographs(self.micrograph_files, outfiles)
        
        os.rmdir(self.tempdir)
        
        self.log.endlog(self.feature_set)
        

def main():
    # Option handling
    parset = MicCtfDeterminePar()
    mergeparset = OptHandler(parset)

    ######## Program
    scan = MicCtfDetermine(mergeparset)
    scan.determine_ctf()


if __name__ == '__main__':
    main()
