# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

import unittest
from zikt.tables_tests import getBasicTable
from zikt.tables import FloatTable
from zikt.stackedbarchart import StackedBarChart
from zikt.cs import TikZCoordinateSystem

class TableTests(unittest.TestCase):
    
    def test_noFailureOnAbscissaLengthSpecified(self):
        table = FloatTable(getBasicTable())
        chart = StackedBarChart(
#                alongsideOrdinateLabelString = 'work left',
#                outerOrdinateLabelString = 'SP',
#                lowestLabelString = '{colHeader}',
                abscissaLength = 10,
#                additionalLowestLabelStyle = 'font=\\scriptsize, rotate=90, anchor=east'
        )
        _ = chart.render(table)