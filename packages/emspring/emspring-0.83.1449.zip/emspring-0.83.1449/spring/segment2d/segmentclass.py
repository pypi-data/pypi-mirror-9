# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to classify excised in-plane rotated segments using SPARX's k-means clustering
"""
from EMAN2 import Analyzers, EMData, EMUtil, Util
from collections import OrderedDict, namedtuple
from fundamentals import rot_shift2D
from spring.csinfrastr.csdatabase import SpringDataBase, base, SegmentTable
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import OpenMpi, Support
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segment import Segment
from spring.segment2d.segmentalign2d import SegmentAlign2dPar
from spring.segment2d.segmentexam import SegmentExam
from tabulate import tabulate
from utilities import model_blank
import numpy as np
import os
import shutil


class SegmentClassPar(SegmentAlign2dPar):
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'segmentclass'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.class_features = Features()
        self.feature_set = self.class_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    

    def add_mask_dimension_to_features(self):
        self.feature_set = self.class_features.set_helix_width_and_height(self.feature_set)
        

    def define_parameters_and_their_properties(self):
        self.feature_set = self.class_features.set_inp_stack(self.feature_set)
        self.feature_set = self.set_class_avg_out_stack(self.feature_set)
        
        self.feature_set = self.class_features.set_reference_option(self.feature_set)
        self.feature_set.relatives['Image reference stack'] = 'Reference image option'
        self.feature_set = self.class_features.set_image_reference_stack(self.feature_set, 'intermediate')
        self.feature_set = self.class_features.set_spring_db_option(self.feature_set, 'intermediate', False)
        self.feature_set = self.set_spring_db_prep_rec(self.feature_set)
        self.feature_set = self.class_features.set_spring_path(self.feature_set)

        self.feature_set = self.set_class_var_out_stack(self.feature_set)
        self.feature_set = self.set_eigenimg_out_stack(self.feature_set)
        self.feature_set = self.class_features.set_pixelsize(self.feature_set)
        
        self.add_mask_dimension_to_features()

        self.feature_set = self.set_class_count(self.feature_set)
        self.feature_set = self.set_iteration_count(self.feature_set)
        self.feature_set = self.set_keep_intermediate_files_option(self.feature_set)
        
        self.feature_set = self.class_features.set_alignment_rotation_and_translation(self.feature_set)
        
        self.feature_set = self.class_features.set_filter_options(self.feature_set)
        self.feature_set = self.set_frc_based_filter_option(self.feature_set)
        self.feature_set = self.class_features.set_binning_option(self.feature_set, default=True)
        self.feature_set = self.class_features.set_binning_factor(self.feature_set, binfactor=6, image='segments')
        self.feature_set = self.class_features.set_mpi(self.feature_set)
        self.feature_set = self.class_features.set_ncpus(self.feature_set)
        self.feature_set = self.class_features.set_temppath(self.feature_set)


    def define_program_states(self):
        self.feature_set.program_states['classify']='Classification of segments'
        self.feature_set.program_states['sx_kmeans']='K-means classification of segments'
        self.feature_set.program_states['spring_align2d']='Multi-reference alignment against obtained classes'
        self.feature_set.program_states['compute_eigenimages_from_aligned_stack']='Compute Eigenimages from aligned ' +\
        'stack'


    def set_class_avg_out_stack(self, feature_set):
        inp1 = 'Class average stack'
        feature_set.parameters[inp1] = 'averages.hdf'
        feature_set.properties[inp1] = feature_set.file_properties(1, ['spi', 'hdf', 'img', 'hed'], 'saveFile')
        
        feature_set.hints[inp1] = 'Stack: accepted image file formats ({0})'.\
        format(', '.join(feature_set.properties[inp1].ext))
        
        feature_set.level[inp1]='beginner'
        
        return feature_set


    def set_class_var_out_stack(self, feature_set):
        inp2 = 'Class variance stack'
        feature_set.parameters[inp2] = 'variances.hdf'
        feature_set.properties[inp2] = feature_set.file_properties(1, ['spi', 'hdf', 'img', 'hed'], 'saveFile')
        feature_set.hints[inp2] = 'Stack: accepted image file formats ({0})'.\
        format(', '.join(feature_set.properties[inp2].ext))
        
        feature_set.level[inp2]='expert'
        
        return feature_set


    def set_eigenimg_out_stack(self, feature_set):
        inp3 = 'Eigenimage stack'
        feature_set.parameters[inp3] = 'eigenimages.hdf'
        feature_set.properties[inp3] = feature_set.file_properties(1, ['spi', 'hdf', 'img', 'hed'], 'saveFile')
        feature_set.hints[inp3] = 'Stack: accepted image file formats ({0})'.\
        format(', '.join(feature_set.properties[inp3].ext))
        
        feature_set.level[inp3]='expert'
        
        return feature_set


    def set_class_count(self, feature_set):
        inp7 = 'Number of classes'
        feature_set.parameters[inp7] = int(5)
        feature_set.hints[inp7] = 'Number of classes to be clustered'
        feature_set.properties[inp7] = feature_set.Range(0, 2000, 1)
        feature_set.level[inp7]='beginner'
        
        return feature_set
    
    
    def set_iteration_count(self, feature_set):
        inp7 = 'Number of iterations'
        feature_set.parameters[inp7] = int(5)
        feature_set.hints[inp7] = 'Number of iteration cycles of clustering and alignment: 0 - only k-means ' + \
        'clustering, 1 - cluster and align, 2 - cluster/align/cluster/align... .'
        feature_set.properties[inp7] = feature_set.Range(0, 200, 1)
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    

    def set_keep_intermediate_files_option(self, feature_set):
        inp15 = 'Keep intermediate files'
        feature_set.parameters[inp15]=bool(False)
        feature_set.hints[inp15]='Keep intermediate images from alignment ' + \
        'which are iteratively generated - EM image stacks are deleted otherwise.'
        
        feature_set.level[inp15]='intermediate'
        
        return feature_set
    
    
    def set_spring_db_prep_rec(self, feature_set):
        inp6 = 'Database prepare option'
        feature_set.parameters[inp6] = bool(True)
        feature_set.hints[inp6] = 'If checked will prepare database entries for 3D refinement using convolved images.'
        feature_set.level[inp6]='expert'
        feature_set.relatives[inp6]='Spring database option'
        
        return feature_set

    
class SegmentClassPreparation(object):
    """
    * Class that holds functions for examining segments from micrographs

    * __init__ Function to interpret multi-input parameters

    """

    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            self.p = self.feature_set.parameters

            self.infilestack = self.p['Image input stack']
            self.infile = self.p['Image input stack']
            self.output_avgstack = self.p['Class average stack']
            self.spring_db_option = self.p['Spring database option']
            self.spring_db_prepare = self.p['Database prepare option']
            self.spring_path = self.p['spring.db file']
            
            self.reference_option = self.p['Reference image option']
            self.reference_stack = self.p['Image reference stack']
            self.output_varstack = self.p['Class variance stack']
            self.eigenstack = self.p['Eigenimage stack']
#            self.center_option = self.p['Center option']
            self.pixelsize_ori = self.p['Pixel size in Angstrom']
            self.noclasses = self.p['Number of classes']
            self.iteration_count = self.p['Number of iterations']
            self.keep_intermediate_files = self.p['Keep intermediate files']
            
            self.restrain_inplane_rotation = self.p['Limit in-plane rotation']
            self.delta_psi = self.p['Delta in-plane rotation angle']
            self.x_range_in_angstrom = self.p['X and Y translation range in Angstrom'][0]
            self.y_range_in_angstrom = self.p['X and Y translation range in Angstrom'][1]
            
            self.setup_segmentalign_filter()
            self.mpi_option = self.p['MPI option']
            self.ncpus = self.p['Number of CPUs']
            self.temppath = self.p['Temporary directory']

            self.binoption=self.p['Binning option']
            self.binfactor=self.p['Binning factor']
            if self.binfactor == 1 and self.binoption is True:
                self.binoption = False

            self.define_helix_or_particle_dimensions()


    def setup_segmentalign_filter(self):
        self.high_pass_filter_option = self.p['High-pass filter option']
        self.low_pass_filter_option = self.p['Low-pass filter option']
        self.high_pass_filter_cutoff = self.p['High and low-pass filter cutoffs in 1/Angstrom'][0]
        self.low_pass_filter_cutoff = self.p['High and low-pass filter cutoffs in 1/Angstrom'][1]
        self.custom_filter_option = self.p['Custom filter option']
        self.custom_filter_file = self.p['Custom-built filter file']
        self.automatic_filter_option = self.p['Automatic filter option']
        self.bfactor = self.p['B-Factor']
        

    def define_helix_or_particle_dimensions(self):
        self.helixwidth, self.helixheight = self.p['Estimated helix width and height in Angstrom']
        self.helixwidthpix_ori = int(round(self.helixwidth / self.pixelsize_ori))
        self.helixheightpix_ori = int(round(self.helixheight / self.pixelsize_ori))


    def apply_binfactor_if_required(self):
        if self.binfactor > 1 and self.binoption is True:
            self.infilestack, self.image_dimension, self.helixwidthpix, self.pixelsize = \
            SegmentExam().apply_binfactor(self.binfactor, self.infilestack, self.image_dimension_ori,
            self.helixwidthpix_ori, self.pixelsize_ori)
            
            self.helixheightpix = int(self.helixheightpix_ori / self.binfactor)
        else:
            self.helixwidthpix = self.helixwidthpix_ori
            self.helixheightpix = self.helixheightpix_ori
            self.pixelsize = self.pixelsize_ori
            self.image_dimension = self.image_dimension_ori
        self.maskwidthpix = self.helixwidthpix
        self.maskwidthpix_ori = self.helixwidthpix_ori


    def determine_minimal_segment_size(self):
        min_segsize = int(np.sqrt(self.helixheightpix ** 2 + self.helixwidthpix ** 2) + 0.5)
        min_segsize = Segment().determine_boxsize_closest_to_fast_values(min_segsize)

        return min_segsize


    def perform_binning_and_trimming_of_input_stack_if_required(self):
        stack = EMData()
        stack.read_image(self.infilestack, 0)
        self.image_dimension_ori = stack.get_xsize()
        self.apply_binfactor_if_required()
        
        min_segsize = self.determine_minimal_segment_size()
        image_count = EMUtil.get_image_count(self.infilestack)
        for each_image_index in list(range(image_count)):
            stack.read_image(self.infilestack, each_image_index)
            if min_segsize < self.image_dimension:
                stack = Util.window(stack, min_segsize, min_segsize, 1, 0, 0, 0)
            stack.write_image(os.path.basename(self.infilestack), each_image_index)
            
        self.infilestack = os.path.basename(self.infilestack)
        if min_segsize < self.image_dimension:
            self.image_dimension = min_segsize
            
        return self.infilestack, self.image_dimension
    

    def perform_binning_and_trimming_of_reference_if_required(self):
        if self.binoption:
            self.reference_stack, image_dimension, self.maskwidthpix, self.pixelsize = \
            SegmentExam().apply_binfactor(self.binfactor, self.reference_stack, self.image_dimension_ori, 
            self.maskwidthpix_ori, self.pixelsize_ori)
            
        img = EMData()
        img.read_image(self.infilestack)
        trimmed_img_size = img.get_xsize()
        
        ref_img = EMData()
        ref_img.read_image(self.reference_stack)
        ref_img_size = ref_img.get_xsize()
        
        if trimmed_img_size < ref_img_size:
            ref_count = EMUtil.get_image_count(self.reference_stack)
            for each_img in list(range(ref_count)):
                ref_img.read_image(self.reference_stack, each_img)
                ref_img = Util.window(ref_img, trimmed_img_size, trimmed_img_size, 1, 0, 0, 0)
                ref_img.write_image(os.path.basename(self.reference_stack), each_img)
        
            self.reference_stack = os.path.basename(self.reference_stack)
        
        return self.reference_stack
            

    def prepare_mask_ori(self):
        self.mask_ori = SegmentExam().make_smooth_rectangular_mask(self.helixwidthpix_ori, self.helixheightpix_ori,
        self.image_dimension_ori)
        
        return self.mask_ori


    def prepare_mask(self):
        if self.helixheightpix > self.image_dimension:
            self.log.wlog('Specified helix height of {0} Angstrom = {1} '.format(self.helixheight, self.helixheightpix) + \
            'pixels is larger than provided image dimension {0} pixels'.format(self.image_dimension))
            self.helixheightpix = self.image_dimension
            
        self.mask = SegmentExam().make_smooth_rectangular_mask(self.helixwidthpix, self.helixheightpix,
        self.image_dimension)
        
        return self.mask


    def setup_mask(self):
        self.mask = self.prepare_mask()
        self.maskfile = 'rectmask.hdf'
        self.mask.write_image(self.maskfile)

        return self.maskfile


class SegmentClassExternalPrograms(object):

    def add_mask_dimensions_to_align2d_features(self):
        self.aligndict['Estimated helix width and height in Angstrom'] = ((self.helixwidth, self.helixheight))
        program_to_be_launched = 'segmentalign2d'
        
        return program_to_be_launched
        

    def run_segmentalign2d_in_separate_process(self, aligndict, align_directory, program_to_be_launched):
        cpu_count = aligndict['Number of CPUs']
        mpi_option = aligndict['MPI option']
        alistack = aligndict['Image output stack']

        segmentalign_parfile = Features().write_parfile(aligndict)
        command_line_string = ' --f {parfile} --d {directory}'.format(parfile=segmentalign_parfile,
        directory=align_directory)

        external_segmentalign_run = OpenMpi()
        if mpi_option is True:
            program_to_be_launched = program_to_be_launched + '_mpi'
            command_line_string = program_to_be_launched + command_line_string
            external_segmentalign_run.check_if_mpi_works_and_launch_command(command_line_string, cpu_count)
        else:
            command_line_string = program_to_be_launched + command_line_string
            external_segmentalign_run.launch_command(command_line_string)
        external_segmentalign_run.check_expected_output_file(program_to_be_launched, os.path.join(align_directory,
        alistack))

        alistack = os.path.join(align_directory, alistack)
        os.remove(segmentalign_parfile)

        return alistack


    def spring_align2d(self, infilestack, reference_stack, reference_option=True, local_refinement=False):
        """
        * Function to launch helical 2D alignment program segmentalign

        #. Input: infilestack, reference stack
        #. Output: aligned stack
        #. Usage: alistack = spring_align2d(infilestack, reference_stack)
        """

        self.log.fcttolog()
        
        self.aligndict = OrderedDict()
        self.aligndict['Image input stack'] = infilestack
        alistack = os.path.splitext(os.path.basename(infilestack))[0] + 'ali.hdf'
        self.aligndict['Image output stack'] = alistack
        self.aligndict['Number of iterations']= 3
        self.aligndict['Internal binning factor']= 1
        self.aligndict['Update references']=True
        self.aligndict['Aligned average stack'] = 'multi_ref_avg.hdf'
        self.aligndict['Image reference stack'] = reference_stack
        self.aligndict['Reference option'] = reference_option 
        self.aligndict['Pixel size in Angstrom'] = self.pixelsize
        
        program_to_be_launched = self.add_mask_dimensions_to_align2d_features()
        
        self.aligndict['Limit in-plane rotation']=self.restrain_inplane_rotation
        self.aligndict['Delta in-plane rotation angle'] = self.delta_psi
        self.aligndict['X and Y translation range in Angstrom'] = ((self.x_range_in_angstrom, self.y_range_in_angstrom))
    
        self.aligndict['Local refinement'] = local_refinement
        self.aligndict['Absolute X and Y translation limit in Angstrom']= ((self.x_range_in_angstrom, self.y_range_in_angstrom))
        
        self.aligndict['High-pass filter option']=self.high_pass_filter_option
        self.aligndict['Low-pass filter option']=self.low_pass_filter_option
        self.aligndict['High and low-pass filter cutoffs in 1/Angstrom']=((self.high_pass_filter_cutoff, 
                                                                           self.low_pass_filter_cutoff))
        self.aligndict['Custom filter option']=self.custom_filter_option
        self.aligndict['Custom-built filter file']=self.custom_filter_file
        self.aligndict['Automatic filter option']=self.automatic_filter_option
        self.aligndict['B-Factor']=self.bfactor
        
        self.aligndict['MPI option'] = self.mpi_option
        self.aligndict['Number of CPUs']=self.ncpus
        self.aligndict['Temporary directory'] = self.temppath 
        
#         segmentalign_parfile = Features().write_parfile(self.aligndict)
        self.align_directory = '{0}{1:02}'.format(program_to_be_launched, self.iteration_index)
#         abspath_logfile = os.path.join(os.path.split(os.path.abspath(os.curdir))[0], self.feature_set.logfile)
        
#         command_line_string = ' --f {parfile} --d {directory}'.format(parfile=segmentalign_parfile,
#         directory=self.align_directory, logfile=abspath_logfile)

        alistack = self.run_segmentalign2d_in_separate_process(self.aligndict, self.align_directory,
        program_to_be_launched)

        return alistack
    

    def sx_kmeans(self, alistack, maskfile, class_count):
        """
        * Function to launch SPARX's k-means analysis

        #. Input: aligned stack, mask file, number of classes 
        #. Output: stack of averages, stack of variances
        #. Usage: avgstack, varstack = sx_kmeans(alistack, maskfile, class_count)
        """

        self.log.fcttolog()
        external_kmeans_run = OpenMpi()
        
        program_to_be_launched = 'sxk_means.py'
        classdir = '{0}{1:02}'.format(os.path.splitext(program_to_be_launched)[0], self.iteration_index)
        program_to_be_launched = Support().search_path_like_which(program_to_be_launched)
        avgstack = os.path.join(classdir, 'averages.hdf')
        varstack = os.path.join(classdir, 'variances.hdf')
        command_line_string = 'springenv {0} {1} {2} '.format(program_to_be_launched, alistack, classdir) + \
        '{0} --K={1} --maxit=500 --rand_seed=-1 --crit=D'.format(maskfile, class_count)

        if self.mpi_option is True:
            command_line_string = command_line_string + ' --MPI'
            external_kmeans_run.check_if_mpi_works_and_launch_command(command_line_string, self.ncpus)
        else:
            external_kmeans_run.launch_command(command_line_string)

        self.log.tlog(command_line_string)

        external_kmeans_run.check_expected_output_file(program_to_be_launched, avgstack)

        return avgstack, varstack
    
  
    def sx_kmeans_groups(self, alistack=None, maskfile=None, noclasses=None):
        """
        * Function to launch SPARX's k-means groups analysis (sx_kmeans_groups.py)

        #. Input: aligned stack, mask file, number of classes 
        #. Output: statistics data
        #. Usage: avgstack, varstack = sx_kmeans_groups(alistack, maskfile, noclasses)
        """
        if alistack is None: alistack = self.alistack
        if maskfile is None: maskfile = self.maskfile
        if noclasses is None: noclasses = self.noclasses

        self.classgrpdir = 'sxk_means_groups'
        external_kmeans_group_run = OpenMpi()
        self.classgrpdir = OpenMpi().check_dir(self.classgrpdir)

        program_to_be_launched = Support().search_path_like_which('sxk_means_groups.py')
        command_line_string = 'springenv {program} {instack} {outdir} {maskfile} --K1=2 \
            --K2={noclasses} --maxit=100 --rand_seed=100 \
            '.format(instack=alistack, program=program_to_be_launched, 
            outdir=self.classgrpdir, maskfile=maskfile, noclasses=noclasses)

        self.log.tlog(command_line_string)
        if self.mpi_option is True:
            command_line_string = command_line_string + ' --MPI'
            external_kmeans_group_run.check_if_mpi_works_and_launch_command(command_line_string, self.ncpus)
        else:
            external_kmeans_group_run.launch_command(command_line_string)


class SegmentClassStatistics(object):
    def compute_eigen_images(self, stack, eigenstack, mask, avg):
        """
          Perform PCA on stack file 
          and Get eigen images
        """
    
        image_count = EMUtil.get_image_count(stack)
        if image_count > 2000:
            eigenimage_count = 200
        else:
            eigenimage_count = int(0.1*image_count)
            
        pca = Analyzers.get('pca_large', {'mask':mask, 'nvec':eigenimage_count})
        e = EMData()
        if avg == 1: 
            s = EMData()
        for each_img_id in list(range(image_count)):
            e.read_image(stack, each_img_id)
            if mask is not None:
                e *= mask
            pca.insert_image(e)
            if avg == 1:
                if each_img_id == 0: 
                    s  = pca
                else:      
                    s += pca
        if avg == 1: 
            pca -= s/image_count
        eigenimages = pca.analyze()
        
        for each_img_id, each_eigenimage in enumerate(eigenimages):
            each_eigenimage.write_image(eigenstack,each_img_id)
        
        return eigenstack
    
        
    def log_member_statistics_from_classes(self, class_avg_stack, source_stack):
        
        class_avg_stack_image = EMData()
        class_count = EMUtil.get_image_count(class_avg_stack)
        raw_image_count = EMUtil.get_image_count(source_stack)
        
        members_of_classes = []
        classes =[]
        log_info = []
        for each_class in list(range(class_count)):
            class_avg_stack_image.read_image(class_avg_stack, each_class)
            members = class_avg_stack_image.get_attr('members')
            if type(members) is list:
                members = [int(each_member) for each_member in members]
                members_str = ', '.join([str(each_member) for each_member in members])
                
                log_info += [[each_class, len(members), len(members) * 100 / float(raw_image_count), members_str]]
                
                this_class = [each_class] * len(members)
                members_class = zip(members, this_class)
                members_of_classes += (members_class)
                classes.append(members)
            elif type(members) is not list:
                log_info += [[each_class, 0, 0, each_class, '0']]
        
        msg = tabulate(log_info, ['class_id', 'member_count', 'member_ratio', 'members'])
        self.log.ilog('The following classes and the corresponding membership statistics are listed:\n{0}'.format(msg))
        
        return members_of_classes, classes
    
            
    def enter_class_assignment_in_database(self, session, members_class):
        for each_member, each_class in members_class:
            each_segment = session.query(SegmentTable).get(each_member + 1)
            each_segment.class_id = each_class
            if self.spring_db_prepare:
                each_segment.ctf_convolved = True
                each_segment.ctf_phase_flipped = False
                each_segment.x_coordinate_A = each_segment.picked_x_coordinate_A
                each_segment.y_coordinate_A = each_segment.picked_y_coordinate_A
            session.merge(each_segment)
        session.commit()
            
        
    def make_align_named_tuple(self):
        return namedtuple('align', 'id alpha tx ty mirror')
    
    
    def get_alignment_info_from_stack(self, aligned_stack, classes):
        algn_img = EMData()
        alignment_data = []
        align_nt = self.make_align_named_tuple()
        for each_cls in classes:
            alignment_cls = []
            for each_member_id in each_cls:
                algn_img.read_image(aligned_stack, each_member_id)
                if algn_img.has_attr('xform.align2d'):
                    trans = algn_img.get_attr('xform.align2d')
                    d = trans.get_params('2D')
                    align_params = align_nt(each_member_id, d['alpha'], self.binfactor * d['tx'], self.binfactor * d['ty'], d['mirror'])
                else:
                    align_params = align_nt(each_member_id, 0, 0, 0, 0)
                alignment_cls.append(align_params)
            
            alignment_data.append(alignment_cls)
        
        return alignment_data


    def compute_average_variance_and_eigenimages_on_orignal_stack(self, output_avgstack, output_varstack, classes,
    alignment_data):
        self.log.fcttolog()
        ori_img = EMData()
        ori_img.read_image(self.infile)
        
        aligned_stack = 'aligned_ori_stack.hdf'
        segment_size = ori_img.get_xsize()
        avg = model_blank(segment_size, segment_size, 1)
        for each_cls_id, each_cls in enumerate(alignment_data):
            cls_avg = model_blank(segment_size, segment_size, 1)
            cls_var = cls_avg.copy()
            for each_img in each_cls:
                ori_img.read_image(self.infile, each_img.id)
                img = rot_shift2D(ori_img, each_img.alpha, each_img.tx, each_img.ty, each_img.mirror)
                img.write_image(aligned_stack, each_img.id)
                
                avg += img
                cls_avg += img
                cls_var += img * img
            
            member_count = len(each_cls)
            cls_avg /= float(member_count)
            cls_avg.set_attr('members', classes[each_cls_id])
            cls_avg.write_image(output_avgstack, each_cls_id)
            cls_var = (cls_var - cls_avg * cls_avg * member_count) / float(member_count - 1)
            cls_var.write_image(output_varstack, each_cls_id)
        self.log.tlog('Averages and variances of aligned stack computed.')

        self.mask_ori = self.prepare_mask_ori()
        self.compute_eigen_images(aligned_stack, self.eigenstack, self.mask_ori, avg)
        self.log.tlog('Eigenimages of aligned stack computed.')
        
        os.remove(aligned_stack)
        

    def create_database_with_stack_id_entries(self, segment_count):
        session = SpringDataBase().setup_sqlite_db(base)
        for each_stack_id in list(range(segment_count)):
            each_segment = SegmentTable()
            each_segment.stack_id = each_stack_id
            session.add(each_segment)
        
        session.commit()
        
        return session
    
    
    def finish_classification(self, avgstack, varstack, aligned_stack, output_avgstack, output_varstack):
        os.remove(self.maskfile)
        if self.iteration_count != 0:
            avg_file = os.path.join(self.align_directory, 'multi_ref_avg.hdf')
        else:
            avg_file = avgstack
        
        members_of_classes, classes = self.log_member_statistics_from_classes(avg_file, aligned_stack)
        
        alignment_data = self.get_alignment_info_from_stack(aligned_stack, classes)
                
        self.compute_average_variance_and_eigenimages_on_orignal_stack(output_avgstack, output_varstack, classes,
        alignment_data)
        
        if self.spring_db_option:
            shutil.copy(self.spring_path, 'spring.db')
            session = SpringDataBase().setup_sqlite_db(base)
        else:
            segment_count = EMUtil.get_image_count(self.infilestack)
            session = self.create_database_with_stack_id_entries(segment_count)
        self.enter_class_assignment_in_database(session, members_of_classes)
            

    def finish_classification_old(self, avgstack, varstack, aligned_stack, output_avgstack, output_varstack):
        os.remove(self.maskfile)
        if self.iteration_count != 0:
            os.rename(os.path.join(self.align_directory, 'multi_ref_avg.hdf'), output_avgstack)
            os.rename(os.path.join(self.align_directory, 'multi_ref_avg_var.hdf'), output_varstack)
        else:
            os.symlink(avgstack, output_avgstack)
            os.symlink(varstack, output_varstack)
        
        members_of_classes = self.log_member_statistics_from_classes(output_avgstack, aligned_stack)
        if self.spring_db_option:
            shutil.copy(self.spring_path, 'spring.db')
            session = SpringDataBase().setup_sqlite_db(base)
        else:
            segment_count = EMUtil.get_image_count(self.infilestack)
            session = self.create_database_with_stack_id_entries(segment_count)
        self.enter_class_assignment_in_database(session, members_of_classes)
            

class SegmentClass(SegmentClassPreparation, SegmentClassExternalPrograms, SegmentClassStatistics):

    def classify(self):
        self.log.fcttolog()

        self.infilestack, self.image_dimension = self.perform_binning_and_trimming_of_input_stack_if_required()
        self.maskfile = self.setup_mask()

        self.log.plog(10)
        self.iteration_index = 0
        if self.reference_option:
            self.reference_stack = self.perform_binning_and_trimming_of_reference_if_required()
                
            aligned_stack = self.spring_align2d(self.infilestack, self.reference_stack, reference_option=True,
            local_refinement=False)
        else:
            aligned_stack = self.infilestack
            
        avgstack, varstack = self.sx_kmeans(aligned_stack, self.maskfile, self.noclasses)
        self.log.plog(30)
        
        for self.iteration_round in list(range(self.iteration_count)):
            self.iteration_index += 1
            if self.iteration_round != 0:
                avgstack, varstack = self.sx_kmeans(aligned_stack, self.maskfile, self.noclasses)
                if not self.keep_intermediate_files:
                    os.remove(aligned_stack)
                
            self.log.plog(80 * (self.iteration_round + 0.5) / self.iteration_count + 30)
            if self.iteration_round == 0 and not self.reference_option:
                aligned_stack = self.spring_align2d(self.infilestack, avgstack, reference_option=True,
                local_refinement=False)
            else:
                aligned_stack = self.spring_align2d(self.infilestack, avgstack, reference_option=True,
                local_refinement=True)
                
            self.log.plog(80 * (self.iteration_round + 1) / self.iteration_count + 30)
        
        self.finish_classification(avgstack, varstack, self.infilestack, self.output_avgstack, self.output_varstack)
        
        self.log.endlog(self.feature_set)


def main():
    # Option handling
    parset = SegmentClassPar()
    mergeparset = OptHandler(parset)

    ######## Program
    stack = SegmentClass(mergeparset)
    stack.classify()

if __name__ == '__main__':
    main()
