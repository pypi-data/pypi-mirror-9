#!/usr/bin/env python
# -*- coding: utf-8 -*-

def mem_info():
    data = {}
    with open('/proc/meminfo') as fp:
        for line in fp:
            cols = line.rstrip('\n').split(':')
            if not len(cols) > 1:
                continue
            if cols[0].strip() == 'MemTotal':
                data['mem_total_kb'] = int(cols[1].split()[0])
                break
    return data

if __name__ == "__main__":
    print mem_info()
