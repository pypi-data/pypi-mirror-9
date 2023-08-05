# Author: Carsten Sachse
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to align particles with a restrained in-plane rotation of 0 or 180 +/- delta degrees
"""
from EMAN2 import EMNumPy
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segmentalign2d import SegmentAlign2dPar, SegmentAlign2d
from spring.segment2d.segmentexam import SegmentExam
import numpy as np
from morphology import threshold_maxval


class ParticleAlign2dPar(SegmentAlign2dPar):
    """
    Class to initiate default dictionary with input parameters including help \
    and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'particlealign2d'
        self.proginfo = __doc__
        self.code_files = [self.progname, self.progname + '_mpi']

        self.align2d_features = Features()
        self.feature_set = self.align2d_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    

    def add_mask_dimension_to_features(self):
        self.feature_set = self.align2d_features.set_particle_inner_and_outer_diameter(self.feature_set)

class ParticleAlign2dPreparation(object):
    def define_helix_or_particle_dimensions(self):
        self.inner_diameter, self.outer_diameter = self.p['Estimated inner and outer particle diameter in Angstrom']
        self.outer_diameter_in_pixel = self.helixwidthpix = int(round(self.outer_diameter / self.pixelsize))
        self.inner_diameter_in_pixel = self.helixheightpix = int(round(self.inner_diameter/ self.pixelsize))
        
        
    def log_mask_dimensions(self):
        return self.log.ilog('Maskfile                    : %s' % ('inner and outer diameter of {0} x {1} pixels'.\
        format(self.inner_diameter_in_pixel, self.outer_diameter_in_pixel)))
        

