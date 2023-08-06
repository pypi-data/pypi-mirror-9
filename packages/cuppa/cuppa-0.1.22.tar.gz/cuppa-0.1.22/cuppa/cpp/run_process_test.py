
#          Copyright Jamie Allsop 2013-2015
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

#-------------------------------------------------------------------------------
#   RunBoostTest
#-------------------------------------------------------------------------------

import os
import sys
import shlex

import cuppa.timer
import cuppa.sconscript_progress
from cuppa.output_processor import IncrementalSubProcess


class TestSuite:

    suites = {}

    @classmethod
    def create( cls, name, scons_env ):
        if not name in cls.suites:
            cls.suites[name] = TestSuite( name, scons_env )
        return cls.suites[name]

    def __init__( self, name, scons_env ):
        self._name = name
        self._scons_env = scons_env
        self._colouriser = scons_env['colouriser']

        sys.stdout.write('\n')
        sys.stdout.write(
            self._colouriser.emphasise( "Starting Test Suite [{}]".format( name ) )
        )
        sys.stdout.write('\n')

        cuppa.sconscript_progress.SconscriptProgress.register_callback( scons_env, self.on_progress )

        self._suite = {}
        self._suite['total_tests']       = 0
        self._suite['passed_tests']      = 0
        self._suite['failed_tests']      = 0
        self._suite['expected_failures'] = 0
        self._suite['skipped_tests']     = 0
        self._suite['aborted_tests']     = 0
        self._suite['total_cpu_times']   = cuppa.timer.CpuTimes( 0, 0, 0, 0 )

        self._tests = []


    def on_progress( self, progress, env, sconscript, target, source ):
        if progress == 'finished':
            self.exit_suite()
            del self.suites[sconscript]


    def enter_test( self, test, expected='success' ) :
        sys.stdout.write(
            self._colouriser.emphasise( "\nTest [%s]..." % test ) + '\n'
        )
        self._tests.append( {} )
        test_case = self._tests[-1]
        test_case['name']     = test
        test_case['expected'] = expected
        test_case['timer']    = cuppa.timer.Timer()


    def exit_test( self, test, status='success' ):
        test_case = self._tests[-1]
        test_case['timer'].stop()
        test_case['status'] = status

        self._write_test_case( test_case )

        self._suite['total_tests'] += 1
        if status == 'success':
            self._suite['passed_tests'] += 1
        elif status == 'failed':
            self._suite['failed_tests'] += 1
        elif status == 'expected_failure':
            self._suite['expected_failures'] += 1
        elif status == 'aborted':
            self._suite['aborted_tests'] += 1
        elif status == 'skipped':
            self._suite['skipped_tests'] += 1

        self._suite['total_cpu_times'] += test_case['timer'].elapsed()

        sys.stdout.write('\n\n')


    def _write_test_case( self, test_case ):
        expected = test_case['expected'] == test_case['status']
        passed   = test_case['status'] == "success"
        meaning  = test_case['status']

        if not expected and passed:
            meaning = 'unexpected_success'

        label = " ".join( meaning.upper().split('_') )

        cpu_times = test_case['timer'].elapsed()
        sys.stdout.write( self._colouriser.highlight( meaning, " = %s = " % label ) )
        self._write_time( cpu_times )


    def exit_suite( self ):

        suite = self._suite

        total_tests  = suite['total_tests']
        passed_tests = suite['passed_tests'] + suite['expected_failures'] + suite['skipped_tests']
        failed_tests = suite['failed_tests'] + suite['aborted_tests']

        expected_failures = suite['expected_failures']
        skipped_tests     = suite['skipped_tests']
        aborted_tests     = suite['aborted_tests']

        suite['status'] = 'passed'
        meaning = 'success'

        if total_tests != passed_tests:
            suite['status'] = 'failed'
            meaning = 'failed'

        sys.stdout.write(
            self._colouriser.emphasise( "\nTest Suite [{}] ".format( self._name ) )
        )

        sys.stdout.write(
            self._colouriser.highlight( meaning, " = {} = ".format( suite['status'].upper() ) )
        )

        sys.stdout.write('\n')

        for test in self._tests:
            sys.stdout.write(
                self._colouriser.emphasise( "\nTest case [{}]".format( test['name'] ) ) + '\n'
            )
            self._write_test_case( test )

        sys.stdout.write('\n\n')

        if total_tests > 0:
            if suite['status'] == 'passed':
                sys.stdout.write(
                    self._colouriser.highlight(
                        meaning,
                        " ( %s of %s Test Cases Passed )" % ( passed_tests, total_tests )
                    )
                )
            else:
                sys.stdout.write(
                    self._colouriser.highlight(
                        meaning,
                        " ( %s of %s Test Cases Failed )" % (failed_tests, total_tests)
                    )
                )
        else:
            sys.stdout.write(
                self._colouriser.colour(
                    'notice',
                    " ( No Test Cases Checked )"
                )
            )

        if passed_tests > 0:
            sys.stdout.write(
                self._colouriser.highlight(
                    meaning,
                    " ( %s %s Passed ) "
                    % (passed_tests, passed_tests > 1 and 'Test Cases' or 'Test Case')
                )
            )

        if failed_tests > 0:
            sys.stdout.write(
                self._colouriser.highlight(
                    meaning,
                    " ( %s %s Failed ) "
                    % (failed_tests, failed_tests > 1 and 'Test Cases' or 'Test Case')
                )
            )

        if expected_failures > 0:
            meaning = 'expected_failure'
            sys.stdout.write(
                self._colouriser.highlight(
                    meaning,
                    " ( %s %s Expected ) "
                    % (expected_failures, expected_failures > 1 and 'Failures' or 'Failure')
                )
            )

        if skipped_tests > 0:
            meaning = 'skipped'
            sys.stdout.write(
                self._colouriser.highlight(
                    meaning,
                    " ( %s %s Skipped ) "
                    % (skipped_tests, skipped_tests > 1 and 'Test Cases' or 'Test Case')
                )
            )

        if aborted_tests > 0:
            meaning = 'aborted'
            sys.stdout.write(
                self._colouriser.highlight(
                    meaning,
                    " ( %s %s Aborted ) "
                    % (aborted_tests, aborted_tests > 1 and 'Test Cases Were' or 'Test Case Was')
                )
            )


        sys.stdout.write('\n')
        self._write_time( self._suite['total_cpu_times'], True )

        self._tests = []
        self._suite = {}

        sys.stdout.write('\n\n')


    def _write( self, text, emphasise=False ):
        if not emphasise:
            sys.stdout.write( text )
        else:
            sys.stdout.write( self._colouriser.emphasise( text ) )


    def _write_time( self, cpu_times, emphasise=False ):

        self._write( " Time:", emphasise )

        self._write(
            " Wall [ {}".format( self._colouriser.emphasise_time_by_digit( duration_from_elapsed( cpu_times.wall ) ) ),
            emphasise
        )

        self._write(
            " ] CPU [ {}".format( self._colouriser.emphasise_time_by_digit( duration_from_elapsed( cpu_times.process ) ) ),
            emphasise
        )

        percent = "{:.2f}".format( float(cpu_times.process) * 100 / cpu_times.wall )

        wall_cpu_percent = "%6s%%" % percent.upper()
        self._write(
            " ] CPU/Wall [ {}".format( self._colouriser.colour( 'time', wall_cpu_percent ) ),
            emphasise
        )

        self._write( " ]", emphasise )


    def message(self, line):
        sys.stdout.write(
            line + "\n"
        )


