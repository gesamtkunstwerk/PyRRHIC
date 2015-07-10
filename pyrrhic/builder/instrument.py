"""
Builder Instrumentation Routines.

Contains functions to be injected by the builder into Python ASTs prior to
elaboration.  These update the current context with information about
the names of modules, wires, etc.
"""
from pyrrhic.pyrast.expr import Id
from pyrrhic.builder import context as ctx
from pyrrhic.builder.bdast import BuilderWhen, Block, BuilderId, BuilderInst

def module_begin(name):
    """
    When called at the beginning of a `Module` definition, this
    function registers its caller with the Builder system, and creates
    a new ctx.
    """
    nc = ctx.BuilderContext(name)
    ctx.context_stack.append(ctx.cur_context)
    ctx.cur_context = nc
    ctx.all_class_contexts[name] = nc

def module_end(name):
    """
    When called at the end of a `Module` definition, this function
    resets the current context back to the enclosing one and performs
    any other needed cleanup.
    """
    ctx.cur_context = ctx.context_stack.pop()


def module_inst_begin(class_name):
    """
    When called at the beginning of a `Module`'s' ``__init__()`` method,
    this creates a new context for that module and adds it to the instance 
    stack.

    Parameters
    ----------
    class_name (str): The (string) name of the class of module being instantiated
    """
    class_context = ctx.all_class_contexts[class_name]

    # `instance_name` is set afterwards by other instrumentation code,
    # and `module` is set by `module_inst_end`
    context = ctx.BuilderInstanceContext( \
        instance_name = None,             \
        class_context = class_context,    \
        module        = None) 

    ctx.context_stack.append(ctx.cur_context)
    ctx.cur_context = context

def module_inst_end(module):
    """
    When called just after a `Module` instantiation, this pops the instance
    context stack and does any other necessary cleanup.

    Parameters
    ----------
    module (Module): The module whose ``__init__()`` method was just called.
    """
    ctx.cur_context.module = module
    module.__context__ = ctx.cur_context
    ctx.all_instance_contexts[module] = ctx.cur_context
    ctx.cur_context = ctx.context_stack.pop()

def make_builder_instance(instance, class_name, inst_name=None):
    """
    Returns a new `BuilderId` referring to `instance` and  updates the current
    context to contain a new `BuilderInstance`.

    Parmeters
    ---------
    inst_name (str): The actual string name of the instance, or `None` if 
                      this is an impicit instance

    instance (Module): The module instance just created

    class_name (str): The string name of the class instantiated
    """
    id = ctx.cur_context.make_builder_id(inst_name)
    binst = BuilderInst(id, instance)
    #ctx.all_instance_contexts[instance].instance_name = inst_name
    return id

def when_begin(cond_expr):
    """
    Pushes conditional `cond_expr` onto the current when condition stack in 
    order to associate it with all the statements contained in the if and 
    else clauses.
    """
    ctx.cond_stack.append(cond_expr)
    # Need to make a new `BuilderContext` so that the updates performed within
    # this `When()` block are distinguished from those outside of it.
    bc = ctx.BuilderContext("__TEMP_WHEN_CONTEXT__")
    ctx.context_stack.append(ctx.cur_context)
    ctx.cur_context = bc

def when_else():
    bc = ctx.BuilderContext("__TEMP_ELSE_CONTEXT__")
    ctx.context_stack.append(ctx.cur_context)
    ctx.cur_context = bc

def when_end():
    """
    Pops the current condition stack at the end of a when statment's body
    in order to generate the final update AST node.
    """
    cond = ctx.cond_stack.pop()
    else_body = ctx.cur_context
    if_body = ctx.context_stack.pop()
    ctx.cur_context = ctx.context_stack.pop()
    upd = BuilderWhen(cond, Block(if_body.updates), Block(else_body.updates))
    ctx.cur_context.updates.append(upd)
