Documentation for pymnl
=======================

pymnl (rhymes with hymnal) is a pure Python re-implmentation of libmnl
and provides a minimal interface to Linux Netlink sockets and messages.
The author and maintainer is Sean Robinson <robinson@tuxfamily.org>.

pymnl should be compatible with Python > 2.4.  An effort has been made
to allow pymnl to work with Py2 and Py3 from a single code base.  See
`"Using pymnl with Python 2 vs Python 3" <python-versions.html>`_
for version-specific caveats.

More information is available at http://pymnl.tuxfamily.org.

See the `API checklist <api-checklist.html>`_ for a detailed list of
which libmnl functions have been implemented.

A short `changelog <Changelog.html>`_ describes the general and API
changes for every release.


Example Applications
--------------------

The examples directory contains small examples of how to use pymnl with
various Netlink protocols.  These are re-implementations of the examples
provided in libmnl.


License
-------

pymnl is licensed under `LGPLv2+ <LICENSE.LGPL.html>`_, however, the
examples are licensed under `GPLv2+ <LICENSE.GPL.html>`_.


Modules
-------

    * `pymnl <pymnl.html>`_
    * `pymnl.attributes <attributes.html>`_
    * `pymnl.genl <genl.html>`_
    * `pymnl.message <message.html>`_
    * `pymnl.nlsocket <nlsocket.html>`_


Warranty
--------

There is none.  Do not rely on it for anything.  It could cause your
computer to apply for a second mortgage on your home, take your underage
children to R-rated movies, or run around your neighborhood in the middle
of the night ringing doorbells.  You. Have. Been. Warned.


.. toctree::
   :hidden:

   pymnl
   attributes
   genl
   message
   nlsocket
   python-versions
   api-checklist
   Changelog
   LICENSE.GPL
   LICENSE.LGPL


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
