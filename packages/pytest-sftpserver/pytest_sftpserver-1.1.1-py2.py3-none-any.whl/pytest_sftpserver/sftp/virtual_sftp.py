# encoding: utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
import calendar
from datetime import datetime
import os
from logging import getLogger
import stat

from twisted.conch.avatar import ConchUser
from twisted.conch.interfaces import ISFTPServer, ISFTPFile
from twisted.conch.ssh.filetransfer import FileTransferServer
from twisted.conch.ssh.session import SSHSession
from twisted.cred.portal import IRealm
from zope import interface


log = getLogger(__name__)


class VirtualSFTPServer(object):
    avatar = None

    interface.implements(ISFTPServer)

    def __init__(self, avatar):
        self.avatar = avatar
        # log.debug("%r", self)

    # def __repr__(self):
    #     return u"<{s.__class__}(avatar={s.avatar})>".format(s=self)

    def _absPath(self, path):
        return os.path.abspath(os.path.join("/", path))

    def _getAttrs(self, path=None, content=None):
        if path:
            content = self.avatar.content_provider.get(path)

        mtime = calendar.timegm(datetime.now().timetuple())
        return {
            "size": len(str(content)),
            "uid": 1,
            "gid": 1,
            "permissions": (
                stat.S_IRWXO |
                stat.S_IRWXG |
                stat.S_IRWXU |
                (stat.S_IFREG if isinstance(content, (basestring, int, long)) else stat.S_IFDIR)
            ),
            "atime": mtime,
            "mtime": mtime
        }

    def gotVersion(self, otherVersion, extData):
        return {}

    def openFile(self, filename, _1=None, _2=None):
        return VirtualSFTPFile(self, self._absPath(filename))

    def removeFile(self, filename):
        filename = self._absPath(filename)
        return self.avatar.content_provider.remove(filename)

    def renameFile(self, oldpath, newpath, copy=False):
        oldpath = self._absPath(oldpath)
        newpath = self._absPath(newpath)
        content = self.avatar.content_provider.get(oldpath)
        if not content:
            return False
        res = self.avatar.content_provider.put(newpath, content)
        if res:
            if not copy:
                res = res and self.avatar.content_provider.remove(oldpath)
        return res

    def makeDirectory(self, path, attrs):
        path = self._absPath(path)
        return self.avatar.content_provider.put(path, {})

    def removeDirectory(self, path):
        path = self._absPath(path)
        return self.avatar.content_provider.remove(path)

    def openDirectory(self, path):
        return VirtualSFTPDirectory(self, self._absPath(path))

    def getAttrs(self, path, followLinks):
        return self._getAttrs(path)

    def setAttrs(self, path, attrs):
        return True

    def readLink(self, path):
        raise NotImplementedError

    def makeLink(self, linkPath, targetPath):
        return self.renameFile(linkPath, targetPath, copy=True)

    def realPath(self, path):
        return self._absPath(path)

    def extendedRequest(self, extName, extData):
        raise NotImplementedError


class VirtualSFTPFile(object):
    interface.implements(ISFTPFile)

    def __init__(self, server, filename):
        self.server = server
        self.filename = filename

        if self.content is None:
            # "Create" new "file"
            self.content = ""

    @property
    def content(self):
        return self.server.avatar.content_provider.get(self.filename)

    @content.setter
    def content(self, value):
        self.server.avatar.content_provider.put(self.filename, value)

    def close(self):
        return True

    def readChunk(self, offset, length):
        return self.content[offset:offset + length]

    def writeChunk(self, offset, data):
        if offset == 0:
            return self.server.avatar.content_provider.put(self.filename, data)
        else:
            if isinstance(self.content, basestring):
                self.content[offset:] = data
                return True
            return False

    def getAttrs(self):
        return self.server._getAttrs(content=self.content)

    def setAttrs(self, attrs):
        raise NotImplementedError


class DirectoryIter(object):
    def __init__(self, vdir):
        self.vdir = vdir
        self.files = vdir.files

    def next(self):
        try:
            f = self.files.pop(0)
        except IndexError:
            raise StopIteration
        else:
            filepath = os.path.join(self.vdir.dir, f)
            content = self.vdir.server.avatar.content_provider.get(filepath)
            is_dir = "-" if isinstance(content, (basestring, int, long)) else "d"
            longname = "{0}rwxrwxrwx{1:>5d} {2:<9d}{3:<9d}{4:>8d} {5:%b %d %H:%M} {6}".format(
                is_dir,  # Dir or file
                1,       # links
                1,       # uid
                1,       # gid
                len(str(content)),
                datetime.now(),
                f
            )
            attrs = self.vdir.server._getAttrs(content=content)
            return f, longname, attrs


class VirtualSFTPDirectory:
    def __init__(self, server, directory):
        self.server = server
        self.dir = directory

    @property
    def files(self):
        if not self.dir:
            return []
        return self.server.avatar.content_provider.list(self.dir)

    def __iter__(self):
        return DirectoryIter(self)

    def close(self):
        self.dir = ""


class VirtualSFTPUser(ConchUser):
    content_provider = None

    def __init__(self, content_provider):
        ConchUser.__init__(self)
        self.channelLookup['session'] = SSHSession
        self.subsystemLookup['sftp'] = FileTransferServer
        self.content_provider = content_provider


class VirtualSFTPRealm(object):
    interface.implements(IRealm)

    def __init__(self, content_provider):
        self.content_provider = content_provider

    def requestAvatar(self, username, mind, *interfaces):
        return interfaces[0], VirtualSFTPUser(self.content_provider), lambda: None
