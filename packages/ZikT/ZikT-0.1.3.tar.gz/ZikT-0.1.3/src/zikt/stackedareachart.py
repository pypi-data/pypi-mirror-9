# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

from zikt.cschart import MultipleValueCoordinateChart
from zikt.helper import Attributes
from zikt.painter import AreaPainter
from zikt.tables_tests import getBasicTable
from zikt.tables import FloatTable

class StackedAreaChart(MultipleValueCoordinateChart):
	base = Attributes(
		parent=MultipleValueCoordinateChart.base,
		painter=[AreaPainter],
		#
		upperLabelString=u"{value}",
		upperLabelStyle=u"",
		additionalUpperLabelStyle=u"",
		lowerLabelString=u"",
		lowerLabelStyle=u"",
		additionalLowerLabelStyle=u"",
		centerLabelString=u"",
		centerLabelStyle=u"",
		additionalCenterLabelStyle=u"",
		#
		stackmode = 'onTopOfZero',
		#
		areaStyle = u"ziktStackedAreaStyle",
		additionalAreaStyle = u"color={outlineColor},fill={fillColor}",
	)
	presettings =  {
		'base': base,
	}
	
	def __init__(self,preset="base", printComments=True, **kwargs):
		MultipleValueCoordinateChart.__init__(self)
		self.attributes = StackedAreaChart.presettings[preset].copy()
		self.attributes.extend(**kwargs)
		self.printComments = printComments
		self.attributeDict = self.attributes.getDict()
		

if __name__ == "__main__":
	c =  StackedAreaChart(ordinateLength=6)
	print c.render(table = FloatTable(getBasicTable()))