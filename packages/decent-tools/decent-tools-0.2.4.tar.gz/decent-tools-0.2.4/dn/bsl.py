#!/usr/bin/env python
"""decentnode bsl programmer."""

import logging
import time
import sys
import argparse
import functools

from pyftdi import serialext
import msp430
import msp430.bsl.target as bsl
from msp430 import memory

MSP430_UART_MODE = 0x30
MSP430_BSL_MODE = 0x31
TC65I_MODE = 0x32


class DnBsl(bsl.SerialBSLTarget, object):
    """Class providing direct access to the BSL of decentnode."""
    def __init__(self):
        """initialize the object."""
        self.download_data = None
        self.options = None
        self.total = 0
        self.current = 0
        self.main_erase_cycles = None
        super(DnBsl, self).__init__()

    def sync(self):
        """\
        Send the sync character and wait for an acknowledge.
        The sync procedure is retried if it fails once or twice.
        """
        self.logger.debug('Sync...')
        if self.blindWrite:
            self.serial.write(msp430.bsl.bsl.BSL_SYNC)
            time.sleep(0.030)
        else:
            for tries in '210':
                self.serial.flushInput()
                self.serial.flushOutput() # fixes DATA_NAK error
                self.serial.write(msp430.bsl.bsl.BSL_SYNC)
                ack = self.serial.read(1)
                if ack == msp430.bsl.bsl.DATA_ACK:
                    self.logger.debug('Sync OK')
                    return
                else:
                    if tries != '0':
                        self.logger.debug('Sync failed, retry...')
                    # if something was received, ensure that a small delay is made
                    if ack:
                        time.sleep(0.2)
            self.logger.error('Sync failed, aborting...')
            raise msp430.bsl.bsl.BSLTimeout('could not sync')

    def reset(self):
        """Reset the device."""
        logging.info('Resetting device')

        self.set_RST(True)
        self.set_TEST(True)
        time.sleep(0.25)

        self.set_RST(False)
        self.set_RST(True)

        time.sleep(0.25)
        self.serial.flushInput()

    def add_dn_options(self, args):
        """add decentnode specific options."""
        self.options, _ = self.parser.parse_args([])
        self.options.invert_test = True
        self.options.invert_reset = True
        self.options.input_format = 'ihex'
        self.options.speed = 38400
        self.options.port = args.port

    def add_program(self, args):
        """add program command."""
        self.add_dn_options(args)
        if not args.no_erase:
            self.options.do_mass_erase = True
            self.add_action(self.mass_erase)

        self.options.do_program = True
        self.add_action(self.program_file)

        self.download_data = memory.Memory()
        data = memory.load(args.firmware, format=self.options.input_format)
        self.download_data.merge(data)
        self.add_action(self.reset)

        segs = [
            len(seg) + 1 if len(seg) & 1 else len(seg)
            for seg in self.download_data]
        self.total = sum(segs)
        self.current = 0

    def add_reset(self, args):
        """add reset command."""
        self.add_dn_options(args)
        self.options.do_reset = True
        self.add_action(self.reset)

    def open_connection(self):
        """FIXME: remove this override ASAP. Find better way."""
        self.logger = logging.getLogger('BSL')
        # already opened
        self.control_delay = self.options.control_delay

        if self.options.extra_erase_cycles is not None:
            self.main_erase_cycles += self.options.extra_erase_cycles

        if self.options.test_on_tx:
            self.testOnTX = True

        if self.options.invert_test:
            self.invertTEST = True

        if self.options.invert_reset:
            self.invertRST = True

        if self.options.swap_reset_test:
            self.swapResetTest = True

        self.set_TEST(True)
        self.set_RST(True)

        if self.options.do_reset:
            return

        if self.options.start_pattern:
            self.start_bsl(self.options.prompt_before_release)

        if self.options.do_mass_erase:
            self.extra_timeout = 6
            self.mass_erase()
            self.extra_timeout = None
            self.BSL_TXPWORD('\xff'*32)
            # remove mass_erase from action list so that it is not done
            # twice
            self.remove_action(self.mass_erase)
        else:
            if self.options.password is not None:
                password = msp430.memory.load(self.options.password
                                              ).get_range(0xffe0,0xffff)
                self.logger.info("Transmitting password: %s",
                                 password.encode('hex'))
                self.BSL_TXPWORD(password)

        # check for extended features (e.g. >64kB support)
        self.logger.debug('Checking if device has extended features')

        if not self.options.do_mass_erase:
            self.BSL_TXPWORD('\xff'*32)

        self.check_extended()

        if self.options.replace_bsl:
            family = msp430.target.identify_device(self.device_id,
                                                   self.bsl_version)
            if family == msp430.target.F1x:
                bsl_name = 'BL_150S_14x.txt'
            elif family == msp430.target.F4x:
                bsl_name = 'BL_150S_44x.txt'
            else:
                raise bsl.BSLError('No replacement BSL for %s' % (family,))

            self.logger.info('Download replacement BSL as requested by --replace-bsl')
            replacement_bsl_txt = pkgutil.get_data('msp430.bsl', bsl_name)
            replacement_bsl = msp430.memory.load('BSL', StringIO(replacement_bsl_txt), format='titext')
            self.program_file(replacement_bsl)

            bsl_start_address = struct.unpack("<H", replacement_bsl.get(0x0220, 2))[0]
            self.execute(bsl_start_address)
            self.logger.info("Starting new BSL at 0x%04x" % (bsl_start_address,))
            time.sleep(0.050)   # give BSL some time to initialize
            #~ if self.options.password is not None:
                #~ self.BSL_TXPWORD(password)
        else:
            if self.bsl_version <= 0x0110:
                self.logger.info('Buggy BSL, applying patch')
                patch_txt = pkgutil.get_data('msp430.bsl', 'patch.txt')
                patch = msp430.memory.load('PATCH', StringIO(patch_txt), format='titext')
                self.program_file(patch)
                self.patch_in_use = True

        if self.options.speed is not None:
            try:
                self.set_baudrate(self.options.speed)
            except bsl.BSLError:
                raise bsl.BSLError("--speed option not supported by BSL on target")

    def memory_write(self, address, data):
        """write to flash memory."""
        if len(data) & 1:  # padding
            data += '\xff'
        while data:
            block, data = data[:self.MAXSIZE], data[self.MAXSIZE:]
            if self.extended_address_mode:
                self.BSL_SETMEMOFFSET(address >> 16)
            self.BSL_TXBLK(address & 0xffff, bytes(block))
            address += len(block)
            self.current += len(block)
            if self.verbose:
                sys.stderr.write("\r Transferred {} of {} bytes ".format(
                    self.current, self.total))


