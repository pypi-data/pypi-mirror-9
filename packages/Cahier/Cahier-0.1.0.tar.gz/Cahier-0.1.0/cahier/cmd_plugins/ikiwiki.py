#!/usr/bin/env python3

# Copyright 2014 Louis Paternault
#
# Cahier is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cahier is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with Cahier.  If not, see <http://www.gnu.org/licenses/>.

"""Define ikiwiki related command line subcommands."""

import argparse
import os
import shlex
import subprocess

import cahier.path

def run_ikiwiki(config, profile, arguments):
    """Run ikiwiki command.

    Arguments:
    - config: configparser object corresponding to ~/.cahier/cahierrc.cfg;
    - profile: current profile;
    - arguments: arguments to pass to IkiWiki (may be None).
    """
    # Building command
    command = ['ikiwiki']
    command.extend(['--setup', os.path.basename(profile['config']['setup'])])
    if config.has_option('wiki', 'options'):
        command.extend((shlex.split(config['wiki']['options'])))
    if arguments:
        command.extend(arguments)

    # Running command
    process = subprocess.Popen(
        command,
        cwd=cahier.path.absfullpath(
            os.path.dirname(profile['config']['setup'])
            ),
        )

    return process.wait()

def do_wiki(config, options, profile):
    """Run 'wiki' command."""
    return run_ikiwiki(config, profile, options.args)

def do_refresh(config, options, profile):
    """Run 'refresh' command."""
    return run_ikiwiki(config, profile, ['--refresh'] + options.args)

def do_rebuild(config, options, profile):
    """Run 'rebuild' command."""
    return run_ikiwiki(config, profile, ['--rebuild'] + options.args)

def load_plugin(subparsers, __ignored):
    """Load current plugin.

    Add parsers to argument, with appropriate actions to make them effective.

    Arguments:
    - subparsers: object to complete with custom commands;
    - parent: may be None.
    """
    # Parser for 'wiki' subcommand
    parser_wiki = subparsers.add_parser(
        'wiki',
        help='Run IkiWiki.',
        )
    parser_wiki.set_defaults(function=do_wiki)
    parser_wiki.add_argument(
        'args',
        nargs=argparse.REMAINDER,
        help="Arguments to pass to IkiWiki",
        default=None,
        )

    # Parser for 'refresh' subcommand
    parser_refresh = subparsers.add_parser(
        'refresh',
        help='Alias for "wiki --refresh"',
        aliases=['fresh'],
        )
    parser_refresh.set_defaults(function=do_refresh)
    parser_refresh.add_argument(
        'args',
        nargs=argparse.REMAINDER,
        help="Arguments to pass to IkiWiki",
        default=None,
        )

    # Parser for 'rebuild' subcommand
    parser_rebuild = subparsers.add_parser(
        'rebuild',
        help='Alias for "wiki --rebuild"',
        )
    parser_rebuild.set_defaults(function=do_rebuild)
    parser_rebuild.add_argument(
        'args',
        nargs=argparse.REMAINDER,
        help="Arguments to pass to IkiWiki",
        default=None,
        )

