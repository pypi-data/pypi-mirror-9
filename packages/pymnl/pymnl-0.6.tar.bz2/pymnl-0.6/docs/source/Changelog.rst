Changelog
=========

v0.1 - released March 14, 2011
------------------------------

Initial alpha version.


v0.5 - release April 17, 2011
-----------------------------

Beta version.

    * Test cases expanded to include 99% code coverage.
    * Improved documentation all over the place, including docstrings
      for many methods.
    * Messages and Payload use the print function added in Python 2.6,
      this should only affect Python 2.5 users.
    * Fixed Attr.new_* methods to be true classmethods and correctly
      instantiate subclasses.

API Change
^^^^^^^^^^

    * AttrParser now receives an optional offset at which to begin parsing.
    * Rename GenlAttrParser to GenlFamilyAttrParser.
    * The Attr.new_strnz method has been renamed to Attr.new_str.
    * Message.put_extra_header method no longer tries to prepend extra
      header to payload, but follows the behavior of libmnl.
    * Attr.get_u* methods are more strict about the size of the attribute
      value returned, no matter what attribute type is claimed.
    * AttrParser parsing methods always return a list.


v0.6 - released March 22, 2015
------------------------------

Beta version.

    * Improved documentation, including some Sphinxification.
    * Improved Makefile.
    * Clean up source as recommended by
      `pep8 <http://github.com/jcrocholl/pep8>`_.
    * Remove unused imports as recommended by
      `pyflakes <https://launchpad.net/pyflakes>`_.
    * Fixed the one failing test under Python 3.
    * Include HTML documentation in sdist package.


API Change
^^^^^^^^^^

    * Remove Netlink socket option flags from base module (duplicated from
      nlsocket module).
    * Added NETLINK_RDMA and NETLINK_CRYPTO family names.
