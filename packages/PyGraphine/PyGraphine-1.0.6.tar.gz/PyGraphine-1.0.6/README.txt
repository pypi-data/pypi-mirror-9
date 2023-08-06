1. To install in userspace run:

$ python setup.py install --user

or to setup in global space

$ sudo setup.py install

2. Run tests:

$ cd graphine/test/; python graph_operations_test.py; cd ../..
$ cd graphine/test/; python graph_test.py; cd ../..

You must see "OK" after test execution

3. Run simple example from python CLI interface:

>>> import graphine
>>> g = graphine.Graph.from_str("e11|e|")
>>> print g
e11|e|
>>> print g.edges(0, 1)
(((0, 1), ), ((0, 1), ))
>>> print g.external_edges
(((0,), ), ((1,), ))

4. Full documentation for this package is available here:
http://graphstate-and-graphine.readthedocs.org/en/latest/
