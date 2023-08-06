# encoding: utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from twisted.application import internet
from twisted.conch.ssh.factory import SSHFactory
from twisted.conch.ssh.keys import Key
from twisted.conch.unix import UnixSFTPDirectory
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernamePassword
from twisted.cred.portal import Portal
from zope.interface import implements


def get_key(path):
    with open(path, "r") as f:
        return Key.fromString(data=f.read())


class DummyChecker(object):
    credentialInterfaces = (IUsernamePassword,)
    implements(ICredentialsChecker)

    def requestAvatarId(self, credentials):
        return credentials.username


def makeService():
    public_key = get_key('id_rsa.pub')
    factory = SSHFactory()
    factory.privateKeys = {'ssh-rsa': get_key('id_rsa')}
    factory.publicKeys = {'ssh-rsa': public_key}
    factory.portal = Portal(UnixSFTPDirectory('.'))
    factory.portal.registerChecker(DummyChecker())

    return internet.TCPServer(2200, factory)


application = service.Application("sftp server")
sftp_server = makeService()
sftp_server.setServiceParent(application)


