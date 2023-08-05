import platform, sys

if platform.system() == 'Windows':  # pragma: no cover
    WIN = True
else:
    WIN = False

# True if we are running on Python 2.
PY2 = sys.version_info[0] == 2


if not PY2:  # pragma: no cover
    string_type = str
    unicode_text = str
    byte_string = bytes

    def u_(s):
        return str(s)

    def bytes_(s):
        return str(s).encode('ascii', 'strict')

else:  # pragma: no cover
    string_type = basestring
    unicode_text = unicode
    byte_string = str

    def u_(s):
        return unicode(s, 'utf-8')

    def bytes_(s):
        return str(s)


def with_metaclass(meta, base=object):
    """Create a base class with a metaclass."""
    return meta("NewBase", (base,), {})