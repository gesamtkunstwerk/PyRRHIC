from pyrrhic.builder.bdast import *
from pyrrhic import Log2Up

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
        r //= self.io.input
        for n in range(stages):
            rnext = Reg(ReadyValIO(UInt(32)))
            rnext //= r
            r = rnext
        self.io.output //= r

class OtherModule(Module):
    io = Wire(UInt(1))

    def make_fifo(stages, input):
        tm = Module(FIFO32(stages))
        tm.io.input //= input
        w = Wire(FIFOIO(UInt(32)))
        w //= tm.io.output
        return w

    r1 = make_fifo(stages=2, input=Lit(0))
    r2 = make_fifo(stages=5, input=Lit(1))

    #r //= io.valid
    def __init__(self):
        print "Initing OtherModule"

class Counter(Module):
  class CounterIO(BundleDec):
    start     = UInt(1)
    finished  = Reverse(UInt(1))


  def __init__(self, max_val):
    self.io = Wire(Counter.CounterIO())
    self.max_val = max_val
    cnt = Reg(UInt(width=Log2Up(max_val)))
    fin = Reg(UInt(1))
    self.io.finished //= fin
    if When(self.io.start):
      cnt //= Lit(0)
      fin //= Lit(0)
    elif When(cnt == Lit(max_val)):
      fin //= Lit(1)
    elif When(~fin):
      cnt //= (cnt + Lit(1))

m = Module(OtherModule())
c = Module(Counter(17))

class BunchOfCounters(Module):
  io = Wire(UInt(1))
  def __init__(self, n, max_val):
    self.counters = []
    ios = Wire(Vec(Counter.CounterIO(), n))
    for i in range(n):
      m = Module(Counter(max_val))
      self.counters.append(m)
      ios[Lit(i)] //= self.counters[i].io

bc = Module(BunchOfCounters(5, 16))
    

