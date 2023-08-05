# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function

import os
import tempfile
import unittest
import re
import shutil


class Test(unittest.TestCase):

    ## XXXvlab: it seems it's already there in PY3 and maybe PY2,
    ## so why keep it ?
    def assertContains(self, haystack, needle, msg=None):
        if not msg:
            msg = "%r should contain %r." % (haystack, needle)
        self.assertTrue(needle in haystack, msg)

    def assertNotContains(self, haystack, needle, msg=None):
        if not msg:
            msg = "%r should not contain %r." % (haystack, needle)
        self.assertTrue(needle not in haystack, msg)

    def assertRegex(self, text, regex, msg=None):
        if not msg:
            msg = "%r should match regex %r." % (text, regex)
        self.assertTrue(re.search(regex, text, re.MULTILINE) is not None, msg)


class BaseTmpDirTest(Test):

    def setUp(self):
        ## put an empty tmp directory up
        self.old_cwd = os.getcwd()
        self.tmpdir = tempfile.mkdtemp()
        os.chdir(self.tmpdir)

    def tearDown(self):
        ## delete the tmp directory
        os.chdir(self.old_cwd)
        shutil.rmtree(self.tmpdir)


def run(test):
    from pprint import pprint
    try:
        from StringIO import StringIO
    except ImportError:  ## PY3
        from io import StringIO
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream)
    runner.run(unittest.makeSuite(test))
    stream.seek(0)
    print(stream.read())
