"""
Builder Instrumentation Routines.

Contains functions to be injected by the builder into Python ASTs prior to
elaboration.  These update the current context with information about
the names of modules, wires, etc.
"""
import builder

def module_begin(name):
    """
    When called at the beginning of a `Module` definition, this
    function registers its caller with the Builder system, and creates
    a new context.
    """
    print "Making context for "+name
    nc = builder.BuilderContext(name)
    builder.classContextStack.append(builder.curClassContext)
    builder.curClassContext = nc
    builder.allClassContexts[name] = nc

def module_end(name):
    """
    When called at the end of a `Module` definition, this function
    resets the current context back to the enclosing one and performs
    any other needed cleanup.
    """
    print "Finished with context for "+name
    print builder.curClassContext.updates
    builder.curClassContext = builder.classContextStack.pop()


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

    builder.instanceContextStack.append(context)

def module_inst_end(module):
    """
    When called just after a `Module` instantiation, this pops the instance
    context stack and does any other necessary cleanup.

    Parameters
    ----------
    module (Module): The module whose ``__init__()`` method was just called.
    """
    print "EXITING INSTANCE CONTEXT FOR "+str(module)
    context = builder.instanceContextStack.pop()
    context.module = module
    builder.allInstanceContexts[module] = context
