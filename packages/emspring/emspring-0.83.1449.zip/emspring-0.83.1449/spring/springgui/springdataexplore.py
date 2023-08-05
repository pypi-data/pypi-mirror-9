# Author: Carsten Sachse 29-Aug-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from PyQt4.QtCore import SIGNAL, Qt, pyqtSignal, QVariant, QThread
from PyQt4.QtGui import QMainWindow, QWidget, QSizePolicy, QMessageBox, QLabel, QAction, QIcon, QFileDialog, QVBoxLayout, \
    QTableWidget, QTableWidgetItem, QPushButton, QGridLayout, QToolBar, QApplication
from matplotlib import cm
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import axes3d
from scipy.spatial import Delaunay
import matplotlib
import matplotlib.cbook as cbook
import numpy as np
import os

try:
    import visvis as vv
    from visvis.backends.backend_pyqt4 import Figure as vvFigure
except:
    pass

class NavigationToolbar2QTSpring(NavigationToolbar2QT):
    """
    Workaround inability to display svg icons with EMAN2/SPARX PyQT4 distribution.
    The only modification is in the extension of the icons files from svg -->png.
    """

    def _init_toolbar(self):
        self.basedir = os.path.join(matplotlib.rcParams[ 'datapath' ],'images')

        a = self.addAction(self._icon('home.png'), 'Home', self.home)
        a.setToolTip('Reset original view')
        a = self.addAction(self._icon('back.png'), 'Back', self.back)
        a.setToolTip('Back to previous view')
        a = self.addAction(self._icon('forward.png'), 'Forward', self.forward)
        a.setToolTip('Forward to next view')
        self.addSeparator()
        a = self.addAction(self._icon('move.png'), 'Pan', self.pan)
        a.setToolTip('Pan axes with left mouse, zoom with right')
        a = self.addAction(self._icon('zoom_to_rect.png'), 'Zoom', self.zoom)
        a.setToolTip('Zoom to rectangle')
        self.addSeparator()
        a = self.addAction(self._icon('subplots.png'), 'Subplots',
                self.configure_subplots)
        a.setToolTip('Configure subplots')

        a = self.addAction(self._icon('qt4_editor_options.png'),
                           'Customize', self.edit_parameters)
        a.setToolTip('Edit curves line and axes parameters')

        a = self.addAction(self._icon('filesave.png'), 'Save',
                self.save_figure)
        a.setToolTip('Save the figure')


        self.buttons = {}

        # Add the x,y location widget at the right side of the toolbar
        # The stretch factor is 1 which means any resizing of the toolbar
        # will resize this label instead of the buttons.
        if self.coordinates:
            self.locLabel = QLabel( '', self )
            self.locLabel.setAlignment(
                    Qt.AlignRight | Qt.AlignTop )
            self.locLabel.setSizePolicy(
                QSizePolicy(QSizePolicy.Expanding,
                                  QSizePolicy.Ignored))
            labelAction = self.addWidget(self.locLabel)
            labelAction.setVisible(True)

        # reference holder for subplots_adjust window
        self.adj_window = None


class NavigationToolbarQTAggSpring(NavigationToolbar2QTSpring):
    def _get_canvas(self, fig):
        return FigureCanvasQTAgg(fig)


class SpringToolbar(NavigationToolbarQTAggSpring):
    def __init__(self, parent_one=None, parent_two=None):
        NavigationToolbarQTAggSpring.__init__(self, parent_one, parent_two)
        
        # push the current view to define home if stack is empty
        
        self._views = cbook.Stack()
        self._positions = cbook.Stack()  # stack of subplot positions
