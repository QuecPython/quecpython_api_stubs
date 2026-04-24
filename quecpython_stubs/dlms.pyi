"""
Function:
This feature provides DLMS (Device Language Message Specification) server functionality
for smart metering applications.
Applicable modules: All modules supporting DLMS functionality.
"""

from typing import Optional, Callable, Any, List, Tuple, Dict, Union

class DLMSEvent:
    """
    DLMS Event object passed to event handlers.

    This object provides context about the DLMS operation being performed.
    It is passed to on_before_read, on_before_action, etc. handlers.

    Attributes:
        index (int): Attribute or method index being accessed.
        selector (int): Selector type (0=no selector, 1=range, 2=entry).
        is_action (bool): True if this is an action (method call), False if read/write.
        selector_params (dict | None): Parsed selector parameters.
            For selector=1 (range): {'from_time': int, 'to_time': int}
            For selector=2 (entry): {'from_entry': int, 'to_entry': int}
        parameters (int | None): Action method parameters (for actions only).

    Example:
        def my_read_handler(self, event):
            print(f"Reading attribute {event.index}")
            if event.selector == 1:
                from_time = event.selector_params['from_time']
                to_time = event.selector_params['to_time']
                print(f"Range query: {from_time} to {to_time}")
            return True  # Allow the operation
    """
    index: int
    selector: int
    is_action: bool
    selector_params: dict | None
    parameters: int | None


class AttributeFlag:
    """Bitmask constants describing COSEM attribute properties.

    Used with ``CosemObject.idx()`` / ``attrs()`` introspection.
    Accessible as ``dlms.AttributeFlag.READONLY`` etc.

    Constants:
        READONLY (int): Attribute cannot be set from Python (e.g. ``Register.unit``).
        VOLATILE (int): Attribute changes frequently and should not be persisted
            (e.g. ``Clock.time``, ``GsmDiagnostic.status``).
        COMPLEX (int): Attribute value is a list or struct; not supported by
            simple scalar serialisers (e.g. ``ProfileGeneric.buffer``).
    """
    READONLY: int
    VOLATILE: int
    COMPLEX: int


class CosemObject:
    """Base class for all COSEM object wrappers.

    All COSEM objects in this module inherit from ``CosemObject`` and share
    the following event hook attributes and per-instance access control.

    ``on_before_read(self, event) -> Optional[bool]``:
        Invoked before the server processes a client GET request.  Return
        ``False`` to reject; ``True`` or ``None`` to allow default handling.
    ``on_after_read(self, event) -> None``:
        Invoked after the server has processed a client GET request.
    ``on_before_write(self, event) -> Optional[bool]``:
        Invoked before the server processes a client SET request.  Return
        ``False`` to deny the write; ``True`` or ``None`` to allow.
    ``on_after_write(self, event) -> None``:
        Invoked after the server has processed a client SET request.
    ``on_before_action(self, event) -> Optional[bool]``:
        Invoked before an ACTION request is dispatched.  Return ``False``
        to reject; ``True`` or ``None`` to allow.  Never fires on objects
        that define no COSEM methods.
    ``on_after_action(self, event) -> None``:
        Invoked after an ACTION request has been dispatched.
    ``access_dict`` (dict | None):
        Per-instance access control overrides.  Keys are attribute indices
        (``int``), values are ``(AccessMode, Authentication)`` tuples.
        Takes precedence over class-level defaults (see :func:`set_default_access`).
    """
    on_before_read: Optional[Callable[['CosemObject', DLMSEvent], Optional[bool]]]
    on_after_read: Optional[Callable[['CosemObject', DLMSEvent], None]]
    on_before_write: Optional[Callable[['CosemObject', DLMSEvent], Optional[bool]]]
    on_after_write: Optional[Callable[['CosemObject', DLMSEvent], None]]
    on_before_action: Optional[Callable[['CosemObject', DLMSEvent], Optional[bool]]]
    on_after_action: Optional[Callable[['CosemObject', DLMSEvent], None]]
    access_dict: Optional[dict]

    def idx(self, name: str) -> int:
        """Return the DLMS attribute index (1-based) for the given Python attribute name.

        Raises ``KeyError`` if *name* is not a known attribute on this type.
        """
        ...

    def attr_name(self, index: int) -> str:
        """Return the Python attribute name for the given DLMS attribute index.

        Raises ``KeyError`` if *index* is not found in this type's attribute table.
        """
        ...

    def attrs(self) -> list:
        """Return a list of ``(attr_index, attr_name)`` tuples for the persistent
        attributes of this object.

        Volatile (e.g. ``Clock.time``), complex (e.g. ``ProfileGeneric.buffer``),
        and read-only attributes are excluded — the returned list is intended for
        use by serializers that save and restore object state.
        """
        ...


def run() -> int:
    """[DEPRECATED] Starts the DLMS server using global configuration.
    
    This function is deprecated. Use the new Server API instead:
        server = dlms.Server(serial_number=12345, flag_id="ABC")
        server.add_object(obj)
        conn = dlms.SerialConnection(uart, hdlc)
        server.add_connection(conn)
        server.start()

    :return: `0` - Successful execution; `-1` - Failed execution
    """
    ...

def stop() -> int:
    """[DEPRECATED] Stops the DLMS server.
    
    This function is deprecated. Use server.stop() instead.

    :return: `0` - Successful execution
    """
    ... 

class Server:
    """DLMS Server instance for connection-centric architecture.
    
    This replaces the old global dlms.run() API. Create a server instance,
    add COSEM objects, add connections, then start the server.
    
    Attributes:
        serial_number (int): Device serial number.
        flag_id (str): Three-character flag ID.
        objects (list): List of registered COSEM objects (read-only).
        running (bool): Whether server is currently running (read-only).
    
    Example:
        # Create server
        server = dlms.Server(serial_number=12345678, flag_id="ABC")
        
        # Add COSEM objects
        clock = dlms.Clock("0.0.1.0.0.255")
        reg = dlms.Register("1.0.1.8.0.255", 0)
        server.add_object(clock)
        server.add_object(reg)
        
        # Create and add connection
        hdlc = dlms.IecHdlcSetup("0.0.22.0.0.255", commSpeed=9600)
        conn = dlms.SerialConnection(uart_port=2, hdlc_setup=hdlc)
        server.add_connection(conn)
        
        # Start server (non-blocking, connections run in threads)
        server.run()
        
        # Stop server when done
        server.stop()
    """
    serial_number: int
    flag_id: str
    objects: list
    running: bool
    
    def __init__(self, serial_number: int, flag_id: str): ...
    
    def add_object(self, obj: Any) -> None:
        """Add a COSEM object to the server's registry.
        
        :param obj: COSEM object (Clock, Register, Data, ProfileGeneric, etc.)
        """
        ...
    
    def add_connection(self, connection: 'SerialConnection | OpticalConnection | MobileConnection | GenericConnection') -> None:
        """Add a connection to the server.
        
        :param connection: Connection instance (SerialConnection, OpticalConnection,
                           MobileConnection, or GenericConnection).
        """
        ...
    
    def run(self) -> None:
        """Start the server and all its connections.
        
        Connections run in separate threads. This method returns immediately.
        """
        ...
    
    def stop(self) -> None:
        """Stop the server and close all connections.
        
        This will signal all connection threads to stop and clean up resources.
        """
        ...

    def monitor(self) -> int:
        """Immediately check all RegisterMonitor thresholds and fire actions.

        Checks all RegisterMonitor thresholds on every active connection right now,
        regardless of the automatic 1-second background polling.

        The server already starts a background thread that polls monitoring
        automatically every second once :meth:`run` is called, so calling
        this method is **optional**.  Use it when you need an instant check
        after updating a monitored value in Python, without waiting for the
        next periodic tick.

        :returns: Number of connections that were checked (≥ 0).
        :raises RuntimeError: If monitoring returns an error for any connection.

        Example - force an immediate check after updating a value::

            energy_register.value = read_meter()
            server.monitor()   # check right now instead of waiting ≤1 s
        """
        ...
        
    def set_event_code(
        self,
        data: Data,
        event_log: Optional[ProfileGeneric] = None,
    ) -> None:
        """Register a Data object as the event-code store and an optional
        ProfileGeneric as the event log.

        Must be called before ``server.run()``.
        """
        ...


class Connection:
    """Abstract base class for all DLMS connection types.

    All connection objects expose these shared attributes regardless of the
    underlying transport (UART, optical probe, cellular UDP, or custom Python).

    Lifecycle callbacks (``on_connected``, ``on_disconnected``) are fired when
    the physical link comes up or goes down.  For C-driven connections (Serial,
    Optical, Mobile) they are called from the C listener thread.  For
    :class:`GenericConnection` they are called from the Python thread that
    calls :meth:`~GenericConnection.connect` / :meth:`~GenericConnection.disconnect`.

    Transport monitor callbacks (``on_send``, ``on_receive``):

    * For C-driven connections they are *monitoring* hooks (logging, diagnostics)
      and are called with data crossing the transport boundary.
    * For :class:`GenericConnection` they *drive* the transport and must be
      set for client mode to work.

    ``recv_buffer`` is an optional pre-allocated :class:`bytearray` used by the
    C layer as a staging area during receive, avoiding GC pressure on the hot
    path.  Required for :class:`MobileConnection`; optional for others.
    """
    on_connected: Optional[Callable[[], None]]
    on_disconnected: Optional[Callable[[], None]]
    on_send: Optional[Callable[[bytes], None]]
    on_receive: Optional[Callable[[int], bytes]]
    recv_buffer: Optional[bytearray]


class SerialConnection(Connection):
    """DLMS Serial Connection over UART with HDLC framing (C-driven).

    Opens and manages the UART internally in a dedicated C thread.
    Use this when the hardware is directly wired (RS-485, optical probe, etc.)
    and no custom transport logic is needed.  For custom transports see
    :class:`GenericConnection`.

    Attributes:
        uart_port (int): UART port number passed at construction (read-only).
        hdlc_setup (IecHdlcSetup): The HDLC setup object (read-only).
        flowcontrol (int): Flow control mode (read-only). 0 = none, 1 = RTS/CTS.

    Example::

        hdlc = dlms.IecHdlcSetup(
            "0.0.22.0.0.255",
            commSpeed=9600,
            windowSizeRx=1, windowSizeTx=1,
            maxInfoLenTx=128, maxInfoLenRx=128,
            deviceAddr=0x10,
        )
        conn = dlms.SerialConnection(uart_port=2, hdlc_setup=hdlc, flowcontrol=0)
        server.add_connection(conn)
    """
    uart_port: int
    hdlc_setup: 'IecHdlcSetup'
    flowcontrol: int

    def __init__(self, uart_port: int, hdlc_setup: 'IecHdlcSetup', flowcontrol: int = 0,
                 *, use_logical_name: bool = True): ...


class OpticalConnection(Connection):
    """DLMS Optical Connection with IEC 62056-21 Mode E protocol negotiation.

    Implements DLMS over an optical probe: negotiates at 300 bps (7E1) using
    Mode E, then switches to the proposed baud rate for HDLC communication.

    Mode E negotiation flow:

    1. Wait for sign-on ``/?...!\\r\\n`` at 300 bps.
    2. Send identification ``/<FLAG><BAUD><MODE>\\r\\n`` at 300 bps.
    3. Wait for ACK (0x06 + protocol control + baud confirm).
    4. Switch to proposed baud rate (8N1) and continue with HDLC.

    Attributes:
        uart_port (int): UART port number (read-only).

    Example::

        local_port = dlms.LocalPortSetup(
            "0.0.20.0.0.255",
            default_mode='E',
            default_baud=300,
            proposed_baud=9600,
            response_time=200,
            device_address="12345678",
            password_1="00000000",
            password_2="11111111",
            password_5="AAAAAAAA",
        )
        hdlc = dlms.IecHdlcSetup("0.0.22.0.0.255", commSpeed=9600, deviceAddr=0x10)
        conn = dlms.OpticalConnection(uart_port=1, local_port_setup=local_port, hdlc_setup=hdlc)
        server.add_connection(conn)
    """
    uart_port: int

    def __init__(self, uart_port: int, local_port_setup: 'LocalPortSetup', hdlc_setup: 'IecHdlcSetup',
                 *, use_logical_name: bool = True): ...


