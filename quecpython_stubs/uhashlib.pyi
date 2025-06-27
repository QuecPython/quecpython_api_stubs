"""
Function:
This module realizes the hash algorithm of the binary data.

Descriptions taken from:
https://developer.quectel.com/doc/quecpython/API_reference/zh/stdlib/uhashlib.html
"""

class SHA1:
    """SHA1 hash algorithm.
    :params bytes: Bytes data can be passed when creating a SHA1 hash object or via hash_obj.update().
    """
    def __init__(self,bytes):
        """Initialize the SHA1 hash algorithm."""

    def update(self, bytes):
        """Update the hash algorithm with the data.
        :params bytes: Bytes data can be passed when creating a SHA256 hash object or via hash_obj.update().
        """
        
    def digest(self):
        """Return the digest of the hash algorithm."""
        

class SHA256:
    """SHA256 hash algorithm.
    :params bytes: Bytes data can be passed when creating a SHA256 hash object or via hash_obj.update().
    """

    def __init__(self):
        """Initialize the SHA256 hash algorithm."""
        
    def update(self, bytes):
        """Update the hash algorithm with the data."""
        
    def digest(self):
        """Return the digest of the hash algorithm."""

class MD5:
    """MD5 hash algorithm.
    :params bytes: Bytes data can be passed when creating a MD5 hash object or via hash_obj.update().
    """

    def __init__(self):
        """Initialize the MD5 hash algorithm."""

    def update(self, bytes):
        """Update the hash algorithm with the data."""
        
    def digest(self):
        """Return the digest of the hash algorithm."""
