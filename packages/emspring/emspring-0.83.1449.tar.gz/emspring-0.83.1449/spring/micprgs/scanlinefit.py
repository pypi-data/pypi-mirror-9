# Author: Carsten Sachse 21-Sep-2010
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
""" 
Program to evaluate scanner performance of scanner by measuring deviation from 45 degree 
line to determine CCD curvature and pincushion parameter.
"""

from EMAN2 import Util
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import DiagnosticPlot
from spring.csinfrastr.csreadinput import OptHandler
from spring.micprgs.scandotfit import ScanDotFit
from spring.micprgs.scansplit import Micrograph
import numpy as np

class ScanLineFitPar:
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'scanlinefit'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.scanlinefit_features = Features()
        self.feature_set = self.scanlinefit_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    
    def define_parameters_and_their_properties(self):
        self.feature_set = self.scanlinefit_features.set_inp_micrograph(self.feature_set)
        self.feature_set = self.scanlinefit_features.set_output_plot(self.feature_set, self.progname + '_diag.pdf')
    
        self.feature_set = self.set_integration_width(self.feature_set)
        self.feature_set = self.set_topleft_coordinates(self.feature_set)
        self.feature_set = self.set_bottomright_coordinates(self.feature_set)
        
    def define_program_states(self):
        self.feature_set.program_states['readmic']='Read input micrograph'
        self.feature_set.program_states['getline']='Get line coordinates from micrograph'
        self.feature_set.program_states['fitcube']='Fit extracted coordinates to cubic function'
        self.feature_set.program_states['visfit']='Visualize extracted line and fitted function'


    def set_integration_width(self, feature_set):
        inp3 = 'Width of integration in pixels'
        feature_set.parameters[inp3] = int(9)
        feature_set.hints[inp3] = 'Use default value: number of pixels used for line determination - otherwise use ' +\
        'with caution.'
        feature_set.properties[inp3] = feature_set.Range(1, 500, 1)
        feature_set.level[inp3]='expert'
        
        return feature_set


    def set_topleft_coordinates(self, feature_set):
        inp4 = 'Topleft coordinates of line'
        feature_set.parameters[inp4] = tuple((180, 2302))
        feature_set.hints[inp4] = 'Integer pair of coordinates (x,y).'
        feature_set.properties[inp4] = feature_set.Range(0, 30000, 1)
        feature_set.level[inp4] = 'intermediate'
        
        return feature_set


    def set_bottomright_coordinates(self, feature_set):
        inp5 = 'Bottomright coordinates of line'
        feature_set.parameters[inp5] = tuple((1889, 215))
        feature_set.hints[inp5] = 'Integer pair of coordinates (x,y).'
        feature_set.properties[inp5] = feature_set.Range(0, 30000, 1)
        feature_set.level[inp5]='intermediate'
        
        return feature_set
    

