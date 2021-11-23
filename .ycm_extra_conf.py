import os

BASE = os.path.dirname( os.path.abspath( __name__ ) )


def Setup( **kwargs ):
    return {
        'sys_path': [
            os.path.join( BASE, 'vendor/rbtools' )
        ]
    }
