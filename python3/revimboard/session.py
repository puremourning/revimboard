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

import os

from rbtools.api import client as rbclient
import rbtools.api.errors as rberrors
from rbtools import api as rbapi

# TODO: hack/use this to load reviewboardrc
# import rbtools.utils.filesystem

import vimspector.utils

from revimboard import api_errors, editor, popup, signs


class Session( object ):
  # RB "data" model
  #
  # Review Request - Top level review thing
  #   - Diff - "revision" of the review (called a diff in reviewboard)
  #     - File Diff - diff of a specific file in that Diff
  #       - File Diff Comment
  #       - Original File
  #       - Patched File
  #
  project_root: str = None
  client: rbclient.RBClient = None
  root: rbapi.resource.RootResource = None
  review_request: rbapi.resource.ReviewRequestResource = None
  review: rbapi.resource.ItemResource = None
  diff: rbapi.resource.DiffResource = None

  def __init__( self,
                project_root: str,
                server: str,
                *args,
                **kwargs ):
    self.project_root = os.path.normpath( project_root )
    self.client = rbclient.RBClient( server, *args, **kwargs )
    self.root = self.client.get_root()

    if not signs.SignDefined( 'ReVimPendingComment' ):
      signs.DefineSign( 'ReVimPendingComment',
                        text = 'c',
                        double_text = 'c',
                        texthl = 'SpellRare' )

  # Must haves:
  #  - rely on .reviewboardrc, making connection options optional
  #  - proper API error handling; it' snot really ok to let the exceptions
  #    bubble as they do now
  #  - get comment text from a drawer-like buffer rather than cmdline
  #  - toggle for issue/not issue, markdown/plain etc.
  #  - view overall review comments (or just say use browser) ?
  #  - load open diff comments from all reviews and add them as signs with
  #    "virtual text" (popup)
  #
  #  - do some operations async because the reviewboard server is _ridiculously_
  #    slow, but how, poll timer :(?
  #
  # Ideas:
  #  - open the review in browser for final submit ?
  #  - automatically apply rbt patch by matching some file in the project ? hmm
  #      not sure about that
  #  - allow replying to comments

  def SetCurrentDiff( self, review_request_id: int, diff_revision: int ):
    self.review_request = self.root.get_review_request(
      review_request_id = review_request_id )
    self.diff = self.root.get_diff( review_request_id = review_request_id,
                                    diff_revision = diff_revision )

    self._LoadDraftReview()


  def AddComment( self, buffer: vim.Buffer, line1: int, line2: int, **kwargs ):
    self._StartReviewIfNeeded()

    def PutComment( text, **kwargs ):
      # TODO(Ben) : Temp - we probably want something per-buffer like
      # b:revimboard_file_diff_id
      filepath = buffer.name
      file_diff = self._FindFileDiff( filepath )
      if not file_diff:
        raise RuntimeError(
          f"Could not file a diff for { filepath } in "
          f"Review { self.review.id } diff revision { self.diff.revision }" )

      self.review.get_diff_comments().create(
        filediff_id = file_diff.id,
        first_line = line1,
        num_lines = ( line2 - line1 ) + 1, # include line2 in the comment
        text = text,
        **kwargs )

      # TODO(Ben): There seems to be a classic race here, that if we request the
      # comments we just added, they aren't there! Great work, reviewboard. top
      # class
      self._UpdatePendingCommentsInBuffer( buffer )

    text = kwargs.pop( 'text', None )

    if not text:
      template_text = "<!-- Put the comment here -->"

      def HandleComment( text ):
        if not text or text == template_text:
          return

        def handle_choice( choice ):
          if choice < 0:
            return

          kwargs.update( {
            'issue_opened': choice == 1,
            'text_type': 'markdown'
          } )
          PutComment( text, **kwargs )

        vimspector.utils.Confirm( '',
                                  'Raise issue?',
                                  handle_choice,
                                  default_value = 1,
                                  options = [ '(Y)es', '(N)o' ],
                                  keys = [ 'y', 'n']  )

      return editor.OpenEditor( template_text, 'markdown', HandleComment )

    return PutComment( text, **kwargs )


  def _AllCommentsOnLine( self, buffer: vim.Buffer, line: int ):
    # find the diff comment at that line
    line_signs = signs.GetPlaced( filepath = buffer.name,
                                  group = 'ReVimReview',
                                  line = line )

    comments = self.review.get_diff_comments( line = line )

    for sign in line_signs:
      for comment in comments:
        if comment.id == int( sign[ 'id' ] ):
          yield comment


  def DeleteComment( self, buffer: vim.Buffer, line: int ):
    for comment in self._AllCommentsOnLine( buffer, line ):
      comment.delete()

    self._UpdatePendingCommentsInBuffer( buffer )


  def ShowComment( self, buffer: vim.Buffer, line: int ):
    for comment in self._AllCommentsOnLine( buffer, line ):
      popup.AtFirstColumn( line, comment.text, 'markdown' )
      # TODO(Ben): What to do if we have multiple comments on this line
      return


  def _LoadDraftReview( self ):
    try:
      self.review = self.root.get_review_draft(
        review_request_id = self.review_request.id )

      # TODO(Ben) if it's not a draft...
      # if self.review.public:
      #   self.review = None

      for buffer in vim.buffers:
        self._UpdatePendingCommentsInBuffer( buffer )
    except rberrors.APIError as e:
      if e.error_code != api_errors.DOES_NOT_EXIST:
        raise


  def _UpdatePendingCommentsInBuffer( self, buffer ):
    file_diff = self._FindFileDiff( buffer.name )
    if not file_diff:
      return

    signs.UnplaceSigns( filepath=buffer.name, group='ReVimReview' )

    for diff_comment in self.review.get_diff_comments():
      if diff_comment.get_filediff().id == file_diff.id:
        signs.PlaceSign( diff_comment.id,
                         'ReVimReview',
                         'ReVimPendingComment',
                         buffer.name,
                         diff_comment.first_line )

        # TODO(Ben): Place a text property
        # TODO(Ben): Attach a popup to the text property?


  def _StartReviewIfNeeded( self ):
    if not self.review:
      self.review = self.review_request.get_reviews().create(
        body_top = "Made in VIM!",
        body_top_text_type = "plain" )


  def _FindFileDiff( self, filepath: str ) -> rbapi.resource.FileDiffResource:
    filepath = os.path.normpath( filepath )

    # if filepath doesn't start with self.project_root ... help ?
    if not filepath.startswith( self.project_root ):
      raise RuntimeError( "That file ain't in the project!" )

    match_path = filepath[ len( self.project_root ): ]

    #
    # Find the file diffs whose path ends with the path of the
    # supplied file relative to the project root. Then pick the one with the
    # shortest overall (canonical )path. (this is the best matching one)
    #
    # Example:
    #
    # project root: /project/root
    # filepath: /project/root/src/Makefile
    # match_path: src/Makefile
    #
    # Perforce paths:
    #
    # * //depot/PATH/Makefile
    #    - suffix Does not match
    # * //depot/PATH/src/Makefile
    #    - Matches with len = 25            <- best match
    # * //depot/PATH/src/test/Makefile
    #    - suffix does not match
    # * //depot/PATH/src/test/src/Makefile
    #    - matches with len: 34
    #
    # Git repo-relative paths:
    #
    # * Makefile
    #  - suffix does not match
    # * src/Makefilwe
    #  - Matches with len= 13               <- best match
    # * src/test/Makefile
    #  - suffix does not match
    # * src/test/src/Makefile
    #  - matches with len = 21
    #
    shortest_matched_len: int = None
    shortest_matched_candidate = None

    for file_diff in self.diff.get_files():
      candidate_path: str = file_diff.dest_file

      if not candidate_path.endswith( match_path ):
        continue

      if ( not shortest_matched_len
           or len( candidate_path ) < shortest_matched_len ):
        shortest_matched_len = len( candidate_path )
        shortest_matched_candidate = file_diff

    return shortest_matched_candidate


# vim: sw=2
