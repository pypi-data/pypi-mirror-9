# -*- coding: utf-8; mode: python -*-

class LocalRepo:
    + dirname
=   + api_repo
=   + full_name
=      + owner, slug

    + scm [property]

    def from_dir(dirname):
        "factory to build a local_repo"

=       + get_origin_by_cmd
=       + get_full_name

    def get_origin_by_cmd(proto):
        + api_repo -> url

    def get_path(origin):
        origin -> full_name

    def pull(account, proto):
        + get_origin_by_cmd(proto) -> origin
        ! manager(+owner, +slug) -> bb_repo
        ! bb_repo._apply_pwd(origin, account) -> origin
        + api_repo.pull(origin)

    def push(account, proto):
        + get_origin_by_cmd(proto) -> origin
        + owner, slug -> bb_repo
        ! bb_repo._apply_pwd(origin, account) -> origin
        + api_repo.push(origin)


class Repo:
    + data
=      + access
=      + size
=      + webpage
=      + description
=       + [scm]
       + uris
=      + full_name
=        + owner, slug

    def from_data(data):


    def get_origin_by_rest(proto):
        + uris -> origin

    def apply_pwd(origin, account):
        origin -> origin

    def clone(account, proto, destdir):
        + get_origin_by_rest
        + apply_pwd
        hgapi.hg_clone

        local_repo = LocaRepo.from_dir(destdir)
        local_repo.pull(account, proto)


creators
--------

  - Repo.from_data()
    - Manager.repo_info()
    - Manager.repo_list()

  - LocalRepo.from_dir()
    - Repo.clone()
    - cli.repo2full_name()
    - cli.repo_create()
    - cli.repo_status()
