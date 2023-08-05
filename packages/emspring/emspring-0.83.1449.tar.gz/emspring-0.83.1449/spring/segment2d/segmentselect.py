# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to select segments according to different criteria such as class member, curvature, diffraction quality
"""
from EMAN2 import EMData
from collections import namedtuple
from scipy import signal
from spring.csinfrastr.csdatabase import SpringDataBase, base, SegmentTable, CtfMicrographTable, HelixTable, \
    CtfFindMicrographTable, CtfTiltMicrographTable
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csreadinput import OptHandler
from sqlalchemy.sql.expression import and_, or_
from tabulate import tabulate
import numpy as np
import shutil


class SegmentSelectPar:
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'segmentselect'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.segmentselect_features = Features()
        self.feature_set = self.segmentselect_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    

    def define_parameters_and_their_properties(self):
        self.feature_set = self.segmentselect_features.set_inp_stack(self.feature_set)
        self.feature_set = self.segmentselect_features.set_out_stack(self.feature_set)
        self.feature_set = self.segmentselect_features.set_spring_path_segments(self.feature_set)
        self.feature_set = self.segmentselect_features.set_database_selected(self.feature_set)
        
        self.feature_set = self.segmentselect_features.set_selection_criteria_from_segment_table(self.feature_set)
        
        
    def define_program_states(self):

        self.feature_set.program_states['extract_segments']='Extract specified classes'


class SegmentSelectPreparation(object):
    """
    * Class that holds functions to extract members from class average stack
    
    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            self.p = self.feature_set.parameters

            self.infile = self.p['Image input stack']
            self.outfile = self.p['Image output stack']
        
            self.spring_db_path = self.p['spring.db file']
            self.db_selected = self.p['Selected database']
            
            self = self.define_selection_parameters_from_segment_table(self, self.p)


    def define_mics_and_helices_selection(self, obj, p):
        obj.mics_selection = p['Micrographs select option']
        obj.mics_in_or_exclude = p['Include or exclude micrographs']
        obj.mics_entries = p['Micrographs list']
        
        obj.helices_selection = p['Helices select option']
        obj.helices_in_or_exclude = p['Include or exclude helices']
        obj.helices_entries = p['Helices list']
        
        return obj


    def define_straightness_selection(self, obj, p):
        obj.straightness_selection = p['Straightness select option']
        obj.straightness_in_or_exclude = p['Include or exclude straight helices']
        obj.curvature_range_perc = p['Persistence length range']
        
        return obj


    def define_defocus_and_astigmatism_selection(self, obj, p):
        obj.defocus_selection = p['Defocus select option']
        obj.defocus_in_or_exclude = p['Include or exclude defocus range']
        obj.defocus_range = p['Defocus range']

        obj.astigmatism_selection = p['Astigmatism select option']
        obj.astigmatism_in_or_exclude = p['Include or exclude astigmatic segments']
        obj.astigmatism_range = p['Astigmatism range']
        
        return obj


    def define_selection_parameters_from_segment_table(self, obj, p):
        obj = self.define_mics_and_helices_selection(obj, p)
        
        obj.segments_selection = p['Segments select option']
        obj.segments_in_or_exclude = p['Include or exclude segments']
        obj.segments_file = p['Segment file']

        obj.classes_selection = p['Classes select option']
        obj.classes_in_or_exclude = p['Include or exclude classes']
        obj.class_type = p['Class type']
        obj.classes_entries = p['Classes list']
        
        obj.persistence_class = p['Persistence class option'] 
        obj.persistence_length = p['Persistence class length in Angstrom']
        obj.class_occupancy_thres = p['Class occupancy threshold']

        obj = self.define_straightness_selection(obj, p)
        
        obj.ccc_layer_selection = p['Layer line correlation select option']
        obj.ccc_layer_in_or_exclude = p['Include or exclude segments based on layer-line correlation']
        obj.ccc_layer_range_perc = p['Correlation layer line range']
        
        obj = self.define_defocus_and_astigmatism_selection(obj, p)
        
        return obj
    

    def prepare_list_from_comma_separated_input(self, entry, filter_criterion):
        """
        * Function to convert comma or semicolon separated entry string to \
        continuous list of classes
        
        #. Input: comma or semicolon separated entry string
        #. Output: list of classes
        #. Usage: list = prepare_list_from_comma_separated_input(inputstring)
        
        >>> from spring.segment2d.segmentselect import SegmentSelect
        >>> ss = SegmentSelect()
        >>> ss.prepare_list_from_comma_separated_input('1 ', 'micrograph')
        [1]
        >>> ss.prepare_list_from_comma_separated_input('1,2', 'class')
        [1, 2]
        >>> input = '1,2, 5-10; 66, 99-101'
        >>> ss.prepare_list_from_comma_separated_input(input, 'class') 
        [1, 2, 5, 6, 7, 8, 9, 10, 66, 99, 100, 101]
        >>> input += '; j'
        >>> ss.prepare_list_from_comma_separated_input(input, 'class') #doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
        ValueError: Specified class numbers could not be interpreted as integer
         numbers, double-check entry.
        """
        classes = []
        error_message = 'Specified {0} numbers could not be interpreted as integer numbers, double-check entry.'.\
        format(filter_criterion)
        for entry in entry.split(';'):
            for each_entry in entry.split(','):
                if each_entry.find('-') >= 1:
                    try:
                        first_class = int(each_entry.split('-')[0])
                        last_class = int(each_entry.split('-')[-1]) + 1
                    except:
                        raise ValueError(error_message)
                    for each_subentry in range(first_class, last_class):
                        classes.append(each_subentry)
                else:
                    try:
                        classes.append(int(each_entry))
                    except:
                        raise ValueError(error_message)
        
        return classes
            

