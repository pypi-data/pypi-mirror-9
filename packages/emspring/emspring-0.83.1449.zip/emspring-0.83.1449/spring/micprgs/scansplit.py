# Author: Carsten Sachse 07-Dec-2010
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to split large scan into individual micrographs. The location of 
individual micrographs is determined by a dummy micrograph reference.
"""
from EMAN2 import EMData, Util, EMNumPy
from collections import namedtuple
from fundamentals import ccfn, image_decimate, mirror
from morphology import threshold_outside
from spring.csinfrastr.csfeatures import Features, FeaturesSupport
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import DiagnosticPlot, Temporary, OpenMpi
from spring.csinfrastr.csreadinput import OptHandler
from utilities import peak_search, model_blank
import matplotlib.cm as cm
import numpy as np
import os
import sys


class Micrograph(object):
    def readmic(self, inputimg):
        """
        * Function to load micrograph and define sizes

        #. Usage: img, nx, ny = readmic(inputimg)
        #. Input: inputimg
        #. Output: image, x and y dimension

        """
        log = Logger()
        log.fcttolog()

        img = EMData()
        img.read_image(inputimg)
        log.ilog('Input micrograph read: %s' %inputimg)

        nx = img.get_xsize()
        ny = img.get_ysize()
        
        return img, nx, ny


    def get_statistics_from_image(self, image, mask=None):
        mean, sigma, imin, imax = Util.infomask(image, mask, True)
        img_stat = namedtuple('image_statistics', 'avg sigma min max')
        statistics = img_stat(mean, sigma, imin, imax)
        
        return statistics
    

    def adjust_gray_values_for_print_and_optimal_display(self, mic):
        stat = self.get_statistics_from_image(mic)
        min_cutoff, max_cutoff = stat.avg - 3.5 * stat.sigma, stat.avg + 3.5 * stat.sigma
        pix_range = stat.max - stat.min
        if stat.avg < stat.min + 0.1 * pix_range:
            min_cutoff = stat.min
        elif stat.avg > stat.min + 0.9 * pix_range:
            max_cutoff = stat.max
            
        adjusted_mic = threshold_outside(mic, min_cutoff, max_cutoff)
        
        return adjusted_mic
    
        
class ScanSplitPar:
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'scansplit'
        self.proginfo = __doc__
        self.code_files = [self.progname, self.progname + '_mpi']

        self.scansplit_features = Features()
        self.feature_set = self.scansplit_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()


    def define_parameters_and_their_properties(self):

        self.feature_set = self.scansplit_features.set_inp_multiple_micrographs(self.feature_set)
        self.feature_set = self.set_mic_out_pattern(self.feature_set)
    
        self.feature_set = self.set_rows_and_cols_count(self.feature_set)
        self.feature_set = self.set_mic_crop_count(self.feature_set)
        self.feature_set = self.set_mic_width_and_height(self.feature_set)
        self.feature_set = self.set_label_width_and_height(self.feature_set)
        self.feature_set = self.scansplit_features.set_scanner_step_size(self.feature_set)
        self.feature_set = self.set_cc_threshold(self.feature_set)
        self.feature_set = self.set_contact_print_option(self.feature_set)
        self.feature_set = self.set_final_print_option(self.feature_set)
        self.feature_set = self.set_normscan_option(self.feature_set)
    
        self.feature_set = self.scansplit_features.set_binning_option(self.feature_set)
        self.feature_set = self.scansplit_features.set_binning_factor(self.feature_set)
        
        self.feature_set = self.scansplit_features.set_mpi(self.feature_set)
        self.feature_set = self.scansplit_features.set_ncpus_scan(self.feature_set)
        self.feature_set = self.scansplit_features.set_temppath(self.feature_set)
    
    def define_program_states(self):
        # status dictionary
        self.feature_set.program_states['readmic']='Read input micrograph'
        self.feature_set.program_states['roughsplit']='Rough splitting of micrograph according to number of rows ' +\
        'and columns'
        self.feature_set.program_states['make_refmic']='Make binary reference micrograph including label'
        self.feature_set.program_states['findlabel']='Find label on micrograph with respect to reference micrograph'
        self.feature_set.program_states['finesplit']='Fine splitting of micrograph according to matched position'
        self.feature_set.program_states['normscan']='Normalize micrograph columns using Niko Grigorieff\'s Normscan'
        self.feature_set.program_states['bin_micrographs']='Bin micrographs by specified factor'
        self.feature_set.program_states['contactprint']='Produce contact print of scan'
        self.feature_set.program_states['finalprint']='Produce final prints of split micrograph'

    def set_mic_out_pattern(self, feature_set):
        inp2 = 'Output micrograph pattern'
        feature_set.parameters[inp2] = 'cs_scan034???.mrc'
        
        feature_set.properties[inp2] = feature_set.file_properties(1, ['jpg', 'tif', 'mrc', 'spi', 'hdf', 'img', 'hed'],
        'saveFile')
        
        feature_set.hints[inp2] = 'If single input micrograph: name of pattern. In case of multiple micrographs ' + \
        'suffix to be attached to corresponding micrograph. Use wildcards cs_scan034\?\?\?.mrc OR cs_scan034*.mrc, ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp2)
        feature_set.level[inp2]='beginner'
        
        return feature_set


    def set_rows_and_cols_count(self, feature_set):
        inp4 = 'Number of columns x rows'
        feature_set.parameters[inp4] = tuple((3, 2))
        feature_set.hints[inp4] = 'Integer value for number of columns x rows of micrographs located on scan.'
        feature_set.properties[inp4] = feature_set.Range(1, 10, 1)
        feature_set.level[inp4]='beginner'
        
        return feature_set


    def set_mic_crop_count(self, feature_set):
        inp5 = 'Number of micrographs to be cropped'
        feature_set.parameters[inp5] = int(6)
        feature_set.hints[inp5] = 'Integer value number of micrographs located on scan (number of rows x number of ' +\
        'columns).'
        feature_set.properties[inp5] = feature_set.Range(1, 100, 1)
        feature_set.level[inp5]='beginner'
        
        return feature_set


    def set_mic_width_and_height(self, feature_set):
        inp6 = 'Micrograph width x height in cm'
        feature_set.parameters[inp6] = tuple((8.0, 9.0))
        feature_set.hints[inp6] = 'Width x height dimension of micrograph in cm.'
        feature_set.properties[inp6] = feature_set.Range(0, 50, 0.1)
        feature_set.level[inp6]='intermediate'
        
        return feature_set


    def set_label_width_and_height(self, feature_set):
        inp7 = 'Label width x height in cm'
        feature_set.parameters[inp7] = tuple((2.7, 1.4))
        feature_set.hints[inp7] = 'Width x height dimension of black label in cm located at bottom of micrograph.'
        feature_set.properties[inp7] = feature_set.Range(0, 10, 0.1)
        feature_set.level[inp7]='expert'
        
        return feature_set


    def set_cc_threshold(self, feature_set):
        inp9 = 'Cross-correlation rejection criterion'
        feature_set.parameters[inp9] = float(1e+4)
        feature_set.hints[inp9] = 'Use the default number to exclude empty positions with no micrograph on scan - ' + \
        'otherwise use with caution.'
        feature_set.properties[inp9] = feature_set.Range(0, 1e+8, 1e+3)
        feature_set.level[inp9]='expert'
        
        return feature_set


    def set_contact_print_option(self, feature_set):
        inp11 = 'Contact print option'
        feature_set.parameters[inp11] = bool(False)
        feature_set.hints[inp11] = 'Option to produce a contact print of the entire scan.'
        feature_set.level[inp11]='intermediate'
        
        return feature_set


    def set_final_print_option(self, feature_set):
        inp12 = 'Final print option'
        feature_set.parameters[inp12] = bool(False)
        feature_set.hints[inp12] = 'Option to produce a final high-contrast print of the cropped micrograph.'
        feature_set.level[inp12]='intermediate'
        
        
        return feature_set


    def set_normscan_option(self, feature_set):
        inp13 = 'Normscan option'
        feature_set.parameters[inp13] = bool(False)
        feature_set.hints[inp13] = 'Option to normalize micrograph columns to eliminate steep grey-value differences '+\
        'in micrograph columns that can be present in Zeiss scans.'
        feature_set.level[inp13]='intermediate'
        
        return feature_set
    

class ScanSplitRough(object):
    """
    * Class that holds all functions required for splitting micrographs 

    * __init__ Function to read in the entered parameter dictionary, load micrograph and initialize \
                    unique temporary directory

    #. Usage: ScanSplit(pardict)
    #. Input: pardict = OrderedDict of program parameters
    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None: 
            self.feature_set = parset
            p = self.feature_set.parameters
            self.infile=p['Micrographs']
            self.micrograph_files = Features().convert_list_of_files_from_entry_string(self.infile)
            self.outfile=p['Output micrograph pattern']
            self.column_count=p['Number of columns x rows'][0]
            self.row_count=p['Number of columns x rows'][1]
            self.mic_count=p['Number of micrographs to be cropped']
            self.mwidth=p['Micrograph width x height in cm'][0]
            self.mheight=p['Micrograph width x height in cm'][1]
            self.lwidth=p['Label width x height in cm'][0]
            self.lheight=p['Label width x height in cm'][1]
            self.scanstep=p['Scanner step size in micrometer']
            self.cc_threshold=p['Cross-correlation rejection criterion']

            self.normscanoption=p['Normscan option']
            self.binoption=p['Binning option']
            self.binfactor=p['Binning factor']
            if self.binfactor == 1 and self.binoption is True:
                self.binoption = False

            self.cprintoption=p['Contact print option']
            self.fprintoption=p['Final print option']

            self.temppath=p['Temporary directory']
            self.mpi_option = p['MPI option']
            self.cpu_count = p['Number of CPUs']


    def roughsplit(self, scanimg, row_count, column_count, no_mics):
        """
        * Function to roughly split scan into micrographs based on given number \
        of rows and columns

        #. Usage: roughsplit(row_count, column_count, mic_count)
        #. Input: number of rows, number of columns, number of micrographs, 
        #. Output: dictionary of roughly windowed micrographs (EMData objects)

        >>> from spring.micprgs.scansplit import ScanSplit
        >>> import numpy as np
        >>> from EMAN2 import EMNumPy
        >>> scanimg = EMNumPy.numpy2em(np.reshape(np.arange(0, 100), (20, 5)))
        >>> mic_one, decfactor = ScanSplit().roughsplit(scanimg, 2, 1, 2)
        >>> np.rint(EMNumPy.em2numpy(mic_one[0]))
        array([[  0.,   1.,   2.,   3.,   4.],
               [  5.,   6.,   7.,   8.,   9.],
               [ 10.,  11.,  12.,  13.,  14.],
               [ 15.,  16.,  17.,  18.,  19.],
               [ 20.,  21.,  22.,  23.,  24.],
               [ 25.,  26.,  27.,  28.,  29.],
               [ 30.,  31.,  32.,  33.,  34.],
               [ 35.,  36.,  37.,  38.,  39.],
               [ 40.,  41.,  42.,  43.,  44.],
               [ 45.,  46.,  47.,  48.,  49.]], dtype=float32)

        >>> scanimg = EMNumPy.numpy2em(np.reshape(np.arange(0, 100), (10, 10)))
        >>> mic_one, decfactor = ScanSplit().roughsplit(scanimg, 1, 2, 2)
        >>> np.rint(EMNumPy.em2numpy(mic_one[0]))
        array([[  0.,   1.,   2.,   3.,   4.],
               [ 10.,  11.,  12.,  13.,  14.],
               [ 20.,  21.,  22.,  23.,  24.],
               [ 30.,  31.,  32.,  33.,  34.],
               [ 40.,  41.,  42.,  43.,  44.],
               [ 50.,  51.,  52.,  53.,  54.],
               [ 60.,  61.,  62.,  63.,  64.],
               [ 70.,  71.,  72.,  73.,  74.],
               [ 80.,  81.,  82.,  83.,  84.],
               [ 90.,  91.,  92.,  93.,  94.]], dtype=float32)
        """
        self.log.fcttolog()

        sizex = scanimg.get_xsize()/column_count
        sizey = scanimg.get_ysize()/row_count

        mic_number = 0 
        miclist = []
        decimation_factor_find = int(sizex/1200) + 1
        for each_row_number in range(row_count):
            for each_column_number in range(column_count):
                centerx = (-column_count + 1)*sizex/2 + each_column_number*sizex 
                centery = (-row_count + 1)*sizey/2 + each_row_number*sizey
                self.log.dlog('centerx: %g, centery: %g'%(centerx, centery))
                splitmic = Util.window(scanimg, sizex, sizey, 1, centerx, centery, 0)
                # bin images to reduce computing time significantly
                if decimation_factor_find > 1:
                    splitmic = image_decimate(splitmic, decimation_factor_find, fit_to_fft=False)
                    self.log.dlog('micgraph was decimated by {0}'.format(decimation_factor_find))
                miclist.append(splitmic)
                self.log.ilog('Micrograph %d roughly windowed' %mic_number)
                mic_number = mic_number + 1

        return miclist, decimation_factor_find
    
    
