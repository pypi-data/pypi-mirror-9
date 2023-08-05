# No shebang line, this module is meant to be imported
#
# Copyright 2013 Oliver Palmer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import shutil
import tempfile
from functools import wraps
from nose.plugins.skip import SkipTest

from pyfarm.core.enums import PY26

if PY26:
    import unittest2 as unittest
else:
    import unittest


def skip_on_ci(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "BUILDBOT_UUID" in os.environ or "TRAVIS" in os.environ:
            raise SkipTest
        return func(*args, **kwargs)
    return wrapper


def requires_ci(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "BUILDBOT_UUID" not in os.environ or "TRAVIS" not in os.environ:
            raise SkipTest
        return func(*args, **kwargs)
    return wrapper

from pyfarm.core.enums import STRING_TYPES


def rm(path):
    try:
        os.remove(path)
    except Exception:
        pass
    try:
        shutil.rmtree(path)
    except Exception:
        pass


class TestCase(unittest.TestCase):
    TEMPDIR_PREFIX = ""
    ORIGINAL_ENVIRONMENT = {}
    temp_directories = set()

    @classmethod
    def remove(cls, path):
        assert isinstance(path, STRING_TYPES), "expected a string for `path`"

        if os.path.isfile(path):
            delete = os.remove
        elif os.path.isdir(path):
            delete = shutil.rmtree
        else:
            delete = lambda path: None

        # delete the path
        try:
            delete(path)

        except (OSError, IOError):
            pass

        else:
            if path in cls.temp_directories:
                cls.temp_directories.remove(path)

    @classmethod
    def setUpClass(cls):
        cls.ORIGINAL_ENVIRONMENT = os.environ.copy()

    @classmethod
    def mktempdir(cls):
        tempdir = tempfile.mkdtemp(prefix=cls.TEMPDIR_PREFIX)
        cls.temp_directories.add(tempdir)
        return tempdir

    def setUp(self):
        self.tempdir = self.mktempdir()
        os.environ.clear()
        os.environ.update(self.ORIGINAL_ENVIRONMENT)

    def tearDown(self):
        try:
            self.remove(self.tempdir)
            map(self.remove, self.temp_directories.copy())
        except AttributeError:
            pass

    def add_cleanup_path(self, path):
        self.addCleanup(rm, path)
