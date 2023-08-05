#!/usr/bin/env python
"""
Test module to check new alignment module
"""
from EMAN2 import EMData
from fundamentals import rot_shift2D
from glob import glob
from multiprocessing import cpu_count
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment2d.segmentalign2d import SegmentAlign2d, SegmentAlign2dPar
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment2d.test_segmentclass import HelixClassPreparation
import os
import sys


class TestSegmentAlign2dPreparation(HelixClassPreparation):
    def apply_in_plane_rotation_in_degree_steps(self):
        self.helix_segments = EMData.read_images('test_segments.hdf')
        self.applied_rotations = []
        for image_number_on_stack, helix in enumerate(self.helix_segments):
            applied_angle = (-len(self.helix_segments) / 2 + image_number_on_stack) * self.rotation_step
            self.applied_rotations.append(applied_angle)
            helix = rot_shift2D(helix, angle=applied_angle, sx=7.0, sy=-1.2)
#            trans_2d = Transform({'type':'2d', 'alpha':-applied_angle, 'tx':6.0, 'ty':-1.2})
#            helix.set_attr('xform.align2d', trans_2d)
            helix.write_image(self.helix_stack, image_number_on_stack)
        

    def setup_reference_stack(self):
        self.reference = EMData()
        self.reference.read_image('test_segments.hdf', 0)
        self.reference.write_image('test_reference.hdf')
        

    def setup_helix_or_particle_dimension(self):
        self.feature_set.parameters['Estimated helix width and height in Angstrom'] = ((self.width_of_helix_in_angstrom,
        int(1.3 * self.width_of_helix_in_angstrom)))

    def setup_of_common_non_mpi_parameters(self):
        self.width_of_helix_in_angstrom = 500
        self.pixelsize = 5.0
        self.helix_stack = 'test_helix_stack.hdf'
        self.reference_stack = 'test_reference.hdf'
        self.aligned_ref = 'test_avg_ali.hdf'
        self.helix_stack_with_applied_alignment = 'test_helix_stack_aligned.hdf'
        self.align_directory = 'align_directory'
        self.custom_filter_file = 'test_filter_file.dat'
        self.restrain_option = True
        self.delta_in_plane_rotation = 30.0
        self.rotation_step = 2
        self.prepare_helix_projection()
        self.setup_reference_stack()
        micrograph_dimension = self.helix_micrograph.get_xsize()
        self.prepare_custom_filter_file(self.custom_filter_file, micrograph_dimension)
        self.apply_in_plane_rotation_in_degree_steps()
        self.logfile, self.directory = EndToEndTest().define_logfile_and_directory(self.feature_set.progname)
        self.feature_set.logfile = self.logfile
        self.feature_set.parameters['Image input stack'] = self.helix_stack
        self.feature_set.parameters['Image output stack'] = self.helix_stack_with_applied_alignment
        self.feature_set.parameters['Number of iterations'] = 2
        self.feature_set.parameters['Update references']=True
        self.feature_set.parameters['Aligned average stack'] = self.aligned_ref
        self.feature_set.parameters['Reference option'] = True
        self.feature_set.parameters['Image reference stack'] = self.reference_stack
        self.feature_set.parameters['Pixel size in Angstrom'] = self.pixelsize
        self.setup_helix_or_particle_dimension()
        
        self.feature_set.parameters['Internal binning factor']=1
        self.feature_set.parameters['Limit in-plane rotation']=self.restrain_option
        self.feature_set.parameters['Delta in-plane rotation angle'] = self.delta_in_plane_rotation
        self.feature_set.parameters['X and Y translation range in Angstrom'] = (100, 10)
        self.feature_set.parameters['Local refinement'] = True
        self.feature_set.parameters['Absolute X and Y translation limit in Angstrom']= (100, 10)
        
        self.feature_set.parameters['High-pass filter option'] = True
        self.feature_set.parameters['Low-pass filter option'] = True
        self.feature_set.parameters['High and low-pass filter cutoffs in 1/Angstrom'] = (0.01, 0.06)
        self.feature_set.parameters['Custom filter option'] = True
        self.feature_set.parameters['Custom-built filter file'] = self.custom_filter_file
        self.feature_set.parameters['Automatic filter option'] = True
        self.feature_set.parameters['B-Factor']=-2000
        self.feature_set.parameters['Temporary directory']=os.path.abspath(os.curdir)

    def teardown_segmentalign2d(self):
        pass
        os.remove('test_segments.hdf')
        os.remove(self.helix_stack)
        os.remove('test_reference.hdf')
        os.remove(self.custom_filter_file)
        os.remove(self.helix_stack_with_applied_alignment)
        if self.update_references:
            os.remove(self.aligned_ref)
            os.remove('{0}_var{1}'.format(os.path.splitext(self.aligned_ref)[0], os.path.splitext(self.aligned_ref)[-1]))
        
            add_files = glob('aqm*hdf') + glob('drm*dat') 
            for each_file in add_files:
                os.remove(each_file)

