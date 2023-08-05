# -*- coding: utf-8; mode: python -*-

import sys
import os.path
import time
import logging
import urlparse

# print 0
import requests
import json
import hgapi
import gitapi

logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger('bucket')

import exceptions as exc
from commodity.pattern import Bunch, MetaBunch

import lurl

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
BB_API1 = 'https://api.bitbucket.org/1.0/{path}'
BB_API1 = 'https://bitbucket.org/api/1.0/{path}'
BB_API2 = 'https://api.bitbucket.org/2.0/{path}'

PROTO_SSH = 'ssh'
PROTO_HTTPS = 'https'


def bb_api1_uri(path):
    uri = BB_API1.format(path=path)
    return uri


def bb_api2_uri(path):
    uri = BB_API2.format(path=path)
    return uri


def reply2json(rep, ok=None):
    ok = ok or 200

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
    def __init__(self, account=None, logger=None, verbose=False):
        self.account = account
        self.timeout = 10
        self._http_session = None
        self.logger = logger or logging.getLogger('bucket')

        self.verbose = verbose

    def auth(self):
        if self.account is None or self.account.is_anonymous():
            return None

        return (self.account.username, self.account.password)

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

        # if self.account:
        #     self.test_auth()

        return self._http_session

    # def test_auth(self):
    #     errors = {
    #         400: [exc.InvalidOrAlreadyRegisteredSSHkey],
    #         401: [exc.InvalidAccount, self.account]}

    #     self.http_get(bb_api1_uri('ssh-keys'), errors=errors)

    def request(self, method, path, data=None, ok=None):
        self.logger.debug("request %s %s %s", method, path, data)
        while 1:
            url = path if path.startswith('http') else bb_api2_uri(path)
            try:
                reply = self.http_session.request(method, url, data=data)
                retval = reply2json(reply, ok=ok)
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
        return "<Session '%s'>" % self.account


class Repo(object):
    def __init__(self, manager, full_name=None, dirname=None):
        assert self.__class__ is not Repo
#        super(Repo, self).__init__()
        self.manager = manager
        self.full_name = full_name
        self.dirname = dirname
        self._data = None
        self._api_repo = None
        self._uris = None
        self._custom_args = []

    @classmethod
    def from_data(cls, manager, full_name):
        try:
            data = MetaBunch(manager.get_repo_info(full_name))
            repo_cls = {'hg': HgRepo, 'git': GitRepo}[data.scm]
            retval = repo_cls(manager, full_name)
        except exc.RemoteException as e:
            if e.reason == "NOT_FOUND":
                raise exc.NoSuchRepo()
            raise

        retval._data = data
        return retval

    @classmethod
    def from_dir(cls, manager, dirname=None):
        dirname = dirname or os.path.join(os.getcwd())

        try:
            return HgRepo.from_dir(manager, dirname)
        except hgapi.HgException as hg_e:
            pass

        try:
            return GitRepo.from_dir(manager, dirname)
        except gitapi.gitapi.GitException as git_e:
            pass

        logger.debug("LocalRepo('%s'):\n%s", dirname, hg_e)
        logger.debug("LocalRepo('%s'):\n%s", dirname, git_e)
        raise exc.NoSuchRepo(dirname)

    @property
    def data(self):
        if self._data is None:
            self._data = MetaBunch(self.manager.get_repo_info(self.full_name))

        return self._data

    @property
    def slug(self):
        return self.full_name.split('/')[1]

    @property
    def api_repo(self):
        if self._api_repo is None:
            self._build_api_repo()

        return self._api_repo

    def as_dict(self):
        retval = {}
        for k in 'name full_name is_private scm size'.split():
            retval[k] = self[k]

        return retval

    def __getitem__(self, key):
        if key == 'size':
            return self.size

        if key == 'webpage':
            return self.wegpage

        return self.data[key]

    def is_private(self):
        return self.data.is_private

    @property
    def size(self):
        return convertSize(self.data.size)

    @property
    def webpage(self):
        return self.data.links.html.href

    @property
    def scm(self):
        if self._api_repo is not None:
            scms = {hgapi.Repo: 'hg', gitapi.Repo: 'git'}
            return scms[self._api_repo.__class__]

        return self.data.scm

    @property
    def uris(self):
        def load_uris():
            retval = {}

            for link in self.data.links.clone:
                proto = link['name']
                retval[proto] = link['href']

            return retval

        if self._uris is None:
            self._uris = load_uris()

        return self._uris

    def _get_origin_by_rest(self, proto):
        return self.uris[proto]

    def _get_origin_by_cmd(self, proto=PROTO_HTTPS):
        assert proto in [PROTO_HTTPS, PROTO_SSH]

        try:
            origin = self._do_get_origin_by_cmd()
            url = lurl.change_login(urlparse.urlparse(origin))

            if url.scheme == proto:
                return url.geturl()

            return lurl.change_proto(url, proto).geturl()
        except KeyError:
            return None

    @classmethod
    def _get_full_name(cls, origin):
        url = urlparse.urlparse(origin)
        if url.hostname != bitbucket_org:
            return None

        return cls._sanitize_full_name(url.path)

    @classmethod
    def _sanitize_full_name(cls, full_name):
        return full_name.strip('/')

    def _apply_pwd(self, origin):
        url = urlparse.urlparse(origin)
        if url.scheme == PROTO_HTTPS and self.is_private():
            username = self.manager.session.account.username
            password = self.manager.session.account.password
            return lurl.change_login(url, username, password).geturl()

        return origin

    def __eq__(self, other):
        return self.scm == other.scm and self.full_name == other.full_name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<{} {}>".format(self.__class__.__name__, self.full_name)


