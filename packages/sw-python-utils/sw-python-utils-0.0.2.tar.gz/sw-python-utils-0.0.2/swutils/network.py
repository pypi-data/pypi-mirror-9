# coding: utf-8
import re
import netifaces

def get_ip4():
    """
    return all ip v4 address of current computer
    :return:
    """
    addresses = []
    for name in netifaces.interfaces():
        for info_array in netifaces.ifaddresses(name).values():
            for info in info_array:
                if info.get('addr'):
                    addr = info['addr']
                    if re.match(r'\d{1,4}\.\d{1,4}\.\d{1,4}\.\d{1,4}', addr):
                        addresses.append(addr)
    return addresses