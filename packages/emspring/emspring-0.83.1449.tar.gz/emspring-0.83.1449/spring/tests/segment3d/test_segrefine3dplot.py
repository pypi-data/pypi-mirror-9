#!/usr/bin/env python
"""
Test module to check segrefine3dplot
"""
from glob import glob
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment3d.segrefine3dplot import SegRefine3dPlot, SegRefine3dPlotPar
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segmentplot import TestSegmentPlotPrepare
from spring.tests.segment3d.test_segmentrefine3d import TestSegmentRefine3dMain
import os


class TestSegRefine3dPlotPrepare(object):
    def setup_segmentrefine3d(self):
        self.test_segmentrefine3d = TestSegmentRefine3dMain()
        self.test_segmentrefine3d.setup()
        self.test_segmentrefine3d.do_test_case_sr1()
        os.rename('spring.db', os.path.join(os.pardir, 'spring.db'))
        os.rename('refinement006.db', os.path.join(os.pardir, 'refinement.db'))
        

class TestSegRefine3dPlot(TestSegRefine3dPlotPrepare, SegRefine3dPlot):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.setup_segmentrefine3d()
        
        self.feature_set = SegRefine3dPlotPar()
        self.feature_set.parameters['refinement.db file']=os.pardir + os.sep + 'refinement.db'
        self.feature_set.parameters['Diagnostic plot prefix'] = 'test_diagnostic.png'
        self.feature_set.parameters['spring.db file']=os.pardir + os.sep + 'spring.db'
        self.feature_set.parameters['Refinement quantities'] = 'coordinates_subunit'#'in-plane_rotation'#'coordinates'#
        self.feature_set.parameters['Batch mode']=True#False#
        self.feature_set.parameters['Set size']='helix'
        self.feature_set = TestSegmentPlotPrepare().setup_selection_criteria_micrograph_and_helix(self.feature_set)
        
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        
    def teardown(self):
        self.test_segmentrefine3d.teardown()
        os.remove('refinement.db')
        diagnostic_files = glob('test_diagnosti*.png')
        for each_file in diagnostic_files:
            os.remove(each_file)
        
        self.testingdir.remove()
        
        
class TestSegRefine3dPlotMain(TestSegRefine3dPlot):
    def do_test_case_sr3dp1(self):
        self.plot_desired_ref_quantities()
        

class TestSegRefine3dPlotMore(TestSegRefine3dPlot):
    def do_test_case_sr3dp2(self):
        self.feature_set.parameters['Refinement quantities'] = 'in-plane_rotation'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        self.do_case_sr3dp3()
        self.do_case_sr3dp3a()
        self.do_case_sr3dp4()
        self.do_case_sr3dp5()
        self.do_case_sr3dp6()
        self.do_case_sr3dp7()
        self.do_case_sr3dp8()
        self.do_case_sr3dp9()
        self.do_case_sr3dp10()
        self.do_case_sr3dp11()
        self.do_case_sr3dp12()
        self.do_case_sr3dp13()
        self.do_case_sr3dp14()

    def do_case_sr3dp3(self):
        self.feature_set.parameters['Refinement quantities'] = 'normalized_in-plane_rotation'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp3a(self):
        self.feature_set.parameters['Refinement quantities'] = 'out-of-plane_tilt'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp4(self):
        self.feature_set.parameters['Refinement quantities'] = 'phi'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp5(self):
        self.feature_set.parameters['Refinement quantities'] = 'theta'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp6(self):
        self.feature_set.parameters['Refinement quantities'] = 'psi'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp7(self):
        self.feature_set.parameters['Set size'] = 'micrograph'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp8(self):
        self.feature_set.parameters['Set size'] = 'data_set'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp9(self):
        self.feature_set.parameters['Refinement quantities'] = 'x_shift'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp10(self):
        self.feature_set.parameters['Refinement quantities'] = 'y_shift'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp11(self):
        self.feature_set.parameters['Refinement quantities'] = 'shift_perpendicular_to_helix'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp12(self):
        self.feature_set.parameters['Refinement quantities'] = 'shift_along_helix'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp13(self):
        self.feature_set.parameters['Refinement quantities'] = 'ccc_peak'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
    def do_case_sr3dp14(self):
        self.feature_set.parameters['Refinement quantities'] = 'coordinates_subunit'
        super(TestSegRefine3dPlot, self).__init__(self.feature_set)
        
        self.plot_desired_ref_quantities()
        
        
class TestSegRefine3dPlotEndToEnd(TestSegRefine3dPlot):
    def do_end_to_end_test_sp_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
 

    def do_end_to_end_test_sp_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        
    
def main():
    tsr3dp = TestSegRefine3dPlotMain()
    tsr3dp.setup()
    tsr3dp.do_test_case_sr3dp1()
        
if __name__ == '__main__':
    main()
