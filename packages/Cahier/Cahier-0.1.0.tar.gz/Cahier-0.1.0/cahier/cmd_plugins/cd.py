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

"""Launch a shell in calendar directory"""

import os
import shlex
import subprocess

def do_cd(config, __ignored, profile):
    """Run a shell in calendar directory

    Arguments:
        - config: configparer object representing ~/.cahierrc;
        - _: command line options;
        - profile: current profile, as a configparser object.
    """
    if not config.has_option('bin', 'shell'):
        config['bin']['shell'] = '$SHELL'
    command = [
        os.path.expandvars(os.path.expanduser(item))
        for item
        in shlex.split(config['bin']['shell'])
        ]
    process = subprocess.Popen(
        command,
        cwd=os.path.expandvars(os.path.expanduser(
            profile['directories']['calendar']
            )),
        )

    return process.wait()

def load_plugin(subparsers, parent):
    """Load current plugin.

    Add parsers to argument, with appropriate actions to make them effective.

    Arguments:
    - subparsers: object to complete with custom commands;
    - parent: may be None.
    """
    # Parser for 'new' subcommand
    parser_cd = subparsers.add_parser(
        'cd',
        help='Run a shell in calendar directory.',
        parents=parent
        )
    parser_cd.set_defaults(function=do_cd)