class MobileConnection(Connection):
    """DLMS Mobile (cellular/UDP) connection with optional relay support.

    Runs a C-managed UDP socket in a background thread.  Supports two modes:

    * **Direct mode** (no ``relay_tcp_setup``): binds to ``tcp_udp_setup.port``
      and communicates directly with clients.
    * **Relay mode** (``relay_tcp_setup`` provided): registers with a UDP relay
      server; the relay routes packets by HDLC server address.  Also enables
      outbound push via :meth:`send`.

    Attributes:
        tcp_udp_setup (TcpUdpSetup): Board-side UDP port config (read-only).
        gprs_setup (GprsSetup): GPRS/APN configuration (read-only).
        gsm_diag (GsmDiagnostic): GSM diagnostic object (read-only).
        relay_tcp_setup (TcpUdpSetup | None): Relay server config, or ``None`` (read-only).
        active (bool): ``True`` once the connection thread has started (read-only).
        on_connected (Callable[[], None] | None): Fired when the UDP socket is bound.
        on_disconnected (Callable[[], None] | None): Fired when the connection drops.

    Example::

        tcp_udp  = dlms.TcpUdpSetup("0.0.25.0.0.255", port=4059)
        relay    = dlms.TcpUdpSetup("0.0.25.0.0.254", port=4060)
        relay.ipReference = ipv4          # ipv4.ipAddress = relay server IP
        gprs     = dlms.GprsSetup("0.0.2.0.0.255")
        gsm      = dlms.GsmDiagnostic("0.0.25.6.0.255")
        recv_buf = bytearray(4096)

        mobile = dlms.MobileConnection(
            tcp_udp_setup=tcp_udp,
            gprs_setup=gprs,
            gsm_diag=gsm,
            recv_buffer=recv_buf,
            relay_tcp_setup=relay,
        )
        mobile.on_connected    = lambda: print("up")
        mobile.on_disconnected = lambda: print("down")
        server.add_connection(mobile)
    """
    tcp_udp_setup: 'TcpUdpSetup'
    gprs_setup: 'GprsSetup'
    gsm_diag: 'GsmDiagnostic'
    relay_tcp_setup: Optional['TcpUdpSetup']
    active: bool

    def __init__(
        self,
        tcp_udp_setup: 'TcpUdpSetup',
        gprs_setup: 'GprsSetup',
        gsm_diag: 'GsmDiagnostic',
        recv_buffer: bytearray,
        relay_tcp_setup: Optional['TcpUdpSetup'] = None,
        *,
        use_logical_name: bool = True,
    ): ...

    def send(self, data: bytes | bytearray) -> int:
        """Send raw bytes over the relay UDP socket (relay mode only).

        Can be used to push unsolicited DLMS frames to a client.  Only
        callable after the connection is active and the relay socket has
        been established.

        :param data: Bytes to send.
        :returns: Number of bytes sent.
        :raises RuntimeError: If the connection is not yet active or has no relay.
        """
        ...


class InterfaceType:
    """Enum-like class for DLMS framing protocol types used by GenericConnection.

    Values:
        HDLC (int = 0): HDLC framing (IEC 62056-46). Use for byte-stream transports
            such as UART, SPI, USB-Serial, RS-485.
        WRAPPER (int = 1): DLMS Wrapper framing (IEC 62056-47). Use for packet
            transports such as UDP, MQTT, G3-PLC.
        HDLC_WITH_MODE_E (int = 2): HDLC with IEC 62056-21 Mode E negotiation.
            Use when the physical layer requires baud-rate negotiation first.
    """
    HDLC: int
    WRAPPER: int
    HDLC_WITH_MODE_E: int


class GenericConnection(Connection):
    """DLMS connection with Python-driven transport (UART, SPI, MQTT, G3-PLC, etc.).

    Unlike :class:`SerialConnection` and :class:`MobileConnection`, no C thread is
    created.  The caller is responsible for opening the physical transport and calling
    :meth:`process_msg` for each received frame.  The DLMS protocol layer runs
    entirely in C; only the I/O loop lives in Python.

    Framing is configured via :class:`InterfaceType`:

    * Byte-stream transports (UART, SPI, USB) -> ``InterfaceType.HDLC`` + ``hdlc_setup``
    * Packet transports (UDP, MQTT, G3-PLC) -> ``InterfaceType.WRAPPER`` + ``tcp_udp_setup``
    * Optical probe -> ``InterfaceType.HDLC_WITH_MODE_E`` + ``hdlc_setup`` + ``local_port_setup``

    Attributes:
        connected (bool): ``True`` after :meth:`connect` has been called (read-only).
        on_send: Transport hook — must be wired in client mode to transmit frames.
        on_receive: Transport hook — must be wired in client mode to receive frames.

    Example - UART transport in a background thread::

        import dlms, _thread, utime
        from machine import UART

        hdlc = dlms.IecHdlcSetup("0.0.22.0.0.255", commSpeed=9600, deviceAddr=0x10)
        conn = dlms.GenericConnection(
            interface_type=dlms.InterfaceType.HDLC,
            frame_size=1024,
            pdu_size=512,
            hdlc_setup=hdlc,
        )
        conn.on_connected    = lambda: print("connected")
        conn.on_disconnected = lambda: print("disconnected")
        server.add_connection(conn)

        def uart_loop():
            uart = UART(2, hdlc.commSpeed, 8, 0, 1, 0)
            conn.connect()
            buf = bytearray(1024)
            while True:
                n = uart.readinto(buf)
                if n:
                    resp = conn.process_msg(buf[:n])
                    if resp:
                        uart.write(resp)
                utime.sleep(0.01)

        _thread.start_new_thread(uart_loop, ())
    """
    connected: bool

    def __init__(
        self,
        interface_type: int,
        frame_size: int = 1024,
        pdu_size: int = 512,
        *,
        hdlc_setup: Optional['IecHdlcSetup'] = None,
        tcp_udp_setup: Optional['TcpUdpSetup'] = None,
        local_port_setup: Optional['LocalPortSetup'] = None,
        use_logical_name: bool = True,
    ): ...

    def connect(self) -> None:
        """Mark the connection as active and fire ``on_connected``.

        Call this after the physical transport has been opened.
        """
        ...

    def disconnect(self) -> None:
        """Mark the connection as inactive and fire ``on_disconnected``.

        Call this when the physical transport closes or an error occurs.
        """
        ...

    def process_msg(self, buffer: bytes | bytearray) -> Optional[bytes]:
        """Process a received DLMS frame and return the response.

        Pass each chunk received from the transport into this method.  The C
        layer accumulates partial frames automatically.  When a complete request
        has been received the response bytes are returned; otherwise ``None`` is
        returned (partial frame, keep reading).

        :param buffer: Raw bytes received from the transport.
        :returns: Response bytes to send back, or ``None`` if more data is needed.
        :raises RuntimeError: If :meth:`connect` has not been called yet.
        """
        ...

    def close(self) -> None:
        """Disconnect and free all C-side resources."""
        ...


class Client:
    """DLMS client for reading/writing objects from a remote meter.

    Supports both direct serial connections and relay-based mobile connections.

    Attributes:
        connected (bool): Physical connection established (read-only).
        associated (bool): DLMS association established (read-only).
        client_address (int): DLMS client address (read-only).
        server_address (int): DLMS server address (read-only).

    Workflow::

        client = dlms.Client(
            client_address=16,
            server_address=dlms.hdlc_server_address(12345),
        )
        conn = dlms.SerialConnection(uart_port=2, hdlc_setup=hdlc)
        conn = mobile          # MobileConnection with relay_tcp_setup set

        client.connect(conn)
        value = client.read(data_obj, 2)
        client.write(data_obj, 2, 42)
        client.disconnect()

    Profile Generic (load profile) reading::

        rows = client.read_profile(
            profile_obj,
            start_index=1,
            count=10
        )
        for row in rows:
            print(row)
    """
    connected: bool
    associated: bool
    client_address: int
    server_address: int
    currentAssociation: 'AssociationLogicalName'
    """AssociationLogicalName object for the active association, or ``None`` when not connected."""

    def __init__(
        self,
        client_address: int = 16,
        server_address: int = 1,
        authentication: int = 0,
        password: Optional[str] = None,
        use_logical_name: bool = True,
        system_title: Optional[bytes] = None,
        authentication_key: Optional[bytes] = None,
        block_cipher_key: Optional[bytes] = None,
        security: int = 0,
    ): ...

    def connect(self, connection: 'SerialConnection | OpticalConnection | MobileConnection') -> None:
        """Establish physical + DLMS association with the server.

        For ``MobileConnection``, creates a UDP socket and routes frames through
        the relay.  The relay identifies the target board by the HDLC server address
        embedded in each frame.

        :param connection: Connection object (SerialConnection, OpticalConnection, or MobileConnection).
        :raises RuntimeError: If the connection fails.
        """
        ...

    def disconnect(self) -> None:
        """Release the DLMS association (RLRQ) and disconnect (DISC), then close resources."""
        ...

    def read(self, obj: Any, attr_index: Optional[int] = None) -> Any:
        """Read a single attribute or all attributes from a DLMS object.

        :param obj: DLMS object (e.g., Data, Register, Clock, …) or logical-name string.
        :param attr_index: Attribute index (int) to read a specific attribute, or ``None``
            to read all attributes 2..max (smart/object mode only).
        :return: Python value of the attribute (single-read), or ``None`` (batch read).
        :raises RuntimeError: On communication error.
        """
        ...

    def write(self, obj: Any, attr_index: Optional[int] = None, value: Any = None) -> None:
        """Write a value to a DLMS object attribute.

        :param obj: DLMS object or logical-name string.
        :param attr_index: Attribute index (int) to write a specific attribute, or ``None``
            to write all attributes 2..max (smart/object mode only).
        :param value: New value (required in simple/string mode; read from object in smart mode).
        :raises RuntimeError: On communication error.
        """
        ...

    def method(self, obj: Any, method_id: int, parameter: Any = None) -> Any:
        """Invoke a DLMS method (action) on an object.

        :param obj: DLMS object.
        :param method_id: Method index (1-based).
        :param parameter: Optional parameter.
        :return: Method response value (or ``None``).
        :raises RuntimeError: On communication error.
        """
        ...

    def get_objects(self) -> list:
        """Retrieve the association view and return live MicroPython DLMS objects.

        Unknown/unsupported COSEM class IDs are silently skipped.

        :return: List of live DLMS objects (Clock, Register, Data, …).
        :raises RuntimeError: On communication error.
        """
        ...

    def get_object_info(self) -> list:
        """Retrieve the association view and return raw object descriptors.

        :return: List of ``(class_id, version, logical_name_str)`` tuples.
        :raises RuntimeError: On communication error.
        """
        ...

    def read_multiple(self, objects: list[tuple[Any, int]]) -> list:
        """Read multiple attributes in one request.

        :param objects: List of ``(obj, attr_index)`` tuples.
        :return: List of values, one per requested attribute.
        :raises RuntimeError: On communication error.
        """
        ...

    def read_profile(self, profile: Any, start_index: int = 1, count: int = 0) -> list:
        """Read buffered entries from a ProfileGeneric object.

        :param profile: ProfileGeneric object.
        :param start_index: First row to read (1-based).
        :param count: Number of rows; 0 = all available.
        :return: List of row lists.
        :raises RuntimeError: On communication error.
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

class Data(CosemObject):
    """
    DLMS Data object. Holds a value (int, bytes, str, bool, or None) and logical_name.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        value (int | bytes | str | bool | None): Data value. Can also be a tuple (object, attribute) for BYREF references.

    Example:
        data = Data("1.0.1.8.0.255", access={2: (AccessMode.READ_WRITE, Authentication.HIGH)})
        data.value = 42
        data.value = b"\\x01\\x02"
        data.value = "hello"
        data.value = True
        data.value = None
        
        # Attribute referencing example (nocopy=True)
        invocation_counter = Data("0.0.43.1.0.255", nocopy=True)
        invocation_counter.value = (security_setup, 6)  # Reference attribute 6 of security_setup
    """
    logical_name: bytes
    value: int | bytes | str | bool | None | tuple
    def __init__(self, logical_name: str, nocopy: bool = False, access: Optional[dict] = None): ...


class Register(CosemObject):
    """
    DLMS Register object.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        value (int): Current register value.
        unit (int): Unit code (see Unit enum) - read-only, automatically derived from OBIS code.
        scaler (int): Scaler for value (default 1).

    Methods:
        reset(): Resets value to default_value.

    Example:
        reg = Register("1.0.1.8.0.255", 0, scaler=1,
                      access={2: (AccessMode.READ, Authentication.NONE)})
        reg.value = 42
        reg.scaler = 10
        print(reg.unit)
        reg.reset()
    """
    logical_name: bytes
    value: int
    unit: int  # Read-only property
    scaler: int
    def __init__(self, logical_name: str, default_value: int, scaler: int = 1, access: Optional[dict] = None): ...
    def reset(self) -> None: ...


class SecuritySetup:
    """
    DLMS SecuritySetup object.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        security_policy (int): Security policy (see SecurityPolicy enum).
        security_suite (int): Security suite version (0, 1, 2).
        min_invocation_counter (int): Minimum invocation counter.
        server_system_title (bytes): Server system title (8 bytes) for High GMAC.
        client_system_title (bytes): Client system title (8 bytes) for High GMAC.
        guek (bytes): Global Unicast Encryption Key (Block Cipher Key, 16 or 32 bytes).
        gak (bytes): Global Authentication Key (16 or 32 bytes).
        gbek (bytes): Global Broadcast Encryption Key (Block Cipher Key, 16 or 32 bytes).
        certificates (list): List of certificate dictionaries with keys: entity, type, serial_number, issuer, subject, subject_alt_name.

    Example:
        sec = SecuritySetup("0.0.43.0.1.255")
        sec.security_policy = SecurityPolicy.AUTHENTICATED_ENCRYPTED
        sec.security_suite = 1
        sec.min_invocation_counter = 1000
        
        # For High GMAC authentication
        highgmac_sec = SecuritySetup("0.0.43.0.2.255")
        highgmac_sec.security_policy = SecurityPolicy.AUTHENTICATED_ENCRYPTED
        highgmac_sec.server_system_title = b'GRX12345'
        highgmac_sec.client_system_title = b'GRX12345'
        highgmac_sec.guek = b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\x09\\x0A\\x0B\\x0C\\x0D\\x0E\\x0F'
        highgmac_sec.gak = b'\\xD0\\xD1\\xD2\\xD3\\xD4\\xD5\\xD6\\xD7\\xD8\\xD9\\xDA\\xDB\\xDC\\xDD\\xDE\\xDF'
        
        # Optional: Add certificates
        highgmac_sec.certificates = [
            {
                'entity': CertificateEntity.SERVER,
                'type': CertificateType.DIGITAL_SIGNATURE,
                'serial_number': '123456',
                'issuer': 'CN=Test CA',
                'subject': 'CN=Test Server',
                'subject_alt_name': ''
            }
        ]
    """
    logical_name: bytes
    security_policy: int
    security_suite: int
    min_invocation_counter: int
    server_system_title: bytes
    client_system_title: bytes
    guek: bytes
    gak: bytes
    gbek: bytes
    certificates: list
    def __init__(self, logical_name: str): ...
    def deinit(self) -> None: ...

class AssociationLogicalName:
    """
    DLMS AssociationLogicalName object.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        app_context_name (bytes | None): Application context name (optional, bytes).
        secret (bytes | None): Secret for authentication (optional, bytes).
        auth_mechanism (str): Authentication mechanism ('None', 'Low', 'High', 'HighGMac').
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
        
        # For High GMAC authentication
        assocHighGMac = AssociationLogicalName("0.0.40.0.4.255")
        assocHighGMac.auth_mechanism = "HighGMac"
        assocHighGMac.security_setup = highgmac_sec
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

