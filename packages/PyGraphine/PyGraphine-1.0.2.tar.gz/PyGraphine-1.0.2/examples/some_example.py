#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import dynamic_diagram_generator
import time

gs = list()

gs.append("e12-33-45-6-e7-67-7--")
gs.append("e12-23-4-e5-66-77-7--")
gs.append("e12-33-45-4-6-e7-77--")
gs.append("e12-34-35-e-56-7-77--")
gs.append("e12-34-56-e5-77-6-7--")
gs.append("e12-33-45-6-67-67--e-")
gs.append("e12-33-45-6-57-7-e7--")
gs.append("e12-e3-45-67-56-7-7--")
gs.append("e12-34-35-6-67-67--e-")
gs.append("e12-33-44-5-6-e7-77--")
gs.append("e12-34-56-56-57--7-e-")
gs.append("e12-33-45-6-56-7-7-e-")
gs.append("e12-23-4-55-66-7-7-e-")
gs.append("e12-34-35-6-e5-7-77--")
gs.append("e12-34-35-6-56-7-7-e-")
gs.append("e12-e3-44-56-5-7-77--")
gs.append("e12-23-4-e5-67-67-7--")
gs.append("e12-34-35-6-e7-67-7--")
gs.append("e12-23-4-e5-56-7-77--")
gs.append("e12-e3-45-67-67-67---")
gs.append("e12-23-4-56-57-e-77--")
gs.append("e12-e3-45-45-6-7-77--")
gs.append("e12-e3-34-5-67-67-7--")
gs.append("e12-e3-45-46-5-7-77--")
gs.append("e12-23-4-56-57-6-7-e-")
gs.append("e12-34-35-e-67-67-7--")
gs.append("e12-34-35-6-57-7-e7--")
gs.append("e12-33-45-6-67-77-e--")
gs.append("e12-e3-45-67-66-77---")
gs.append("e12-23-4-56-56-7-7-e-")
gs.append("e12-33-45-6-e6-77-7--")
gs.append("e12-e3-34-5-56-7-77--")
gs.append("e12-e3-44-56-7-67-7--")
gs.append("e12-34-56-e5-67-7-7--")
gs.append("e12-34-35-6-e6-77-7--")
gs.append("e12-23-4-55-67-6-7-e-")
gs.append("e12-33-45-4-6-77-e7--")
gs.append("e12-34-35-e-66-77-7--")
gs.append("e12-e3-45-46-7-67-7--")
gs.append("e12-23-4-45-6-67-7-e-")
gs.append("e12-23-4-45-6-e7-77--")
gs.append("e12-e3-44-55-6-7-77--")
gs.append("e12-e3-34-5-66-77-7--")
gs.append("e12-34-56-e7-56-7-7--")
gs.append("e12-34-56-45-7-6-7-e-")
gs.append("e12-34-35-6-67-77-e--")

misha = set()
with open("turb4loop.log", "r") as f:
    for l in f:
        if ":" in l:
            misha.add(l[:-1].split(" ")[0])

gs = map(lambda g: g.replace("-", "|"), gs)
my = set()
i = 1
t = time.time()
for g in gs:
    for _g in dynamic_diagram_generator.generate(g, possible_fields=["aA", "aa"], possible_external_fields="Aa", possible_vertices=["aaA"]):
        print i, _g
        my.add(str(_g))
        i += 1

print len(my)
print len(misha)
print len(my - misha)

print "time = ", (time.time() - t), "sec"