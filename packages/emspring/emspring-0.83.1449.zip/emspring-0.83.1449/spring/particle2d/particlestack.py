# Author: Carsten Sachse
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to extract particles from micrographs 
"""
from collections import namedtuple
from spring.csinfrastr.csdatabase import SpringDataBase, base
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segment import SegmentPar, Segment
from tabulate import tabulate
import os

class ParticleStackPar(SegmentPar):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'particlestack'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.segment_features = Features()
        self.feature_set = self.segment_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()
    
    def set_center_and_remove_ends_for_helices(self):
        pass
#         self.feature_set = self.set_center_option(self.feature_set)

    def set_helix_or_particle_centering(self):
        self.set_center_and_remove_ends_for_helices()
        
    def set_segment_or_window_features(self):
        self.feature_set = self.set_particle_coordinate_files(self.feature_set)
        self.feature_set = self.set_window_size(self.feature_set)
        self.feature_set = self.segment_features.set_particle_inner_and_outer_diameter(self.feature_set)
        
    def define_program_states(self):
        self.feature_set.properties['Number of lines Logfile']=6000

        self.feature_set.program_states['assign_reorganize']='Initialize micrographs and segments to convert them ' + \
        'into Spring\'s file structure'
        self.feature_set.program_states['readmic']='Loading new micrograph'
        self.feature_set.program_states['center_segments']='Segments are centered in their x and y position'
        self.feature_set.program_states['window_segment']='Windowing particles from micrograph'

    def set_particle_coordinate_files(self, feature_set):
        inp3 = 'Particle coordinates'
        feature_set.parameters[inp3] = 'scan034.box'
        feature_set.properties[inp3] = feature_set.file_properties(1000, ['box', 'txt'], 'getFiles')
        feature_set.hints[inp3] = 'Input: file with identical name of corresponding micrograph (accepted file ' + \
        'formats EMAN\'s Boxer and EMAN2\'s *.%s coordinates)' % (', '.join(self.properties[inp3].ext))
        feature_set.level[inp3]='beginner'

        return feature_set
    
        
    def set_window_size(self, feature_set):
        inp4 = 'Window size in Angstrom'
        feature_set.parameters[inp4] = int(600)
        feature_set.hints[inp4] = 'Size should be 2 x particle diameter'
        feature_set.properties[inp4] = feature_set.Range(100, 1500, 50)
        feature_set.level[inp4]='beginner'
        
        return feature_set
    

    def set_center_option(self, feature_set):
        inp7 = 'Center option'
        feature_set.parameters[inp7] = bool(True)
        feature_set.hints[inp7] = 'Particle are centered with respect to their x and y position'
        feature_set.level[inp7]='intermediate'

        return feature_set


class ParticleStack(Segment):
    def define_segment_or_window_parameters(self, p):
        self.coordinate_files_entry = p['Particle coordinates']
        self.window_size = p['Window size in Angstrom']
        self.inner_diameter, self.outer_diameter = p['Estimated inner and outer particle diameter in Angstrom']
    
    def make_micinfo_named_tuple(self):
        micinfo = namedtuple('micinfo', 'mic_id micrograph coordinate_list picked_coordinates')
        
        return micinfo
    
    
    def single_out(self, pair):
        micrograph_coordinates = []
        micinfo = self.make_micinfo_named_tuple()
        for mic_id, (micfile, coordfile, overlap) in enumerate(pair):
            coord_line = self.get_picked_coordinates_from_file(coordfile, overlap)
            
            xcoord = []
            ycoord = []
            for each_coordinate_line in ''.join(coord_line).splitlines():
                xcenter, ycenter = self.convert_coordinate_line_to_xy_coordinates(each_coordinate_line)
                xcoord.append(xcenter)
                ycoord.append(ycenter)
            
            coord = zip(xcoord, ycoord)
            micrograph_coordinates.append(micinfo(mic_id, micfile, coordfile, coord))
        
        return micrograph_coordinates
        

    def prepare_windowing(self):
        pairs = self.assign_reorganize(self.micrograph_files, self.coordinate_files)
        micrograph_coordinates = self.single_out(pairs)
        
        return micrograph_coordinates
    
    
    def excise_particles_from_micrographs(self, micrograph_coordinates):
        if self.spring_db_option:
            session = SpringDataBase().setup_sqlite_db(base, self.spring_path)
        else:
            session = None

        micrograph_img, matched_mic_find, micrograph_name, log_info, ctf_info, each_image_index = \
        self.pre_loop_setup()
        
        for each_mic_index, each_mic in enumerate(micrograph_coordinates):
            
            micrograph_img, matched_mic_find, micrograph_name = self.read_micrograph_and_get_ctf_info(micrograph_img,
            matched_mic_find, micrograph_name, session, each_mic)
            
            for (xcoord, ycoord) in each_mic.picked_coordinates:
                
                windowed_segment, ctf_info = self.window_segment_and_invert_normalize_and_ctf_correct(session,
                self.segsizepix, each_mic, micrograph_img, matched_mic_find, xcoord, ycoord, ctf_info, each_image_index)
                
                windowed_segment.write_image(self.outfile, each_image_index)
                
                log_info += [[each_image_index, each_mic.mic_id, micrograph_name, xcoord, ycoord, self.normoption,
                self.invertoption]]
                
                each_image_index = each_image_index + 1
            self.log.plog(100 * (each_mic_index + 1) / len(micrograph_coordinates) - 10)
            
        msg = tabulate(log_info, ['Particle_id', 'mic_id', 'micrograph', 'x_coordinate', 'y_coordinate',
        'normalization', 'contrast_inversion'])

        if self.ctfcorrect_option:
            msg += '\n' + tabulate(ctf_info, self.get_ctfinfo_header())
        self.log.ilog(log_info)
                
        return self.outfile
    
                
    def window_particles(self):
        micrograph_coordinates = self.prepare_windowing()
        self.log.plog(10)
        imgstack = self.excise_particles_from_micrographs(micrograph_coordinates)
        if self.binoption is True: 
            binned_imgstack = '{0}-{1}xbin{2}'.format(os.path.splitext(imgstack)[0], self.binfactor,
            os.path.splitext(imgstack)[-1])
            
            self.binstack(imgstack, binned_imgstack, self.binfactor)
        
        self.log.endlog(self.feature_set)
        
    
def main():
    # Option handling
    parset = ParticleStackPar()
    mergeparset = OptHandler(parset)
 
    ######## Program
    mic = ParticleStack(mergeparset)
    mic.window_particles()

if __name__ == '__main__':
    main()
