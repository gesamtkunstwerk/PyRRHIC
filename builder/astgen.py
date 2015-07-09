"""
PyRRHIC Module Generator -- First Stage of PyRRHIC Compilation.

Generates a Builder AST from a given Python source by walking its AST
and transforming it appropriately.

This module also includes utility functions for producing Python
`ast.Node` objects.
"""
import builder, pyrast
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
    code = compile(past, path, mode='exec')
    return code

def name_id(id, store=False):
    if not isinstance(id, str):
        return id
    if store:
        return ast.Name(id = id, ctx=ast.Store())
    else:
        return ast.Name(id = id, ctx=ast.Load())

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
        targets = [name_id(ids)]
    return ast.Assign(targets=targets, value=rval)


class ModuleAssignLV(object):
    """
    Represents an lvalue of an assignment statement that declares a wire/reg.

    This is needed for wire and register declarations that might be
    written as ``w = Wire(...)`` or as ``self.w = Wire(...)`` (or via
    other classes on the left hand side).
    """
    def __init__(self, assign):
        self.attrs = []
        lval = assign.targets[0]
        while isinstance(lval, ast.Attribute):
            self.attrs.append(lval.attr)
            lval = lval.value
        self.attrs.append(lval.id) # `lval` should be `ast.Name` here
        self.attrs.reverse()
        self.lval = assign.targets[0] # Save original lvalue for later use
        self.set_lvstr()


    def set_lvstr(self):
      """
      Sets the `lvstr` value based on all the attributes in `self.attrs`
      Should only be called be `__init__`.
      """
      self.lvstr = None
      for attr in self.attrs:
        if self.lvstr == None:
          self.lvstr = attr
        else:
          self.lvstr += "_" + attr


    def new_id(self, store = False, shadow = False):
        """
        Returns an assignment lvalue equivalent to the one with which this
        `ModuleAssignLV` was initialized, though possibly with a different
        `ctx` value depending on `store`.
        """
        res = copy.deepcopy(self.lval)
        if store:
          res.ctx = ast.Store()
        else:
          res.ctx = ast.Load()
        return res

    def new_shadow_id(self, store = False):
        """
        Returns an an assignment lvalue AST node similar to the result of
        `new_id()`, but with a name prefixed by "__" and suffixed by "_MODULE__"
        """
        shadow_name = "__" + self.lvstr + "_MODULE__"
        return name_id(shadow_name, store)


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
        Translates a module instantiation (``m = Module(M(...))``) into
        an instrumented instantiation :
        
        >>> instrument.module_inst_begin()
        >>> m = BuilderId("m")
        >>> __m_MODULE__ = M(...)
        >>> instrument.module_inst_end(__m_MODULE__)
        >>> BuilderInst(m, __m_MODULE__)

        Parameters
        ----------
        assign (ast.Assign): An AST node instantiating a module
        """
        assign = self.generic_visit(assign)
        call = assign.value         # Should be `ast.Call` type
        lval = ModuleAssignLV(assign)
        instName = ast.Str(s = lval.lvstr)
        modClassInit = call.args[0] # Also `ast.Call` type
        modClassName = ast.Str(s = modClassInit.func.id)

        # Prologue and epilogue
        beginFunc = instrument.module_inst_begin.__name__
        endFunc = instrument.module_inst_end.__name__
        begin = inst_call(beginFunc, [instName, modClassName])
        end = inst_call(endFunc, [lval.new_shadow_id()])


        # Turn assignment `m = Module(M(...))` into a `BuilderId` declaration
        # and a `_MODULE__` declaration
        pid = make_call(pyrast.Id.__name__, [instName]).value
        bid = make_call(BuilderId.__name__, [pid]).value
        idAssign = ast.Assign([lval.new_id(store = True)], bid)
        modAssign = ast.Assign([lval.new_shadow_id(store = True)], modClassInit)
  
        # Make a `BuilderInst` call to generate a context update
        blval = lval.new_id(store = False)
        binst_args = [blval, lval.new_shadow_id()]
        binst = make_call(BuilderInst.__name__, binst_args)

        res = [begin, idAssign, modAssign, end, binst]
        for i in res:
          print ast.dump(i)
        return res

    def instrument_builder_dec(self, assign):
        """
        Translates a circuit element (wire or register) declaration of the form
        ``w = Wire(type)`` into an identifier assignment and a ``Wire()`` call:
        ``w = BuilderId("w")`` and ``Wire(type, idt="w")``
        """
        assign = self.generic_visit(assign)
        call = assign.value
        func = call.func.id
        lvid = ModuleAssignLV(assign)
        elemName = ast.Str(s = lvid.lvstr)

        pid = make_call(pyrast.Id.__name__, [elemName]).value
        bid = make_call(BuilderId.__name__, [pid]).value
        newAssign = ast.Assign([lvid.new_id(store = True)], bid)
        newCall = copy.deepcopy(call)
        newCall.keywords.append(ast.keyword(arg="idt", value=lvid.new_id()))
        print "new assign: "+str(ast.dump(newAssign))
        print "new call: "+str(ast.dump(newCall))
        return [newAssign, ast.Expr(newCall)]

    def instrument_when(self, if_stmt):
        """
        Translates an if statement with a `When()`-wrapped test field into
        a series of calls into the builder runtime that generates a `WhenStmt`.

        More specifically, ``if When(cond): [ifbody] else: [elsebody]`` becomes:

        >>> builder.when_begin(cond)
        >>> ifbody
        >>> builder.when_else()
        >>> elsebody
        >>> builder.when_end()
        """
        if_stmt = self.generic_visit(if_stmt)
        cond = if_stmt.test.args[0]
        print "COND: "+str(cond)
        
        begin = inst_call(instrument.when_begin.__name__, [cond])
        else_call = inst_call(instrument.when_else.__name__, [])
        end = inst_call(instrument.when_end.__name__, [])

        res = [begin] + if_stmt.body + [else_call] + if_stmt.orelse + [end]
        return res

    def instrument_wiring(self, aug_assign):
        """
        Transforms a wiring operator ``w1 //= w2`` into ``Connect(w1, w2)``.

        Parameters
        ----------
        aug_assign (ast.AugAssign) A Python AST for ``//=``
        """
        lhs = copy.deepcopy(aug_assign.target)
        rhs = copy.deepcopy(aug_assign.value)
        for term in [lhs, rhs]:
            term.ctx = ast.Load()
        res = make_call(builder.BuilderAST.Connect.__name__, [lhs, rhs])
        print "NEW WIRING : "+ast.dump(res)
        return res

    def check_for_module_instance(self, assign):
        """
        Returns true iff `assign` is a wrapped instantiation of a module, of the
        form ``m = Module(M(...))``
        """
        lval = assign.targets[0]    # Should be an `ast.Name`
        if isinstance(assign.value, ast.Call):
            call = assign.value
            if call.func.id == "Module":
                return True
        return False

    def check_for_builder_dec(self, assign):
        """
        Returns true iff `assign` os a wrapped `BuilderAST.BuilderDec` instance
        of the form `x = Wire(type, onReset)`.
        """
        lval = assign.targets[0]
        if isinstance(assign.value, ast.Call):
            call = assign.value
            if call.func.id in [Wire.__name__, Reg.__name__]:
                return True
        return False

    def check_for_when(self, if_stmt):
        """
        Returns true iff `if_stmt` has a `test` field consisting of a `When()`
        statement.
        """
        if isinstance(if_stmt.test, ast.Call):
          if if_stmt.test.func.id == 'When':
            return True
        return False

    def visit_Assign(self, node):
        if self.check_for_module_instance(node):
            return self.instrument_instance(node)
        if self.check_for_builder_dec(node):
            return self.instrument_builder_dec(node)
        return node

    def visit_AugAssign(self, node):
        if isinstance(node.op, ast.FloorDiv):
            return self.instrument_wiring(node)
        return node

    def visit_ClassDef(self, node):
        if self.check_for_module(node):
            return self.instrument_module(node)
        return node

    def visit_If(self, node):
        if self.check_for_when(node):
          return self.instrument_when(node)
        return node
