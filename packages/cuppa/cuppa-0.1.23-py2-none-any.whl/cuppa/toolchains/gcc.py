
#          Copyright Jamie Allsop 2011-2015
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

#-------------------------------------------------------------------------------
#   GCC Toolchain
#-------------------------------------------------------------------------------

import SCons.Script

from subprocess import Popen, PIPE
import re
import shlex
from exceptions import Exception


from cuppa.cpp.create_version_file_cpp import CreateVersionHeaderCpp, CreateVersionFileCpp
from cuppa.cpp.run_boost_test import RunBoostTestEmitter, RunBoostTest
from cuppa.cpp.run_process_test import RunProcessTestEmitter, RunProcessTest
from cuppa.cpp.run_gcov_coverage import RunGcovCoverageEmitter, RunGcovCoverage
from cuppa.output_processor import command_available
import cuppa.build_platform


class GccException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)


class Gcc(object):


    @classmethod
    def default_version( cls ):
        if not hasattr( cls, '_default_version' ):
            command = "g++ --version"
            if command_available( command ):
                version = Popen( shlex.split( command ), stdout=PIPE).communicate()[0]
                cls._default_version = 'gcc' + re.search( r'(\d)\.(\d)', version ).expand(r'\1\2')
            else:
                cls._default_version = None
        return cls._default_version


    @classmethod
    def supported_versions( cls ):
        return [
            "gcc",
            "gcc49",
            "gcc48",
            "gcc47",
            "gcc46",
            "gcc45",
            "gcc44",
            "gcc43",
            "gcc42",
            "gcc41",
            "gcc40",
            "gcc34"
        ]


    @classmethod
    def available_versions( cls ):
        if not hasattr( cls, '_available_versions' ):
            cls._available_versions = []
            for version in cls.supported_versions():
                if version == "gcc":
                    continue
                command = "g++-{} --version".format( re.search( r'(\d)(\d)', version ).expand(r'\1.\2') )
                if command_available( command ):
                    reported_version = Popen( shlex.split( command ), stdout=PIPE).communicate()[0]
                    reported_version = 'gcc' + re.search( r'(\d)\.(\d)', reported_version ).expand(r'\1\2')
                    if version == reported_version:
                        cls._available_versions.append( version )
                    else:
                        raise GccException("GCC toolchain [{}] reporting version as [{}].".format( version, reported_version ) )
            if cls._available_versions:
                cls._available_versions.append( "gcc" )
        return cls._available_versions


    @classmethod
    def add_options( cls, add_option ):
        pass


    @classmethod
    def add_to_env( cls, env, add_toolchain, add_to_supported ):
        for version in cls.supported_versions():
            add_to_supported( version )

        for version in cls.available_versions():
            add_toolchain( version, cls( version ) )


    @classmethod
    def default_variants( cls ):
        return [ 'dbg', 'rel' ]


    def _linux_lib_flags( self, env ):
        self.values['static_link']     = '-Xlinker -Bstatic'
        self.values['dynamic_link']    = '-Xlinker -Bdynamic'

        STATICLIBFLAGS  = self.values['static_link']   + ' ' + re.search( r'(.*)(,\s*LIBS\s*,)(.*)', env['_LIBFLAGS'] ).expand( r'\1, STATICLIBS,\3' )
        DYNAMICLIBFLAGS = self.values['dynamic_link']  + ' ' + re.search( r'(.*)(,\s*LIBS\s*,)(.*)', env['_LIBFLAGS'] ).expand( r'\1, DYNAMICLIBS,\3' )
        return STATICLIBFLAGS + ' ' + DYNAMICLIBFLAGS


    def __init__( self, version ):

        if version == "gcc":
            if self.default_version():
                version = self.default_version()
            else:
                version = self.available_versions()[0]

        self.values = {}

        self._version = re.search( r'(\d)(\d)', version ).expand(r'\1.\2')
        self.values['name'] = version

        self._initialise_toolchain( version )

        self.values['CXX'] = "g++-{}".format( self._version )
        self.values['CC']  = "gcc-{}".format( self._version )

        env = SCons.Script.DefaultEnvironment()

        SYSINCPATHS = '${_concat(\"' + self.values['sys_inc_prefix'] + '\", SYSINCPATH, \"'+ self.values['sys_inc_suffix'] + '\", __env__, RDirs, TARGET, SOURCE)}'

        self.values['_CPPINCFLAGS'] = '$( ' + SYSINCPATHS + ' ${_concat(INCPREFIX, INCPATH, INCSUFFIX, __env__, RDirs, TARGET, SOURCE)} $)'

        if cuppa.build_platform.name() == "Linux":
            self.values['_LIBFLAGS'] = self._linux_lib_flags( env )
        else:
            self.values['_LIBFLAGS'] = env['_LIBFLAGS']


    def __getitem__( self, key ):
        return self.values.get( key )


    def name( self ):
        return self.values['name']


    def family( self ):
        return "gcc"


    def version( self ):
        return self._version


    def binary( self ):
        return self.values['CXX']


    def initialise_env( self, env ):
        env['CXX']          = self.values['CXX']
        env['CC']           = self.values['CC']
        env['_CPPINCFLAGS'] = self.values['_CPPINCFLAGS']
        env['_LIBFLAGS']    = self.values['_LIBFLAGS']
        env['SYSINCPATH']   = []
        env['INCPATH']      = [ '#.', '.' ]
        env['LIBPATH']      = []
        env['CPPDEFINES']   = []
        env['LIBS']         = []
        env['STATICLIBS']   = []
        env['DYNAMICLIBS']  = self.values['dynamic_libraries']


    def variants( self ):
        pass


    def supports_coverage( self ):
        return 'coverage_cxx_flags' in self.values


    def version_file_builder( self, env, namespace, version, location ):
        return CreateVersionFileCpp( env, namespace, version, location )


    def version_file_emitter( self, env, namespace, version, location ):
        return CreateVersionHeaderCpp( env, namespace, version, location )


    def test_runner( self, tester, final_dir, expected ):
        if not tester or tester =='process':
            return RunProcessTest( expected ), RunProcessTestEmitter( final_dir )
        elif tester=='boost':
            return RunBoostTest( expected ), RunBoostTestEmitter( final_dir )


    def test_runners( self ):
        return [ 'process', 'boost' ]


    def coverage_runner( self, program, final_dir ):
        return RunGcovCoverageEmitter( program, final_dir ), RunGcovCoverage( program, final_dir )


    def update_variant( self, env, variant ):
        if variant == 'dbg':
            env.MergeFlags( self.values['debug_cxx_flags'] + self.values['debug_c_flags'] + self.values['debug_link_cxx_flags'] )
        elif variant == 'rel':
            env.MergeFlags( self.values['release_cxx_flags'] + self.values['release_c_flags'] + self.values['release_link_cxx_flags'] )
        elif variant == 'cov':
            env.MergeFlags( self.values['coverage_cxx_flags'] + self.values['coverage_c_flags'] )
            env.Append( CXXFLAGS = self.values['coverage_cxx_flags'] )
            env.AppendUnique( LINKFLAGS = self.values['coverage_link_cxx_flags'] )
        if env['stdcpp']:
            env.ReplaceFlags( "-std={}".format(env['stdcpp']) )

    def _initialise_toolchain( self, toolchain ):
        if toolchain == 'gcc34':
            self.values['sys_inc_prefix']  = '-I'
        else:
            self.values['sys_inc_prefix']  = '-isystem'

        self.values['sys_inc_suffix']  = ''

        CommonCxxFlags = [ '-Wall', '-fexceptions', '-g' ]
        CommonCFlags   = [ '-Wall', '-g' ]

        if re.match( 'gcc4[3-6]', toolchain ):
            CommonCxxFlags += [ '-std=c++0x' ]
        elif re.match( 'gcc47', toolchain ):
            CommonCxxFlags += [ '-std=c++11' ]
        elif re.match( 'gcc4[8-9]', toolchain ):
            CommonCxxFlags += [ '-std=c++1y' ]

        self.values['debug_cxx_flags']    = CommonCxxFlags + []
        self.values['release_cxx_flags']  = CommonCxxFlags + [ '-O3', '-DNDEBUG' ]
        self.values['coverage_cxx_flags'] = CommonCxxFlags + [ '--coverage' ]

        self.values['debug_c_flags']      = CommonCFlags + []
        self.values['release_c_flags']    = CommonCFlags + [ '-O3', '-DNDEBUG' ]
        self.values['coverage_c_flags']   = CommonCFlags + [ '--coverage' ]

        CommonLinkCxxFlags = []
        if cuppa.build_platform.name() == "Linux":
            CommonLinkCxxFlags = ['-rdynamic', '-Wl,-rpath=.' ]

        self.values['debug_link_cxx_flags']    = CommonLinkCxxFlags
        self.values['release_link_cxx_flags']  = CommonLinkCxxFlags
        self.values['coverage_link_cxx_flags'] = CommonLinkCxxFlags + [ '--coverage' ]

        DynamicLibraries = []
        if cuppa.build_platform.name() == "Linux":
            DynamicLibraries = [ 'pthread', 'rt' ]
        self.values['dynamic_libraries'] = DynamicLibraries


    def __get_gcc_coverage( self, object_dir, source ):
        # -l = --long-file-names
        # -p = --preserve-paths
        # -b = --branch-probabilities
        return 'gcov -o ' + object_dir \
               + ' -l -p -b ' \
               + source + ' > ' + source + '_summary.gcov'


    def abi_flag( self, env ):
        if env['stdcpp']:
            return '-std={}'.format(env['stdcpp'])
        elif re.match( 'gcc4[3-6]', self.values['name'] ):
            return '-std=c++0x'
        elif re.match( 'gcc47', self.values['name'] ):
            return '-std=c++11'
        elif re.match( 'gcc4[8-9]', self.values['name'] ):
            return '-std=c++1y'


    def stdcpp_flag_for( self, standard ):
        return "-std={}".format( standard )


    @classmethod
    def output_interpretors( cls ):
        return [
        {
            'title'     : "Fatal Error",
            'regex'     : r"(FATAL:[ \t]*(.*))",
            'meaning'   : 'error',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1 ],
            'file'      : None,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "In File Included From",
            'regex'     : r"(In file included\s+|\s+)(from\s+)([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+)(:[0-9]+)?)([,:])",
            'meaning'   : 'info',
            'highlight' : set( [ 1, 3, 4 ] ),
            'display'   : [ 1, 2, 3, 4, 7 ],
            'file'      : 3,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "In Function Info",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:[ \t]+([iI]n ([cC]lass|[cC]onstructor|[dD]estructor|[fF]unction|[mM]ember [fF]unction|[sS]tatic [fF]unction|[sS]tatic [mM]ember [fF]unction).*))",
            'meaning'   : 'info',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1, 2 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Skipping Instantiation Contexts 2",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+):[0-9]+)(:[ \t]+(\[[ \t]+[Ss]kipping [0-9]+ instantiation contexts[, \t]+.*\]))",
            'meaning'   : 'info',
            'highlight' : set( [ 1, 2 ] ),
            'display'   : [ 1, 2, 4 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Skipping Instantiation Contexts",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+))(:[ \t]+(\[[ \t]+[Ss]kipping [0-9]+ instantiation contexts[ \t]+\]))",
            'meaning'   : 'info',
            'highlight' : set( [ 1, 2 ] ),
            'display'   : [ 1, 2, 4 ],
            'file'      : 2,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Instantiated From",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+))(:[ \t]+([iI]nstantiated from .*))",
            'meaning'   : 'info',
            'highlight' : set( [ 1, 2] ),
            'display'   : [ 1, 2, 4 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Instantiation of",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:[ \t]+(In instantiation of .*))",
            'meaning'   : 'info',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1, 2 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Required From",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+):[0-9]+)(:[ \t]+required from .*)",
            'meaning'   : 'info',
            'highlight' : set( [ 1, 2 ] ),
            'display'   : [ 1, 2, 4 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Compiler Warning 2",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+):([0-9]+))(:[ \t]([Ww]arning:[ \t].*))",
            'meaning'   : 'warning',
            'highlight' : set( [ 1, 2 ] ),
            'display'   : [ 1, 2, 5 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Compiler Note 2",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+):[0-9]+)(:[ \t]([Nn]ote:[ \t].*))",
            'meaning'   : 'info',
            'highlight' : set( [ 1, 2 ] ),
            'display'   : [ 1, 2, 4 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Compiler Note",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+))(:[ \t]([Nn]ote:[ \t].*))",
            'meaning'   : 'info',
            'highlight' : set( [ 1, 2 ] ),
            'display'   : [ 1, 2, 4 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "General Note",
            'regex'     : r"([Nn]ote:[ \t].*)",
            'meaning'   : 'info',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1 ],
            'file'      : None,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Compiler Error 2",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+):[0-9]+)(:[ \t](.*))",
            'meaning'   : 'error',
            'highlight' : set( [ 1, 2 ] ),
            'display'   : [ 1, 2, 4 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Compiler Warning",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+))(:[ \t]([Ww]arning:[ \t].*))",
            'meaning'   : 'warning',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1, 2, 4 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Undefined Reference 2",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+\.o:([][{}() \t#%$~\w&_:+/\.-]+):([0-9]+))(:[ \t](undefined reference.*))",
            'meaning'   : 'warning',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1, 4 ],
            'file'      : 2,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Compiler Error",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+))(:[ \t](.*))",
            'meaning'   : 'error',
            'highlight' : set( [ 1, 2 ] ),
            'display'   : [ 1, 2, 4 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Linker Warning",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:\(\.text\+[0-9a-fA-FxX]+\))(:[ \t]([Ww]arning:[ \t].*))",
            'meaning'   : 'warning',
            'highlight' : set( [ 1, 2 ] ),
            'display'   : [ 1, 2, 4 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Linker Error",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:([0-9]+):[0-9]+)(:[ \t](.*))",
            'meaning'   : 'error',
            'highlight' : set( [ 1, 2 ] ),
            'display'   : [ 1, 2, 4 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Linker Error 2",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+\(.text\+[0-9A-Za-z]+\):([ \tA-Za-z0-9_:+/\.-]+))(:[ \t](.*))",
            'meaning'   : 'error',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1, 4 ],
            'file'      : 1,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Linker Error 3",
            'regex'     : r"(([][{}() \t#%$~\w&_:+/\.-]+):\(\.text\+[0-9a-fA-FxX]+\))(:(.*))",
            'meaning'   : 'error',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1, 4 ],
            'file'      : 2,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Linker Error - lib not found",
            'regex'     : r"(.*(ld.*):[ \t](cannot find.*))",
            'meaning'   : 'error',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1 ],
            'file'      : None,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Linker Error - cannot open output file",
            'regex'     : r"(.*(ld.*):[ \t](cannot open output file.*))(:[ \t](.*))",
            'meaning'   : 'error',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1, 4 ],
            'file'      : None,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Linker Error - unrecognized option",
            'regex'     : r"(.*(ld.*))(:[ \t](unrecognized option.*))",
            'meaning'   : 'error',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1, 3 ],
            'file'      : None,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "No such File or Directory",
            'regex'     : r"(.*:(.*))(:[ \t](No such file or directory.*))",
            'meaning'   : 'error',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1, 3 ],
            'file'      : None,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Undefined Reference",
            'regex'     : r"([][{}() \t#%$~\w&_:+/\.-]+)(:[ \t](undefined reference.*))",
            'meaning'   : 'error',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1, 2 ],
            'file'      : None,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "General Warning",
            'regex'     : r"([Ww]arning:[ \t].*)",
            'meaning'   : 'warning',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1 ],
            'file'      : None,
            'line'      : None,
            'column'    : None,
        },
        {
            'title'     : "Auto-Import Info",
            'regex'     : r"(([Ii]nfo:[ \t].*)\(auto-import\))",
            'meaning'   : 'info',
            'highlight' : set( [ 1 ] ),
            'display'   : [ 1 ],
            'file'      : None,
            'line'      : None,
            'column'    : None,
        },
    ]
