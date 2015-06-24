"""
The PyRRHIC Abstract Syntax Tree representation
"""
        
import inspect

class LineInfo:
    """
    Contains Python source file and line number information to associate
    with a PyRRHIC AST node.
    
    Extracted using Python's [[inspect.currentframe]] routine
    """
    def __init__(self, frames = 2):
        """
        Constructs a `LineInfo` object from the current stack trace.
        
        Parameters
        ----------
        
        frames: Int
            The number of stack frames outward needed to obtain the line
            of PyRRHIC source generating this AST node.
        
        """
        # The actual line of interest should correspond to the third 
        # innermost stack frome.
        frameInfo = inspect.getouterframes(inspect.currentframe())[frames]
        self.source = frameInfo[1]
        self.line   = frameInfo[2]
        self.module = frameInfo[3]
        self.string = frameInfo[4]

class Expr:
    """PyRRHIC Expression AST"""
    lineInfo = None
    
    # Kinds of expressinos that are available
    BinExprType, UnExprType, LitType = range(3)
    
    def __add__(self, other):
        return Add(self, other)
    
    def __sub__(self, other):
        return Sub(self, other)
    
    def __invert__(self):
        return Invert(self)
    
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
    
    def __init__(self, value):
        self.value = value
        self.lineInfo = LineInfo(2)
        
    def __str__(self):
        return str(self.value)

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