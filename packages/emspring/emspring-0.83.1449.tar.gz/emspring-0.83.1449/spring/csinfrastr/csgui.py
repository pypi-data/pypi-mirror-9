#!/usr/bin/env python
# Author: Carsten Sachse 21-Sep-2010
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from PyQt4.QtCore import QSignalMapper, SIGNAL, SLOT, Qt, QThread, pyqtSignal, QSemaphore
from PyQt4.QtGui import QApplication, QWidget, QGridLayout, QVBoxLayout, QLineEdit, QDoubleSpinBox, QCheckBox, QLabel, \
    QPushButton, QProgressBar, QStatusBar, QFrame, QTextBrowser, QMessageBox, QFileDialog, QFont, QCompleter, QComboBox, \
    QListWidget, QAbstractItemView, QTabWidget
from collections import OrderedDict
from functools import partial
from glob import glob
from math import log10
from random import random
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import NameGenerator
from spring.csinfrastr.csproductivity import ExtLauncher
from textwrap import wrap
from time import sleep
import os
"""
* Several classes for Graphical User Interface'
"""


class LauncherGui(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self._run_semaphore = QSemaphore(1)
        
    def pass_program_command_line(self, progname, dirprogname):
        self.progname = progname
        self.dirprogname = dirprogname

    def run(self):
        if self._run_semaphore.available() == 0:
            self._run_semaphore.release(1)

        self.proc = ExtLauncher()
        self.proc.qlaunch(self.progname, self.dirprogname)
        self.proc.proc.waitForFinished(-1)
    
        self.stop()
            
    def stop(self):
        self.proc.finished()
        self._run_semaphore.acquire(1)
        
    def __del__(self):
        self.exiting = True
        self.wait()
        
        
class ProgressBarUpdater(QThread):
    #: this signal is emitted whenever the barUpdater has performed a single
    #  step
    progress = pyqtSignal(int)
    #: this signal publishes the minimum amount of required steps
    minimumChanged = pyqtSignal(int)
    #: this signal publishes the maximum amount of required steps
    maximumChanged = pyqtSignal(int)
    #: this signal gets the logfile while it is written
    log = pyqtSignal(str)
    #: this signal transmits the error
    err = pyqtSignal(str)

    def __init__(self, pardict=None, statedict = None, progname=None, parent=None):
        """
        this semaphore is used to stop the thread from outside.  As long
        as the thread is permitted to run, it has yet a single resource
        available.  If the thread is stopped, this resource is acquired,
        and the thread breaks its counting loop at the next iteration.
        """
        QThread.__init__(self, parent)
        self.maximum = 100.0
        self.parameters = pardict
        self.program_states = statedict
        self.progname = progname
        
        self._run_semaphore = QSemaphore(1)

    def readLogncount(self, logfile = None):
        if logfile is None: logfile = self.logfile
        fh = open(logfile)
        fh.seek(0 , os.SEEK_END)  # Go to the end of the file
        hasended = False
        state = 0
        while True:
            QApplication.processEvents()
            line = fh.readline()
            if not line:
                sleep(0.1)    # Sleep briefly
                continue
            
            self.log.emit(line.strip())
            if line.find(':progress state:') >= 0:
                part_line = line.split(':')[-1]
                percent = int(part_line.split('%')[0].strip())
                if percent * 100.0 / (self.maximum) > state: 
                    state = percent * 100.0 / (self.maximum)
                    self.progress.emit(state)
            if line.find('End of program {0}'.format(self.progname[0:-4])) >= 0:
                self.progress.emit(100)
                hasended = True
                self.err.emit('Status: Completed.')
                break
            if line.find('Error:') >= 0 and line.find('TypeError:') < 0:
                spliterr = line.split(':')
                self.err.emit('Status: Interrupted ({0}).'.format(spliterr[0].strip(':')))
                hasended = True
                break
            for event in self.program_states:
                if line.find(':' + event) >= 0:
                    self.err.emit('Status: {0}'.format(self.program_states[event]))
                    break
            # check, if the thread is still permitted to run.  This test
            # fails, if the single resource of this semaphore is acquired,
            # which is done by the stop() method, just to stop work at
            # precisly this point
            if self._run_semaphore.available() == 0:
                # release the resource again to enable a restart of this barUpdater
                self._run_semaphore.release(1)
                # break the loop.  A real barUpdater would typically roll back
                # his work to leave the state of the application unchanged,
                # because the work was forcibly interrupted.
                break
            if hasended is True:
                break
        fh.close()

    def run(self):
        """
        published our minimum and maximum values.  A real barUpdater thread
        would typically calculate the number of required steps

        update maximum by multiplying by number of files and number images on stack
        """
        
        self.minimumChanged.emit(1)
        self.maximumChanged.emit(self.maximum)
        
        while True:
            if os.path.exists(self.logfile): 
                break
        self.readLogncount(self.logfile)
        

    def stop(self):
        """
        acquire the single resource of our run semaphore.  No resources
        are now available anymore, so next time, run() checks the number
        of available resources, it sees none and returns.
        """
        lfile = open(self.logfile, 'a')
        lfile.write('%s was interrupted by the GUI' %self.progname)
        lfile.close()

        self._run_semaphore.acquire(1)
        
    def __del__(self):
        self.exiting = True
#        self.wait()
        
        
class NumbersOptionsGuiWindow(object):

    def appendWidgetToLevel(self, *widgets):
        for widget in widgets:
            if self.level[self.name] in ['beginner']:
                self.beginners.append(widget)
            elif self.level[self.name] in ['intermediate']:
                self.intermediates.append(widget)
            elif self.level[self.name] in ['expert']:
                self.experts.append(widget)

    def compute_number_of_digits_from_properties(self, obj, name):
        obj.digits = log10(obj.properties[name].step)
        if obj.digits > 0:
            obj.digits = 0
        else:
            obj.digits = abs(obj.digits)
        return obj


    def setToolTipIncludingLineBreak(self, hint_txt):
        return self.thisWidget.setToolTip('\n'.join(wrap(hint_txt)))
    

    def convert_angstrom_string(self, name):
        """
        >>> from spring.csinfrastr.csgui import NumbersOptionsGuiWindow 
        >>> n = NumbersOptionsGuiWindow()
        >>> n.convert_angstrom_string('This is my Angstrom')
        'This is my \\xc5'
        >>> n.convert_angstrom_string('This is my Angstrom site')
        'This is my \\xc5 site'
        >>> n.convert_angstrom_string('This is my first Angstrom, second Angstrom and third Angstrom')
        'This is my first \\xc5, second \\xc5 and third \\xc5'
        """
        split_angstrom = name.split('Angstrom')
        lname = u'\xc5'.encode('latin-1').join(split_angstrom)
            
        return lname
    

    def prepareSpinBox(self):
        if self.name.find('Angstrom') >= 0: 
            lname = self.convert_angstrom_string(self.name)
        else:
            lname = self.name
        self.label.setText('%s' %(lname))
        self = self.compute_number_of_digits_from_properties(self, self.name)
        self.thisWidget = QDoubleSpinBox()

        self.setToolTipIncludingLineBreak('{0} Example (default): \'{1}\''.format(self.hints[self.name], 
        self.default_params[self.name]))

        self.appendWidgetToLevel(self.label)
        

    def insertOneSpinBox(self):
        self.widgets[self.name]=self.thisWidget
        self.gridlayout.addWidget(self.thisWidget, self.cellrow + 1, 2, 1, 2)
        self.thisWidget.setRange(self.properties[self.name].minimum, self.properties[self.name].maximum)
        self.thisWidget.setSingleStep(self.properties[self.name].step)
        self.thisWidget.setDecimals(self.digits)
        self.appendWidgetToLevel(self.thisWidget)
        

    def insertDoubleSpinBox(self):
        self.widgets[self.name + '1']=self.thisWidget
        self.gridlayout.addWidget(self.thisWidget, self.cellrow + 1, 2)
        self.thisWidget.setRange(self.properties[self.name].minimum, self.properties[self.name].maximum)
        self.thisWidget.setSingleStep(self.properties[self.name].step)
        self.thisWidget.setDecimals(self.digits)
        self.appendWidgetToLevel(self.thisWidget)

        self.thisWidget = QDoubleSpinBox()
        self.widgets[self.name + '2']=self.thisWidget
        self.gridlayout.addWidget(self.thisWidget, self.cellrow + 1, 3)
        self.thisWidget.setRange(self.properties[self.name].minimum, self.properties[self.name].maximum)
        self.thisWidget.setSingleStep(self.properties[self.name].step)
        self.thisWidget.setDecimals(self.digits)

        self.setToolTipIncludingLineBreak('{0} Example (default): \'{1}\''.format(self.hints[self.name], 
        self.default_params[self.name]))

        self.appendWidgetToLevel(self.thisWidget)
    
    
    def insertCheckBox(self):
        self.thisWidget = QCheckBox()
        self.widgets[self.name]=self.thisWidget
        self.gridlayout.addWidget(self.thisWidget, self.cellrow + 1, 2, 1, 2)
        self.thisWidget.setText('%s' %(self.name))

        self.setToolTipIncludingLineBreak('{0} Example (default): \'{1}\''.format(self.hints[self.name], 
        self.default_params[self.name]))

        self.appendWidgetToLevel(self.thisWidget)


class FilesGuiWindow(object):
    def insertLineEdit(self):
        self.label.setText('%s' %(self.name))
        self.thisWidget = QLineEdit()
        self.widgets[self.name]=self.thisWidget
        self.gridlayout.addWidget(self.thisWidget, self.cellrow + 1, 2, 1, 2)

        self.setToolTipIncludingLineBreak('{0} Example (default): \'{1}\''.format(self.hints[self.name], 
        self.default_params[self.name]))

        self.appendWidgetToLevel(self.label, self.thisWidget)

    def setLineEditAccordingToFileProperties(self):
        if self.properties[self.name].ftype == 'getFile':
            self.button.setText('Input')
            self.connect(self.button, SIGNAL('clicked()'), self.getfilemapper, SLOT('map()'))
            self.getfilemapper.setMapping(self.button, str(self.cellrow))
            self.button.setToolTip('Browse file')
            self.gridlayout.addWidget(self.button, self.cellrow + 1, 4)
        elif self.properties[self.name].ftype == 'getFiles':
            self.button.setText('Input')
            self.connect(self.button, SIGNAL('clicked()'), self.getfilesmapper, SLOT('map()'))
            self.getfilesmapper.setMapping(self.button, str(self.cellrow))
            self.button.setToolTip('Browse file')
            self.gridlayout.addWidget(self.button, self.cellrow + 1, 4)
        elif self.properties[self.name].ftype == 'saveFile':
            self.addOpenButtonToViewResult()
        elif self.properties[self.name].ftype == 'getDir':
            self.button.setText('Directory')
            self.connect(self.button, SIGNAL('clicked()'), self.getdirmapper, SLOT('map()'))
            self.getdirmapper.setMapping(self.button, str(self.cellrow))
            self.button.setToolTip('Browse directory')
            self.gridlayout.addWidget(self.button, self.cellrow + 1, 4)
        
        if self.properties[self.name].ftype in ['getFile', 'getFiles', 'getDir']:
            self.appendWidgetToLevel(self.button)
            self.widgets[self.name + 'button']=self.button
        

    def addOpenButtonToViewResult(self):
        self.openbutton.setText('Open result')
        self.openbutton.setToolTip('Open output file')
        self.openbutton.setEnabled(False)
        self.connect(self.openbutton, SIGNAL('clicked()'), self.openbuttonmapper, SLOT('map()'))
        self.openbuttonmapper.setMapping(self.openbutton, str(self.cellrow))
        self.widgets[self.name + 'openbutton'] = self.openbutton
        self.gridlayout.addWidget(self.openbutton, self.cellrow + 1, 4)
        self.appendWidgetToLevel(self.openbutton)
        

    def connectCheckBoxToEnableOther(self):
        """
        * Function connect widget to Checkbox and dis and enable upon click 
        """
        if self.name in self.relatives:
            if type(self.parameters[self.name]) is tuple and type(self.parameters[self.relatives[self.name][0]]) is \
            bool:
                self.connect(self.widgets[self.relatives[self.name][1]], SIGNAL('toggled(bool)'),
                              self.widgets[self.name + '1'], SLOT('setEnabled(bool)'))
                self.widgets[self.name + '1'].setEnabled(False)
                self.connect(self.widgets[self.relatives[self.name][0]], SIGNAL('toggled(bool)'), 
                             self.widgets[self.name + '2'], SLOT('setEnabled(bool)'))
                self.widgets[self.name + '2'].setEnabled(False)
                for widg in [self.label]:
                    self.connect(self.widgets[self.relatives[self.name][1]], SIGNAL('toggled(bool)'), 
                                 widg, SLOT('setEnabled(bool)'))
                    widg.setEnabled(False)
                    self.connect(self.widgets[self.relatives[self.name][0]], SIGNAL('toggled(bool)'), 
                                 widg, SLOT('setEnabled(bool)'))
                    widg.setEnabled(False)
            elif type(self.parameters[self.name]) is not tuple and type(self.parameters[self.relatives[self.name]]) is \
            bool:
                for widg in [self.thisWidget, self.button, self.label]:
                    self.connect(self.widgets[self.relatives[self.name]], SIGNAL('toggled(bool)'), 
                                 widg, SLOT('setEnabled(bool)'))
                    widg.setEnabled(False)


    def insertComboBox(self):
        self.label.setText('{0}'.format(self.name))
        self.thisWidget = QComboBox()
        choices = [each_choice.capitalize() for each_choice in self.properties[self.name].choices]
        self.thisWidget.addItems(choices)
        self.widgets[self.name]=self.thisWidget
        self.gridlayout.addWidget(self.thisWidget, self.cellrow + 1, 2, 1, 2)

        self.setToolTipIncludingLineBreak('{0} Example (default): \'{1}\''.format(self.hints[self.name], 
        self.default_params[self.name]))

        self.appendWidgetToLevel(self.label, self.thisWidget)
        

class GuiWindow(NumbersOptionsGuiWindow, FilesGuiWindow):

    def setupUi(self, Window):
        self.setWindowTitle('%s' %self.progname)

        self.gridlayout = QGridLayout(self)

        la = QLabel()
        la.setText(self.pinfo)
        self.gridlayout.addWidget(la, 0, 0, 1, 5, Qt.AlignCenter | Qt.AlignJustify)

        self.widgets = OrderedDict()
        
        self.beginners = []
        self.intermediates = []
        self.experts = []
        for self.cellrow, self.name in enumerate(self.parameters):
            if self.level[self.name] in ['beginner', 'intermediate', 'expert']:
                self.label = QLabel()
                # prepare button
                self.button = QPushButton()
                self.openbutton = QPushButton()
                if type(self.parameters[self.name]) is bool:
                    self.insertCheckBox()
                    
                elif type(self.parameters[self.name]) in [int, float] or type(self.parameters[self.name]) is tuple:
                    self.prepareSpinBox()
                    if type(self.parameters[self.name]) in [int, float]:
                        self.insertOneSpinBox()
                    elif type(self.parameters[self.name]) is tuple:
                        self.insertDoubleSpinBox()
                elif type(self.parameters[self.name]) == str:
                    if self.properties[self.name].__str__().startswith('file'):
                        self.insertLineEdit()
                        self.setLineEditAccordingToFileProperties()
                    elif self.properties[self.name].__str__().startswith('choice'):
                        self.insertComboBox()
                self.gridlayout.addWidget(self.label, self.cellrow + 1, 1)
                self.connectCheckBoxToEnableOther()
                self.widgets[self.name + 'label']=self.label
            
        # PushButton Start
        self.pbstart = QPushButton() 
        self.pbstart.setObjectName('Startbutton')
        self.pbstart.setText('OK')
        self.pbstart.setToolTip('Start %s' %self.progname)
        self.gridlayout.addWidget(self.pbstart, self.cellrow + 2, 4)

        # PushButton Stop
        self.pbstop = QPushButton() 
        self.pbstop.setObjectName('Stopbutton')
        self.pbstop.setText('Cancel')
        self.pbstop.setToolTip('Cancel %s' %self.progname)
        self.pbstop.setEnabled(False)
        self.gridlayout.addWidget(self.pbstop, self.cellrow + 2, 3)

        self.gridlayout.setColumnStretch(0, 0)

        # a PushButton to enter the defaults
        self.pbdef = QPushButton()
        self.pbdef.setObjectName('Defaultbutton')
        self.pbdef.setText('Defaults')
        self.pbdef.setFixedWidth(80)
        self.pbdef.setToolTip('Default values are filled from %s' %self.progname)
        self.gridlayout.addWidget(self.pbdef, self.cellrow + 2, 0)
        self.gridlayout.setColumnStretch(0, 0)

        # Progressbar
        self.progressbar = QProgressBar(self)
        self.gridlayout.addWidget(self.progressbar, self.cellrow + 2, 1, 1, 1)

        # Statusbar
        self.statusBar = QStatusBar()
        self.statusBar.showMessage('Status: Ready')
        self.gridlayout.addWidget(self.statusBar, self.cellrow + 3, 1, 1, 3)

        # additional textbrowser
        self.logFrame = QFrame()
        self.logFrame.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)

        self.loglayout = QVBoxLayout()
        self.logFrame.setMinimumWidth(500)
        self.logFrame.setLayout(self.loglayout)
        self.textBrowser = QTextBrowser(self)
        self.textBrowser.setFontPointSize(QFont().pointSize()-2)
        self.loglayout.addWidget(self.textBrowser)
        self.textBrowser.clear()
