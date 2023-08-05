#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import dynamic_diagram_generator
import time

gs = list()

gs.append("e11|e|")
gs.append("e12|23|3|e|")
gs.append("e12|e3|33||")


i = 1
t = time.time()
for g in gs:
    print "-----"
    for _g in dynamic_diagram_generator.generate(g, possible_fields=["aA", "aa", "ad", "dd", "dA"], possible_external_fields="Aa", possible_vertices=["adA"]):
        print i, _g
        i += 1

print "time = ", (time.time() - t), "sec"