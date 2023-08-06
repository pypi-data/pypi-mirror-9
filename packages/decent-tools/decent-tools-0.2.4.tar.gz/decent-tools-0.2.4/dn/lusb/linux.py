"""linux implementation of usb kernel driver detachment."""

import logging
from dn.lusb.common import wait_for_driver, usb_find_by_serial

logger = logging.getLogger(__name__)


def detach_kernel_driver(serial):
    """detach kernel driver for given serial."""
    dev = usb_find_by_serial(serial)
    if dev.is_kernel_driver_active(0):
        logger.debug('Detaching kernel driver')
        dev.detach_kernel_driver(0)
    if dev.is_kernel_driver_active(0):
        logger.warning(
            'Kernel driver not properly attached. Proceeding anyways')
    logger.info('Kernel driver detached')


def is_kernel_driver_active(serial):
    """check kernel driver attached for given serial."""
    dev = usb_find_by_serial(serial)
    return dev.is_kernel_driver_active(0)


def attach_kernel_driver(path, serial):
    """attach kernel driver for given serial."""
    dev = usb_find_by_serial(serial)
    if not dev.is_kernel_driver_active(0):
        dev.attach_kernel_driver(0)
        wait_for_driver(path)
        logger.info('Kernel driver attached')