#        self.gridlayout.addWidget(self.logFrame, 0, 5, self.cellrow + 2, 5)
        self.gridlayout.addWidget(self.logFrame, self.cellrow + 4, 1, 6, 4)
        self.logFrame.hide()

        # CheckBox expand dialog
        self.logButton = QCheckBox()
        self.logButton.setCheckable(True)
        self.logButton.setText('Log')
        self.logButton.setToolTip('Log will display logfile in console below')
        self.gridlayout.addWidget(self.logButton, self.cellrow + 2, 5)
        
        self.setupAdditionalParameters()
            

    def activateAdditionalOptions(self):
        
        sel_keys = [ self.additional_keys[each_index.row()] for each_index in self.listoptions.selection.selectedIndexes() ]
        added_relatives = [self.relatives[each_key] for each_key in sel_keys if each_key in self.relatives.keys()]
        
        sel_keys += added_relatives
        self.active_parameter_keys = self.minimal_param_keys + sel_keys
        
        widget_keys = [each_widg for each_widg in self.widgets if each_widg not in self.minimal_widg_keys]
        [self.widgets[each_widg].setVisible(False) for each_widg in widget_keys]
        
        for each_key in sel_keys:
            widget_keys = [each_widg for each_widg in self.widgets if each_widg.startswith(each_key)]
            [self.widgets[each_widg].setVisible(True) for each_widg in widget_keys]


    def updateMinimalKeys(self):
        self.minimal_widg_keys = []
        self.minimal_param_keys = []
        for each_key in self.active_parameter_keys:
            self.minimal_param_keys.append(each_key)
            attached_keys = [each_widg for each_widg in self.widgets if each_widg.startswith(each_key)]
            self.minimal_widg_keys += attached_keys


    def setupAdditionalParameters(self):
        self.levels = ['beginner', 'intermediate', 'expert']
        self.levelchoice = QComboBox()
        self.levelchoice.addItems([each_level.title() for each_level in self.levels])
        self.levelchoice.setToolTip('Change the level of input parameters from beginner to expert.')
        self.connect(self.levelchoice, SIGNAL('currentIndexChanged(int)'), self.hideEntriesBasedOnLevel)
        self.gridlayout.addWidget(self.levelchoice, 0, 7, 1, 1)
        
        self.listlabel = QLabel()
        self.listlabel.setText('Additional parameters (level)')
        self.gridlayout.addWidget(self.listlabel, 0, 6, 1, 1)
        
        self.listoptions = QListWidget()
        self.listoptions.setSelectionMode(QAbstractItemView.MultiSelection)
        self.listoptions.selection = self.listoptions.selectionModel()
        self.listoptions.setToolTip('Choose additional parameters.')
        self.connect(self.listoptions, SIGNAL('itemClicked(QListWidgetItem*)'), self.activateAdditionalOptions)
        self.gridlayout.addWidget(self.listoptions, 1, 6, self.cellrow - 1, 2)
        self.additional_keys = [each_name for each_name in self.parameters if self.level[each_name] != 'beginner']
        self.listoptions.addItems(self.additional_keys)
        
        self.active_parameter_keys = [each_key for each_key in self.level if self.level[each_key] == 'beginner']
        self.updateMinimalKeys()

        
