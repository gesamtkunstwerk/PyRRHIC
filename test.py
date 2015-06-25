from pyrast import *
from builder import *

BuilderContext.curContext = BuilderContext("BASE")

a = Lit(1)
b = Lit(10)
c = SReg(Mux(a > b, a - b, a))[10:9]
print c

w = WireDec(Id("W"), UInt(8))
print w


class ReadyValIO(BundleDec):
    ready = UInt(1)
    valid = Reverse(UInt(1))
    
class MyIO(BundleDec):
    rv = ReadyValIO()
    def __init__(self, width):
        self.data = UInt(width)

w = Wire(MyIO(10))
w = Wire(SInt(16))
c = Connect(w, Lit(65534))
print c
print BuilderContext.curContext.renameMap()