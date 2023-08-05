# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

from zikt.cschart import MultipleValueCoordinateChart
from zikt.helper import Attributes
from zikt.painter import PlotPainter
from zikt.tables_tests import getBasicTable
from zikt.tables import FloatTable

class PlotChart(MultipleValueCoordinateChart):
	base = Attributes(
		parent=MultipleValueCoordinateChart.base,
		painter=[PlotPainter],
		#
		valuePointLabelAboveString=u"{value}",
		valuePointLabelAboveStyle=u"",
		valuePointLabelBelowString=u"",
		valuePointLabelBelowStyle=u"",
		#
		plotMarks = ["square*"],
		plotMarkStyle = "ziktPlotChartMark",
		additionalPlotMarkStyle = u"mark={mark},mark options={{color={outlineColor}}}",
		#
		lineStyle = u"ziktPlotChartLine",
		additionalLineStyle = u"color={drawColor}",
		lineInstruction = u"({lastCoordinate}) -- ({coordinate})",
		#
		abscissaJutStyle=None,
		abscissaTickLabelString=u"",
	)
	presettings =  {
		'base': base,
	}
	
	def __init__(self,preset="base", printComments=True, **kwargs):
		MultipleValueCoordinateChart.__init__(self)
		self.attributes = PlotChart.presettings[preset].copy()
		self.attributes.extend(**kwargs)
		self.printComments = printComments
		self.attributeDict = self.attributes.getDict()
		

if __name__ == "__main__":
	c =  PlotChart(ordinateLength=6,stackmode = True)
	print c.render(table = FloatTable(getBasicTable()))