class HgRepo(Repo):
    @classmethod
    def from_dir(cls, manager, dirname):
        repo = HgRepo(manager, full_name=None, dirname=dirname)
        origin = repo._get_origin_by_cmd()
        repo.full_name = repo._get_full_name(origin)
        return repo

    def _build_api_repo(self):
        assert self.dirname is not None
        self._api_repo = hgapi.Repo(self.dirname)
        self._api_repo.hg_id()

    def _do_get_origin_by_cmd(self):
        return self.api_repo.hg_paths()['default']

    def clone(self, proto, destdir):
        def do_clone():
            if not os.path.exists(destdir):
                origin = self._get_origin_by_rest(proto)
                origin = self._apply_pwd(origin)

                logger.debug("cloning %s", origin)
                hgapi.hg_clone(origin, destdir, *self._custom_args)
                return True

            if not os.path.isdir(destdir):
                raise exc.UnrelatedContent(destdir)

            local = HgRepo.from_dir(self.manager, destdir)
            if self != local:
                raise exc.UnrelatedContent(destdir)

            self.dirname = destdir
            self.pull(proto)

        try:
            return do_clone()
        except hgapi.hgapi.HgException as e:
            raise exc.CloneError(e)

    def pull(self, proto):
        origin = self._apply_pwd(self._get_origin_by_cmd(proto))
        self.api_repo.hg_pull(origin)
        self.api_repo.hg_update('tip')

    def push(self, proto):
        origin = self._apply_pwd(self._get_origin_by_cmd(proto))
        self.api_repo.hg_push(origin)


