"""
Builder Instrumentation Routines.

Contains functions to be injected by the builder into Python ASTs prior to
elaboration.  These update the current context with information about
the names of modules, wires, etc.
"""
import builder
from builder.BuilderAST import BuilderWhen, Block

def module_begin(name):
    """
    When called at the beginning of a `Module` definition, this
    function registers its caller with the Builder system, and creates
    a new context.
    """
    nc = builder.BuilderContext(name)
    builder.context_stack.append(builder.cur_context)
    builder.cur_context = nc
    builder.allClassContexts[name] = nc

def module_end(name):
    """
    When called at the end of a `Module` definition, this function
    resets the current context back to the enclosing one and performs
    any other needed cleanup.
    """
    builder.cur_context = builder.context_stack.pop()


def module_inst_begin(instanceName, className):
    """
    When called just before a `Module`'s' ``__init__()`` method, this creates a new
    context for that module and adds it to the instance stack.

    Parameters
    ----------

    instanceName (str): The (string) name of the instance being created

    className (str): The (string) name of the class of module being instantiated
    """
    classContext = builder.allClassContexts[className]
    context = builder.BuilderInstanceContext( \
        instanceName = instanceName,  \
        classContext = classContext,  \
        module = None) # Will be set afterwards by `module_init_end`
    builder.context_stack.append(builder.cur_context)
    builder.cur_context = context

def module_inst_end(module):
    """
    When called just after a `Module` instantiation, this pops the instance
    context stack and does any other necessary cleanup.

    Parameters
    ----------
    module (Module): The module whose ``__init__()`` method was just called.
    """
    builder.cur_context.module = module
    module.__context__ = builder.cur_context
    builder.allInstanceContexts[module] = builder.cur_context
    builder.cur_context = builder.context_stack.pop()
  
def when_begin(cond_expr):
    """
    Pushes conditional `cond_expr` onto the current when condition stack in 
    order to associate it with all the statements contained in the if and 
    else clauses.
    """
    builder.cond_stack.append(cond_expr)
    # Need to make a new `BuilderContext` so that the updates performed within
    # this `When()` block are distinguished from those outside of it.
    bc = builder.BuilderContext("__TEMP_WHEN_CONTEXT__")
    builder.context_stack.append(builder.cur_context)
    builder.cur_context = bc

def when_else():
    bc = builder.BuilderContext("__TEMP_ELSE_CONTEXT__")
    builder.context_stack.append(builder.cur_context)
    builder.cur_context = bc

def when_end():
    """
    Pops the current condition stack at the end of a when statment's body
    in order to generate the final update AST node.
    """
    cond = builder.cond_stack.pop()
    else_body = builder.cur_context
    if_body = builder.context_stack.pop()
    builder.cur_context = builder.context_stack.pop()
    upd = BuilderWhen(cond, Block(if_body.updates), Block(else_body.updates))
    builder.cur_context.updates.append(upd)