#        self._views.clear()
#        self._positions.clear()
        
        self.update()
        if self._views.empty(): 
            self.push_current()
        self._idDrag=self.canvas.mpl_connect('motion_notify_event', self.mouse_move)
        self._xypress = None
        self.push_current()
        self._button_pressed = None

        self.basedir = os.path.dirname(__file__)
        
        a = self.addAction(self._icon('..{sep}images{sep}icons{sep}zoom-in.png'.format(sep=os.sep)), 'Zoom-in', self._on_custom_zoom_in)
        zoom_tip = '- also use scrollwheel to zoom in or out. Right mouse button to drag canvas.'
        a.setToolTip('Zoom-in ' + zoom_tip)
        a = self.addAction(self._icon('..{sep}images{sep}icons{sep}zoom-out.png'.format(sep=os.sep)), 'Zoom-out', self._on_custom_zoom_out)
        a.setToolTip('Zoom-out ' + zoom_tip)
        

    def compute_updated_limits_after_zoom(self, zoom_factor, limits):
        x1, x2 = limits
        zoomed_offset = abs(x2 - x1) / zoom_factor
        zoomed_limits = x1 + zoomed_offset, x2 - zoomed_offset
        
        return zoomed_limits


    def zoom_in_or_out_of_figure(self, zoom_factor):

        if self._xypress is None:
            self._xypress = [((self.canvas.figure.axes[0], 0))]
        
        self.push_current()
        for a, ind in self._xypress:
            zoomed_x = self.compute_updated_limits_after_zoom(zoom_factor, a.get_xlim())
            zoomed_y = self.compute_updated_limits_after_zoom(zoom_factor, a.get_ylim())
        
            a.set_xlim(min(zoomed_x), max(zoomed_x))
            a.set_ylim(min(zoomed_y), max(zoomed_y))
        
        self.push_current()
        self._update_view()

    def _on_custom_zoom_in(self):
        zoom_factor = 1.25
        self.zoom_in_or_out_of_figure(zoom_factor)

    def _on_custom_zoom_out(self):
        zoom_factor = -1.25
        self.zoom_in_or_out_of_figure(zoom_factor)
        
    def drag_pan(self, event):
        'the drag callback with right-mouse button'

        self.push_current()
        for a, ind in self._xypress:
            #safer to use the recorded button at the press than current button:
            #multiple button can get pressed during motion...
            a.drag_pan(1, event.key, event.x, event.y)
        self.dynamic_update()


