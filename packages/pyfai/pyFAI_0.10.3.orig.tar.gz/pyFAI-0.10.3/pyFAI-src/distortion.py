# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Project: Azimuthal integration
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
from __future__ import absolute_import, print_function, division, with_statement

__author__ = "Jérôme Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20/03/2015"
__status__ = "development"

import logging, threading
import os, sys
import numpy
logger = logging.getLogger("pyFAI.distortion")
logging.basicConfig(level=logging.INFO)
from math import ceil, floor
from . import detectors
from .opencl import ocl
if ocl:
    from . import ocl_azim_lut, ocl_azim_csr
else:
    ocl_azim_lut = ocl_azim_csr = None
from .utils import timeit
from .third_party import six
import fabio

try:
    from . import _distortion
except ImportError:
    logger.warning("Import _distortion cython implementation failed ... pure python version is terribly slow !!!")
    _distortion = None


class Distortion(object):
    """
    This class applies a distortion correction on an image.

    New version compatible both with CSR and LUT...
    """
    def __init__(self, detector="detector", shape=None, method="LUT", device=None, workgroup=8):
        """
        @param detector: detector instance or detector name
        @param shape: shape of the output image
        @param method: "lut" or "csr", the former is faster
        @param device: Name of the device: None for OpenMP, "cpu" or "gpu" or the id of the OpenCL device a 2-tuple of integer
        @param workgroup: workgroup size for CSR on OpenCL
        """
        if isinstance(detector, six.string_types):
            self.detector = detectors.detector_factory(detector)
        else:  # we assume it is a Detector instance
            self.detector = detector
        if "shape" in dir(self.detector):
            self.shape = self.detector.shape
            if shape is not None and self.shape != shape:
                logger.warning("unconsistency in detector geometry, got %s and expected %s" % (shape, self.shape))
                self.shape = shape
        else:
            self.shape = shape
        self.shape = tuple([int(i) for i in self.shape])
        self._sem = threading.Semaphore()

        self.bin_size = None
        self.max_size = None
        self.pos = None
        self.lut = None
        self.delta0 = self.delta1 = None  # max size of an pixel on a regular grid ...
        self.integrator = None
        if not method:
            self.method = "lut"
        else:
            self.method = method.lower()
        self.device = device
        if not workgroup:
            self.workgroup = 8
        else:
            self.workgroup = int(workgroup)

    def __repr__(self):
        return os.linesep.join(["Distortion correction %s on device %s for detector shape %s:" % (self.method, self.device, self.shape),
                                self.detector.__repr__()])

    def reset(self, method=None, device=None, workgroup=None):
        """
        reset the distortion correction and re-calculate the look-up table

        @param method: can be "lut" or "csr", "lut" looks faster
        @param device: can be None, "cpu" or "gpu" or the id as a 2-tuple of integer
        @param worgroup: enforce the workgroup size for CSR.
        """
        with self._sem:
            self.max_size = None
            self.pos = None
            self.lut = None
            self.delta0 = self.delta1 = None
            self.integrator = None
            if method is not None:
                self.method = method.lower()
            if device is not None:
                self.device = device
            if workgroup is not None:
                self.workgroup = int(workgroup)

        self.calc_init()

    @timeit
    def calc_pos(self):
        if self.delta1 is None:
            with self._sem:
                if self.delta1 is None:
                    pos_corners = numpy.empty((self.shape[0] + 1, self.shape[1] + 1, 2), dtype=numpy.float64)
                    d1 = numpy.outer(numpy.arange(self.shape[0] + 1, dtype=numpy.float64), numpy.ones(self.shape[1] + 1, dtype=numpy.float64)) - 0.5
                    d2 = numpy.outer(numpy.ones(self.shape[0] + 1, dtype=numpy.float64), numpy.arange(self.shape[1] + 1, dtype=numpy.float64)) - 0.5
                    pos_corners[:, :, 0], pos_corners[:, :, 1] = self.detector.calc_cartesian_positions(d1, d2)
                    pos_corners[:, :, 0] /= self.detector.pixel1
                    pos_corners[:, :, 1] /= self.detector.pixel2
                    pos = numpy.empty((self.shape[0], self.shape[1], 4, 2), dtype=numpy.float32)
                    pos[:, :, 0, :] = pos_corners[:-1, :-1]
                    pos[:, :, 1, :] = pos_corners[:-1, 1: ]
                    pos[:, :, 2, :] = pos_corners[1: , 1: ]
                    pos[:, :, 3, :] = pos_corners[1: , :-1]
                    self.pos = pos
                    self.delta0 = int((numpy.ceil(pos_corners[1:, :, 0]) - numpy.floor(pos_corners[:-1, :, 0])).max())
                    self.delta1 = int((numpy.ceil(pos_corners[:, 1:, 1]) - numpy.floor(pos_corners[:, :-1, 1])).max())
        return self.pos

    @timeit
    def calc_size(self):
        """
        Considering the "half-CCD" spline from ID11 which describes a (1025,2048) detector,
        the physical location of pixels should go from:
        [-17.48634 : 1027.0543, -22.768829 : 2028.3689]
        We chose to discard pixels falling outside the [0:1025,0:2048] range with a lose of intensity

        """
        if self.pos is None:
            pos = self.calc_pos()
        else:
            pos = self.pos
        if self.max_size is None:
            with self._sem:
                if self.max_size is None:
                    if _distortion:
                        self.bin_size = _distortion.calc_size(self.pos, self.shape)
                    else:
                        pos0min = numpy.floor(pos[:, :, :, 0].min(axis=-1)).astype(numpy.int32).clip(0, self.shape[0])
                        pos1min = numpy.floor(pos[:, :, :, 1].min(axis=-1)).astype(numpy.int32).clip(0, self.shape[1])
                        pos0max = (numpy.ceil(pos[:, :, :, 0].max(axis=-1)).astype(numpy.int32) + 1).clip(0, self.shape[0])
                        pos1max = (numpy.ceil(pos[:, :, :, 1].max(axis=-1)).astype(numpy.int32) + 1).clip(0, self.shape[1])
                        self.bin_size = numpy.zeros(self.shape, dtype=numpy.int32)
                        max0 = 0
                        max1 = 0
                        for i in range(self.shape[0]):
                            for j in range(self.shape[1]):
                                if (pos0max[i, j] - pos0min[i, j]) > max0:
                                    old = max0
                                    max0 = pos0max[i, j] - pos0min[i, j]
                                    print(old, "new max0", max0, i, j)
                                if (pos1max[i, j] - pos1min[i, j]) > max1:
                                    old = max1
                                    max1 = pos1max[i, j] - pos1min[i, j]
                                    print(old, "new max1", max1, i, j)

                                self.bin_size[pos0min[i, j]:pos0max[i, j], pos1min[i, j]:pos1max[i, j]] += 1
                    self.max_size = self.bin_size.max()

    def calc_init(self):
        """
        initialize all arrays
        """
        self.calc_pos()
        self.calc_size()
        self.calc_LUT()
        if ocl and self.device is not None:
            if "lower" in dir(self.device):
                self.device = self.device.lower()
                if self.method == "lut":
                    self.integrator = ocl_azim_lut.OCL_LUT_Integrator(self.lut, self.shape[0] * self.shape[1], devicetype=self.device)
                else:
                    self.integrator = ocl_azim_csr.OCL_CSR_Integrator(self.lut, self.shape[0] * self.shape[1], devicetype=self.device,
                                                                      block_size=self.workgroup)
            else:
                if self.method == "lut":
                    self.integrator = ocl_azim_lut.OCL_LUT_Integrator(self.lut, self.shape[0] * self.shape[1],
                                                                platformid=self.device[0], deviceid=self.device[1])
                else:
                    self.integrator = ocl_azim_csr.OCL_CSR_Integrator(self.lut, self.shape[0] * self.shape[1],
                                                                platformid=self.device[0], deviceid=self.device[1],
                                                                block_size=self.workgroup)

    @timeit
    def calc_LUT(self):
        if self.max_size is None:
            self.calc_size()
        if self.lut is None:
            with self._sem:
                if self.lut is None:
                    if _distortion:
                        if self.method == "lut":
                            self.lut = _distortion.calc_LUT(self.pos, self.shape, self.bin_size, max_pixel_size=(self.delta0, self.delta1))
                        else:
                            self.lut = _distortion.calc_CSR(self.pos, self.shape, self.bin_size, max_pixel_size=(self.delta0, self.delta1))
                    else:
                        lut = numpy.recarray(shape=(self.shape[0] , self.shape[1], self.max_size), dtype=[("idx", numpy.uint32), ("coef", numpy.float32)])
                        lut[:, :, :].idx = 0
                        lut[:, :, :].coef = 0.0
                        outMax = numpy.zeros(self.shape, dtype=numpy.uint32)
                        idx = 0
                        buffer = numpy.empty((self.delta0, self.delta1))
                        quad = Quad(buffer)
                        for i in range(self.shape[0]):
                            for j in range(self.shape[1]):
                                # i,j, idx are indexes of the raw image uncorrected
                                quad.reinit(*list(self.pos[i, j, :, :].ravel()))
                                # print(self.pos[i, j, 0, :], self.pos[i, j, 1, :], self.pos[i, j, 2, :], self.pos[i, j, 3, :]
                                try:
                                    quad.populate_box()
                                except Exception as error:
                                    print("error in quad.populate_box of pixel %i, %i: %s" % (i, j, error))
                                    print("calc_area_vectorial", quad.calc_area_vectorial())
                                    print(self.pos[i, j, 0, :], self.pos[i, j, 1, :], self.pos[i, j, 2, :], self.pos[i, j, 3, :])
                                    print(quad)
                                    raise
                #                box = quad.get_box()
                                for ms in range(quad.get_box_size0()):
                                    ml = ms + quad.get_offset0()
                                    if ml < 0 or ml >= self.shape[0]:
                                        continue
                                    for ns in range(quad.get_box_size1()):
                                        # ms,ns are indexes of the corrected image in short form, ml & nl are the same
                                        nl = ns + quad.get_offset1()
                                        if nl < 0 or nl >= self.shape[1]:
                                            continue
                                        val = quad.get_box(ms, ns)
                                        if val <= 0:
                #                            print("Val ", val, i, j, idx, ms, ns, ml, nl
                                            continue
                                        k = outMax[ml, nl]
                                        lut[ml, nl, k].idx = idx
                                        lut[ml, nl, k].coef = val
                                        outMax[ml, nl] = k + 1
                                idx += 1
                        lut.shape = (self.shape[0] * self.shape[1]), self.max_size
                        self.lut = lut

    def correct(self, image):
        """
        Correct an image based on the look-up table calculated ...

        @param image: 2D-array with the image
        @return: corrected 2D image
        """
        if self.device:
            if self.integrator is None:
                self.calc_init()
            out = self.integrator.integrate(image)[1]
        else:
            if self.lut is None:
                self.calc_LUT()
            if self.method == "lut":
                if _distortion is not None:
                    out = _distortion.correct_LUT(image, self.shape, self.lut)
                else:
                    big = image.ravel().take(self.lut.idx) * self.lut.coef
                    out = big.sum(axis=-1)
            elif self.method == "csr":
                if _distortion is not None:
                    out = _distortion.correct_CSR(image, self.shape, self.lut)
                else:
                    big = self.lut[0] * image.ravel().take(self.lut[1])
                    indptr = self.lut[2]
                    out = numpy.zeros(indptr.size - 1)
                    for i in range(indptr.size - 1):
                        out[i] = big[indptr[i]:indptr[i + 1]].sum()
        out.shape = self.shape
        return out

    def uncorrect(self, image):
        """
        Take an image which has been corrected and transform it into it's raw (with loss of information)

        @param image: 2D-array with the image
        @return: uncorrected 2D image and a mask (pixels in raw image
        """
        if self.lut is None:
            self.calc_LUT()
        if self.method == "lut":
            if _distortion is not None:
                out, mask = _distortion.uncorrect_LUT(image, self.shape, self.lut)
            else:
                out = numpy.zeros(self.shape, dtype=numpy.float32)
                mask = numpy.zeros(self.shape, dtype=numpy.int8)
                lmask = mask.ravel()
                lout = out.ravel()
                lin = image.ravel()
                tot = self.lut.coef.sum(axis=-1)
                for idx in range(self.lut.shape[0]):
                    t = tot[idx]
                    if t <= 0:
                        lmask[idx] = 1
                        continue
                    val = lin[idx] / t
                    lout[self.lut[idx].idx] += val * self.lut[idx].coef
        elif self.method == "csr":
            if _distortion is not None:
                out = _distortion.uncorrect_CSR(image, self.shape, self.lut)
            else:
                raise NotImplementedError()
        return out, mask


