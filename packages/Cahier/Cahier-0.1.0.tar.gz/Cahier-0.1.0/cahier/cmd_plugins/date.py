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

"""Date-related options (new, edit, show, attach)."""

import argparse
import datetime
import heapq
import logging
import os
import shlex
import shutil
import subprocess

import cahier

LOGGER = logging.getLogger(__name__)

WEEKDAYS = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
]

def last_items(profile, config, number=1):
    """Return the 'number' last items of 'profile'.

    """
    recent = []
    extension = config['wiki']['extension']
    fileformat = config['wiki']['fileformat']
    for filename in os.listdir(
            cahier.path.absfullpath(profile['directories']['calendar'])
        ):
        if filename.endswith('.' + extension):
            if config.has_option('wiki', 'fileformat-length'):
                length = config['wiki']['fileformat-length']
                stripped_filename = filename[0:int(length)]
            else:
                stripped_filename = filename[:-(len(extension)+1)]
            date = datetime.datetime.strptime(stripped_filename, fileformat)
            heapq.heappush(recent, (date.timestamp(), (date, filename)))
            if number != -1 and len(recent) > number:
                heapq.heappop(recent)

    return [
        (
            os.path.join(
                cahier.path.absfullpath(profile['directories']['calendar']),
                item[1][1],
                ),
            item[1][0]
        )
        for item in [heapq.heappop(recent) for _ in range(len(recent))]
        ]

def make_hour(string):
    """Take an (maybe) incomplete hour, and return an hour matching "%H:%M:%S".

    """
    if string:
        string = ":".join(string)
    else:
        string = "00"
    while string.count(':') < 2:
        string += ":00"
    return string

def next_date(date, workdays, skip):
    """Return the date following date, respecting workdays.

    Arguments:
    - date: start date (return the first one after this one, and after today.
    - workdays: work days, with time.
    - skip: numbers of matching days to skip.
    """
    day = datetime.timedelta(days=1)
    date += day
    if not workdays:
        today = datetime.date.today()
        if (date + datetime.timedelta(days=skip)).date() < today:
            return datetime.date.today()
        else:
            return date + datetime.timedelta(days=skip)
    workdays = dict([
        (day[0], make_hour(day[1:]))
        for day
        in [day.split(':') for day in shlex.split(workdays)]
        ])

    date -= day
    while skip > -1:
        date += day
        skip -= 1
        while WEEKDAYS[date.isoweekday() - 1] not in workdays.keys():
            date += day
    return datetime.datetime.combine(
        date.date(),
        datetime.datetime.strptime(
            workdays[WEEKDAYS[date.isoweekday() - 1]], "%H:%M:%S"
            ).time()
        )

def copy_template(filename, date, config, dry):
    """Copy template for filename.

    If an appropriate template is defined in configuration, copy it as
    'filename', passing 'date' as an argument to string formatting.

    If not, create an empty file as 'filename'.
    """
    if config.has_option('wiki', 'template'):
        if dry:
            LOGGER.info(
                "Copying template {src} to {dst}.\n".format(
                    src=cahier.path.expand(config['wiki']['template'], filename),
                    dst=filename,
                )
                )
        else:
            template = open(
                cahier.path.expand(config['wiki']['template'], filename),
                'r'
                )
            newfile = open(filename, 'a')
            newfile.write(template.read().format(date=date))
            template.close()
            newfile.close()
    else:
        if dry:
            LOGGER.info("Creating empty file {}.\n".format(filename))
        else:
            open(filename, 'a').close()

def attach_file(filename, destination, plugin_directory, dry):
    """Attach file to a calendar entry.

    Arguments:
    - filename: filename to attach;
    - destination: directory in which 'filename' will be copied;
    - plugin_directory: directory of ftplugins, used to (maybe) preprocess
      filename,
    - dry: if set, only print what wourd be done.
    """
    extension = filename.split('.')[-1]
    if extension == filename:
        extension = None

    if extension and os.path.exists(os.path.join(
            plugin_directory,
            "{}.cfg".format(extension)
        )):
        plugin = cahier.config.load_ftplugin(os.path.join(
            plugin_directory,
            "{}.cfg".format(extension),
            ))
        for command in [option
                        for option
                        in plugin.options('preprocess')
                        if option.startswith('cmd')
                       ]:
            command = cahier.path.expand(
                plugin['preprocess'][command],
                filename
                )
            if dry:
                LOGGER.info("Running '{}'.\n".format(command))
            else:
                subprocess.call(command, shell=True)
        filename = cahier.path.expand(
            plugin['preprocess']['name'],
            filename
            )
    basename = os.path.basename(filename)
    if os.path.exists(os.path.join(destination, basename)):
        if 'n' == cahier.io.ask(
                """File {basename} already exist in directory {destination}. Overwrite?""".format( #pylint: disable=line-too-long
                    basename=basename,
                    destination=destination
                    ),
                choices=['y', 'n'],
                default='n',
            ):
            return
    if dry:
        LOGGER.info("Copying {} to {}.\n".format(filename, destination))
    else:
        shutil.copy2(filename, destination)

