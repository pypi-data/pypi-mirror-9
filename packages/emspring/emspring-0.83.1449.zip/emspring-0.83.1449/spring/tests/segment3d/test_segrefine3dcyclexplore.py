#!/usr/bin/env python
"""
Test module to check Segrefine3dcyclexplore
"""
from glob import glob
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment3d.segrefine3dcyclexplore import SegRefine3dCycleExplorePar, SegRefine3dCycleExplore
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment3d.test_segmentrefine3d import TestSegmentRefine3dMain
import os


class TestSegRefine3dCycleExplorePrepare(object):
    def setup_segmentrefine3d(self):
        self.test_segmentrefine3d = TestSegmentRefine3dMain()
        self.test_segmentrefine3d.setup()
        self.test_segmentrefine3d.do_test_case_sr1()
        os.rename('refinement006.db', os.pardir + os.sep + 'refinement.db')
        

class TestSegRefine3dCycleExplore(TestSegRefine3dCycleExplorePrepare, SegRefine3dCycleExplore):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.setup_segmentrefine3d()
        
        self.feature_set = SegRefine3dCycleExplorePar()
        self.feature_set.parameters['refinement.db file']=os.pardir + os.sep + 'refinement.db'
        self.feature_set.parameters['Diagnostic plot prefix'] = 'test_diagnostic.png'
        self.feature_set.parameters['Criterion'] = 'excluded_out_of_plane_tilt_count'
        self.feature_set.parameters['Batch mode']=True#
        
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        
    def teardown(self):
        self.test_segmentrefine3d.teardown()
        os.remove('refinement.db')
        diagnostic_files = glob('test_diagnosti*.png')
        for each_file in diagnostic_files:
            os.remove(each_file)
        
        self.testingdir.remove()
        
        
class TestSegRefine3dCycleExploreMain(TestSegRefine3dCycleExplore):
    def do_test_case_sr3dce1(self):
        self.plot_refinement_criteria_per_cycle()
        

class TestSegRefine3dCycleExploreMore(TestSegRefine3dCycleExplore):
    def do_test_case_sr3dce2(self):
        self.feature_set.parameters['Criterion'] = 'excluded_out_of_plane_tilt_count'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        self.do_case_sr3dce3()
        self.do_case_sr3dce3a()
        self.do_case_sr3dce4()
        self.do_case_sr3dce5()
        self.do_case_sr3dce6()
        self.do_case_sr3dce7()
        self.do_case_sr3dce8()
        self.do_case_sr3dce9()
        self.do_case_sr3dce10()
        self.do_case_sr3dce11()
        self.do_case_sr3dce12()
        self.do_case_sr3dce13()
        self.do_case_sr3dce14()

    def do_case_sr3dce3(self):
        self.feature_set.parameters['Criterion'] = 'excluded_inplane_count'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce3a(self):
        self.feature_set.parameters['Criterion'] = 'total_excluded_count'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce4(self):
        self.feature_set.parameters['Criterion'] = 'fsc_0143'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce5(self):
        self.feature_set.parameters['Criterion'] = 'fsc_05'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce6(self):
        self.feature_set.parameters['Criterion'] = 'xshift_error'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce7(self):
        self.feature_set.parameters['Criterion'] = 'mean_peak'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce8(self):
        self.feature_set.parameters['Criterion'] = 'amp_corr_quarter_nyquist'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce9(self):
        self.feature_set.parameters['Criterion'] = 'amp_corr_half_nyquist'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce10(self):
        self.feature_set.parameters['Criterion'] = 'amp_corr_3quarter_nyquist'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce11(self):
        self.feature_set.parameters['Criterion'] = 'amp_correlation'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce12(self):
        self.feature_set.parameters['Criterion'] = 'helical_ccc_error'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce13(self):
        self.feature_set.parameters['Criterion'] = 'mean_helical_ccc'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce14(self):
        self.feature_set.parameters['Criterion'] = 'variance'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce15(self):
        self.feature_set.parameters['Criterion'] = 'inplane_error'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
    def do_case_sr3dce16(self):
        self.feature_set.parameters['Criterion'] = 'outofplane_error'
        super(TestSegRefine3dCycleExplore, self).__init__(self.feature_set)
        
        self.plot_refinement_criteria_per_cycle()
        
        
class TestSegRefine3dCycleExploreEndToEnd(TestSegRefine3dCycleExplore):
    def do_end_to_end_test_sp_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
 

    def do_end_to_end_test_sp_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        
    
def main():
    tsr3dp = TestSegRefine3dCycleExploreMain()
    tsr3dp.setup()
    tsr3dp.do_test_case_sr3dce1()
        
if __name__ == '__main__':
    main()