class SpringDataExplore3d(QWidget):
    def __init__(self, xyz_data, zxy_labels, *args):
        QWidget.__init__(self, *args)
        
        self.fig = vvFigure(self)
        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.fig._widget)
        
        self.setLayout(self.layout)
        
        self.plot3d(xyz_data, zxy_labels)
        
        
    def compute_meshindex_for_vertices(self, xyz):
        # set to convex surface for meshing
        # find center of data
        center = np.average(xyz, 0)
        #center data
        vxyz = xyz - center
        
        vx, vy, z = np.hsplit(vxyz, 3)
        # find x-y plane distance to each point
        radials = np.sqrt(vx**2 + vy**2)
        # get max and adjust so that arctan ranges between +-45 deg
        maxRadial = np.max(radials)/0.7
        #get angle on sphere
        xi =  np.arctan2(radials / maxRadial, 1)
        #force z axis data to sphere
        vz = maxRadial * np.cos(xi)
        vxyz = np.hstack([vx, vy, vz])
        vxyz = np.append(vxyz, [[0.7, 0.7, -0.7],[-0.7, 0.7, -0.7],[0.7, -0.7, -0.7],[-0.7, -0.7, -0.7]], axis=0)
           
        # Send data to convex_hull program qhull
        dly = Delaunay(vxyz)
        meshIndx = dly.convex_hull
        
        # Check each triangle facet and flip if
        # vertex order puts back side out
        
        for index, (I1, I2, I3) in enumerate(meshIndx):
            a = vxyz[I1,:] - vxyz[I2,:] 
            b = vxyz[I2,:] - vxyz[I3,:] 
            c = np.cross(a, b)
            if np.dot(c, vxyz[I2,:]) > 0:
                meshIndx[index] = (I1, I3, I2)
                
        return meshIndx
    

    def set_aspect_ratio(self, x_distance, y_distance, z_distance, ax):
        z_aspect_ratio = max(1, int(np.max([x_distance, y_distance]) / float(z_distance)))
        y_aspect_ratio = max(1, int(np.max([x_distance, z_distance]) / float(y_distance)))
        
        ax.daspect = 1, y_aspect_ratio, z_aspect_ratio
        
        return ax
    

    def set_limits_and_labels(self, zxy_labels, x, y, z, ax):
        ax.SetLimits(rangeX=[min(x), max(x)], rangeY=[min(y), max(y)], rangeZ=[min(z), max(z)])
        ax.axis.zLabel = zxy_labels[0]
        ax.axis.xLabel = zxy_labels[1]
        ax.axis.yLabel = zxy_labels[2]
        
        return ax
    

    def plot3d(self, xyz, zxy_labels):
                
        meshIndex = self.compute_meshindex_for_vertices(xyz)
                
        x, y, z = np.hsplit(xyz, 3)
        
        x_distance = np.max(x) - np.min(x)
        y_distance = np.max(y) - np.min(y)
        z_distance = np.max(z) - np.min(z)
        
        xyz = np.append(xyz, [[np.max(x), np.max(y), np.min(z)],
                              [np.min(x), np.max(y), np.min(z)],
                              [np.max(x), np.min(y), np.min(z)],
                              [np.min(x), np.min(y), np.min(z)]], axis=0)

        #normalize depVal for color mapping   
        depVal = z
        dataRange = np.max(depVal) - np.min(depVal)
        depVal = (depVal- np.min(depVal)) /  dataRange    
    
        # Get axes
        ax = vv.gca()
        ax = self.set_aspect_ratio(x_distance, y_distance, z_distance, ax)
        ax = self.set_limits_and_labels(zxy_labels, x, y, z, ax)
        
        ms = vv.Mesh(ax, xyz, faces=meshIndex, normals=xyz)
        ms.SetValues(np.reshape(depVal,np.size(depVal)))
        
        ms.ambient = 0.9
        ms.diffuse = 0.4
        ms.colormap = vv.CM_JET
        ms.faceShading='smooth'
        ms.edgeColor = (0.5,0.5,0.5,1)
        ms.edgeShading = 'smooth'
        ms.faceColor = (1,1,1,1)
        ms.shininess = 50
        ms.specular = 0.35
        ms.emission = 0.45
      
        
class SpringDataExploreDraw(object):
        
    def extract_rise_rotation_from_symmetry_grid(self, symmetry_grid):
        helical_rises, temp = zip(*symmetry_grid[:,0].tolist())
        temp, helical_rotations = zip(*symmetry_grid[0,].tolist())
        
        return helical_rises, helical_rotations
        
        
    def set_adjustable_tick_values(self, subplot, rise_count, rotation_count, rise_start_end, rotation_start_end):
        rise_start, rise_end = rise_start_end
        rotation_start, rotation_end = rotation_start_end
        
        x = list(range(rise_count))
        y = list(range(rotation_count))
        
        def rotations(x, pos):
            new_tick = rotation_start + x * ((rotation_end - rotation_start) / float(rotation_count - 1))
            return '{0:.4}'.format(new_tick)

        def rises(y, pos):
            new_tick = rise_start + y * ((rise_end - rise_start) / float(rise_count - 1))
            return '{0:.4}'.format(new_tick)
        
        formatter_x = FuncFormatter(rotations)
        formatter_y = FuncFormatter(rises)
        subplot.xaxis.set_major_formatter(formatter_x)
        subplot.yaxis.set_major_formatter(formatter_y)
        
        return subplot


    def set_x_and_y_label(self, subplot, label_x_and_y):
        label_y, label_x = label_x_and_y
        subplot.set_xlabel(label_x)
        subplot.set_ylabel(label_y)
        
        return subplot
    

    def set_grid_values_and_labels_to_tick_axes(self, subplot, matrix, symmetry_grid):
        rise_count, rotation_count = matrix.shape
        rotation_start_end = (symmetry_grid[0][0][1], symmetry_grid[0][-1][1])
        
        rise_start_end = (symmetry_grid[0][0][0], symmetry_grid[-1][0][0])
        
        subplot = self.set_adjustable_tick_values(subplot, rise_count, rotation_count, rise_start_end,
        rotation_start_end)

        return subplot
        

    def add_colorbar_to_figure(self, label, array_img):
        cax = self.fig.add_axes()
        cbar = self.fig.colorbar(array_img, cax)
        cbar.set_label(label)


    def finish_drawing_and_update_views_for_toolbar_navigation(self):
        self.canvas.draw()
        self.mpl_toolbar.update()


    def draw_2dmatrix_plot(self, matrix, data_grid_pairs, labels):
        self.axes = self.fig.add_subplot(111)
