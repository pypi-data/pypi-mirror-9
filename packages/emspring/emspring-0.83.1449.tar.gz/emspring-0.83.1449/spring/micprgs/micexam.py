# Author: Carsten Sachse 26-Jan-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
""" 
Program to examine micrograph quality by computing a localized power spectrum
using EMAN2's e2scaneval.py and an averaged power spectrum from overlapping 
tiles using SPARX' sx_welch_pw2.py
"""

from EMAN2 import Region, EMData, Util, EMNumPy
from filter import filt_gaussl
from fundamentals import image_decimate, welch_pw2
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import DiagnosticPlot, Temporary, OpenMpi
from spring.csinfrastr.csreadinput import OptHandler
from spring.micprgs.scansplit import Micrograph
from spring.segment2d.segmentexam import SegmentExam
from utilities import model_circle
import matplotlib.cm as cm
import matplotlib.font_manager as font_manager
import matplotlib.image as mpimg
import numpy as np
import os


class MicrographExamPar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'micexam'
        self.proginfo = __doc__
        self.code_files = [self.progname, self.progname + '_mpi']

        self.micexam_features = Features()
        self.feature_set = self.micexam_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    
    def define_parameters_and_their_properties(self):
        
        self.feature_set = self.micexam_features.set_inp_multiple_micrographs(self.feature_set)
        self.feature_set = self.micexam_features.set_output_plot_pattern(self.feature_set, self.progname + '_diag.pdf')
    
        self.feature_set = self.micexam_features.set_pixelsize(self.feature_set)
        self.feature_set = self.micexam_features.set_power_tile_size(self.feature_set)
        self.feature_set = self.micexam_features.set_tile_overlap(self.feature_set)
        self.feature_set = self.set_complete_tile_array_option(self.feature_set)
        self.feature_set = self.micexam_features.set_binning_option(self.feature_set, default=True)
        self.feature_set = self.micexam_features.set_binning_factor(self.feature_set, binfactor=3)

        self.feature_set = self.micexam_features.set_mpi(self.feature_set)
        self.feature_set = self.micexam_features.set_ncpus_scan(self.feature_set)
        self.feature_set = self.micexam_features.set_temppath(self.feature_set)

    def define_program_states(self):
        self.feature_set.program_states['readmic']='Read input micrograph'
        self.feature_set.program_states['e2scaneval']='e2scaneval.py computes local powerspectra across micrograph'
        self.feature_set.program_states['computepower']='Compute powerspectrum of overlapping tiles'
        self.feature_set.program_states['visualize_power']='Visualize powerspectrum'


    def set_complete_tile_array_option(self, feature_set):
        inp6 = 'Complete tile array option'
        feature_set.parameters[inp6] = bool(False)
        feature_set.hints[inp6] = 'A complete array of tiles with no gaps will be generated across the micrograph'
        feature_set.level[inp6]='expert'
        
        return feature_set
    

