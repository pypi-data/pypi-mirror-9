
#          Copyright Declan Traynor 2012
#          Copyright Jamie Allsop 2012-2014
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

#-------------------------------------------------------------------------------
#   Colouriser
#-------------------------------------------------------------------------------

import re


try:
    import colorama
    colorama_available = True
except ImportError:
    print 'Output Colourisation disabled. To enabled, install colorama'
    colorama_available = False


class Colouriser(object):

    @classmethod
    def create( cls ):
        if colorama_available:
            colorama.init()
        return cls()


    def __init__( self ):
        self.use_colour = False


    def enable( self ):
        self.use_colour = True


    def colour( self, meaning, text ):
        if not self.use_colour:
            return text
        else:
            return self.start_colour( meaning ) + text + colorama.Style.RESET_ALL


    def emphasise( self, text ):
        if not self.use_colour:
            return text
        else:
            return colorama.Style.BRIGHT + text + colorama.Style.RESET_ALL


    def emphasise_time_by_group( self, time_text ):
        if not self.use_colour:
            return time_text
        else:
            time_elements = re.findall( r'[0-9]+[:.,]?', time_text )
            time_found = False
            emphasised = self.start_colour('time')
            empty = re.compile( r'00[:.]|000[,]?' )
            for element in time_elements:
                if not time_found and not empty.match( element ):
                    time_found = True
                    emphasised += self.start_highlight('time')
                emphasised += element

            emphasised += colorama.Style.RESET_ALL

            return emphasised


    def emphasise_time_by_digit( self, time_text ):
        if not self.use_colour:
            return time_text
        else:
            time_found = False
            emphasised = self.start_colour('time')
            for char in time_text:
                if not time_found and char.isdigit() and int(char) > 0:
                    time_found = True
                    emphasised += self.start_highlight('time')
                emphasised += char

            emphasised += colorama.Style.RESET_ALL

            return emphasised


    def highlight( self, meaning, text ):
        if not self.use_colour:
            return text
        else:
            return self.start_highlight( meaning ) + text + colorama.Style.RESET_ALL


    ## Make these functions into simple dictionary lookups

    def start_colour( self, meaning ):
        if meaning == 'error':
            return colorama.Fore.RED
        elif meaning == 'warning':
            return colorama.Fore.BLUE
        elif meaning == 'summary':
            return colorama.Fore.BLACK
        elif meaning == 'passed':
            return colorama.Fore.GREEN
        elif meaning == 'success':
            return colorama.Fore.GREEN
        elif meaning == 'unexpected_success':
            return colorama.Fore.GREEN
        elif meaning == 'expected_failure':
            return colorama.Fore.YELLOW
        elif meaning == 'failure':
            return colorama.Fore.RED
        elif meaning == 'failed':
            return colorama.Fore.RED
        elif meaning == 'aborted':
            return colorama.Fore.RED
        elif meaning == 'skipped':
            return colorama.Fore.BLACK
        elif meaning == 'notice':
            return colorama.Fore.YELLOW
        elif meaning == 'time':
            return colorama.Fore.BLUE
        elif meaning == 'info':
            return ''

    def start_highlight( self, meaning ):
        if meaning == 'error':
            return colorama.Style.BRIGHT + colorama.Back.RED + colorama.Fore.WHITE
        elif meaning == 'warning':
            return colorama.Style.BRIGHT + colorama.Back.BLUE + colorama.Fore.WHITE
        elif meaning == 'summary':
            return colorama.Style.BRIGHT + colorama.Back.BLACK + colorama.Fore.WHITE
        elif meaning == 'success':
            return colorama.Style.BRIGHT + colorama.Back.GREEN + colorama.Fore.WHITE
        elif meaning == 'unexpected_success':
            return colorama.Style.BRIGHT + colorama.Back.GREEN + colorama.Fore.BLACK
        elif meaning == 'passed':
            return colorama.Style.BRIGHT + colorama.Back.GREEN + colorama.Fore.WHITE
        elif meaning == 'expected_failure':
            return colorama.Style.BRIGHT + colorama.Back.YELLOW + colorama.Fore.WHITE
        elif meaning == 'failure':
            return colorama.Style.BRIGHT + colorama.Back.RED + colorama.Fore.WHITE
        elif meaning == 'failed':
            return colorama.Style.BRIGHT + colorama.Back.RED + colorama.Fore.WHITE
        elif meaning == 'aborted':
            return colorama.Style.BRIGHT + colorama.Back.RED + colorama.Fore.BLACK
        elif meaning == 'skipped':
            return colorama.Style.BRIGHT + colorama.Back.BLACK + colorama.Fore.WHITE
        elif meaning == 'notice':
            return colorama.Style.BRIGHT + colorama.Back.YELLOW + colorama.Fore.WHITE
        elif meaning == 'time':
            return colorama.Style.BRIGHT + colorama.Back.BLUE + colorama.Fore.WHITE
        elif meaning == 'info':
            return ''
