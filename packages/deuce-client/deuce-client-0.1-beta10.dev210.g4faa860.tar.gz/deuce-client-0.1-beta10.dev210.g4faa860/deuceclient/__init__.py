"""
Deuce Client API
"""

__DEUCECLIENT_VERSION__ = {
    'major': 0,
    'minor': 1
}


def version():
    """Return the Deuce Client Version"""
    return '{0:}.{1:}'.format(__DEUCECLIENT_VERSION__['major'],
                              __DEUCECLIENT_VERSION__['minor'])
