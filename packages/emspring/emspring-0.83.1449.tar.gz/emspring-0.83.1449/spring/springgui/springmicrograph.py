# Author: Carsten Sachse 17-Jan-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Springmicrograph - suite of programs that work with micrographs
"""
from PyQt4.QtGui import QMainWindow, QWidget, QTabWidget, QGridLayout, QApplication
from spring.micprgs.micctfdetermine import MicCtfDeterminePar
from spring.micprgs.micexam import MicrographExamPar
from spring.micprgs.michelixtrace import MicHelixTracePar
from spring.micprgs.scandotfit import ScanDotFitPar
from spring.micprgs.scanlinefit import ScanLineFitPar
from spring.micprgs.scanrowcolcorr import ScanRowColCorrPar
from spring.micprgs.scansplit import ScanSplitPar
from spring.springgui.spring3d_launch import SpringGuiTop, Spring3dGuiScrollTabs
from spring.springgui.spring_menu import GuiActions
from textwrap import wrap
import os
import sys


class SpringMicrographGui(QWidget):

    def addScanSpringTabs(self):
        self.tabWidget.addTab(self.scanSplitW, self.scansplit_features.progname.title())
        self.tabWidget.setTabToolTip(0, '\n'.join(wrap(self.scansplit_features.progname.title() + ' - ' + \
        self.scansplit_features.proginfo)))
        
        self.tabWidget.addTab(self.micExamW, self.micexam_features.progname.title())
        self.tabWidget.setTabToolTip(1, '\n'.join(wrap(self.micexam_features.progname.title() + ' - ' + \
        self.micexam_features.proginfo)))
        
        self.tabWidget.addTab(self.micCtfDetermineTab, self.micctfdetermine_features.progname.title())
        self.tabWidget.setTabToolTip(2, '\n'.join(wrap(self.micctfdetermine_features.progname.title() + ' - ' + \
        self.micctfdetermine_features.proginfo)))
        
        self.tabWidget.addTab(self.micHelixTraceTab, self.michelixtrace_features.progname.title())
        self.tabWidget.setTabToolTip(3, '\n'.join(wrap(self.michelixtrace_features.progname.title() + ' - ' + \
        self.michelixtrace_features.proginfo)))
        
        self.tabWidget.addTab(self.lineFitW, self.scanlinefit_features.progname.title())
        self.tabWidget.setTabToolTip(4, '\n'.join(wrap(self.scanlinefit_features.progname.title() + ' - ' + \
        self.scanlinefit_features.proginfo)))
        
        self.tabWidget.addTab(self.dotFitW, self.scandotfit_features.progname.title())
        self.tabWidget.setTabToolTip(5, '\n'.join(wrap(self.scandotfit_features.progname.title() + ' - ' + \
        self.scandotfit_features.proginfo)))
        
        self.tabWidget.addTab(self.rowColCorrW, self.scanrowcolcorr_features.progname.title())
        self.tabWidget.setTabToolTip(6, '\n'.join(wrap(self.scanrowcolcorr_features.progname.title() + ' - ' + \
        self.scanrowcolcorr_features.proginfo)))
        

    def __init__(self, parent=None):
        QWidget.__init__(self)

        springmicrographtop = SpringGuiTop('springscan_logo{0}png'.format(os.extsep))
        self.tabWidget = QTabWidget()

        self.scansplit_features = ScanSplitPar()
        self.scanSplitW = Spring3dGuiScrollTabs(self.scansplit_features)

        self.micexam_features = MicrographExamPar()
        self.micExamW = Spring3dGuiScrollTabs(self.micexam_features)

        self.micctfdetermine_features = MicCtfDeterminePar()
        self.micCtfDetermineTab = Spring3dGuiScrollTabs(self.micctfdetermine_features)

        self.michelixtrace_features = MicHelixTracePar()
        self.micHelixTraceTab = Spring3dGuiScrollTabs(self.michelixtrace_features)

        self.scanlinefit_features = ScanLineFitPar()
        self.lineFitW = Spring3dGuiScrollTabs(self.scanlinefit_features)

        self.scandotfit_features = ScanDotFitPar()
        self.dotFitW = Spring3dGuiScrollTabs(self.scandotfit_features)

        self.scanrowcolcorr_features = ScanRowColCorrPar()
        self.rowColCorrW = Spring3dGuiScrollTabs(self.scanrowcolcorr_features)

        self.addScanSpringTabs()

        layout = QGridLayout()
        layout.addWidget(springmicrographtop.pic, 0, 0, 4, 1)
        layout.addWidget(self.tabWidget, 0, 1, 7, 7)
        layout.setColumnStretch(0, 0)
        self.setLayout(layout)


class SpringMicrographMain(QMainWindow, GuiActions):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.package = 'emspring'        
        SpringMicrographCentral = SpringMicrographGui()
        self.setCentralWidget(SpringMicrographCentral)

        # inherit body of layout of actions
        self.setupUi(self)

def main():
    app = QApplication(sys.argv)
    window = SpringMicrographMain()

    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

