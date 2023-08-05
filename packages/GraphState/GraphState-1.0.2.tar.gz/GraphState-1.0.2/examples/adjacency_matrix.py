#!/usr/bin/python



import sys
import nickel

name = sys.argv[1]

edges = nickel.Nickel(string=name).edges
adj = nickel.Nickel(string=name).adjacent
nickel_ = str(nickel.Canonicalize(edges))

if name <> nickel_:
    raise ValueError, "Non mininal nickel index %s, minmal = %s" % (name, nickel_)

external = dict()
print "   ", " ".join(map(str, adj.keys()))
print
for node in adj:
    print node, " ",
    ext = adj[node].count(-1)
    if ext > 0:
        external[node] = ext
    for node_ in adj:
        cnt = adj[node].count(node_)
        print cnt,
    print

print
print "external legs :"
for node in external:
    print "   vertex %s: %s leg(s)" % (node, external[node])