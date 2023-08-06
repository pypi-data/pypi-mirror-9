#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Project: Fast Azimuthal integration
#             https://github.com/pyFAI/pyFAI
#
#
#    Copyright (C) European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
# 
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# 
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = "Jerome Kieffer"
__date__ = "20/10/2014"
__name__ = "histogram"
__license__ = "GPLv3+"
__copyright__ = "2011-2014, ESRF"
__contact__ = "jerome.kieffer@esrf.fr"

import cython
import numpy
cimport numpy
import sys
import logging
logger = logging.getLogger("pyFAI.histogram_nomp")
from libc.math cimport floor
EPS32 = (1.0 + numpy.finfo(numpy.float32).eps)


@cython.cdivision(True)
cdef inline double getBinNr(double x0, double pos0_min, double delta) nogil:
    """
    calculate the bin number for any point
    param x0: current position
    param pos0_min: position minimum
    param delta: bin width
    """
    return (x0 - pos0_min) / delta


@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
def histogram(numpy.ndarray pos not None, \
              numpy.ndarray weights not None, \
              int bins=100,
              bin_range=None,
              pixelSize_in_Pos=None,
              nthread=None,
              float empty=0.0):
    """
    Calculates histogram of pos weighted by weights

    @param pos: 2Theta array
    @param weights: array with intensities
    @param bins: number of output bins
    @param pixelSize_in_Pos: size of a pixels in 2theta: DESACTIVATED
    @param nthread: OpenMP is disabled. unused

    @return 2theta, I, weighted histogram, raw histogram
    """

    assert pos.size == weights.size
    assert bins > 1
    cdef:
        int  size = pos.size
        float[:] cpos = numpy.ascontiguousarray(pos.ravel(), dtype=numpy.float32)
        float[:] cdata = numpy.ascontiguousarray(weights.ravel(), dtype=numpy.float32)
        numpy.ndarray[numpy.float64_t, ndim = 1] out_data = numpy.zeros(bins, dtype="float64")
        numpy.ndarray[numpy.float64_t, ndim = 1] out_count = numpy.zeros(bins, dtype="float64")
        numpy.ndarray[numpy.float64_t, ndim = 1] out_merge = numpy.zeros(bins, dtype="float64")
        double delta, min0, max0
        double a = 0.0
        double d = 0.0
        double fbin = 0.0
        double epsilon = 1e-10
        int bin = 0, i, idx
    if pixelSize_in_Pos:
        logger.warning("No pixel splitting in histogram")

    if bin_range is not None:
        min0 = min(bin_range)
        max0 = max(bin_range) * EPS32
    else:
        min0 = pos.min()
        max0 = pos.max() * EPS32

    delta = (max0 - min0) / float(bins)


    with nogil:
        for i in range(size):
            d = cdata[i]
            a = cpos[i]
            fbin = getBinNr(a, min0, delta)
            bin = < int > fbin
            if bin<0 or bin>= bins:
                continue
            out_count[bin] += 1.0
            out_data[bin] += d

        for idx in range(bins):
            if out_count[idx] > epsilon:
                out_merge[idx] = out_data[idx] / out_count[idx]
            else:
                out_merge[idx] = empty

    out_pos = numpy.linspace(min0 + (0.5 * delta), max0 - (0.5 * delta), bins)

    return out_pos, out_merge, out_data, out_count


@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
def histogram2d(numpy.ndarray pos0 not None,
                numpy.ndarray pos1 not None,
                bins not None,
                numpy.ndarray weights not None,
                split=False,
                nthread=None,
                float empty=0.0):
    """
    Calculate 2D histogram of pos0,pos1 weighted by weights

    @param pos0: 2Theta array
    @param pos1: Chi array
    @param weights: array with intensities
    @param bins: number of output bins int or 2-tuple of int
	@param split: pixel splitting is disabled in histogram
    @param nthread: OpenMP is disabled. unused

    @return  I, edges0, edges1, weighted histogram(2D), unweighted histogram (2D)
    """
    assert pos0.size == pos1.size
    assert pos0.size == weights.size
    cdef:
        int  bins0, bins1, i, j, bin0, bin1
        int  size = pos0.size
    try:
        bins0, bins1 = tuple(bins)
    except:
        bins0 = bins1 = int(bins)
    if bins0 <= 0:
        bins0 = 1
    if bins1 <= 0:
        bins1 = 1
    cdef:
        float[:] cpos0 = numpy.ascontiguousarray(pos0.ravel(), dtype=numpy.float32)
        float[:] cpos1 = numpy.ascontiguousarray(pos1.ravel(), dtype=numpy.float32)
        float[:] data = numpy.ascontiguousarray(weights.ravel(), dtype=numpy.float32)
        numpy.ndarray[numpy.float64_t, ndim = 2] out_data = numpy.zeros((bins0, bins1), dtype="float64")
        numpy.ndarray[numpy.float64_t, ndim = 2] out_count = numpy.zeros((bins0, bins1), dtype="float64")
        numpy.ndarray[numpy.float64_t, ndim = 2] out_merge = numpy.zeros((bins0, bins1), dtype="float64")
        double min0 = pos0.min()
        double max0 = pos0.max() * EPS32
        double min1 = pos1.min()
        double max1 = pos1.max() * EPS32
        double delta0 = (max0 - min0) / float(bins0)
        double delta1 = (max1 - min1) / float(bins1)
        double fbin0, fbin1, p0, p1, d
        double epsilon = 1e-10

    if split:
        logger.warning("No pixel splitting in histogram")

    edges0 = numpy.linspace(min0 + (0.5 * delta0), max0 - (0.5 * delta0), bins0)
    edges1 = numpy.linspace(min1 + (0.5 * delta1), max1 - (0.5 * delta1), bins1)
    with nogil:
        for i in range(size):
            p0 = cpos0[i]
            p1 = cpos1[i]
            d = data[i]
            fbin0 = getBinNr(p0, min0, delta0)
            fbin1 = getBinNr(p1, min1, delta1)
            bin0 = < int > floor(fbin0)
            bin1 = < int > floor(fbin1)
            if (bin0<0) or (bin1<0) or (bin0>=bins0) or (bin1>=bins1):
                continue
            out_count[bin0, bin1] += 1.0
            out_data[bin0, bin1] += d

        for i in range(bins0):
            for j in range(bins1):
                if out_count[i, j] > epsilon:
                    out_merge[i, j] = out_data[i, j] / out_count[i, j]
                else:
                    out_merge[i, j] = empty

    return out_merge, edges0, edges1, out_data, out_count
