# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to interactively inspect 3D reconstructions from segmentrefine3d using slice viewer
"""
from EMAN2 import EMData
from PyQt4.QtGui import QApplication
from fundamentals import mirror
from spring.csinfrastr.csfeatures import Features, FeaturesSupport
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment3d.refine.sr3d_main import SegmentRefine3d
from spring.segment3d.segclassreconstruct import SegClassReconstruct
from spring.segment3d.segrefine3dinspect_gui import SegRefine3dInspectCommonOperations, SegRefine3dInspectGui
import numpy as np
import sys


class SegRefine3dInspectPar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'       
        self.progname = 'segrefine3dinspect'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.segrefine3dinspect_features = Features()
        self.feature_set = self.segrefine3dinspect_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()


    def define_parameters_and_their_properties(self):
        self.feature_set = self.set_reconstruction_to_be_inspected(self.feature_set)
        self.feature_set = self.segrefine3dinspect_features.set_interactive_vs_batch_mode(self.feature_set)
        self.feature_set = self.set_processed_reconstruction(self.feature_set)
        
        self.feature_set = self.set_bfactor_option(self.feature_set)
        self.feature_set = self.set_bfactor_and_resolution_cutoff(self.feature_set)
        self.feature_set = self.set_sn_weighting_option(self.feature_set)
        self.feature_set = self.set_fsc_curve(self.feature_set)

        self.feature_set = self.set_real_space_mask_option(self.feature_set)
        self.feature_set = self.set_mask_type(self.feature_set)
        
        self.feature_set = self.set_layer_line_mask_option(self.feature_set)
        self.feature_set = self.segrefine3dinspect_features.set_helical_symmetry_reconstruction(self.feature_set)
        self.feature_set = self.segrefine3dinspect_features.set_helical_symmetry(self.feature_set)
        self.feature_set = self.segrefine3dinspect_features.set_rotational_symmetry(self.feature_set)
        self.feature_set = self.segrefine3dinspect_features.set_polar_apolar_helix_choice(self.feature_set)
        self.feature_set = self.set_long_helix_option(self.feature_set)
        self.feature_set = self.set_helix_length(self.feature_set)
        self.feature_set = self.set_swap_helix(self.feature_set)
        
        
    def define_program_states(self):
        self.feature_set.program_states['apply_structural_mask_if_demanded']='Generate and apply structural mask'
        self.feature_set.program_states['apply_layerline_filter_if_demanded']='Generate and apply layer-line filter'
        self.feature_set.program_states['apply_bfactor_if_demanded']='Apply B-factor'


    def set_reconstruction_to_be_inspected(self, feature_set):
        inp2 = 'Volume reconstruction'
        feature_set.parameters[inp2]='recvol_1223apix.hdf'
        feature_set.properties[inp2]=feature_set.file_properties(1,['hdf'],'getFile')
        feature_set.hints[inp2]='Untreated 3D reconstruction to be inspected: accepted image file formats ({0}).'.\
        format(', '.join(feature_set.properties[inp2].ext))
        
        feature_set.level[inp2]='beginner'
        
        return feature_set
    
    
    def set_processed_reconstruction(self, feature_set):
        inp9 = 'Output volume name'
        feature_set.parameters[inp9]='recvol.hdf'
        feature_set.properties[inp9]=feature_set.file_properties(1,['hdf'],'saveFile')
        feature_set.hints[inp9]='Output name for processed volume: accepted image file formats ({0}).'.\
        format(', '.join(feature_set.properties[inp9].ext))
        
        feature_set.level[inp9]='intermediate'
        feature_set.relatives[inp9]='Batch mode'
        
        return feature_set
    
        
    def set_interactive_vs_batch_mode(self, feature_set):
        inp3 = 'Interactive vs. batch mode'
        feature_set.parameters[inp3]='interactive'
        feature_set.hints[inp3]='Choose between interactive vs. batch inspection mode of 3D reconstruction.'
        feature_set.properties[inp3]=feature_set.choice_properties(2, ['interactive', 'batch'], 'QComboBox')
        feature_set.level[inp3]='intermediate'
        
        return feature_set
    
    
    def set_bfactor_option(self, feature_set):
        inp12 = 'B-factor'
        feature_set.parameters[inp12] = bool(True)
        feature_set.hints[inp12] = 'Option to apply a B-factor to the structure.'
        feature_set.level[inp12]='intermediate'
        feature_set.relatives[inp12]='Batch mode'

        return feature_set
    
    
    def set_bfactor_and_resolution_cutoff(self, feature_set):
        inp11 = 'B-factor and resolution cutoff'
        feature_set.parameters[inp11] = tuple((-200.0, 5.0))
        feature_set.hints[inp11] = 'B-factor in 1/Angstrom^2 and resolution cutoff in Angstrom.'
        feature_set.properties[inp11] = feature_set.Range(-10000, 10000, 0.1)
        feature_set.relatives[inp11] = (('B-factor', 'B-factor'))
        feature_set.level[inp11]='intermediate'

        return feature_set
    
    
    def set_real_space_mask_option(self, feature_set):
        inp12 = 'Real-space mask'
        feature_set.parameters[inp12] = bool(True)
        feature_set.hints[inp12] = 'Option to apply a real-space mask of choice to the structure.'
        feature_set.level[inp12]='intermediate'
        feature_set.relatives[inp12]='Batch mode'

        return feature_set
    
    
    def set_mask_type(self, feature_set):
        inp12 = 'Mask type'
        feature_set.parameters[inp12] = str('structure')
        feature_set.hints[inp12] = 'Type of real-space mask to apply: a cylinder mask based on the provided inner ' + \
        'and outer width of structure or a general structural mask based on thresholding.'
        
        feature_set.properties[inp12] = feature_set.choice_properties(2, ['cylinder', 'structure'],
        'QComboBox')
        
        feature_set.level[inp12]='intermediate'
        feature_set.relatives[inp12]='Real-space mask'

        return feature_set
    
    
    def set_layer_line_mask_option(self, feature_set):
        inp12 = 'Layer-line Fourier filter'
        feature_set.parameters[inp12] = bool(True)
        feature_set.hints[inp12] = 'Option to apply a Fourier filter at the positions of the layer lines.'
        feature_set.level[inp12]='expert'
        feature_set.relatives[inp12]='Batch mode'

        return feature_set
    
    
    def set_long_helix_option(self, feature_set):
        inp12 = 'Long helix'
        feature_set.parameters[inp12] = bool(False)
        feature_set.hints[inp12] = 'Option to generate a long volume with helical symmetry imposed.'
        feature_set.level[inp12]='expert'
        feature_set.relatives[inp12]='Batch mode'

        return feature_set
    
    
    def set_sn_weighting_option(self, feature_set):
        inp12 = 'Signal-to-noise weighting'
        feature_set.parameters[inp12] = bool(False)
        feature_set.hints[inp12] = 'Option to apply a signal-to-noise weighting based on FSC curve from Rosenthal ' + \
        'and Henderson, 2003 J Mol Biol. This measure avoids amplification of noise.'
        feature_set.level[inp12]='expert'

        return feature_set
    
    
    def set_fsc_curve(self, feature_set):
        inp1 = 'FSC curve'
        feature_set.parameters[inp1] = 'fsc_curve.dat'
        feature_set.properties[inp1] = feature_set.file_properties(1, ['dat', 'db'], 'getFile')
        feature_set.hints[inp1] = 'FSC curve corresponding to provided reconstruction: ' + \
        FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)
        feature_set.relatives[inp1]='Signal-to-noise weighting'
        
        feature_set.level[inp1]='expert'
        
        return feature_set


    def set_helix_length(self, feature_set):
        inp6 = 'Helix length in Angstrom'
        feature_set.parameters[inp6]=int(1000)
        feature_set.hints[inp6]='Helix length in Angstrom.'
        feature_set.properties[inp6]=feature_set.Range(0,10000,50)
        feature_set.level[inp6]='expert'
        feature_set.relatives[inp6]='Long helix'
        
        return feature_set
    
    
    def set_swap_helix(self, feature_set):
        inp12 = 'Swap handedness'
        feature_set.parameters[inp12] = bool(False)
        feature_set.hints[inp12] = 'Apply mirror operation to helix to swap handedness'
        feature_set.level[inp12]='expert'
        feature_set.relatives[inp12]='Batch mode'

        return feature_set
    
    


class SegRefine3dInspectPreparation(object):
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters
            
            self.infile = p['Volume reconstruction']
            self.outfile = p['Output volume name']
            
            self.batch_mode = p['Batch mode']
            self.bfactor_option = p['B-factor']
            self.bfactor, self.resolution_cutoff = p['B-factor and resolution cutoff']
            self.sn_weighting = p['Signal-to-noise weighting']
            self.fsc_file = p['FSC curve']
            
            self.pixelsize = p['Pixel size in Angstrom']
            self.helix_inner_width, self.helixwidth = p['Estimated helix inner and outer diameter in Angstrom']
            self.real_space_mask = p['Real-space mask']
            self.mask_type = p['Mask type']
            self.layerline_filter_option = p['Layer-line Fourier filter']
            self.rise_or_pitch_choice = p['Helical rise/rotation or pitch/number of units per turn choice']
            self.helical_symmetry = p['Helical symmetry in Angstrom or degrees']
            self.rotational_symmetry = p['Rotational symmetry']
            self.polar_helix = p['Helix polarity']
            
            self.long_helix_option = p['Long helix']
            self.helix_length = p['Helix length in Angstrom']
            self.swap_helix = p['Swap handedness']
            
            self.helical_symmetry = \
            SegRefine3dInspectCommonOperations().convert_helical_symmetry_from_pitch_unit_number_to_rise_rotation(
            self.rise_or_pitch_choice, self.helical_symmetry)


    def apply_bfactor_if_demanded(self, vol, bfactor, res_cutoff, pixelsize, fsc_line):
        if self.bfactor_option:
            self.log.fcttolog()
            
            vol = SegRefine3dInspectCommonOperations().apply_bfactor_and_resolution_cutoff(vol, bfactor, res_cutoff,
            pixelsize, fsc_line)
            
        return vol
    
    
    def assemble_volume_from_image_slices(self, image_slice):
        """
        >>> from spring.segment3d.segrefine3dinspect import SegRefine3dInspect
        >>> SegRefine3dInspect().assemble_volume_from_image_slices(np.ones((3, 3)))
        array([[[ 1.,  1.,  1.],
                [ 1.,  1.,  1.],
                [ 1.,  1.,  1.]],
        <BLANKLINE>
               [[ 1.,  1.,  1.],
                [ 1.,  1.,  1.],
                [ 1.,  1.,  1.]],
        <BLANKLINE>
               [[ 1.,  1.,  1.],
                [ 1.,  1.,  1.],
                [ 1.,  1.,  1.]]])
        """
        col_count, row_count = np.shape(image_slice)
        vol = np.zeros((col_count, row_count, row_count))
        
        for each_z_plane in list(range(row_count)):
            vol[:,:,each_z_plane]=image_slice
        
        return vol
    
    
    def apply_cylinder_mask_if_demanded(self, vol):
        if self.mask_type == 'cylinder' and vol is not None or not self.batch_mode:
            self.log.fcttolog()
            
            cyl_xsize = vol.get_xsize()
            cyl_zsize = vol.get_zsize()
            cylinder_mask = SegClassReconstruct().make_smooth_cylinder_mask(round(self.helixwidth / self.pixelsize), 
            round(self.helix_inner_width / self.pixelsize), cyl_xsize, cyl_zsize, 0.0)
        
            masked_vol = vol * cylinder_mask
        else:
            cylinder_mask = None
            masked_vol = None
        
        return masked_vol, cylinder_mask
    
            
    def apply_structural_mask_if_demanded(self, vol):
        if self.mask_type == 'structure' and vol is not None or not self.batch_mode:
            self.log.fcttolog()
            
            structural_mask = SegmentRefine3d().build_structural_mask_from_volume(vol, round(self.helixwidth\
            / self.pixelsize), round(self.helix_inner_width / self.pixelsize), self.pixelsize, width_falloff=0.0)
            
            masked_vol = vol * structural_mask
            masked_vol.process_inplace('normalize')
        else:
            structural_mask = None
            masked_vol = None
        
        return masked_vol, structural_mask
            
    
    def apply_layerline_filter_if_demanded(self, vol, pixelsize, helical_symmetry, helixwidth):
        if self.layerline_filter_option and vol is not None or not self.batch_mode:
            self.log.fcttolog()
            
            masked_vol, layer_mask = SegmentRefine3d().generate_and_apply_layerline_filter(vol, pixelsize,
            helical_symmetry, self.rotational_symmetry, helixwidth)
            masked_vol.process_inplace('normalize')
        else:
            masked_vol = None
            layer_mask = None
            
        return masked_vol, layer_mask
    
    
class SegRefine3dInspect(SegRefine3dInspectPreparation):
    def launch_interactive_inspect_gui(self, cart_volumes):
        app = QApplication(sys.argv)
        symexplor = SegRefine3dInspectGui(self.feature_set, cart_volumes)
        symexplor.show()
        app.exec_()


    def choose_correct_volume_for_batch_mode_depending_on_options(self, original_vol, layer_vol, cylinder_vol,
    cylinder_layer_vol, structural_vol, structural_layer_vol):
        if self.layerline_filter_option and not self.real_space_mask:
            nobfactor_vol = layer_vol
        elif not self.layerline_filter_option and not self.real_space_mask:
            nobfactor_vol = original_vol
        elif not self.layerline_filter_option and self.mask_type == 'cylinder':
            nobfactor_vol = cylinder_vol
        elif self.layerline_filter_option and self.mask_type == 'cylinder':
            nobfactor_vol = cylinder_layer_vol
        elif not self.layerline_filter_option and self.mask_type == 'structure':
            nobfactor_vol = structural_vol
        elif self.layerline_filter_option and self.mask_type == 'structure':
            nobfactor_vol = structural_layer_vol
        
        return nobfactor_vol


    def check_whether_pixelsize_set_in_volume(self, original_vol):
        if original_vol.has_attr('apix_x') and original_vol.has_attr('apix_y') and original_vol.has_attr('apix_z'):
            if original_vol.get_attr('apix_x') != 1.0:
                self.pixelsize = original_vol.get_attr('apix_x')
                self.feature_set.parameters['Pixel size in Angstrom'] = self.pixelsize
        

    def launch_inspection_of_reconstruction(self):
        original_vol = EMData()
        original_vol.read_image(self.infile)
        original_vol.process_inplace('normalize')
        
        self.check_whether_pixelsize_set_in_volume(original_vol)
                
        layer_vol, layer_mask = self.apply_layerline_filter_if_demanded(original_vol, self.pixelsize,
        self.helical_symmetry, self.helixwidth)
        
        self.log.plog(10)
        structural_vol, structural_mask = self.apply_structural_mask_if_demanded(original_vol)
        self.log.plog(20)
        structural_layer_vol, structural_mask = self.apply_structural_mask_if_demanded(layer_vol)
        self.log.plog(30)
        cylinder_vol, cylinder_mask = self.apply_cylinder_mask_if_demanded(original_vol)
        self.log.plog(40)
        cylinder_layer_vol, cylinder_mask = self.apply_cylinder_mask_if_demanded(layer_vol)
        self.log.plog(50)
        
        if self.batch_mode:
            nobfactor_vol = self.choose_correct_volume_for_batch_mode_depending_on_options(original_vol, layer_vol,
            cylinder_vol, cylinder_layer_vol, structural_vol, structural_layer_vol)
            
            if self.sn_weighting:
                fsc_line = SegRefine3dInspectCommonOperations().read_fsc_line_from_file(self.fsc_file,
                original_vol.get_xsize())
            else:
                fsc_line = None

            vol = self.apply_bfactor_if_demanded(nobfactor_vol, self.bfactor,
            self.resolution_cutoff, self.pixelsize, fsc_line)
            
            vol.process_inplace('normalize')
            if self.long_helix_option:
                vol = SegRefine3dInspectCommonOperations().prepare_long_helix(vol, self.helix_length, self.helixwidth,
                self.pixelsize, self.helical_symmetry, self.rotational_symmetry, self.polar_helix)

            if self.swap_helix:
                vol = mirror(vol)
                
            vol = SegClassReconstruct().set_isotropic_pixelsize_in_volume(self.pixelsize, vol)
            vol.write_image(self.outfile)
            self.log.plog(90)
        elif not self.batch_mode:
            volume_collection = SegRefine3dInspectCommonOperations().make_volume_collection_named_tuple()
            
            cart_volumes = volume_collection(original_vol, layer_vol, cylinder_mask, structural_mask)
            
            self.log.plog(90)
            self.launch_interactive_inspect_gui(cart_volumes)
        
        self.log.endlog(self.feature_set)
        
            
def main():
    # Option handling
    parset = SegRefine3dInspectPar()
    mergeparset = OptHandler(parset)

    ######## Program
    reconstruction = SegRefine3dInspect(mergeparset)
    reconstruction.launch_inspection_of_reconstruction()

if __name__ == '__main__':
    main()