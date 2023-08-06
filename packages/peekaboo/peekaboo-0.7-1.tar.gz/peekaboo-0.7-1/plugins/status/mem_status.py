#!/usr/bin/env python

import psutil

def mem_status():
    data = {}
    data['vmem'] = dict(psutil.virtual_memory()._asdict())
    data['swap'] = dict(psutil.swap_memory()._asdict())
    return data

if __name__ == "__main__":
    print mem_status()
