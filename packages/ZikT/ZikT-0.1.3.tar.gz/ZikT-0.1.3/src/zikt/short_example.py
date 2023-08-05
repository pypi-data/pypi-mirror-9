# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

from zikt.tables import FloatTable
from zikt.barchart import BarChart

data = [
	['A','B','C'],
	[2,12,-3]
	]

table = FloatTable(data)

chart = BarChart()

chartCode = chart.render(table)

print "\\begin{tikzpicture}"
print chartCode
print "\\end{tikzpicture}"