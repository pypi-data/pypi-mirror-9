# Author: Carsten Sachse 17-Jan-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Spring2d - suite of programs that analyze two-dimensional images of helices
"""
from PyQt4.QtGui import QMainWindow, QWidget, QTabWidget, QGridLayout, QApplication
from spring.segment2d.segclassexam import SegClassExamPar
from spring.segment2d.segclasslayer import SegClassLayerPar
from spring.segment2d.seglayer2lattice import SegLayer2LatticePar
from spring.segment2d.segment import SegmentPar
from spring.segment2d.segmentalign2d import SegmentAlign2dPar
from spring.segment2d.segmentclass import SegmentClassPar
from spring.segment2d.segmentctfapply import SegmentCtfApplyPar
from spring.segment2d.segmentexam import SegmentExamPar
from spring.segment2d.segmentplot import SegmentPlotPar
from spring.segment2d.segmentselect import SegmentSelectPar
from spring.springgui.spring3d_launch import SpringGuiTop, Spring3dGuiScrollTabs
from spring.springgui.spring_menu import GuiActions
from textwrap import wrap
import os
import sys


class Segment2dGui(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self)
        
        segment2dguitop = SpringGuiTop('spring2d_logo{0}png'.format(os.extsep))
        self.tabWidget = QTabWidget()

        self.segment_features = SegmentPar()
        self.segmentTab = Spring3dGuiScrollTabs(self.segment_features)

#         self.sctfapply_feature_set = SegmentCtfApplyPar()
#         self.segmentCtfApplyTab = Spring3dGuiScrollTabs(self.sctfapply_feature_set)

        self.segmentexam_features = SegmentExamPar()
        self.segmentExamTab = Spring3dGuiScrollTabs(self.segmentexam_features)

        self.segmentclass_features = SegmentClassPar()
        self.SegmentClassTab = Spring3dGuiScrollTabs(self.segmentclass_features)

        self.segmentalign2d_features = SegmentAlign2dPar()
        self.segmentAlign2dTab = Spring3dGuiScrollTabs(self.segmentalign2d_features)

        self.segclassexam_features = SegClassExamPar()
        self.segClassExamTab = Spring3dGuiScrollTabs(self.segclassexam_features)

        self.segclasslayer_features = SegClassLayerPar()
        self.segClassLayerTab = Spring3dGuiScrollTabs(self.segclasslayer_features)

        self.seglayer2lattice_features = SegLayer2LatticePar()
        self.segLayer2LatticeTab = Spring3dGuiScrollTabs(self.seglayer2lattice_features)
        
        self.segmentselect_features = SegmentSelectPar()
        self.segmentselectTab = Spring3dGuiScrollTabs(self.segmentselect_features)
        
        self.segmentplot_features = SegmentPlotPar()
        self.segmentPlotTab = Spring3dGuiScrollTabs(self.segmentplot_features)
        
        self.addSpring2dTabs()

        layout = QGridLayout()
        layout.addWidget(segment2dguitop.pic, 0, 0, 4, 1)
        layout.addWidget(self.tabWidget, 0, 1, 7, 7)
        layout.setColumnStretch(0, 0)
        self.setLayout(layout)


    def addSpring2dTabs(self):
        self.tabWidget.addTab(self.segmentTab, self.segment_features.progname.title())
        self.tabWidget.setTabToolTip(0, '\n'.join(wrap(self.segment_features.progname.title() + ' - ' + \
        self.segment_features.proginfo)))
                                     
        self.tabWidget.addTab(self.segmentExamTab, self.segmentexam_features.progname.title())
        self.tabWidget.setTabToolTip(1, '\n'.join(wrap(self.segmentexam_features.progname.title() + ' - ' + \
        self.segmentexam_features.proginfo)))
        
        self.tabWidget.addTab(self.SegmentClassTab, self.segmentclass_features.progname.title())
        self.tabWidget.setTabToolTip(2, '\n'.join(wrap(self.segmentclass_features.progname.title() + ' - ' + \
        self.segmentclass_features.proginfo)))
        
        self.tabWidget.addTab(self.segmentAlign2dTab, self.segmentalign2d_features.progname.title())
        self.tabWidget.setTabToolTip(3, '\n'.join(wrap(self.segmentalign2d_features.progname.title() + ' - ' + \
        self.segmentalign2d_features.proginfo)))
        
        self.tabWidget.addTab(self.segClassExamTab, self.segclassexam_features.progname.title())
        self.tabWidget.setTabToolTip(4, '\n'.join(wrap(self.segclassexam_features.progname.title() + ' - ' + \
        self.segclassexam_features.proginfo)))
        
        self.tabWidget.addTab(self.segClassLayerTab, self.segclasslayer_features.progname.title())
        self.tabWidget.setTabToolTip(5, '\n'.join(wrap(self.segclasslayer_features.progname.title() + ' - ' + \
        self.segclasslayer_features.proginfo)))
        
        self.tabWidget.addTab(self.segLayer2LatticeTab, self.seglayer2lattice_features.progname.title())
        self.tabWidget.setTabToolTip(6, '\n'.join(wrap(self.seglayer2lattice_features.progname.title() + ' - ' + \
        self.seglayer2lattice_features.proginfo)))
        
        self.tabWidget.addTab(self.segmentPlotTab, self.segmentplot_features.progname.title())
        self.tabWidget.setTabToolTip(7, '\n'.join(wrap(self.segmentplot_features.progname.title() + ' - ' + \
        self.segmentplot_features.proginfo)))
        

class Segment2dMain(QMainWindow, GuiActions):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.package = 'emspring'        
        TwodExamCentral = Segment2dGui()
        self.setCentralWidget(TwodExamCentral)

        # inherit body of layout of actions
        self.setupUi(self)

def main():
    app = QApplication(sys.argv)
    window = Segment2dMain()

    window.show()
    app.exec_()

if __name__ == '__main__':
    main()
