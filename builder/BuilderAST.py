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
    __is_reversed__ = False

class Reverse(BuilderType):
    __is_reversed__ = True

    def __init__(self, type):
        self.type = type

    def __as_lower_type__(self):
        raise AssertionError("Shouldn't be called")

class BundleDec(BuilderType):
    def __as_lower_type__(self):
        fields = {}
        for f in inspect.getmembers(self):
            (name, type) = f
            if name[0] == "_":
                continue
            orientation = Field.Default
            if isinstance(type, BuilderType) and type.__is_reversed__:
                orientation = Field.Reverse
                type = type.type
            fields[name] = Field(name = name,
                                    type = type.__as_lower_type__(),
                                    orientation = orientation)
        return Bundle(fields)
    def __init__(self):
        builder.cur_context.updates += [BuilderTypeDec(self)]

class BuilderStmt(Stmt):
    isDec = False
    def __init__(self):
        print "ADDING "+str(self)
        builder.cur_context.updates += [self]

    # def traverse_exprs(self, func):
    #     """
    #     Finds all `Expr`s (`BuilderExpr` and otherwise) in this statement,
    #     and calls their `__traverse__()` function with the supplied `func`
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
        self.__n__ = builder.cur_context.instanceCount
        builder.cur_context.instanceCount += 1
        self.__name__ = name
    def __repr__(self):
        return "{"+str(self.__name__)+" : "+(super(BuilderId, self).__repr__())+"}"

class BuilderDec(BuilderStmt):
    def __init__(self, idt):
        self.idt = idt
        name = builder.cur_context.name
        print "ADDING CONTEXT UPDATE "+str(self)+" to "+name
        builder.cur_context.updates += [self]



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

    def traverse_exprs(self, func):
        self.idt = self.idt.__traverse__(func)

    def elaborate(self):
        return WireDec(self.idt, self.btype.__as_lower_type__())

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

    def traverse_exprs(self, func):
        self.idt = self.idt.__traverse__(func)
        if self.onReset != None:
            self.onReset = self.onReset.__traverse__(func)

    def elaborate(self):
        return RegDec(idt = self.idt, \
                        type = self.btype.__as_lower_type__(), \
                        onReset = self.onReset)

class BuilderTypeDec(BuilderStmt):
    def __init__(self, bundleDec):
        self.bundleDec = bundleDec
    def elaborate(self):
        return TypeDec(self.bundleDec.__as_lower_type__())
    def traverse_exprs(self, func):
        pass

class Connect(BuilderStmt):
    def __init__(self, lval, rval):
        self.lval = lval
        self.rval = rval
        BuilderStmt.__init__(self)
    def traverse_exprs(self, func):
        self.lval = self.lval.__traverse__(func)
        self.rval = self.rval.__traverse__(func)
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
        self.__context__ = builder.cur_context
        self.__context__.className = name
        print "Set context for "+str(self)+" to "+str(self.__context__.className)

class Module(BuilderStmt):
    __metaclass__ = ModuleBuilder

    def elaborate(self):
        stmts = []
        self.__context__.renameIds()
        for upd in self.__context__.updates:
            stmts += [upd.elaborate()]
        return ModuleDec(self.__context__.name, self.io, stmts)

    def traverse_exprs(self, func):
        return self

    def derived_name(self):
        """
        Returns an appropriate name for an instance of the child type with
        whatever parameter values it has.
        """
        print "Deriving name for "+str(self)+": "+self.__context__.className
        return self.__context__.className
