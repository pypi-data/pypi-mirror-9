# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
from EMAN2 import EMData, Util, EMNumPy, EMUtil
from fundamentals import ccfnp
import os
import shutil
from spring.csinfrastr.csdatabase import RefinementCycleHelixTable, RefinementCycleSegmentTable, SpringDataBase, base, \
    SegmentTable, HelixTable
from spring.csinfrastr.csproductivity import DiagnosticPlot
from spring.micprgs.scansplit import Micrograph
from spring.segment2d.segment import Segment
from spring.segment2d.segmentexam import SegmentExam
from spring.segment2d.segmentplot import SegmentPlot
from spring.segment3d.refine.sr3d_reconstruct import SegmentRefine3dFsc
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from spring.springgui.springdataexplore import SpringDataExploreDraw
from statistics import ccc
from utilities import model_blank

from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
from scipy.optimize.minpack import curve_fit
from sqlalchemy.sql.expression import desc, and_
from tabulate import tabulate

import matplotlib.cm as cm
import numpy as np


class EulerPlot(object):

    def read_angles_from_file(self, filename):
        f = open(filename, 'r')
        
        phi, theta, psi = [], [], []
        spider = False
        for each_line in f.readlines():
            if each_line.strip().startswith(';'):
                spider = True
            elif spider:
                psi.append(float(each_line.split()[2]))
                theta.append(float(each_line.split()[3]))
                phi.append(float(each_line.split()[4]))
            else:
                psi.append(float(each_line.split()[0]))
                theta.append(float(each_line.split()[1]))
                phi.append(float(each_line.split()[2]))
        
        f.close()

        return phi, theta, psi


    def spider_unit_vector_transformation_by_euler_angles(self, phi, theta, psi=None):
        """
        v = Rv', where  R is the matrix for transforming vector v' to vector v. 

        R = R(psi) * R(theta) * R(phi) 

         
        R(psi)   =   cos(psi)  sin(psi)  0
                    -sin(psi)  cos(psi)  0
                        0         0      1   
        
                     
        R(theta) =   cos(theta)  0 -sin(theta)
                        0        1     0
                     sin(theta)  0  cos(theta)
                     
        
        R(phi)   =   cos(phi)  sin(phi)  0 
                    -sin(phi)  cos(phi)  0 
                        0         0      1  
                        
        equivalent Euler angles phi, theta, psi = 180 + phi, theta, 180 + psi = \
        phi + 90, theta, 270 - psi
        
        """
        unit_vector = np.array([1,0,0])
        
        phi = np.deg2rad(phi)
        theta = np.deg2rad(theta)
        
        R_phi = np.array([[np.cos(phi), -np.sin(phi), 0],
            [np.sin(phi), np.cos(phi), 0],
            [0, 0, 1]])
        
        R_theta = np.array([[np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)]]) 
        
        R1 = np.dot(R_phi, unit_vector)
        R2 = np.dot(R_theta, R1)

        if psi is None:
            R3 = R2
        else:
            psi = np.deg2rad(psi)
            R_psi = np.array([[np.cos(psi), -np.sin(psi), 0],
                [np.sin(psi), np.cos(psi), 0],
                [0, 0, 1]])
        
            R3 = np.dot(R_psi, R2)
        
        return R3
    

    def convert_3d_xyz_vector_latitude_and_longitude(self, x, y, z):
        """
        >>> from spring.segment3d.refine.sr3d_diagnostics import EulerPlot
        >>> e = EulerPlot()
        >>> e.convert_3d_xyz_vector_latitude_and_longitude( 1., 1., 1.)
        (0.61547970867038748, 0.78539816339744828)
        >>> la, lo = e.convert_3d_xyz_vector_latitude_and_longitude( 1., 1., 1.)
        >>> e.convert_latitude_and_longitude_to_xyz(la, lo, np.sqrt(3))
        (0.99999999999999978, 0.99999999999999967, 1.0)
        """
        R = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        latitude = np.arcsin(z / R)
        longitude = np.arctan2(y, x)

        return latitude, longitude


    def convert_latitude_and_longitude_to_xyz(self, latitude, longitude, radius=1.0):
        x = radius * np.cos(latitude) * np.cos(longitude)
        y = radius * np.cos(latitude) * np.sin(longitude)
        z = radius * np.sin(latitude)
        
        return x, y, z 


    def plot_euler_angles_on_spherical_projection_scatter(self, fig, phi_angles, theta_angles, psi_angles):
        
        subplot = fig.add_subplot(111, projection='hammer')

        x, y, z = self.spider_unit_vector_transformation_by_euler_angles(phi_angles, theta_angles)
        latitude, longitude = self.convert_3d_xyz_vector_latitude_and_longitude(x, y, z)
         
        x0, y0, z0 = self.spider_unit_vector_transformation_by_euler_angles([0], [0])
        la0, lo0 = self.convert_3d_xyz_vector_latitude_and_longitude(x0, y0, z0)
        subplot.plot(longitude, latitude, 'x', markersize=3)
        subplot.plot(lo0, la0, 'x')

        subplot = self.set_label_and_grid_of_hammer_sphere(subplot)

        return fig
        

    def add_colorbar_to_upper_left_corner(self, fig, im):
        cax = fig.add_axes([0.01, 0.65, 0.01, 0.3])
        cbar = fig.colorbar(im, cax)
        cbar.set_label('Number of projections', fontsize=10)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(6)


    def set_label_and_grid_of_hammer_sphere(self, subplot):
        subplot.set_xlabel('Latitude ' + r'$(^\circ)$')
        subplot.set_ylabel('Longitude ' + r'$(^\circ)$')
        subplot.set_aspect('auto')
        subplot.grid(True, linewidth=0.2)
        
        return subplot


    def plot_euler_angles_on_spherical_projection(self, fig, phi_angles, theta_angles, psi_angles):
        
        subplot = fig.add_subplot(111, projection='hammer')

        x, y, z = self.spider_unit_vector_transformation_by_euler_angles(phi_angles, theta_angles)
        latitude, longitude = self.convert_3d_xyz_vector_latitude_and_longitude(x, y, z)
         
        bin_count = 90
        xedges = np.linspace(-np.pi, np.pi, bin_count) 
        yedges = np.linspace(-np.pi / 2.0, np.pi / 2.0, bin_count)

        H, xedges, yedges = np.histogram2d(longitude, latitude, bins=(xedges, yedges))
        X, Y = np.meshgrid(xedges, yedges)
        im = subplot.pcolormesh(X, Y, H.transpose(), cmap=cm.YlOrRd)

        self.add_colorbar_to_upper_left_corner(subplot.get_figure(), im)
            
        subplot = self.set_label_and_grid_of_hammer_sphere(subplot)

        return fig
        

    def plot_euler_angle_scatter(self, fig, phi_angles, theta_angles):
        subplot = fig.add_subplot(111)

        subplot = self.set_phi_theta_label_x_and_y(subplot)

        hex = subplot.hexbin(phi_angles, theta_angles, cmap=cm.YlOrRd)

        self.add_colorbar_to_upper_left_corner(subplot.get_figure(), hex)

        return fig


    def prepare_plot_including_solid_sphere(self, ax1, side_of_spere='front'):
        if side_of_spere in ['back']:
            view_angle = 180
        else:
            view_angle = 0
        ax1.view_init(0, view_angle)
        ax1.set_title('{0} of sphere'.format(side_of_spere.title()))
        ax1.set_aspect('equal')
        ax1.set_xticklabels([])
        ax1.set_zticklabels([])
        ax1.set_xlabel('x')
        ax1.set_ylabel('y')
        ax1.set_zlabel('z')
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = 1 * np.outer(np.cos(u), np.sin(v))
        y = 1 * np.outer(np.sin(u), np.sin(v))
        z = 1 * np.outer(np.ones(np.size(u)), np.cos(v))
        ax1.plot_surface(x, y, z, rstride=5, cstride=5, color='yellow')

        return ax1


    def plot_euler_angles_on_sphere(self, fig, phi_angles, theta_angles, psi_angles):
        from mpl_toolkits.mplot3d import Axes3D
        ax1 = fig.add_subplot(121, projection='3d')
        ax2 = fig.add_subplot(122, projection='3d')

        ax1 = self.prepare_plot_including_solid_sphere(ax1, side_of_spere='front')
        ax2 = self.prepare_plot_including_solid_sphere(ax2, side_of_spere='back')

        xx, yy, zz = self.spider_unit_vector_transformation_by_euler_angles(phi_angles, theta_angles)
        
        xxx = xx[xx >= 0]
        yyy = yy[xx >= 0]
        zzz = zz[xx >= 0]
        ax1.plot(xxx, yyy, zzz,'r.', markersize=3)

        xxx = xx[xx < 0]
        yyy = yy[xx < 0]
        zzz = zz[xx < 0]
        ax2.plot(xxx, yyy, zzz,'r.', markersize=3)

        return fig


    def set_phi_theta_label_x_and_y(self, subplot):
        subplot.set_xlabel(r'$\phi (^\circ)$')
        subplot.set_ylabel(r'$\theta (^\circ)$')

        return subplot


    def plot_euler_angles_on_polar_plot_scatter(self, fig, phi_angles, theta_angles, psi_angles):
        subplot = fig.add_subplot(111, polar=True)
        
        phi_rad = np.deg2rad(phi_angles) % (2 * np.pi)
        subplot.plot(phi_rad, theta_angles, 'x', markersize=3)
        subplot.grid(True)
        subplot.set_rmax(max(90, max(theta_angles)))
        subplot = self.set_phi_theta_label_x_and_y(subplot)
        
        return fig


    def plot_euler_angles_on_polar_plot_hist(self, fig, phi_angles, theta_angles, psi_angles):
        subplot = fig.add_subplot(111, polar=True)
        
        phi_rad = np.deg2rad(phi_angles) % (2 * np.pi)

        bin_count = 91
        xedges = np.linspace(0, 2 * np.pi, bin_count) 
        yedges = np.linspace(min(0, min(theta_angles)), max(theta_angles), bin_count)

        H, xedges, yedges = np.histogram2d(phi_rad, theta_angles, bins=(xedges, yedges))
        X, Y = np.meshgrid(xedges, yedges)
        im = subplot.pcolormesh(X, Y, H.transpose(), cmap=cm.YlOrRd)

        self.add_colorbar_to_upper_left_corner(subplot.get_figure(), im)
        subplot.grid(True)
        subplot = self.set_phi_theta_label_x_and_y(subplot)
        
        return fig

        
