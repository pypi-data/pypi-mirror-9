#!/usr/bin/env python
"""
Test module to check readibility of input
"""
from collections import OrderedDict
from glob import glob
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.csinfrastr.csreadinput import Features, ReadInputFile
from spring.micprgs.scansplit import ScanSplitPar
import os
import random
import subprocess
import sys


class EndToEndTest(object):
    def define_logfile_and_directory(self, program):
        directory = '{0}_test'.format(program)
        logfile = '{0}_test.log'.format(program)
        
        return logfile, directory
        
    def feed_in_parameter_values_at_prompt(self, feature_set):
        parameters = [each_key for each_key in feature_set.level \
                      if feature_set.level[each_key] in ['beginner', 'intermediate', 'expert']]
        script = ''
        for name in parameters:
            if type(feature_set.parameters[name]) is not tuple and feature_set.relatives.has_key(name):
                if feature_set.parameters[feature_set.relatives[name]] is False:
                    pass
                else:
                    script = script + """{0}\n""".format(feature_set.parameters[name])
            elif type(feature_set.parameters[name]) is tuple and feature_set.relatives.has_key(name):
                if feature_set.parameters[feature_set.relatives[name][0]] is False:
                    pass
                else:
                    script = script + """{0}\n""".format(feature_set.parameters[name])
            else:
                script = script + """{0}\n""".format(feature_set.parameters[name])
        
        return script

    def launch_program_at_prompt(self, program, logfile, directory, script):
        self.program_command = ['{0} --p --l {1} --d {2}'.format(program, logfile, directory)]
        try:
            process = subprocess.Popen(self.program_command, stdin=subprocess.PIPE, shell=True)
            process.communicate(input=script)
            process.wait()
        except OSError:
            pass

    def launch_program_to_read_inputfile(self, program, filename, logfile, directory):
        command_line = '{0} --f {1} --l {2} --d {3}'.format(program, filename, os.path.basename(logfile), directory)
        sys.stderr.write(command_line)
        try:
            subprocess.call(command_line.split())
        except OSError:
            pass

    def analyze_logfile(self, logfilename):
        logfile = open(logfilename, 'r')
        logfile_lines = logfile.readlines()
        logfile.close()

        logdict = OrderedDict()
        end_of_program_line_found = False
        for each_line in logfile_lines:
            if each_line.find('=') > 1:
                par = each_line.split('=')[0].split(':')[-1].strip()
                parval = each_line.split('=')[-1].strip()
                try:
                    logdict[par] 
                except:
                    logdict[par] = parval
            if each_line.find('End of program'):
                end_of_program_line_found = True
        
        assert end_of_program_line_found == True
        
        return logdict

    def check_logged_values_against_input(self, feature_set, logdict, prompt=True):
        for name in feature_set.parameters:
            sys.stderr.write('{0}={1}\n'.format(feature_set.parameters[name], logdict[name]))
            if type(feature_set.parameters[name]) is not tuple and feature_set.relatives.has_key(name) and prompt:
                if feature_set.parameters[feature_set.relatives[name]] is False:
                    pass
            elif type(feature_set.parameters[name]) is tuple and feature_set.relatives.has_key(name) and prompt:
                if feature_set.parameters[feature_set.relatives[name][0]] is False and \
                feature_set.parameters[feature_set.relatives[name][1]] is False:
                    pass
            else:
                assert str(logdict[name]).endswith(str(feature_set.parameters[name]))

    def cleanup_working_directory(self, directory):
        print directory
        files = glob('{0}/*'.format(directory))
        for each_file in files:
            os.renames(each_file, os.path.basename(each_file))
            
    def do_end_to_end_inputfile(self, feature_set):
        logfile, directory = self.define_logfile_and_directory(feature_set.progname)
        
        filename = Features().write_parfile(feature_set.parameters)
        self.launch_program_to_read_inputfile(feature_set.progname, filename, logfile, directory)
        logdict = self.analyze_logfile(os.path.join(directory, logfile))
        self.check_logged_values_against_input(feature_set, logdict, prompt=False)
        self.cleanup_working_directory(directory)
        os.remove(logfile)
        os.remove(filename)

    def do_end_to_end_prompt(self, feature_set):
        logfile, directory = self.define_logfile_and_directory(feature_set.progname)
        
        script = self.feed_in_parameter_values_at_prompt(feature_set)
        self.launch_program_at_prompt(feature_set.progname, logfile, directory, script)
        logdict = self.analyze_logfile(os.path.join(directory, logfile))
        self.check_logged_values_against_input(feature_set, logdict)
        self.cleanup_working_directory(directory)
        os.remove(logfile)

