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

"""Input/Output utils."""

import datetime

def ask(message, choices=None, default=None, casesensitive=True):
    """Ask for user input, and return it.

    Arguments:
    - message: message to print;
    - default: returned value is no input is given;
    - choices: if not None, keep asking user until input is an item of it;
    - casesensitive: if True, choices argument is case sensitive.
    """
    if choices:
        message += " ({})".format(", ".join(choices))
    else:
        choices = []
    if default:
        print("TAGADA")
        message += " [{default}]".format(
            default=default,
            )
    message += ": "
    if casesensitive:
        lc_choices = {}
    else:
        lc_choices = {s.lower():s for s in choices}
    while True:
        try:
            choice = input(message)
        except EOFError:
            print()
            raise
        if choice == "" and default:
            return default
        if not choices:
            return choice
        if choice in choices:
            return choice
        if (not casesensitive) and (choice in lc_choices):
            return lc_choices[choice]

def ask_date(message, default):
    """Ask for user input, which is expected to be a date.

    This function keeps asking until valid date is provided.

    Arguments:
    - message: message displayed to user;
    - default: default date to return if no input is given.
    """
    message += " (format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS')"
    while True:
        proposition = ask(
            message,
            default=default.strftime("%Y-%m-%d"),
            )
        try:
            date = datetime.datetime.strptime(
                proposition,
                "%Y-%m-%d %H:%M:%S",
                )
            break
        except ValueError:
            try:
                date = datetime.datetime.strptime(
                    proposition,
                    "%Y-%m-%d",
                    )
                break
            except ValueError:
                pass
    return date

def ask_yesno(message, default):
    """Ask for yes or no."""
    if default:
        default = 'yes'
    else:
        default = 'no'

    while True:
        proposition = ask(
            message,
            default=default,
            )
        if 'yes'.startswith(proposition.lower()):
            return True
        if 'no'.startswith(proposition.lower()):
            return False