class Quad(object):
    """

                                     |
                                     |
                                     |                       xxxxxA
                                     |      xxxxxxxI'xxxxxxxx     x
                             xxxxxxxxIxxxxxx       |               x
                Bxxxxxxxxxxxx        |             |               x
                x                    |             |               x
                x                    |             |               x
                 x                   |             |                x
                 x                   |             |                x
                 x                   |             |                x
                 x                   |             |                x
                 x                   |             |                x
                  x                  |             |                 x
                  x                  |             |                 x
                  x                  |             |                 x
                  x                 O|             P              A'  x
 -----------------J------------------+--------------------------------L-----------------------
                  x                  |                                 x
                  x                  |                                  x
                  x                  |                                  x
                   x                 |     xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxD
                   CxxxxxxxxxxxxxxxxxKxxxxx
                                     |
                                     |
                                     |
                                     |
        """
    def __init__(self, buffer):
        self.box = buffer
        self.A0 = self.A1 = None
        self.B0 = self.B1 = None
        self.C0 = self.C1 = None
        self.D0 = self.D1 = None
        self.offset0 = self.offset1 = None
        self.box_size0 = self.box_size1 = None
        self.pAB = self.pBC = self.pCD = self.pDA = None
        self.cAB = self.cBC = self.cCD = self.cDA = None
        self.area = None

    def get_idx(self, i, j):
        pass
    def get_box(self, i, j):
        return self.box[i, j]
    def get_offset0(self):
        return self.offset0
    def get_offset1(self):
        return self.offset1
    def get_box_size0(self):
        return self.box_size0
    def get_box_size1(self):
        return self.box_size1

    def reinit(self, A0, A1, B0, B1, C0, C1, D0, D1):
        self.box[:, :] = 0.0
        self.A0 = A0
        self.A1 = A1
        self.B0 = B0
        self.B1 = B1
        self.C0 = C0
        self.C1 = C1
        self.D0 = D0
        self.D1 = D1
        self.offset0 = int(floor(min(self.A0, self.B0, self.C0, self.D0)))
        self.offset1 = int(floor(min(self.A1, self.B1, self.C1, self.D1)))
        self.box_size0 = int(ceil(max(self.A0, self.B0, self.C0, self.D0))) - self.offset0
        self.box_size1 = int(ceil(max(self.A1, self.B1, self.C1, self.D1))) - self.offset1
        self.A0 -= self.offset0
        self.A1 -= self.offset1
        self.B0 -= self.offset0
        self.B1 -= self.offset1
        self.C0 -= self.offset0
        self.C1 -= self.offset1
        self.D0 -= self.offset0
        self.D1 -= self.offset1
        self.pAB = self.pBC = self.pCD = self.pDA = None
        self.cAB = self.cBC = self.cCD = self.cDA = None
        self.area = None

    def __repr__(self):
        return os.linesep.join(["offset %i,%i size %i, %i" % (self.offset0, self.offset1, self.box_size0, self.box_size1), "box: %s" % self.box[:self.box_size0, :self.box_size1]])

    def init_slope(self):
        if self.pAB is None:
            if self.B0 == self.A0:
                self.pAB = numpy.inf
            else:
                self.pAB = (self.B1 - self.A1) / (self.B0 - self.A0)
            if self.C0 == self.B0:
                self.pBC = numpy.inf
            else:
                 self.pBC = (self.C1 - self.B1) / (self.C0 - self.B0)
            if self.D0 == self.C0:
                self.pCD = numpy.inf
            else:
                self.pCD = (self.D1 - self.C1) / (self.D0 - self.C0)
            if self.A0 == self.D0:
                self.pDA = numpy.inf
            else:
                self.pDA = (self.A1 - self.D1) / (self.A0 - self.D0)
            self.cAB = self.A1 - self.pAB * self.A0
            self.cBC = self.B1 - self.pBC * self.B0
            self.cCD = self.C1 - self.pCD * self.C0
            self.cDA = self.D1 - self.pDA * self.D0


    def calc_area_AB(self, I1, I2):
        if numpy.isfinite(self.pAB):
            return 0.5 * (I2 - I1) * (self.pAB * (I2 + I1) + 2 * self.cAB)
        else:
            return 0
    def calc_area_BC(self, J1, J2):
        if numpy.isfinite(self.pBC):
            return 0.5 * (J2 - J1) * (self.pBC * (J1 + J2) + 2 * self.cBC)
        else:
            return 0
    def calc_area_CD(self, K1, K2):
        if numpy.isfinite(self.pCD):
            return 0.5 * (K2 - K1) * (self.pCD * (K2 + K1) + 2 * self.cCD)
        else:
            return 0
    def calc_area_DA(self, L1, L2):
        if numpy.isfinite(self.pDA):
            return 0.5 * (L2 - L1) * (self.pDA * (L1 + L2) + 2 * self.cDA)
        else:
            return 0
    def calc_area_old(self):
        if self.area is None:
            if self.pAB is None:
                self.init_slope()
            self.area = -self.calc_area_AB(self.A0, self.B0) - \
               self.calc_area_BC(self.B0, self.C0) - \
               self.calc_area_CD(self.C0, self.D0) - \
               self.calc_area_DA(self.D0, self.A0)
        return self.area

    def calc_area_vectorial(self):
        if self.area is None:
            self.area = numpy.cross([self.C0 - self.A0, self.C1 - self.A1], [self.D0 - self.B0, self.D1 - self.B1]) / 2.0
        return self.area
    calc_area = calc_area_vectorial

    def populate_box(self):
        if self.pAB is None:
            self.init_slope()
        self.integrateAB(self.B0, self.A0, self.calc_area_AB)
        self.integrateAB(self.A0, self.D0, self.calc_area_DA)
        self.integrateAB(self.D0, self.C0, self.calc_area_CD)
        self.integrateAB(self.C0, self.B0, self.calc_area_BC)
        if (self.box / self.calc_area()).min() < 0:
            print(self.box)
            self.box[:, :] = 0
            print("AB")
            self.integrateAB(self.B0, self.A0, self.calc_area_AB)
            print(self.box)
            self.box[:, :] = 0
            print("DA")
            self.integrateAB(self.A0, self.D0, self.calc_area_DA)
            print(self.box)
            self.box[:, :] = 0
            print("CD")
            self.integrateAB(self.D0, self.C0, self.calc_area_CD)
            print(self.box)
            self.box[:, :] = 0
            print("BC")
            self.integrateAB(self.C0, self.B0, self.calc_area_BC)
            print(self.box)
            print(self)
            raise RuntimeError()
        self.box /= self.calc_area_vectorial()

    def integrateAB(self, start, stop, calc_area):
        h = 0
