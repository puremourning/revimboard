" revimboard - A ReviewBoard client for VIM
" 
" Copyright 2021 Ben Jackson
" 
" Licensed under the Apache License, Version 2.0 (the "License");
" you may not use this file except in compliance with the License.
" You may obtain a copy of the License at
" 
"     http://www.apache.org/licenses/LICENSE-2.0
" 
" Unless required by applicable law or agreed to in writing, software
" distributed under the License is distributed on an "AS IS" BASIS,
" WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
" See the License for the specific language governing permissions and
" limitations under the License.


let s:cpoptions = &cpoptions
set cpoptions&vim

let s:init = v:false

function s:Init()
  if s:init
    return
  endif

  py3 << trim EOF
    import revimboard
    revimboard.init.SetUpPython( vim.eval( 'g:revimboard_home' ) )
    revimboard_session = None
  EOF
  let s:init = v:true
endfunction

function s:CheckSession()
  call s:Init()

  if py3eval( 'not revimboard_session' )
    echom "Need to call revimboard#Connect() first"
    return
  endif
endfunction

function revimboard#Connect()
  call s:Init()

  call inputsave()


  let project_root = input( "Project Root: ", getcwd(), "dir" )
  let server = input( "Server address: " )
  let username = input( "Username: " )
  let password = inputsecret( "Password:" )
  let review_req_id = input( "Review ID: " )
  let diff_revision = input( "Diff revision: ", "1" )

  call inputrestore()

  call revimboard#SetCurrentDiff(
        \ project_root,
        \ server,
        \ review_req_id,
        \ diff_revision,
        \ username,
        \ password )

endfunction

" FIXME: Allow any options for the rbtools client ?
function! revimboard#SetCurrentDiff(
      \ project_root,
      \ server,
      \ review_req_id,
      \ diff_revision,
      \ username,
      \ password )
  call s:Init()

  py3 << trim EOF
    revimboard_session = revimboard.init.Connect(
      vim.eval( 'a:project_root' ),
      vim.eval( 'a:server' ),
      username = vim.eval( 'a:username' ),
      password = vim.eval( 'a:password' ) )

    revimboard_session.SetCurrentDiff( vim.eval( 'a:review_req_id' ),
                                       vim.eval( 'a:diff_revision' ) )
  EOF
endfunction

function! revimboard#AddCommentFromSelection()
  call s:CheckSession()

  py3 << trim EOF
    line1, _ = vim.current.buffer.mark( '<' )
    line2, _ = vim.current.buffer.mark( '>' )

    import vimspector.utils
    comment = vimspector.utils.AskForInput( "Comment: " )

    if comment is not None:
      revimboard_session.AddComment( vim.current.buffer.name,
                                     line1,
                                     line2,
                                     comment )
  EOF
endfunction

function! revimboard#AddComment( line1, line2, comment )
  call s:CheckSession()

  py3 << trim EOF
    revimboard_session.AddComment( vim.current.buffer.name,
                                   int( vim.eval( 'a:line1' ) ),
                                   int( vim.eval( 'a:line2' ) ),
                                   vim.eval( 'a:comment' ) )
  EOF
endfunction

let &cpoptions = s:cpoptions

" vim: sw=2
