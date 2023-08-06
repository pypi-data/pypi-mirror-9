from __future__ import unicode_literals

# pylint:disable=invalid-name
PY2 = str is bytes
PY3 = str is not bytes

if PY2:  # pragma: no cover (PY2 only)
    text = unicode  # flake8: noqa

    def n(s):
        if isinstance(s, bytes):
            return s
        else:
            return s.encode('UTF-8')
else:  # pragma: no cover (PY3 only)
    text = str

    def n(s):
        if isinstance(s, text):
            return s
        else:
            return s.decode('UTF-8')
