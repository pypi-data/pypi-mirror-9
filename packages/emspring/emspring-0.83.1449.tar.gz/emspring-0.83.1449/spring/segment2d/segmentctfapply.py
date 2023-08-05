# Author: Carsten Sachse 23-Aug-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to correct helical segments by determined CTF
"""
from EMAN2 import EMData
from filter import filt_ctf
from spring.csinfrastr.csdatabase import SpringDataBase, base, SegmentTable, CtfFindMicrographTable, \
    CtfTiltMicrographTable, CtfMicrographTable
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import OpenMpi
from spring.csinfrastr.csreadinput import OptHandler
from tabulate import tabulate
from utilities import generate_ctf
import numpy as np
import os
import shutil


class SegmentCtfApplyPar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'segmentctfapply'
        self.proginfo = __doc__
        self.code_files = [self.progname, self.progname + '_mpi']

        self.segmentctfapply_features = Features()
        self.feature_set = self.segmentctfapply_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()



    def define_parameters_and_their_properties(self):
        self.feature_set = self.segmentctfapply_features.set_inp_stack(self.feature_set)
        self.feature_set = self.segmentctfapply_features.set_out_stack(self.feature_set)
        
        self.feature_set = self.segmentctfapply_features.set_spring_path_segments(self.feature_set)
        
        self.feature_set = self.segmentctfapply_features.set_pixelsize(self.feature_set)
        self.feature_set = self.set_ctf_correct(self.feature_set)
        
        self.feature_set = self.segmentctfapply_features.set_mpi(self.feature_set)
        self.feature_set = self.segmentctfapply_features.set_ncpus(self.feature_set)
        self.feature_set = self.segmentctfapply_features.set_temppath(self.feature_set)


    def define_program_states(self):
        self.feature_set.program_states['get_ctf_values_from_database_and_compute_local_ctf_based_if_demanded']=\
        'Retrieve CTF values from database'
        self.feature_set.program_states['apply_ctf_to_segments']='Convolute each segment with CTF parameters'


    def add_ctf_correct_option_as_relative(self, feature_set, inp7):
        if 'CTF correct option' in feature_set.parameters:
            feature_set.relatives[inp7] = 'CTF correct option'
            
        return feature_set
    

    def set_ctffind_or_ctftilt_choice(self, feature_set):
        inp7 = 'CTFFIND or CTFTILT'
        feature_set.parameters[inp7] = str('ctftilt')
        feature_set.hints[inp7] = 'Choose whether \'ctffind\' or \'ctftilt\' values are used for CTF correction.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['ctffind', 'ctftilt'], 'QComboBox')
        feature_set = self.add_ctf_correct_option_as_relative(feature_set, inp7)
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    
    
    def set_ctfconvolve_or_ctfphase_flip_option(self, feature_set):
        inp7 = 'convolve or phase-flip'
        feature_set.parameters[inp7] = str('convolve')
        feature_set.hints[inp7] = 'Choose whether to \'convolve\' or \'phase-flip\' images with determined CTF.'
        feature_set.properties[inp7] = feature_set.choice_properties(2, ['convolve', 'phase-flip'], 'QComboBox')
        feature_set = self.add_ctf_correct_option_as_relative(feature_set, inp7)
        feature_set.level[inp7]='intermediate'

        return feature_set
    
    
    def set_astigmatism_option(self, feature_set):
        inp6 = 'Astigmatism correction'
        feature_set.parameters[inp6] = bool(True)
        feature_set.hints[inp6] = 'Option to correct for astigmatism in image otherwise average defocus is used.'
        feature_set = self.add_ctf_correct_option_as_relative(feature_set, inp6)
        feature_set.level[inp6]='expert'
        
        return feature_set
    
    
    def set_ctf_correct(self, feature_set):
        feature_set = self.set_ctffind_or_ctftilt_choice(feature_set)
        feature_set = self.set_ctfconvolve_or_ctfphase_flip_option(feature_set)
        feature_set = self.set_astigmatism_option(feature_set)
        
        return feature_set
    

class SegmentCtfApplyCtfFindCtfTilt(object):

    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters
            self.infile = p['Image input stack']
            self.outfile = p['Image output stack']
            
            self.spring_path = p['spring.db file']
            
            self.pixelsize = float(p['Pixel size in Angstrom'])
            self = self.define_ctf_correction_parameters(self, p)
            
            self.mpi_option = p['MPI option']
            self.cpu_count = p['Number of CPUs']
            self.temppath=p['Temporary directory']


    def define_ctf_correction_parameters(self, obj, p):
        obj.ctffind_or_ctftilt_choice = p['CTFFIND or CTFTILT']
        obj.convolve_or_phaseflip_choice = p['convolve or phase-flip']
        obj.astigmatism_option = p['Astigmatism correction']
        
        return obj
    

class SegmentCtfApplyConversion(SegmentCtfApplyCtfFindCtfTilt):
    def compute_local_defocus_from_ctftilt_parameters(self, coord_x, coord_y, df1, df2, center_x, center_y, pixelsize,
    taxis, tangle):
        """
        >>> from spring.segment2d.segmentctfapply import SegmentCtfApply
        >>> s = SegmentCtfApply()
        >>> s.compute_local_defocus_from_ctftilt_parameters(500, 500, 37735.65, 42714.57, 500, 500, 5.0, 135.10, -19.97)
        (37735.650000000001, 42714.57)
        >>> s.compute_local_defocus_from_ctftilt_parameters(1, 1000, 37735.65, 42714.57, 500, 500, 5.0, 135.10, -19.97)
        (37739.1747698892, 42718.094769889198)
        >>> s.compute_local_defocus_from_ctftilt_parameters(1, 1, 37735.65, 42714.57, 500, 500, 5.0, 135.10, -19.97)
        (36453.488353587752, 41432.408353587751)
        >>> s.compute_local_defocus_from_ctftilt_parameters(1000, 1, 37735.65, 42714.57, 500, 500, 5.0, 135.10, -19.97)
        (37734.694692328063, 42713.614692328061)
        >>> c_x = np.array([1000, 500])
        >>> c_y = np.array([1, 500])
        >>> s.compute_local_defocus_from_ctftilt_parameters(c_x, c_y, 37735.65, 42714.57, 500, 500, 5.0, 135.10, -19.97)
        (array([ 37734.69469233,  37735.65      ]), array([ 42713.61469233,  42714.57      ]))
        """
        """
        This is the CTFTILT convention (inverted tiltangle) from version 1.7 (May 2012)
        This is a typical CTFTILT output::
        
                      DFMID1      DFMID2      ANGAST     TLTAXIS      TANGLE          CC
                    37735.65    42714.57       78.74      135.10       -19.97     0.39982  Final Values
        
        
             EQUATION FOR CALCULATING DEFOCUS DFL1,DFL2 AT LOCATION NX,NY:
        
                  DFL1  = DFMID1 +DF
                  DFL2  = DFMID2 +DF
                  DF    = (N1*DX+N2*DY)*PSIZE*TAN(TANGLE)
                  DX    = CX-NX
                  DY    = CY-NY
                  CX    = CENTER_X =          500
                  CY    = CENTER_Y =          500
                  PSIZE = PIXEL SIZE [A] =       5.0000
                  N1,N2 = TILT AXIS NORMAL:
                     N1 =  SIN(TLTAXIS) =    0.705872
                     N2 = -COS(TLTAXIS) =    0.708339
        
        
            36453.64,    41432.56    <--(DFMID1,DFMID2)-->       37734.70,    42713.62
                   1,           1    <------(NX,NY)------>           1000,           1
                  +----------------------------------------------------------+
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                   37735.65,    42714.57                  |
                  |                        500,         500                  |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  |                                                          |
                  +----------------------------------------------------------+
                   1,        1000    <------(NX,NY)------>           1000,        1000
            37739.17,    42718.09    <--(DFMID1,DFMID2)-->       39020.23,    43999.15
        """
        n1 = np.sin(np.deg2rad(taxis))
        n2 = -np.cos(np.deg2rad(taxis))
        
        dx = center_x - coord_x
        dy = center_y - coord_y
        
        df = (n1*dx + n2*dy) * pixelsize * np.tan(np.deg2rad(tangle))
        df1_local = df1 + df
        df2_local = df2 + df
        
        return df1_local, df2_local
    
    
    def convert_mrc_defocus_to_sparx_defocus(self, defocus1, defocus2, astigmation_angle):
        """
        >>> from spring.micprgs.micctfdetermine import MicCtfDetermine
        >>> SegmentCtfApply().convert_mrc_defocus_to_sparx_defocus(18000.0, 22000.0, 20.0)
        (20000.0, 4000.0, 25.0)
        >>> SegmentCtfApply().convert_mrc_defocus_to_sparx_defocus(18000.0, 22000.0, 80.0)
        (20000.0, 4000.0, 145.0)
        >>> SegmentCtfApply().convert_mrc_defocus_to_sparx_defocus(22000.0, 18000.0, 80.0)
        (20000.0, 4000.0, 55.0)
        """
        df1_df2_diff = defocus1 - defocus2
        if df1_df2_diff < 0:
            astigmation_angle_sparx = 45.0 - astigmation_angle 
        elif df1_df2_diff >= 0:
            astigmation_angle_sparx = 135.0 - astigmation_angle 
        
        astigmatism_sparx = abs(df1_df2_diff)
        avg_defocus_sparx = sum([defocus1, defocus2]) / 2.0

        astigmation_angle_sparx = astigmation_angle_sparx % 180
        
        return avg_defocus_sparx, astigmatism_sparx, astigmation_angle_sparx
    
    
    def convert_mrc_defocus_to_spider_defocus(self, defocus1, defocus2, astigmation_angle):
        """
        >>> from spring.micprgs.micctfdetermine import MicCtfDetermine
        >>> SegmentCtfApply().convert_mrc_defocus_to_spider_defocus(18000.0, 22000.0, 20.0)
        (20000.0, 4000.0, 155.0)
        >>> SegmentCtfApply().convert_mrc_defocus_to_spider_defocus(18000.0, 22000.0, 80.0)
        (20000.0, 4000.0, 35.0)
        >>> SegmentCtfApply().convert_mrc_defocus_to_spider_defocus(22000.0, 18000.0, 80.0)
        (20000.0, 4000.0, 125.0)
        """
        df1_df2_diff = defocus1 - defocus2
        if df1_df2_diff < 0:
            astigmation_angle_sparx = astigmation_angle + 135
        elif df1_df2_diff >= 0:
            astigmation_angle_sparx = astigmation_angle + 45
        
        astigmatism_sparx = abs(df1_df2_diff)
        avg_defocus_sparx = sum([defocus1, defocus2]) / 2.0

        astigmation_angle_sparx = astigmation_angle_sparx % 180
        
        return avg_defocus_sparx, astigmatism_sparx, astigmation_angle_sparx
    
    
class SegmentCtfApplyDatabase(SegmentCtfApplyConversion):

    def raise_error_if_not_found(self, spring_path, matched_mic_find):
        if matched_mic_find is None:
            find_error_msg = 'Specified {0} file does not contain micrograph information from '.format(spring_path) + \
            'CTFFIND. Please re-run MicCtfDetermine.'
            raise ValueError(find_error_msg)

    def get_micrograph_from_database_by_micid(self, session, mic_id, spring_path):
        matched_mic_find = session.query(CtfFindMicrographTable).get(mic_id)
        self.raise_error_if_not_found(spring_path, matched_mic_find)
        
        return matched_mic_find
    
    def get_micrograph_from_database_by_micname(self, session, micrograph_file, spring_path):
        matched_mic_find = session.query(CtfFindMicrographTable).\
        filter(CtfFindMicrographTable.micrograph_name == os.path.basename(micrograph_file)).first()
        
        self.raise_error_if_not_found(spring_path, matched_mic_find)
        
        return matched_mic_find
    

    def get_ctfparameters_from_database(self, ctffind_or_ctftilt_choice, astigmatism_option, pixelsize, session,
    each_segment, matched_mic_find, spring_path):
        if ctffind_or_ctftilt_choice in ['ctftilt']:
            matched_mic_tilt = session.query(CtfTiltMicrographTable).get(matched_mic_find.id)
            self.raise_error_if_not_found(spring_path, matched_mic_tilt)
            
            local_df1, local_df2 = self.compute_local_defocus_from_ctftilt_parameters(each_segment.x_coordinate_A /
            matched_mic_find.pixelsize, each_segment.y_coordinate_A / matched_mic_find.pixelsize,
            matched_mic_tilt.defocus1, matched_mic_tilt.defocus2, matched_mic_tilt.center_x, matched_mic_tilt.center_y,
            matched_mic_find.pixelsize, matched_mic_tilt.tilt_axis, matched_mic_tilt.tilt_angle)
            
            defocus1 = local_df1
            defocus2 = local_df2
            astigmation_angle = matched_mic_tilt.astigmation_angle
        elif ctffind_or_ctftilt_choice in ['ctffind']:
            defocus1 = matched_mic_find.defocus1
            defocus2 = matched_mic_find.defocus2
            astigmation_angle = matched_mic_find.astigmation_angle
            
        avg_defocus, astigmatism, astig_angle = self.convert_mrc_defocus_to_sparx_defocus(defocus1, defocus2,
        astigmation_angle)
        
        matched_mic = session.query(CtfMicrographTable).get(matched_mic_find.id)
        if not astigmatism_option:
            astigmatism = 0
            astig_angle = 0
        ctf_params = [avg_defocus * 1e-4, matched_mic.spherical_aberration, matched_mic.voltage, pixelsize, 0,
        matched_mic.amplitude_contrast, astigmatism * 1e-4, astig_angle]
        
        return ctf_params, avg_defocus, astigmatism, astig_angle


    def update_ctfparameters_in_database(self, ctffind_or_ctftilt_choice, convolve_or_phaseflip_choice,
    astigmatism_option, session, each_segment, avg_defocus, astigmatism, astig_angle):
        each_segment.avg_defocus = avg_defocus
        each_segment.astigmatism = astigmatism
        each_segment.astigmation_angle = astig_angle
        if ctffind_or_ctftilt_choice in ['ctftilt']:
            each_segment.ctffind_applied = False
            each_segment.ctftilt_applied = True
        elif ctffind_or_ctftilt_choice in ['ctffind']:
            each_segment.ctffind_applied = True
            each_segment.ctftilt_applied = False
            
        if convolve_or_phaseflip_choice in ['convolve']:
            each_segment.ctf_convolved = True
            each_segment.ctf_phase_flipped = False
        elif convolve_or_phaseflip_choice in ['phase-flip']:
            each_segment.ctf_convolved = False
            each_segment.ctf_phase_flipped = True
        
        if astigmatism_option:
            each_segment.ctf_astigmatism_applied = True
        else:
            each_segment.ctf_astigmatism_applied = False
        
        return session, each_segment
    

    def get_ctf_values_from_database_and_compute_local_ctf_based_if_demanded(self, ctffind_or_ctftilt_choice,
    convolve_or_phaseflip_choice, astigmatism_option, pixelsize, spring_path):
        self.log.fcttolog()
        self.log.plog(10)
        session = SpringDataBase().setup_sqlite_db(base)
        
        matched_segments = session.query(SegmentTable).order_by(SegmentTable.stack_id).all()
        ctf_parameters = []
        for each_segment in matched_segments:
            matched_mic_find = self.get_micrograph_from_database_by_micid(session, each_segment.mic_id, spring_path)
            
            ctf_params, avg_defocus, astigmatism, astig_angle = \
            self.get_ctfparameters_from_database(ctffind_or_ctftilt_choice, astigmatism_option, pixelsize, session,
            each_segment, matched_mic_find, spring_path)
            
            ctf_parameters.append(ctf_params)
            
            session, each_segment = self.update_ctfparameters_in_database(ctffind_or_ctftilt_choice,
            convolve_or_phaseflip_choice, astigmatism_option, session, each_segment, avg_defocus, astigmatism,
            astig_angle)
            
            session.merge(each_segment)
        
        session.commit()
        
        return ctf_parameters
    
    
class SegmentCtfApply(SegmentCtfApplyDatabase):

    def filter_image_by_ctf_convolve_or_phaseflip(self, convolve_or_phaseflip_choice, segment, each_segment_ctf_p):
        local_ctf = generate_ctf(each_segment_ctf_p)
        if convolve_or_phaseflip_choice in ['convolve']:
            segment = filt_ctf(segment, local_ctf)
        elif convolve_or_phaseflip_choice in ['phase-flip']:
            segment = filt_ctf(segment, local_ctf, binary=True)
            
        return segment
    

    def apply_ctf_to_segments(self, segment_ids, ctf_parameters, convolve_or_phaseflip_choice, infile_stack,
    outfile_stack):
        
        self.log.fcttolog()
        self.log.plog(20)
        segment = EMData()
        if ctf_parameters != []:
            log_info = [ctf_parameters[0][1:5]]
            msg = tabulate(log_info, ['Cs(mm)', 'voltage(kV)', 'pixelsize', 'bfactor', 'amp_contrast'])
            self.log.ilog(msg)

        log_info = []
        for each_local_seg_id, each_seg_id in enumerate(segment_ids):
            each_segment_ctf_p = ctf_parameters[each_local_seg_id]
            segment.read_image(infile_stack, each_seg_id)
            
            segment = self.filter_image_by_ctf_convolve_or_phaseflip(convolve_or_phaseflip_choice, segment,
            each_segment_ctf_p)
            
            segment.write_image(outfile_stack, each_local_seg_id)
            
            log_info += [[each_seg_id, each_local_seg_id, each_segment_ctf_p[0], each_segment_ctf_p[6],
            each_segment_ctf_p[7]]]
    
        if ctf_parameters != []:
            msg = tabulate(log_info, ['segment_id', 'local_id', 'avg_defocus(microm)', 'astigmatism', 'astig_angle'])
            self.log.ilog(log_info)
            self.log.plog(90)
        
        
    def apply_ctf_to_segment_stack(self):
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        
        shutil.copy(self.spring_path, 'spring.db')
        
        ctf_parameters = \
        self.get_ctf_values_from_database_and_compute_local_ctf_based_if_demanded(self.ctffind_or_ctftilt_choice,
        self.convolve_or_phaseflip_choice, self.astigmatism_option, self.pixelsize, self.spring_path)
        
        segment_ids = list(range(len(ctf_parameters)))
        
        self.apply_ctf_to_segments(segment_ids, ctf_parameters, self.convolve_or_phaseflip_choice, self.infile,
        self.outfile)
        
        self.log.endlog(self.feature_set)

            
def main():
    # Option handling
    parset = SegmentCtfApplyPar()
    mergeparset = OptHandler(parset)

    ######## Program
    stack = SegmentCtfApply(mergeparset)
    stack.apply_ctf_to_segment_stack()

if __name__ == '__main__':
    main()
