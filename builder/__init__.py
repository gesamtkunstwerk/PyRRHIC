from pyrast import *
import inspect

class BuilderContext(object):
    """
    Encapsulates all state pertaining an elaboration.
    """

    # Invariant: this should always contain a NEW context to into which the
    # the next module declaration dumps its updates, and then can rename and
    # add to the `allContexts` dictionary once it's done.
    curContext = None

    allContexts = {}

    BaseContextName = "__BASE_CONTEXT__"
    NewContextName = "__NEW_CONTEXT__"

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
            if isinstance(expr, BuilderId):
                return rmap[expr]
            else:
                return expr
        for u in self.updates:
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
            if u.isDec:
                if u.idt.idt in names:
                    names[u.idt.idt] += [u.idt]
                else:
                    names[u.idt.idt] = [u.idt]
        return names

    def elaborateAll(self):
        bc = self.allContexts[self.BaseContextName]
        stmts = []
        for u in bc.updates:
            print u
            stmts += [u.elaborate()]
        return stmts

BuilderContext.curContext = BuilderContext(BuilderContext.NewContextName)
BuilderContext.allContexts[BuilderContext.BaseContextName] = \
    BuilderContext(BuilderContext.BaseContextName)