class ScanSplitFind(ScanSplitRough):

    def make_refmic(self, mwidth = None, mheight = None, lwidth = None, lheight = None, scanstep = None):
        """
        * Function to generate a reference micrograph including black label at \
        bottom with the given dimensions

        #. Usage: make_refmic(mwidth, mheight, lwidth, lheight, scanstep)
        #. Input: micrograph widht, micrograph height, label width, label \
        height, scanner stepsize
        #. Output: reference micrograph

        >>> from spring.micprgs.scansplit import ScanSplit
        >>> refmic = ScanSplit().make_refmic(9, 10, 3, 2, 10000)
        >>> import numpy as np
        >>> from EMAN2 import EMNumPy
        >>> np.rint(EMNumPy.em2numpy(refmic))
        array([[ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.],
               [ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.],
               [ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.],
               [ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.],
               [ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.],
               [ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.],
               [ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.],
               [ 1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.],
               [ 1.,  1.,  1.,  0.,  0.,  0.,  1.,  1.,  1.],
               [ 1.,  1.,  1.,  0.,  0.,  0.,  1.,  1.,  1.]], dtype=float32)
  
        """
        self.log.fcttolog()
          
        if mwidth is None: mwidth = self.mwidth
        if mheight is None: mheight = self.mheight
        if lwidth is None: lwidth = self.lwidth
        if lheight is None: lheight = self.lheight
        if scanstep is None: scanstep = self.scanstep

        labelx = int(lwidth*1e+4/(scanstep))
        labely = int(lheight*1e+4/(scanstep))
        labelimg = model_blank(labelx, labely)

        mic_width = int(mwidth*1e+4/(scanstep))
        mic_height = int(mheight*1e+4/(scanstep))

        try:
            refmic = Util.pad(labelimg, mic_width, mic_height, 1, 
                                   0, int(round(mic_height/2 - labely/2)), 0, '1')
        except:
            refmic = Util.pad(labelimg, mic_width, mic_height, 1, 
                                   0, int(round(mic_height/2 - labely/2 - 1)), 0, '1')

        return refmic
    

    def adjust_refmic(self, refmic, miclist):
        """
        * Function to adjust size of reference microgrph to the size of rough split
        """

        mic = miclist[0]
        nx = int(mic.get_xsize())
        ny = int(mic.get_ysize())
        self.log.ilog('Pad label to %d, %d' %(nx, ny))

        # pad reference micrograph
        labelimg = refmic
        self.log.dlog('labelimg of %g and %g to be padded to: %g, %g' %
                      (labelimg.get_xsize(), labelimg.get_ysize(), nx, ny))
        try:
            labelpd = Util.pad(labelimg, nx, labelimg.get_ysize(), 1, 0, 0, 0, '0')
        except:
            labelpd = Util.window(labelimg, nx, labelimg.get_ysize(), 1, 0, 0, 0)
    
        try:
            labelpd = Util.pad(labelpd, nx, ny, 1, 0, 0, 0, '0')
        except:
            labelpd = Util.window(labelpd, nx, ny, 1, 0, 0, 0)
            
        return labelpd
    

    def determine_micrograph_offset_against_reference_micrograph(self, refmic_with_label_top, refmic_with_label_bottom,
    micrograph):
        mirror_ccpeaks = []
        mirror_xoffset = []
        mirror_yoffset = []
        x_dimension = int(micrograph.get_xsize())
        for reference_micrograph_with_label in [refmic_with_label_top, refmic_with_label_bottom]:
            ccimg = ccfn(micrograph, reference_micrograph_with_label, center=True) 
            ccimg = Util.window(ccimg, int(0.5 * x_dimension), int(0.5 * x_dimension), 1, 0, 0, 0) #
            peakcc = peak_search(ccimg, 1, +1)
            ccvv, nnn, nnn, nnn, ccxx, ccyy = peakcc[0]
            mirror_ccpeaks.append(ccvv)
            mirror_xoffset.append(ccxx)
            mirror_yoffset.append(ccyy)
        
        if mirror_ccpeaks[0] == max(mirror_ccpeaks):
            ccvv = mirror_ccpeaks[0]
            ccxx = mirror_xoffset[0]
            ccyy = mirror_yoffset[0]
            
        return ccvv, ccxx, ccyy
    

    def findlabel(self, miclist, decimation_factor_find, scanstep):
        """
        * Function to locate micrograph position using cross-correlation map with reference micrograph

        #. Usage: findlabel(refmic, miclist)
        #. Input: stack of roughly split micrographs, reference micrograph, number of micrographs,\
        dictionary that holds micrograph objects, number of micrographs
        #. Output: Position of X-offset and Y-offset and cross-correlation peak value of match
        """
        self.log.fcttolog()

        refmic = self.make_refmic(scanstep=scanstep*decimation_factor_find)

        refmic_with_label_top = self.adjust_refmic(refmic, miclist)
        refmic_with_label_bottom = mirror(refmic_with_label_top, axis='y')
        
        ccpeaks = []
        xoffset = []
        yoffset = []
        for each_mic_number, each_micrograph in enumerate(miclist):
            ccvv, ccxx, ccyy = self.determine_micrograph_offset_against_reference_micrograph(refmic_with_label_top, 
                                                                        refmic_with_label_bottom, each_micrograph)
                
            ccpeaks.append(ccvv)
            xoffset.append(ccxx*decimation_factor_find)
            yoffset.append(ccyy*decimation_factor_find)
            
            self.log.ilog('Micrograph center was found at %d, %d pixels with respect to reference \
                            micrograph (%g cc-value)' %
                            (xoffset[each_mic_number], yoffset[each_mic_number], ccpeaks[each_mic_number]))

        return xoffset, yoffset, ccpeaks
    

