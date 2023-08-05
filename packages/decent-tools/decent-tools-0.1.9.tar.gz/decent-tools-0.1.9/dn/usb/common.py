"""Helper module for kernel driver attaching."""
import os
import time
import logging

WAIT_TIMEOUT = 5


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
