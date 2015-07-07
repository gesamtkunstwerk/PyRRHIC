from pyrast import *
from builder.BuilderAST import *

class ReadyValIO(BundleDec):
    ready = Reverse(UInt(1))
    valid = UInt(1)
    def __init__(self, data):
      self.data = data

class FIFOIO(BundleDec):
    def __init__(self, data):
      self.input = ReadyValIO(data)
      self.output = Reverse(ReadyValIO(data))

class FIFO32(Module):
    def __init__(self, stages):
        self.io = Wire(FIFOIO(UInt(32)))
        r = Wire(FIFOIO(UInt(32)))
        Connect(r, self.io.input)
        for n in range(stages):
            rnext = Reg(ReadyValIO(UInt(32)))
            Connect(rnext, r)
            r = rnext
        Connect(self.io.output, r)

class OtherModule(Module):
    io = UInt(1)

    def make_fifo(stages, input):
        tm = Module(FIFO32(stages))
        Connect(tm.io.input, input)
        w = Wire(FIFOIO(UInt(32)))
        Connect(w, tm.io.output)
        return w

    r1 = make_fifo(stages=2, input=Lit(0))
    r2 = make_fifo(stages=5, input=Lit(1))

    #Connect(r, io.valid)
    def __init__(self):
        print "Initing OtherModule"

m = Module(OtherModule())