class GUI(QWidget, GuiWindow):
    """
    * Class to receive input parameters from GUI

    #. Input = default parameter dictionary
    #. Output = updated parameter dictionary
    """
    def __init__(self, parset, parent = None):
        QWidget.__init__(self, parent)

        self.parset = parset
        self.parameters = parset.parameters
        self.default_params = parset.parameters.copy()
        self.pinfo = parset.proginfo
        self.hints = parset.hints
        self.properties = parset.properties
        self.program_states = parset.program_states
        self.relatives = parset.relatives
        self.level = parset.level

        self.progname = parset.progname

        self.getfilemapper = QSignalMapper(self)
        self.getfilesmapper = QSignalMapper(self)
        self.savefilemapper = QSignalMapper(self)
        self.getdirmapper = QSignalMapper(self)
        self.openbuttonmapper = QSignalMapper(self)
        self.readParamsMapper = QSignalMapper(self)

        # inherit body of layout
        self.setupUi(self)

        # the actual barUpdater thread
        self.lineUpdater = Updater(self.default_params, self.properties, self)
        self.lineUpdater.updatedDirListSignal.connect(partial(self.updateLineEditCompleter))
        # once autocompleter started it is then updated every time mouse is moved
        self.lineUpdater.start()
        self.setMouseTracking(True)

        # the actual barUpdater thread
        self.barUpdater = ProgressBarUpdater(self.parameters, self.program_states, self.progname, self)

        self.connect(self.getfilemapper, SIGNAL('mapped(const QString &)'), self.getFile)
        self.connect(self.getfilesmapper, SIGNAL('mapped(const QString &)'), self.getFiles)
        self.connect(self.savefilemapper, SIGNAL('mapped(const QString &)'), self.saveFile)
        self.connect(self.getdirmapper, SIGNAL('mapped(const QString &)'), self.getDir)
        self.connect(self.openbuttonmapper, SIGNAL('mapped(const QString &)'), self.openDemandedOutput)

        # PushButton Start connect
        self.connect(self.pbstart, SIGNAL('clicked()'), self.readParametersFromGui )

        # PushButton Stop connect
        self.connect(self.pbstop, SIGNAL('clicked()'), self.startOver)

        # a PushButton to enter the defaults
        self.connect(self.pbdef, SIGNAL('clicked()'), self.enterDefaults)

        # receive progressbar
        self.barUpdater.progress.connect(self.progressbar.setValue)

        # CheckBox expand dialog
        self.connect(self.logButton, SIGNAL('toggled(bool)'), self.logFrame, SLOT('setVisible(bool)'))

        # update log continuously
        self.barUpdater.log.connect(partial(self.textBrowser.append))
        self.barUpdater.err.connect(partial(self.statusBar.showMessage))
        
        # switch the enabled states of the actions according to whether the
        # barUpdater is running or not
        self.barUpdater.finished.connect(partial(self.jobDone))

    def startOver(self):
        self.barUpdater.stop()
        self.guiJob.stop()
        self.startOverSignal = True
        

    def getFileFromDialog(self, value):
        rkey = list(self.parameters.keys())[int(value)]
        fname = QFileDialog.getOpenFileName(self, 'Choose file', '.', 
            'Files ({0})'.format('*.' + ' *.'.join(self.properties[rkey].ext)))
        return fname

    def getFile(self, value):	
        fname = self.getFileFromDialog(value) 
        
        if fname != '':
            self.setTextInWidget(fname, value)


    def getFilesFromDialog(self, value, dir=os.curdir):
        rkey = list(self.parameters.keys())[int(value)]
        
        fname = QFileDialog.getOpenFileNames(self, 'Choose files', '{0}'.format(dir), 'Files ({0})'.\
        format('*.' + ' *.'.join(self.properties[rkey].ext)))
        
        return fname

    def getFiles(self, value):	
        fname = self.getFilesFromDialog(value) 
        
        if fname != []:
            self.setTextInWidget(fname.join(','), value)

    def saveFile(self, value):
        rkey = list(self.parameters.keys())[int(value)]
        
        fname = str(QFileDialog.getSaveFileName(self , 'Save file', '.', 'Files ({0})'.\
        format('*.' + ' *.'.join(self.properties[rkey].ext)))) 
        
        if fname != '':
            self.setTextInWidget(fname, value)

    def getDir(self, value):
        fname = str(QFileDialog.getExistingDirectory(self , 'Choose directory', '.')) 
        if fname != '':
            self.setTextInWidget(fname, value)

    def setTextInWidget(self, fname, value):
        self.thisWidget=self.widgets[list(self.parameters.keys())[int(value)]]
        self.thisWidget.setText(fname)


    def enterParametersInGui(self, parameters):
        for name in parameters:
            if name in self.active_parameter_keys:
                value = parameters[name]
            else:
                value = None
                
            if type(value) in [int, float]:
                self.thisWidget = self.widgets[name]
                self.thisWidget.setValue(value)
            elif type(value) is bool:
                if value is True:
                    self.thisWidget = self.widgets[name]
                    self.thisWidget.setCheckState(Qt.Checked)
            elif type(value) is tuple:
                self.thisWidget = self.widgets[name + '1']
                self.thisWidget.setValue(value[0])
                self.thisWidget = self.widgets[name + '2']
                self.thisWidget.setValue(value[1])
            elif type(value) is str:
                self.thisWidget = self.widgets[name]
                if self.properties[name].__str__().startswith('file'):
                    self.thisWidget.setText(value)
                elif self.properties[name].__str__().startswith('choice'):
                    index = self.thisWidget.findText(value.capitalize())
                    self.thisWidget.setCurrentIndex(index)


    def enterDefaults(self):
        self.enterParametersInGui(self.default_params)
        self.pbstart.setToolTip('Start {0} now.'.format(self.progname))

    def readParametersFromGui(self, event=None):
        self.scanParams()
        if self.warn is True:
            QMessageBox.warning(self, 'WARNING: incomplete set of input parameters',
                """<p>WARNING: Incomplete set of input parameters. Please enter requested \
                parameters in \'{0}\'.</br></p>""".format(self.last_name))
        else:
            self.jobStart()

    def scanParams(self):
        self.warn = False
        for self.last_name in self.parameters:
            if self.last_name in self.active_parameter_keys:
                if type(self.default_params[self.last_name]) is tuple:
                    self.thisWidget=self.widgets[self.last_name + '1']
                else:
                    self.thisWidget=self.widgets[self.last_name]
                
                if type(self.default_params[self.last_name]) is str and \
                not self.properties[self.last_name].__str__().startswith('choice'):
                    if not self.thisWidget.isHidden() and self.thisWidget.isEnabled():
                        if str(self.thisWidget.text()) is '':
                            self.warn = True
                            break


    def hideEntriesBasedOnLevel(self, intLevel):
        currentLevel = self.levels[intLevel]
        if currentLevel in ['expert']:
            self.active_parameter_keys = [each_key for each_key in self.level
                                          if self.level[each_key] in ['beginner', 'intermediate', 'expert']]

            self.additional_keys = []
            self.listoptions.setVisible(False)
            for every_item in self.beginners + self.intermediates + self.experts:
                every_item.show()
        else:
            for every_item in self.beginners + self.intermediates + self.experts:
                every_item.hide()
        
        if currentLevel in ['intermediate']:
            self.active_parameter_keys = [each_key for each_key in self.level 
                                          if self.level[each_key] in ['beginner', 'intermediate']]

            self.additional_keys = [each_name for each_name in self.parameters if self.level[each_name] in ['expert']]
            for every_item in self.beginners + self.intermediates:
                every_item.show()
        elif currentLevel in ['beginner']:
            self.active_parameter_keys = [each_key for each_key in self.level if self.level[each_key] in ['beginner']]
            self.additional_keys = [each_name for each_name in self.parameters 
                                    if self.level[each_name] in ['intermediate', 'expert']]

            for every_item in self.beginners:
                every_item.show()
                
        if currentLevel in ['beginner', 'intermediate']:
            self.listoptions.setVisible(True)
            self.listoptions.clear()
            self.listoptions.addItems(self.additional_keys)

        self.updateMinimalKeys()
    
    def readParams(self):
        for name in self.default_params:
            if name in self.active_parameter_keys:
                if type(self.default_params[name]) is bool:
                    self.thisWidget=self.widgets[name]
                    if self.thisWidget.isChecked():
                        self.parameters[name]=True
                    else:
                        self.parameters[name]=False
                elif type(self.default_params[name]) is int: 
                    self.thisWidget=self.widgets[name]
                    self.parameters[name]=int(self.thisWidget.value())
                elif type(self.default_params[name]) is float: 
                    self.thisWidget=self.widgets[name]
                    self.parameters[name]=float(self.thisWidget.value())
                elif type(self.default_params[name]) is tuple:
                    self.thisWidget=self.widgets[name + '1']
                    if type(self.default_params[name][0]) is int: 
                        first=int(self.thisWidget.value())
                    elif type(self.default_params[name][0]) is float: 
                        first=float(self.thisWidget.value())
                    self.thisWidget=self.widgets[name + '2']
                    if type(self.default_params[name][0]) is int: 
                        second=int(self.thisWidget.value())
                    elif type(self.default_params[name][0]) is float: 
                        second=float(self.thisWidget.value())
                    self.parameters[name]=tuple((first, second))
                elif type(self.default_params[name]) is str:
                    self.thisWidget=self.widgets[name]
                    if self.properties[name].__str__().startswith('file'):
                        self.parameters[name] = str(str(self.thisWidget.text()))
                    elif self.properties[name].__str__().startswith('choice'):
                        self.parameters[name] = str(str(self.thisWidget.currentText()))
