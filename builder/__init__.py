from pyrast import *
import inspect

# Invariant: this should always contain a NEW context to into which the
# the next module declaration dumps its updates, and then can rename and
# add to the `allClassContexts` dictionary once it's done.
curClassContext = None

# The top of this stack should always be `curClassContext`.  It is pushed
# to and popped from whenever entering and exiting a `Module` class
# definition's body, respectively.
classContextStack = []

# Tracks the mapping of class names to their class contexts.
allClassContexts = {}

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
            u.traverseExprs(replace)

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
                if u.idt.name.idt in names:
                    names[u.idt.name.idt] += [u.idt]
                else:
                    names[u.idt.name.idt] = [u.idt]
        return names


# When a `Module` is defined, members declared in its body are to be added here
curClassContext = BuilderContext(NewContextName)

# Tracks which `BuilderContext` corresponds to each module type based on the
# string of each type's name.
allClassContexts[BaseContextName] = BuilderContext(BaseContextName)

# The top of this stack contains the conext into which any wire/register
# declarations should be added.
instanceContextStack = []

# Tracks which `BuilderInstanceContext` corresponds to each module instance
# based on each instance's reference (that is, ``allInstanceContexts[m]``
# contains module `m`'s context.)
allInstanceContexts = {}

def elaborateAll():
    print allInstanceContexts
    for inst in allInstanceContexts:
        ic = allInstanceContexts[inst]
        ic.renameIds()
        stmts = []
        for u in ic.updates:
            print u
            stmts += [u.elaborate()]
        print stmts
        return stmts

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
        self.classContext = classContext
        self.updates = [] + classContext.updates
