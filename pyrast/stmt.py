
class Stmt:
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
    def __init__(self, idt, type):
        self.idt = idt
        self.type = type
    def __str__(self):
        return "reg " + str(self.idt) + " : " + str(self.type)
        
class ConnectStmt(Stmt):
    def __init__(self, lval, rval):
        self.lval = lval
        self.rval = rval
        
class ModuleDec(Stmt):
    def __init__(self, idt, io, stmts):
        self.idt = idt
        self.io = io
        self.stmts = stmts
        
    