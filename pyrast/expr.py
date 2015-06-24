

class Expr:
    """PyRRHIC Expression AST"""
    lineInfo = None
    
    # Kinds of expressinos that are available
    BinExprType, UnExprType, LitType, GenericType = range(4)
    
    exprType = GenericType
    
    def __add__(self, other):
        return Add(self, other)
    
    def __sub__(self, other):
        return Sub(self, other)
    
    def __invert__(self):
        return Invert(self)
        
    def __getslice__(self, a, b):
        return Bits(self, a, b)
    
    def __gt__(self, other):
        return Gt(self, other)
    
    def __lt__(self, other):
        return Lt(self, other)
    
    def parens(self):
        """
        Adds parentheses around the string representation of this expression
        if it is not a literal.  Used in larger composit expressions' string
        representations.
        """
        if self.exprType == Expr.LitType:
            return str(self)
        else:
            return "("+str(self)+")"

class Lit(Expr):
    """PyRRHIC Literal Expression"""
    
    exprType = Expr.LitType
    
    def __init__(self, value, width = None, signed = False):
        self.value = value
        self.width = width
        self.signed = signed
        self.lineInfo = LineInfo(2)
        
    def __str__(self):
        return str(self.value)

class Id(Expr):
    def __init__(self, id):
        self.id = id
    def __str__(self):
        return str(id)

class BinExpr(Expr):
    exprType = Expr.BinExprType
    
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __str__(self):
        return self.a.parens() + " " + self.symbol + " " + self.b.parens()

class Add(BinExpr):
    symbol = "+"
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)

class Sub(BinExpr):
    symbol = "-"
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)

class UnExpr(Expr):
    exprType = Expr.UnExprType
    
    def __init__(self, e):
        self.e = e
    def __str__(self):
        return self.symbol + self.e.parens()

class Invert(UnExpr):
    symbol = "~"
    def __init__(self, e):
        UnExpr.__init__(self, e)
  
class Reg(Expr):
    def __init__(self, value, enable = None):
        self.value = value
        self.enable = enable
    def __str__(self):
        if self.enable != None:
            return "Reg("+str(self.value)+", "+str(self.enable)+")"     
        else:
            return "Reg("+str(self.value)+")"
 
class Bits(Expr):
    def __init__(self, e, msb, lsb):
        self.e = e
        self.msb = msb
        self.lsb = lsb
    def __str__(self):
        return self.e.parens() + "[" + str(self.msb) + ":" + str(self.lsb) + "]"

class Cat(Expr):
    def __init__(self, *args):
        self.exprs = args
    def __str__(self):
        res = self.exprs[0]
        for s in self.exprs[1:]:
            res += ", " + str(s)
        return "Cat("+res+")"

class Eq(BinExpr):
    symbol = "=="
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)

class Neq(BinExpr):
    symbol = "!="
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)
        
class Lt(BinExpr):
    symbol = "<"
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)
        
class Gt(BinExpr):
    symbol = ">"
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)
        
class Mux(Expr):
    def __init__(self, sel, a, b):
        self.a = a
        self.b = b
        self.sel = sel
    def __str__(self):
        return "Mux(" + str(self.sel) + ", " + str(self.a) + ", " + str(self.b) + ")"        
