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
    w = Wire(UInt(1))
    m = Module(TestModule())
    Connect(m.w, w)

class OtherModule(Module):
    io = ReadyValIO()
    r = Reg(type=UInt(1), onReset=Lit(0))

    def make_reg(width=1):
        mr = Reg(type=UInt(width))
        w = Wire(UInt(width))
        print "W = " + str(w)
        Connect(w, mr)
        return w

    r1 = make_reg(width=2)
    r2 = make_reg(width=3)

    #Connect(r, io.valid)
    def __init__(self):
        print "INiting OtherModule"

m = Module(OtherModule())