#        self._xypress = [(self.axes, 0)]
        
        column_count, row_count = matrix.shape
        for each_column_index in range(column_count):
            line, = self.axes.plot(range(row_count), [each_column_index]*row_count, '.', markersize=0.01, picker=5)  # 5 points tolerance

        label_x_and_y = labels[1:]
        self.axes = self.set_grid_values_and_labels_to_tick_axes(self.axes, matrix, data_grid_pairs)
        self.axes = self.set_x_and_y_label(self.axes, label_x_and_y)
        
        array_img  = self.axes.imshow(matrix, origin='lower', interpolation='nearest')
        if labels[0] != '':
            self.add_colorbar_to_figure(labels[0], array_img)
        
        self.finish_drawing_and_update_views_for_toolbar_navigation()
        
        self.matrix = matrix
        self.symmetry_grid = data_grid_pairs
        
        
    def draw_1d_dimensions_stacked(self, matrix, data_grid_pairs, labels, picked_point):
        helical_rotation_cc = matrix[picked_point[1]].ravel()
        if len(helical_rotation_cc) > 1:
            self.axes1 = self.fig.add_subplot(211)
        else:
            self.axes1 = self.fig.add_subplot(111)
#        self._xypress = [(self.axes1, 0)]
        
        helical_rises, temp = zip(*data_grid_pairs[:,0].tolist())
        helical_rise_cc = matrix[:,picked_point[0]].ravel()
        
        heading = labels[0]
        
        self.axes1.set_ylabel(heading)
        self.axes1.set_xlabel(labels[1])
        line, = self.axes1.plot(helical_rises, helical_rise_cc, 'x', picker=5, label=labels[1])
        self.axes1.plot(helical_rises, helical_rise_cc)
        
        if len(helical_rotation_cc) > 1:
            self.axes2 = self.fig.add_subplot(212)
            self.axes2.set_ylabel(heading)
            self.axes2.set_xlabel(labels[2])
            temp, helical_rotations = zip(*data_grid_pairs[0,].tolist())
            line2, = self.axes2.plot(helical_rotations, helical_rotation_cc, 'x', picker=5, label=labels[2])
            self.axes2.plot(helical_rotations, helical_rotation_cc)
        
        self.finish_drawing_and_update_views_for_toolbar_navigation()
        
        
    def draw_3d_surface_plot(self, data, data_grid_pairs, labels):
        self.axes5 = self.fig.add_subplot(111, projection='3d')

        temp, helical_rotations = zip(*data_grid_pairs[0,].tolist())
        helical_rises, temp = zip(*data_grid_pairs[:,0].tolist())
        
        helical_rotations, helical_rises = np.meshgrid(helical_rotations, helical_rises)
        
        surf = self.axes5.plot_surface(helical_rises, helical_rotations, data, rstride=1, cstride=1, cmap=cm.jet,
        alpha=0.6, linewidth=0, antialiased=False)
        
        self.axes5.w_zaxis.set_major_locator(LinearLocator(10))
        self.axes5.w_zaxis.set_major_formatter(FormatStrFormatter('%.03f'))
        
        self.axes5.set_zlabel(labels[0])
        self.axes5.set_xlabel(labels[1])
        self.axes5.set_ylabel(labels[2])
