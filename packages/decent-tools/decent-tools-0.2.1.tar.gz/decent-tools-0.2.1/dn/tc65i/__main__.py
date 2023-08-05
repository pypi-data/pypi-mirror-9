#!/usr/bin/env python

"""tc65i main module used from command line."""

from __future__ import print_function
import argparse
import itertools
import functools
import collections
import re
import logging
import os
import dateutil.parser as dateparser
import sys

import serial

import dn.ftdicbus as cbus
from dn.tc65i import obex, at


logger = logging.getLogger(__name__)

TIMEOUT = 3.0
BAUDRATE = 115200

MAX_CLOSE_TRY = 5


class Tc65i(object):

    """Tc65i modem manager."""

    File = collections.namedtuple(
        'File', 'type permission owner group size modified name')
    File.aligns = '<<<<><<'

    def __init__(self, ser):
        """initialize Tc65i object."""
        self.obex_mode = False
        self.ser = ser

    def __enter__(self):
        """called when with statement is executed."""
        return self

    def __exit__(self, _, value, traceback):
        self.close_obex()

    def open_obex(self):
        """switch into obex data mode."""
        if not self.obex_mode:
            at.send(self.ser, 'AT\\Q3')
            at.send(self.ser, 'AT^SQWE=0')
            at.send(self.ser, 'AT^SQWE=3')
            obex.connect(self.ser)
            self.obex_mode = True
            logger.info('obex mode opened')

    def close_obex(self):
        """switch into at command mode."""
        if self.obex_mode:
            obex.disconnect(self.ser)
            for close_try in xrange(MAX_CLOSE_TRY):
                try:
                    logger.debug(
                        'trying (%d left) to close obex mode' % close_try)
                    at.send(self.ser, '+++', term_char='', timeout=1)
                    break
                except at.ATException:
                    pass
            else:
                raise IOError(
                    'Cannot close obex mode. tc65i does not '
                    'respond to +++ after %d tries' % MAX_CLOSE_TRY)
            at.send(self.ser, 'ATE')
            self.obex_mode = False
            logger.info('obex mode closed')

    def obexer(func):
        def actual(*args, **kwargs):
            """perform obex guarding and call the wrapping function."""
            self = args[0]
            if not self.obex_mode:
                self.open_obex()
            args = (self.ser,) + args[1:]
            return getattr(obex, func.__name__)(*args, **kwargs)
        return functools.wraps(func)(actual)

    def ater(func):
        def actual(*args, **kwargs):
            """perform at guarding and call the wrapping function."""
            self = args[0]
            if self.obex_mode:
                self.close_obex()
            args = (self.ser,) + args[1:]
            return getattr(at, func.__name__)(*args, **kwargs)
        return functools.wraps(func)(actual)

    @ater
    def send(*args, **kwargs):
        pass

    @ater
    def getconfig(*args, **kwargs):
        pass

    @obexer
    def getfile(*args, **kwargs):
        pass

    @obexer
    def putfile(*args, **kwargs):
        pass

    @obexer
    def listdir(*args, **kwargs):
        pass

    @obexer
    def changedir(*args, **kwargs):
        pass

    @obexer
    def removeobject(*args, **kwargs):
        pass

    @obexer
    def erasestorage(*args, **kwargs):
        pass

    @obexer
    def makedir(*args, **kwargs):
        pass

    @obexer
    def proctriplet(*args, **kwargs):
        pass

    @obexer
    def abort(*args, **kwargs):
        pass

    def freespace(self):
        """retrieve the free space."""
        return self.proctriplet(obex.Triplet.frombytes([0x32, 0x01, 0x02]))

    def totalspace(self):
        """retrieve the total space."""
        return self.proctriplet(obex.Triplet.frombytes([0x32, 0x01, 0x01]))

    def lsconfig(self):
        """return formatted configuration lines."""
        res = []
        conf_ptrn = re.compile('("[^\"]*")')
        for line in self.getconfig():
            confstr = conf_ptrn.findall(line)
            if confstr:
                res.append('AT^SCFG={},{}'.format(
                    confstr[0], ','.join(confstr[1:])))
        return '\n'.join(res)

    def lsall(self, parent=''):
        def check_perm(perm, ctx):
            return perm if perm in ctx else '-'

        def ls_perms(ctx):
            """format permission line."""
            return check_perm(
                'R', ctx) + check_perm('W', ctx) + check_perm('D', ctx)

        rootelem = self.listdir()
        if len(rootelem) == 0:
            return []

        files = []
        for child in rootelem:
            uperm = child.attrib.get('user-perm', '')
            gperm = child.attrib.get('group-perm', '')
            operm = child.attrib.get('other-perm', '')
            mod = child.attrib.get('modified', '')
            if mod:
                mod = dateparser.parse(mod)
            perm = ('d' if child.tag == 'folder' else '-') + ls_perms(uperm)
            perm += ls_perms(gperm) + ls_perms(operm)
            name = child.attrib.get('name', '')
            file_ = Tc65i.File(
                child.attrib.get('type', ''),
                perm,
                child.attrib.get('owner', ''),
                child.attrib.get('group', ''),
                child.attrib.get('size', '0'),
                mod,
                parent+'/' + name,
                )
            files.append(file_)
            if file_.permission[0] == 'd' and 'R' in file_.permission:
                self.changedir(dir_=name)
                kids = self.lsall(parent=(file_.name))
                self.changedir("..")
                files += kids
        return files

    @classmethod
    def formatfiles(cls, files):
        """format file information."""
        def max_item_len(items, ind):
            return max([len(str(item[ind])) for item in items])

        titles = [str.capitalize(f) for f in cls.File._fields]

        files_str = [
            tuple([str(v) for v in f._asdict().values()]) for f in files]

        max_lengths = [
            max_item_len([titles] + files_str, i) for i in xrange(len(titles))]

        titlef_str = ' '.join(
            ['{{:^{}}}'] * len(max_lengths)).format(*max_lengths)

        f_str = ' '.join([
            '{{:{}{}}}'] * len(max_lengths)).format(*itertools.chain(*zip(
                cls.File.aligns, max_lengths)))
        file_list = [f_str.format(*f) for f in files_str]
        return '\n'.join([titlef_str.format(*titles)] + file_list)


