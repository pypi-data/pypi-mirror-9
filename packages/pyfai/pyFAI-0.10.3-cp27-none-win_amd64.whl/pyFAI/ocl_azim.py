# -*- coding: utf-8 -*-
#
#    Project: Azimuthal integration
#             https://github.com/kif/pyFAI
#
#    Copyright (C) European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
#                            D. Karkoulis (dimitris.karkoulis@gmail.com)
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
C++ less implementation of Dimitris' code based on PyOpenCL

TODO and trick from dimitris still missing:
  * dark-current subtraction is still missing
  * In fact you might want to consider doing the conversion on the GPU when
    possible. Think about it, you have a uint16 to float which for large arrays
    was slow.. You load on the graphic card a uint16 (2x transfer speed) and
    you convert to float inside so it should be blazing fast.


"""
__author__ = "Jérôme Kieffer"
__license__ = "GPLv3"
__date__ = "29/09/2014"
__copyright__ = "2012, ESRF, Grenoble"
__contact__ = "jerome.kieffer@esrf.fr"

import os
import logging
import threading
import numpy
from .utils import concatenate_cl_kernel
from .opencl import ocl, pyopencl, allocate_cl_buffers, release_cl_buffers
if pyopencl:
    mf = pyopencl.mem_flags
else:
    raise ImportError("pyopencl is not installed")
logger = logging.getLogger("pyFAI.ocl_azim_pyocl")


class Integrator1d(object):
    """
    Attempt to implements ocl_azim using pyopencl
    """
    BLOCK_SIZE = 128
    def __init__(self, filename=None):
        """

        @param filename: file in which profiling information are saved
        """
        self.BLOCK_SIZE = 128
        self.tdim = (self.BLOCK_SIZE,)
        self.wdim_bins = None
        self.wdim_data = None
        self._tth_min = self._tth_max = self.tth_min = self.tth_max = None
        self.nBins = -1
        self.nData = -1
        self.platformid = -1
        self.deviceid = -1
        self.useFp64 = False
        self.devicetype = "gpu"
        self.filename = filename
        self.tth_out = None
        if "write" in dir(filename):
            self.logfile = filename
        elif filename:
            self.logfile = open(self.filename, "a")
        else:
            self.logfile = None
        self.lock = threading.Semaphore()
        #Those are pointer to memory on the GPU (or None if uninitialized
        self._cl_mem = {"tth": None,
                        "tth_delta": None,
                        "image": None,
                        "solidangle": None,
                        "dark": None,
                        "mask": None,
                        "histogram": None,
                        "uhistogram": None,
                        "weights": None,
                        "uweights": None,
                        "span_ranges": None,
                        "tth_min_max": None,
                        "tth_range": None,
                        "dummyval": None,
                        "dummyval_delta": None}
        self._cl_kernel_args = {"uimemset2": [],
                                "create_histo_binarray": [],
                                "imemset": [],
                                "ui2f2": [],
                                "get_spans": [],
                                "group_spans": [],
                                "solidangle_correction": [],
                                "dummyval_correction": []}
        self._cl_program = None
        self._ctx = None
        self._queue = None
        self.do_solidangle = None
        self.do_dummy = None
        self.do_mask = None
        self.do_dark = None
        self.useTthRange = None

    def __dealloc__(self):
        self.tth_out = None
        self._queue.finish()
        self._free_buffers()
        self._free_kernels()
        self._cl_program = None
        self._queue = None
        self._ctx = None

    def __repr__(self):
        return os.linesep.join(
            [("PyOpenCL implementation of ocl_xrpd1d.ocl_xrpd1D_fullsplit"
              " C++ class. Logging in %s") % self.filename,
             ("device: %s, platform %s device %s"
              " 64bits:%s image size: %s histogram size: %s") %
             (self.devicetype, self.platformid, self.deviceid,
              self.useFp64, self.nData, self.nBins)])

    def log(self, **kwarg):
        """
        log in a file all opencl events
        """
        if self.logfile:
            for key, event in kwarg.items():
#                if  event is an event
                event.wait()
                self.logfile.write(
                    " %s: %.3fms\t" %
                    (key, (1e-6 * (event.profile.END - event.profile.START))))
            self.logfile.write(os.linesep)
            self.logfile.flush()

    def _allocate_buffers(self):
        """
        Allocate OpenCL buffers required for a specific configuration

        allocate_CL_buffers() is a private method and is called by
        configure().  Given the size of the image and the number of
        the bins, all the required OpenCL buffers are allocated.

        The method performs a basic check to see if the memory
        required by the configuration is smaller than the total global
        memory of the device. However, there is no built-in way in
        OpenCL to check the real available memory.

        In the case allocate_CL_buffers fails while allocating
        buffers, it will automatically deallocate the buffers that did
        not fail and leave the flag hasBuffers to 0.

        Note that an OpenCL context also requires some memory, as well
        as Event and other OpenCL functionalities which cannot and are
        not taken into account here.

        The memory required by a context varies depending on the
        device. Typical for GTX580 is 65Mb but for a 9300m is ~15Mb

        In addition, a GPU will always have at least 3-5Mb of memory
        in use.

        Unfortunately, OpenCL does NOT have a built-in way to check
        the actual free memory on a device, only the total memory.
        """
        utype = None
        if self.useFp64:
            utype = numpy.int64
        else:
            utype = numpy.int32

        buffers = [
            ("tth", mf.READ_ONLY, numpy.float32, self.nData),
            ("tth_delta", mf.READ_ONLY, numpy.float32, self.nData),
            ("tth_min_max", mf.READ_ONLY, numpy.float32, 2),
            ("tth_range", mf.READ_ONLY, numpy.float32, 2),
            ("mask", mf.READ_ONLY, numpy.int32, self.nData),
            ("image", mf.READ_ONLY, numpy.float32, self.nData),
            ("solidangle", mf.READ_ONLY, numpy.float32, self.nData),
            ("dark", mf.READ_ONLY, numpy.float32, self.nData),
            ("histogram", mf.READ_WRITE, numpy.float32, self.nBins),
            ("uhistogram", mf.READ_WRITE, utype, self.nBins),
            ("weights", mf.READ_WRITE, numpy.float32, self.nBins),
            ("uweights", mf.READ_WRITE, utype, self.nBins),
            ("span_ranges", mf.READ_WRITE, numpy.float32, self.nData),
            ("dummyval", mf.READ_ONLY, numpy.float32, 1),
            ("dummyval_delta", mf.READ_ONLY, numpy.float32, 1),
        ]

        if self.nData < self.BLOCK_SIZE:
            raise RuntimeError(("Fatal error in allocate_CL_buffers."
                                " nData (%d) must be >= BLOCK_SIZE (%d)\n"),
                               self.nData, self.BLOCK_SIZE)

        # TODO it seems that the device should be a member parameter
        # like in the most recent code
        device = ocl.platforms[self.platformid].devices[self.deviceid]
        self._cl_mem = allocate_cl_buffers(buffers, device, self._ctx)

    def _free_buffers(self):
        """
        free all memory allocated on the device
        """
        self._cl_mem = release_cl_buffers(self._cl_mem)

    def _free_kernels(self):
        """
        free all kernels
        """
        for kernel in self._cl_kernel_args:
            self._cl_kernel_args[kernel] = []
        self._cl_program = None

    def _compile_kernels(self, kernel_file=None):
        """
        Compile the kernel
        
        @param kernel_file: filename of the kernel (to test other kernels)
        """
        kernel_file = kernel_file or "ocl_azim_kernel_2.cl"
        kernel_src = concatenate_cl_kernel([kernel_file])

        compile_options = "-D BLOCK_SIZE=%i  -D BINS=%i -D NN=%i" % \
                            (self.BLOCK_SIZE, self.nBins, self.nData)
        if self.useFp64:
            compile_options += " -D ENABLE_FP64"

        try:
            self._cl_program = pyopencl.Program(self._ctx, kernel_src)
            self._cl_program.build(options=compile_options)
        except pyopencl.MemoryError as error:
            raise MemoryError(error)

    def _set_kernel_arguments(self):
        """Tie arguments of OpenCL kernel-functions to the actual kernels

        set_kernel_arguments() is a private method, called by configure().
        It uses the dictionary _cl_kernel_args.

        Note that by default, since TthRange is disabled, the
        integration kernels have tth_min_max tied to the tthRange
        argument slot.

        When setRange is called it replaces that argument with
        tthRange low and upper bounds. When unsetRange is called, the
        argument slot is reset to tth_min_max.
        """
        self._cl_kernel_args["create_histo_binarray"] = \
            [self._cl_mem[i] for i in ("tth", "tth_delta", "uweights",
                                       "tth_min_max", "image", "uhistogram",
                                       "span_ranges", "mask", "tth_min_max")]
        self._cl_kernel_args["get_spans"] = \
            [self._cl_mem[i] for i in ["tth", "tth_delta",
                                       "tth_min_max", "span_ranges"]]
        self._cl_kernel_args["solidangle_correction"] = \
            [self._cl_mem["image"], self._cl_mem["solidangle"]]
        self._cl_kernel_args["dummyval_correction"] = \
            [self._cl_mem["image"], self._cl_mem["dummyval"],
             self._cl_mem["dummyval_delta"]]
        self._cl_kernel_args["uimemset2"] = \
            [self._cl_mem["uweights"], self._cl_mem["uhistogram"]]
        self._cl_kernel_args["imemset"] = [self._cl_mem["mask"], ]
        self._cl_kernel_args["ui2f2"] = \
            [self._cl_mem[i] for i in ("uweights", "uhistogram",
                                       "weights", "histogram")]

    def _calc_tth_out(self, lower, upper):
        """
        Calculate the bin-center position in 2theta
        """
        self.tth_min = numpy.float32(lower)
        self.tth_max = numpy.float32(upper)
        delta = (upper - lower) / (self.nBins)
        self.tth_out = numpy.linspace(lower + 0.5 * delta,
                                      upper - 0.5 * delta,
                                      self.nBins)

    def getConfiguration(self, Nimage, Nbins, useFp64=None):
        """getConfiguration gets the description of the integrations
        to be performed and keeps an internal copy

        @param Nimage: number of pixel in image
        @param Nbins: number of bins in regrouped histogram
        @param useFp64: use double precision. By default the same as init!
        """
        if Nimage < 1 or Nbins < 1:
            raise RuntimeError(("getConfiguration with Nimage=%s and"
                                " Nbins=%s makes no sense") % (Nimage, Nbins))
        if useFp64 is not None:
            self.useFp64 = bool(useFp64)
        self.nBins = Nbins
        self.nData = Nimage
        self.wdim_data = (Nimage + self.BLOCK_SIZE - 1) & \
            ~ (self.BLOCK_SIZE - 1),
        self.wdim_bins = (Nbins + self.BLOCK_SIZE - 1) & \
            ~ (self.BLOCK_SIZE - 1),

    def configure(self, kernel=None):
        """
        The method configure() allocates the OpenCL resources required
        and compiled the OpenCL kernels.  An active context must exist
        before a call to configure() and getConfiguration() must have
        been called at least once. Since the compiled OpenCL kernels
        carry some information on the integration parameters, a change
        to any of the parameters of getConfiguration() requires a
        subsequent call to configure() for them to take effect.

        If a configuration exists and configure() is called, the
        configuration is cleaned up first to avoid OpenCL memory leaks

        @param kernel_path: is the path to the actual kernel
        """
        if self.nBins < 1 or self.nData < 1:
            raise RuntimeError(("configure() with Nimage=%s and"
                                " Nbins=%s makes no sense") %
                               (self.nData, self.nBins))
        if not self._ctx:
            raise RuntimeError("You may not call config() at this point."
                               " There is no Active context."
                               " (Hint: run init())")

        #If configure is recalled, force cleanup of OpenCL resources
        #to avoid accidental leaks
        self.clean(True)
        with self.lock:
            self._allocate_buffers()
            self._compile_kernels(kernel)
            self._set_kernel_arguments()
            # We need to initialise the Mask to 0
            imemset = self._cl_program.imemset(self._queue, self.wdim_data,
                                               self.tdim, self._cl_mem["mask"])
        if self.logfile:
            self.log(memset_mask=imemset)

    def loadTth(self, tth, dtth, tth_min=None, tth_max=None):
        """
        Load the 2th arrays along with the min and max value.

        loadTth maybe be recalled at any time of the execution in
        order to update the 2th arrays.

        loadTth is required and must be called at least once after a
        configure()
        """

        if not self._ctx:
            raise RuntimeError("You may not call loadTth() at this point."
                               " There is no Active context."
                               " (Hint: run init())")
        if not self._cl_mem["tth"]:
            raise RuntimeError("You may not call loadTth() at this point,"
                               " OpenCL is not configured"
                               " (Hint: run configure())")

        ctth = numpy.ascontiguousarray(tth.ravel(), dtype=numpy.float32)
        cdtth = numpy.ascontiguousarray(dtth.ravel(), dtype=numpy.float32)
        with self.lock:
            self._tth_max = (ctth + cdtth).max() * \
                (1.0 + numpy.finfo(numpy.float32).eps)
            self._tth_min = max(0.0, (ctth - cdtth).min())
            if tth_min is None:
                tth_min = self._tth_min

            if tth_max is None:
                tth_max = self._tth_max
            copy_tth = pyopencl.enqueue_copy(self._queue,
                                             self._cl_mem["tth"], ctth)
            copy_dtth = pyopencl.enqueue_copy(self._queue,
                                              self._cl_mem["tth_delta"], cdtth)
            pyopencl.enqueue_copy(self._queue, self._cl_mem["tth_min_max"],
                                  numpy.array((self._tth_min, self._tth_max),
                                              dtype=numpy.float32))
            logger.debug("kernel get_spans sizes: \t%s %s",
                         self.wdim_data, self.tdim)
            get_spans = \
                self._cl_program.get_spans(self._queue, self.wdim_data,
                                           self.tdim,
                                           *self._cl_kernel_args["get_spans"])
            # Group 2th span ranges group_spans(__global float *span_range)
            logger.debug("kernel group_spans sizes: \t%s %s",
                         self.wdim_data, self.tdim)
            group_spans = \
                self._cl_program.group_spans(self._queue,
                                             self.wdim_data,
                                             self.tdim,
                                             self._cl_mem["span_ranges"])
            self._calc_tth_out(tth_min, tth_max)
        if self.logfile:
            self.log(copy_2th=copy_tth, copy_delta2th=copy_dtth,
                     get_spans=get_spans, group_spans=group_spans)

    def setSolidAngle(self, solidAngle):
        """
        Enables SolidAngle correction and uploads the suitable array
        to the OpenCL device.

        By default the program will assume no solidangle correction
        unless setSolidAngle() is called.  From then on, all
        integrations will be corrected via the SolidAngle array.

        If the SolidAngle array needs to be changes, one may just call
        setSolidAngle() again with that array

        @param solidAngle: the solid angle of the given pixel
        @type solidAngle: ndarray
        """
        if not self._ctx:
            raise RuntimeError("You may not call Integrator1d.setSolidAngle()"
                               " at this point. There is no Active context."
                               " (Hint: run init())")
        cSolidANgle = numpy.ascontiguousarray(solidAngle.ravel(),
                                              dtype=numpy.float32)
        with self.lock:
            self.do_solidangle = True
            copy_solidangle = pyopencl.enqueue_copy(self._queue,
                                                    self._cl_mem["solidangle"],
                                                    cSolidANgle)
        if self.logfile:
            self.log(copy_solidangle=copy_solidangle)

    def unsetSolidAngle(self):
        """
        Instructs the program to not perform solidangle correction from now on.

        SolidAngle correction may be turned back on at any point
        """
        with self.lock:
            self.do_solidangle = False

    def setMask(self, mask):
        """
        Enables the use of a Mask during integration. The Mask can be
        updated by recalling setMask at any point.

        The Mask must be a PyFAI Mask. Pixels with 0 are masked
        out. TODO: check and invert!

        @param mask: numpy.ndarray of integer.
        """
        if not self._ctx:
            raise RuntimeError("You may not call"
                               " Integrator1d.setDummyValue(dummy,delta_dummy)"
                               " at this point. There is no Active context."
                               " (Hint: run init())")
        cMask = numpy.ascontiguousarray(mask.ravel(), dtype=numpy.int32)
        with self.lock:
            self.do_mask = True
            copy_mask = pyopencl.enqueue_copy(self._queue,
                                              self._cl_mem["mask"], cMask)
        if self.logfile:
            self.log(copy_mask=copy_mask)

    def unsetMask(self):
        """
        Disables the use of a Mask from that point.
        It may be re-enabled at any point via setMask
        """
        with self.lock:
            self.do_mask = False

    def setDummyValue(self, dummy, delta_dummy):
        """
        Enables dummy value functionality and uploads the value to the
        OpenCL device.

        Image values that are similar to the dummy value are set to 0.

        @param dummy: value in image of missing values (masked pixels?)
        @param delta_dummy: precision for dummy values
        """
        if not self._ctx:
            raise RuntimeError("You may not call"
                               " Integrator1d.setDummyValue(dummy,delta_dummy)"
                               " at this point. There is no Active context."
                               " (Hint: run init())")
        else:
            with self.lock:
                self.do_dummy = True
                pyopencl.enqueue_copy(self._queue, self._cl_mem["dummyval"],
                                      numpy.array((dummy,),
                                                  dtype=numpy.float32))
                pyopencl.enqueue_copy(self._queue,
                                      self._cl_mem["dummyval_delta"],
                                      numpy.array((delta_dummy,),
                                                  dtype=numpy.float32))

    def unsetDummyValue(self):
        """Disable a dummy value.
        May be re-enabled at any time by setDummyValue
        """
        with self.lock:
            self.do_dummy = False

    def setRange(self, lowerBound, upperBound):
        """
        Instructs the program to use a user - defined range for 2th
        values

        setRange is optional. By default the integration will use the
        tth_min and tth_max given by loadTth() as integration
        range. When setRange is called it sets a new integration range
        without affecting the 2th array. All values outside that range
        will then be discarded when interpolating.  Currently, if the
        interval of 2th (2th + -d2th) is not all inside the range
        specified, it is discarded. The bins of the histogram are
        RESCALED to the defined range and not the original tth_max -
        tth_min range.

        setRange can be called at any point and as many times required
        after a valid configuration is created.

        @param lowerBound: lower bound of the integration range
        @type lowerBound: float
        @param upperBound: upper bound of the integration range
        @type upperBound: float
        """
        if self._ctx is None:
            raise RuntimeError("You may not call setRange() at this point."
                               " There is no Active context."
                               " (Hint: run init())")
        if not (self.nData > 1 and self._cl_mem["tth_range"]):
            raise RuntimeError("You may not call setRange() at this point,"
                               " the required buffers are not allocated"
                               " (Hint: run config())")

        with self.lock:
            self.useTthRange = True
            copy_2thrange = \
                pyopencl.enqueue_copy(self._queue, self._cl_mem["tth_range"],
                                      numpy.array((lowerBound, upperBound),
                                                  dtype=numpy.float32))
            self._cl_kernel_args["create_histo_binarray"][8] = \
                self._cl_mem["tth_range"]
            self._cl_kernel_args["get_spans"][2] = self._cl_mem["tth_range"]

        if self.logfile:
            self.log(copy_2thrange=copy_2thrange)

    def unsetRange(self):
        """
        Disable the use of a user-defined 2th range and revert to
        tth_min,tth_max range

        unsetRange instructs the program to revert to its default
        integration range. If the method is called when no
        user-defined range had been previously specified, no action
        will be performed
        """

        with self.lock:
            if self.useTthRange:
                self._calc_tth_out(self._tth_min, self._tth_max)
            self.useTthRange = False
            self._cl_kernel_args["create_histo_binarray"][8] = \
                self._cl_mem["tth_min_max"]
            self._cl_kernel_args["get_spans"][2] = self._cl_mem["tth_min_max"]

    def execute(self, image):
        """
        Perform a 1D azimuthal integration

        execute() may be called only after an OpenCL device is
        configured and a Tth array has been loaded (at least once) It
        takes the input image and based on the configuration provided
        earlier it performs the 1D integration.  Notice that if the
        provided image is bigger than N then only N points will be
        taked into account, while if the image is smaller than N the
        result may be catastrophic.  set/unset and loadTth methods
        have a direct impact on the execute() method.  All the rest of
        the methods will require at least a new configuration via
        configure().

        Takes an image, integrate and return the histogram and weights

        @param image: image to be processed as a numpy array
        @return: tth_out, histogram, bins

        TODO: to improve performances, the image should be casted to
        float32 in an optimal way: currently using numpy machinery but
        would be better if done in OpenCL
        """
        assert image.size == self.nData
        if not self._ctx:
            raise RuntimeError("You may not call execute() at this point."
                               " There is no Active context."
                               " (Hint: run init())")
        if not self._cl_mem["histogram"]:
            raise RuntimeError("You may not call execute() at this point,"
                               " kernels are not configured"
                               " (Hint: run configure())")
        if not self._tth_max:
            raise RuntimeError("You may not call execute() at this point."
                               " There is no 2th array loaded."
                               " (Hint: run loadTth())")

        with self.lock:
            copy_img = pyopencl.enqueue_copy(
                self._queue,
                self._cl_mem["image"],
                numpy.ascontiguousarray(image.ravel(),
                                        dtype=numpy.float32))
            logger.debug("kernel uimemset2 sizes: \t%s %s",
                         self.wdim_bins, self.tdim)
            memset = \
                self._cl_program.uimemset2(self._queue, self.wdim_bins,
                                           self.tdim,
                                           *self._cl_kernel_args["uimemset2"])

            if self.do_dummy:
                logger.debug("kernel dummyval_correction sizes: \t%s %s",
                             self.wdim_data, self.tdim)
                dummy = self._cl_program.dummyval_correction(
                    self._queue, self.wdim_data, self.tdim,
                    self._cl_kernel_args["dummyval_correction"])

            if self.do_solidangle:
                sa = self._cl_program.solidangle_correction(
                    self._queue, self.wdim_data, self.tdim,
                    *self._cl_kernel_args["solidangle_correction"])
            logger.debug("kernel create_histo_binarray sizes: \t%s %s",
                         self.wdim_data, self.tdim)
            integrate = self._cl_program.create_histo_binarray(
                self._queue, self.wdim_data, self.tdim,
                *self._cl_kernel_args["create_histo_binarray"])
            #convert to float
            convert = self._cl_program.ui2f2(self._queue, self.wdim_data,
                                             self.tdim,
                                             *self._cl_kernel_args["ui2f2"])
            histogram = numpy.empty(self.nBins, dtype=numpy.float32)
            bins = numpy.empty(self.nBins, dtype=numpy.float32)
            copy_hist = pyopencl.enqueue_copy(self._queue, histogram,
                                              self._cl_mem["histogram"])
            copy_bins = pyopencl.enqueue_copy(self._queue, bins,
                                              self._cl_mem["weights"])

            if self.logfile:
                self.log(copy_in=copy_img, memset2=memset)
                if self.do_dummy:
                    self.log(dummy_corr=dummy)
                if self.do_solidangle:
                    self.log(solid_angle=sa)
                self.log(integrate=integrate, convert_uint2float=convert,
                         copy_hist=copy_hist, copy_bins=copy_bins)
            pyopencl.enqueue_barrier(self._queue).wait()

        return self.tth_out, histogram, bins

    def init(self, devicetype="GPU", useFp64=True,
             platformid=None, deviceid=None):
        """Initial configuration: Choose a device and initiate a
        context.  Devicetypes can be GPU, gpu, CPU, cpu, DEF, ACC,
        ALL. Suggested are GPU,CPU. For each setting to work there
        must be such an OpenCL device and properly installed. E.g.: If
        Nvidia driver is installed, GPU will succeed but CPU will
        fail. The AMD SDK kit (AMD APP) is required for CPU via
        OpenCL.

        @param devicetype: string in ["cpu","gpu", "all", "acc"]
        @param useFp64: boolean specifying if double precision will be used
        @param platformid: integer
        @param devid: integer
        """
        if self._ctx is None:
            self._ctx = ocl.create_context(devicetype, useFp64,
                                           platformid, deviceid)
            device = self._ctx.devices[0]

            self.devicetype = pyopencl.device_type.to_string(device.type)
            if (self.devicetype == "CPU")\
                    and (device.platform.vendor == "Apple"):
                logger.warning("This is a workaround for Apple's OpenCL"
                               " on CPU: enforce BLOCK_SIZE=1")
                self.BLOCK_SIZE = 1
                self.tdim = (self.BLOCK_SIZE,)

                if self.nBins:
                    self.wdim_bins = (self.nBins + self.BLOCK_SIZE - 1) & \
                        ~ (self.BLOCK_SIZE - 1),
                if self.nData:
                    self.wdim_data = (self.nData + self.BLOCK_SIZE - 1) & \
                        ~ (self.BLOCK_SIZE - 1),

            self.useFp64 = "fp64" in device.extensions
            platforms = pyopencl.get_platforms()
            self.platformid = platforms.index(device.platform)
            devices = platforms[self.platformid].get_devices()
            self.deviceid = devices.index(device)
            if self.filename:
                self._queue = pyopencl.CommandQueue(
                    self._ctx,
                    properties=pyopencl.command_queue_properties.PROFILING_ENABLE)
            else:
                self._queue = pyopencl.CommandQueue(self._ctx)
        else:
            logger.warning("Recycling existing context ..."
                           " if you want to get start from scratch,"
                           " use clean()")

    def clean(self, preserve_context=False):
        """
        Free OpenCL related resources allocated by the library.

        clean() is used to reinitiate the library back in a vanilla
        state.  It may be asked to preserve the context created by
        init or completely clean up OpenCL. Guard/Status flags that
        are set will be reset.

        @param preserve_context: preserves or destroys all OpenCL resources
        @type preserve_context: bool
        """

        with self.lock:
            self._free_buffers()
            self._free_kernels()
            if not preserve_context:
                self._queue = None
                self._ctx = None

    def get_status(self):
        """return a dictionnary with the status of the integrator: for
        compatibilty with former implementation"""
        out = {'dummy': bool(self.do_dummy),
               'mask': bool(self.do_mask),
               'dark': bool(self.do_dark),
               "solid_angle": bool(self.do_solidangle),
               "pos1": False,
               'pos0': (self._tth_max is not None),
               'compiled': (self._cl_program is not None),
               'size': self.nData,
               'context': (self._ctx is not None)}
        return out
