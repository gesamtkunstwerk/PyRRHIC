from pyrrhic.builder import context as ctx
from pyrrhic.pyrast import ModuleDec

def elaborate_all_instances():
    # All instance contexts must be renamed before elaboration
    # so that the new names are propagated into the PyRRHIC AST nodes.
    for inst in ctx.all_instance_contexts:
      ctx.all_instance_contexts[inst].rename()

    for inst in ctx.all_instance_contexts:
        ic = ctx.all_instance_contexts[inst]
        ic.renameIds()
        stmts = []
        for u in ic.updates:
            stmts += [u.elaborate()]
        mdec = ModuleDec(ic.name, ic.module.io, stmts)
        ctx.elaborated_instances[inst] = mdec
    ctx.all_instance_contexts = {}

