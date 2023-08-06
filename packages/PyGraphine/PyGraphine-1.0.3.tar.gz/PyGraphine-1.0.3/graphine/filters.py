#!/usr/bin/python
# -*- coding: utf8
"""
Module provides tools to create relevance filters for graphs that can be used for searching of relevant subgraphs:

>>> graph.x_relevant_sub_graphs(filters=my_filters)

Any filter must be a function with 2 parameters. First is subgraph edges list, second is super graph. Function is responsible
to decide if graph is relevant and returns boolean decision value (``True`` if subgraph is relevant). Filter function must have
:attr:`graphine.filters.graph_filter` decorator. To create composite filter ``+`` operator can be used:

>>> composite_filters = connected + vertex_irreducible

Additionally package contains set of predefined filters: for subgraph connectivity, 1-irreducibility etc.:

1. :attr:`graph_state.filters.connected`
2. :attr:`graph_state.filters.one_irreducible`
3. :attr:`graph_state.filters.vertex_irreducible`
4. :attr:`graph_state.filters.no_tadpoles` (no tadpoles in co-subgraph)
"""
import graph_state


def graph_filter(qualifier):
    """
    Marker decorator for filters.
    """
    return [qualifier]


def is_relevant(relevance_condition):
    def wrapper(edges_list, super_graph):
        return relevance_condition.is_relevant(edges_list, super_graph)

    return [wrapper]


def has_n_borders(n):
    """
    Filter graphs only with :attr:`n` count of borders (border vertices)
    """
    @graph_filter
    def _has_n_borders(edges_list, super_graph):
        borders = set()
        for e in edges_list:
            if e.is_external():
                borders.add(e.internal_node)
        return len(borders) == n
    return _has_n_borders


def _graph_state_wrapper1(fun):
    def wrapper(edges_list, super_graph):
        return fun(edges_list)
    return wrapper


def _graph_state_wrapper2(fun):
    def wrapper(edges_list, super_graph):
        return fun(edges_list, super_graph.edges())
    return wrapper

one_irreducible = graph_filter(_graph_state_wrapper1(graph_state.operations_lib.is_1_irreducible))
connected = graph_filter(_graph_state_wrapper1(graph_state.operations_lib.is_graph_connected))
no_tadpoles = graph_filter(_graph_state_wrapper2(graph_state.operations_lib.has_no_tadpoles_in_counter_term))
vertex_irreducible = graph_filter(_graph_state_wrapper1(graph_state.operations_lib.is_vertex_irreducible))
