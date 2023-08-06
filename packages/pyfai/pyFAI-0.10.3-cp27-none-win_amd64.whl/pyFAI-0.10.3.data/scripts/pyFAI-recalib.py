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
pyFAI - recalib

A tool for refining the geometry of a detector using a reference sample and a previously known calibration file.


"""

__author__ = "Jerome Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "29/09/2014"
__satus__ = "development"

import os, sys, gc, threading, time, logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyFAI.recalib")
import pyFAI, pyFAI.calibration
from pyFAI.calibration import Recalibration
try:
    from rfoo.utils import rconsole
    rconsole.spawn_server()
except ImportError:
    logging.debug("No socket opened for debugging -> install rfoo")


# This is for debugging with rconsole
c = None
if __name__ == "__main__":
    c = Recalibration()
    c.parse()
    c.preprocess()
    c.extract_cpt("blob")
    c.refine()
    c.postProcess()
    if c.interactive:
        raw_input("Press enter to quit")
