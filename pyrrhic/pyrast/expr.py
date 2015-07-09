

class Expr(object):
    """PyRRHIC Expression AST"""
    __line_info__ = None

    # Set to true if no parentheses are needed around this expression
    __is_single_term__ = False

    def __add__(self, other):
        return Add(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __invert__(self):
        return Invert(self)

    def __getslice__(self, a, b):
        return Bits(self, a, b)

    def __eq__(self, other):
        return Eq(self, other)

    def __gt__(self, other):
        return Gt(self, other)

    def __lt__(self, other):
        return Lt(self, other)

    def __getattr__(self, attr):
        if len(attr) > 2 and attr[0:1] == "__":
            return super(self, object).__getattr__(attr)
        else:
            return SubField(self, attr)
  
    def __getitem__(self, item):
        return SubItem(self, item)

    def __parens__(self):
        """
        Adds parentheses around the string representation of this expression
        if it is not a literal.  Used in larger composite expressions' string
        representations.
        """
        if self.__is_single_term__:
            return str(self)
        else:
            return "("+str(self)+")"

    def __traverse__(self, func):
        """
        Performs a pre-order traversal of this `Expr` AST and applies `func`
        to each node encountered along the way, replacing it with the
        result returned by `func`.

        Note that this function modifies the AST on which it operates.
        """
        return func(self)

class Lit(Expr):
    """PyRRHIC Literal Expression"""
    __is_single_term__ = True

    def __init__(self, value, width = None, signed = False):
        self.value = value
        self.width = width
        self.signed = signed

    def __str__(self):
        return str(self.value)


class Id(Expr):
    __is_single_term__ = True

    def __init__(self, idt):
        self.__idt__ = idt

    def __str__(self):
        return str(self.__idt__)
    def __repr__(self):
        return str(self.__idt__)

class SubField(Expr):
    __is_single_term__ = True

    def __init__(self, base, attr):
        self.__base__ = base
        self.__attr__ = attr

    def __traverse__(self, func):
        self.__base__ = self.__base__.__traverse__(func)
        return func(self)

    def __str__(self):
        return str(self.__base__) + "." + str(self.__attr__)

    def __repr__(self):
        return self.__str__()

class SubItem(Expr):
    def __init__(self, base, item):
        self.__base__ = base
        self.__item__ = item

    def __traverse__(self, func):
        self.__base__ = self.__base__.__traverse__(func)
        self.__item__ = self.__item__.__traverse__(func)
        return func(self)

    def __repr__(self):
        return str(self.__base__) + "[" + str(self.__item__) + "]"

class BinExpr(Expr):
    def __init__(self, a, b):
        self.__a__ = a
        self.__b__ = b

    def __str__(self):
        return self.__a__.__parens__() + " " + self.__symbol__ + " " + self.__b__.__parens__()

    def __traverse__(self, func):
        self.__a__ = self.__a__.__traverse__(func)
        self.__b__ = self.__b__.__traverse__(func)
        return func(self)

class Add(BinExpr):
    __symbol__ = "+"
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)

class Sub(BinExpr):
    __symbol__ = "-"
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)

class UnExpr(Expr):
    __is_single_term__ = True
    def __init__(self, e):
        self.e = e
    def __str__(self):
        return self.__symbol__ + self.e.__parens__()
    def __traverse__(self, func):
        self.e = self.e.__traverse__(func)
        return func(self)

class Invert(UnExpr):
    __symbol__ = "~"
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
    def __traverse__(self, func):
        self.value = self.value.__traverse__(func)
        return func(self)

class Bits(Expr):
    def __init__(self, e, msb, lsb):
        self.e = e
        self.msb = msb
        self.lsb = lsb

    def __str__(self):
        return self.e.__parens__() + "[" + str(self.msb) + ":" + str(self.lsb) + "]"
    def __traverse__(self, func):
        self.e = self.e.__traverse__(func)
        return func(self)

class Cat(Expr):
    def __init__(self, *args):
        self.exprs = args
    def __str__(self):
        res = self.exprs[0]
        for s in self.exprs[1:]:
            res += ", " + str(s)
        return "Cat("+res+")"
    def __traverse__(self, func):
        newExprs = []
        for e in self.exprs:
            newExprs += [e.__traverse__(func)]
        self.exprs = newExprs
        return func(self)

class Eq(BinExpr):
    __symbol__ = "=="
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)

class Neq(BinExpr):
    __symbol__ = "!="
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)

class Lt(BinExpr):
    __symbol__ = "<"
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)

class Gt(BinExpr):
    __symbol__ = ">"
    def __init__(self, a, b):
        BinExpr.__init__(self, a, b)

class Mux(Expr):
    def __init__(self, sel, a, b):
        self.__a__ = a
        self.__b__ = b
        self.__sel__ = sel

    def __str__(self):
        return "Mux(" + str(self.__sel__) + ", " + str(self.__a__) + ", " + str(self.__b__) + ")"

    def __traverse__(self, func):
        self.__sel__ = self.__sel__.__traverse__(func)
        self.__a__ = self.__a__.__traverse__(func)
        self.__b__ = self.__b__.__traverse__(func)
        return func(self)