def stdout_from_program( program_file ):
    return program_file + '.stdout.log'


def stderr_from_program( program_file ):
    return program_file + '.stderr.log'


def report_from_program( program_file ):
    return program_file + '.report.xml'


def store_durations( results ):
    if 'cpu_time' in results:
        results['cpu_duration']  = duration_from_elapsed(results['cpu_time'])
    if 'wall_time' in results:
        results['wall_duration'] = duration_from_elapsed(results['wall_time'])
    if 'user_time' in results:
        results['user_duration'] = duration_from_elapsed(results['user_time'])
    if 'sys_time' in results:
        results['sys_duration']  = duration_from_elapsed(results['sys_time'])


class RunProcessTestEmitter:

    def __init__( self, final_dir ):
        self._final_dir = final_dir


    def __call__( self, target, source, env ):
        program_file = os.path.join( self._final_dir, os.path.split( source[0].path )[1] )
        target = []
        target.append( stdout_from_program( program_file ) )
        target.append( stderr_from_program( program_file ) )
        return target, source


class ProcessStdout:

    def __init__( self, log ):
        self.log = open( log, "w" )


    def __call__( self, line ):
        self.log.write( line + '\n' )


    def __exit__( self, type, value, traceback ):
        if self.log:
            self.log.close()


class ProcessStderr:

    def __init__( self, log ):
        self.log = open( log, "w" )


    def __call__( self, line ):
        self.log.write( line + '\n' )


    def __exit__( self, type, value, traceback ):
        if self.log:
            self.log.close()