def main():
    """run from command line."""
    dnbsl = DnBsl()

    parser = argparse.ArgumentParser()
    parser.add_argument('-nc', '--no-cbus', action='store_true',
                        help='do not change cbus pins')
    dbg_grp = parser.add_mutually_exclusive_group()
    dbg_grp.add_argument('-d', '--debug', action='store_true',
                         help='print debugging information')
    dbg_grp.add_argument('-v', '--verbose', action='store_true',
                         help='try to be a bit more verbose')

    subs = parser.add_subparsers(title='commands')

    reset_p = subs.add_parser('reset', help='Reset mote')
    reset_p.set_defaults(func=dnbsl.add_reset)

    program_p = subs.add_parser('program', help='Interactive shell')
    program_p.add_argument('-f', '--firmware', metavar='PATH',
                           help='binary firmware to transfer',
                           required=True)
    program_p.add_argument('-ne', '--no-erase', action='store_true',
                           help='do not send mass erase command before'
                           ' programming')
    program_p.set_defaults(func=dnbsl.add_program)
    parser.add_argument('port', metavar='PATH',
                        help='serial port to connect')
    args = parser.parse_args()

    root_logger = logging.getLogger('')
    handler = logging.StreamHandler()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.ERROR)
    dnbsl.verbose = 0

    if args.verbose:
        dnbsl.verbose = 1
        root_logger.setLevel(logging.INFO)

    if args.debug:
        dnbsl.verbose = 3
        root_logger.setLevel(logging.DEBUG)
        fmt = '[%(filename)s:%(lineno)d] %(message)s'
        handler.setFormatter(logging.Formatter(fmt))

    dnbsl.create_option_parser()
    dnbsl.add_extra_options()
    args.func(args)
    dnbsl.open(dnbsl.options.port,
               ignore_answer=dnbsl.options.ignore_answer)

    # Monkey patching serialext.read to prevent returning partial data
    def monkey_read(self, size=1):
        """This version waits the timeout even there is partial data read."""
        data = ''
        start = time.time()
        while size > 0:
            buf = self.udev.read_data(size)
            data += buf
            size -= len(buf)
            if self._timeout > 0:
                if time.time() - start > self._timeout:
                    break
            time.sleep(0.01)
        return data
    dnbsl.serial.read = functools.partial(monkey_read, dnbsl.serial)
    ftdi_dev = dnbsl.serial.udev
    try:
        if not args.no_cbus:
            ftdi_dev.set_bitmode(MSP430_BSL_MODE,
                                 ftdi_dev.BITMODE_CBUS)
        dnbsl.do_the_work()
        if not args.no_cbus:
            ftdi_dev.set_bitmode(MSP430_UART_MODE,
                                 ftdi_dev.BITMODE_CBUS)
    finally:
        dnbsl.close()
        try:
            ftdi_dev.usb_dev.attach_kernel_driver(0)
        except NotImplementedError:
            dnbsl.logger.info('Kernel driver attaching not implemented')


if __name__ == '__main__':
    main()
