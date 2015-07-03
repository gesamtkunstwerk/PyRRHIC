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