#        print(start, stop, calc_area(start, stop)
        if start < stop:  # positive contribution
            P = ceil(start)
            dP = P - start
#            print("Integrate", start, P, stop, calc_area(start, stop)
            if P > stop:  # start and stop are in the same unit
                A = calc_area(start, stop)
                if A != 0:
                    AA = abs(A)
                    sign = A / AA
                    dA = (stop - start)  # always positive
#                    print(AA, sign, dA
                    h = 0
                    while AA > 0:
                        if dA > AA:
                            dA = AA
                            AA = -1
                        self.box[int(floor(start)), h] += sign * dA
                        AA -= dA
                        h += 1
            else:
                if dP > 0:
                    A = calc_area(start, P)
                    if A != 0:
                        AA = abs(A)
                        sign = A / AA
                        h = 0
                        dA = dP
                        while AA > 0:
                            if dA > AA:
                                dA = AA
                                AA = -1
                            self.box[int(floor(P)) - 1, h] += sign * dA
                            AA -= dA
                            h += 1
                # subsection P1->Pn
                for i in range(int(floor(P)), int(floor(stop))):
                    A = calc_area(i, i + 1)
                    if A != 0:
                        AA = abs(A)
                        sign = A / AA

                        h = 0
                        dA = 1.0
                        while AA > 0:
                            if dA > AA:
                                dA = AA
                                AA = -1
                            self.box[i , h] += sign * dA
                            AA -= dA
                            h += 1
                # Section Pn->B
                P = floor(stop)
                dP = stop - P
                if dP > 0:
                    A = calc_area(P, stop)
                    if A != 0:
                        AA = abs(A)
                        sign = A / AA
                        h = 0
                        dA = abs(dP)
                        while AA > 0:
                            if dA > AA:
                                dA = AA
                                AA = -1
                            self.box[int(floor(P)), h] += sign * dA
                            AA -= dA
                            h += 1
        elif    start > stop:  # negative contribution. Nota is start=stop: no contribution
            P = floor(start)
            if stop > P:  # start and stop are in the same unit
                A = calc_area(start, stop)
                if A != 0:
                    AA = abs(A)
                    sign = A / AA
                    dA = (start - stop)  # always positive
                    h = 0
                    while AA > 0:
                        if dA > AA:
                            dA = AA
                            AA = -1
                        self.box[int(floor(start)), h] += sign * dA
                        AA -= dA
                        h += 1
            else:
                dP = P - start
                if dP < 0:
                    A = calc_area(start, P)
                    if A != 0:
                        AA = abs(A)
                        sign = A / AA
                        h = 0
                        dA = abs(dP)
                        while AA > 0:
                            if dA > AA:
                                dA = AA
                                AA = -1
                            self.box[int(floor(P)) , h] += sign * dA
                            AA -= dA
                            h += 1
                # subsection P1->Pn
                for i in range(int(start), int(ceil(stop)), -1):
                    A = calc_area(i, i - 1)
                    if A != 0:
                        AA = abs(A)
                        sign = A / AA
                        h = 0
                        dA = 1
                        while AA > 0:
                            if dA > AA:
                                dA = AA
                                AA = -1
                            self.box[i - 1 , h] += sign * dA
                            AA -= dA
                            h += 1
                # Section Pn->B
                P = ceil(stop)
                dP = stop - P
                if dP < 0:
                    A = calc_area(P, stop)
                    if A != 0:
                        AA = abs(A)
                        sign = A / AA
                        h = 0
                        dA = abs(dP)
                        while AA > 0:
                            if dA > AA:
                                dA = AA; AA = -1
                            self.box[int(floor(stop)), h] += sign * dA
                            AA -= dA
                            h += 1


