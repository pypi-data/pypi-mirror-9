#!/usr/bin/python

import sys
import nickel

name = sys.argv[1]

edges = nickel.Nickel(string=name).edges
adj = nickel.Nickel(string=name).adjacent
nickel_ = str(nickel.Canonicalize(edges))

if name <> nickel_:
    raise ValueError, "Non mininal nickel index %s, minmal = %s" % (name, nickel_)

print nickel.Nickel(string=name).edges