class TestSegmentAlign2d(TestSegmentAlign2dPreparation, SegmentAlign2d, EndToEndTest):

    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = SegmentAlign2dPar()
        
        self.setup_of_common_non_mpi_parameters()
        self.feature_set.parameters['MPI option'] = False
        
        super(TestSegmentAlign2d, self).__init__(self.feature_set)
        

    def check_rotation(self, helix_stack, applied_rotations, delta_in_plane_rotation, rotation_step,
    restrain_inplane_rotation):
        helix_stack_aligned = EMData.read_images(helix_stack)
        for image_number_on_stack, helix in enumerate(helix_stack_aligned):
            alignment = helix.get_attr('xform.align2d')
            rotation_angle = alignment.get_params('2D')['alpha']
            translation_x = alignment.get_params('2D')['tx']
            translation_y = alignment.get_params('2D')['ty']
            
            applied_rotation_angle = -applied_rotations[image_number_on_stack]
            
            sys.stderr.write('\n{0}={1}; {2}, {3}'.format(rotation_angle %180, applied_rotation_angle %180,
            translation_x, translation_y))
            
            assert 360 != float(applied_rotation_angle) %360 


    def teardown(self):
        self.teardown_segmentalign2d()
 
        self.testingdir.remove()


class TestSegmentAlign2dMain(TestSegmentAlign2d):
    def do_test_case_sa1(self):

        self.perform_segmentalign2d()

        self.check_rotation(self.helix_stack, self.applied_rotations, self.delta_in_plane_rotation, self.rotation_step,
        self.restrain_option)
        
class TestSegmentAlign2dMore(TestSegmentAlign2d):
    def do_test_case_sa2(self):
        """
        * Single-CPU segmentalign test without reference and local refinement option
        """
        self.restrain_option=False
        self.feature_set.parameters['Limit in-plane rotation']=self.restrain_option
        self.feature_set.parameters['Reference option']= False
        self.feature_set.parameters['Local refinement'] = True
         
        super(TestSegmentAlign2d, self).__init__(self.feature_set)
         
        self.perform_segmentalign2d()
 
        self.check_rotation(self.helix_stack, self.applied_rotations, self.delta_in_plane_rotation, self.rotation_step,
        self.restrain_option)
         

    def do_test_case_sa3(self):
        """
        * Single-CPU segmentalign2d test without update option
        """
        self.feature_set.parameters['Update references']=False
        
        super(TestSegmentAlign2d, self).__init__(self.feature_set)
        
        self.perform_segmentalign2d()


class TestSegmentAlign2dEndToEnd(TestSegmentAlign2d):
    def do_end_to_end_test_sa_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
 
    def do_end_to_end_test_sa_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        
class TestSegmentAlign2dMpi(TestSegmentAlign2d):
    def do_end_to_end_test_sa_inputfile_with_MPI(self):
        """
        * Standard Multi-CPU segmentalign2d run
        """
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)


    def do_end_to_end_test_sa_inputfile_with_MPI_2(self):
        """
        * Multi-CPU segmentalign2d run without reference (use average as starting reference)
        """
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Reference option']= False
        self.feature_set.parameters['Local refinement'] = True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
        
        
    def do_end_to_end_test_sa_inputfile_with_MPI_3(self):
        """
        * Standard Multi-CPU segmentalign2d run
        """
        self.update_references = False
        self.feature_set.parameters['Update references']=self.update_references
        self.feature_set.parameters['MPI option'] = True
        self.feature_set.parameters['Number of CPUs']=min(8, cpu_count())
        
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)


def main():
    talign = TestSegmentAlign2dMain()
    talign.setup()
    talign.do_test_case_sa1()
        
if __name__ == '__main__':
    main()
