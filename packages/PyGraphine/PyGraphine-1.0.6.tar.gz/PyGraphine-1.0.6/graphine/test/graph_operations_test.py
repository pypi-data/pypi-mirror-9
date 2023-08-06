#!/usr/bin/python
# -*- coding: utf8
#
# Test of relevant subgraphs searching and subgraph filters from graphine.filters:
# testing of graph connectivity, irreducibility...,
#

import unittest

from graph_state import graph_state as gs
from graphine import graph as gr
from graphine import graph_operations as go
from graphine import filters


class GraphOperationsTestCase(unittest.TestCase):
    def testRelevantSubGraphsTails(self):
        g = gr.Graph.from_str("e12|e23|3||")
        gExternalIds = set(map(lambda e: e.edge_id, g.external_edges))
        subGraphs = [x for x in g.x_relevant_sub_graphs(filters=filters.connected + filters.one_irreducible,
                                                        result_representator=gr.Representator.asGraph,
                                                        cut_edges_to_external=False)]
        sgExternalIds = set()
        for g in subGraphs:
            for e in g.external_edges:
                sgExternalIds.add(e.edge_id)
        self.assertTrue(gExternalIds.issuperset(sgExternalIds))

    def testRelevantSubGraphs(self):
        g = gr.Graph.from_str("e12|e23|3||")
        subGraphs = [str(x) for x in g.x_relevant_sub_graphs(filters=filters.connected + filters.one_irreducible,
                                                             result_representator=gr.Representator.asGraph,
                                                             cut_edges_to_external=False)]
        self.assertEqual(set(subGraphs), set(['e12|e2||', 'e12|2||', 'e12|e3|3||']))

    def testRelevantSubGraphsWithIndexRepresentator(self):
        g = gr.Graph.from_str("e12|e23|3||")
        subGraphs = [x for x in g.x_relevant_sub_graphs(filters=filters.connected + filters.one_irreducible,
                                                        result_representator=gr.Representator.asList,
                                                        cut_edges_to_external=False)]
        sgIndexes = set()
        for sg in subGraphs:
            for e in sg:
                sgIndexes.add(e.edge_id)
        gIndexes = set(map(lambda e: e.edge_id, g.edges()))
        self.assertEqual(sgIndexes, gIndexes)

    def testHasNoTadPoles(self):
        self.doTestHasNoTadPoles("ee18|233|334||ee5|667|78|88||", [(1, 2), (1, 3), (2, 3), (2, 3)],
                                 expectedResult=False)
        self.doTestHasNoTadPoles("ee18|233|334||ee5|667|78|88||", [(1, 2), (1, 3), (2, 3)],
                                 expectedResult=False)
        self.doTestHasNoTadPoles("e111|e|", [(-1, 0), (-1, 0), (-1, 1), (-1, 1), (0, 1), (0, 1)],
                                 expectedResult=False)

    def test1Irreducibility(self):
        self.doTest1Irreducibility("ee12|e22|e|", expectedResult=True)
        self.doTest1Irreducibility("ee0|", expectedResult=True)
        self.doTest1Irreducibility("ee|", expectedResult=True)
        self.doTest1Irreducibility("ee11|ee|", expectedResult=True)
        self.doTest1Irreducibility("eee1|eee|", expectedResult=False)
        self.doTest1Irreducibility("ee12|eee|eee|", expectedResult=False)
        self.doTest1Irreducibility("ee12|ee2|ee|", expectedResult=True)

    def testConnected(self):
        self.doTestConnected("ee0|", expectedResult=True)
        self.doTestConnected("ee|", expectedResult=True)
        self.doTestConnected("ee11|ee|", expectedResult=True)
        self.doTestConnected("eee1|eee|", expectedResult=True)
        self.doTestConnected("ee12|eee|eee|", expectedResult=True)
        self.doTestConnected("ee12|ee1|ee|", expectedResult=True)

    def testVertexIrreducibility(self):
        self.doTestVertexIrreducibility("e11|e22||", expectedResult=False)
        self.doTestVertexIrreducibility("ee11|22|ee|", expectedResult=False)
        self.doTestVertexIrreducibility("ee12|ee2|ee|", expectedResult=True)
        self.doTestVertexIrreducibility("011|22|2|", expectedResult=False)
        self.doTestVertexIrreducibility("012|12|2|", expectedResult=False)
        self.doTestVertexIrreducibility("012|222||", expectedResult=False)
        self.doTestVertexIrreducibility("1122|22||", expectedResult=True)
        self.doTestVertexIrreducibility("1|2|3|4||", expectedResult=False)

    def doTestHasNoTadPoles(self, nickel, subGraph, expectedResult):
        subGraph = gr.Graph([gs.Edge(e) for e in subGraph], renumbering=False)
        graph = gr.Graph(gs.GraphState.from_str(nickel))
        self.assertEquals(go.has_tadpoles_in_counter_term(subGraph, graph), expectedResult)

    def doTest1Irreducibility(self, nickel, expectedResult):
        graph = gr.Graph(gs.GraphState.from_str(nickel))
        self.assertEquals(go.is_1_irreducible(graph), expectedResult)

    def doTestConnected(self, nickel, expectedResult):
        graph = gr.Graph(gs.GraphState.from_str(nickel))
        self.assertEquals(go.is_connected(graph), expectedResult)

    def doTestVertexIrreducibility(self, nickel, expectedResult):
        graph = gr.Graph(gs.GraphState.from_str(nickel))
        self.assertEquals(go.is_vertex_irreducible(graph), expectedResult)


if __name__ == "__main__":
    unittest.main()
