# Author: Carsten Sachse 25-Dec-2013
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from spring.csinfrastr.csproductivity import OpenMpi
from spring.segment2d.segclassexam import SegClassExam, SegClassExamPar
import os


class SegClassExamMpi(SegClassExam):
    
    def prepare_segclassexam_mpi(self):
        self.comm, self.rank, self.size, self.log, self.tempdir = OpenMpi().setup_mpi_and_simultaneous_logging(self.log,
        self.feature_set.logfile, self.temppath)
        
        classno_start, classno_end = self.prepare_segclassexam()
        if self.rank == 0:
            classes = list(range(classno_start, classno_end + 1))
            classes = OpenMpi().split_sequence_evenly(classes, self.size)
        else:
            classes = None
        
        classes = self.comm.scatter(classes, root=0)

        return classes[0], classes[-1]


    def collect_powers_and_print_figures_and_finish_mpi(self, figures):

        power_img, power_img_enh = self.get_local_power_stacks()
        OpenMpi().gather_stacks_from_cpus_to_common_stack(self.comm, power_img, self.power_img)
        OpenMpi().gather_stacks_from_cpus_to_common_stack(self.comm, power_img_enh, self.power_enhanced_img)
    
        self.print_figures(figures)
        self.comm.barrier()

        os.rmdir(self.tempdir)
        if self.rank == 0:
            self.log.endlog(self.feature_set)


    def get_local_power_stacks(self):
        power_img = os.path.join(self.tempdir, self.power_img)
        power_img_enh = os.path.join(self.tempdir, self.power_enhanced_img)
        return power_img, power_img_enh

    def exam_classes(self):
        classno_start, classno_end = self.prepare_segclassexam_mpi()
        power_img, power_img_enh = self.get_local_power_stacks()

        figures = self.perform_class_examination(self.avgstack, self.varstack, classno_start, classno_end, power_img,
        power_img_enh)

        self.collect_powers_and_print_figures_and_finish_mpi(figures)

def main():
    parset = SegClassExamPar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    stack = SegClassExamMpi(reduced_parset)
    stack.exam_classes()

if __name__ == '__main__':
    main()
