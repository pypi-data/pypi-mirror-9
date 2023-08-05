# Author: Carsten Sachse 21-Sep-2010
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

""" 
Program to evaluate performance of scanner by measuring dots spaced 2.5 mm apart. 
"""
from EMAN2 import Util
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import DiagnosticPlot
from spring.csinfrastr.csreadinput import OptHandler
from spring.micprgs.scansplit import Micrograph
import numpy as np

class ScanDotFitPar:
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'scandotfit'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.scandotfit_features = Features()
        self.feature_set = self.scandotfit_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
        
    def define_parameters_and_their_properties(self):
        self.feature_set = self.scandotfit_features.set_inp_micrograph(self.feature_set)
        self.feature_set = self.scandotfit_features.set_output_plot(self.feature_set, self.progname + '_diag.pdf')
    
        self.feature_set = self.scandotfit_features.set_scanner_step_size(self.feature_set)
        self.feature_set = self.set_integration_width(self.feature_set)
        self.feature_set = self.set_topleft_coordinates(self.feature_set)
        self.feature_set = self.set_topright_coordinates(self.feature_set)
        self.feature_set = self.set_bottomleft_coordinates(self.feature_set)
        
    
    def define_program_states(self):
        self.feature_set.program_states['readmic']='Read input micrograph'
        self.feature_set.program_states['searchdots']='Determines positions of dots by center of gravity calculation'
        self.feature_set.program_states['dotdistance']='Calculates distance between dots'
        self.feature_set.program_states['visdots']='Visualization of dots'


    def set_integration_width(self, feature_set):
        inp4 = 'Width of integration in pixels'
        feature_set.parameters[inp4] = int(100)
        
        feature_set.hints[inp4] = 'Use default value: width of box in pixels used for dot determination - otherwise ' +\
        'use with caution.'
        
        feature_set.properties[inp4] = feature_set.Range(1, 500, 1)
        feature_set.level[inp4] = 'expert'
        
        return feature_set


    def set_topleft_coordinates(self, feature_set):
        inp5 = 'Topleft coordinates of dot grid' #p[inp5]=tuple((3309,13355))
        feature_set.parameters[inp5] = tuple((539, 2129))
        feature_set.hints[inp5] = 'Comma-separated integer pair of coordinates (x, y).'
        feature_set.properties[inp5] = self.feature_set.Range(0, 30000, 1)
        feature_set.level[inp5]='intermediate'
        
        return feature_set


    def set_topright_coordinates(self, feature_set):
        inp6 = 'Topright coordinates of dot grid' #p[inp6]=tuple((9023,13607))
        feature_set.parameters[inp6] = tuple((1493, 2173))
        feature_set.hints[inp6] = 'Comma-separated integer pair of coordinates (x, y).'
        feature_set.properties[inp6] = feature_set.Range(0, 30000, 1)
        feature_set.level[inp6]='intermediate'
        
        return feature_set


    def set_bottomleft_coordinates(self, feature_set):
        inp7 = 'Bottomleft coordinates of dot grid' #p[inp7]=tuple((3909,138))
        feature_set.parameters[inp7] = tuple((638, 46))
        feature_set.hints[inp7] = 'Comma-separated integer pair of coordinates (x, y).'
        feature_set.properties[inp7] = feature_set.Range(0, 30000, 1)
        feature_set.level[inp7]='intermediate'
        
        return feature_set


