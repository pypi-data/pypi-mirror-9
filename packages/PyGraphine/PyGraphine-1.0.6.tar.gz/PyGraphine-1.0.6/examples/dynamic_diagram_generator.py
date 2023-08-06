#!/usr/bin/python
# -*- coding: utf8
#
# Generator of dynamical diagrams in statistical physics models. See example in "percolation_generator_example.py"
# To use call generate() function where
# graph_topology -- given topology in correspondent static model. 
# possible_fields -- possible fields of model where. Each of fields must be denoted as single letter.
# If field has correspondent delayed field
# then it should have different lettercases (lowercase or uppercase). 
# possible_external_fields -- fields which are located on the external egdes
# possible_vertices -- list of possible fields combinations in vertices


__author__ = 'batya239@gmail.com'


import graph_state_config_with_fields
import graph_state
import itertools
import graphine
import collections

emptyListDict = lambda: collections.defaultdict(list)
zeroDict = lambda: collections.defaultdict(lambda: 0)
emptySetDict = lambda: collections.defaultdict(set)


def generate(graph_topology, possible_fields, possible_external_fields, possible_vertices):
    if not isinstance(graph_topology, str):
        graph_topology = str(graph_topology)

    possible_external_fields = list(possible_external_fields)

    possible_vertices_rank = emptyListDict()
    for v in possible_vertices:
        possible_vertices_rank[len(v)].append(VertexIndex(tuple(v)))

    possible_fields_index = emptySetDict()
    for f in possible_fields:
        map(lambda i: possible_fields_index[f[i]].add(f[1 - i]), (0, 1))

    graph_stub = graph_state_config_with_fields.from_str(graph_topology)

    return do_bfs(graph_stub, possible_fields_index, possible_external_fields, possible_vertices_rank)


def do_bfs(graph_stub, possible_fields_index, possible_external_fields, possible_vertices_rank):
    edges = graph_stub.edges()
    all_vertices = graph_stub.vertices
    vertices = sorted(all_vertices)
    vertices.remove(graph_stub.external_vertex)
    vertices.reverse()

    result = set()
    q = [(edges, vertices, possible_external_fields, Poset())]
    while len(q):
        edges, vertices, possible_external_fields, poset = q.pop()
        for obj in assign_fields_in_vertex(edges, vertices, possible_fields_index, possible_external_fields, possible_vertices_rank, poset):
            if isinstance(obj, tuple):
                q.append(obj)
            elif isinstance(obj, graphine.Graph):
                result.add(obj)

    return result


