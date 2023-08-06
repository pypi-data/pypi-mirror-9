#!C:\Python27\python.exe
# -*- coding: utf-8 -*-
#
#    Project: Azimuthal integration
#             https://github.com/kif/pyFAI
#
#    Copyright (C) European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
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
pyFAI-calib

A tool for determining the geometry of a detector using a reference sample.


"""

__author__ = "Jerome Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "29/09/2014"
__satus__ = "development"

import os, sys, logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyFAI.calib")
import pyFAI, pyFAI.calibration
from pyFAI.calibration import Calibration
try:
    from rfoo.utils import rconsole
    rconsole.spawn_server()
except ImportError:
    logging.debug("No socket opened for debugging. Please install rfoo")


# This is for debugging with rconsole
c = None
if __name__ == "__main__":
    c = Calibration()
    c.parse()
    c.read_pixelsSize()
    c.preprocess()
    c.gui_peakPicker()
    raw_input("Press enter to quit")
