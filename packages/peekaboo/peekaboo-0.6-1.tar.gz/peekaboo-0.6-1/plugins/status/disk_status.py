#!/usr/bin/env python

import os
import os.path

check_fs = [ 'ext3', 'ext4', 'xfs' ]

def _disk_usage(path):
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize / 1024
    total = st.f_blocks * st.f_frsize / 1024
    used = (st.f_blocks - st.f_bfree) * st.f_frsize / 1024
    return {'free_kb': free, 'total_kb': total, 'used_kb': used}

def _get_mounts():
    mounts = []
    f = open('/proc/mounts', 'r')
    for line in f.readlines():
        cols = line.rstrip('\n').split(' ', 6)
        if cols[2] in check_fs and os.path.ismount(cols[1]):
            mounts.append(cols[1])
    return mounts

def disk_status():
    data = {'disk': {}}
    for mount in _get_mounts():
        data['disk'][mount] = _disk_usage(mount)
    return data

if __name__ == "__main__":
    print disk_status()
