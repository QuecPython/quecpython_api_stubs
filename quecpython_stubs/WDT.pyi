"""
Function:
This class provides a system restart operation when an APP 
application fails to execute due to an exception.
Applicable modules: All modules supporting WDT functionality.

Descriptions taken from:
https://developer.quectel.com/doc/quecpython/API_reference/en/peripherals/machine.WDT.html?highlight=WDT
"""


from machine import WDT

def feed() -> int:
    """This method is used for feeding dogs.

    :return: `0` - Successful execution; `-1` - Failed execution
    """
    ...

def stop() -> int:
    """This method is used to disable the soft dog function.

    :return: `0` - Successful execution; `-1` - Failed execution
    """
    ...