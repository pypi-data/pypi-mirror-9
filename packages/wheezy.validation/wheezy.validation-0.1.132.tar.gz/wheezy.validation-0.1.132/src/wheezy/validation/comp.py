
""" ``comp`` module.
"""

import sys

from gettext import NullTranslations


PY_MAJOR = sys.version_info[0]
PY_MINOR = sys.version_info[1]
PY2 = PY_MAJOR == 2
PY3 = PY_MAJOR >= 3
null_translations = NullTranslations()

if PY3:  # pragma: nocover
    def iterkeys(d):
        return d.keys()

    def iteritems(d):
        return d.items()

    def copyitems(d):
        return list(d.items())

    regex_pattern = (str,)
else:  # pragma: nocover
    def iterkeys(d):
        return d.iterkeys()

    def iteritems(d):
        return d.iteritems()

    def copyitems(d):
        return d.items()

    regex_pattern = (str, unicode)

if PY3:  # pragma: nocover
    def ref_gettext(t):
        return t.gettext
else:  # pragma: nocover
    def ref_gettext(t):
        return t.ugettext


def ref_getter(model):
    # if model is a dict
    if hasattr(model, '__iter__'):
        return type(model).__getitem__
    else:
        return getattr


if PY3 and PY_MINOR >= 3:  # pragma: nocover
    from decimal import Decimal
else:  # pragma: nocover
    try:
        from cdecimal import Decimal  # noqa
    except ImportError:
        from decimal import Decimal  # noqa


if PY2 and PY_MINOR == 4:  # pragma: nocover
    __import__ = __import__
else:  # pragma: nocover
    # perform absolute import
    __saved_import__ = __import__

    def __import__(n, g=None, l=None, f=None):
        return __saved_import__(n, g, l, f, 0)
