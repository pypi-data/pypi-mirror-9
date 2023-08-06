#!/usr/bin/python
#
# Script generates graph picture using pydot library (You NEED installed pydot)
#
# Sample input:
#   $ python draw.py "e11|e|"
# Output will be a file "e11|e|.png" placed in script folder
#

import nickel

import os
import sys

try:
    import pydot
except ImportError:
    print "you need to install pydot module for python, also you may need to install graphviz"
    sys.exit(1)

def prepare(nomenkl):
    def isInternal(node):
        return node <> -1

    edges = nickel.Nickel(string=nomenkl).edges

    lines = []
    nodes = dict()
    ext_cnt = 0
    for edge in edges:
        nodes__ = list()
        for node in edge:
            if isInternal(node):
                nodes__.append(("%s_%s" % (nomenkl, node), "%s" % node))
            else:
                nodes__.append(("%s_E_%s" % (nomenkl, ext_cnt), "ext"))
                ext_cnt += 1
            if nodes__[-1][0] not in nodes.keys():
                nodes[nodes__[-1][0]] = nodes__[-1][1]
        lines.append([n[0] for n in nodes__])
    return nodes, lines


def Cluster(nomenkl):
    fontsize = "12"
    width = "0.1"
    nodes, lines = prepare(nomenkl)
    cluster = pydot.Cluster(nomenkl.replace('|', '_'), label=nomenkl)
    for node in nodes:
        if nodes[node] == 'ext':
            cluster.add_node(pydot.Node(node, label='""', fontsize=fontsize, width=width, color='white'))
        else:
            cluster.add_node(pydot.Node(node, label='"%s"'%nodes[node], fontsize=fontsize, width=width))

    for line in lines:
        cluster.add_edge(pydot.Edge(line[0], line[1]))
    return cluster


def save_png(nomenkl, filename=None ):
    if filename == None:
        filename = "%s.png" % nomenkl
        G = pydot.Dot(graph_type="graph")
        G.add_subgraph(Cluster(nomenkl))
#        print G.to_string()
        open(filename, 'w').write(G.create_png())
    return filename

name = sys.argv[1]

edges = nickel.Nickel(string=name).edges
nickel_ = str(nickel.Canonicalize(edges))

if name <> nickel_:
    raise ValueError, "Non mininal nickel index %s, minmal = %s" % (name, nickel_)

res = save_png(name)
print "File %s created in %s" % (res, os.getcwd())