class ScanSplitOptions(ScanSplitFind):

    def assign_edge_value_to_edge_columns(self, column_number, column_count):
        """
        >>> ScanSplit().assign_edge_value_to_edge_columns(2, 100)
        6
        >>> ScanSplit().assign_edge_value_to_edge_columns(66, 100)
        66
        >>> ScanSplit().assign_edge_value_to_edge_columns(95, 100)
        94
        """
        if column_number < 0.06 * column_count:
            reference_column_number = int(0.06 * column_count)
        elif column_number > 0.94 * column_count:
            reference_column_number = int(0.94 * column_count)
        else:
            reference_column_number = column_number
        
        return reference_column_number
            

    def normalize_columns(self, micrograph):
        """
        determine number of columns
        pull out each column
        normalize
        """
        column_count = micrograph.get_xsize()
        row_count = int(0.5*micrograph.get_ysize())

        micrograph_center = Util.window(micrograph, column_count, row_count, 1, 0, 0, 0)

        for column_number in range(column_count):
            reference_column_number = self.assign_edge_value_to_edge_columns(column_number, column_count)
            reference_column = micrograph_center.get_col(reference_column_number)
            mean, sigma, imin, imax = Micrograph().get_statistics_from_image(reference_column)
            normalized_column = (micrograph.get_col(column_number) - mean) / sigma

            micrograph.set_col(normalized_column, column_number)
        
        return micrograph
            

    def normscan(self, miclist):
        """
        * Function to normalize micrograph columns from Zeiss scans

        #. Usage: normscan(normscanpath, miclist)
        #. Input: list of micrographs
        #. Output: Series of normalized micrographs, list of normalized micrograph filenames

        """
        self.log.fcttolog()

        normmiclist = []
        micrograph = EMData()
        for each_micfile in miclist:
            self.log.ilog('Normalize micrograph {0} columns.'.format(each_micfile))
            micrograph.read_image(each_micfile)
            self.micrograph = self.normalize_columns(micrograph)

            self.micrograph.write_image(each_micfile)
            normmiclist.append(each_micfile)
            
        return normmiclist
    

    def contactprint(self, scanimg, infile):
        """
        * Function to generate a contact print of the negative scan 

        #. Usage: contactprint(scanimg, infile) 
        #. Input: micrograph EMData object, input filename 
        #. Output: compressed contact print ( file)
        """
        
        outfile = '{0}_cprint{1}pdf'.format(os.path.splitext(os.path.basename(infile))[0], os.extsep)
        fig = self.prepare_print(scanimg, infile, outfile)
        fig.savefig(outfile, dpi=300, orientation='portrait')


    def prepare_print(self, img, infile, outfile, fig_number=None):
        """
        * Function to write print

        #. Usage: fig = prepare_print(img, infile, outfile, fig_number)
        #. Input: image to be printed, input filename, outputfilename, figure number
        #. Output: figure to be saved
        """

        split_micrograph_plot = DiagnosticPlot()
        fig = split_micrograph_plot.add_header_and_footer(self.feature_set, infile, outfile)

        ax1 = fig.add_subplot(111)
        if img.get_xsize() > 5000:
            decimation_factor = int(img.get_xsize()/5000) + 1
            img = Util.decimate(img, decimation_factor, decimation_factor, 1)
            self.log.dlog('Image {0} was binned by {1}'.format(outfile, decimation_factor))
            
        img_array = np.copy(EMNumPy.em2numpy(img))
        self.log.dlog('Image {0} was converted to Numpy array'.format(infile))

        height, width = img_array.shape
        if height > width:
            img_array = np.swapaxes(img_array, 0, 1)
        ax1.imshow(img_array, cmap=cm.gray, interpolation='nearest')

        return fig


    def finalprint(self, miclist):
        """
        * Function to generate final prints of the cropped micrographs 

        #. Usage: finalprint(miclist, scanstep, tempdir)
        #. Input: list of micrographs, scanner stepsize, temporary directory
        #. Output: series of final prints (compressed JPG file)
        """

        splitmic = EMData()
        for filenumber, infile in enumerate(miclist):
            outfile = '{0}_fprint{1}pdf'.format(infile.split(os.extsep)[0], os.extsep)
            splitmic.read_image(infile)
            splitmic = Micrograph().adjust_gray_values_for_print_and_optimal_display(splitmic)

            fig = self.prepare_print(splitmic, infile, outfile, filenumber)
            self.log.ilog('Micrograph {0} saved.'.format(outfile))
            fig.savefig(outfile, dpi=300, orientation='portrait')
            
        
    def bin_micrographs(self, miclist, binfactor):
        """
        * Function to bin series of micrographs by binfactor

        #. Usage: bin_micrographs(miclist, binfactor)
        #. Input: list of micrograph names, binfactor (1x = nobinning)
        #. Output: micrograph names will be appended by -binfactorxbinned.ext
        """
        self.log.fcttolog()

        mics_binned = []
        if binfactor < 2:
            sys.stderr.write('Bin factor of %g too low, binning is not required' %binfactor)
        else:
            micg = EMData()
            for mic in miclist: 
                micbin = mic.split(os.extsep)
                micg.read_image(mic)
                micg = image_decimate(micg, binfactor, fit_to_fft=False)
                micbinned = micbin[0] + '-' + '%d' %binfactor + 'xbin' + os.extsep + micbin[-1]
                micg.write_image(micbinned)
                mics_binned.append(micbinned)
                self.log.ilog('Micrograph %s was binned to %s.' %(mic, micbinned))
        
        return mics_binned
    