class AssociationShortName:
    """DLMS Association Short Name object (class id 12, typically COSEM 0.0.40.0.0.255).

    Used to define an SN-mode (Short Name referencing) association with optional
    Low authentication.  Pair with a connection created with ``use_logical_name=False``.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        secret (bytes | None): Authentication password for Low authentication (empty = no auth).
        objects (list): List of DLMS objects accessible through this association.
        security_setup (SecuritySetup | None): Optional SecuritySetup object reference.

    Example::

        assoc_sn = dlms.AssociationShortName("0.0.40.0.0.255")
        assoc_sn.secret = b"PASSword"   # Low auth password
        server.add_object(assoc_sn)

        conn = dlms.MobileConnection(
            tcp_udp_setup=tcp_udp,
            gprs_setup=gprs,
            gsm_diag=gsm,
            recv_buffer=recv_buf,
            use_logical_name=False,  # SN mode
        )
    """
    logical_name: bytes
    secret: bytes | None
    objects: list
    security_setup: 'SecuritySetup | None'
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
    def __init__(
        self,
        conformance: int = 0,
        maxReceivePduSize: int = 0,
        maxSendPduSize: int = 0,
        dlmsVersionNumber: int = 0,
        qualityOfService: int = 0
    ): ...


class Unit:
    """
    DLMS Unit enum. Use as Unit.ACTIVE_POWER, Unit.VOLTAGE, etc.

    Example:
        reg.unit = Unit.ACTIVE_POWER
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

ANY: int = -1
"""Wildcard sentinel for datetime tuple fields in time-valued attributes.
Equivalent to ``0xFFFF`` for the year field and ``0xFF`` for all other fields.

Example::

    from dlms import ANY
    port.listening_window = [
        [(ANY, ANY, ANY, 8, 0, 0), (ANY, ANY, ANY, 18, 0, 0)]
    ]
"""

class AccessMode:
    """
    DLMS AccessMode enum. Defines read/write permissions for object attributes.

    Example:
        access={2: (AccessMode.READ, Authentication.NONE)}
    """
    NONE: int = 0
    READ: int = 1
    WRITE: int = 2
    READ_WRITE: int = 3
    AUTHENTICATED_READ: int = 4
    AUTHENTICATED_WRITE: int = 5
    AUTHENTICATED_READ_WRITE: int = 6

class Authentication:
    """
    DLMS Authentication level enum.

    Example:
        access={2: (AccessMode.READ_WRITE, Authentication.HIGH)}
    """
    NONE: int = 0
    LOW: int = 1
    HIGH: int = 2
    HIGH_MD5: int = 3
    HIGH_SHA1: int = 4
    HIGH_GMAC: int = 5
    HIGH_SHA256: int = 6
    HIGH_ECDSA: int = 7


class AddressState:
    """
    M-Bus address assignment state enum (``DLMS_ADDRESS_STATE``).

    Used with ``MbusSlavePortSetup.address_state``.

    Example::

        slave_port.address_state = dlms.AddressState.ASSIGNED
    """
    NONE: int = 0
    """Address not yet assigned since last power-up."""
    ASSIGNED: int = 1
    """Address assigned (manually or automatically)."""


def set_serial_number(serial: int) -> None:
    """Sets the DLMS device serial number."""
    ...


def set_flag_id(flag_id: str) -> None:
    """Sets the DLMS flag ID."""
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

class LocalPortSetup:
    """
    DLMS LocalPortSetup object for optical port configuration (Class ID 19).
    
    This object configures the optical port for IEC 62056-21 communication,
    including Mode E protocol negotiation, baud rate switching, and password protection.
    
    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        default_mode (int): Default optical protocol mode (DLMS_OPTICAL_PROTOCOL_MODE enum).
        default_baud (int): Default baud rate (typically 300 bps for Mode E).
        proposed_baud (int): Proposed baud rate after negotiation (9600 or 19200 bps).
        response_time (int): Response time in milliseconds (default 1000).
        device_address (bytes | None): Device address (max 6 bytes).
        password_1 (bytes | None): P1 password (lowest security level).
        password_2 (bytes | None): P2 password (medium security level).
        password_5 (bytes | None): P5 password (highest security level).
    
    Example:
        # Basic optical port setup
        optical_port = LocalPortSetup(
            "0.0.19.0.0.255",
            default_mode=0,      # Mode E
            default_baud=300,    # Start at 300 bps
            proposed_baud=9600,  # Switch to 9600 bps
            response_time=1000,
            device_address=b"MTR001",
            password_1=b"00000000",  # P1: read-only access
            password_2=b"12345678",  # P2: read/write access
            password_5=b"87654321"   # P5: full access
        )
        
        # Modify after creation
        optical_port.proposed_baud = 19200
        optical_port.password_2 = b"newpass123"
    """
    logical_name: bytes
    default_mode: int
    default_baud: int
    proposed_baud: int
    response_time: int
    device_address: bytes | None
    password_1: bytes | None
    password_2: bytes | None
    password_5: bytes | None
    def __init__(
        self,
        logical_name: str,
        default_mode: int = 0,
        default_baud: int = 300,
        proposed_baud: int = 9600,
        response_time: int = 1000,
        device_address: Optional[bytes] = None,
        password_1: Optional[bytes] = None,
        password_2: Optional[bytes] = None,
        password_5: Optional[bytes] = None
    ): ...

class Clock(CosemObject):
    """
    DLMS Clock object.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes - read-only.
        time (tuple): Current time as (year, month, day, hour, minute, second) - read/write.
        begin (tuple): DST begin time as (year, month, day, hour, minute, second) - read/write.
        end (tuple): DST end time as (year, month, day, hour, minute, second) - read/write.
        time_zone (int): Time zone offset in minutes - read/write.
        deviation (int): DST deviation in minutes - read/write.
        base (int): Clock base (see Clock.BASE_* enum) - read/write.
        status (int): Status flags - read/write.
        enabled (bool): Whether clock is enabled - read/write.

    Enum values:
        BASE_NONE: int = 0
        BASE_CRYSTAL: int = 1
        BASE_FREQUENCY_50: int = 2
        BASE_FREQUENCY_60: int = 3
        BASE_GPS: int = 4
        BASE_RADIO: int = 5

    Example:
        clk = Clock("0.0.1.0.0.255", time_zone=0, deviation=60, base=Clock.BASE_FREQUENCY_50,
                   access={2: (AccessMode.READ, Authentication.NONE)})
        # All properties are writable
        clk.time = (2025, 8, 8, 12, 0, 0)
        clk.time_zone = -480  # UTC-8
        clk.begin = (2025, 3, 9, 2, 0, 0)  # DST start
        clk.end = (2025, 11, 2, 2, 0, 0)  # DST end
        clk.deviation = 60  # 1 hour DST
        clk.enabled = True
        clk.base = Clock.BASE_GPS
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
        base: int = BASE_FREQUENCY_50,
        access: Optional[dict] = None
    ): ...
    def adjust_to_quarter(self) -> None:
        """Action 1: Adjust time to nearest quarter hour (0, 15, 30, 45 minutes)."""
        ...
    def adjust_to_minute(self) -> None:
        """Action 3: Adjust time to nearest minute."""
        ...
    def adjust_to_preset_time(self) -> None:
        """Action 4: Set time to the preset time value."""
        ...
    def preset_adjusting_time(self, time: tuple) -> None:
        """Action 5: Set the preset time to be used by adjust_to_preset_time().
        
        Args:
            time: Tuple of (year, month, day, hour, minute, second)
        """
        ...
    def shift_time(self, seconds: int) -> None:
        """Action 6: Shift the current time by the specified number of seconds.
        
        Args:
            seconds: Number of seconds to shift (positive or negative)
        """
        ...


class ProfileGeneric(CosemObject):
    """
    DLMS ProfileGeneric object for load profile data collection.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        capture_objects (list): List of (object, attribute, data_index) tuples to capture.
        capture_period (int): Capture interval in seconds.
        sort_method (int): Sort method for the buffer (use FIFO, LIFO, LARGEST, or SMALLEST constants).
        sort_object (object): Object reference for sorting (required if sort_method is LARGEST or SMALLEST).
        sort_object_attribute_index (int): Attribute index of sort object.
        sort_object_data_index (int): Data index of sort object.
        profile_entries (int): Maximum number of profile entries.
        entries_in_use (int): Current number of entries in the buffer (read-only).
        buffer_size (int): Size of buffer data in bytes (read-only).

    Class Constants:
        FIFO (int): First-in-first-out sorting (value: 0).
        LIFO (int): Last-in-first-out sorting (value: 1).
        LARGEST (int): Sort by largest value (value: 2).
        SMALLEST (int): Sort by smallest value (value: 3).

    Methods:
        None

    Example:
        load_profile = ProfileGeneric(
            logical_name="1.0.99.1.0.255",
            capture_objects=[
                (clock, 2, 0),   # Timestamp column
                (reg, 2, 0)      # Value column
            ],
            capture_period=900,  # 15 minutes
            sort_method=ProfileGeneric.FIFO,
            profile_entries=8928,  # 31 days worth
            access={
                2: (AccessMode.READ, Authentication.LOW),
                1: (AccessMode.AUTHENTICATED_WRITE, Authentication.HIGH),
            }
        )
        
        # Custom data provider
        def provide_buffer_data(self, event):
            if event.index != 2:
                return True  # Use default for non-buffer attributes
            # Return list of rows: [[timestamp1, value1], [timestamp2, value2], ...]
            return [[1234567890, 100], [1234567900, 105]]
        
        load_profile.on_before_read = provide_buffer_data
    """
    # Class constants for sort_method
    FIFO: int
    LIFO: int
    LARGEST: int
    SMALLEST: int
    
    logical_name: bytes
    capture_objects: list
    capture_period: int
    sort_method: int
    sort_object: Optional[Any]
    sort_object_attribute_index: int
    sort_object_data_index: int
    profile_entries: int
    entries_in_use: int
    buffer_size: int
    def __init__(
        self,
        logical_name: str,
        capture_objects: Optional[list] = None,
        capture_period: Optional[int] = None,
        sort_method: Optional[int] = None,
        sort_object: Optional[Any] = None,
        profile_entries: Optional[int] = None,
        entries_in_use: Optional[int] = None,
        access: Optional[dict] = None
    ): ...
    def deinit(self) -> None: ...

class PushSetup(CosemObject):
    """
    DLMS PushSetup object for automated data push notifications.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        objectList (list): List of (object, attr_idx, data_idx) tuples to push.
        destination (str): Destination address (e.g., "192.168.1.100:4059").
        retries (int): Number of retry attempts.
        retryDelay (int): Delay between retries in seconds.
        randomisationStartInterval (int): Randomization interval to prevent simultaneous pushes.
        communicationWindow (list): List of time windows [(start, end), ...] where times are 6-tuples (year, month, day, hour, min, sec). Use -1 for unspecified fields.

    Methods:
        generate_pdu(): Generates DLMS DATA-NOTIFICATION PDU for push operation.

    Example:
        pushSetup = PushSetup(
            "0.0.25.9.0.255",
            objectList=[(reg, 2, 0), (clock, 2, 0)],
            destination="192.168.1.100:4059",
            retries=3,
            retryDelay=60,
            randomisationStartInterval=5
        )
        
        # Set communication windows (6-tuple format: year, month, day, hour, min, sec)
        pushSetup.communicationWindow = [
            [(-1, -1, -1, 9, 0, 0), (-1, -1, -1, 12, 0, 0)],   # 9 AM to 12 PM daily
            [(-1, -1, -1, 14, 0, 0), (-1, -1, -1, 17, 0, 0)]   # 2 PM to 5 PM daily
        ]
        
        # Action handler for push
        def handle_push_action(self, event):
            if event.index == 1:  # Push action
                pdu = self.generate_pdu()
                # Send pdu via network...
                return True
            return True
        
        pushSetup.on_before_action = handle_push_action
    """
    logical_name: bytes
    objectList: list
    destination: str
    retries: int
    retryDelay: int
    randomisationStartInterval: int
    communicationWindow: list
    def __init__(
        self,
        logical_name: str,
        objectList: Optional[list] = None,
        destination: Optional[str] = None,
        retries: int = 3,
        retryDelay: int = 60,
        randomisationStartInterval: int = 0,
        communicationWindow: Optional[list] = None,
        access: Optional[dict] = None
    ): ...
    def generate_pdu(self) -> bytes: ...
    def deinit(self) -> None: ...

