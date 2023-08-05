# -*- coding: utf-8 -*-
"""
This module provides complement functions for lib NetworkX
- Function to  compute bipartite  from two columns of nodes
    *understand third columns containing weight
    *
- Function to compute graph from a pandas adjancy matrix
NetworkX graphs and project it on one dimension.

"""

__version__ = "0.0.4"

from core import jaccard_distance
from core import inverse_norm1
from core import FromDataFrame
from core import graphFromPandasAdjancyMatrix
from core import mapBipartite
from core import projectGraph
from core import exportGEXF
from core import proclamer

