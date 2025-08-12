"""
Function:
This feature provides DLMS (Device Language Message Specification) server functionality
for smart metering applications.
The following interfaces are implemented in the LPA method and require users and card vendors to confirm whether the eSIM card supports LPA functionality.
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

class Data:
    """
    DLMS Data object. Holds a value (int, bytes, str, bool, or None) and logical_name.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        value (int | bytes | str | bool | None): Data value.

    Example:
        data = Data("1.0.1.8.0.255")
        data.value = 42
        data.value = b"\x01\x02"
        data.value = "hello"
        data.value = True
        data.value = None
    """
    logical_name: bytes
    value: int | bytes | str | bool | None
    def __init__(self, logical_name: str): ...


class Register:
    """
    DLMS Register object.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        value (int): Current register value.
        unit (int): Unit code (see Unit enum).
        scaler (int): Scaler for value (default 1).

    Methods:
        reset(): Resets value to default_value.

    Example:
        reg = Register("1.0.1.8.0.255", 0, unit=Unit.KWH, scaler=1)
        reg.value = 42
        reg.unit = Unit.VOLTAGE
        reg.scaler = 10
        reg.reset()
    """
    logical_name: bytes
    value: int
    unit: int
    scaler: int
    def __init__(self, logical_name: str, default_value: int, unit: Optional[int] = None, scaler: int = 1): ...
    def reset(self) -> None: ...


class SecuritySetup:
    """
    DLMS SecuritySetup object.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        security_policy (int): Security policy (see SecurityPolicy enum).
        security_suite (int): Security suite version (0, 1, 2).
        min_invocation_counter (int): Minimum invocation counter.

    Example:
        sec = SecuritySetup("0.0.43.0.1.255")
        sec.security_policy = SecurityPolicy.AUTHENTICATED_ENCRYPTED
        sec.security_suite = 1
        sec.min_invocation_counter = 1000
    """
    logical_name: bytes
    security_policy: int
    security_suite: int
    min_invocation_counter: int
    def __init__(self, logical_name: str): ...

class AssociationLogicalName:
    """
    DLMS AssociationLogicalName object.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        app_context_name (bytes | None): Application context name (optional, bytes).
        secret (bytes | None): Secret for authentication (optional, bytes).
        auth_mechanism (str): Authentication mechanism ('None', 'Low', 'High').
        objects (list): List of DLMS objects (Register, Data, etc.).
        clientSAP (int): Client SAP (Service Access Point).
        security_setup (SecuritySetup | None): Security setup object.
        context (DLMSContext): DLMS context info (session/configuration).

    Example:
        assoc = AssociationLogicalName("0.0.43.0.1.255")
        assoc.app_context_name = b"..."
        assoc.secret = b"password"
        assoc.auth_mechanism = "High"
        assoc.objects = [reg, data]
        assoc.clientSAP = 1
        assoc.security_setup = sec
        assoc.context = DLMSContext(dlmsVersionNumber=6)
    """
    logical_name: bytes
    app_context_name: bytes | None
    secret: bytes | None
    auth_mechanism: str
    objects: list
    clientSAP: int
    security_setup: 'SecuritySetup | None'
    context: 'DLMSContext'
    def __init__(self, logical_name: str): ...

class Conformance:
    """
    DLMS Conformance enum. Use as Conformance.READ, Conformance.WRITE, etc.

    Example:
        ctx.conformance = Conformance.READ | Conformance.WRITE
    """
    NONE: int = 0
    RESERVED_ZERO: int = 1
    GENERAL_PROTECTION: int = 2
    GENERAL_BLOCK_TRANSFER: int = 4
    READ: int = 8
    WRITE: int = 16
    UN_CONFIRMED_WRITE: int = 32
    DELTA_VALUE_ENCODING: int = 64
    RESERVED_SEVEN: int = 128
    ATTRIBUTE_0_SUPPORTED_WITH_SET: int = 256
    PRIORITY_MGMT_SUPPORTED: int = 512
    ATTRIBUTE_0_SUPPORTED_WITH_GET: int = 1024
    BLOCK_TRANSFER_WITH_GET_OR_READ: int = 2048
    BLOCK_TRANSFER_WITH_SET_OR_WRITE: int = 4096
    BLOCK_TRANSFER_WITH_ACTION: int = 8192
    MULTIPLE_REFERENCES: int = 16384
    INFORMATION_REPORT: int = 32768
    DATA_NOTIFICATION: int = 65536
    ACCESS: int = 131072
    PARAMETERIZED_ACCESS: int = 262144
    GET: int = 524288
    SET: int = 1048576
    SELECTIVE_ACCESS: int = 2097152
    EVENT_NOTIFICATION: int = 4194304
    ACTION: int = 8388608

class DLMSContext:
    """
    DLMSContext object for session and configuration management.

    Attributes:
        conformance (int): Conformance flags (see Conformance enum).
        maxReceivePduSize (int): Maximum receive PDU size.
        maxSendPduSize (int): Maximum send PDU size.
        dlmsVersionNumber (int): DLMS version number.
        qualityOfService (int): Quality of service.

    Example:
        ctx = DLMSContext(conformance=Conformance.READ | Conformance.WRITE, maxReceivePduSize=1024)
    """
    conformance: int
    maxReceivePduSize: int
    maxSendPduSize: int
    dlmsVersionNumber: int
    qualityOfService: int
    def __init__(self, **kwargs): ...


class Unit:
    """
    DLMS Unit enum. Use as Unit.KWH, Unit.VOLTAGE, etc.

    Example:
        reg.unit = Unit.KWH
        reg.unit = Unit.VOLTAGE
    """
    NONE: int = 0
    YEAR: int = 1
    MONTH: int = 2
    WEEK: int = 3
    DAY: int = 4
    HOUR: int = 5
    MINUTE: int = 6
    SECOND: int = 7
    PHASE_ANGLE_DEGREE: int = 8
    TEMPERATURE: int = 9
    LOCAL_CURRENCY: int = 10
    LENGTH: int = 11
    SPEED: int = 12
    VOLUME_CUBIC_METER: int = 13
    CORRECTED_VOLUME: int = 14
    VOLUME_FLUX_HOUR: int = 15
    CORRECTED_VOLUME_FLUX_HOUR: int = 16
    VOLUME_FLUX_DAY: int = 17
    CORRECTED_VOLUME_FLUX_DAY: int = 18
    VOLUME_LITER: int = 19
    MASS_KG: int = 20
    FORCE: int = 21
    ENERGY: int = 22
    PRESSURE_PASCAL: int = 23
    PRESSURE_BAR: int = 24
    ENERGY_JOULE: int = 25
    THERMAL_POWER: int = 26
    ACTIVE_POWER: int = 27
    APPARENT_POWER: int = 28
    REACTIVE_POWER: int = 29
    ACTIVE_ENERGY: int = 30
    APPARENT_ENERGY: int = 31
    REACTIVE_ENERGY: int = 32
    CURRENT: int = 33
    ELECTRICAL_CHARGE: int = 34
    VOLTAGE: int = 35
    ELECTRICAL_FIELD_STRENGTH: int = 36
    CAPACITY: int = 37
    RESISTANCE: int = 38
    RESISTIVITY: int = 39
    MAGNETIC_FLUX: int = 40
    INDUCTION: int = 41
    MAGNETIC: int = 42
    INDUCTIVITY: int = 43
    FREQUENCY: int = 44
    ACTIVE: int = 45
    REACTIVE: int = 46
    APPARENT: int = 47
    V260: int = 48
    A260: int = 49
    MASS_KG_PER_SECOND: int = 50
    CONDUCTANCE: int = 51
    KELVIN: int = 52
    RU2H: int = 53
    RI2H: int = 54
    CUBIC_METER_RV: int = 55
    PERCENTAGE: int = 56
    AMPERE_HOURS: int = 57
    ENERGY_PER_VOLUME: int = 60
    WOBBE: int = 61
    MOLE_PERCENT: int = 62
    MASS_DENSITY: int = 63
    PASCAL_SECOND: int = 64
    JOULE_KILOGRAM: int = 65
    PRESSURE_GRAM_PER_SQUARE_CENTIMETER: int = 66
    PRESSURE_ATMOSPHERE: int = 67
    SIGNAL_STRENGTH_MILLI_WATT: int = 70
    SIGNAL_STRENGTH_MICRO_VOLT: int = 71
    DB: int = 72
    INCH: int = 128
    FOOT: int = 129
    POUND: int = 130
    FAHRENHEIT: int = 131
    RANKINE: int = 132
    SQUARE_INCH: int = 133
    SQUARE_FOOT: int = 134
    ACRE: int = 135
    CUBIC_INCH: int = 136
    CUBIC_FOOT: int = 137
    OTHER: int = 254
    NO_UNIT: int = 255


class SecurityPolicy:
    """
    DLMS SecurityPolicy enum. Use as SecurityPolicy.AUTHENTICATED, etc.

    Example:
        sec.security_policy = SecurityPolicy.AUTHENTICATED_ENCRYPTED
    """
    NOTHING: int = 0
    AUTHENTICATED: int = 1
    ENCRYPTED: int = 2
    AUTHENTICATED_ENCRYPTED: int = 3
    AUTHENTICATED_REQUEST: int = 4
    ENCRYPTED_REQUEST: int = 8
    DIGITALLY_SIGNED_REQUEST: int = 16
    AUTHENTICATED_RESPONSE: int = 32
    ENCRYPTED_RESPONSE: int = 64
    DIGITALLY_SIGNED_RESPONSE: int = 128

def get_all_objects() -> list:
    """Returns a list of all DLMS objects currently registered. Use for debug purposes only."""
    ...

def print_all_objects() -> None:
    """Prints all DLMS objects to the console/log."""
    ...

def set_default_clock(clock: Clock) -> None:
    """Sets the default DLMS clock object."""
    ...

def set_serial_number(serial: int) -> None:
    """Sets the DLMS device serial number."""
    ...

def get_serial_number() -> int:
    """Gets the DLMS device serial number."""
    ...

def set_flag_id(flag_id: str) -> None:
    """Sets the DLMS flag ID."""
    ...

def get_flag_id() -> str:
    """Gets the DLMS flag ID."""
    ...

def set_hdlc(cfg: IecHdlcSetup) -> None:
    """Configures IEC HDLC settings for DLMS communications."""
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

class IecHdlcSetup:
    """
    DLMS IEC HDLC Setup object.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        commSpeed (int): Communication speed (baud rate, e.g. 9600).
        windowSizeRx (int): Receive window size.
        windowSizeTx (int): Transmit window size.
        maxInfoLenTx (int): Maximum info length for transmit.
        maxInfoLenRx (int): Maximum info length for receive.
        timeout (int): Inactivity timeout (seconds).
        deviceAddr (int): Device address (default 0x10).

    Example:
        hdlc = IecHdlcSetup("0.0.22.0.0.255", commSpeed=9600, windowSizeRx=1, windowSizeTx=1,
                            maxInfoLenTx=128, maxInfoLenRx=128, timeout=120, deviceAddr=0x10)
        hdlc.commSpeed = 19200
        hdlc.windowSizeRx = 2
        hdlc.deviceAddr = 0x20
    """
    logical_name: bytes
    commSpeed: int
    windowSizeRx: int
    windowSizeTx: int
    maxInfoLenTx: int
    maxInfoLenRx: int
    timeout: int
    deviceAddr: int
    def __init__(
        self,
        logical_name: str,
        commSpeed: int = 9600,
        windowSizeRx: int = 1,
        windowSizeTx: int = 1,
        maxInfoLenTx: int = 128,
        maxInfoLenRx: int = 128,
        timeout: int = 120,
        deviceAddr: int = 0x10
    ): ...

class Clock:
    """
    DLMS Clock object.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        time (tuple): Current time as (year, month, day, hour, minute, second).
        begin (tuple): Begin time as (year, month, day, hour, minute, second).
        end (tuple): End time as (year, month, day, hour, minute, second).
        time_zone (int): Time zone offset.
        deviation (int): Deviation (minutes).
        base (int): Clock base (see Clock.BASE_* enum).
        status (int): Status flags.
        enabled (bool): Whether clock is enabled.

    Enum values:
        BASE_NONE: int = 0
        BASE_CRYSTAL: int = 1
        BASE_FREQUENCY_50: int = 2
        BASE_FREQUENCY_60: int = 3
        BASE_GPS: int = 4
        BASE_RADIO: int = 5

    Example:
        clk = Clock("0.0.1.0.0.255", time_zone=0, deviation=60, base=Clock.BASE_FREQUENCY_50)
        clk.time = (2025, 8, 8, 12, 0, 0)
        clk.enabled = True
    """
    logical_name: bytes
    time: tuple
    begin: tuple
    end: tuple
    time_zone: int
    deviation: int
    base: int
    status: int
    enabled: bool
    BASE_NONE: int = 0
    BASE_CRYSTAL: int = 1
    BASE_FREQUENCY_50: int = 2
    BASE_FREQUENCY_60: int = 3
    BASE_GPS: int = 4
    BASE_RADIO: int = 5
    def __init__(
        self,
        logical_name: str,
        begin: tuple = (...),
        end: tuple = (...),
        time_zone: int = 0,
        deviation: int = 60,
        base: int = BASE_FREQUENCY_50
    ): ...