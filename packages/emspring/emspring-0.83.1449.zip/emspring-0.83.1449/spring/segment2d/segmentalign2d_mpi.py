# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Created on Apr 14, 2011

@author: sachse
"""
from EMAN2 import Util
from spring.csinfrastr.csproductivity import OpenMpi
from spring.segment2d.segmentalign2d import SegmentAlign2dPar, SegmentAlign2d
import os


class SegmentAlign2dMpiPreparation(SegmentAlign2d):
    """
    * class that holds functions for MPI functions of segmentalign
    """
    def update_local_ids_in_list_of_named_tuple(self, named_tuples):
        """
        >>> from collections import namedtuple
        >>> info = namedtuple('info', 'stack_id local_id')
        >>> l = [info(10, 10), info(11, 11)]
        >>> from spring.segment2d.segmentalign2d_mpi import SegmentAlign2dMpi
        >>> SegmentAlign2dMpi().update_local_ids_in_list_of_named_tuple(l)
        [info(stack_id=10, local_id=0), info(stack_id=11, local_id=1)]
        """
        updated_list = []
        for each_local_id, each_item in enumerate(named_tuples):
            updated_item = each_item._replace(local_id = each_local_id)
            updated_list.append(updated_item)
            
        return updated_list
    
    
    def prepare_alignment_mpi(self):
        self.comm, self.rank, self.size, self.log, self.tempdir = OpenMpi().setup_mpi_and_simultaneous_logging(self.log,
        self.feature_set.logfile, self.temppath)
        
        self.log.fcttolog()
        
        if self.rank == 0: 
            images_info, self.image_dimension = self.get_image_alignments_from_stack(self.alignment_stack_name)
            
            images_info = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(images_info)
            images_info = OpenMpi().split_sequence_evenly(images_info, self.size)
        else:
            images_info = None
            self.image_dimension = None
        
        images_info = self.comm.scatter(images_info, root=0)
        self.image_dimension = self.comm.bcast(self.image_dimension, root=0)
        
        images_info = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(images_info,
        self.get_image_list_named_tuple())
        
        images_info = self.update_local_ids_in_list_of_named_tuple(images_info)
        
        if not self.reference_option:
            image_ids = [each_image.stack_id for each_image in images_info]
            ref_center = self.average_stack(self.alignment_stack_name, image_ids, align=True)
            
            distributed_emdata_files = OpenMpi().write_out_emdata_from_distributed_nodes_to_common_disk(self.comm,
            ref_center, 'avg_ref.hdf')
            
            if self.rank == 0:
                combined_avg = OpenMpi().reduce_emdata_on_main_node(ref_center, distributed_emdata_files,
                read_first=False)
                
                combined_avg.write_image('average.hdf')
        
            self.reference_stack_name = 'average.hdf'
            
        if self.rank == 0:
            alignment_info = self.define_flow_of_alignment(self.pixelsize, self.binfactor, self.number_of_iterations,
            max(self.x_range_A, self.y_range_A))
            
            self.log.plog(10)
            alignment_info = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(alignment_info)
        else:
            alignment_info = None
        
        alignment_info = self.comm.bcast(alignment_info, root=0)
        alignment_info = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(alignment_info, 
        self.get_align_info_nt())
        
        
        return alignment_info, images_info
    
        
class SegmentAlign2dMpi(SegmentAlign2dMpiPreparation):
    def mpi_reduce_reference_stack(self, distributed_odd_averages, distributed_even_averages, 
                                   distributed_variances, distributed_image_counts, reference_stack):
        """
        * Function to sum up even and odd images from reference stack
        """
        for each_reference_number, each_reference in enumerate(reference_stack):
            reference_stack[each_reference_number].odd_average.to_zero()
            reference_stack[each_reference_number].even_average.to_zero()
            reference_stack[each_reference_number].variance.to_zero()
            reference_stack[each_reference_number].number_of_images[''] = 0
            for each_reference_stack in distributed_odd_averages:
                Util.add_img(reference_stack[each_reference_number].odd_average, 
                             each_reference_stack[each_reference_number])
            for each_reference_stack in distributed_even_averages:
                Util.add_img(reference_stack[each_reference_number].even_average, 
                             each_reference_stack[each_reference_number])
            for each_reference_stack in distributed_variances:
                Util.add_img(reference_stack[each_reference_number].variance, 
                             each_reference_stack[each_reference_number])
            for each_reference_image_count in distributed_image_counts:
                reference_stack[each_reference_number].number_of_images[''] += \
                each_reference_image_count[each_reference_number]
                             
        return reference_stack
    
    
    def mpi_gather_assigned_images(self, distributed_assignments, reference_image_count):
        """
        >>> from spring.segment2d.segmentalign2d_mpi import SegmentAlign2dMpi
        >>> distributed_assignments = [[[0, 2], [1]], [[4], [3]], [[5, 6, 7], []], [[8, 9], []]]
        >>> SegmentAlign2dMpi().mpi_gather_assigned_images(distributed_assignments, 2)
        [[0, 2, 4, 5, 6, 7, 8, 9], [1, 3]]
        """
        gathered_assigned_images = list(range(reference_image_count))
        for each_ref_id in list(range(reference_image_count)):
            gathered_assigned_images[each_ref_id] = []
            for each_cpu in distributed_assignments:
                for each_assigned_image in each_cpu[each_ref_id]:
                    gathered_assigned_images[each_ref_id].append(each_assigned_image)
            
        return gathered_assigned_images
        

    def gather_assigned_images_from_cpus_to_common_assigment_on_root(self, assigned_images, reference_stack):
        distributed_assignments = self.comm.gather(assigned_images, root=0)
        if self.rank == 0:
            assigned_images = self.mpi_gather_assigned_images(distributed_assignments, len(reference_stack))
            
        return assigned_images
    
    
    def gather_averages_from_cpus_to_common_reference_stack_on_root(self, reference_stack):
        odd_average = []
        even_average = []
        variance = []
        matched_image_counts = []
        
        for each_reference in reference_stack:
            odd_average.append(each_reference.odd_average)
            even_average.append(each_reference.even_average)
            variance.append(each_reference.variance)
            matched_image_counts.append(each_reference.number_of_images[''])
        
        distributed_odd_averages = self.comm.gather(odd_average, root=0)
        distributed_even_averages = self.comm.gather(even_average, root=0)
        distributed_variances = self.comm.gather(variance, root=0 )
        distributed_image_count = self.comm.gather(matched_image_counts, root=0)
        
        if self.rank == 0:
            reference_stack = self.mpi_reduce_reference_stack(distributed_odd_averages,
                distributed_even_averages, distributed_variances, distributed_image_count, reference_stack)
            
        return reference_stack
            
            
    def perform_iterative_alignment_mpi(self, alignment_info, images_info):
        image_ids = [each_image.stack_id for each_image in images_info]
        
        determined_params = None
        previous_binfactor = 0
        merged_references = 'combined_avg.hdf'
        for align_id, each_info in enumerate(alignment_info):
            if align_id == 0:
                reference_stack = None
            else:
                reference_stack = self.prepare_reference_stack(merged_references)
            
            previous_params, refine_locally = self.define_previous_params_and_refine_locally(images_info,
            determined_params, previous_binfactor, align_id, each_info)
                
            alignment_stack_name, reference_stack, bin_mask = \
            self.bin_references_and_images(self.alignment_stack_name, self.reference_stack_name, reference_stack,
            each_info, image_ids, align_id, previous_binfactor)
            
            self.comm.barrier()
            ringref, polar_interpolation_parameters, ring_weights, reference_stack = \
            self.prepare_reference_images_for_alignment(bin_mask, reference_stack)
            
            self.log.plog(80 * (align_id + 0.5) / len(alignment_info) + 10)
            
            assigned_images, determined_params, reference_stack = \
            self.align_images_to_references(alignment_stack_name, reference_stack, previous_params, ringref,
            polar_interpolation_parameters, ring_weights, each_info, refine_locally)
            
            self.comm.barrier()
            reference_stack = self.gather_averages_from_cpus_to_common_reference_stack_on_root(reference_stack)
            
            assigned_images = self.gather_assigned_images_from_cpus_to_common_assigment_on_root(assigned_images,
            reference_stack)
            
            if self.rank == 0:
                similarity_criterion, reference_stack = \
                self.pass_alignment_parameters_from_reference_groups_to_images(reference_stack, each_info, assigned_images,
                bin_mask, alignment_stack_name, self.aligned_averages)
            
                msg = 'ITERATION #{0}        criterion = {1}'.format(each_info.iteration_id, similarity_criterion)
                self.log.tlog(msg)
 
                for each_ref_id, each_reference in enumerate(reference_stack):
                    each_reference.total_average.write_image(merged_references, each_ref_id)
                    
                self.log.plog(80 * (align_id + 1) / len(alignment_info) + 10)
            previous_binfactor = each_info.binfactor
            self.comm.barrier()
            
        determined_params = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(determined_params)
        determined_params = self.comm.gather(determined_params, root=0)
        
        if self.rank == 0:
            determined_params = OpenMpi().merge_sequence_of_sequences(determined_params)
        
            determined_params = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(determined_params,
            self.get_image_list_named_tuple())
        
#            self.write_aligned_unfiltered_averages_and_variances(reference_stack)
            self.generate_aligned_output_file_and_update_header_of_input(each_image, determined_params)
            os.remove(merged_references)
            if not self.reference_option:
                os.remove(self.reference_stack_name)
            
        self.comm.barrier()
            
        self.log.ilog('Alignment parameters were applied to new output file {0}.'.format(self.outfile))
        
        self.cleanup_segmentalign2d()
        if self.rank == 0:
            self.log.endlog(self.feature_set)
        
        
    def perform_segmentalign2d_mpi(self):
        alignment_info, images_info = self.prepare_alignment_mpi()
        self.perform_iterative_alignment_mpi(alignment_info, images_info)
        
def main():
    parset = SegmentAlign2dPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    stack = SegmentAlign2dMpi(reduced_parset)
    stack.perform_segmentalign2d_mpi()


if __name__ == '__main__':
    main()
