"""
Function:
This feature provides DLMS (Device Language Message Specification) server functionality
for smart metering applications.
Applicable modules: All modules supporting DLMS functionality.
"""

from typing import Optional

def run() -> int:
    """Starts the DLMS server.

    :return: `0` - Successful execution; `-1` - Failed execution
    """
    ...

def stop() -> int:
    """Stops the DLMS server.

    :return: `0` - Successful execution
    """
    ... 

def handle_request(
    recv_buff: bytes,
    recv_buff_len: int
) -> bytearray:
    """Handles a DLMS request message received from UART or TCP.

    :param recv_buff: Request message bytes from UART or TCP
    :param recv_buff_len: Length of request message
    :return: Response message (processed DLMS data) if successful; empty bytes if failed
    """
    ...

def uart_open(port: Optional[int] = None) -> int:
    """Opens UART port for DLMS communications.

    :param port: UART port number, defaults to `UART2` if not specified
    :return: `0` - Successful execution; `-1` - Failed execution
    :raise ValueError: If invalid port number provided
    """
    ...

def uart_close() -> int:
    """Closes the UART port used for DLMS communications.

    :return: `0` - Successful execution
    """
    ...