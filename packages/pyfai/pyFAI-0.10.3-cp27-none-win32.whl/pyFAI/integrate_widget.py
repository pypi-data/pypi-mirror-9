#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    Project: Fast Azimuthal integration
#             https://github.com/kif/pyFAI
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
from __future__ import absolute_import, print_function, with_statement, division

"""
pyFAI-integrate

A graphical tool (based on PyQt4) for performing azimuthal integration on series of files.


"""

__author__ = "Jerome Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "13/03/2015"
__satus__ = "development"

import sys
import logging
import json
import os
import time
import types
import threading
import math

import os.path as op
import numpy
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyFAI.integrate_widget")
from .gui_utils import QtCore, QtGui, uic, SIGNAL, QtWebKit

import fabio
from .detectors import ALL_DETECTORS, detector_factory
from .opencl import ocl
from .utils import float_, int_, str_, get_ui_file
from .io import HDF5Writer
from .azimuthalIntegrator import AzimuthalIntegrator
from .third_party import six

UIC = get_ui_file("integration.ui")

FROM_PYMCA = "From PyMca"

class Browser(QtGui.QMainWindow):

    def __init__(self, default_url="http://google.com"):
        """
            Initialize the browser GUI and connect the events
        """
        QtGui.QMainWindow.__init__(self)
        self.resize(800, 600)
        self.centralwidget = QtGui.QWidget(self)

        self.mainLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setMargin(1)

        self.frame = QtGui.QFrame(self.centralwidget)

        self.gridLayout = QtGui.QVBoxLayout(self.frame)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)

        self.horizontalLayout = QtGui.QHBoxLayout()
        self.tb_url = QtGui.QLineEdit(self.frame)
        self.bt_back = QtGui.QPushButton(self.frame)
        self.bt_ahead = QtGui.QPushButton(self.frame)

        self.bt_back.setIcon(QtGui.QIcon().fromTheme("go-previous"))
        self.bt_ahead.setIcon(QtGui.QIcon().fromTheme("go-next"))
        self.horizontalLayout.addWidget(self.bt_back)
        self.horizontalLayout.addWidget(self.bt_ahead)
        self.horizontalLayout.addWidget(self.tb_url)
        self.gridLayout.addLayout(self.horizontalLayout)

        self.html = QtWebKit.QWebView()
        self.gridLayout.addWidget(self.html)
        self.mainLayout.addWidget(self.frame)
        self.setCentralWidget(self.centralwidget)

        self.tb_url.returnPressed.connect(self.browse)
        self.bt_back.clicked.connect(self.html.back)
        self.bt_ahead.clicked.connect(self.html.forward)

        self.default_url = default_url
        self.tb_url.setText(self.default_url)
        self.browse()

    def browse(self):
        """
        Make a web browse on a specific url and show the page on the
        Webview widget.
        """
        print("browse " + self.tb_url.text())
        url = QtCore.QUrl.fromUserInput(self.tb_url.text())
        print(str(url))
#         self.html.setUrl(url)
        self.html.load(url)
#         self.html.show()


