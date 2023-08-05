# Author: Carsten Sachse 
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
Productivity module with general infrastructure support
"""
from EMAN2 import EMData, EMUtil, display
from getpass import getuser
import math
import os
import shutil
import signal
import subprocess
import sys
import time

from PyQt4.QtCore import QProcess, QProcessEnvironment, QIODevice, QThread
from tabulate import tabulate

import matplotlib.pyplot as plt
import numpy as np


try:
    from mpi4py import MPI
except:
    pass


class DiagnosticPlot(object):

    def __init__(self, fig_no=None):
        if fig_no is None:
            start_fig = 0 
        else:
            start_fig = fig_no
            
        self.fig_no = iter(list(range(start_fig, 10000)))
        self.plt = plt
        self.fig = self.plt.figure(fig_no)


    def get_empty_fig(self):
        
        return self.fig
    
    
    def create_next_figure(self):
        self.fig = self.plt.figure(self.fig_no.next())
        
        return self.fig
    
        
    def add_header_and_footer(self, feature_set=None, infile=None, outfile=None):
        """
        * Function to add header for matplotlib output plots
        
        #. Input: infile name, outfile name to be added to header
        #. Output: figure with header 
        #. Usage: fig = DiagnosticPlot(fig).add_header_and_footer(feature_set, \
        infile, outfile)
        """
        if feature_set is None: 
            feature_set = self.feature_set
        if infile is None: 
            infile = list(feature_set.parameters.values())[0]
        if outfile is None: 
            outfile = list(feature_set.parameters.values())[1]

        self.fig.suptitle('{prg} {infile} {outfile}'.format(prg=feature_set.progname,
        infile=os.path.basename(list(feature_set.parameters.values())[0]), outfile=os.path.basename(outfile)))

        self.fig.subplots_adjust(left=None, bottom=0.3, right=None, top=None, wspace=0.3, hspace=None)
        parameters = parameter_values = ''
        for name in feature_set.parameters:
            parameters += '{0:<80}\n'.format(name) 
            if str(feature_set.parameters[name]).startswith(os.sep):
                filename_split = feature_set.parameters[name].split(os.sep)
                value = (os.sep.join(filename_split[-3:]))
            else:
                value = feature_set.parameters[name]
            parameter_values += '= {0}\n'.format(value)

        parameters += '{ltime} (PID={pid})'.format(ltime=time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime()),
                                             pid=os.getpid())
        parameter_values += '   Printed to {0}'.format(os.path.basename(outfile))
        
        if len(feature_set.parameters) < 12:
            self.fig.text(0.1, 0.03, parameters, fontsize=4)
            self.fig.text(0.43, 0.03, parameter_values, fontsize=4)
        else:
            self.fig.text(0.1, 0.03, parameters, fontsize=3)
            self.fig.text(0.43, 0.03, parameter_values, fontsize=3)

        return self.fig


    def set_fontsize_to_all_ticklabels_of_subplots(self, subplot_collection, font_size=4):
        for each_subplot in subplot_collection:
            for t in each_subplot.get_xticklabels():
                t.set_fontsize(font_size)
            
            for t in each_subplot.get_yticklabels():
                t.set_fontsize(font_size)
                
        return subplot_collection
    
    def __del__(self):
        plt.close()
        

class Support(object):
    def define_levels_beginner_intermediate_expert(self):
        levels = {'beginner':['beginner'], 
                  'intermediate':['beginner', 'intermediate'], 
                  'expert':['beginner', 'intermediate', 'expert']}
        
        return levels
    
    
    def search_path_like_which(self, exe):
        for each_dir in os.environ['PATH'].split(os.pathsep):
            binpath = os.path.join(each_dir, exe) 
            if os.path.exists(binpath):
                return os.path.abspath(binpath)
        return None
    
    
    def compute_byte_size_of_image_stack(self, xsize, ysize, image_count):
        """
        >>> a = np.polyfit([1, 10000, 500**2], [10124, 50120, 1010120], 2) 
        >>> np.polyval(a, 300 * 300)
        370119.99999999919
        >>> from spring.csinfrastr.csproductivity import Support
        >>> Support().compute_byte_size_of_image_stack(300, 300, 1)
        370120
        >>> Support().compute_byte_size_of_image_stack(300, 300, 10)
        3610120
        """
        header_size =  10120
        byte_size =  header_size + image_count * xsize * ysize * 4
        
        return byte_size
    
    
class ExtLauncher(QThread):
    """
    Class that holds functions for external system viewers
    """
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.qlaunchproc = set([])
        

    def construct_command_line(self, ofile):
        from platform import system
        ofileext = os.path.splitext(str(ofile))[-1].strip(os.extsep)
        args = None
        try:
            if ofileext in ['mrc', 'spi', 'hdf', 'img', 'hed']:
                prg = Support().search_path_like_which('springenv')
                args =  Support().search_path_like_which('e2display.py')
            elif system() == 'Darwin':
                prg = 'open'
            elif os.name == 'nt':
                prg = 'start'
            elif system() == 'Linux':
                prg = 'gnome-open'
        except:
            print('Platform not recognized or supported')
        if args is None:
            dirprogname = '{0} {1}'.format(prg, ofile)
        else:
            dirprogname = '{0} {1} {2}'.format(prg, args, ofile)
            
        print(dirprogname)
        
        return prg, args


    def display_em(self, em_file):
        display(em_file)
        
        
    def qlaunch(self, prg, args):
        QProcessEnvironment.systemEnvironment()
        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        self.proc.start(prg, args, QIODevice.ReadWrite)
        self.qlaunchproc.add(self.proc) 
        self.proc.finished.connect(lambda: self.qlaunchproc.remove(self.proc))
        
    def finished(self):
        self.proc.terminate()


    def qlaunch_open_file(self, ofile):
        prg, add_args = self.construct_command_line(ofile)
        if add_args is None:
            args = [ofile]
        else: 
            args = [add_args, ofile]

        self.qlaunch(prg, args)


    def __del__(self):
        self.exiting = True
        self.wait()
        
        
class IOFormatError(IOError):
    pass

class Errors(object):
    def check_valerr(self, value):
        try:
            value = float(value)
            if value < self.properties[self.name].minimum or value > self.properties[self.name].maximum:
                raise ValueError()
        except ValueError:
            error_message = '{0}: value \'{1}\' '.format(self.feature_set.progname, self.name) + \
                             '{0} is outside the pre-defined input range (min={1}, max={2}).'.format(value, 
                              self.properties[self.name].minimum, self.properties[self.name].maximum)
            sys.stderr.write(error_message)
            raise ValueError(error_message)
        

    def check_filerr(self, file_name):
        try:
            if self.name in self.relatives and self.parameters[self.relatives[self.name]] is False:
                pass
            elif self.parameters[self.name].find('nosetest_') >= 0:
                print('File was generated by nosetest suite. Test is fine. Exit')
                sys.exit()
            elif file_name in ['.']:
                pass
            elif os.path.exists(file_name):
                print('{0} found'.format(file_name))
            elif not os.path.exists(file_name):
                raise IOError
        except IOError:
            error_message = 'File or directory \'{0}\' was not found.'.format(file_name)
            sys.stderr.write(error_message)
            raise IOError(error_message)
        self.check_fileformat(file_name)


    def check_fileformat(self, file_name):
        try:
            if self.properties[self.name].ext[0] == '*':
                pass
            elif self.name in self.relatives and self.parameters[self.relatives[self.name]] is False:
                pass
            elif file_name.split(os.extsep)[-1] not in self.properties[self.name].ext:
                raise IOFormatError()
        except IOFormatError:
            error_message = 'File format \'{0}\' for \'{1}\' is not supported.'.format(file_name.split(os.extsep)[-1], 
                                                                              self.name)
            sys.stderr.write(error_message)
            raise IOError(error_message)

        
"""
Disk Space
Simple class for working out the free disk space on a system

