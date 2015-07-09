TAB = "  "

class Stmt(object):
    """
    PyRRHIC Statement AST Nodes
    """
    lineInfo = None
    __isBuilderStmt__ = False

    def firrtl_lines(self, indent=0):
        """
        Returns a list of strings containing the FIRRTL code for this statement
        at the level of indentation specified by `indent`.
        """
        return [TAB*indent + str(self)]

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
        
class ConnectStmt(Stmt):
    def __init__(self, lval, rval):
        self.lval = lval
        self.rval = rval
        
    def __str__(self):
        return str(self.lval) + " := " + str(self.rval)

class WhenStmt(Stmt):
  def __init__(self, cond, if_stmts, else_stmts):
      self.cond = cond
      self.if_stmts = if_stmts
      self.else_stmts = else_stmts

  def firrtl_lines(self, indent=0):
      lines = []
      
      lines.append(TAB*indent + "when " + str(self.cond) + ":")
      for s in self.if_stmts:
          lines += s.firrtl_lines(indent + 1)
      if len(self.else_stmts) > 0:
          lines.append(TAB*indent + "else:")
          for s in self.else_stmts:
              lines += s.firrtl_lines(indent + 1)

      return lines
            

class ModuleDec(Stmt):
    def __init__(self, idt, io, stmts):
        self.idt = idt
        self.io = io
        self.stmts = stmts

    def __str__(self):
      lines = self.firrtl_lines()
      res = ""
      for l in lines:
        res += l + "\n"
      return res

    def firrtl_lines(self, indent=0):
        lines = []

        lines.append(TAB*indent + "module " + str(self.idt) + ":")
        for s in self.stmts:
          lines += s.firrtl_lines(indent + 1)

        return lines

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
