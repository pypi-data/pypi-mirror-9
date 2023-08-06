#!/usr/bin/python
# -*- coding: utf8
#
# Test graphine.Graph class for base operations like evaluation of internal or external vertices
# calculation of loops count, shrinking to point etc.
#

__author__ = 'dima'


import unittest
import graph_state
from graphine import Graph, Representator


class GraphTest(unittest.TestCase):
    EYE_EDGES = [(-1, 3), (-1, 0), (-1, 0), (0, 4), (0, 3), (3, 4), (3, 4), (-1, 4)]
    EYE = Graph([graph_state.Edge(e) for e in EYE_EDGES], renumbering=False)
    EYE_MIN = Graph([graph_state.Edge(e) for e in EYE_EDGES])

    def test_creation(self):
        pass

    def test_external_vertex(self):
        g = Graph.from_str("e11|e|")
        self.assertEqual(g.external_vertex, -1)

    def test_external_edges(self):
        g = Graph.from_str("ee11|ee|")
        external_edges = g.external_edges
        self.assertEqual(len(external_edges), 4)
        self.assertEqual(external_edges[0], external_edges[1])
        self.assertEqual(external_edges[2], external_edges[3])
        self.assertEqual(external_edges[0].internal_node, 0)
        self.assertEqual(external_edges[2].internal_node, 1)
        self.assertEqual(g.external_edges_count, 4)

    def test_internal_edges(self):
        g = Graph.from_str("ee11|ee|")
        internal_edges = g.internal_edges
        self.assertEqual(len(internal_edges), 2)
        self.assertEqual(internal_edges[0], internal_edges[1])

    def test_vertices(self):
        g = Graph.from_str("ee11|ee|")
        self.assertEqual(g.vertices, set([-1, 0, 1]))

        g = Graph([graph_state.Edge(e) for e in [(-1, 0), (0, 2), (2, -1)]], renumbering=False)
        self.assertEqual(g.vertices, set([-1, 0, 2]))

    def test_edges_indices(self):
        g = Graph.from_str("ee11|ee|")
        self.assertEqual(len(set(g.edges_indices)), 6)

    def test_internal_edges_count(self):
        g = Graph.from_str("ee11|ee|")
        self.assertEqual(g.internal_edges_count, 2)

    def test_loops_count(self):
        g = Graph.from_str("ee11|ee|")
        self.assertEqual(g.loops_count, 1)
        g = Graph.from_str("11|")
        self.assertEqual(g.loops_count, 1)

        g = Graph.from_str("12|22|")
        self.assertEqual(g.loops_count, 2)
        g = Graph.from_str("ee12|e22|e|")
        self.assertEqual(g.loops_count, 2)

        g = Graph.from_str("e12|23|3|e|")
        self.assertEqual(g.loops_count, 2)
        g = Graph.from_str("12|23|3||")
        self.assertEqual(g.loops_count, 2)

    def test_edges(self):
        self.assertEqual(len(GraphTest.EYE.edges(3, 4)), 2)
        self.assertEqual(len(GraphTest.EYE.edges(1, 2)), 0)

        self.assertEqual(set([e.nodes for e in GraphTest.EYE.edges(nickel_ordering=False)]), set(GraphTest.EYE_EDGES))
        self.assertEqual(len(GraphTest.EYE.edges(nickel_ordering=False)), len(GraphTest.EYE_EDGES))

    def test_to_graph_state(self):
        self.assertEqual(str(GraphTest.EYE.to_graph_state()), "ee12|e22|e|")

    def test_get_bound_vertices(self):
        self.assertEqual(GraphTest.EYE.get_bound_vertices(), set([0, 3, 4]))

    def test_create_vertex_index(self):
        self.assertEqual(GraphTest.EYE.create_vertex_index(), 5)

    def test_delete_vertex(self):
        g = Graph.from_str("e12|e2||")
        g1 = g.delete_vertex(2, transform_edges_to_external=False)
        self.assertEqual(str(g1), "e1|e|")
        g2 = g.delete_vertex(2, transform_edges_to_external=True)
        self.assertEqual(str(g2), "ee1|ee|")

    def test_contains(self):
        g_sub = Graph.from_str("12|2||")
        self.assertTrue(GraphTest.EYE_MIN.contains(g_sub))
        g_sub = Graph.from_str("12|222||")
        self.assertFalse(GraphTest.EYE_MIN.contains(g_sub))

    def test_shrink_to_point(self):
        g = Graph.from_str("ee12|223|3|ee|")
        g_sub = Graph([graph_state.Edge(e) for e in [(2, 1), (1, 2)]], renumbering=False)
        shrunk = g.shrink_to_point(g_sub)
        self.assertEqual(str(shrunk), "ee11|22|ee|")

        shrunk, new_vertex = g.shrink_to_point(g_sub, with_aux_info=True)
        self.assertEqual(str(shrunk), "ee11|22|ee|")
        self.assertEqual(len(shrunk.edges(4)), 4)

    def test_batch_shrink_to_point(self):
        g = Graph.from_str("ee12|2223|3|ee|")
        g_sub1 = Graph([graph_state.Edge(e) for e in [(2, 1), (1, 2)]], renumbering=False)
        g_sub2 = Graph([graph_state.Edge(e) for e in [(2, 1), (3, 2), (3, 2)]], renumbering=False)
        self.assertEqual(str(g.batch_shrink_to_point([g_sub1, g_sub2])), "ee11|ee|")


if __name__ == "__main__":
    unittest.main()
