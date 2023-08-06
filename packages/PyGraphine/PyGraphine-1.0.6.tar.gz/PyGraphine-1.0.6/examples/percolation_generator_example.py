#!/usr/bin/python
# -*- coding: utf8
#
# Generation of Feynman diagrams for percolation theory in statistical physics in order of 3-loops
# based on "static" diagrams of \phi^3 theory.
#
# run script:
#   $ python percolation_generator_example.py
# expected output of script is:
# 1 e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|Aa_aA|aA|0a|
# 2 e12|23|4|45|5|e|:0A_aA_aA|Aa_aA|aA|aA_aA|aA|0a|
# 3 e12|34|35|e|55||:0A_aA_aA|aA_Aa|aA_aA|0a|Aa_Aa||
# 4 e12|e3|44|55|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|aA||
# 5 e12|23|4|e5|55||:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA||
# 6 e12|23|4|e5|55||:0A_aA_aA|aA_aA|aA|0a_Aa|aA_aA||
# 7 e12|23|4|e5|55||:0a_Aa_Aa|Aa_Aa|Aa|0A_aA|Aa_Aa||
# 8 e12|23|4|e5|55||:0a_Aa_Aa|aA_Aa|Aa|0A_aA|Aa_Aa||
# 9 e12|e3|45|45|5||:0A_aA_aA|0a_Aa|aA_aA|Aa_Aa|Aa||
# 10 e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|Aa|aA|0a|
# 11 e12|34|35|4|5|e|:0A_aA_aA|aA_aA|Aa_aA|aA|aA|0a|
# 12 e12|34|35|4|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|
# 13 e12|34|35|4|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|
# 14 e12|34|34|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|
# 15 e12|34|34|5|5|e|:0A_aA_aA|Aa_aA|aA_aA|aA|aA|0a|
# 16 e12|e3|34|5|55||:0A_aA_aA|0a_Aa|aA_aA|Aa|aA_aA||
# 17 e12|33|44|5|5|e|:0A_aA_aA|aA_aA|aA_aA|aA|aA|0a|
# generated in XXX sec.

__author__ = 'batya239@gmail.com'

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
