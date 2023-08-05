#!/usr/bin/env python
"""
Test module to check segmentselect
"""
from EMAN2 import EMUtil
from spring.csinfrastr.csdatabase import SpringDataBase, base, SegmentTable
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment2d.segmentselect import SegmentSelectPar, SegmentSelect
from spring.tests.segment3d.test_segmentrefine3d import TestSegmentRefine3dSetupForOthers
import os
import sys


class TestSegmentSelectPreparation(object):
    def setup_segmentrefine3d(self):
        self.tsr3d = TestSegmentRefine3dSetupForOthers()
        self.tsr3d.setup_sr3d()


    def check_filtered_values_in_or_outside_range(self, each_value, value_range, in_or_exclude):
        if in_or_exclude == 'include':
            sys.stderr.write('\n:{0} <= {1} <= {2}'.format(min(value_range), each_value, max(value_range)))
            assert min(value_range) <= each_value <= max(value_range)
        if in_or_exclude == 'exclude':
            sys.stderr.write('\n{1} < {0}\n{1} > {2}'.format(min(value_range), each_value, max(value_range)))
            assert each_value < min(value_range) or each_value > max(value_range)


    def check_values_in_filtered_database(self):
        self.session = SpringDataBase().setup_sqlite_db(base, self.test_database)
        segments = self.session.query(SegmentTable).all()
        
        for each_segment in segments:
            defocus_range = ((self.feature_set.parameters['Defocus range']))
            defocus_in_or_exclude = self.feature_set.parameters['Include or exclude defocus range']
            
            self.check_filtered_values_in_or_outside_range(each_segment.avg_defocus, defocus_range,
            defocus_in_or_exclude)
            
            sys.stderr.write('\nSelected defoci checked. ok')
            
            astigmatism_range = ((self.feature_set.parameters['Astigmatism range']))
            astigmatism_in_or_exclude = self.feature_set.parameters['Include or exclude astigmatic segments']
            
            self.check_filtered_values_in_or_outside_range(each_segment.astigmatism, astigmatism_range,
            astigmatism_in_or_exclude)
            
            sys.stderr.write('\nSelected astigmatism checked. ok')
    
#             curvature_range = ((self.feature_set.parameters['Persistence length range']))
#             curvature_in_or_exclude = self.feature_set.parameters['Include or exclude straight helices']
#             
#             self.check_filtered_values_in_or_outside_range(each_segment.curvature, curvature_range,
#             curvature_in_or_exclude)
#             
#             sys.stderr.write('\nSelected straightness checked. ok')
#             
#             layer_cc_range = ((self.feature_set.parameters['Correlation layer line range']))
#             
#             layer_cc_in_or_exclude = self.feature_set.parameters['Include or exclude segments based on layer-line ' + \
#             'correlation']
#             
#             self.check_filtered_values_in_or_outside_range(each_segment.ccc_layer, layer_cc_range,
#             layer_cc_in_or_exclude)
#             
#             sys.stderr.write('\nSelected layer-line correlation checked. ok')
            
    def check_number_of_images_on_output_stack(self):
        assert EMUtil.get_image_count(self.test_selected_stack) == self.session.query(SegmentTable).count()
        
    def check_results(self):
        self.check_values_in_filtered_database()
        self.check_number_of_images_on_output_stack()
        
    
    def prepare_segment_file(self):
        sfile = open(self.test_segment_file, 'w')
        
        stack_ids = ['{0}\n'.format(each_stack_id) for each_stack_id in list(range(5)) + list(range(10, 55))]
        sfile.writelines(stack_ids)
        sfile.close()

        
    def setup_selection_criteria_from_segment_table(self, feature_set):
        feature_set.parameters['Segments select option'] = True
        feature_set.parameters['Include or exclude segments'] = 'include'
        feature_set.parameters['Segment file'] = self.test_segment_file
        
        feature_set.parameters['Micrographs select option'] = True
        feature_set.parameters['Include or exclude micrographs'] = 'include'
        feature_set.parameters['Micrographs list'] = '1'
        
        feature_set.parameters['Helices select option'] = True
        feature_set.parameters['Include or exclude helices'] = 'include'
        feature_set.parameters['Helices list'] = '1,2'
        
        feature_set.parameters['Classes select option'] = True
        feature_set.parameters['Include or exclude classes'] = 'include'
        feature_set.parameters['Class type']='class_id'
        feature_set.parameters['Classes list'] = '0, 1, 2'
        
        feature_set.parameters['Persistence class option'] = True
        feature_set.parameters['Persistence class length in Angstrom'] = 700
        feature_set.parameters['Class occupancy threshold']=0.5

        feature_set.parameters['Straightness select option'] = True
        feature_set.parameters['Include or exclude straight helices'] = 'include'
        feature_set.parameters['Persistence length range'] = (0, 80)
        
        feature_set.parameters['Defocus select option'] = True
        feature_set.parameters['Include or exclude defocus range'] = 'include'
        feature_set.parameters['Defocus range'] = (0, 23000)
        
        feature_set.parameters['Astigmatism select option'] = True
        feature_set.parameters['Include or exclude astigmatic segments'] = 'include'
        feature_set.parameters['Astigmatism range'] = (0, 10000)
        
        feature_set.parameters['Layer line correlation select option'] = True
        feature_set.parameters['Include or exclude segments based on layer-line correlation'] = 'include'
        feature_set.parameters['Correlation layer line range']=((0, 80))
        
        return feature_set
    
    
