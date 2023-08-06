1. To install in userspace run:

$ python setup.py install --user

or to setup in global space

$ sudo setup.py install

2. Run tests:

$ cd nickel; python nickel_test.py; cd ..
$ cd graph_state; python graph_state_test.py; cd ..

You must see "OK" after test execution

3. Run simple example from python CLI interface:

>>> import graph_state
>>> g = graph_state.GraphState.from_str("ee12|e22|e|")
>>> print g
ee12|e22|e|
>>> print g.edges
(((0,), ), ((0,), ), ((0, 1), ), ((0, 2), ), ((1,), ), ((1, 2), ), ((1, 2), ), ((2,), ))
>>> print g.nodes
[-1, 0, 1, 2]

4. Full documentation for this package is available here:
http://graphstate-and-graphine.readthedocs.org/en/latest/