#                if self.thisWidget.isHidden() and self.level[name] not in ['beginner']:
#                    self.parameters[name]=None
            else:
                self.parameters[name]=None
        

    def jobSetup(self):
        self.prgparfile = Features().write_parfile(self.parameters, self.progname)
        self.directory = NameGenerator().make_directory(self.progname)
        self.logfile = 'report' + os.extsep + 'log'#NameGenerator().make_logfile(self.progname)#
        self.dirprogname = '--f {0} --l {1} --d {2}'.format(self.prgparfile, self.logfile, self.directory)
        self.barUpdater.logfile = self.directory + os.sep + self.logfile
        
        
    def jobStart(self):
        self.statusBar.showMessage('Status: Initialized.')
        self.pbstart.setEnabled(False)
        self.pbstop.setEnabled(True)
        self.pbstop.setText('Cancel')
        self.readParams()
        self.startOverSignal = False
        self.enableOpenButton(False)
        self.jobSetup()
        self.guiJob = LauncherGui()
        self.guiJob.finished.connect(partial(self.jobDone))
        self.guiJob.pass_program_command_line(self.progname, self.dirprogname.split())
#        self.jobSetup()
#        self.guiJob = LauncherGui(self.progname, self.dirprogname.split())
#        self.guiJob.finished.connect(partial(self.jobDone))
        self.guiJob.start()
        self.barUpdater.start()

    def enableOpenButton(self, TrueOrFalse):
        for self.name in self.parameters:
            if type(self.parameters[self.name]) == str:
                if self.properties[self.name].__str__().startswith('file') and \
                                self.properties[self.name].ftype == 'saveFile':
                    self.widgets[self.name + 'openbutton'].setEnabled(TrueOrFalse)
                    self.widgets[self.name + 'openbutton'].setToolTip('Open %s' % self.parameters[self.name])

    def jobDone(self):
        self.pbstop.setEnabled(False)
        self.pbstart.setEnabled(True)
