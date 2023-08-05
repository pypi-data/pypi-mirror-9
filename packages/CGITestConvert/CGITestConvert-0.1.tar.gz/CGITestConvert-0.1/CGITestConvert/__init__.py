#!/usr/bin/python
"""Converts CGITest Eclipse camera tracking files to Nuke .chan camera files.

## License

The MIT License (MIT)

CGITestConvert
Copyright (c) 2015 Sean Wallitsch
http://github.com/shidarin/CGITestConvert/

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

# =============================================================================
# IMPORTS
# =============================================================================

from argparse import ArgumentParser
import csv
import os

# =============================================================================
# GLOBALS
# =============================================================================

__author__ = "Sean Wallitsch"
__copyright__ = "Copyright 2015, Sean Wallitsch"
__credits__ = ["Sean Wallitsch", ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Sean Wallitsch"
__email__ = "shidarin@alphamatte.com"
__status__ = "Development"

CHAN = "{frame}\t{transX}\t{transY}\t{transZ}\t{rotX}\t{rotY}\t{rotZ}\n"

# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================


def _parse_args():
    """Parses CLI arguments"""
    parser = ArgumentParser()
    parser.add_argument(
        "input_file",
        help="the file to be converted"
    )
    parser.add_argument(
        "-d",
        "--destination",
        help="specify an output directory to save converted files to. If not "
             "provided will default to ./converted/"
    )
    parser.add_argument(
        "-f",
        "--frame",
        help="specify what frame to start the converted chan file on",
        default=1,
        type=int,
    )

    args = parser.parse_args()

    if not args.destination:
        args.destination = './converted/'

    return args

# =============================================================================
# FUNCTIONS
# =============================================================================


def cgitest_read(filename):
    """Reads a csv text file generated from CGITest and returns a dictionary"""
    csv_file = open(filename, 'rb')
    next(csv_file)  # Header
    reader = csv.DictReader(csv_file)

    frames = {}
    for i, values in enumerate(reader):
        frames[i] = values

    csv_file.close()

    return frames


def chan_write(filename, cgitest_dict, start_frame=1):
    """Given a filename and a CGITest dictionary, writes a chan file"""
    filename += '.chan'
    data = []
    for i in range(len(cgitest_dict)):
        frame = cgitest_dict[i]
        data.append(
            CHAN.format(
                frame=i + start_frame,
                transX=frame['vehLongitude'],
                transY=frame['vehAltitude'],
                transZ=frame['vehLatitude'],
                rotX=frame['losEarthX'],
                rotY=frame['losEarthY'],
                rotZ=frame['losEarthZ'],
            )
        )

    with open(filename, 'wb') as f:
        f.writelines(data)


def main():
    args = _parse_args()

    filepath = os.path.abspath(args.input_file)
    filename = '.'.join(os.path.basename(filepath).split('.')[:-1])
    destination_dir = os.path.abspath(args.destination)

    if not os.path.exists(destination_dir):
        print(
            "Destination directory {dir} does not exist.".format(
                dir=destination_dir
            )
        )
        print("Creating destination directory.")
        os.makedirs(destination_dir)

    data = cgitest_read(filepath)

    chan_write(
        os.path.join(destination_dir, filename),
        data,
        start_frame=args.frame
    )