def test():
    import numpy
    buffer = numpy.empty((20, 20), dtype=numpy.float32)
    Q = Quad(buffer)
    Q.reinit(7.5, 6.5, 2.5, 5.5, 3.5, 1.5, 8.5, 1.5)
    Q.init_slope()
#    print(Q.calc_area_AB(Q.A0, Q.B0)
#    print(Q.calc_area_BC(Q.B0, Q.C0)
#    print(Q.calc_area_CD(Q.C0, Q.D0)
#    print(Q.calc_area_DA(Q.D0, Q.A0)
    print(Q.calc_area())
    Q.populate_box()
    print(Q)
#    print(Q.get_box().sum()
    print(buffer.sum())
    print("#"*50)

    Q.reinit(8.5, 1.5, 3.5, 1.5, 2.5, 5.5, 7.5, 6.5)
    Q.init_slope()
#    print(Q.calc_area_AB(Q.A0, Q.B0)
#    print(Q.calc_area_BC(Q.B0, Q.C0)
#    print(Q.calc_area_CD(Q.C0, Q.D0)
#    print(Q.calc_area_DA(Q.D0, Q.A0)
    print(Q.calc_area())
    Q.populate_box()
    print(Q)
#    print(Q.get_box().sum()
    print(buffer.sum())

    Q.reinit(0.9, 0.9, 0.8, 6.9, 4.3, 3.9, 4.3, 0.9)
