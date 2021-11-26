# revimboard - A ReviewBoard client for VIM
#
# Copyright 2021 Ben Jackson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import vim

from vimspector import utils


def AtFirstColumn( buffer_line: int, text: str, syntax: str, **kwargs ):
  # Need to find the screen position of the first text column of the current
  # window
  win_info = utils.Call( 'getwininfo', int( vim.eval( 'win_getid()' )  ) )[ 0 ]
  screen_col = int( win_info[ 'wincol' ] ) + int( win_info[ 'textoff' ] )

  win_line = buffer_line - int( win_info[ 'topline' ] )
  screen_line = int( win_info[ 'winrow' ] ) + win_line - 1

  options = {
    'pos': 'botleft',
    'line': screen_line,
    'col': screen_col,
    'border': [],
    'padding': [ 0, 1, 0, 1 ],
    'resize': True,
    'close': 'button',
    'drag': True,
    'moved': 'any',
    # TODO(Ben): &ambiwidth needs to be single else this looks dodge
    'borderchars': [ '─', '│', '─', '│', '╭', '╮', '┛', '╰' ]
  }
  options.update( kwargs )
  win_id = utils.Call( 'popup_create', text.splitlines(), options )
  utils.Call( 'win_execute', win_id, f'set syntax={ syntax }' )


# vim: sw=2
