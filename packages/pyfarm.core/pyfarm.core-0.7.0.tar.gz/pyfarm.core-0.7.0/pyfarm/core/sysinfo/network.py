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
Network
-------

Returns information about the network including ip address, dns, data
sent/received, and some error information.
"""

import netifaces
import socket
import netaddr
import psutil

from pyfarm.core.logger import getLogger
from pyfarm.core.utility import convert
from pyfarm.core.sysinfo.osdata import OperatingSystemInfo

logger = getLogger("network_info")
os_info = OperatingSystemInfo()


class NetworkInfo(object):
    """
    .. note::
        This class has already been instanced onto `pyfarm.system.network`

    Namespace class which returns information about the network
    adapters and their state information.
    """
    @property
    def _iocounter(self):
        """
        Mapping to the internal network io counter class
        """
        interface = self.interface()
        values = psutil.net_io_counters(pernic=True)
        return values[interface]

    def packets_sent(self):
        """
        Returns the total number of packets sent over the network
        interface provided by :meth:`interface`
        """
        return self._iocounter.packets_sent

    def packets_received(self):
        """
        Returns the total number of packets received over the network
        interface provided by :meth:`interface`
        """
        return self._iocounter.packets_recv

    def data_sent(self):
        """
        Amount of data sent in megabytes over the network
        interface provided by :meth:`interface`
        """
        return convert.bytetomb(self._iocounter.bytes_sent)

    def data_received(self):
        """
        Amount of data received in megabytes over the network
        interface provided by :meth:`interface`
        """
        return convert.bytetomb(self._iocounter.bytes_recv)

    def incoming_error_count(self):
        """
        Returns the number of packets which we failed
        to receive on the network interface provided by :meth:`interface`
        """
        return self._iocounter.errin

    def outgoing_error_count(self):
        """
        Returns the number of packets which we failed
        to receive on the network interface provided by :meth:`interface`
        """
        return self._iocounter.errout

    def hostname(self):
        """
        Returns the the best guess hostname of this machine by comparing the
        hostname, fqdn, and reverse lookup of the ip address.
        """
        hostname_is_local = False
        hostname = socket.gethostname()
        fqdn = socket.getfqdn()

        # we might get the proper fqdn if we finish the hostname
        if fqdn == hostname:
            fqdn = socket.getfqdn(hostname + ".")

        if hostname.startswith("localhost"):
            logger.warning("hostname resolved to or contains 'locahost'")
            hostname_is_local = True

        if fqdn.startswith("localhost"):
            logger.warning("fqdn resolved to or contains 'locahost'")

        if os_info.IS_MAC and fqdn.endswith(".local"):
            logger.warning(
                "OS X appended '.local' to hostname, this may cause unexpected "
                "problems with DNS on the network")

        if hostname_is_local or fqdn != hostname:
            return fqdn
        else:
            return hostname

    def addresses(self):
        """Returns a list of all non-local ip addresses."""
        addresses = []

        for interface in self.interfaces():
            addrinfo = netifaces.ifaddresses(interface)
            for address in addrinfo.get(socket.AF_INET, []):
                addr = address.get("addr")

                if addr is not None:
                    try:
                        ip = netaddr.IPAddress(addr)
                    except ValueError:  # pragma: no cover
                        logger.error(
                            "could not convert %s to a valid IP object" % addr)
                    else:
                        if ip in IP_PRIVATE:
                            yield addr
                            addresses.append(addr)

        if not addresses:
            logger.error("no addresses could be found")

    def interfaces(self):
        """Returns the names of all valid network interface names"""
        results = []

        for name in netifaces.interfaces():
            # only add network interfaces which have IPv4
            addresses = netifaces.ifaddresses(name)

            if socket.AF_INET not in addresses:
                continue

            if any(addr.get("addr") for addr in addresses[socket.AF_INET]):
                yield name
                results.append(name)

        if not results:
            logger.warning("failed to find any interfaces")

    def interface(self, addr=None):
        """
        Based on the result from :meth:`ip` return the network interface
        in use
        """
        addr = self.ip() if addr is None else addr

        for interface in netifaces.interfaces():
            addresses = netifaces.ifaddresses(interface).get(socket.AF_INET, [])
            for address in addresses:
                if address.get("addr") == addr:
                    # in some cases we can get non-standard names
                    # off of the name, select the first name only
                    return interface.split(":")[0]

        raise ValueError(  # pragma: no cover
            "could not determine network interface for `%s`" % addr)

    def ip(self, as_object=False):
        """
        Attempts to retrieve the ip address for use on the network.  Because
        a host could have several network adapters installed this method will:

        * find all network adapters on the system which contain network
          addressable IPv4 addresses
        * measure the bytes sent/received and the packets sent/received for
          each adapter found
        * return the adapter with the most number of packets and bytes
          sent and received
        """
        # get the amount of traffic for each network interface,
        # we use this to help determine if the most active interface
        # is the interface dns provides
        sums = []
        counters = psutil.net_io_counters(pernic=True)

        for address in self.addresses():
            interface = self.interface(address)

            try:
                counter = counters[interface]

            except KeyError:  # pragma: no cover
                total_bytes = 0

            else:
                total_bytes = counter.bytes_sent + counter.bytes_recv

            sums.append((address, total_bytes))

        if not sums:  # pragma: no cover
            raise ValueError("no ip address found")

        # sort addresses based on how 'active' they appear
        sums.sort(cmp=lambda a, b: 1 if a[1] > b[1] else -1, reverse=True)

        ip = netaddr.IPAddress(sums[0][0])

        # now that we have an address, check it against some of
        # our address groups but don't raise exceptions since that
        # should be handled/fail in higher level code

        if ip in IP_SPECIAL_USE:
            logger.warning("ip() discovered a special use address")

        if ip in IP_LOOPBACK:
            logger.warning("ip() discoverd a loopback address")

        if ip in IP_LINK_LOCAL:
            logger.error("ip() discovered a link local address")

        if ip in IP_MULTICAST:
            logger.error("ip() discovered a multicast address")

        if ip in IP_BROADCAST:
            logger.error("ip() discovered a broadcast address")

        return str(ip) if not as_object else ip


IP_SPECIAL_USE = netaddr.IPNetwork("0.0.0.0/8")
IP_LINK_LOCAL = netaddr.IPNetwork("169.254.0.0/16")
IP_LOOPBACK = netaddr.IPNetwork("127.0.0.0/8")
IP_MULTICAST = netaddr.IPNetwork("224.0.0.0/4")
IP_BROADCAST = netaddr.IPNetwork("255.255.255.255")
IP_PRIVATE = netaddr.IPSet([
    netaddr.IPNetwork("10.0.0.0/8"),
    netaddr.IPNetwork("172.16.0.0/12"),
    netaddr.IPNetwork("192.168.0.0/16")])
IP_NONNETWORK = netaddr.IPSet([
    IP_SPECIAL_USE,
    IP_LINK_LOCAL,
    IP_LOOPBACK,
    IP_MULTICAST,
    IP_BROADCAST])
