# pyi文件介绍

本文件主要简单介绍pyi文件如何编写。详细介绍请参阅：<https://peps.python.org/pep-0484/>

什么是pyi文件？
在Python3中，`.pyi`文件是存根文件(stub file)。这个"pyi"中的"i"代表接口即interface，作为公共接口。
**存根文件仅包含模块公共接口的描述，没有任何实现。**

编写请参考模板：`usocket.pyi`

# 示例讲解

## 示例一

以下是pyi文件的函数定义

- 1、如下参数后通过冒号标识该参数的类型（python基础类型：str、int、list、tuple...更多自定义类型参阅PEP484）。
- 2、函数定义关键字def语句中，形参列表后，冒号前通过`-> {类型}`来标识当前函数的返回值类型。
- 3、函数体首行注释（注：必须是三对双引号的注释且必须是函数体首行）
- 4、文档建议采用reStructuredText风格。详细请参阅：<https://wiki.python.org/moin/reStructuredText>

```python
def getaddrinfo(host: str, port: int = 8080):
    """Parses the domain name of DNS. —— （此处是当前函数的简略注释信息。）

    Parses the domain name of the host (host) and port (port) into a 5-tuple sequence used to create the socket. The structure of the tuple is below:
    (family, type, proto, canonname, sockaddr) —— （此处是当前函数的详细注释信息。）
    
    @param host: The domain name of the host.
    @param port: The port.
    @return: (family, type, proto, canonname, sockaddr)
    """
    ...  # 注：pyi文件中允许使用"..."代替任何实现细节。它是仅包含类型信息的文件，没有运行时代码。另，此处函数体可以留空，`...`是非必要的。
```

## 示例二

该示例表示一个只有单行文档注释的函数定义。

```python
def allocate_lock():
    """Creates and Return a mutex object."""
```


## 示例三

```python
AF_INET = ...  # 地址族，IPV4类型。
AF_INET6 = ...  # 地址族，IPV6类型。
SOCK_STREAM = ...  # socket类型，TCP的流式套接字。
IPPROTO_TCP = ...  # 协议号，TCP协议。
IPPROTO_UDP = ...  # 协议号，UDP协议。


class socket(object):
    """Socket"""

    def __init__(self, af=AF_INET, type=SOCK_STREAM, proto=IPPROTO_TCP):
        """Socket对象初始化函数。
    	
    	NOTE:
        根据给定的地址族、套接字类型以及协议类型参数，创建一个新的套接字对象。
        在大多数情况下不需要指定proto，也不建议这样做，因为某些MicroPython端口可能会省略IPPROTO_*常量。
    
        @af:地址族（参考常量说明）。
        @type:socket类型（参考常量说明）。
        @proto:协议号（参考常量说明）。
        """
    
    def bind(self, address: tuple = ("192.168.0.1", 80)):
        """该方法用于套接字绑定指定address，必须尚未绑定。
    	
    	NOTE:
        1、作为服务器时，需要进行绑定，以固定服务器的address。
        2、作为客户端时，绑定address用来指定套接字进行数据处理（配合usocket.TCP_CUSTOMIZE_PORT使用）。
    
        @address:包含地址和端口号的元组或列表。
        """
    
    def listen(self, backlog: int):
        """该方法用于套接字服务端开启监听客户端连接，可指定最大客户端连接数。
    
        @backlog:接受套接字的最大个数，至少为0。
        """
    
    def accept(self):
        """该方法用于套接字服务端接受连接请求。
    
        @return:成功返回元组，包含新的套接字和客户端地址以及客户端端口，形式为：(conn,address,port)。
        conn,新的套接字对象，用来和客户端交互;
        address,连接到服务器的客户端地址;
        port,连接到服务器的客户端端口。
        """
```
