"""
The server.
Handle requests, deliver them to the storage and then return the status.

Python 2/3 compatibility:
    pysftpserver natively speaks bytes.
    So make sure to correctly handle them, specifically in Python 3.
    In addiction, please note that arguments passed to the storage are in bytes too.
"""

import os
import sys
import select
import struct
import errno

from pysftpserver.pysftpexceptions import SFTPException, SFTPForbidden, SFTPNotFound

SSH2_FX_OK = 0
SSH2_FX_EOF = 1
SSH2_FX_NO_SUCH_FILE = 2
SSH2_FX_PERMISSION_DENIED = 3
SSH2_FX_FAILURE = 4
SSH2_FX_OP_UNSUPPORTED = 8

SSH2_FXP_INIT = 1
SSH2_FXP_OPEN = 3
SSH2_FXP_CLOSE = 4
SSH2_FXP_READ = 5
SSH2_FXP_WRITE = 6
SSH2_FXP_LSTAT = 7
SSH2_FXP_FSTAT = 8
SSH2_FXP_SETSTAT = 9
SSH2_FXP_FSETSTAT = 10
SSH2_FXP_OPENDIR = 11
SSH2_FXP_READDIR = 12
SSH2_FXP_REMOVE = 13
SSH2_FXP_MKDIR = 14
SSH2_FXP_RMDIR = 15
SSH2_FXP_REALPATH = 16
SSH2_FXP_STAT = 17
SSH2_FXP_RENAME = 18
SSH2_FXP_READLINK = 19
SSH2_FXP_SYMLINK = 20

SSH2_FXP_VERSION = 2
SSH2_FXP_STATUS = 101
SSH2_FXP_HANDLE = 102
SSH2_FXP_DATA = 103
SSH2_FXP_NAME = 104
SSH2_FXP_ATTRS = 105

SSH2_FXP_EXTENDED = 200

SSH2_FILEXFER_VERSION = 3

SSH2_FXF_READ = 0x00000001
SSH2_FXF_WRITE = 0x00000002
SSH2_FXF_APPEND = 0x00000004
SSH2_FXF_CREAT = 0x00000008
SSH2_FXF_TRUNC = 0x00000010
SSH2_FXF_EXCL = 0x00000020

SSH2_FILEXFER_ATTR_SIZE = 0x00000001
SSH2_FILEXFER_ATTR_UIDGID = 0x00000002
SSH2_FILEXFER_ATTR_PERMISSIONS = 0x00000004
SSH2_FILEXFER_ATTR_ACMODTIME = 0x00000008
SSH2_FILEXFER_ATTR_EXTENDED = 0x80000000


