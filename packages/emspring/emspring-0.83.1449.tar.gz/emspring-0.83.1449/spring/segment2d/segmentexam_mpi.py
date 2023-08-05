# Author: Carsten Sachse 1-Jan-2012
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from EMAN2 import EMData
from spring.csinfrastr.csproductivity import OpenMpi
from spring.segment2d.segmentexam import SegmentExam, SegmentExamPar
import os


class SegmentExamMpi(SegmentExam):

    def generate_local_name_for_reduction(self, emdata_file, rank):
        """
        >>> from spring.segment2d.segmentexam_mpi import SegmentExamMpi
        >>> SegmentExamMpi().generate_local_name_for_reduction('ps_234567891.hdf', 2)
        'ps_2345678912.hdf'
        """
        local_emdata_file = '{pre}{rank}{ext}'.format(pre=os.path.splitext(emdata_file)[0], rank=rank,
        ext=os.path.splitext(emdata_file)[1])
        
        return local_emdata_file
    

    def reduce_emdata_from_memory_on_main_node(self, widthavg):
        widthavg_file = 'width_avg.hdf'
        local_width_avg = self.generate_local_name_for_reduction(widthavg_file, self.rank)
        widthavg.write_image(local_width_avg)
        local_width_avg = self.comm.gather(local_width_avg, root=0)
        if self.rank == 0:
            widthavg = OpenMpi().reduce_emdata_on_main_node(widthavg, local_width_avg)
        else:
            widthavg = None
            
        return widthavg


    def prepare_segmentexam_mpi(self):
        self.comm, self.rank, self.size, self.log, self.tempdir = OpenMpi().setup_mpi_and_simultaneous_logging(self.log,
        self.feature_set.logfile, self.temppath)
        
        if self.rank == 0:
            segment_ids = self.copy_database_and_filter_segment_ids()
            segment_ids = OpenMpi().split_sequence_evenly(segment_ids, self.size)
        else:
            segment_ids = None
        segment_ids = self.comm.scatter(segment_ids, root=0)

        binned_stack = self.tempdir + os.path.basename(self.infilestack)
            
        self.infilestack, self.segsizepix, self.helixwidthpix, self.pixelsize = self.apply_binfactor(self.binfactor,
        self.infilestack, self.segsizepix, self.helixwidthpix, self.pixelsize, segment_ids, binned_stack)

        self.segsizepix = self.comm.bcast(self.segsizepix, root=0)
        self.helixwidthpix = self.comm.bcast(self.helixwidthpix, root=0)
        self.pixelsize = self.comm.bcast(self.pixelsize, root=0)
        self.comm.barrier()
        
        if self.rank == 0:
            self.log.plog(10)
            
        return segment_ids
    

    def add_powers_locally_and_reduce_on_main_node(self, segment_ids):
        masked_infilestack = os.path.join(self.tempdir, 'infilestack-masked.hdf')
        power_infilestack = os.path.join(self.tempdir, 'infilestack-power.hdf')
        
        avg_periodogram = self.add_power_spectra_from_verticalized_stack(self.infilestack, segment_ids,
        self.helixwidthpix, masked_infilestack, power_infilestack)
        
        local_power_img = self.generate_local_name_for_reduction(self.power_img, self.rank)
        if self.enhanced_power_option:
            local_power_enhanced_img = self.generate_local_name_for_reduction(self.power_enhanced_img, self.rank)
        else:
            local_power_enhanced_img = self.generate_local_name_for_reduction(os.path.splitext(self.power_img)[0] + \
            '_enh' + os.path.splitext(self.power_img)[-1], self.rank)
        avg_periodogram_enhanced = self.write_avg_periodograms(avg_periodogram, local_power_img,
        local_power_enhanced_img)
        
        self.comm.barrier()
        local_power_img = self.comm.gather(local_power_img, root=0)
        local_power_enhanced_img = self.comm.gather(local_power_enhanced_img, root=0)
        if self.rank == 0:
            avg_periodogram = OpenMpi().reduce_emdata_on_main_node(avg_periodogram, local_power_img)
            avg_periodogram.write_image(self.power_img)
            
            avg_periodogram_enhanced = OpenMpi().reduce_emdata_on_main_node(avg_periodogram_enhanced,
            local_power_enhanced_img)
            
            if self.enhanced_power_option:
                avg_periodogram_enhanced.write_image(self.power_enhanced_img)
            avg_collapsed_power_line, avg_collapsed_line_enhanced = self.collapse_periodograms(avg_periodogram,
            avg_periodogram_enhanced)
            
            self.log.plog(60)
        else:
            avg_collapsed_power_line = None
            avg_collapsed_line_enhanced = None
            
        self.comm.barrier()
        
        return avg_periodogram, power_infilestack, masked_infilestack, avg_periodogram_enhanced, \
        avg_collapsed_power_line, avg_collapsed_line_enhanced
    

    def correlate_layer_line_region_mpi(self, segment_ids, avg_periodogram, power_infilestack):
        if self.layer_ccc_option:
            avg_periodogram = EMData()
            avg_periodogram.read_image(self.power_img)

            correlations = self.correlate_layer_lines_of_average_power_with_individual_segments(avg_periodogram,
            power_infilestack, segment_ids)
            
            correlations = self.comm.gather(correlations, root=0)
            segment_ids = self.comm.gather(segment_ids, root=0)
            if self.rank == 0:
                correlations = OpenMpi().merge_sequence_of_sequences(correlations)
                segment_ids = OpenMpi().merge_sequence_of_sequences(segment_ids)
                self.enter_correlation_values_in_database(correlations, segment_ids)
        self.comm.barrier()
        os.remove(power_infilestack)


    def determine_width_from_collapsed_profile_mpi(self, segment_ids, masked_infilestack):
        temp_rowsadd, widths = self.determine_width(masked_infilestack, self.segsizepix, segment_ids)
        common_masked_stack = 'common_masked.hdf'
        OpenMpi().gather_stacks_from_cpus_to_common_stack(self.comm, masked_infilestack, common_masked_stack)
        common_rows = 'common_rows.hdf'
        OpenMpi().gather_stacks_from_cpus_to_common_stack(self.comm, temp_rowsadd, common_rows)
        self.widths = self.comm.gather(widths, root=0)
        
        return common_masked_stack, common_rows


    def visualize_avg_var_widths_and_power_spectra_mpi(self, avg_periodogram, avg_periodogram_enhanced,
    avg_collapsed_power_line, avg_collapsed_line_enhanced, common_masked_stack, common_rows):
        if self.rank == 0:
            widthavg, widthvar, twodavg, twodvar = self.compute_avg_and_var_of_width_and_image(common_masked_stack,
            common_rows)
            
            os.remove(common_masked_stack)
            self.widths = OpenMpi().merge_sequence_of_sequences(self.widths)
            
            self.visualize_power_avg_and_width_analysis(widthavg, widthvar, self.widths, twodavg, twodvar,
            avg_periodogram, avg_periodogram_enhanced, avg_collapsed_power_line, avg_collapsed_line_enhanced)
            
            self.log.plog(80)

        self.cleanup(self.infilestack)

    def add_up_power_spectra(self):
        segment_ids  = self.prepare_segmentexam_mpi()
        
        avg_periodogram, power_infilestack, masked_infilestack, avg_periodogram_enhanced, avg_collapsed_power_line, \
        avg_collapsed_line_enhanced = self.add_powers_locally_and_reduce_on_main_node(segment_ids)
                     
        self.correlate_layer_line_region_mpi(segment_ids, avg_periodogram, power_infilestack)
        common_masked_stack, common_rows = self.determine_width_from_collapsed_profile_mpi(segment_ids, masked_infilestack)
        
        self.visualize_avg_var_widths_and_power_spectra_mpi(avg_periodogram, avg_periodogram_enhanced,
        avg_collapsed_power_line, avg_collapsed_line_enhanced, common_masked_stack, common_rows)
            
        os.rmdir(self.tempdir)
        self.comm.barrier()
        if self.rank == 0:
            self.log.endlog(self.feature_set)

def main():
    parset = SegmentExamPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    stack = SegmentExamMpi(reduced_parset)
    stack.add_up_power_spectra()

if __name__ == '__main__':
    main()
