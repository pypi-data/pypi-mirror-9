__all__ = ["colls", "edit", "keys", "notebook", "query", "view"]

# these lines here are to let ipython find tregex
import os
import corpkit
path_to_module = os.path.dirname(corpkit.__file__)
os.environ["PATH"] += os.pathsep + path_to_module

from query import interrogator
from query import interroplot
from query import dependencies
from query import multiquery
from query import conc
from query import topix_search

from view import plotter
from view import table
from view import topix_plot
from view import tally
from view import quickview

from keys import keywords
from colls import collocates

from edit import merger
from edit import surgeon
from edit import mather

from notebook import report_display