"""
The PyRRHIC Abstract Syntax Tree representation
"""

from expr import *
from stmt import *
from pyrtype import *
import inspect

class LineInfo:
    """
    Contains Python source file and line number information to associate
    with a PyRRHIC AST node.

    Extracted using Python's `inspect.currentframe` routine
    """

    def __init__(self, frames = 2):
        """
        Constructs a `LineInfo` object from the current stack trace.

        Parameters
        ----------

        frames: Int
            The number of stack frames outward needed to obtain the line
            of PyRRHIC source generating this AST node.

        """
        # The actual line of interest should correspond to the third
        # innermost stack frome.
        frameInfo = None
        #print inspect.getouterframes(inspect.currentframe())
        frameInfo = inspect.getouterframes(inspect.currentframe())[frames]
        self.source = frameInfo[1]
        self.line   = frameInfo[2]
        self.module = frameInfo[3]
        self.string = frameInfo[4]

    def assignedVar(self):
        """
        If this line is an assignment, return the name of the variable LValue.
        """
        return self.string[0].split("=")[0].strip()
