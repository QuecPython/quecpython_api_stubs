
def save():
    """save configure to file"""
    ...


def init():
    """init configure"""
    ...


def setProductInfo(pk,ps) -> bool:
    """Set product info
    
    pk: ProductKey generated when you create the product on Developer Center.
    ps: ProductSecret generated when you create the product on Developer Center.
    
    :return:True: Successful execution,False: Failed execution
    """
    ...
    
    
def setDevSecret(ds):
    """set device secret
    
    ds: device secret
    """
    ...


def setServer(url):
    """set server url
    
    url: server url
    """
    ...


def saveBootstrap(url, mcc):
    """save bootstrap
    
    url: bootstrap url
    mcc: mcc
    """
    ...
    
    
def setLifetime(lifetime):
    """set lifetime
    
    lifetime: lifetime
    """
    ...


def setEventCb(eventlist)-> int:
    """Set the callback function for the event
    
    eventlist: Event list
    
    :return:1: Successful execution,rest: Failed execution
    """
    ...
    

def setMcuVer(comp_no, version, infoCB, resultCB) -> bool:
    """Set the MCU version
    
    comp_no: Component number
    version: MCU version
    infoCB: Callback function for information
    resultCB: Callback function for result
    
    :return:True: Successful execution,False: Failed execution
    """
    ...


def setAppVer(version, resultCB):
    """Set the application version
    
    version: App component version.
    resultCB: Callback function of the App upgrade results.
    """
    ...


def setOtaInfo(comp_no, version, comp_type):
    """set ota information
    
    comp_no: component number
    version: component version
    comp_type: component type
    """
    ...


def setBsEt(type):
    """set broker security type
    
    type: tcp, psk, tls, cer
    """
    ...


def getBsEt():
    """get broker ethernet type"""
    ...


def getMqttCert():
    """get mqtt certificate"""
    ...


def setOtaKey(key):
    """set ota key
    
    key: ota key
    """
    ...

def getOtaKey():
    """get ota key"""
    ...
