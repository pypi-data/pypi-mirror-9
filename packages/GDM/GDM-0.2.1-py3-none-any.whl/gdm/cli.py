#!/usr/bin/env python

"""Command-line interface."""

import sys
import argparse

from . import CLI, VERSION, DESCRIPTION
from . import common
from . import commands

log = common.logger(__name__)


def main(args=None, function=None):
    """Process command-line arguments and run the program."""

    # Shared options
    debug = argparse.ArgumentParser(add_help=False)
    debug.add_argument('-V', '--version', action='version', version=VERSION)
    group = debug.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='count', default=0,
                       help="enable verbose logging")
    group.add_argument('-q', '--quiet', action='store_const', const=-1,
                       dest='verbose', help="only display errors and prompts")
    project = argparse.ArgumentParser(add_help=False)
    project.add_argument('-r', '--root', metavar='PATH',
                         help="root directory of the project")
    shared = {'formatter_class': common.WideHelpFormatter,
              'parents': [project, debug]}

    # Main parser
    parser = argparse.ArgumentParser(prog=CLI, description=DESCRIPTION,
                                     **shared)

    subs = parser.add_subparsers(help="", dest='command', metavar="<command>")

    # Install parser
    info = "get the specified versions of all dependencies"
    sub = subs.add_parser('install', description=info.capitalize() + '.',
                          help=info, **shared)
    sub.add_argument('-f', '--force', action='store_true',
                     help="overwrite uncommitted changes in dependencies")

    # Uninstall parser
    info = "remove all installed dependencies"
    subs.add_parser('uninstall', description=info.capitalize() + '.',
                    help=info, **shared)

    # Display parser
    info = "show the current hash of each dependency"
    subs.add_parser('list', description=info.capitalize() + '.',
                    help=info, **shared)

    # Parse arguments
    args = parser.parse_args(args=args)
    kwargs = {'root': args.root}
    if args.command == 'install':
        function = commands.install
        kwargs['force'] = args.force
    elif args.command == 'uninstall':
        function = commands.uninstall
    elif args.command == 'list':
        function = commands.display
    if function is None:
        parser.print_help()
        sys.exit(1)

    # Configure logging
    common.configure_logging(args.verbose)

    # Run the program
    try:
        log.debug("running command...")
        success = function(**kwargs)
    except KeyboardInterrupt:
        msg = "command cancelled"
        if common.verbosity == common.MAX_VERBOSITY:
            log.exception(msg)
        else:
            log.debug(msg)
        success = False
    if success:
        log.debug("command succeeded")
    else:
        log.debug("command failed")
        sys.exit(1)


if __name__ == '__main__':  # pragma: no cover (manual test)
    main()