def assign_fields_in_vertex(graph_edges, vertices, possible_fields_index, possible_external_fields, possible_vertices_rank, poset):
    vertex = vertices.pop()
    vertex_edges, other_edges = graph_state.operations_lib.split_edges_for_node(graph_edges, vertex)

    to_assign = list()
    not_assign = other_edges
    existed_fields = zeroDict()

    new_vertices = set()

    for e in vertex_edges:
        f = e.get_attr_regard_to(vertex, "fields")
        if f is not None and (f[0] != graph_state.Fields.EXTERNAL or e.is_external()):
            field = e.fields[0 if e.nodes[0] == vertex else 1]
            existed_fields[field] += 1
            not_assign.append(e)
        else:
            to_assign.append((e, f))
            c_node = e.co_node(vertex)
            if c_node != e.external_node and c_node not in vertices:
                new_vertices.add(c_node)

    for i in possible_vertices_rank[len(vertex_edges)]:
        supp = i.supplement(existed_fields)
        if supp is not None:
            flatten_supp = flatten_multi_set(supp)
            assert len(to_assign) == len(flatten_supp)
            for fields_perm in set(itertools.permutations(flatten_supp)):
                new_edges = list(not_assign)
                new_possible_external_fields = list(possible_external_fields)
                new_poset = poset.copy()
                suitable = True
                for f, (e, exist_fields) in itertools.izip(fields_perm, to_assign):
                    if exist_fields is None:
                        if e.is_external():
                            if f not in new_possible_external_fields:
                                suitable = False
                                break
                            new_possible_external_fields.remove(f)
                            is_lessier = f == f.isupper()
                            if not new_poset.can_be_border(is_lessier, vertex):
                                suitable = False
                                break
                            new_poset.update_border(is_lessier, vertex)
                        fields = graph_state.Fields((f, graph_state.Fields.EXTERNAL) if e.nodes[0] == vertex else (graph_state.Fields.EXTERNAL, f))
                    else:
                        # assert not e.is_external()
                        # assert not exist_fields[1] == graph_state.Fields.EXTERNAL
                        f_is_upper = f.islower()
                        is_order_producer = (f_is_upper and exist_fields[1].isupper()) or (not f_is_upper and exist_fields[1].islower())
                        if e.nodes[0] == vertex:
                            fields = graph_state.Fields((f, exist_fields[1]))
                        else:
                            fields = graph_state.Fields((exist_fields[1], f))
                        if fields[1] not in possible_fields_index[fields[0]]:
                            suitable = False
                            break
                        if is_order_producer:
                            params = (e.co_node(vertex), vertex) if f_is_upper else (vertex, e.co_node(vertex))
                            if new_poset.has_order(*params):
                                suitable = False
                                break
                            else:
                                new_poset.update(*(params[::-1]))
                    new_edges.append(e.copy(fields=fields))
                if suitable:
                    if len(vertices):
                        yield new_edges, list(vertices), new_possible_external_fields, new_poset
                    else:
                        yield graphine.Graph(new_edges)


class Poset(object):
    def __init__(self, lessers=None, greaters=None, lessiers=None, greatest=None):
        self._lessers = emptySetDict() if lessers is None else lessers
        self._greaters = emptySetDict() if greaters is None else greaters

        self._lessiers = set() if lessiers is None else lessiers
        self._greatest = set() if greatest is None else greatest

    def update(self, lesser, greater):
        if lesser in self._lessers[greater]:
            return
        self._lessers[greater].add(lesser)
        self._greaters[lesser].add(greater)
        for l in frozenset(self._lessers[lesser]):
            self.update(l, greater)
        for g in frozenset(self._greaters[greater]):
            self.update(lesser, g)

    def update_border(self, is_lessier, index):
        if is_lessier:
            self._lessiers.add(index)
            for i in self._greatest:
                self.update(index, i)
        else:
            self._greatest.add(index)
            for i in self._lessiers:
                self.update(i, index)

    def can_be_border(self, is_lessier, index):
        for i in self._greatest if is_lessier else self._lessiers:
            if is_lessier:
                if self.has_order(i, index):
                    return False
            else:
                if self.has_order(index, i):
                    return False
        return True

    def has_order(self, lesser, greater):
        if lesser in self._lessers[greater]:
            return True
        if lesser in self._lessiers and greater in self._greatest:
            return True
        return False

    def copy(self):
        copied_lessers = emptySetDict()
        for g, ls in self._lessers.iteritems():
            copied_lessers[g] = set(ls)

        copied_greaters = emptySetDict()
        for l, gs in self._greaters.iteritems():
            copied_greaters[l] = set(gs)
        return Poset(copied_lessers, copied_greaters, set(self._lessiers), set(self._greatest))


class VertexIndex(object):
    def __init__(self, index_str):
        self._undelying = zeroDict()
        for c in index_str:
            self._undelying[c] += 1

    def supplement(self, fields_dict):
        supp = dict()
        for f, c in fields_dict.items():
            existed_count = self._undelying.get(f, 0)
            if existed_count < c:
                return None
            elif existed_count != c:
                supp[f] = existed_count - c

        if len(fields_dict) == len(self._undelying):
            return supp
        for f, c in self._undelying.items():
            if f not in supp:
                supp[f] = c
        return supp

    def __str__(self):
        return "".join(sorted(flatten_multi_set(self._undelying)))

    __repr__ = __str__


def flatten_multi_set(multi_set):
    result = []
    for i, c in multi_set.iteritems():
        result += [i] * c
    return result
