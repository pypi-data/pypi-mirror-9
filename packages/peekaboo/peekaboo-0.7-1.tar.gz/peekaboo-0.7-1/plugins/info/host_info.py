#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

def host_info():
    data = {}
    data['hostname'] = socket.gethostname()
    return data

if __name__ == "__main__":
    print host_info()
