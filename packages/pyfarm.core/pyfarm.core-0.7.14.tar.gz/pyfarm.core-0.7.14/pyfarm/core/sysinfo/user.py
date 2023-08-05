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

"""
User
----

Returns information about the current user such as the user name, admin
access, or other related information.
"""

import os
import ctypes

pwd, getpass = None, None

try:
    import pwd

except ImportError:  # pragma: no cover
    import getpass

from pyfarm.core.sysinfo import system


def username():
    """
    Returns the current user name.  On posix based platforms this uses
    :func:`pwd.getpwuid` and on windows it falls back to
    :func:`getpass.getuser`.
    """
    if pwd is not None:
        return pwd.getpwuid(os.getuid())[0]
    elif getpass is not None:  # pragma: no cover
        return getpass.getuser()
    else:  # pragma: no cover
        raise NotImplementedError("neither `getpass` or `pwd` were imported")


def is_administrator():  # pragma: no cover
    """
    Return True if the current user is root (Linux) or running as an
    Administrator (Windows).
    """
    if system.IS_POSIX:
        return os.getuid() == 0
    elif system.IS_WINDOWS:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

    osname = system.OS(system.OS())
    raise NotImplementedError("`is_administrator` is not implemented for %s" % osname)
