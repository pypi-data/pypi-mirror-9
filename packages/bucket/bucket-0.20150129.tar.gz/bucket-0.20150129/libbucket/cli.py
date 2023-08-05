# -*- coding: utf-8; mode: python -*-

import sys
import os
import getpass
import logging
import webbrowser

logging.basicConfig()
logger = logging.getLogger('bucket')

import api
from commodity.pattern import Bunch, MetaBunch
from commodity.args import parser, args

import exceptions as exc


def msg(text, fd=None):
    fd = fd or args.stdout
    fd.write(text + '\n')


def repo2owner_slug(repo):
    if repo.count('/') != 1 or repo.endswith('/'):
        raise exc.WrongRepoPathFormat()

    owner, slug = repo.split('/')
    if not owner:
        if args.account is None:
            raise exc.OwnerRequired()

        owner = args.account.username

    return owner, slug


def repo_info():
    owner, slug = repo2owner_slug(args.repo)
    repo = args.manager.repo_info(owner, slug)

    for atr in 'slug name  description  scm access size updated_on'.split():
        key = atr.replace('_', ' ') + ':'
        value = repo[atr]
        if not value.strip():
            continue

        msg("{:12} {}".format(key, value))


def repo_create():
    owner, slug = repo2owner_slug(args.repo)
    scm = 'git' if args.create_git else 'hg'

    args.stdout.write("Creating '{}/{}' ({})\n".format(owner, slug, scm))
    args.manager.repo_create(owner, slug, scm=scm)


def repo_delete():
    owner, slug = repo2owner_slug(args.repo)

    # FIXME: prompt to confirm deletion
    args.stdout.write("Deleting '{}/{}'\n".format(owner, slug))
    args.manager.repo_delete(owner, slug)


def repo_ls():
    if args.owner is None:
        if args.account.is_anonymous():
            raise exc.OwnerRequired()

        args.owner = args.account.username

    item = u'{owner.username}/{slug}'
    if args.ls_size:
        item = u'{size:>13} - ' + item

    if args.ls_access:
        item = u'{access:7} - ' + item

    if args.ls_scm:
        item = u'{scm:3} - ' + item

    lines = []
    for repo in args.manager.repo_list(owner=args.owner):
        line = item.format(**repo) + u'\n'
        lines.append(line)

    for line in lines:
        args.stdout.write(line.encode('utf-8'))


def repo_clone():
    owner, slug = repo2owner_slug(args.repo)
    repo = args.manager.repo_info(owner, slug)

    destdir = os.path.join(args.clone_destdir or os.path.join(os.getcwd()), slug)

    msg("Clonning '{}/{}' to '{}' ({}/{}) ".format(
        owner, slug, destdir, repo.scm, args.clone_proto))

    if not repo.clone(args.clone_proto, destdir):
        msg("  repository already cloned, updating")

    msg("OK")


def relpath(name):
    retval = os.path.relpath(name)
    if retval.startswith('..'):
        return name

    return retval


def repo_sync():
    owner = args.sync_owner
    if owner is None:
        if args.account.is_anonymous():
            raise exc.OwnerRequired()

        owner = args.account.username

    repos = list(args.manager.repo_list(owner))
    names = [repo.full_name for repo in repos]

    maxname = max(len(name) for name in names)
    maxpath = len(args.clone_destdir) + maxname - len(owner)

    msg("Target directory is: {}".format(args.clone_destdir))

    for repo in repos:
        destdir = os.path.join(args.clone_destdir or os.path.join(os.getcwd()), repo.slug)

        proto_info = "({}/{})".format(repo.scm, args.clone_proto)
        msg("Syncing {0:<{1}} {4} ".format(
            repo.full_name, maxname, relpath(destdir), maxpath, proto_info))

        try:
            repo.clone(args.clone_proto, destdir)
        except exc.CloneError as e:
            logger.error(e)

    msg("OK")


def repo_website():
    repo = args.manager.repo_info(*repo2owner_slug(args.repo))
    url = repo.webpage

    if args.site_settings:
        url += '/admin'

    msg("Openning '{}'".format(url))
    webbrowser.open(url)


## PARSER ##


def setup_parser():
    parser.add_argument('--account', '-a',
                        help='account in the form user[:pass] or config-key', type=str)
    parser.add_argument('--config', '-c',
                        help='process config file')
    parser.add_argument('--verbosity', '-v', action='count', default=0,
                        help='verbosity level')

    commands = parser.add_subparsers(dest='command')

    setup_parser_ls(commands)
    setup_parser_info(commands)
    setup_parser_create(commands)
    setup_parser_delete(commands)
    setup_parser_clone(commands)
    setup_parser_sync(commands)
    setup_parser_site(commands)