class ParticleAlign2dMask(object):
    
    def make_one_sided_smooth_circular_mask(self, outer_diameter_in_pixel, inner_diameter_in_pixel, segment_size_in_pixel,
    width_falloff=0.1):
        """
        >>> from spring.particle2d.particlealign2d import ParticleAlign2d
        >>> p = ParticleAlign2d()
        >>> circular_mask = p.make_one_sided_smooth_circular_mask(4, 0, 10)
        >>> EMNumPy.em2numpy(circular_mask)
        array([[ 0.18188323,  0.18188323,  0.18188323,  0.18188323,  0.18188323,
                 0.18188323,  0.18188323,  0.18188323,  0.18188323,  0.18188323],
               [ 0.18188323,  0.18188323,  0.18188323,  0.06593479,  0.10953172,
                 0.12490867,  0.10953172,  0.06593479,  0.18188323,  0.18188323],
               [ 0.18188323,  0.18188323,  0.09460077,  0.2676172 ,  0.42799017,
                 0.48670098,  0.42799017,  0.2676172 ,  0.09460077,  0.18188323],
               [ 0.18188323,  0.06593479,  0.2676172 ,  0.57476914,  0.8788265 ,
                 0.99999994,  0.8788265 ,  0.57476914,  0.2676172 ,  0.06593479],
               [ 0.18188323,  0.10953172,  0.42799017,  0.8788265 ,  0.99999994,
                 0.99999994,  0.99999994,  0.8788265 ,  0.42799017,  0.10953172],
               [ 0.18188323,  0.12490867,  0.48670098,  0.99999994,  0.99999994,
                 0.99999994,  0.99999994,  0.99999994,  0.48670098,  0.12490867],
               [ 0.18188323,  0.10953172,  0.42799017,  0.8788265 ,  0.99999994,
                 0.99999994,  0.99999994,  0.8788265 ,  0.42799017,  0.10953172],
               [ 0.18188323,  0.06593479,  0.2676172 ,  0.57476914,  0.8788265 ,
                 0.99999994,  0.8788265 ,  0.57476914,  0.2676172 ,  0.06593479],
               [ 0.18188323,  0.18188323,  0.09460077,  0.2676172 ,  0.42799017,
                 0.48670098,  0.42799017,  0.2676172 ,  0.09460077,  0.18188323],
               [ 0.18188323,  0.18188323,  0.18188323,  0.06593479,  0.10953172,
                 0.12490867,  0.10953172,  0.06593479,  0.18188323,  0.18188323]], dtype=float32)
        >>> circular_mask = p.make_one_sided_smooth_circular_mask(46, 13, 67)
        """
        outer_diameter_in_pixel = int(outer_diameter_in_pixel)
        inner_diameter_in_pixel = int(inner_diameter_in_pixel)
        odd = (outer_diameter_in_pixel) %2
        if odd:
            outer_diameter_in_pixel -= 1 
            
        odd = (inner_diameter_in_pixel) %2
        if odd:
            inner_diameter_in_pixel -= 1
            
        falloff_line, falloff_len = SegmentExam().generate_falloff_line(int(segment_size_in_pixel), width_falloff)
        pixels_to_fill = (segment_size_in_pixel - outer_diameter_in_pixel - 2 * (falloff_len)) / 2
        outer_ring_width = (outer_diameter_in_pixel - inner_diameter_in_pixel) / 2
        
        inner_mask = np.append(np.ones(outer_ring_width), np.append(np.zeros(inner_diameter_in_pixel),
        np.ones(outer_ring_width)))
        
        if pixels_to_fill < 0:
            falloff_zeros = falloff_line[:(segment_size_in_pixel - outer_diameter_in_pixel) / 2]
        else:
            falloff_zeros = np.append(falloff_line, np.zeros(pixels_to_fill))
            
        line_right = np.append(inner_mask, falloff_zeros)
        line = np.append(np.flipud(falloff_zeros), line_right)
        if len(line) < segment_size_in_pixel:
            line = np.append(np.zeros(1), line)
        
        mask = np.zeros((segment_size_in_pixel, segment_size_in_pixel))

        mask[segment_size_in_pixel / 2] = line
         
        emmask = EMNumPy.numpy2em(np.copy(mask))
        rotmask = emmask.rotavg_i()
        edge = (segment_size_in_pixel - outer_diameter_in_pixel) / 2
        value_at_edge = rotmask.get_value_at(segment_size_in_pixel / 2, int(edge))
        
        rotmask = threshold_maxval(rotmask, value_at_edge)
        rotmask /= value_at_edge
        
        return rotmask
        
        
    def make_smooth_circular_mask(self, outer_diameter_in_pixel, inner_diameter_in_pixel, segment_size_in_pixel,
    width_falloff=0.1):
        """
        >>> from spring.particle2d.particlealign2d import ParticleAlign2d
        >>> p = ParticleAlign2d()
        >>> circular_mask = p.make_smooth_circular_mask(4, 2, 10)
        >>> EMNumPy.em2numpy(circular_mask)
        array([[  1.81883231e-01,   1.81883231e-01,   1.81883231e-01,
                  1.81883231e-01,   1.81883231e-01,   1.81883231e-01,
                  1.81883231e-01,   1.81883231e-01,   1.81883231e-01,
                  1.81883231e-01],
               [  1.81883231e-01,   1.81883231e-01,   1.81883231e-01,
                  6.59347922e-02,   1.09531723e-01,   1.24908671e-01,
                  1.09531723e-01,   6.59347922e-02,   1.81883231e-01,
                  1.81883231e-01],
               [  1.81883231e-01,   1.81883231e-01,   9.46007743e-02,
                  2.67617196e-01,   4.27990168e-01,   4.86700982e-01,
                  4.27990168e-01,   2.67617196e-01,   9.46007743e-02,
                  1.81883231e-01],
               [  1.81883231e-01,   6.59347922e-02,   2.67617196e-01,
                  5.68024158e-01,   8.48794281e-01,   9.60687220e-01,
                  8.48794281e-01,   5.68024158e-01,   2.67617196e-01,
                  6.59347922e-02],
               [  1.81883231e-01,   1.09531723e-01,   4.27990168e-01,
                  8.48794281e-01,   8.46149981e-01,   7.65159965e-01,
                  8.46149981e-01,   8.48794281e-01,   4.27990168e-01,
                  1.09531723e-01],
               [  1.81883231e-01,   1.24908671e-01,   4.86700982e-01,
                  9.60687220e-01,   7.65159965e-01,  -5.96046448e-08,
                  7.65159965e-01,   9.60687220e-01,   4.86700982e-01,
                  1.24908671e-01],
               [  1.81883231e-01,   1.09531723e-01,   4.27990168e-01,
                  8.48794281e-01,   8.46149981e-01,   7.65159965e-01,
                  8.46149981e-01,   8.48794281e-01,   4.27990168e-01,
                  1.09531723e-01],
               [  1.81883231e-01,   6.59347922e-02,   2.67617196e-01,
                  5.68024158e-01,   8.48794281e-01,   9.60687220e-01,
                  8.48794281e-01,   5.68024158e-01,   2.67617196e-01,
                  6.59347922e-02],
               [  1.81883231e-01,   1.81883231e-01,   9.46007743e-02,
                  2.67617196e-01,   4.27990168e-01,   4.86700982e-01,
                  4.27990168e-01,   2.67617196e-01,   9.46007743e-02,
                  1.81883231e-01],
               [  1.81883231e-01,   1.81883231e-01,   1.81883231e-01,
                  6.59347922e-02,   1.09531723e-01,   1.24908671e-01,
                  1.09531723e-01,   6.59347922e-02,   1.81883231e-01,
                  1.81883231e-01]], dtype=float32)
        """
        outer_mask = self.make_one_sided_smooth_circular_mask(outer_diameter_in_pixel, 0, segment_size_in_pixel,
        width_falloff)
        
        if inner_diameter_in_pixel == 0:
            combined_mask = outer_mask
        else:
            adjusted_inverted_diameter = max(0, inner_diameter_in_pixel - 2 * width_falloff * segment_size_in_pixel)
            
            if adjusted_inverted_diameter == 0:
                width_falloff = inner_diameter_in_pixel / float( 2 * segment_size_in_pixel)
            inner_mask = self.make_one_sided_smooth_circular_mask(adjusted_inverted_diameter, 0, segment_size_in_pixel,
            width_falloff)
        
            combined_mask = outer_mask - inner_mask
        
        return combined_mask
    
        
    def prepare_mask(self, helixwidthpix, helixheightpix, image_dimension):
        self.mask = self.make_smooth_circular_mask(helixwidthpix, helixheightpix, image_dimension)
        
        return self.mask
    
    
class ParticleAlign2d(ParticleAlign2dPreparation, ParticleAlign2dMask, SegmentAlign2d):
    pass
        
def main():
    # Option handling
    parset = ParticleAlign2dPar()
    mergeparset = OptHandler(parset)

    ######## Program
    stack = ParticleAlign2d(mergeparset)
    stack.perform_segmentalign2d()

if __name__ == '__main__':
    main()