class AIWidget(QtGui.QWidget):
    """
    """
    def __init__(self, input_data=None):
        self.ai = AzimuthalIntegrator()
        self.input_data = input_data
        self.output_path = None
        self.output_format = None
        self.slow_dim = None
        self.fast_dim = None
        self.name = None
        self._sem = threading.Semaphore()
        QtGui.QWidget.__init__(self)
        try:
            uic.loadUi(UIC, self)
        except AttributeError as error:
            logger.error("I looks like your installation suffers from this bug: http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=697348")
            raise RuntimeError("Please upgrade your installation of PyQt (or apply the patch)")
        self.all_detectors = list(ALL_DETECTORS.keys())
        self.all_detectors.sort()
        self.detector.addItems([i.capitalize() for i in self.all_detectors])
        self.detector.setCurrentIndex(self.all_detectors.index("detector"))
        # connect file selection windows
        self.connect(self.file_poni, SIGNAL("clicked()"), self.select_ponifile)
        self.connect(self.file_splinefile, SIGNAL("clicked()"), self.select_splinefile)
        self.connect(self.file_mask_file, SIGNAL("clicked()"), self.select_maskfile)
        self.connect(self.file_dark_current, SIGNAL("clicked()"), self.select_darkcurrent)
        self.connect(self.file_flat_field, SIGNAL("clicked()"), self.select_flatfield)
        # connect button bar
        self.okButton = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        self.saveButton = self.buttonBox.button(QtGui.QDialogButtonBox.Save)
        self.resetButton = self.buttonBox.button(QtGui.QDialogButtonBox.Reset)
        self.connect(self.okButton, SIGNAL("clicked()"), self.proceed)
        self.connect(self.saveButton, SIGNAL("clicked()"), self.dump)
        self.connect(self.buttonBox, SIGNAL("helpRequested()"), self.help)
        self.connect(self.buttonBox, SIGNAL("rejected()"), self.die)
        self.connect(self.resetButton, SIGNAL("clicked()"), self.restore)

        self.connect(self.detector, SIGNAL("currentIndexChanged(int)"), self.detector_changed)
        self.connect(self.do_OpenCL, SIGNAL("clicked()"), self.openCL_changed)
        self.connect(self.platform, SIGNAL("currentIndexChanged(int)"), self.platform_changed)
        self.set_validators()
        self.restore()
        self.progressBar.setValue(0)
        self.hdf5_path = None

    def set_validators(self):
        """
        Set all validators for text entries
        """
        npt_validator = QtGui.QIntValidator()
        npt_validator.setBottom(1)
        self.nbpt_rad.setValidator(npt_validator)
        self.nbpt_azim.setValidator(npt_validator)

        wl_validator = QtGui.QDoubleValidator(self)
        wl_validator.setBottom(1e-15)
        wl_validator.setTop(1e-6)
        self.wavelength.setValidator(wl_validator)

        distance_validator = QtGui.QDoubleValidator(self)
        distance_validator.setBottom(0)
        self.pixel1.setValidator(distance_validator)
        self.pixel2.setValidator(distance_validator)
        self.poni1.setValidator(distance_validator)
        self.poni2.setValidator(distance_validator)

        angle_validator = QtGui.QDoubleValidator(self)
        distance_validator.setBottom(-math.pi)
        distance_validator.setTop(math.pi)
        self.rot1.setValidator(angle_validator)
        self.rot2.setValidator(angle_validator)
        self.rot3.setValidator(angle_validator)
        # done at widget level
#        self.polarization_factor.setValidator(QtGui.QDoubleValidator(-1, 1, 3))


    def proceed(self):
        with self._sem:
            out = None
            config = self.dump()
            logger.debug("Let's work a bit")
            self.set_ai()

    #        Default Keyword arguments
            kwarg = {"unit": "2th_deg",
                     "dummy": None,
                     "delta_dummy": None,
                     "polarization_factor":None,
                     "filename": None,
                     "safe": False,
                     }

            if self.q_nm.isChecked():
                kwarg["unit"] = "q_nm^-1"
            elif self.tth_deg.isChecked():
                kwarg["unit"] = "2th_deg"
            elif self.tth_rad.isChecked():
                kwarg["unit"] = "2th_rad"
            elif self.r_mm.isChecked():
                kwarg["unit"] = "r_mm"
            elif self.q_A.isChecked():
                kwarg["unit"] = "q_A^-1"
            else:
                logger.warning("Undefined unit !!! falling back on 2th_deg")

            kwarg["correctSolidAngle"] = bool(self.do_solid_angle.isChecked())

            if bool(self.do_dummy.isChecked()):
                kwarg["dummy"] = float_(self.val_dummy.text())
                delta_dummy = str(self.delta_dummy.text())
                if delta_dummy:
                    kwarg["delta_dummy"] = float(delta_dummy)
                else:
                    kwarg["delta_dummy"] = None
            if bool(self.do_polarization.isChecked()):
                kwarg["polarization_factor"] = float(self.polarization_factor.value())
            else:
                kwarg["polarization_factor"] = None

            nbpt_rad = str(self.nbpt_rad.text()).strip()
            if not nbpt_rad:
