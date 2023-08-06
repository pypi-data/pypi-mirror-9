import sys

if sys.version_info < (2, 7):
    from path import Path
else: #Pathlib seems to only support python 2.7 and up
    from pathlib import Path

if sys.version_info < (2, 7):
    import unittest2 as unittest
else: #unittest2 is needed for python less then 2.6
    import unittest

del sys
