#!/usr/bin/python
# -*- coding: utf8
__author__ = 'batya239@gmail.com'

import graph_state
import graphine


MAIN_GRAPH_CONFIG = graph_state.PropertiesConfig.create(graph_state.PropertyKey(name="fields",
                                                                                is_directed=True,
                                                                                externalizer=graph_state.Fields.externalizer()))

gs_builder = MAIN_GRAPH_CONFIG


gs_builder.Fields = graph_state.Fields

new_edge = MAIN_GRAPH_CONFIG.new_edge


def from_str(graph_state_str):
    return graphine.Graph.from_str(graph_state_str, MAIN_GRAPH_CONFIG)


def graph(edges):
    return graphine.Graph(edges)