#    Q = Quad((-0.3, 1.9), (-0.4, 2.9), (1.3, 2.9), (1.3, 1.9))
    Q.init_slope()
    print("calc_area_vectorial", Q.calc_area())
#    print(Q.A0, Q.A1, Q.B0, Q.B1, Q.C0, Q.C1, Q.D0, Q.D1
#    print("Slope", Q.pAB, Q.pBC, Q.pCD, Q.pDA
#    print(Q.calc_area_AB(Q.A0, Q.B0), Q.calc_area_BC(Q.B0, Q.C0), Q.calc_area_CD(Q.C0, Q.D0), Q.calc_area_DA(Q.D0, Q.A0)
    print(Q.calc_area())
    Q.populate_box()
    print(buffer.T)
#    print(Q.get_box().sum()
    print(Q.calc_area())

    print("#"*50)

    import fabio, numpy
#    workin on 256x256
#    x, y = numpy.ogrid[:256, :256]
#    grid = numpy.logical_or(x % 10 == 0, y % 10 == 0) + numpy.ones((256, 256), numpy.float32)
#    det = detectors.FReLoN("frelon_8_8.spline")

#    # working with halfccd spline
    x, y = numpy.ogrid[:1024, :2048]
    grid = numpy.logical_or(x % 100 == 0, y % 100 == 0) + numpy.ones((1024, 2048), numpy.float32)
    det = detectors.FReLoN("halfccd.spline")
    # working with halfccd spline
