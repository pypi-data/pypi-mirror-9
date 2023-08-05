# Author: Carsten Sachse 21-Sep-2010
# Copyright: EMBL (2010 - 2015)
# License: see license.txt for details
"""
* Several classes to read input parameters from user: DefaultInput, PromptUser, ReadInputFile, ReadCommandLine \
(adapted from Hans-Peter Langtangen 'A Primer on Scientific Programming with Python')
"""
from glob import glob
from spring.csinfrastr.csfeatures import Features
from spring.csinfrastr.cslogger import Logger, FileCompleter, InputCompleter
from spring.csinfrastr.csproductivity import Errors
import os
import readline
import sys

class CommandLineOptions:
    """
    * Class that defines common command line options
    """
    def define_options(self, progname, package, version_num, infile, outfile, proginfo):
        from argparse import ArgumentParser, SUPPRESS
        parser = ArgumentParser(prog=progname, description=proginfo) 

        parser.add_argument('input_output', nargs='*',
            help='Input and output files')
        parser.add_argument('--g', '--GUI', action='store_true', default=False, 
            help='GUI option: read input parameters from GUI', )
        parser.add_argument('--p', '--promptuser', action='store_true', default=False,
            help='Prompt user option: read input parameters from prompt', )
        parser.add_argument('--f', '--parameterfile', dest='filename',  
            help='File option: read input parameters from FILENAME')
        parser.add_argument('--c', '--cmd', action='store_true', default=False,
            help='Command line parameter option: read input parameters from command line and default input ' + \
            'dictionary in program', )
        parser.add_argument('--l', '--logfile', dest='logfilename', 
            help='Output logfile name as specified') 
        parser.add_argument('--d', '--directory', dest='directory_name', 
            help='Output directory name as specified') 

        #Print rst: to generate localized rst file for sphinx documentation
        parser.add_argument('--print_rst', action='store_true', help=SUPPRESS )
        
        parser.add_argument('--version', action='version', version='{0} from package {1}-{2}'.format(progname,
        package.title(), version_num))
        
        return parser

    def add_cmdline_options_from_parameter_dictionary(self):
        """
        * Function to add parameter-defined options to become command line options
        """
        parameters = [each_key for each_key in self.levels if self.levels[each_key] in ['beginner', 'intermediate', 'expert']]
        for name in parameters:
            help_string = self.hints[name] + ' (default: %(default)s)'
            if type(self.parameters[name]) is bool:
                try:
                    self.feature_set.parser.add_argument('--{0}'.format('_'.join(name.split()).lower()), 
                    '--{0}'.format(name[0:3].lower()), action='store_true', default=False, help=help_string)
                except:
                    self.feature_set.parser.add_argument('--{0}'.format('_'.join(name.lower().split())), 
                    action='store_true', default=False, help=help_string)
            elif type(self.parameters[name]) is not bool:
                try:
                    self.feature_set.parser.add_argument('--{0}'.format('_'.join(name.split()).lower()), 
                    '--{0}'.format(name[0:3].lower()), dest='{0}'.format(name), 
                    default=self.parameters[name], type=type(self.parameters[name]), help=help_string)
                except:
                    self.feature_set.parser.add_argument('--{0}'.format('_'.join(name.lower().split())),
                    dest='{0}'.format(name), default=self.parameters[name], type=type(self.parameters[name]),
                    help=help_string)

    def override_cmdlineopts(self):
        # override boolean parameters from command line
        for name in self.parameters:
            if type(self.parameters[name]) is bool:
                if self.options.__dict__['_'.join(name.split()).lower()] is True:
                    self.parameters[name] = True
                else:
                    self.parameters[name] = False

        