class Run(argparse.Action):

    """argparse helper."""

    def __init__(self, option_strings, dest, **kwargs):
        super(Run, self).__init__(option_strings, dest, **kwargs)
        self.func = getattr(kwargs, 'func', None)

    def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(namespace, 'actions'):
            namespace.actions = []
        if len(values) == 0:
            pairs = [(self, None)]
        elif isinstance(values, basestring):
            pairs = [(self, values)]
        else:
            pairs = [(self, v) for v in values]
        namespace.actions.extend(pairs)


def cb_print_settings(modem, path, args):
    """print modem settings."""
    print(modem.lsconfig())


def cb_list_dir(modem, path, args):
    """list directory contents."""
    files = modem.lsall()
    print('Available {} of {} bytes'.format(
        modem.freespace(), modem.totalspace()))
    print(modem.formatfiles(files))


def cb_put_file(modem, path, args):
    """put file (to remote --destination directory optionally)."""
    destpath = args.destination + '/' + os.path.basename(path)
    with open(path, 'r') as fp_:
        modem.removeobject(destpath)
        modem.putfile(destpath, fp_)
    logger.info('transferred {} to {}'.format(path, destpath))


def cb_get_file(modem, path, args):
    """get file (to local --destination directory optionally)."""
    destfile = sys.stdout
    if args.destination:
        destfile = open(args.destination, 'w')
    try:
        destfile.write(modem.getfile(path))
    finally:
        if args.destination:
            destfile.close()


def cb_make_dir(modem, path, args):
    """create new directory."""
    logger.info('creating ' + path)
    modem.makedir(path)


def cb_remove(modem, path, args):
    """delete file or directory."""
    logger.info('deleting ' + path)
    modem.removeobject(path)


def cb_format(modem, path, args):
    """erase entire storage."""
    logger.info('formatting ...')
    modem.erasestorage()
    logger.info('formatted')


