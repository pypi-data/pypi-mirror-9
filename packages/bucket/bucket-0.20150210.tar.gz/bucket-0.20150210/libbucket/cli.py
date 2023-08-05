# -*- coding: utf-8; mode: python -*-

import sys
import os
import getpass
import logging
import webbrowser
import argparse

logging.basicConfig()
logger = logging.getLogger('bucket')

from commodity.args import parser, args

import api
import exceptions as exc


def canceled():
    msg('-- canceled')
    sys.exit(1)


def msg(text, fd=None):
    fd = fd or args.stdout
    fd.write(str(text) + '\n')


class readable_dir(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        prospective_dir = values

        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError(
                "readable_dir: '{0}' is not a valid path".format(prospective_dir))

        if os.access(prospective_dir, os.R_OK):
            setattr(namespace, self.dest, prospective_dir)
            return

        raise argparse.ArgumentTypeError(
            "readable_dir: '{0}' is not a readable dir".format(prospective_dir))


def repo2full_name(repo):
    if repo is None:
        repo = api.Repo.from_dir(args.manager).full_name

    if repo.count('/') != 1 or repo.endswith('/'):
        raise exc.WrongRepoPathFormat()

    owner, slug = repo.split('/')
    if not owner:
        if args.account is None:
            raise exc.OwnerRequired()

        owner = args.account.username

    return owner + '/' + slug


def get_repo():
    full_name = repo2full_name(args.repo)

    try:
        return api.Repo.from_data(args.manager, full_name)

    except exc.BasicException:
        if not args.repo.startswith('/'):
            raise

        return get_alternate_repo(args.repo)


def get_alternate_repo(repo):
    full_name = repo2full_name(args.repo)
    owner = full_name.split('/')[0]

    for owner in [owner] + get_config_owners(owner):
        try:
            return api.Repo.from_data(args.manager, full_name)
        except exc.BasicException:
            logger.info("trying {}: FAIL".format(full_name))

    raise exc.NoSuchRepo(full_name)


def get_config_owners(owner):
    try:
        accounts = args.ui.account.values()
    except KeyError:
        return []

    retval = []
    for account in accounts:
        if account.count(':') > 1:
            logger.warning("wrong account format: '%s'", account)

        retval.append(account.split(':')[0])

    if owner in retval:
        retval.remove(owner)

    return retval


def repo_info():
    repo = get_repo()

    for atr in 'full_name name description scm is_private size updated_on'.split():
        key = atr.replace('_', ' ') + ':'
        value = str(repo[atr])
        if not value.strip():
            continue

        msg("{:12} {}".format(key, value))


def repo_create():
    full_name = repo2full_name(args.repo)

    scm = 'git' if args.create_git else 'hg'

    if not args.create_yes:
        answer = raw_input("create '{}' ({}) repository? (Y/n): ".format(full_name, scm))
        if answer.lower() not in ['', 'y', 'yes']:
            canceled()

    else:
        msg("creating '{}' ({})".format(full_name, scm))

    args.manager.repo_create(full_name, scm=scm)

    if args.create_local:
        msg("pushing local content to '{}'".format(full_name))
        repo = api.LocalRepo.from_dir()
        repo.push(args.manager.repo_info(full_name), args.create_proto, args.account)


def confirm_irrecoverable_operation():
    answer = raw_input("This is an IRRECOVERABLE operation!!\nAre you sure? (write uppercase 'yes'): ")
    if answer != 'YES':
        canceled()


def repo_delete():
    full_name = repo2full_name(args.repo)

    if not args.delete_yes:
        confirm_irrecoverable_operation()

    msg("Deleting '{}'\n".format(full_name))
    args.manager.repo_delete(full_name)


def repo_ls():
    if args.owner is None:
        if args.account.is_anonymous():
            raise exc.OwnerRequired()

        args.owner = args.account.username

    item = u'{full_name}'
    if args.ls_access:
        item = u'{is_private:7} - ' + item

    if args.ls_scm:
        item = u'{scm:3} - ' + item

    if args.ls_size:
        item = u'{size:>13} - ' + item

    lines = []
    for repo in args.manager.repo_list(owner=args.owner):
        line = item.format(**repo.as_dict()) + u'\n'
        lines.append(line)

    for line in lines:
        args.stdout.write(line.encode('utf-8'))


def repo_clone():
    repo = get_repo()

    destdir = os.path.join(args.clone_destdir or os.path.join(os.getcwd()), repo.slug)

    msg("Clonning '{}' to '{}' ({}/{}) ".format(
        repo.full_name, destdir, repo.scm, args.clone_proto))

    if not repo.clone(args.clone_proto, destdir):
        msg("  repository already cloned, updating")


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
    msg("Owner '{}' has {} repositories".format(owner, len(repos)))

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


def repo_website():
    repo = args.manager.repo_info(repo2full_name(args.repo))
    url = repo.webpage

    if args.site_settings:
        url += '/admin'

    msg("Openning '{}'".format(url))
    webbrowser.open(url)


def repo_status():
    bb_repos = []
    not_bb_repos = []
    not_repos = []

    for d in os.listdir(args.clone_destdir):
        args.stdout.write('.')
        args.stdout.flush()

        path = os.path.join(args.clone_destdir, d)
        if not os.path.isdir(path):
            continue

        try:
            local_repo = api.LocalRepo.from_dir(path)
            if local_repo.path:
                bb_repos.append(local_repo)
            else:
                not_bb_repos.append(local_repo)

        except exc.NoSuchRepo:
            not_repos.append(d)

    print

    for r in bb_repos:
        msg("+ {:<3} - {:<30} - {}".format(r.scm, os.path.split(r.dirname)[1], r.path))

    msg("\n -- Not bitbucket.org repos:")
    for r in not_bb_repos:
        msg("- {:<3} - {:<30} - {}".format(r.scm, os.path.split(r.dirname)[1], r.origin))

    msg('\n -- Not a repository:')
    for r in not_repos:
        msg(r)


def ssh_ls():
    msg("SSH public keys for user: %s" % args.account.username)
    key_summaries = args.manager.key_manager.list_key_summaries()
    if not key_summaries:
        msg("No keys found")
        return

    print str.join('\n', key_summaries)


def ssh_add():
    pk = args.manager.key_manager.add_key(args.ssh_keylabel, args.ssh_keyfile)
    msg('PK for the uploaded key: %s' % pk)


def ssh_del():
    args.manager.key_manager.delete_key_by_label(args.ssh_keylabel)


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
    setup_parser_status(commands)
    setup_parser_ssh(commands)


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
    subparser.add_argument('repo', nargs='?')


def setup_parser_create(commands):
    subparser = create_subparser(commands, 'create', func=repo_create,
                                 help="create a repository in bitbucket server")
    add_proto_args(subparser, 'create_proto')
    subparser.add_argument('repo')
    subparser.add_argument('--yes', '-y', dest='create_yes', action='store_true',
                           help="don't ask for confirmation")
    subparser.add_argument('--git', dest='create_git', action='store_true',
                           help='create a git repository')
    subparser.add_argument('--from-local', dest='create_local', action='store_true',
                           help="push current content to the created repo")

    # --hg
    # --public
    # --private
    # --desc
    # --clone


def setup_parser_delete(commands):
    subparser = create_subparser(commands, 'delete', func=repo_delete,
                                 help='delete de given repository')
    subparser.add_argument('repo')
    subparser.add_argument('--yes', '-y', dest='delete_yes', action='store_true',
                           help="don't ask for confirmation")


def add_proto_args(parser, dest):
    parser.add_argument('--https', dest=dest, action='store_const', const=api.PROTO_HTTPS,
                        help='use HTTPS to clone')
    parser.add_argument('--ssh', dest=dest, action='store_const', const=api.PROTO_SSH,
                        help='use SSH to clone')


def add_destdir_arg(parser):
    parser.add_argument(
        '--destdir', '-d', dest='clone_destdir', metavar='dirname',
        action=readable_dir,
        help='the directory where your repositories are')


def setup_parser_clone(commands):
    subparser = create_subparser(commands, 'clone', func=repo_clone,
                                 help="clone/update given repository")
    subparser.add_argument('repo', metavar='[owner]/repository',
                           help='repository to clone')
    add_proto_args(subparser, 'clone_proto')
    add_destdir_arg(subparser)


def setup_parser_sync(commands):
    subparser = create_subparser(commands, 'sync', func=repo_sync,
                                 help='clone/update a bunch of repositories')
    add_proto_args(subparser, 'clone_proto')
    add_destdir_arg(subparser)
    subparser.add_argument('--owner', '-o', dest='sync_owner',
                           help="sync all 'owner' repositories")


def setup_parser_site(commands):
    subparser = create_subparser(commands, 'site', func=repo_website,
                                 help="open bitbucket webpage for the repository")
    subparser.add_argument('repo', nargs='?')
    subparser.add_argument('--settings', '-s', dest="site_settings", action="store_true",
                           help="open settings page")


def setup_parser_status(commands):
    subparser = create_subparser(commands, 'st', func=repo_status,
                                 help="show status for your repository bunch")
    add_destdir_arg(subparser)


def setup_parser_ssh(commands):
    default_pub_keyfile = '~/.ssh/id_rsa.pub'
    p = create_subparser(commands, 'ssh-ls', func=ssh_ls,
                         help='List your account SSH keys')

    p = create_subparser(commands, 'ssh-add', func=ssh_add,
                         help='Upload a SSH key to your account')
    p.add_argument('ssh_keylabel', metavar='keylabel',
                   help='the user-visible label on the key')
    p.add_argument('ssh_keyfile', metavar='keyfile', nargs='?',
                   type=argparse.FileType('r'),
                   default=file(os.path.expanduser(default_pub_keyfile)),
                   help="public key file path [default: '{}']".format(
                       default_pub_keyfile))

    p = create_subparser(commands, 'ssh-del', func=ssh_del,
                         help='Delete a SSH key by label')
    p.add_argument('ssh_keylabel', metavar='keylabel',
                   help='key label. Run ssh-ls')


def create_subparser(root, name, func, help=""):
    cmd = root.add_parser(name, help=help)  # , argument_default=argparse.SUPPRESS)
    cmd.set_defaults(func=func)
    return cmd


def parse_args(argv=None, ns=None, stdout=None):
    argv = argv or sys.argv[1:]
    if isinstance(argv, (str, unicode)):
        argv = argv.split()

    load_config_file(argv)

    try:
        parser.parse_args(argv, ns)
    except argparse.ArgumentTypeError as e:
        logger.error(e)
        sys.exit(1)

    args.stdout = stdout or sys.stdout
    setup_verbosity()

    args.clone_proto = args.get('clone_proto') or api.PROTO_HTTPS

    args.account = setup_account(args.account)
    logger.info("Authenticated as: %s", args.account.username)
    args.manager = api.RepoManager(args.account)


def load_config_file(argv):
    auxp = argparse.ArgumentParser(add_help=False)
    auxp.add_argument('--config', '-c', default=os.path.expanduser('~/.bucket'))
    values, pos = auxp.parse_known_args(argv)

    if not os.path.isfile(values.config):
        logger.error("bad file: %s", values.config)
    else:
        parser.load_config_file(values.config)


def setup_verbosity():
    try:
        level = [logging.WARNING, logging.INFO, logging.DEBUG][args.verbosity]
    except IndexError:
        level = logging.DEBUG

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
        msg('-- ok')
    except exc.BasicException as e:
        print e

        if not args.verbosity:
            print "Try 'bucket -v'"
        sys.exit(1)
