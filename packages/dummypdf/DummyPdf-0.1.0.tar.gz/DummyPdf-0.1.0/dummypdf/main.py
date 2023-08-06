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

"""Generate dummy pdf files"""

import argparse
import logging
import papersize
import random
import re
import sys
import textwrap

from dummypdf import VERSION
from dummypdf import errors
from dummypdf.pdf import generate, get_color
import dummypdf

LOGGER = logging.getLogger(dummypdf.__name__)
LOGGER.addHandler(logging.StreamHandler())

def positive_int(arg):
    """Return a positive argument corresponding to ``arg``."""
    try:
        number = int(arg)
    except ValueError:
        raise argparse.ArgumentTypeError(arg)
    if number <= 0:
        raise argparse.ArgumentTypeError(arg)
    return number

def filename(extension=None):
    """Return the filename.

    - If no argument is provided, return the bare file name.
    - If an argument is provided, it is the extension of the file to be
      returned.
    """

    if extension is None:
        return "dummy"
    else:
        return "dummy.{}".format(extension)

def type_papersize(text):
    """Parse 'text' as the argument of --papersize.

    Return a tuple of :class:`decimal.Decimal`.
    """
    try:
        return papersize.parse_papersize(text)
    except papersize.PapersizeException as error:
        raise argparse.ArgumentTypeError(str(error))


def commandline_parser():
    """Return a command line parser."""

    parser = argparse.ArgumentParser(
        description="Generate dummy PDF",
        formatter_class=argparse.RawTextHelpFormatter,
        )

    parser.add_argument(
        '--version',
        help='Show version',
        action='version',
        version='%(prog)s ' + VERSION
        )

    parser.add_argument(
        '--file', '-f',
        default=filename('pdf'),
        help=(
            'Destination file. Default is "dummy.pdf".'
            ),
        type=str,
        )

    parser.add_argument(
        '--number', '-n',
        help="Number of pages.",
        default=1,
        type=positive_int,
        )

    parser.add_argument(
        '--orientation', '-o',
        help="Paper orientation. Default depends on the paper size.",
        default=None,
        choices=["portrait", "landscape"],
        )

    parser.add_argument(
        '--start', '-s',
        help="Number of first page.",
        default=1,
        type=int,
        )

    parser.add_argument(
        '--papersize', '-p',
        default="a4",
        type=type_papersize,
        help=textwrap.dedent("""
        Paper size, as either a named size (e.g. "A4" or "letter"), or a couple
        of lengths (e.g. "21cmx29.7cm" or "7in 8in"…). Default value is A4.
        """),
        )

    parser.add_argument(
        '--color', '-c',
        default='deterministic',
        help=textwrap.dedent("""
        Color to use. Can be:

        - deterministic (default): a random color is used, but calls to
          dummypdf using the same arguments give the same color (note that
          calls with different version of this program may lead to different
          colors used).
        - random: a random color is used (different on each call).
        - RED,GREEN,BLUE: a RGB color, where RED, GREEN and BLUE are integers
          between 0 and 255.
        - named colors: {colors}.
        """.format(
            colors=", ".join(str(color) for color in get_color()),
            )),
        )

    return parser

def process_options(options):
    "Return processed options (might catch errors unnoticed by :mod:`argparse`."
    processed = {}

    processed['first'] = options.start
    processed['orientation'] = options.orientation
    processed['last'] = options.start + options.number - 1
    processed['file'] = options.file

    if options.papersize is None:
        pass
    else:
        processed['paperformat'] = options.papersize

    color_re = re.compile(r'(?P<red>\w+),(?P<green>\w+),(?P<blue>\w+)')
    if options.color.lower() in ['deterministic', 'random']:
        if options.color.lower() == 'deterministic':
            random.seed("-".join(str(item) for item in [
                processed['first'],
                processed['last'],
                options.papersize,
                ]))
        processed['color'] = [
            random.randint(64, 255),
            random.randint(0, 191),
            random.randint(0, 255),
            ]
        random.shuffle(processed['color'])
    elif color_re.match(options.color):
        processed['color'] = [int(color) for color in color_re.match(options.color).groups()]
        for color in processed['color']:
            if color > 255:
                raise errors.ArgumentError(
                    "Option '--color' must be an integer between 0 and 255."
                    )
    else:
        processed['color'] = get_color(options.color)

    return processed

def main():
    """Main function"""

    try:
        options = process_options(commandline_parser().parse_args(sys.argv[1:]))
        generate(
            name=options["file"],
            first=options["first"],
            last=options["last"],
            color=options["color"],
            paperformat=options["paperformat"],
            )

    except errors.DummyPdfError as error:
        LOGGER.error(error)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    main()
