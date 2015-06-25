from pyrast import Type, Bundle, Field
import inspect

class BuilderType:
    __isReversed__ = False
    __kind__ = Type.BuilderType
    
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
            if type.__kind__ == Type.BuilderType and type.__isReversed__:
                orientation = Field.Reverse
                type = type.type
            fields[name] = Field(name = name, type = type.__asType__(), orientation = orientation)
        return Bundle(fields)