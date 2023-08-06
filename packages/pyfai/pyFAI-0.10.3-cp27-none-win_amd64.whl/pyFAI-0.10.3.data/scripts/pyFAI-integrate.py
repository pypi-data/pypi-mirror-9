#!C:\Python27\python.exe
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

"""
pyFAI-integrate

A graphical tool (based on PyQt4) for performing azimuthal integration on series of files.


"""

__author__ = "Jerome Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20/03/2015"
__satus__ = "production"
import sys, logging, json, os, time, types, threading
import os.path as op
import numpy
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyFAI")
import pyFAI, fabio
from pyFAI.opencl import ocl
import pyFAI.utils
from pyFAI.integrate_widget import AIWidget
try:
    from argparse import ArgumentParser
except ImportError:
    from pyFAI.third_party.argparse import ArgumentParser

try:
    from rfoo.utils import rconsole
    rconsole.spawn_server()
    logger.debug("Socket opened for debugging using rfoo")
except ImportError:
    logger.debug("No socket opened for debugging -> please install rfoo")


window = None

if __name__ == "__main__":
    usage = "pyFAI-integrate [options] file1.edf file2.edf ..."
    version = "pyFAI-integrate version %s from %s" % (pyFAI.version, pyFAI.date)
    description = """
    PyFAI-integrate is a graphical interface (based on Python/Qt4) to perform azimuthal integration
on a set of files. It exposes most of the important options available within pyFAI and allows you
to select a GPU (or an openCL platform) to perform the calculation on."""
    epilog = """PyFAI-integrate saves all parameters in a .azimint.json (hidden) file. This JSON file
is an ascii file which can be edited and used to configure online data analysis using
the LImA plugin of pyFAI.

Nota: there is bug in debian6 making the GUI crash (to be fixed inside pyqt)
http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=697348"""
    parser = ArgumentParser(usage=usage, description=description, epilog=epilog)
    parser.add_argument("-V", "--version", action='version', version=version)
    parser.add_argument("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="switch to verbose/debug mode")
    parser.add_argument("-o", "--output",
                      dest="output", default=None,
                      help="Directory or file where to store the output data")
    parser.add_argument("-f", "--format",
                      dest="format", default=None,
                      help="output data format (can be HDF5)")
    parser.add_argument("-s", "--slow-motor",
                      dest="slow", default=None,
                      help="Dimension of the scan on the slow direction (makes sense only with HDF5)")
    parser.add_argument("-r", "--fast-motor",
                      dest="rapid", default=None,
                      help="Dimension of the scan on the fast direction (makes sense only with HDF5)")
    parser.add_argument("--no-gui",
                      dest="gui", default=True, action="store_false",
                      help="Process the dataset without showing the user interface.")
    parser.add_argument("args", metavar='FILE', type=str, nargs='*',
                        help="Files to be integrated")
    options = parser.parse_args()

    # Analyse arguments and options
    args = pyFAI.utils.expand_args(options.args)
#        if len(args) != 1:
#            parser.error("incorrect number of arguments")
    if options.verbose:
        logger.info("setLevel: debug")
        logger.setLevel(logging.DEBUG)
    if options.gui:
        from PyQt4 import QtCore, QtGui, uic
        app = QtGui.QApplication([])
        if not args:
            dia = QtGui.QFileDialog(directory=os.getcwd())
            dia.setFileMode(QtGui.QFileDialog.ExistingFiles)
            dia.exec_()
            args = [str(i) for i in  dia.selectedFiles()]

        window = AIWidget()
        window.set_input_data(args)
        window.show()
        sys.exit(app.exec_())
    else:
        # TODO
        raise NotImplemented
