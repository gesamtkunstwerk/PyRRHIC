from pyrast import *
import inspect



class BuilderType:
    __isBuilderType__ = True
    __isReversed__    = False    

class Reverse(BuilderType):
    __isReversed__ = True
    
    def __init__(self, type):
        self.type = type
        
    def __asType__(self):
        raise AssertionError("Shouldn't be called")

class BundleDec(BuilderType):   
    def __asType__(self):
        fields = {}
        print inspect.getmembers(self)
        for f in inspect.getmembers(self):
            (name, type) = f
            if name[0] == "_":
                continue
            orientation = Field.Default
            print f
            if type.__isBuilderType__ and type.__isReversed__:
                orientation = Field.Reverse
                type = type.type
            fields[name] = Field(name = name, type = type.__asType__(), orientation = orientation)
        return Bundle(fields)
 
       
class BuilderId(Expr):
    __isBuilderExpr__ = True
    count = 0
    isReg = False
    
    def __init__(self, name, type):
        self.n = BuilderId.count
        self.name = name
        self.type = type
        BuilderId.count += 1       
        
class Wire(BuilderId):
    def __init__(self, name, type):
        BuilderId.__init__(self, name, type)
    
class Reg(BuilderId):
    isReg = False
    def __init__(self, name, type, onReset):
        self.onReset = onReset
        BuilderId.__init__(self, name, type)