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

"""Command plugin management.

Subcommands are defined as plugins, which are submodules of this one. Function
'load_commands()' is called on each modules, to let it add subcommands to the
parser.
"""

import glob
import importlib
import os

def load_commands(subparsers, parent=None):
    """Load all commands."""
    for name in glob.glob(os.path.join(os.path.dirname(__file__), "*.py")):
        if name.endswith(".py") and os.path.basename(name) != "__init__.py":
            plugin = importlib.import_module(
                'cahier.cmd_plugins.{}'.format(os.path.basename(name[:-len('.py')])) #pylint: disable=line-too-long
                )
            plugin.load_plugin(subparsers, parent)