class ScriptAction:
    """
    DLMS ScriptAction for ScriptTable.

    Class Constants:
        Write (int): Write action type (value: 1).
        Execute (int): Execute action type (value: 2).

    Example:
        # Execute action
        action_close = ScriptAction(
            type=ScriptAction.Execute,
            target=disconnect_control,
            method=1,
            parameter=0
        )
        
        # Write action
        action_write = ScriptAction(
            type=ScriptAction.Write,
            target=reg,
            attribute=2,
            parameter=12345
        )
    """
    Write: int = 1
    Execute: int = 2
    def __init__(
        self,
        type: int,
        target: object,
        method: Optional[int] = None,
        attribute: Optional[int] = None,
        parameter: Optional[int | bool] = None
    ): ...

class ScriptTable(CosemObject):
    """
    DLMS ScriptTable object for script-based automation.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.

    Methods:
        add_script(id, actions): Adds a script with given ID and actions.
        get_scripts(): Returns list of configured script IDs.
        remove_script(id): Removes a script by ID.
        execute_script(id): Executes a script by ID (for testing).

    Example:
        script_table = ScriptTable(
            "0.0.10.0.106.255",
            access={
                1: (AccessMode.AUTHENTICATED_WRITE, Authentication.HIGH),
            }
        )
        
        # Add script with single action
        action = ScriptAction(type=ScriptAction.Execute, target=disconnect_control, method=1)
        script_table.add_script(id=1, actions=action)
        
        # Add script with multiple actions
        script_table.add_script(id=2, actions=[action1, action2])
        
        # Remove script
        script_table.remove_script(id=1)
        
        # Action handler
        def handle_script_execute(self, event):
            script_id = event.parameters
            print(f"Executing script {script_id}")
            return True  # Let C execute the script
        
        script_table.on_before_action = handle_script_execute
    """
    logical_name: bytes
    def __init__(self, logical_name: str, access: Optional[dict] = None): ...
    def add_script(self, id: int, actions: ScriptAction | list) -> None: ...
    def get_scripts(self) -> list: ...
    def remove_script(self, id: int) -> bool: ...
    def execute_script(self, id: int) -> bool: ...
    def deinit(self) -> None: ...

class ActivityCalendar(CosemObject):
    """
    DLMS ActivityCalendar object for tariff scheduling.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        calendar_name_active (str): Name of active calendar.
        calendar_name_passive (str): Name of passive calendar.

    Methods:
        add_season_profile(name, start_time, week_name, passive): Adds a season profile.
        add_week_profile(name, monday, tuesday, wednesday, thursday, friday, saturday, sunday, passive): Adds a week profile.
        add_day_profile(day_id, actions, passive): Adds a day profile.
        get_season_profiles(passive): Returns list of season profiles.
        get_week_profiles(passive): Returns list of week profiles.
        get_day_profiles(passive): Returns list of day profiles.
        clear_profiles(passive): Clears all profiles.
        copy_active_to_passive(): Copies active calendar to passive.
        activate_passive_calendar(): Activates the passive calendar.

    Example:
        activity_calendar = ActivityCalendar(
            "0.0.13.0.0.255",
            calendar_name_active="Summer2024",
            calendar_name_passive="Winter2024"
        )
        
        # Add season
        activity_calendar.add_season_profile(
            name="Summer",
            start_time=(7, 1, -1),  # July 1st
            week_name="SummerWeek",
            passive=True
        )
        
        # Add week profile
        activity_calendar.add_week_profile(
            name="SummerWeek",
            monday=1, tuesday=1, wednesday=1, thursday=1, friday=1,
            saturday=2, sunday=2,
            passive=True
        )
        
        # Add day profile
        activity_calendar.add_day_profile(
            day_id=1,
            actions=[
                ((6, 0, 0), script_table, 1),   # 6 AM: script 1
                ((9, 0, 0), script_table, 2),   # 9 AM: script 2
            ],
            passive=True
        )
    """
    logical_name: bytes
    calendar_name_active: str
    calendar_name_passive: str
    def __init__(
        self,
        logical_name: str,
        calendar_name_active: str = "",
        calendar_name_passive: str = "",
        access: Optional[dict] = None
    ): ...
    def add_season_profile(self, name: str, start_time: tuple, week_name: str, passive: bool = False) -> None: ...
    def add_week_profile(
        self,
        name: str,
        monday: int,
        tuesday: int,
        wednesday: int,
        thursday: int,
        friday: int,
        saturday: int,
        sunday: int,
        passive: bool = False
    ) -> None: ...
    def add_day_profile(self, day_id: int, actions: list, passive: bool = False) -> None: ...
    def get_season_profiles(self, passive: bool = False) -> list: ...
    def get_week_profiles(self, passive: bool = False) -> list: ...
    def get_day_profiles(self, passive: bool = False) -> list: ...
    def clear_profiles(self, passive: bool = False) -> None: ...
    def copy_active_to_passive(self) -> None: ...
    def activate_passive_calendar(self) -> None: ...
    def deinit(self) -> None: ...

class DisconnectControl(CosemObject):
    """
    DLMS DisconnectControl object for remote load switching.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        output_state (bool): Current output state (True=connected, False=disconnected).
        control_state (int): Control state (0=disconnected, 1=connected, 2=ready_for_reconnection).
        control_mode (int): Control mode (0=MODE_0, 1=MODE_1, 2=MODE_2, etc.).

    Methods:
        remote_disconnect(): Disconnects the load (method 1).
        remote_reconnect(): Reconnects the load (method 2).

    Example:
        disconnect_control = DisconnectControl(
            "0.0.96.3.10.255",
            output_state=True,
            control_state=1,
            control_mode=1,
            access={
                2: (AccessMode.READ, Authentication.NONE),
                4: (AccessMode.AUTHENTICATED_WRITE, Authentication.HIGH),
            }
        )
        
        # Action handler
        def handle_disconnect_action(obj, event):
            action_names = {1: "DISCONNECT", 2: "RECONNECT"}
            print(f"Action: {action_names.get(event.index)}")
            return True
        
        disconnect_control.on_before_action = handle_disconnect_action
    """
    logical_name: bytes
    output_state: bool
    control_state: int
    control_mode: int
    def __init__(
        self,
        logical_name: str,
        output_state: bool = False,
        control_state: int = 0,
        control_mode: int = 0,
        access: Optional[dict] = None
    ): ...
    def remote_disconnect(self) -> None: ...
    def remote_reconnect(self) -> None: ...

class SingleActionSchedule(CosemObject):
    """
    DLMS SingleActionSchedule object for scheduled script execution.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        executed_script (tuple): Tuple of (script_table, script_id) to execute.
        execution_type (int): Execution type (1=TYPE1: specific date/time).
        execution_times (list): List of execution time tuples (year, month, day, hour, min, sec, dow). Use -1 for wildcards.

    Example:
        action_schedule = SingleActionSchedule(
            "0.0.15.0.1.255",
            executed_script=(script_table, 1),
            execution_type=1,
            execution_times=[
                (-1, -1, -1, 2, 0, 0, -1),  # Daily at 2:00 AM
            ],
            access={
                2: (AccessMode.READ_WRITE, Authentication.HIGH),
            }
        )
    """
    logical_name: bytes
    executed_script: tuple
    execution_type: int
    execution_times: list
    def __init__(
        self,
        logical_name: str,
        executed_script: Optional[tuple] = None,
        execution_type: int = 1,
        execution_times: Optional[list] = None,
        access: Optional[dict] = None
    ): ...
    def deinit(self) -> None: ...

class ExtendedRegister(CosemObject):
    """
    DLMS ExtendedRegister object with status and capture time.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        value (int | float | str): Current register value.
        scaler (int): Scaler for value (10^scaler).
        unit (int): Unit code (see Unit enum).
        status (int | None): Status code (0=OK, None=no status).
        capture_time (tuple | None): Capture time as (year, month, day, hour, minute, second).

    Methods:
        reset(): Resets the register value (action 1).

    Example:
        energy_register = ExtendedRegister(
            "1.0.1.8.0.255",
            value=12345678,
            scaler=-3,  # Divide by 1000
            unit=Unit.ACTIVE_ENERGY,
            status=0,
            capture_time=(2025, 1, 15, 10, 30, 0),
            access={
                2: (AccessMode.READ, Authentication.NONE),
            }
        )
    """
    logical_name: bytes
    value: int | float | str
    scaler: int
    unit: int
    status: int | None
    capture_time: tuple | None
    def __init__(
        self,
        logical_name: str,
        value: int | float | str = 0,
        scaler: int = 0,
        unit: Optional[int] = None,
        status: Optional[int] = None,
        capture_time: Optional[tuple] = None,
        access: Optional[dict] = None
    ): ...
    def reset(self) -> None: ...

class MacAddressSetup:
    """
    DLMS MacAddressSetup object (Class ID 43) for Ethernet/cellular MAC address configuration.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        mac_address (bytes): MAC address (6 bytes).

    Example:
        mac_setup = MacAddressSetup(
            "0.0.25.0.0.255",
            mac_address=b'\\x00\\x11\\x22\\x33\\x44\\x55'
        )
        print(':'.join(['%02X' % b for b in mac_setup.mac_address]))
    """
    logical_name: bytes
    mac_address: bytes
    def __init__(
        self,
        logical_name: str,
        mac_address: Optional[bytes] = None,
        access: Optional[dict] = None
    ): ...


class GprsSetup:
    """
    DLMS GprsSetup object (Class ID 45) for cellular/GPRS network configuration.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        apn (str): Access Point Name for the cellular network.
        pin_code (int): SIM PIN code (0 = no PIN required).

    Example:
        gprs = GprsSetup(
            "0.1.25.0.0.255",
            apn="internet",
            pin_code=0
        )
        gprs.apn = "m2m.carrier.net"
    """
    logical_name: bytes
    apn: str
    pin_code: int
    def __init__(
        self,
        logical_name: str,
        apn: str = "",
        pin_code: int = 0,
        access: Optional[dict] = None
    ): ...


class IPv4Setup:
    """
    DLMS IPv4Setup object (Class ID 42) for IP address configuration.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        datalink_reference (GprsSetup | MacAddressSetup | None): Reference to the data-link layer setup object.
        ip_address (str): IP address (e.g., "0.0.0.0" for DHCP, or "192.168.1.10" for static).
        subnet_mask (str): Subnet mask (e.g., "255.255.255.0").
        gateway_ip_address (str): Default gateway IP address.
        use_dhcp (bool): True to obtain IP address via DHCP.
        primary_dns_address (str): Primary DNS server IP address.
        secondary_dns_address (str): Secondary DNS server IP address.

    Example:
        ipv4 = IPv4Setup(
            "0.0.25.1.0.255",
            datalink_reference=gprs,
            ip_address="0.0.0.0",
            use_dhcp=True,
            primary_dns_address="8.8.8.8",
            secondary_dns_address="8.8.4.4"
        )
    """
    logical_name: bytes
    datalink_reference: Optional[Any]
    ip_address: str
    subnet_mask: str
    gateway_ip_address: str
    use_dhcp: bool
    primary_dns_address: str
    secondary_dns_address: str
    def __init__(
        self,
        logical_name: str,
        datalink_reference: Optional[Any] = None,
        ip_address: str = "0.0.0.0",
        subnet_mask: str = "255.255.255.0",
        gateway_ip_address: str = "0.0.0.0",
        use_dhcp: bool = True,
        primary_dns_address: str = "0.0.0.0",
        secondary_dns_address: str = "0.0.0.0",
        access: Optional[dict] = None
    ): ...


class TcpUdpSetup:
    """
    DLMS TcpUdpSetup object (Class ID 41) for TCP/UDP port configuration.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        port (int): TCP/UDP port number (default DLMS port is 4059).
        ip_reference (IPv4Setup | None): Reference to the IPv4Setup object.
        max_segment_size (int): Maximum segment size (MTU) in bytes.
        max_simultaneous_connections (int): Maximum number of concurrent connections.
        inactivity_timeout (int): Inactivity timeout in seconds (0 = disabled).

    Example:
        tcp_udp = TcpUdpSetup(
            "0.0.25.2.0.255",
            port=4059,
            ip_reference=ipv4,
            max_segment_size=1460,
            max_simultaneous_connections=1,
            inactivity_timeout=120
        )
    """
    logical_name: bytes
    port: int
    ip_reference: Optional[Any]
    max_segment_size: int
    max_simultaneous_connections: int
    inactivity_timeout: int
    def __init__(
        self,
        logical_name: str,
        port: int = 4059,
        ip_reference: Optional[Any] = None,
        max_segment_size: int = 1460,
        max_simultaneous_connections: int = 1,
        inactivity_timeout: int = 0,
        access: Optional[dict] = None
    ): ...


class AdjacentCell:
    """
    DLMS AdjacentCell object.

    Represents a neighbouring cell visible to the device but not currently serving.

    Attributes:
        cell_id (int): Cell identifier.
        signal_quality (int): Received signal level (dBm, typically negative).

    Example:
        adj = AdjacentCell(cell_id=99999, signal_quality=-95)
        print(adj.cell_id, adj.signal_quality)
    """
    cell_id: int
    signal_quality: int
    def __init__(self, cell_id: int = 0, signal_quality: int = 0): ...


class GsmCellInfo:
    """
    DLMS GsmCellInfo object.

    Contains detailed information about the currently serving cell.

    Attributes:
        cell_id (int): Cell identifier (CID).
        location_id (int): Location area code (LAC) or tracking area code (TAC for LTE).
        signal_quality (int): Received signal level (dBm, typically negative).
        ber (int): Bit error rate class (0-7 per GSM 05.08; 0 if not applicable).
        mobile_country_code (int): MCC (e.g., 220 for Serbia).
        mobile_network_code (int): MNC (e.g., 5 for A1 Srbija).
        channel_number (int): ARFCN (GSM), UARFCN (UMTS), or EARFCN (LTE).

    Example:
        cell = GsmCellInfo()
        cell.cell_id = 12345
        cell.mobile_country_code = 220
        cell.mobile_network_code = 5
        print(cell)
    """
    cell_id: int
    location_id: int
    signal_quality: int
    ber: int
    mobile_country_code: int
    mobile_network_code: int
    channel_number: int
    def __init__(self): ...


