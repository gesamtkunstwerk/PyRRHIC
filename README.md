# PyRRHIC -- Python RTL Refactoring and High-level IC Constructor

## Overview
PyRRHIC is designed to act as a Python front-end to the greater Chisel/EDEN
ecosystem (https://chisel.eecs.berkeley.edu) for hardware design.  It
emits, presently, a FIRRTL-like IR.

To try it out, run:

```
$> python pyrrhic.py test.py
```

This will result in a text dump of the pseudo-FIRRTL IR derived from the
elaboration of PyRRHIC Python code in `test.py`.  This file does not
contain any _real_ circuits, but merely lists exampls of the PyRRHIC 
syntax as a surrogate for documentation.


## Structure

PyRRHIC to (Pseudo-)FIRRTL compilation consists of these phases:

1. Instrumentation / AST Generation
2. Elaboration / Execution
3. Translation
4. *TODO* Type Checking and Error Reporting

## TODOs

PyRRHIC won't be useful without a large amount of additional work.  The
current output can't even be tested until the FIRRTL compiler is released,
so it obviously far from correct or complete.  Here are some of the bigger
known issues:

1. Module IOs don't follow the current FIRRTL spec.
  We currently declare an explicit `io` field in each module, whereas
  FIRRTL requires that explicit `input` and `output` statements be made
  at the beginning of a module's body.
2. There are no error messages.
  Well, there's also no type checking, or syntactic checking.  What's needed
  is a general strategy for propagating error messages up from the inside
  to the user.  The line number information from the original PyRRHIC
  Python source file is available during the instrumentation phase, and
  needs to be added into the builder AST.
3. No memories yet.  Need to `Mem` and `accessor` types.
4. Various FIRRTL `primop`s are missing -- look at the AST files for details
5. We need to coalesce module instances with identical bodies. 
  Currently, every single module instantiation results in a unique module
  type declaration, which is not ideal.
