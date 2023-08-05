
#          Copyright Jamie Allsop 2011-2014
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

#-------------------------------------------------------------------------------
#   CoverageMethod
#-------------------------------------------------------------------------------


from SCons.Script import Flatten

import cuppa.sconscript_progress


class CoverageMethod(object):

    def __init__( self ):
        pass


    def __call__( self, env, program, sources, final_dir=None ):
        if final_dir == None:
            final_dir = env['abs_final_dir']

        emitter, builder = env['toolchain'].coverage_runner( program, final_dir )

        env['BUILDERS']['CoverageBuilder'] = env.Builder( action=builder, emitter=emitter )

        coverage = env.CoverageBuilder( [], Flatten( [ sources ] ) )
        cuppa.sconscript_progress.SconscriptProgress.add( env, coverage )
        return coverage


    @classmethod
    def add_to_env( cls, env ):
        env.AddMethod( cls(), "Coverage" )
