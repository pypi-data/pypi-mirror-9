# Author: Carsten Sachse 21-Sep-2010
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
""" 
Program to evaluate the performance of scanner by correlating adjacent rows 
and lines with each other from a pure noise image.
"""
from EMAN2 import Util
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import DiagnosticPlot
from spring.csinfrastr.csreadinput import OptHandler
from spring.micprgs.scansplit import Micrograph
from statistics import ccc

class ScanRowColCorrPar:
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'scanrowcolcorr'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.scanrowcolcorr_features = Features()
        self.feature_set = self.scanrowcolcorr_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    
    def define_parameters_and_their_properties(self):
        self.feature_set = self.scanrowcolcorr_features.set_inp_micrograph(self.feature_set)
        self.feature_set = self.scanrowcolcorr_features.set_output_plot(self.feature_set, self.progname + '_diag.pdf')
    
        self.feature_set = self.set_mic_area(self.feature_set)
    
    def define_program_states(self):
        self.feature_set.program_states['readmic']='Read input micrograph'
        self.feature_set.program_states['evalrowcc']='Evaluate row-to-row cross-correlation'
        self.feature_set.program_states['evalcolcc']='Evaluate column-to-column cross-correlation'
        self.feature_set.program_states['visrowcolcc']='Visualize row-to-row and column-to-column correlation'

    def set_mic_area(self, feature_set):
        inp3 = 'Percentage of micrograph area to be analyzed'
        feature_set.parameters[inp3] = int(90)
        feature_set.hints[inp3] = '0-100 percent from the row and column dimensions of micrograph.'
        feature_set.properties[inp3] = feature_set.Range(0, 100, 1)
        feature_set.level[inp3]='expert'
        
        return feature_set


class ScanRowColCorr(object):
    """
    * Class that holds all functions required for computing row-to-row and column-to-column cross-correlation

    * __init__ Function to read in the entered parameter dictionary and load micrograph

    #. Usage: ScanRowColCorr(pardict)
    #. Input: pardict = OrderedDict of program parameters

    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters
            self.infile=p['Micrograph']
            self.outfile=p['Diagnostic plot']
            self.area=p['Percentage of micrograph area to be analyzed']

            #Micrograph.readmic(self, self.infile)
            self.img, self.nx, self.ny = Micrograph().readmic(self.infile)

    def evalrowcc(self, area = None):
        """
        * Function to evaluate cross-correlation of adjacent rows

        #. Usage: rows, ccrows, output2 = evalrowcc(area)
        #. Input: area = area in percent to included in analysis of input micrograph, i.e. exclude label
        #. Output: list of rows, list of cross-correlation

        """
        if area is None: area = self.area
        self.log.fcttolog()
        edge = int(self.nx*(100 - area)/100)

        self.row = []
        self.ccrow = []
        k = 0 
        for eachRow in range(1 + edge, self.ny - 1 - edge):
            if (eachRow == 1 + edge): 
                img1dline1 = self.img.get_row(eachRow)
            else:
                img1dline2 = self.img.get_row(eachRow)
                #img1dline2.write_image('rowstackcc.spi', k)
                k = k +1 
                self.row.append(eachRow)
                self.ccrow.append(ccc(img1dline1, img1dline2))
                img1dline1 = img1dline2
                self.log.ilog('Correlated row %d with row %d: cross-correlation of %f' %
                              (eachRow, eachRow -1, self.ccrow[-1]))
        return self.row, self.ccrow

    def evalcolcc(self, area = None):
        """
        * Function to evaluate cross-correlation of adjacent columns

        #. Usage: cols, cccols, output2 = evalrowcc(area)
        #. Input: area = area in percent to included in analysis of input micrograph, i.e. exclude label
        #. Output: list of columns, list of cross-correlation
        """
        if area is None: area = self.area
        self.log.fcttolog()

        self.col = []
        self.cccol = []
        for eachCol in range(0, self.nx):
            if (eachCol == 0): 
                img1dline1 = self.img.get_col(eachCol)
                img1dline1 = Util.window(img1dline1, int(area*self.ny/100), 1, 1, 0, 0, 0)
            else:
                img1dline2 = self.img.get_col(eachCol)
                img1dline2 = Util.window(img1dline2, int(area*self.ny/100), 1, 1, 0, 0, 0)
                self.col.append(eachCol)
                self.cccol.append(ccc(img1dline1, img1dline2))
                img1dline1 = img1dline2
                self.log.ilog('Correlated column %d with column %d: cross-correlation of %f' %
                              (eachCol, eachCol -1, self.cccol[-1]))
        return self.col, self.cccol

    def visrowcolcc(self, row = None, ccrow = None, col = None, cccol = None):
        """
        * Function to visualize results of row-to-row and column-to-column cross-correlation \
        using matplotlib

        #. Usage: output = visrowcolcc(row, ccrow, col, cccol)
        #. Input: row = list of rows, ccrow = list of row-to-row cross-correlation, col = list of \
                        columns, cccol = list of column-to-column correlation
        #. Output: output plot to saved to PDF, SVG, or PNG, TIF, JPG format
        """
        self.log.fcttolog()

        if row is None: row = self.row
        if ccrow is None: ccrow = self.ccrow
        if col is None: col = self.col
        if cccol is None: cccol = self.cccol

        scanrowcolcorr_fit_plot = DiagnosticPlot()
        self.fig = scanrowcolcorr_fit_plot.add_header_and_footer(self.feature_set)
        
        ax1 = self.fig.add_subplot(111)
        ax1.plot(row, ccrow, 'x', markeredgewidth=0.4, markersize=0.4, label = 'row-to-row correlation')
        ax1.plot(col, cccol, 'x', markeredgewidth=0.4, markersize=0.4, label = 'column-to-column correlation')
        ax1.set_title('Adjacent pixel correlation of pure noise image')
        ax1.legend(loc=3)
        ax1.set_xlabel('Row or column number')
        ax1.set_ylabel('Cross-correlation')
        ax1.set_ylim(0, 1)
        ax1.set_xlim(0, row[-1])
        ax1.minorticks_on()
        ax1.grid(True)
        self.fig.savefig(self.outfile)

        return self.fig


    def perform_scanrowcolcorr(self):
        self.log.plog(10)
        self.evalrowcc()
        self.log.plog(40)
        self.evalcolcc()
        self.log.plog(70)
        self.visrowcolcc()
        self.log.endlog(self.feature_set)
        

def main():
    # Option handling
    parset = ScanRowColCorrPar()
    mergeparset = OptHandler(parset)

    ###### Program
    mic = ScanRowColCorr(mergeparset)
    mic.perform_scanrowcolcorr()

if __name__ == '__main__':
    main()
