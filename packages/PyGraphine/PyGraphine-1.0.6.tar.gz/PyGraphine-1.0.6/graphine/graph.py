#!/usr/bin/python
# -*- coding: utf8
import copy
import graph_state
import graph_operations
import itertools
import collections
from functools import wraps
assert graph_state.Edge.CREATE_EDGES_INDEX


class Representator(object):
    """
    see Graph#xRelevantSubGraphs
    """

    def __init__(self):
        raise AssertionError

    @staticmethod
    def asList(edge_list):
        return edge_list

    @staticmethod
    def asGraph(edge_list):
        return Graph(edge_list, renumbering=False)

    @staticmethod
    def asMinimalGraph(edge_list):
        return Graph(edge_list, renumbering=True)


KeyAndParams = collections.namedtuple("KeyAndParams", ["key", "params", "kwargs"])


def cached_method(some_class_method):
    @wraps(some_class_method)
    def wrapper(self, *params, **kwargs):
        hidden_key = "_" + some_class_method.__name__
        kwargs_k = frozenset(map(lambda t: t, kwargs.items())) if len(kwargs) else None
        key_and_params = KeyAndParams(hidden_key, params, kwargs_k)
        if key_and_params not in self._internal_cache:
            self._internal_cache[key_and_params] = some_class_method(self, *params, **kwargs)
        return self._internal_cache[key_and_params]

    return wrapper


