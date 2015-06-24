
class Stmt:
    """
    PyRRHIC Statement AST Nodes
    """
    lineInfo = None
    
class WireDec(Stmt):
    def __init__(self, id, type):
        self.id = id
        self.type = type
    def __str__(self):
        return "wire " + str(id) + " : " + str(type)

class RegDec(Stmt):
    def __init__(self, id, type):
        self.id = id
        self.type = type
    def __str__(self):
        return "reg " + str(id) + " : " + str(type)
    