class OptHandler(Features, CommandLineOptions):
    """
    * Class to handle the standard options of all cspackages

    #. Input: parser (contains all information about program options, parameter \
    dictionary, help dictionary, range dictionary)
    """

    def __init__(self, parset):
        self.feature_set = parset
        self.feature_set.default_params = parset.parameters.copy()

        self.parameters = parset.parameters
        self.levels = parset.level
        self.hints = parset.hints
        self.properties = parset.properties
        self.program_states = parset.program_states
        self.proginfo = parset.proginfo
        self.progname = parset.progname
        self.package = self.feature_set.eggmeta['Package']
        self.version = self.feature_set.eggmeta['Version']

        self.feature_set.parser = self.define_options(self.progname, self.feature_set.eggmeta['Package'], 
                                              self.feature_set.eggmeta['Version'], list(self.parameters.values())[0], 
                                              list(self.parameters.values())[1], parset.proginfo)
        self.add_cmdline_options_from_parameter_dictionary()

        self.evaluate_given_cmdline_option()
        self.make_and_change_to_new_working_directory()
        self.logfile = Logger().startlog(self.feature_set, debug=True)

    def evaluate_given_cmdline_option(self):
        """
        * Function to evaluate command line options and feed parameters in \
        program via chosen route 
        """
        self.options = self.feature_set.parser.parse_args()
        args = self.options.input_output

        if self.options.print_rst is True:
            from .csdocu import RecordRst
            RecordRst(self.feature_set)
        ######### Option handling
        # option 1: Command line
        if len(args) == 2:
            inp = ReadCommandLine(self.feature_set)
            self.options.c = True

        # option 2: read p from file
        if self.options.c is True:
            inp = DefaultInput(self.feature_set)
            self.override_cmdlineopts()
        elif self.options.filename is not None:
            self.feature_set.filename = self.options.filename
            inp = ReadInputFile(self.feature_set)
        # option 3: get p from prompt
        elif self.options.p is True: 
            inp = PromptUser(self.feature_set)
        # option 4: get p from GUI
        elif self.options.g is True: 
            self.startGui()
        else:
            self.feature_set.parser.print_help()
            sys.exit()

        self.feature_set.parameters = inp.parameters


    def make_and_change_to_new_working_directory(self):
        """
        * Function to make new working directory
        """
        from spring.csinfrastr.cslogger import NameGenerator
        
        self.change_filenames_to_absolute_paths()
                    
        if self.options.directory_name is None:
            new_directory_name = NameGenerator().make_directory(self.feature_set.progname)
        else:
            new_directory_name = self.options.directory_name
            
        if new_directory_name != os.path.curdir:
            try:
                os.mkdir(new_directory_name)
            except:
                error_message = 'Specified directory exists and cannot be overwritten. Please use different one.'
                raise IOError(error_message)
        
            os.chdir(new_directory_name)

    def change_filenames_to_absolute_paths(self):
        for self.name in self.parameters:
            if type(self.parameters[self.name]) is str:
                if self.properties[self.name].__str__().startswith('file'):
                    if self.properties[self.name].ftype in ['getFile', 'getFiles', 'getDir']:
                        if self.name in self.feature_set.relatives and \
                            self.parameters[self.feature_set.relatives[self.name]] is False:
                            pass
                        else:
                            if os.path.abspath(self.parameters[self.name]) == os.path.abspath(os.curdir):
                                self.parameters[self.name]=os.path.abspath(os.curdir)
                            elif not self.parameters[self.name].startswith(os.sep):
                                self.parameters[self.name]=os.path.join(os.path.abspath(os.curdir),
                                self.parameters[self.name])
                    elif self.properties[self.name].ftype in ['saveFile']:
                        if self.parameters[self.name].startswith(os.sep):
                            self.parameters[self.name]=os.path.basename(self.parameters[self.name])

    def startGui(self):
        """
        * Function to launch GUI
        """
        from PyQt4.QtGui import QApplication
        from PyQt4.QtCore import SIGNAL, SLOT
        from spring.csinfrastr.csgui import GUI
        
        app = QApplication(sys.argv)
        app.connect(app, SIGNAL('lastWindowClosed()') , app , SLOT('quit()'))
        self.window = GUI(self.feature_set)
        self.window.show()
        sys.exit(app.exec_())

class DefaultInput:
    """
    * Class to use default input parameters from program

    #. Input = default paramter dictionary
    #. Output = default parameter dictionary
    """
    def __init__(self, parset):
        print(parset.proginfo)
        print('Default input paramters demanded')
        self.parameters = parset.parameters


