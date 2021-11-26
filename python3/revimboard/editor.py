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

import vimspector.utils


CALLBACKS = {}


def OpenEditor( what, filetype, callback ):
  orig_win = vim.current.window

  orig_win_id = vimspector.utils.WindowID( orig_win, orig_win.tabpage )

  tmp_bufname = vim.eval( 'tempname()' )
  vim.command( f"rightbelow 10split { tmp_bufname }" )
  buf = vim.current.buffer
  buf.options[ 'bufhidden' ] = 'wipe'
  buf.options[ 'buflisted' ] = False

  CALLBACKS[ buf.number ] = {
    'fn': callback,
    'tempfile': tmp_bufname,
  }

  editor_win_id = vimspector.utils.WindowID( vim.current.window,
                                             vim.current.window.tabpage )

  # When the buffer is wiped out, we're done
  #
  vim.command( "autocmd BufWipeout <buffer> "
               f"py3 revimboard.editor.Close( { buf.number } )" )

  # TODO(Ben): This doesn't work, because vim's code doesn't actually update
  # `wp` when WinClosed moves the cursor; you have to use WinLeave which is
  # triggered eaelier.
  # vim.command( f"autocmd WinClosed { editor_win_id } "
  #              f"echom 'jump to window { orig_win_id }'" )

  vimspector.utils.SetBufferContents( buf, what )
  vimspector.utils.Call( 'setbufvar', buf.number, '&filetype', filetype )


def Close( buffer_number ):
  callback = CALLBACKS[ buffer_number ]

  try: 
    buffer_text =  '\n'.join ( vimspector.utils.Call( 'readfile',
                                                      callback[ 'tempfile' ] ) )
    vimspector.utils.Call( 'delete', callback[ 'tempfile' ] )
  except vim.error:
    buffer_text = ''
    pass

  try:
    callback[ 'fn' ]( buffer_text )
  except KeyError:
    pass

# vim: sw=2
