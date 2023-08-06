1.to install in userspace run:

$ python setup.py install --user

or to setup in global space

$ sudo setup.py install

2. run tests:

$ cd nickel; python nickel_test.py; cd ..
$ cd graph_state; python graph_state_test.py; cd ..

You must see "OK" after test execution

3. run simple example from python CLI interface:

>>> import graphine
>>> g = graphine.Graph.from_str("e11|e|")
>>> print g
e11|e|
>>> print g.edges(0, 1)
(((0, 1), ), ((0, 1), ))
>>> print g.external_edges
(((0,), ), ((1,), ))
