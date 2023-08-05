# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''


from zikt.cschart import MultipleValueCoordinateChart
from zikt.helper import Attributes
from zikt.painter import BarPainter
from zikt.tables_tests import getBasicTable
from zikt.tables import FloatTable

class StackedBarChart(MultipleValueCoordinateChart):
	base = Attributes(
		#TODO: high: schaue of diese parents bei den Attributen nicht weg können
		parent=MultipleValueCoordinateChart.base,
		painter=[BarPainter],
		startMargin=0.5,
		endMargin=0.5,
		#
		upperLabelString=u"{value}",
		upperLabelStyle=u"",
		lowerLabelString=u"",
		lowerLabelStyle=u"",
		centerLabelString=u"",
		centerLabelStyle=u"",
		#
		stackmode = 'onTopOfZero',
		#
		barStyle = u"ziktStackedBarStyle",
		additionalBarStyle = u"color={outlineColor},fill={fillColor}",
		barWidthRatio = 0.6,
		#
		abscissaTickStyle=None,
		abscissaJutStyle=None,
		abscissaTickLabelString=u"",
	)
	presettings =  {
		'base': base,
	}
	
	def __init__(self,preset="base", printComments=True, **kwargs):
		MultipleValueCoordinateChart.__init__(self)
		self.attributes = StackedBarChart.presettings[preset].copy()
		self.attributes.extend(**kwargs)
		self.printComments = printComments
		self.attributeDict = self.attributes.getDict()
		

if __name__ == "__main__":
	c =  StackedBarChart(ordinateLength=6,stackmode = "onTopOfZero")
	print c.render(table = FloatTable(getBasicTable()))