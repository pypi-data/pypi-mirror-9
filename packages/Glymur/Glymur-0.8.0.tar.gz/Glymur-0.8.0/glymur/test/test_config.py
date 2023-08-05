"""These tests are for edge cases where OPENJPEG does not exist, but
OPENJP2 may be present in some form or other.
"""
import contextlib
import ctypes
import imp
import os
import sys
import tempfile
import unittest

if sys.hexversion <= 0x03030000:
    from mock import patch
else:
    from unittest.mock import patch

import glymur
from glymur import Jp2k

from .fixtures import (WARNING_INFRASTRUCTURE_ISSUE,
                       WARNING_INFRASTRUCTURE_MSG,
                       WINDOWS_TMP_FILE_MSG)


def openjpeg_not_found_by_ctypes():
    """
    Need to know if openjpeg library can be picked right up by ctypes for one
    of the tests.
    """
    with patch.dict('os.environ',
                    {'DYLD_FALLBACK_LIBRARY_PATH': '/opt/local/lib'}):
        if ctypes.util.find_library('openjpeg') is None:
            return True
        else:
            return False


@contextlib.contextmanager
def chdir(dirname=None):
    """
    This context manager restores the value of the current working directory
    (cwd) after the enclosed code block completes or raises an exception.  If a
    directory name is supplied to the context manager then the cwd is changed
    prior to running the code block.

    Shamelessly lifted from
    http://www.astropython.org/snippet/2009/10/chdir-context-manager
    """
    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)


@unittest.skipIf(sys.hexversion < 0x03020000,
                 "TemporaryDirectory introduced in 3.2.")
@unittest.skipIf(glymur.lib.openjp2.OPENJP2 is None,
                 "Needs openjp2 library first before these tests make sense.")
class TestSuite(unittest.TestCase):
    """Test suite for configuration file operation."""

    @classmethod
    def setUpClass(cls):
        imp.reload(glymur)
        imp.reload(glymur.lib.openjp2)

    @classmethod
    def tearDownClass(cls):
        imp.reload(glymur)
        imp.reload(glymur.lib.openjp2)

    def setUp(self):
        self.jp2file = glymur.data.nemo()

    def tearDown(self):
        pass

    def test_config_file_via_environ(self):
        """Verify that we can read a configuration file set via environ var."""
        with tempfile.TemporaryDirectory() as tdir:
            configdir = os.path.join(tdir, 'glymur')
            os.mkdir(configdir)
            filename = os.path.join(configdir, 'glymurrc')
            with open(filename, 'wt') as tfile:
                tfile.write('[library]\n')

                # Need to reliably recover the location of the openjp2 library,
                # so using '_name' appears to be the only way to do it.
                libloc = glymur.lib.openjp2.OPENJP2._name
                line = 'openjp2: {0}\n'.format(libloc)
                tfile.write(line)
                tfile.flush()
                with patch.dict('os.environ', {'XDG_CONFIG_HOME': tdir}):
                    imp.reload(glymur.lib.openjp2)
                    Jp2k(self.jp2file)

    @unittest.skipIf(WARNING_INFRASTRUCTURE_ISSUE, WARNING_INFRASTRUCTURE_MSG)
    @unittest.skipIf(os.name == "nt", WINDOWS_TMP_FILE_MSG)
    def test_xdg_env_config_file_is_bad(self):
        """A non-existant library location should be rejected."""
        with tempfile.TemporaryDirectory() as tdir:
            configdir = os.path.join(tdir, 'glymur')
            os.mkdir(configdir)
            fname = os.path.join(configdir, 'glymurrc')
            with open(fname, 'w') as fptr:
                with tempfile.NamedTemporaryFile(suffix='.dylib') as tfile:
                    fptr.write('[library]\n')
                    fptr.write('openjp2: {0}.not.there\n'.format(tfile.name))
                    fptr.flush()
                    with patch.dict('os.environ', {'XDG_CONFIG_HOME': tdir}):
                        # Misconfigured new configuration file should
                        # be rejected.
                        regex = 'could not be loaded'
                        with self.assertWarnsRegex(UserWarning, regex):
                            imp.reload(glymur.lib.openjp2)

    @unittest.skipIf(glymur.lib.openjp2.OPENJPEG is None,
                     "Needs openjp2 and openjpeg before this test make sense.")
    @unittest.skipIf(os.name == "nt", WINDOWS_TMP_FILE_MSG)
    def test_library_specified_as_None(self):
        """Verify that we can stop library from being loaded by using None."""
        with tempfile.TemporaryDirectory() as tdir:
            configdir = os.path.join(tdir, 'glymur')
            os.mkdir(configdir)
            fname = os.path.join(configdir, 'glymurrc')
            with open(fname, 'w') as fptr:
                # Essentially comment out openjp2 and preferentially load
                # openjpeg instead.
                fptr.write('[library]\n')
                fptr.write('openjp2: None\n')
                msg = 'openjpeg: {0}\n'
                msg = msg.format(glymur.lib.openjp2.OPENJPEG._name)
                fptr.write(msg)
                fptr.flush()
                with patch.dict('os.environ', {'XDG_CONFIG_HOME': tdir}):
                    imp.reload(glymur.lib.openjp2)
                    self.assertIsNone(glymur.lib.openjp2.OPENJP2)
                    self.assertIsNotNone(glymur.lib.openjp2.OPENJPEG)

    @unittest.skipIf(glymur.lib.openjp2.OPENJPEG is None,
                     "Needs openjpeg before this test make sense.")
    @unittest.skipIf(openjpeg_not_found_by_ctypes(),
                     "OpenJPEG must be found before this test can work.")
    @unittest.skipIf(os.name == "nt", WINDOWS_TMP_FILE_MSG)
    def test_config_dir_but_no_config_file(self):

        with tempfile.TemporaryDirectory() as tdir:
            configdir = os.path.join(tdir, 'glymur')
            os.mkdir(configdir)
            with patch.dict('os.environ', {'XDG_CONFIG_HOME': tdir}):
                # Should still be able to load openjpeg, despite the
                # configuration file not being there
                imp.reload(glymur.lib.openjpeg)
                self.assertIsNotNone(glymur.lib.openjp2.OPENJPEG)

    @unittest.skipIf(os.name == "nt", WINDOWS_TMP_FILE_MSG)
    def test_config_file_in_current_directory(self):
        """A configuration file in the current directory should be honored."""
        libloc = glymur.lib.openjp2.OPENJP2._name
        with tempfile.TemporaryDirectory() as tdir1:
            fname = os.path.join(tdir1, 'glymurrc')
            with open(fname, 'w') as fptr:
                fptr.write('[library]\n')
                fptr.write('openjp2: {0}\n'.format(libloc))
                fptr.flush()
                with chdir(tdir1):
                    # Should be able to load openjp2 as before.
                    imp.reload(glymur.lib.openjp2)
                    self.assertEqual(glymur.lib.openjp2.OPENJP2._name, libloc)
