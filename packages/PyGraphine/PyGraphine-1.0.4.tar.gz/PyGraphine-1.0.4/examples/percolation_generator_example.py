#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import dynamic_diagram_generator
import time

three_loops = list()

three_loops.append("e12|23|4|45|5|e|")
three_loops.append("e12|34|35|e|55||")
three_loops.append("e12|e3|44|55|5||")
three_loops.append("e12|23|4|e5|55||")
three_loops.append("e12|e3|45|45|5||")
three_loops.append("e12|34|35|4|5|e|")
three_loops.append("e12|34|34|5|5|e|")
three_loops.append("e12|e3|34|5|55||")
three_loops.append("e12|33|44|5|5|e|")

i = 1
t = time.time()
for gs in three_loops:
    for _g in dynamic_diagram_generator.generate(gs, possible_fields=["aA"], possible_external_fields="Aa", possible_vertices=["aaA", "aAA"]):
        print i, _g
        i += 1
print "generated in " + str(time.time() - t) + " sec."