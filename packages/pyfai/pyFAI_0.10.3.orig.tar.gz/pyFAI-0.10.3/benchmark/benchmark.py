#!/usr/bin/python
# coding: utf-8
# author: Jérôme Kieffer
# Benchmark for Azimuthal integration of PyFAI

from __future__ import print_function, division

import json
import sys
import time
import timeit
import os
import platform
import subprocess
import numpy
import fabio
import os.path as op
import logging
sys.path.append(op.join(op.dirname(op.dirname(op.abspath(__file__))), "test"))
import utilstest

try:
    from rfoo.utils import rconsole
    rconsole.spawn_server()
except ImportError:
    print("No socket opened for debugging -> please install rfoo")

# We use the locally build version of PyFAI
pyFAI = utilstest.UtilsTest.pyFAI
ocl = pyFAI.opencl.ocl
from pyFAI.gui_utils import pylab, update_fig

ds_list = ["Pilatus1M.poni", "halfccd.poni", "Frelon2k.poni", "Pilatus6M.poni", "Mar3450.poni", "Fairchild.poni"]
datasets = {"Fairchild.poni": utilstest.UtilsTest.getimage("1880/Fairchild.edf"),
            "halfccd.poni": utilstest.UtilsTest.getimage("1882/halfccd.edf"),
            "Frelon2k.poni": utilstest.UtilsTest.getimage("1881/Frelon2k.edf"),
            "Pilatus6M.poni": utilstest.UtilsTest.getimage("1884/Pilatus6M.cbf"),
            "Pilatus1M.poni": utilstest.UtilsTest.getimage("1883/Pilatus1M.edf"),
            "Mar3450.poni": utilstest.UtilsTest.getimage("2201/LaB6_260210.mar3450")
            }

# Handle to the Bench instance: allows debugging from outside if needed
bench = None


