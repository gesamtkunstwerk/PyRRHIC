"""
PyRRHIC Builder Abstract Syntax Tree.

This is a superset of the PyRRHIC AST nodes (`pyrast/`) generated
from the initial PyRRHIC Python input, and elaborated by the builder
package into `pyrast`.
"""
from pyrast import *
import builder
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
        builder.curClassContext.updates += [BuilderTypeDec(self)]

class BuilderStmt(Stmt):
    isDec = False
    def __init__(self):
        print "ADDING "+str(self)
        builder.curClassContext.updates += [self]

    # def traverseExprs(self, func):
    #     """
    #     Finds all `Expr`s (`BuilderExpr` and otherwise) in this statement,
    #     and calls their `traverse()` function with the supplied `func`
    #     """
    #     raise AssertionError("Not implemented....")

    # def elaborate(self):
    #     """
    #     Returns a lower-level PyRRHIC AST for this statment.
    #     """
    #     raise AssertionError("Not implemented...")


class BuilderExpr(Expr):
    pass

class BuilderId(BuilderExpr):
    def __init__(self, name):
        # Add this Id as a declaration to the current builder context
        self.n = builder.curClassContext.instanceCount
        builder.curClassContext.instanceCount += 1
        self.name = name
    def __repr__(self):
        return "{"+str(self.name)+" : "+(super(BuilderId, self).__repr__())+"}"

class BuilderDec(BuilderStmt):
    def __init__(self, idt):
        self.idt = idt
        name = builder.curClassContext.name
        print "ADDING CONTEXT UPDATE "+str(self)+" to "+name
        builder.curClassContext.updates += [self]



class Wire(BuilderDec):
    isReg = False
    def __init__(self, type, idt = None):
        """
        Represents a wire declaration.

        Keyword arguments:
        idt -- a `BuilderId` identifier to be linked with this wire.
                By default, this is `None` and is added by the AST walk
                before elaboration
        btype -- A `BuilderType` argument
        """
        self.btype = type
        self.idt = idt
        super(Wire, self).__init__(idt)

    def __repr__(self):
        return "wire "+str(self.idt)+": "+str(self.btype)

    def traverseExprs(self, func):
        self.idt = self.idt.traverse(func)

    def elaborate(self):
        return WireDec(self.idt, self.btype.__asType__())

class Reg(BuilderDec):
    isReg = True

    def __init__(self, type, onReset = None, idt = None):
        """
        Represents a register declaration.

        Keyword arguments:
        idt -- a `BuilderId` identifier to be linked with this wire.
                By default, this is `None` and is added by the AST walk
                before elaboration
        btype -- A `BuilderType` argument
        """
        self.onReset = onReset
        self.btype = type
        self.idt = idt
        super(Reg, self).__init__(idt)

    def __repr__(self):
        return "reg "+str(self.idt)+": "+str(self.btype)

    def traverseExprs(self, func):
        self.idt = self.idt.traverse(func)
        if self.onReset != None:
            self.onReset = self.onReset.traverse(func)

    def elaborate(self):
        return RegDec(idt = self.idt, \
                        type = self.btype.__asType__(), \
                        onReset = self.onReset)

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
        return ConnectStmt(self.lval, self.rval)
    def __repr__(self):
        return str(self.lval) + " := " + str(self.rval)

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
        self.__context__ = builder.curClassContext
        self.__context__.className = name

class Module(BuilderStmt):
    __metaclass__ = ModuleBuilder

    def elaborate(self):
        stmts = []
        self.__context__.renameIds()
        for upd in self.__context__.updates:
            stmts += [upd.elaborate()]
        return ModuleDec(self.__context__.name, self.io, stmts)

    def traverseExprs(self, func):
        return self

    def derivedName(self):
        """
        Returns an appropriate name for an instance of the child type with
        whatever parameter values it has.
        """
        return self.__context__.className
