# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

from __future__ import division
from zikt.cschart import MultipleValueCoordinateChart
from types import LambdaType

#TODO:high: test painters with tables containing significant null value patterns

def getLabelNode(coord, name,attributeDict,renderer,orientation=None):
	style = renderer.attributeDict[name+"Style"]
	try:
		additionalStyle = renderer.attributeDict["additional"+name.title()+"Style"]
	except:
		additionalStyle = ""
	string = renderer.attributeDict[name+"String"]
	if style != None and string != None and string != "":
		string = string(attributeDict) if isinstance(string, LambdaType) else string.format(**attributeDict)
		style = style(attributeDict) if isinstance(style, LambdaType) else style.format(**attributeDict)
		additionalStyle = additionalStyle(attributeDict) if isinstance(additionalStyle, LambdaType) else additionalStyle.format(**attributeDict)
		style = ",".join([style,additionalStyle])
		if orientation  == None:
			orientationStyle = ""
		else:
			orientationStyle = renderer.getStyle('orientedLabelStyle' + orientation) + ","
		return "\\path ({c}) node[{orientationStyle}{style}] {{{label}}};".format(
			c=coord,
			orientationStyle=orientationStyle,
			style=style,
			label=string
		)
	else:
		return None
	##
##
		
class PlotPainter():
	@staticmethod
	def paint(renderer,table,labelTable,rowIndex):
		lineResult = []
		markResult = []
		labelResult = []
		lastCoord=None
		for colIndex in range(table.getColCount()):
			if table.getCell(colIndex,rowIndex) == None:
				continue
			coord = MultipleValueCoordinateChart.getValueCoordinateName(colIndex,rowIndex)
			formatDict = renderer.getCellDict(colIndex,rowIndex,table,labelTable)
			formatDict.update({
				'mark' : renderer.getRowAttribute(rowIndex,'plotMarks'),
			})
			# the label above
			labelAbove = getLabelNode(coord, "valuePointLabelAbove", formatDict, renderer, orientation = 'Above')
			if labelAbove != None:
				labelResult.append(labelAbove)
			# the label below
			labelBelow = getLabelNode(coord, "valuePointLabelBelow", formatDict, renderer, orientation = 'Below')
			if labelBelow != None:
				labelResult.append(labelBelow)
			# the plot marks
			if renderer.attributes.plotMarkStyle != None:
				markStyle = (renderer.attributes.plotMarkStyle + ", " + renderer.attributes.additionalPlotMarkStyle).format(**dict(formatDict.items()))
				markResult.append("\\path[{style}] plot coordinates {{({c})}};".format(c=coord, style=markStyle))
			# the plot line
			if renderer.attributes.lineStyle != None:
				lineStyle = (renderer.attributes.lineStyle + ", " + renderer.attributes.additionalLineStyle).format(**dict(formatDict.items()))
				if lastCoord !=None:
					lineResult.append(("\path[{style}] "+renderer.getRowAttribute(rowIndex,'lineInstruction')+";").format(lastCoordinate=lastCoord, coordinate=coord, style=lineStyle))
			# for the next iteration... :)			
			lastCoord = coord
			##
		return '\n'.join(['\n'.join(lineResult),'\n'.join(markResult),'\n'.join(labelResult)])
		##

class BarPainter:
	@staticmethod
	def paint(renderer,table,labelTable,rowIndex):
		if rowIndex == 0:
			return ""
		barResult = []
		labelResult = []
		for colIndex in range(table.getColCount()):
			if table.getCell(colIndex,rowIndex) == None:
				continue
			##
			coord = MultipleValueCoordinateChart.getValueCoordinateName(colIndex,rowIndex)
			lowerCoord = MultipleValueCoordinateChart.getValueCoordinateName(colIndex,rowIndex-1)
			formatDict = renderer.getCellDict(colIndex,rowIndex,table,labelTable,designOffset=-1)
			# the bar
			barStyle = (renderer.attributes.barStyle + "," + renderer.attributes.additionalBarStyle).format(**formatDict)
			offset = (renderer.attributes.abscissaTickDelta * renderer.attributes.barWidthRatio) / 2
			v1 = renderer.tcoord(renderer.transformTikZVector(-offset,0))
			v2 = renderer.tcoord(renderer.transformTikZVector(offset,0))
			#:TODO another conclicting revision has changed these lines to these: (check if this is correct!)
			#v1 = renderer.tcoord((-offset,0))
			#v2 = renderer.tcoord((offset,0))
			
			barResult.append(
				"\\path[coordinate] ({c2}) ++{v2} coordinate(t);\\path[{style}] ({c1}) ++{v1} rectangle (t);".format(
					style=barStyle,
					c1=coord,
					c2=lowerCoord,
					v1=v1,
					v2=v2,
					offset=offset,
					unit=renderer.attributes.baseunit,
				)
			)
		return '\n'.join(['\n'.join(barResult),'\n'.join(labelResult)])
	
class AreaPainter:
	@staticmethod
	def paint(renderer,table,labelTable,rowIndex):
		if rowIndex == 0:
			return ""
		upperCoordsLeftToRight = []
		lowerCoordsLeftToRight = []
		areaFormatDict = renderer.getCellDict(None,rowIndex,table,labelTable,designOffset=-1)
		areaStyle = (renderer.attributes.areaStyle + "," + renderer.attributes.additionalAreaStyle).format(**areaFormatDict)
		for colIndex in range(table.getColCount()):
			if table.getCell(colIndex,rowIndex) == None:
				continue
			upperCoordsLeftToRight.append(MultipleValueCoordinateChart.getValueCoordinateName(colIndex,rowIndex))
			lowerCoordsLeftToRight.append(MultipleValueCoordinateChart.getValueCoordinateName(colIndex,rowIndex-1))
			colFormatDict = renderer.getCellDict(colIndex,rowIndex,table,labelTable,designOffset=-1)
			
			
#			labelAbove = getLabelNode(coord, "valuePointLabelAbove", formatDict, renderer, orientation = 'Above')
#			if labelAbove != None:
#				labelResult.append(labelAbove)
#			
#			if renderer.attributes.centerLabelString != None and renderer.attributes.centerLabelString != "":
#				centerLabelStyle = (renderer.attributes.centerLabelStyle + "," + renderer.attributes.additionalCenterLabelStyle).format(**colFormatDict)
#				
#			upperLabelStyle = (renderer.attributes.upperLabelStyle + "," + renderer.attributes.additionalUpperLabelStyle).format(**colFormatDict)
#			lowerLabelStyle = (renderer.attributes.lowerLabelStyle + "," + renderer.attributes.additionalLowerLabelStyle).format(**colFormatDict)
			
			
		areaTikZ = "\\path[{style}] {lowerPath} -- {upperPath} -- cycle;".format(
			style = areaStyle,
			lowerPath = " -- ".join("({c})".format(c=c) for c in lowerCoordsLeftToRight),
			upperPath = " -- ".join("({c})".format(c=c) for c in reversed(upperCoordsLeftToRight)),
		)
		return '\n'.join([areaTikZ])