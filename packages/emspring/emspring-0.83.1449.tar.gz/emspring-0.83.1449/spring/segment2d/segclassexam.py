# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to examine helix classes to compute their collapsed (1D) and 2D power spectrum and width profile of helices
"""
from EMAN2 import EMData, EMUtil, Util, periodogram
from matplotlib.backends.backend_pdf import PdfPages, FigureCanvasPdf
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import OpenMpi, Temporary
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segmentexam import SegmentExamPar, SegmentExam
import os
from utilities import model_blank


class SegClassExamPar(SegmentExamPar):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'segclassexam'
        self.proginfo = __doc__
        self.code_files = [self.progname, self.progname + '_mpi']

        self.segclassexam_features = Features()
        self.feature_set = self.segclassexam_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    
    def define_parameters_and_their_properties(self):
        self.feature_set = self.segclassexam_features.set_class_avg_stack(self.feature_set)
        self.feature_set = self.segclassexam_features.set_output_plot(self.feature_set, self.progname + '_diag.pdf')

        self.feature_set = self.set_class_var_option(self.feature_set)
        self.feature_set = self.set_class_var_stack(self.feature_set)
        
        self.feature_set = self.segclassexam_features.set_output_power_spectrum(self.feature_set)
        self.feature_set = self.segclassexam_features.set_enhance_power_option(self.feature_set)
        self.feature_set = self.segclassexam_features.set_output_enhanced_power_spectrum(self.feature_set)
        self.feature_set = self.segclassexam_features.set_pixelsize(self.feature_set)
        self.feature_set = self.segclassexam_features.set_helix_width(self.feature_set)
        self.feature_set = self.segclassexam_features.set_power_cutoff(self.feature_set)
        self.feature_set = self.segclassexam_features.set_class_number_range_to_be_analyzed(self.feature_set)
        
        self.feature_set = self.segclassexam_features.set_mpi(self.feature_set)
        self.feature_set = self.segclassexam_features.set_ncpus(self.feature_set)
        self.feature_set = self.segclassexam_features.set_temppath(self.feature_set)


    def define_program_states(self):
        super(SegClassExamPar, self).define_program_states()

        self.feature_set.program_states['prepare_segclassexam']='Prepare classes for analysis.'
        self.feature_set.program_states['perform_class_examination']='Extract classes, profiles and power spectra.'
        self.feature_set.program_states['print_figures']='Save diagnostic plots to file.'


    def set_class_var_option(self, feature_set):
        inp2 = 'Class variance option'
        feature_set.parameters[inp2] = False
        feature_set.hints[inp2] = 'Check if variances of classes are to be analyzed.'
        feature_set.level[inp2]='intermediate'
        
        return feature_set


    def set_class_var_stack(self, feature_set):
        inp2 = 'Class variance stack'
        feature_set.parameters[inp2] = 'variances.hdf'
        feature_set.properties[inp2] = self.file_properties(1, ['spi', 'hdf', 'img', 'hed'], 'getFile')
        feature_set.hints[inp2] = 'Stack: accepted image file formats (%s)' % \
        (', '.join(feature_set.properties[inp2].ext))
        feature_set.level[inp2]='intermediate'
        feature_set.relatives[inp2]='Class variance option'
        
        return feature_set


class SegClassExam(SegmentExam):
    """
    * Class that holds functions for examining segments from micrographs

    * __init__ Function to interpret multi-input parameters

    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.avgstack = p['Class average stack']
            self.infile = self.avgstack
            self.outfile = p['Diagnostic plot']
            self.cls_var_option = p['Class variance option']
            self.varstack = p['Class variance stack']
            
            self.power_img = p['Power spectrum output image']
            self.enhanced_power_option = p['Enhanced power spectrum option']
            self.power_enhanced_img = p['Enhanced power spectrum output image']
            self.ori_pixelsize = p['Pixel size in Angstrom']
            self.helixwidth = p['Estimated helix width in Angstrom']
            self.helixwidthpix = int(round(self.helixwidth / self.ori_pixelsize))
            self.rescutoff = p['Power spectrum resolution cutoff in 1/Angstrom']
            self.classno_range = p['Class number range to be analyzed']

            self.binfactor = int(round(1/(self.rescutoff * self.ori_pixelsize * 2)))

            self.stack = EMData()
            self.stack.read_image(self.avgstack, 0)
            self.segsizepix = self.stack.get_xsize()
            if self.binfactor > 1:
                self.avgstack, self.segsizepix, self.helixwidthpix, self.pixelsize = \
                SegmentExam().apply_binfactor(self.binfactor, self.avgstack, self.segsizepix, self.helixwidthpix,
                self.ori_pixelsize)
                                
                self.helixwidthpix *= self.binfactor
                self.pixelsize = self.ori_pixelsize / float(self.binfactor)
                
                if self.cls_var_option:
                    self.varstack, segsizepix, helixwidthpix, pixelsize = \
                    SegmentExam().apply_binfactor(self.binfactor, self.varstack, self.segsizepix, self.helixwidthpix, 
                    self.ori_pixelsize)

            self.mpi_option = p['MPI option']
            self.cpu_count = p['Number of CPUs']
            self.temppath = p['Temporary directory']


    def display_helix_width_and_normal_profile(self, avg, var):
        widthavg = self.project_helix(avg)
        widthvar = self.project_helix(var)
        self.ax2.set_title('Helix width profile', fontsize=8)
        self.ax2 = self.add_width_profile_from_avg_and_var(widthavg, widthvar, self.pixelsize, self.ax2)
        self.log.ilog('Width profile of average segment included in montage')
        
        vertical_avg = self.project_normal_to_helix(avg)
        vertical_var = self.project_normal_to_helix(var)
        self.ax4.set_title('Helix normal profile', fontsize=8)
        self.ax4 = self.add_width_profile_from_avg_and_var(vertical_avg, vertical_var, self.pixelsize, self.ax4, 'normal')
        self.log.ilog('Normal profile of average segment included in montage')

    
    def check_maximum_class_number(self, avgstack, classno_range):
        max_class_number = EMUtil.get_image_count(avgstack) - 1
        if max_class_number < classno_range[1]:
            msg = 'Class average stack does not have specified class number. Therefore class number range is ' + \
            'corrected to available class numbers, i.e. {0}.'.format(max_class_number)
            
            classno_range = ((classno_range[0], max_class_number))
            self.log.wlog(msg)
            
        return classno_range


    def prepare_segclassexam(self):
        self.log.fcttolog()
        self.helixmask = self.make_smooth_rectangular_mask(self.helixwidthpix, 0.7 * self.segsizepix, self.segsizepix, 
        width_falloff=0.15)

        self.classno_range = self.check_maximum_class_number(self.avgstack, self.classno_range)
        classno_start, classno_end = self.classno_range
        self.log.plog(10)

        return classno_start, classno_end


    def rename_plot_title_for_multiple_classes(self, infile, outfile, classno_start, classno_end, each_class_index,
    feature_set):
        class_file = '{0}_class{1:04}{2}'.format(os.path.splitext(infile)[0], each_class_index,
        os.path.splitext(infile)[-1])
        
        plot_file = '{0}_class{1:04}{2}'.format(os.path.splitext(outfile)[0], each_class_index,
        os.path.splitext(outfile)[-1])
        
        feature_set.parameters[list(feature_set.parameters.keys())[0]] = class_file
        feature_set.parameters[list(feature_set.parameters.keys())[1]] = plot_file
                
        return plot_file, feature_set


    def perform_class_examination(self, avgstack, varstack, classno_start, classno_end, power_img, power_enhanced_img):
        self.log.fcttolog()

        figures = []
        avg = EMData()
        var = EMData()
        
        classes_iter = list(range(classno_start, classno_end + 1))
        for each_cls_id, each_class in enumerate(classes_iter):
            if len(classes_iter) > 1:
                plot_file, self.feature_set = self.rename_plot_title_for_multiple_classes(self.infile, self.outfile,
                classno_start, classno_end, each_class, self.feature_set)
            else:
                plot_file = self.outfile

            fig = self.setup_fourxtwo()
            avg.read_image(avgstack, each_class)
            avg *= self.helixmask

            if self.cls_var_option:
                var.read_image(varstack, each_class)
            else:
                var = model_blank(avg.get_xsize(), avg.get_ysize(), 1)

            self.display_average_and_variance(avg, var)
            self.display_helix_width_and_normal_profile(avg, var)

            padsize = 4 * avg.get_xsize()
            padded_avg = Util.pad(avg, padsize, padsize, 1, 0, 0, 0, '0')
            avg_periodogram = periodogram(padded_avg)
            avg_periodogram.set_attr('cls', each_class)
            avg_periodogram.write_image(power_img, each_cls_id)

            avg_periodogram_enhanced = self.enhance_power(avg_periodogram, self.pixelsize)
            if self.enhanced_power_option:
                avg_periodogram_enhanced.set_attr('cls', each_class)
                avg_periodogram_enhanced.write_image(power_enhanced_img, each_cls_id)

            self.log.plog(30 * (each_class + 0.5 - 1) / (classno_end + 1) + 10)

            avg_collapsed_power_line = self.collapse_power(avg_periodogram)
            avg_collapsed_line_enhanced = self.collapse_power(avg_periodogram_enhanced)

            self.display_power_spectra_enhanced_and_collapsed(avg_periodogram, avg_periodogram_enhanced,
            avg_collapsed_power_line, avg_collapsed_line_enhanced)

            figures.append((fig, plot_file))
            self.log.plog(30 * (each_class) / (classno_end + 1) + 10)
        
        return figures


    def print_figures(self, figures):
        self.log.fcttolog()
        if os.path.splitext(self.outfile)[-1].endswith('pdf') and not hasattr(self, 'comm'):
            pdf = PdfPages(self.outfile)

        for each_id, (each_fig, each_plot_file) in enumerate(figures):
            if os.path.splitext(self.outfile)[-1].endswith('pdf') and not hasattr(self, 'comm'):
                canvas = FigureCanvasPdf(each_fig) 
                each_fig.savefig(pdf, format='pdf')
            elif not os.path.splitext(self.outfile)[-1].endswith('pdf') and len(figures) > 1 or \
            os.path.splitext(self.outfile)[-1].endswith('pdf') and hasattr(self, 'comm'):
                each_fig.savefig(each_plot_file, dpi=600)
            else:
                each_fig.savefig(self.outfile, dpi=600)
            self.log.ilog('The diagnostic plot {0} was added.'.format(each_plot_file))
            self.log.plog(60 * (each_id) / (len(figures)) + 40)

        if os.path.splitext(self.outfile)[-1].endswith('pdf') and not hasattr(self, 'comm'):
            pdf.close()
            self.log.ilog('The diagnostic plot {0} was saved.'.format(self.outfile))


    def print_figures_and_finish(self, figures):
        self.print_figures(figures)
        os.rmdir(self.tempdir)
        self.log.endlog(self.feature_set)


    def exam_classes(self):
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        self.tempdir = Temporary().mktmpdir(self.temppath)

        classno_start, classno_end = self.prepare_segclassexam()

        figures = self.perform_class_examination(self.avgstack, self.varstack, classno_start, classno_end,
        self.power_img, self.power_enhanced_img)

        self.print_figures_and_finish(figures)


def main():
    # Option handling
    parset = SegClassExamPar()
    mergeparset = OptHandler(parset)

    ######## Program
    stack = SegClassExam(mergeparset)
    stack.exam_classes()

if __name__ == '__main__':
    main()