class PromptUser(Errors):
    """
    * Class to receive input parameters from prompt
    if no input is given default parameters are taken

    #. Input = default paramter dictionary
    #. Output = updated parameter dictionary
    """
    def __init__(self, parset):
        self.feature_set = parset
        self.parameters = parset.parameters
        self.levels = parset.level
        self.hints = parset.hints
        self.properties = parset.properties
        self.relatives = parset.relatives
        print(parset.proginfo)
        print('Please enter the input parameters at the prompt (ENTER for default, ' + \
              'Hit Tab for suggestions and autocomplete):')
        
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        
        self.prompt_user()

    def check_numbers_and_boolean_input(self, entered):
        if type(self.parameters[self.name]) is tuple:
            super(PromptUser, self).check_valerr(eval(entered)[0])
            super(PromptUser, self).check_valerr(eval(entered)[1])
            if type(self.parameters[self.name][0]) is float:
                self.parameters[self.name]=(float(eval(entered)[0]), float(eval(entered)[1]))
            elif type(self.parameters[self.name][0]) is int:
                self.parameters[self.name]=(int(eval(entered)[0]), int(eval(entered)[1]))
            else:
                self.parameters[self.name] = eval(entered)
        elif type(self.parameters[self.name]) is float:
            super(PromptUser, self).check_valerr(entered)
            self.parameters[self.name] = float(entered)
        elif type(self.parameters[self.name]) is int:
            super(PromptUser, self).check_valerr(entered)
            self.parameters[self.name] = int(entered)
        elif type(self.parameters[self.name]) is bool:
            if str(entered).title() in ['True', 'Yes', 'Y']:
                self.parameters[self.name] = True
            elif str(entered).title() in ['False', 'No', 'N']:
                self.parameters[self.name] = False
            else:
                error_message = 'Input not understood: True/False or Yes/No.'
                sys.stderr.write(error_message)
                raise TypeError(error_message)

    def check_prompt_against_expected_strings(self, entered):
        if type(self.parameters[self.name]) is str:
            entered = entered.strip().strip('\n')
            if self.properties[self.name].__str__().startswith('file'):
                if entered.find(',') >= 0:
                    file_list = entered.split(',')
                elif entered.find('*') >= 0 or entered.find('?') >= 0:
                    file_list = glob(entered)
                    file_list.sort()
                    if file_list == []:
                        file_list = [entered]
                else:
                    file_list = [entered]

                for each_file in file_list:
                    if self.properties[self.name].ftype in ['getFile', 'getFiles', 'saveFile']:
                        super(PromptUser, self).check_fileformat(each_file)
                        if self.properties[self.name].ftype not in ['saveFile']:
                            super(PromptUser, self).check_filerr(each_file)
                    elif self.properties[self.name].ftype in ['getDir']:
                        super(PromptUser, self).check_filerr(each_file)
                
                self.parameters[self.name] = entered
            elif self.properties[self.name].__str__().startswith('choice'):
                if str(entered).lower() in self.properties[self.name].choices:
                    self.parameters[self.name] = str(entered).lower()
                else:
                    error_message = 'Input not understood: {0}.'.format(self.properties[self.name].choices.__str__())
                    sys.stderr.write(error_message)
                    raise TypeError(error_message)

    def setup_tab_autocompleter(self):
        if type(self.parameters[self.name]) is bool:
            self.comp = InputCompleter(['true', 'false', 'True', 'False'])
        elif type(self.parameters[self.name]) is str:
            if self.properties[self.name].__str__().startswith('choice'):
                self.comp = InputCompleter(self.properties[self.name].choices)
            elif self.properties[self.name].__str__().startswith('file'):
                if self.properties[self.name].ftype in ['getFile', 'getFiles', 'saveFile', 'getDir']:
                    self.comp = FileCompleter()
                    readline.set_completer(self.comp.complete)
                else:
                    self.comp = InputCompleter([str(self.parameters[self.name])])
        else:
            self.comp = InputCompleter([str(self.parameters[self.name])])
        readline.set_completer(self.comp.complete)
        entered = raw_input('Please enter {0}: {1}= \n>>> '.format(self.name, self.parameters[self.name]))
        entered = str(entered).strip()
        return entered

    def prompt_user(self):
        """
        * Function to prompt user on parameter input, performs parameter \
        checking based on type of input and checks whether entered values are \
        in expected range

        """
        parameters = [each_key for each_key in self.levels if self.levels[each_key] in ['beginner', 'intermediate', 'expert']]
        for self.name in parameters:
            while True:
                try:
                    if type(self.parameters[self.name]) is not tuple and self.relatives.has_key(self.name):
                        if self.parameters[self.relatives[self.name]] is False:
                            break
                    elif type(self.parameters[self.name]) is tuple and self.relatives.has_key(self.name):
                        if self.parameters[self.relatives[self.name][0]] is False and \
                        self.parameters[self.relatives[self.name][1]] is False:
                            break
                    print('\n' + self.hints[self.name])
                    entered = self.setup_tab_autocompleter()
                    if entered.lower() in ['quit', 'end', 'quit()', 'end()']:
                        raise EOFError
                    elif entered is not '':
                        self.check_numbers_and_boolean_input(entered)
                        self.check_prompt_against_expected_strings(entered)
                    else:
                        break
                    break
                except EOFError:
                    raise SystemExit('\n{0} terminated.'.format(self.feature_set.progname))
                except:
                    print ' Hit Tab to get suggestions and auto-complete.'
                    pass

        return self.parameters

