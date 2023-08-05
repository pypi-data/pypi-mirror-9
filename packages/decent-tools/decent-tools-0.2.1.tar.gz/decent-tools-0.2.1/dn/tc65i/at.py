"""handle at command transmission and receiving the response."""

import logging

logger = logging.getLogger(__name__)

E_OK = 'OK'
E_ERROR = 'ERROR'
LE = '\r\n'

AT_CONFIG = 'AT^SCFG'
AT_Q = '?'


class ATException(Exception):

    """raised when AT command related exception occurs."""

    pass


def send(serdev, cmd, term_char=LE, timeout=None):
    logger.debug('Sending {} to {}'.format(cmd, serdev.name))
    if timeout:
        old = serdev.timeout
        serdev.timeout = timeout
    try:
        serdev.flushInput()
        serdev.flushOutput()
        serdev.write(cmd + term_char)
        serdev.flush()
        response = []
        while True:
            line = serdev.readline()
            logger.debug('AT reply: {}'.format(line))
            if not line:
                raise ATException(
                    response if response
                    else (
                        'No reply from %s within %.1f sec, make sure tc65i'
                        ' is powered, attached, or not running MIDlet'
                        % (serdev.name, serdev.timeout))
                    )
            elif line == LE:
                continue
            elif line == E_OK + LE:
                success = True
                break
            elif line == E_ERROR + LE:
                success = False
                break
            else:
                response.append(line.strip())
        logger.debug('Result: ({}) {}'.format(success, response))
        return success, response
    finally:
        if timeout:
            serdev.timeout = old


def getconfig(serdev, ret_success=False):
    """read configuration of the modem."""
    res = send(serdev, AT_CONFIG + AT_Q)
    return res if ret_success else res[1]
