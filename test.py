from pyrast import *
from builder.BuilderAST import *

class ReadyValIO(BundleDec):
    ready = UInt(1)
    valid = Reverse(UInt(1))

class RVData(ReadyValIO):
    def __init__(self, data):
        self.data = data

class FIFO32IO(BundleDec):
    input = RVData(UInt(32))
    output = RVData(UInt(32))

class FIFO32(Module):

    def __init__(self, stages):
        self.io = Wire(FIFO32IO())
        r = Wire(RVData(UInt(32)))
        for n in range(stages):
            rnext = Reg(RVData(UInt(32)))
            Connect(rnext, r)
            r = rnext
        #Connect(self.io.output, r)

class OtherModule(Module):
    io = ReadyValIO()
    r = Reg(type=UInt(1), onReset=Lit(0))

    def make_reg(width=1):
        mr = Reg(type=UInt(width))
        w = Wire(UInt(width))
        print "W = " + str(w)
        Connect(w, mr)
        tm = Module(FIFO32(6))
        Connect(tm.io.input.valid, w)
        return w

    r1 = make_reg(width=2)
    r2 = make_reg(width=3)

    #Connect(r, io.valid)
    def __init__(self):
        print "INiting OtherModule"

m = Module(OtherModule())