#        self.guiJob.finished()
        
        os.rename(self.prgparfile, self.directory + os.sep + 'parameters.par')
        if self.startOverSignal is False:
            self.enableOpenButton(True)
                    
    def openDemandedOutput(self, value):
        rkey = list(self.parameters.keys())[int(value)]
        outfile = self.directory + os.sep + os.path.basename(self.parameters[rkey])
        self.external_program = ExtLauncher()
        if os.path.exists(outfile):
            outfiles = [outfile]
        else:
            outfiles = self.getFilesFromDialog(value, self.directory)
        if outfiles != []:
            for each_file in outfiles:
                self.external_program.qlaunch_open_file(each_file)

    def mouseMoveEvent(self, event):
#        print 'Mouse Pointer is currently hovering at: ', event.pos()
        self.lineUpdater.start()

    def updateLineEditCompleter(self, completeDict):
        for name in self.default_params:
            if type(self.default_params[name]) is str:
                if self.properties[name].__str__().startswith('file'):
                    self.lineEditCompleter = QCompleter(completeDict[name])
                    self.lineEditCompleter.setCompletionMode(QCompleter.InlineCompletion)
                    self.lineEditCompleter.setCaseSensitivity(Qt.CaseInsensitive)
                
                    self.widgets[name].setCompleter(self.lineEditCompleter)