#                mb = QtGui.QMessageBox()
#                mb.setText("You must provide the number of output radial bins !")
#
#                icon=QtGui.QMessageBox.Warning, buttons=QtGui.QMessageBox.Warning)
#
#                msgBox.exec_()
                ret = QtGui.QMessageBox.warning(self, "PyFAI integrate",
                                          "You must provide the number of output radial bins !",)
                return {}
                # raise RuntimeError("The number of output point is undefined !")
            kwarg["npt_rad"] = int(str(self.nbpt_rad.text()).strip())
            if self.do_2D.isChecked():
                kwarg["npt_azim"] = int(str(self.nbpt_azim.text()).strip())

            if self.do_OpenCL.isChecked():
                platform = ocl.get_platform(self.platform.currentText())
                pid = platform.id
                did = platform.get_device(self.device.currentText()).id
                if (pid is not None) and (did is not None):
                    kwarg["method"] = "csr_ocl_%i,%i" % (pid, did)
                else:
                    kwarg["method"] = "csr_ocl"
            else:
                if len(self.input_data) > 5:
                    kwarg["method"] = "csr"
                else:
                    kwarg["method"] = "splitbbox"

            if self.do_radial_range.isChecked():
                try:
                    rad_min = float_(self.radial_range_min.text())
                    rad_max = float_(self.radial_range_max.text())
                except ValueError as error:
                    logger.error("error in parsing radial range: %s" % error)
                else:
                    kwarg["radial_range"] = (rad_min, rad_max)
                if kwarg["radial_range"] == (None, None):
                    kwarg["radial_range"] = None

            if self.do_azimuthal_range.isChecked():
                try:
                    azim_min = float_(self.azimuth_range_min.text())
                    azim_max = float_(self.azimuth_range_max.text())
                except ValueError as error:
                    logger.error("error in parsing azimuthal range: %s" % error)
                else:
                    kwarg["azimuth_range"] = (azim_min, azim_max)
                if kwarg["azimuth_range"] == (None, None):
                    kwarg["azimuth_range"] = None
            if self.do_poisson.isChecked():
                kwarg["error_model"] = "poisson"
            else:
                kwarg["error_model"] = None
            logger.info("Parameters for integration:%s%s" % (os.linesep,
                            os.linesep.join(["\t%s:\t%s" % (k, v) for k, v in kwarg.items()])))

            logger.debug("processing %s" % self.input_data)
            start_time = time.time()
            if self.input_data in [None, []]:
                logger.warning("No input data to process")
                return

            elif "ndim" in dir(self.input_data) and (self.input_data.ndim == 3):
                # We have a numpy array of dim3
                if "npt_azim" in kwarg:
                    out = numpy.zeros((self.input_data.shape[0], kwarg["npt_azim"], kwarg["npt_rad"]), dtype=numpy.float32)
                    for i in range(self.input_data.shape[0]):
                        self.progressBar.setValue(100.0 * i / self.input_data.shape[0])
                        kwarg["data"] = self.input_data[i]
                        out[i] = self.ai.integrate2d(**kwarg)[0]

                else:
                    if "npt_rad" in kwarg:  # convert npt_rad -> npt
                            kwarg["npt"] = kwarg.pop("npt_rad")
                    out = numpy.zeros((self.input_data.shape[0], kwarg["npt"]), dtype=numpy.float32)
                    for i in range(self.input_data.shape[0]):
                        self.progressBar.setValue(100.0 * i / self.input_data.shape[0])
                        kwarg["data"] = self.input_data[i]
                        out[i] = self.ai.integrate1d(**kwarg)[1]

            elif "__len__" in dir(self.input_data):
                out = []
                if self.hdf5_path:
                    import h5py
                    hdf5 = h5py.File(self.output_path)
                    if self.fast_dim:
                        if "npt_azim" in kwarg:
                            ds = hdf5.create_dataset("diffraction", (1, self.fast_dim, kwarg["npt_azim"], kwarg["npt_rad"]),
                                                      dtype=numpy.float32,
                                                      chunks=(1, self.fast_dim, kwarg["npt_azim"], kwarg["npt_rad"]),
                                                      maxshape=(None, self.fast_dim, kwarg["npt_azim"], kwarg["npt_rad"]))
                        else:
                            ds = hdf5.create_dataset("diffraction", (1, self.fast_dim, kwarg["npt_rad"]),
                                                      dtype=numpy.float32,
                                                      chunks=(1, self.fast_dim, kwarg["npt_rad"]),
                                                      maxshape=(None, self.fast_dim, kwarg["npt_rad"]))
                    else:
                        if "npt_azim" in kwarg:
                            ds = hdf5.create_dataset("diffraction", (1, kwarg["npt_azim"], kwarg["npt_rad"]),
                                                      dtype=numpy.float32,
                                                      chunks=(1, kwarg["npt_azim"], kwarg["npt_rad"]),
                                                      maxshape=(None, kwarg["npt_azim"], kwarg["npt_rad"]))
                        else:
                            ds = hdf5.create_dataset("diffraction", (1, kwarg["npt_rad"]),
                                                      dtype=numpy.float32,
                                                      chunks=(1, kwarg["npt_rad"]),
                                                      maxshape=(None, kwarg["npt_rad"]))

                for i, item in enumerate(self.input_data):
                    self.progressBar.setValue(100.0 * i / len(self.input_data))
                    logger.debug("processing %s" % item)
                    if isinstance(item, (six.text_type, six.binary_type)) and op.exists(item):
                        fab_img = fabio.open(item)
                        multiframe = (fab_img.nframes > 1)
                        kwarg["data"] = fab_img.data
                        if self.hdf5_path is None:
                            if self.output_path and op.isdir(self.output_path):
                                outpath = op.join(self.output_path, op.splitext(op.basename(item))[0])
                            else:
                                outpath = op.splitext(item)[0]
                            if "npt_azim" in kwarg and not multiframe:
                                kwarg["filename"] = outpath + ".azim"
                            else:
                                kwarg["filename"] = outpath + ".dat"
                    else:
                        logger.warning("item is not a file ... guessing it is a numpy array")
                        kwarg["data"] = item
                        kwarg["filename"] = None
                        multiframe = False
                    if multiframe:
                        if kwarg["filename"]:
                            outpath = op.splitext(kwarg["filename"])[0]
                        kwarg["filename"] = None
                        writer = HDF5Writer(outpath + "_pyFAI.h5")
                        writer.init(config)
                        for i in range(fab_img.nframes):
                            kwarg["data"] = fab_img.getframe(i).data
                            radial = None
                            azimuthal = None
                            if "npt_azim" in kwarg:
                                res = self.ai.integrate2d(**kwarg)
                            else:
                                if "npt_rad" in kwarg:  # convert npt_rad -> npt
                                    kwarg["npt"] = kwarg.pop("npt_rad")
                                res = self.ai.integrate1d(**kwarg)
                            writer.write(res, index=i)
                        writer.close()
                    else:
                        if kwarg.get("npt_azim"):
                            res = self.ai.integrate2d(**kwarg)
                        else:
                            if "npt_rad" in kwarg:  # convert npt_rad -> npt
                                kwarg["npt"] = kwarg.pop("npt_rad")
                            res = self.ai.integrate1d(**kwarg)
                    out.append(res)

                    #TODO manage HDF5 stuff !!!
            logger.info("Processing Done in %.3fs !" % (time.time() - start_time))
            self.progressBar.setValue(100)
        self.die()
        return out

    def die(self):
        logger.debug("bye bye")
        self.deleteLater()

    def help(self):
        logger.debug("Please, help")
        self.help_browser = Browser("http://pyfai.readthedocs.org/en/latest/pyFAI.html")
        self.help_browser.show()

    def dump(self, filename=".azimint.json"):
        """
        Dump the status of the current widget to a file in JSON

        @param filename: path where to save the config
        @type filename: str

        """
        logger.info("Dump!")
        to_save = { "poni": str(self.poni.text()).strip(),
                    "detector": str(self.detector.currentText()).lower(),
                    "wavelength":float_(self.wavelength.text()),
                    "splineFile":str(self.splineFile.text()).strip(),
                    "pixel1": float_(self.pixel1.text()),
                    "pixel2":float_(self.pixel2.text()),
                    "dist":float_(self.dist.text()),
                    "poni1":float_(self.poni1.text()),
                    "poni2":float_(self.poni2.text()),
                    "rot1":float_(self.rot1.text()),
                    "rot2":float_(self.rot2.text()),
                    "rot3":float_(self.rot3.text()),
                    "do_dummy": bool(self.do_dummy.isChecked()),
                    "do_mask":  bool(self.do_mask.isChecked()),
                    "do_dark": bool(self.do_dark.isChecked()),
                    "do_flat": bool(self.do_flat.isChecked()),
                    "do_polarization":bool(self.do_polarization.isChecked()),
                    "val_dummy":float_(self.val_dummy.text()),
                    "delta_dummy":float_(self.delta_dummy.text()),
                    "mask_file":str(self.mask_file.text()).strip(),
                    "dark_current":str(self.dark_current.text()).strip(),
                    "flat_field":str(self.flat_field.text()).strip(),
                    "polarization_factor":float_(self.polarization_factor.value()),
                    "nbpt_rad":int_(self.nbpt_rad.text()),
                    "do_2D":bool(self.do_2D.isChecked()),
                    "nbpt_azim":int_(self.nbpt_azim.text()),
                    "chi_discontinuity_at_0": bool(self.chi_discontinuity_at_0.isChecked()),
                    "do_solid_angle": bool(self.do_solid_angle.isChecked()),
                    "do_radial_range": bool(self.do_radial_range.isChecked()),
                    "do_azimuthal_range": bool(self.do_azimuthal_range.isChecked()),
                    "do_poisson": bool(self.do_poisson.isChecked()),
                    "radial_range_min":float_(self.radial_range_min.text()),
                    "radial_range_max":float_(self.radial_range_max.text()),
                    "azimuth_range_min":float_(self.azimuth_range_min.text()),
                    "azimuth_range_max":float_(self.azimuth_range_max.text()),
                   }
        if self.q_nm.isChecked():
            to_save["unit"] = "q_nm^-1"
        elif self.q_A.isChecked():
            to_save["unit"] = "q_A^-1"
        elif self.tth_deg.isChecked():
            to_save["unit"] = "2th_deg"
        elif self.tth_rad.isChecked():
            to_save["unit"] = "2th_rad"
        elif self.r_mm.isChecked():
            to_save["unit"] = "r_mm"
        try:
            with open(filename, "w") as myFile:
                json.dump(to_save, myFile, indent=4)
        except IOError as error:
            logger.error("Error while saving config: %s" % error)
        else:
            logger.debug("Saved")
        return to_save

    def restore(self, filename=".azimint.json"):
        """
        restore from JSON file the status of the current widget

        @param filename: path where the config was saved
        @type filename: str

        """
        logger.debug("Restore")
        if not op.isfile(filename):
            logger.error("No such file: %s" % filename)
            return
        data = json.load(open(filename))
        setup_data = {  "poni": self.poni.setText,
#        "detector": self.all_detectors[self.detector.getCurrentIndex()],
                        "wavelength":lambda a:self.wavelength.setText(str_(a)),
                        "splineFile":lambda a:self.splineFile.setText(str_(a)),
                        "pixel1":lambda a: self.pixel1.setText(str_(a)),
                        "pixel2":lambda a:self.pixel2.setText(str_(a)),
                        "dist":lambda a:self.dist.setText(str_(a)),
                        "poni1":lambda a:self.poni1.setText(str_(a)),
                        "poni2":lambda a:self.poni2.setText(str_(a)),
                        "rot1":lambda a:self.rot1.setText(str_(a)),
                        "rot2":lambda a:self.rot2.setText(str_(a)),
                        "rot3":lambda a:self.rot3.setText(str_(a)),
                        "do_dummy": self.do_dummy.setChecked,
                        "do_dark": self.do_dark.setChecked,
                        "do_flat": self.do_flat.setChecked,
                        "do_polarization": self.do_polarization.setChecked,
                        "val_dummy":lambda a: self.val_dummy.setText(str_(a)),
                        "delta_dummy":lambda a: self.delta_dummy.setText(str_(a)),
                        "do_mask":  self.do_mask.setChecked,
                        "mask_file":lambda a:self.mask_file.setText(str_(a)),
                        "dark_current":lambda a:self.dark_current.setText(str_(a)),
                        "flat_field":lambda a:self.flat_field.setText(str_(a)),
                        "polarization_factor":self.polarization_factor.setValue,
                        "nbpt_rad":lambda a:self.nbpt_rad.setText(str_(a)),
                        "do_2D":self.do_2D.setChecked,
                        "nbpt_azim":lambda a:self.nbpt_azim.setText(str_(a)),
                        "chi_discontinuity_at_0": self.chi_discontinuity_at_0.setChecked,
                        "do_radial_range": self.do_radial_range.setChecked,
                        "do_azimuthal_range": self.do_azimuthal_range.setChecked,
                        "do_poisson": self.do_poisson.setChecked,
                        "radial_range_min":lambda a:self.radial_range_min.setText(str_(a)),
                        "radial_range_max":lambda a:self.radial_range_max.setText(str_(a)),
                        "azimuth_range_min":lambda a:self.azimuth_range_min.setText(str_(a)),
                        "azimuth_range_max":lambda a:self.azimuth_range_max.setText(str_(a)),
                        "do_solid_angle": self.do_solid_angle.setChecked,
                   }
        for key, value in setup_data.items():
            if key in data:
                value(data[key])
        if "unit" in data:
            unit = data["unit"].lower()
            if unit == "q_nm^-1":
                self.q_nm.setChecked(1)
            elif unit == "q_A^-1":
                self.q_A.setChecked(1)
            elif unit == "2th_deg":
                self.tth_deg.setChecked(1)
            elif unit == "2th_rad":
                self.tth_rad.setChecked(1)
            elif unit == "r_mm":
                self.r_mm.setChecked(1)
        if "detector" in data:
            detector = data["detector"].lower()
            if detector in self.all_detectors:
                self.detector.setCurrentIndex(self.all_detectors.index(detector))

    def select_ponifile(self):
        ponifile = QtGui.QFileDialog.getOpenFileName()
        self.poni.setText(ponifile)
        self.set_ponifile(ponifile)

    def select_splinefile(self):
        logger.debug("select_splinefile")
        splinefile = str(QtGui.QFileDialog.getOpenFileName())
        if splinefile:
            try:
                self.ai.detector.set_splineFile(splinefile)
                self.pixel1.setText(str(self.ai.pixel1))
                self.pixel2.setText(str(self.ai.pixel2))
                self.splineFile.setText(self.ai.detector.splineFile or "")
            except Exception as error:
                logger.error("failed %s on %s" % (error, splinefile))

    def select_maskfile(self):
        logger.debug("select_maskfile")
        maskfile = str(QtGui.QFileDialog.getOpenFileName())
        if maskfile:
            self.mask_file.setText(maskfile or "")
            self.do_mask.setChecked(True)

    def select_darkcurrent(self):
        logger.debug("select_darkcurrent")
        darkcurrent = str(QtGui.QFileDialog.getOpenFileName())
        if darkcurrent:
            self.dark_current.setText(str_(darkcurrent))
            self.do_dark.setChecked(True)

    def select_flatfield(self):
        logger.debug("select_flatfield")
        flatfield = str(QtGui.QFileDialog.getOpenFileName())
        if flatfield:
            self.flat_field.setText(str_(flatfield))
            self.do_flat.setChecked(True)

    def set_ponifile(self, ponifile=None):
        if ponifile is None:
            ponifile = self.poni.text()
        try:
            self.ai = AzimuthalIntegrator.sload(ponifile)
        except Exception as error:
            logger.error("file %s does not look like a poni-file, error %s" % (ponifile, error))
            return
        self.pixel1.setText(str_(self.ai.pixel1))
        self.pixel2.setText(str_(self.ai.pixel2))
        self.dist.setText(str_(self.ai.dist))
        self.poni1.setText(str_(self.ai.poni1))
        self.poni2.setText(str_(self.ai.poni2))
        self.rot1.setText(str_(self.ai.rot1))
        self.rot2.setText(str_(self.ai.rot2))
        self.rot3.setText(str_(self.ai.rot3))
        self.splineFile.setText(str_(self.ai.detector.splineFile))
        self.wavelength.setText(str_(self.ai._wavelength))
        name = self.ai.detector.name.lower()
        if name in self.all_detectors:
            self.detector.setCurrentIndex(self.all_detectors.index(name))
        else:
            self.detector.setCurrentIndex(self.all_detectors.index("detector"))

    def set_input_data(self, stack, stack_name=None):
        self.input_data = stack
        self.name = stack_name
    setStackDataObject = set_input_data

    def setSelectionMask(self, mask=None):
        """
        PyMca Plugin specific

        @param mask: 2D array with the masked region

        """
        if (mask is not None) and (mask.sum() > 0):
            self.ai.mask = mask
            self.do_mask.setChecked(True)
            self.mask_file.setText(FROM_PYMCA)

    def setBackgroundImage(self, dark=None):
        """
        PyMca Plugin specific

        @param dark: 2D array with the dark-current

        """
        if (dark is not None) and (dark.sum() > 0):
            self.ai.darkcurrent = dark
            self.do_dark.setChecked(True)
            self.dark_current.setText(FROM_PYMCA)

    def _float(self, kw, default=0):
        fval = default
        txtval = str(self.__dict__[kw].text())
        if txtval:
            try:
                fval = float(txtval)
            except ValueError:
                logger.error("Unable to convert %s to float: %s" % (kw, txtval))
        return fval

    def set_ai(self):
        poni = str(self.poni.text()).strip()
        if poni and op.isfile(poni):
            self.ai = AzimuthalIntegrator.sload(poni)
        detector = str(self.detector.currentText()).lower().strip() or "detector"
        self.ai.detector = detector_factory(detector)

        wavelength = str(self.wavelength.text()).strip()
        if wavelength:
            try:
                fwavelength = float(wavelength)
            except ValueError:
                logger.error("Unable to convert wavelength to float: %s" % wavelength)
            else:
                if fwavelength <= 0 or fwavelength > 1e-6:
                    logger.warning("Wavelength is in meter ... unlikely value %s" % fwavelength)
                self.ai.wavelength = fwavelength

        splineFile = str(self.splineFile.text()).strip()
        if splineFile and op.isfile(splineFile):
            self.ai.detector.splineFile = splineFile

        self.ai.pixel1 = self._float("pixel1", 1)
        self.ai.pixel2 = self._float("pixel2", 1)
        self.ai.dist = self._float("dist", 1)
        self.ai.poni1 = self._float("poni1", 0)
        self.ai.poni2 = self._float("poni2", 0)
        self.ai.rot1 = self._float("rot1", 0)
        self.ai.rot2 = self._float("rot2", 0)
        self.ai.rot3 = self._float("rot3", 0)

        if self.chi_discontinuity_at_0.isChecked():
            self.ai.setChiDiscAtZero()

        mask_file = str(self.mask_file.text()).strip()
        if mask_file  and bool(self.do_mask.isChecked()):
            if op.exists(mask_file):
                try:
                    mask = fabio.open(mask_file).data
                except Exception as error:
                    logger.error("Unable to load mask file %s, error %s" % (mask_file, error))
                else:
                    self.ai.mask = mask