class ScanLineFit(object):
    """
    * Class that holds functions for determining deviation of an ideal 45 degree line

    * __init__ Function to read in the entered parameter dictionary and load micrograph

    #. Usage: ScanLineFit(pardict)
    #. Input: pardict = OrderedDict of program parameters
    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.infile = p['Micrograph']
            self.outfile = p['Diagnostic plot']
            self.topleft = p['Topleft coordinates of line']
            self.bottomright = p['Bottomright coordinates of line']
            self.iwidth = p['Width of integration in pixels']

            self.img, self.nx, self.ny = Micrograph().readmic(self.infile)
        
    def getline(self, iwidth = None, topleft = None, bottomright = None):
        """
        * Function to determine 45 degree line and their corresponding x, y coordinates using\
                        rough starting coordindates and refine by center-of-gravity measurements
        
        #. Usage: output1 = getline(iwidth, topleft, bottomright)
        #. Input: iwidth = integration width, topleft = topleft coordinates of line, bottomright = \
                        bottom right coordinates of line
        #. Output: 1. array of x and y
        """
        self.log.fcttolog()
        if iwidth is None: iwidth = self.iwidth
        if topleft is None: topleft = self.topleft
        if bottomright is None: bottomright = self.bottomright

        df = ScanDotFit()
        slope, icept = df.pttoline(topleft, bottomright)

        if topleft[1] < bottomright[1]:
            startrow, endrow = topleft[1] - iwidth, bottomright[1] + iwidth
            #startrow, endrow = topleft[1] - integration_width, bottomright[1] - integration_width
        else:
            startrow, endrow = bottomright[1] + iwidth, topleft[1] - iwidth
        self.log.dlog('startrow: %g, endrow: %g' %(startrow, endrow))

        self.linex = [int(round((eachRow-icept)/slope)) for eachRow in range(startrow, endrow)]
        self.liney = [eachRow for eachRow in range(startrow, endrow)]

        def cog_row(img, nx, ny, iwidth, linex, liney, k):
            xoffset = int(-nx/2 + linex[k] + 0.5)
            yoffset = int(-ny/2 + liney[k] + 0.5)
            rowimg = Util.window(img, iwidth, 1, 1, xoffset, yoffset, 0)
            #rowimg.write_image('rowstack.spi', k)
            xshift = rowimg.phase_cog()
            self.log.ilog('Offset from ideal line: %g' %xshift[0])
            linexx = xshift[0] + linex[k]
            self.log.ilog('Pixel density added to array: idealcol %g, measuredcol %g, row %g' %
                          (linex[k], linexx, liney[k]))
            return linexx

        self.linex = [cog_row(self.img, self.nx, self.ny, iwidth, self.linex, self.liney, k) \
                        for k in range(len(self.linex))]
        return self.linex, self.liney

    def fitcube(self, linex = None, liney = None):
        """
        * Function to perform cubic polynomial fit to binary line and determine 

        #. Usage: polyvar, fitliney3, fitliney1 = fitcube(linex, liney)
        #. Input: linex = x and liney = y array of thresholded 45 degree line
        #. Output: list of a, b, c, d (a, b, c = measure of CCD curvature, d = pincushion \
                        or barrel distortion), fitliney3 = computed array of cubic fit, \
                        fitliney1 = computed array of linear fit
        """
        self.log.fcttolog()
        if linex is None: linex = self.linex
        if liney is None: liney = self.liney

        self.polyvar = np.polyfit(linex, liney, 3)
        polyline = np.polyfit(linex, liney, 1)
        self.log.ilog('The threshold pixel line has been fitted with a cubic function:')
        self.log.ilog('Fit: %g*x^3 + %g*x^2 + %g*x + %g' %
                      (self.polyvar[0], self.polyvar[1], self.polyvar[2], self.polyvar[3]))
        # compute line according to fit variables
        self.fitliney3 = np.polyval(self.polyvar, linex)
        self.fitliney1 = np.polyval(polyline, linex)

        return self.polyvar, self.fitliney3, self.fitliney1

    def visfit(self, linex = None, liney = None, polyvar = None, fitliney3 = None, fitliney1 = None):
        """
        * Function to visualize 45 degree line including cubic polynomial fit using matplotlib

        #. Usage: output = visfit(linex, liney, polyvar, fitliney3, fitliney1)
        #. Input: linex = x and liney = y array of thresholded 45 degree line, polyvar = list \
                        of a, b, c, d (a, b, c = measure of CCD curvature, d = pincushion or \
                        barrel distortion fitliney3 = computed array of cubic fit, fitliney1 \
                        = computed array of linear fit
        #. Output: output plot to saved to PDF, SVG, or PNG, TIF, JPG format
        """
        import matplotlib.font_manager as font_manager
        from math import sqrt
        self.log.fcttolog()

        if linex is None: linex = self.linex
        if liney is None: liney = self.liney
        if polyvar is None: polyvar = self.polyvar
        if fitliney3 is None: fitliney3 = self.fitliney3
        if fitliney1 is None: fitliney1 = self.fitliney1

        distance = sqrt((self.linex[-1]-self.linex[0])**2+(self.liney[-1]-self.liney[0])**2)
        self.log.ilog('Line distance from center in pixel: %g' %(distance/2))
        magpin = polyvar[0]*(distance/2)**3
        magccd = polyvar[1]*(distance/2)**2
        self.log.ilog('Magnitude pincushion: %g, CCD curvature: %g (pixel)' %(magpin, magccd))

        scanlinefit_plot = DiagnosticPlot()
        self.fig = scanlinefit_plot.add_header_and_footer(self.feature_set)

        ax1 = self.fig.add_subplot(111)
        ax1.plot(linex, liney, 'x', markeredgewidth=0.02, markersize=0.4, label = 'Thresholded line')
        ax1.plot(linex, fitliney3, linewidth = .02, label = 'Fit: %g*x^3 + %g*x^2 + %g*x + %g' 
                 %(polyvar[0], polyvar[1], polyvar[2], polyvar[3]))
        ax1.plot(linex, fitliney1, linewidth = .02, label = 'Linear fit')
        ax1.set_title('45 Degree line with fitted cubic function')
        ax1.text(1.3, 0.25, 'magnitude pincushion: %g, CCD curvature: %g (pixel)' %(magpin, magccd), fontsize=8)
        ax1.legend(loc=(.2,0.85) , prop=font_manager.FontProperties(size='x-small'))
        ax1 = ScanDotFit().vismic(self.nx, self.ny, ax1)
        self.fig.savefig(self.outfile)
        return self.fig

    def perform_scanlinefit(self):
        self.log.plog(10)
        self.getline()
        self.log.plog(40)
        self.fitcube()
        self.log.plog(70)
        self.visfit()
        self.log.endlog(self.feature_set)
        
def main():
    # Option handling
    parset = ScanLineFitPar()
    mergeparset = OptHandler(parset)
    ######## Program
    mic = ScanLineFit(mergeparset)
    mic.perform_scanlinefit()

if __name__ == '__main__':
    main()
