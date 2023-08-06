import pyopencl,numpy
import pyFAI,fabio
data=fabio.open("testimages/Pilatus1M.edf").data
ai=pyFAI.load("testimages/Pilatus1M.poni")
try:
    ai.xrpd_LUT_OCL(data,1000,devicetype="CPU")
except pyopencl.LogicError as e:
    print e
