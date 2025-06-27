"""
Function:
The module uses the binary data compressed by DEFLATE Algorithm to decompress (generally used in the zlib library and the gzip archiver). 
This module realizes subsets of the corresponding CPython module. See CPython file zlib for more detailed information.

See CPython file struct for detailed information: https://docs.python.org/3.5/library/zlib.html#module-zlib

Descriptions taken from:
https://developer.quectel.com/doc/quecpython/API_reference/zh/stdlib/uzlib.html
"""

def decompress(data, wbits=0, bufsize=0):
    """Returns the compressed bytes object. 
    :param data: data is assumed to be the zlib stream (with the zlib header)
    :param wbits: wbits is the window size of DEFLATE dictionary when decompressing. (8–15, the dictionary size is the power of 2 of wbits value).
    :param bufsize: bufsize is for compatibility with CPython and will be ignored.
    :return: decompressed bytes object
    """

def DecompIO(stream, wbits=0, bufsize=1):
    """Creates a stream decorator that allows data to be transparently compressed in another stream
    :param stream: stream to be compressed
    :param wbits:  wbits is the window size of DEFLATE dictionary when DecompIO.
    :param bufsize: 

    :return:
    """

