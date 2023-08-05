# Author: Carsten Sachse 17-Feb-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Spring (Single Particle Reconstruction from Images of kNown Geometries) - 
suite of programs for processing cryo-EM images of helices
"""
from PyQt4.QtCore import SIGNAL, SLOT, Qt, QRect
from PyQt4.QtGui import QMessageBox, QAction, QIcon, QMenu, QMenuBar, QToolBar, \
    QWidget
from spring.csinfrastr.cslogger import GetMetaData
from spring.csinfrastr.csproductivity import ExtLauncher
import os


class GuiActionsMenuTrigger(object):

    def openManual(self):
        """openManual(self)
        Opens the manual supplied with this application in the user's
        web browser.
        """
        web_address = 'http://www.sachse.embl.de/emspring'
        
        self.manual_browser = ExtLauncher()
        self.manual_browser.qlaunch_open_file(web_address)
        
        
class GuiActionsMenu(GuiActionsMenuTrigger):
    def createFileMenu(self):
        # open
        
        self.openAction = QAction(QIcon(os.path.join(os.path.dirname(__file__),
        '{pardir}{sep}images{sep}icons{sep}open.png'.format(pardir=os.pardir, sep=os.sep))), 'Open Parameter File',
        self)
        
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.setStatusTip('Open')

        self.saveAction = QAction(QIcon(os.path.join(os.path.dirname(__file__),
        '{pardir}{sep}images{sep}icons{sep}save.png'.format(pardir=os.pardir, sep=os.sep))), 'Save Parameter File',
        self)
        
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip('Save')

        # exit
        
        self.exitAction = QAction(QIcon(os.path.join(os.path.dirname(__file__),
        '{pardir}{sep}images{sep}icons{sep}exit.png'.format(pardir=os.pardir, sep=os.sep))), 'Exit Spring', self)
        
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit')
        self.connect(self.exitAction, SIGNAL('triggered()'), SLOT('close()'))

        # File menu
        self.menu_File = QMenu(self.menubar)
        self.menu_File.setTitle('&File')
        self.menu_File.setObjectName('menu_File')
        self.menu_File.addAction(self.openAction)
        self.menu_File.addAction(self.saveAction)
        self.menu_File.addAction(self.exitAction)


    def createViewMenu(self):
        self.beginnerAction = QAction('Beginner', self)
        self.beginnerAction.setShortcut('Ctrl+1')
        self.beginnerAction.setStatusTip('Beginner')
        self.beginnerAction.setToolTip('Displays beginner-level spring programs')

        self.intermediateAction = QAction('Intermediate', self)
        self.intermediateAction.setShortcut('Ctrl+2')
        self.intermediateAction.setStatusTip('Intermediate')
        self.intermediateAction.setToolTip('Displays intermediate-level spring programs')

        self.expertAction = QAction('Expert', self)
        self.expertAction.setShortcut('Ctrl+3')
        self.expertAction.setStatusTip('Expert')
        self.expertAction.setToolTip('Displays expert-level spring programs')

        #  View menu
        self.menu_View = QMenu(self.menubar)
        self.menu_View.setTitle('&View')
        self.menu_View.setObjectName('menu_View')
        self.menu_View.addAction(self.beginnerAction)
        self.menu_View.addAction(self.intermediateAction)
        self.menu_View.addAction(self.expertAction)
        

    def createHelpMenu(self):
        ## create actions
        # about
        self.aboutAction = QAction('Information about Spring', self)
        self.aboutAction.setStatusTip('About')
        self.connect(self.aboutAction, SIGNAL('triggered()'), self.helpAbout)

        # manual
        
        self.manualAction = QAction(QIcon(os.path.join(os.path.dirname(__file__),
        '{pardir}{sep}images{sep}icons{sep}help.png'.format(pardir=os.pardir, sep=os.sep))), 'Documentation - Open ' + \
        'Manual', self)
        
        self.manualAction.setStatusTip('Documentation')
        self.connect(self.manualAction, SIGNAL('triggered()'), self.openManual)

        # Help menu
        self.menu_Help = QMenu(self.menubar)
        self.menu_Help.setTitle('&Help')
        self.menu_Help.setObjectName('menu_Help')
        self.menu_Help.addAction(self.aboutAction)
        self.menu_Help.addAction(self.manualAction)


class GuiActions(QWidget, GuiActionsMenu):
    def setupUi(self, Window):

        self.statusBar()
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0,0,543,27))
        self.setMenuBar(self.menubar)

        self.createFileMenu()
        self.createViewMenu()
        self.createHelpMenu()
        
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_View.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        ## Toolbar
        self.toolbar = QToolBar()
#        self.toolbar.setGeometry(QRect(100,100,543,27))
#        self.toolbar.setGeometry(QRect(100,500,543,27))
#        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.openAction)
        self.toolbar.addAction(self.saveAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.beginnerAction)
        self.toolbar.addAction(self.intermediateAction)
        self.toolbar.addAction(self.expertAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.manualAction)
        
        self.addToolBar(Qt.ToolBarArea(Qt.LeftToolBarArea), self.toolbar)

    def helpAbout(self): 
        meta = GetMetaData(self.package)
        eggmeta = meta.release_meta()
        QMessageBox.about(self, 'About Scambl',
            """<b>%s (%s)</b> <p>%s <p>&copy; %s <p>Author: %s <p>Maintainer: %s, %s <p>License: %s<p>Status: %s""" % \
            (self.package.title(), eggmeta['Version'], __doc__, eggmeta['Copyright'], eggmeta['Author'],
            eggmeta['Maintainer'], eggmeta['Author-email'], eggmeta['License'], 
            eggmeta['Classifier: Development Status']))

