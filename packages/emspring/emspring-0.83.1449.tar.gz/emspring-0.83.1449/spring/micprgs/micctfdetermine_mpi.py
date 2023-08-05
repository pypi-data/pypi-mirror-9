# Author: Carsten Sachse 11-Aug-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from spring.csinfrastr.csdatabase import SpringDataBase, base
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.csproductivity import OpenMpi
from spring.micprgs.micctfdetermine import MicCtfDetermine, MicCtfDeterminePar
from tabulate import tabulate
import os
import shutil

class ScanMpi(object):
    def startup_scan_mpi_programs(self):
        self.comm, self.rank, self.size, self.log, self.tempdir = OpenMpi().setup_mpi_and_simultaneous_logging(self.log,
        self.feature_set.logfile, self.temppath)
        
        self.outfiles = Features().rename_series_of_output_files(self.micrograph_files, self.outfile)
        
        self.log.fcttolog()
        if self.rank == 0:
            if len(self.micrograph_files) == 0:
                msg = 'No micrographs found in {0}.'.format(self.infile)
                raise ValueError(msg)
            elif len(self.micrograph_files) < self.size:
                msg = 'You requested a larger number of CPUs than microcraphs. To optimally make use of the ' + \
                'resources. Please reduce number of requested CPUs to ' + \
                '{0} for {0} micrographs.'.format(len(self.micrograph_files))
                raise ValueError(msg)
            self.micrograph_files = OpenMpi().split_sequence_evenly(self.micrograph_files, self.size)
            self.outfiles = OpenMpi().split_sequence_evenly(self.outfiles, self.size)
            
            table_data = [ (each_rank_id, ', '.join(each_fileset)) 
                          for each_rank_id, each_fileset in enumerate(self.micrograph_files)]

            msg = tabulate(table_data, ['node_id', 'micrographs'])
            log_str = 'The following nodes will handle the following micrographs:\n{0}'.format(msg)
            self.log.ilog(log_str)
            
        else:
            self.micrograph_files = None
        self.micrograph_files = self.comm.scatter(self.micrograph_files, root=0)
        self.outfiles = self.comm.scatter(self.outfiles, root=0)


    def end_scan_mpi_programs(self):
        self.comm.barrier()
        if self.rank == 0:
            self.log.endlog(self.feature_set)
        os.rmdir(self.tempdir)


