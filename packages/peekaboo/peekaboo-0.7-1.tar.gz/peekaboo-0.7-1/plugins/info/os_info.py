#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE

def lsb_release():
    output = Popen(['lsb_release', '-a'], stdout=PIPE).communicate()[0]
    data = {}
    for line in output.split('\n'):
        col = line.split(':', 2)
        if len(col) < 2:
            continue
        key = col[0].strip()
        val = col[1].strip()
        if key == 'Distributor ID':
            data['os_distro'] = val
        elif key == 'Release':
            data['os_release'] = val
    return data

if __name__ == "__main__":
    print lsb_release()
