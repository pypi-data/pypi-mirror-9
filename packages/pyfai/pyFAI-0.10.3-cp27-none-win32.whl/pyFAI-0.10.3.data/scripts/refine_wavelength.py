#!c:\python27\python.exe
# -*- coding: utf-8 -*-
#
#    Project: Azimuthal integration 
#             https://github.com/kif/pyFAI
#
#    File: "$Id$"
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

__author__ = "Jérôme Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "12/07/2011"
__doc__ = """
Refine the wavelength from a set of images taken with various geometries.
For numerical efficiency, the wavelength has to be in ANGSTROM

Usage:
    $ refine_wavelength -w=1.54 poni1 poni2 poni3 poni4
"""
import sys, os, logging
import numpy
from numpy import sin, arcsin
from scipy.optimize import fmin_slsqp
from pyFAI.geometryRefinement import GeometryRefinement

class RefineWavelength(object):
    def __init__(self, wavelength, listFiles=None):
        self.wavelength_init = wavelength
        self.wavelength = wavelength
        self.listFiles = []
        self.listPoni = []
        self.listPoints = []
        self.listRefiner = []
        self.bounds = []
        self.param = []
        if listFiles:
            for oneFile in listFiles:
                self.addFile(oneFile)
        self.param.append(wavelength)
        self.bounds.append((0.9 * wavelength, 1.1 * wavelength))
        self.nbImg = len(self.listPoni)


    def __repr__(self):
        lstTxt = [ "%s\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f\t%6.3f" % (j, i.dist, i.poni1, i.poni2, i.rot1, i.rot2, i.rot3) for i, j in zip(self.listRefiner, self.listFiles)]
        lstTxt.append("Wavelength: %s" % self.wavelength)
        return os.linesep.join(lstTxt)


    def addFile(self, filename):
        if filename in self.listFiles:
            return
        basename = os.path.splitext(filename)[0]
        if filename.endswith(".poni") and os.path.isfile(basename + ".py"):
            poni = filename
            pointFile = basename + ".py"
        elif filename.endswith(".py") and os.path.isfile(basename + ".poni"):
            poni = filename
            pointFile = basename + ".py"
        try:
            points = eval(open(pointFile).read().replace("data=", ""))
        except:
            logging.error("error in reading %s" % pointFile)
            return
        refinement = GeometryRefinement(points)
        refinement.load(poni)
#        print refinement
        self.listPoints.append(numpy.array(points).astype("float64"))
        self.listPoni.append(refinement.param)

        refinement.dist_min = 0.5 * refinement.dist
        refinement.dist_max = 2 * refinement.dist
        refinement.poni1_min = min(0.9 * refinement.poni1, 1.1 * refinement.poni1)
        refinement.poni1_max = max(0.9 * refinement.poni1, 1.1 * refinement.poni1)
        refinement.poni2_min = min(0.9 * refinement.poni2, 1.1 * refinement.poni2)
        refinement.poni2_max = max(0.9 * refinement.poni2, 1.1 * refinement.poni2)
        refinement.rot1_min = min(0.9 * refinement.rot1, 1.1 * refinement.rot1)
        refinement.rot1_max = max(0.9 * refinement.rot1, 1.1 * refinement.rot1)
        refinement.rot2_min = min(0.9 * refinement.rot2, 1.1 * refinement.rot2)
        refinement.rot2_max = max(0.9 * refinement.rot2, 1.1 * refinement.rot2)
        refinement.rot3_min = min(0.9 * refinement.rot3, 1.1 * refinement.rot3)
        refinement.rot3_max = max(0.9 * refinement.rot3, 1.1 * refinement.rot3)
        self.listRefiner.append(refinement)
        self.listFiles.append(poni)
#        self.listFiles.append(pointFile)
        self.param += refinement.param
        self.bounds += [(refinement.dist_min, refinement.dist_max),
                        (refinement.poni1_min, refinement.poni1_max),
                        (refinement.poni2_min, refinement.poni2_max),
                        (refinement.rot1_min, refinement.rot1_max),
                        (refinement.rot2_min, refinement.rot2_max),
                        (refinement.rot3_min, refinement.rot3_max)]

    def residu1(self, param):
        res = []
        for i, ref in enumerate(self.listRefiner):
            points = self.listPoints[i]
            d1 = points[:, 0]
            d2 = points[:, 1]
            tth = 2 * arcsin(param[-1] * sin(points[:, 2] / 2.0) / self.wavelength_init)
            res.append(ref.tth(d1, d2, param[i * 6: (i + 1) * 6]) - tth)
        return numpy.concatenate(tuple(res))

    def residu2(self, param):
        return (self.residu1(param) ** 2).sum()

    def chi2(self, param=None):
        if param is not None:
            return self.residu2(param)
        else:
            return self.residu2(self.param)
#        sum = 0.0
#        for oneRef in self.listRefiner:
#            sum += oneRef.chi2()
#        return sum


    def refine2(self, maxiter=1000):
        param = []
        for i in self.listRefiner:
            param.append(i.param)
        param.append([self.wavelength])
        self.param = numpy.concatenate(tuple(param)).astype("float64")
        newParam = fmin_slsqp(self.residu2, self.param, iter=maxiter,
                              bounds=self.bounds, iprint=2,
                              acc=1.0e-12)
        print newParam
        print "Constrained Least square", self.chi2(), "--> ", self.chi2(newParam)
        if self.chi2(newParam) < self.chi2():
            i = abs(self.param - newParam).argmax()
            print "maxdelta on: ", i, self.param[i], "-->", newParam[i]
            self.param = newParam
            self.wavelength = newParam[-1]
            for i, ref in enumerate(self.listRefiner):
                ref.param = newParam[6 * i:6 * (i + 1) ]
                ref.dist = newParam[6 * i]
                ref.poni1 = newParam[6 * i + 1]
                ref.poni2 = newParam[6 * i + 2]
                ref.rot1 = newParam[6 * i + 3]
                ref.rot2 = newParam[6 * i + 4]
                ref.rot3 = newParam[6 * i + 5]

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print __doc__
        sys.exit(1)
    wavelength = None
    listFiles = []
    for arg in sys.argv[1:]:
        if arg.find("-h") in [0, 1]:
            print(__doc__)
            sys.exit(0)
        elif arg.find("-w=") in [0, 1]:
            wavelength = float(arg.split("=")[1])
        elif os.path.isfile(arg):
            listFiles.append(arg)
    if wavelength is None:
        wavelength = raw_input("WaveLength (A) ? ")
    refinement = RefineWavelength(wavelength, listFiles)
    print refinement
    last = refinement.chi2() + 1
#    print last - 1
    while refinement.chi2() < last:
        last = refinement.chi2()
        refinement.refine2()
        print refinement



