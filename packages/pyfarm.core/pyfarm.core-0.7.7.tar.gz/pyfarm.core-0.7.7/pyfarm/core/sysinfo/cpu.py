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
CPU
---

Contains information about the cpu and its relation to the operating
system such as load, processing times, etc.
"""

import psutil

# TODO: add 'logical' option to get only the real core count
# TODO: use new psutil function
# TODO: add normalized keyword (since hyperthreading/etc is
# not 100% the same as a real core)
def total_cpus():
    """Returns the total number of cpus installed on the system."""
    return psutil.NUM_CPUS


def load(self, iterval=1):
    """
    Returns the load across all cpus value from zero to one.  A value
    of 1.0 means the average load across all cpus is 100%.
    """
    return psutil.cpu_percent(iterval) / self.NUM_CPUS  # pragma: no cover


def user_time():
    """
    Returns the amount of time spent by the cpu in user
    space
    """
    return psutil.cpu_times().user


def system_time():
    """
    Returns the amount of time spent by the cpu in system
    space
    """
    return psutil.cpu_times().system


def idle_time():
    """
    Returns the amount of time spent by the cpu in idle
    space
    """
    return psutil.cpu_times().idle


def iowait():
    """
    Returns the amount of time spent by the cpu waiting
    on io

    .. note::
        on platforms other than linux this will return None
    """
    try:
        cpu_times = psutil.cpu_times()
        if hasattr(cpu_times, "iowait"):
            return psutil.cpu_times().iowait
    except AttributeError:  # pragma: no cover
        return None