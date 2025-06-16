"""
Function:
The modem module provides the method of reading device information.

Descriptions taken from:
https://developer.quectel.com/doc/quecpython/API_reference/en/syslib/modem.html
"""


def getDevImei():
    """Gets the device IMEI.

    :return: If successful, it returns the device IMEI in string type. If failed, it returns the integer value -1.
    """


def getDevModel():
    """Gets the device model.

    :return: If successful, it returns the device model in string type. If failed, it returns the integer value -1.
    """


def getDevSN():
    """Gets the device serial number.

    :return: If successful, it returns the device serial number in string type. If failed, it returns the integer value -1.
    """


def getDevFwVersion():
    """Gets the device firmware version.

    :return: If successful, it returns the device firmware version in string type. If failed, it returns the integer value -1.
    """


def getDevProductId():
    """Gets the device manufacture ID.

    :return: If successful, it returns the device manufacture ID in string type. If failed, it returns the integer value -1.
    """

def getDevMAC():
    """Get Device MAC Address
        
    This method retrieves the device's MAC address.
    Currently only supported on FCM360W modules.
    
    :return: On success - Returns the device MAC address as a string (format: "XX:XX:XX:XX:XX:XX")
             On failure - Returns integer -1
    """