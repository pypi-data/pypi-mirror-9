# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Project: Fast Azimuthal Integration
#             https://github.com/pyFAI/pyFAI
#
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


from __future__ import absolute_import, print_function, division

__author__ = "Jerome Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20/03/2015"
__status__ = "beta"
__docformat__ = 'restructuredtext'
__doc__ = """

Module for "high-performance" writing in either 1D with Ascii , or 2D with FabIO
or even nD with n varying from  2 to 4 using HDF5

Stand-alone module which tries to offer interface to HDF5 via H5Py and
capabilities to write EDF or other formats using fabio.

Can be imported without h5py but then limited to fabio & ascii formats.

TODO:
* add monitor to HDF5
"""
import fabio
import json
import logging
import numpy
import os
import posixpath
import sys
import threading
import time

from .utils import StringTypes
from . import units
from . import version


logger = logging.getLogger("pyFAI.io")
try:
    import h5py
except ImportError as error:
    h5py = None
    logger.error("h5py module missing")
else:
    try:
        h5py._errors.silence_errors()
    except AttributeError:  # old h5py
        pass





def get_isotime(forceTime=None):
    """
    @param forceTime: enforce a given time (current by default)
    @type forceTime: float
    @return: the current time as an ISO8601 string
    @rtype: string
    """
    if forceTime is None:
        forceTime = time.time()
    localtime = time.localtime(forceTime)
    gmtime = time.gmtime(forceTime)
    tz_h = localtime.tm_hour - gmtime.tm_hour
    tz_m = localtime.tm_min - gmtime.tm_min
    return "%s%+03i:%02i" % (time.strftime("%Y-%m-%dT%H:%M:%S", localtime), tz_h, tz_m)

def from_isotime(text, use_tz=False):
    """
    @param text: string representing the time is iso format
    """
    if len(text) == 1:
        # just in case someone sets as a list
        text = text[0]
    try:
        text = text.decode("ascii")
    except:
        text = str(text)
    if len(text) < 19:
        logger.warning("Not a iso-time string: %s" % text)
        return
    base = text[:19]
    if use_tz and len(text) == 25:
        sgn = 1 if  text[:19] == "+" else -1
        tz = 60 * (60 * int(text[20:22]) + int(text[23:25])) * sgn
    else:
        tz = 0
    return time.mktime(time.strptime(base, "%Y-%m-%dT%H:%M:%S")) + tz

def is_hdf5(filename):
    """
    Check if a file is actually a HDF5 file

    @param filename: this file has better to exist
    """
    signature = [137, 72, 68, 70, 13, 10, 26, 10]
    if not os.path.exists(filename):
        raise IOError("No such file %s" % (filename))
    with open(filename, "rb") as f:
        raw = f.read(8)
    sig = [ord(i) for i in raw] if sys.version_info[0] < 3 else [int(i) for i in raw]
    return sig == signature


class Writer(object):
    """
    Abstract class for writers.
    """
    CONFIG_ITEMS = ["filename", "dirname", "extension", "subdir", "hpath"]
    def __init__(self, filename=None, extension=None):
        """

        """
        self.filename = filename
        if os.path.exists(filename):
            logger.warning("Destination file %s exists" % filename)
        self._sem = threading.Semaphore()
        self.dirname = None
        self.subdir = None
        self.extension = extension
        self.fai_cfg = {}
        self.lima_cfg = {}


    def __repr__(self):
        return "Generic writer on file %s" % (self.filename)

    def init(self, fai_cfg=None, lima_cfg=None):
        """
        Creates the directory that will host the output file(s)
        @param fai_cfg: configuration for worker
        @param lima_cfg: configuration for acquisition
        """

        with self._sem:
            if fai_cfg is not None:
                self.fai_cfg = fai_cfg
            if lima_cfg is not None:
                self.lima_cfg = lima_cfg
            if self.filename is not None:
                dirname = os.path.dirname(self.filename)
                if dirname and not os.path.exists(dirname):
                    try:
                        os.makedirs(dirname)
                    except Exception as err:
                        logger.info("Problem while creating directory %s: %s" % (dirname, err))
    def flush(self, *arg, **kwarg):
        """
        To be implemented
        """
        pass

    def write(self, data):
        """
        To be implemented
        """
        pass

    def setJsonConfig(self, json_config=None):
        """
        Sets the JSON configuration
        """

        if type(json_config) in StringTypes:
            if os.path.isfile(json_config):
                config = json.load(open(json_config, "r"))
            else:
                 config = json.loads(json_config)
        else:
            config = dict(json_config)
        for k, v in  config.items():
            if k in self.CONFIG_ITEMS:
                self.__setattr__(k, v)


