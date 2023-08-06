import sys


if sys.version_info < (2, 7):
    import unittest2 as unittest  # noqa
else:
    import unittest  # noqa
