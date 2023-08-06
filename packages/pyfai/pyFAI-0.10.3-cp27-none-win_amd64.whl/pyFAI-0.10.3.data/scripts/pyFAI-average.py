#!C:\Python27\python.exe
# -*- coding: utf-8 -*-
#
#    Project: Fast Azimuthal integration
#             https://github.com/kif/pyFAI
#
#
#    Copyright (C) European Synchrotron Radiation Facility, Grenoble, France
#
#    Authors: Jérôme Kieffer <Jerome.Kieffer@ESRF.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
pyFAI-average is a small utility that averages out a serie of files,
for example for dark, or flat or calibration images
"""
__author__ = "Jerome Kieffer, Picca Frédéric-Emmanuel"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20/03/2015"
__status__ = "production"

import os
import sys
import fabio
import logging
import pyFAI
import pyFAI.utils
try:
    from argparse import ArgumentParser
except ImportError:
    from pyFAI.third_party.argparse import ArgumentParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("average")

def main():
    usage = "pyFAI-average [options] [options] -o output.edf file1.edf file2.edf ..."
    version = "pyFAI-average version %s from %s" % (pyFAI.version, pyFAI.date)
    description = """
    This tool can be used to average out a set of dark current images using
    mean or median filter (along the image stack). One can also reject outliers
    be specifying a cutoff (remove cosmic rays / zingers from dark)
    """
    epilog = """It can also be used to merge many images from the same sample when using a small beam
    and reduce the spotty-ness of Debye-Sherrer rings. In this case the "max-filter" is usually
    recommended.
    """
    parser = ArgumentParser(usage=usage, description=description, epilog=epilog)
    parser.add_argument("-V", "--version", action='version', version=version)
    parser.add_argument("-o", "--output", dest="output",
                      type=str, default=None,
                      help="Output/ destination of average image")
    parser.add_argument("-m", "--method", dest="method",
                      type=str, default="mean",
                      help="Method used for averaging, can be 'mean'(default) or 'median', 'min' or 'max'")
    parser.add_argument("-c", "--cutoff", dest="cutoff", type=float, default=None,
                  help="Take the mean of the average +/- cutoff * std_dev.")
    parser.add_argument("-F", "--format", dest="format", type=str, default="edf",
                  help="Output file/image format (by default EDF)")
    parser.add_argument("-d", "--dark", dest="dark", type=str, default=None,
                  help="Dark noise to be subtracted")
    parser.add_argument("-f", "--flat", dest="flat", type=str, default=None,
                  help="Flat field correction")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="switch to verbose/debug mode")
    parser.add_argument("args", metavar='FILE', type=str, nargs='+',
                        help="Files to be processed")

    options = parser.parse_args()

    # Analyse aruments and options
    images = pyFAI.utils.expand_args(options.args)

    if options.verbose:
        pyFAI.utils.logger.setLevel(logging.DEBUG)
    else:
        pyFAI.utils.logger.setLevel(logging.INFO)
    if  options.output:
        output = options.output
    else:
        output = "%s_%s" % (os.path.commonprefix(images), options.method)
        if options.cutoff:
            output += "_cutoff_%s_std" % options.cutoff
        output += "_%s_frames.%s" % (len(images), options.format)
    if options.flat:
        flats = pyFAI.utils.expand_args([options.flat])
    else:
        flats = None
    if options.dark:
        darks = pyFAI.utils.expand_args([options.dark])
    else:
        darks = None

    if images:
        dataout = pyFAI.utils.averageImages(images, filter_=options.method, cutoff=options.cutoff,
                                            threshold=0, format=options.format, output=output,
                                            flats=flats, darks=darks)
        return dataout

if __name__ == "__main__":
    main()
