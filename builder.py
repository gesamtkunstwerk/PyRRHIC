from pyrast import *
import inspect

class BuilderContext:
    """
    Encapsulates all state pertaining an elaboration.
    """
  
    curContext = None
    allContexts = {}
    
    def __init__(self, name):
        self.updates = []
        self.instanceCount = 0
        self.name = name
        BuilderContext.curContext = self
        BuilderContext.allContexts[name] = self
        
    def renameIds(self):
        """
        Replaces all `BuilderId` instances in this context with unique
        PyRRHIC `Id`s.
        """
        rmap = self.renameMap()
        def replace(expr):
            if isinstance(expr, BuilderId):
                return rmap[expr]
            else:
                return expr
        for u in self.updates:
            u.traverseExprs(replace)
    
    def renameMap(self):
        """
        Builds a renaming of all `BuilderId` instances in this context
        to unique PyRRHIC `Id`s
        """
        names = self.collectIds()
        renameMap = {}
        for name in names:
            # Give the first entry the "real" name and make temporary ids
            # for all the other instances
            idt = names[name][0]
            renameMap[idt] = Id(name)
            if len(names[name]) > 1:
                cnt = 0
                for idt in names[name][1:]:
                    renameMap[idt] = Id("_t_"+name+"_"+str(cnt))
                    cnt += 1
        return renameMap
        
    def collectIds(self):
        """
        Makes a dictionary containing every string ised in a `BuilderId` in
        this context.  Each value contains all `BuilderId`s using that name.
        """
        names = {}
        for u in self.updates:
            if u.isDec:
                if u.idt.name in names:
                    names[u.idt.name] += [u.idt]
                else:
                    names[u.idt.name] = [u.idt]
        return names

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
            fields[name] = Field(name = name, type = type.__asType__(), orientation = orientation)
        return Bundle(fields)
 
class BuilderExpr(Expr):
    pass       
       
class BuilderId(BuilderExpr):    
    def __init__(self, type):
        self.lineInfo = LineInfo(3)
        self.name = self.lineInfo.assignedVar()
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
        
class Node(BuilderExpr):
    """
    Represents the value wired to some `BuilderId` at a particular point
    during the elaboration phase.
    
    As wires and registers are assigned values with `Connect()`, their
    correponding `curNode` field is updated to a new `Node` instance that
    represents the result of that connection.
    """
    
    def __init__(self, base, value):
        self.base = base
        self.value = value
        
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
    
class BuilderDec(BuilderStmt):
    isDec = True
    def __init__(self, idt):
        self.idt = idt
    def traverseExprs(self, func):
        self.idt = self.idt.traverse(func)
        
class Connect(BuilderStmt):
    def __init__(self, lval, rval):
        self.lval = lval
        self.rval = rval
        BuilderStmt.__init__(self)
    def traverseExprs(self, func):
        self.lval = self.lval.traverse(func)
        self.rval = self.rval.traverse(func)
        
class ModuleBuilder(Type):
    """
    Metaclass to creating PyRRHIC `ModuleDec` instances from 
    `Module` class definitions.
    """
    def __init__(self, name, bases, attrs):
        """
        Creates this module's `ModuleDec` based on the state of the current
        builder context.
        """
        self.context = BuilderContext.curContext
        stmts = []
        for upd in self.context.updates:
            stmts += []
            
        
            
      
    
    