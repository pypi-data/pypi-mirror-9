# Author: Carsten Sachse 17-Feb-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Spring (Single Particle Reconstruction from Images of kNown Geometries) - 
suite of programs for processing cryo-EM images of helices
"""
from argparse import ArgumentParser
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QStackedWidget, QGridLayout, QComboBox, QLabel, QFileDialog
from spring.csinfrastr.csdatabase import SpringDataBase, RefinementCycleTable, RefinementCycleHelixTable, \
    RefinementCycleSegmentTable, RefinementCycleSegmentSubunitTable, refine_base, SegmentTable, HelixTable, \
    CtfMicrographTable, CtfFindMicrographTable, CtfTiltMicrographTable, SubunitTable, base, GridTable, GridRefineTable, \
    grid_base
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import GetMetaData
from spring.springgui.spring2d_launch import Segment2dGui
from spring.springgui.spring3d_launch import Spring3dGui
from spring.springgui.spring_menu import GuiActions
from spring.springgui.springmicrograph import SpringMicrographGui
import os
import spring.springgui.spring2d_launch
import spring.springgui.spring3d_launch
import spring.springgui.springmicrograph
import sys


class SpringGuiTop(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)

        self.suitename = os.path.basename(sys.argv[0])
        self.setWindowTitle('%s' %self.suitename)

        self.subPackageComboBox = QComboBox()
        self.subPackageComboBox.addItems(['Springmicrograph', 'Spring2d', 'Spring3d'])
        
        
class SpringGui(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        self.springguitop = SpringGuiTop()
        
        self.stackedWidget = QStackedWidget()
        self.springMicrographW = SpringMicrographGui()
        self.spring2dW = Segment2dGui()
        self.spring3dW = Spring3dGui()
        
        self.suite_description = QLabel()
        self.springmicrograph_description = '{0}'.format(spring.springgui.springmicrograph.__doc__)
        self.spring2d_description = '{0}'.format(spring.springgui.spring2d_launch.__doc__)
        self.spring3d_description = '{0}'.format(spring.springgui.spring3d_launch.__doc__)
        
        self.suite_description.setText(self.springmicrograph_description)

        self.stackedWidget.addWidget(self.springMicrographW)
        self.stackedWidget.addWidget(self.spring2dW)
        self.stackedWidget.addWidget(self.spring3dW)
        
        layout = QGridLayout()
        layout.addWidget(self.springguitop.subPackageComboBox, 0, 0, 1, 1)
        layout.addWidget(self.suite_description, 0, 1, 1, 1)

        layout.addWidget(self.stackedWidget, 1, 0, 4, 4)
        layout.setColumnStretch(0, 0)
        self.setLayout(layout)
        
        self.connect(self.springguitop.subPackageComboBox, SIGNAL('currentIndexChanged(QString)'), self.setWidgetStack)
    
    def setWidgetStack(self, text):
        if text == 'Springmicrograph':
            self.stackedWidget.setCurrentIndex(0)
            self.suite_description.setText(self.springmicrograph_description)
        elif text == 'Spring2d':
            self.stackedWidget.setCurrentIndex(1)
            self.suite_description.setText(self.spring2d_description)
        elif text == 'Spring3d':
            self.stackedWidget.setCurrentIndex(2)
            self.suite_description.setText(self.spring3d_description)
        

class SpringMain(QMainWindow, GuiActions):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.package = 'emspring'

        self.guiWindow = SpringGui()
        
        # inherit body of layout of actions
        self.setupUi(self)
        self.connect(self.beginnerAction, SIGNAL('triggered()'), self.changeToBeginnerDisplay)
        self.connect(self.intermediateAction, SIGNAL('triggered()'), self.changeToIntermediateDisplay)
        self.connect(self.expertAction, SIGNAL('triggered()'), self.changeToExpertDisplay)
        self.connect(self.openAction, SIGNAL('triggered()'), self.openParFile)
        self.connect(self.saveAction, SIGNAL('triggered()'), self.saveParFile)
        
        self.setCentralWidget(self.guiWindow)
        self.changeToBeginnerDisplay()


    def getCurrentTab(self):
        currentTab = self.guiWindow.stackedWidget.currentWidget().tabWidget.currentWidget().springTab

        return currentTab


    def openParFile(self):
        fname = QFileDialog.getOpenFileName(self , 'Choose file', '.', 'Files ({0})'.format('*.par'))
        if fname != '':
            from spring.csinfrastr.csreadinput import ReadInputFile
            currentTab = self.getCurrentTab()
            currentTab.parset.filename = fname
            inp = ReadInputFile(currentTab.parset)
            currentTab.enterParametersInGui(inp.parameters)
            
        
    def saveParFile(self):
        fname = str(QFileDialog.getSaveFileName(self , 'Save file', '.', '{0}'.format('Parameter text file (*.par);; ' +\
        'Python submission script (*.py)' ))) 
        
        if fname != '':            
            currentTab = self.getCurrentTab()
            currentTab.readParams()
            
        if fname.endswith('par'):
            Features().write_parameters_in_file(currentTab.parset.parameters, fname)
        elif fname.endswith('py'):
            sub_string  = Features().get_submission_script_str(currentTab.parset.progname, currentTab.parset.parameters)
            script = open(fname, 'w')
            script.write(sub_string)
            script.close()
            
            
    def removeTabsFromIndices(self, tab_indices):
        for each_index in tab_indices:
            self.guiWindow.stackedWidget.currentWidget().tabWidget.removeTab(each_index)


    def removeAllTabsFromAllWidgets(self):
        self.currentIndex = self.guiWindow.stackedWidget.currentIndex()
        self.currentTabIndex = self.guiWindow.stackedWidget.currentWidget().tabWidget.currentIndex()
        for each_index in [0, 1, 2]:
            self.guiWindow.stackedWidget.setCurrentIndex(each_index)
            
            tab_indices = list(range(self.guiWindow.stackedWidget.currentWidget().tabWidget.count()))
            tab_indices.reverse()
            self.removeTabsFromIndices(tab_indices)


    def removeTabsInThreeWidgetsFromIndices(self, indices_one, indices_two, indices_three):
        self.guiWindow.stackedWidget.setCurrentIndex(0)
        self.removeTabsFromIndices(indices_one)
        self.guiWindow.stackedWidget.setCurrentIndex(1)
        self.removeTabsFromIndices(indices_two)
        self.guiWindow.stackedWidget.setCurrentIndex(2)
        self.removeTabsFromIndices(indices_three)


    def displayEntriesBasedOnLevel(self, level):
        for eachWidgetIndex in list(range(self.guiWindow.stackedWidget.count())):
            self.guiWindow.stackedWidget.setCurrentIndex(eachWidgetIndex)
            for eachTabIndex in list(range(self.guiWindow.stackedWidget.currentWidget().tabWidget.count())):
                self.guiWindow.stackedWidget.currentWidget().tabWidget.setCurrentIndex(eachTabIndex)
                
                if level == 'beginner':
                    self.guiWindow.stackedWidget.currentWidget().tabWidget.currentWidget().\
                    springTab.hideEntriesBasedOnLevel(0)
        

    def setBackToPreviousView(self):
        self.guiWindow.stackedWidget.setCurrentIndex(self.currentIndex)
        self.guiWindow.stackedWidget.currentWidget().tabWidget.setCurrentIndex(self.currentTabIndex)


    def changeToBeginnerDisplay(self):
        self.setWindowTitle('Beginner')
        
        self.removeAllTabsFromAllWidgets()
        self.addAllExpertTabs()
        self.displayEntriesBasedOnLevel('beginner')
        self.removeTabsInThreeWidgetsFromIndices([6, 5, 4, 3, 1, 0], [7, 6, 5, 4, 3, 2, 1], [7, 6, 5, 4, 3, 1, 0])
        
        self.setBackToPreviousView()
        
        
    def changeToIntermediateDisplay(self):
        self.setWindowTitle('Intermediate')
    
        self.removeAllTabsFromAllWidgets()
        self.addAllExpertTabs()
        self.displayEntriesBasedOnLevel('intermediate')
        self.removeTabsInThreeWidgetsFromIndices([6, 5, 4, 3], [7, 6, 5, 3, 1], [7, 6, 4, 1, 0])
        
        self.setBackToPreviousView()
        
        
    def addAllExpertTabs(self):
        self.guiWindow.springMicrographW.addScanSpringTabs()
        self.guiWindow.spring2dW.addSpring2dTabs()
        self.guiWindow.spring3dW.addSpring3dTabs()


    def changeToExpertDisplay(self):
        self.setWindowTitle('Expert')
        
        self.removeAllTabsFromAllWidgets()
        self.addAllExpertTabs()
        self.displayEntriesBasedOnLevel('expert')
        
        self.setBackToPreviousView()
        

class AutoRefinementCycleTable(object):
    pass
 

class AutoRefinementCycleHelixTable(object):
    pass
 

class AutoRefinementCycleSegmentTable(object):
    pass
 

class AutoRefinementCycleSegmentSubunitTable(object):
    pass
 

class AutoSegmentTable(object):
    pass
 

class AutoHelixTable(object):
    pass
 

class AutoCtfMicrographTable(object):
    pass
 

class AutoCtfFindMicrographTable(object):
    pass
 

class AutoCtfTiltMicrographTable(object):
    pass
 

class AutoSubunitTable(object):
    pass


class AutoGridTable(object):
    pass
 

class AutoGridRefineTable(object):
    pass
 

class DataBaseUpdate(object):    
    def update_refinement_db(self, input_db, output_db):
        s = SpringDataBase()
        tables = ['cycles', 'cycle_helices', 'cycle_segments', 'cycle_subunits']
    
        autotables = [AutoRefinementCycleTable, AutoRefinementCycleHelixTable, AutoRefinementCycleSegmentTable,
        AutoRefinementCycleSegmentSubunitTable]
    
        target_tables = [RefinementCycleTable, RefinementCycleHelixTable, RefinementCycleSegmentTable,
        RefinementCycleSegmentSubunitTable]
    
        session = s.autoload_tables_into_session(input_db, tables, autotables)
        updated_session = s.setup_sqlite_db(refine_base, output_db)
    
        for each_autotable, each_target_table in zip(autotables, target_tables):
            updated_session = s.transfer_records_from_table(each_autotable, each_target_table, session, updated_session)
        updated_session.commit()
        

    def update_spring_db(self, input_db, output_db):
        s = SpringDataBase()
        tables = ['segments', 'helices', 'CtfMicrographs', 'CtfFindMicrographs', 'CtfTiltMicrographs', 'subunits']

        autotables = [AutoSegmentTable, AutoHelixTable, AutoCtfMicrographTable, AutoCtfFindMicrographTable,
        AutoCtfTiltMicrographTable, AutoSubunitTable]

        target_tables = [SegmentTable, HelixTable, CtfMicrographTable, CtfFindMicrographTable,CtfTiltMicrographTable,
        SubunitTable]
    
    
        session = s.autoload_tables_into_session(input_db, tables, autotables)
        updated_session = s.setup_sqlite_db(base, output_db)
    
        for each_autotable, each_target_table in zip(autotables, target_tables):
            updated_session = s.transfer_records_from_table(each_autotable, each_target_table, session, updated_session)
        updated_session.commit()


    def update_grid_db(self, input_db, output_db):
        s = SpringDataBase()
        tables = ['grids', 'grid_refine']
        autotables = [AutoGridTable, AutoGridRefineTable]
        target_tables = [GridTable, GridRefineTable]
    
        session = s.autoload_tables_into_session(input_db, tables, autotables)
        updated_session = s.setup_sqlite_db(grid_base, output_db)
    
        for each_autotable, each_target_table in zip(autotables, target_tables):
            updated_session = s.transfer_records_from_table(each_autotable, each_target_table, session, updated_session)
        updated_session.commit()


def define_program_options():
    proginfo = __doc__
    progname = 'emspring'
    eggmeta = GetMetaData(progname).release_meta()
    parser = ArgumentParser(prog=progname, description=proginfo)
    parser.add_argument('-inp', '--input', action='store', help='source database (*db) file name')
    parser.add_argument('-out', '--output', action='store', help='updated database (*db) file name')

    parser.add_argument('--version', action='version', version='GUI from package {0}-{1}'.format(progname.title(),
    eggmeta['Version']))

    parser.add_argument('-udb', '--update_db', action='store', help='Choose whether to update \'spring.db\', ' + \
    '\'refinement.db\' or \'grid.db\'.')

    args = parser.parse_args()

    return args


def main():
    args = define_program_options()
    
    if args.update_db is None:
        app = QApplication(sys.argv)
        window = SpringMain()

        window.show()
        app.exec_()

    if args.update_db in ['refinement.db', 'spring.db', 'grid.db'] and args.input is None and args.output is None: 
        print 'No databases were updated. Please provide input and output names for databases.'
    elif args.update_db in ['refinement.db']:
        DataBaseUpdate().update_refinement_db(args.input, args.output)
    elif args.update_db in ['spring.db']:
        DataBaseUpdate().update_spring_db(args.input, args.output)
    elif args.update_db in ['grid.db']:
        DataBaseUpdate().update_grid_db(args.input, args.output)
            

if __name__ == '__main__':
    main()

