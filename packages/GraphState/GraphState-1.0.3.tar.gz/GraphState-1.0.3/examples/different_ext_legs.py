#!/usr/bin/python

import graph_state


def edges(adjlist):
    defaultField = 'a'
    extNodeMap = {-2: 'A', -3: 'B', -4: 'C'}
    edgeList = list()
    for edge in adjlist:
        nodes = list()
        fields = list()

        if edge[0] in extNodeMap:
            nodes = [-1, edge[1]]
            fields = ['0', extNodeMap[edge[0]]]
        elif edge[1] in extNodeMap:
            nodes = [edge[0], -1]
            fields = [extNodeMap[edge[1]], '0']
        else:
            nodes = edge
            fields = [defaultField, defaultField]

        edgeList.append(graph_state.Edge(nodes, fields=graph_state.Fields(fields)))
    return edgeList

# [-1,x], [-2,x], [-3,x], [-4,x] denotes an external leg connected to vertex x

# different ext legs will be marked by different fields associated with ext leg
# this works fine for simple models (like phi^4 model) and results in compact notation
#
# In general case colors (graph_state.Rainbow) must be used instead of fields


print "old style notation all ext legs are equivalent"

print "\n -1 -> a"
adjlist = [[-1, 0], [0, 1], [0, 2], [-1, 1], [1, 2], [1, 3], [-1, 2], [2, 3], [3, -1]]
print adjlist

print str(graph_state.GraphState(edges(adjlist)))

print "\nnew style notation : some ext legs marked as different"
print "\n -1 -> a, -2 -> A, -3 -> B, -4 -> C\n"


adjlist = [[-2, 0], [0, 1], [0, 2], [-3, 1], [1, 2], [1, 3], [-3, 2], [2, 3], [3, -2]]
print adjlist

print str(graph_state.GraphState(edges(adjlist)))

adjlist = [[-4, 0], [0, 1], [0, 2], [-3, 1], [1, 2], [1, 3], [2, 3], [3, -2]]
print adjlist

print str(graph_state.GraphState(edges(adjlist)))
