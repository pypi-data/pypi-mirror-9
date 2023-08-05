#!/usr/bin/env python
"""
Test module to check scanlinefit
"""
from EMAN2 import EMNumPy
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.micprgs.scanlinefit import ScanLineFitPar, ScanLineFit
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
import numpy as np
import os

class TestScanLineFit(ScanLineFit):
    """
    Test class that tests work of scanlinefit
    """
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.feature_set = ScanLineFitPar()
        self.prepare_line_micrograph()

        self.feature_set.parameters['Micrograph']='test_linemic.mrc'
        self.feature_set.parameters['Diagnostic plot']='test_scanlinefit.png'
        self.feature_set.parameters['Topleft coordinates of line']=((0,2000))
        self.feature_set.parameters['Bottomright coordinates of line']=((1498,201))
        self.feature_set.parameters['Width of integration in pixels']=15

        super(TestScanLineFit, self).__init__(self.feature_set)


    def prepare_line_micrograph(self):
        """
        Prepare a micrograph with defined line
        """
        self.linemic = np.zeros((2000,1500))
        self.icept = 2000
        self.slope = -1.2
        self.curvature = 1e-7
        self.pincushion = 1e-10

        polyvar = [self.pincushion, self.curvature, self.slope, self.icept]
        linex = np.arange(0,2000)
        self.line = np.polyval(polyvar, linex)

        # swap rows and col for EMData objects
        for row, col in enumerate(self.line):
            if 0 < row < 1500:
                self.linemic[np.rint(col)][row] += 1

        self.linemicimg = EMNumPy.numpy2em(np.copy(self.linemic))
        #self.linemicimg = mirror(self.linemicimg)
        self.linemicimg.write_image('test_linemic.mrc')
        """
        from EMAN2 import display
        display(self.linemicimg)
        #import matplotlib.pyplot as plt
        #plt.imshow(self.linemic)
        #plt.show()
        """
    def compare_fit(self):
        """
        * Function to compare fit with input data
        """
        assert round(self.pincushion, 9) == round(self.polyvar[0], 9)
        assert round(self.curvature, 5) == round(self.polyvar[1], 5)
        assert round (self.slope) == round(self.polyvar[2])
        assert round(self.icept, -3) == round(self.polyvar[3], -3)

    def teardown(self):
        os.remove('test_linemic.mrc')
        os.remove('test_scanlinefit.png')

        self.testingdir.remove()


class TestScanLineFitMain(TestScanLineFit):
    def do_test_case_lf1(self):
        self.perform_scanlinefit()
        self.compare_fit()


class TestScanLineFitMore(TestScanLineFit):
    def do_end_to_end_test_lf_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)

    def do_end_to_end_test_lf_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)

def main():
    tlf = TestScanLineFitMain()
    tlf.setup()
    tlf.do_test_case_lf1()
        
if __name__ == '__main__':
    main()
