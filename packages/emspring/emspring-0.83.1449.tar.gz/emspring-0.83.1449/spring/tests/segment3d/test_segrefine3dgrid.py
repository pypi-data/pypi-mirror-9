#!/usr/bin/env python
"""
Test module to check segrefine3dgrid
"""
from glob import glob
from multiprocessing import cpu_count
import os
import shutil
from spring.csinfrastr.csdatabase import SpringDataBase, grid_base, GridRefineTable
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment3d.segrefine3dgrid import SegRefine3dGridPar, SegRefine3dGrid
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment3d.test_segmentrefine3d import TestSegmentRefine3dSetup, TestSegmentRefine3dMain


class TestSegRefine3dGridSetup(TestSegmentRefine3dSetup):
    def prepare_grid_database_to_be_continued(self):
        
        grid_session = SpringDataBase().setup_sqlite_db(grid_base, self.grid_db)
        this_grid, first, second = SegRefine3dGrid().enter_variables_into_grid_database(self.prim_var, self.sec_var, 
        self.prim_range, self.sec_range, self.prim_inc, self.sec_inc, 'rise/rotation')
        
        grid_session.add(this_grid)
        
        grid_cycle = GridRefineTable()
        
        grid_cycle.dirname = 'helical_rise_or_pitch_8_helical_rotation_or_number_of_units_per_turn_40'
        grid_cycle.primary_value = 8.0
        grid_cycle.secondary_value = 40.0
        
        grid_cycle.fsc_0143 = 12.0
        grid_cycle.fsc_05 = 18.0
        grid_cycle.amp_correlation = 0.7
        grid_cycle.variance = 0.3
        grid_cycle.xshift_error = 12.5
        grid_cycle.inplane_error = 2.0
        grid_cycle.outofplane_error = 5.0
        grid_cycle.excluded_inplane_ratio = 0.1
        grid_cycle.em_files_2d = ['this_file.hdf']
        grid_cycle.em_files_3d = ['that_file.hdf']
        grid_session.add(grid_cycle)
        
        grid_session.commit()
        
        
    def setup_of_common_sr3dg_non_mpi_parameters(self):
        self.feature_set = SegRefine3dGridPar()
        self.input_stack = 'test_stack.hdf'
        self.prim_var = 'helical_rise_or_pitch'
        self.sec_var = 'helical_rotation_or_number_of_units_per_turn'
        self.grid_db = os.path.join(os.pardir, 'grid.db')
        self.prim_range = ((8.0, 12.0))
        self.sec_range = ((40.0, 60.0))
        self.prim_inc = 2.0
        self.sec_inc = 10.0
        
        self.feature_set.parameters['First parameter']=self.prim_var
        self.feature_set.parameters['Second parameter']=self.sec_var
        self.feature_set.parameters['Lower and upper limit first parameter']=self.prim_range
        self.feature_set.parameters['Lower and upper limit second parameter']=self.sec_range
        self.feature_set.parameters['First and second parameter increment']=((self.prim_inc, self.sec_inc))
        self.feature_set.parameters['Subgrid option']=False
        self.feature_set.parameters['Part and number of subgrids']=(3, 3)
        self.feature_set.parameters['Grid continue option']=False
        self.feature_set.parameters['Grid database']=self.grid_db
        self.setup_main_segmentrefine3d_parameters()
        
class TestSegRefine3dGrid(TestSegRefine3dGridSetup, SegRefine3dGrid):
    def setup_srg3d(self):
        self.setup_of_common_sr3dg_non_mpi_parameters()
        self.feature_set.parameters['MPI option']=False
        self.feature_set.parameters['Number of CPUs']=min(3, cpu_count())
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)
        
        self.prepare_apolar_helix = False
        self.generate_input_stack_from_helix()
        
        super(TestSegRefine3dGridSetup, self).__init__(self.feature_set)
        
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()
        
        self.setup_srg3d()

    def teardown(self):
        parfiles = glob('*par')
        logfiles = glob('*log')
        directory = 'helical_rise_or_pitch'
        dirfiles = glob('{dir}*{sep}*'.format(dir=directory, sep=os.sep))
        for each_file in logfiles + parfiles + dirfiles:
            os.remove(each_file)
        for each_dir in glob('{0}*'.format(directory)):
            shutil.rmtree(each_dir)
           
        os.remove(self.input_stack)
        os.remove(os.path.join(os.path.pardir, 'spring.db'))
        for each_file in glob('gri*.db'):
            os.remove(each_file)
         
        if self.feature_set.parameters['Continue refinement option'] is True:
            self.tsr3d.testingdir.remove()
        self.testingdir.remove()
            
        
class TestSegRefine3dGridMain(TestSegRefine3dGrid):
    def do_test_case_srg1(self):
        """
        Test standard Segrefine3dgrid 
        """
        self.launch_segmentrefine3d_jobs()


class TestSegRefine3dGridMore(TestSegRefine3dGrid):
    def to_test_case_srg2(self):
        """
        Test Segrefine3dgrid using subgrid option
        """
        self.feature_set.parameters['Subgrid option']=True
          
        super(TestSegRefine3dGridSetup, self).__init__(self.feature_set)
        self.launch_segmentrefine3d_jobs()
         
         
    def to_test_case_srg3(self):
        """
        Test Segrefine3dgrid using continue grid option
        """
        self.feature_set.parameters['Subgrid option']=False
        self.feature_set.parameters['Grid continue option']=True
          
        self.prepare_grid_database_to_be_continued()
          
        super(TestSegRefine3dGridSetup, self).__init__(self.feature_set)
          
        self.launch_segmentrefine3d_jobs()
        os.remove(self.grid_db)
          
          
    def to_test_case_srg4(self):
        """
        Test Segrefine3dgrid using continue refinement option
        """
        self.feature_set.parameters['Continue refinement option']=True
        self.feature_set.parameters['refinement.db file']='refinement006.db'
        self.feature_set.parameters['Number of iterations']=3
        os.remove(os.path.join(os.pardir, 'spring.db'))
         
        super(TestSegRefine3dGridSetup, self).__init__(self.feature_set)
        self.tsr3d = TestSegmentRefine3dMain()
        self.tsr3d.setup()
        self.tsr3d.do_test_case_sr1()
         
        self.launch_segmentrefine3d_jobs()
        self.tsr3d.clean_files_from_iterations()
        
          
    def to_test_case_srg5(self):
        """
        Test Segrefine3dgrid using swapped primary and secondary variables
        """
        self.feature_set.parameters['First parameter']=self.sec_var
        self.feature_set.parameters['Second parameter']=self.prim_var
        self.feature_set.parameters['Lower and upper limit first parameter']=self.sec_range
        self.feature_set.parameters['Lower and upper limit second parameter']=self.prim_range
        self.feature_set.parameters['First and second parameter increment']=((self.sec_inc, self.prim_inc))
 
        super(TestSegRefine3dGridSetup, self).__init__(self.feature_set)
        self.launch_segmentrefine3d_jobs()
         

class TestSegRefine3dGridEndToEnd(TestSegRefine3dGrid):
    def do_end_to_end_test_sr3d_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
 

    def do_end_to_end_test_sr3d_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        
        
def main():
    tsr3d = TestSegRefine3dGridMain()
    tsr3d.setup()
    tsr3d.do_test_case_srg1()
        
if __name__ == '__main__':
    main()