class SegmentRefine3dDiagnosticsVisualizeTicksMontages(SegmentRefine3dFsc):
    def add_color_bar_according_to_array(self, label, img, location):
        cax = self.fig.add_axes(location)
        cbar = self.fig.colorbar(img, cax)
        cbar.set_label(label, fontsize=8)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(5)


    def reformat_ticklabels_according_to_image_plot(self, helical_parameter, max_label_count):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> SegmentRefine3d().reformat_ticklabels_according_to_image_plot(range(31), 8)
        (['0.0', '4.0', '8.0', '12.0', '16.0', '20.0', '24.0', '28.0', '30.0'], 4)
        >>> SegmentRefine3d().reformat_ticklabels_according_to_image_plot(range(31), 6)
        (['0.0', '6.0', '12.0', '18.0', '24.0', '30.0'], 6)
        """
        rise_multiple = 1
        helical_parameter = np.array(helical_parameter, dtype=float)
        if len(helical_parameter) > max_label_count:
            rise_multiple = int(len(helical_parameter) / max_label_count) + 1
            
            helical_parameter = np.arange(helical_parameter[0], helical_parameter[-1], rise_multiple * \
            (helical_parameter[1] - helical_parameter[0])).tolist() + [helical_parameter[-1]]
            
        helical_parameter = ['{0:.4}'.format(parameter) for parameter in helical_parameter]
        
        return helical_parameter, rise_multiple

    def add_grid_to_plot(self, subplot, cc_array, symmetry_grid, color_gray=True):
        
        subplot = SpringDataExploreDraw().set_grid_values_and_labels_to_tick_axes(subplot, cc_array, symmetry_grid)
        
        if self.rise_rot_or_pitch_unit_choice in ['rise/rotation']:
            subplot.set_xlabel('Helical rotation (degrees)', fontsize=4)
            subplot.set_ylabel('Helical rise (Angstrom)', fontsize=4)
        if self.rise_rot_or_pitch_unit_choice in ['pitch/unit_number']:
            subplot.set_xlabel('Number of units per turn', fontsize=4)
            subplot.set_ylabel('Helical pitch (Angstrom)', fontsize=4)
        
        if color_gray:
            img = subplot.imshow(cc_array, cmap=cm.gray, interpolation='nearest', origin='lower')
        else:
            img = subplot.imshow(cc_array, cmap=cm.jet, interpolation='nearest', origin='lower')
            
        return img
    
            
    def montage_reprojections_to_image_according_to_given_shape(self, diagnostic_stack, symmetry_grid):
        symmetry_reprojection = EMData()
        
        symmetry_reprojection.read_image(diagnostic_stack, 0)
        xdimension = symmetry_reprojection.get_xsize()
        ydimension = symmetry_reprojection.get_ysize()
        new_xdimension = int(xdimension - 1)
        new_ydimension = int(ydimension - 1)
        stat = Micrograph().get_statistics_from_image(symmetry_reprojection)
        
        collection_of_all_rises = []
        for all_rises_index, all_rises in enumerate(symmetry_grid):
            rotation_collection_of_each_rise = []
            for each_rotation_index, each_symmetry_pair in enumerate(all_rises):
                each_reconstr_number = all_rises_index*len(all_rises) + each_rotation_index
                symmetry_reprojection.read_image(diagnostic_stack, each_reconstr_number)
                
                symmetry_reprojection = \
                Micrograph().adjust_gray_values_for_print_and_optimal_display(symmetry_reprojection)
                
                symmetry_reprojection = Util.window(symmetry_reprojection, new_xdimension, new_ydimension, 1, 0, 0, 0)
                
                symmetry_reprojection = Util.pad(symmetry_reprojection, xdimension, ydimension, 1, 0, 0, 0,
                '{0}'.format(stat.min))
                
                symmetry_reprojection_array = np.copy(EMNumPy.em2numpy(symmetry_reprojection))
                rotation_collection_of_each_rise.append(symmetry_reprojection_array)
            collection_of_all_rises.append(np.hstack(rotation_collection_of_each_rise))
        montage = np.vstack(collection_of_all_rises)
        
        return montage 
    
    
    def distribute_x_and_y_ticks_evenly_along_montage(self, subplot, montage, rotation_count, rise_count,
    xtick_count=None, ytick_count=None):
        if xtick_count is None:
            xtick_count = rotation_count
        if ytick_count is None:
            ytick_count = rise_count
            
        y_offset = montage.shape[0] / (rise_count)
        x_offset = montage.shape[1] / (rotation_count)
        yticks_location = np.linspace(0, montage.shape[0] - y_offset, ytick_count) + y_offset / 2
        xticks_location = np.linspace(0, montage.shape[1] - x_offset, xtick_count) + x_offset / 2
        subplot.xaxis.set_ticks(xticks_location)
        subplot.yaxis.set_ticks(yticks_location)
        
        return subplot
    

    def move_ticks_to_correct_location(self, subplot, montage, symmetry_grid):
        rise_count = symmetry_grid.shape[0]
        rotation_count = symmetry_grid.shape[1]
        ytick_count = 10
        xtick_count = 10
        if ytick_count > rise_count:
            ytick_count = rise_count
        if xtick_count > rotation_count:
            xtick_count = rotation_count
            
        subplot = self.distribute_x_and_y_ticks_evenly_along_montage(subplot, montage, rotation_count, rise_count,
        xtick_count, ytick_count)
        
        helical_rises, helical_rotations = \
        SpringDataExploreDraw().extract_rise_rotation_from_symmetry_grid(symmetry_grid)
        
        xtick_labels = np.linspace(helical_rotations[0], helical_rotations[-1], xtick_count)
        ytick_labels = np.linspace(helical_rises[0], helical_rises[-1], ytick_count)
        subplot.set_xticklabels(xtick_labels)
        subplot.set_yticklabels(ytick_labels)
        
        return subplot 
    
    
class SegmentRefine3dDiagnostics(SegmentRefine3dDiagnosticsVisualizeTicksMontages):
    def setup_statistics_plot_layout(self):
        
        segmentrefine3d_plot = DiagnosticPlot()
        segmentrefine3d_plot.plt.ioff()
            
        column_count = 4
        row_count = 3
        self.ax1 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (0, 0), rowspan=1, colspan=1)
        self.ax2 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (1, 0), rowspan=1, colspan=1)
        self.ax9 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (2, 0), rowspan=1, colspan=1)
        self.ax10 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (0, 1), rowspan=1, colspan=1)
        self.ax11 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (1, 1), rowspan=1, colspan=1)
        self.ax12 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (2, 1), rowspan=1, colspan=1)
        self.ax3 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (0, 2), rowspan=1, colspan=1)
        self.ax4 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (1, 2), rowspan=1, colspan=1)
        self.ax8 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (2, 2), rowspan=1, colspan=1)
        self.ax5 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (0, 3), rowspan=1, colspan=1)
        self.ax6 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (1, 3), rowspan=1, colspan=1)
        self.ax7 = segmentrefine3d_plot.plt.subplot2grid((row_count, column_count), (2, 3), rowspan=1, colspan=1)
#        self.ax7 = plt.subplot2grid((row_count, column_count), (2, 3), rowspan=1, colspan=1, projection='hammer')
        
        subplot_collection = [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6, self.ax7, self.ax8, self.ax9,
        self.ax10, self.ax11, self.ax12]
            
        subplot_collection = segmentrefine3d_plot.set_fontsize_to_all_ticklabels_of_subplots(subplot_collection)

        return segmentrefine3d_plot

    
    def visualize_in_plane_rotation_angles(self, subplot, in_plane_rotations):
        bin_count = 360
        subplot.hist(in_plane_rotations, bin_count, facecolor='g', rwidth=1, rasterized=True)
        subplot.set_xlabel('Segment polarity (degrees)', fontsize=6)
        subplot.set_xlim(-10, 370)
        
        return subplot
    

    def evaluate_in_plane_rotation_angles(self, subplot, ref_session, last_cycle, model_id):
        ref_segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.model_id == model_id).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).all()
        
        diff_in_plane_rotations = [each_ref_segment.norm_inplane_angle for each_ref_segment in ref_segments]
        
        subplot = self.visualize_in_plane_rotation_angles(subplot, diff_in_plane_rotations)
        
        return subplot
    
    
    def make_five_xticks_from_all_helix_ids(self, helix_ids):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> import numpy as np
        >>> SegmentRefine3d().make_five_xticks_from_all_helix_ids(np.arange(1, 22))
        [1, '', '', '', '', 6, '', '', '', '', 11, '', '', '', '', 16, '', '', '', '', 21]
        >>> SegmentRefine3d().make_five_xticks_from_all_helix_ids(np.arange(1, 3))
        [1, 2]
        >>> helix_ids = np.append(np.arange(1, 7), np.arange(9, 12))
        >>> SegmentRefine3d().make_five_xticks_from_all_helix_ids(helix_ids)
        [1, '', 3, '', 5, '', 9, '', 11]
        """
        five_tick_ids = np.rint(np.linspace(0, len(helix_ids) - 1, 5))
        tick_list = []
        for each_id, each_helix_id in enumerate(helix_ids):
            if each_id in five_tick_ids:
                tick_list.append(each_helix_id)
            else:
                tick_list.append('')
        
        return tick_list
    
    
    def plot_forward_difference_x_shift(self, subplot, ref_session, last_cycle, model_id, max_shift_range):
        
        ref_segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
        filter(RefinementCycleSegmentTable.model_id == model_id).\
        filter(RefinementCycleSegmentTable.selected == True).all()
        
        forward_differences = np.array([each_ref_segment.forward_diff_x_shift_A for each_ref_segment in ref_segments])
        forward_rot = np.array([each_ref_segment.forward_diff_inplane for each_ref_segment in ref_segments])
        forward_tilt = np.array([each_ref_segment.forward_diff_outofplane for each_ref_segment in ref_segments])

        bin_count = self.compute_bin_count_from_quantity_and_step(forward_differences, last_cycle.translation_step)
                                                     
        xshift_error = np.std(forward_differences) 
        inplane_error = np.std(forward_rot) 
        outofplane_error = np.std(forward_tilt) 
        avg_label = 'Stdevs x-shift (Angstrom): {0:.3}\n'.format(float(xshift_error)) + \
                    'In-plane rotation (degree): {0:.3}\n'.format(float(inplane_error)) + \
                    'Out-of-plane tilt (degree): {0:.3}'.format(float(outofplane_error)) 

        subplot.hist(forward_differences, bin_count, label=avg_label, facecolor='g', rwidth=0.2, rasterized=True)
        subplot.legend(loc=0, ncol=1, prop=FontProperties(size=4))
        subplot.set_xlim(-1.1 * max_shift_range, 1.1 * max_shift_range)
        subplot.set_xlabel('Forward difference X-shift error \nnormal to helix (Angstrom)', fontsize=6)
        
        errors = (xshift_error, inplane_error, outofplane_error)

        return subplot, errors
            
        
    def get_polarity_ratios_per_helix(self, subplot, ref_session, last_cycle):
        helices = ref_session.query(RefinementCycleHelixTable).\
        filter(RefinementCycleHelixTable.cycle_id == last_cycle.id).all()
        
        segment_polarities = [(each_helix.id, each_helix.segment_count_0_degree, each_helix.segment_count_180_degree) \
                               for each_helix in helices \
                              if not each_helix.segment_count_0_degree == 0 and not each_helix.segment_count_180_degree == 0]
        
        if segment_polarities != []:
            helix_ids, segment_count_0, segment_count_180 = zip(*segment_polarities) 
            segment_count_0 = np.float64(segment_count_0)
            segment_count_180 = np.float64(segment_count_180)
            
            ratio_segment_polarity_per_helix = 100 * segment_count_0 / (segment_count_0 + segment_count_180)
            
            x_ticks = self.make_five_xticks_from_all_helix_ids(helix_ids)
            subplot.bar(helix_ids, ratio_segment_polarity_per_helix, align='center')
            subplot.set_xticks(helix_ids)
            subplot.set_xticklabels(x_ticks)
            subplot.set_xlim(0, max(helix_ids) + 0.5)
            subplot.set_ylim(0, 100)
            subplot.set_xlabel('% of predominant polarity per helix', fontsize=6)
        
        return subplot
    
        
    def get_plot_parameters_from_last_cycle(self, ref_session, last_cycle, model_id):
        ref_segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
        filter(RefinementCycleSegmentTable.model_id == model_id).\
        filter(RefinementCycleSegmentTable.selected == True).all()
        
        x_shifts = np.array([each_ref_segment.helix_shift_x_A for each_ref_segment in ref_segments])
        y_shifts = np.array([each_ref_segment.helix_shift_y_A for each_ref_segment in ref_segments])
        out_of_plane_angles = np.array([each_ref_segment.theta for each_ref_segment in ref_segments]) - 90.0
        stack_ids = [each_ref_segment.stack_id for each_ref_segment in ref_segments]
        ref_ids = [each_ref_segment.id for each_ref_segment in ref_segments]
