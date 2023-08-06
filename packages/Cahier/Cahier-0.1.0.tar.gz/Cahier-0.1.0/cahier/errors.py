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

"""Error definition."""

class CahierError(Exception):
    """General exception. Other custom exception should inherit from it."""
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message

class UnknownProfile(CahierError):
    """Profile cannot be found."""

    def __init__(self, profile):
        super().__init__()
        self.profile = profile

    def __str__(self):
        return """No profile named "{profile}".""".format(profile=self.profile)
