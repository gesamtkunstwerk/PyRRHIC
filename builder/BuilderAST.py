"""
PyRRHIC Builder Abstract Syntax Tree.

This is a superset of the PyRRHIC AST nodes (`pyrast/`) generated
from the initial PyRRHIC Python input, and elaborated by the builder
package into `pyrast`.
"""
from pyrast import *
from builder import BuilderContext

class BuilderType:
    __isReversed__ = False

class Reverse(BuilderType):
    __isReversed__ = True

    def __init__(self, type):
        self.type = type

    def __asType__(self):
        raise AssertionError("Shouldn't be called")

class BundleDec(BuilderType):
    def __asType__(self):
        fields = {}
        for f in inspect.getmembers(self):
            (name, type) = f
            if name[0] == "_":
                continue
            orientation = Field.Default
            if isinstance(type, BuilderType) and type.__isReversed__:
                orientation = Field.Reverse
                type = type.type
            fields[name] = Field(name = name,
                                    type = type.__asType__(),
                                    orientation = orientation)
        return Bundle(fields)
    def __init__(self):
        BuilderContext.curContext.updates += [BuilderTypeDec(self)]

class BuilderExpr(Expr):
    pass

class BuilderId(BuilderExpr):
    def __init__(self, type):
        self.lineInfo = LineInfo(3)
        self.idt = self.lineInfo.assignedVar()
        self.type = type
        self.curNode = BaseId(self)

        # Add this Id as a declaration to the current builder context
        self.n = BuilderContext.curContext.instanceCount
        BuilderContext.curContext.instanceCount += 1
        BuilderContext.curContext.updates += [BuilderDec(self)]

class BaseId(BuilderExpr):
    """
    The value contained by a `BuilderId`'s `curNode` before anything
    has been wired to it.
    """
    def __init__(self, idt):
        self.idt = idt


class Wire(BuilderId):
    isReg = False
    def __init__(self, type):
        BuilderId.__init__(self, type)

class Reg(BuilderId):
    isReg = True

    def __init__(self, type, onReset):
        self.onReset = onReset
        BuilderId.__init__(self, type)

class BuilderStmt(Stmt):
    isDec = False
    def __init__(self):
        print "ADDING "+str(self)
        BuilderContext.curContext.updates += [self]

    def traverseExprs(self, func):
        """
        Finds all `Expr`s (`BuilderExpr` and otherwise) in this statement,
        and calls their `traverse()` function with the supplied `func`
        """
        raise Error("Not implemented....")

    def elaborate(self):
        """
        Returns a lower-level PyRRHIC AST for this statment.
        """
        raise Error("Not implemented...")

class BuilderDec(BuilderStmt):
    isDec = True
    def __init__(self, idt):
        self.idt = idt
        self.isRed = idt.isReg
    def traverseExprs(self, func):
        self.idt = self.idt.traverse(func)

class BuilderTypeDec(BuilderStmt):
    def __init__(self, bundleDec):
        self.bundleDec = bundleDec
    def elaborate(self):
        return TypeDec(self.bundleDec.__asType__())
    def traverseExprs(self, func):
        pass

class Connect(BuilderStmt):
    def __init__(self, lval, rval):
        self.lval = lval
        self.rval = rval
        BuilderStmt.__init__(self)
    def traverseExprs(self, func):
        self.lval = self.lval.traverse(func)
        self.rval = self.rval.traverse(func)
    def elaborate(self):
        return ConnectStmt(lval, rval)

class ModuleBuilder(type):
    """
    Metaclass to creating PyRRHIC `ModuleDec` instances from
    `Module` class definitions.
    """
    def __init__(self, name, bases, attrs):
        """
        Creates this module's `ModuleDec` based on the state of the current
        builder context.
        """
        self.__context__ = BuilderContext.curContext
        self.__context__.name = name
        self.__lineInfo__ = LineInfo(2)

        # Add this one, and make a new Context for the next `Module` invocation
        if name != "Module":
            BC = BuilderContext
            BC.allContexts[name] = self.__context__
            BC.curContext = BC(BuilderContext.NewContextName)
            BC.allContexts[BC.BaseContextName].updates += [self()]

class Module(BuilderStmt):
    __metaclass__ = ModuleBuilder

    def elaborate(self):
        stmts = []
        self.__context__.renameIds()
        for upd in self.__context__.updates:
            stmts += [upd.elaborate()]
        print self.__context__.name
        return ModuleDec(self.__context__.name, self.io, stmts)

    def traverseExprs(self, func):
        return self
