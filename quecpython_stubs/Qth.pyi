"""
Function:
QthSDK API

Descriptions taken from:
https://iot-docs.acceleronix.io/deviceDevelop/DeviceAccessPlan/cellular/QuecPython/api/quecpython-api-01.html
"""


#Product configuration API

def setProductInfo(pk,ps) -> bool:
    """Set product info
    
    pk: ProductKey generated when you create the product on Developer Center.
    ps: ProductSecret generated when you create the product on Developer Center.
    
    :return:True: Successful execution,False: Failed execution
    """
    
def setServer(url) -> bool:
    """Set server address
    
    url: Server address
    
    :return:True: Successful execution,False: Failed execution
    """

def setLifetime(lifetime) -> bool:
    """Set the lifetime of the product
    
    lifetime: Lifetime of the product
    
    :return:True: Successful execution,False: Failed execution
    """
def setEventCb(eventlist)-> int:
    """Set the callback function for the event
    
    eventlist: Event list
    
    :return:1: Successful execution,rest: Failed execution
    """
    
def setMcuVer(comp_no, version, infoCB, resultCB) -> bool:
    """Set the MCU version
    
    comp_no: Component number
    version: MCU version
    infoCB: Callback function for information
    resultCB: Callback function for result
    
    :return:True: Successful execution,False: Failed execution
    """
def setAppVer(version, resultCB):
    """Set the application version
    
    version: App component version.
    resultCB: Callback function of the App upgrade results.
    """
  
#Network Configuration API
def setApn(apn, username, password):
    """Set APN
    
    apn: APN
    username: APN username
    password: APN password
    
    return: NULL
    """
    
#Device Connection API
def init() -> bool:
    """Initialize the device connection
    
    return: True if initialization is successful, False otherwise
    """
    
def start() -> bool:
    """Start the device connection
    
    return: True if the device is connected, False otherwise
    """
    
def stop():
    """Stop the device connection"""
    
def state() -> bool:
    """Get the device connection state
    
    return: True if the device is connected, False otherwise
    """
    
def reset():
    """Reset the device connection"""
    
#Data Interaction API
def sendTrans(mode, value) -> bool:
    """Send a transaction to the device
    
    mode: Transaction mode
    value: Transaction value
    
    return: True if the transaction was sent, False otherwise
    """
    
def sendTsl(mode, value) -> bool:
    """Send a TSL command to the device
    
    mode: TSL command mode
    value: TSL command value
    
    return: True if the command was sent, False otherwise
    """
    
def ackTsl(mode, value, pkgId) -> bool:
    """Send an ACK to the device
    
    mode: ACK mode
    value: ACK value
    pkgId: Package ID
    
    return: True if the ACK was sent, False otherwise
    """
    
def ackTslServer(mode, serverId, value, pkgId) -> bool:
    """Send an ACK to the server
    
    mode: ACK mode
    serverId: Server ID
    value: ACK value
    pkgId: Package ID
    
    return: True if the ACK was sent, False otherwise
    """
    
#OTA upgrade API
def otaRequest() -> bool:
    """Request an OTA upgrade
    
    return: True if the request was sent, False otherwise
    """
    
def otaAction(otaAction) -> bool:
    """Send an OTA action
    
    otaAction: OTA action
    
    return: True if the action was sent, False otherwise
    """