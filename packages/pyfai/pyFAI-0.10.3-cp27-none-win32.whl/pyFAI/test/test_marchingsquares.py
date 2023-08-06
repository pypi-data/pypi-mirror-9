#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Project: Fast Azimuthal Integration
#             https://github.com/pyFAI/pyFAI
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

"test suite for marching_squares / isocontour"

__author__ = "Jérôme Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "15/12/2014"


import unittest
import os
import numpy
import logging, time
import sys
import fabio
if __name__ == '__main__':
    import pkgutil, os
    __path__ = pkgutil.extend_path([os.path.dirname(__file__)], "pyFAI.test")
from .utilstest import UtilsTest, Rwp, getLogger
logger = getLogger(__file__)
pyFAI = sys.modules["pyFAI"]
from pyFAI.marchingsquares import isocontour
if logger.getEffectiveLevel() <= logging.INFO:
    import pylab

class TestMarchingSquares(unittest.TestCase):
    def test_isocontour(self):
            ref = 50
            y, x = numpy.ogrid[-100:100:0.1, -100:100:0.1]
            r = numpy.sqrt(x * x + y * y)

            c = isocontour(r, ref)
            self.assertNotEqual(0, len(c), "controur plot contains not point")
            i = numpy.round(c).astype(numpy.int32)
            self.assert_(abs(r[(i[:, 0], i[:, 1])] - ref).max() < 0.05, "contour plot not working correctly")
            if logger.getEffectiveLevel() <= logging.INFO:
                pylab.imshow(r)
                pylab.plot(c[:, 1], c[:, 0], ",")
                pylab.show()

def test_suite_all_marchingsquares():
    testSuite = unittest.TestSuite()
    testSuite.addTest(TestMarchingSquares("test_isocontour"))

    return testSuite

if __name__ == '__main__':
    mysuite = test_suite_all_marchingsquares()
    runner = unittest.TextTestRunner()
    runner.run(mysuite)