#        cset = self.axes5.contour(helical_rises, helical_rotations, data, zdir='z')
#        cset = self.axes5.contour(helical_rises, helical_rotations, data, zdir='x')
#        cset = self.axes5.contour(helical_rises, helical_rotations, data, zdir='y')
#        fig.colorbar(surf)
        
        self.add_colorbar_to_figure(labels[0], surf)
        
        self.finish_drawing_and_update_views_for_toolbar_navigation()
        
        
    def on_draw(self, data_grid, data_grid_pairs, labels, dimension='2d', picked_point=((0,0))):
        self.previously_picked_point=picked_point
        if dimension == '1d':
            self.draw_1d_dimensions_stacked(data_grid, data_grid_pairs, labels, picked_point)
        elif dimension == '2d':
            self.draw_2dmatrix_plot(data_grid, data_grid_pairs, labels)
        elif dimension == '3d':
            self.draw_3d_surface_plot(data_grid, data_grid_pairs, labels)
    
        self.dimension = dimension
        
        
class SpringDataExplore(QMainWindow,  QThread, SpringDataExploreDraw):
    picked_left_point = pyqtSignal(tuple)
    picked_middle_point = pyqtSignal(tuple)
    picked_label = pyqtSignal(str)
    index_2d = pyqtSignal(tuple)
    
    def __init__(self, figure=None, parent=None):
        QMainWindow.__init__(self, parent)
        QThread.__init__(self, parent) 

        self.create_new_figure(figure)
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar('Ready')


    def save_plot(self):
        file_choices = 'PNG (*.png)|*.png'
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    
    def set_about_text(self, msg):
        self.about_message = msg
        
        
    def on_about(self):
        msg = self.about_message
        QMessageBox.about(self, 'About the demo', msg.strip())
    
    
    def on_pick(self, event):
        if event.mouseevent.button in [1,2]:
            try:
                grid_point = event.artist
                xdata = grid_point.get_xdata()
                ydata = grid_point.get_ydata()
                ind = event.ind
                label = event.artist.get_label()
                picked_point = ((float(xdata[ind]), float(ydata[ind])))
                if event.mouseevent.button == 1:
                    if self.dimension == '1d':
                        self.picked_label.emit(label)
                        self.index_2d.emit(self.previously_picked_point)
                    self.picked_left_point.emit(picked_point)
                elif event.mouseevent.button == 2:
                    self.picked_middle_point.emit(picked_point)
            except TypeError:
                msg = 'Please zoom in further in unambiguously assign data grid point.'
                QMessageBox.warning(self, 'Impossible to assign data grid point', msg.strip())
        
    
    def zoom_in_or_out(self, event):
        if event.button == 'up' or 'down':
            if event.button == 'up':
                zoom_factor = 1.1
            elif event.button == 'down':
                zoom_factor = -1.1
                
            x, y = event.x, event.y
            self.mpl_toolbar._xypress=[]
            
            for i, a in enumerate(self.mpl_toolbar.canvas.figure.get_axes()):
                if x is not None and y is not None and a.in_axes(event) \
                        and a.get_navigate() and a.can_zoom():
                    self.mpl_toolbar._xypress.append(( a, i))

            self.mpl_toolbar.zoom_in_or_out_of_figure(zoom_factor)
            

    def press_pan(self, event):
        self.mpl_toolbar._xypress = []
        self.mpl_toolbar._button_pressed = 3
        for i, a in enumerate(self.canvas.figure.get_axes()):
            if event.x is not None and event.y is not None and a.in_axes(event) and a.get_navigate():
                a.start_pan(event.x, event.y, 3)
                self.mpl_toolbar._xypress.append((a, i))
                self.canvas.mpl_disconnect(self.mpl_toolbar._idDrag)
                self.mpl_toolbar._idDrag = self.canvas.mpl_connect('motion_notify_event', self.mpl_toolbar.drag_pan)
                

    def release_pan(self, event):
        if self.mpl_toolbar._button_pressed is None:
            return
        self.canvas.mpl_disconnect(self.mpl_toolbar._idDrag)
        self.mpl_toolbar._idDrag=self.canvas.mpl_connect('motion_notify_event', self.mpl_toolbar.mouse_move)
        for a, ind in self.mpl_toolbar._xypress:
            a.end_pan()
        if not self.mpl_toolbar._xypress: 
            return
        self.mpl_toolbar._xypress = []
        self.mpl_toolbar._button_pressed=None
        self.mpl_toolbar.push_current()
        self.mpl_toolbar.release(event)
        self.mpl_toolbar.draw()
        
    def drag_canvas_upon_button_press(self, event):
        if event.button == 3 and self.mpl_toolbar._button_pressed is None:
            self.press_pan(event)
            
            
    def release_canvas_upon_button_release(self, event):
        if event.button == 3 and self.mpl_toolbar._button_pressed is not None:
            self.release_pan(event)
    
    
    def create_new_figure(self, figure):
        self.main_frame = QWidget()
        if figure is None:
            self.fig = Figure()
        else:
            self.fig = figure
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setParent(self.main_frame)
        

    def create_main_frame(self):
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect('scroll_event', self.zoom_in_or_out)
        self.canvas.mpl_connect('button_press_event', self.drag_canvas_upon_button_press)
        self.canvas.mpl_connect('button_release_event', self.release_canvas_upon_button_release)
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = SpringToolbar(self.canvas, self.main_frame)
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.mpl_toolbar)
        vbox.addWidget(self.canvas)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    
    
    def create_status_bar(self, status_text):
        status_text = QLabel()
        self.statusBar().addWidget(status_text, 1)
        
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu('&File')
        
        load_file_action = self.create_action('&Save plot',
            shortcut='Ctrl+S', slot=self.save_plot, 
            tip='Save the plot')
        quit_action = self.create_action('&Quit', slot=self.close, 
            shortcut='Ctrl+Q', tip='Close the application')
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu('&Help')
        about_action = self.create_action('&About', 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))


    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)


    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal='triggered()'):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(':/%s.png' % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


class SpringDataExploreTable(QTableWidget):
    primary_id_signal = pyqtSignal(int)
    def __init__(self, table_matrix, labels, *args):
        QTableWidget.__init__(self, *args)
        
        self.setSortingEnabled(False)
        self.setColumnCount(table_matrix.shape[0])
        self.setRowCount(table_matrix.shape[1])
        self.setHorizontalHeaderLabels(labels)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        
        for column_index, each_column in enumerate(table_matrix):
            for row_index, each_data in enumerate(each_column):
                try:
                    each_item = QTableWidgetItem(float(each_data))
                except:
                    each_item = QTableWidgetItem(str(each_data))
                    
                each_item.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )

                try:
                    each_item.setData(0, QVariant(float(each_data)))
                except:
                    each_item.setData(0, QVariant(str(each_data)))
                self.setItem(row_index, column_index, each_item)
                
        self.connect(self.verticalHeader(), SIGNAL('sectionClicked(int)'), self.emit_row_from_table)
        
        self.sortItems(0)
        self.setSortingEnabled(True)
    
        self.selection = self.selectionModel() 
        
    def emit_row_from_table(self, row):
        indexes = self.selection.selectedIndexes()

        prim_id = self.item(indexes[0].row(), 0).text()
        self.primary_id_signal.emit(int(prim_id))
        

