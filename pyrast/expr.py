

class Expr:
    """PyRRHIC Expression AST"""
    __isBuilderExpr__ = False
    
    lineInfo = None
    
    # Set to true if no parentheses are needed around this expression
    isSingleTerm = False
    
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
        if it is not a literal.  Used in larger composite expressions' string
        representations.
        """
        if self.isSingleTerm:
            return str(self)
        else:
            return "("+str(self)+")"
    
    def traverse(self, func):
        """
        Performs a pre-order traversal of this `Expr` AST and applies `func`
        to each node encountered along the way, replacing it with the
        result returned by `func`.
        
        Note that this function modifies the AST on which it operates.
        """
        return func(self)

class Lit(Expr):
    """PyRRHIC Literal Expression"""
    isSingleTerm = True
    
    def __init__(self, value, width = None, signed = False):
        self.value = value
        self.width = width
        self.signed = signed
        
    def __str__(self):
        return str(self.value)


class Id(Expr):
    isSingleTerm = True
    
    def __init__(self, idt):
        self.idt = idt
        
    def __str__(self):
        return str(self.idt)

class BinExpr(Expr):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def __str__(self):
        return self.a.parens() + " " + self.symbol + " " + self.b.parens()
    
    def traverse(self, func):
        self.a = self.a.traverse(func)
        self.b = self.b.traverse(func)
        return func(self)

class Add(BinExpr):
    symbol = "+"
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)

class Sub(BinExpr):
    symbol = "-"
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)

class UnExpr(Expr):
    isSingleTerm = True
    def __init__(self, e):
        self.e = e
    def __str__(self):
        return self.symbol + self.e.parens()
    def traverse(self, func):
        self.e = self.e.traverse(func)
        return func(self)

class Invert(UnExpr):
    symbol = "~"
    def __init__(self, e):
        UnExpr.__init__(self, e)
  
class SReg(Expr):
    def __init__(self, value, enable = None):
        self.value = value
        self.enable = enable
    def __str__(self):
        if self.enable != None:
            return "Reg("+str(self.value)+", "+str(self.enable)+")"     
        else:
            return "Reg("+str(self.value)+")"
    def traverse(self, func):
        self.value = self.value.traverse(func)
        return func(self)
 
class Bits(Expr):
    def __init__(self, e, msb, lsb):
        self.e = e
        self.msb = msb
        self.lsb = lsb
    def __str__(self):
        return self.e.parens() + "[" + str(self.msb) + ":" + str(self.lsb) + "]"
    def traverse(self, func):
        self.e = self.e.traverse(func)
        return func(self)

class Cat(Expr):
    def __init__(self, *args):
        self.exprs = args
    def __str__(self):
        res = self.exprs[0]
        for s in self.exprs[1:]:
            res += ", " + str(s)
        return "Cat("+res+")"
    def traverse(self, func):
        newExprs = []
        for e in self.exprs:
            newExprs += [e.traverse(func)]
        self.exprs = newExprs
        return func(self)

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
    def traverse(self, func):
        self.sel = self.sel.traverse(func)
        self.a = self.a.traverse(func)
        self.b = self.b.traverse(func)
        return func(self)