class Bench(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    LABELS = {"splitBBox": "CPU_serial",
          "lut": "CPU_LUT_OpenMP",
          "lut_ocl": "%s_LUT_OpenCL",
          "csr": "CPU_CSR_OpenMP",
          "csr_ocl": "%s_CSR_OpenCL",
          }

    def __init__(self, nbr=10, repeat=1, memprofile=False, unit="2th_deg"):
        self.reference_1d = {}
        self.LIMIT = 8
        self.repeat = repeat
        self.nbr = nbr
        self.results = {}
        self.meth = []
        self._cpu = None
        self.fig = None
        self.ax = None
        self.starttime = time.time()
        self.plot = None
        self.plot_x = []
        self.plot_y = []
        self.do_memprofile = memprofile
        self.fig_mp = None
        self.ax_mp = None
        self.plot_mp = None
        self.memory_profile = ([], [])
        self.unit = unit
        self.out_2d = (500, 360)
        self.setup = """import pyFAI,fabio
ai=pyFAI.load(r"%s")
data = fabio.open(r"%s").data
"""
        self.setup_1d = self.setup + "N=min(data.shape)" + os.linesep
        self.setup_2d = self.setup + "N=(%i,%i)%s" % (self.out_2d[0], self.out_2d[0], os.linesep)
        self.stmt_1d = "ai.integrate1d(data, N, safe=False, unit='" + self.unit + "', method='%s')"
        self.stmt_2d = ("ai.integrate2d(data, %i, %i, unit='" % self.out_2d) + self.unit + "', method='%s')"

    def get_cpu(self):
        if self._cpu is None:
            if os.name == "nt":
                self._cpu = platform.processor()
            elif os.path.exists("/proc/cpuinfo"):
                cpuinfo = [i.split(": ", 1)[1] for i in open("/proc/cpuinfo") if i.startswith("model name")]
                if not cpuinfo:
                    cpuinfo = [i.split(": ", 1)[1] for i in open("/proc/cpuinfo") if i.startswith("cpu")]
                self._cpu = cpuinfo[0].strip()
            elif os.path.exists("/usr/sbin/sysctl"):
                proc = subprocess.Popen(["sysctl", "-n", "machdep.cpu.brand_string"], stdout=subprocess.PIPE)
                proc.wait()
                self._cpu = proc.stdout.read().strip()
            old = self._cpu
            self._cpu = old.replace("  ", " ")
            while old != self._cpu:
                old = self._cpu
                self._cpu = old.replace("  ", " ")
        return self._cpu

    def get_gpu(self, devicetype="gpu", useFp64=False, platformid=None, deviceid=None):
        if ocl is None:
            return "NoGPU"
        ctx = ocl.create_context(devicetype, useFp64, platformid, deviceid)
        return ctx.devices[0].name

    def get_mem(self):
        """
        Returns the occupied memory for memory-leak hunting in MByte
        """
        pid = os.getpid()
        if os.path.exists("/proc/%i/status" % pid):
            for l in open("/proc/%i/status" % pid):
                if l.startswith("VmRSS"):
                    mem = int(l.split(":", 1)[1].split()[0]) / 1024.
        else:
            mem = 0
        return mem

    def print_init(self, t):
        print(" * Initialization time: %.1f ms" % (1000.0 * t))
        self.update_mp()

    def print_exec(self, t):
        print(" * Execution time rep : %.1f ms" % (1000.0 * t))
        self.update_mp()

    def print_sep(self):
        print("*" * 80)
        self.update_mp()

    def get_ref(self, param):
        if param not in self.reference_1d:
            fn = datasets[param]
            setup = self.setup_1d % (param, fn)
            exec setup
            res = eval(self.stmt_1d % ("splitBBox"))
            self.reference_1d[param] = res
            del ai, data
        return self.reference_1d[param]

    def bench_1d(self, method="splitBBox", check=False, opencl=None):
        """
        @param method: method to be bechmarked
        @param check: check results vs ref if method is LUT based
        @param opencl: dict containing platformid, deviceid and devicetype
        """
        self.update_mp()
        if opencl:
            if (ocl is None):
                print("No pyopencl")
                return
            if (opencl.get("platformid") is None) or (opencl.get("deviceid") is None):
                platdev = ocl.select_device(opencl.get("devicetype"))
                if not platdev:
                    print("No such OpenCL device: skipping benchmark")
                    return
                platformid, deviceid = opencl["platformid"], opencl["deviceid"] = platdev
            else:
                platformid, deviceid = opencl["platformid"], opencl["deviceid"]
            devicetype = opencl["devicetype"] = ocl.platforms[platformid].devices[deviceid].type
            print("Working on device: %s platform: %s device: %s" % (devicetype, ocl.platforms[platformid], ocl.platforms[platformid].devices[deviceid]))
            label = "1D_" + (self.LABELS[method] % devicetype)
            method += "_%i,%i" % (opencl["platformid"], opencl["deviceid"])
            memory_error = (pyFAI.opencl.pyopencl.MemoryError, MemoryError, pyFAI.opencl.pyopencl.RuntimeError, RuntimeError)
        else:
            print("Working on processor: %s" % self.get_cpu())
            label = "1D_" + self.LABELS[method]
            memory_error = (MemoryError, RuntimeError)
        results = {}
        first = True
        for param in ds_list:
            self.update_mp()
            fn = datasets[param]
            setup = self.setup_1d % (param, fn)
            stmt = self.stmt_1d % method
            exec setup
            size = data.size / 1.0e6
            print("1D integration of %s %.1f Mpixel -> %i bins" % (op.basename(fn), size, N))
            try:
                t0 = time.time()
                res = eval(stmt)
                self.print_init(time.time() - t0)
            except memory_error as error:
                print(error)
                break
            self.update_mp()
            if check:
                if "lut" in method:
                    try:
                        print("lut: shape= %s \t nbytes %.3f MB " % (ai._lut_integrator.lut.shape, ai._lut_integrator.lut_nbytes / 2 ** 20))
                    except MemoryError as error:
                        print(error)
                elif "csr" in method:
                    try:
                        print("csr: size= %s \t nbytes %.3f MB " % (ai._csr_integrator.data.size, ai._csr_integrator.lut_nbytes / 2 ** 20))
                    except MemoryError as error:
                        print(error)

            del ai, data
            self.update_mp()
            try:
                t = timeit.Timer(stmt, setup + stmt)
                tmin = min([i / self.nbr for i in t.repeat(repeat=self.repeat, number=self.nbr)])
            except memory_error as error:
                print(error)
                break
            self.update_mp()
            self.print_exec(tmin)
            tmin *= 1000.0
            if check:
                ref = self.get_ref(param)
                R = utilstest.Rwp(res, ref)
                print("%sResults are bad with R=%.3f%s" % (self.WARNING, R, self.ENDC) if R > self.LIMIT else"%sResults are good with R=%.3f%s" % (self.OKGREEN, R, self.ENDC))
                self.update_mp()
                if R < self.LIMIT:
                    results[size] = tmin
                    self.update_mp()
                    if first:
                        if opencl:
                            self.new_curve(results, label, style="--")
                        else:
                            self.new_curve(results, label, style="-")
                        first = False
                    else:
                        self.new_point(size, tmin)
            else:
                results[size] = tmin
                if first:
                    self.new_curve(results, label)
                    first = False
                else:
                    self.new_point(size, tmin)
        self.print_sep()
        self.meth.append(label)
        self.results[label] = results
        self.update_mp()

    def bench_2d(self, method="splitBBox", check=False, opencl=None):
        self.update_mp()
        if opencl:
            if (ocl is None):
                print("No pyopencl")
                return
            if (opencl.get("platformid") is None) or (opencl.get("deviceid") is None):
                platdev = ocl.select_device(opencl.get("devicetype"))
                if not platdev:
                    print("No such OpenCL device: skipping benchmark")
                    return
                platformid, deviceid = opencl["platformid"], opencl["deviceid"] = platdev
            devicetype = opencl["devicetype"] = ocl.platforms[platformid].devices[deviceid].type
            print("Working on device: %s platform: %s device: %s" % (devicetype, ocl.platforms[platformid], ocl.platforms[platformid].devices[deviceid]))
            method += "_%i,%i" % (opencl["platformid"], opencl["deviceid"])
            label = "2D_%s_parallel_OpenCL" % devicetype
            memory_error = (pyFAI.opencl.pyopencl.MemoryError, MemoryError, pyFAI.opencl.pyopencl.RuntimeError, RuntimeError)

        else:
            print("Working on processor: %s" % self.get_cpu())
            label = "2D_" + self.LABELS[method]
            memory_error = (MemoryError, RuntimeError)

        results = {}
        first = True
        for param in ds_list:
            self.update_mp()
            fn = datasets[param]
            setup = self.setup_2d % (param, fn)
            stmt = self.stmt_2d % method
            exec setup
            size = data.size / 1.0e6
            print("2D integration of %s %.1f Mpixel -> %s bins" % (op.basename(fn), size, N))
            try:
                t0 = time.time()
                res = eval(stmt)
                self.print_init(time.time() - t0)
            except memory_error as error:
                print(error)
                break
            self.update_mp()
            if check:
                print("lut.shape= %s \t lut.nbytes %.3f MB " % (ai._lut_integrator.lut.shape, ai._lut_integrator.size * 8.0 / 1e6))
            ai.reset()
            del ai, data
            try:
                t = timeit.Timer(stmt, setup + stmt)
                tmin = min([i / self.nbr for i in t.repeat(repeat=self.repeat, number=self.nbr)])
            except memory_error as error:
                print(error)
                break
            self.update_mp()
            del t
            self.update_mp()
            self.print_exec(tmin)
            tmin *= 1000.0
            results[size] = tmin
            if first:
                self.new_curve(results, label)
                first = False
            else:
                self.new_point(size, tmin)
            self.update_mp()
        self.print_sep()
        self.meth.append(label)
        self.results[label] = results
        self.update_mp()

    def bench_gpu1d(self, devicetype="gpu", useFp64=True, platformid=None, deviceid=None):
        self.update_mp()
        print("Working on %s, in " % devicetype + ("64 bits mode" if useFp64 else"32 bits mode") + "(%s.%s)" % (platformid, deviceid))
        if ocl is None or not ocl.select_device(devicetype):
            print("No pyopencl or no such device: skipping benchmark")
            return
        results = {}
        label = "Forward_OpenCL_%s_%s_bits" % (devicetype, ("64" if useFp64 else"32"))
        first = True
        for param in ds_list:
            self.update_mp()
            fn = datasets[param]
            ai = pyFAI.load(param)
            data = fabio.open(fn).data
            size = data.size
            N = min(data.shape)
            print("1D integration of %s %.1f Mpixel -> %i bins (%s)" % (op.basename(fn), size / 1e6, N, ("64 bits mode" if useFp64 else"32 bits mode")))

            try:
                t0 = time.time()
                res = ai.xrpd_OpenCL(data, N, devicetype=devicetype, useFp64=useFp64, platformid=platformid, deviceid=deviceid)
                t1 = time.time()
            except Exception as error:
                print("Failed to find an OpenCL GPU (useFp64:%s) %s" % (useFp64, error))
                continue
            self.print_init(t1 - t0)
            self.update_mp()
            ref = ai.xrpd(data, N)
            R = utilstest.Rwp(res, ref)
            print("%sResults are bad with R=%.3f%s" % (self.WARNING, R, self.ENDC) if R > self.LIMIT else"%sResults are good with R=%.3f%s" % (self.OKGREEN, R, self.ENDC))
            setup = """
import pyFAI,fabio
ai=pyFAI.load(r"%s")
data = fabio.open(r"%s").data
N=min(data.shape)
out=ai.xrpd_OpenCL(data,N, devicetype=r"%s", useFp64=%s, platformid=%s, deviceid=%s)""" % (param, fn, devicetype, useFp64, platformid, deviceid)
            t = timeit.Timer("ai.xrpd_OpenCL(data,N,safe=False)", setup)
            tmin = min([i / self.nbr for i in t.repeat(repeat=self.repeat, number=self.nbr)])
            del t
            self.update_mp()
            self.print_exec(tmin)
            print("")
            if R < self.LIMIT:
                size /= 1e6
                tmin *= 1000.0
                results[size] = tmin
                if first:
                    self.new_curve(results, label)
                    first = False
                else:
                    self.new_point(size, tmin)
                self.update_mp()
        self.print_sep()
        self.meth.append(label)
        self.results[label] = results
        self.update_mp()

    def save(self, filename="benchmark.json"):
        self.update_mp()
        json.dump(self.results, open(filename, "w"), indent=4)

    def print_res(self):
        self.update_mp()
        print("Summary: execution time in milliseconds")
        print("Size/Meth\t" + "\t".join(self.meth))
        for i in self.size:
            print("%7.2f\t\t" % i + "\t\t".join("%.2f" % (self.results[j].get(i, 0)) for j in self.meth))

    def init_curve(self):
        self.update_mp()
        if self.fig:
            print("Already initialized")
            return
        if (sys.platform in ["win32", "darwin"]) or ("DISPLAY" in os.environ):
            self.fig = pylab.figure()
            self.fig.show()
            self.ax = self.fig.add_subplot(1, 1, 1)
            self.ax.set_autoscale_on(False)
            self.ax.set_xlabel("Image size in Mega-Pixels")
            self.ax.set_ylabel("Frames processed per second")
            self.ax.set_yscale("log", basey=2)
            t = [1, 2, 5, 10, 20, 50, 100, 200, 400, 500]
            self.ax.set_yticks([float(i) for i in t])
            self.ax.set_yticklabels([str(i)for i in t])
            self.ax.set_xlim(0.5, 17)
            self.ax.set_ylim(0.5, 500)
            self.ax.set_title(self.get_cpu() + " / " + self.get_gpu())
            update_fig(self.fig)

    def new_curve(self, results, label, style="-"):
        """
        Create a new curve within the current graph

        @param results: dict with execution time in function of size
        @param label: string with the title of the curve
        @param style: the style of the line: "-" for plain line, "--" for dashed
        """
        self.update_mp()
        if not self.fig:
            return
        self.plot_x = list(results.keys())
        self.plot_x.sort()
        self.plot_y = [1000.0 / results[i] for i in self.plot_x]
        self.plot = self.ax.plot(self.plot_x, self.plot_y, "o" + style, label=label)[0]
        self.ax.legend()
        update_fig(self.fig)

    def new_point(self, size, exec_time):
        """
        Add new point to current curve

        @param size: of the system
        @parm exec_time: execution time in ms
        """
        self.update_mp()
        if not self.plot:
            return

        self.plot_x.append(size)
        self.plot_y.append(1000.0 / exec_time)
        self.plot.set_data(self.plot_x, self.plot_y)
        update_fig(self.fig)

    def display_all(self):
        if not self.fig:
            return
        for k in self.meth:
            self.new_curve(self.results[k], k)
        self.ax.legend()
        self.fig.savefig("benchmark.png")
        self.fig.show()
#        plt.ion()


    def update_mp(self):
        """
        Update memory profile curve
        """
        if not self.do_memprofile:
            return
        self.memory_profile[0].append(time.time() - self.starttime)
        self.memory_profile[1].append(self.get_mem())
        if not self.fig_mp:
            self.fig_mp = pylab.figure()
            self.fig_mp.show()
            self.ax_mp = self.fig_mp.add_subplot(1, 1, 1)
            self.ax_mp.set_autoscale_on(False)
            self.ax_mp.set_xlabel("Run time (s)")
            self.ax_mp.set_xlim(0, 100)
            self.ax_mp.set_ylim(0, 2 ** 10)
            self.ax_mp.set_ylabel("Memory occupancy (MB)")
            self.ax_mp.set_title("Memory leak hunter")
            self.plot_mp = self.ax_mp.plot(*self.memory_profile)[0]
        else:
            self.plot_mp.set_data(*self.memory_profile)
            tmax = self.memory_profile[0][-1]
            mmax = max(self.memory_profile[1])
            if tmax > self.ax_mp.get_xlim()[-1]:
                self.ax_mp.set_xlim(0, tmax)
            if mmax > self.ax_mp.get_ylim()[-1]:
                self.ax_mp.set_ylim(0, mmax)

        if self.fig_mp.canvas:
            update_fig(self.fig_mp)

    def get_size(self):
        if len(self.meth) == 0:
            return []
        size = list(self.results[self.meth[0]].keys())
        for i in self.meth[1:]:
            s = list(self.results[i].keys())
            if len(s) > len(size):
                size = s
        size.sort()
        return size
    size = property(get_size)


if __name__ == "__main__":
    try:
        from argparse import ArgumentParser
    except:
        from pyFAI.third_party.argparse import ArgumentParser
    description = """Benchmark for Azimuthal integration
    """
    epilog = """  """
    usage = """benchmark [options] """
    version = "pyFAI benchmark version " + pyFAI.version
    parser = ArgumentParser(usage=usage, description=description, epilog=epilog)
    parser.add_argument("-v", "--version", action='version', version=version)
    parser.add_argument("-d", "--debug",
                        action="store_true", dest="debug", default=False,
                        help="switch to verbose/debug mode")
    parser.add_argument("-c", "--cpu",
                        action="store_true", dest="opencl_cpu", default=False,
                        help="perform benchmark using OpenCL on the CPU")
    parser.add_argument("-g", "--gpu",
                        action="store_true", dest="opencl_gpu", default=False,
                        help="perform benchmark using OpenCL on the GPU")
    parser.add_argument("-a", "--acc",
                        action="store_true", dest="opencl_acc", default=False,
                        help="perform benchmark using OpenCL on the Accelerator (like XeonPhi/MIC)")
    parser.add_argument("-s", "--small",
                        action="store_true", dest="small", default=False,
                        help="Limit the size of the dataset to 6 Mpixel images (for computer with limited memory)")
    parser.add_argument("-n", "--number",
                        dest="number", default=10, type=int,
                        help="Number of repetition of the test, by default 10")
    parser.add_argument("-2d", "--2dimention",
                        action="store_true", dest="twodim", default=False,
                        help="Benchmark also algorithm for 2D-regrouping")
    parser.add_argument("--no-1dimention",
                        action="store_false", dest="onedim", default=True,
                        help="Do not benchmark algorithms for 1D-regrouping")

    parser.add_argument("-m", "--memprof",
                        action="store_true", dest="memprof", default=False,
                        help="Perfrom memory profiling (Linux only)")
    parser.add_argument("-r", "--repeat",
                        dest="repeat", default=1, type=int,
                        help="Repeat each benchmark x times to take the best")

    options = parser.parse_args()
    if options.small:
        ds_list = ds_list[:4]
    if options.debug:
            pyFAI.logger.setLevel(logging.DEBUG)
    print("Averaging over %i repetitions (best of %s)." % (options.number, options.repeat))
    bench = Bench(options.number, options.repeat, options.memprof)
    bench.init_curve()
    if options.onedim:
        bench.bench_1d("splitBBox")
        bench.bench_1d("lut", True)
        bench.bench_1d("csr", True)
        if options.opencl_cpu:
            bench.bench_1d("lut_ocl", True, {"devicetype": "CPU"})
            bench.bench_1d("csr_ocl", True, {"devicetype": "CPU"})
        if options.opencl_gpu:
            bench.bench_1d("lut_ocl", True, {"devicetype": "GPU"})
            bench.bench_1d("csr_ocl", True, {"devicetype": "GPU"})
        if options.opencl_acc:
            bench.bench_1d("lut_ocl", True, {"devicetype": "ACC"})
            bench.bench_1d("csr_ocl", True, {"devicetype": "ACC"})

    if options.twodim:
        bench.bench_2d("splitBBox")
        bench.bench_2d("lut", True)
        if options.opencl_cpu:
            bench.bench_2d("lut_ocl", True, {"devicetype": "CPU"})
        if options.opencl_gpu:
            bench.bench_2d("lut_ocl", True, {"devicetype": "GPU"})
        if options.opencl_acc:
            bench.bench_2d("lut_ocl", True, {"devicetype": "ACC"})

    bench.save()
    bench.print_res()
    bench.update_mp()

    bench.ax.set_ylim(0.5, 500)
    pylab.ion()
    raw_input("Enter to quit")
