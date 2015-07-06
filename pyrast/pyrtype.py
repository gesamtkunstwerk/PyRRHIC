"""
PyRRHIC Type System AST
"""

class Type:
    def __as_lower_type__(self):
        return self
        
class UInt(Type):
    def __init__(self, width = None):
        self.width = width

    def __str__(self):
        return "UInt("+str(self.width)+")"

class SInt(Type):
    def __init__(self, width = None):
        self.width = width
        
class Bundle(Type):
    def __init__(self, fields):
        self.fields = fields
        self.width = 0
        for k in self.fields:
            field = self.fields[k]
            self.width += field.type.width
    
    def __as_lower_type__(self):
        fields = {}
        for k in self.fields:
            fields[k] = self.fields[k].__as_lower_type__()
        return Bundle(fields)
  
class Field:
    Default, Reverse = range(2)
    
    def __init__(self, orientation, name, type):
        self.orientation = orientation
        self.name = name
        self.type = type.__as_lower_type__()
        
    def __as_lower_type__(self):
        return Field(orientation = self.orientation, name = self.name, type = self.type.__as_lower_type__())
    
class Vec(Type):
    def __init__(self, type, count):
        self.type = type.__as_lower_type__()
        self.count = count
        self.width = self.type.width * count
    
    def __as_lower_type__(self):
        return Vec(type = self.type.__as_lower_type__(), count = self.count)
    
    
    
