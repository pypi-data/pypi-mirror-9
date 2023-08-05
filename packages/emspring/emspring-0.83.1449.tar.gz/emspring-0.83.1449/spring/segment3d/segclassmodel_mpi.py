# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from spring.csinfrastr.csproductivity import OpenMpi
from spring.segment3d.segclassmodel import SegClassModelPar, SegClassModel
import json
import os


class SegClassModelMpi(SegClassModel):
    def prepare_merged_stack_of_projections_mpi(self):
        sr3d = self.prepare_sr3d_object_with_filter_settings()

        projection_size, projection_info = self.prepare_prj_through_series_of_models()

        for each_model_id, each_reference in enumerate(self.references):
            if self.rank == 0:
                reference_info, pixelinfo = self.prepare_volume_for_projection(projection_size, sr3d, each_model_id, each_reference)
                
                reference_info = list(reference_info)
                pixelinfo = list(pixelinfo)
            else:
                reference_info = None
                pixelinfo = None
            
            reference_info = self.comm.bcast(reference_info, root=0)
            pixelinfo = self.comm.bcast(pixelinfo, root=0)
            
            pixelinfo_nt = sr3d.make_pixel_info_named_tuple()
            reference_info_nt = sr3d.make_reference_info_named_tuple()
            
            pixelinfo = pixelinfo_nt._make(pixelinfo)
            reference_info = reference_info_nt._make(reference_info)

            projection_stack, projection_parameters, fine_projection_stack, fine_projection_parameters = \
            sr3d.project_through_reference_volume_in_helical_perspectives('medium', reference_info.model_id,
            reference_info.ref_file, pixelinfo, reference_info.helical_symmetry, reference_info.rotational_symmetry)

            if self.rank == 0:
                projection_info = self.summarize_prj_info(projection_info, each_model_id, projection_stack,
                projection_parameters)
            
            self.comm.barrier()
        
        if self.rank == 0:
            merged_prj_stack, projection_info = self.merge_prj_stacks_and_collect_prj_info(projection_info)

            dfile = open('prj_info.dat', 'w')
            json.dump(projection_info, dfile, indent=4, sort_keys=False)
            dfile.close()
        
        else:
            merged_prj_stack = None
            projection_info = None

        self.comm.barrier()

        return  merged_prj_stack, projection_info


    def match_reprojections_to_classes(self):
        self.comm, self.rank, self.size, self.log, self.tempdir = OpenMpi().setup_mpi_and_simultaneous_logging(self.log,
        self.feature_set.logfile, self.temppath)
        
        merged_prj_stack, prj_info = self.prepare_merged_stack_of_projections_mpi()
        
        os.rmdir(self.tempdir)
        if self.rank == 0:
            self.log.endlog(self.feature_set)
        

def main():
    parset = SegClassModelPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    class_average = SegClassModelMpi(reduced_parset)
    class_average.match_reprojections_to_classes()


if __name__ == '__main__':
    main()