def run_editnew(command, config, options, profile):
    """Run edit or new command.

    Arguments:
        - command: command line subcommand to run;
        - config: configparer object representing ~/.cahierrc;
        - options: command line options;
        - profile: current profile, as a configparser object.
    """
    items = last_items(profile, config)
    last_filename, last_date = items[0]
    if command == 'edit':
        filename = last_filename
        if options.ask:
            print("\n".join([
                os.path.relpath(
                    items[0][:-len('.mdwn')],
                    cahier.path.absfullpath(profile['directories']['calendar']) #pylint: disable=line-too-long
                    )
                for items
                in last_items(profile, config, -1)
                ]))
            filename = os.path.join(
                os.path.dirname(filename),
                "{}.mdwn".format(cahier.io.ask(
                    "Filename",
                    default=os.path.basename(filename[:-len('.mdwn')])
                    )),
                )
    elif command == 'new':
        newdate = next_date(
            last_date,
            profile['options']['workdays'],
            skip=options.skip,
            )
        if options.ask:
            print("\n".join([
                "{:%Y-%m-%d %H:%M:%S}".format(items[1])
                for items
                in last_items(profile, config, -1)
                ]))
            cahier.io.ask_date('Date', newdate)
        filename = os.path.join(
            cahier.path.absfullpath(
                profile['directories']['calendar']
                ),
            "{}.mdwn".format(
                newdate.strftime(config['wiki']['fileformat'])
                ),
            )
        copy_template(filename, newdate, config, options.dry)
    if options.dry:
        LOGGER.info(
            "Running '{cmd}'.\n".format(
                cmd=cahier.path.expand(config['bin']['editor'], filename)
            )
            )
    else:
        subprocess.call(
            cahier.path.expand(config['bin']['editor'], filename),
            shell=True,
            )

    return 0

def do_new(config, options, profile):
    """Run command "new"."""
    return run_editnew('new', config, options, profile)

def do_edit(config, options, profile):
    """Run command "edit"."""
    return run_editnew('edit', config, options, profile)

def do_show(config, options, profile):
    """Run command "show"."""
    items = last_items(profile, config, options.s)
    print('\n'.join([
        "{0}: {1:%c}".format(*item)
        for item
        in [
            (
                os.path.relpath(
                    item[0],
                    cahier.path.absfullpath(profile['directories']['calendar'])
                ),
                item[1],
            )
            for item
            in items
            ]
        ]))
    return 0

def do_attach(config, options, profile):
    """Run command "attach"."""
    items = last_items(profile, config)
    last_filename = items[0][0]
    if options.ask:
        print("\n".join([
            os.path.relpath(
                items[0][:-len('.mdwn')],
                cahier.path.absfullpath(profile['directories']['calendar']),
                )
            for items
            in last_items(profile, config, -1)
            ]))
        last_filename = os.path.join(
            os.path.dirname(last_filename),
            "{}.mdwn".format(cahier.io.ask(
                "Entry",
                default=os.path.basename(last_filename[:-len('.mdwn')])
                )),
            )
    dirname = last_filename[0:-len('.mdwn')]
    if not os.path.exists(dirname):
        if options.dry:
            LOGGER.info("Creating directory {}.\n".format(dirname))
        else:
            os.mkdir(dirname)
    for filename in options.files:
        attach_file(
            filename,
            dirname,
            os.path.join(cahier.CAHIERRC, "ftplugins"),
            options.dry,
            )
    return 0

def do_rm(config, options, profile):
    """Run command "remove"."""
    items = last_items(profile, config)
    if options.dry:
        LOGGER.info("Removing {}.\n".format(items[0][0]))
    else:
        if (
                options.force
                or ((not options.force) and
                    cahier.io.ask_yesno(
                        'Remove {} ?'.format(os.path.relpath(
                            items[0][0],
                            cahier.path.absfullpath(profile['directories']['calendar']) #pylint: disable=line-too-long
                            )),
                        True,
                        )
                   )
            ):
            os.remove(items[0][0])
    return 0

def load_plugin(subparsers, parent):
    """Load current plugin.

    Add parsers to argument, with appropriate actions to make them effective.

    Arguments:
    - subparsers: object to complete with custom commands;
    - parent: may be None.
    """
    # Common options
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        '-n',
        '--dry-run',
        action='store_true',
        help='Does nothing, but print entry that would be done.',
        dest='dry',
        default=False,
        )

    # Parser for 'new' subcommand
    parser_new = subparsers.add_parser(
        'new',
        help='Add new date item.',
        parents=parent + [common],
        )
    parser_new.set_defaults(function=do_new)
    parser_new.add_argument(
        '-s',
        '--skip',
        metavar='NUMBER',
        action='store',
        type=int,
        help='Number of entries to skip.',
        default=0
        )

    # Parser for 'edit' subcommand
    parser_edit = subparsers.add_parser(
        'edit',
        help='Edit last entry.',
        parents=parent + [common],
        )
    parser_edit.set_defaults(function=do_edit)

    # Parser for 'show' subcommand
    parser_show = subparsers.add_parser(
        'show',
        help='Show last entry.',
        parents=parent + [common],
        )
    parser_show.set_defaults(function=do_show)
    parser_show.add_argument(
        '-s',
        metavar='NUMBER',
        action='store',
        type=int,
        help='Number of entries to show.',
        default=1
        )

    # Parser for 'attach' subcommand
    parser_attach = subparsers.add_parser(
        'attach',
        help='Attach file to current entry.',
        parents=parent + [common],
        )
    parser_attach.set_defaults(function=do_attach)
    parser_attach.add_argument(
        'files',
        nargs='+',
        help="Files to attach to latest date."
        )

    # Parser for 'rm' subcommand
    parser_rm = subparsers.add_parser(
        'rm',
        help='Remove the last entry',
        parents=parent + [common],
        )
    parser_rm.add_argument(
        '-f',
        dest='force',
        action='store_true',
        help='Force deletion.',
        default=False
        )
    parser_rm.set_defaults(function=do_rm)

