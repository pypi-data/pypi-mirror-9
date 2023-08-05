# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to extract overlapping segments from micrographs 
"""
import os
import shutil
from spring.csinfrastr.csdatabase import SpringDataBase, base, CtfMicrographTable, HelixTable, SegmentTable, refine_base, \
    RefinementCycleSegmentTable, RefinementCycleHelixTable
from spring.csinfrastr.csfeatures import FeaturesSupport, Features
from spring.csinfrastr.cslogger import Logger
from spring.micprgs.scansplit import Micrograph
from spring.segment2d.segmentctfapply import SegmentCtfApplyPar, SegmentCtfApply
from spring.segment2d.segmentselect import SegmentSelect

from tabulate import tabulate

import numpy as np


class SegmentPar:
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'segment'
        self.proginfo = __doc__
        self.code_files = ['segment_prep', 'segment_int', 'segmentctfapply', self.progname, self.progname + '_mpi']

        self.segment_features = Features()
        self.feature_set = self.segment_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    

    def set_segment_or_window_features(self):
        self.feature_set = self.set_segment_coordinate_files(self.feature_set)
        self.feature_set = self.set_segment_size(self.feature_set)
        self.feature_set = self.segment_features.set_helix_width(self.feature_set)
        self.feature_set = self.set_segmentation_step(self.feature_set)
        self.feature_set = self.set_perturb_step_option(self.feature_set)


    def set_center_and_remove_ends_for_helices(self):
        self.feature_set = self.set_remove_helix_ends_option(self.feature_set)

    def set_helix_or_particle_centering(self):
        self.set_center_and_remove_ends_for_helices()
        self.feature_set = self.set_rotation_option(self.feature_set)
        self.feature_set = self.set_straightening_option(self.feature_set)

    def define_parameters_and_their_properties(self):
        self.feature_set = self.segment_features.set_inp_multiple_micrographs(self.feature_set)
        self.feature_set = self.segment_features.set_out_stack(self.feature_set)
    
        self.feature_set = self.segment_features.set_spring_db_option(self.feature_set)
        self.feature_set = self.segment_features.set_spring_path(self.feature_set)
        self.set_segment_or_window_features()
        self.feature_set = self.segment_features.set_pixelsize(self.feature_set)
        self.feature_set = self.set_ctf_correct(self.feature_set)
        self.feature_set = self.segment_features.set_binning_option(self.feature_set, image='segments')
        self.feature_set = self.segment_features.set_binning_factor(self.feature_set, image='segments')
        self.feature_set = self.set_invert_option(self.feature_set)
        self.feature_set = self.set_normalization_option(self.feature_set)
        self.feature_set = self.set_rows_normalization_option(self.feature_set)
        
        self.feature_set = self.segment_features.set_micrograph_and_helix_selection_criteria(self.feature_set)
        self.feature_set = self.segment_features.set_curvature_selection_criteria(self.feature_set)
        self.feature_set = self.segment_features.set_defocus_and_astigmatism_selection_criteria(self.feature_set)
        self.set_helix_or_particle_centering()

        self.feature_set = self.set_frame_processing_option(self.feature_set)
        self.feature_set = self.set_frame_first_and_last_frame(self.feature_set)
        self.feature_set = self.set_ref_db_frame_processing(self.feature_set)

        self.feature_set = self.segment_features.set_mpi(self.feature_set)
        self.feature_set = self.segment_features.set_ncpus(self.feature_set)
        self.feature_set = self.segment_features.set_temppath(self.feature_set)

        
    def define_program_states(self):
        self.feature_set.program_states['assign_reorganize']='Initialize micrographs and segments to convert them ' + \
        'into Spring\'s file structure'
        self.feature_set.program_states['single_out']='Single out individual helices from micrograph'
        self.feature_set.program_states['readmic']='Loading new micrograph'
        self.feature_set.program_states['center_segments']='Segments are centerd with respect to helix axis'
        self.feature_set.program_states['window_segment']='Windowing segments from micrograph'

    def set_segment_coordinate_files(self, feature_set):
        inp3 = 'Segment coordinates'
        feature_set.parameters[inp3] = 'scan034_boxes.txt'
        feature_set.properties[inp3] = feature_set.file_properties(1000, ['box', 'txt', 'star', 'db'], 'getFiles')
        feature_set.hints[inp3] = 'Input: file with identical name of corresponding micrograph (accepted file ' + \
        'formats EMAN\'s Helixboxer/Boxer, EMAN2\'s E2helixboxer and Bsoft filament parameters coordinates: {0}{1}). '.\
        format(os.extsep, FeaturesSupport().add_file_extensions_in_comma_separated_string(feature_set, inp3)) + \
        'When using the frame processing please specify a previously generated spring.db to provide the coordinates. ' + \
        'Make sure that helix paths are continuous. A helix path can follow a C- or S-path but must NOT form a U-turn.'\
        
        feature_set.level[inp3]='beginner'

        return feature_set


    def set_segment_size(self, feature_set):
        inp4 = 'Segment size in Angstrom'
        feature_set.parameters[inp4] = int(700)
        feature_set.hints[inp4] = 'Molecular mass (i.e. signal) increases with segment size and helix defects ' + \
        'become more pronounced. Final image size = segement size + stepsize.'
        feature_set.properties[inp4] = feature_set.Range(100, 1500, 50)
        feature_set.level[inp4]='beginner'
        
        return feature_set


    def set_segmentation_step(self, feature_set):
        inp5 = 'Step size of segmentation in Angstrom'
        feature_set.parameters[inp5] = int(70)
        feature_set.hints[inp5] = 'Overlapping segments are related views according to helical symmetry, i.e. step ' + \
        'size should be a multiple of helical rise (stepsize of 0 corresponds to one central box per helix).'
        feature_set.properties[inp5] = feature_set.Range(0, 2000, 1)
        feature_set.level[inp5]='beginner'
        
        return feature_set


    def set_perturb_step_option(self, feature_set):
        inp6 = 'Perturb step option'
        feature_set.parameters[inp6] = bool(False)
        feature_set.hints[inp6] = 'Perturb the segmentation step between the windowed segments. Takes specified ' + \
        'step size and applies a random shift along the helix between +/- stepsize / 2 . This is ' + \
        'useful to avoid artifacts in the Fourier transforms of class averages.'
        feature_set.level[inp6]='intermediate'
        
        return feature_set
    
    
    def set_invert_option(self, feature_set):
        inp6 = 'Invert option'
        feature_set.parameters[inp6] = bool(True)
        feature_set.hints[inp6] = 'Inversion of image densities for cryo data, i.e. protein becomes white.'
        feature_set.level[inp6]='beginner'
        
        return feature_set


    def set_center_option(self, feature_set):
        inp7 = 'Center option'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Segments are centered with respect to their helix axis. Use this option with ' + \
        'caution as it will only work for rigid and dense specimens, e.g. tubulur crystals.'
        feature_set.level[inp7]='intermediate'

        return feature_set


    def set_remove_helix_ends_option(self, feature_set):
        inp7 = 'Remove helix ends option'
        feature_set.parameters[inp7] = bool(False)
        feature_set.hints[inp7] = 'Ends of helices are removed by half the segment size. This depends on how you ' + \
        'boxed the helices.'
        feature_set.level[inp7]='intermediate'

        return feature_set


    def set_normalization_option(self, feature_set):
        inp7 = 'Normalization option'
        feature_set.parameters[inp7] = bool(True)
        feature_set.hints[inp7] = 'Segments are normalized with a mean of 0 and standard deviation of 1.'
        feature_set.level[inp7]='intermediate'
        
        return feature_set


    def set_rotation_option(self, feature_set):
        inp8 = 'Rotation option'
        feature_set.parameters[inp8] = bool(True)
        feature_set.hints[inp8] = 'Segments are rotated with helix axis perpendicular to image rows.' 
        feature_set.level[inp8]='intermediate'
        
        return feature_set
    
    
    def set_straightening_option(self, feature_set):
        inp8 = 'Unbending option'
        feature_set.parameters[inp8] = bool(False)
        feature_set.hints[inp8] = 'Segments are computationally unbent or straightened according to coordinates of ' + \
        'helix axis in addition to rotation.'
        if 'Rotation option' in feature_set.parameters:
            feature_set.relatives[inp8]='Rotation option'
        feature_set.level[inp8]='experimental'
        
        return feature_set
    
    
    def set_ctf_correct_option(self, feature_set):
        inp8 = 'CTF correct option'
        feature_set.parameters[inp8] = bool(True)
        feature_set.hints[inp8] = 'Segments are CTF corrected with determined CTF parameters.'
        feature_set.level[inp8]='intermediate'
        
        return feature_set
    

    def set_rows_normalization_option(self, feature_set):
        inp13 = 'Row normalization option'
        feature_set.parameters[inp13] = bool(False)
        feature_set.hints[inp13] = 'Option to normalize micrographs row by row to eliminate artifacts as they occur '+\
        'in Falcon II images or frames if they are not correctly linearized.'
        feature_set.level[inp13]='intermediate'
        
        return feature_set
    
    
    def set_ctf_correct(self, feature_set):
        feature_set = self.set_ctf_correct_option(feature_set)
        feature_set = SegmentCtfApplyPar().set_ctffind_or_ctftilt_choice(feature_set)
        feature_set = SegmentCtfApplyPar().set_ctfconvolve_or_ctfphase_flip_option(feature_set)
        feature_set = SegmentCtfApplyPar().set_astigmatism_option(feature_set)
        
        return feature_set
        
        
    def set_frame_processing_option(self, feature_set):
        inp5 = 'Frame processing option'
        feature_set.parameters[inp5] = bool(False)
        feature_set.hints[inp5] = 'This option will prepare of stack containing frame helix segments from direct ' + \
        'electron detectors and is intended for subsequent helix-based movie processing using \'segmentrefine3d\'. ' + \
        'Prior to this option run \'segmentrefine3d\' using the combined average of all frames. For input of the \'Frame ' + \
        'processing option\' using \'segment\' please provide: 1. \'Micrographs\' as an mrc-stack file ' + \
        '2. \'Segment coordinates\' - use previous spring.db as input instead of pure coordinate files. ' + \
        '3. \'spring.db file\' previous spring.db (same file as 2.) and ' + \
        '4. \'Refinement.db to process\' from your last \'segmentrefine3d\' cycle. This option will generate the ' + \
        'following output: 1. Stack of frame helix segments, ' + \
        '2. spring_frames.db with copies of all segment entries from the previous spring.db and ' + \
        '3. refinement_frames.db with copies of previous orientation parameters. With those output files of the ' + \
        '\'segment\' run you can launch \'segmentrefine3d\' with \'Frame motion correction\''
        
        feature_set.level[inp5]='expert'
         
        return feature_set
     
     
    def set_frame_first_and_last_frame(self, feature_set):
        inp5 = 'First and last frame'
        feature_set.parameters[inp5] = ((1, 6))
        feature_set.hints[inp5] = 'Choose first and last frame to be processed from direct detector movies.'
        feature_set.properties[inp5] = feature_set.Range(0, 400, 1)
        feature_set.relatives[inp5] = ('Frame processing option', 'Frame processing option')
        feature_set.level[inp5]='expert'
         
        return feature_set
    
        
    def set_ref_db_frame_processing(self, feature_set):
        inp5 = 'Refinement.db to process'
        feature_set.parameters[inp5] = 'refinement.db'
        feature_set.properties[inp5] = feature_set.file_properties(1, ['db'], 'getFiles')
        feature_set.hints[inp5] = 'Input: refinement.db from previous combined average frame run of segmentrefine3d. '
        feature_set.relatives[inp5] = 'Frame processing option'
        feature_set.level[inp5]='expert'
         
        return feature_set


class SegmentAssign(object):

    def create_link(self, micfile, overlapdir):
        """
        Function to create symbolic link in new directory

        #. Input: micfile (file for wich symbolic link is to be created), overlapdir = new directory for\
            symbolic link location
        #. Output: symbolic link absolute path 
        #. Usage: micabsfile = create_link(micfile, ovelapdir)
        """

        micabsfile = os.path.join(overlapdir, os.path.basename(micfile))
        try:
            os.symlink(micfile, micabsfile)
        except OSError:
            os.remove(micabsfile)
            os.symlink(micfile, micabsfile)

        self.log.ilog('Symbolic link {0} created'.format(micabsfile))

        return micabsfile
    
    
    def reorganize_micrographs_and_coordinate_files_into_separate_directories(self, pair):
        """
        * Function to reorganize micrographs and coordinate files into \
        separate directories micrograph and corresponding segment file into \
        separate subdirectories using symbolic links
        
        #. Input: list of 3-tuples (micrograph file, segment file, overlapping letters)
        #. Output: None
        #. Usage: reorganize_micrographs_and_coordinate_files_into_separate_directories(pair)
        """

        for micfile, segfile, overlap in pair:
            overlapdir = overlap
            try:
                os.mkdir(overlapdir)
                self.log.ilog('Directory {0} created'.format(overlapdir))
            except OSError:
                self.log.ilog('Directory {0} exists'.format(overlapdir))
                pass

            self.create_link(micfile, overlapdir)
            self.create_link(segfile, overlapdir)
            
        return micfile, segfile, overlapdir
        
        
    def assign_micrograph_segment_pairs(self, micrograph_files, coordinate_files):
        """
        * Function to assign pairs of micrographs and segment files based on \
        their common filenames

        #. Input: micrograph_files = list of input micrographs, \
        coordinate_files = list of segment files
        #. Ouput: list of tuples consisting micrograph, corresponding segment \
        file and their common base filename
        #. Usage: assign_micrograph_segment_pairs(micrograph_files, coordinate_files)

        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> mics = ['A.tif', 'B.tif', 'C.tif', 'Y.tif']
        >>> boxes = ['A.box', 'B.box', 'C.box', 'Z.box']
        >>> s.assign_micrograph_segment_pairs(mics, boxes)
        [('A.tif', 'A.box', 'A'), ('B.tif', 'B.box', 'B'), ('C.tif', 'C.box', 'C')]
        >>> boxes = ['A_boxes.txt', 'B_boxes.txt', 'C_boxes.txt', 'Z_boxes.txt']
        >>> s.assign_micrograph_segment_pairs(mics, boxes)
        [('A.tif', 'A_boxes.txt', 'A'), ('B.tif', 'B_boxes.txt', 'B'), ('C.tif', 'C_boxes.txt', 'C')]
        """

        if coordinate_files[0].endswith('_boxes.txt'):
            coord_files = dict([(os.path.splitext(os.path.basename(each_coord_file))[0][0:-len('_boxes')], each_coord_file) 
                            for each_coord_file in coordinate_files])
        else:
            coord_files = dict([(os.path.splitext(os.path.basename(each_coord_file))[0], each_coord_file) 
                            for each_coord_file in coordinate_files])

        pair = []
        for micrograph_file in micrograph_files:
            micrograph_base = os.path.splitext(os.path.basename(micrograph_file))[0]
            if coord_files.has_key(micrograph_base):
                common_coord = coord_files[micrograph_base]
                pair.append((micrograph_file, common_coord, micrograph_base))
            else:
                self.log.ilog('Micrograph {0} is ignored could not be matched with a segment file'.\
                              format(micrograph_file))

        log_info = []
        for each_micrograph, each_coord_file, each_overlap in pair:
            log_info += [[os.path.basename(each_micrograph), os.path.basename(each_coord_file), each_overlap]]

        msg = tabulate(log_info, ['micrograph', 'coordinate_file', 'overlapping_string'])
        self.log.ilog('The following micrograph/coordinate pairs have been assigned:\n{0}'.format(msg))

        return pair
    

    def remove_helices_segments_from_tables(self, session, segments, combined_included_segments, segment_table,
    helix_table, red_helix_ids):
        helices = session.query(helix_table).order_by(helix_table.id).all()
 
        SpringDataBase().remove_all_previous_entries(session, helix_table)
        session.commit()
 
        red_helix_id = 0
        hel_columns = SpringDataBase().get_columns_from_table(helix_table)
        helices_to_update = np.zeros(len(helices))
        for each_helix in helices:
            if each_helix.id in list(set(red_helix_ids)):
                data = SpringDataBase().get_data_from_entry(hel_columns, each_helix)
                red_helix_id += 1
                data['id'] = red_helix_id
                session.add(helix_table(**data))
                helices_to_update[each_helix.id - 1] = red_helix_id

        SpringDataBase().remove_all_previous_entries(session, segment_table)
        session.commit()

        red_stack_id = 0
        seg_columns = SpringDataBase().get_columns_from_table(segment_table)
        for each_segment in segments:
            if each_segment.stack_id in combined_included_segments:
                data = SpringDataBase().get_data_from_entry(seg_columns, each_segment)
                data['stack_id'] = red_stack_id
                if data.has_key('helix_id'):
                    data['helix_id'] = helices_to_update[red_helix_ids[red_stack_id] - 1]
                red_stack_id += 1
                data['id'] = red_stack_id
                session.add(segment_table(**data))
        
        session.commit()


    def perform_helix_based_segment_selection_incl_segment_helix_removal_from_springdb(self, db_name):
        if self.straightness_selection or self.mics_selection or self.helices_selection or self.defocus_selection \
        or self.astigmatism_selection:
            shutil.copy(db_name, 'spring.db')
            db_name = 'spring.db'
            session = SpringDataBase().setup_sqlite_db(base, db_name)
            segments = session.query(SegmentTable).order_by(SegmentTable.stack_id).all()

            self.curvature_range, self.ccc_layer_range = SegmentSelect().convert_curvature_ccc_layer_range(db_name,
            self.straightness_selection, self.curvature_range_perc)

            included_segments_mics, included_segments_helices, included_segments_curve, included_segments_defocus, \
            included_segments_astigmatism, excluded_mics_count, excluded_helix_count, excluded_curvature_count, \
            excluded_defocus_count, excluded_astig_count = \
            SegmentSelect().filter_by_properties_that_keep_helices_together(self, session, segments)

            combined_included_segments = list(set(range(len(segments))).intersection(included_segments_mics, 
                    included_segments_helices, included_segments_curve, included_segments_defocus, 
                    included_segments_astigmatism))

            red_helix_ids = [each_segment.helix_id for each_segment in segments \
                             if each_segment.stack_id in combined_included_segments]

            self.remove_helices_segments_from_tables(session, segments, combined_included_segments, SegmentTable,
            HelixTable, red_helix_ids)
            
            if self.frame_option:
                ref_db = 'refinement.db'
                shutil.copy(self.ref_db, ref_db)
                self.ref_db = ref_db
                ref_session = SpringDataBase().setup_sqlite_db(refine_base, ref_db)
                
                ref_segments = ref_session.query(RefinementCycleSegmentTable).\
                                        order_by(RefinementCycleSegmentTable.stack_id).all()
                
                self.remove_helices_segments_from_tables(ref_session, ref_segments, combined_included_segments,
                RefinementCycleSegmentTable, RefinementCycleHelixTable, red_helix_ids)
            
        return db_name


    def assign_reorganize(self, micrograph_files, coordinate_files):
        """
        * Function to match micrographs and corresponding segment file 

        #. Input: list of input micrographs, list of segment files
        #. Output: assigned pair of micrograph and segments
        #. Usage: assign_reorganize(micrograph_files, coordinate_files)
        """
        self.log.fcttolog()

        if coordinate_files[0].endswith('db'):
            db_name = coordinate_files[0]
            db_name = self.perform_helix_based_segment_selection_incl_segment_helix_removal_from_springdb(db_name)
                
            session = SpringDataBase().setup_sqlite_db(base, db_name)

            helices = session.query(HelixTable).order_by(HelixTable.id).all()
        
            mic_ids = []
            [mic_ids.append(each_helix.mic_id) for each_helix in helices if each_helix.mic_id not in mic_ids]

            mics = [session.query(CtfMicrographTable).get(each_mic_id) for each_mic_id in mic_ids]
            mic_ending = list(set([os.path.splitext(each_mic)[-1] for each_mic in micrograph_files]))
            if len(mic_ending) == 1 and mic_ending[0].endswith('mrcs'):
                pair = [(str(os.path.join(each_mic.dirname, 
                        os.path.splitext(os.path.basename(each_mic.micrograph_name))[0] + os.extsep + 'mrcs')), 
                        db_name, os.path.splitext(os.path.basename(each_mic.micrograph_name))[0]) 
                        for each_mic in mics]
            else:
                pair = [(str(os.path.join(each_mic.dirname, each_mic.micrograph_name)), db_name, 
                         os.path.splitext(os.path.basename(each_mic.micrograph_name))[0]) 
                        for each_mic in mics]
        else:
            pair = self.assign_micrograph_segment_pairs(micrograph_files, coordinate_files)

        if pair == []:
            errstring = 'No micrographs could be matched with segment files. Nothing to be done. Abort {0}'.\
            format(os.path.basename(__file__).split(os.extsep)[0])
            self.log.errlog(errstring)
            raise IOError(errstring)

        self.reorganize_micrographs_and_coordinate_files_into_separate_directories(pair)
        
        return pair
    

class SegmentPreparation(Micrograph, SegmentAssign):
    """
    * Class that holds functions for extracting segments from micrographs

    * __init__ Function to interpret multi-input parameters

    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.infile = p['Micrographs']
            self.outfile = p['Image output stack']
            self.spring_db_option = p['Spring database option']
            self.spring_path = p['spring.db file']
            self.spring_path = os.path.abspath(self.spring_path)
            
            self.pixelsize = float(p['Pixel size in Angstrom'])
            self.define_segment_or_window_parameters(p)
            self.define_ctf_parameters(p)
            
            self.invertoption=p['Invert option']
            self.centeroption=False
            self.normoption=p['Normalization option']
            self.row_normalization=p['Row normalization option']
            self.binoption=p['Binning option']
            self.binfactor=p['Binning factor']
            if self.binfactor == 1 and self.binoption is True:
                self.binoption = False

            self = SegmentSelect().define_mics_and_helices_selection(self, p)
            self = SegmentSelect().define_straightness_selection(self, p)
            self = SegmentSelect().define_defocus_and_astigmatism_selection(self, p)

            self.segsizepix = self.determine_boxsize_closest_to_fast_values(self.window_size / self.pixelsize, ten=True)
            if self.ctfcorrect_option:
                ctf_window_size = 1.3 * self.window_size / self.pixelsize
                self.window_sizepix = self.determine_boxsize_closest_to_fast_values(ctf_window_size)
            else:
                self.window_sizepix = self.segsizepix

            self.frame_option = p['Frame processing option']
            self.frame_range = p['First and last frame']
            self.spring_db_frames = 'spring_{0}-{1}frames.db'.format(self.frame_range[0], self.frame_range[-1])
            self.ref_db = p['Refinement.db to process']
            self.ref_db_frames = 'refinement_{0}-{1}frames.db'.format(self.frame_range[0], self.frame_range[-1])
            
            self.micrograph_files = Features().convert_list_of_files_from_entry_string(self.infile)
            self.coordinate_files = Features().convert_list_of_files_from_entry_string(self.coordinate_files_entry)
            

    def define_segment_or_window_parameters(self, p):
        self.coordinate_files_entry = p['Segment coordinates']
        self.segment_size = p['Segment size in Angstrom']
        
        self.remove_ends=p['Remove helix ends option']
        if Features().convert_list_of_files_from_entry_string(self.coordinate_files_entry)[0].endswith('db'):
            self.remove_ends = False
        
        self.stepsize = p['Step size of segmentation in Angstrom']
        if self.stepsize == 0:
            self.remove_ends = False
            
        self.perturb_step = p['Perturb step option']
        self.window_size = self.segment_size + 1.2 * self.stepsize
        self.helixwidth = p['Estimated helix width in Angstrom']
        self.helixwidthpix = int(round(self.helixwidth/self.pixelsize))
        
        self.rotoption=p['Rotation option']
        self.unbending=p['Unbending option']

        self.averaging_option=False
        self.averaging_distance=10 * self.stepsize#p['Local averaging distance in Angstrom']
        
        self.mpi_option = p['MPI option']
        self.cpu_count = p['Number of CPUs']
        if self.cpu_count == 1:
            self.mpi_option = False
        self.temppath=p['Temporary directory']
            

    def define_ctf_parameters(self, p):
        self.ctfcorrect_option = p['CTF correct option']
        self = SegmentCtfApply().define_ctf_correction_parameters(self, p)


    def get_strip_frame(self, first_frame):
        if first_frame == 0:
            first_frame_strip = ''
        else:
            first_frame_strip = '{0}'.format(first_frame)
        
        return first_frame_strip
        

    def get_message_for_frame_missing(self, first_frame, first_str, mics):
        msg = 'Specified {0} frame {1} cannot be found in pool of provided micrographs ({2}). '.\
        format(first_str, first_frame, ', '.join(mics)) + \
        'Double-check existance of frame or correct {0} frame entry.\n'.format(first_str)

        return msg


    def check_whether_provided_frame_number_matches_provided_micrographs(self, micrographs, input_mics, frame_range):
        """
        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> mics = ['test.hdf', 'tost.hdf']
        >>> input_mics = ['test_{0:03}.hdf'.format(each) for each in list(range(5))]
        >>> s.check_whether_provided_frame_number_matches_provided_micrographs(mics, input_mics, (0, 4))
        [('test.hdf', ['test_000.hdf', 'test_001.hdf', 'test_002.hdf', 'test_003.hdf', 'test_004.hdf'])]
        >>> s.check_whether_provided_frame_number_matches_provided_micrographs(mics, input_mics, (2, 4))
        [('test.hdf', ['test_002.hdf', 'test_003.hdf', 'test_004.hdf'])]
        >>> s.check_whether_provided_frame_number_matches_provided_micrographs(mics, input_mics, (2, 7)) #doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        ValueError: Specified last frame 7 cannot be found in pool of provided 
        micrographs (test_000.hdf, test_001.hdf, test_002.hdf, test_003.hdf, 
        test_004.hdf). Double-check existance of frame or correct last frame entry.
        """
        first_frame, last_frame = frame_range
        first_frame_strip = self.get_strip_frame(first_frame)
        last_frame_strip = self.get_strip_frame(last_frame)

        assigned_inp_mics = []
        expected_pattern = set(['{0}'.format(each_id) if each_id != 0 else '' 
                             for each_id in list(range(first_frame, last_frame + 1))])
            
        for each_mic in micrographs:
            micrograph_base = os.path.splitext(os.path.basename(each_mic))[0]

            common_inp = [os.path.basename(each_inp) for each_inp in input_mics if micrograph_base in each_inp]
            common_full_path_inp = [each_inp for each_inp in input_mics if micrograph_base in each_inp]

            mics = [each_full_inp for each_inp, each_full_inp in zip(common_inp, common_full_path_inp) 
                    if os.path.splitext(each_inp)[0].startswith(micrograph_base)]

            diff = [os.path.splitext(each_inp)[0][len(micrograph_base):] for each_inp in common_inp 
                    if os.path.splitext(each_inp)[0].startswith(micrograph_base)]

            diff_strip = [each_diff.strip('_').lstrip('0') for each_diff in diff]
            
            assigned_mics = dict(zip(diff_strip, mics))
            if mics != []:
                msg = ''
                if not assigned_mics.has_key(first_frame_strip):
                    msg += self.get_message_for_frame_missing(first_frame, 'first', mics)
                elif not assigned_mics.has_key(last_frame_strip):
                    msg += self.get_message_for_frame_missing(last_frame, 'last', mics)
                if not assigned_mics.has_key(first_frame_strip) or not assigned_mics.has_key(last_frame_strip):
                    raise ValueError(msg)

            overlap = expected_pattern.intersection(diff_strip)
            if len(overlap) > 0:
                common_inp_full_path = [assigned_mics[each_overlap] for each_overlap in overlap]
                common_inp_full_path.sort()
                assigned_inp_mics.append((each_mic, common_inp_full_path))

        return assigned_inp_mics

    
    def check_whether_provided_frame_number_matches_provided_micrographs_old(self, micrographs, input_mics, frame_count):
        """
        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> mics = ['test.hdf', 'tost.hdf']
        >>> input_mics = ['test_{0:03}.hdf'.format(each) for each in list(range(5))]
        >>> s.check_whether_provided_frame_number_matches_provided_micrographs_old(mics, input_mics, 5)
        [('test.hdf', ['test_000.hdf', 'test_001.hdf', 'test_002.hdf', 'test_003.hdf', 'test_004.hdf'])]
        >>> input_mics = ['test_{0:02}.hdf'.format(each) for each in list(range(5))]
        >>> s.check_whether_provided_frame_number_matches_provided_micrographs_old(mics, input_mics, 5)
        [('test.hdf', ['test_00.hdf', 'test_01.hdf', 'test_02.hdf', 'test_03.hdf', 'test_04.hdf'])]
        >>> input_mics = ['test_{0:02}.hdf'.format(each) for each in list(range(5, 10))]
        >>> s.check_whether_provided_frame_number_matches_provided_micrographs_old(mics, input_mics, 5)
        [('test.hdf', ['test_05.hdf', 'test_06.hdf', 'test_07.hdf', 'test_08.hdf', 'test_09.hdf'])]
        >>> s.check_whether_provided_frame_number_matches_provided_micrographs_old(mics, input_mics, 6) #doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        ValueError: The number of provided frames (=6) from test_05.hdf, 
        test_06.hdf, test_07.hdf, test_08.hdf, test_09.hdf does not match the 
        'Processing frame number' (=6) specified. Please, change input 
        files of frames or the 'Processing frame number'.
        >>> input_mics = ['test_ttt.hdf'.format(each) for each in list(range(5))]
        >>> s.check_whether_provided_frame_number_matches_provided_micrographs_old(mics, input_mics, 4) #doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        ValueError: The provided frames (test_ttt.hdf, test_ttt.hdf, 
        test_ttt.hdf, test_ttt.hdf, test_ttt.hdf) can not be 
        assigned because they do not follow the pattern: test.hdf - 
        test_000.hdf, test_001.hdf, test_002.hdf, test_003.hdf, test_004.hdf.
        Please rename to make frames assignable to previous micrograph.
        """
        assigned_inp_mics = []
        for each_mic in micrographs:
            micrograph_base = os.path.splitext(os.path.basename(each_mic))[0]

            common_inp = [os.path.basename(each_inp) for each_inp in input_mics if micrograph_base in each_inp]
            diff = [os.path.splitext(each_inp)[0][len(micrograph_base):] for each_inp in common_inp 
                    if os.path.splitext(each_inp)[0].startswith(micrograph_base)]
            diff_strip = [each_diff.strip('_').strip('0') for each_diff in diff]
            
            expected_patterns = []
            for each_first_frame in list(range(400)):
                expected_patterns.append(['{0}'.format(each_id) if each_id != 0 else '' 
                for each_id in list(range(each_first_frame, each_first_frame + len(diff_strip)))])
            
            if diff_strip in expected_patterns:
                common_inp_full_path = [each_inp for each_inp in input_mics if micrograph_base in each_inp]
                if len(diff) > 0:
                    if len(diff) != frame_count:
                        msg = 'The number of provided frames (={0}) from {1} '.format(frame_count, ', '.join(common_inp)) + \
                        'does not match the \'Processing frame number\' (={0}) specified. '.format(frame_count) + \
                        'Please, change input files of frames or the \'Processing frame number\'.'
                        raise ValueError(msg)
                    else:
                        assigned_inp_mics.append((each_mic, common_inp_full_path))
            else:
                expected_pattern_underscore = ['_{0:03}'.format(each_id) for each_id in list(range(len(diff)))]
                micrograph_ext = os.path.splitext(os.path.basename(each_mic))[-1]
                expected_mics = [micrograph_base + each_pattern + micrograph_ext 
                                 for each_pattern in expected_pattern_underscore]
 
                msg = 'The provided frames ({0}) can not be assigned because '.format(', '.join(common_inp)) + \
                'they do not follow the pattern: {0} - {1}. '.format(os.path.basename(each_mic), ', '.join(expected_mics) ) + \
                'Please rename to make frames assignable to previous micrograph.'
 
                raise ValueError(msg)

        return assigned_inp_mics

    
    def check_whether_spring_db_entries_match_provided_micrographs(self):
        if not self.coordinate_files[0].endswith('db'):
            msg = 'Please provide coordinates from previous spring.db that need to be frame processed.'
            raise ValueError(msg)
        else:
            spring_db = self.coordinate_files[0]

        session = SpringDataBase().setup_sqlite_db(base, spring_db)
        helices = session.query(HelixTable).order_by(HelixTable.id).all()
        
        mic_ids = []
        [mic_ids.append(each_helix.mic_id) for each_helix in helices if each_helix.mic_id not in mic_ids]

        mics = session.query(CtfMicrographTable).all()
        
        demanded_frame_count = self.frame_range[-1] - self.frame_range[0]
        micrographs = []
        for each_mic in mics:
            mic_name = os.path.join(each_mic.dirname, each_mic.micrograph_name)
            mic_base = os.path.splitext(each_mic.micrograph_name)[0]
            micrographs.append(str(mic_name))
            search_str_mics = ' '.join(self.micrograph_files)
            if search_str_mics.find(mic_base) < 0:
                msg = 'Micrograph {0} could not be found in provided micrographs. Double-check existence.'.format(mic_name)
                raise ValueError(msg)
            if search_str_mics.find(mic_base) < demanded_frame_count:
                msg = 'The processing frame number does not match the number of provided micrographs for ' + \
                '{0}. Double check.'.format(mic_name)
                raise ValueError(msg)

        return micrographs

    
    def validate_input(self):
        if 0 < self.stepsize < self.pixelsize: 
            error_message = 'Segmentation step size can not be smaller than pixel size.'
            raise ValueError(error_message)
        
        coord_ending = list(set([os.path.splitext(each_file)[-1] for each_file in self.coordinate_files]))
        if not coord_ending[0].endswith('db'):
            if self.straightness_selection or self.mics_selection or self.helices_selection or \
            self.defocus_selection or self.astigmatism_selection:
                err_msg = 'You have specified selection criteria, please provide the coordinates with a ' + \
                'spring.db from previous segment or segmentrefine3d runs. This spring.db will be used for ' + \
                'assessing the criteria.'
                raise ValueError(err_msg)
                
        if self.frame_option:
            first_frame, last_frame = self.frame_range
            if last_frame < first_frame:
                msg = 'The specified first frame {0} is greater than '.format(first_frame) + \
                'the last frame {0}. Please make first frame smaller or equal to last frame.'.format(last_frame)
                raise ValueError(msg)
            if not coord_ending[0].endswith('db'):
                err_msg = 'As you specified the \'Frame processing option\', please provide coordinates by the ' + \
                'the previously run spring.db instead of the original coordinate files.'
                raise ValueError(err_msg)

            ending_mics = set([os.path.splitext(each_mic)[-1] for each_mic in self.micrograph_files])
            if len(ending_mics) == 1 and list(ending_mics)[0].endswith('mrcs'):
                assigned_mics = []
                for each_mic in self.micrograph_files:
                    mic_frames = [os.path.splitext(each_mic)[0] + '@{0}{1}mrcs'.format(each_frame, os.extsep) 
                                  for each_frame in range(first_frame, last_frame + 1)]
                    assigned_mics.append((each_mic, mic_frames))
            else:
                mics = self.check_whether_spring_db_entries_match_provided_micrographs()

                assigned_mics = self.check_whether_provided_frame_number_matches_provided_micrographs(mics,
                self.micrograph_files, self.frame_range)

            source_session = SpringDataBase().setup_sqlite_db(base, self.spring_path)
            new_session = SpringDataBase().setup_sqlite_db(base, self.spring_db_frames)

            new_session = self.copy_micrograph_info_on_ctffind_and_ctftilt(assigned_mics, source_session, new_session)
        else:
            assigned_mics = None
        
        return assigned_mics

        
    def determine_boxsize_closest_to_fast_values(self, boxsize_ori, ten=False):
        """
        # Values taken from http://blake.bcm.edu/emanwiki/EMAN2/BoxSize
        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> s.determine_boxsize_closest_to_fast_values(333)
        352
        >>> s.determine_boxsize_closest_to_fast_values(333, ten=True)
        360
        """
        fast_size = [32, 33, 35, 40, 44, 48, 52, 64, 66, 72, 84, 100, 104, 112, 128, 130, 132, 140, 150, 160, 168, 180,
        182, 192, 196, 220, 224, 240, 256, 260, 288, 300, 320, 324, 330, 352, 360, 384, 416, 420, 440, 448, 450, 480,
        512, 540, 576, 600, 625, 640, 648, 675, 720, 729, 750, 768, 800, 810, 864, 900, 960, 972, 1000, 1024, 1080,
        1125, 1152, 1200, 1215, 1250, 1280, 1296, 1350, 1440, 1458, 1500, 1536, 1600, 1620, 1728, 1800, 1875, 1920,
        1944, 2000, 2025, 2048, 2160, 2187, 2250, 2304, 2400, 2430, 2500, 2560, 2592, 2700, 2880, 2916, 3000, 3072,
        3125, 3200, 3240, 3375, 3456, 3600, 3645, 3750, 3840, 3888, 4000, 4050, 4320, 4374, 4500, 4608, 4800, 4860,
        5000, 5120, 5184, 5400, 5625, 5760, 5832, 6000, 6075, 6144, 6250, 6400, 6480, 6750, 6912, 7200, 7290, 7500,
        7680, 7776, 8000, 8100]
        
        if ten:
            fast_size = [each_size for each_size in fast_size if (each_size) % 10 == 0]

        fast_size_id = np.argmin(np.abs(boxsize_ori - np.array(fast_size)))
        fast_box = fast_size[fast_size_id]
        if fast_box < boxsize_ori:
            fast_box = fast_size[fast_size_id + 1]
        
        return fast_box
        