class HDF5Writer(Writer):
    """
    Class allowing to write HDF5 Files.

    """
    CONFIG = "pyFAI"
    DATASET_NAME = "data"
    def __init__(self, filename, hpath="data", fast_scan_width=None):
        """
        Constructor of an HDF5 writer:

        @param filename: name of the file
        @param hpath: name of the group: it will contain data (2-4D dataset), [tth|q|r] and pyFAI, group containing the configuration
        @param fast_scan_width: set it to define the width of
        """
        Writer.__init__(self, filename)
        self.hpath = hpath
        self.fast_scan_width = None
        if fast_scan_width is not None:
            try:
                self.fast_scan_width = int(fast_scan_width)
            except:
                pass
        self.hdf5 = None
        self.group = None
        self.dataset = None
        self.pyFAI_grp = None
        self.radial_values = None
        self.azimuthal_values = None
        self.error_values = None
        self.has_radial_values = False
        self.has_azimuthal_values = False
        self.has_error_values = False
        self.chunk = None
        self.shape = None
        self.ndim = None

    def __repr__(self):
        return "HDF5 writer on file %s:%s %sinitialized" % (self.filename, self.hpath, "" if self._initialized else "un")

    def init(self, fai_cfg=None, lima_cfg=None):
        """
        Initializes the HDF5 file for writing
        @param fai_cfg: the configuration of the worker as a dictionary
        """
        logger.debug("in init")
        Writer.init(self, fai_cfg, lima_cfg)
        with self._sem:
            # TODO: this is Debug statement
            open("fai_cfg.json", "w").write(json.dumps(self.fai_cfg, indent=4))
            open("lima_cfg.json", "w").write(json.dumps(self.lima_cfg, indent=4))
            self.fai_cfg["nbpt_rad"] = self.fai_cfg.get("nbpt_rad", 1000)
            if h5py:
                try:
                    self.hdf5 = h5py.File(self.filename)
                except IOError:  # typically a corrupted HDF5 file !
                    os.unlink(self.filename)
                    self.hdf5 = h5py.File(self.filename)
            else:
                logger.error("No h5py library, no chance")
                raise RuntimeError("No h5py library, no chance")
            self.group = self.hdf5.require_group(self.hpath)
            self.group.attrs["NX_class"] = "NXentry"
            self.pyFAI_grp = self.hdf5.require_group(posixpath.join(self.hpath, self.CONFIG))
            self.pyFAI_grp.attrs["desc"] = "PyFAI worker configuration"
            for key, value in self.fai_cfg.items():
                if value is None:
                    continue
                try:
                    self.pyFAI_grp[key] = value
                except:
                    print("Unable to set %s: %s" % (key, value))
                    self.close()
                    sys.exit(1)
            rad_name, rad_unit = str(self.fai_cfg.get("unit", "2th_deg")).split("_", 1)
            self.radial_values = self.group.require_dataset(rad_name, (self.fai_cfg["nbpt_rad"],), numpy.float32)
            if self.fai_cfg.get("nbpt_azim", 0) > 1:
                self.azimuthal_values = self.group.require_dataset("chi", (self.fai_cfg["nbpt_azim"],), numpy.float32)
                self.azimuthal_values.attrs["unit"] = "deg"
                self.azimuthal_values.attrs["interpretation"] = "scalar"
                self.azimuthal_values.attrs["long name"] = "Azimuthal angle"

            self.radial_values.attrs["unit"] = rad_unit
            self.radial_values.attrs["interpretation"] = "scalar"
            self.radial_values.attrs["long name"] = "diffraction radial direction"
            if self.fast_scan_width:
                self.fast_motor = self.group.require_dataset("fast", (self.fast_scan_width,) , numpy.float32)
                self.fast_motor.attrs["long name"] = "Fast motor position"
                self.fast_motor.attrs["interpretation"] = "scalar"
                self.fast_motor.attrs["axis"] = "1"
                self.radial_values.attrs["axis"] = "2"
                if self.azimuthal_values is not None:
                    chunk = 1, self.fast_scan_width, self.fai_cfg["nbpt_azim"], self.fai_cfg["nbpt_rad"]
                    self.ndim = 4
                    self.azimuthal_values.attrs["axis"] = "3"
                else:
                    chunk = 1, self.fast_scan_width, self.fai_cfg["nbpt_rad"]
                    self.ndim = 3
            else:
                self.radial_values.attrs["axis"] = "1"
                if self.azimuthal_values is not None:
                    chunk = 1, self.fai_cfg["nbpt_azim"], self.fai_cfg["nbpt_rad"]
                    self.ndim = 3
                    self.azimuthal_values.attrs["axis"] = "2"
                else:
                    chunk = 1, self.fai_cfg["nbpt_rad"]
                    self.ndim = 2

            if self.DATASET_NAME in self.group:
                del self.group[self.DATASET_NAME]
            shape = list(chunk)
            if self.lima_cfg.get("number_of_frames", 0) > 0:
                if self.fast_scan_width is not None:
                    size[0] = 1 + self.lima_cfg["number_of_frames"] // self.fast_scan_width
                else:
                    size[0] = self.lima_cfg["number_of_frames"]
            dtype = self.lima_cfg.get("dtype") or self.fai_cfg.get("dtype")
            if dtype is None:
                dtype = numpy.float32
            else:
                dtype = numpy.dtype(dtype)
            self.dataset = self.group.require_dataset(self.DATASET_NAME, shape, dtype=dtype, chunks=chunk,
                                                      maxshape=(None,) + chunk[1:])
            if self.fai_cfg.get("nbpt_azim", 0) > 1:
                self.dataset.attrs["interpretation"] = "image"
            else:
                self.dataset.attrs["interpretation"] = "spectrum"
            self.dataset.attrs["signal"] = "1"
            self.chunk = chunk
            self.shape = chunk
            name = "Mapping " if self.fast_scan_width else "Scanning "
            name += "2D" if self.fai_cfg.get("nbpt_azim", 0) > 1 else "1D"
            name += " experiment"
            self.group["title"] = numpy.string_(name)
            self.group["program"] = numpy.string_("PyFAI")
            self.group["start_time"] = numpy.string_(get_isotime())

    def flush(self, radial=None, azimuthal=None):
        """
        Update some data like axis units and so on.

        @param radial: position in radial direction
        @param  azimuthal: position in azimuthal direction
        """
        with self._sem:
            if not self.hdf5:
                raise RuntimeError('No opened file')
            if radial is not None:
                if radial.shape == self.radial_values.shape:
                    self.radial_values[:] = radial
                else:
                    logger.warning("Unable to assign radial axis position")
            if azimuthal is not None:
                if azimuthal.shape == self.azimuthal_values.shape:
                    self.azimuthal_values[:] = azimuthal
                else:
                    logger.warning("Unable to assign azimuthal axis position")
            self.hdf5.flush()

    def close(self):
        logger.debug("In close")
        if self.hdf5:
            self.flush()
            with self._sem:
                self.hdf5.close()
                self.hdf5 = None

    def write(self, data, index=0):
        """
        Minimalistic method to limit the overhead.
        @param data: array with intensities or tuple (2th,I) or (I,2th,chi)
        """
        logger.debug("In write, index %s" % index)
        radial = None
        azimuthal = None
        error = None
        if isinstance(data, numpy.ndarray):
            I = data
        elif isinstance(data, (list, tuple)):
            n = len(data)
            if n == 2:
                radial, I = data
            elif n == 3:
                if data[0].ndim == 2:
                    I, radial, azimuthal = data
                else:
                    radial, I, error = data
        with self._sem:
            if self.dataset is None:
                logger.warning("Writer not initialized !")
                return
            if self.fast_scan_width:
                index0, index1 = (index // self.fast_scan_width, index % self.fast_scan_width)
                if index0 >= self.dataset.shape[0]:
                    self.dataset.resize(index0 + 1, axis=0)
                self.dataset[index0, index1] = data
            else:
                if index >= self.dataset.shape[0]:
                    self.dataset.resize(index + 1, axis=0)
                self.dataset[index] = I
            if (not self.has_azimuthal_values) and \
               (azimuthal is not None) and \
               self.azimuthal_values is not None:
                self.azimuthal_values[:] = azimuthal
            if (not self.has_azimuthal_values) and \
               (azimuthal is not None) and \
               self.azimuthal_values is not None:
                self.azimuthal_values[:] = azimuthal
                self.has_azimuthal_values = True
            if (not self.has_radial_values) and \
               (radial is not None) and \
               self.radial_values is not None:
                self.radial_values[:] = radial
                self.has_radial_values = True


class AsciiWriter(Writer):
    """
    Ascii file writer (.xy or .dat)
    """
    def __init__(self, filename=None, prefix="fai_", extension=".dat"):
        """

        """
        Writer.__init__(self, filename, extension)
        self.header = None
        if os.path.isdir(filename):
            self.directory = filename
        else:
            self.directory = os.path.dirname(filename)
        self.prefix = prefix
        self.index_format = "%04i"
        self.start_index = 0

    def __repr__(self):
        return "Ascii writer on file %s" % (self.filename)

    def init(self, fai_cfg=None, lima_cfg=None):
        """
        Creates the directory that will host the output file(s)

        """
        Writer.init(self, fai_cfg, lima_cfg)
        with self._sem:
            headerLst = ["", "== Detector =="]
            if "detector" in self.fai_cfg:
                headerLst.append("Detector: %s" % self.fai_cfg["detector"])
            if "splineFile" in self.fai_cfg:
                headerLst.append("SplineFile: %s" % self.fai_cfg["splineFile"])
            if  "pixel1" in self.fai_cfg:
                headerLst.append("PixelSize: %.3e, %.3e m" % (self.fai_cfg["pixel1"], self.fai_cfg["pixel2"]))
            if "mask_file" in self.fai_cfg:
                headerLst.append("MaskFile: %s" % (self.fai_cfg["mask_file"]))

            headerLst.append("== pyFAI calibration ==")
            if "poni1" in self.fai_cfg:
                headerLst.append("PONI: %.3e, %.3e m" % (self.fai_cfg["poni1"], self.fai_cfg["poni2"]))
            if "dist" in self.fai_cfg:
                headerLst.append("Distance Sample to Detector: %s m" % self.fai_cfg["dist"])
            if "rot1" in self.fai_cfg:
                headerLst.append("Rotations: %.6f %.6f %.6f rad" % (self.fai_cfg["rot1"], self.fai_cfg["rot2"], self.fai_cfg["rot3"]))
            if "wavelength" in self.fai_cfg:
                headerLst.append("Wavelength: %s" % self.fai_cfg["wavelength"])
            if "dark_current" in self.fai_cfg:
                headerLst.append("Dark current: %s" % self.fai_cfg["dark_current"])
            if "flat_field" in self.fai_cfg:
                headerLst.append("Flat field: %s" % self.fai_cfg["flat_field"])
            if "polarization_factor" in self.fai_cfg:
                headerLst.append("Polarization factor: %s" % self.fai_cfg["polarization_factor"])
            headerLst.append("")
            if "do_poisson" in self.fai_cfg:
                headerLst.append("%14s %14s %s" % (self.fai_cfg["unit"], "I", "sigma"))
            else:
                headerLst.append("%14s %14s" % (self.fai_cfg["unit"], "I"))
#            headerLst.append("")
            self.header = os.linesep.join([""] + ["# " + i for i in headerLst] + [""])
        self.prefix = lima_cfg.get("prefix", self.prefix)
        self.index_format = lima_cfg.get("index_format", self.index_format)
        self.start_index = lima_cfg.get("start_index", self.start_index)
        if not self.subdir:
            self.directory = lima_cfg.get("directory", self.directory)
        elif self.subdir.startswith("/"):
            self.directory = self.subdir
        else:
            self.directory = os.path.join(lima_cfg.get("directory", self.directory), self.subdir)
        if not os.path.exists(self.directory):
            logger.warning("Output directory: %s does not exist,creating it" % self.directory)
            try:
                os.makedirs(self.directory)
            except Exception as error:
                logger.info("Problem while creating directory %s: %s" % (self.directory, error))


    def write(self, data, index=0):
        filename = os.path.join(self.directory, self.prefix + (self.index_format % (self.start_index + index)) + self.extension)
        if filename:
            with open(filename, "w") as f:
                f.write("# Processing time: %s%s" % (get_isotime(), self.header))
                numpy.savetxt(f, data)

class FabioWriter(Writer):
    """
    Image file writer based on FabIO

    TODO !!!
    """
    def __init__(self, filename=None):
        """

        """
        Writer.__init__(self, filename)
        self.header = None
        self.directory = None
        self.prefix = None
        self.index_format = "%04i"
        self.start_index = 0
        self.fabio_class = None

    def __repr__(self):
        return "Image writer on file %s" % (self.filename)

    def init(self, fai_cfg=None, lima_cfg=None):
        """
        Creates the directory that will host the output file(s)

        """
        Writer.init(self, fai_cfg, lima_cfg)
        with self._sem:
#            dim1_unit = units.to_unit(fai_cfg.get("unit", "r_mm"))
            header_keys = ["dist", "poni1", "poni2", "rot1", "rot2", "rot3",
#                           "chi_min", "chi_max",
#                           dim1_unit.REPR + "_min",
#                           dim1_unit.REPR + "_max",
#                           "pixelX", "pixelY",
#                           "dark", "flat", "polarization_factor", "normalization_factor"
                            ]
            header = {"dist": str(fai_cfg.get("dist")),
                      "poni1": str(fai_cfg.get("poni1")),
                      "poni2": str(fai_cfg.get("poni2")),
                      "rot1": str(fai_cfg.get("rot1")),
                      "rot2": str(fai_cfg.get("rot2")),
                      "rot3": str(fai_cfg.get("rot3")),
#                      "chi_min": str(fai_cfg.get("chi_min")),
#                      "chi_max": str(fai_cfg.get("chi_max")),
#                      dim1_unit.REPR + "_min": str(fai_cfg.get("dist")),
#                      dim1_unit.REPR + "_max": str(fai_cfg.get("dist")),
#                      "pixelX": str(fai_cfg.get("dist")),  # this is not a bug ... most people expect dim1 to be X
#                      "pixelY": str(fai_cfg.get("dist")),  # this is not a bug ... most people expect dim2 to be Y
#                      "polarization_factor": str(fai_cfg.get("dist")),
#                      "normalization_factor":str(fai_cfg.get("dist")),
                      }

#            if self.splineFile:
#                header["spline"] = str(self.splineFile)
#
#            if dark is not None:
#                if self.darkfiles:
#                    header["dark"] = self.darkfiles
#                else:
#                    header["dark"] = 'unknown dark applied'
#            if flat is not None:
#                if self.flatfiles:
#                    header["flat"] = self.flatfiles
#                else:
#                    header["flat"] = 'unknown flat applied'
#            f2d = self.getFit2D()
#            for key in f2d:
#                header["key"] = f2d[key]
        self.prefix = fai_cfg.get("prefix", "")
        self.index_format = fai_cfg.get("index_format", "%04i")
        self.start_index = fai_cfg.get("start_index", 0)
        if not self.subdir:
            self.directory = directory
        elif self.subdir.startswith("/"):
            self.directory = self.subdir
        else:
            self.directory = os.path.join(directory, self.subdir)
        if not os.path.exists(self.directory):
            logger.warning("Output directory: %s does not exist,creating it" % self.directory)
            try:
                os.makedirs(self.directory)
            except Exception as error:
                logger.info("Problem while creating directory %s: %s" % (self.directory, error))


    def write(self, data, index=0):
        filename = os.path.join(self.directory, self.prefix + (self.index_format % (self.start_index + index)) + self.extension)
        if filename:
            with open(filename, "w") as f:
                f.write("# Processing time: %s%s" % (get_isotime(), self.header))
                numpy.savetxt(f, data)


class Nexus(object):
    """
    Writer class to handle Nexus/HDF5 data
    Manages:
    entry
        pyFAI-subentry
            detector

    #TODO: make it thread-safe !!!
    """
    def __init__(self, filename, mode="r"):
        """
        Constructor

        @param filename: name of the hdf5 file containing the nexus
        @param mode: can be r or a
        """
        self.filename = os.path.abspath(filename)
        self.mode = mode
        if not h5py:
            logger.error("h5py module missing: NeXus not supported")
            raise RuntimeError("H5py module is missing")
        if os.path.exists(self.filename) and self.mode == "r":
            self.h5 = h5py.File(self.filename, mode=self.mode)
        else:
            self.h5 = h5py.File(self.filename)
        self.to_close = []

    def close(self):
        """
        close the filename and update all entries
        """
        end_time = get_isotime()
        for entry in self.to_close:
            entry["end_time"] = end_time
        self.h5.close()

    # Context manager for "with" statement compatibility
    def __enter__(self, *arg, **kwarg):
        return self

    def __exit__(self, *arg, **kwarg):
        self.close()

    def get_entry(self, name):
        """
        Retrieves an entry from its name

        @param name: name of the entry to retrieve
        @return: HDF5 group of NXclass == NXentry
        """
        for grp_name in self.h5:
            if  grp_name == name:
                grp = self.h5[grp_name]
                if isinstance(grp, h5py.Group) and \
                    "start_time" in grp and  \
                    "NX_class" in grp.attrs and \
                    grp.attrs["NX_class"] == "NXentry" :
                        return grp

    def get_entries(self):
        """
        retrieves all entry sorted the latest first.

        @return: list of HDF5 groups
        """
        entries = [(grp, from_isotime(self.h5[grp + "/start_time"].value))
                    for grp in self.h5
                    if (isinstance(self.h5[grp], h5py.Group) and \
                        "start_time" in self.h5[grp] and  \
                        "NX_class" in self.h5[grp].attrs and \
                        self.h5[grp].attrs["NX_class"] == "NXentry")]
        entries.sort(key=lambda a: a[1], reverse=True)  # sort entries in decreasing time
        return [self.h5[i[0]] for i in entries]

    def find_detector(self, all=False):
        """
        Tries to find a detector within a NeXus file, takes the first compatible detector

        @param all: return all detectors found as a list
        """
        result = []
        for entry in self.get_entries():
            for instrument in self.get_class(entry, "NXsubentry") + self.get_class(entry, "NXinstrument"):
                for detector in self.get_class(instrument, "NXdetector"):
                    if all:
                        result.append(detector)
                    else:
                        return detector
        return result

    def new_entry(self, entry="entry", program_name="pyFAI", title="description of experiment", force_time=None):
        """
        Create a new entry

        @param entry: name of the entry
        @param program_name: value of the field as string
        @param title: value of the field as string
        @force_time: enforce the start_time (as string!)
        @return: the corresponding HDF5 group
        """
        nb_entries = len(self.get_entries())
        entry_grp = self.h5.require_group("%s_%04i" % (entry, nb_entries))
        entry_grp.attrs["NX_class"] = "NXentry"
        entry_grp["title"] = numpy.string_(title)
        entry_grp["program_name"] = numpy.string_(program_name)
        if force_time:
            entry_grp["start_time"] = numpy.string_(force_time)
        else:
            entry_grp["start_time"] = numpy.string_(get_isotime())
        self.to_close.append(entry_grp)
        return entry_grp

    def new_instrument(self, entry="entry", instrument_name="id00",):
        """
        Create an instrument in an entry or create both the entry and the instrument if
        """
        if not isinstance(entry, h5py.Group):
            entry = self.new_entry(entry)
        return self.new_class(entry, instrument_name, "NXinstrument")
#        howto external link
        # myfile['ext link'] = h5py.ExternalLink("otherfile.hdf5", "/path/to/resource")

    def new_class(self, grp, name, class_type="NXcollection"):
        """
        create a new sub-group with  type class_type
        @param grp: parent group
        @param name: name of the sub-group
        @param class_type: NeXus class name
        @return: subgroup created
        """
        sub = grp.require_group(name)
        sub.attrs["NX_class"] = class_type
        return sub

    def new_detector(self, name="detector", entry="entry", subentry="pyFAI"):
        """
        Create a new entry/pyFAI/Detector

        @param detector: name of the detector
        @param entry: name of the entry
        @param subentry: all pyFAI description of detectors should be in a pyFAI sub-entry
        """
        entry_grp = self.new_entry(entry)
        pyFAI_grp = self.new_class(entry_grp, subentry, "NXsubentry")
        pyFAI_grp["definition_local"] = numpy.string_("pyFAI")
        pyFAI_grp["definition_local"].attrs["version"] = version
        det_grp = self.new_class(pyFAI_grp, name, "NXdetector")
        return det_grp


    def get_class(self, grp, class_type="NXcollection"):
        """
        return all sub-groups of the given type within a group

        @param grp: HDF5 group
        @param class_type: name of the NeXus class
        """
        coll = [grp[name] for name in grp
               if (isinstance(grp[name], h5py.Group) and \
                   "NX_class" in grp[name].attrs and \
                   grp[name].attrs["NX_class"] == class_type)]
        return coll

    def get_data(self, grp, class_type="NXdata"):
        """
        return all dataset of the the NeXus class NXdata

        @param grp: HDF5 group
        @param class_type: name of the NeXus class
        """
        coll = [grp[name] for name in grp
               if (isinstance(grp[name], h5py.Dataset) and \
                   "NX_class" in grp[name].attrs and \
                   grp[name].attrs["NX_class"] == class_type)]
        return coll

    def deep_copy(self, name, obj, where="/", toplevel=None, excluded=None, overwrite=False):
        """
        perform a deep copy:
        create a "name" entry in self containing a copy of the object
        
        @param where: path to the toplevel object (i.e. root)
        @param  toplevel: firectly the top level Group
        @param excluded: list of keys to be excluded
        @param overwrite: replace content if already existing
        """
        if (excluded is not None) and (name in excluded):
            return
        if not toplevel:
            toplevel = self.h5[where]
        if isinstance(obj, h5py.Group):
            if not name in toplevel:
                grp = toplevel.require_group(name)
                for k, v in obj.attrs.items():
                        grp.attrs[k] = v
        elif isinstance(obj, h5py.Dataset):
            if name in toplevel:
                if overwrite:
                    del toplevel[name]
                    logger.warning("Overwriting %s in %s" % (toplevel[name].name, self.filename))
                else:
                    logger.warning("Not overwriting %s in %s" % (toplevel[name].name, self.filename))
                    return
            toplevel[name] = obj.value
            for k, v in obj.attrs.items():
                toplevel[name].attrs[k] = v