class TestSegmentSelect(TestSegmentSelectPreparation, SegmentSelect, SegmentSelectPar):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.setup_segmentrefine3d()
        self.feature_set = SegmentSelectPar()
        
        self.test_stack = self.tsr3d.input_stack
        self.test_selected_stack = 'test_selected.hdf'
        self.test_database = 'test_selected.db'
        self.test_segment_file = 'test_segment_file.dat'

        self.prepare_segment_file()
        self.feature_set.parameters['Image input stack']=self.test_stack
        self.feature_set.parameters['Image output stack']=self.test_selected_stack
        
        self.feature_set.parameters['spring.db file']=os.path.join(os.pardir, 'spring.db')
        self.feature_set.parameters['Selected database']=self.test_database
            
        self.feature_set = self.setup_selection_criteria_from_segment_table(self.feature_set)

        super(TestSegmentSelect, self).__init__(self.feature_set)
        

    def teardown(self):
        database_file = 'spring.db'
        os.remove(database_file)
        os.remove(os.path.join(os.pardir, database_file))
        os.remove(self.test_database)
        os.remove(self.test_segment_file)
        
        os.remove(self.test_stack)
        os.remove(self.test_selected_stack)

        self.testingdir.remove()


class TestSegmentSelectMain(TestSegmentSelect):
    def do_test_case_scex1(self):
        self.extract_segments()
        self.check_results()


# class TestSegmentSelectEndToEnd(TestSegmentSelect):
#     def do_end_to_end_test_scex_inputfile(self):
#         EndToEndTest().do_end_to_end_inputfile(self.feature_set)
#         self.check_results()
#         
# 
#     def do_end_to_end_test_scex_prompt(self):
#         EndToEndTest().do_end_to_end_prompt(self.feature_set)
#         self.check_results()
        

class TestSegmentSelectMore(TestSegmentSelect):
    def do_test_case_scex2(self):
        self.feature_set.parameters['Include or exclude defocus range'] = 'exclude'
        self.feature_set.parameters['Defocus range'] = (0, 12000)
        self.feature_set.parameters['Include or exclude segments based on layer-line correlation'] = 'exclude'
        self.feature_set.parameters['Correlation layer line range']=((0.1, 0.4))
        
        self.feature_set.parameters['Include or exclude straight helices'] = 'exclude'
        self.feature_set.parameters['Include or exclude classes'] = 'exclude'
        self.feature_set.parameters['Class type']='class_model_id'
        self.feature_set.parameters['Classes list'] = '0'
        
        super(TestSegmentSelect, self).__init__(self.feature_set)
        self.extract_segments()
        self.check_results()
    
def main():
    tscex = TestSegmentSelectMain()
    tscex.setup()
    tscex.do_test_case_scex1()
        
if __name__ == '__main__':
    main()