class MicrographExamEval(object):
    """
    * Class that holds functions for examining micrograph quality

    * __init__ Function to read in the entered parameter dictionary and load micrograph

    #. Usage: MicrographExam(pardict)
    #. Input: pardict = OrderedDict of program parameters
    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.infile=p['Micrographs']
            self.micrograph_files = Features().convert_list_of_files_from_entry_string(self.infile)
            self.outfile = p['Diagnostic plot pattern']
            self.ori_pixelsize = p['Pixel size in Angstrom']
            self.tile_size_A = p['Tile size power spectrum in Angstrom']
            self.tile_overlap = p['Tile overlap in percent']
            self.fullarropt = p['Complete tile array option']
            self.binoption = p['Binning option']
            self.binfactor = p['Binning factor']
            if self.binfactor == 1 and self.binoption is True:
                self.binoption = False
            
            self.temppath=p['Temporary directory']
            self.mpi_option = p['MPI option']
            self.cpu_count = p['Number of CPUs']


    def bin_micrograph(self, each_micrograph_file, binoption, binfactor, ori_pixelsize, tile_size_A=None, tempdir=None):
        if binoption:
            if tempdir is not None:
                temp_binned = os.path.join(tempdir, os.path.basename(each_micrograph_file))
            else:
                temp_binned = None
            each_micrograph_file, segsizepix = SegmentExam().bin_image_stack_by_binfactor(each_micrograph_file,
            binfactor, binned_stack=temp_binned)
            
            pixelsize = ori_pixelsize * binfactor
        else:
            pixelsize = ori_pixelsize
            
        if tile_size_A is not None:
            tile_size = 2 * int(tile_size_A / (2 * pixelsize))
        else:
            tile_size = None
        
        return each_micrograph_file, pixelsize, tile_size
    

    def prepare_parameters_for_tiling(self, tilesize, pixelsize):
        nx = self.nx
        ny = self.ny
        if 1.1 < pixelsize < 3.5:
            binfactor = int(7.0 / pixelsize + 0.5)
        elif pixelsize <= 1.1:
            binfactor = 6
        elif pixelsize >= 3.5:
            binfactor = 1
            
        if binfactor >= 2:
            powermic = image_decimate(self.img, binfactor)
            tilesize = tilesize / binfactor
            nx = powermic.get_xsize()
            ny = powermic.get_ysize()
            self.log.ilog('Micrograph %s was binned %d x for local power spectra analysis' % (self.infile, binfactor))
            self.log.dlog('e2scaneval: tilesize:%g, nx: %g, ny: %g' % (tilesize, nx, ny))
        else:
            powermic = EMData(self.img) # duplicate img object
        powermic.del_attr('bitspersample')
        powermic.del_attr('datatype')
        sigma = powermic.get_attr('sigma')
        
        return nx, ny, tilesize, powermic, sigma


    def adjust_columns_and_rows_depending_on_array_option(self, tilesize, fullarropt, nx, ny):
        if fullarropt is True:
            box_count_columns = nx / int(tilesize) # number of boxes in x
            separation_columns = tilesize # separation between boxes
            box_count_rows = ny / int(tilesize)
            separation_rows = tilesize
        elif fullarropt is False:
            box_count_columns = nx / int(1.5 * tilesize) # number of boxes in x
            box_count_rows = ny / int(1.5 * tilesize)
            self.log.dlog('{0}, {1}, {2}, {3}'.format(nx, ny, box_count_columns, box_count_rows))
            separation_columns = tilesize * 3 / 2 + (nx % (tilesize * 3 / 2)) / box_count_columns - 1 # separation between boxes
            separation_rows = tilesize * 3 / 2 + (ny % int(1.5 * tilesize)) / box_count_rows
            
        return box_count_columns, box_count_rows, separation_columns, separation_rows


    def insert_tiles_onto_micrograph(self, tilesize, powermic, sigma, box_count_columns, box_count_rows,
    separation_columns, separation_rows):
        for x in range(box_count_columns):
            for y in range(box_count_rows):
                
                cl = powermic.get_clip(Region(x * separation_columns + (separation_columns - tilesize) / 2, y * \
                separation_rows + (separation_rows - tilesize) / 2, tilesize, tilesize))
                
                cl.process_inplace('normalize.edgemean')
                cl.process_inplace('math.realtofft')
                cl.process_inplace('normalize.edgemean')
                try:
                    cl *= 5.0 * float(sigma) / float(cl.get_attr('sigma'))                 
                except:
                    pass
                powermic.insert_clip(cl, (x * separation_columns + (separation_columns - tilesize) / 2, y * \
                separation_rows + (separation_rows - tilesize) / 2, 0))
                
                self.log.ilog('Power spectrum added in column %d and row %d' % (x, y))
                
        return powermic
    

    def e2scaneval(self, tilesize, fullarropt, pixelsize):
        """
        * Function to use EMAN2's e2scaneval.py
        
        #. Usage: output1 = e2scaneval(tilesize)
        #. Input: tilesize in pixels
        #. Output: MRC file with 'eval' appended
        """
        self.log.fcttolog()

        nx, ny, tilesize, powermic, sigma = self.prepare_parameters_for_tiling(tilesize, pixelsize)
        
        box_count_columns, box_count_rows, separation_columns, separation_rows = \
        self.adjust_columns_and_rows_depending_on_array_option(tilesize, fullarropt, nx, ny)

        powermic = self.insert_tiles_onto_micrograph(tilesize, powermic, sigma, box_count_columns, box_count_rows,
        separation_columns, separation_rows)

        self.evalpng = self.tempdir + 'eval.png'
        powermic.write_image(self.evalpng)
        
        return self.evalpng
    

class MicrographExamExtract(MicrographExamEval):
    def enhance_ps(self, powerspec, tilesize):
        """
        * Function that enhances power spectrum by compensating against decay of amplitudes

        #. Usage: output = enhance_ps(powerspec)
        #. Input: 2D powerspec
        #. Output: 2D powerspec compensated for decay of amplitudes
        """

        radius = (tilesize*0.03)
        mask = model_circle(int(radius), int(tilesize), int(tilesize), nz=1)
        mask = (mask - 1)*(-1)

        pw2rotavg = powerspec.rotavg_i()
        power_filtered = filt_gaussl(powerspec, 0.03)
        
        avg, sigma, minimum_of_power_filtered, maximum_of_power_filtered = \
        Micrograph().get_statistics_from_image(power_filtered)

        if minimum_of_power_filtered <= 0:
            power_filtered += maximum_of_power_filtered*1e-30
        pw2enhance = mask * pw2rotavg / power_filtered

        self.log.ilog('Power spectrum enhanced: dividing by low-pass filtered rotational average')

        return pw2enhance, pw2rotavg, mask


    def reduce_twod2oned(self, rotpowspec):
        """
        * Function to reduce 2D rotational power spectrum to 1D image

        #. Usage: output = reduce_twod2oned(rotpowspec)
        #. Input: 2D power spectrum
        #. Output: 1D power spectrum
        """

        nx = rotpowspec.get_xsize()
        pw2line = rotpowspec.get_col(nx/2)
        pw2redline = Util.window(pw2line, nx/2, 1, 1, nx/4, 0, 0) 

        return pw2redline
    

    def compute_power_spectra(self, mic, pixelsize, tilesize, tile_overlap):
        """
        * Function to compute rotational power spectrum

        #. Usage: compute_power_spectra
        """
        self.log.fcttolog()

        edge=int(0.05*mic.get_xsize())
        binfactor = int(2.5/pixelsize + 0.5)
        if binfactor >= 2:
            welchmic = image_decimate(mic, binfactor)
            tilesize = tilesize/binfactor
            edge = edge/binfactor
            self.log.ilog('Micrograph %s was binned %gx for high-resolution 1D analysis' %
                          (self.infile, binfactor))
            pixelsize = pixelsize*binfactor
        else:
            welchmic = EMData(mic)

        pw2 = welch_pw2(welchmic, tilesize, tile_overlap, tile_overlap, edge, edge)

        # compute 1D rotational average
        pw2rops = pw2.rotavg()
        pw2oned = np.copy(EMNumPy.em2numpy(pw2rops))
        self.log.ilog('1D rotational power spectrum computed')

        # enhance 1D rotational power spec
        pw2enhance, pw2rotavg, mask = self.enhance_ps(pw2, tilesize)
        pw2redline = self.reduce_twod2oned(pw2enhance)
        pw2lineenh = np.copy(EMNumPy.em2numpy(pw2redline))
        self.log.ilog('1D rotational power spectrum enhanced')

        # mask 2D power spectrum
        pw2 = pw2 * mask * (-1)
        pw2sum = self.tempdir + 'pw2.png'
        pw2.write_image(pw2sum)
        self.log.ilog('Power spectrum computed: %s' %pw2sum)

        # mask 2D rotational avg power spectrum
        pw2rotavg = pw2rotavg*mask*(-1)
        pw2sumrotavg = self.tempdir + 'pw2_rotavg.png'
        pw2rotavg.write_image(pw2sumrotavg)

        self.log.ilog('Power spectrum rotationally averaged computed: %s' %pw2sumrotavg)
        
        return pw2sum, pw2sumrotavg, pw2oned, pw2lineenh
    

class MicrographExam(MicrographExamExtract):
    
    def add_entire_micrograph_with_power_tile_overlay(self, evalpng, infile, ax1):
        # ax1
        evalimg = mpimg.imread(evalpng)
        ax1.imshow(evalimg, cmap=cm.gray, interpolation='nearest')
        os.remove(evalpng)
        self.log.ilog('Micrograph %s included in montage' % infile)
        
        return ax1


    def add_sum_of_overlapping_powerspectra(self, pw2sum, ax2):
        # ax2
        ax2.set_title('Sum of overlapping power spectra')
        twodpow = mpimg.imread(pw2sum)
        ax2.imshow(twodpow, cmap=cm.gray, interpolation='nearest')
        os.remove(pw2sum)
        self.log.ilog('Sum of power spectra included')
        
        return ax2


    def add_rotational_avg_of_above(self, pw2sumrotavg, ax3):
        # ax3
        ax3.set_title('Rotational avg of above')
        two2davg = mpimg.imread(pw2sumrotavg)
        ax3.imshow(two2davg, cmap=cm.gray)
        os.remove(pw2sumrotavg)
        self.log.ilog('Rotational average included in montage')
        
        return ax3


    def add_one_dimensional_power_spectra(self, pw2oned, pw2lineenh, pixelsize, ax4):
        # ax4
        ax4.set_title('Power spectra profile of above')
        ax4.title.set_fontsize(9)
        ax4.set_yticks([])
        for t in ax4.get_xticklabels():
            t.set_fontsize(6)
        
        ax4.set_xlabel('Resolution (1/Angstrom)', fontsize=8)
#        linex = np.arange(1, 1 + len(pw2oned))
#        linex = linex / (len(linex) * 2 * pixelsize)
        linex = np.linspace(0, 1/(2 * pixelsize), len(pw2oned))
        pw2oned = pw2oned / max(pw2oned)
        ax4.plot(linex, pw2oned, linewidth=.2)
        
#        linex = self.compute_one_over_angstrom_line(pw2lineenh, pixelsize)
        linex = np.linspace(0, 1/(2 * pixelsize), len(pw2lineenh))
        ax4.plot(linex, pw2lineenh, linewidth=0.2, label='enhanced')
        ax4.set_xlim(0, linex[-1])
        ax4.legend(loc=(0.2, -0.5), prop=font_manager.FontProperties(size='x-small'))
        self.log.ilog('One-dimensional profiles included in montage')
        
        return ax4
    

    def visualize_power(self, evalpng, pw2sum, pw2sumrotavg, pw2oned, pw2lineenh, pixelsize, infile, outfile):
        """
        * Function to visualize power analysis of micrograph

        #. Usage: fig = visualize_power(evalpng, pw2sum, pw2sumrotavg, pw2oned, pw2lineenh)
        #. Input: evalpng = micrograph montage from e2scaneval.py, pw2sum = computed sum of \
            overlapping powerspectra, pw2sumrotavg = rotational average of sum, pw2oned = \
            1D profile of rotational average, pw2lineenh = enhanced 1D profile comensated \
            against amplitude decay
        """
        self.log.fcttolog()

        micexam_plot = DiagnosticPlot()
        ax1 = micexam_plot.plt.subplot2grid((3,3), (0,0), colspan=2, rowspan=3)
        ax2 = micexam_plot.plt.subplot2grid((3,3), (0,2), colspan=1, rowspan=1)
        ax3 = micexam_plot.plt.subplot2grid((3,3), (1,2), colspan=1, rowspan=1)
        ax4 = micexam_plot.plt.subplot2grid((3,3), (2,2), colspan=1, rowspan=1)

        self.fig = micexam_plot.add_header_and_footer(self.feature_set, infile, outfile)
        
        ax1 = self.add_entire_micrograph_with_power_tile_overlay(evalpng, infile, ax1)
        ax2 = self.add_sum_of_overlapping_powerspectra(pw2sum, ax2)
        ax3 = self.add_rotational_avg_of_above(pw2sumrotavg, ax3)

        for plot in (ax1, ax2, ax3):
            plot.set_xticks([]); plot.set_yticks([])
            plot.title.set_fontsize(9)

        ax4 = self.add_one_dimensional_power_spectra(pw2oned, pw2lineenh, pixelsize, ax4)

        self.log.ilog('Montage %s written.' %outfile)
        self.fig.savefig(outfile, orientation='landscape', dpi=400)

        return self.fig
    

    def examine_scans_computing_total_and_local_powerspectra(self, micrograph_files, outfiles):
        
        self.log.plog(10)
        for each_micrograph_index, each_micrograph_file in enumerate(micrograph_files):
            each_micrograph_file, self.pixelsize, self.tilesize = self.bin_micrograph(each_micrograph_file,
            self.binoption, self.binfactor, self.ori_pixelsize, self.tile_size_A, self.tempdir)
            
            self.img, self.nx, self.ny = Micrograph().readmic(each_micrograph_file)
            eval_png = self.e2scaneval(self.tilesize, self.fullarropt, self.pixelsize)
            
            pw2sum, pw2sumrotavg, pw2oned, pw2lineenh = self.compute_power_spectra(self.img, self.pixelsize,
            self.tilesize, self.tile_overlap)
            
            self.visualize_power(eval_png, pw2sum, pw2sumrotavg, pw2oned, pw2lineenh, self.pixelsize,
            each_micrograph_file, outfiles[each_micrograph_index])
            
            if self.binoption:
                os.remove(each_micrograph_file)
            self.log.plog((each_micrograph_index + 1) * 100.0 / len(micrograph_files))
        
    
    def exam_scans(self):
        if len(self.micrograph_files) < self.cpu_count:
            self.cpu_count = len(self.micrograph_files)
            self.feature_set.parameters['Number of CPUs']=self.cpu_count
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        self.tempdir = Temporary().mktmpdir(self.temppath)
        
        outfiles = Features().rename_series_of_output_files(self.micrograph_files, self.outfile)
        
        self.examine_scans_computing_total_and_local_powerspectra(self.micrograph_files, outfiles)
        
        os.rmdir(self.tempdir)
        self.log.endlog(self.feature_set)
        
def main():
    # Option handling
    parset = MicrographExamPar()
    mergeparset = OptHandler(parset)

    ######## Program
    micrograph = MicrographExam(mergeparset)
    micrograph.exam_scans()

if __name__ == '__main__':
    main()