class TestReadInputFile(EndToEndTest):
    """
    Test class that checks that data is read from file
    """

    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()
        # simulate cmdline --f parfile option
        # Option handling
        self.feature_set = ScanSplitPar()

    def do_test_case_rif1(self):
        """
        Test case rif1: to read input values from file, write out default values and read input files again
        """
        self.feature_set.filename = Features().write_parfile(self.feature_set.parameters)
        self.inp = ReadInputFile(self.feature_set)

        for name in self.inp.parameters:
            assert self.inp.parameters[name] == self.feature_set.parameters[name]

    def do_test_case_rif2(self):
        """
        Test case rif2: to read input values from file, change all possible input values and make sure they are not \
        identical to default dictionary
        """
        self.refpardict = self.feature_set.parameters.copy()

        self.generate_randomentries_that_are_of_correct_type()
        self.feature_set.filename = Features().write_parfile(self.feature_set.parameters)
        self.inp = ReadInputFile(self.feature_set)

        for name in self.inp.parameters:
            assert self.inp.parameters[name] != self.refpardict[name]

    def do_test_case3(self):
        """
        Test case rif3: to read input values from file, and check whether they arrived in logfile
        """
        self.feature_set.parameters[list(self.feature_set.parameters.keys())[0]]='nosetest_file.tif'
        self.feature_set.filename = Features().write_parfile(self.feature_set.parameters)
        logfile, directory = self.define_logfile_and_directory('scansplit')
        self.launch_program_to_read_inputfile('scansplit', self.feature_set.filename, logfile, directory)
        logdict = self.analyze_logfile(os.path.join(directory, logfile))
        self.check_logged_values_against_input(self.feature_set, logdict, prompt=False)

        os.remove(os.path.join(directory, logfile))
        os.rmdir(directory)

    def generate_randomentries_that_are_of_correct_type(self):
        for name in self.feature_set.parameters:
            if type(self.feature_set.parameters[name]) is bool:
                if self.feature_set.parameters[name] == True:
                    self.feature_set.parameters[name] = False
                elif self.feature_set.parameters[name] == False:
                    self.feature_set.parameters[name] = True
            elif type(self.feature_set.parameters[name]) is tuple:
                val1 = random.uniform(self.feature_set.properties[name].minimum,
                self.feature_set.properties[name].maximum)
                
                val2 = random.uniform(self.feature_set.properties[name].minimum,
                self.feature_set.properties[name].maximum)
                
                self.feature_set.parameters[name] = tuple((val1, val2))
            elif type(self.feature_set.parameters[name]) is int:
                self.feature_set.parameters[name] = random.randint(self.feature_set.properties[name].minimum,
                self.feature_set.properties[name].maximum)
                
            elif type(self.feature_set.parameters[name]) is float:
                self.feature_set.parameters[name] = random.uniform(self.feature_set.properties[name].minimum,
                self.feature_set.properties[name].maximum)
                
            elif type(self.feature_set.parameters[name]) is str:
                self.feature_set.parameters[name] = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))

    def teardown(self):
        os.remove(self.feature_set.filename)
        self.testingdir.remove()
    
