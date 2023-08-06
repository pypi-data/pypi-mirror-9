#!/usr/bin/python
#
# Script prints adjacency list of graph by given Nickel index. 
# Example:
#   $ python adjacency_list.py "e11|e|"
# Expected output:
#   (((0,), ), ((0, 1), ), ((0, 1), ), ((1,), ))

import sys
import graph_state

name = sys.argv[1]

gs = graph_state.GraphState.from_str(name)

nickel_ = str(gs)
if name <> nickel_:
    raise ValueError, "Non mininal nickel index %s, minimal = %s" % (name, nickel_)

print gs.edges

