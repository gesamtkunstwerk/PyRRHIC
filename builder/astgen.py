"""
PyRRHIC Builder Module Generator

Generates a Builder AST from a given Python source by walking its AST
and transforming it appropriately.

This module also includes utility functions for producing Python
`ast.Node` objects.
"""
import builder
from builder import instrument
from builder.BuilderAST import *
import ast, inspect, copy

def compile_pyrrhic(path):
    """
    Parses the Python source at `path`, gets the AST, transforms it,
    and returns the compiled AST.
    """
    f = open(path, "r")
    src = f.read()
    f.close()
    past = ast.parse(src)
    ModuleWalker().visit(past)
    past = ast.fix_missing_locations(past)
    print ast.dump(past)
    code = compile(past, path, mode='exec')
    return code

def name_id(id, store=False):
    if not isinstance(id, str):
        return id
    if store:
        return ast.Name(id = id, ctx=ast.Store())
    else:
        return ast.Name(id=id, ctx=ast.Load())

def make_call(func, args=[]):
    return ast.Expr(ast.Call(func=name_id(func), args=args, keywords=[]))

def id_attr(ids):
    res = name_id(ids[0])
    for i in ids[1:]:
        res = ast.Attribute(res, i, ast.Load())
    return res

def inst_call(func, args=[]):
    """
    Returns an `ast.Call` to `func` where `func` is replaced by
    `builder.instrument.func`.
    """
    func = id_attr(["builder", "instrument", func])
    return make_call(func, args)


def assign_id(ids, rval):
    """
    Returns a Python AST `Assign` node that assigns node `rval` to all
    identifiers named by `ids`.  If `ids` is a scalar, that is also valid.
    """
    targets = []
    if isinstance(ids, list):
        for i in ids:
            targets.append(name_id(i))
    else:
        targets = [name_id(i)]
    return ast.Assign(targets=targets, value=rval)

class ModuleWalker(ast.NodeTransformer):
    """
    Finds PyRRHIC module definitions in a Python AST and transforms them.

    More speficically, it does the following:
    1. Inserts calls to `ModuleBegin(name)` at the beginning of the
        body of any class derived from `Module`
    2. Inserts call to `ModuleEnd()` at the end of the body of any
        class derived from `Module`
    3. Replaces any assignment of a Python identifier to `Wire()` or
        `Reg()` with an asignment to a `BuilderId`, and adds
        a new `BuilderDec` statement after it.
    """


    def check_for_module(self, node):
        """
        Returns `True` iff `node` is a PyRRHIC module definition.

        Note that `node` must be a `ClassDef`
        """
        isModule = False
        for base in node.bases:
            if base.id == "Module":
                isModule = True
        return isModule

    def instrument_module(self, module):
        """
        Adds a prologue and epilogue to the body of `module`

        module (ast.ClassDef): An AST node for defining a module.
        """
        new = self.generic_visit(module)
        name = [ast.Str(s=module.name)]
        new.body.insert(0, inst_call("module_begin", name))
        new.body.append(inst_call(instrument.module_end.__name__, name))
        return new

    def instrument_instance(self, assign):
        """
        Translates a module instantiation (``m = Module(M(...))``)

        assign (ast.Assign): An AST node instantiating a module
        """
        call = assign.value         # Should be `ast.Call` type
        lval = assign.targets[0]    # Should be an `ast.Name`
        instName = ast.Str(s = lval.id)
        modClassInit = call.args[0] # Also `ast.Call` type
        modClassName = ast.Str(s = modClassInit.func.id)

        # Prologue and epilogue
        beginFunc = instrument.module_inst_begin.__name__
        endFunc = instrument.module_inst_end.__name__
        begin = inst_call(beginFunc, [instName, modClassName])
        end = inst_call(endFunc, [ast.Str("Blah")])

        # Turn assignment `m = Module(M(...))` into assignment `m = M(...)`
        newAssign = ast.Assign([lval], modClassInit)

        print "BEGIN: "+ast.dump(begin)
        print "NEW ASSIGN "+ast.dump(newAssign)
        print "END "+ast.dump(end)

        return [begin, newAssign, end]

    def check_for_module_instance(self, assign):
        """
        Returns true iff `node` is a wrapped instantiation of a module, of the
        form ``m = Module(M(...))``
        """
        lval = assign.targets[0]    # Should be an `ast.Name`
        if isinstance(assign.value, ast.Call):
            call = assign.value
            if call.func.id == "Module":
                return True
        return False

    def visit_Assign(self, node):
        if self.check_for_module_instance(node):
            return self.instrument_instance(node)
        return node

    def visit_ClassDef(self, node):
        if self.check_for_module(node):
            return self.instrument_module(node)
        return node