class TestReadPrompt(EndToEndTest):
    """
    Test class that checks input from interactive prompt
    """
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()
        # simulate cmdline --p prompt option
        # Option handling
        self.feature_set = ScanSplitPar()
        self.logfile, self.directory = self.define_logfile_and_directory('scansplit')

        for name in self.feature_set.parameters:
            if type(self.feature_set.parameters[name]) is str:
                if self.feature_set.parameters[name] == list(self.feature_set.parameters.values())[0]:
                    self.feature_set.parameters[name] = 'nosetest_{0}'.format(self.feature_set.parameters[name])
                if self.feature_set.properties[name].ftype in ['getFile', 'getFiles']:
                    open(self.feature_set.parameters[name], 'w').close()
                elif self.feature_set.properties[name].ftype in ['getDir']:
                    self.feature_set.parameters[name] = os.path.split(self.feature_set.parameters[name])[-1]
                    os.mkdir(self.feature_set.parameters[name])

    def do_test_case_rp3(self):
        """
        Test case rp3: read from prompt, simulates proper input, generated from default parameter dictionary
        """
        script = self.feed_in_parameter_values_at_prompt(self.feature_set)
        self.launch_program_at_prompt('scansplit', self.logfile, self.directory, script)
        logdict = self.analyze_logfile(os.path.join(self.directory, self.logfile))
        self.check_logged_values_against_input(self.feature_set, logdict, prompt=False)
 
    def do_test_case_rp4(self):
        """
        Test case rp4: to read from prompt, generates wrong input multiple times and corrects to accepted input \
        (failure of test is possible because of random component in wrong input)
        """
        script = self.feed_in_randompars(self.feature_set)

        self.launch_program_at_prompt('scansplit', self.logfile, self.directory, script)
        self.logdict = self.analyze_logfile(os.path.join(self.directory, self.logfile))
        self.check_logdict_noassert()

    def feed_in_randompars(self, feature_set):
        script = ''
        for name in feature_set.parameters:
            for i in range(random.randint(1,10)):
                script = script + """{0}\n""".format(''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10)))
            if type(feature_set.parameters[name]) is bool:
                if feature_set.parameters[name] == True:
                    enterstring = 'False'
                elif feature_set.parameters[name] == False:
                    enterstring = 'True'
            elif type(feature_set.parameters[name]) is tuple:
                if type(feature_set.parameters[name][0]) is float:
                    val1 = random.uniform(feature_set.properties[name].minimum, feature_set.properties[name].maximum)
                    val2 = random.uniform(feature_set.properties[name].minimum, feature_set.properties[name].maximum)
                elif type(feature_set.parameters[name][0]) is int:
                    val1 = random.randint(feature_set.parameters[name][0] + 1, feature_set.properties[name].maximum)
                    val2 = random.randint(feature_set.parameters[name][1] + 1, feature_set.properties[name].maximum)
                enterstring = '{0},{1}'.format(val1, val2)
            elif type(feature_set.parameters[name]) is int:
                enterstring = '{0}'.format(random.randint(feature_set.parameters[name] + 1,
                feature_set.properties[name].maximum))
                
            elif type(feature_set.parameters[name]) is float:
                enterstring = '{0}'.format(random.uniform(feature_set.properties[name].minimum,
                feature_set.properties[name].maximum))
                
            elif type(feature_set.parameters[name]) is str and feature_set.properties[name].ftype in ['saveFile']:
                enterstring = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10)) + os.extsep + \
                feature_set.properties[name].ext[0]
            else:
                enterstring = '{0}'.format(feature_set.parameters[name])

            script = script + """{0}\n""".format(enterstring)
        
        return script

    def check_logdict_noassert(self):
        for name in self.feature_set.parameters:
            sys.stderr.write('{0}={1}\n'.format(self.feature_set.parameters[name], self.logdict[name]))

            if type(self.feature_set.parameters[name]) is str and self.feature_set.properties[name].ftype in ['getFile',
            'getFiles', 'getDir']:
                assert self.logdict[name].endswith(str(self.feature_set.parameters[name]))
            elif self.feature_set.relatives.has_key(name):
                if self.feature_set.parameters[self.feature_set.relatives[name]] is False:
                    assert not str(self.logdict[name]).endswith(str(self.feature_set.parameters[name]))
                else:
                    assert str(self.logdict[name]).endswith(str(self.feature_set.parameters[name]))
            else:
                assert not self.logdict[name].endswith(str(self.feature_set.parameters[name]))

    def teardown(self):
        for name in self.feature_set.parameters:
            if type(self.feature_set.parameters[name]) is str:
                if self.feature_set.properties[name].ftype in ['getFile', 'getFiles']:
                    os.remove(self.feature_set.parameters[name])
                elif self.feature_set.properties[name].ftype in ['getDir']:
                    os.rmdir(self.feature_set.parameters[name])
        os.remove(os.path.join(self.directory, self.logfile))
        os.rmdir(self.directory)
        self.testingdir.remove()

