# -*- coding:utf-8; tab-width:4; mode:python -*-


class BBException(Exception):
    def __str__(self):
        msg = Exception.__str__(self)
        if not msg.strip():
            msg = self.message

        return 'bitbucket error:\n  %s: %s' % (
            self.__class__.__name__, msg)


class Forbidden(BBException): pass

class RequestError(BBException): pass

class InvalidOrAlreadyRegisteredSSHkey(BBException): pass
class InvalidCredentials(BBException): pass

class RepositoryAlreadyExists(BBException): pass
class RepositoryNotFound(BBException): pass
class NotLocalCopy(BBException): pass
class ServiceUnavailable(BBException): pass
class UnrelatedContent(BBException): pass

class NoSuchKey(BBException): pass
class NoSuchUser(BBException): pass
class AuthenticationError(BBException): pass


class InvalidFormat(BBException): pass

class OwnerRequired(BBException):
    message = "Must specify an account or repository owner"

class WrongRepoPathFormat(BBException):
    message = "Wrong repository path format. It should match [owner]/repository_name"


class CommandError(BBException):
    pass


#    def __str__(self):
#        ex = self.args[0]
#        cmd = str.join(' ', ex.cmd)
#        return "[%s] %s\n%s\n%s" % (ex.returncode, cmd, ex.output, ex.err)
