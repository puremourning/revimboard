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


def SignDefined( name ):
  if utils.Exists( "*sign_getdefined" ):
    return int(
      vim.eval( f"len( sign_getdefined( '{ utils.Escape( name ) }' ) )" )
    )

  return False


def DefineSign( name, text, double_text, texthl, col = 'right', **kwargs ):
  # TODO(Ben): Switch to sign_define()
  if utils.GetVimValue( vim.options, 'ambiwidth', '' ) == 'double':
    text = double_text

  if col == 'right':
    if int( utils.Call( 'strdisplaywidth', text ) ) < 2:
      text = ' ' + text

  text = text.replace( ' ', r'\ ' )

  cmd = f'sign define { name } text={ text } texthl={ texthl }'
  for key, value in kwargs.items():
    cmd += f' { key }={ value }'

  vim.command( cmd )


def PlaceSign( sign_id, group, name, file_name, line ):
  # TODO(BenJ): fix priority - use the vimspector setting mechanism ?
  priority = 1000

  # TODO(Ben): change to sign_place
  cmd = ( f'sign place { sign_id } '
          f'group={ group } '
          f'name={ name } '
          f'priority={ priority } '
          f'line={ line } '
          f'file={ file_name }' )

  vim.command( cmd )


def UnplaceSign( sign_id, group ):
  # TODO(Ben): switch to sign_unplace()
  vim.command( f'sign unplace { sign_id } group={ group }' )


def UnplaceSigns( group, filepath ):
  utils.Call( 'sign_unplace', group, { 'buffer': filepath } )


def GetPlaced( filepath, group, line ):
  return utils.Call( 'sign_getplaced', filepath, {
    'group': group,
    'lnum': line
  } )[ 0 ][ 'signs' ]



# vim: sw=2