class RunProcessTest:

    def __init__( self, expected ):
        self._expected = expected


    def __call__( self, target, source, env ):

        executable = str( source[0].abspath )
        working_dir, test = os.path.split( executable )
        program_path = source[0].path
        suite = env['build_dir']

        if cuppa.build_platform.name() == "Windows":
            executable = '"' + executable + '"'

        test_command = executable

        test_suite = TestSuite.create( suite, env )

        test_suite.enter_test( test, expected=self._expected )

        try:
            return_code = self.__run_test( program_path,
                                           test_command,
                                           working_dir )

            if return_code < 0:
                self.__write_file_to_stderr( stderr_from_program( program_path ) )
                print >> sys.stderr, "Test was terminated by signal: ", -return_code
                test_suite.exit_test( test, 'aborted' )
            elif return_code > 0:
                self.__write_file_to_stderr( stderr_from_program( program_path ) )
                print >> sys.stderr, "Test returned with error code: ", return_code
                test_suite.exit_test( test, 'failed' )
            else:
                test_suite.exit_test( test, 'success' )

            return return_code

        except OSError, e:
            print >> sys.stderr, "Execution of [", test_command, "] failed with error: ", e
            return 1


    def __run_test( self, program_path, test_command, working_dir ):
        process_stdout = ProcessStdout( stdout_from_program( program_path ) )
        process_stderr = ProcessStderr( stderr_from_program( program_path ) )

        return_code = IncrementalSubProcess.Popen2( process_stdout,
                                                    process_stderr,
                                                    shlex.split( test_command ),
                                                    cwd=working_dir )
        return return_code


    def __write_file_to_stderr( self, file_name ):
        error_file = open( file_name, "r" )
        for line in error_file:
            print >> sys.stderr, line
        error_file.close()



#def nanosecs_from_time( time_in_seconds ):
#    seconds, subseconds = time_in_seconds.split('.')
#    nanoseconds = subseconds
#    decimal_places = len(subseconds)
#    if decimal_places < 9:
#        nanoseconds = int(subseconds) * 10**(9-decimal_places)
#    return int(seconds) * 1000000000 + int(nanoseconds)


def duration_from_elapsed( total_nanosecs ):
    secs, remainder      = divmod( total_nanosecs, 1000000000 )
    millisecs, remainder = divmod( remainder, 1000000 )
    microsecs, nanosecs  = divmod( remainder, 1000 )
    hours, remainder     = divmod( secs, 3600 )
    minutes, secs        = divmod( remainder, 60 )

    duration = "%02d:%02d:%02d.%03d,%03d,%03d" % ( hours, minutes, secs, millisecs, microsecs, nanosecs )
    return duration
