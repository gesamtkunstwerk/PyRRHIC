import inspect
from pyrrhic.pyrast import Id

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
        from pyrrhic.builder import bdast
        def replace(expr):
            if isinstance(expr, bdast.BuilderId):
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
        from pyrrhic.builder import bdast
        for u in self.updates:
            if isinstance(u, bdast.BuilderDec):
                print "\tCollected "+str(u.idt)
                if u.idt.__name__.__idt__ in names:
                    names[u.idt.__name__.__idt__] += [u.idt]
                else:
                    names[u.idt.__name__.__idt__] = [u.idt]
        return names

    def make_builder_id(self, name):
        """
        Returns a new `bdast.BuilderId` with name `name`, or creates
        a new temporary name if `name` is `None`.

        name (str): String name from which to create an identifier
        """
        from pyrrhic.builder.bdast import BuilderId
        if name == None:
            name_str = "_"+self.name+"_tmp_"
            id = BuilderId(Id(name_str))
        else:
            id = BuilderId(Id(name))
        return id

# Always contains the context in which to log the next update
cur_context = BuilderContext(BaseContextName)
context_stack = []


# Tracks which `BuilderContext` corresponds to each module type based on the
# string of each type's name.
all_class_contexts = {}
all_class_contexts[BaseContextName] = BuilderContext(BaseContextName)


# Tracks which `BuilderInstanceContext` corresponds to each module instance
# based on each instance's reference (that is, ``all_instance_contexts[m]``
# contains module `m`'s context.)
all_instance_contexts = {}

# When an instance is elaborated, it gets added to this dict and removed
# from `all_instance_contexts`.
elaborated_instances = {}

# When an instance is elaborated, its desired name is added to this dictionary.
# If a name is already present, the instance is renamed to ahve a name that
# ends with `_N` where `N` is the current number of modules with that name.
instance_names = {}

# Contains the nearest-enclosing conditional expression
cond_stack = []

class BuilderInstanceContext(BuilderContext):
    """
    Contains all information pertaining to the elaboration of an instance
    of a PyRRHIC module.
    """
    def __init__(self, instance_name, class_context, module):
        """
        Parameters
        ----------
        instance_name (str): name of the instance of this module
        class_context (BuilderContext): context for the class that of which
                                        this module is an instance.
        module (Module): instance associated with this context.
        """
        self.instance_name = instance_name
        self.className = class_context.name
        self.class_context = class_context
        self.instanceCount = class_context.instanceCount
        self.name = class_context.name + "_INSTANCE"
        self.updates = [] + class_context.updates

    def rename(self):
        """
        Sets the name of this instance context to one that does not yet
        appear in the global `instance_names` dictionary.
        """
        print "Module = "+str(self.module)
        desired_name = self.module.derived_name()
        if desired_name in instance_names:
            count = len(instance_names[desired_name])
            self.name = "_" + desired_name + "_" + str(count)
            instance_names[desired_name].append(self)
        else:
            self.name = desired_name
            instance_names[desired_name] = [self]
        return self.name
