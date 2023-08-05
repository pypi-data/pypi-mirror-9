#!/usr/bin/env python
"""Get version of a package/module with one function call.

Example:

    >>> import django, tornado, flask
    >>> from v import v
    >>> v(django)
    ((1, 3, 1, 'final', 0), 'VERSION')
    >>> v(tornado)
    ('4.0.2', 'version')
    >>> v(flask)
    ('0.9', '__version__')
"""

__version__ = __VERSION__ = version = VERSION = (1, 0)

ATTRIBUTES = (
    'VERSION',
    'version',
    '__version__',
    '__VERSION__'
)


class UnknownVersion(Exception):
    """Raised if a version of a package/module is unknown.
    """


def v(module):
    """Return value and name of the attribute specifying a version of a module.
    """
    for attr in ATTRIBUTES:
        if hasattr(module, attr):
            version = getattr(module, attr)
            return version, attr
    raise UnknownVersion('Could not determine a version of {}'.format(module.__name__))