class ReadInputFile:
    """
    Class to receive input parameters from an input file
    input = default parameter dictionary, filename
    output = updated parameter dictionary
    """
    def __init__(self, parset):
        self.parameters = parset.parameters
        self.properties = parset.properties
        print(parset.proginfo)
        print('Input parameters are read from {0}'.format(parset.filename))
        self.read_file(parset.filename)
    
    def clear_parameters(self, parameters):
        for name in parameters:
            parameters[name]=None
        
        return parameters
    
    def evaluate_value_type(self, value, teipp):
        try:
            teipp(value)
        except ValueError:
            error_message = ('\'{0}\' received \'{1}\'\nPlease enter {2} value from {3} to {4}'.format(self.name, value, 
                                        teipp, self.properties[self.name].minimum, self.properties[self.name].maximum))
            raise ValueError(error_message)


    def enter_received_value_if_it_is_tuple_of_numbers(self, received_value, type_of_value):
        if type_of_value is tuple:
            received_value = received_value.strip('(')
            received_value = received_value.strip(')')
            if ',' in received_value:
                valentries = received_value.split(',')
            if ';' in received_value:
                valentries = received_value.split(';')
            self.evaluate_value_type(valentries[0], float)
            self.evaluate_value_type(valentries[-1], float)
            if type(self.default_params[self.name][0]) is float:
                self.parameters[self.name]=(float(eval(received_value)[0]), float(eval(received_value)[1]))
            elif type(self.default_params[self.name][0]) is int:
                self.parameters[self.name]=(int(eval(received_value)[0]), int(eval(received_value)[1]))
            else:
                self.parameters[self.name] = eval(received_value)
            
        return received_value


    def enter_received_value_if_it_is_boolean_option(self, received_value, type_of_value):
        if type_of_value is bool:
            if received_value.strip() in ['True', 'Yes', 'Y', 'yes', 'y']:
                self.parameters[self.name] = True
            elif received_value.strip() in ['False', 'No', 'N', 'no', 'n']:
                self.parameters[self.name] = False

    def enter_received_value_if_it_is_number(self, received_value, type_of_value):
        if type_of_value is float:
            self.evaluate_value_type(received_value, float)
            self.parameters[self.name] = float(received_value)
        elif type_of_value is int:
            self.evaluate_value_type(received_value, float)
            self.parameters[self.name] = int(float(received_value))


    def enter_received_value_if_it_is_file_or_available_choice(self, received_value, type_of_value):
        if type_of_value is str:
            if self.properties[self.name].__str__().startswith('choice'):
                if received_value.lower() not in self.properties[self.name].choices:
                    error_message = 'Choice \'{0}\' not referenced in default parameter dictionary. Choose between {1}'\
                    .format(received_value, self.properties[self.name].choices.__str__())
                    raise ValueError(error_message)
                else:
                    self.parameters[self.name] = received_value.lower()
            else:
                self.parameters[self.name] = received_value


    def read_file(self, filename):
        infile = open( filename, 'r')  
         
        self.default_params = self.parameters.copy()
        self.parameters = self.clear_parameters(self.parameters)
        for line in infile:
            if '=' in line:
                name, received_value = line.split('=')
                self.name = name.strip()
                received_value = received_value.strip()
                if self.name in self.parameters:
                    if received_value == 'None':
                        pass
                    else:
                        type_of_value = type(self.default_params[self.name])
                        self.enter_received_value_if_it_is_tuple_of_numbers(received_value, type_of_value)
                        self.enter_received_value_if_it_is_number(received_value, type_of_value)
                        self.enter_received_value_if_it_is_boolean_option(received_value, type_of_value)
                        self.enter_received_value_if_it_is_file_or_available_choice(received_value, type_of_value)
                else:
                    print('Parameter \'{0}\' is of no use for the program because not '.format(self.name)) + \
                          'referenced in default parameter dictionary'
        
        return self.parameters

class ReadCommandLine:
    """
    * Class to receive input parameters from the command line

    #. Input = default parameter dictionary
    #. Output = updated parameter dictionary
    """
    def __init__(self, parset):
        self.parameters = parset.parameters
        self.parser = parset.parser
        options = self.parser.parse_args()
        self.args = options.input_output
        print(parset.proginfo)
        print('Input and output files detected from command line')
        self._read_command_line()

    def _read_command_line(self):
        self.parameters[list(self.parameters.keys())[0]] = self.args[0]
        self.parameters[list(self.parameters.keys())[1]] = self.args[1]
        return self.parameters