class ScanDotFit(object):
    """
    * Class that holds functions for automated distance measurements from regular dots on micrograph

    * __init__ Function to read in the entered parameter dictionary and load micrograph

    #. Usage: ScanDotFit(pardict)
    #. Input: pardict = OrderedDict of program parameters
    """
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset  
            p = self.feature_set.parameters
            self.infile = p['Micrograph']
            self.outfile = p['Diagnostic plot']
            self.stepsize = p['Scanner step size in micrometer']
            self.boxwidth = p['Width of integration in pixels']
            self.topleft = p['Topleft coordinates of dot grid']
            self.topright = p['Topright coordinates of dot grid']
            self.bottomleft = p['Bottomleft coordinates of dot grid']

            #Micrograph.readmic(self, self.infile)
            self.img, self.nx, self.ny = Micrograph().readmic(self.infile)

    def pttoline(self, ptone = None, pttwo = None):
        """
        * Function that determines line equation from two given points

        #. Usage: slope, intercept = pttoline(ptone, pttwo)
        #. Input: ptone = tuple of x,y coordinates, pttwo = tuple of x,y coordinates
        #. Output: slope, intercept
        """
        import numpy as np

        if ptone is None: ptone = self.topleft
        if pttwo is None: pttwo = self.topright

        x0, y0 = ptone
        x1, y1 = pttwo

        linex = [x0, x1]
        liney = [y0, y1]
        self.slope, self.icept = np.polyfit(linex, liney, 1)
        self.log.ilog('Fitted line intercept: %g, slope: %g' %(self.icept, self.slope))

        return self.slope, self.icept

    def searchdots(self, boxwidth = None, topleft = None, topright = None, bottomleft = None, stepsize = None):
        """
        * Function to determine coordinates of dots by center of gravity measurements

        #. Usage: dotx, doty = (boxwidth, topleft, topright, bottomleft, stepsize)
        #. Input: boxwidth width of integration, topleft/topright/bottomleft coordinate pair
        #. Output: dotx and doty = list of X and Y coordinates of dots

        """
        from math import cos, sin, atan, sqrt
        self.log.fcttolog()

        if boxwidth is None: boxwidth = self.boxwidth
        if topleft is None: topleft = self.topleft
        if topright is None: topright = self.topright
        if bottomleft is None: bottomleft = self.bottomleft
        if stepsize is None: stepsize = self.stepsize

        self.pttoline()

        self.no_cols = int(round(sqrt((topleft[1]-topright[1])**2+(topleft[0]-topright[0])**2)/(2500/stepsize)))
        self.no_rows = int(round(sqrt((topleft[1]-bottomleft[1])**2+(topleft[0]-bottomleft[0])**2)/(2500/stepsize)))
        self.log.ilog('Number of dot columns detected: %g' %self.no_cols)
        self.log.ilog('Number of dot rows detected: %g' %self.no_rows)

        def cog_dots(img, x0, y0, slope, stepsize, boxwidth, no_cols, no_rows):
            xoffset = int(-self.nx/2 + x0 + cos(atan(slope))*eachCol*2500/stepsize + \
            sin(atan(slope))*eachRow*2500/stepsize + 0.5)
            yoffset = int(-self.ny/2 + y0 + sin(atan(slope))*eachCol*2500/stepsize - \
            cos(atan(slope))*eachRow*2500/stepsize + 0.5)
            dotimg = Util.window(img, boxwidth, boxwidth, 1, xoffset, yoffset, 0)
            # dotimg.write_image('dotstack.spi', eachCol*no_cols+eachRow)
            self.log.dlog('X-offset: %g, Y-offset: %g' %(xoffset, yoffset))
            shift = dotimg.phase_cog()
            self.log.ilog('Offset from ideal dot at column %g and row %g : %g, %g' \
            %(eachCol, eachRow, shift[0], shift[1]))
            xcoord = x0 + shift[0] + cos(atan(slope))*eachCol*2500/stepsize + \
            sin(atan(slope))*eachRow*2500/stepsize 
            ycoord = y0 + shift[1] + sin(atan(slope))*eachCol*2500/stepsize - \
            cos(atan(slope))*eachRow*2500/stepsize 
            return xcoord, ycoord

        self.dots = [cog_dots(self.img, topleft[0], topleft[1], self.slope, stepsize, boxwidth, 
                              self.no_cols, self.no_rows) for eachCol in range(self.no_cols) 
                     for eachRow in range(self.no_rows)]

        return self.dots, self.no_cols, self.no_rows

    def dotdistance(self, dots = None, stepsize = None, no_cols = None, no_rows = None):
        """
        * Function to determine distances between adjacent dots

        #. Usage: distances = dotdistance(dots, stepsize, no_cols, no_rows)
        #. Input: dots = list of X and Y coordinates of dots, scanner stepsize, number of columns,\
        number of rows
        #. Output: list of horizontal and vertical distances from adjacent dots

        """
        from math import sqrt
        self.log.fcttolog()

        if dots is None: dots = self.dots
        if stepsize is None: stepsize = self.stepsize
        if no_cols is None: no_cols = self.no_cols
        if no_rows is None: no_rows = self.no_rows

        def calc_horid(dots, no_rows, stepsize, k):
                x0, y0 = dots[k]
                x1, y1 = dots[k+no_rows]
                dist = sqrt((y1-y0)**2 + (x1-x0)**2)*stepsize
                self.log.ilog('Horizontal distance between dot %g and dot %g determined: %g micrometer' \
                %(k, k+no_rows, dist))
                return dist

        self.horidots = [calc_horid(dots, no_rows, stepsize, k) for k in range(no_rows*(no_cols-1))]

        def calc_vertd(dots, stepsize, j):
                x0, y0 = dots[j]
                x1, y1 = dots[j+1]
                dist = sqrt((y1-y0)**2 + (x1-x0)**2)*stepsize
                if dist < 4000:
                    self.log.ilog('Vertical distance between dot %g and dot %g determined: %g micrometer'\
                    %(j, j+1, dist))
                    return dist
                else:
                    pass

        self.vertdots = [calc_vertd(dots, stepsize, j) for j in range(no_cols*no_rows-1)]
        return self.horidots, self.vertdots

    def vismic(self, nx, ny, subplot):
        """
        * Function to prepare a micrograph in row and column dimension for matplotlib

        #. Usage: plot = vismic(nx, ny, subplot)
        #. Input: nx = number of rows, ny = number of columns, subplot = idendity of subplot
        #. Output: subplot to be returned
        """
        ax1 = subplot
        self.log.fcttolog()

        for t in ax1.get_xticklabels(): t.set_fontsize(8)
        for t in ax1.get_yticklabels(): t.set_fontsize(8)
        ax1.set_xlabel('Row')
        ax1.set_ylabel('Column')
        ax1.set_xlim(0, nx)
        ax1.set_ylim(0, ny)
        ax1.axis('scaled')
        ax1.minorticks_on()
        ax1.grid(True)

        return ax1

    def visdots(self, dots = None, horidots = None, vertdots = None):
        """
        * Function to visualize detected dots using matplotlib

        #. Usage: output = visfit(dots, horidots, vertdots)
        #. Input: dots = list of X and Y coordinates of dots, horidots, vertdots = list of distances
        #. Output: output plot to saved to PDF, PNG format
        """
        import matplotlib.font_manager as font_manager
        self.log.fcttolog()

        if dots is None: dots = self.dots
        if horidots is None: horidots = self.horidots
        if vertdots is None: vertdots = self.vertdots

        # unpack dots
        xarr = []; yarr = []
        for xy in dots:
            xarr.append(xy[0])
            yarr.append(xy[1])

        scandotfit_plot = DiagnosticPlot()
        self.fig = scandotfit_plot.add_header_and_footer(self.feature_set)

        ax1 = self.fig.add_subplot(121)
        ax1.plot(xarr, yarr, 'x', markeredgewidth=0.2, markersize=3)
        ax1.set_title('Detected dots on micrograph')
        ax1 = self.vismic(self.nx, self.ny, ax1)

        vertdotsarr = np.array([i for i in vertdots if i is not None])/1000
        self.vertical_mean = np.mean(vertdotsarr)
        self.vertical_stdev = np.std(vertdotsarr)
        self.log.ilog('Mean distance of vertical distances: %g, standard deviation (mm): %g' %
                      (self.vertical_mean, self.vertical_stdev))
        horidotsarr = np.array([i for i in horidots if i is not None])/1000
        self.horizontal_mean = np.mean(horidotsarr)
        self.horizontal_stdev = np.std(horidotsarr)
        self.log.ilog('Mean distance of horizontal distances: %g, standard deviation (mm): %g' %
                      (self.horizontal_mean, self.horizontal_stdev))

        ax2 = self.fig.add_subplot(122)
        ax2.set_title('2.5 mm dot distances')
        ax2.hist(vertdotsarr, 40, label='Mean vertical distance: %g\nstdev: %g (mm)' %
                 (self.vertical_mean, self.vertical_stdev))
        ax2.hist(horidotsarr, 40, label='Mean horizontal distance: %g\nstdev: %g (mm)' %
                 (self.horizontal_mean, self.horizontal_stdev))
        ax2.legend(loc='best' , prop=font_manager.FontProperties(size='x-small'))
        ax2.set_xlabel('Distance (mm)')
        ax2.set_ylabel('Number of measurements')
        for t in ax2.get_xticklabels(): t.set_fontsize(8)
        for t in ax2.get_yticklabels(): t.set_fontsize(8)
        
        self.fig.savefig(self.outfile)
        return self.outfile

    def perform_scandotfit(self):
        self.log.plog(10)
        self.searchdots()
        self.log.plog(40)
        self.dotdistance()
        self.log.plog(70)
        self.visdots()
        
        self.log.endlog(self.feature_set)
        
def main():
    # Option handling
    parset = ScanDotFitPar()
    mergeparset = OptHandler(parset)

    ######## Program
    mic = ScanDotFit(mergeparset)
    mic.perform_scandotfit()

if __name__ == '__main__':
    main()
