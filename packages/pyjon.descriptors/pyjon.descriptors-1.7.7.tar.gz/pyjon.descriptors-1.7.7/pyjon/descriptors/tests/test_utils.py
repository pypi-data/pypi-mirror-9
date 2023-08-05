import six
from xml.etree import cElementTree as ET
from pyjon.descriptors import Descriptor

# this is the location of the test directory relative to the setup.py file
basetestdir = "pyjon/descriptors/tests/"


def get_descriptor(xml_schemafile, encoding, buffersize=16384):
    """helper function to construct a descriptor instance from
    a schema file to help test implementations

    @param xml_schemafile: the filename that contains the xml schema
    that should normally be in the database but is in a static file
    for test purposes
    @type xml_schemafile: string object (unicode on Python 2)

    @param encoding: the encoding of the stream to read (ie: 'utf-8')
    @type encoding: string

    @param buffersize: the size of the buffer in bytes for the read operation.
    This will be used by the readers that perform buffering themselves
    @type buffersize: int
    """
    payload_tree = ET.parse(xml_schemafile)
    return Descriptor(payload_tree, encoding, buffersize=buffersize)


def open_file(path, flags):
    """Open the specified file. Compatible with Python 2 & 3: the "b" flag has
    more meanings in Python 3; the "newline" parameter doesn't exist in Python
    2.
    """

    if flags and 'b' in flags:
        # Honor explicit "b" flags.
        return open(path, flags)

    if six.PY2:
        # On Python 2, always open as binary (matters on Windows).
        return open(path, flags + 'b')

    # On Python 3, open as text.
    return open(path, flags, newline='')
