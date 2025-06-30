

def getPkgId():
    """get package id"""
    ...


def format(pid, cmd, byte):
    """format protocol
    
    pid: package id
    cmd: command
    byte: byte array
    """
    ...

def unformat(byte):
    """unformat protocol
    
    byte: byte array
    """
    ...

def ttlv_format(dicts):
    """ttlv format
    
    :param dicts: ttlv dicts
    """
    ...


def ttlv_unformat(byte):
    """ttlv unformat
    
    :param byte: ttlv byte
    """
    ...
