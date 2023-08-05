#!/usr/bin/env python
# Author: Carsten Sachse 21-Sep-2010
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details

from collections import OrderedDict
from getpass import getuser
from spring.csinfrastr.csproductivity import Errors
import logging
import os
import re
import readline
import socket
import sys
import time
import urllib2


class GetMetaData:
    """
    * Class to get metadata from PKG-INFO egg
    """
    def __init__(self, package):
        self.package = package
        self.read_pkginfo()
        self.add_fields()


    def read_pkginfo(self):
        import pkg_resources
        dist = pkg_resources.get_distribution(self.package)
        pkginfo = dist.get_metadata('PKG-INFO')
        self.metadata = OrderedDict()
        for line in pkginfo.split('\n'):
            if ':' in line:
                if 'Classifier' in line:
                    lsplit = line.split(':')
                    k, v = ':'.join(lsplit[:2]), ''.join(lsplit[2:])
                else:
                    lsplit= line.split(':')
                    k, v = lsplit[-2], lsplit[-1]
                last_key = k.strip()
                last_value = v.strip()
                self.metadata[last_key]=last_value


    def add_fields(self):
        # additional entries
        self.metadata['Package'] = self.package
        self.metadata['Maintainer'] = self.metadata['Author']
        self.metadata['Copyright'] = '2010 - %s, EMBL' %time.localtime()[0]


    def release_meta(self):
        return self.metadata


class ParameterFilter(Errors):
    """
    * Class that filters whether specified values are within specified range, and 
    checks whether files exist
    """
    def __init__(self, parset=None):
        if parset is not None:
            self.feature_set = parset
            self.parameters = parset.parameters
            self.default_params = parset.default_params
            self.level = parset.level
            self.properties = parset.properties
            self.relatives = parset.relatives

            self.check_input_parameters_values_and_files()
            

    def check_input_parameters_values_and_files(self):
        from spring.csinfrastr.csfeatures import Features
        self.completion_required = False
        for self.name in self.parameters:
            if type(self.parameters[self.name]) in [int, float]:
                self.check_valerr(self.parameters[self.name])
            elif type(self.parameters[self.name]) is tuple:
                self.check_valerr(self.parameters[self.name][0])
                self.check_valerr(self.parameters[self.name][1])
            elif type(self.parameters[self.name]) is str:
                if self.properties[self.name].__str__().startswith('file'):
                    filelist = Features().convert_list_of_files_from_entry_string(self.parameters[self.name])
                    self.check_fileexistence_and_fileformat(filelist)
            elif self.parameters[self.name] is None and self.level[self.name] in ['beginner']:
                error_message = 'Value for \'{0}\' was not entered or received correctly. '.format(self.name) + \
                'This is an essential parameter. Please enter a value for \'{0}\' and start again.'.format(self.name)
                raise ValueError(error_message)
            elif self.parameters[self.name] is None and not self.level[self.name] in ['beginner']:
                self.completion_required = True
                self.parameters[self.name] = self.default_params[self.name]
                

    def check_fileexistence_and_fileformat(self, filelist):
        for file in filelist:
            if self.properties[self.name].ftype in ['getFile', 'getFiles', 'saveFile']:
                self.check_fileformat(file)
                if self.properties[self.name].ftype not in ['saveFile']:
                    self.check_filerr(file)
            elif self.properties[self.name].ftype in ['getDir']:
                self.check_filerr(file)
                

class MultiCaster(object):
    def __init__(self, filelist):
        self.filelist = filelist

    def write(self, str):
        for f in self.filelist:
            f.write(str)
            

    def writelines(self, str):
        for f in self.filelist:
            f.writelines(str)
            

    def flush(self):
        for f in self.filelist:
            f.flush()


class NameGenerator(object):
    def make_directory(self, program):
        directory_name = '%s_' %(program.split('.')[0]) + time.strftime('%d_%b_%Y_%H_%M_%S') + \
        '_' + '%d' %os.getpid()
        
        return directory_name
    

    def make_logfile(self, program):
        directory_name = self.make_directory(program)
        logfile = directory_name + os.extsep + 'log'
        
        return logfile
        

class Logger(ParameterFilter):
    """
    * Logger class to intitialize logfile and logging information
    """
    def __init__(self):
