
class Stmt:
    """
    PyRRHIC Statement AST Nodes
    """
    lineInfo = None
    
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
    