#            elif mask_file==FROM_PYMCA:
#                self.ai.mask = mask
        dark_files = [i.strip() for i in str(self.dark_current.text()).split(",")
                      if op.isfile(i.strip())]
        if dark_files and bool(self.do_dark.isChecked()):
            self.ai.set_darkfiles(dark_files)

        flat_files = [i.strip() for i in str(self.flat_field.text()).split(",")
                      if op.isfile(i.strip())]
        if flat_files and bool(self.do_flat.isChecked()):
            self.ai.set_flatfiles(flat_files)

    def detector_changed(self):
        logger.debug("detector_changed")
        detector = str(self.detector.currentText()).lower()
        inst = detector_factory(detector)
        if inst.force_pixel:
            self.pixel1.setText(str(inst.pixel1))
            self.pixel2.setText(str(inst.pixel2))
            self.splineFile.setText("")
        elif self.splineFile.text():
            splineFile = str(self.splineFile.text()).strip()
            if op.isfile(splineFile):
                inst.set_splineFile(splineFile)
                self.pixel1.setText(str(inst.pixel1))
                self.pixel2.setText(str(inst.pixel2))
            else:
                logger.warning("No such spline file %s" % splineFile)
        self.ai.detector = inst

    def openCL_changed(self):
        logger.debug("do_OpenCL")
        do_ocl = bool(self.do_OpenCL.isChecked())
        if do_ocl:
            if ocl is None:
                self.do_OpenCL.setChecked(0)
                return
            if self.platform.count() == 0:
                self.platform.addItems([i.name for i in ocl.platforms])

    def platform_changed(self):
        logger.debug("platform_changed")
        if ocl is None:
            self.do_OpenCL.setChecked(0)
            return
        platform = ocl.get_platform(str(self.platform.currentText()))
        for i in range(self.device.count())[-1::-1]:
            self.device.removeItem(i)
        self.device.addItems([i.name for i in platform.devices])


