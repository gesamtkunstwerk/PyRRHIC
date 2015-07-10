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
syntax as a substitute for _real_ documentation.

Try creating some PyRRHIC circuits by following the example in `test.py`.
You will find bugs, or language features you don't like.  When you do,
fix them and make a pull request.

Just for the sake of example, consider the following code from `test.py`:
```python
class Counter(Module):
  class CounterIO(BundleDec):
    start     = UInt(1)
    finished  = Reverse(UInt(1))


  def __init__(self, max_val):
    self.io = Wire(Counter.CounterIO())
    self.max_val = max_val
    cnt = Reg(UInt(width=Log2Up(max_val)))
    fin = Reg(UInt(1))

    self.io.finished //= fin
    if When(self.io.start):
      cnt //= Lit(0)
      fin //= Lit(0)
    elif When(cnt == Lit(max_val)):
      fin //= Lit(1)
    elif When(~fin):
      cnt //= (cnt + Lit(1))

c = Module(Counter(17))
```

Compiling this code with PyRRHIC results in the following pseudo-IR:

```
module Counter:
  wire self_io : { default start : UInt<1>, reverse finished : UInt<1> }
  reg cnt : UInt<4>
  reg fin : UInt<1>
  self_io.finished := fin
  when self_io.start:
    cnt := 0
    fin := 0
  else:
    when cnt == 16:
      fin := 1
    else:
      when ~fin:
        cnt := cnt + 1
```

## Structure

PyRRHIC to (Pseudo-)FIRRTL compilation consists of these phases:

1. Instrumentation / AST Generation

  - This phase uses Python's own AST library to parse the PyRRHIC input,
    walk the AST, and instrument PyRRHIC-related constructs with calls into
    the builder (see below).
   - This is done by `builder/astgen.py`, which
    inserts calls to the routines in `builder/instrument.py`

2. Elaboration / Execution
  - When the instrumented AST is executed, the user's Python program calls
  into the *builder*, which tracks wire and register declarations, module
  definitions and instantiations.  Each of these results in an *update* to
  the current *context*, which is associated with some module or instance.
  There is a context stack in `builder/context.py` which is modified
  whenever entering or exiting a new module or instance definition.

3. Translation

  - After the user's (instrumented) Python code has executed, the set of
  contexts created in the builder is traversed, and each context's set 
  of updates is transformed into a list of FIRRTL circuit element 
  declarations.  A pre-processing step converts all temporary identifiers
  (`BuilderId` objects) into real identifiers and resolves namespace
  collisions by renaming in the case of conflicts.

4. *TODO* Type Checking and Error Reporting
  
  - Somebody needs to do this..

## TODOs

PyRRHIC won't be useful without a large amount of additional work.  The
current output can't even be tested until the FIRRTL compiler is released,
so it obviously far from correct or complete.  Here are some of the bigger
known issues:

1. Module IOs don't follow the current FIRRTL spec.
  
  - We currently declare an explicit `io` field in each module, whereas
  FIRRTL requires that explicit `input` and `output` statements be made
  at the beginning of a module's body.

2. There are no error messages.
  
  - Well, there's also no type checking, or syntactic checking.  
  What's needed
  is a general strategy for propagating error messages up from the inside
  to the user.  The line number information from the original PyRRHIC
  Python source file is available during the instrumentation phase, and
  needs to be added into the builder AST.
  
  - There are also PyRRHIC-specific errors that need to be detected. For
  example, if a module instantiation is not wrapped in `Module()`, this
  should be caught at elaboration time, and reported.  Modules also
  must always list `Module` as a base class, even if they inherit from
  another class that derives from `Module`.  This is because the 
  instrumentation phase needs to see this relationship syntactically, 
  without access to the actual type hierarchy.

3. No memories yet.  Need to `Mem` and `accessor` types.

4. Various FIRRTL `primop`s are missing -- look at the AST files for details

5. We need to coalesce module instances with identical bodies. 

  - Currently, every single module instantiation results in a unique module
  type declaration, which is not ideal.
