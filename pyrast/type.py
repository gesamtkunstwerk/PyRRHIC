"""
PyRRHIC Type System AST
"""

class Type:
    __isBuilderType__ = False

    def __asType__(self):
        return self
        
class UInt(Type):
    def __init__(self, width):
        self.width = width

    def __str__(self):
        return "UInt("+str(self.width)+")"

class SInt(Type):
    def __init__(self, width):
        self.width = width
        
class Bundle(Type):
    def __init__(self, fields):
        self.fields = fields
        self.width = 0
        for k in self.fields:
            field = self.fields[k]
            self.width += field.type.width
    
    def __asType__(self):
        fields = {}
        for k in self.fields:
            fields[k] = self.fields[k].__asType__()
        return Bundle(fields)
  
class Field:
    Default, Reverse = range(2)
    
    def __init__(self, orientation, name, type):
        self.orientation = orientation
        self.name = name
        self.type = type.__asType__()
        
    def __asType__(self):
        return Field(orientation = self.orientation, name = self.name, type = self.type.__asType__())
    
class Vec(Type):
    def __init__(self, type, count):
        self.type = type.__asType__()
        self.count = count
        self.width = self.type.width * count
    
    def __asType__(self):
        return Vec(type = self.type.__asType__(), count = self.count)
    
    
    