class GsmDiagnostic:
    """
    DLMS GsmDiagnostic object (Class ID 47) for cellular network monitoring.

    Provides real-time cellular network diagnostics including registration status,
    serving cell information, and neighbouring cell list. Call ``update()`` to
    refresh all values from the QuecPython ``net`` module.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        operator_name (str | None): Operator name string, or ``None`` if unavailable.
        status (int): Network registration status (see status constants below).
        circuit_switch_status (int): Circuit-switched connection status.
        packet_switch_status (int): Packet-switched technology in use (see ps constants).
        cell_info (GsmCellInfo): Serving cell information (read-only object, updated by ``update()``).
        adjacent_cells (list[AdjacentCell]): List of neighbouring cells (read-only, updated by ``update()``).
        adjacent_cells_count (int): Number of adjacent/neighbour cells (read-only).

        Legacy direct-access attributes (equivalent to ``cell_info.xxx``):
        cell_id (int): Serving cell identifier.
        location_id (int): Location area / tracking area code.
        signal_quality (int): Received signal level (dBm).
        ber (int): Bit error rate class (0-7).
        mobile_country_code (int): MCC.
        mobile_network_code (int): MNC.
        channel_number (int): Channel number (ARFCN / UARFCN / EARFCN).

    Status constants (``status`` attribute):
        0 = NOT_REGISTERED (DLMS_GSM_STATUS_NONE)
        1 = HOME_NETWORK    (DLMS_GSM_STATUS_HOME_NETWORK)
        2 = SEARCHING       (DLMS_GSM_STATUS_SEARCHING)
        3 = DENIED          (DLMS_GSM_STATUS_DENIED)
        4 = UNKNOWN         (DLMS_GSM_STATUS_UNKNOWN)
        5 = ROAMING         (DLMS_GSM_STATUS_ROAMING)

    Packet-switch status constants (``packet_switch_status`` attribute):
        0 = INACTIVE, 1 = GPRS, 2 = EGPRS, 3 = UMTS, 4 = HSDPA, 5 = LTE, ...

    Example:
        gsm_diag = GsmDiagnostic("0.0.25.6.0.255")

        # Refresh from live network
        gsm_diag.update()

        print(gsm_diag.operator_name)       # e.g., "A1 Srbija"
        print(gsm_diag.status)              # e.g., 1 (HOME_NETWORK)
        print(gsm_diag.packet_switch_status)  # e.g., 5 (LTE)

        ci = gsm_diag.cell_info
        print(ci.mobile_country_code, ci.mobile_network_code)  # e.g., 220, 5
        print(ci.location_id, ci.channel_number)               # TAC, EARFCN

        for adj in gsm_diag.adjacent_cells:
            print(adj.cell_id, adj.signal_quality)
    """
    logical_name: bytes
    operator_name: Optional[str]
    status: int
    circuit_switch_status: int
    packet_switch_status: int
    cell_info: GsmCellInfo
    adjacent_cells: list
    adjacent_cells_count: int
    # Legacy direct-access shortcuts (mirror cell_info fields)
    cell_id: int
    location_id: int
    signal_quality: int
    ber: int
    mobile_country_code: int
    mobile_network_code: int
    channel_number: int
    def __init__(self, logical_name: str, access: Optional[dict] = None): ...
    def update(self) -> None:
        """Refresh all fields from the QuecPython ``net`` module.

        Calls ``net.getCellInfo()``, ``net.getSignal()``, ``net.operatorName()``,
        and ``net.getState()`` to populate ``operator_name``, ``status``,
        ``cell_info``, and ``adjacent_cells``.  Emits a warning (does not raise)
        if the network is unavailable.
        """
        ...


class RegisterMonitor(CosemObject):
    """
    DLMS RegisterMonitor object (Class ID 21) for threshold-based monitoring.

    Watches a configurable target attribute and triggers ScriptTable actions
    when the monitored value crosses configured threshold levels.

    Attributes:
        logical_name (str): DLMS logical name (OBIS code) string.
        thresholds (list[int | float]): Ordered list of threshold values (low to high).
        monitored_value (tuple[object, int] | None): ``(dlms_obj, attribute_index)``
            identifying the attribute to monitor, or ``None`` if not configured.
        actions (list[dict]): One dict per threshold, each with keys ``"up"`` and
            ``"down"`` mapping to ``(ScriptTable, selector)`` tuples or ``None``.

    Note:
        RegisterMonitor (Class 21) has no COSEM action methods; ``on_before_action`` /
        ``on_after_action`` are never fired.

    Example::

        reg = dlms.Register("1.0.1.8.0.255")
        st  = dlms.ScriptTable("0.0.10.0.100.255")

        rm = dlms.RegisterMonitor("0.0.16.1.0.255")
        rm.thresholds      = [5000, 25000]
        rm.monitored_value = (reg, 2)           # watch attribute 2 (value)
        rm.actions = [
            {"up": (st, 1), "down": (st, 2)},   # actions for threshold 1
            {"up": (st, 1), "down": (st, 2)},   # actions for threshold 2
        ]
    """
    logical_name: str
    thresholds: list
    monitored_value: Optional[tuple]
    actions: list
    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...
    def deinit(self) -> None: ...

class CaptureMethod:
    """CompactData capture method.
    """
    IMPLICIT = 0
    INVOKE = 1

class CompactData(CosemObject):
    """
    DLMS CompactData object (Class ID 62) for template-based compact encoding.

    Encodes multiple capture-object attribute values into a compact binary
    buffer without per-value type tags, reducing bandwidth on constrained links.

    Encoding is performed automatically:

    * ``capture_method=dlms.CaptureMethod.IMPLICIT``: buffer is refreshed on every read of
      ``buffer`` (attribute 2).
    * ``capture_method=dlms.CaptureMethod.INVOKE``: buffer is refreshed when the client
      invokes method 2.

    The ``on_before_read`` / ``on_before_action`` handlers let Python code
    update the values of the capture objects before encoding.  **Handlers must not
    set** ``event.handled = True`` - encoding must proceed after the handler returns.

    Attributes:
        logical_name (str): DLMS logical name (OBIS code) string.
        buffer (bytes): Current compact-encoded payload (also writeable for
            sub-protocol / pre-encoded payloads).
        capture_objects (list[tuple]): List of ``(dlms_obj, attr_idx, data_idx)``
            tuples defining what is captured.
        template_id (int): Template identifier (0-255).
        template_description (bytes): Auto-maintained type template (read-only).
        capture_method (int): ``0`` = IMPLICIT, ``1`` = INVOKE.

    Example::

        clock = dlms.Clock("0.0.1.0.0.255")
        reg   = dlms.Register("1.0.1.8.0.255")

        cd = dlms.CompactData(
            "0.0.96.60.0.255",
            capture_objects=[(clock, 2, 0), (reg, 2, 0)],
            template_id=1,
            capture_method=0,   # IMPLICIT
        )

        def refresh(self, event):
            if event.index == 2:
                # update reg.value from hardware here
                pass

        cd.on_before_read = refresh

        # Manual capture (e.g. at startup, before server starts):
        # cd.capture(server)
    """
    logical_name: str
    buffer: bytes
    capture_objects: list
    template_id: int
    template_description: bytes
    capture_method: CaptureMethod
    def __init__(
        self,
        logical_name: str,
        capture_objects: Optional[list] = None,
        template_id: int = 0,
        capture_method: int = CaptureMethod.IMPLICIT,
        access: Optional[dict] = None,
    ): ...

    def capture(self, server: object) -> None:
        """Manually trigger a capture cycle outside a live DLMS request.

        Encodes the current values of all capture objects into the buffer
        and refreshes ``template_description``.

        The caller must freshen capture-object values (e.g.
        ``reg.value = ...``) before calling this.

        :param server: A running ``dlms.Server`` instance (used to obtain
            DLMS settings for the encoding).
        :raises ValueError: If the server has no connections or if
            encoding fails.
        """
        ...


class MbusSlavePortSetup(CosemObject):
    """
    DLMS MbusSlavePortSetup object (Class ID 25) for M-Bus slave/meter port configuration.

    Use this object when the QuecPython device **is** the M-Bus slave (meter).
    It exposes the device's M-Bus port parameters to a DLMS client
    (master/concentrator) reading the COSEM object model.

    Attributes:
        logical_name (str): DLMS logical name (OBIS code) string.
        default_baud (int): Default M-Bus baud rate as an integer (e.g. ``9600``).
            Valid values: 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600,
            115200.  A ``ValueError`` is raised for any other value.
        available_baud (int): Baud rate currently in use / available, same valid
            values as ``default_baud``.
        address_state (int): Whether the slave has been assigned an M-Bus address.
            Use ``dlms.AddressState.NONE`` or ``dlms.AddressState.ASSIGNED``.
        bus_address (int): M-Bus primary address of this slave (0-255; valid slave
            range is 1-250).

    Example::

        slave_port = dlms.MbusSlavePortSetup("0.0.24.9.0.255")
        slave_port.default_baud   = 9600
        slave_port.available_baud = 9600
        slave_port.address_state  = dlms.AddressState.ASSIGNED
        slave_port.bus_address    = 1

        def on_read(self, event):
            # Refresh address state from driver before client reads it
            slave_port.address_state = dlms.AddressState.ASSIGNED if get_mbus_assigned() else dlms.AddressState.NONE

        slave_port.on_before_read = on_read
    """
    logical_name: str
    default_baud: int
    available_baud: int
    address_state: int
    bus_address: int

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...


class G3PlcMacCounters(CosemObject):
    """
    DLMS G3PlcMacCounters object (Class ID 90) - G3-PLC MAC Layer Counters.

    Holds per-device MAC-layer packet statistics for G3-PLC (ITU-T G.9903)
    networks.  All counters are unsigned 32-bit integers.

    Method 1 (reset): clears all counters.  Because there is no server-side
    C dispatch for class 90, the ``on_before_action`` Python hook is the sole
    handler - set it to implement the actual PHY-level counter reset.

    Attributes:
        logical_name (str): DLMS logical name (OBIS code), e.g. ``"0.0.29.1.0.255"``.
        tx_data_packet_count (int): Total data packets transmitted (attr 2).
        rx_data_packet_count (int): Total data packets received (attr 3).
        tx_cmd_packet_count (int): Total command packets transmitted (attr 4).
        rx_cmd_packet_count (int): Total command packets received (attr 5).
        csma_fail_count (int): CSMA failures (attr 6).
        csma_no_ack_count (int): CSMA no-acknowledge count (attr 7).
        bad_crc_count (int): Frames rejected due to bad CRC (attr 8).
        tx_data_broadcast_count (int): Broadcast data packets transmitted (attr 9).
        rx_data_broadcast_count (int): Broadcast data packets received (attr 10).

    Example::

        counters = dlms.G3PlcMacCounters("0.0.29.1.0.255")
        counters.tx_data_packet_count = 100

        def do_reset(self, event):
            self.tx_data_packet_count = 0
            self.rx_data_packet_count = 0
            # ... reset all counters in hardware ...

        counters.on_before_action = do_reset
    """
    logical_name: str
    tx_data_packet_count: int
    rx_data_packet_count: int
    tx_cmd_packet_count: int
    rx_cmd_packet_count: int
    csma_fail_count: int
    csma_no_ack_count: int
    bad_crc_count: int
    tx_data_broadcast_count: int
    rx_data_broadcast_count: int

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...


class G3PlcMacSetup(CosemObject):
    """
    DLMS G3PlcMacSetup object (Class ID 91) - G3-PLC MAC Layer Setup.

    Configures G3-PLC MAC layer parameters (tone mask, CSMA settings, neighbour
    table, etc.) for ITU-T G.9903 compliant devices.

    Method 1 (get_neighbour_table): Returns the neighbour table to the client.
    There is no server-side C dispatch for class 91; implement via
    ``on_before_action``.

    Neighbour table dict keys: ``short_address`` (int), ``payload_modulation_scheme``
    (int), ``tone_map`` (bytes), ``modulation`` (int), ``tx_gain`` (int),
    ``tx_res`` (int), ``tx_coeff`` (bytes), ``lqi`` (int), ``phase_differential``
    (int), ``tmr_valid_time`` (int), ``no_data`` (int).

    Key table dict keys: ``id`` (int), ``key`` (bytes, 16 bytes).

    MAC POS table dict keys: ``short_address`` (int), ``lqi`` (int), ``valid_time`` (int).

    Attributes:
        logical_name (str): DLMS logical name (OBIS code), e.g. ``"0.0.29.0.0.255"``.
        short_address (int): MAC short address of this node (attr 2).
        rc_coord (int): Routing cost to the coordinator (attr 3).
        pan_id (int): PAN identifier (attr 4).
        key_table (list[dict]): List of ``{id, key}`` dicts (attr 5).
        frame_counter (int): Frame counter (attr 6).
        tone_mask (bytes): Packed bit-array of active sub-carriers (attr 7).
        tmr_ttl (int): TMR time-to-live (attr 8).
        max_frame_retries (int): Maximum MAC frame retransmissions (attr 9).
        neighbour_table_entry_ttl (int): Neighbour entry lifetime in seconds (attr 10).
        neighbour_table (list[dict]): Neighbour table entries (attr 11).
        high_priority_window_size (int): HP contention window size (attr 12).
        cscm_fairness_limit (int): CSCM fairness limit (attr 13).
        beacon_randomization_window_length (int): Beacon randomisation window (attr 14).
        mac_a (int): MAC Wα weighting factor (attr 15).
        mac_k (int): MAC K CSMA parameter (attr 16).
        min_cw_attempts (int): Minimum contention window attempts (attr 17).
        cenelec_legacy_mode (int): CENELEC legacy mode flag (attr 18).
        fcc_legacy_mode (int): FCC legacy mode flag (attr 19).
        max_be (int): Maximum back-off exponent (attr 20).
        max_csma_backoffs (int): Maximum CSMA back-offs (attr 21).
        min_be (int): Minimum back-off exponent (attr 22).
        mac_broadcast_max_cw_enabled (int): Use max CW for broadcast (attr 23).
        mac_transmit_atten (int): Transmit attenuation in dB (attr 24).
        mac_pos_table (list[dict]): Neighbour POS table (attr 25).
        mac_duplicate_detection_ttl (int): Duplicate detection TTL in seconds (attr 26).
    """
    logical_name: str
    short_address: int
    rc_coord: int
    pan_id: int
    key_table: list
    frame_counter: int
    tone_mask: bytes
    tmr_ttl: int
    max_frame_retries: int
    neighbour_table_entry_ttl: int
    neighbour_table: list
    high_priority_window_size: int
    cscm_fairness_limit: int
    beacon_randomization_window_length: int
    mac_a: int
    mac_k: int
    min_cw_attempts: int
    cenelec_legacy_mode: int
    fcc_legacy_mode: int
    max_be: int
    max_csma_backoffs: int
    min_be: int
    mac_broadcast_max_cw_enabled: int
    mac_transmit_atten: int
    mac_pos_table: list
    mac_duplicate_detection_ttl: int

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...


