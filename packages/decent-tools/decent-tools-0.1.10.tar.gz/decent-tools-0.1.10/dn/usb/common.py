"""Helper module for kernel driver attaching."""
from __future__ import print_function
import os
import time
import logging
import usb

WAIT_TIMEOUT = 5
FTDI_VENDOR = 0x0403
FTDI_PRODUCT = 0x6001
SERIAL_MAX_LEN = 256


def wait_for_driver(device_path):
    """wait until the device file is present."""
    elapsed = 0
    logging.debug('waiting for driver')
    while True:
        if os.path.exists(device_path):
            try:
                tryee = os.open(device_path, os.O_NONBLOCK)
                if tryee > 0:
                    os.close(tryee)
                    return
            except OSError:
                pass
        time.sleep(0.01)
        elapsed = elapsed + 0.01
        if elapsed > WAIT_TIMEOUT:
            raise IOError('Not accessible: ' + str(device_path))


def test_wait_with_manual_plug():
    """immediately plug ftdi once running this function."""
    wait_for_driver('/dev/tty.usbserial-A900gwLV')
    return True


def usb_find_by_serial(serial):
    """return usb device with given serial."""
    devs = usb.core.find(
        find_all=True, idVendor=FTDI_VENDOR, idProduct=FTDI_PRODUCT)
    for dev in devs:
        if usb.util.get_string(dev, SERIAL_MAX_LEN,
                               dev.iSerialNumber) == serial:
            return dev
    raise IOError("No ftdi mote is found")


def print_motes():
    """return usb devices with given serial."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store_true', help='Compact format')
    args = parser.parse_args()
    found = usb.core.find(
        find_all=True, idVendor=FTDI_VENDOR, idProduct=FTDI_PRODUCT)
    serials = [
        usb.util.get_string(dev, SERIAL_MAX_LEN, dev.iSerialNumber)
        for dev in found]
    paths = ['/dev/tty.usbserial-' + s for s in serials]
    if not args.c:
        path_title = 'Expected path'
        serial_title = 'Serial'
        serial_max = max([len(s) for s in serials + [serial_title]])
        path_max = max([len(s) for s in paths + [path_title]])
        print(
            '%s %s' %
            (serial_title.center(serial_max), path_title.center(path_max)))
        print('%s %s' % ('-' * serial_max, '-' * path_max))
    for s, p in zip(serials, paths):
        if args.c:
            print('%s,%s' % (s, p))
        else:
            print('%s %s' % (s.ljust(serial_max), p.ljust(path_max)))
        
