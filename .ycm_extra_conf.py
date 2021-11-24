import os

BASE = os.path.dirname( os.path.abspath( __name__ ) )


def Settings( **kwargs ):
    return {
        'sys_path': [
            os.path.join( BASE, 'vendor', 'rbtools' ),
            os.path.join( BASE, '..', 'vimspector', 'python3' )
        ]
    }