class G3Plc6LoWPAN(CosemObject):
    """
    DLMS G3Plc6LoWPAN object (Class ID 92) - G3-PLC 6LoWPAN Adaptation Layer.

    Manages the 6LoWPAN/LOADng routing configuration for a G3-PLC network node,
    including routing table, blacklist, broadcast log, context information, and
    group membership tables.

    No COSEM methods are defined for class 92.

    Sub-struct dict keys:

    ``routing_configuration`` entries (14 keys):
        ``net_traversal_time``, ``routing_table_entry_ttl``, ``kr``, ``km``,
        ``kc``, ``kq``, ``kh``, ``krt``, ``rreq_retries``, ``rreq_req_wait``,
        ``blacklist_table_entry_ttl``, ``unicast_rreq_gen_enable``,
        ``rlc_enabled``, ``add_rev_link_cost``.

    ``routing_table`` entries (6 keys):
        ``destination_address``, ``next_hop_address``, ``route_cost``,
        ``hop_count``, ``weak_link_count``, ``valid_time``.

    ``context_information_table`` entries (5 keys):
        ``cid``, ``context_length``, ``context`` (bytes, 16), ``compression``,
        ``valid_lifetime``.

    ``blacklist_table`` entries (2 keys):
        ``neighbour_address``, ``valid_time``.

    ``broadcast_log_table`` entries (3 keys):
        ``source_address``, ``sequence_number``, ``valid_time``.

    Attributes:
        logical_name (str): DLMS logical name (OBIS code), e.g. ``"0.0.29.2.0.255"``.
        max_hops (int): Maximum LOADng routing hops (attr 2).
        weak_lqi_value (int): LQI threshold below which a link is "weak" (attr 3).
        security_level (int): Minimum security level for adaptation frames (attr 4).
        prefix_table (bytes): List of prefixes defined on this PAN (attr 5).
        routing_configuration (list[dict]): LOADng routing parameters (attr 6).
        broadcast_log_table_entry_ttl (int): Broadcast log TTL in minutes (attr 7).
        routing_table (list[dict]): LOADng routing table entries (attr 8).
        context_information_table (list[dict]): 6LoWPAN context information (attr 9).
        blacklist_table (list[dict]): Blacklisted neighbours (attr 10).
        broadcast_log_table (list[dict]): Broadcast log entries (attr 11).
        group_table (list[int]): Group addresses this device belongs to (attr 12).
        max_join_wait_time (int): Network join timeout in seconds (attr 13).
        path_discovery_time (int): Path discovery timeout in seconds (attr 14).
        active_key_index (int): Index of active GMK (attr 15).
        metric_type (int): LOADng routing metric type (attr 16).
        coord_short_address (int): Coordinator short address (attr 17).
        disable_default_routing (int): 1 = disable LOADng (attr 18).
        device_type (int): DLMS_PAN_DEVICE_TYPE enum value (attr 19).
        default_coord_route_enabled (int): 1 = create default route to coordinator (attr 20).
        destination_address (list[int]): Addresses for which this router provides connectivity (attr 21).
        low_lqi (int): Low LQI threshold (attr 22).
        high_lqi (int): High LQI threshold (attr 23).

    Note:
        G3Plc6LoWPAN (Class 92) defines no COSEM methods; ``on_before_action`` /
        ``on_after_action`` are never fired.
    """
    logical_name: str
    max_hops: int
    weak_lqi_value: int
    security_level: int
    prefix_table: bytes
    routing_configuration: list
    broadcast_log_table_entry_ttl: int
    routing_table: list
    context_information_table: list
    blacklist_table: list
    broadcast_log_table: list
    group_table: list
    max_join_wait_time: int
    path_discovery_time: int
    active_key_index: int
    metric_type: int
    coord_short_address: int
    disable_default_routing: int
    device_type: int
    default_coord_route_enabled: int
    destination_address: list
    low_lqi: int
    high_lqi: int

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...


class TokenStatusCode:
    """Token processing result codes (DLMS_TOKEN_STATUS_CODE_*).

    Example::
        if token_gw.token_status_code == TokenStatusCode.TOKEN_EXECUTION_OK:
            ...
    """
    FORMAT_OK: int = 0
    AUTHENTICATION_OK: int = 1
    VALIDATION_OK: int = 2
    TOKEN_EXECUTION_OK: int = 3
    TOKEN_FORMAT_FAILURE: int = 4
    AUTHENTICATION_FAILURE: int = 5
    VALIDATION_RESULT_FAILURE: int = 6
    TOKEN_EXECUTION_RESULT_FAILURE: int = 7
    TOKEN_RECEIVED: int = 8


class TokenDelivery:
    """Token delivery channel (DLMS_TOKEN_DELIVERY_*).

    Example::
        token_gw.token_delivery = TokenDelivery.REMOTE
    """
    REMOTE: int = 0
    LOCAL: int = 1
    MANUAL: int = 2


class CreditType:
    """Credit type (DLMS_CREDIT_TYPE_*).

    Example::
        credit_obj.type = CreditType.TOKEN
    """
    TOKEN: int = 0
    RESERVED: int = 1
    EMERGENCY: int = 2
    TIME_BASED: int = 3
    CONSUMPTION_BASED: int = 4


class CreditStatus:
    """Credit lifecycle status (DLMS_CREDIT_STATUS_*).

    Example::
        if credit_obj.status == CreditStatus.IN_USE:
            ...
    """
    ENABLED: int = 0
    SELECTABLE: int = 1
    INVOKED: int = 2
    IN_USE: int = 3
    CONSUMED: int = 4


class CreditConfiguration:
    """Credit configuration bitflags (DLMS_CREDIT_CONFIGURATION_*).
    Values may be OR-ed together.

    Example::
        credit_obj.credit_configuration = CreditConfiguration.VISUAL | CreditConfiguration.TOKENS
    """
    NONE: int = 0x00
    VISUAL: int = 0x01
    CONFIRMATION: int = 0x02
    PAID_BACK: int = 0x04
    RESETTABLE: int = 0x08
    TOKENS: int = 0x10


class CreditCollectionConfiguration:
    """Conditions under which credit is collected (DLMS_CREDIT_COLLECTION_CONFIGURATION_*).
    Values may be OR-ed together.

    Example::
        credit_obj.credit_collection_configuration = (
            CreditCollectionConfiguration.DISCONNECTED |
            CreditCollectionConfiguration.LOAD_LIMITING
        )
    """
    NONE: int = 0x00
    DISCONNECTED: int = 0x01
    LOAD_LIMITING: int = 0x02
    FRIENDLY_CREDIT: int = 0x04


class ChargeType:
    """Charge collection method (DLMS_CHARGE_TYPE_*).

    Example::
        charge_obj.charge_type = ChargeType.CONSUMPTION_BASED_COLLECTION
    """
    CONSUMPTION_BASED_COLLECTION: int = 0
    TIME_BASED_COLLECTION: int = 1
    PAYMENT_EVENT_BASED_COLLECTION: int = 2


class ChargeConfiguration:
    """Charge configuration bitflags (DLMS_CHARGE_CONFIGURATION_*).
    Values may be OR-ed together.

    Example::
        charge_obj.charge_configuration = ChargeConfiguration.CONTINUOUS_COLLECTION
    """
    NONE: int = 0x00
    PERCENTAGE_BASED_COLLECTION: int = 0x01
    CONTINUOUS_COLLECTION: int = 0x02


class AccountStatus:
    """Account lifecycle state (DLMS_ACCOUNT_STATUS_*).

    Example::
        account_obj.account_status = AccountStatus.ACTIVE
    """
    NEW_INACTIVE_ACCOUNT: int = 1
    ACTIVE: int = 2
    CLOSED: int = 3


class AccountPaymentMode:
    """Payment mode for an account (DLMS_ACCOUNT_PAYMENT_MODE_*).

    Example::
        account_obj.payment_mode = AccountPaymentMode.PREPAYMENT
    """
    CREDIT: int = 1
    PREPAYMENT: int = 2


class AccountCreditStatus:
    """Account credit status bitflags (DLMS_ACCOUNT_CREDIT_STATUS_*).
    Multiple flags can be active at once.

    Example::
        if account_obj.credit_status & AccountCreditStatus.LOW_CREDIT:
            alert_user()
        if account_obj.credit_status & AccountCreditStatus.OUT_OF_CREDIT:
            disconnect_supply()
    """
    NONE: int = 0x00
    IN_CREDIT: int = 0x01
    LOW_CREDIT: int = 0x02
    NEXT_CREDIT_ENABLED: int = 0x04
    NEXT_CREDIT_SELECTABLE: int = 0x08
    CREDIT_REFERENCE_LIST: int = 0x10
    SELECTABLE_CREDIT_IN_USE: int = 0x20
    OUT_OF_CREDIT: int = 0x40
    RESERVED: int = 0x80


class Currency:
    """Currency type used in Account.currency (DLMS_CURRENCY_*).

    Example::
        account_obj.currency = {"name": b"EUR", "scale": -2, "unit": Currency.MONETARY}
    """
    TIME: int = 0
    CONSUMPTION: int = 1
    MONETARY: int = 2


class TokenGateway(CosemObject):
    """
    DLMS TokenGateway object (Class ID 115) for token-based prepayment metering.

    Handles credit-token ingestion: validates incoming tokens, records the last
    processed token and its metadata, and exposes the resulting credit to Credit
    and Account objects.

    Attributes:
        logical_name (str): OBIS code string, default ``"0.0.19.40.0.255"``.
        token (bytes): Last accepted/processed token (raw bytes).
        time (tuple): Timestamp of last token processing as
            ``(year, month, day, hour, min, sec)``.
        descriptions (list[str]): Human-readable descriptions of credit types
            associated with this gateway.
        delivery_method (int): Token delivery method
            (``DLMS_TOKEN_DELIVERY`` enum value).
        status (int): Current token status (``DLMS_TOKEN_STATUS`` enum value).
        data_value (bytes): Bit-array representing the processed token data.

    Methods (invoked via ``on_before_action``):
        1 - enter(token): Submit a credit token for processing.
        2 - enter_DLMS_token: alternative token entry path.
        3 - enter_token_DLMS: alternative token entry path.
    """
    logical_name: str
    token: bytes
    time: tuple
    descriptions: list
    delivery_method: int
    status: int
    data_value: bytes

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...
    def deinit(self) -> None: ...


class Credit(CosemObject):
    """
    DLMS Credit object (Class ID 112) for managing a single prepayment credit.

    Each instance represents one credit account whose balance is tracked and
    drawn down as energy is consumed.  Multiple Credit objects may coexist in
    an Account.

    Attributes:
        logical_name (str): OBIS code string, default ``"0.0.19.10.0.255"``.
        current_credit_amount (int): Current credit balance (signed 32-bit).
        type (int): Credit type (``DLMS_CREDIT_TYPE`` enum value).
        priority (int): Credit priority (lowest priority consumed first).
        warning_threshold (int): Balance level at which a low-credit warning fires.
        limit (int): Minimum allowable balance (may be negative for debt headroom).
        credit_configuration (int): ``DLMS_CREDIT_CONFIGURATION`` bitmask flags.
        status (int): Current credit status bitmask.
        preset_credit_amount (int): Value loaded on next top-up.
        credit_available_threshold (int): Amount available before blocking.
        period (tuple): Timestamp as ``(year, month, day, hour, min, sec)``.

    Methods (invoked via ``on_before_action``):
        1 - update_amount(amount): Adjust current credit by delta.
        2 - set_amount_to_value(amount): Set credit to an absolute value.
        3 - invoke_credit: Apply a top-up from preset_credit_amount.
    """
    logical_name: str
    current_credit_amount: int
    type: int
    priority: int
    warning_threshold: int
    limit: int
    credit_configuration: int
    status: int
    preset_credit_amount: int
    credit_available_threshold: int
    period: tuple

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...