class MicCtfDetermineMpi(MicCtfDetermine, ScanMpi):

    def gather_ctf_and_enter_in_database(self, ctffind_params_list, ctftilt_params_list):
        ctffinds = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(ctffind_params_list)
        ctftilts = OpenMpi().convert_list_of_namedtuples_to_list_of_lists(ctftilt_params_list)
        ctffinds = self.comm.gather(ctffinds, root=0)
        ctftilts = self.comm.gather(ctftilts, root=0)
        micrograph_files = self.comm.gather(self.micrograph_files, root=0)
        if self.rank == 0:
            ctffinds = OpenMpi().merge_sequence_of_sequences(ctffinds)
            ctftilts = OpenMpi().merge_sequence_of_sequences(ctftilts)
            micrograph_files = OpenMpi().merge_sequence_of_sequences(micrograph_files)
            ctffind_tuple = self.make_ctffind_parameters_named_tuple()
            
            ctffind_params_combined_list = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(ctffinds,
            ctffind_tuple)
            
            ctftilt_tuple = self.make_ctftilt_parameters_named_tuple()
            
            ctftilt_params_combined_list = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(ctftilts,
            ctftilt_tuple)
            
            self.enter_ctffind_and_ctftilt_values_in_database(micrograph_files, ctffind_params_combined_list,
            ctftilt_params_combined_list)


    def fill_micrographs_list_with_dummy(self, micrograph_files, max_micrograph_count):
        """
        >>> from spring.micprgs.micctfdetermine_mpi import MicCtfDetermineMpi
        >>> MicCtfDetermineMpi().fill_micrographs_list_with_dummy(['dim', 'dum'], 4) 
        ['dim', 'dum', 'place_holder', 'place_holder']
        >>> MicCtfDetermineMpi().fill_micrographs_list_with_dummy(['dim', 'dum'], 2) 
        ['dim', 'dum']
        """
        while len(micrograph_files) < max_micrograph_count:
            micrograph_files += ['place_holder']
        
        return micrograph_files


    def insure_that_every_node_has_the_same_number_of_micrographs(self, micrograph_files):
        micrograph_count = self.comm.gather(len(micrograph_files), root=0)
        if self.rank == 0:
            max_micrograph_count = max(micrograph_count)
        else:
            max_micrograph_count = None
            
        max_micrograph_count = self.comm.bcast(max_micrograph_count, root=0)
        
        micrograph_files = self.fill_micrographs_list_with_dummy(micrograph_files, max_micrograph_count)
        
        return micrograph_files
        
        
    def run_ctffind_and_ctftilt_for_given_micrographs(self, micrograph_files, outfiles):
        if self.rank == 0:
            if self.spring_db_option:
                shutil.copy(self.spring_path, 'spring.db')
            else:
                SpringDataBase().setup_sqlite_db(base)
                
        self.comm.barrier()
        session, ctf_parameters, micrograph_files = self.setup_database_and_ctfinfo(micrograph_files)
        
        micrograph_files = self.insure_that_every_node_has_the_same_number_of_micrographs(micrograph_files)
        
        self.log.plog(10)
        for each_micrograph_index, each_micrograph_file in enumerate(micrograph_files):
            if each_micrograph_file != 'place_holder':
                ctffind_parameters, ctftilt_parameters = \
                self.run_ctffind_and_ctftilt_for_each_micrograph(micrograph_files, outfiles, each_micrograph_index,
                each_micrograph_file)
            else:
                np_ctffind = self.make_ctffind_parameters_named_tuple()
                ctffind_parameters = np_ctffind._make(4 * [None])
                ctftilt_parameters = self.make_empty_ctftilt_parameters()
            
            self.comm.barrier()
            
            ctffinds = OpenMpi().convert_list_of_namedtuples_to_list_of_lists([ctffind_parameters])
            ctftilts = OpenMpi().convert_list_of_namedtuples_to_list_of_lists([ctftilt_parameters])
            
            those_micrographs = self.comm.gather(each_micrograph_file, root=0)
            ctffinds = self.comm.gather(ctffinds, root=0)
            ctftilts = self.comm.gather(ctftilts, root=0)
            if self.rank == 0:
                ctffinds = OpenMpi().merge_sequence_of_sequences(ctffinds)
                ctftilts = OpenMpi().merge_sequence_of_sequences(ctftilts)
                ctffind_tuple = self.make_ctffind_parameters_named_tuple()
                
                ctffind_params_combined_list = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(ctffinds,
                ctffind_tuple)
                
                ctftilt_tuple = self.make_ctftilt_parameters_named_tuple()
                
                ctftilt_params_combined_list = OpenMpi().convert_list_of_lists_to_list_of_provided_namedtuple(ctftilts,
                ctftilt_tuple)
            
                zipped_info = zip(those_micrographs, ctffind_params_combined_list, ctftilt_params_combined_list)
                for that_micrograph_file, each_ctffind, each_ctftilt in zipped_info:
                    if each_ctffind.defocus1 is not None:
                        session = self.enter_ctffind_values_in_database(session, that_micrograph_file,
                        self.ori_pixelsize, ctf_parameters, each_ctffind)
            
                    if each_ctftilt.defocus1 is not None:
                        session = self.enter_ctftilt_values_in_database(session, that_micrograph_file,
                        ctf_parameters.pixelsize, each_ctftilt)
            
                session.commit()
        
        self.ctftilt_parameters = ctftilt_parameters
        

    def determine_ctf(self):
        self.startup_scan_mpi_programs()
        
        if self.micrograph_files != []:
            self.run_ctffind_and_ctftilt_for_given_micrographs(self.micrograph_files, self.outfiles)
        
        self.comm.barrier()
                
        self.end_scan_mpi_programs()

def main():
    parset = MicCtfDeterminePar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    micrograph = MicCtfDetermineMpi(reduced_parset)
    micrograph.determine_ctf()


if __name__ == '__main__':
    main()
