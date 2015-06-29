"""
PyRRHIC Builder Module Generator

Generates a Builder AST from a given Python source by walking its AST
and transforming it appropriately.

This module also includes utility functions for producing Python
`ast.Node` objects.
"""
from builder.BuilderAST import *
import ast, inspect

ModuleBegin = "__module_begin__"
ModuleEnd = "__module_end__"

def process(path):
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
    code = compile(past, path, mode='exec')
    return code

def name_id(id, store=False):
    if store:
        return ast.Name(id = id, ctx=ast.Store())
    else:
        return ast.Name(id=id, ctx=ast.Load())

def make_call(func, args=[]):
    return ast.Expr(ast.Call(func=name_id(func), args=args, keywords=[]))

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

        module (ClassDef): An AST node for defining a module.
        """
        new = self.generic_visit(module)
        name = [ast.Str(s=module.name)]
        new.body.insert(0, make_call(ModuleBegin, name))
        new.body.append(make_call(ModuleEnd, name))
        return new

    def visit_ClassDef(self, node):
        if self.check_for_module(node):
            return self.instrument_module(node)
        return node
