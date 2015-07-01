from pyrast import *
from builder.BuilderAST import *

class TestModule(Module):
    w = Wire(UInt(1))

class ReadyValIO(BundleDec):
    ready = UInt(1)
    valid = Reverse(UInt(1))

class MyIO(BundleDec):
    print "in myio"
    def __init__(self, width):
        self.rv = ReadyValIO()
        self.data = UInt(width)

class SomeModule(Module):
    io = MyIO(16)
    w = Wire(UInt(8))
    m = Module(TestModule())

class OtherModule(Module):
    io = ReadyValIO()
    r = Reg(type=UInt(1), onReset=Lit(0))
    Connect(r, io.valid)
