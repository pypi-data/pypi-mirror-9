# -*- coding: utf-8; mode: python -*-

import sys
import os.path
import time
import logging

# print 0
import requests
import json
import hgapi
import gitapi

logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger('bucket')

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


bitbucket_org = 'bitbucket.org'
# BB_API1 = 'https://api.bitbucket.org/1.0/{path}'
BB_API2 = 'https://api.bitbucket.org/2.0/{path}'


# def bb_api1_uri(path):
#     uri = BB_API1.format(path=path)
#     return uri


def bb_api2_uri(path):
    uri = BB_API2.format(path=path)
    return uri


def reply2json(rep, ok=None, errors=None):
    ok = ok or 200
    errors = errors or {}

    if rep.status_code != ok:
        raise exc.RemoteException.from_reply(rep)

    if not rep.content:
        return None

    return json.loads(rep.content)


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

    # def test_auth(self):
    #     errors = {
    #         400: [exc.InvalidOrAlreadyRegisteredSSHkey],
    #         401: [exc.InvalidCredentials, self.credentials]}

    #     self.http_get(bb_api1_uri('ssh-keys'), errors=errors)

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


class LocalRepo(Bunch):
    @classmethod
    def from_dir(cls, dirname=None):
        dirname = dirname or os.path.join(os.getcwd())

        try:
            return HgLocalRepo.from_dir(dirname)
        except hgapi.HgException as hg_e:
            pass

        try:
            return GitLocalRepo.from_dir(dirname)
        except gitapi.gitapi.GitException as git_e:
            pass

        logger.debug("LocalRepo('%s'):\n%s", dirname, hg_e)
        logger.debug("LocalRepo('%s'):\n%s", dirname, git_e)
        raise exc.NotRepo(dirname)


class HgLocalRepo(LocalRepo):
    @property
    def scm(self):
        return 'hg'

    @classmethod
    def from_dir(cls, dirname):
        raw_repo = hgapi.Repo(dirname)
        raw_repo.hg_id()

        data = Bunch()
        data.raw_repo = raw_repo
        data.origin = cls.get_origin(raw_repo)
        data.path = cls.get_path(data.origin)
        data.dirname = dirname
        return HgLocalRepo(**data)

    @classmethod
    def get_origin(cls, raw_repo):
        try:
            return raw_repo.hg_paths()['default']
        except KeyError:
            return None

    @classmethod
    def get_path(cls, origin):
        try:
            i = origin.index(bitbucket_org) + len(bitbucket_org)
        except (ValueError, AttributeError):
            return None

        return origin[i:].strip('/')

    def pull(self):
        self.raw_repo.hg_pull()
        self.raw_repo.hg_update('tip')

    def push(self, bb_repo, proto, account=None):
        password = ':' + account.password if account else ''
        push_url = bb_repo.uris[proto].format(password)
        self.repo.hg_push(push_url)


class GitLocalRepo(LocalRepo):
    @property
    def scm(self):
        return 'git'

    @classmethod
    def from_dir(cls, dirname):
        raw_repo = gitapi.Repo(dirname)
        raw_repo.git_id()

        data = Bunch()
        data.raw_repo = raw_repo
        data.origin = cls.get_origin(raw_repo)
        data.path = cls.get_path(data.origin)
        data.dirname = dirname
        return GitLocalRepo(**data)

    @classmethod
    def get_origin(cls, api_repo):
        remote = api_repo.git_command('remote', 'show', 'origin')
        prefix = 'Fetch URL: '

        path = ''
        for line in remote.split('\n'):
            line = line.strip()
            if line.startswith('Fetch'):
                i = line.index(prefix) + len(prefix)
                path = line[i:]
                break

        return path

    @classmethod
    def get_path(cls, origin):
        try:
            i = origin.index(bitbucket_org) + len(bitbucket_org)
        except ValueError:
            return None

        return origin[i:].strip('/').rstrip('.git')

    def pull(self):
        self.raw_repo.git_pull()

    def push(self, bb_repo, proto, account=None):
        # FIXME
        raise AssertionError()


class Repo(Bunch):
    def __init__(self, data):
        # print data.keys()
        super(Repo, self).__init__()
        self.data = MetaBunch(data)
        owner = Bunch(data['owner'])
        self.owner = owner.username
        self.owner_data = owner
        self.access = 'private' if data['is_private'] else 'public'
        self.size = convertSize(data['size'])

        self.slug = data['full_name'].split('/')[1]

        for a in 'name scm full_name description updated_on'.split():
            setattr(self, a, data[a])

        self._load_uris(data)
        self.webpage = self.data.links.html.href

    @classmethod
    def form_data(cls, data):
        scm = data['scm']
        return {'hg': HgRepo, 'git': GitRepo}[scm](data)

    def _load_uris(self, data):
        self.uris = {}

        for link in data['links']['clone']:
            proto = link['name']
            uri = link['href']
            if proto == 'https':
                uri = uri.replace('@', '{}@')

            self.uris[proto] = uri

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.full_name)


class HgRepo(Repo):
    def clone(self, proto, destdir):
        try:
            return self.do_clone(proto, destdir)
        except hgapi.hgapi.HgException as e:
            raise exc.CloneError(e)

    def do_clone(self, proto, destdir):
        if not os.path.exists(destdir):
            hgapi.hg_clone(self.uris[proto], destdir)
            return True

        if not os.path.isdir(destdir):
            raise exc.UnrelatedContent(destdir)

        local_repo = LocalRepo.from_dir(destdir)
        if local_repo.scm != 'hg' or local_repo.path != self.full_name:
            raise exc.UnrelatedContent(destdir)

        local_repo.pull()
        return False


class GitRepo(Repo):
    def clone(self, proto, destdir):
        try:
            return self.do_clone(proto, destdir)
        except gitapi.gitapi.GitException as e:
            raise exc.CloneError(e)

    def do_clone(self, proto, destdir):
        if not os.path.exists(destdir):
            gitapi.git_clone(self.uris[proto], destdir)
            return True

        if not os.path.isdir(destdir):
            raise exc.UnrelatedContent(destdir)

        local_repo = LocalRepo.from_dir(destdir)
        if local_repo.scm != 'git' or local_repo.path != self.full_name:
            raise exc.UnrelatedContent(destdir)

        local_repo.pull()
        return False


class RepoManager(object):
    def __init__(self, account=None):
        self.session = Session(account)

    def repo_info(self, owner, slug):
        errors = {
            403: [exc.InvalidCredentials, self.session.credentials],
            404: [exc.RepositoryNotFound, owner + '/' + slug]}

        data = self.session.http_get('repositories/{}/{}'.format(owner, slug), errors=errors)
        return Repo.form_data(data)

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
            yield Repo.form_data(i)

    def repo_create(self, owner, repo_slug, scm='hg', is_private=True, description=''):
        data = dict(
            scm=scm,
            is_private='true' if bool(is_private) else 'false',
            description=description)

        self.session.http_post('repositories/{}/{}'.format(owner, repo_slug), data=data)

    def repo_delete(self, owner, repo_slug):
        self.session.http_delete('repositories/{}/{}'.format(owner, repo_slug), ok=204)