class SegmentSelectFilter(SegmentSelectPreparation):

    def read_segment_selection_from_file(self, segments, segments_selection, segments_in_or_exclude, segment_file):
        if segments_selection:
            sfile = open(segment_file, 'r')
            try:
                segment_ids = [int(each_line) for each_line in sfile.readlines() if not each_line.startswith('#')]
            except:
                msg = 'Content of segment selection file could not be interpreted as integer. Double-check correct ' + \
                'format of segment ids.'
                raise ValueError(msg)
            sfile.close()

            if segments_in_or_exclude == 'include':
                included_segments = [each_segment.stack_id for each_segment in segments 
                                    if each_segment.stack_id in segment_ids]
            elif segments_in_or_exclude == 'exclude':
                included_segments = [each_segment.stack_id for each_segment in segments 
                                    if each_segment.stack_id not in segment_ids]

        elif not segments_selection:
            included_segments = [each_segment.stack_id for each_segment in segments]
                    
        excluded_seg_count = len(segments) - len(set(included_segments))
        
        return included_segments, excluded_seg_count


    def compute_local_average_from_measurements(self, segment_measurements, window_size):
        """
        >>> from spring.segment2d.segmentselect import SegmentSelect
        >>> SegmentSelect().compute_local_average_from_measurements(np.arange(10), 4)
        array([ 1.  ,  1.  ,  1.5 ,  2.5 ,  3.5 ,  4.5 ,  5.5 ,  6.5 ,  7.5 ,  8.25])
        >>> rand_series = [0.33, -0.84, -0.55, 0.27, 0.26, -0.09, -0.85, -0.18, 0.71, 0.07]
        >>> SegmentSelect().compute_local_average_from_measurements(rand_series, 5)
        array([-0.49 , -0.326, -0.106, -0.19 , -0.192, -0.118, -0.03 , -0.068,
               -0.036,  0.276])
        >>> SegmentSelect().compute_local_average_from_measurements(np.arange(10), 12)
        array([ 2.5,  2.5,  2.7,  3.1,  3.7,  4.5,  5.4,  6.1,  6.6,  6.9])
        >>> SegmentSelect().compute_local_average_from_measurements(rand_series, 2) #doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
          File '/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/doctest.py', 
              line 1231, in __run
            compileflags, 1) in test.globs
          File '<doctest segment.SegmentSelect.compute_local_average_from_measurements[4]>', 
              line 1, in <module>
            SegmentSelect().compute_local_average_from_measurements(rand_series, 2)
          File 'spring/segment2d/segment.py', line 994, in 
              compute_local_average_from_measurements
            raise ValueError, msg
        ValueError: Please choose larger averaging distance or decrease step 
        size of segmentation to allow smaller local averaging. Otherwise turn off 
        local averaging option.

        """
        if window_size < 3:
            msg = 'Please choose larger averaging distance or decrease step size of segmentation to allow smaller ' + \
            'local averaging. Otherwise turn off local averaging option.'
            raise ValueError(msg)
        window_function = np.zeros(len(segment_measurements))
        if window_size > len(segment_measurements):
            window_size = len(segment_measurements)
        for each_index in range(window_size):
            window_function[each_index] = 1.0
            
        window_function = (np.roll(window_function, (len(segment_measurements) - window_size)/2))/window_size
        
        measurements_with_borders = np.r_[segment_measurements[window_size-1:0:-1], segment_measurements,
        segment_measurements[-1:-window_size:-1]]
        
        locally_averaged_measurements = signal.fftconvolve(measurements_with_borders, window_function, mode='same')

        locally_averaged_measurements = locally_averaged_measurements[window_size-1:-(window_size - 1)]
        
        return locally_averaged_measurements
            
            
    def determine_included_stack_ids_according_to_class_persistence(self, segments, class_in_or_exclude,
    persistence_length, class_list, helices, class_occupancy_thres=0.5, class_attr='class_id'):
        """
        >>> from spring.segment2d.segmentselect import SegmentSelect
        >>> class_list = [1, 2]
        >>> stack_ids = range(10, 30)
        >>> class_ids = 6 * [0] + 6 * [1] + 8 * [2] 
        >>> helix_ids = 10 * [11] + 10 * [12]
        >>> distances = 2 * np.linspace(0, 1400, 10).tolist()
        >>> segment_nt = namedtuple('seg', 'stack_id class_id, helix_id, distance_from_start_A')
        >>> segments = [segment_nt._make(each_info) for each_info in zip(stack_ids, class_ids, helix_ids, distances)]
        >>> helix_nt = namedtuple('hel', 'id')
        >>> helices = [helix_nt(each_helix_id) for each_helix_id in set(helix_ids)]
        >>> s = SegmentSelect()
        >>> s.determine_included_stack_ids_according_to_class_persistence(segments, 'include', 700, class_list, helices)
        [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
        >>> s.determine_included_stack_ids_according_to_class_persistence(segments, 'exclude', 700, class_list, helices)
        [10, 11, 12, 13, 14, 15]
        >>> helix_ids = 10 * [15] + 10 * [12]
        >>> segments = [segment_nt._make(each_info) for each_info in zip(stack_ids, class_ids, helix_ids, distances)]
        >>> s.determine_included_stack_ids_according_to_class_persistence(segments, 'include', 700, class_list, helices)
        [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        >>> class_list = [0, 1]
        >>> class_ids = 1 * [0] + 1 * [1] + 8 * [2] + 1 * [0] + 1 * [1] + 8 * [2] 
        >>> segments = [segment_nt._make(each_info) for each_info in zip(stack_ids, class_ids, helix_ids, distances)]
        >>> s.determine_included_stack_ids_according_to_class_persistence(segments, 'include', 700, class_list, helices)
        []
        """
        stack_ids = np.array([each_segment.stack_id for each_segment in segments])
        class_ids = np.array([getattr(each_segment, class_attr) for each_segment in segments])
        helix_ids = np.array([each_segment.helix_id for each_segment in segments])
        distances = np.array([each_segment.distance_from_start_A for each_segment in segments])
        classes_present = np.in1d(class_ids, np.array(class_list))
        if class_in_or_exclude == 'exclude':
            classes_present = np.invert(classes_present)

        classes_percent = classes_present.astype(float)
        finally_selected = np.array([])
        log_ids = np.array([])
        hel_ids = np.array([])
        occ = np.array([])
        
        to_be_logged = []

        for each_helix in helices:
            classes_helix = classes_percent[helix_ids == each_helix.id]
            stepsize = (np.diff(distances[helix_ids == each_helix.id]))
            if len(stepsize) > 0:
                avg_count = int(round(persistence_length / abs(np.mean(stepsize))))
                avg_classes = self.compute_local_average_from_measurements(classes_helix, avg_count)
                selected = avg_classes > class_occupancy_thres
                if len(selected[selected == True]) <= 3:
                    selected = np.zeros(len(selected), dtype=bool)
                finally_selected = np.append(finally_selected, selected)
    
                to_be_logged += zip(stack_ids[helix_ids == each_helix.id], len(avg_classes) * [each_helix.id], avg_classes)
    
                log_ids = np.append(log_ids, stack_ids[helix_ids == each_helix.id])
                hel_ids = np.append(hel_ids, len(avg_classes) * [each_helix.id])
                occ = np.append(occ, avg_classes)
        
        finally_selected = finally_selected.astype(bool)
        included_segments_classes = stack_ids[finally_selected].tolist()

        msg = tabulate(to_be_logged, headers=['stack_id', 'helix_id', 'class_occupancy'])
        self.log.ilog(msg)

        return included_segments_classes


    def filter_segments_by_classes_and_persistence(self, session, segments, classes_selection, class_in_or_exclude,
    class_entries, persistence_class, persistence_length, class_occupancy_thres, class_type):
        class_attr = class_type
            
        if classes_selection:
            class_list = self.prepare_list_from_comma_separated_input(class_entries, 'class')
            if class_in_or_exclude == 'include' and not persistence_class:
                included_segments_classes = [each_segment.stack_id for each_segment in segments 
                                             if getattr(each_segment, class_attr) in class_list]
                    
            elif class_in_or_exclude == 'exclude' and not persistence_class:
                included_segments_classes = [each_segment.stack_id for each_segment in segments 
                                             if getattr(each_segment, class_attr) not in class_list]

            if persistence_class:
                helices = session.query(HelixTable).order_by(HelixTable.id).all()

                included_segments_classes = self.determine_included_stack_ids_according_to_class_persistence(segments,
                class_in_or_exclude, persistence_length, class_list, helices, class_occupancy_thres, class_attr)
                    
        elif not classes_selection:
            included_segments_classes = [each_segment.stack_id for each_segment in segments]
                    
        excluded_count = len(segments) - len(set(included_segments_classes))
        
        return included_segments_classes, excluded_count


    def filter_segments_by_entry_string(self, segments, attr_id, attr_selection, attr_in_or_exclude,
    attr_entries, filter_criterion):

        if attr_selection:
            attr_list = self.prepare_list_from_comma_separated_input(attr_entries, filter_criterion)
            if attr_in_or_exclude == 'include':
                included_segments_classes = [each_segment.stack_id for each_segment in segments 
                                             if getattr(each_segment, attr_id) in attr_list]
                    
            elif attr_in_or_exclude == 'exclude':
                included_segments_classes = [each_segment.stack_id for each_segment in segments 
                                             if getattr(each_segment, attr_id) not in attr_list]

        elif not attr_selection:
            included_segments_classes = [each_segment.stack_id for each_segment in segments]
                    
        excluded_count = len(segments) - len(set(included_segments_classes))
        
        return included_segments_classes, excluded_count
    
        
    def get_excluded_count(self, session, included_segments_classes):
        segment_count = session.query(SegmentTable).order_by(SegmentTable.stack_id).count()
        excluded_count = segment_count - len(set(included_segments_classes))
        
        return excluded_count

    
    def filter_segments_by_property(self, session, segment_table_property, property_selection, property_in_or_exclude,
    property_range):
        included_segments_property = []
        if property_selection:
            if property_in_or_exclude == 'include':
                included_segments = session.query(SegmentTable).\
                filter(and_(segment_table_property >= property_range[0], 
                            segment_table_property <= property_range[1])).all()
                            
                included_segments_property = [each_segment.stack_id for each_segment in included_segments]

            elif property_in_or_exclude == 'exclude':
                included_segments = session.query(SegmentTable).\
                filter(or_(segment_table_property < property_range[0], 
                           segment_table_property > property_range[1])).all()
                           
                included_segments_property = [each_segment.stack_id for each_segment in included_segments]

        elif not property_selection:
            included_segments = session.query(SegmentTable).all()
            included_segments_property = [each_segment.stack_id for each_segment in included_segments]
            
        excluded_count = self.get_excluded_count(session, included_segments_property)
        
        return included_segments_property, excluded_count
    

    def filter_by_properties_that_keep_helices_together(self, obj, session, segments):
        included_segments_mics, excluded_mics_count = self.filter_segments_by_entry_string(segments, 'mic_id', 
        obj.mics_selection, obj.mics_in_or_exclude, obj.mics_entries, 'micrograph')

        included_segments_helices, excluded_helix_count = self.filter_segments_by_entry_string(segments, 
        'helix_id', obj.helices_selection, obj.helices_in_or_exclude, obj.helices_entries, 'helix')

        included_segments_curve, excluded_curvature_count = self.filter_segments_by_property(session, 
        SegmentTable.curvature, obj.straightness_selection, obj.straightness_in_or_exclude, obj.curvature_range)

        included_segments_defocus, excluded_defocus_count = self.filter_segments_by_property(session, 
        SegmentTable.avg_defocus, obj.defocus_selection, obj.defocus_in_or_exclude, obj.defocus_range)

        included_segments_astigmatism, excluded_astig_count = self.filter_segments_by_property(session, 
        SegmentTable.astigmatism, obj.astigmatism_selection, obj.astigmatism_in_or_exclude, obj.astigmatism_range)

        return included_segments_mics, included_segments_helices, included_segments_curve, included_segments_defocus,\
        included_segments_astigmatism, excluded_mics_count, excluded_helix_count, excluded_curvature_count, \
        excluded_defocus_count, excluded_astig_count


    def filter_by_property_that_take_helices_apart(self, obj, session, segments):
        included_segments_classes, excluded_class_count = self.filter_segments_by_classes_and_persistence(session, 
        segments, obj.classes_selection, obj.classes_in_or_exclude, obj.classes_entries, obj.persistence_class, 
        obj.persistence_length, obj.class_occupancy_thres, obj.class_type)

        included_segments_ccc_layer, excluded_layer_count = self.filter_segments_by_property(session, 
        SegmentTable.ccc_layer, obj.ccc_layer_selection, obj.ccc_layer_in_or_exclude, obj.ccc_layer_range)

        return included_segments_classes, included_segments_ccc_layer, excluded_class_count, excluded_layer_count


    def check_whether_all_segments_were_excluded(self, combined_included_segments, included_segments_mics,
    included_segments_helices, included_segments_classes, included_segments_curve, included_segments_defocus,
    included_segments_astigmatism, included_segments_ccc_layer):
        """
        >>> from spring.segment2d.segmentselect import SegmentSelect
        >>> s = SegmentSelect()
        >>> s.check_whether_all_segments_were_excluded([], [0], [0], [0], [0], [0], [0], [0])#doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        ValueError: All segments were excluded as a result of stringent 
        selection criteria. Please, use less stringent criteria.
        >>> s.check_whether_all_segments_were_excluded([], [], [0], [0], [0], [0], [0], [0])#doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        ValueError: All segments were excluded because of 'micrograph' 
        selection criteria. Please, use less stringent selection criteria 
        for micrographs.
        >>> s.check_whether_all_segments_were_excluded([], [0], [], [], [0], [0], [0], [0])#doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
            ...
        ValueError: All segments were excluded because of 'helix', 
        'class' selection criteria. Please, use less stringent 
        selection criteria for helices, classes.
        """
        keyword = []
        if included_segments_mics == []:
            keyword.append(('micrograph', 'micrographs'))
        if included_segments_helices == []:
            keyword.append(('helix', 'helices'))
        if included_segments_classes == []:
            keyword.append(('class', 'classes'))
        if included_segments_curve == []:
            keyword.append(('straightness', 'straightness of helix'))
        if included_segments_defocus == []:
            keyword.append(('defocus', 'defocus'))
        if included_segments_astigmatism == []:
            keyword.append(('astigmatism', 'astigmatism'))
        if included_segments_ccc_layer == []:
            keyword.append(('layer-line correlation', 'layer-line correlation'))
        if keyword != []:
            keyword_one, keyword_two = zip(*keyword)
            error_message = 'All segments were excluded because of \'{0}\' '.format('\', \''.join(keyword_one)) + \
                'selection criteria. Please, use less stringent selection criteria for {0}. '.format(', '.join(keyword_two))
            raise ValueError(error_message)
        
        if combined_included_segments == []:
            message = 'All segments were excluded as a result of stringent selection criteria. Please, use less ' + \
            'stringent criteria.'
            raise ValueError(message)
        
        
    def summarize_counts(self, included_segments, excluded_seg_count, included_segments_mics, included_segments_helices,
    included_segments_defocus, included_segments_astigmatism, excluded_mics_count, excluded_helix_count,
    excluded_defocus_count, excluded_astig_count, included_segments_curve, included_segments_classes,
    included_segments_ccc_layer, excluded_class_count, excluded_curvature_count, excluded_layer_count):
                
        combined_included_segments = list(set(included_segments_curve).intersection(included_segments,
        included_segments_mics, included_segments_helices, included_segments_classes, included_segments_defocus,
        included_segments_astigmatism, included_segments_ccc_layer))
        
        self.check_whether_all_segments_were_excluded(combined_included_segments, included_segments_mics,
        included_segments_helices, included_segments_classes, included_segments_curve, included_segments_defocus,
        included_segments_astigmatism, included_segments_ccc_layer)
        
        excluded_counts = namedtuple('excluded_counts', 'seg_count mic_count helix_count class_count ' + \
                                     'curvature_count defocus_count astig_count layer_cc_count')
        
        excluded_segment_counts = excluded_counts(excluded_seg_count, excluded_mics_count, excluded_helix_count,
        excluded_class_count, excluded_curvature_count, excluded_defocus_count, excluded_astig_count,
        excluded_layer_count)
        
        combined_included_segments.sort()
        
        return excluded_segment_counts, combined_included_segments

        
    def filter_non_orientation_parameters_based_on_selection_criteria(self, obj, spring_db='spring.db',
    keep_helices_together=False):
        session = SpringDataBase().setup_sqlite_db(base, spring_db)
        
        segments = session.query(SegmentTable).order_by(SegmentTable.stack_id).all()
        included_segments, excluded_seg_count = self.read_segment_selection_from_file(segments, obj.segments_selection,
        obj.segments_in_or_exclude, obj.segments_file)

        included_segments_mics, included_segments_helices, included_segments_curve, included_segments_defocus, \
        included_segments_astigmatism, excluded_mics_count, excluded_helix_count, excluded_curvature_count, \
        excluded_defocus_count, excluded_astig_count = \
        self.filter_by_properties_that_keep_helices_together(obj, session, segments)
        
        included_segments_classes, included_segments_ccc_layer, excluded_class_count, excluded_layer_count = \
        self.filter_by_property_that_take_helices_apart(obj, session, segments)

        excluded_segment_counts, combined_included_segments = self.summarize_counts(included_segments,
        excluded_seg_count, included_segments_mics, included_segments_helices, included_segments_defocus,
        included_segments_astigmatism, excluded_mics_count, excluded_helix_count, excluded_defocus_count,
        excluded_astig_count, included_segments_curve, included_segments_classes, included_segments_ccc_layer,
        excluded_class_count, excluded_curvature_count, excluded_layer_count)
        
        if keep_helices_together:
            helix_ids = list(set([each_segment.helix_id for each_segment in segments 
                         if each_segment.stack_id in combined_included_segments]))
            
            combined_included_segments = [each_segment.stack_id for each_segment in segments 
                                          if each_segment.helix_id in helix_ids]
            
            combined_included_segments.sort()

        msg = 'The selection resulted in the following number of included and excluded segments:\n'
        msg += tabulate(zip(['included', 'excluded'], 
                       [str(len(combined_included_segments)), str(len(segments) - len(combined_included_segments))]), 
                       ['total', str(len(segments))])

        msg += '\nThe number of segments that were excluded listed by criteria:\n'
        msg += tabulate(zip(list(excluded_segment_counts._fields), list(excluded_segment_counts)))
        msg += '\nThe following {0} segments are included in the selection:\n{1}'.\
        format(len(combined_included_segments), ', '.join([str(each_seg) for each_seg in combined_included_segments]))
        self.log.ilog(msg)

        return combined_included_segments, excluded_segment_counts 
    
    
