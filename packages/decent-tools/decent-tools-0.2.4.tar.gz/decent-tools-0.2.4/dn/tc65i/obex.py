"""implements basic obex protocol module."""

import array
import struct
import logging
import os
import time
import xml.etree.ElementTree as ET

HEADER_COUNT = 0xC0
HEADER_NAME = 0x01
HEADER_TYPE = 0x42
HEADER_LENGTH = 0xC3
HEADER_TIME = 0x44
HEADER_DESCRIPTION = 0x05
HEADER_TARGET = 0x46
HEADER_HTTP = 0x47
HEADER_BODY = 0x48
HEADER_END_OF_BODY = 0x49
HEADER_WHO = 0x4A
HEADER_CONNECTION_ID = 0xCB
HEADER_APP_PARAMETERS = 0x4C
HEADER_AUTH_CHALLENGE = 0x4D
HEADER_AUTH_RESPONSE = 0x4E
HEADER_CREATOR_ID = 0xCF
HEADER_WAN_UUID = 0x50
HEADER_OBJECT_CLASS = 0x51
HEADER_SESSION_PARAMETERS = 0x52
HEADER_SESSION_SEQUENCE_NUMBER = 0x93

REQUEST_CONNECT = 0x80
REQUEST_DISCONNECT = 0x81
REQUEST_PUT = 0x02
REQUEST_GET = 0x03
REQUEST_SETPATH = 0x85
REQUEST_SETPATH2 = 0x86
REQUEST_SESSION = 0x87
REQUEST_ABORT = 0xFF
REQUEST_FINAL = 0x80

FLAG_SETPATH_CREATE = 0x00
FLAG_SETPATH_NOCREATE = 0x02
FLAG_SETPATH_PARENT_FOLDER = 0x03

RESPONSE_SUCCESS = 0x20
RESPONSE_CONTINUE = 0x10
RESPONSE_CREATED = 0x21
RESPONSE_BADREQUEST = 0x40
RESPONSE_FINAL = 0x80

MAX_PART_LEN = 512

logger = logging.getLogger(__name__)


class ObexException(Exception):
    pass


class Triplet(object):

    """Helper class to store triple object."""

    def __init__(self, tag, len_, value):
        self.tag = tag
        self.len_ = len_
        self.value = value

    @classmethod
    def frombytes(cls, bytes_):
        return cls(bytes_[0], bytes_[1], bytes_[2:])

    def bytes(self):
        return [self.tag, self.len_] + self.value


def bytestoint(bytes_, short=0):
    if len(bytes_) > 0:
        return (bytes_[-1] << short) + bytestoint(bytes_[:-1], short+8)
    return 0


def shorttobytes(shrt):
    return strtobytes(struct.pack('!H', shrt))  # unsigned short 2 bytes


def longtobytes(lng):
    return strtobytes(struct.pack('!L', lng))  # unsigned int 4 bytes


def bytestostr(bytes_):
    return array.array('B', bytes_).tostring()


def strtobytes(str_):
    return array.array('B', str_).tolist()


def buildrequest(opcode, data):
    return [opcode] + shorttobytes(3 + len(data)) + data


def buildheader(type_, data):
    return [type_] + shorttobytes(3 + len(data)) + data


def isvalid_responsecode(code):
    return (
        code & RESPONSE_SUCCESS or
        code & RESPONSE_CREATED or
        code & RESPONSE_CONTINUE)


def parsenullstrfunc(data):
    return (
        3 + bytestoint(data[1:3]),
        bytestostr(data[3:3+bytestoint(data[1:3])]))


def parselenfunc(data):
    return (1 + 4, bytestoint(data[1:1+4]))


def getheaderfunc(type_):
    if type_ == HEADER_COUNT or type_ == HEADER_LENGTH:
        return parselenfunc
    return parsenullstrfunc


def getheaderlen(data):
    return getheaderfunc(data[0])(data)[0]


def getheader(data):
    return getheaderfunc(data[0])(data)[1]


def parseheaders(data):
    if len(data) == 0:
        return dict()
    return dict(
        [(data[0], getheader(data))] +
        parseheaders(data[getheaderlen(data):]).items())


