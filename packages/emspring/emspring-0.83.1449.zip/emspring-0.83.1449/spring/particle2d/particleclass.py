# Author: Carsten Sachse
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to classify windowed particles using SPARX's k-means clustering
"""
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.csreadinput import OptHandler
from spring.particle2d.particlealign2d import ParticleAlign2d
from spring.segment2d.segmentclass import SegmentClass, SegmentClassPar
from spring.segment2d.segmentexam import SegmentExam
import numpy as np

class ParticleClassPar(SegmentClassPar):
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'particleclass'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.class_features = Features()
        self.feature_set = self.class_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    

    def add_mask_dimension_to_features(self):
        self.feature_set = self.class_features.set_particle_inner_and_outer_diameter(self.feature_set)
        

class ParticleClassPreparation(SegmentClass):
    def define_helix_or_particle_dimensions(self):
        self.inner_diameter, self.outer_diameter = self.p['Estimated inner and outer particle diameter in Angstrom']
        self.outer_diameter_in_pixel_ori = int(round(self.outer_diameter / self.pixelsize_ori))
        self.inner_diameter_in_pixel_ori = int(round(self.inner_diameter/ self.pixelsize_ori))
        
    def apply_binfactor_if_required(self):
        if self.binfactor > 1 and self.binoption is True:
            self.infilestack, self.image_dimension, self.outer_diameter_in_pixel, self.pixelsize = \
            SegmentExam().apply_binfactor(self.binfactor, self.infilestack, self.image_dimension_ori,
            self.outer_diameter_in_pixel_ori, self.pixelsize_ori)
            
            self.inner_diameter_in_pixel = self.inner_diameter / self.pixelsize
        else:
            self.outer_diameter_in_pixel = self.outer_diameter_in_pixel_ori
            self.pixelsize = self.pixelsize_ori
            self.image_dimension = self.image_dimension_ori

        self.maskwidthpix = self.outer_diameter_in_pixel
        self.maskwidthpix_ori = self.outer_diameter_in_pixel_ori
        
        
    def prepare_mask_ori(self):
        self.mask_ori = ParticleAlign2d().make_smooth_circular_mask(self.outer_diameter_in_pixel_ori,
        self.inner_diameter_in_pixel_ori, self.image_dimension_ori)
        
        return self.mask_ori
    
    
    def prepare_mask(self):
        self.mask = ParticleAlign2d().make_smooth_circular_mask(self.outer_diameter_in_pixel,
        self.inner_diameter_in_pixel, self.image_dimension)
        
        return self.mask
    

class ParticleClass(ParticleClassPreparation):
    def determine_minimal_segment_size(self):
        min_segsize = int(np.sqrt(self.outer_diameter_in_pixel ** 2 + self.outer_diameter_in_pixel ** 2) + 0.5)
        return min_segsize
    
    def add_mask_dimensions_to_align2d_features(self):
        self.aligndict['Estimated inner and outer particle diameter in Angstrom'] = ((self.inner_diameter,
        self.outer_diameter))
        
        program_to_be_launched = 'particlealign2d'
        
        return program_to_be_launched

def main():
    # Option handling
    parset = ParticleClassPar()
    mergeparset = OptHandler(parset)

    ######## Program
    stack = ParticleClass(mergeparset)
    stack.classify()

if __name__ == '__main__':
    main()