class SegmentSelect(SegmentSelectFilter):

    def remove_all_previous_entries(self, session, column_name):
        column = session.query(column_name).all()
        for each_item in column:
            session.delete(each_item)
        
        return session
    

    def copy_segments_onto_output_stack(self, segment_ids):
        segment = EMData()
        for each_new_id, each_seg_id in enumerate(segment_ids):
            segment.read_image(self.infile, each_seg_id)
            segment.write_image(self.outfile, each_new_id)
            self.log.ilog('Segment {0} included in the output stack: new segment {1}.'.format(each_seg_id, each_new_id))
            

    def add_filtered_segments(self, segment_ids, session, updated_session):

        segments = session.query(SegmentTable).all()
        columns = SpringDataBase().get_columns_from_table(SegmentTable)
        each_updated_seg_id = 0
        for each_segment in segments:
            if each_segment.stack_id in segment_ids:
                data = SpringDataBase().get_data_from_entry(columns, each_segment)
                data['stack_id'] = each_updated_seg_id
                each_updated_seg_id += 1
                data.__delitem__('id')
                updated_session.add(SegmentTable(**data))
            
        return updated_session
    
        
    def update_ccc_layer_in_each_helix(self, updated_session, each_helix):
        segments = updated_session.query(SegmentTable).filter(SegmentTable.helix_id == each_helix.id)
        ccc_layer = [each_segment.ccc_layer for each_segment in segments]
        if ccc_layer != []:
            if ccc_layer[0] is not None:
                each_helix.avg_ccc_layer = np.mean(ccc_layer)
        
        return updated_session
    

    def update_curvature_in_each_helix(self, updated_session, each_helix):
        segments = updated_session.query(SegmentTable).filter(SegmentTable.helix_id == each_helix.id)
        curvature = [each_segment.curvature for each_segment in segments]
        if curvature != []:
            if curvature[0] is not None:
                each_helix.avg_curvature = np.mean(curvature)
        
        return updated_session


    def update_inplane_angle_in_each_helix(self, updated_session, each_helix):
        segments = updated_session.query(SegmentTable.inplane_angle).filter(SegmentTable.helix_id == each_helix.id)
        inplane_angle = [each_segment.inplane_angle for each_segment in segments]
        if inplane_angle != []:
            if inplane_angle[0] is not None:
                each_helix.avg_inplane_angle = np.mean(inplane_angle)
        
        return updated_session
    

    def update_records_in_helix(self, updated_session):
        helices = updated_session.query(HelixTable).all()
        
        for each_helix in helices:
            updated_session = self.update_ccc_layer_in_each_helix(updated_session, each_helix)
            updated_session = self.update_curvature_in_each_helix(updated_session, each_helix)
            updated_session = self.update_inplane_angle_in_each_helix(updated_session, each_helix)
            
            updated_session.merge(each_helix)
            
        return updated_session
            
    
    def write_out_new_database_for_filtered_stack(self, segment_ids):
        session = SpringDataBase().setup_sqlite_db(base)
        updated_session = SpringDataBase().setup_sqlite_db(base, self.db_selected)
    
        updated_session = SpringDataBase().copy_all_table_data_from_one_session_to_another_session(CtfMicrographTable,
        updated_session, session)

        updated_session = SpringDataBase().copy_all_table_data_from_one_session_to_another_session(CtfFindMicrographTable,
        updated_session, session)

        updated_session = SpringDataBase().copy_all_table_data_from_one_session_to_another_session(CtfTiltMicrographTable,
        updated_session, session)

        updated_session = SpringDataBase().copy_all_table_data_from_one_session_to_another_session(HelixTable,
        updated_session, session)

        updated_session = self.add_filtered_segments(segment_ids, session, updated_session)
        
        updated_session.commit()
        
        updated_session = self.update_records_in_helix(updated_session)
        
        updated_session.commit()
        
        
    def convert_relative_range_to_absolute_range_values(self, pers_length, curvature_range_percent):
        """
        >>> from spring.segment2d.segmentselect import SegmentSelect
        >>> s = SegmentSelect()
        >>> s.convert_relative_range_to_absolute_range_values(np.arange(10), [80, 100])
        (7, 9)
        >>> s.convert_relative_range_to_absolute_range_values(np.arange(10), [0, 20])
        (0, 1)
        >>> s.convert_relative_range_to_absolute_range_values(np.arange(10), [60, 80])
        (5, 7)
        """
        lower_bound, upper_bound = curvature_range_percent
        lower_bound_id = int(len(pers_length) * lower_bound / 100.0 - 0.5)
        upper_bound_id = int(len(pers_length) * upper_bound / 100.0 - 0.5)
        
        sorted_pers_length = np.sort(pers_length)

        curvature_range_vals = (sorted_pers_length[lower_bound_id], sorted_pers_length[upper_bound_id])
        
        return curvature_range_vals


    def convert_curvature_ccc_layer_range(self, spring_db, straightness_selection, curvature_range,
    ccc_layer_selection=None, ccc_layer_range=None):
        session = SpringDataBase().setup_sqlite_db(base, spring_db)
        segments = session.query(SegmentTable).all()
        
        if straightness_selection:
            pers_length = np.array([each_segment.curvature for each_segment in segments])
            curvature_range = self.convert_relative_range_to_absolute_range_values(pers_length, curvature_range)

        if ccc_layer_selection:
            ccc_layer = np.array([each_segment.ccc_layer for each_segment in segments])
            ccc_layer_range = self.convert_relative_range_to_absolute_range_values(ccc_layer, ccc_layer_range)
        
        return curvature_range, ccc_layer_range


    def extract_segments(self):
        self.log.fcttolog()
        shutil.copy(self.spring_db_path, 'spring.db')
        
        self.curvature_range, self.ccc_layer_range = self.convert_curvature_ccc_layer_range('spring.db',
        self.straightness_selection, self.curvature_range_perc, self.ccc_layer_selection, self.ccc_layer_range_perc)
        
        combined_included_segments, excluded_segment_counts = \
        self.filter_non_orientation_parameters_based_on_selection_criteria(self, keep_helices_together=False)
        
        self.log.plog(10)
        if combined_included_segments != []:
            self.write_out_new_database_for_filtered_stack(combined_included_segments)
            self.log.plog(20)
            self.copy_segments_onto_output_stack(combined_included_segments)
            self.log.plog(90)
        else:
            self.log.wlog('No segments passed the selection criteria. No sensible selection possible. Please ' + \
                          'revise criteria.')
            
        self.log.endlog(self.feature_set)
        
def main():
    # Option handling
    parset = SegmentSelectPar()
    
    mergeparset = OptHandler(parset)

    ######## Program
    stack = SegmentSelect(mergeparset)
    stack.extract_segments()

if __name__ == '__main__':
    main()