def proctriplet(serdev, triplet):
    """send triplet object and return the result."""
    header = buildheader(HEADER_APP_PARAMETERS, triplet.bytes())
    _, hdrs = procrequest(serdev, REQUEST_PUT | REQUEST_FINAL, header)
    res = Triplet.frombytes(hdrs[HEADER_APP_PARAMETERS])
    return bytestoint(strtobytes(res.value))


def writerequest(serdev, request):
    serdev.flushInput()
    serdev.write(bytestostr(request))
    serdev.flush()


def readresponse(serdev, timeout):
    start = time.time()
    code = ''
    while time.time() - start < timeout or timeout is None:
        code = serdev.read(1)
        if len(code) > 0:
            break
        time.sleep(0.001)
    if len(code) == 0:
        raise ObexException(
            'Empty reply, make sure obex mode is configured on the tc65i')
    logger.debug('response header {:#x}'.format(ord(code)))
    len_str = serdev.read(2)
    length = bytestoint(strtobytes(len_str)) - 3  # code and length are 3 bytes
    logger.debug('response length {:#x}'.format(length))
    data = serdev.read(length)
    logger.debug('response: {}'.format([hex(ord(x)) for x in data]))
    return ord(code), length, strtobytes(data)


def connect(serdev):
    """send connect request."""
    fsuid = [
        0x6b, 0x01, 0xcb, 0x31, 0x41, 0x06, 0x11, 0xd4,
        0x9a, 0x77, 0x00, 0x50, 0xda, 0x3f, 0x47, 0x1f]
    header = buildheader(HEADER_TARGET, fsuid)
    info = [0x13, 0x00] + shorttobytes(0xffff)  # version, flags, max packet length
    procrequest(serdev, REQUEST_CONNECT, info + header)


def disconnect(serdev):
    """send disconnect request."""
    procrequest(serdev, REQUEST_DISCONNECT, shorttobytes(3))


def procrequest(serdev, opcode, data, timeout=10):
    """process a request with opcode and data."""
    request = buildrequest(opcode, data)
    logger.debug('sending {} bytes: {}'.format(
        len(request), [hex(x) for x in request]))

    writerequest(serdev, request)
    code, length, data = readresponse(serdev, timeout=timeout)
    logger.debug("{:#x} len={}: {}".format(code, length, data))

    if not isvalid_responsecode(code):
        raise ObexException('Unknown response code {:#x}'.format(code))
    if code & RESPONSE_BADREQUEST:
        raise ValueError(
            'Bad request received opcode: {:#x} data: {!s}'.format(
                opcode, data))

    headers = parseheaders(data)

    return code, headers


def procbodyrequest(serdev, opcode, data, timeout=10):
    """process body type request with opcode and data."""
    def reqiterator():
        """send and receive responses until RESPONSE_FINAL received."""
        code, headers = procrequest(serdev, opcode, data, timeout=timeout)
        yield headers
        while code & RESPONSE_CONTINUE:
            code, headers = procrequest(
                serdev, REQUEST_GET | REQUEST_FINAL,
                shorttobytes(3), timeout=timeout)
            yield headers

    body = ''
    for headers in reqiterator():
        try:
            body += headers[HEADER_BODY]
        except KeyError:
            logger.info(
                'Body header not found for request 0x%x,'
                ' possibly the last request' % opcode)

    return body


def getfile(serdev, path):
    """retrieve file from the modem."""
    parson = path.split('/', 1)
    if len(parson) > 1:  # go further inside
        changedir(serdev, parson[0])
        res = getfile(serdev, parson[1])
        changedir(serdev, '..')
    elif len(parson) == 1:  # time to get it
        destname = parson[0]
        namehdr = buildheader(
            HEADER_NAME, strtobytes(destname.encode('utf-16be')))
        logger.debug('namehdr: {}'.format([hex(x) for x in namehdr]))
        res = procbodyrequest(serdev, REQUEST_GET | REQUEST_FINAL, namehdr)
    return res


