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

"""Fonction principale"""

import argparse
import logging
import os
import shlex
import sys

from cahier import errors
import cahier
import cahier.cmd_plugins
import cahier.config
import cahier.io
import cahier.path

LOGGER = logging.getLogger(cahier.__name__)
LOGGER.addHandler(logging.StreamHandler())

def select_profile(option_profile, profiles, confirm, casesensitive=False):
    """Return the selected profile.

    Arguments:
        - option_profile: profile set in command line arguments (None if none
          was given).
        - profiles: dictionary of profiles, as returned by
          cahier.config.load_profiles().
        - confirm (boolean): True iff force user to confirm (unless profile is
          set).
        - casesensitive: is profile chooser case sensitive?
        """
    # Is command line argument profile a valid one?
    if option_profile:
        for item in profiles.keys():
            if option_profile.lower() == item.lower():
                return item
        raise errors.UnknownProfile(option_profile)

    # Looking for matching paths in profile configuration
    cwd = os.path.abspath(os.getcwd())
    match = {}
    for (profile, config) in profiles.items():
        if config.has_option('directories', "sources"):
            for path in shlex.split(config['directories']['sources']):
                fullpath = cahier.path.absfullpath(path)
                if cwd.startswith(fullpath):
                    if profile in match:
                        if len(fullpath) > match[profile]:
                            match[profile] = len(fullpath)
                    else:
                        match[profile] = len(fullpath)
    match = [t[0] for t in sorted(match.items(), key=lambda t: -t[1])]

    # match now contains the list of matching directories. If only one matches,
    # it is the one. Else, user has to choose.
    if len(match) == 0:
        return cahier.io.ask(
            "Select profile",
            choices=profiles.keys(),
            default=None,
            casesensitive=casesensitive,
            )
    elif len(match) == 1:
        if confirm:
            return cahier.io.ask(
                "Select profile",
                choices=profiles.keys(),
                default=match[0],
                casesensitive=casesensitive,
                )
        else:
            return match[0]
    else:
        return cahier.io.ask(
            "Select profile",
            choices=match,
            default=match[0],
            casesensitive=casesensitive,
            )

def commandline_parser():
    """Return an argument parser"""

    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        '-a', '--ask',
        action='store_true',
        help='Force asking profile and filename (if relevant).',
        )
    parent.add_argument(
        '-p', '--profile',
        action='store',
        nargs=1,
        help='Force profile',
        )

    parser = argparse.ArgumentParser(
        description="Manage ikiwiki calendar items.",
        parents=[parent],
        )

    parser.add_argument(
        '--version',
        action='version',
        version=(
            '%(prog)s ' + cahier.VERSION
            )
        )

    cahier.cmd_plugins.load_commands(parser.add_subparsers(), [parent])

    return parser

def main():
    """Main function."""
    try:
        LOGGER.setLevel(logging.INFO)
        options = commandline_parser().parse_args(sys.argv[1:])
        if not hasattr(options, "function"):
            raise errors.CahierError("A subcommand is required.")

        config = cahier.config.load_cahierrc(
            os.path.join(cahier.CAHIERRC, 'cahier.cfg')
            )
        profiles = cahier.config.load_profiles(
            os.path.join(cahier.CAHIERRC, 'profiles')
            )
        if options.profile:
            options.profile = options.profile[0]
        profile = select_profile(
            options.profile,
            profiles,
            options.ask,
            config['options'].getboolean('casesensitive'),
            )

        sys.exit(options.function(config, options, profiles[profile]))
    except errors.CahierError as error:
        LOGGER.error("Error: " + str(error) + "\n")
        sys.exit(1)
    except EOFError:
        sys.exit(0)


if __name__ == "__main__":
    main()

