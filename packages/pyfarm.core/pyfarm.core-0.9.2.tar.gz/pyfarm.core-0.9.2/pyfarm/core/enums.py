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
Enums
=====

Provides enum values for certain aspect of PyFarm.  See below for more
detailed information.


Operating System
----------------

Describes an operating system type.

.. csv-table:: **OperatingSystem**
    :header: Attribute, Description
    :widths: 10, 50

    LINUX, operating system on agent is a Linux variant
    WINDOWS, operating system on agent is a Windows variant
    MAC, operating system on agent is an Apple OS variant
    BSD, operating system on agent is a BSD variant


Agent State
-----------

The last known state of the remote agent, used for making queue decisions
and locking off resources.

.. csv-table::
    :header: Attribute, Description
    :widths: 10, 50

    OFFLINE, agent cannot be reached
    ONLINE, agent is waiting for work
    DISABLED, agent is online but cannot accept work
    RUNNING, agent is currently processing work
    ALLOC, special internal state used when the agent entry is being built


Work State
----------

The state a job or task is currently in.  These values apply more directly
to tasks as job statuses are built from task status values.

.. csv-table::
    :header: Attribute, Description
    :widths: 10, 50

    PAUSED, this task cannot be assigned right now but can be once unpaused
    RUNNING, work is currently being processed
    DONE, work is finished (previous failures may be present)
    FAILED, work as failed and cannot be continued


Use Agent Address
-----------------

Describes which address should be used to contact the agent

.. csv-table::
    :header: Attribute, Description
    :widths: 10, 50

    LOCAL, use the address which was provided by the agent
    REMOTE, use the address which we received the request from
    HOSTNAME, disregard both the local IP and the remote IP and use the hostname
    PASSIVE, agent cannot be contacted but will still request work and process jobs

:const PY_MAJOR:
    the major Python version

:const PY_MINOR:
    the minor Python version

:const PY_VERSION:
    a tuple containing the major and minor Python versions

:const PY3:
    True if running Python 3

:const PY2:
    True if running Python 2

:const PY26:
    True if running Python 2.6

:const PY27:
    True if running Python 2.7

:const NOTSET:
    Instance of the object class, mainly used when None is actually
    a valid value

:const STRING_TYPES:
    A tuple of string types, provided for Python 3 backwards compatibility

:const NUMERIC_TYPES:
    A tuple of numeric types, provided for Python 3 backwards compatibility

:const INTEGER_TYPES:
    A tuple of integer types, provided for Python 3 backwards compatibility

:const BOOLEAN_TRUE:
    A set containing strings and other objects representing ``True`` under
    some conditions.  Generally used by
    :func:`pyfarm.core.utility.convert.bool`

:const BOOLEAN_FALSE:
    A set containing strings and other objects representing ``False`` under
    some conditions.  Generally used by
    :func:`pyfarm.core.utility.convert.bool`

:const NONE:
    A set containing strings and other objects which represent ``None`` under
    some conditions.  Generally used by
    :func:`pyfarm.core.utility.convert.none`

:const INTERACTIVE_INTERPRETER:
    True when we're running inside an interactive interpreter such as
    a Python shell like IPython.  This value will also be True if
    there's an active debugger.

:const OS:
    The current os type, the value will map to one of the values in
    :class:`.OperatingSystem`

:const POSIX:
    True if ``OS in (OperatingSystem.LINUX, OperatingSystem.MAC)``

:const WINDOWS:
    True if ``OS == OperatingSystem.WINDOWS``

:const LINUX:
    True if ``OS == OperatingSystem.LINUX``

:const MAC:
    True if ``OS == OperatingSystem.MAC``
