from pyrast import *
import inspect

BaseContextName = "__BASE_CONTEXT__"
NewContextName = "__NEW_CONTEXT__"


class BuilderContext(object):
    """
    Encapsulates all state pertaining an elaboration.
    """
    def __init__(self, name = NewContextName):
        self.updates = []
        self.instanceCount = 0
        self.name = name

    def renameIds(self):
        """
        Replaces all `BuilderId` instances in this context with unique
        PyRRHIC `Id`s.
        """
        rmap = self.renameMap()
        def replace(expr):
            if isinstance(expr, BuilderAST.BuilderId):
                print "Renaming expression "+str(expr)
                return rmap[expr]
            else:
                return expr
        for u in self.updates:
            print "Renaming update "+str(u)
            u.traverse_exprs(replace)

    def renameMap(self):
        """
        Builds a renaming of all `BuilderId` instances in this context
        to unique PyRRHIC `Id`s
        """
        names = self.collectIds()
        renameMap = {}
        for name in names:
            # Give the first entry the "real" name and make temporary ids
            # for all the other instances
            idt = names[name][0]
            renameMap[idt] = Id(name)
            if len(names[name]) > 1:
                cnt = 0
                for idt in names[name][1:]:
                    renameMap[idt] = Id("_t_"+name+"_"+str(cnt))
                    cnt += 1
        return renameMap

    def collectIds(self):
        """
        Makes a dictionary containing every string ised in a `BuilderId` in
        this context.  Each value contains all `BuilderId`s using that name.
        """
        names = {}
        for u in self.updates:
            if isinstance(u, BuilderAST.BuilderDec):
                print "\tCollected "+str(u.idt)
                if u.idt.__name__.__idt__ in names:
                    names[u.idt.__name__.__idt__] += [u.idt]
                else:
                    names[u.idt.__name__.__idt__] = [u.idt]
        return names

# Always contains the context in which to log the next update
cur_context = BuilderContext(BaseContextName)
context_stack = []


# Tracks which `BuilderContext` corresponds to each module type based on the
# string of each type's name.
allClassContexts = {}
allClassContexts[BaseContextName] = BuilderContext(BaseContextName)


# Tracks which `BuilderInstanceContext` corresponds to each module instance
# based on each instance's reference (that is, ``allInstanceContexts[m]``
# contains module `m`'s context.)
allInstanceContexts = {}

# When an instance is elaborated, it gets added to this dict and removed
# from `allInstanceContexts`.
elaboratedInstances = {}

# When an instance is elaborated, its desired name is added to this dictionary.
# If a name is already present, the instance is renamed to ahve a name that
# ends with `_N` where `N` is the current number of modules with that name.
instanceNames = {}

# Contains the nearest-enclosing conditional expression
cond_stack = []

def elaborate_all_instances():
    global allInstanceContexts
    global elaboratedInstances

    # All instance contexts must be renamed before elaboration
    # so that the new names are propagated into the PyRRHIC AST nodes.
    for inst in allInstanceContexts:
      allInstanceContexts[inst].rename()

    for inst in allInstanceContexts:
        ic = allInstanceContexts[inst]
        ic.renameIds()
        stmts = []
        for u in ic.updates:
            stmts += [u.elaborate()]
        mdec = ModuleDec(ic.name, ic.module.io, stmts)
        elaboratedInstances[inst] = mdec
    allInstanceContexts = {}


class BuilderInstanceContext(BuilderContext):
    """
    Contains all information pertaining to the elaboration of an instance
    of a PyRRHIC module.
    """
    def __init__(self, instanceName, classContext, module):
        """
        Parameters
        ----------
        instanceName (str): name of the instance of this module
        classContext (BuilderContext): context for the class that of which
                                        this module is an instance.
        module (Module): instance associated with this context.
        """
        self.instanceName = instanceName
        self.className = classContext.name
        self.classContext = classContext
        self.instanceCount = classContext.instanceCount
        self.name = classContext.name + "_INSTANCE"
        self.updates = [] + classContext.updates

    def rename(self):
        """
        Sets the name of this instance context to one that does not yet
        appear in the global `instanceNames` dictionary.
        """
        print "Module = "+str(self.module)
        desired_name = self.module.derived_name()
        if desired_name in instanceNames:
            count = len(instanceNames[desired_name])
            self.name = "_" + desired_name + "_" + str(count)
            instanceNames[desired_name].append(self)
        else:
            self.name = desired_name
            instanceNames[desired_name] = [self]
        return self.name