class SFTPServer(object):

    def __init__(self, storage, logfile=None, fd_in=0, fd_out=1, raise_on_error=False):
        self.input_queue = b''
        self.output_queue = b''
        self.payload = b''
        self.fd_in = fd_in
        self.fd_out = fd_out
        self.buffer_size = 8192
        self.storage = storage
        self.handles = dict()
        self.dirs = dict()  # keep the path of opened dirs to reconstruct it later
        self.handle_cnt = 0
        self.raise_on_error = raise_on_error
        self.logfile = None
        if logfile:
            self.logfile = open(logfile, 'a')
            sys.stderr = self.logfile

    def new_handle(self, filename, flags=0, attrs=dict(), is_opendir=False):
        if is_opendir:
            handle = self.storage.opendir(filename)
        else:
            os_flags = 0x00000000
            if flags & SSH2_FXF_READ and flags & SSH2_FXF_WRITE:
                os_flags |= os.O_RDWR
            elif flags & SSH2_FXF_READ:
                os_flags |= os.O_RDONLY
            elif flags & SSH2_FXF_WRITE:
                os_flags |= os.O_WRONLY
            if flags & SSH2_FXF_APPEND:
                os_flags |= os.O_APPEND
            if flags & SSH2_FXF_CREAT:
                os_flags |= os.O_CREAT
            if flags & SSH2_FXF_TRUNC and flags & SSH2_FXF_CREAT:
                os_flags |= os.O_TRUNC
            if flags & SSH2_FXF_EXCL and flags & SSH2_FXF_CREAT:
                os_flags |= os.O_EXCL
            mode = attrs.get(b'perm', 0o666)
            handle = self.storage.open(filename, os_flags, mode)

        if self.handle_cnt == 0xffffffffffffffff:
            raise OverflowError()
        self.handle_cnt += 1
        handle_id = bytes(self.handle_cnt)

        self.handles[handle_id] = handle
        if (is_opendir):
            self.dirs[handle_id] = filename

        return handle_id

    def log(self, txt):
        if not self.logfile:
            return
        self.logfile.write(txt + '\n')
        self.logfile.flush()

    def consume_int(self):
        value, = struct.unpack('>I', self.payload[0:4])
        self.payload = self.payload[4:]
        return value

    def consume_int64(self):
        value, = struct.unpack('>Q', self.payload[0:8])
        self.payload = self.payload[8:]
        return value

    def consume_string(self):
        slen = self.consume_int()
        s = self.payload[0:slen]
        self.payload = self.payload[slen:]
        return s

    def consume_handle(self):
        handle_id = self.consume_string()
        return self.handles[handle_id]

    def consume_handle_and_id(self):
        handle_id = self.consume_string()
        return self.handles[handle_id], handle_id

    def consume_attrs(self):
        attrs = {}
        flags = self.consume_int()
        if flags & SSH2_FILEXFER_ATTR_SIZE:
            attrs[b'size'] = self.consume_int64()
        if flags & SSH2_FILEXFER_ATTR_UIDGID:
            attrs[b'uid'] = self.consume_int()
            attrs[b'gid'] = self.consume_int()
        if flags & SSH2_FILEXFER_ATTR_PERMISSIONS:
            attrs[b'perm'] = self.consume_int()
        if flags & SSH2_FILEXFER_ATTR_ACMODTIME:
            attrs[b'atime'] = self.consume_int()
            attrs[b'mtime'] = self.consume_int()
        if flags & SSH2_FILEXFER_ATTR_EXTENDED:
            count = self.consume_int()
            if count:
                attrs[b'extended'] = [
                    {self.consume_string(): self.consume_string()}
                    for i in range(count)
                ]

        return attrs

    def consume_filename(self, default=None):
        filename = self.consume_string()
        if filename == b'.':
            filename = self.storage.home.encode()
        elif len(filename) == 0:
            if default:
                filename = default
            else:
                raise SFTPNotFound()
        if self.storage.verify(filename):
            return filename
        raise SFTPForbidden()

    def encode_attrs(self, attrs):
        flags = SSH2_FILEXFER_ATTR_SIZE | \
            SSH2_FILEXFER_ATTR_UIDGID | \
            SSH2_FILEXFER_ATTR_PERMISSIONS | \
            SSH2_FILEXFER_ATTR_ACMODTIME
        return struct.pack('>IQIIIII', flags,
                           attrs[b'size'],
                           attrs[b'uid'],
                           attrs[b'gid'],
                           attrs[b'perm'],
                           int(attrs[b'atime']),
                           int(attrs[b'mtime']))

    def send_msg(self, msg):
        msg_len = struct.pack('>I', len(msg))
        self.output_queue += msg_len + msg

    def send_status(self, sid, status, exc=None):
        if status != SSH2_FX_OK and self.raise_on_error:
            if exc:
                raise exc
            raise SFTPException()
        self.log("sending status %d" % status)
        msg = struct.pack('>BII', SSH2_FXP_STATUS, sid, status)
        if exc and exc.msg:
            msg += struct.pack('>I', len(exc.msg)) + exc.msg
            msg += struct.pack('>I', 0)
        self.send_msg(msg)

    def send_data(self, sid, buf, size):
        msg = struct.pack('>BII', SSH2_FXP_DATA, sid, size)
        msg += buf
        self.send_msg(msg)

    def run(self):
        while True:
            if self.run_once():
                return

    def run_once(self):
        wait_write = []
        if len(self.output_queue) > 0:
            wait_write = [self.fd_out]
        rlist, wlist, xlist = select.select([self.fd_in], wait_write, [])
        if self.fd_in in rlist:
            buf = os.read(self.fd_in, self.buffer_size)
            if len(buf) <= 0:
                return True
            self.input_queue += buf
            self.process()
        if self.fd_out in wlist:
            rlen = os.write(self.fd_out, self.output_queue)
            if rlen <= 0:
                return True
            self.output_queue = self.output_queue[rlen:]

    def process(self):
        while True:
            if len(self.input_queue) < 5:
                return
            msg_len, msg_type = struct.unpack('>IB', self.input_queue[0:5])
            if len(self.input_queue) < msg_len + 4:
                return
            self.payload = self.input_queue[5:4 + msg_len]
            self.input_queue = self.input_queue[msg_len + 4:]
            if msg_type == SSH2_FXP_INIT:
                msg = struct.pack(
                    '>BI', SSH2_FXP_VERSION, SSH2_FILEXFER_VERSION)
                self.send_msg(msg)
            else:
                msg_id = self.consume_int()
                if msg_type in list(self.table.keys()):
                    try:
                        self.table[msg_type](self, msg_id)
                    except SFTPForbidden as e:
                        self.send_status(msg_id, SSH2_FX_PERMISSION_DENIED, e)
                    except SFTPNotFound as e:
                        self.send_status(msg_id, SSH2_FX_NO_SUCH_FILE, e)
                    except OSError as e:
                        if e.errno == errno.ENOENT:
                            self.send_status(
                                msg_id, SSH2_FX_NO_SUCH_FILE, SFTPNotFound()
                            )
                        else:
                            self.send_status(msg_id, SSH2_FX_FAILURE)
                    except Exception as e:
                        self.send_status(msg_id, SSH2_FX_FAILURE)
                else:
                    self.send_status(msg_id, SSH2_FX_OP_UNSUPPORTED)

    def send_dummy_item(self, sid, item, filename):
        # In case of readlink responses
        # There's no need to add the attrs,
        # But longname is still needed
        # item is the linked and filename is the link
        attrs = self.storage.stat(filename, lstat=True)

        msg = struct.pack('>BII', SSH2_FXP_NAME, sid, 1)
        msg += struct.pack('>I', len(item)) + item  # filename

        if b'longname' in attrs and attrs[b'longname']:  # longname
            longname = attrs[b'longname']
        else:
            longname = item
        msg += struct.pack('>I', len(longname)) + longname

        self.send_msg(msg)

    def send_item(self, sid, item, parent_dir=None):
        if parent_dir:  # in case of readdir response
            attrs = self.storage.stat(item, parent=parent_dir)
        else:
            attrs = self.storage.stat(item)

        msg = struct.pack('>BII', SSH2_FXP_NAME, sid, 1)
        msg += struct.pack('>I', len(item)) + item  # filename

        if b'longname' in attrs and attrs[b'longname']:  # longname
            longname = attrs[b'longname']
        else:
            longname = item
        msg += struct.pack('>I', len(longname)) + longname

        msg += self.encode_attrs(attrs)
        self.send_msg(msg)

    def _realpath(self, sid):
        filename = self.consume_filename(default=b'.')
        self.send_item(sid, filename)

    def _stat(self, sid):
        filename = self.consume_filename()
        attrs = self.storage.stat(filename)
        msg = struct.pack('>BI', SSH2_FXP_ATTRS, sid)
        msg += self.encode_attrs(attrs)
        self.send_msg(msg)

    def _lstat(self, sid):
        filename = self.consume_filename()
        attrs = self.storage.stat(filename, lstat=True)
        msg = struct.pack('>BI', SSH2_FXP_ATTRS, sid)
        msg += self.encode_attrs(attrs)
        self.send_msg(msg)

    def _fstat(self, sid):
        handle_id = self.consume_string()
        handle = self.handles[handle_id]
        attrs = self.storage.stat(handle, fstat=True)
        msg = struct.pack('>BI', SSH2_FXP_ATTRS, sid)
        msg += self.encode_attrs(attrs)
        self.send_msg(msg)

    def _setstat(self, sid):
        filename = self.consume_filename()
        attrs = self.consume_attrs()
        self.storage.setstat(filename, attrs)
        self.send_status(sid, SSH2_FX_OK)

    def _fsetstat(self, sid):
        handle_id = self.consume_string()
        handle = self.handles[handle_id]
        attrs = self.consume_attrs()
        self.storage.setstat(handle, attrs, fsetstat=True)
        self.send_status(sid, SSH2_FX_OK)

    def _opendir(self, sid):
        filename = self.consume_filename()
        handle_id = self.new_handle(filename, is_opendir=True)
        msg = struct.pack('>BII', SSH2_FXP_HANDLE, sid, len(handle_id))
        msg += handle_id
        self.send_msg(msg)

    def _readdir(self, sid):
        handle, handle_id = self.consume_handle_and_id()
        try:
            item = next(handle)
            self.send_item(sid, item, parent_dir=self.dirs[handle_id])
        except StopIteration:
            self.send_status(sid, SSH2_FX_EOF)

    def _close(self, sid):
        # here we need to hold the handle id
        handle_id = self.consume_string()
        handle = self.handles[handle_id]
        self.storage.close(handle)

        del(self.handles[handle_id])
        try:
            del(self.dirs[handle_id])
        except KeyError:
            pass  # it wasn't an opened dir

        self.send_status(sid, SSH2_FX_OK)

    def _open(self, sid):
        filename = self.consume_filename()
        flags = self.consume_int()
        attrs = self.consume_attrs()
        handle_id = self.new_handle(filename, flags, attrs)
        msg = struct.pack('>BII', SSH2_FXP_HANDLE, sid, len(handle_id))
        msg += handle_id
        self.send_msg(msg)

    def _read(self, sid):
        handle = self.consume_handle()
        off = self.consume_int64()
        size = self.consume_int()
        chunk = self.storage.read(handle, off, size)
        if len(chunk) == 0:
            self.send_status(sid, SSH2_FX_EOF)
        elif len(chunk) > 0:
            self.send_data(sid, chunk, len(chunk))
        else:
            self.send_status(sid, SSH2_FX_FAILURE)

    def _write(self, sid):
        handle = self.consume_handle()
        off = self.consume_int64()
        chunk = self.consume_string()
        if self.storage.write(handle, off, chunk):
            self.send_status(sid, SSH2_FX_OK)
        else:
            self.send_status(sid, SSH2_FX_FAILURE)

    def _mkdir(self, sid):
        filename = self.consume_filename()
        attrs = self.consume_attrs()
        self.storage.mkdir(
            filename,
            attrs.get(b'perm', 0o777)
        )
        self.send_status(sid, SSH2_FX_OK)

    def _rmdir(self, sid):
        filename = self.consume_filename()
        self.storage.rmdir(filename)
        self.send_status(sid, SSH2_FX_OK)

    def _rm(self, sid):
        filename = self.consume_filename()
        self.storage.rm(filename)
        self.send_status(sid, SSH2_FX_OK)

    def _rename(self, sid):
        oldpath = self.consume_filename()
        newpath = self.consume_filename()
        self.storage.rename(oldpath, newpath)
        self.send_status(sid, SSH2_FX_OK)

    def _symlink(self, sid):
        linkpath = self.consume_filename()
        targetpath = self.consume_filename()
        self.storage.symlink(linkpath, targetpath)
        self.send_status(sid, SSH2_FX_OK)

    def _readlink(self, sid):
        filename = self.consume_filename()
        link = self.storage.readlink(filename)
        self.send_dummy_item(sid, link, filename)

    table = {
        SSH2_FXP_REALPATH: _realpath,
        SSH2_FXP_LSTAT: _lstat,
        SSH2_FXP_FSTAT: _fstat,
        SSH2_FXP_STAT: _stat,
        SSH2_FXP_OPENDIR: _opendir,
        SSH2_FXP_READDIR: _readdir,
        SSH2_FXP_CLOSE: _close,
        SSH2_FXP_OPEN: _open,
        SSH2_FXP_READ: _read,
        SSH2_FXP_WRITE: _write,
        SSH2_FXP_MKDIR: _mkdir,
        SSH2_FXP_RMDIR: _rmdir,
        SSH2_FXP_REMOVE: _rm,
        SSH2_FXP_SETSTAT: _setstat,
        SSH2_FXP_FSETSTAT: _fsetstat,
        SSH2_FXP_RENAME: _rename,
        SSH2_FXP_SYMLINK: _symlink,
        SSH2_FXP_READLINK: _readlink
    }
