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

"""Management of configuration files."""

import configparser
import os
import shlex

from cahier import errors

class ConfigurationError(errors.CahierError):
    """Error in configuration files."""
    def __init__(self, filename, message):
        super(ConfigurationError, self).__init__()
        self.filename = filename
        self.message = message

    def __str__(self):
        return "Configuration error ({filename}): {message}".format(
            filename=self.filename,
            message=self.message,
            )

def config_assert_has(config, name, section, option):
    """Assert that 'config' as 'section' defined, with 'option' key in it.

    Raise a ConfigurationError() if not.
    """
    if not config.has_section(section):
        raise ConfigurationError(
            filename=name,
            message=(
                "Missing section {section} in file {filename}."
                ).format(section=section, filename=name),
            )
    if option and (not config.has_option(section, option)):
        raise ConfigurationError(
            filename=name,
            message=(
                "Missing key {key} in section {section} in file {filename}."
                ).format(key=option, section=section, filename=name)
            )

def load_cahierrc(filename):
    """Load ~/.cahier/cahier.cfg, and return it as a configparser object."""
    config = configparser.ConfigParser()
    config.read_dict({
        'options': {
            'casesensitive': "True",
            },
        'bin': {
            'editor': "$EDITOR",
            },
        'wiki': {
            'extension': "mdwn",
            },
        })
    config.read([filename])
    if config.has_section('wiki'):
        if 'fileformat' not in config['wiki'].keys():
            raise ConfigurationError(
                filename=filename,
                message="missing key 'fileformat' in section 'wiki'.",
                )
    else:
        raise ConfigurationError(
            filename=filename,
            message="missing section 'wiki'.",
            )
    return config

def load_ftplugin(filename):
    """Load ftplugin.

    Return plugin 'filename' as a configparser object.
    """
    # Reading file
    config = configparser.ConfigParser()
    config.read_dict({
        'preprocess': {},
        })
    config.read([filename])

    # Checking arguments
    for key in config['preprocess']:
        if key == 'name' or key.startswith('cmd'):
            continue
        raise ConfigurationError(
            filename=filename,
            message=(
                """"{key}" key (in section {section}) must """
                """be 'name' or start with 'cmd'."""
                ).format(key=key, section="preprocess")
            )

    return config

def load_profiles(dirname):
    """Load profiles of directory 'dirname'.

    Return a dictionary of profiles, as configparser objects indexed by
    basenames.
    """
    profiles = {}
    for root, __ignored, files in os.walk(dirname):
        for filename in files:
            if filename.endswith('.cfg'):
                # Preprocessing
                basename = filename[:-len('.cfg')]
                fullname = os.path.join(root, filename)

                # Reading configuration
                config = configparser.ConfigParser()
                config.read_dict({
                    'options': {
                        'workdays': "",
                        },
                    })
                config.read([fullname])

                # Checking for compulsory arguments
                config_assert_has(config, fullname, 'directories', 'calendar')
                config_assert_has(config, fullname, 'config', 'setup')
                workdays = shlex.split(config['options']['workdays'])
                if len(workdays) != len(set([
                        day.split(':')[0]
                        for day
                        in workdays
                    ])):
                    raise ConfigurationError(
                        fullname,
                        (
                            "Only one item by day is allowed in "
                            "key 'workdays' of section 'options'."
                        ),
                        )

                profiles[basename] = config
    return profiles

