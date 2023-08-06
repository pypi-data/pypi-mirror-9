#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import isfile
from subprocess import call, PIPE, CalledProcessError, check_output

def _cmd_exists(cmd):
    return call("type " + cmd, shell=True,
        stdout=PIPE, stderr=PIPE) == 0

def _get_dmi_info(name, fname):
    val = ''
    try:
        if _cmd_exists('sudo') and _cmd_exists('dmidecode'):
            val = check_output(['sudo', 'dmidecode', '-s', 'system-serial-number'])
        else:
            raise Exception('Missing binary')
    except:
        if isfile(fname):
            f = open(fname, 'r')
            val = f.readline()
            f.close
    return val.strip()

def dmidecode_info():
    data = {}
    data['serial_number'] = _get_dmi_info('system-serial-number', '/sys/devices/virtual/dmi/id/product_serial')
    data['manufacturer'] = _get_dmi_info('system-manufacturer', '/sys/devices/virtual/dmi/id/chassis_vendor')
    data['product_version'] = _get_dmi_info('product_version', '/sys/devices/virtual/dmi/id/product_version')
    data['product'] = _get_dmi_info('system-product-name', '/sys/devices/virtual/dmi/id/product_name')
    data['bios_date'] = _get_dmi_info('bios-release-date', '/sys/devices/virtual/dmi/id/bios_date')
    data['bios_vendor'] = _get_dmi_info('bios-vendor', '/sys/devices/virtual/dmi/id/bios_vendor')
    data['bios_version'] = _get_dmi_info('bios-version', '/sys/devices/virtual/dmi/id/bios_version')
    return data

if __name__ == "__main__":
    print dmidecode_info()