by Stuart Colville http://muffinresearch.co.uk
License: http://www.opensource.org/licenses/mit-license.php

"""


class DiskSpace():

    """Free Disk Space"""

    def __init__(self, path='/'):
        """Init class and retrieves disk space info"""
        self.disk = os.statvfs(path)

    def has_free_space(self, limit):
        """Bool returns true if remaining space is above limit %"""
        if float(self.percent_free()) < float(limit):
            return False
        else:
            return True

    def percent_free(self):
        """Gets the amount of space left as a percentage"""
        return (math.ceil(float(100) / float(self.bytes_capacity())
                                                * self.bytes_free()))

    def bytes_capacity(self):
        """Returns the total capacity in bytes"""
        return self.disk.f_frsize * self.disk.f_blocks

    def bytes_free(self):
        """Returns the free space in bytes"""
        return self.disk.f_frsize * self.disk.f_bavail

    def bytes_used(self):
        """Returns the used space in bytes"""
        return self.disk.f_frsize * (self.disk.f_blocks -
                                                   self.disk.f_bavail)

    @staticmethod
    def humanize_bytes(bytes, kilo=1024):

        """Humanizes bytes

        See http://en.wikipedia.org/wiki/Kilobyte for info on the
        different ways to interpret whether a kilobyte is 1,024 bytes
        or 1,000 bytes

        >>> from spring.csinfrastr.csproductivity import DiskSpace
        >>> DiskSpace().humanize_bytes(1024 ** 2)
        '1.00MB'
        >>> DiskSpace().humanize_bytes(1024 ** 3)
        '1.00GB'
        >>> DiskSpace().humanize_bytes(1024 ** 4)
        '1.00TB'
        """
        if kilo != 1024:
            kilo = 1000
            
        label = ['KB', 'MB' , 'GB', 'TB']

        if bytes < kilo:
            human_bytes = '%d' % bytes
        elif bytes >= kilo and bytes < math.pow(kilo, 2):
            human_bytes = '%.2F%s' % (float(bytes/kilo), label[0])
        elif bytes >= math.pow(kilo, 2) and bytes < math.pow(kilo, 3):
            human_bytes = '%.2F%s' % (float(bytes/math.pow(kilo, 2)), label[1])
        elif bytes >= math.pow(kilo, 3) and bytes < math.pow(kilo, 4):
            human_bytes = '%.2F%s' % (float(bytes/math.pow(kilo, 3)), label[2])
        elif bytes >= math.pow(kilo, 4) and bytes < math.pow(kilo, 5):
            human_bytes = '%.2F%s' % (float(bytes/math.pow(kilo, 4)), label[3])
        
        return human_bytes
        
        
class Temporary(object):
    def remove_dir_and_everything_inside(self, tempdir):
        if os.path.isdir(tempdir):
            files_to_be_deleted = os.listdir(tempdir)
            [os.remove(os.path.join(tempdir, each_file)) for each_file in files_to_be_deleted]
            shutil.rmtree(tempdir)


    def generate_tmpdir_name(self, temppath):
        tmpdir = temppath + os.sep + getuser() + '-' + time.strftime('%d_%b_%Y_%H_%M_%S') + '-' + '%d' % os.getpid() + \
        os.sep
        
        return tmpdir


    def check_available_space_in_curdir_and_add_to_error_if_not_enough_space_available(self):
        ds = DiskSpace(os.curdir)
        if ds.bytes_free() < 100000:
            err_msg = '\nIt looks like you ran out of disk space because currently only ' + \
            '{0} are available in the '.format(ds.humanize_bytes(ds.bytes_free())) + \
            'current directory {0}.'.format(os.path.abspath(os.curdir))
        else:
            err_msg = ''
        
        return err_msg


    def check_available_space_in_temppath_and_raise_error_if_not_enough_space_available(self, temppath, size):
        err_msg = None
        if size is not None:
            ds = DiskSpace(temppath)
            if 1.1 * size > ds.bytes_free():
                this_node_name = os.uname()[1]
                err_msg = 'The specified \'Temporary directory\' \'{0}\' does not have sufficient space '.format(temppath) + \
                'to carry out the task. Only {0} are available '.format(ds.humanize_bytes(ds.bytes_free())) + \
                'on {0}. The program is projected to require a minimum of '.format(this_node_name) + \
                '{0} in the temporary directory. '.format(ds.humanize_bytes(1.1 * size)) + \
                '\nSolutions: (1) Tile the job further ' + \
                'to run on more nodes which will distribute the temporary data onto more hard drives. ' + \
                '\n(2) The required disk space directly correlates with the size and number of requested projections. ' +\
                'Reduce the \'Alignment size\' or \'Number of projections azimuthal/out-of-plane angle\' parameters ' +\
                'if necessary. ' 
                
                if ds.bytes_capacity() > size:
                    err_msg += '\n(3) Clean-up the \'Temporary directory\' \'{0}\' '.format(temppath) + \
                    'on {0} because the drive has '.format(this_node_name) + \
                    '{0} of total capacity. '.format(ds.humanize_bytes(ds.bytes_capacity()))
                    err_msg += '\n(4) Remove other jobs that may concurrently fill up the temporary disk space. '
                    
                err_msg += '\n* If you do not know what all of ' + \
                'above means or if you do not have sufficient temporary disk space available choose ' + \
                'an alternative location for this task, e.g. the current directory \'.\' ' + \
                'Be aware, in case you are using distributed computing on multiple nodes, ' + \
                'this action will lead to unnecessary network traffic and slow down your ' + \
                'entire network significantly.'
            
        return err_msg


    def mkdir_temporary_directory(self, temppath, size=None):
        
        err_msg = self.check_available_space_in_temppath_and_raise_error_if_not_enough_space_available(temppath, size)
        tmpdir = self.generate_tmpdir_name(temppath)
        
        os.mkdir(tmpdir)
        
        return tmpdir, err_msg


    def mktmpdir(self, temppath, byte_size=None):
        tmpdir, err_msg = self.mkdir_temporary_directory(temppath, byte_size)
        
        _excepthook = sys.excepthook 

        def excepthook(t,v,tb): 
            _excepthook(t,v,tb) 
                    
            self.remove_dir_and_everything_inside(tmpdir)
            err_msg = self.check_available_space_in_curdir_and_add_to_error_if_not_enough_space_available()
            err_msg += '\nThe following temporary directory was cleared and removed:\n'
            err_msg += tmpdir
                    
            sys.stderr.write(err_msg)
            sys.exit(1)
        
        sys.excepthook = excepthook 
        
        return tmpdir
    
    
    def get_deletion_info_named_tuple(self):
        from collections import namedtuple
        del_i = namedtuple('del_info', 'rank_id node process_id directory space')
        
        return del_i
    

    def generate_tempdir_from_user(self, tempdir, this_user):
        return '{tmpdir}{sep}{user}*'.format(tmpdir=tempdir, user=this_user, sep=os.sep)
    

    def generate_deletion_info_from_nodefile(self, nodefile_string, tempdir, space=3, this_user=None):
        """
        >>> from spring.csinfrastr.csproductivity import Temporary
        >>> t = Temporary()
        >>> t.generate_deletion_info_from_nodefile(['cl1', 'cl2'], '/tmp', 3, 'me') #doctest: +NORMALIZE_WHITESPACE
         [del_info(rank_id=0, node='cl1', process_id=None, directory='/tmp/me*', space=3), 
         del_info(rank_id=1, node='cl2', process_id=None, directory='/tmp/me*', space=3)]
        """
        if this_user is None:
            this_user = getuser()
        
        del_i = self.get_deletion_info_named_tuple()
        
        nodelist = [del_i(each_node_index, each_node.strip(), None, 
        self.generate_tempdir_from_user(tempdir, this_user), space) for each_node_index, each_node in \
        enumerate(nodefile_string)] 
        
        return nodelist


    def read_through_every_logline_and_extract_deletion_info(self, logfile_lines):
        """
        >>> from spring.csinfrastr.csproductivity import Temporary
        >>> t = Temporary()
        >>> t.read_through_every_logline_and_extract_deletion_info(['Number of CPUs = 2', \
'rank_id node_name       process_id      directory    space',\
'0       clnode215.embl.de       8291    /tmp/sachse-11_Jul_2012_14_31_02-8291/    3.95',\
'1       clnode215.embl.de       8292    /tmp/sachse-11_Jul_2012_14_31_05-8292/    3.95']) #doctest: +NORMALIZE_WHITESPACE
        [del_info(rank_id='0', node='clnode215.embl.de', process_id='8291', 
        directory='/tmp/sachse-11_Jul_2012_14_31_02-8291/', space='3.95'), 
        del_info(rank_id='1', node='clnode215.embl.de', 
        process_id='8292', directory='/tmp/sachse-11_Jul_2012_14_31_05-8292/', space='3.95')]
        """
        del_i = self.get_deletion_info_named_tuple()
        
        browse = False
        cpu_count = None
        nodelist = []
        for each_line in logfile_lines:
            if cpu_count is not None:
                if browse:
                    nodelist.append(del_i._make(each_line.split()))
                    if len(nodelist) >= cpu_count:
                        browse = False
            if each_line.find('Number of CPUs') >= 0:
                cpu_count = int(each_line.split('=')[-1])
            if each_line.find('node_name') > 0:
                browse = True
        
        return nodelist
    

    def generate_deletion_info_from_start_end_node(self, start, end, nodes_prefix, tempdir, space, this_user=None):
        """
        >>> from spring.csinfrastr.csproductivity import Temporary
        >>> t = Temporary()
        >>> t.generate_deletion_info_from_start_end_node(1,4,'cl','/tmp', 3.98, 'me') #doctest: +NORMALIZE_WHITESPACE
        [del_info(rank_id=0, node='cl1', process_id=None, directory='/tmp/me*', space=3.98), 
        del_info(rank_id=1, node='cl2', process_id=None, directory='/tmp/me*', space=3.98), 
        del_info(rank_id=2, node='cl3', process_id=None, directory='/tmp/me*', space=3.98), 
        del_info(rank_id=3, node='cl4', process_id=None, directory='/tmp/me*', space=3.98)]
        """
        if this_user is None:
            this_user = getuser()
        del_i = self.get_deletion_info_named_tuple()
        nodelist = [del_i(each_node_index, '{0}{1}'.format(nodes_prefix, each_node_id), None, 
        self.generate_tempdir_from_user(tempdir, this_user), space) for each_node_index, each_node_id in \
        enumerate(list(range(start, end + 1)))] 
        
        return nodelist
    
    
class OpenMpiChecks(object):
    def check_dir(self, directory):
        """
        * Function to check existence of directory and rename if existent to \
        make room for next functions

        #. Input: arbitrary number of directories
        #. Output: 
        #. Usage: checkdir('this_directory')
        """
        if os.path.isdir(directory):
            from spring.csinfrastr.cslogger import Logger
            self.log = Logger()
            newdirectory = time.strftime(directory + time.strftime('_%d_%b_%Y_%H_%M_%S', 
                                            time.localtime( os.path.getctime(directory) )))
            os.rename(directory, newdirectory)
            self.log.ilog('{0} was renamed to {1} to make room for following program'.format(directory, newdirectory))
            directory = newdirectory 
        
        return directory


    def check_expected_output_file(self, program_to_be_launched, file_expected):
        if not os.path.isfile(file_expected):
            error_message = '{prg} did not finish successfully. The output '.format(prg=program_to_be_launched) + \
            'file {output} was not found, please check logfile of {prg} for details.'.format(output=file_expected, 
            prg=program_to_be_launched)
            raise IOError(error_message)
        

class OpenMpiLaunch(OpenMpiChecks):
    """
    Class that holds functions for OpenMpi usage
    """
    def get_nodes_from_pe_hostfile(self, hostfile):
        """
        >>> hostfile_str = 'node1.embl.de 3 R815.q@node1.embl.de UNDEFINED\\nnode2.embl.de 2 R815.q@node.embl.de UNDEFINED'
        >>> t = open('testhostfile.dat', 'w')
        >>> t.write(hostfile_str)
        >>> t.close()
        >>> from spring.csinfrastr.csproductivity import OpenMpi
        >>> OpenMpi().get_nodes_from_pe_hostfile('testhostfile.dat')
        ['node1.embl.de', 'node1.embl.de', 'node1.embl.de', 'node2.embl.de', 'node2.embl.de']
        >>> os.remove('testhostfile.dat')
        """
        file_lines = [n.split() for n in open(hostfile)]
        nodes = [each_line[0] for each_line in file_lines for each_cpu in list(range(int(each_line[1])))]

        return nodes


    def get_nodes_from_LSB_MCPU_HOSTS_variable(self, variable):
        """
        >>> variable = 'compute082 3 compute089 4 compute-n065 10'
        >>> from spring.csinfrastr.csproductivity import OpenMpi
        >>> OpenMpi().get_nodes_from_LSB_MCPU_HOSTS_variable(variable) #doctest: +NORMALIZE_WHITESPACE
        ['compute082', 'compute082', 'compute082', 'compute089', 'compute089', 
        'compute089', 'compute089', 'compute-n065', 'compute-n065', 
        'compute-n065', 'compute-n065', 'compute-n065', 'compute-n065', 
        'compute-n065', 'compute-n065', 'compute-n065', 'compute-n065'] 
        """
        vars = variable.split()
        nodes = [vars[2 * each_var] for each_var in range(len(vars)/2) for each_node in range(int(vars[2 * each_var + 1]))]
        
        return nodes


    def get_nodes_from_SLURM_by_running_srun_hostname(self):
        srun_process = subprocess.Popen('srun -l /bin/hostname', stdout=subprocess.PIPE, shell=True)
        stdout, log_stderr = srun_process.communicate()
        srun_process.wait()

        lines = [each_line for each_line in stdout.split('\n') if each_line != '']
        lines.sort()
        nodes = [each_line.split()[-1] for each_line in lines]
        
        return nodes


    def add_mpi_cmds(self, command_line_string, CPU_count):
        abspath_main = Support().search_path_like_which(command_line_string.split()[0])
        command_line_string = ' '.join([abspath_main] + command_line_string.split()[1:])
        abspath_mpirun = Support().search_path_like_which('mpirun')
        # SLURM support Oct-2014 tested by University of Auckland, NZ (Ambroise and Peter) 
        if os.getenv('SLURM_JOB_NODELIST'):
            preargs = 'srun --mpi=openmpi '
        elif os.getenv('PBS_NODEFILE') or os.getenv('PE_HOSTFILE') or \
        os.getenv('LSB_MCPU_HOSTS'):
            if os.getenv('PBS_NODEFILE'):
                nodes = [n.strip() for n in open(os.environ['PBS_NODEFILE'])]
            elif os.getenv('PE_HOSTFILE'):
                nodes = self.get_nodes_from_pe_hostfile(os.environ['PE_HOSTFILE'])
            elif os.getenv('LSB_MCPU_HOSTS'):
                nodes = self.get_nodes_from_LSB_MCPU_HOSTS_variable(os.environ['LSB_MCPU_HOSTS'])
#             elif os.getenv('SLURM_JOB_NODELIST'):
#                 nodes = self.get_nodes_from_SLURM_by_running_srun_hostname()
            nodefile_name = 'nodefile.dat'
            nodefile = open(nodefile_name, 'w')
            for each_node in nodes:
                nodefile.write('{0}\n'.format(each_node))
            nodefile.close()
            
            preargs = '{mpirun} -v --hostfile {nodefile} -np {nocpu} '.format(mpirun=abspath_mpirun, 
            nodefile=nodefile_name, nocpu=len(nodes))
        else:
            from multiprocessing import cpu_count
            if CPU_count > cpu_count():
                CPU_count = cpu_count()
            preargs = '{mpirun} -np {nocpu} '.format(mpirun=abspath_mpirun, nocpu=CPU_count)
        command_line_string = preargs + command_line_string
        
        return command_line_string


    def launch_command(self, command_line_string):
        from spring.csinfrastr.cslogger import Logger
        self.log = Logger()
        self.log.tlog(command_line_string)
        myenv = os.environ.copy()
        myenv['PYTHONPATH'] = ':'.join(sys.path) + ':' + os.environ['PYTHONPATH']
        subprocess.call(command_line_string.split(), env=myenv)
    
    
    def check_if_mpi_works_and_launch_command(self, command_line_string, cpu_count):
        try:
            import mpi4py
        except ImportError:
            warnstr = 'Mpi4py not installed, program proceeds with single CPU.'
            print('\nWARNING: ' + warnstr)
        else:
            command_line_string = self.add_mpi_cmds(command_line_string, cpu_count)
        
        self.launch_command(command_line_string)


    def launch_mpi_version_of_program(self, cpu_count, feature_set, parfile):
        progname_mpi = feature_set.progname + '_mpi'
        abspath_logfile = feature_set.logfile 
        
        command_line_string = '{prg} --f {parfile} --d {directory} --l {logfile}'.format(prg = progname_mpi, 
        parfile=parfile, directory=os.path.curdir, logfile=abspath_logfile)

        self.check_if_mpi_works_and_launch_command(command_line_string, cpu_count)
        os.remove(parfile)


    def setup_and_start_mpi_version_if_demanded(self, mpi_option, feature_set, cpu_count, exiting=True):
        from spring.csinfrastr.csfeatures import Features
        if mpi_option is True:
            external_mpi_run = OpenMpi()
            parfile = Features().write_parfile(feature_set.parameters)
            external_mpi_run.launch_mpi_version_of_program(cpu_count, feature_set, parfile)
            
            cleanup_script = 'cleanup.py'
            if os.path.isfile(cleanup_script):
                abs_python = Support().search_path_like_which('python')
                command_line_string = '{0} {1} {2}'.format('springenv', abs_python, cleanup_script)
                external_mpi_run.check_if_mpi_works_and_launch_command(command_line_string, cpu_count)
                os.remove(cleanup_script)
                
            if exiting:
                sys.exit()


class OpenMpiPythonObjects(OpenMpiLaunch):
    def split_sequence_evenly(self, seq, size):
        """
        >>> from spring.csinfrastr.csproductivity import OpenMpi
        >>> OpenMpi().split_sequence_evenly(list(range(9)), 4)
        [[0, 1], [2, 3, 4], [5, 6], [7, 8]]
        >>> OpenMpi().split_sequence_evenly(list(range(18)), 4)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12, 13], [14, 15, 16, 17]]
        """
        newseq = []
        splitsize = 1.0/size*len(seq)
        for i in range(size):
            newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
        return newseq
    
    
    def merge_sequence_of_sequences(self, seq):
        """
        >>> from spring.csinfrastr.csproductivity import OpenMpi
        >>> OpenMpi().merge_sequence_of_sequences([list(range(9)), list(range(3))])
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 0, 1, 2]
        >>> OpenMpi().merge_sequence_of_sequences([list(range(9)), [], list(range(3))])
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 0, 1, 2]
        """
        newseq = [number for sequence in seq for number in sequence]
        
        return newseq
    
    
    def gather_named_tuples_of_naparrays_from_cpus_to_common_named_tuple(self, comm, named_tuple):
        new_tuple = []
        for each_tuple in list(named_tuple):
            gathered_tuples = comm.gather(each_tuple, root=0) 
            if comm.rank == 0:
                new_tuple.append(np.array(self.merge_sequence_of_sequences(gathered_tuples)))
        if comm.rank == 0:
            gathered_named_tuple = named_tuple._make(new_tuple)
        else:
            gathered_named_tuple = None
        
        return gathered_named_tuple
        
        
    def convert_list_of_namedtuples_to_list_of_lists(self, list_of_namedtuples):
        """
        >>> from collections import namedtuple
        >>> helix_items = 'micrograph segment_list directory coordinates'
        >>> helix_info = namedtuple('helixinfo', helix_items)
        >>> to_convert = [helix_info(1*i, 2*i, 3*i, 4*i) for i in range(5)]
        >>> from spring.segment2d.segment_mpi import SegmentMpi
        >>> OpenMpi().convert_list_of_namedtuples_to_list_of_lists(to_convert)
        [[0, 0, 0, 0], [1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12], [4, 8, 12, 16]]
        >>> OpenMpi().convert_list_of_namedtuples_to_list_of_lists([helix_info(1*i, 2*i, 3*i, 4*i)])
        [[4, 8, 12, 16]]
        """
        list_of_lists = [ list(each_namedtuple) for each_namedtuple in list_of_namedtuples ]
        
        return list_of_lists


    def convert_list_of_lists_to_list_of_provided_namedtuple(self, list_of_lists, named_tuple):
        """
        >>> from collections import namedtuple
        >>> helix_items = 'micrograph segment_list directory coordinates'
        >>> helix_info = namedtuple('helixinfo', helix_items)
        >>> l = [[0, 0, 0, 0], [1, 2, 3, 4], [2, 4, 6, 8], [3, 6, 9, 12], [4, 8, 12, 16]]
        >>> o = OpenMpi()
        >>> o.convert_list_of_lists_to_list_of_provided_namedtuple(l, helix_info) #doctest: +NORMALIZE_WHITESPACE
        [helixinfo(micrograph=0, segment_list=0, directory=0, coordinates=0), 
        helixinfo(micrograph=1, segment_list=2, directory=3, coordinates=4), 
        helixinfo(micrograph=2, segment_list=4, directory=6, coordinates=8), 
        helixinfo(micrograph=3, segment_list=6, directory=9, coordinates=12), 
        helixinfo(micrograph=4, segment_list=8, directory=12, coordinates=16)]
        """
        list_of_namedtuples = [ named_tuple._make(each_list) for each_list in list_of_lists ]
        
        return list_of_namedtuples
    

class OpenMpiEMData(OpenMpiPythonObjects):
    def gather_stacks_from_cpus_to_common_stack(self, comm, local_stack, common_stack):
        """
        * Function to merge stacks from local disks to a single common stack
        """
        distributed_stacks = comm.gather(local_stack, root=0)
        distributed_stacks = comm.bcast(distributed_stacks, root=0)
        
        if comm.rank == 0:
            if os.path.isfile(common_stack):
                os.remove(common_stack)
            
        temp = EMData()
        for each_cpu, stack_of_each_cpu in enumerate(distributed_stacks):
            comm.barrier()
            if each_cpu == comm.rank and stack_of_each_cpu is not None:
                if os.path.isfile(stack_of_each_cpu):
                    local_stack_image_count = EMUtil.get_image_count(stack_of_each_cpu)
                    for each_local_image_index in range(local_stack_image_count):
                        temp.read_image(stack_of_each_cpu, each_local_image_index)
                        temp.append_image(common_stack)
                    os.remove(stack_of_each_cpu)
        
        return common_stack
    
    
    def transfer_series_of_images_from_cpus_to_common_disk(self, comm, local_images):
        """
        * Function to relocate series of local images/volumes to a common space in working directory
        """
        temp = EMData()
        images_in_common_dir = []
        for each_cpu in list(range(comm.size)):
            comm.barrier()
            for each_local_image in local_images:
                if each_cpu == comm.rank and os.path.isfile(each_local_image):
                    local_image_count = EMUtil.get_image_count(each_local_image)
                    image_in_common_directory = os.path.abspath(os.path.basename(each_local_image))
                    for each_local_image_index in range(local_image_count):
                        temp.read_image(each_local_image, each_local_image_index)
                        temp.write_image(image_in_common_directory, each_local_image_index)
                        images_in_common_dir.append(image_in_common_directory)
                        os.remove(each_local_image)
        
        comm.barrier()
        
        return images_in_common_dir
                
        
    def write_out_emdata_from_distributed_nodes_to_common_disk(self, comm, fftvol, file_name):
        """
        * Function to write out local images/volumes to a common space with node id in file suffix
        """
        accessible_local_emdata = os.path.splitext(file_name)
        
        emdata_file_name = '{prefix}{rank:03}{ext}'.format(prefix=accessible_local_emdata[0], rank=comm.rank,
        ext=accessible_local_emdata[-1])
        
        for each_cpu in list(range(comm.size)):
            comm.barrier()
            if each_cpu == comm.rank:
                fftvol.write_image(emdata_file_name)
        emdata_files = comm.gather(emdata_file_name, root=0)
        
        return emdata_files
    

    def reduce_emdata_on_main_node(self, emdata, distributed_emdata_files, read_first=False):
        temp = EMData()
        for each_index, each_file in enumerate(distributed_emdata_files):
            if not read_first and each_index == 0:
                pass
            else:
                if each_file is not None:
                    temp.read_image(each_file)
                    emdata += temp
            if each_file is not None:
                os.remove(each_file)
        
        emdata /= len(distributed_emdata_files)
        
        return emdata
    

class OpenMpi(OpenMpiEMData):
    def start_main_mpi(self, parset):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        
        if rank == 0:
            # Option handling
            from spring.csinfrastr.csreadinput import OptHandler
            mergeparset = OptHandler(parset)
            parameters = mergeparset.parameters
            current_directory = os.path.abspath(os.path.curdir)
            logfile = mergeparset.logfile
            package = mergeparset.package
            progname = mergeparset.progname
            version = mergeparset.version
        else:
            parameters = None
            current_directory = None
            logfile = None
            package = None
            progname = None
            version = None
            
        parameters = comm.bcast(parameters, root=0)
        logfile = comm.bcast(logfile, root=0)
        package = comm.bcast(package, root=0)
        progname = comm.bcast(progname, root=0)
        version = comm.bcast(version, root=0)
        current_directory = comm.bcast(current_directory, root=0)
        if rank != 0:
            os.chdir(current_directory)
            
        from spring.csinfrastr.csfeatures import Features
        reduced_parset = Features().reduce_features_to_parameters_for_mpi(parameters)
        reduced_parset.logfile = logfile
        reduced_parset.package = package
        reduced_parset.progname = progname
        reduced_parset.version = version
        
        return reduced_parset
    

    def write_out_tempdir_record_and_cleanup_script(self, tempdir_str):
        
        cleanup_script = 'cleanup.py'
        cscript = open(cleanup_script, 'w')
        cscript.write('\'\'\'{0}\'\'\''.format(tempdir_str))
        cleanup_code = """
