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

"""Define git command line subcommand."""

import argparse
import subprocess

import cahier.path

def do_git(__ignored, options, profile):
    """Run git command."""
    # Building command
    command = ['git']
    if options.args:
        command.extend(options.args)

    # Running command
    process = subprocess.Popen(
        command,
        cwd=cahier.path.absfullpath(
            profile['directories']['calendar']
            ),
        )

    return process.wait()


def load_plugin(subparsers, __ignored):
    """Load current plugin.

    Add parsers to argument, with appropriate actions to make them effective.

    Arguments:
    - subparsers: object to complete with custom commands;
    - _: unused.
    """
    # Parser for 'git' subcommand
    parser_git = subparsers.add_parser('git', help='Run git.')
    parser_git.set_defaults(function=do_git)
    parser_git.add_argument(
        'args',
        nargs=argparse.REMAINDER,
        help="Arguments to pass to git",
        default=None,
        )