class Charge(CosemObject):
    """
    DLMS Charge object (Class ID 113) for consumption-based charging.

    Computes charges from energy/volume consumption using a tariff table and
    accumulates the result into the Account's aggregated debt.

    Attributes:
        logical_name (str): OBIS code string, default ``"0.0.19.20.0.255"``.
        total_amount_paid (int): Cumulative amount paid so far (signed 32-bit).
        charge_type (int): ``DLMS_CHARGE_TYPE`` enum value.
        priority (int): Determines order in which charges are applied.
        unit_charge_active (dict): Active tariff structure::

            {
              "charge_per_unit_scaling": {"commodity_scale": int, "price_scale": int},
              "commodity":               {"target": dlms_obj_or_none, "attribute_index": int},
              "charge_tables":           [{"index": bytes, "charge_per_unit": int}, ...]
            }

        unit_charge_passive (dict): Pending (next-period) tariff, same schema.
        unit_charge_activation_time (tuple): When passive becomes active,
            ``(year, month, day, hour, min, sec)``.
        period (int): Charging interval in seconds (uint32).
        charge_configuration (int): ``DLMS_CHARGE_CONFIGURATION`` bitmask.
        last_collection_time (tuple): Timestamp of last charge collection.
        last_collection_amount (int): Amount collected at last collection.
        total_amount_remaining (int): Balance still owed (signed 32-bit).
        proportion (uint16): Proportion factor (0-65535).

    Methods (invoked via ``on_before_action``):
        1 - update_unit_charge: Copy passive tariff tables to active.
        2 - activate: Activate the passive unit charge immediately.
        3 - collect: Perform a charge collection cycle.
        4 - update_last_collection_time: Update the collection timestamp.
        5 - update_total_amount_remaining: Recalculate remaining balance.
        6 - set_total_amount_paid: Reset the total-paid counter.
    """
    logical_name: str
    total_amount_paid: int
    charge_type: int
    priority: int
    unit_charge_active: dict
    unit_charge_passive: dict
    unit_charge_activation_time: tuple
    period: int
    charge_configuration: int
    last_collection_time: tuple
    last_collection_amount: int
    total_amount_remaining: int
    proportion: int

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...


class Account(CosemObject):
    """
    DLMS Account object (Class ID 111) - top-level prepayment controller.

    The Account links Credit and Charge objects, manages payment mode and status,
    and coordinates token gateway configurations.  It is the central entry point
    for prepayment operations.

    Attributes:
        logical_name (str): OBIS code string, default ``"0.0.19.0.0.255"``.
        payment_mode (int): ``DLMS_ACCOUNT_PAYMENT_MODE`` enum (1=credit, 2=prepayment).
        account_status (int): ``DLMS_ACCOUNT_STATUS`` enum.
        current_credit_in_use (int): Index of the Credit currently being drawn down.
        current_credit_status (int): ``DLMS_ACCOUNT_CREDIT_STATUS`` bitmask.
        available_credit (int): Sum of positive Credit balances.
        amount_to_clear (int): Debt amount to be cleared before credits are usable.
        clearance_threshold (int): Minimum payment needed to exit over-limit state.
        aggregated_debt (int): Total accumulated debt.
        credit_references (list[str]): OBIS strings for associated Credit objects.
        charge_references (list[str]): OBIS strings for associated Charge objects.
        credit_charge_configurations (list[dict]): List of::

            {"credit_reference": str, "charge_reference": str,
             "collection_configuration": int}

        token_gateway_configurations (list[dict]): List of::

            {"credit_reference": str, "token_proportion": int}

        account_activation_time (tuple): ``(year, month, day, hour, min, sec)``.
        account_closure_time (tuple): ``(year, month, day, hour, min, sec)``.
        currency (dict): ``{"name": str, "scale": int, "unit": int}``
            where *unit* is a ``DLMS_CURRENCY`` enum value.
        low_credit_threshold (int): Balance where a low-credit alarm is raised.
        next_credit_available_threshold (int): Balance below which next credit kicks in.
        max_provision (int): Maximum credit provision amount (uint16).
        max_provision_period (int): Maximum provisioning period in seconds (int32).

    Methods (all dispatched to ``on_before_action``; Account has no C dispatch):
        1-18: Various prepayment management methods (activate, deactivate,
              update_credit, clear_debt, set_payment_mode, etc.).
    """
    logical_name: str
    payment_mode: int
    account_status: int
    current_credit_in_use: int
    current_credit_status: int
    available_credit: int
    amount_to_clear: int
    clearance_threshold: int
    aggregated_debt: int
    credit_references: list
    charge_references: list
    credit_charge_configurations: list
    token_gateway_configurations: list
    account_activation_time: tuple
    account_closure_time: tuple
    currency: dict
    low_credit_threshold: int
    next_credit_available_threshold: int
    max_provision: int
    max_provision_period: int

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...


class RequiredProtection:
    """Bitmask flags controlling which protection mechanisms are required
    for access to a DataProtection object (DLMS_REQUIRED_PROTECTION).

    These values may be OR-combined.
    """
    NONE: int
    """No protection required (0x00)."""
    AUTHENTICATED_REQUEST: int
    """Requests must be authenticated (0x04)."""
    ENCRYPTED_REQUEST: int
    """Requests must be encrypted (0x08)."""
    DIGITALLY_SIGNED_REQUEST: int
    """Requests must be digitally signed (0x10)."""
    AUTHENTICATED_RESPONSE: int
    """Responses must be authenticated (0x20)."""
    ENCRYPTED_RESPONSE: int
    """Responses must be encrypted (0x40)."""
    DIGITALLY_SIGNED_RESPONSE: int
    """Responses must be digitally signed (0x80)."""


class ProtectionType:
    """Type of cryptographic protection applied (DLMS_PROTECTION_TYPE).

    Used as the first element of each ``protection_parameters_get/set`` tuple.
    """
    AUTHENTICATION: int
    """Authentication-only protection (1)."""
    ENCRYPTION: int
    """Encryption-only protection (2)."""
    AUTHENTICATION_ENCRYPTION: int
    """Combined authentication and encryption (3)."""


class DataProtectionKeyType:
    """Key-choice discriminant for the inner key_info tuple
    (DLMS_DATA_PROTECTION_KEY_TYPE).

    Used as the first element of the ``key_info`` nested tuple inside each
    ``protection_parameters_get/set`` entry.
    """
    IDENTIFIED: int
    """Pre-shared identified key (0).  Pair with ``IdentifiedKeyType``."""
    WRAPPED: int
    """Wrapped (encrypted) key (1).  Pair with ``WrappedKeyType`` + key bytes."""
    AGREED: int
    """Agreed key (key agreement, e.g. ECDH) (2).  Pair with params + data bytes."""


class IdentifiedKeyType:
    """Identified key sub-type (DLMS_DATA_PROTECTION_IDENTIFIED_KEY_TYPE).

    Used as the second element of a ``(DataProtectionKeyType.IDENTIFIED, ...)``
    key_info tuple.
    """
    UNICAST_ENCRYPTION: int
    """Global unicast encryption key (0)."""
    BROADCAST_ENCRYPTION: int
    """Global broadcast encryption key (1)."""


class WrappedKeyType:
    """Wrapped key sub-type (DLMS_DATA_PROTECTION_WRAPPED_KEY_TYPE).

    Used as the second element of a ``(DataProtectionKeyType.WRAPPED, ...)``
    key_info tuple.
    """
    MASTER_KEY: int
    """Master key (0)."""



class StatusMapping(CosemObject):
    """DLMS StatusMapping object (Class ID 63, version 0).

    Represents a status word and a mapping between status bits and COSEM entries.

    Note: All attribute GET operations for attrs 2 and 3 are handled internally;
    all remote SET operations are rejected with ``READ_WRITE_DENIED``
    (update via the Python API directly).

    Attributes:
        logical_name: OBIS code string (e.g. ``"0.0.96.5.4.255"``).
        status_word: 2-tuple ``(dlms_type: int, value: int | bytes)`` - attribute 2.

            The CHOICE type tag selects the encoding:

            ============  ===  =========================
            DLMS type     Tag  ``value`` Python type
            ============  ===  =========================
            unsigned       17  ``int`` (0-255)
            long-unsigned  18  ``int`` (0-65535)   **default**
            uint32          6  ``int`` (0-2³²-1)
            uint64         21  ``int``
            bit-string      4  ``bytes`` (bit count = len×8)
            octet-string    9  ``bytes``
            visible-string 10  ``bytes``
            utf8-string    12  ``bytes``
            ============  ===  =========================

            Default: ``(18, 0)`` - long-unsigned, all bits clear.

        mapping_table: 2-tuple ``(ref_table_id: int, mapping: int | List[int])``
            - attribute 3.

            * If *mapping* is an ``int``: long-unsigned CHOICE - single starting
              entry index into the referenced table.
            * If *mapping* is a ``list[int]``: array CHOICE - one uint16 per bit
              position mapping to a referenced-table entry.

            Default: ``(0, 0)`` - ref_table_id 0, single entry 0.

    """
    logical_name: str
    status_word: Tuple[int, Union[int, bytes]]
    mapping_table: Tuple[int, Union[int, List[int]]]

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...


class Arbitrator(CosemObject):
    """DLMS Arbitrator object (Class ID 68).

    Resolves conflicts between concurrent requests from different actors using
    a weighted permissions model.

    Note: The C implementation has no dispatch for class 68.  All action
    methods (``push``, method 1) must be handled by ``on_before_action``.

    Attributes:
        logical_name: OBIS code string (e.g. ``"0.0.96.5.4.255"``).
        actions: list of ``(ScriptTable_obj_or_None, selector:int)`` tuples -
            the requested actions indexed by action ID.
        permissions_table: list of ``bytes`` - one bitset row per actor,
            bit N set = actor has permission for action N.
        weightings_table: list of ``list[int]`` - uint16 weights;
            outer index = actor, inner index = action.
        most_recent_requests_table: list of ``bytes`` - most recent requests
            for each actor as bitsets.
        last_outcome: ``int`` (0-255) - the number of the winning action after
            the last arbitration.
    """
    logical_name: str
    actions: List[Tuple[Any, int]]
    permissions_table: List[bytes]
    weightings_table: List[List[int]]
    most_recent_requests_table: List[bytes]
    last_outcome: int

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...


class DataProtection(CosemObject):
    """DLMS DataProtection object (Class ID 30).

    Provides cryptographic protection for DLMS data.

    Note: Attribute GET operations and action dispatch for class 30 are not
    implemented natively.  All READ/ACTION behaviour must be driven via
    ``on_before_read`` / ``on_before_action`` Python callbacks.

    Attributes:
        logical_name: OBIS code string (e.g. ``"0.0.29.0.0.255"``).
        protection_buffer: ``bytes`` - protection buffer (attr 2).
        required_protection: ``int`` - bitmask of ``RequiredProtection`` flags (attr 6).
        protection_object_list: List of 3-tuples ``(object_or_None, attribute_index: int,
            data_index: int)`` describing the protected COSEM objects (attr 3)::

                data_protection.protection_object_list = [
                    (my_register, 2, 0),
                ]

        protection_parameters_get: List of 6-tuples for GET protection parameters
            (attr 4).  Each tuple: ``(protection_type, id, originator, recipient,
            information, key_info)`` where all byte fields are ``bytes`` and
            ``key_info`` is a nested tuple keyed by ``DataProtectionKeyType``:

            - **IDENTIFIED**: ``(DataProtectionKeyType.IDENTIFIED, IdentifiedKeyType.X)``
            - **WRAPPED**:    ``(DataProtectionKeyType.WRAPPED, WrappedKeyType.X, key: bytes)``
            - **AGREED**:     ``(DataProtectionKeyType.AGREED, params: bytes, data: bytes)``

            Example::

                data_protection.protection_parameters_get = [
                    (ProtectionType.AUTHENTICATION, b'', b'', b'', b'',
                     (DataProtectionKeyType.IDENTIFIED,
                      IdentifiedKeyType.UNICAST_ENCRYPTION)),
                ]

        protection_parameters_set: Same format as ``protection_parameters_get``
            but for SET operations (attr 5).
    """
    logical_name: str
    protection_buffer: bytes
    required_protection: int
    protection_object_list: List[Tuple[Any, int, int]]
    protection_parameters_get: List[Tuple]
    protection_parameters_set: List[Tuple]

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...
    def deinit(self) -> None: ...


class MbusMasterPortSetup(CosemObject):
    """
    DLMS MbusMasterPortSetup object (Class ID 74) for M-Bus master port configuration.

    Exposes the communication speed of the M-Bus master port to a DLMS client.
    The QuecPython device is acting as the M-Bus **master / concentrator** when
    this object is present.

    Attributes:
        logical_name (str): DLMS logical name (OBIS code) string.
        comm_speed (int): M-Bus communication speed as an integer (e.g. ``9600``).
            Valid values: 300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600,
            115200.  A ``ValueError`` is raised for any other value.

    Methods: None (class 74 defines no COSEM methods).

    Note:
        MbusMasterPortSetup has no COSEM methods; ``on_before_action`` /
        ``on_after_action`` are never fired.

    Example::

        mbus_master = dlms.MbusMasterPortSetup("0.0.24.3.0.255")
        mbus_master.comm_speed = 9600
    """
    logical_name: str
    comm_speed: int

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...