class SegmentPreparationFileRead(SegmentPreparation):
    def read_coordinate_lines_from_eman_format_and_separate_helices(self, box_coord):
        """
        >>> lines = ['50\\t50\\t100\\t100\\t-1\\n', '40\\t40\\t100\\t100\\t0\\n']
        >>> lines += ['30\\t30\\t100\\t100\\t-2\\n', '20\\t20\\t100\\t100\\t-1\\n',]
        >>> box_coord = lines + ['10\\t10\\t100\\t100\\t-2\\n']
        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> s.read_coordinate_lines_from_eman_format_and_separate_helices(box_coord) #doctest: +NORMALIZE_WHITESPACE
        ['50\\t50\\t100\\t100\\t-1\\n40\\t40\\t100\\t100\\t0\\n30\\t30\\t100\\t100\\t-2\\n', 
        '20\\t20\\t100\\t100\\t-1\\n10\\t10\\t100\\t100\\t-2\\n']
        """
        helixcoord = []
        helix = ''
        for each_file_line in box_coord:
            helix = helix + each_file_line
            if each_file_line.endswith('-2\n'):
                helixcoord.append(helix)
                helix = ''
        
        if helixcoord == []:
            helixcoord.append(helix)
            
        return helixcoord


    def add_start_or_end_flag(self, bsoft_coord, id_pos, helixcoord, helix, previous_helix_id, each_index,
    current_helix_id):
        next_line = bsoft_coord[each_index + 1]
        if next_line != '\n':
            next_helix_id = next_line.split()[id_pos]
            if previous_helix_id != current_helix_id:
                helix = helix + '\t-1\n'
                previous_helix_id = current_helix_id
            elif next_helix_id != current_helix_id:
                helix = helix + '\t-2\n'
                helixcoord.append(helix)
                helix = ''
            else:
                helix = helix + '\t0\n'
                
        return helix, previous_helix_id


    def append_final_helix(self, helixcoord, helix):
        helix = helix + '\t-2\n'
        helixcoord.append(helix)
        coordinate_lines = False
        
        return helixcoord, coordinate_lines
    

    def read_coordinate_lines_from_bsoft_particle_format_and_convert_to_eman_format(self, bsoft_coord, segment_size=40.0):
        """
        >>> bsoft = [ '_particle.select\\n']
        >>> ln1 = '1    1       0  1.0000  366.00 2058.00    0.00  20.000  20.0'
        >>> ln1 += '00   0.000  1.0000  0.0000  0.0000   34.79  1.0000    1\\n'
        >>> ln2 = '2    1       0  1.0000  382.43 2046.59    0.00  20.000  20.0'
        >>> ln2 += '00   0.000  1.0000  0.0000  0.0000   34.79  1.0000    1\\n'
        >>> ln3 = '3    2       0  1.0000 1326.17 2107.80    0.00  20.000  20.0'
        >>> ln3 += '00   0.000  1.0000  0.0000  0.0000  -54.08  1.0000    2\\n'
        >>> ln4 = '4    2       0  1.0000 1326.17 2107.80    0.00  20.000  20.0'
        >>> ln4 += '00   0.000  1.0000  0.0000  0.0000  -54.08  5.0000    2\\n'
        >>> ln5 = '5    2       0  1.0000 1326.17 2107.80    0.00  20.000  20.0'
        >>> ln5 += '00   0.000  1.0000  0.0000  0.0000  -54.08  5.0000    2\\n'
        >>> bsoft += [ln1, ln2, ln3, ln4, ln5, '\\n', '\\n', 'loop_\\n']
        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> s.read_coordinate_lines_from_bsoft_particle_format_and_convert_to_eman_format(bsoft) #doctest: +NORMALIZE_WHITESPACE
        ['346.0\\t2038.0\\t40.0\\t40.0\\t-1\\n362.43\\t2026.59\\t40.0\\t40.0\\t-2\\n', 
        '1306.17\\t2087.8\\t40.0\\t40.0\\t-1\\n1306.17\\t2087.8\\t40.0\\t40.0\\t0\\n1306.17\\t2087.8\\t40.0\\t40.0\\t-2\\n']
        >>> bsoft = [ '_filament.z\\n','      1      1  366.00 2058.00    0.00\\n']
        >>> bsoft += ['      1      2  461.00 1992.00    0.00\\n']
        >>> bsoft += ['      2      1  553.00 1905.00    0.00\\n']
        >>> bsoft += ['      3      1  641.00 1838.00    0.00\\n']
        >>> bsoft += ['      3      2  707.33 1800.67    0.00\\n', '\\n']
        >>> s.read_coordinate_lines_from_bsoft_particle_format_and_convert_to_eman_format(bsoft)
        []
        """
        helixcoord = []
        helix = ''
        coordinate_lines = False
        previous_helix_id = '0'
        for each_index, each_file_line in enumerate(bsoft_coord):
            if each_file_line.startswith('_particle.select'):
                coordinate_lines = True
            if coordinate_lines and len(each_file_line.split()) == 16:
                current_helix_id = (each_file_line.split()[-1])
                each_coord_line = '{x}\t{y}\t{box_x}\t{box_y}'.format(x=float(each_file_line.split()[4]) - segment_size/2,
                y=float(each_file_line.split()[5]) - segment_size/2, box_x=segment_size, box_y=segment_size)
                                                                                      
                helix = helix + each_coord_line
                
                helix, previous_helix_id = self.add_start_or_end_flag(bsoft_coord, -1, helixcoord, helix,
                previous_helix_id, each_index, current_helix_id)
                
            if each_file_line.startswith('loop_') and coordinate_lines:
                helixcoord, coordinate_lines= self.append_final_helix(helixcoord, helix)
        
        return helixcoord
    
    
    def read_coordinate_lines_from_bsoft_filament_format_and_convert_to_eman_format(self, bsoft_coord,
    segment_size=40.0):
        """
        >>> bsoft =  [ '_filament.z\\n']
        >>> bsoft += ['      1      1  366.00 2058.00    0.00\\n']
        >>> bsoft += ['      1      2  461.00 1992.00    0.00\\n']
        >>> bsoft += ['      1      3  553.00 1905.00    0.00\\n']
        >>> bsoft += ['      2      1  641.00 1838.00    0.00\\n']
        >>> bsoft += ['      2      2  707.33 1800.67    0.00\\n', '\\n']
        >>> from spring.segment2d.segment import Segment
        >>> s = Segment()
        >>> s.read_coordinate_lines_from_bsoft_filament_format_and_convert_to_eman_format(bsoft) #doctest: +NORMALIZE_WHITESPACE
        ['346.0\\t2038.0\\t40.0\\t40.0\\t-1\\n441.0\\t1972.0\\t40.0\\t40.0\\t0\\n533.0\\t1885.0\\t40.0\\t40.0\\t-2\\n', 
        '621.0\\t1818.0\\t40.0\\t40.0\\t-1\\n687.33\\t1780.67\\t40.0\\t40.0\\t-2\\n']
        >>> bsoft = ['_filament.id\\n', '_filament.node_id\\n']
        >>> bsoft += ['_filament.id\\n', '_filament.node_id\\n', '_filament.x\\n']
        >>> bsoft += ['_filament.y\\n', '_filament.z\\n'] 
        >>> bsoft += ['      1      1  100.00  100.00    0.00\\n']
        >>> bsoft += ['      1      2   60.00   60.00    0.00\\n', '\\n', '\\n']
        >>> s.read_coordinate_lines_from_bsoft_filament_format_and_convert_to_eman_format(bsoft)
        ['80.0\\t80.0\\t40.0\\t40.0\\t-1\\n40.0\\t40.0\\t40.0\\t40.0\\t-2\\n']
        """
        helixcoord = []
        helix = ''
        coordinate_lines = False
        previous_helix_id = '0'
        for each_index, each_file_line in enumerate(bsoft_coord):
            if each_file_line.startswith('_filament.z'):
                coordinate_lines = True
            if coordinate_lines and len(each_file_line.split()) == 5:
                current_helix_id = (each_file_line.split()[0])
                each_coord_line = '{x}\t{y}\t{box_x}\t{box_y}'.format(x=float(each_file_line.split()[2]) - segment_size/2,
                y=float(each_file_line.split()[3]) - segment_size/2, box_x=segment_size, box_y=segment_size)
                                                                                      
                helix = helix + each_coord_line
                
                helix, previous_helix_id = self.add_start_or_end_flag(bsoft_coord, 0, helixcoord, helix,
                previous_helix_id, each_index, current_helix_id)
                
            if each_file_line == '\n' and coordinate_lines:
                helixcoord, coordinate_lines = self.append_final_helix(helixcoord, helix)
        
        return helixcoord
    