class Graph(object):
    """
    :class:`Graph` object can be created from both list of edges and :class:`GraphState` object as a first parameter. Additionally one
    can use :meth:`Graph.from_str` for creation from :class:`GraphState` serialized string and given :class:`PropertiesConfig`.

    In case of list of edges passed in constructor this list will be processed to list of edges that are relevant to minimal Nickel notation.
    If you don't need that then specify :attr:`renumbering` parameter as ``False``.
    """
    def __init__(self, obj, renumbering=True):
        """
        obj - both of edges list or GraphState object
        renumbering - reordering edges using GraphState
        """
        self._internal_cache = dict()
        if isinstance(obj, (list, tuple)):
            assert len(obj)
            self._underlying = graph_state.GraphState(obj) if renumbering else obj
        elif isinstance(obj, graph_state.GraphState):
            self._underlying = obj
        else:
            raise AssertionError("unsupported obj type - %s" % type(obj))
        self._next_vertex_index = max(reduce(lambda t, e: t + tuple(n.index for n in e.nodes), self.edges(), tuple())) + 1
        self._external_vertex = graph_state.operations_lib.get_external_node(self._underlying)


    @staticmethod
    def from_str(string, properties_config=None):
        """
        :param string: GraphState serialized string
        :type string: str.
        :param properties_config: valid properties configuration do deserialize string
        :type properties_config: :class:`PropertiesConfig`
        :return: constructed :class:`Graph` object
        """
        return Graph(graph_state.GraphState.from_str(string, properties_config=properties_config))

    @property
    @cached_method
    def external_vertex(self):
        """
        Returns external vertex of graph.
        """
        return graph_state.operations_lib.get_external_node(self._underlying)

    @property
    @cached_method
    def external_edges(self):
        """
        Returns external edges of graph. See :attr:`external_edges_count`, :attr:`internal_edges`.
        """
        return graph_state.operations_lib.edges_for_node(self._underlying, self.external_vertex)

    @property
    def external_edges_count(self):
        """
        Returns count of external edges. See :attr:`external_edges`, :attr:`external_edges`.
        """
        return len(self.external_edges)

    @property
    @cached_method
    def internal_edges(self):
        """
        Returns internal edges of graph. See :meth:`external_edges`, :meth:`internal_edges_count`.
        """
        return tuple(filter(lambda e: not e.is_external(), self))

    @property
    @cached_method
    def vertices(self):
        """
        Returns vertices of graph (includes external vertex). See :meth:`get_bound_vertices`.
        """
        return graph_state.operations_lib.get_vertices(self._underlying)

    @property
    @cached_method
    def edges_indices(self):
        """
        Returns indices of edges. See :class:`Edge`, :attr:`Edge.edge_id`.
        """
        return frozenset(map(lambda e: e.edge_id, self))

    @property
    @cached_method
    def internal_edges_count(self):
        """
        Returns internal edges of graph. See :meth:`internal_edges`.
        """
        return len(self.internal_edges)

    @property
    @cached_method
    def loops_count(self):
        """
        Returns count of loops in diagram (graph).
        """
        return self.internal_edges_count - len(self.vertices) + (1 if len(self.edges(self.external_vertex)) != 0 else 0) + 1

    @property
    def presentable_str(self):
        return self.to_graph_state().topology_str()

    @cached_method
    def edges(self, vertex=None, vertex2=None, nickel_ordering=False):
        """
        Returns edges of graph for corresponding :attr:`vertex` and :attr:`vertex2` if specified.

        >>> Graph.from_str("e11|e|", config).edges(0)
        [(0, -1), (0, 1), (0, 1)]


        >>> Graph.from_str("e11|e|", config).edges(0, 1)
        [(0, 1), (0, 1)]
        """
        if vertex is None:
            if nickel_ordering or isinstance(self._underlying, graph_state.GraphState):
                return tuple(self.to_graph_state().edges)
            else:
                return tuple(self._underlying)
        else:
            es = graph_state.operations_lib.edges_for_node(self._underlying, vertex)
            if vertex2 is not None:
                es = graph_state.operations_lib.edges_for_node(es, vertex2)
            return es

    @cached_method
    def to_graph_state(self):
        """
        Returns :class:`GraphState` of given graph.
        """
        try:
            return self._underlying \
                if isinstance(self._underlying, graph_state.GraphState) \
                else graph_state.GraphState(self._underlying)
        except StandardError as e:
            raise ValueError("Can't create GraphState: %s" % e.message)

    @cached_method
    def get_bound_vertices(self):
        """
        Returns vertices of graph that are bound to external vertex.
        """
        return graph_state.operations_lib.get_bound_vertices(self._underlying)

    def create_vertex_index(self):
        """
        Creates and returns index of vertex that are not occurred among vertex indices of given graph.
        """
        to_return = self._next_vertex_index
        self._next_vertex_index += 1
        return to_return

    def change(self, edges_to_remove=None, edges_to_add=None, renumbering=True):
        """
        Returns graph with deleted edges :attr:`edges_to_remove` and added :attr:`edges_to_add`.
        """
        new_edges = self.edges()
        new_edges = Graph._sub_tuple(new_edges, edges_to_remove)
        new_edges += tuple(edges_to_add)
        return Graph(new_edges, renumbering=renumbering)

    def delete_vertex(self, vertex, transform_edges_to_external=False):
        """
        Deletes vertex from graph and makes all of edges containing specified vertex external.
        """
        assert vertex != self.external_vertex
        if transform_edges_to_external:
            edges = self.edges(vertex)
            for e in edges:
                if self.external_vertex in e.nodes:
                    raise AssertionError()
            node_map = {vertex: self.external_vertex}
            n_edges = map(lambda e: e.copy(node_map), edges)
            return self.change(edges, n_edges)
        else:
            return self - self.edges(vertex)

    def contains(self, other_graph):
        """
        Returns if graph has given graph as subset of edges.
        """
        self_edges = list(self.edges())
        for e in other_graph:
            if e in self_edges:
                self_edges.remove(e)
            else:
                return False
        return True

    def batch_shrink_to_point(self, sub_graphs, with_aux_info=False):
        """
        Method shrinks given collection of :attr:`sub_graphs` (can be edges or graphs) to point and returns shrunk graph.
        If :attr:`with_aux_info` specified as ``True`` then method returns pair where the first element is shrunk graph but
        the second are indices of vertices created while shrink operation.
        """
        if not len(sub_graphs):
            return (self, list()) if with_aux_info else self

        vertex_transformation = ID_VERTEX_TRANSFORMATION
        g = self
        new_vertices = list()
        for sub_graph in sub_graphs:
            all_edges = sub_graph.edges() if isinstance(sub_graph, Graph) else sub_graph
            g, new_vertex, vertex_transformation = g._shrink_to_point(all_edges, vertex_transformation)
            new_vertices.append(new_vertex)
        assert g
        return (g, new_vertices) if with_aux_info else g

    def shrink_to_point(self, edges, with_aux_info=False):
        """
        Method shrinks given :attr:`edges` to point and returns shrunk graph. If :attr:`with_aux_info`
        specified as ``True`` then method returns pair where the first element is shrunk graph but the second are indices of vertices
        created while shrink operation.
        """
        result = self._shrink_to_point(edges)
        return result[0:2] if with_aux_info else result[0]

    def _shrink_to_point(self, un_transformed_edges, vertex_transformation=None):
        """
        immutable operation
        """
        if not vertex_transformation:
            vertex_transformation = ID_VERTEX_TRANSFORMATION

        edges = map(lambda e: e.copy(vertex_transformation.mapping), un_transformed_edges)

        new_raw_edges = list(self.edges())
        marked_vertexes = set()
        for edge in edges:
            v1, v2 = edge.nodes
            if v1 != self.external_vertex and v2 != self.external_vertex:
                new_raw_edges.remove(edge)
                marked_vertexes.add(v1)
                marked_vertexes.add(v2)
        new_edges = list()
        curr_vertex_transformation_map = dict()
        for edge in new_raw_edges:
            copy_map = {}
            for v in edge.nodes:
                if v in marked_vertexes:
                    curr_vertex_transformation_map[v] = self._next_vertex_index
                    copy_map[v] = self._next_vertex_index
            if len(copy_map):
                new_edges.append(edge.copy(copy_map))
            else:
                new_edges.append(edge)
        return Graph(new_edges, renumbering=False), \
               self._next_vertex_index, \
               vertex_transformation.add(VertexTransformation(curr_vertex_transformation_map))

    def remove_tadpoles(self):
        return Graph(filter(lambda e: e.nodes[0] != e.nodes[1], self.edges()))

    def to_tadpole(self):
        """
        Creates graph copy and removes all external edges from its.
        """
        return Graph(self.internal_edges)

    def x_relevant_sub_graphs(self,
                              filters=list(),
                              result_representator=None,
                              cut_edges_to_external=True,
                              exact=True):

        """
        :param filters: condition to decide if subgraph is relevant. :attr:`filters` is list of filter. See :mod:`graphine.filters` overview.
        :param result_representator: defines representation of returned result. Can be one of: :attr:`graphine.Representator.asGraph`
        (without vertices renumbering and Nickel canonicalization),
        :attr:`graphine.Representator.asMinimalGraph` (graph that has minimal Nickel notation), :attr:`graphine.Representator.asList` (edges list)

        :param cut_edges_to_external: representate edges of vertex included in subgraph that are not included in subgraph as external edges for subgraph
        :param exact: yield self graph as relevant subgraph
        :return: iterator of  relevant subgraph for given condition (filters)
        """
        if result_representator is None:
            result_representator=Representator.asGraph
        
        simple_cache = dict()
        exact_sub_graph_iterator = graph_operations.x_sub_graphs(self, cut_edges_to_external=cut_edges_to_external)
        sg_iterator = exact_sub_graph_iterator if exact else itertools.chain(exact_sub_graph_iterator, (self.edges(),))
        for sub_graph_as_list in sg_iterator:
            sub_graph_as_tuple = tuple(sub_graph_as_list)
            is_valid = simple_cache.get(sub_graph_as_tuple, None)
            if is_valid is None:
                is_valid = True
                for a_filter in filters:
                    if not a_filter(sub_graph_as_list, self):
                        is_valid = False
                        break
            if is_valid:
                yield result_representator(sub_graph_as_list)

    def __add__(self, other):
        if isinstance(other, graph_state.Edge):
            return Graph(self.edges() + (other,), renumbering=False)
        elif isinstance(other, (list, tuple)):
            if not len(other):
                return self
            return Graph(self.edges() + tuple(other), renumbering=False)
        raise AssertionError("unsupported type: %s" % type(other))

    def __sub__(self, other):
        if isinstance(other, graph_state.Edge):
            return Graph(Graph._sub_tuple(self.edges(), (other,)), renumbering=False)
        elif isinstance(other, (list, tuple)):
            if not len(other):
                return self
            return Graph(Graph._sub_tuple(self.edges(), other), renumbering=False)
        elif isinstance(other, Graph):
            return Graph(Graph._sub_tuple(self.edges(), other.edges()), renumbering=False)
        raise AssertionError("unsupported type: %s" % type(other))

    def __div__(self, other):
        assert isinstance(other, Graph)
        return self.shrink_to_point(other)

    @staticmethod
    def _sub_tuple(tuple_a, tuple_b):
        copied_a = list(tuple_a)
        for x in tuple_b:
            copied_a.remove(x)
        return copied_a

    def __len__(self):
        return len(self._underlying)

    def __iter__(self):
        return iter(self._underlying)

    def __contains__(self, item):
        assert isinstance(item, graph_state.Edge)
        return item in self.edges()

    def __str__(self):
        return str(self.to_graph_state())

    __repr__ = __str__

    @cached_method
    def __hash__(self):
        return hash(self.to_graph_state()) + 37 * hash(self.vertices)

    def __eq__(self, other):
        assert isinstance(other, Graph)
        return self.to_graph_state() == other.to_graph_state() and self.vertices == other.vertices


class VertexTransformation(object):
    def __init__(self, mapping=None):
        """
        self._mapping - only non-identical index mappings
        """
        self._mapping = mapping if mapping else dict()

    @property
    def mapping(self):
        return self._mapping

    def add(self, another_vertex_transformation):
        """
        composition of 2 transformations
        """
        composed_mapping = dict()
        usedKeys = set()
        for k, v in self._mapping.items():
            av = another_vertex_transformation.mapping.get(v, None)
            if av:
                composed_mapping[k] = another_vertex_transformation.mapping[v]
                usedKeys.add(v)
            else:
                composed_mapping[k] = v
        for k, v in another_vertex_transformation.mapping.items():
            if k not in usedKeys:
                composed_mapping[k] = v
        return VertexTransformation(composed_mapping)

    def map(self, vertex_index):
        index_mapping = self._mapping.get(vertex_index, None)
        if index_mapping:
            return index_mapping
        return vertex_index


ID_VERTEX_TRANSFORMATION = VertexTransformation()