#!/usr/bin/env python
"""
Test module to check segmentplot
"""
from glob import glob
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment2d.segmentplot import SegmentPlot, SegmentPlotPar
from spring.segment3d.refine.sr3d_main import SegmentRefine3d
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segmentselect import TestSegmentSelect
from spring.tests.segment3d.test_segmentrefine3d import TestSegmentRefine3d
import numpy as np
import os


class TestSegmentPlotPrepare(object):
    def generate_input_database_from_helix(self):
        self.azimuthal_step = 20
        self.out_of_plane_range = [-8, 8]
        self.out_of_plane_step = 8
        self.helical_rotation = 50.0
        self.helix_start = 1
        
        self.euler_list = SegmentRefine3d().generate_Euler_angles_for_projection(self.azimuthal_step,
        self.out_of_plane_range, self.out_of_plane_step, self.helical_rotation)
        
        self.perturbed_alignment_parameters = \
        TestSegmentRefine3d().apply_random_rotations_x_and_y_shifts_to_projection_parameters(self.euler_list, 30)
        
        coord = np.arange(len(self.perturbed_alignment_parameters)) * 100.0
        coordinates = ((coord, coord))
        TestSegmentRefine3d().prepare_database_for_refinement(self.perturbed_alignment_parameters, 5.0, coordinates)
        

    def setup_selection_criteria_micrograph_and_helix(self, feature_set):
        feature_set.parameters['Micrographs select option'] = False
        feature_set.parameters['Include or exclude micrographs'] = 'include'
        feature_set.parameters['Micrographs list'] = '1'
        
        feature_set.parameters['Helices select option'] = False
        feature_set.parameters['Include or exclude helices'] = 'include'
        feature_set.parameters['Helices list'] = '1'
    
        return feature_set
        

class TestSegmentPlot(TestSegmentPlotPrepare, SegmentPlot):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = SegmentPlotPar()
        self.feature_set.parameters['spring.db file']=os.pardir + os.sep + 'spring.db'
        self.feature_set.parameters['Diagnostic plot prefix'] = 'test_diagnostic.png'
        self.feature_set.parameters['Quantities'] = 'in-plane_rotation'#
        self.feature_set.parameters['Batch mode']=True#False
        self.feature_set.parameters['Set size']='helix'

        self.tsegsel = TestSegmentSelect()
        self.tsegsel.test_segment_file = 'test_segment_file.dat'
        self.feature_set = self.tsegsel.setup_selection_criteria_from_segment_table(self.feature_set)
        self.tsegsel.prepare_segment_file()
        
        self.generate_input_database_from_helix()
        
        super(TestSegmentPlot, self).__init__(self.feature_set)
        
        
    def teardown(self):
        os.remove('spring.db')
        os.remove(os.pardir + os.sep + 'spring.db')
        diagnostic_file = glob('test_diagnosti*.png')
        if self.batch_mode and diagnostic_file != []:
            os.remove(diagnostic_file[0])
        
        self.testingdir.remove()

        
class TestSegmentPlotMain(TestSegmentPlot):
    def do_test_case_sp1(self):
        self.plot_desired_quantities()
        

class TestSegmentPlotMore(TestSegmentPlot):
    def do_test_case_sp2(self):
        self.feature_set.parameters['Quantities'] = 'coordinates'#'in-plane_rotation'
        super(TestSegmentPlot, self).__init__(self.feature_set)
        
        self.plot_desired_quantities()
        
        
    def do_test_case_sp3(self):
        self.feature_set.parameters['Quantities'] = 'curvature'
        super(TestSegmentPlot, self).__init__(self.feature_set)
        
        self.plot_desired_quantities()
        
        
    def do_test_case_sp4(self):
        self.feature_set.parameters['Quantities'] = 'defocus'
        super(TestSegmentPlot, self).__init__(self.feature_set)
        
        self.plot_desired_quantities()
        
        
    def do_test_case_sp5(self):
        self.feature_set.parameters['Quantities'] = 'astigmatism'
        super(TestSegmentPlot, self).__init__(self.feature_set)
        
        self.plot_desired_quantities()
        
        
    def do_test_case_sp6(self):
        self.feature_set.parameters['Quantities'] = 'layer-line correlation'
        super(TestSegmentPlot, self).__init__(self.feature_set)
        
        self.plot_desired_quantities()
        
        
    def do_test_case_sp7(self):
        self.feature_set.parameters['Quantities'] = 'classes'
        super(TestSegmentPlot, self).__init__(self.feature_set)
        
        self.plot_desired_quantities()
        
        
    def do_test_case_sp8(self):
        self.feature_set.parameters['Set size'] = 'micrograph'
        super(TestSegmentPlot, self).__init__(self.feature_set)
         
        self.plot_desired_quantities()
        
        
    def do_test_case_sp9(self):
        self.feature_set.parameters['Set size'] = 'data_set'
        super(TestSegmentPlot, self).__init__(self.feature_set)
        
        self.plot_desired_quantities()
        
        
    def do_test_case_sp10(self):
        self.feature_set.parameters['Quantities'] = 'class_models'
        super(TestSegmentPlot, self).__init__(self.feature_set)
        
        self.plot_desired_quantities()


class TestSegmentPlotEndToEnd(TestSegmentPlot):
    def do_end_to_end_test_sp_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
 

    def do_end_to_end_test_sp_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        
    
def main():
    tsp = TestSegmentPlotMain()
    tsp.setup()
    tsp.do_test_case_sp1()
        
if __name__ == '__main__':
    main()
