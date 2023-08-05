# Author: Carsten Sachse 08-Jun-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to iteratively refine multiple 3D structures of helical specimens competitively from segment stacks
"""

from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment3d.refine.sr3d_main import SegmentRefine3d
from spring.segment3d.refine.sr3d_parameters import SegmentRefine3dPar


class SegMultiRefine3dPar(SegmentRefine3dPar):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'       
        self.progname = 'segmultirefine3d'
        self.proginfo = __doc__
        self.code_files = [self.progname, self.progname + '_mpi']

        self.segmentrefine3d_features = Features()
        self.feature_set = self.segmentrefine3d_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()


    def define_parameters_and_their_properties(self):
        super(SegMultiRefine3dPar, self).define_input_output_segmentrefine3d()
        super(SegMultiRefine3dPar, self).define_segmentrefine3d_parameters()
        
        self.feature_set = self.remove_key_from_feature_set(self.feature_set, 'Filter layer-lines option')
        
        
    def set_helical_symmetry_parameters(self):
        self.feature_set = self.set_helical_symmetries(self.feature_set)
        self.feature_set.relatives['Helical rise/rotation or pitch/number of units per turn choice']='Symmetrize helix'
        self.feature_set.relatives['Helical symmetries in Angstrom or degrees']='Symmetrize helix'
        self.feature_set = self.set_rotational_symmetries(self.feature_set)
        self.feature_set = self.set_polar_apolar_helix_choices(self.feature_set)


    def set_helical_symmetries(self, feature_set):
        inp8 = 'Helical symmetries in Angstrom or degrees'
        feature_set.parameters[inp8] = '(1.408, 22.03); (40, 60); (60, 80)'
        feature_set.hints[inp8] = 'List of semicolon-separated pairs of \'helical rise/pitch\' (Angstrom) and ' + \
        '\'rotation/number of units per turn\' to be imposed to 3D reconstructions. '
        feature_set.properties[inp8] = feature_set.file_properties(1, ['*'], None)
        feature_set.level[inp8] = 'beginner'
        
        return feature_set


    def set_reference_volume(self, feature_set):
        inp9 = 'Reference volumes'
        feature_set.parameters[inp9]='reference_vol???.hdf'
        feature_set.properties[inp9]=feature_set.file_properties(3,['hdf'],'getFiles')
        feature_set.hints[inp9]='Either single reference volume or list of references to be used for competitive ' + \
        '3D structure refinement. If multiple references specified header information provides helical ' + \
        'symmetry information. Accepted image file formats ({0}).'.format(', '.join(feature_set.properties[inp9].ext))
        feature_set = self.set_relatives_and_level(feature_set, inp9)
        
        return feature_set
    
    
    def set_rotational_symmetries(self, feature_set):
        inp7 = 'Rotational symmetries'
        feature_set.parameters[inp7] = '1, 1, 1'
        feature_set.hints[inp7] = 'List of comma-separated rotational symmetries. Position in list corresponds to ' + \
        'order of list of \'Helical symmetries\'.'
        feature_set.properties[inp7] = feature_set.file_properties(1, ['*'], None)
        feature_set.level[inp7]='intermediate'
        
        return feature_set
    
    
    def set_polar_apolar_helix_choices(self, feature_set):
        inp7 = 'Helix polarities'
        feature_set.parameters[inp7] = str('polar, apolar')
        feature_set.hints[inp7] = 'Choose whether helix is \'polar\' or \'apolar\'. Polar helices have different ' + \
        'ends at the top and bottom. Only the predominant direction within a helix will be used for the ' + \
        'reconstruction. In apolar helices they are related by 180 degree rotation. Thus each segment can be ' + \
        'inserted twice in the 3D reconstruction in opposite directions.'
        feature_set.properties[inp7] = feature_set.file_properties(1, ['*'], None)
        feature_set.level[inp7]='intermediate'

        return feature_set
    
    
    def remove_key_from_feature_set(self, feature_set, remove_key):
        attr = ['parameters', 'properties', 'hints', 'relatives', 'level']
        for each_attr in attr:
            if getattr(feature_set, each_attr).has_key(remove_key):
                getattr(feature_set, each_attr).__delitem__(remove_key)
        
        return feature_set


    def define_program_states(self):
        super(SegMultiRefine3dPar, self).define_program_states()


class SegMultiRefine3d(SegmentRefine3d):
    pass
    
            
def main():
    # Option handling
    parset = SegMultiRefine3dPar()
    mergeparset = OptHandler(parset)

    ######## Program
    stack = SegMultiRefine3d(mergeparset)
    stack.perform_iterative_projection_matching_and_3d_reconstruction()


if __name__ == '__main__':
    main()