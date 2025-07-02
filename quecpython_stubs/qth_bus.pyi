"""qth_bus.pyi"""


def sendTrans(mode, value) -> bool:
    """Send a transaction to the device
    
    mode: Transaction mode
    value: Transaction value
    
    return: True if the transaction was sent, False otherwise
    """
    ...


def sendTsl(mode, value) -> bool:
    """Send a TSL command to the device
    
    mode: TSL command mode
    value: TSL command value
    
    return: True if the command was sent, False otherwise
    """
    ...


def ackTsl(mode, value, pkgId) -> bool:
    """Send an ACK to the device
    
    mode: ACK mode
    value: ACK value
    pkgId: Package ID
    
    return: True if the ACK was sent, False otherwise
    """
    ...


def ackTslServer(mode, serverId, value, pkgId) -> bool:
    """Send an ACK to the server
    
    mode: ACK mode
    serverId: Server ID
    value: ACK value
    pkgId: Package ID
    
    return: True if the ACK was sent, False otherwise
    """
    ...


def sendOutsideLocation(location):
    """sendOutsideLocation location 
    
    location: Location to send
    """
    ...


def getDevInfo(idList):
    """get device information
    
    idList: List of device IDs
    """
    ...

def ackDevInfo(idList, pkgId):
    """ack devivce information
    
    idList: List of device IDs
    pkgId: Package ID
    """
    ...


def sendDevInfo(idList):
    """send device information

    idList: List of device IDs
    """
    ...

def getDevStatus(idList):
    """get device status
    
    idList: List of device IDs
    """
    ...


def ackDevStatus(idList, pkgId):
    """ack device status
    
    idList: List of device IDs
    pkgId: Package ID
    """
    ...


def sendDevStatus(idList):
    """send device status
    
    idList: List of device IDs
    """
    ...
