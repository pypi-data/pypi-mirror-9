#!/usr/bin/python

import nickel

# [-1,x] denotes an external leg connected to vertex x

adjlist = [[-1, 0], [0, 1], [0, 2], [1, 2], [1, 3], [2, 3], [3, -1]]

print str(nickel.Canonicalize(adjlist))


# no need for nodes to be ordered in some way
# and no need for ordering lines

adjlist = [[6, 4], [2, 4], [4, -1], [-1, 0], [0, 6], [0, 2], [6, 2]]

print str(nickel.Canonicalize(adjlist))