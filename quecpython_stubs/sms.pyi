"""
SMS (Short Message Service)
The sms module provides SMS functionality including reading, sending, deleting messages, and configuration.

Note: This module is not supported on the following models:
EC800GCN_LD, EC800GCN_LB, EC800MCN_LE, EC800MCN_GA, EC600MCN_LF, 
EC600MCN_LA, EC800MCN_GD, EC600MCN_CC, EG810MCN_GA, EC600MCN_LE, 
BC25, EC600GCN_LD, EC600KCN_LC, EC800MCN_LF, EC600GCN_LD.
For custom versions, actual functionality may vary.

Descriptions taken from:
https://developer.quectel.com/doc/quecpython/API_reference/zh/iotlib/sms.html
"""


def sendTextMsg(phoneNumber: str, msg: str, codeMode: str) -> int:
    """Sends a text SMS message (empty messages not supported)
    
    :param phoneNumber: Recipient phone number (max 20 bytes)
    :param msg: Message content (max 140 bytes per message)
    :param codeMode: Encoding mode ('GSM' for English, 'UCS2' for Chinese/English)
    :return: 0 if successful, -1 if failed
    
    Note: Long message support varies by device series:
    - EC600N/EG912N/EG915N/EC200A: UCS2(420B), GSM(960B)
    - EC200U/EC600U/EG912U/EG915U: UCS2(280B), GSM(640B)
    - Others: UCS2(70B), GSM(160B)
    """

def sendPduMsg(phoneNumber: str, msg: str, codeMode: str) -> int:
    """Sends a PDU format SMS message (empty messages not supported)
    
    :param phoneNumber: Recipient phone number (max 20 bytes)
    :param msg: Message content (max 140 bytes per message)
    :param codeMode: Encoding mode ('GSM' or 'UCS2')
    :return: 0 if successful, -1 if failed
    
    Note: Long message support same as sendTextMsg()
    """

def deleteMsg(index: int, delmode: int = 0) -> int:
    """Deletes SMS messages by index
    
    :param index: Message index number
    :param delmode: Deletion mode (0: single message, 4: all messages)
    :return: 0 if successful, -1 if failed
    
    Note: The EC600G/EC800G series only supports the invocation method of sms.deleteMsg(index), and does not support the invocation method of sms.deleteMsg(index,delmode).
    """

def setSaveLoc(mem1: str, mem2: str, mem3: str) -> int:
    """Configures SMS storage locations
    
    :param mem1: Location for read/delete operations 
        Value	Meaning
        "SM"	SIM message storage
        "ME"	Mobile device information storage
        "MT"	Not supported yet
    :param mem2: Location for write/send operations 
    :param mem3: Location for received messages 
    :return: 0 if successful, -1 if failed
    
    Note: The default storage space for different series of messages varies. Users can set it according to their own needs. 
    For the EC600N/EG912N/EG915N/EC800M/EG810M/EC200A series, if you want to change the storage location of the received messages,
    you need to set both mem2 and mem3 simultaneously. 
    For the EC200U/EC600U/EG912U/EG915U/EC600G/EC800G series, you only need to set mem3.
    """

def getSaveLoc() -> tuple:
    """Gets current SMS storage configuration
    
    :return: 
        Success: Returns tuple data in the format ([loc1, current_nums, max_nums], [loc2, current_nums, max_nums], [loc3, current_nums, max_nums]), as shown in the table below: 
            Parameters	Type	Explanation
            loc1	 String	 The location where messages are read and deleted. The specific meaning is the same as mem1 in sms.setSaveLoc.
            loc2	 String	 The location where messages are written and sent. The specific meaning is the same as mem1 in sms.setSaveLoc.
            loc3	 String	 The storage location for received messages. The specific meaning is the same as mem1 in sms.setSaveLoc.
            current_nums	 Integer	 The current number of SMS messages in the space.
            max_nums	 Integer	 The maximum number of SMS messages that can be stored in the space.
        Failure: Return -1.
    """

def getMsgNums() -> int:
    """Gets total number of stored SMS messages
    
    :return: Message count or -1 on failure
    """

def searchPduMsg(index: int) -> str:
    """This method is used to obtain the content of the SMS in the PDU format.
    
    :param : Message index (0 to MAX-1)index - The index required to retrieve the SMS, an integer value, within the range of 0 to MAX - 1. MAX represents the maximum number of SMS that the module can store.
    :return: 
        Success: Returns the string-type PDU data, which is the content of the text message, including the time when the message was received.
        Therefore, the PDU data for the same text message content is different. 
        Failure: Returning integer -1.
    """

def searchTextMsg(index: int) -> tuple:
    """Retrieves text-format SMS content
    
    :param : integer value, and range for obtaining the SMS are required, which is 0 to MAX - 1. MAX represents the maximum number of SMS that the module can store.
    :return: Tuple or -1 on failure
        Parameter	Type	Explanation
        phoneNumber	String	Source phone number of the SMS
        msg	String	SMS content
        msgLen	Integer	SMS message length
    """

def getPduLength(pduMsg: str) -> int:
    """Gets actual length of PDU-formatted message
    
    :param pduMsg: PDU-formatted message string
    :return: Actual PDU message length or -1 on failure
    """

def decodePdu(pduMsg: str, pduLen: int) -> tuple:
    """Decodes PDU-formatted SMS content
    
    :param pduMsg: PDU-formatted message string
    :param pduLen: Actual PDU message length
    :return: Tuple (phoneNumber, msg, time, msgLen) or -1 on failure
        Parameter	Type	Explanation
        phoneNumber	String	Source phone number of the SMS
        msg	String	SMS content
        time	Integer	Time when the SMS was received
        msgLen	Integer	Length of the SMS message
    """

def getCenterAddr() -> str:
    """Gets current SMS center number
    
    :return: SMS center number string or -1 on failure
    """

def setCenterAddr(addr: str) -> int:
    """Sets SMS center number (not recommended for normal use)
    
    :param addr: New SMS center number
    :return: 0 if successful, -1 if failed
    """

def setCallback(usrFun: callable) -> int:
    """Registers callback for incoming SMS notifications
    
    :param usrFun: Callback function with signature:
        def callback(args: list):
            args[0]: SIM slot ID (int)
            args[1]: Message index (int)
            args[2]: Storage location (str)
    :return: 0 if successful, -1 if failed
    
    Note: Legacy callback formats also supported (see documentation)
    """