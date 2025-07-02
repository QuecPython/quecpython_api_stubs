"""
Function:
The QEsimTool software is mainly used to handle the situation of an empty eSIM card. 
The QEsimTool software needs to download data from the operator's server and requires 
the personal computer to have normal access to the Internet.

The following interfaces are implemented in the LPA method and require users and card vendors to confirm whether the eSIM card supports LPA functionality.
Applicable modules: All modules supporting esim functionality.

Descriptions taken from:
https://developer.quectel.com/doc/quecpython/Application_guide/en/network-comm/esim/index.html?highlight=esim#eSIM-API-Introduction
"""

from sim import esim

def getEID() -> int:
    """Set the ICCID of the eSIM card.
    
    :return: `ICCID` - Successful execution
    """
    
def setCallback(usrFun:int) -> None:
    """Notify the application layer of the results of downloading and installing the Profile.
    
    :return: `None`
    """
    
def getProfileInfo(mode:int) -> list[dict]:
    """Query the current SIM card configuration file
    
    :return: `list[dict]` - Successful execution
    """
    
def profileOTA(activationCode, confirmationCode) -> int:
    """Download and install the Operator Profile
    
    :param result: Result of OTA profile download.
    :type result: Integer, 0: success, 1: failure
    """    
    
def profileHandle(profile_tag:int, iccid:str) -> int:
    """Control the current SIM card configuration file
    
    :return: `0` - Successful execution; `-1` - Failed execution        
    """
    
def getProfileDelNotification() -> list[dict]:
    """Obtain the configuration file to be deleted

    return:'The list of configuration files to be deleted'
    """
    
def reportProfileDelNotification(iccid:str) -> list[dict]:
    """Report the configuration file to be deleted
    
    return:'The list of configuration files to be deleted'
    """