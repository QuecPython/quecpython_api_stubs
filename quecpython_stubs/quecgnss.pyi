"""
Function:
This feature provides the APIs of the built-in GNSS feature.
Only EC200UCNAA/EC200UCNLA/EC200UEUAA/EC800MCNGA/EC800GCNGA series module supports this feature.

Descriptions taken from:
https://developer.quectel.com/doc/quecpython/API_reference/en/gnsslib/quecgnss.html
"""


def init():
    """Initializes the built-in GNSS feature.

    :return:0 - Successful execution;-1 - Failed execution
    """


def get_state():
    """Gets the current working status of the built-in GNSS feature.

    :return:
    0	int	GNSS feature is disabled.
    1	int	GNSS firmware is being updated.
    2	int	GNSS is positioning. In this mode, the module can read the GNSS location data. After obtaining the location data, the user needs to analyze the corresponding sentence to determine whether the location data is effective. For example, if the status of GNRMC sentences is A or V, A indicates valid positioning and V indicates invalid positioning.
    """


def gnssEnable(opt):
    """Enables or disables GNSS feature. If you use the built-in GNSS feature for the first time after powering the module on, you need not call this function to enable GNSS feature, but call quecgnss.init() directly. quecgnss.init() will automatically enable the GNSS feature when GNSS feature is initialized.

    :param opt:Integer type. Enable or disable GNSS.0 - Disable the GNSS feature.;1 - Enable the GNSS feature.
    :return:0 - Successful execution;-1 - Failed execution
    """


def read(size):
    """Gets GNSS location data.

    :param size:Integer type. Size of the data to be read. Unit: byte.
    :return:A tuple (size, data) - Successful execution
        size - Size of the data read.
        data - GNSS location data.
    """

def setPriority(Priority):
    """Sets the priority between GNSS and LTE for radio resource usage.

    :param Priority: int. The priority value to set. Meaning:
    Priority    BG95M1/M3
    0    GNSS > LTE
    1    LTE > GNSS
    :return: int. 0 for success, -1 for failure.
    """

def getPriority():
    """Gets the current priority between GNSS and LTE for radio resource usage.

    Priority    BG95M1/M3
    0    GNSS > LTE
    1    LTE > GNSS
    :return: int. The current priority value. Meaning:
    """

def configSet(config_type, config_value):
    """Sets GNSS configuration parameters.

    :param config_type: int. Configuration option type:
    Value    Description
    0       Configure satellite system
    1       Configure output NMEA sentence type
    2       Configure AGPS enable status
    3       Configure APFLASH enable status
    4       Configure GNSS backup power status

    :param config_value: int. Configuration value based on config_type:
        
    For config_type = 0 (satellite system):
    Value    Description
    0    GPS
    1    GPS + BeiDou
    3    GPS + GLONASS + Galileo
    4    GPS + GLONASS
    5    GPS + BeiDou + Galileo
    6    GPS + Galileo
    7    BeiDou
        
    For config_type = 1 (NMEA sentence type - bitmap):
    Value (decimal)    Binary    Description
    0    000000    Disable all
    1    000001    GGA
    2    000010    RMC
    4    000100    GSV
    8    001000    GSA
    16    010000    VTG
    32    100000    GLL
    63    111111    All output
        
    For config_type = 2 (AGPS enable):
    Value     Description
    0    Disable
    1    Enable
        
    For config_type = 3 (APFLASH enable):
    Value    Description
    0    Disable
    1    Enable
        
    For config_type = 4 (Backup power - EC800M GB/GD series only):
    Value    Description
    0    Disable
    1    Enable

    :return: int. 0 for success, non-zero for failure.
    """

def configGet(config_type):
    """Gets current GNSS configuration parameters.

    :param config_type: int. Configuration option type:
    Value    Description
    0    Satellite system
    1    Output NMEA sentence type
    2    AGPS enable status
    3    APFLASH enable status
    4    GNSS backup power status

    :return: int. Current configuration value. Meaning:
        
    For config_type = 0 (satellite system):
    Value   Description
    0    GPS
    1    GPS + BeiDou
    3    GPS + GLONASS + Galileo
    4    GPS + GLONASS
    5    GPS + BeiDou + Galileo
    6    GPS + Galileo
    7    BeiDou
    -1   Failure
        
    For config_type = 1 (NMEA sentence type):
    Value    Description
    0    Disabled
    1    GGA
    2    RMC
    4    GSV
    8    GSA
    16   VTG
    32   GLL
    63   All enabled
    Other    Bitwise combination of enabled sentences
    -1   Failure
        
    For config_type = 2 (AGPS status):
    Value    Description
    0    Disabled
    1    Enabled
    -1   Failure
        
    For config_type = 3 (APFLASH status):
    Value    Description
    0    Disabled
    1    Enabled
    -1   Failure
        
    For config_type = 4 (Backup power status):
    Value     Description
    0     Disabled
    1     Enabled
    -1    Failure
    """