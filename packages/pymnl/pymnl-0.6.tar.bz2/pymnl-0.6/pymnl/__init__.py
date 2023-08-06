# -*- coding: utf-8 -*-
#
# pymnl -- a minimalistic pure Python interface for netlink
# Copyright 2011,2015 Sean Robinson <robinson@tuxfamily.org>
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public License
#  as published by the Free Software Foundation; either version 2.1 of
#  the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA
#
# This module is heavily influenced by the excellent libmnl
# from Pablo Neira Ayuso <pablo@netfilter.org>.  However,
# pymnl does not use libmnl.

"""
The NETLINK_* constants in this module help determine which family
(a.k.a. sub-protocol or socket bus) to connect with.  For example::

    >>> import pymnl
    >>> import pymnl.nlsocket
    >>> sock = pymnl.nlsocket.Socket(pymnl.NETLINK_ROUTE)
    >>> sock.bind()

will bind :data:`sock` to the kernel's routing information so that
queries can be run and changes can be requested.


========================= ================
Family Name               Family Function
========================= ================
NETLINK_ROUTE             Routing/device hook
NETLINK_UNUSED            Unused number
NETLINK_USERSOCK          Reserved for user mode socket protocols
NETLINK_FIREWALL          Firewalling hook
NETLINK_INET_DIAG         INET socket monitoring
NETLINK_NFLOG             netfilter/iptables ULOG
NETLINK_XFRM              ipsec
NETLINK_SELINUX           SELinux event notifications
NETLINK_ISCSI             Open-iSCSI
NETLINK_AUDIT             auditing
NETLINK_FIB_LOOKUP
NETLINK_CONNECTOR
NETLINK_NETFILTER         netfilter subsystem
NETLINK_IP6_FW
NETLINK_DNRTMSG           DECnet routing messages
NETLINK_KOBJECT_UEVENT    Kernel messages to userspace
NETLINK_GENERIC
NETLINK_SCSITRANSPORT     SCSI Transports
NETLINK_ECRYPTFS
NETLINK_RDMA
NETLINK_CRYPT             Crypto layer
========================= ================

.. data:: MAX_LINKS

.. data:: NET_MAJOR

    Major 36 is reserved for networking
"""


def PYMNL_ALIGN(align_size):
    """ Return a function to calculate alignment.

        Only works with alignment on powers of 2.
    """
    return lambda len: (((len) + align_size - 1) & ~(align_size - 1))

#
# linux/netlink.h
#

# netlink types
NETLINK_ROUTE = 0             # Routing/device hook
NETLINK_UNUSED = 1            # Unused number
NETLINK_USERSOCK = 2          # Reserved for user mode socket protocols
NETLINK_FIREWALL = 3          # Firewalling hook
NETLINK_INET_DIAG = 4         # INET socket monitoring
NETLINK_NFLOG = 5             # netfilter/iptables ULOG
NETLINK_XFRM = 6              # ipsec
NETLINK_SELINUX = 7           # SELinux event notifications
NETLINK_ISCSI = 8             # Open-iSCSI
NETLINK_AUDIT = 9             # auditing
NETLINK_FIB_LOOKUP = 10
NETLINK_CONNECTOR = 11
NETLINK_NETFILTER = 12        # netfilter subsystem
NETLINK_IP6_FW = 13
NETLINK_DNRTMSG = 14          # DECnet routing messages
NETLINK_KOBJECT_UEVENT = 15   # Kernel messages to userspace
NETLINK_GENERIC = 16
NETLINK_SCSITRANSPORT = 18    # SCSI Transports
NETLINK_ECRYPTFS = 19
NETLINK_RDMA = 20
NETLINK_CRYPTO = 21           # Crypto layer

MAX_LINKS = 32

NET_MAJOR = 36          # Major 36 is reserved for networking
