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

"""Path utils."""

import os

import cahier

def expand(line, filename):
    """Return a line of a configuration file, while processing 'filename'.

    The line is formatted with the following variables:
    - configdir: configuration directory (something liki '~/.cahier');
    - basename: basename of 'filename' (without extension);
    - filename: same, with extension;
    - dirname: directory of 'filename'.
    """
    extension = filename.split('.')[-1]
    if extension == filename:
        extension = ""
    else:
        extension = '.{}'.format(extension)

    return os.path.expandvars(os.path.expanduser(line.format(
        configdir=cahier.CAHIERRC,
        basename=filename[0:-len(extension)],
        filename=filename,
        dirname=absfullpath(os.path.dirname(filename)),
        )))

def absfullpath(path):
    """Return an absolute version of 'path'.

    User directory ('~') and environment variables are replaced by their values.
    """
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