class GitRepo(Repo):
    @classmethod
    def from_dir(cls, manager, dirname):
        repo = GitRepo(manager, full_name=None, dirname=dirname)
        origin = repo._get_origin_by_cmd()
        repo.full_name = repo._get_full_name(origin)
        return repo

    def _build_api_repo(self):
        self._api_repo = gitapi.Repo(self.dirname)
        self._api_repo.git_id()

    def _do_get_origin_by_cmd(self):
        remote = self.api_repo.git_command('remote', 'show', 'origin')
        prefix = 'Fetch URL: '

        retval = ''
        for line in remote.split('\n'):
            line = line.strip()
            if line.startswith('Fetch'):
                i = line.index(prefix) + len(prefix)
                retval = line[i:]
                break

        return retval

    @classmethod
    def _sanitize_full_name(cls, full_name):
        return full_name.strip('/').rstrip('.git')

    def clone(self, proto, destdir):
        def do_clone():
            if not os.path.exists(destdir):
                origin = self._get_origin_by_rest(proto)
                origin = self._apply_pwd(origin)

                logger.debug("cloning %s", origin)
                gitapi.git_clone(origin, destdir)
                return True

            if not os.path.isdir(destdir):
                raise exc.UnrelatedContent(destdir)

            local = GitRepo.from_dir(self.manager, destdir)

            if self != local:
                raise exc.UnrelatedContent(destdir)

            self.dirname = destdir
            self.pull(proto)

        try:
            return do_clone()
        except hgapi.hgapi.HgException as e:
            raise exc.CloneError(e)

    def pull(self, proto):
        origin = self._apply_pwd(self._get_origin_by_cmd(proto))
        self.api_repo.git_pull(origin)

    def push(self, proto):
        origin = self._apply_pwd(self._get_origin_by_cmd(proto))
        self.api_repo.git_push(origin)


class RepoManager(object):
    def __init__(self, account=None):
        self.session = Session(account)
        self._keymanager = None

    def get_repo_info(self, full_name):
        return self.session.http_get('repositories/{}'.format(full_name))

    def repo_list(self, owner):
        def page_iter_request(url):
            while 1:
                data = self.session.http_get(url)
                for k in data['values']:
                    yield k

                url = data.get('next')
                if not url:
                    break

        for i in sorted(page_iter_request('repositories/{}'.format(owner))):
            yield Repo.from_data(self, i['full_name'])

    def repo_create(self, full_name, scm='hg', is_private=True, description=''):
        data = dict(
            scm=scm,
            is_private='true' if bool(is_private) else 'false',
            description=description)

        self.session.http_post('repositories/{}'.format(full_name), data=data)

    def repo_delete(self, full_name):
        try:
            self.session.http_delete('repositories/{}'.format(full_name), ok=204)
        except exc.RemoteException as e:
            if e.reason == 'NOT_FOUND':
                raise exc.NoSuchRepo(full_name)
            raise

    @property
    def key_manager(self):
        if self._keymanager is None:
            self._keymanager = SshKeyManager(self.session)

        return self._keymanager


class SshKeyManager(object):
    def __init__(self, session):
        self.session = session

    def list_keys(self):
        return self.session.http_get(bb_api1_uri('ssh-keys'))

    def list_key_labels(self):
        return list(set([x['label'] for x in self.list_keys()]))

    def list_key_summaries(self):
        retval = []

        template = "pk: {pk:>8} |  label: {label:<12} |  {key_summary}"
        for key in self.list_keys():
            retval.append(template.format(
                label=key['label'],
                pk=key['pk'],
                key_summary=self._key_summary(key['key'])))

        return retval

    def _key_summary(self, keycontent):
        fields = keycontent.split()
        proto = seq = host = ''
        try:
            proto = fields[0]
            seq = fields[1]
            host = fields[2]
        except IndexError:
            pass

        return "{0} {1}...{2} {3}".format(proto, seq[:12], seq[-12:], host)

    def add_key(self, label, keyfile):
        try:
            retval = self.session.http_post(
                bb_api1_uri('ssh-keys'.format(self.session.account.username)),
                data=dict(label=label, key=keyfile.read()))
        except exc.RemoteException as e:
            if e.reason == 'BAD_REQUEST':
                raise exc.NoValidKey()
            raise

        return retval['pk']

    def delete_key_by_label(self, label):
        keys = self.find_keys_by_label(label)
        if not keys:
            raise exc.NoSuchKey(label)

        for key in keys:
            self.delete_key_by_id(key['pk'])

    def delete_key_by_id(self, pk):
        self.session.http_delete(bb_api1_uri('ssh-keys/%s' % pk), ok=204)

    def find_keys_by_label(self, label):
        retval = []
        for key in self.list_keys():
            if key['label'] == label:
                retval.append(key)

        return retval