class ScanSplit(ScanSplitOptions):
    def split_output_string(self, outfile):
        """
        >>> ScanSplit().split_output_string('test_???.mrc')
        ['test_', '.mrc']
        >>> ScanSplit().split_output_string('test_??.mrc')
        ['test_', '.mrc']
        >>> ScanSplit().split_output_string('test_?.mrc')
        ['test_', '.mrc']
        >>> ScanSplit().split_output_string('test_*.mrc')
        ['test_', '.mrc']
        >>> ScanSplit().split_output_string('test_%02d.mrc')
        ['test_', '.mrc']
        """
#        if outfile is None: outfile = self.outfile

        if '???' in outfile: 
            output_split = outfile.split('???')
        elif '??' in outfile: 
            output_split = outfile.split('??')
        elif '?' in outfile: 
            output_split = outfile.split('?')
        elif '*' in outfile: 
            output_split = outfile.split('*')
        elif '%02d' in outfile: 
            output_split = outfile.split('%02d')
        else: 
            output_split = outfile.split(os.extsep)
            output_split[-2] = output_split[-2] + '_'
            output_split[-1] = os.extsep + output_split[-1]

        return output_split
    

    def compute_micrograph_center_in_scan(self, col_row_number, col_row_count, size, offset, mic_number):
        column_number, row_number = col_row_number
        column_count, row_count = col_row_count
        xoffset, yoffset = offset
        sizex, sizey = size
        centerx = (-column_count + 1)*sizex/2 + \
                        column_number*sizex + xoffset[mic_number]
        centery = (-row_count + 1)*sizey/2 + \
                        row_number*sizey + yoffset[mic_number]
        self.log.dlog('Micrograph\'s off-center position: {0} and {1}'.format(centerx, centery))
        
        return centerx, centery


    def check_and_adjust_windowing_paramters(self, scan_dimension, mic_dimension, center):
        """
        * Function to adjust windowing parameter in case of incompletely scanned micrographs
        
        >>> ScanSplit().check_and_adjust_windowing_paramters((1500, 1000), (500, 500), (300, 300))
        (500, 450, 300, 275)
        >>> ScanSplit().check_and_adjust_windowing_paramters((1000, 1000), (500, 500), (300, 300))
        (450, 450, 275, 275)
        >>> ScanSplit().check_and_adjust_windowing_paramters((1500, 1500), (500, 500), (300, 300))
        (500, 500, 300, 300)
        """
        nx, ny = scan_dimension
        mic_width, mic_height = mic_dimension
        centerx, centery = center
        
        newmic_width = mic_width
        newmic_height = mic_height
        if (abs(centerx) + mic_width/2 > nx/2): 
            overhang_x = abs(nx/2 - abs(centerx) - mic_width/2)
            newmic_width = mic_width - overhang_x
            if centerx < 0: 
                centerx = centerx + (mic_width - newmic_width)/2
            elif centerx > 0: 
                centerx = centerx - (mic_width - newmic_width)/2
                
            if newmic_width %2 != 0: 
                newmic_width = newmic_width - 1
            self.log.ilog('X-overhang is %g pixel while windowing. Micrograph size adjusted to %g x %g pixels' %
                          (overhang_x, newmic_width, newmic_height))

        if (abs(centery) + mic_height/2 > ny/2): 
            overhang_y = abs(ny/2 - abs(centery) - mic_height/2)
            newmic_height = mic_height - overhang_y
            if centery < 0: 
                centery = centery + (mic_height - newmic_height)/2
            elif centery > 0: 
                centery = centery - (mic_height - newmic_height)/2
            if newmic_height %2 != 0: 
                newmic_height = newmic_height - 1
            self.log.ilog('Y-overhang is %g pixel while windowing. Micrograph size adjusted to %g x %g pixels' %
                          (overhang_y, newmic_width, newmic_height))

        self.log.dlog('Windowing paramters: centerx: %g, centery: %g, newmic_width: %g, newmic_height: %g' %
                      (centerx, centery, newmic_width, newmic_height))
        
        return newmic_width, newmic_height, centerx, centery


    def finesplit(self, row_count, column_count, mwidth, mheight, scanstep, xoffset, yoffset, ccpeaks, cc_threshold,
    outfile):
        """
        * Function to finely split scan into micrographs according to found micrograph location

        #. Usage: finesplit(row_count, column_count, mwidth, mheight, scanstep, xoffset,\
        yoffset, ccpeaks, cc_threshold, outfile)
        #. Input: number of rows, number of colums, number of micrographs,\
        micrograph width, micrograph height, scanner stepsize, X-offset center, Y-offset center,\
        list of cross-correlation peaks, cross-correlation threshold
        #. Output: series of cropped micrographs

        """
        xsize = self.nx/column_count
        ysize = self.ny/row_count

        mic_width = int(mwidth*10000/(scanstep))
        mic_height = int(mheight*10000/(scanstep))
        self.log.dlog('imgx: %g, imgy: %g sizex: %g, sizey: %g, mic_width: %g, mixy: %g' %
                      (self.nx, self.ny, xsize, ysize, mic_width, mic_height))

        mic_number = 0 
        miclist = []
        output_split = self.split_output_string(outfile)
        
        for each_row_number in range(row_count):
            for each_column_number in range(column_count):
                if ccpeaks[mic_number] > cc_threshold: 
                    centerx, centery = self.compute_micrograph_center_in_scan((each_column_number, each_row_number),
                    (column_count, row_count), (xsize, ysize), (xoffset, yoffset), mic_number)
                    
                    newmic_width, newmic_height, centerx, centery = self.check_and_adjust_windowing_paramters((self.nx,
                    self.ny), (mic_width, mic_height), (centerx, centery))
                    
                    if row_count == 1 and column_count == 1:
                        splitmic = self.img
                    else:
                        splitmic = Util.window(self.img, int(newmic_width), int(newmic_height), 1, int(centerx),
                        int(centery), 0)

                    fname = output_split[-2] + '%03d'%mic_number + output_split[-1]
                    self.log.ilog('Micrograph %s neatly windowed: %g x %g cm' %
                                  (fname, newmic_width*scanstep/10000, 
                                   newmic_height*scanstep/10000))
                    splitmic.write_image(fname)
                    miclist.append(fname)
                    mic_number = mic_number + 1
                else:
                    self.log.ilog('Micrograph {0} was NOT windowed because of low cross-correlation. '.format(mic_number) + \
                    'If this is not correct, lower cross-correlation threshold')
        if mic_number is 0: 
            error_message = 'Exited because no micrographs found on scan (check cross-correlation '+ \
            'between dummy micrograph and set cc-threshold in parameters)'
            raise ValueError(error_message)
        else:
            pass
        
        return miclist
    

    def perform_splitscan_by_finding_location_with_respect_to_reference_micrograph(self, micrograph_files, outfiles):
        self.log.plog(10)
        for each_micrograph_index, each_micrograph_file in enumerate(micrograph_files):
            self.img, self.nx, self.ny = Micrograph().readmic(each_micrograph_file)
        
            miclist, decimation_factor_find = self.roughsplit(self.img, self.row_count, self.column_count,
            self.mic_count)
            
            self.log.plog(90 * (each_micrograph_index + 0.2) / len(micrograph_files) + 10)
            xoffset, yoffset, ccpeaks = self.findlabel(miclist, decimation_factor_find, self.scanstep)
            self.log.plog(90 * (each_micrograph_index + 0.5) / len(micrograph_files) + 10)
            
            miclist = self.finesplit(self.row_count, self.column_count, self.mwidth, self.mheight, self.scanstep,
            xoffset, yoffset, ccpeaks, self.cc_threshold, outfiles[each_micrograph_index])
            
            self.log.plog(90 * (each_micrograph_index + 0.8) / len(micrograph_files) + 10)
    
            if self.normscanoption: 
                self.normalized_mics = self.normscan(miclist)
            if self.binoption: 
                mics_binned = self.bin_micrographs(miclist, self.binfactor)
            if self.fprintoption: 
                self.finalprint(miclist)
            if self.cprintoption:
                self.contactprint(self.img, each_micrograph_file)
            self.log.plog(90 * (each_micrograph_index + 1) / len(micrograph_files) + 10)
            

    def perform_splitscan(self):
        if len(self.micrograph_files) < self.cpu_count:
            self.cpu_count = len(self.micrograph_files)
            self.feature_set.parameters['Number of CPUs']=self.cpu_count
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        self.tempdir = Temporary().mktmpdir(self.temppath)
        
        outfiles = Features().rename_series_of_output_files(self.micrograph_files, self.outfile)
        self.perform_splitscan_by_finding_location_with_respect_to_reference_micrograph(self.micrograph_files, outfiles)
        
        os.rmdir(self.tempdir)
        self.log.endlog(self.feature_set)
        
        
def main():
    # Option handling
    parset = ScanSplitPar()
    mergeparset = OptHandler(parset)

    ######## Program
    scan = ScanSplit(mergeparset)
    scan.perform_splitscan()
    
    
if __name__ == '__main__':
    main()