class SpringDataExploreTablePane(QWidget):
    def __init__(self, table_matrix, labels, *args):
        QWidget.__init__(self, *args)
        
        self.table_matrix = table_matrix
        self.labels = labels
        
        self.data_table = SpringDataExploreTable(self.table_matrix, self.labels)
        
        self.gridlayout = QGridLayout(self)

        self.exportAction = QAction(QIcon(os.path.join(os.path.dirname(__file__),
        '{pardir}{sep}images{sep}icons{sep}export_table.png'.format(pardir=os.pardir, sep=os.sep))),
         'Export table data', self)                         
        
        self.exportAction.setShortcut('Ctrl+E')
        self.connect(self.exportAction, SIGNAL('triggered()'), self.saveDataInFile)
        
        self.clipAction = QAction(QIcon(os.path.join(os.path.dirname(__file__),
        '{pardir}{sep}images{sep}icons{sep}clipboard.png'.format(pardir=os.pardir, sep=os.sep))), 
        'Copy data to clipboard', self)
        
        self.clipAction.setShortcut('Ctrl+C')
        self.connect(self.clipAction, SIGNAL('triggered()'), self.copySelectedCellsToClipboard)
        
        self.table_toolbar = QToolBar()
        self.table_toolbar.addAction(self.exportAction)
        self.table_toolbar.addAction(self.clipAction)
        
        self.gridlayout.addWidget(self.table_toolbar, 0, 0)
        self.gridlayout.addWidget(self.data_table, 1, 0)

        
    def saveDataInFile(self):
        fname = str(QFileDialog.getSaveFileName(self , 'Export table data', '.', 'Files ({0})'.\
        format(['*.csv', '*.tsv', '*.tab']))) 
        
        textTable = self.getSelectedCellsInTextFormat()
            
        if fname.endswith('csv'):
            delim_char = ','
        else:
            delim_char = '\t'
            
        if fname != '':
            import csv
    
            ofile = open(fname, 'w')
            ofile.write(delim_char.join(self.labels) + '\n')
            out = csv.writer(ofile, delimiter=delim_char)
            for each_row in textTable:
                out.writerow(each_row)
            
            ofile.close()
            
            
    def getSelectedCellsInTextFormat(self):
        indexes = self.data_table.selection.selectedIndexes()

        if indexes == []:
            swapped_table = self.table_matrix.T
            new_array = np.array([str(each_value) for each_value in swapped_table.reshape(swapped_table.size)])
            new_array = new_array.reshape(swapped_table.shape)
            textTable = new_array.tolist()
        else:
            columns = indexes[-1].column() - indexes[0].column() + 1
            rows = len(indexes) / columns
            textTable = [[''] * columns for i in list(range(rows))]
    
            for i, index in enumerate(indexes):
                textTable[i % rows][i / rows] = str(self.data_table.item(index.row(), index.column()).text())
    
        return textTable
    
        
    def copySelectedCellsToClipboard(self):
        textTable = self.getSelectedCellsInTextFormat()
        QApplication.clipboard().setText('\n'.join(('\t'.join(i) for i in textTable)))
        
class SpringCommon(object):
    def setup_spring_page_top(self, obj, feature_set):
        filename = ''
        if type(feature_set.parameters.values()[0]) is str:
            if os.path.exists(feature_set.parameters.values()[0]):
                filename = ': ' + os.path.basename(feature_set.parameters.values()[0])
                
        obj.setWindowTitle(feature_set.progname.title() + filename)
        obj.program_description = QLabel()
        obj.program_description.setText(feature_set.proginfo)
        obj.exit_button = QPushButton()
        obj.exit_button.setText('Exit')
        
        exitIcon = QIcon(os.path.join(os.path.dirname(__file__),
        '{pardir}{sep}images{sep}icons{sep}exit.png'.format(pardir=os.pardir, sep=os.sep)))
        
        obj.exit_button.setIcon(exitIcon)
        obj.exit_button.setShortcut('Ctrl+Q')
        obj.connect(obj.exit_button, SIGNAL('clicked()'), obj.close)
        obj.layout = QGridLayout()
        obj.layout.addWidget(obj.program_description, 0, 0, 1, 2)
        obj.layout.addWidget(obj.exit_button, 0, 4, 1, 1)
        
        return obj
