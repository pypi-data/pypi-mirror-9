#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import netifaces
import netaddr

def network_info():
    data = {}
    for ifn in netifaces.interfaces():
        link = netifaces.ifaddresses(ifn)[netifaces.AF_LINK][0]
        inet = None
        try:
            inet = netifaces.ifaddresses(ifn)[netifaces.AF_INET][0]
        except:
            pass

        data[ifn] = {}
        try:
            data[ifn]['ipv4'] = inet['addr']
        except:
            pass
        try:
            data[ifn]['broadcast'] = inet['broadcast']
        except:
            pass
        try:
            data[ifn]['netmask'] = inet['netmask']
        except:
            pass
        try:
            data[ifn]['hwaddr'] = link['addr']
        except:
            pass
        try:
            cidr = netaddr.IPNetwork('{0}/{1}'.format(inet['addr'], inet['netmask']))
            data[ifn]['network'] = str(cidr.network)
        except:
            pass
    return { 'interfaces': data }

if __name__ == "__main__":
    print network_info()