#        mean_peak = np.mean([each_ref_segment.peak for each_ref_segment in ref_segments])
        
        return x_shifts, y_shifts, out_of_plane_angles, stack_ids
    

    def get_x_and_y_shifts_perpendicular_to_helix_from_penultimate_cycle(self, stack_ids, ref_cycle_id):
        prev_ref_cycle_id = ref_cycle_id - 1
        if os.path.exists('refinement{0:03}.db'.format(prev_ref_cycle_id)):
            prev_session, temp_ref_db, last_cycle = self.get_ref_session_and_last_cycle(prev_ref_cycle_id)
            ref_segments = prev_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).all()
            
            prev_session.close()
            os.remove(temp_ref_db)

            x_shifts = np.array([each_ref_segment.helix_shift_x_A for each_ref_segment in ref_segments 
            if each_ref_segment.stack_id in stack_ids])
            
            y_shifts = np.array([each_ref_segment.helix_shift_y_A for each_ref_segment in ref_segments 
            if each_ref_segment.stack_id in stack_ids])
            
        else:
            x_shifts = np.zeros(len(stack_ids))
            y_shifts = np.zeros(len(stack_ids))
            
        return x_shifts, y_shifts
        
        
    def compute_bin_count_from_quantity_and_step(self, quantity, quantity_step):
        bin_count = int(round((max(quantity) - min(quantity)) / quantity_step))
        bin_count = max(10, bin_count)
            
        return bin_count
    

    def evaluate_shifts_perpendicular_to_helix_axis(self, subplot, x_shifts, xshift_step, max_range,
    global_eval_label=False):
        
        bin_count = self.compute_bin_count_from_quantity_and_step(x_shifts, xshift_step)
        
        avg_stdev = SegmentPlot().add_avg_and_stdev_for_label(x_shifts)
        subplot.hist(x_shifts, bin_count, label=avg_stdev, facecolor='b', rwidth=0.2, rasterized=True)
        subplot.legend(loc=0, ncol=1, prop=FontProperties(size=4))
        if global_eval_label:
            subplot.set_ylabel('Number of segments', fontsize=6)
            subplot.set_xlabel('Cumulative X-shifts normal to helix', fontsize=6)
        else:
            subplot.set_xlabel('Refined X-shifts (Angstrom)', fontsize=6)
        subplot.set_xlim(-1.1 * max_range, 1.1 * max_range)
        
        return subplot
    
    
    def plot_x_and_yshifts_in_scattered(self, plot, subplot, x_shifts, y_shifts, max_range=False):
        
        if not max_range:
            max_range = np.max(np.append(np.abs(x_shifts), np.abs(y_shifts)))
        subplot.set_xlim(-1.1 * max_range, 1.1 * max_range)
        subplot.set_ylim(-1.1 * max_range, 1.1 * max_range)
        
        if len(x_shifts) < 500:
            subplot.scatter(x_shifts, y_shifts, s=0.2, rasterized=True)
        else:
            hex = subplot.hexbin(x_shifts, y_shifts, cmap=cm.YlOrRd)
            cax = plot.fig.add_axes([0.03, 0.75, 0.01, 0.1])
            cbar = plot.fig.colorbar(hex, cax)
            cbar.set_label('Number of segments', fontsize=6)
            for t in cbar.ax.get_yticklabels():
                t.set_fontsize(5)

        return subplot, max_range
    
    
    def plot_fsc_lines(self, subplot, fsc_lines, pixelsize):
        
        for each_id, each_field in enumerate(fsc_lines._fields):
            fsc_line = fsc_lines.__getattribute__(each_field)
            label_txt = each_field
            if each_id == 0:
                resolution = SegmentExam().make_oneoverres(fsc_line, pixelsize)
                label_txt = 'FSC(0.143/0.5) in Angstrom\n' + each_field
            
            if fsc_line[0] is not None:
                fsc_0143 = self.get_resolution_closest_to_value(0.143, fsc_line, resolution)
                fsc_05 = self.get_resolution_closest_to_value(0.5, fsc_line, resolution)
                plot_label = label_txt + ': {0:.3}/{1:.3}'.format(fsc_0143, fsc_05)
                subplot.plot(resolution, fsc_line, label=plot_label, linewidth=0.2)
        
        subplot.legend(loc=0, ncol=1, prop=FontProperties(size=3))
        subplot.set_xlim(0, resolution[-1])
        subplot.set_ylim(0, 1)
        subplot.set_ylabel('Fourier shell correlation', fontsize=6)
        subplot.set_xlabel('Resolution (1/Angstrom)', fontsize=6)
        
        resolution_cutoff = (fsc_05, fsc_0143)
        
        return subplot, resolution_cutoff
    
        
    def generate_histogram_of_angular_distribution(self, subplot, angles, out_of_plane_count, labeltxt=None):
        subplot.hist(angles, max(10, 2 * out_of_plane_count), facecolor='r', rwidth=0.2, rasterized=True, label=labeltxt)
        lower_x = min(angles)
        upper_x = max(angles)
        if abs(lower_x - upper_x) < 1:
            lower_x -= 4
            upper_x += 4
        subplot.set_xlim(lower_x, upper_x) 

        return subplot
        
        
    def evaluate_out_of_plane_tilt_angles(self, subplot, out_of_plane_angles, out_of_plane_count, resolution_aim):
        
        if resolution_aim in ['high', 'max']:
            out_of_plane_count  *= 5 
       
        subplot = self.generate_histogram_of_angular_distribution(subplot, out_of_plane_angles, out_of_plane_count)
        subplot.set_title('Out of plane angles (degrees)', fontsize=6)
        
        return subplot
    
    
    def evaluate_azimuthal_angles(self, subplot, azimuthal_angles, azimuthal_count):
        diff_angles = np.diff(np.sort(azimuthal_angles))
        avg_angle_sampling = np.mean(diff_angles)
        dev_angle_sampling = np.std(diff_angles)
        label_txt = 'Sampling: avg/stdev({0:.3}, {1:.3})'.format(avg_angle_sampling, dev_angle_sampling)
        
        subplot = self.generate_histogram_of_angular_distribution(subplot, azimuthal_angles, azimuthal_count, label_txt)
        subplot.legend(loc=0, prop=font_manager.FontProperties(size=4))
        right_hand = subplot.twinx()
        right_hand.set_ylabel('Number of segments', fontsize=6)
        right_hand.set_yticks([])
        
        return subplot, avg_angle_sampling, dev_angle_sampling
    
    
    def get_segment_helix_count_and_length_from_spring_db(self):
        temp_db = self.copy_spring_db_to_tempdir()
        session = SpringDataBase().setup_sqlite_db(base, temp_db)

        total_segment_count = session.query(SegmentTable).count()
        helices = session.query(HelixTable).all()
        mic_count = len(set([each_helix.mic_id for each_helix in helices]))
        helix_count = session.query(HelixTable).count()
        session.close()
        os.remove(temp_db)

        hel_mic_count = (helix_count, mic_count)
        total_length = np.sum([each_helix.length for each_helix in helices])
        
        length = (total_length + 2 * helix_count * self.alignment_size_in_A, total_length) 
        
        return total_segment_count, hel_mic_count, length
    

    def plot_excluded_criteria_as_bar_plot(self, subplot, last_cycle):
        bars = [
                last_cycle.excluded_mic_count, 
                last_cycle.excluded_class_count, 
                last_cycle.excluded_helix_count,
                last_cycle.excluded_defocus_count, 
                last_cycle.excluded_astigmatism_count, 
                last_cycle.excluded_curvature_count]
        
        ref_bars = [ 
                    last_cycle.excluded_inplane_count, 
                    last_cycle.excluded_out_of_plane_tilt_count,
                    last_cycle.excluded_helix_shift_x_count, 
                    last_cycle.excluded_prj_cc_count, 
                    last_cycle.excluded_layer_cc_count,
                    last_cycle.total_excluded_count]
        
        total_segment_count, hel_mic_count, length = self.get_segment_helix_count_and_length_from_spring_db()
        
        labels = ['Micrograph {0:.3}%'.format(100*float(last_cycle.excluded_mic_count) / total_segment_count), 
        'Classes {0:.3}%'.format(100*float(last_cycle.excluded_class_count) / total_segment_count),
        'Helices {0:.3}%'.format(100*float(last_cycle.excluded_helix_count) / total_segment_count), 
        'Defocus {0:.3}%'.format(100*float(last_cycle.excluded_defocus_count) / total_segment_count),  
        'Astigmatism {0:.3}%'.format(100*float(last_cycle.excluded_astigmatism_count) / total_segment_count),   
        'Straightness {0:.3}%'.format(100*float(last_cycle.excluded_curvature_count) / total_segment_count)]
            
        ref_labels = [
        'Delta in-plane {0:.3}%'.format(100*float(last_cycle.excluded_inplane_count) / last_cycle.segment_count),
        'Out-of-plane tilt {0:.3}%'.format(100*float(last_cycle.excluded_out_of_plane_tilt_count) / last_cycle.segment_count), 
        'Forward x-shift {0:.3}%'.format(100*float(last_cycle.excluded_helix_shift_x_count) / last_cycle.segment_count),
        'CCC projection {0:.3}%'.format(100*float(last_cycle.excluded_prj_cc_count) / last_cycle.segment_count), 
        'CCC layer line {0:.3}%'.format(100*float(last_cycle.excluded_layer_cc_count) / last_cycle.segment_count),
        'Total excluded {0:.3}%'.format(100*float(last_cycle.total_excluded_count) / last_cycle.segment_count)]
        
        if self.enforce_even_phi:
            bars += [last_cycle.excluded_phi_count]
            labels += ['Uneven phi {0:.3}%'.format(100*float(last_cycle.excluded_phi_count) / last_cycle.segment_count)]
        
        right_hand = subplot.twinx()
        right_hand.set_yticks([])
        
        y_label = '{0} excluded refined segments from total: {1}'.\
        format(int(last_cycle.total_excluded_count), int(last_cycle.segment_count))
        
        right_hand.set_ylabel(y_label, fontsize=4)
        
        x_ref = range(len(bars), len(bars) + len(ref_bars))
        subplot.bar(x_ref, ref_bars, color='green')

        x = range(len(bars))
        subplot.bar(x, bars, color='blue')
        subplot.set_xlim(0, len(bars) + len(ref_bars))
            
        y_label = 'Excluded segments from total: {0}'.format(int(total_segment_count))
        subplot.set_ylabel(y_label, fontsize=4)
        
        subplot.set_xticks(x + x_ref)
        subplot.set_xticklabels(labels + ref_labels, fontsize=4, rotation=30)
            
        return subplot, total_segment_count, hel_mic_count, length
       
    
    def generate_diagnostics_statistics_file_name(self, iteration_number, pixelsize, diagnostic_plot_prefix):
        diagnostic_plot_file = self.generate_file_name_with_apix(iteration_number,
        '{pre}_stat{ext}'.format(pre=os.path.splitext(diagnostic_plot_prefix)[0],
        ext=os.path.splitext(diagnostic_plot_prefix)[-1]), pixelsize)
        
        return diagnostic_plot_file
    

    def enter_cycle_criteria_in_database(self, ref_session, last_cycle, errors, unit_count, avg_sampling,
    dev_sampling):
        xshift_error, inplane_error, outofplane_error = errors

        last_cycle.asym_unit_count = unit_count
        last_cycle.avg_azimuth_sampling = avg_sampling
        last_cycle.dev_azimuth_sampling = dev_sampling
        last_cycle.xshift_error = xshift_error
        last_cycle.inplane_error = inplane_error
        last_cycle.outofplane_error = outofplane_error
        ref_session.merge(last_cycle)
        ref_session.commit()
        

    def log_processing_statistics(self, resolution, unit_count, helical_symmetry, length, hel_mic_count, segment_count,
    alignment_size_A, stepsize_A, pixelsize):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.log_processing_statistics((10, 5), 10000, (1.408, 22.03), (10000, 20000), (10,2), (888, 1000), 300, 50, 1.2)
        u'-----------------------------------------------------------  ---------  --------\\nResolution at FSC (0.5/0.143) (Angstrom)                        10          5\\nNumber of asymmetric units (before/after symmetrization)       888      10000\\nHelical rise/rotation (Angstrom/degrees)                         1.408     22.03\\nTotal length of helices including/excluding ends (Angstrom)  10000      20000\\nNumber of included/total segments                              888       1000\\nNumber of micrographs/helices                                    2         10\\nAlignment size/segment step size (Angstrom)                    300         50\\nPixel size on the specimen (Angstrom)                            1.2\\n-----------------------------------------------------------  ---------  --------'
        """
        res_05, res_0143 = resolution
        rise, rotation = helical_symmetry
        length_ends, lengths = length
        included_segment_count, total_segment_count = segment_count
        helix_count, mic_count = hel_mic_count
        
        table_data = [
                      ['Resolution at FSC (0.5/0.143) (Angstrom)', res_05, res_0143],
                      ['Number of asymmetric units (before/after symmetrization)', included_segment_count, unit_count],
                      ['Helical rise/rotation (Angstrom/degrees)', rise, rotation],
                      ['Total length of helices including/excluding ends (Angstrom)', length_ends, lengths], 
                      ['Number of included/total segments', included_segment_count, total_segment_count],
                      ['Number of micrographs/helices', mic_count, helix_count],
                      ['Alignment size/segment step size (Angstrom)', alignment_size_A, stepsize_A],
                      ['Pixel size on the specimen (Angstrom)', pixelsize, None]
                      ]
        
        msg = tabulate(table_data)
        self.log.ilog('Image processing statistics summary:\n{0}'.format(msg))
        
        return msg
        
        
    def evaluate_alignment_parameters_and_summarize_in_plot(self, alignment_parameters, symmetry_alignment_parameters,
    fsc_lines, ref_cycle_id, each_reference, pixelinfo, diagnostic_plot_prefix, resolution_aim):
        self.log.fcttolog()
        segmentrefine3dplot = self.setup_statistics_plot_layout()
        
        ref_session, temp_ref_db, last_cycle = self.get_ref_session_and_last_cycle(ref_cycle_id)
        
        helix_shifts_x, helix_shifts_y, out_of_plane_angles, stack_ids = \
        self.get_plot_parameters_from_last_cycle(ref_session, last_cycle, each_reference.model_id)
        
        self.ax1.set_ylabel('Y-shifts along helix axis (Angstrom)', fontsize=6)
        self.ax1.set_title('Cumulative X-shifts normal to helix', fontsize=6)
        
        self.ax1, max_shift_range = self.plot_x_and_yshifts_in_scattered(segmentrefine3dplot, self.ax1, helix_shifts_x,
        helix_shifts_y)
        
        self.ax2 = self.evaluate_shifts_perpendicular_to_helix_axis(self.ax2, helix_shifts_x, pixelinfo.pixelsize,
        max_shift_range, global_eval_label=True)
        
        self.ax9, resolution = self.plot_fsc_lines(self.ax9, fsc_lines, pixelinfo.pixelsize)
        
        prev_helix_shifts_x, prev_helix_shifts_y = \
        self.get_x_and_y_shifts_perpendicular_to_helix_from_penultimate_cycle(stack_ids, ref_cycle_id)
        
        ref_helix_shifts_x = helix_shifts_x - prev_helix_shifts_x 
        ref_helix_shifts_y = helix_shifts_y - prev_helix_shifts_y 
        
        self.ax10.set_title('Refined X-shifts (Angstrom)', fontsize=6)

        self.ax10, max_shift_range = self.plot_x_and_yshifts_in_scattered(segmentrefine3dplot, self.ax10,
        ref_helix_shifts_x, ref_helix_shifts_y, max_shift_range)
        
        self.ax11 = self.evaluate_shifts_perpendicular_to_helix_axis(self.ax11, ref_helix_shifts_x, pixelinfo.pixelsize,
        max_shift_range)
        
        self.ax3 = self.evaluate_out_of_plane_tilt_angles(self.ax3, out_of_plane_angles,
        self.out_of_plane_tilt_angle_count, resolution_aim)

        self.ax4 = self.evaluate_in_plane_rotation_angles(self.ax4, ref_session, last_cycle, each_reference.model_id)
        
        self.ax12, errors = self.plot_forward_difference_x_shift(self.ax12, ref_session, last_cycle,
        each_reference.model_id, max_shift_range)
        
        phi_angles = np.array(alignment_parameters)[:,2]
        symmetry_phi_angles = np.array(symmetry_alignment_parameters)[:,1]
        
        self.ax5.set_title('Angular coverage before\n and after symmetrization', fontsize=6)
        self.evaluate_azimuthal_angles(self.ax5, phi_angles.ravel(), self.azimuthal_angle_count)
        
        unit_count = len(symmetry_phi_angles.ravel())
        included_segment_count = len(phi_angles.ravel())
        if self.frame_motion_corr:
            unit_count /= self.frame_count
            included_segment_count /= self.frame_count
        
        ax6_title = 'Asymmetric units before: {0} after: {1}'.format(included_segment_count, unit_count)
        if self.frame_motion_corr:
            ax6_title += ' (excl. frames)'
        self.ax6.set_title(ax6_title, fontsize=6)
        
        self.ax6, avg_sampling, dev_sampling = self.evaluate_azimuthal_angles(self.ax6, symmetry_phi_angles.ravel(),
        self.azimuthal_angle_count)
        
        self.enter_cycle_criteria_in_database(ref_session, last_cycle, errors, unit_count, avg_sampling,
        dev_sampling)
        
        self.ax6.set_xlabel('Azimuthal angles (degrees)', fontsize=6)
        
#        self.ax7 = self.plot_euler_angles_on_sphere(self.ax7, phi_angles, theta_angles, psi_angles)
        self.ax7 = self.get_polarity_ratios_per_helix(self.ax7, ref_session, last_cycle)
        
        ref_session.close()
        shutil.copy(temp_ref_db, 'refinement{0:03}.db'.format(ref_cycle_id))
        os.remove(temp_ref_db)

        self.ax8, total_segment_count, hel_mic_count, length = self.plot_excluded_criteria_as_bar_plot(self.ax8,
        last_cycle)
        
        diagnostic_plot_file = self.generate_diagnostics_statistics_file_name(ref_cycle_id, pixelinfo.pixelsize,
        diagnostic_plot_prefix)
        
        segmentrefine3dplot.fig.suptitle('{file}: statistics iteration{iter:03}'.format(file=diagnostic_plot_file,
        iter=ref_cycle_id))
        
        segmentrefine3dplot.plt.draw()
        segmentrefine3dplot.fig.savefig(diagnostic_plot_file, dpi=600)
        segmentrefine3dplot.plt.close()
        segmentrefine3dplot.plt.ion()
    
        if self.frame_motion_corr:
            total_segment_count /= self.frame_count
            hel_mic_count = [each_count / self.frame_count for each_count in hel_mic_count]
            length = [each_count / self.frame_count for each_count in length] 
        segment_count = (included_segment_count, total_segment_count)

        self.log_processing_statistics(resolution, unit_count, each_reference.helical_symmetry, length, hel_mic_count,
        segment_count, self.alignment_size_in_A, self.stepsize, pixelinfo.pixelsize)
        
    
class SegmentRefine3dSummary(SegmentRefine3dDiagnostics):
    def setup_summary_figure(self):
        segmentrefine3d_sumfig = DiagnosticPlot()
            
        column_count = 3
        row_count = 2
        self.ax20 = segmentrefine3d_sumfig.plt.subplot2grid((row_count, column_count), (0, 0), rowspan=1, colspan=1)
        self.ax21 = segmentrefine3d_sumfig.plt.subplot2grid((row_count, column_count), (0, 1), rowspan=1, colspan=1)
        self.ax22 = segmentrefine3d_sumfig.plt.subplot2grid((row_count, column_count), (0, 2), rowspan=1, colspan=1)
        self.ax23 = segmentrefine3d_sumfig.plt.subplot2grid((row_count, column_count), (1, 0), rowspan=1, colspan=3)
    
        subplot_collection = [self.ax22, self.ax23]
        subplot_collection = segmentrefine3d_sumfig.set_fontsize_to_all_ticklabels_of_subplots(subplot_collection)
        
        return segmentrefine3d_sumfig
    
    
    def determine_mean_angle(self, out_of_plane_angles):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> angles = np.array([33, 33, 44.5, 44.5, 44.5, 45, 66])
        >>> s.determine_mean_angle(angles)
        44.5
        >>> angles = np.array([33, 33, 33, 33, 33, 33, 44.5, 44.5, 44.5, 45, 66, 66, 66, 66, 66])
        >>> s.determine_mean_angle(angles)
        45.0
        """
        unique_angles = np.unique(out_of_plane_angles)
        
        mean_oop_angle = unique_angles[np.argmin(np.abs(unique_angles - np.mean(out_of_plane_angles)))]
                                                        
        return mean_oop_angle


    def get_mean_out_of_plane_angle(self, ref_session, last_cycle, model_id):
        ref_segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
        filter(RefinementCycleSegmentTable.model_id == model_id).\
        filter(RefinementCycleSegmentTable.selected == True).all()
        
        out_of_plane_angles = np.array([each_ref_segment.out_of_plane_angle for each_ref_segment in ref_segments])
        mean_oop_angle = self.determine_mean_angle(out_of_plane_angles)
            
        return mean_oop_angle
    

    def generate_experimental_sum_of_powerspectra(self, ref_session, last_cycle, large_binned_stack,
    mean_out_of_plane, pixelinfo, model_id):
        
        out_of_plane_bin = int((self.out_of_plane_tilt_angle_range[-1] - self.out_of_plane_in_or_ex_range[0])) \
        / float(max(1, self.out_of_plane_tilt_angle_count - 1))

        upper_oop_angle = mean_out_of_plane + out_of_plane_bin
        lower_oop_angle = mean_out_of_plane - out_of_plane_bin
        if not hasattr(self, 'comm'):
            ref_segments = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
            filter(RefinementCycleSegmentTable.model_id == model_id).\
            filter(and_(RefinementCycleSegmentTable.out_of_plane_angle >= lower_oop_angle),
                        (RefinementCycleSegmentTable.out_of_plane_angle <= upper_oop_angle)).\
            filter(RefinementCycleSegmentTable.selected == True).all()
        elif hasattr(self, 'comm'):
            ref_segments = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
            filter(RefinementCycleSegmentTable.rank_id == self.rank).\
            filter(RefinementCycleSegmentTable.model_id == model_id).\
            filter(and_(RefinementCycleSegmentTable.out_of_plane_angle >= lower_oop_angle),
                        (RefinementCycleSegmentTable.out_of_plane_angle <= upper_oop_angle)).\
            filter(RefinementCycleSegmentTable.selected == True).all()
        
        segment = EMData()
        segment.read_image(large_binned_stack)
        segment_size = segment.get_xsize() 
        
        segment_stack = os.path.join(self.tempdir, 'rot_stack.hdf')
        stack_ids = [each_ref_segment.stack_id for each_ref_segment in ref_segments]
        
        helixmask = SegmentExam().make_smooth_rectangular_mask(pixelinfo.helixwidthpix, segment_size * 0.8 ,
        segment_size)
        
        for each_ref_id, each_ref_segment in enumerate(ref_segments):
            segment.read_image(large_binned_stack, each_ref_segment.local_id)
            if not self.unbending:
                inplane_angle = each_ref_segment.inplane_angle
                shift_x = each_ref_segment.helix_shift_x_A / pixelinfo.pixelsize
            else:
                inplane_angle = each_ref_segment.unbent_ip_angle
                
                shift_x, shift_y = \
                SegClassReconstruct().compute_distances_to_helical_axis(each_ref_segment.unbent_shift_x_A /
                pixelinfo.pixelsize, each_ref_segment.unbent_shift_y_A / pixelinfo.pixelsize, inplane_angle)
                
            rot_segment = Segment().shift_and_rotate_image(segment, inplane_angle, 0, 0)
            rot_segment = Util.window(rot_segment, segment_size, segment_size, 1, 0, 0, 0)
            shifted_helixmask = Segment().shift_and_rotate_image(helixmask, 0, shift_x, 0)
            rot_segment *= shifted_helixmask
            rot_segment.write_image(segment_stack, each_ref_id)
        
        paddingsize = 3
        if os.path.isfile(segment_stack):
            avg_periodogram = SegmentExam().add_power_spectra_from_verticalized_stack(segment_stack, stack_ids, 
            helixwidth=None, padsize=paddingsize)
            
            os.remove(segment_stack)
        else:
            avg_periodogram = model_blank(paddingsize * segment_size, paddingsize * segment_size, 1, 0)
        
        return avg_periodogram, segment_size
            
    
    def generate_simulated_power_from_latest_reconstruction(self, resolution_aim, reconstruction, segment_size,
    mean_out_of_plane, each_reference, pixelinfo):
        rec = EMData()
        rec.read_image(reconstruction)
        
        projection_size, rec_volume, variance = \
        self.prepare_volume_for_projection_by_masking_and_thresholding(resolution_aim, rec, pixelinfo,
        each_reference.helical_symmetry, each_reference.point_symmetry)
        
        projection_parameters = self.generate_Euler_angles_for_projection(self.azimuthal_angle_count,
        [mean_out_of_plane, mean_out_of_plane], 1, each_reference.helical_symmetry[1])
        
        ten_evenly = int(len(projection_parameters) / 10 + 0.5)
        projection_parameters = projection_parameters[::ten_evenly]
        diagnostic_stack = os.path.join(self.tempdir, 'simulated_proj.hdf')
        prj_ids = list(range(len(projection_parameters)))
        
        diagnostic_stack = SegClassReconstruct().project_through_reference_using_parameters_and_log(projection_parameters, 
        segment_size, prj_ids, diagnostic_stack, rec_volume)
        
        sim_power = SegmentExam().add_power_spectra_from_verticalized_stack(diagnostic_stack, prj_ids,
        pixelinfo.helixwidthpix, padsize=3)
            
        sim_power_enhanced = SegmentExam().enhance_power(sim_power, pixelinfo.pixelsize)
        
        return sim_power, sim_power_enhanced, diagnostic_stack, projection_parameters, variance
        
        
    def make_experimental_and_simulated_power_spectra_figure(self, sim_power, exp_power, sim_power_enhanced,
    exp_power_enhanced, mean_out_of_plane, each_reference, pixelinfo):
        montage_power = SegClassReconstruct().montage_exp_vs_sim_power_spectrum(exp_power, sim_power)
        
        montage_power_enhanced = SegClassReconstruct().montage_exp_vs_sim_power_spectrum(exp_power_enhanced,
        sim_power_enhanced)
    
        amp_cc = SegClassReconstruct().compute_amplitude_correlation_between_sim_and_exp_power_spectrum(sim_power,
        exp_power)
        
        power = np.copy(EMNumPy.em2numpy(montage_power))
        self.ax20.set_title('Experimental vs simulated', fontsize=8)
        self.ax20.imshow(power, cmap=cm.hot_r, interpolation='nearest')
        
        power_enh = np.copy(EMNumPy.em2numpy(montage_power_enhanced))
        self.ax21.set_title('Enhanced power spectra', fontsize=8)
        self.ax21.imshow(power_enh, cmap=cm.hot_r, interpolation='nearest')
        
        self.ax20.set_yticks([])
        self.ax20.set_xticks([])
        
        self.ax21.set_yticks([])
        self.ax21.set_xticks([])
    
        rise, rotation = each_reference.helical_symmetry
        self.ax22.set_title('Amplitude correlation of \nsimulated vs experimental power spectra\nat out-of-plane ' + \
        'angle of {0:.5}'.format(round(mean_out_of_plane, 3)), fontsize=7)

        quarter, half, three_quarter, full = \
        SegClassReconstruct().get_quarter_half_3quarter_nyquist_average_from_amp_correlation(amp_cc)
        
        resolution = SegmentExam().make_oneoverres(amp_cc, pixelinfo.pixelsize)
        
        if rotation == 0 or rise == 0:
            pitch_txt = ''
        else:
            pitch, unit_number = SegClassReconstruct().convert_rise_rotation_pair_to_pitch_unit_pair((rise, rotation))
            pitch_txt = 'Pitch/unit number = ({0:.4}, {1:.4})'.format(round(pitch, 4), round(unit_number, 4))
        
        label_txt = 'Amplitude correlation\n(avg = {0:.7}/{1:.7}/{2:.7}/{3:.7}\n'.\
                       format(round(quarter, 5), round(half, 5), round(three_quarter, 5), round(full, 5)) + \
                       'at 0.25/0.5/0.75/1 of Nyquist freq cutoff.)\n' + \
                       'Helical rise/rotation = ({0:.4}, {1:.4})\n'.format(round(rise, 4), round(rotation, 4)) + \
                       pitch_txt
        
        self.ax22.plot(resolution, amp_cc, label=label_txt)
        self.ax22.legend(loc=0, prop=FontProperties(size=4))
        self.ax22.set_ylim(0, 1)
        self.ax22.set_xlim(0, max(resolution))
        self.ax22.set_xlabel('Resolution (1/Angstrom)', fontsize=6)
        
        return amp_cc
    
    
    def get_segment_closest_to_given_phi(self, ref_session, last_cycle, each_theta, each_phi, model_id):
        max_cc_segments = ref_session.query(RefinementCycleSegmentTable).\
        filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
        filter(RefinementCycleSegmentTable.theta == each_theta).\
        filter(RefinementCycleSegmentTable.model_id == model_id).\
        filter(RefinementCycleSegmentTable.selected == True).\
        order_by(desc(RefinementCycleSegmentTable.peak)).all()
        
        phis = [each_segment.phi for each_segment in max_cc_segments ]
        if len(phis) > 0:
            phis = np.array(phis)
            closest_phi = phis[np.argmin(np.abs(phis - each_phi))]
            azimuthal_inc = 360 / float(self.azimuthal_angle_count)
            lower_phi = closest_phi - azimuthal_inc / 2.0
            upper_phi = closest_phi + azimuthal_inc / 2.0
            
            out_of_plane_range = abs(self.out_of_plane_tilt_angle_range[-1] - self.out_of_plane_tilt_angle_range[0])
            out_of_plane_inc = out_of_plane_range / float(self.out_of_plane_tilt_angle_count - 1)
            lower_theta = each_theta - out_of_plane_inc / 2.0
            upper_theta = each_theta + out_of_plane_inc / 2.0

            max_cc_segments = ref_session.query(RefinementCycleSegmentTable).\
            filter(RefinementCycleSegmentTable.cycle_id == last_cycle.id).\
            filter(RefinementCycleSegmentTable.model_id == model_id).\
            filter(RefinementCycleSegmentTable.selected == True).\
            filter(and_(RefinementCycleSegmentTable.theta > lower_theta,
                        RefinementCycleSegmentTable.theta < upper_theta)).\
            filter(and_(RefinementCycleSegmentTable.phi > lower_phi,
                        RefinementCycleSegmentTable.phi < upper_phi)).\
            order_by(desc(RefinementCycleSegmentTable.peak)).all()
        else:
            max_cc_segments = None
        
        return max_cc_segments
    

    def get_inplane_rotation_and_x_and_y_shifts_from_segment_entry(self, max_cc_segment, pixelsize):
        if not self.unbending:
            inplane_angle = max_cc_segment.inplane_angle
            shift_x = max_cc_segment.shift_x_A / pixelsize
            shift_y = max_cc_segment.shift_y_A / pixelsize
        else:
            inplane_angle = max_cc_segment.unbent_ip_angle
            shift_x = max_cc_segment.unbent_shift_x_A / pixelsize
            shift_y = max_cc_segment.unbent_shift_y_A / pixelsize
            
        return inplane_angle, shift_x, shift_y
    

    def prepare_projection_images_and_cc_maps_on_diagnostic_stack(self, large_binned_stack, diagnostic_stack,
    projection_parameters, pixelinfo, projection, segment, blank, helixmask, each_prj_id, max_cc_segments):
        projection.read_image(diagnostic_stack, each_prj_id)
        projection.process_inplace('normalize')
        projection = Util.window(projection, pixelinfo.alignment_size, pixelinfo.alignment_size, 1, 0, 0, 0)
        projection.write_image(diagnostic_stack, each_prj_id)
        if max_cc_segments is not None:
            peaks = [each_segment.peak for each_segment in max_cc_segments]
            avg_peak = np.average(peaks)
            stdev_peak = np.std(peaks)
            closest_id = np.argmin(np.abs(peaks - (avg_peak + stdev_peak)))
            
            max_cc_segment = max_cc_segments[closest_id]
            
            inplane_angle, shift_x, shift_y = \
            self.get_inplane_rotation_and_x_and_y_shifts_from_segment_entry(max_cc_segment, pixelinfo.pixelsize)
            
            segment.read_image(large_binned_stack, max_cc_segment.local_id)
            trans_segment = Segment().shift_and_rotate_image(segment, inplane_angle, shift_x, shift_y)
            trans_segment = Util.window(trans_segment, pixelinfo.alignment_size, pixelinfo.alignment_size, 1, 0, 0, 0)
            
            trans_segment *= helixmask
            trans_segment.process_inplace('normalize')
            trans_segment.write_image(diagnostic_stack, 2 * len(projection_parameters) + each_prj_id)
            
            cc_map = ccfnp(trans_segment, projection)
            cc_map.process_inplace('normalize')
            cc_map.write_image(diagnostic_stack, 3 * len(projection_parameters) + each_prj_id)
        else:
            blank.write_image(diagnostic_stack, 2 * len(projection_parameters) + each_prj_id)
            blank.write_image(diagnostic_stack, 3 * len(projection_parameters) + each_prj_id)

        return diagnostic_stack
    
    
    def prepare_average_from_maximum_of_20_images(self, diagnostic_stack, gallery_id, max_cc_segments, pixelinfo,
    large_binned_stack, helix_mask):
        average = model_blank(pixelinfo.alignment_size, pixelinfo.alignment_size, 1, 0)
        segment = EMData()
        if max_cc_segments is not None:
            for each_img_id, each_segment in enumerate(max_cc_segments):
                if each_img_id < 20:
                    inplane_angle, shift_x, shift_y = \
                    self.get_inplane_rotation_and_x_and_y_shifts_from_segment_entry(each_segment, pixelinfo.pixelsize)
                    
                    segment.read_image(large_binned_stack, each_segment.local_id)
                    trans_segment = Segment().shift_and_rotate_image(segment, inplane_angle, shift_x, shift_y)
                    average += Util.window(trans_segment, pixelinfo.alignment_size, pixelinfo.alignment_size, 1, 0, 0, 0)
            
            average *= helix_mask
        average.process_inplace('normalize')
        average.write_image(diagnostic_stack, gallery_id)
        
        return diagnostic_stack
    

    def generate_cc_maps_and_aligned_segments(self, ref_session, last_cycle, large_binned_stack, diagnostic_stack,
    projection_parameters, pixelinfo, model_id, segment_info=None):
        projection = EMData()
        segment = EMData()
        projection.read_image(diagnostic_stack)
        blank = model_blank(pixelinfo.alignment_size, pixelinfo.alignment_size, 1, 0)
        helixmask = SegmentExam().make_smooth_rectangular_mask(pixelinfo.helixwidthpix, pixelinfo.helix_heightpix, 
        pixelinfo.alignment_size)

        for each_prj_id, (each_phi, each_theta, each_psi, each_x, each_y) in enumerate(projection_parameters):
            if not hasattr(self, 'comm'):
                max_cc_segments = self.get_segment_closest_to_given_phi(ref_session, last_cycle, each_theta, each_phi,
                model_id)
            elif hasattr(self, 'comm'):
                max_cc_segments = segment_info[each_prj_id]
            
            diagnostic_stack = self.prepare_projection_images_and_cc_maps_on_diagnostic_stack(large_binned_stack,
            diagnostic_stack, projection_parameters, pixelinfo, projection, segment, blank, helixmask, each_prj_id,
            max_cc_segments)
            
            diagnostic_stack = self.prepare_average_from_maximum_of_20_images(diagnostic_stack, 
            1 * len(projection_parameters) + each_prj_id,  max_cc_segments, pixelinfo, 
            large_binned_stack, helixmask)
            
        return diagnostic_stack
    
    
    def get_azimuthal_angles_from_projection_parameters(self, projection_parameters):
        azimuthal_series = np.array(projection_parameters)[:,0].tolist()
        azimuthal_series = ['{0:.1f}'.format(round(each_angle, 1)) for each_angle in azimuthal_series]
        
        return azimuthal_series


    def perform_fit_of_gaussian(self, x_cc_arr, pixels):#, id=None):
        def gauss(x, *p):
            A, mu, sigma = p
            return A * np.exp(-(x-mu) ** 2/(2. * sigma **2))

        if len(pixels) > 3:
            increment = 2 * (pixels[-1] - pixels[-2])
            initial_guess = [x_cc_arr.max(), pixels[np.argmax(x_cc_arr)], increment]
            pixel_range = pixels.max() - pixels.min()
        
            try:
                coeff, var_matrix = curve_fit(gauss, pixels, x_cc_arr, p0=initial_guess)
                stick_with_guess = False
                if coeff[2] > pixel_range / 2.0:
                    stick_with_guess = True
            except RuntimeError:
                stick_with_guess = True
    
            if stick_with_guess: 
                coeff = [x_cc_arr.max(), pixels[np.argmax(x_cc_arr)], pixel_range / 2.0]
        else:
            coeff = 3 * [None]

