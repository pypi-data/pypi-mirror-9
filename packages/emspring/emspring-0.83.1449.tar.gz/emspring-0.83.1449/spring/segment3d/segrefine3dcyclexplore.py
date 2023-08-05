# Author: Carsten Sachse 29-Aug-2011
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Program to interactively explore refinement cycle statistics
"""
from spring.csinfrastr.csdatabase import SpringDataBase, refine_base, RefinementCycleTable
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import DiagnosticPlot
from spring.csinfrastr.csreadinput import OptHandler
from spring.segment2d.segmentplot import SegmentPlot
from spring.segment3d.seggridexplore import SegGridExploreSupport
from sqlalchemy.sql.expression import asc
import numpy as np
import os
import shutil


class SegRefine3dCycleExplorePar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and status dictionary
    """
    def __init__(self):
        # package/program identity
        self.package = 'emspring'       
        self.progname = 'segrefine3dcyclexplore'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.seggridexplore_features = Features()
        self.feature_set = self.seggridexplore_features.setup(self)
        
        self.define_parameters_and_their_properties()
        self.define_program_states()


    def define_parameters_and_their_properties(self):
        self.feature_set = self.seggridexplore_features.set_inp_refinement_path(self.feature_set)
        self.feature_set = self.seggridexplore_features.set_interactive_vs_batch_mode(self.feature_set)
        
        self.feature_set = self.seggridexplore_features.set_diagnostic_prefix(self.feature_set, 'intermediate', 
        'Batch mode')
        
        self.feature_set = self.set_criterion_to_be_plotted(self.feature_set)
        
    def define_program_states(self):
        self.feature_set.program_states['extract_desired_criteria']='Extract desired refinement criteria'
        self.program_states['launch_segrefine3dcyclexplore_gui']='Explore different refinement criteria interactively'

    

    def set_criterion_to_be_plotted(self, feature_set):
        inp9 = 'Criterion'
        feature_set.parameters[inp9]=str('mean_helical_ccc')
        
        criteria = SegRefine3dCycleExploreSupport().get_segrefin3dcyclexpore_criteria()
        
        feature_set.properties[inp9] = feature_set.choice_properties(2, criteria, 'QComboBox')
        
        feature_set.hints[inp9]=SpringDataBase().get_hints_from_refinement_cycle(criteria)
        feature_set.relatives[inp9]=('Batch mode')
        feature_set.level[inp9]='intermediate'
        
        return feature_set
    
    
class SegRefine3dCycleExploreSupport(object):
    def get_segrefin3dcyclexpore_criteria(self):
        criteria = SegGridExploreSupport().get_common_criterias() + \
        SegRefine3dCycleExploreSupport().get_additional_criteria()
        
        return criteria


    def get_additional_criteria(self):
        return ['excluded_out_of_plane_tilt_count', 'excluded_inplane_count', 'total_excluded_count']
    
    
class SegRefine3dCycleExplorePreparation(object):
    def __init__(self, parset = None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters
            
            self.refinement_db = p['refinement.db file']
            self.infile = self.refinement_db
            self.batch_mode = p['Batch mode']
            self.outfile_prefix = p['Diagnostic plot prefix']
            
            self.criterion = p['Criterion']
            
            
    def get_refinement_info_from_database(self, refinement_db):
        ref_session = SpringDataBase().setup_sqlite_db(refine_base, refinement_db)
        ref_cycles = ref_session.query(RefinementCycleTable).order_by(asc(RefinementCycleTable.id)).all()
        
        ref_data = []
        ylabels = []
        filtered_quant = []
        
        criteria = SegRefine3dCycleExploreSupport().get_segrefin3dcyclexpore_criteria()
        
        for each_attr in criteria:
            ref_data, ylabels, filtered_quant = SegGridExploreSupport().get_all_attr_from_search_result(ref_cycles,
            each_attr, filtered_quant, ref_data, ylabels, RefinementCycleTable)
            
        ref_cycle_ids = [each_ref_cycle.id for each_ref_cycle in ref_cycles]
        
        xlabel = 'Iteration cycle'
        
        ref_data = [(ylabels[each_id], np.array([ref_cycle_ids, each_ref_data])) for (each_id, each_ref_data) in\
        enumerate(ref_data)]
        
        labels = [[xlabel, each_y_label] for each_y_label in ylabels]
        
        hints = SpringDataBase().get_hints_from_refinement_cycle(filtered_quant)
        
        return ref_data, labels, criteria, hints
    
    
class SegRefine3dCycleExplore(SegRefine3dCycleExplorePreparation):
    
    def plot_data_on_figure(self, xy_quantities, labels, criterion_id):
        self.log.fcttolog()
        
        figures = []
        segmentplot_plot = DiagnosticPlot()
        self.log.plog(20)
        for quant_index, (each_set_id_label, each_segid_xy) in enumerate(xy_quantities):
            fig = segmentplot_plot.create_next_figure()
            
            filename = '{0}_{1}{2}'.format(os.path.splitext(self.outfile_prefix)[0],
            '_'.join(each_set_id_label.lower().split()), os.path.splitext(self.outfile_prefix)[-1])
            
            if self.batch_mode:
                fig = segmentplot_plot.add_header_and_footer(self.feature_set, self.infile, filename)
        
            ax1 = fig.add_subplot(111)
            
            ax1.set_title('{0}'.format(each_set_id_label.title()))
            x_label, y_label = labels[quant_index]
            x_data, y_data = each_segid_xy
            ax1.plot(x_data, y_data, 'x')
            ax1.plot(x_data, y_data, ':')
            [each_tick.set_fontsize(8) for each_tick in ax1.get_xticklabels() + ax1.get_yticklabels()]
            
            ax1.set_xlabel(x_label, fontsize=8)
            ax1.set_ylabel(y_label, fontsize=8)
                    
            if self.batch_mode and quant_index in criterion_id:
                fig.savefig(filename)
            elif not self.batch_mode:
                figures.append(fig)
            self.log.plog(70 * (quant_index + 1) / len(xy_quantities) + 20)
            self.log.ilog('{0}{1} plot was generated.'.format(each_set_id_label[0].capitalize(), each_set_id_label[1:]))
        
        return figures
    
    
        
    def plot_refinement_criteria_per_cycle(self):
        work_refinement_db = os.path.basename(self.refinement_db)
        shutil.copy(self.refinement_db, work_refinement_db)
            
        xy_quantities, labels, criteria, hints = self.get_refinement_info_from_database(work_refinement_db)
        
        criterion_id = [crit_id for (crit_id, each_criterion) in enumerate(criteria) if each_criterion == self.criterion]
        
        self.log.plog(10)
        figures = self.plot_data_on_figure(xy_quantities, labels, criterion_id)
        if not self.batch_mode:
            SegmentPlot().launch_interactive_plot_gui(self.feature_set, figures, xy_quantities, labels, hints)
        
        self.log.endlog(self.feature_set)
        
        
def main():
    # Option handling
    parset = SegRefine3dCycleExplorePar()
    mergeparset = OptHandler(parset)

    ######## Program
    sseg = SegRefine3dCycleExplore(mergeparset)
    sseg.plot_refinement_criteria_per_cycle()

if __name__ == '__main__':
    main()
