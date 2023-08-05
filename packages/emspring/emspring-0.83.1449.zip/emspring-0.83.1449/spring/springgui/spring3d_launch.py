# Author: Carsten Sachse 17-Jan-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Spring3d - suite of programs that reconstruct 3D images from segmented helical particles
"""
from PyQt4.QtGui import QMainWindow, QWidget, QTabWidget, QPixmap, QLabel, QGridLayout, QApplication, QScrollArea
from spring.csinfrastr.csgui import GUI
from spring.segment3d.refine.sr3d_main import SegmentRefine3dPar
from spring.segment3d.segclassmodel import SegClassModelPar
from spring.segment3d.segclassreconstruct import SegClassReconstructPar
from spring.segment3d.seggridexplore import SegGridExplorePar
from spring.segment3d.segmultirefine3d import SegMultiRefine3dPar
from spring.segment3d.segrefine3dgrid import SegRefine3dGridPar
from spring.segment3d.segrefine3dinspect import SegRefine3dInspectPar
from spring.segment3d.segrefine3dplot import SegRefine3dPlotPar
from spring.springgui.spring_menu import GuiActions
from textwrap import wrap
import os
import sys

class Spring3dGuiScrollTabs(QScrollArea):
    def __init__(self, features=None, parent=None):
        QWidget.__init__(self)
        
        self.features = features
        self.springTab = GUI(features)
        self.setWidget(self.springTab)
        
        
class SpringGuiTop(QWidget):
    def __init__(self, logofile=None, parent=None):
        QWidget.__init__(self)

        self.suitename = os.path.basename(sys.argv[0])
        self.setWindowTitle('%s' %self.suitename)

        self.pic = QLabel()
        self.pic.setGeometry(10, 10, 544, 100)
        #use full ABSOLUTE path to the image, not relative
        
        self.pic.setPixmap(QPixmap(os.path.join(os.path.dirname(__file__),
        '{pdir}{sep}images{sep}{logo}'.format(pdir=os.pardir, sep=os.sep, logo=logofile))))
        

class Spring3dGui(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)

        segment3dguitop=SpringGuiTop('spring3d_logo{0}png'.format(os.extsep))

        self.tabWidget = QTabWidget()

        self.segrefine3dgrid_features = SegRefine3dGridPar()
        self.SegRefine3dGridTab = Spring3dGuiScrollTabs(self.segrefine3dgrid_features)

        self.segmentrefine3d_features = SegmentRefine3dPar()
        self.segmentRefine3dTab = Spring3dGuiScrollTabs(self.segmentrefine3d_features)

        self.seggridexplore_features = SegGridExplorePar()
        self.segGridExploreTab = Spring3dGuiScrollTabs(self.seggridexplore_features)
        
        self.segrefine3dplot_features= SegRefine3dPlotPar()
        self.segRefine3dPlotTab = Spring3dGuiScrollTabs(self.segrefine3dplot_features)
        
        self.segclassreconstruct_features = SegClassReconstructPar()
        self.segClassReconstructTab = Spring3dGuiScrollTabs(self.segclassreconstruct_features)
        
        self.segrefine3dinspect_features = SegRefine3dInspectPar()
        self.segRefine3dInspectTab = Spring3dGuiScrollTabs(self.segrefine3dinspect_features)

        self.segclassmodel_features = SegClassModelPar()
        self.segClassModelTab = Spring3dGuiScrollTabs(self.segclassmodel_features)

        self.segmultirefine3d_features = SegMultiRefine3dPar()
        self.segMultiRefine3dTab = Spring3dGuiScrollTabs(self.segmultirefine3d_features)

        self.addSpring3dTabs()

        layout = QGridLayout()
        layout.addWidget(segment3dguitop.pic, 0, 0, 4, 1)
        layout.addWidget(self.tabWidget, 0, 1, 7, 7)
        layout.setColumnStretch(0, 0)
        self.setLayout(layout)


    def addSpring3dTabs(self):
        self.tabWidget.addTab(self.segClassReconstructTab, self.segclassreconstruct_features.progname.title())
        self.tabWidget.setTabToolTip(0, '\n'.join(wrap(self.segclassreconstruct_features.progname.title() + ' - ' + \
        self.segclassreconstruct_features.proginfo)))
        
        self.tabWidget.addTab(self.segGridExploreTab, self.seggridexplore_features.progname.title())
        self.tabWidget.setTabToolTip(1, '\n'.join(wrap(self.seggridexplore_features.progname.title() + ' - ' + \
        self.seggridexplore_features.proginfo)))
        
        self.tabWidget.addTab(self.segmentRefine3dTab, self.segmentrefine3d_features.progname.title())
        self.tabWidget.setTabToolTip(2, '\n'.join(wrap(self.segmentrefine3d_features.progname.title() + ' - ' + \
        self.segmentrefine3d_features.proginfo)))
        
        self.tabWidget.addTab(self.SegRefine3dGridTab, self.segrefine3dgrid_features.progname.title())
        self.tabWidget.setTabToolTip(3, '\n'.join(wrap(self.segrefine3dgrid_features.progname.title() + ' - ' + \
        self.segrefine3dgrid_features.proginfo)))
        
        self.tabWidget.addTab(self.segRefine3dPlotTab, self.segrefine3dplot_features.progname.title())
        self.tabWidget.setTabToolTip(4, '\n'.join(wrap(self.segrefine3dplot_features.progname.title() + ' - ' + \
        self.segrefine3dplot_features.proginfo)))
        
        self.tabWidget.addTab(self.segRefine3dInspectTab, self.segrefine3dinspect_features.progname.title())
        self.tabWidget.setTabToolTip(5, '\n'.join(wrap(self.segrefine3dinspect_features.progname.title() + ' - ' + \
        self.segrefine3dinspect_features.proginfo)))

        self.tabWidget.addTab(self.segClassModelTab, self.segclassmodel_features.progname.title())
        self.tabWidget.setTabToolTip(6, '\n'.join(wrap(self.segclassmodel_features.progname.title() + ' - ' + \
        self.segclassmodel_features.proginfo)))

        self.tabWidget.addTab(self.segMultiRefine3dTab, self.segmultirefine3d_features.progname.title())
        self.tabWidget.setTabToolTip(7, '\n'.join(wrap(self.segmultirefine3d_features.progname.title() + ' - ' + \
        self.segmultirefine3d_features.proginfo)))


class Spring3dMain(QMainWindow, GuiActions):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.package = 'emspring'

        Spring3dCentral = Spring3dGui()
        self.setCentralWidget(Spring3dCentral)

        # inherit body of layout of actions
        self.setupUi(self)

def main():
    app = QApplication(sys.argv)
    window = Spring3dMain()

    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
