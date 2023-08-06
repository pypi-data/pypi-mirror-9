import argparse
import sys

from vcstool.clients import vcstool_clients
from vcstool.crawler import find_repositories
from vcstool.executor import execute_jobs, generate_jobs, output_repositories, output_results

from .command import add_common_arguments, Command


class CustomCommand(Command):

    command = 'custom'
    help = 'Run a custom command'

    def __init__(self, args):
        super(CustomCommand, self).__init__(args)
        self.args = args.args


def get_parser():
    parser = argparse.ArgumentParser(description='Run a custom command', prog='vcs custom')
    group = parser.add_argument_group('"custom" command parameters restricting the repositories')
    for client_type in [c.type for c in vcstool_clients if c.type not in ['tar']]:
        group.add_argument('--%s' % client_type, action='store_true', default=False, help="Run command on '%s' repositories" % client_type)
    group = parser.add_argument_group('"custom" command parameters')
    group.add_argument(
        '--args', required=True, nargs='*', help='Arbitrary arguments passed to each vcs invocation. '
        'It must be passed after other arguments since it collects all following options.')
    return parser


def main(args=None):
    parser = get_parser()
    add_common_arguments(parser)

    # separate anything followed after --args to not confuse argparse
    if args is None:
        args = sys.argv[1:]
    try:
        index = args.index('--args') + 1
    except ValueError:
        # should generate error due to missing --args
        parser.parse_known_args(args)

    client_args = args[index:]
    args = parser.parse_args(args[0:index])
    args.args = client_args

    # check if any client type is specified
    any_client_type = False
    for client in vcstool_clients:
        if client.type in args and args.__dict__[client.type]:
            any_client_type = True
            break
    # if no client type is specified enable all client types
    if not any_client_type:
        for client in vcstool_clients:
            if client.type in args:
                args.__dict__[client.type] = True

    command = CustomCommand(args)

    # filter repositories by specified client types
    clients = find_repositories(command.paths)
    clients = [c for c in clients if c.type in args and args.__dict__[c.type]]

    if command.output_repos:
        output_repositories(clients)
    jobs = generate_jobs(clients, command)
    results = execute_jobs(jobs, show_progress=True)

    output_results(results, hide_empty=args.hide_empty)

    any_error = any([r['returncode'] != 0 for r in results])
    return 1 if any_error else 0


def bzr_main(args=None):
    if args is None:
        args = sys.argv[1:]
    return main(['--bzr', '--args'] + args)


def git_main(args=None):
    if args is None:
        args = sys.argv[1:]
    return main(['--git', '--args'] + args)


def hg_main(args=None):
    if args is None:
        args = sys.argv[1:]
    return main(['--hg', '--args'] + args)


def svn_main(args=None):
    if args is None:
        args = sys.argv[1:]
    return main(['--svn', '--args'] + args)

if __name__ == '__main__':
    sys.exit(main())