def cb_run(modem, path, args):
    """run jar on the modem."""
    logger.info('running {} ...'.format(path))
    match = re.match(r'(a\:)?\/*(.*)', path)
    res = modem.send('AT^SJRA="a:/{}"'.format(match.group(2)))
    logger.info('AT result: {}'.format(res))


def cb_abort(modem, path, args):
    """abort running application."""
    logger.info('aborting ...')
    modem.abort()


def cb_atcmd(modem, path, args):
    """execute AT command and print the result."""
    logger.info('running at command {} ...'.format(path))
    res = modem.send(path)
    logger.info(res)


def cb_dump(modem, path, args):
    """dump from modem."""
    try:
        while True:
            sys.stdout.write(modem.ser.read(1))
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass


def main():
    """call module from command line."""
    root_logger = logging.getLogger('')
    handler = logging.StreamHandler()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.ERROR)

    parser = argparse.ArgumentParser()
    act_grp = parser.add_argument_group(
        'available commands (all are recursive)')
    act_grp.add_argument(
        '-ls', '--list-dir', help=cb_list_dir.__doc__,
        action=Run, nargs=0).func = cb_list_dir
    act_grp.add_argument(
        '-pf', '--put-file', metavar='FILE', nargs='+',
        help=cb_put_file.__doc__, action=Run).func = cb_put_file
    act_grp.add_argument(
        '-gf', '--get-file', metavar='PATH', nargs='+',
        help=cb_get_file.__doc__, action=Run).func = cb_get_file
    act_grp.add_argument(
        '-rm', '--remove', metavar='PATH', nargs='+',
        help=cb_remove.__doc__, action=Run).func = cb_remove
    act_grp.add_argument(
        '-md', '--make-dir', metavar='PATH', nargs='+',
        help=cb_make_dir.__doc__, action=Run).func = cb_make_dir
    act_grp.add_argument(
        '-fm', '--format', action=Run, nargs=0,
        help=cb_format.__doc__).func = cb_format
    act_grp.add_argument(
        '-ru', '--run', action=Run, metavar='PATH', nargs=1,
        help=cb_run.__doc__).func = cb_run
    act_grp.add_argument(
        '-ab', '--abort', action=Run, nargs=0,
        help=cb_abort.__doc__).func = cb_abort
    act_grp.add_argument(
        '-at', '--exec-at', action=Run, metavar='COMMAND', nargs='+',
        help=cb_atcmd.__doc__).func = cb_atcmd
    act_grp.add_argument(
        '-ps', '--print-settings', help=cb_print_settings.__doc__,
        action=Run, nargs=0).func = cb_print_settings
    act_grp.add_argument(
        '-du', '--dump', help=cb_dump.__doc__,
        action=Run, nargs=0).func = cb_dump

    dbg_grp = parser.add_mutually_exclusive_group()
    dbg_grp.add_argument(
        '-d', '--debug', action='store_true',
        help='print debugging information')
    dbg_grp.add_argument(
        '-v', '--verbose', action='store_true',
        help='try to be a bit more verbose')

    parser.add_argument(
        '-n', '--no-cbus', action='store_true',
        help='do not change cbus pins')
    parser.add_argument(
        '-D', '--destination', metavar='PATH',
        help='destination directory', default='')
    parser.add_argument(
        'port', metavar='PATH',
        help='serial device to connect')

    args = parser.parse_args()

    if not hasattr(args, 'actions'):
        print('No commands defined')
        parser.print_help()
        return

    if args.verbose:
        root_logger.setLevel(logging.INFO)
    if args.debug:
        handler.setFormatter(logging.Formatter(
            '[%(filename)s:%(lineno)d] %(message)s'))
        root_logger.setLevel(logging.DEBUG)

    if not args.no_cbus:
        cbus.set_cbus_pins(args.port, cbus.TC65I_MODE)
    try:
        with serial.serial_for_url(args.port) as ser:
            ser.timeout = TIMEOUT
            ser.baudrate = BAUDRATE
            with Tc65i(ser) as modem:
                if hasattr(args, 'actions'):
                    for action, param in args.actions:
                        action.func(modem, param, args)
    finally:
        if not args.no_cbus:
            cbus.set_cbus_pins(args.port, cbus.MSP430_UART_MODE)


if __name__ == '__main__':
    main()
