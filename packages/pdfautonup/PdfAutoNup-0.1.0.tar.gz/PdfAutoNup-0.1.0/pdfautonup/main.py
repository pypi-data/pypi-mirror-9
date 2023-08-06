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

"""Main function for the command."""

from PyPDF2.generic import NameObject, createStringObject
from collections import namedtuple
from fractions import gcd
import PyPDF2
import logging
import os
import sys

from pdfautonup import errors, options, paper
import pdfautonup

LOGGER = logging.getLogger(pdfautonup.__name__)
LOGGER.addHandler(logging.StreamHandler())

def lcm(a, b):
    """Return least common divisor of arguments"""
    # pylint: disable=invalid-name
    return a * b / gcd(a, b)

def dist_to_round(x):
    """Return distance of ``x`` to ``round(x)``."""
    return abs(x - round(x))

class PageIterator:
    """Iterotor over pages of several pdf documents."""
    # pylint: disable=too-few-public-methods

    def __init__(self, files):
        self.files = files

    def __iter__(self):
        for pdf in self.files:
            for num in range(pdf.numPages):
                yield pdf.getPage(num)

    def __len__(self):
        return sum([pdf.numPages for pdf in self.files])

    def repeat_iterator(self, num):
        """Iterator over pages, repeated ``num`` times."""
        for __ignored in range(int(num)):
            yield from self

def _aggregate_metadata(files):
    """Aggregate metadat from input files.
    """
    input_info = [file.getDocumentInfo() for file in files]
    output_info = PyPDF2.pdf.DocumentInformation()

    if len(files) == 1:
        return input_info[0]

    for key in ["/Title", "/Author", "/Keywords", "/Creator", "/Subject"]:
        values = set([
            data[key]
            for data
            in input_info
            if (key in data and data[key])
            ])
        if len(values):
            value = ', '.join(['“{}”'.format(item) for item in values])
            if len(values) != len(files):
                value += ", and maybe others."
            output_info[NameObject(key)] = createStringObject(value)
    return output_info

class DestinationFile:
    """Destination pdf file"""

    #: A target size, associated with the number of source pages that will fit
    #: in it, per width and height (``cell_number[0]`` and ``cell_number[1]``).
    Fit = namedtuple('Fit', ['cell_number', 'target_size'])

    def __init__(self, source_size, target_size, metadata=None, interactive=False):

        self.source_size = source_size
        self.interactive = interactive


        self.cell_number, self.target_size = min(
            self.fit(source_size, target_size),
            self.fit(source_size, (target_size[1], target_size[0])),
            key=self.ugliness,
            )

        self.pdf = PyPDF2.PdfFileWriter()
        self.current_pagenum = 0
        self.current_page = None

        if metadata:
            self._set_metadata(metadata)

    def ugliness(self, fit):
        """Return the "ugliness" of this ``fit``.

        - A layout that fits perfectly has an ugliness of 0.
        - The maximum ugliness is 1.
        """
        target_width, target_height = fit.target_size
        source_width, source_height = self.source_size
        return (
            dist_to_round(target_width / source_width)**2
            +
            dist_to_round(target_height / source_height)**2
            )

    def fit(self, source_size, target_size):
        """Return a :class:`self.Fit` object for arguments.

        The main function is computing the number of source pages per
        destination pages.
        """
        cell_number = (
            max(1, round(target_size[0] / source_size[0])),
            max(1, round(target_size[1] / source_size[1])),
            )
        return self.Fit(cell_number, target_size)

    @property
    def pages_per_page(self):
        """Return the number of source pages per destination page."""
        return self.cell_number[0] * self.cell_number[1]

    def cell_center(self, num):
        """Return the center of ``num``th cell of page."""
        width, height = self.cell_number
        return (
            self.target_size[0] * (num % width) / width,
            self.target_size[1] * (height - 1 - num // width) / height,
            )

    def add_page(self, page):
        """Add ``page`` to the destination file.

        It is added at the right place, and a new blank page is created if
        necessary.
        """
        if self.current_pagenum == 0:
            self.current_page = self.pdf.addBlankPage(
                width=self.target_size[0],
                height=self.target_size[1],
                )
        (x, y) = self.cell_center(self.current_pagenum)
        self.current_page.mergeTranslatedPage(
            page,
            x,
            y,
            )
        self.current_pagenum = (self.current_pagenum + 1) % self.pages_per_page

    def write(self, filename):
        """Write destination file."""
        if self.interactive and os.path.exists(filename):
            question = "File {} already exists. Overwrite (y/[n])? ".format(
                filename
                )
            if input(question).lower() != "y":
                raise errors.UserCancel()
        self.pdf.write(open(filename, 'w+b'))

    def _set_metadata(self, metadata):
        """Set metadata on current pdf."""
        #Source:
        #    http://two.pairlist.net/pipermail/reportlab-users/2009-November/009033.html
        try:
            # pylint: disable=protected-access, no-member
            # Since we are accessing to a protected membre, which can no longer exist
            # in a future version of PyPDF2, we prevent errors.
            infodict = self.pdf._info.getObject()
            infodict.update(metadata)
            infodict.update({
                NameObject('/Producer'): createStringObject(
                    'PdfAutoNup, using the PyPDF2 library — http://TODO'
                    )
            })
        except AttributeError:
            LOGGER.warning("Could not copy metadata from source document.")

def rectangle_size(rectangle):
    """Return the dimension of rectangle (width, height)."""
    return (
        rectangle.upperRight[0] - rectangle.lowerLeft[0],
        rectangle.upperRight[1] - rectangle.lowerLeft[1],
        )

def nup(arguments):
    """Build destination file."""
    input_files = [
        PyPDF2.PdfFileReader(pdf)
        for pdf
        in arguments.files
        ]
    pages = PageIterator(input_files)

    page_sizes = list(zip(*[rectangle_size(page.mediaBox) for page in pages]))
    source_size = (max(page_sizes[0]), max(page_sizes[1]))
    target_size = paper.target_papersize(arguments.target_size)

    dest = DestinationFile(
        source_size,
        target_size,
        interactive=arguments.interactive,
        metadata=_aggregate_metadata(input_files),
        )

    if arguments.repeat == 'auto':
        if len(pages) == 1:
            arguments.repeat = 'fit'
        else:
            arguments.repeat = 1
    if type(arguments.repeat) == int:
        repeat = arguments.repeat
    elif arguments.repeat == 'fit':
        repeat = lcm(dest.pages_per_page, len(pages)) // len(pages)
    for page in pages.repeat_iterator(repeat):
        dest.add_page(page)

    dest.write(options.destination_name(arguments.output, arguments.files[0]))

def main():
    """Main function"""
    arguments = options.commandline_parser().parse_args(sys.argv[1:])

    try:
        nup(arguments)
    except KeyboardInterrupt:
        print()
        sys.exit(1)
    except errors.PdfAutoNupError as error:
        LOGGER.error(error)
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
