from pyrast import *
from builder.BuilderAST import *



class ReadyValIO(BundleDec):
    ready = UInt(1)
    valid = Reverse(UInt(1))

class MyIO(BundleDec):
    rv = ReadyValIO()
    def __init__(self, width):
        self.data = UInt(width)

class SomeModule(Module):
    io = MyIO(16)
    w = Wire(UInt(8))
    #Connect(io.data, w)

class OtherModule(Module):
    io = ReadyValIO()
    r = Reg(type=UInt(1), onReset=Lit(0))
    Connect(r, io.valid)
   # Connect(io.ready, r)
