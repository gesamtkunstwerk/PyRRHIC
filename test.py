from pyrast import *
from builder.BuilderAST import *
import math
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
    io = Wire(UInt(1))

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

class Counter(Module):
  class CounterIO(BundleDec):
    start     = UInt(1)
    finished  = Reverse(UInt(1))

  io = Wire(CounterIO())

  def __init__(self, max_val):
    self.max_val = max_val
    cnt = Reg(UInt(int(math.ceil(math.log(max_val)))))
    fin = Reg(UInt(1))
    if When(self.io.start):
      Connect(cnt, Lit(0))
      Connect(fin, Lit(0))
    elif When(cnt == Lit(max_val)):
      Connect(fin, Lit(1))
    elif When(~fin):
      Connect(cnt, cnt + Lit(1))

m = Module(OtherModule())
c = Module(Counter(17))