class TestReadCmdLine(TestReadPrompt):
    """
    Class that tests command line behavior to pass parameters into program
    """
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()
        super(TestReadCmdLine, self).setup()
        self.logfile, self.directory = self.define_logfile_and_directory('scansplit')
        self.cmdlinestr = 'scansplit --cmd --l {0} --d {1}'.format(self.logfile, self.directory)

    def do_test_case_rcl5(self):
        """
        Test case rcl5: to read command line arguments and turn all options on via command line
        """
        self.design_cmdlinestr_opts()
        self.turn_switches()
        self.launch_scansplit_cmd()
        self.logdict = self.analyze_logfile(os.path.join(self.directory, self.logfile))
        self.check_logdict_assert_cmd()

    def do_test_case_rcl6(self):
        """
        Test case rcl6: to read command line arguments with all options turned off
        """
        self.design_cmdlinestr()
        self.turn_switches()
        self.launch_scansplit_cmd()
        self.logdict = self.analyze_logfile(os.path.join(self.directory, self.logfile))
        self.check_logdict_assert_cmd(match=False)

    def do_test_case_rcl7(self):
        """
        Test case rcl7: include random input and output file in command line
        """
        self.cmdlinestr = 'scansplit --l {0} --d {1}'.format(self.logfile, self.directory)
        self.design_random_cmdlinestr()
        self.launch_scansplit_cmd()
        self.logdict = self.analyze_logfile(os.path.join(self.directory, self.logfile))
        self.check_logdict_assert_inpout()


    def turn_switches(self, option=True):
        for name in self.feature_set.parameters:
            if type(self.feature_set.parameters[name]) is bool:
                self.feature_set.parameters[name] = option

    def design_cmdlinestr(self):
        self.cmdlinestr += ' {0}'.format(list(self.feature_set.parameters.values())[0])
        self.cmdlinestr += ' {0}'.format(list(self.feature_set.parameters.values())[1])

    def design_random_cmdlinestr(self):
        inputfile = list(self.feature_set.parameters.values())[0]
        self.cmdlinestr += ' {0}'.format(inputfile)
        self.feature_set.parameters[list(self.feature_set.parameters.keys())[0]] = inputfile
        sys.stderr.write(list(self.feature_set.parameters.values())[0])
        #self.cmdlinestr += ' {0}'.format(self.feature_set.pardict.values()[1])
        
        outputfile = '{0}{1}{2}'.format(''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10)), os.extsep,
        (list(self.feature_set.parameters.values())[1]).split(os.extsep)[-1])
        
        self.cmdlinestr += ' {0}'.format(outputfile)
        self.feature_set.parameters[list(self.feature_set.parameters.keys())[1]] = outputfile
        sys.stderr.write(list(self.feature_set.parameters.values())[1])

    def design_cmdlinestr_opts(self):
        self.design_cmdlinestr()
        for name in self.feature_set.parameters:
            if type(self.feature_set.parameters[name]) is bool:
                #sys.stderr.write(' --{0}'.format(name[0:2].lower()))
                self.cmdlinestr += (' --{0}'.format(name[0:3].lower()))
            elif name in self.feature_set.relatives:
                self.cmdlinestr += (' --{0}'.format('_'.join(name.lower().split())))
                self.cmdlinestr += '={0}'.format(self.feature_set.parameters[name])
                #sys.stderr.write(' --{0}'.format('_'.join(name.lower().split())))

    def launch_scansplit_cmd(self, cmdlinestr=None):
        if cmdlinestr is None: 
            cmdlinestr = self.cmdlinestr
        sys.stderr.write(cmdlinestr)
        subprocess.call(cmdlinestr.split())

    def check_logdict_assert_inpout(self):
        sys.stderr.write('{0}={1}'.format(list(self.feature_set.parameters.values())[0], list(self.logdict.values())[0]))
        assert str(list(self.logdict.values())[0]).endswith('{0}'.format(list(self.feature_set.parameters.values())[0]))
        assert str(list(self.logdict.values())[1]).endswith('{0}'.format(list(self.feature_set.parameters.values())[1]))
#        assert list(self.feature_set.parameters.values())[1] == list(self.logdict.values())[1]

    def check_logdict_assert_cmd(self, match=True):
        for name in self.feature_set.parameters:
            if type(self.feature_set.parameters[name]) is bool:
                sys.stderr.write('{0}:{1}={2}\n'.format(name, self.feature_set.parameters[name], self.logdict[name]))
                if match is True:
                    assert self.logdict[name].endswith(str(self.feature_set.parameters[name]))
                elif match is False:
                    assert not self.logdict[name].endswith(str(self.feature_set.parameters[name]))

    def teardown(self):
        super(TestReadCmdLine, self).teardown()
        self.testingdir.remove()

class TestWriteRst(object):
    """
    Class that tests command line behavior to pass parameters into program
    """
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()
        self.cmdlinestr = 'scansplit --print_rst'

    def do_test_case_twrst1(self):
        subprocess.call(self.cmdlinestr.split(' '))

    def teardown(self):
        os.remove('scansplit.rst')
        os.remove('scansplit_functions.rst')
        self.testingdir.remove()
