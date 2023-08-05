# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to assign a series of 3D models to class averages
"""
from EMAN2 import EMData, EMUtil
from collections import OrderedDict, namedtuple
from spring.csinfrastr.csdatabase import SpringDataBase, SegmentTable, base
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import OpenMpi, Temporary
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segmentclass import SegmentClass
from spring.segment2d.segmentselect import SegmentSelect
from spring.segment3d.refine.sr3d_main import SegmentRefine3d
from spring.segment3d.refine.sr3d_mpi import SegmentRefine3dMpi
from tabulate import tabulate
import json
import os
import shutil


class SegClassModelPar(object):
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'segclassmodel'
        self.proginfo = __doc__
        self.code_files = [self.progname, self.progname + '_mpi']

        self.segclassmodel_features = Features()
        self.feature_set = self.segclassmodel_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()


    def define_parameters_and_their_properties(self):
        self.feature_set = self.set_inp_multiple_models(self.feature_set)
        self.feature_set = self.segclassmodel_features.set_class_avg_stack(self.feature_set)
        self.feature_set = self.segclassmodel_features.set_spring_path_segments(self.feature_set)
        
        self.feature_set = self.segclassmodel_features.set_in_or_exclude_classes_option(self.feature_set)
        self.feature_set = self.segclassmodel_features.set_in_or_exclude_classes(self.feature_set)
        self.feature_set = self.segclassmodel_features.set_classes_to_be_in_or_excluded(self.feature_set)
        
        self.feature_set = self.segclassmodel_features.set_angular_projection_count(self.feature_set)
        self.feature_set = self.segclassmodel_features.set_out_of_plane_tilt_angle_range(self.feature_set)
        
        self.feature_set = self.segclassmodel_features.set_keep_intermediate_files_option(self.feature_set, 
        hinttxt='Keep reprojection stack of models.')

        self.feature_set = self.segclassmodel_features.set_pixelsize(self.feature_set)
        self.feature_set = self.segclassmodel_features.set_helix_width_and_height(self.feature_set)
        self.feature_set = self.segclassmodel_features.set_alignment_rotation_and_translation(self.feature_set)
        self.feature_set = self.segclassmodel_features.set_internal_binning(self.feature_set)
        
        self.feature_set = self.segclassmodel_features.set_filter_options(self.feature_set)

        self.feature_set = self.segclassmodel_features.set_mpi(self.feature_set)
        self.feature_set = self.segclassmodel_features.set_ncpus(self.feature_set)
        self.feature_set = self.segclassmodel_features.set_temppath(self.feature_set)

        
    def set_inp_multiple_models(self, feature_set):
        inp1 = 'Reference volumes'
        feature_set.parameters[inp1]='recvol???.hdf'
        feature_set.properties[inp1]=feature_set.file_properties(10, ['hdf'], 'getFiles')

        feature_set.hints[inp1]='Input 3D reconstructions: to be reprojected and used for projection matching with ' + \
        'provided classes. They should be generated using segmentrefine3d or segclassreconstruct because they ' + \
        'require \'rise/rotation\' and \'point_sym\' entries in their header.' 
        
        feature_set.level[inp1]='beginner'

        return feature_set
    

    def define_program_states(self):
        self.feature_set.program_states['prepare_models']='Prepare provided models for 3D reprojection'
        self.feature_set.program_states['launch_segmentalign2d_to_match_classes_against_projections']= \
        'Aligns class averages to model reprojections'

        
class SegClassModelPrepare(object):
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.infile = p['Class average stack']
            self.models_input = p['Reference volumes']
            self.references = Features().convert_list_of_files_from_entry_string(self.models_input)
            self.spring_path = p['spring.db file']

            self.classes_selection = p['Classes select option']
            self.classes_in_or_exclude = p['Include or exclude classes']
            self.classes_entries = p['Classes list']
        
            self.keep_intermediate_files = p['Keep intermediate files']
            self.pixelsize = p['Pixel size in Angstrom']
            self.helixwidth, self.helixheight = p['Estimated helix width and height in Angstrom']
            self.helixwidthpix = int(round(self.helixwidth / self.pixelsize))
            self.helix_heightpix = int(round(self.helixheight / self.pixelsize))
        
            self.binfactor = p['Internal binning factor']
            self.restrain_inplane_rotation = p['Limit in-plane rotation']
            self.delta_psi = p['Delta in-plane rotation angle']
            if not self.restrain_inplane_rotation:
                self.delta_psi = 180
            self.x_range_A, self.y_range_A = p['X and Y translation range in Angstrom']

            self.out_of_plane_tilt_angle_range = p['Out-of-plane tilt angle range']
        
            self.azimuthal_angle_count, self.out_of_plane_tilt_angle_count = p['Number of projections azimuthal/' + \
            'out-of-plane angle']

            self.high_pass_filter_option = p['High-pass filter option']
            self.low_pass_filter_option = p['Low-pass filter option']
            self.high_pass_filter_cutoff = p['High and low-pass filter cutoffs in 1/Angstrom'][0]
            self.low_pass_filter_cutoff = p['High and low-pass filter cutoffs in 1/Angstrom'][1]
            self.custom_filter_option = p['Custom filter option']
            self.custom_filter_file = p['Custom-built filter file']
            self.bfactor = p['B-Factor']

            self.mpi_option = p['MPI option']
            self.cpu_count = p['Number of CPUs']
            self.temppath=p['Temporary directory']
            

    def prepare_sr3d_object_with_filter_settings(self):
        if hasattr(self, 'comm'):
            sr3d = SegmentRefine3dMpi()
            [setattr(sr3d, each_param, getattr(self, each_param)) for each_param in ['comm', 'rank', 'size']]
        else:
            sr3d = SegmentRefine3d()

        params = ['low_pass_filter_option', 'low_pass_filter_cutoff', 'high_pass_filter_option',
        'high_pass_filter_cutoff', 'custom_filter_option', 'custom_filter_file', 'bfactor', 'pixelsize', 'helixwidth', 
        'helixwidthpix', 'out_of_plane_tilt_angle_range', 'azimuthal_angle_count', 'out_of_plane_tilt_angle_count', 
        'tempdir', 'keep_intermediate_files']

        [setattr(sr3d, each_param, getattr(self, each_param)) for each_param in params]
        
        sr3d.helix_inner_widthpix = 0
        sr3d.layer_line_filter = False
        sr3d.fsc_filter = None

        return sr3d


class SegClassModelProject(SegClassModelPrepare):
    def get_helical_and_point_group_symmetry_from_volume(self, ref_file):
        ref_vol = EMData()
        ref_vol.read_image(ref_file)

        msg = ''
        if not ref_vol.has_attr('rise/rotation') or not ref_vol.has_attr('point_sym'):
            msg += 'Provided model file {0} does not have the \'rise/rotation\' attribute in the header. '
        if not ref_vol.has_attr('point_sym'):
            msg += 'Provided model file {0} does not have the \'point_sym\' attribute in the header. '
        if msg != '':
            msg +='Double-check that it was generated by segmentrefine3d or segclassreconstruct.'
            raise ValueError(msg)

        hel_sym_entry = ref_vol.get_attr('rise/rotation')
        hel_sym = hel_sym_entry.strip('(').strip(')').split(',')
        rise = float(hel_sym[0])
        rotation = float(hel_sym[1])
        helical_symmetry = (rise, rotation)

        point_symmetry = ref_vol.get_attr('point_sym')
        rotational_symmetry = int(point_symmetry[-1])
        if ref_vol.has_attr('apix_z'):
            if ref_vol.get_attr('apix_z') != 1.0:
                pixelsize = ref_vol.get_attr('apix_z')
            else:
                pixelsize = self.pixelsize

        rec_size = ref_vol.get_xsize()

        ref_vol = \
        SegmentRefine3d().rescale_reference_volume_in_case_vol_pixelsize_differs_from_current_pixelsize(rec_size,
        ref_vol, self.pixelsize)

        ref_vol.write_image(os.path.basename(ref_file))

        return rec_size, helical_symmetry, rotational_symmetry, point_symmetry, pixelsize


    def prepare_prj_through_series_of_models(self):
        class_avg = EMData()
        class_avg.read_image(self.infile)
        projection_size = class_avg.get_xsize()
        projection_info = []

        return projection_size, projection_info


    def prepare_volume_for_projection(self, projection_size, sr3d, each_model_id, each_reference):
        recsize, helical_symmetry, rotational_symmetry, point_symmetry, pixelsize = \
        self.get_helical_and_point_group_symmetry_from_volume(each_reference)
        
        pixel_info_nt = sr3d.make_pixel_info_named_tuple()
        pixelinfo = pixel_info_nt(pixelsize, projection_size, recsize, self.helixwidthpix, 0, self.helix_heightpix)
        
#         sr3d.pixelsize = pixelsize
#         sr3d.helical_symmetry = helical_symmetry
#         sr3d.rotational_symmetry_start = int(point_symmetry[-1])
        reference_file = os.path.basename(each_reference)

        reference_info_nt = sr3d.make_reference_info_named_tuple()

        reference_info = reference_info_nt(each_model_id, reference_file, None, None, helical_symmetry, point_symmetry,
        rotational_symmetry, None)

        ref_vol = sr3d.filter_and_mask_reference_volume('medium', reference_info, pixelinfo)

        ref_vol.write_image(reference_file)

        return reference_info, pixelinfo


    def summarize_prj_info(self, projection_info, each_model_id, projection_stack, projection_parameters):
        model_ids = len(projection_parameters) * [each_model_id]
        projection_stack = len(projection_parameters) * [projection_stack]
        prj_ids = list(range(len(projection_parameters)))
        projection_info += zip(prj_ids, model_ids, projection_stack)

        return projection_info

    def get_prj_info_nt(self):
        return namedtuple('prj_info', 'prj_id model_id prj_stack')


    def get_proj_refs_file_name(self):
        merged_prj_stack = 'proj_refs.hdf'

        return merged_prj_stack


    def merge_prj_stacks_and_collect_prj_info(self, projection_info):
        prj = EMData()
        merged_prj_stack = self.get_proj_refs_file_name()
        for each_total_id, (each_prj_id, each_model_id, each_projection_stack) in enumerate(projection_info):
            prj.read_image(each_projection_stack, each_prj_id)
            prj.write_image(merged_prj_stack, each_total_id)
        
        single_prj_files = set(zip(*projection_info)[2])
        [os.remove(each_prj_file) for each_prj_file in single_prj_files]
        
        prj_info = self.get_prj_info_nt()

        projection_info = [prj_info._make(each_info) for each_info in projection_info]

        return merged_prj_stack, projection_info


    def prepare_class_avg_stack(self):
        class_count = EMUtil.get_image_count(self.infile)
        classes = set(range(class_count))
        
        if self.classes_selection:
            classes_sel = SegmentSelect().prepare_list_from_comma_separated_input(self.classes_entries, 'class')
            if self.classes_in_or_exclude == 'include':
                classes = classes.intersection(classes_sel)
            if self.classes_in_or_exclude == 'exclude':
                classes = classes.difference(classes_sel)

        img = EMData()
        local_infile = os.path.splitext(os.path.basename(self.infile))[0] + '_tmp' + \
        os.path.splitext(os.path.basename(self.infile))[-1]
        for each_sel_class, each_class in enumerate(classes):
            img.read_image(self.infile, each_class)
            img.write_image(local_infile, each_sel_class)

        return local_infile, classes
    
                
    def prepare_merged_stack_of_projections(self):
        sr3d = self.prepare_sr3d_object_with_filter_settings()

        projection_size, projection_info = self.prepare_prj_through_series_of_models()

        for each_model_id, each_reference in enumerate(self.references):
            reference_info, pixelinfo = self.prepare_volume_for_projection(projection_size, sr3d, each_model_id,
            each_reference)

            projection_stack, projection_parameters, fine_projection_stack, fine_projection_parameters = \
            sr3d.project_through_reference_volume_in_helical_perspectives('medium', reference_info.model_id,
            reference_info.ref_file, pixelinfo, reference_info.helical_symmetry, reference_info.rotational_symmetry)

            projection_info = self.summarize_prj_info(projection_info, each_model_id, projection_stack,
            projection_parameters)
        
        merged_prj_stack, projection_info = self.merge_prj_stacks_and_collect_prj_info(projection_info)

        return  merged_prj_stack, projection_info


class SegClassModel(SegClassModelProject):
    def launch_segmentalign2d_to_match_classes_against_projections(self, infilestack, merged_prj_stack):
        self.log.fcttolog()
        
        self.aligndict = OrderedDict()
        self.aligndict['Image input stack'] = infilestack
        alistack = os.path.splitext(os.path.basename(infilestack))[0] + 'ali.hdf'
        self.aligndict['Image output stack'] = alistack
        self.aligndict['Number of iterations']= 3
        self.aligndict['Internal binning factor']= 1
        self.aligndict['Update references']=False
        self.aligndict['Aligned average stack'] = 'multi_ref_avg.hdf'
        self.aligndict['Image reference stack'] = merged_prj_stack
        self.aligndict['Reference option'] = True
        self.aligndict['Pixel size in Angstrom'] = self.pixelsize
        
        self.aligndict['Estimated helix width and height in Angstrom'] = ((self.helixwidth, self.helixheight))
        self.aligndict['Limit in-plane rotation']=self.restrain_inplane_rotation
        self.aligndict['Delta in-plane rotation angle'] = self.delta_psi
        self.aligndict['X and Y translation range in Angstrom'] = ((self.x_range_A, self.y_range_A))
    
        self.aligndict['Local refinement'] = False
        self.aligndict['Absolute X and Y translation limit in Angstrom']= ((self.x_range_A, self.y_range_A))
        
        self.aligndict['High-pass filter option']=self.high_pass_filter_option
        self.aligndict['Low-pass filter option']=self.low_pass_filter_option
        self.aligndict['High and low-pass filter cutoffs in 1/Angstrom']=((self.high_pass_filter_cutoff, 
                                                                           self.low_pass_filter_cutoff))
        self.aligndict['Automatic filter option']=False
        self.aligndict['Custom filter option']=self.custom_filter_option
        self.aligndict['Custom-built filter file']=self.custom_filter_file
        self.aligndict['B-Factor']=self.bfactor
        
        self.aligndict['MPI option'] = self.mpi_option
        self.aligndict['Number of CPUs']=self.cpu_count
        self.aligndict['Temporary directory'] = self.temppath 

        segmentalign_dir ='segmentalign2d00' 

        alistack = SegmentClass().run_segmentalign2d_in_separate_process(self.aligndict, segmentalign_dir,
        'segmentalign2d')

        if not self.keep_intermediate_files:
            files_in_dir = os.listdir(segmentalign_dir)
            [os.remove(os.path.join(segmentalign_dir, each_file)) for each_file in files_in_dir]
            os.rmdir(segmentalign_dir)
            os.remove(merged_prj_stack)

        return infilestack
        
    
    def get_matched_prj_id_from_alignment_stack_and_assign_model(self, infilestack, prj_info, reduced_classes):
        class_count = EMUtil.get_image_count(infilestack)
        class_img = EMData()

        cls_assigned_prj = []
        for each_class in list(range(class_count)):
            class_img.read_image(infilestack, each_class)
            cls_assigned_prj.append(class_img.get_attr('assign'))
                         
        cls_assigned_models = [prj_info[each_assigned_prj].model_id for each_assigned_prj in cls_assigned_prj]
    
        os.remove(infilestack)
        all_class_count = EMUtil.get_image_count(self.infile)
        if all_class_count > class_count:
            all_cls_assigned_models = []
            for each_class in list(range(all_class_count)):
                if each_class in reduced_classes:
                    all_cls_assigned_models += [cls_assigned_models[each_red_class_id] 
                                                for each_red_class_id, each_red_class in enumerate(reduced_classes) 
                                                if each_class == each_red_class]
                if each_class not in reduced_classes:
                    all_cls_assigned_models += [None]
        else:
            all_cls_assigned_models = cls_assigned_models
            
        return all_cls_assigned_models
    

    def udpate_segments_in_spring_db_with_assigned_model(self, cls_assigned_models):
        shutil.copy(self.spring_path, 'spring.db')
        session = SpringDataBase().setup_sqlite_db(base)
        
        segments = session.query(SegmentTable).order_by(SegmentTable.id).all()
        
        loginfo =[]
        for each_segment in segments:
            if each_segment.class_id is not None:
                assigned_model = cls_assigned_models[each_segment.class_id]
                each_segment.class_model_id = assigned_model
                session.merge(each_segment)
                loginfo.append((each_segment.stack_id, each_segment.class_id, assigned_model))
            
        session.commit()
        msg = tabulate(loginfo, ['stack_id', 'class_id', 'class_model_id'])
        self.log.ilog('The following segments on the stack have been assigned with the respective models:\n{0}'.format(msg))


    def perform_projection_or_pick_up_completed_prj_in_case_of_mpi(self):
        if not self.mpi_option:
            merged_prj_stack, prj_info = self.prepare_merged_stack_of_projections()
        else:
            merged_prj_stack = self.get_proj_refs_file_name()
            if not os.path.isfile(merged_prj_stack):
                msg = '{0} did not generate projections correctly. '.format(self.feature_set.progname.title())
                'Look for previous error messages to find out the reason.'
                raise ValueError(msg)

            prj_info = json.load(open('prj_info.dat'))
            os.remove('prj_info.dat')
            prj_info_nt = self.get_prj_info_nt()
            prj_info = [prj_info_nt._make(each_prj_info) for each_prj_info in prj_info]

        return merged_prj_stack, prj_info


    def match_reprojections_to_classes(self):
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count,
        exiting=False)

        self.tempdir = Temporary().mktmpdir(self.temppath)

        local_infile, reduced_classes = self.prepare_class_avg_stack()
        merged_prj_stack, prj_info = self.perform_projection_or_pick_up_completed_prj_in_case_of_mpi()
            
        infilestack = self.launch_segmentalign2d_to_match_classes_against_projections(local_infile, merged_prj_stack)

        cls_assigned_models = self.get_matched_prj_id_from_alignment_stack_and_assign_model(infilestack, prj_info,
        reduced_classes)
        
        self.udpate_segments_in_spring_db_with_assigned_model(cls_assigned_models)

        os.rmdir(self.tempdir)
        self.log.endlog(self.feature_set)


def main():
    # Option handling
    parset = SegClassModelPar()
    mergeparset = OptHandler(parset)

    ######## Program
    classes = SegClassModel(mergeparset)
    classes.match_reprojections_to_classes()


if __name__ == '__main__':
    main()
