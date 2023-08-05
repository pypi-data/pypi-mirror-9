#!/usr/bin/env python
"""
Sets FTDI CBUS bits using the bit-banging mode.

CBUS is used to select active target connected
FTDI serial interface. Following modes are defined:
    MSP430_UART_MODE    = 0x30
    MSP430_BSL_MODE     = 0x31
    TC65I_MODE          = 0x32
"""

import argparse
import ftdi
import re
import logging
import contextlib

from dn import usb

logger = logging.getLogger(__name__)

MSP430_UART_MODE = 0x30
MSP430_BSL_MODE = 0x31
TC65I_MODE = 0x32

FTDI_VENDOR = 0x0403
FTDI_PRODUCT = 0x6001


def extract_serial(device):
    """return serial number from device path."""
    match = re.match('^.*tty.usbserial-(.*)$', device)
    if match:
        serial = match.group(1)
        return serial
    logger.warn("Serial number is not recognized %s", device)


@contextlib.contextmanager
def open_ftdi(device):
    """open before and to close after the operation."""
    serial = extract_serial(device)
    usb.detach_kernel_driver(serial)
    try:
        ftdic = ftdi.ftdi_new()
        if not ftdic:
            raise IOError("Cannot allocate ftdi context")
        try:
            if serial is None:
                usb_desc = ftdi.ftdi_usb_open(
                    ftdic, FTDI_VENDOR, FTDI_PRODUCT)
            else:
                usb_desc = ftdi.ftdi_usb_open_desc(
                    ftdic, FTDI_VENDOR, FTDI_PRODUCT,
                    None, serial)
            if usb_desc < 0:
                raise IOError(usb_desc, "Can't open ftdi device")
            try:
                yield ftdic
            finally:
                ftdi.ftdi_usb_close(ftdic)
        finally:
            ftdi.ftdi_free(ftdic)
    finally:
        usb.attach_kernel_driver(device, serial)


def set_cbus_pins(device, mode, ftdic=None):
    """set cbus pins in CBUS mode."""
    with open_ftdi(device) as ftdic:
        ftdi.ftdi_set_bitmode(ftdic, mode, ftdi.BITMODE_CBUS)
        logger.info("ftdi cbus pins changed to: {0:#x}".format(mode))


def get_cbus_pins(device, ftdic=None):
    """read value of cbus pins."""
    with open_ftdi(device) as ftdic:
        pins = ftdi.new_ucharp()
        val = ftdi.ftdi_read_pins(ftdic, pins)
        res = ftdi.ucharp_value(val)
        logger.debug("ftdi cbus pins read: {0:#x}".format(res))


def main():
    """use module functions from command line."""
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    choices = {
        'msp430-uart': MSP430_UART_MODE,
        'msp430-bsl': MSP430_BSL_MODE, 'tc65i': TC65I_MODE}
    group.add_argument(
        '-m', '--mode', metavar='MODE', choices=choices.keys(),
        help='set predefined mode (%s)' % (', '.join(choices.keys())))
    group.add_argument(
        '-s', '--set', metavar='VALUE', help='set raw value in 0xHH format')
    group.add_argument(
        '-r', '--read', action='store_true',
        help='print raw value in 0xHH format')
    parser.add_argument(
        '-p', '--port', metavar='PATH',
        help='serial device path', required=True)
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='verbose output')
    parser.add_argument(
        '-d', '--debug', action='store_true', help='debug output')
    parser.add_argument(
        '-t', '--attach-timeout', metavar='SECONDS',
        help='''timeout until device node appears after attaching kernel
                driver (default is %.1f sec)''' % usb.common.WAIT_TIMEOUT)
    args = parser.parse_args()

    root_logger = logging.getLogger('')
    handler = logging.StreamHandler()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.ERROR)

    if args.verbose:
        root_logger.setLevel(logging.INFO)

    if args.debug:
        root_logger.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(
            '[%(filename)s:%(lineno)d] %(message)s'))

    if args.attach_timeout:
        usb.common.WAIT_TIMEOUT = float(args.attach_timeout)

    if args.mode:
        set_cbus_pins(args.port, choices[args.mode])
    elif args.set:
        set_cbus_pins(args.port, int(args.set, 16))
    elif args.read:
        print get_cbus_pins(args.port)


if __name__ == '__main__':
    main()