def setup_parser_ls(commands):
    subparser = create_subparser(commands, 'ls', func=repo_ls,
                                 help="list all repositories of the given owner")
    subparser.add_argument('owner', nargs='?',
                           help='Bitbucket repo owner [default:authenticated user]')

    subparser.add_argument('--size', '-s', dest='ls_size', action='store_true',
                           help='show repo size')
    subparser.add_argument('--access', '-a', dest='ls_access', action='store_true',
                           help='show repo access: public/private')
    subparser.add_argument('--scm', dest='ls_scm', action='store_true',
                           help='show scm: hg/git')


def setup_parser_info(commands):
    subparser = create_subparser(commands, 'info', func=repo_info,
                                 help='show detailed info about the given repository')
    subparser.add_argument('repo')


def setup_parser_create(commands):
    subparser = create_subparser(commands, 'create', func=repo_create,
                                 help="create a repository in bitbucket server")
    subparser.add_argument('repo')
    subparser.add_argument('--git', dest='create_git', action='store_true',
                           help='create a git repository')
    # --hg
    # --public
    # --private
    # --desc
    # --clone


def setup_parser_delete(commands):
    subparser = create_subparser(commands, 'delete', func=repo_delete,
                                 help='delete de given repository')
    subparser.add_argument('repo')


def add_proto_args(parser, dest):
    parser.add_argument('--https', dest=dest, action='store_const', const='https',
                        help='use HTTPS to clone')
    parser.add_argument('--ssh', dest=dest, action='store_const', const='ssh',
                        help='use SSH to clone')


def setup_parser_clone(commands):
    subparser = create_subparser(commands, 'clone', func=repo_clone,
                                 help="clone/update given repository")
    subparser.add_argument('repo', metavar='[owner]/repository',
                           help='repository to clone')
    add_proto_args(subparser, 'clone_proto')
    subparser.add_argument('--destdir', '-d', dest='clone_destdir', metavar='dirname',
                           help='local target directory')


def setup_parser_sync(commands):
    subparser = create_subparser(commands, 'sync', func=repo_sync,
                                 help='clone/update a bunch of repositories')
    add_proto_args(subparser, 'clone_proto')
    subparser.add_argument('--destdir', '-d', dest='clone_destdir', metavar='dirname',
                           help='local target directory')
    subparser.add_argument('--owner', '-o', dest='sync_owner',
                           help="sync all 'owner' repositories")


def setup_parser_site(commands):
    subparser = create_subparser(commands, 'site', func=repo_website,
                                 help="open bitbucket webpage for the repository")
    subparser.add_argument('repo')
    subparser.add_argument('--settings', '-s', dest="site_settings", action="store_true",
                           help="open settings page")


def create_subparser(root, name, func, help=""):
    cmd = root.add_parser(name, help=help)  # , argument_default=argparse.SUPPRESS)
    cmd.set_defaults(func=func)
    return cmd


def parse_args(argv=None, ns=None, stdout=None):
    argv = argv or sys.argv[1:]
    if isinstance(argv, (str, unicode)):
        argv = argv.split()

#    ns = ns or Bunch()
#    ns.clone_proto = 'https'

    parser.parse_args(argv, ns)

    setup_verbosity()

    args.stdout = stdout or sys.stdout
    args.config = args.config or os.path.expanduser('~/.bucket')

    if args.config:
        logger.debug("load config: %s", args.config)
        if not os.path.isfile(args.config):
            logger.error("bad file: %s", args.config)
        else:
            parser.load_config_file(args.config)

    parser.update_config()
    args.clone_proto = args.get('clone_proto') or 'https'

    args.account = setup_account(args.account)
    logger.info("Authenticated as: %s", args.account.username)
    args.manager = api.RepoManager(args.account)


def setup_verbosity():
    level = [logging.WARNING, logging.INFO, logging.DEBUG][args.verbosity]
    logger.setLevel(level)
    if args.verbosity:
        print "logger level is:", logging.getLevelName(level)


def get_password(username):
    return getpass.getpass("{0}'s password: ".format(username))


def setup_account(account):
    if account is None:
        return api.Account()

    account = account.strip(':')
    nfields = account.count(':') + 1

    if nfields > 2:
        raise Exception("account argument ({}) wrong format: 'user:pass'".format(account))

    if nfields == 2:
        username, password = account.split(':')
    else:
        username = account
        password = get_password(account)

    return api.Account(username, password)


setup_parser()


def run():
    try:
        args.func()
    except exc.BBException as e:
        print e
        sys.exit(1)
