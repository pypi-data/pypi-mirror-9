#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE

def virtual_info():
    output = Popen(['lspci'], stdout=PIPE).communicate()[0]

    data = { 'is_virtual': False }
    model = output.lower()
    if 'vmware' in model:
       data['virtual'] = 'VMware'
       data['is_virtual'] = True
    elif 'virtualbox' in model:
       data['virtual'] = 'VirtualBox'
       data['is_virtual'] = True
    elif 'qemu' in model:
       data['virtual'] = 'kvm'
       data['is_virtual'] = True
    elif 'virtio' in model:
       data['virtual'] = 'kvm'
       data['is_virtual'] = True
    return data

if __name__ == "__main__":
    print virtual_info()
