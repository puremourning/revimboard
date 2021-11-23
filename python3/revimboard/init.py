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

import sys
import os

# Do not import any revimboard stuff here
from vimspector import utils


def SetUpPython( base_dir: str ):
    sys.path.insert( 0, os.path.join( base_dir, 'vendor', 'rbtools' ) )

    try:
        from rbtools.api import client as rbclient # noqa
    except ImportError:
        utils.UserMessage( "Can't import rbtools api client" )


def SelfTest():
    from rbtools.api import client as rbclient

    client = rbclient.RBClient( "http://reviews" )
    root = client.get_root()

    print( str( root ) )


def Connect( *args , **kwargs ):
    from revimboard import session
    return session.Session( *args, **kwargs )
