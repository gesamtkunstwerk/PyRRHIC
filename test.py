from pyrast import *
from builder import *

a = Lit(1)
b = Lit(10)
c = Reg(Mux(a > b, a - b, a))[10:9]
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

b = MyIO(10)
print b