import sys
from mpi4py import MPI 
from spring.csinfrastr.csproductivity import Temporary
from tabulate import tabulate

comm = MPI.COMM_WORLD
rank = comm.rank

for each_lid, each_line in enumerate(__doc__.split('\\n')):
    rank_rec, host, pid, tempdir, space = each_line.split()
    if rank == int(rank_rec):
        Temporary().remove_dir_and_everything_inside(tempdir)
        temp_msg = [rank, host, pid, tempdir]
        
comm.barrier()
temp_msg = comm.gather(temp_msg, root = 0)

if rank == 0:
    header = ['rank', 'host', 'process_id', 'temporary directory']
    tab_msg = tabulate(temp_msg, header)
    msg = '\\nThe following temporary directories were cleared and removed:\\n{0}'.format(tab_msg)
    sys.stderr.write(msg)
    """
        cscript.write(cleanup_code)
        cscript.close()
        
        return cleanup_script
    

    def split_message_string_into_chunks_of_xx(self, msg, chunk_size=200):
        mmsg = [msg[i:i + chunk_size] for i in list(range(0, len(msg), chunk_size))]

        return mmsg


    def setup_mpi_abort_upon_exception_on_any_node(self, comm, tempdir_str):
        comm.Set_errhandler(MPI.ERRORS_ARE_FATAL)
        _excepthook = sys.excepthook 

        def excepthook(t,v,tb): 
            _excepthook(t,v,tb) 
            if not MPI.Is_finalized() and MPI.Is_initialized(): 
                err_msg = Temporary().check_available_space_in_curdir_and_add_to_error_if_not_enough_space_available()

                err_msg += '\nRank {0} on machine {1} with process ID {2} '.format(comm.rank, os.uname()[1], os.getpid())+\
                'raised an error message. Find the corresponding error message above. All other MPI processes are ' + \
                'aborted. Ignore the error messages thereafter as they can arise as a result of the aborting '+ \
                'procedure.\n'
                if tempdir_str is not None:
                    self.write_out_tempdir_record_and_cleanup_script(tempdir_str)
                    
                mmsg = self.split_message_string_into_chunks_of_xx(err_msg)
                sys.stderr.writelines(mmsg)
                MPI.COMM_WORLD.Abort(1) 
        sys.excepthook = excepthook 
        
        return comm
    

    def setup_interrupt(self, tempdir_str, size):
        abs_mpirun = Support().search_path_like_which('mpirun')
        abs_python = Support().search_path_like_which('python')
        nodefile_name = os.path.join(os.path.split(os.path.abspath(os.curdir))[-1], 'nodefile.dat')
        cleanup_script = os.path.join(os.path.split(os.path.abspath(os.curdir))[-1], 'cleanup.py')

        def interrupt_handler(signal, frame):
            if not MPI.Is_finalized() and MPI.Is_initialized(): 
                if tempdir_str is not None:
                    self.write_out_tempdir_record_and_cleanup_script(tempdir_str)
                    msg = '\n{0} was terminated. All files are kept. '.format(os.path.basename(sys.argv[0])) + \
                    'Please remember to clean up the temporary directories of this run on the respective nodes. ' + \
                    'For this purpose a cleanup script has been prepared - simply run:\n'

                    msg += '\'{0} -np {1} '.format(abs_mpirun, size)
                    if os.getenv('PBS_NODEFILE') or os.getenv('PE_HOSTFILE') or \
                    os.getenv('LSB_MCPU_HOSTS') or os.getenv('SLURM_JOB_NODELIST'):
                        msg +='--hostfile {0} '.format(nodefile_name)

                    msg += 'springenv {0} {1}\' in the current directory.\n'.format(abs_python, cleanup_script)

                    msg += '\nThe following temporary directories are affected:\n{0}\n'.format(tempdir_str)
                    mmsg = self.split_message_string_into_chunks_of_xx(msg)
                    sys.stderr.writelines(mmsg)
                MPI.COMM_WORLD.Abort(1) 
        
        signal.signal(signal.SIGINT, interrupt_handler)
        

    def get_node_names_and_broadcast_to_each_node(self, comm):
        this_node = os.uname()[1]
        nodes = comm.gather(this_node, root=0)
        nodes = comm.bcast(nodes, root=0)

        return nodes, this_node


    def get_job_current_count_on_this_node(self, comm):
        nodes, this_node = self.get_node_names_and_broadcast_to_each_node(comm)
        job_count_on_this_node = len([True for each_node in nodes if each_node == this_node])
        
        unique_nodes = list(set(nodes))
        
        return job_count_on_this_node, this_node, unique_nodes
        

    def get_first_local_tempdir(self, comm, tempdir):
        nodes, this_node = self.get_node_names_and_broadcast_to_each_node(comm)

        nodes = np.array(nodes)
        tempdirs = comm.gather(tempdir, root=0)
        tempdirs = np.array(comm.bcast(tempdirs, root=0))
        first_local_tempdir = tempdirs[nodes == this_node][0]

        return first_local_tempdir


    def make_tempdir_and_log_including_node_name(self, log, temppath, comm, rank, size, byte_size=None):
        if temppath is not None:
            from spring.csinfrastr.cslogger import Logger
            self.log = Logger()

            this_node = os.uname()[1]
            if byte_size is None:
                byte_size = 1024 ** 3
                
            for each_rank in list(range(size)):
                if each_rank == rank:
                    tempdir, err_msg = Temporary().mkdir_temporary_directory(temppath, byte_size)
                comm.barrier()
                
            first_local_tempdir = self.get_first_local_tempdir(comm, tempdir)
            if not first_local_tempdir.startswith(tempdir):
                byte_size = Support().compute_byte_size_of_image_stack(512, 512, 1000)
                
            temp_info = [rank, this_node, os.getpid(), tempdir, DiskSpace().humanize_bytes(byte_size)]

            tempdir_record = comm.gather(temp_info, root = 0)
            
            if rank == 0:
                log_str = 'The following temporary directories were made:\n'
                log_tab_str = tabulate(tempdir_record, ['rank_id', 'node_name', 'process_id', 'directory', 'space_required'])
                self.log.ilog(log_str + log_tab_str)
                tempdir_str = '\n'.join(log_tab_str.split('\n')[2:])
            else:
                tempdir_str = None
            tempdir_str = comm.bcast(tempdir_str, root=0)
        else:
            tempdir = None

        return tempdir, tempdir_str, err_msg


    def setup_mpi_and_simultaneous_logging(self, log, logfile_name, temppath, byte_size=None):
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
        
        if rank != 0:
            log.__init__()
            log.set_logfile(logfile_name)
        
        comm.barrier()
        
        tempdir, tempdir_record, err_msg = self.make_tempdir_and_log_including_node_name(log, temppath, comm, rank,
        size, byte_size)
        
        if rank == 0:
            self.setup_interrupt(tempdir_record, size)
        
        comm.barrier()

        comm = self.setup_mpi_abort_upon_exception_on_any_node(comm, tempdir_record)
        if err_msg is not None:
            raise ValueError(err_msg)
        
        return comm, rank, size, log, tempdir
        
        
class TestingDirectory():
    def __init__(self, progname=None):
        if progname is None:
            self.testdir='testing'
        else:
            if progname.startswith('test'):
                self.testdir = progname
            else:
                self.testdir='testing_{0}'.format(progname)

    def create(self):
        os.mkdir(self.testdir)
        os.chdir(self.testdir)

    def remove(self):
        os.chdir(os.pardir)
        files_to_be_removed = os.listdir(self.testdir)
        [os.remove(os.path.join(self.testdir, each_file)) for each_file in files_to_be_removed]
        shutil.rmtree(self.testdir)
        
