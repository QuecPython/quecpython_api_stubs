
def bootstrap(et, pk, dk, mcc):
    """bootstrap
    
    :param et: et
    :param pk: pk
    :param dk: dk
    :param mcc: mcc
    :return:
    """
    ...


def state():
    """get state"""
    ...


def register(url, lifetime, pk, ps, dk):
    """mqtt register
    
    url: mqtt url
    lifetime: lifetime
    pk: pk
    ps: ps
    dk: dk
    """
    ...


def login(url, lifetime, pk, ps, dk, ds):
    """mqtt login
    
    url: mqtt url
    lifetime: lifetime
    pk: pk
    ps: ps
    dk: dk
    ds: ds
    """
    ...


def reset(url, lifetime, pk, ps, dk, ds):
    """mqtt reset
    
    url: mqtt url
    lifetime: lifetime
    pk: pk
    ps: ps
    dk: dk
    ds: ds
    """
    ...


def send(topic_type, cmd, payload, pkgId=0, qos=0):
    """mqtt send
    
    topic_type: topic_type
    cmd: cmd
    payload: payload
    pkgId: pkgId
    qos: qos
    """
    ...
