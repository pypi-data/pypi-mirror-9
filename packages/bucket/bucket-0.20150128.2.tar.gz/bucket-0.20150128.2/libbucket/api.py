# -*- coding: utf-8; mode: python -*-

import sys
import os.path
import time
import logging
import webbrowser

# print 0
import requests
import json
import hgapi
import gitapi

logging.getLogger("requests").setLevel(logging.WARNING)

import exceptions as exc
from commodity.pattern import Bunch, MetaBunch

# import math
# http://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
# def convertSize(size):
#     size_name = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
#     i = int(math.floor(math.log(size, 1024)))
#     p = math.pow(1024, i)
#     s = round(size / p, 2)
#     if (s > 0):
#         return '%s %s' % (s, size_name[i])
#     else:
#         return '0B'


def convertSize(bytes):
    k = float(bytes) / 1000
    return "{:.0f} KB".format(k)


BB_API1 = 'https://api.bitbucket.org/1.0/{path}'
BB_API2 = 'https://api.bitbucket.org/2.0/{path}'


def bb_api1_uri(path):
    uri = BB_API1.format(path=path)
    return uri


def bb_api2_uri(path):
    uri = BB_API2.format(path=path)
    return uri


def reply2json(req, ok=None, errors=None):

    def raise_error(error):
        e = error[0]
        args = error[1:]
        raise e(*args)

    ok = ok or 200
    errors = errors or {}

    if req.status_code != ok:
        raise_error(errors[req.status_code])

    if not req.content:
        return None

    return json.loads(req.content)


class Account(object):
    def __init__(self, username=None, password=None):
        self.username = username or "anonymous"
        self.password = password

    @classmethod
    def from_args(cls, *args):
        assert len(args) == 2
        return Account(str.join(':', args))

    def is_anonymous(self):
        return self.username == "anonymous"

    def __str__(self):
        pwd = '*' * len(self.password) if self.password else None
        return '"{}:{}"'.format(self.username, pwd)


class Session(object):
    def __init__(self, credentials=None, logger=None, verbose=False):
        self.credentials = credentials
        self.timeout = 10
        self._http_session = None
        self.logger = logger or logging.getLogger('bitbucket')

        self.verbose = verbose

    def auth(self):
        if self.credentials is None or self.credentials.is_anonymous():
            return None

        return (self.credentials.username, self.credentials.password)

    @property
    def http_session(self):
        if self._http_session is not None:
            return self._http_session

        self._http_session = requests.Session()
        self._http_session.auth = self.auth()
        self._http_session.timeout = self.timeout

        if self.logger.level == logging.DEBUG:
            pass
#            self._http_session.config['verbose'] = sys.stderr

        # if self.credentials:
        #     self.test_auth()

        return self._http_session

    def test_auth(self):
        errors = {
            400: [exc.InvalidOrAlreadyRegisteredSSHkey],
            401: [exc.InvalidCredentials, self.credentials]}

        self.http_get(bb_api1_uri('ssh-keys'), errors=errors)

    def request(self, method, path, data=None, ok=None, errors=None):
        logging.debug("request %s %s %s", method, path, data)
        while 1:
            url = path if path.startswith('http') else bb_api2_uri(path)
            try:
                reply = self.http_session.request(method, url, data=data)
                retval = reply2json(reply, ok=ok, errors=errors)
                break

            except exc.ServiceUnavailable:
                time.sleep(1)

            except requests.exceptions.ConnectionError, e:
                self.logger.error(e)
                sys.exit(1)

        return retval

    def http_get(self, path, **kargs):
        return self.request('get', path, **kargs)

    def http_put(self, path, **kargs):
        return self.request('put', path, **kargs)

    def http_post(self, path, **kargs):
        for key, val in kargs['data'].copy().items():
            if val is None:
                del kargs['data'][key]

        return self.request('post', path, **kargs)

    def http_delete(self, path, **kargs):
        return self.request('delete', path, **kargs)

    def __repr__(self):
        return "<Session '%s'>" % self.credentials


class Repo(Bunch):
    def __init__(self, data):
        # print data.keys()
        super(Repo, self).__init__()
        self.data = MetaBunch(data)
        self.owner = Bunch(data['owner'])
        self.access = 'private' if data['is_private'] else 'public'
        self.size = convertSize(data['size'])

        self.slug = data['full_name'].split('/')[1]

        for a in 'name scm full_name description updated_on'.split():
            setattr(self, a, data[a])

        self.load_clone_uris(data)
        self.webpage = self.data.links.html.href

    @classmethod
    def make(cls, data):
        scm = data['scm']
        return {'hg': HgRepo, 'git': GitRepo}[scm](data)

    def load_clone_uris(self, data):
        self.clone_uris = {}

        for link in data['links']['clone']:
            self.clone_uris[link['name']] = link['href']

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.full_name)


class HgRepo(Repo):
    def clone(self, proto, destdir):
        def is_same_repo():
            right_paths = set(self.clone_uris.values())
            dir_paths = set(repo.hg_paths().values())
            return right_paths.intersection(dir_paths)

        if not os.path.exists(destdir):
            hgapi.hg_clone(self.clone_uris[proto], destdir)
            return True

        if not os.path.isdir(destdir):
            raise exc.UnrelatedContent(destdir)

        repo = hgapi.Repo(destdir)
        if not is_same_repo():
            raise exc.UnrelatedContent(destdir)

        repo.hg_pull()
        repo.hg_update('tip')
        return False


class GitRepo(Repo):
    def clone(self, proto, destdir):
        def is_same_repo():
            right_paths = self.clone_uris.values()
            remotes = repo.git_command('remote', 'show', 'origin')
            for path in right_paths:
                if path in remotes:
                    return True

                return False

        if not os.path.exists(destdir):
            gitapi.git_clone(self.clone_uris[proto], destdir)
            return True

        if not os.path.isdir(destdir):
            raise exc.UnrelatedContent(destdir)

        repo = gitapi.Repo(destdir)
        if not is_same_repo():
            raise exc.UnrelatedContent(destdir)

        repo.git_pull()
        return False


class RepoManager(object):
    def __init__(self, account=None):
        self.session = Session(account)

    def repo_info(self, owner, slug):
        errors = {
            403: [exc.InvalidCredentials, self.session.credentials],
            404: [exc.RepositoryNotFound, owner + '/' + slug]}

        data = self.session.http_get('repositories/{}/{}'.format(owner, slug), errors=errors)
        return Repo.make(data)

    def repo_list(self, owner):
        def page_iter_request(url, errors):
            while 1:
                data = self.session.http_get(url, errors=errors)
                for k in data['values']:
                    yield k

                url = data.get('next')
                if not url:
                    break

        errors = {
            401: [exc.AuthenticationError, self.session.credentials],
            404: [exc.NoSuchUser, owner]}

        for i in sorted(page_iter_request('repositories/{}'.format(owner), errors)):
            yield Repo.make(i)

    def repo_create(self, owner, repo_slug, scm='hg', is_private=True, description=''):
        data = dict(
            scm=scm,
            is_private='true' if bool(is_private) else 'false',
            description=description)

        self.session.http_post('repositories/{}/{}'.format(owner, repo_slug), data=data)

    def repo_delete(self, owner, repo_slug):
        self.session.http_delete('repositories/{}/{}'.format(owner, repo_slug), ok=204)
