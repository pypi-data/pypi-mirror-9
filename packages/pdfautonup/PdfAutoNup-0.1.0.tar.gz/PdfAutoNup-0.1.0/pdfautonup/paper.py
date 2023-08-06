#!/usr/bin/env python3

# Copyright Louis Paternault 2011-2014
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""Paper-size related functions"""

import os
import papersize
import subprocess

from pdfautonup import errors

def parse_lc_paper(string):
    """Parse LC_PAPER locale variable

    We assume units are milimeters.
    """
    dimensions = {}
    for line in string.split('\n'):
        if line.startswith("width="):
            dimensions["width"] = papersize.parse_length("{}mm".format(line[6:]))
        if line.startswith("height="):
            dimensions["height"] = papersize.parse_length("{}mm".format(line[7:]))
    if len(dimensions) == 2:
        return (dimensions["width"], dimensions["height"])
    raise errors.CouldNotParse(string)

def target_papersize(target_size):
    """Return the target paper size.

    :param str target_size: Target size, if provided by user in command line.
    """
    # pylint: disable=too-many-return-statements

    # Option set by user on command line
    if target_size is not None:
        return papersize.parse_papersize(target_size[0])

    # LC_PAPER environment variable (can be read from "locale -k LC_PAPER"
    try:
        return parse_lc_paper(subprocess.check_output(
            ["locale", "-k", "LC_PAPER"],
            universal_newlines=True,
            ))
    except (subprocess.CalledProcessError, errors.CouldNotParse):
        pass

    # PAPERSIZE environment variable
    try:
        return papersize.parse_papersize(os.environ['PAPERSIZE'].strip())
    except KeyError:
        pass

    # file described by the PAPERCONF environment variable
    try:
        return papersize.parse_papersize(
            open(os.environ['PAPERCONF'], 'r').read().strip()
            )
    except errors.CouldNotParse:
        raise
    except: # pylint: disable=bare-except
        pass

    # content of /etc/papersize
    try:
        return papersize.parse_papersize(open('/etc/papersize', 'r').read().strip())
    except errors.CouldNotParse:
        raise
    except: # pylint: disable=bare-except
        pass

    # stdout of the paperconf command
    try:
        return papersize.parse_papersize(subprocess.check_output(
            ["paperconf"],
            universal_newlines=True,
            ).strip())
    except (subprocess.CalledProcessError, errors.CouldNotParse):
        pass

    # Eventually, if everything else has failed, a4
    return papersize.parse_papersize('a4')
