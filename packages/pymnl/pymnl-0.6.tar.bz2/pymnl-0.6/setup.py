#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

from pymnl.tests.testcommand import test

def get_version():
    version_file = open("docs/VERSION")
    try:
        version = version_file.readline()
    finally:
        version_file.close()
    return version[:-1]

setup(
    name = "pymnl",
    version = get_version(),
    author = "Sean Robinson",
    author_email = "robinson@tuxfamily.org",
    maintainer_email = "pymnl-dev@lists.tuxfamily.org",
    description = """
pymnl (rhymes with hymnal) is a pure Python re-implmentation of libmnl and
provides a minimal, object-oriented interface to Linux Netlink sockets and
messages.""",
    url = "http://pymnl.tuxfamily.org/",
    packages = ['pymnl', 'pymnl.tests'],
    provides = ['pymnl'],

    platforms = "Linux",
    license = "LGPL for module; GPL for example scripts",
    keywords = "Netlink genl rtnl socket",
    download_url = "http://downloads.tuxfamily.org/pymnl/",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System',
    ],
    cmdclass={'test': test},
)