"""

import sys

# Python 2.5 is not supported across the board.  If
# somehow someone made it to this point, stop here.
PY_MAJOR, PY_MINOR = sys.version_info[0:2]
PY_VERSION = (PY_MAJOR, PY_MINOR)
if PY_VERSION <= (2, 5):  # pragma: no cover
    raise RuntimeError("Python 2.5 and below is not supported")

from collections import namedtuple

NOTSET = object()

# general Python version constants which are
# used elsewhere
PY3 = PY_MAJOR == 3
PY2 = PY_MAJOR == 2
PY26 = PY_VERSION == (2, 6)
PY27 = PY_VERSION == (2, 7)

try:  # pragma: no cover
    STRING_TYPES = (str, unicode)
    NUMERIC_TYPES = (int, long, float, complex)
    INTEGER_TYPES = (int, long)
except NameError:  # pragma: no cover
    STRING_TYPES = (str, )
    NUMERIC_TYPES = (int, float, complex)
    INTEGER_TYPES = int

# constants used by pyfarm.core.utility.convert by provided
# here so they could be reused elsewhere
BOOLEAN_TRUE = set(["1", "t", "y", "true", "yes", True, 1])
BOOLEAN_FALSE = set(["0", "f", "n", "false", "no", False, 0])
NONE = set(["none", "null", "", None, 0])

try:  # pragma: no cover
    range_ = xrange
except NameError:  # pragma: no cover
    range_ = range


def Enum(classname, **kwargs):
    """
    Produce an enum object using :func:`.namedtuple`

    >>> Foo = Enum("Foo", A=1, B=2)
    >>> assert Foo.A == 1 and Foo.B == 2
    >>> FooTemplate = Enum("Foo", A=int, instance=False)
    >>> Foo = FooTemplate(A=1)
    >>> assert Foo.A == 1

    :param str classname:
        the name of the class to produce

    :keyword to_dict:
        a callable function to add to the named tuple for
        converting the internal values into a dictionary

    :keyword bool instance:
        by default calling :func:`.Enum` will produce an instanced
        :func:`.namedtuple` object, setting ``instance`` to False
        will instead produce the named tuple without instancing it
    """
    to_dict = kwargs.pop("to_dict", None)
    instance = kwargs.pop("instance", True)
    template = namedtuple(classname, kwargs.keys())

    if to_dict is not None:
        setattr(template, "to_dict", to_dict)

    return template(**kwargs) if instance else template


class Values(namedtuple("Values", ("int", "str"))):
    """
    Stores values to be used in an enum.  Each time this
    class is instanced it will ensure that the input values
    are of the correct type and unique.
    """
    # Numerical types which are specific to the enums
    # only.
    try:
        NUMERIC_TYPES = (int, long)
    except NameError:  # pragma: no cover
        NUMERIC_TYPES = (int, )

    check_uniqueness = True
    _integers = set()

    def __init__(self, *args, **kwargs):
        if not isinstance(self.int, self.NUMERIC_TYPES):
            raise TypeError("`int` must be an number")

        if not isinstance(self.str, STRING_TYPES):
            raise TypeError("`str` must be a string")

        if self.check_uniqueness and self.int in self._integers:
            raise ValueError("value %s is being reused" % self.int)
        else:
            self._integers.add(self.int)

        self._values = set([self.int, self.str])

    def __hash__(self):
        return self.str.__hash__()

    def __int__(self):
        return self.int

    def __str__(self):
        return self.str

    def __repr__(self):  # pragma: no cover
        return "%s(%s, %s)" % (
            self.__class__.__name__, self.int, repr(self.str))

    def __contains__(self, item):
        if isinstance(item, STRING_TYPES):
            return item == self.str
        elif isinstance(item, self.NUMERIC_TYPES):
            return item == self.int
        elif isinstance(item, Values):
            return item.str == self.str and item.int == self.int
        else:  # pragma: no cover
            return False

    def __eq__(self, other):
        return self.__contains__(other)

    def __gt__(self, other):
        if isinstance(other, self.NUMERIC_TYPES):
            return other < self.int
        elif isinstance(other, Values):
            return other.int < self.int
        else:
            raise NotImplementedError("Cannot compare against %s" % type(other))

    def __ge__(self, other):
        if isinstance(other, self.NUMERIC_TYPES):
            return other <= self.int
        elif isinstance(other, Values):
            return other.int <= self.int
        else:
            raise NotImplementedError("Cannot compare against %s" % type(other))

    def __lt__(self, other):
        if isinstance(other, self.NUMERIC_TYPES):
            return other > self.int
        elif isinstance(other, Values):
            return other.int > self.int
        else:
            raise NotImplementedError("Cannot compare against %s" % type(other))

    def __le__(self, other):
        if isinstance(other, self.NUMERIC_TYPES):
            return other >= self.int
        elif isinstance(other, Values):
            return other.int >= self.int
        else:
            raise NotImplementedError("Cannot compare against %s" % type(other))


def cast_enum(enum, enum_type):
    """
    Pulls the requested ``enum_type`` from ``enum`` and produce a new
    named tuple which contains only the requested data

    >>> from pyfarm.core.enums import Enum, Values
    >>> FooBase = Enum("Foo", A=Values(int=1, str="1")
    >>> Foo = cast_enum(FooBase, str)
    >>> assert Foo.A == "1"
    >>> Foo = cast_enum(FooBase, int)
    >>> assert Foo.A == 1
    >>> assert Foo._map == {"A": 1, 1: "A"}

    .. warning::
        This function does not perform any kind of caching.  For the most
        efficient usage it should only be called once per process or
        module for a given enum and enum_type combination.
    """
    enum_data = {}
    reverse_map = {}

    # construct the reverse mapping and push
    # the request type into enum_data
    for key, value in enum._asdict().items():
        reverse_map[value.int] = value.str
        reverse_map[value.str] = value.int

        if enum_type is int:
            enum_data[key] = value.int
        elif enum_type is str:
            enum_data[key] = value.str
        else:
            raise TypeError("Valid values for `enum_type` are int or str")

    class MappedEnum(
        namedtuple(
            enum.__class__.__name__, enum_data.keys())):  # pragma: no cover
        _map = reverse_map
        _enum = enum

        def __contains__(self, item):
            if item in self._map:
                return True
            else:
                for key, value in self._enum._asdict().items():
                    if item in value:
                        return True
            return False

    return MappedEnum(**enum_data)


# 1xx - work states
# NOTE: these values are directly tested test_enums.test_direct_work_values
_WorkState = Enum(
    "WorkState",
    PAUSED=Values(100, "paused"),
    RUNNING=Values(105, "running"),
    DONE=Values(106, "done"),
    FAILED=Values(107, "failed"))

# 2xx - agent states
# NOTE: these values are directly tested test_enums.test_direct_agent_values
_AgentState = Enum(
    "AgentState",
    DISABLED=Values(200, "disabled"),
    OFFLINE=Values(201, "offline"),
    ONLINE=Values(202, "online"),
    RUNNING=Values(203, "running"))

# 3xx - non-queue related modes or states
# NOTE: these values are directly tested test_enums.test_direct_os_values
_OperatingSystem = Enum(
    "OperatingSystem",
    LINUX=Values(300, "linux"),
    WINDOWS=Values(301, "windows"),
    MAC=Values(302, "mac"),
    BSD=Values(304, "bsd"),
    OTHER=Values(303, "other"))

# NOTE: these values are directly tested test_enums.test_direct_agent_addr
_UseAgentAddress = Enum(
    "UseAgentAddress",
    LOCAL=Values(310, "local"),
    REMOTE=Values(311, "remote"),
    HOSTNAME=Values(312, "hostname"),
    PASSIVE=Values(313, "passive"))

# string versions of the enums above
WorkState = cast_enum(_WorkState, str)
AgentState = cast_enum(_AgentState, str)
OperatingSystem = cast_enum(_OperatingSystem, str)
UseAgentAddress = cast_enum(_UseAgentAddress, str)

# integer versions of the enums above, mainly declared for
# direct use within queries
DBWorkState = cast_enum(_WorkState, int)
DBAgentState = cast_enum(_AgentState, int)
DBOperatingSystem = cast_enum(_OperatingSystem, int)
DBUseAgentAddress = cast_enum(_UseAgentAddress, int)

RUNNING_WORK_STATES = set([
    WorkState.RUNNING])

DB_RUNNING_WORK_STATES = set([
    DBWorkState.RUNNING])

FAILED_WORK_STATES = set([
    WorkState.FAILED])

DB_FAILED_WORK_STATES = set([
    DBWorkState.FAILED])


def operating_system(plat=sys.platform):
    """
    Returns the operating system for the given platform.  Please
    note that while you can call this function directly you're more
    likely better off using values in :mod:`pyfarm.core.enums` instead.
    """
    if plat.startswith("linux"):
        return "linux"
    elif plat.startswith("win"):
        return "windows"
    elif plat.startswith("darwin"):
        return "mac"
    elif "bsd" in plat:
        return "bsd"
    else:
        return "other"

INTERACTIVE_INTERPRETER = hasattr(sys, "ps1") or sys.gettrace() is not None

# operating system information
OS = operating_system()
POSIX = OS in (OperatingSystem.LINUX, OperatingSystem.MAC)
WINDOWS = OS == OperatingSystem.WINDOWS
LINUX = OS == OperatingSystem.LINUX
MAC = OS == OperatingSystem.MAC
BSD = OS == OperatingSystem.BSD
