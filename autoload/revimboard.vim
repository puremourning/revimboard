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
    echohl WarningMsg
    echom "Need to call revimboard#Connect() first"
    echohl None
    return v:false
  endif

  return v:true
endfunction

function revimboard#Connect( ... )
  call s:Init()

  call inputsave()


  if a:0 > 0
    if a:1 == '.'
      let project_root = getcwd()
    else
      let project_root = expand( a:1 )
    endif
  else
    let project_root = input( "Project Root: ", getcwd(), "dir" )
  endif

  if a:0 > 1
    let server = a:2
  else
    let server = input( "Server address: " )
  endif

  if a:0 > 2
    let username = a:3
  else
    let username = input( "Username: " )
  endif

  if a:0 > 3 && a:4 != "*"
    let password = a:4
  else
    let password = inputsecret( "Password: " )
  endif

  if a:0 > 4
    let review_req_id = a:5
  else
    let review_req_id = input( "Review ID: " )
  endif

  " TODO: get latest revision for review_req_id and make default
  if a:0 > 5
    let diff_revision = a:6
  else
    let diff_revision = input( "Diff revision: ", "1" )
  endif

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

function! revimboard#AddComment( ... ) range
  if !s:CheckSession()
    return
  endif

  if a:firstline < 1
    let firstline = line( '.' )
    let lastline = line( '.' )
  else
    let firstline = a:firstline
    let lastline = a:lastline
  endif

  if a:0 == 0
    call inputsave()
    " TODO: Switch to some UI/buffer that can accept the input, e.g.
    " Split a new buffer and make it current
    " have some BufClose ? event
    " have some mapping <ctrl-enter> ?
    " hmmmm
    let args = {
          \ 'text': input( "Comment: " ),
          \ 'issue_opened': input( "Raise Issue Y/N? ", "Y" ) == "Y",
          \ 'text_type': ( input( "Markdown? ", "Y" ) == "Y" )
          \              ? "markdown" 
          \              : "plain",
          \ }
    call inputrestore()
  elseif type( a:1 ) == v:t_string
    let args = {
          \ 'text': a:1
          \ }
  elseif type( a:1 ) == v:t_dict
    let args = a:1
  endif

  py3 << trim EOF
    revimboard_session.AddComment( vim.current.buffer,
                                   int( vim.eval( 'firstline' ) ),
                                   int( vim.eval( 'lastline' ) ),
                                   **vim.eval( 'args' ) )
  EOF
endfunction

function! revimboard#DeleteComment( ... )
  if !s:CheckSession()
    return
  endif

  py3 << trim EOF
    revimboard_session.DeleteComment( vim.current.buffer,
                                      vim.current.window.cursor[ 0 ] )
  EOF

endfunction


function! revimboard#ShowComment()
  if !s:CheckSession()
    return
  endif

  py3 << trim EOF
    revimboard_session.ShowComment( vim.current.buffer,
                                    vim.current.window.cursor[ 0 ] )
  EOF

endfunction

let &cpoptions = s:cpoptions

" vim: sw=2