class Updater(QThread):
    """
    Class of function to perform update tasks
    """
    updatedDirListSignal = pyqtSignal(dict)
    def __init__(self, defdict=None, rangedict=None, parent=None):
        QThread.__init__(self, parent)

        self.default_params = defdict
        self.properties = rangedict

        self._run_semaphore = QSemaphore(1)

    def run(self):
        
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.
        self.updateFileAutoCompleter()

    def updateFileAutoCompleter(self):
        completeDict = {}
        QApplication.processEvents()
        for name in self.default_params:
            if type(self.default_params[name]) == str:
                if self.properties[name].__str__().startswith('file'):
                    # set up extension-specific completer 
                    completeDirList = []
                    for ext in self.properties[name].ext:
                        completeDirList += glob('*{0}{1}'.format(os.extsep, ext))
             
                    completeDict[name] = completeDirList
        self.updatedDirListSignal.emit(completeDict)
        sleep(random())

    def __del__(self):
        self.wait()


class QTabWidgetCloseable(QTabWidget):
    def __init__(self, parent = None):
        QTabWidget.__init__(self, parent)
        
        self.setTabsClosable(True)
        self.connect(self, SIGNAL('tabCloseRequested(int)'), self.closeTab)
        
        
    def closeTab(self, tab_id):
        if tab_id != 0:
            self.removeTab(tab_id)
            
        