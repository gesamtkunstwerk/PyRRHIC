
class Stmt(object):
    """
    PyRRHIC Statement AST Nodes
    """
    lineInfo = None
    __isBuilderStmt__ = False
    
class WireDec(Stmt):
    def __init__(self, idt, type):
        self.idt = idt
        self.type = type
    def __str__(self):
        return "wire " + str(self.idt) + " : " + str(self.type)

class RegDec(Stmt):
    def __init__(self, idt, type, onReset = None):
        self.idt = idt
        self.type = type
        self.onReset = onReset
    def __str__(self):
        res = "reg " + str(self.idt) + " : " + str(self.type)
        if self.onReset != None:
            res += " [" + str(self.onReset)+ "]"
        return res
        
class TypeDec(Stmt):
    def __init__(self, bundle):
        self.bundle = bundle
        
class ConnectStmt(Stmt):
    def __init__(self, lval, rval):
        self.lval = lval
        self.rval = rval
        
    def __str__(self):
        return str(self.lval) + " := " + str(self.rval)

class ModuleDec(Stmt):
    def __init__(self, idt, io, stmts):
        self.idt = idt
        self.io = io
        self.stmts = stmts

    def __str__(self):
        res = "module "+str(self.idt)+":\n"
        for stmt in self.stmts:
          res += "  " + str(stmt) + "\n"
        return res

class ModuleInst(Stmt):
    def __init__(self, inst_idt, mod_idt):
      """
      Parameters
      ----------
      inst_idt (Id): name of the instance being declared in the current scope
      mod_idt (Id): name of the module type being instantiated
      """
      self.inst_idt = inst_idt
      self.mod_idt = mod_idt
     
    def __str__(self):
      return "inst " + str(self.inst_idt) + " : " + str(self.mod_idt)