#        import logging
        self.log = logging.getLogger(getuser())
        
        self.start_time = time.time()
    

    def log_individual_parameters(self, parameters, to_be_printed=False):
        for name in parameters:
            parinfo = '%-40s = %s' % (name, parameters[name])
            self.log.info('{0}'.format(parinfo))
            if to_be_printed:
                print parinfo


    def startlog(self, parset, debug=True):
        """
        * Function to initiate logfile with time and name of program, adds input to header
        """
        self.debug = debug

        self.feature_set = parset
        self.parameters = parset.parameters
        self.properties = parset.properties
        self.relatives = parset.relatives
        self.progname = parset.progname
        self.version = parset.eggmeta['Version']
        self.package = parset.eggmeta['Name'].title()
        self.devstate = parset.eggmeta['Classifier: Development Status']

        options = self.feature_set.parser.parse_args()

        if options.logfilename is None:
            logfile = 'report.log'#NameGenerator().make_logfile(self.progname)
        else:
            logfile = options.logfilename
            
        lgfile=open(logfile,'a')
        mc = MultiCaster([sys.stderr, lgfile])
        sys.stderr = mc

        if self.debug is True or self.devstate.strip()[0] in ['1', '2', '3', '4']:
            logging.basicConfig(level=logging.DEBUG, filename=logfile, filemode='a')
        else:
            logging.basicConfig(level=logging.INFO, filename=logfile, filemode='a')

        self.log.info('\n'+ '#'*100 + '\n' + ' '*5 + 'Beginning of the program ' + self.progname + \
                      ' (' + self.package + ' v' + self.version +')' + ': ' + \
                      time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())+ '\n' + '#'*100)
        self.log.info('\n' + '#'*44 + ' INPUT ' +'#'*44)

        self.fcttolog()
        receive_statement = 'The following input parameters have been received:'
        print(receive_statement)
        self.log.info(receive_statement)
        self.log_individual_parameters(self.parameters, to_be_printed=True)
        super(Logger, self).__init__(self.feature_set)
        
        if self.completion_required:
            self.log.info('\n' + '-'*100 + '\nThe final set of parameters has been completed with the provided ' + \
                          'default parameters:')
            self.log_individual_parameters(self.parameters)
        self.log.info('\n' + '#'*44 + ' START ' +'#'*44)
        self.plog(1)

        return logfile


    def set_logfile(self, logfile):
        self.log = logging.basicConfig(level=logging.INFO, filename=logfile, filemode='a')


    def fcttolog(self):
        """
        * Function to switch logger idendity to the function calling
        """
        import inspect
        caller = inspect.getouterframes(inspect.currentframe())[1][3]
        try:
            from mpi4py import MPI
            comm = MPI.COMM_WORLD
            caller = 'CPU{0}:{1}'.format(comm.Get_rank(), caller)
        except:
            pass
            
        self.log = logging.getLogger(caller)
        self.log.info('\n')


    def ilog(self, msg):
        """
        * Function to add info message for log
        """
        self.log.info(msg)


    def in_progress_log(self):
        """
        * Function to add 'in progress' message and time
        """
        self.tlog('\t\tin progress ...')
        

    def plog(self, percent):
        """
        * Function to add 'progress state' message for progress bar
        """
        self.log.info('progress state: {0} %  [{1:41}]'.format(int(percent), '=' * int(percent / 2.5) + '>'))
        

    def tlog(self, msg):
        """
        * Function to add info message to log including an additional time statement
        """
        self.log.info('{0}\n\tlogged on {1}'.format(msg, time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())))
        

    def dlog(self, msg):
        """
        * Function to add debug message for log
        """
        self.log.debug(msg)


    def wlog(self, msg):
        """
        * Function to add error message for log
        """
        self.log.warning(msg)


    def errlog(self, msg):
        """
        * Function to add error message for log
        """
        self.log.error(msg)


    def check_for_latest_version(self, feature_set):
        version_check = urllib2.urlopen('http://www.google-analytics.com/collect' + \
        '?v=1&tid=UA-46010145-1&cid=123&t=event&ec=Version%20Check&ea=Endlog&el={0}'.format(getuser()), timeout=1).close
        
        version_file = urllib2.urlopen("http://www.sachse.embl.de/emspring/_static/version.txt", timeout=1)
        latest_version = [version_file.read()]
        
        running_version = feature_set.version
        if running_version in latest_version and len(latest_version[0]) < 20:
            pass
        else:
            update_msg = 'Warning: Please update your {0}{1} package '.format(feature_set.package, running_version) + \
                          'as there is a new version {0} for download available '.format(latest_version[0]) + \
                          'from www.sachse.embl.de/emspring/install.html'
            print update_msg
            self.log.warning(update_msg)


    def endlog(self, feature_set):
        """
        * Function to finish log with time and name of program
        """
        if sys.argv[0].endswith(feature_set.progname):
            try:
                self.check_for_latest_version(feature_set)
            except urllib2.URLError or socket.timeout:
                pass
        elif sys.argv[0].endswith('nosetests'):
            pass
        
        total_time = time.time() - self.start_time
        self.fcttolog()
        self.plog(100)
        self.log.info('\n' + '#'*100) 
        cpu_time = time.gmtime(total_time)
        self.log.info('\n' + ' '*20 + 'Elapsed CPU time: ' + \
        '{0} d {1:02}:{2:02}:{3:02}'.format(cpu_time.tm_mday - 1, cpu_time.tm_hour, cpu_time.tm_min, cpu_time.tm_sec))
        
        self.log.info('\n' + '#'*100 + '\n' + ' '*20 + 'End of program ' + '%s: ' %feature_set.progname + \
                      time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime())+ '\n' + '#'*100)


class FileCompleter(object):
    def _listdir(self, root):
        "List directory 'root' appending the path separator to subdirs."
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res


    def _complete_path(self, path=None):
        "Perform completion of filesystem path."
        if not path:
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
                for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']


    def complete_file(self, args):
        "Completions for the 'extra' command."
        if not args:
            return self._complete_path(path=None)
        # treat the last arg as a path and complete it
        return self._complete_path(args[-1])


    def complete(self, text, state):
        "Generic readline completion entry point."
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        args = line

        return (self.complete_file(args) + [None])[state]


class InputCompleter(object):
    """
    http://stackoverflow.com/questions/5637124/tab-completion-in-pythons-raw-input
    """
    def __init__(self, words):
        self.words = words
        self.re_space = re.compile('.*\s+$', re.M)

    def complete(self, text, state):
        "Generic readline completion entry point."
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        # show all words
        if not line:
            return [c + ' ' for c in self.words][state]
        # account for last argument ending in a space
        if self.re_space.match(buffer):
            line.append('')
        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in self.words:
            impl = getattr(self, 'complete_%s' % cmd)
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + ' '][state]
        results = [c + ' ' for c in self.words if c.startswith(cmd)] + [None]
        return results[state]

    