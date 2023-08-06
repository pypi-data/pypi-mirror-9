#!/usr/bin/python
#coding: utf-8

from __future__ import division, with_statement, print_function

__doc__ = "Benchmark for HDF5 writing" 
__author__ ="Jérôme Kieffer"
__date__ = "2014-09-24"

import os
import time
from argparse import ArgumentParser
import tempfile
import numpy
from pyFAI import io
import logging
logger = logging.getLogger("Bench_hdf5")
logger.setLevel(logging.INFO)

def parse():
    """
    Parse command line arguments
    """ 
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--dir', dest='directory', default=tempfile.gettempdir(),
                        help='Destination directory (/tmp)')
    parser.add_argument('-n', '--number', dest='n', default=1024, type=int,
                        help='Number of frames to write')
    parser.add_argument('-w', '--width', dest='width', default=1024, type=int,
                        help='width of a frame (1024)')
    parser.add_argument('-H', '--height', dest='height', default=1024, type=int,
                        help='height of the image (1024)')
    parser.add_argument('-t', '--type', dest='dtype', default="float32", type=str,
                        help='data type of item (float32)')
    parser.add_argument('-b', '--bsize', dest='bsize', default=10, type=int,
                        help='size of the random buffer for frames (10)')
    opt = parser.parse_args()
    return opt


def bench_hdf5(n=1024, shape=(1024, 1024), dtype="float32", dirname=None, bsize=10):
    """
    Actually performs the HDF5 writing benchmark 
    @param n: number of frames to be written
    @param shape: 2-tuple of integer describing the shape of the image 
    @param bsize: number of frames in buffer
    """
    tmp_dir = tempfile.mkdtemp(dir=dirname)
    h5file = os.path.join(tmp_dir, "junk.h5")
    logger.info("Writing large dataset %ix(%i,%i) of %s to %s." % (n, shape[0], shape[1], dtype, h5file))
    
    dtype = numpy.dtype(dtype)
    if dtype.kind == "f":
        data = numpy.random.random((bsize, shape[0], shape[1])).astype(dtype)
    elif dtype.name.find("int") >= 0:
        size = bsize * shape[0] * shape[1]
        maxi = 2 ** (dtype.itemsize * 8 - 1) - 1
        data = numpy.random.random_integers(0, maxi, size=size).astype(dtype)
        data.shape = (bsize, shape[0], shape[1])
    else:
        raise RuntimeError("unhandled data type %s" % dtype)
    size = n * shape[0] * shape[1]
    nbytes = size * dtype.itemsize
    nmbytes = nbytes / 1e6
    t0 = time.time()
    writer = io.HDF5Writer(filename=h5file, hpath="data")
    writer.init({"nbpt_azim": shape[0], "nbpt_rad": shape[1], "dtype": dtype.name})
    for i in range(n):
        writer.write(data[i % bsize], i)
    writer.close()
    t = time.time() - t0
    bps = nbytes / t
    logger.info("Writing of %.3fMB in HDF5 took %.3fs (%.3f MByte/s)" % (nmbytes, t, nmbytes / t))
    statinfo = os.stat(h5file)
    assert statinfo.st_size > nbytes

    # Clean up
    os.unlink(h5file)
    os.removedirs(tmp_dir)
    return bps

if __name__ == "__main__":
    opts = parse()
    print(bench_hdf5(dirname=opts.directory,
                     n=opts.n, 
                     shape=(opts.height, opts.width),
                     dtype=opts.dtype, 
                     bsize=opts.bsize))
