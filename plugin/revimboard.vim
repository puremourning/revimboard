" py3 revimboard_session.MakeComment('src/tcl/testKit_TestLibFoundation.tcl', 299, 300, 'test' )
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

" Boilerplate {{{
if !has( 'python3' )
  echohl WarningMsg
  echom 'Revimboard unavailable: Requires Vim compiled with +python3'
  echohl None
  finish
endif

let s:cpoptions = &cpoptions
set cpoptions&vim

if exists( 'g:loaded_revimbaord' )
  let &cpoptions = s:cpoptions
  finish
endif
" }}}

let g:loaded_revimbaord = 1
let g:revimboard_home = expand( '<sfile>:p:h:h' )

nnoremap <silent> <Plug>(ReVimBoardAddComment)
      \ :call revimboard#AddComment()<CR>
xnoremap <silent> <Plug>(ReVimBoardAddComment)
      \ :call revimboard#AddComment()<CR>

command! -nargs=* -bar ReVimConnect
      \ call revimboard#Connect( <f-args> )
command! -range -nargs=? ReVimAddComment
      \ <line1>,<line2>call revimboard#AddComment( <f-args> )


" Boilerplate {{{
let &cpoptions = s:cpoptions
" }}}

" vim: sw=2 foldmethod=marker