#         if id is not None:
#             data_fit = gauss(pixels, *coeff)
#      
#             import matplotlib.pyplot as plt
#             plt.clf()
#             plt.plot(pixels, x_cc_arr, 'x', label='Test data')
#             plt.plot(pixels, data_fit, label='Fitted data')
#             plt.plot(pixels[len(pixels) /2 - 1], x_cc_arr[len(pixels) /2 - 1], 'o')
#             plt.legend()
#             plt.savefig('test{0:02}.pdf'.format(id))

        return coeff[2]


    def average_and_summarize_results_of_error_esimation(self, projection_parameters, x_err_data, y_err_data):
        x_stdevs, x_pixels, x_ccs = zip(*x_err_data)
        y_stdevs, y_pixels, y_ccs = zip(*y_err_data)
        avg_x_err = np.average([each_dev for each_dev in x_stdevs if each_dev is not None])
        avg_y_err = np.average([each_dev for each_dev in y_stdevs if each_dev is not None])
        azimuthal_series = self.get_azimuthal_angles_from_projection_parameters(projection_parameters)

        tbl_msg = tabulate(zip(azimuthal_series, x_stdevs, y_stdevs), ['Azimuthal angle (degree)', 
        'x-shift stdev (Angstrom)', 'y-shift stdev (Angstrom)'])

        self.log.ilog('Peaks of cross correlation maps were fitted with Gaussian functions. As a result the shift ' + \
        'peak widths can be estimated as follows:\n{0}'.format(tbl_msg))

        log_msg = 'Estimated x and y-shift peak widths (stdev): {0:.2f}, {1:.2f} Angstrom'.format(round(avg_x_err, 2),
        round(avg_y_err, 2))
        
        x_pix_cc = [list(x_pixels[0])] + list(x_ccs)
        x_meas_tbl = 2 * '\n' + tabulate(zip(*x_pix_cc), 
        ['X-shift (A)/cc'] + ['{0} (deg)'.format(each_azimuth) for each_azimuth in azimuthal_series])

        y_pix_cc = [list(y_pixels[0])] + list(y_ccs)
        y_meas_tbl = 2 * '\n' + tabulate(zip(*y_pix_cc), 
        ['Y-shift (A)/cc'] + ['{0} (deg)'.format(each_azimuth) for each_azimuth in azimuthal_series])

        self.log.ilog(log_msg + x_meas_tbl + y_meas_tbl)

        return log_msg


    def compute_shift_error_from_cc_map(self, pixelsize, x_cc, helix_half_width):
        x_cc_arr = np.copy(EMNumPy.em2numpy(x_cc))

        x_pixels = pixelsize * (np.arange(len(x_cc_arr)) - len(x_cc_arr) / 2)
        
        x_cc_arr = x_cc_arr[(-helix_half_width <= x_pixels) & (x_pixels <= helix_half_width)]
        x_pixels = x_pixels[(-helix_half_width <= x_pixels) & (x_pixels <= helix_half_width)]
        x_stdev = self.perform_fit_of_gaussian(x_cc_arr, x_pixels)

        return x_stdev, x_pixels, x_cc_arr


    def get_error_estimates_from_cc_maps(self, diagnostic_stack, cc_map_ids, pixelinfo, each_reference):
        rise, rotation = each_reference.helical_symmetry
        
        img = EMData()
        if rotation != 0:
            half_pitch_distance = abs(0.35 * (rise * 360.0 / rotation) / float(each_reference.rotational_symmetry))
        if rise == 0 and rotation == 0:
            if cc_map_ids != []:
                img.read_image(diagnostic_stack, cc_map_ids[0])
                half_pitch_distance = abs(0.25 * pixelinfo.pixelsize * img.get_xsize())
        else:
            half_pitch_distance = abs(0.35 * (rise * 360.0) / float(each_reference.rotational_symmetry))
            
        helix_half_width = 0.25 * pixelinfo.helixwidthpix * pixelinfo.pixelsize
        
        x_err_data = []
        y_err_data = []
        for each_cc_map_id in cc_map_ids:
            img.read_image(diagnostic_stack, each_cc_map_id)
            x_cc = img.get_row(img.get_xsize() / 2)
            x_err_data.append(self.compute_shift_error_from_cc_map(pixelinfo.pixelsize, x_cc, helix_half_width))

            y_cc = img.get_col(img.get_ysize() / 2)
            y_err_data.append(self.compute_shift_error_from_cc_map(pixelinfo.pixelsize, y_cc, half_pitch_distance))

        return x_err_data, y_err_data


    def make_angles_centered_around_phi_and_continuous(self, azimuthal_angles, each_phi):
        """
        >>> from spring.segment3d.refine.sr3d_main import SegmentRefine3d
        >>> s = SegmentRefine3d()
        >>> s.make_angles_centered_around_phi_and_continuous(range(0, 360, 90), 180)
        (array([0, 1, 2, 3]), array([   0.,   90.,  180.,  270.]))
        >>> s.make_angles_centered_around_phi_and_continuous(range(0, 360, 72), 144)
        (array([0, 1, 2, 3, 4]), array([   0.,   72.,  144.,  216.,  288.]))
        >>> s.make_angles_centered_around_phi_and_continuous(range(0, 360, 90), 90)
        (array([3, 0, 1, 2]), array([ -90.,    0.,   90.,  180.]))
        >>> s.make_angles_centered_around_phi_and_continuous(range(0, 360, 72), 72)
        (array([4, 0, 1, 2, 3]), array([ -72.,    0.,   72.,  144.,  216.]))
        >>> s.make_angles_centered_around_phi_and_continuous(range(0, 360, 90), 270)
        (array([1, 2, 3, 0]), array([  90.,  180.,  270.,  360.]))
        >>> s.make_angles_centered_around_phi_and_continuous(range(0, 360, 72), 288)
        (array([2, 3, 4, 0, 1]), array([ 144.,  216.,  288.,  360.,  432.]))
        """
        centered_angles = np.array(azimuthal_angles)
        lower_bound = each_phi - 180.0
        upper_bound = each_phi + 180.0

        angles_id = np.arange(len(centered_angles))
        lower_end_ids = angles_id[centered_angles < lower_bound]
        unchanged_ids = angles_id[(lower_bound <= centered_angles) & (centered_angles < upper_bound)]
        upper_end_ids = angles_id[centered_angles >= upper_bound]
        centered_ids = np.concatenate([upper_end_ids, unchanged_ids, lower_end_ids])

        lower_end = centered_angles[centered_angles < lower_bound] + 360.0
        unchanged = centered_angles[(lower_bound <= centered_angles) & (centered_angles < upper_bound)]
        upper_end = centered_angles[centered_angles >= upper_bound] - 360.0
        centered_angles = np.concatenate([upper_end, unchanged, lower_end])
        centered_ids = centered_ids[np.argsort(centered_angles)]
        centered_angles = centered_angles[np.argsort(centered_angles)]

        return centered_ids, centered_angles


    def determine_angular_error(self, projection_parameters, img_ids, diagnostic_stack, azimuthal_angles,
    azimuth_prj_stack, azimuth_half_range, model_id, azimuth=True):
        img = EMData()
        azimuth_err = []
        phi_angles = []
        for each_img_id, each_param in zip(img_ids, projection_parameters):
            img.read_image(diagnostic_stack, each_img_id)
            if azimuth:
                each_phi = each_param[0]
            else:
                each_phi = each_param[1]
            
            centered_ids, centered_angles = self.make_angles_centered_around_phi_and_continuous(azimuthal_angles,
            each_phi)
 
            lower_filt = each_phi - azimuth_half_range
            upper_filt = each_phi + azimuth_half_range
   
            centered_ids = centered_ids[(lower_filt <= centered_angles) & (centered_angles <= upper_filt)] 
            centered_angles = centered_angles[(lower_filt <= centered_angles) & (centered_angles <= upper_filt)] 

            prj = EMData()
            cc_values = np.array([])
            for each_prj_id in centered_ids:
                prj.read_image(azimuth_prj_stack, model_id * len(azimuthal_angles) + int(each_prj_id))
                cc_values = np.append(cc_values, (ccc(prj, img)))
            
            phi_angles.append(each_phi)
            ang_err = self.perform_fit_of_gaussian(cc_values, centered_angles)
            azimuth_err.append((ang_err, centered_angles, cc_values))
        
        return azimuth_err, phi_angles

        
    def average_and_summarize_results_of_ang_error_estimation(self, projection_parameters, azimuth_err_data,
    tilt_err_data, rot_err_data):
    
        azimuth_err, azimuth_ang, azimuth_cc = zip(*azimuth_err_data)
        tilt_err, tilt_ang, tilt_cc = zip(*tilt_err_data)
        rot_err, rot_ang, rot_cc = zip(*rot_err_data)
        
        azimuthal_series = self.get_azimuthal_angles_from_projection_parameters(projection_parameters)
        tbl_msg_azimuth = tabulate(zip(azimuthal_series, azimuth_err, tilt_err, rot_err), ['Projection azimuthal angle (degree)', 
        'Azimuthal stdev (degree)', 'Out-of-plane stdev', 'In-plane rotation stdev'])

        self.log.ilog('Peaks of angular correlation were fitted with Gaussian functions. As a result the azimuthal, ' + \
        'out-of-plane tilt and in-plane rotation peak widths (stdev) can be estimated as follows:\n{0}'.format(tbl_msg_azimuth))

        avg_azimuth_err = np.average([each_err for each_err in azimuth_err if each_err is not None])
        avg_tilt_err = np.average([each_err for each_err in tilt_err if each_err is not None])
        avg_rot = np.average([each_err for each_err in rot_err if each_err is not None])

        log_msg = 'Estimated azimuthal, out-of-plane tilt and in-plane rotation peak widths (stdev): ' + \
        ' {0:.2f}, {1:.2f}, {2:.2f} degree'.format(round(avg_azimuth_err, 2), np.round(avg_tilt_err, 2), np.round(avg_rot))
        
        azimuth_tbl = '\n'
        for each_ang_arr, each_cc_arr in zip(azimuth_ang, azimuth_cc):
            azimuth_tbl += '{0}\n\n'.format(tabulate(zip(each_ang_arr, each_cc_arr), 
            ['Azimuthal angle (degree)', 'Cross correlation']))

        tilt_tbl = '\n'
        if not np.isnan(avg_tilt_err):
            for each_ang_arr, each_cc_arr in zip(tilt_ang, tilt_cc):
                tilt_tbl += '{0}\n\n'.format(tabulate(zip(each_ang_arr, each_cc_arr), 
                ['Out-of-plane tilt angle (degree)', 'Cross correlation']))

        rot_ang_cc = [list(rot_ang[0])] + list(rot_cc)
        rot_tbl = 2 * '\n' + tabulate(zip(*rot_ang_cc), 
        ['In-plane rotation (angle)/cc'] + ['{0} (deg)'.format(each_azimuth) for each_azimuth in azimuthal_series])

        self.log.ilog(log_msg + azimuth_tbl + tilt_tbl + rot_tbl)
    
        return log_msg


    def get_error_estimates_from_angles(self, prj_info, diagnostic_stack, projection_parameters, img_ids,
    each_reference):
        azimuthal_params = self.get_azimuthal_angles_from_prj_params(prj_info.projection_parameters,
        each_reference.model_id)

        azimuth_prj_stack = self.get_prj_stack_name_with_ending(prj_info.projection_stack, 'az')

        azimuthal_angles = [each_param.phi for each_param in azimuthal_params]
        azimuth_half_range = 4 * 360.0 / self.azimuthal_angle_count #180.0 / float(each_reference.rotational_symmetry)

        azimuth_err, azimuthal_angles = self.determine_angular_error(projection_parameters, img_ids, diagnostic_stack,
        azimuthal_angles, azimuth_prj_stack, azimuth_half_range, each_reference.model_id)

        tilt_params = self.get_out_of_plane_angles_from_prj_params(prj_info.projection_parameters,
        each_reference.model_id)

        tilt_prj_stack = self.get_prj_stack_name_with_ending(prj_info.projection_stack, 'out')
            
        tilt_angles = [each_param.theta for each_param in tilt_params]
        if len(tilt_angles) > 10:
            tilt_half_range = 0.5 * (max(tilt_angles) - min(tilt_angles)) 
    
            tilt_err, out_tilt_angles = self.determine_angular_error(projection_parameters, img_ids, diagnostic_stack,
            tilt_angles, tilt_prj_stack, tilt_half_range, each_reference.model_id, azimuth=False)
        else:
            tilt_holder = len(azimuthal_angles) * [np.nan]
            tilt_err = zip(tilt_holder, tilt_holder, tilt_holder)
            
        return azimuth_err, tilt_err


    def get_error_estimates_for_inplane_rotation(self, diagnostic_stack, img_ids, prj_ids):
        img = EMData()
        prj = EMData()
        ip_rot_err = []
        for each_img_id, each_prj_id in zip(img_ids, prj_ids):
            img.read_image(diagnostic_stack, each_img_id)
            prj.read_image(diagnostic_stack, each_prj_id)
            
            img_arr = np.copy(EMNumPy.em2numpy(img))
            prj_arr = np.copy(EMNumPy.em2numpy(prj))

            circ_img_arr, r_i, r_t = self.reproject_image_into_polar(img_arr)
            circ_prj_arr, r_i, r_t = self.reproject_image_into_polar(prj_arr)
            
            circ_img = EMNumPy.numpy2em(np.copy(circ_img_arr))
            circ_prj = EMNumPy.numpy2em(np.copy(circ_prj_arr))

            cc_map = ccfnp(circ_img, circ_prj)
            rot_cc = cc_map.get_row(cc_map.get_xsize() / 2)
            pixelsize = 360 / float(cc_map.get_ysize())
            ip_rot_err.append(self.compute_shift_error_from_cc_map(pixelsize, rot_cc, 10 * pixelsize))
            
        return ip_rot_err
    

    def generate_nice_gallery_of_ten_images_corresponding_projections(self, ref_session, last_cycle, ref_cycle_id,
    large_binned_stack, diagnostic_stack, projection_parameters, pixelinfo, each_reference, diagnostic_plot_prefix,
    prj_info, segment_info=None):

        gallery_stack = self.generate_cc_maps_and_aligned_segments(ref_session, last_cycle, large_binned_stack,
        diagnostic_stack, projection_parameters, pixelinfo, each_reference.model_id, segment_info)
        
        diagnostic_file = self.generate_diagnostics_reprojection_file_name(ref_cycle_id, pixelinfo.pixelsize,
        diagnostic_plot_prefix, os.extsep + 'hdf')

        gallery_count = EMUtil.get_image_count(gallery_stack)
        img = EMData()
        for each_image in list(range(gallery_count)):
            img.read_image(gallery_stack, each_image)
            img.process_inplace('normalize')
            img.append_image(diagnostic_file)
                
        stacked_params = np.zeros((4, len(projection_parameters)), dtype=object)
        
        montage = self.montage_reprojections_to_image_according_to_given_shape(gallery_stack, stacked_params)
        
        azimuthal_series = self.get_azimuthal_angles_from_projection_parameters(projection_parameters)
                
        self.ax23.imshow(montage, cmap=cm.gray, interpolation='nearest')
        y_labels = ['projections', 'averages (from max. 20)', 'highest cc images', 'cc maps']
        
        self.ax23 = self.distribute_x_and_y_ticks_evenly_along_montage(self.ax23, montage,
        len(projection_parameters), len(y_labels))
        
        self.ax23.set_xticklabels(azimuthal_series)
        self.ax23.set_yticklabels(y_labels)
            
        self.ax23.set_xlabel('Azimuthal angle phi (degrees)', fontsize=6)

        return self.ax23
    
    
    def prepare_gallery_figure(self, ref_session, last_cycle, model_id):
        segmentrefine3d_sumfig = self.setup_summary_figure()
        mean_out_of_plane = self.get_mean_out_of_plane_angle(ref_session, last_cycle, model_id)
        
        return mean_out_of_plane, segmentrefine3d_sumfig


    def prepare_upper_part_of_figure(self, resolution_aim, latest_reconstruction, each_reference, pixelinfo,
    mean_out_of_plane, exp_power, segment_size, ref_cycle_id, diagnostic_plot_prefix):
        exp_power_enhanced = SegmentExam().enhance_power(exp_power, pixelinfo.pixelsize)
        
        sim_power, sim_power_enhanced, diagnostic_stack, projection_parameters, variance = \
        self.generate_simulated_power_from_latest_reconstruction(resolution_aim, latest_reconstruction, segment_size,
        mean_out_of_plane, each_reference, pixelinfo)
        
        amp_cc = self.make_experimental_and_simulated_power_spectra_figure(sim_power, exp_power, sim_power_enhanced,
        exp_power_enhanced, mean_out_of_plane, each_reference, pixelinfo)
        
        diagnostic_file = self.generate_diagnostics_reprojection_file_name(ref_cycle_id, pixelinfo.pixelsize,
        diagnostic_plot_prefix, '_power' + os.extsep + 'hdf')
        for each_image in [exp_power, exp_power_enhanced, sim_power, sim_power_enhanced]:
            each_image.process_inplace('normalize')
            each_image.append_image(diagnostic_file)
            
        return diagnostic_stack, projection_parameters, amp_cc, variance
    

    def generate_diagnostics_reprojection_file_name(self, ref_cycle_id, pixelsize, diagnostic_plot_prefix,
    extension=None):
        if extension is None:
            extension = os.path.splitext(diagnostic_plot_prefix)[-1]
        
        file_name = '{pre}_exp_vs_reproj{ext}'.format(pre=os.path.splitext(diagnostic_plot_prefix)[0], ext=extension)
        reproj_plot = self.generate_file_name_with_apix(ref_cycle_id, file_name, pixelsize)

        return reproj_plot


    def finalize_figure_with_gallery(self, ref_cycle_id, segmentrefine3d_sumfig, ax23, pixelsize, diagnostic_plot_prefix,
    shift_msg, angle_msg):
        reproj_plot = self.generate_diagnostics_reprojection_file_name(ref_cycle_id, pixelsize,
        diagnostic_plot_prefix)
        
        log_msg = shift_msg + '\n' + angle_msg
        ax23.set_title(log_msg, fontsize=6)

        segmentrefine3d_sumfig.fig.suptitle('{file}: gallery'.format(file=reproj_plot))
        segmentrefine3d_sumfig.fig.savefig(reproj_plot, dpi=600)
        
        return segmentrefine3d_sumfig
    

    def summarize_each_bin_round_with_simulated_vs_experimental_images_and_powerspectra(self, resolution_aim,
    large_binned_stack, latest_reconstruction, ref_cycle_id, each_reference, pixelinfo, diagnostic_plot_prefix,
    prj_info):
        ref_session, temp_ref_db, last_cycle = self.get_ref_session_and_last_cycle(ref_cycle_id)
        
        mean_out_of_plane, segmentrefine3d_sumfig = self.prepare_gallery_figure(ref_session, last_cycle,
        each_reference.model_id)
        
        exp_power, segment_size = self.generate_experimental_sum_of_powerspectra(ref_session, last_cycle,
        large_binned_stack, mean_out_of_plane, pixelinfo, each_reference.model_id)
        
        diagnostic_stack, projection_parameters, amp_cc, variance = self.prepare_upper_part_of_figure(resolution_aim,
        latest_reconstruction, each_reference, pixelinfo, mean_out_of_plane, exp_power, segment_size, ref_cycle_id,
        diagnostic_plot_prefix)
        
        self.ax23 = self.generate_nice_gallery_of_ten_images_corresponding_projections(ref_session, last_cycle,
        ref_cycle_id, large_binned_stack, diagnostic_stack, projection_parameters, pixelinfo, each_reference,
        diagnostic_plot_prefix, prj_info)
        
        cc_map_ids = [3 * len(projection_parameters) + each_cc_map_id \
                   for each_cc_map_id, each_cc_map in enumerate(projection_parameters)]

        x_err_data, y_err_data = self.get_error_estimates_from_cc_maps(diagnostic_stack, cc_map_ids, pixelinfo,
        each_reference)

        shift_msg = self.average_and_summarize_results_of_error_esimation(projection_parameters, x_err_data, y_err_data)

        img_ids = [len(projection_parameters) * 2 + each_img_id \
                    for each_img_id, each_param in enumerate(projection_parameters)]
            
        prj_ids = [each_img_id for each_img_id, each_param in enumerate(projection_parameters)]
            
        if prj_info.projection_stack is not None:
            azimuth_err, tilt_err = self.get_error_estimates_from_angles(prj_info, diagnostic_stack,
            projection_parameters, img_ids, each_reference)
        
            rot_err = self.get_error_estimates_for_inplane_rotation(diagnostic_stack, img_ids, prj_ids)

            angle_msg = self.average_and_summarize_results_of_ang_error_estimation(projection_parameters, azimuth_err,
            tilt_err, rot_err)
        else:
            angle_msg = ''

        ref_session.close()
        os.remove(temp_ref_db)

        os.remove(diagnostic_stack)
        
        self.finalize_figure_with_gallery(ref_cycle_id, segmentrefine3d_sumfig, self.ax23, pixelinfo.pixelsize,
        diagnostic_plot_prefix, shift_msg, angle_msg)
        
        return amp_cc, variance
    