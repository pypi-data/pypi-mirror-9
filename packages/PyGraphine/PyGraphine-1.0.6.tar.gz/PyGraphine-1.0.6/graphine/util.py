#!/usr/bin/python
# -*- coding: utf8
import graph_state
import graph


def find_shortest_momentum_flow(graph, _from=None, to=None):
    external_edges = graph.edges(graph.external_vertex)
    start_vertex = external_edges[0].internal_nodes[0] if _from is None else _from.internal_node
    target_vertex = external_edges[1].internal_nodes[0] if to is None else to.internal_node
    queue = [start_vertex]
    distances = {start_vertex: ()}
    while len(queue):
        vertex = queue[0]
        del queue[0]
        dist = distances.get(vertex)
        for e in graph.edges(vertex):
            if e.is_external():
                continue
            v = e.nodes[1 if e.nodes[0] == vertex else 0]
            e_dist = distances.get(v)
            new_dist = 1 + len(dist)
            if e_dist is None or len(e_dist) > new_dist:
                if v == target_vertex and new_dist == 1:
                    return (e, e.nodes[0] == vertex),
                sign = e.nodes[0] == vertex
                distances[v] = dist + ((e, sign),)
                queue.append(v)
    return distances[target_vertex]


def has_intersecting_by_vertices_graphs(graphs):
    """
    return True if some of graphs hash non-trivial intersection on vertices
    """
    if not len(graphs):
        return False
    unique_vertices = set()
    for g in graphs:
        internal_vertices = g.vertices - set([g.external_vertex])
        old_len = len(unique_vertices)
        unique_vertices |= internal_vertices
        if len(unique_vertices) != old_len + len(internal_vertices):
            return True
    return False