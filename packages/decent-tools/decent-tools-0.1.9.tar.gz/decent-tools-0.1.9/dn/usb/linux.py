"""linux implementation of usb kernel driver detachment."""

import logging
import usb
from dn.usb.common import wait_for_driver

FTDI_VENDOR = 0x0403
FTDI_PRODUCT = 0x6001
SERIAL_MAX_LEN = 256
logger = logging.getLogger(__name__)


def usb_find(serial):
    """return usb devices with give serial."""
    found = None
    if serial:
        devs = usb.core.find(
            find_all=True, idVendor=FTDI_VENDOR, idProduct=FTDI_PRODUCT)
        for dev in devs:
            if usb.util.get_string(dev, SERIAL_MAX_LEN,
                                   dev.iSerialNumber) == serial:
                found = dev
    else:
        found = usb.core.find(idVendor=FTDI_VENDOR, idProduct=FTDI_PRODUCT)
    if not found:
        raise IOError("No ftdi mote is found")
    return found


def detach_kernel_driver(serial):
    """detach kernel driver for given serial."""
    dev = usb_find(serial)
    if dev.is_kernel_driver_active(0):
        logger.debug('Detaching kernel driver')
        dev.detach_kernel_driver(0)
    if dev.is_kernel_driver_active(0):
        logger.warning(
            'Kernel driver not properly attached. Proceeding anyways')
    logger.info('Kernel driver detached')


def is_kernel_driver_active(serial):
    """check kernel driver attached for given serial."""
    dev = usb_find(serial)
    return dev.is_kernel_driver_active(0)


def attach_kernel_driver(path, serial):
    """attach kernel driver for given serial."""
    dev = usb_find(serial)
    if not dev.is_kernel_driver_active(0):
        dev.attach_kernel_driver(0)
        wait_for_driver(path)
        logger.info('Kernel driver attached')