#    x, y = numpy.ogrid[:2048, :2048]
#    grid = numpy.logical_or(x % 100 == 0, y % 100 == 0).astype(numpy.float32) + numpy.ones((2048, 2048), numpy.float32)
#    det = detectors.FReLoN("frelon.spline")

    print(det, det.max_shape)
    dis = Distortion(det)
    print(dis)
    lut = dis.self.calc_size()
    print(dis.lut_size)
    print(lut.mean())

    dis.calc_LUT()
    out = dis.correct(grid)
    fabio.edfimage.edfimage(data=out.astype("float32")).write("test_correct.edf")

    print("*"*50)

#    x, y = numpy.ogrid[:2048, :2048]
#    grid = numpy.logical_or(x % 100 == 0, y % 100 == 0)
#    det = detectors.FReLoN("frelon.spline")
#    print(det, det.max_shape
#    dis = Distortion(det)
#    print(dis
#    lut = dis.self.calc_size()
#    print(dis.lut_size
#    print("LUT mean & max", lut.mean(), lut.max()
#    dis.calc_LUT()
#    out = dis.correct(grid)
#    fabio.edfimage.edfimage(data=out.astype("float32")).write("test2048.edf")
    from .gui_utils import pylab
    pylab.imshow(out)  # , interpolation="nearest")
    pylab.show()

if __name__ == "__main__":
    det = dis = lut = None
    test()