class MbusDiagnostic(CosemObject):
    """
    DLMS MbusDiagnostic object (Class ID 77) for M-Bus channel diagnostics.

    Monitors link quality, broadcast-frame counters, and transmission statistics
    for a single M-Bus communication channel.

    Attributes:
        logical_name (str): DLMS logical name (OBIS code) string.
        received_signal_strength (int): Received signal strength in dBµV (0-255).
        channel_id (int): M-Bus channel identifier (0-255).
        link_status (int): Current link state (DLMS_MBUS_LINK_STATUS enum value).
        broadcast_frames (list[dict]): List of ``{'client_id': int, 'counter': int,
            'timestamp': tuple}`` dicts describing per-client broadcast counters.
        transmissions (int): Total number of transmitted M-Bus frames.
        received_frames (int): Total number of successfully received frames.
        failed_received_frames (int): Number of frames received with errors.
        capture_time (dict): ``{'attribute_id': int, 'timestamp': tuple}`` giving
            the attribute that was last captured and when.

    Example::

        diag = dlms.MbusDiagnostic("0.0.24.8.0.255")
        diag.received_signal_strength = 120

        def on_reset(self, event):
            if event.index == 1:
                reset_hardware_counters()

        diag.on_before_action = on_reset
    """
    logical_name: str
    received_signal_strength: int
    channel_id: int
    link_status: int
    broadcast_frames: list
    transmissions: int
    received_frames: int
    failed_received_frames: int
    capture_time: dict

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...

    def reset(self) -> None:
        """COSEM method 1 - reset all counters (invoked by the server event loop)."""
        ...


class MbusPortSetup(CosemObject):
    """
    DLMS MbusPortSetup object (Class ID 76) for M-Bus port configuration.

    Describes the communication port used by an M-Bus master device.

    Attributes:
        logical_name (str): DLMS logical name (OBIS code) string.
        profile_selection (str): OBIS code of the associated profile (6-byte OBIS).
        port_communication_status (int): Current port state (DLMS_MBUS_PORT_COMMUNICATION_STATE).
        data_header_type (int): Data header type (DLMS_MBUS_DATA_HEADER_TYPE).
        primary_address (int): M-Bus primary address (0-255).
        identification_number (int): M-Bus identification number.
        manufacturer_id (int): 2-byte manufacturer identifier.
        mbus_version (int): M-Bus protocol version.
        device_type (int): Meter device type (DLMS_MBUS_METER_TYPE).
        max_pdu_size (int): Maximum protocol data unit size in bytes.
        listening_window (list[list]): Ordered list of ``[start_tuple, end_tuple]``
            pairs, where each tuple is ``(year, month, day, hour, min, sec)``.
            Use ``0xFFFF`` / ``0xFF`` for wildcard ("any") date fields.

    Note:
        MbusPortSetup has no COSEM methods; ``on_before_action`` /
        ``on_after_action`` are never fired.

    Example::

        port = dlms.MbusPortSetup("0.0.24.7.0.255")
        port.primary_address = 1
        port.listening_window = [
            [(ANY, ANY, ANY, 8, 0, 0),
             (ANY, ANY, ANY, 18, 0, 0)]
        ]
    """
    logical_name: str
    profile_selection: str
    port_communication_status: int
    data_header_type: int
    primary_address: int
    identification_number: int
    manufacturer_id: int
    mbus_version: int
    device_type: int
    max_pdu_size: int
    listening_window: list

    def __init__(
        self,
        logical_name: str,
        access: Optional[dict] = None,
    ): ...


class MbusClient(CosemObject):
    """
    DLMS MbusClient object (Class ID 72) representing an M-Bus slave meter.

    Links a slave meter to its port (``MbusPortSetup``) and stores capture
    definitions plus identification/status fields.

    Attributes:
        logical_name (str): DLMS logical name (OBIS code) string.
        capture_period (int): Capture interval in seconds.
        primary_address (int): M-Bus primary address (0-255).
        mbus_port: Reference to the ``MbusPortSetup`` port object (or ``None``).
        capture_definition (list[tuple]): List of ``(data_bytes, value_bytes)``
            tuples that define which M-Bus data records are captured
            (each element is a ``(bytes, bytes)`` pair).
        identification_number (int): Slave meter identification number.
        manufacturer_id (int): 2-byte manufacturer code.
        data_header_version (int): M-Bus data header version.
        device_type (int): Meter device type.
        access_number (int): Access number counter.
        status (int): Current meter status byte.
        alarm (int): Current meter alarm byte.
        configuration (int): 2-byte configuration word.
        encryption_key_status (int): Encryption key status (DLMS_MBUS_ENCRYPTION_KEY_STATUS).

    Example::

        port   = dlms.MbusPortSetup("0.0.24.7.0.255")
        client = dlms.MbusClient("0.0.24.1.0.255", mbus_port=port)
        client.capture_period = 900   # 15 min
        client.device_type = 3        # gas meter

        def on_capture(self, event):
            if event.index == 3:  # capture method
                update_client_data(client)

        client.on_before_action = on_capture
    """
    logical_name: str
    capture_period: int
    primary_address: int
    mbus_port: Optional[object]
    capture_definition: list
    identification_number: int
    manufacturer_id: int
    data_header_version: int
    device_type: int
    access_number: int
    status: int
    alarm: int
    configuration: int
    encryption_key_status: int

    def __init__(
        self,
        logical_name: str,
        mbus_port: Optional[object] = None,
        access: Optional[dict] = None,
    ): ...


class SapAssignment:
    """
    DLMS SapAssignment object for SAP (Service Access Point) configuration.

    Attributes:
        logical_name (bytes): DLMS logical name (OBIS code) as bytes.
        sap_assignment_list (list): List of (sap_id, logical_device_name) tuples.

    Methods:
        connect_logical_device(sap_id, device_name): Adds or updates a SAP assignment.

    Example:
        sap = SapAssignment(
            logical_name='0.0.41.0.0.255',
            sap_assignment_list=[(1, b'GRX0000000012345')]
        )
        
        # Add or update SAP assignment
        sap.connect_logical_device(2, b'GRX0000000067890')
    """
    logical_name: bytes
    sap_assignment_list: list
    def __init__(
        self,
        logical_name: str,
        sap_assignment_list: Optional[list] = None
    ): ...
    def connect_logical_device(self, sap_id: int, device_name: bytes | str) -> None: ...

def set_kek(kek: bytes) -> None:
    """Sets the KEK (Key Encryption Key) / master key for key wrapping.
    
    :param kek: 16-byte master key for key encryption
    """
    ...

def get_kek() -> bytes:
    """Gets the current KEK (Key Encryption Key) / master key.
    
    :return: 16-byte master key
    """
    ...

def set_default_access(obj_class: type, access: dict) -> None:
    """Sets class-level default access control for a DLMS object type.
    
    :param obj_class: DLMS object class (e.g., Register, Data, ProfileGeneric)
    :param access: Dictionary mapping attribute index to (AccessMode, Authentication) tuples
    
    Example:
        set_default_access(Register, {
            2: (AccessMode.READ, Authentication.NONE),
        })
        set_default_access(Data, {
            2: (AccessMode.READ_WRITE, Authentication.HIGH),
        })
    """
    ...

def hdlc_server_address(serial: int) -> int:
    """Computes the HDLC server address for a board identified by its serial number.

    The relay routes DLMS frames to boards by HDLC server address using the formula::

        server_address = (serial % 10000) + 1000

    Examples:
        serial 12345  ->  server_address 3345
        serial  5678  ->  server_address 6678
        serial  1000  ->  server_address 2000

    :param serial: Board serial number (non-negative integer).
    :return: HDLC server address to pass to ``dlms.Client(server_address=...)``.
    """
    ...

class Serializer:
    """Abstract base class for DLMS serializers (defined in ``dlms_serializer.py``).

    Subclass this to implement custom back-ends (EEPROM, cloud, MQTT, etc.).
    Override ``save_all``, ``load_all``, ``save``, and ``load``.
    ``ignore`` has a default implementation that stores entries in
    ``self._ignored`` for subclasses to inspect.

    Example::

        class MySerializer(dlms_serializer.Serializer):
            def save_all(self, server):
                for obj in server.object_registry:
                    self._write_somewhere(obj)
            def load_all(self, server): ...
            def save(self, obj): ...
            def load(self, obj): ...
    """

    def __init__(self) -> None: ...

    def ignore(self, target: object, attribute: int) -> None:
        """Register a (type-or-instance, attribute-index) pair to skip.

        Stores the entry in ``self._ignored``; subclasses may read it to
        implement filtering.
        """
        ...

    def save_all(self, server_or_list: object) -> None: ...
    def load_all(self, server_or_list: object) -> None: ...
    def save(self, obj: object) -> None: ...
    def load(self, obj: object) -> None: ...


class BinarySerializer(Serializer):
    """Serializes and restores DLMS object attributes to/from per-object binary
    files stored in a directory on the Helios filesystem.

    Each DLMS object is saved to a separate file named ``<ln>.bin``
    (e.g. ``1.1.33.25.0.255.bin``) inside the given directory.
    The directory must already exist (``/usr`` is always available).

    Example::

        ser = dlms.BinarySerializer("/usr")
        ser.ignore(dlms.ProfileGeneric, 2)   # skip capture buffer
        ser.ignore(dlms.Clock, 2)            # skip current time
        ser.save_all(server)                 # persist all objects

        # on next boot:
        ser = dlms.BinarySerializer("/usr")
        ser.ignore(dlms.ProfileGeneric, 2)
        ser.ignore(dlms.Clock, 2)
        ser.load_all(server)
    """

    def __init__(self, dir: str) -> None:
        """Create a serializer targeting *dir*.

        :param dir: Path to an existing writable directory, e.g. ``"/usr"``.
                    A trailing slash is stripped automatically.
        """
        ...

    def save(self, obj: object) -> None:
        """Save a single DLMS object to ``{dir}/{ln}.bin``.

        :param obj: Any DLMS object (Register, Clock, Data, …).
        :raises TypeError: If *obj* is not a recognised DLMS object.
        :raises OSError: If the file cannot be opened or written.
        :raises RuntimeError: If the Gurux serialiser reports an error.
        """
        ...

    def load(self, obj: object) -> None:
        """Restore a single DLMS object from ``{dir}/{ln}.bin``.

        :param obj: Any DLMS object.
        :raises TypeError: If *obj* is not a recognised DLMS object.
        :raises OSError: If the file cannot be opened.
        :raises RuntimeError: If the Gurux deserialiser reports an error.
        """
        ...

    def save_all(self, server_or_list: object) -> None:
        """Save every DLMS object in *server_or_list*.

        :param server_or_list: A ``Server`` instance or a plain ``list`` of
                               DLMS objects.
        :raises TypeError: If the argument is neither a Server nor a list.
        :raises OSError: If any file cannot be written (e.g. disk full).
        :raises RuntimeError: On serialiser error; the message includes the
                              zero-based object index and the Gurux error code.
        """
        ...

    def load_all(self, server_or_list: object) -> None:
        """Restore every DLMS object in *server_or_list*.

        Objects whose ``.bin`` file does not exist are silently skipped
        (first-boot convenience — no file means "use the compiled-in defaults").

        :param server_or_list: A ``Server`` instance or a plain ``list`` of
                               DLMS objects.
        :raises TypeError: If the argument is neither a Server nor a list.
        :raises OSError: On unexpected I/O error (not raised for missing files).
        :raises RuntimeError: On deserialiser error.
        """
        ...

    def get_size(self, server_or_list: object) -> int:
        """Return the total byte count of all existing ``.bin`` files for the
        objects in *server_or_list* (non-destructive — files are not modified).

        :param server_or_list: A ``Server`` instance or a plain ``list``.
        :return: Sum of file sizes in bytes; 0 for objects with no saved file.
        """
        ...

    def ignore(self, target: object, attribute: int) -> None:
        """Exclude *attribute* of *target* from serialization and
        deserialization.

        Can be called with either a DLMS **class** (affects every instance of
        that class) or a specific DLMS **object instance** (affects only that
        one object).

        :param target: A DLMS type (e.g. ``dlms.ProfileGeneric``) or a specific
                       DLMS object instance.
        :param attribute: 1-based attribute index to skip (e.g. ``2`` for the
                          value/buffer attribute of most objects).
        :raises RuntimeError: If the ignore list is full
                              (capacity is fixed at compile time).

        Example::

            ser.ignore(dlms.ProfileGeneric, 2)  # skip buffer for all PG objects
            ser.ignore(my_register, 3)          # skip scaler/unit for one object
        """
        ...


# ---------------------------------------------------------------------------
# JsonSerializer — defined in dlms_serializer.py (pure Python)
# ---------------------------------------------------------------------------

class JsonSerializer(Serializer):
    """Serialize/deserialize DLMS object attributes in per-object JSON files.

    Defined in ``dlms_serializer.py``.  Import it from there::

        from dlms_serializer import JsonSerializer

    Each object is saved to ``{dir}/{logical_name}.json`` (e.g.
    ``/usr/1.2.3.4.5.6.json``).

    Binary values (security keys, OCTET STRINGs) are not losslessly
    representable in JSON — use :class:`BinarySerializer` when full round-trip
    fidelity is required.

    Example::

        from dlms_serializer import JsonSerializer

        ser = JsonSerializer("/usr")
        ser.ignore(dlms.Register, 2)   # skip value of all Registers
        ser.save_all(server)

        # on next boot:
        ser.load_all(server)
    """

    def __init__(self, path: str) -> None:
        """
        :param path: Path to an existing directory (e.g. ``"/usr"``).
        """
        ...

    def save_all(self, server_or_list: object) -> None:
        """Serialize all objects to per-object JSON files."""
        ...

    def load_all(self, server_or_list: object) -> None:
        """Restore objects from per-object JSON files (missing files skipped)."""
        ...

    def save(self, obj: object) -> None:
        """Persist one object to ``{dir}/{logical_name}.json``."""
        ...

    def load(self, obj: object) -> None:
        """Load one object from ``{dir}/{logical_name}.json`` if present."""
        ...