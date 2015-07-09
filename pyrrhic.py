#!/usr/bin/python
"""
Compiles a PyRRHIC Source File.
"""
from pyrrhic import builder
from pyrrhic.builder import elaborate_all_instances
from pyrrhic.builder import context as ctx
from pyrrhic.builder import astgen
import sys

if len(sys.argv) < 2:
  print "Usage: pyrric [sources]"
  sys.exit(-1)

for a in sys.argv[1:]:
  code = astgen.compile_pyrrhic(a)
  exec(code)

elaborate_all_instances()

print "\n\n---------------\n"
for c in ctx.elaborated_instances:
    mdec = ctx.elaborated_instances[c]
    print str(mdec)
    print "\n"
