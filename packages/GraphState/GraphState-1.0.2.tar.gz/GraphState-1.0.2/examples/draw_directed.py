#!/usr/bin/python

import nickel
import graph_state

import os
import sys

try:
    import pydot
except ImportError:
    print "you need to install pydot module for python, also you may need to install graphviz"
    sys.exit(1)


def prepare(gs_string):
    def isInternal(node):
        return node <> -1

    edges = graph_state.GraphState.fromStr(gs_string).edges

    lines = []
    nodes = dict()
    ext_cnt = 0
    for edge in edges:
        nodes__ = list()
        for node in edge.nodes:
            if isInternal(node):
                nodes__.append(("%s_%s" % (gs_string, node), "%s" % node))
            else:
                nodes__.append(("%s_E_%s" % (gs_string, ext_cnt), "ext"))
                ext_cnt += 1
            if nodes__[-1][0] not in nodes.keys():
                nodes[nodes__[-1][0]] = nodes__[-1][1]
#        print edge.nodes, edge.fields, edge.colors
        lines.append(([n[0] for n in nodes__], edge.fields, edge.colors))
    return nodes, lines


def Cluster(gs_string):
    fontsize = "12"
    width = "0.1"
    nodes, lines = prepare(gs_string)
    cluster = pydot.Cluster("%s" % gs_string.replace('-', '_').replace(':', '_'), label="\"%s\"" % gs_string)
    for node in nodes:
#        print node
        if nodes[node] == 'ext':
            cluster.add_node(pydot.Node("\"%s\"" % node, label='""', fontsize=fontsize, width=width, color='white'))
        else:
            cluster.add_node(pydot.Node("\"%s\"" % node, label='"%s"' % nodes[node], fontsize=fontsize, width=width))
#    print cluster.to_string()

    for line, fields, colors in lines:
        print line, fields, colors, "%s %s"%(fields,colors)
        label=""
        if fields is not None:
            label += str(fields).replace('0','')
        if colors is not None:
            label += " " + str(colors)
        cluster.add_edge(pydot.Edge("\"%s\"" % line[0], "\"%s\"" % line[1], label=label))
    return cluster


def save_png(nomenkl, filename=None ):
    if filename == None:
        filename = "%s.png" % nomenkl.replace(":","_")
        G = pydot.Dot(graph_type="digraph")
        G.add_subgraph(Cluster(nomenkl))
        print G.to_string()
        open(filename, 'w').write(G.create_png())
    return filename

name = sys.argv[1]

gs = graph_state.GraphState.fromStr(name)
nickel_ = str(gs)

if name != nickel_:
    raise ValueError, "Non mininal nickel index %s, minmal = %s" % (name, nickel_)

res = save_png(name)
print "File %s created in %s" % (res, os.getcwd())