#!c:\python27\python.exe
# -*- coding: utf-8 -*-
#
#    Project: Azimuthal integration
#             https://github.com/kif/pyFAI
#
#    Copyright (C) European Synchrotron Radiation Facility, Grenoble, France
#
#    Authors: Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
#             V. Aramdo Solé <sole@esrf.fr>
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
drawMask_pymca

Use PyMca module to define a mask
"""

__author__ = "Jerome Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20/03/2015"
__satus__ = "Production"
import os
from pyFAI.gui_utils import QtCore, QtGui
import pyFAI
import pyFAI.utils
try:
    import PyMca
    from PyMca import MaskImageWidget
except ImportError:
    from PyMca5.PyMca import MaskImageWidget
import fabio
import numpy

try:
    from argparse import ArgumentParser
except ImportError:
    from pyFAI.third_party.argparse import ArgumentParser


def main():
    usage = "drawMask_pymca file1.edf file2.edf ..."
    version = "pyFAI-average version %s from %s" % (pyFAI.version, pyFAI.date)
    description = """
    Draw a mask, i.e. an image containing the list of pixels which are considered invalid
    (no scintillator, module gap, beam stop shadow, ...).
    This will open a PyMca window and let you draw on the first image
    (provided) with different tools (brush, rectangle selection, ...).
    When you are finished, come back to the console and press enter.
    """
    epilog = """The mask image is saved into file1-masked.edf.
    Optionally the script will print the number of pixel masked
    and the intensity masked (as well on other files provided in input)"""
    parser = ArgumentParser(usage=usage, description=description, epilog=epilog)
    parser.add_argument("-v", "--version", action='version', version=version)
    parser.add_argument("args", metavar='FILE', type=str, nargs='+',
                        help="Files to be processed")

    options = parser.parse_args()
    if len(options.args) < 1:
        parser.error("Incorrect number of arguments: please provide an image to draw a mask")

    processFile = pyFAI.utils.expand_args(options.args)

    qapp = QtGui.QApplication([])
    w = MaskImageWidget.MaskImageWidget()
    e = fabio.open(processFile[0]).data
    w.setImageData(e)
    w.show()
    outfile = os.path.splitext(processFile[0])[0] + "-mask.edf"
    _ = raw_input("Press enter when you are finished. You mask-file will ba saved into %s%s" % (outfile, os.linesep))
    m = w.getSelectionMask()

    fabio.edfimage.edfimage(data=m).write(outfile)
    print("Selected %i datapoints on file %s" % (m.sum(), processFile[0]))
    for datafile in processFile:
        data = fabio.open(datafile).data[numpy.where(m)]
        print("On File: %s,\t mean= %s \t std= %s" % (datafile, data.mean(), data.std()))

if __name__ == "__main__":
    main()
