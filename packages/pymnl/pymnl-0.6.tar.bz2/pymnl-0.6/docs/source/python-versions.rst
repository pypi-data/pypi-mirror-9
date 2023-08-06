Using pymnl with Python 2 vs Python 3
=====================================

Using pymnl With Python 2
-------------------------

Recommend Using b'' For Strings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To help you remember that strings are treated as 8-bit (non-unicode), use
the b'' decoration on strings headed for Netlink.  If you want to hardcode
the genl family name nl80211 in your script, using b'nl80211' should
highlight the type of the string.  While this is not vital in Py2, it will
make it easier to transfer your code to Py3 in the future.


Attr Expects 8-bit Strings
^^^^^^^^^^^^^^^^^^^^^^^^^^

Attr.new_str() and Attr.new_strz() expect an 8-bit (non-unicode) string.
Because this is the default type for Py2 strings, no special considerations
are required, but it is recommended to use the b'' decoration as shown
above.


Examples Use __future__ print()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To be compatible with Py2 and Py3, the example scripts in ./examples/ use
the new print function included starting in Python 2.6.  I.E.::

        from __future__ import print_function

While the library should work with Python versions greater than 2.4, the
examples, as written, require at least Python 2.6.


Using pymnl With Python 3
-------------------------

bytes Versus string
^^^^^^^^^^^^^^^^^^^

pymnl uses 8-bit (non-unicode) strings.  Passing unicode strings into pymnl
will cause problems, either immediately or once your data is passed to
Netlink.  To ensure your strings are of the right type, use the b''
decoration.  So, the hardcoded genl family name nl80211 in your script
should be written as b'nl80211'.

Conversely, the strings coming out of Netlink are 8-bit and will print like
b'string'.  At some point, you may want to decode the bytes into a string.
In Python 3.x, this code snippet (adapted from genl-family-get.py)::

    print("name=%s\tid=%u" % (attrs['name'], attrs['id']))
    print("name=%s\tid=%u" % (attrs['name'].decode(), attrs['id']))

would have an output similar to this::

    name=b'nl80211' id=17
    name=nl80211    id=17


Attr Expects 8-bit Strings
^^^^^^^^^^^^^^^^^^^^^^^^^^

Attr.new_str() and Attr.new_strz() expect an 8-bit (non-unicode) string.
To ensure that you are passing the correct string type, use strings.encode().
An example (adapted from genl-family-get.py)::

    Attr.new_strz(CTRL_ATTR_FAMILY_NAME, sys.argv[1].encode())

Notice that sys.argv[1] is encoded before being passed to new_strz().


Attr Returns 8-bit Strings
^^^^^^^^^^^^^^^^^^^^^^^^^^

Attr.get_str_stripped() and Attr.get_str() return an 8-bit string, which
in Py3 is a bytes.  An example, while code in Py2 would return "nl80211"
(without double quotes), Py3 will return "b'nl80211'" (with single quotes,
but without double quotes).  So, be aware that the return value will be a
bytes in Py3, but a string in Py2.