def putfile(serdev, path, file_):
    parson = path.split('/', 1)
    if len(parson) > 1:  # # go further inside
        changedir(serdev, parson[0])
        putfile(serdev, parson[1], file_)
        changedir(serdev, '..')
    elif len(parson) == 1:  # time to put it
        destname = parson[0]
        stat = os.fstat(file_.fileno())
        logger.info('Putting file({} bytes) {} with chunk size of {}'.format(
            stat.st_size, destname, MAX_PART_LEN))
        first = True
        for chunk in iter(lambda: file_.read(MAX_PART_LEN), ''):
            logger.debug('Putting file chunk')
            last = len(chunk) < MAX_PART_LEN
            headers = []
            logger.debug('chunk first:{} last:{}'.format(first, last))
            if first:
                first = False
                namehdr = buildheader(HEADER_NAME, strtobytes(
                    destname.encode('utf-16be')))
                logger.debug('namehdr: {}'.format([hex(x) for x in namehdr]))
                headers.extend(namehdr)
                lenhdr = [HEADER_LENGTH] + longtobytes(stat.st_size)
                logger.debug('lenhdr: {}'.format([hex(x) for x in lenhdr]))
                headers.extend(lenhdr)
                timehdr = buildheader(HEADER_TIME, strtobytes(time.strftime(
                    '%Y%m%dT%H%M%S', time.localtime(stat.st_mtime))))
                logger.debug('timehdr: {}'.format([hex(x) for x in timehdr]))
                headers.extend(timehdr)
            type_ = HEADER_END_OF_BODY if last else HEADER_BODY
            bodyhdr = buildheader(type_, strtobytes(chunk))
            logger.debug('bodyhdr: {}'.format([hex(x) for x in bodyhdr]))
            headers.extend(bodyhdr)
            req = (REQUEST_PUT | REQUEST_FINAL) if last else REQUEST_PUT
            procrequest(serdev, req, headers)


def listdir(serdev):
    """list directory content."""
    header = buildheader(HEADER_TYPE, strtobytes('x-obex/folder-listing'))
    xmlstr = procbodyrequest(serdev, REQUEST_GET | REQUEST_FINAL, header)
    files = ET.fromstring(xmlstr)
    return files


def removeobject(serdev, path):
    """delete file or folder by given path."""
    parson = path.split('/', 1)

    if len(parson) > 1:  # go further inside
        changedir(serdev, parson[0])
        removeobject(serdev, parson[1])  # remove whatever it is
        changedir(serdev, '..')
    elif len(parson) == 1:  # time to remove it
        obj = parson[0]
        folders = listdir(serdev).findall('folder')
        found = [k for k in folders if k.attrib['name'] == obj]
        isfolder = len(found) > 0
        if isfolder:  # then remove kids first
            changedir(serdev, obj)
            for k in listdir(serdev):
                removeobject(serdev, k.attrib['name'])  # remove whatever it is
            changedir(serdev, '..')
        logger.info('Removing object ' + obj)
        namehdr = buildheader(
            HEADER_NAME, strtobytes(parson[0].encode('utf-16be')))
        logger.debug('namehdr: {}'.format([hex(x) for x in namehdr]))
        procrequest(serdev, REQUEST_PUT | REQUEST_FINAL, namehdr)


def makedir(serdev, path):
    """make directory on given path."""
    parson = path.split('/', 1)
    if len(parson) > 0:  # go further inside
        changedir(serdev, parson[0], create=True)
        if len(parson) > 1:
            makedir(serdev, parson[1])
        changedir(serdev, '..')


def changedir(serdev, dir_, create=False):
    if dir_ is None or dir_ == '':
        logger.info('Ignoring invalid directory name \'{}\''.format(dir_))
        return
    elif dir_ == '/' or dir_.lower() == 'a:' or dir_.lower() == 'a:/':
        dir_ = ''

    if dir_ == '..':
        flag = FLAG_SETPATH_PARENT_FOLDER
        header = []
    else:
        flag = FLAG_SETPATH_CREATE if create else FLAG_SETPATH_NOCREATE
        header = buildheader(HEADER_NAME, strtobytes(dir_.encode('utf-16be')))

    logger.info('Changing to {}'.format(dir_))
    procrequest(serdev, REQUEST_SETPATH, [flag, 0x00] + header)


def erasestorage(serdev):
    """format modem storage."""
    erasehdr = buildheader(HEADER_APP_PARAMETERS, [0x31, 0x00])
    logger.debug('erasehdr: {}'.format([hex(x) for x in erasehdr]))
    procrequest(serdev, REQUEST_PUT | REQUEST_FINAL, erasehdr, timeout=100)


def abort(serdev):
    """stop running application on the modem."""
    procrequest(serdev, REQUEST_ABORT | REQUEST_FINAL, [])
