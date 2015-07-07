#!/usr/bin/python
"""
Compiles a PyRRHIC Source File.
"""
from builder import astgen
import sys

if len(sys.argv) < 2:
  print "Usage: pyrric [sources]"
  sys.exit(-1)

for a in sys.argv[1:]:
  code = astgen.compile_pyrrhic(a)
  exec(code)

builder.elaborate_all_instances()

print "\n\n---------------\n"
for ctx in builder.elaboratedInstances:
    mdec = builder.elaboratedInstances[ctx]
    print str(mdec)
    print "\n"
