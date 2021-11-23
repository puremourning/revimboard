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

import os

from rbtools.api import client as rbclient
from rbtools import api as rbapi


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
  repository: rbapi.resource.ItemResource = None
  review: rbapi.resource.ItemResource = None

  def __init__( self,
                project_root: str,
                server: str,
                *args,
                **kwargs ):
    self.project_root = os.path.normpath( project_root )
    self.client = rbclient.RBClient( server, *args, **kwargs )
    self.root = self.client.get_root()

  # Must haves:
  #  - rely on .reviewboardrc, making connection options optional
  #  - get comment text from a drawer-like buffer rather than cmdline
  #  - toggle for issue/not issue, markdown/plain etc.
  #  - overall review comments (or just say use browser) ?
  #
  # Ideas:
  #  - open the review in browser for final submit ?
  #  - automatically apply rbt patch by matching some file in the project ? hmm
  #      not sure about that
  #  - load open diff comments from all reviews and add them as signs with
  #    "virtual text" (popup)
  #  - allow replying to comments

  def SetCurrentDiff( self,
                      review_request_id: int,
                      diff_revision: int ):
    self.review_request = self.root.get_review_request(
      review_request_id = review_request_id )
    self.repository = self.review_request.get_repository()
    self.diff = self.root.get_diff( review_request_id = review_request_id,
                                    diff_revision = diff_revision )


  def AddComment( self,
                  filepath: str,
                  line1: int,
                  line2: int,
                  comment: str ):
    self._StartReviewIfNeeded()

    file_diff = self._FindFileDiff( filepath )

    self.review.get_diff_comments().create(
      filediff_id = file_diff.id,
      first_line = line1,
      num_lines = ( line2 - line1 ) + 1, # include line2 in the comment
      issue_opened = True,
      text_type = 'markdown',
      text = comment )


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

    if shortest_matched_candidate is None:
      raise RuntimeError( f"Could not file a diff for { filepath } in "
                          "files: { self.diff.get_files() }" )

    return shortest_matched_candidate


# vim: sw=2
