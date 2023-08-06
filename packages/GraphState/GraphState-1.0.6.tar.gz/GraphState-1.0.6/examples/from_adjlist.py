#!/usr/bin/python
#
# Script creates GraphState object from given adjacency list
# For example: 
#   $ python from_adjlist.py "[[-1, 0], [0, 1], [0, 2], [1, 2], [1, 3], [2, 3], [3, -1]]"
# Expected output:
#   e12|23|3|e|

import graph_state
import sys



adjlist = eval(sys.argv[1])
adjlist = map(lambda e: graph_state.Edge(e), adjlist)

print graph_state.GraphState(adjlist)
