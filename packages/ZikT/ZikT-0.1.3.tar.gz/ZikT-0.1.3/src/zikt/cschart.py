# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

from __future__ import division
from zikt.helper import ziktRenderException, Attributes
#import math
from zikt.cs import TikZCoordinateSystem
from legend import Legend
#import sys
import copy


class MultipleValueCoordinateChart(TikZCoordinateSystem):
	"""
	A very basic renderer that take n lines from the table as input and defines TikZ coordinates aliases at the coresponding coordinates.
	"""
	base = Attributes(
		parent=TikZCoordinateSystem.empty_preset,
		#
		relevantRowCount = 2,  # how many rows from the input table are used to print a value coordinate
		stackmode = False, # if true, the values’ coordinates are not set directly by the value but “stacked” by adding the value to all former values 
		ordinateLength = 5,  # default length of the ordinate
		alwaysIncludeZero = False, # if true, ordinate domain is enlarged to include zero if it does not contain zero naturally
		#TODO: low : add additional upper and lower space to this AND the BarChart (maybe common super class?); the additional space could be specifed as percentage of the ordinate domain
		#additionalUpperOrdinateDomain = None, # percentage of the ordinate domain that get added to the upper end of the ordinate to get some graphical space above the highest coordinate
		#additionalLowerOrdinateDomain = None, # percentage of the ordinate domain that get added to the lower end of the ordinate to get some graphical space above the highest coordinate
		#
		# Margins
		#
		startMargin=0.7,  # margin before the first column
		endMargin=0.7,  # margin after the first column
		columnMargin=1,  # margin between two columns
		abscissaTickDelta = 1,
		#
		# TikZ classes for colors
		#
		#TODO: low (until working on graphs that are not derived from cschart): move this "row classes" to the most upper renderer class
		drawColors = ["colorElementOneDraw","colorElementTwoDraw","colorElementThreeDraw","colorElementFourDraw","colorElementFiveDraw","colorElementSixDraw","colorElementSevenDraw","colorElementEightDraw","colorElementNineDraw","colorElementTenDraw","colorElementElevenDraw","colorElementTwelve"],
		fillColors = ["colorElementOneFill","colorElementTwoFill","colorElementThreeFill","colorElementFourFill","colorElementFiveFill","colorElementSixFill","colorElementSevenFill","colorElementEightFill","colorElementNineFill","colorElementTenFill","colorElementElevenFill","colorElementTwelveFill"], 
		outlineColors = ["colorElementOneOutline","colorElementTwoOutline","colorElementThreeOutline","colorElementFourOutline","colorElementFiveOutline","colorElementSixOutline","colorElementSevenOutline","colorElementEightOutline","colorElementNineOutline","colorElementTenOutline","colorElementElevenOutline","colorElementTwelveOutline"], 
		#
		# TikZ strings
		#
		columnTikZString = None, 
		valueTikZString = None, 
		#
		# Labels (styles, additional styles and strings)
		#
		maximumLabelStyle=u'',
		minimumLabelStyle=u'',
		highestLabelStyle=u'',
		lowestLabelStyle=u'',
		#
		additionalMaximumLabelStyle=u'',
		additionalMinimumLabelStyle=u'',
		additionalHighestLabelStyle=u'',
		additionalLowestLabelStyle=u'',
		#
		maximumLabelString=u'',
		minimumLabelString=u'',
		highestLabelString=u'',
		lowestLabelString=u'',
		#
		painter=None,
		legend=False,
		legendFont=None,
	)
	presettings =  {
		'base': base,
	}
	
	def __init__(self,preset="base", printComments=True, **kwargs):
		TikZCoordinateSystem.__init__(self)
		self.attributes = MultipleValueCoordinateChart.presettings[preset].copy()
		self.attributes.extend(**kwargs)
		self.printComments = printComments
		self.attributeDict = self.attributes.getDict()
		# ToDo: make the values for the value columns flexible by using a table row; that way, this chart can be used even for specific numerical indices of the value columns; …
		# if the array is None, the values will be automatically calculates with omni distances for the value columns; if the values come from the input table, the columnMargin attribute
		# will not be used for the rendering.
		self.valueColumnsValues = None
		
	def getRowAttribute(self, rowIndex, attributeName):
		attribute = self.attributeDict[attributeName]
		if not isinstance(attribute, list):
			return attribute
		else:
			return attribute[rowIndex % len(attribute)]
		
	@staticmethod
	def getValueCoordinateName(colIndex, rowIndex):
		return "v-%i-%i"%(colIndex, rowIndex)
	
	def getValueColumn(self, colIndex, table,  minValue,  maxValue, labelTable = None):
		if labelTable == None:
			labelTable = table
		result=[]
		col = table.getCol(colIndex)
		labelCol = labelTable.getCol(colIndex)
		# calculate sum (total)
		total = 0
		for cell in col:
			if cell != None:
				total += cell
		#
		# define the value coordinates
		for i in range(len(col)):
			if col[i] == None:
				continue
			coordinateName = MultipleValueCoordinateChart.getValueCoordinateName(colIndex, i)
			coordinate = self.tcoord((colIndex, col[i]))
			result.append( "\\coordinate (%s) at %s;"%(coordinateName, coordinate))
		#
		# set the coordinates on the outer lines and the abscissa
		maxCoordinate = self.tcoord((colIndex, maxValue))
		minCoordinate = self.tcoord((colIndex, minValue))
		result.append( "\\coordinate (%s) at %s;"%("min-"+str(colIndex), minCoordinate))
		result.append( "\\coordinate (%s) at %s;"%("max-"+str(colIndex), maxCoordinate))
		abscissaCoordinate = None
		if self.abscissaDefined:
			abscissaCoordinate = self.tcoord((colIndex, self.attributes.abscissaValue))
			result.append( "\\coordinate (%s) at %s;"%("abscissa-"+str(colIndex), abscissaCoordinate))
		#
		minColValue, maxColValue = table.getMinMaxOfCol(colIndex)
		minColValueIndex,  maxColValueIndex = table.getMinMaxIndicesOfCol(colIndex)
		lowestValueCoordinate = MultipleValueCoordinateChart.getValueCoordinateName(colIndex, minColValueIndex)
		highestValueCoordinate = MultipleValueCoordinateChart.getValueCoordinateName(colIndex, maxColValueIndex)
		minimumCoordinate = "min-"+str(colIndex)
		maximumCoordinate = "max-"+str(colIndex)
		#
		columnDict={
			'lowestValueCoordinate' : lowestValueCoordinate, 
			'highestValueCoordinate' : highestValueCoordinate,
			'minimumCoordinate' : minimumCoordinate,
			'maximumCoordinate' : maximumCoordinate,
			'abscissaCoordinate' : "abscissa-"+str(colIndex),
			'colHeader' : table.getColHeader(colIndex), 
			'minValue' : minColValue, 
			'maxValue' : maxColValue,
			'total' : total,
		}
		# 
		# column labels
		# maximum label
		if (self.attributes.maximumLabelString != None) and (self.attributes.maximumLabelString != ""):
			style = self.getStyle("orientedLabelStyleAbove")
			if (self.attributes.maximumLabelStyle != None) and (self.attributes.maximumLabelStyle != ""):
				style +=  "," + self.attributes.maximumLabelStyle
			if (self.attributes.additionalMaximumLabelStyle != None) and (self.attributes.additionalMaximumLabelStyle != ""):
				style +=  "," + self.attributes.additionalMaximumLabelStyle.format(**dict(self.attributeDict.items()+columnDict.items()))
			string = self.attributes.maximumLabelString.format(**dict(self.attributeDict.items()+columnDict.items()))
			result.append("\\path ({c}) node[{style}] {{{label}}};".format(c=maximumCoordinate, style=style, label=string))
		# minimum label
		if (self.attributes.minimumLabelString != None) and (self.attributes.minimumLabelString != ""):
			style = self.getStyle("orientedLabelStyleBelow")
			if (self.attributes.minimumLabelStyle != None) and (self.attributes.minimumLabelStyle != ""):
				style +=  "," + self.attributes.minimumLabelStyle
			if (self.attributes.additionalMinimumLabelStyle != None) and (self.attributes.additionalMinimumLabelStyle != ""):
				style +=  "," + self.attributes.additionalMinimumLabelStyle.format(**dict(self.attributeDict.items()+columnDict.items()))
			string = self.attributes.minimumLabelString.format(**dict(self.attributeDict.items()+columnDict.items()))
			result.append("\\path ({c}) node[{style}] {{{label}}};".format(c=minimumCoordinate, style=style, label=string))
		# highest label
		if (self.attributes.highestLabelString != None) and (self.attributes.highestLabelString != ""):
			style = self.getStyle("orientedLabelStyleAbove")
			if (self.attributes.highestLabelStyle != None) and (self.attributes.highestLabelStyle != ""):
				style +=  "," + self.attributes.highestLabelStyle
			if (self.attributes.additionalHighestLabelStyle != None) and (self.attributes.additionalHighestLabelStyle != ""):
				style +=  "," + self.attributes.additionalHighestLabelStyle.format(**dict(self.attributeDict.items()+columnDict.items()))
			string = self.attributes.highestLabelString.format(**dict(self.attributeDict.items()+columnDict.items()))
			result.append("\\path ({c}) node[{style}] {{{label}}};".format(c=highestValueCoordinate, style=style, label=string))
		# lowest label
		if (self.attributes.lowestLabelString != None) and (self.attributes.lowestLabelString != ""):
			style = self.getStyle("orientedLabelStyleBelow")
			if (self.attributes.lowestLabelStyle != None) and (self.attributes.lowestLabelStyle != ""):
				style +=  "," + self.attributes.lowestLabelStyle
			if (self.attributes.additionalLowestLabelStyle != None) and (self.attributes.additionalLowestLabelStyle != ""):
				style +=  "," + self.attributes.additionalLowestLabelStyle.format(**dict(self.attributeDict.items()+columnDict.items()))
			string = self.attributes.lowestLabelString.format(**dict(self.attributeDict.items()+columnDict.items()))
			result.append("\\path ({c}) node[{style}] {{{label}}};".format(c=lowestValueCoordinate, style=style, label=string))
		#
		# write the column TikZ string
		if (self.attributes.columnTikZString != None) and (self.attributes.columnTikZString != ""):
			columnTikZString=self.attributes.columnTikZString.format(**dict(self.attributes.getDict().items()+columnDict.items()))
			result.append(columnTikZString)
		#
		# write the value TikZ strings
		if (self.attributes.valueTikZString != None) and (self.attributes.valueTikZString != ""):
			for i in range(len(col)):
				valueDict = {
					'index' : i, 
					'value' : labelCol[i],
					'paintValue' : col[i], 
					'coordinate' : MultipleValueCoordinateChart.getValueCoordinateName(colIndex, i), 
					'fillColor' : self.attributes.fillColors[i % len(self.attributes.fillColors)], 
					'outlineColor' : self.attributes.outlineColors[i % len(self.attributes.outlineColors)], 
				}
				valueTikZString=self.attributes.valueTikZString.format(**dict(self.attributes.getDict().items()+columnDict.items()+valueDict.items()))
				result.append(valueTikZString)
		#
		return "\n".join(result)
	
	def render(self,table):
		labelTable = table
		originalTable = copy.deepcopy(table)
		if self.attributes.stackmode:
			if self.attributes.stackmode == "onTopOfZero":
				onTopOfZero = True
			elif self.attributes.stackmode == "onTopOfFirstRow":
				onTopOfZero = False
			else:
				raise ziktRenderException("unknown stack mode %s"%(self.attributes.stackmode))
			table = table.getStacked(onTopOfZero = onTopOfZero)	
			firstRow = [0 for x in range(table.getColCount())]
			labelTable.insertRow(0, firstRow, "")
		rowCount = table.getRowCount()
		colCount = table.getColCount()
		minValue,  maxValue = table.getMinMax()
		#
		# if wanted, extend ordinate domain to include zero if it’s not already in there
		#TODO: mach das in cs.initDimensions!!! Dann funktioniert das nicht nur für cscharts sondern für alle CS!
		#Gleiches gilt für die noch fehlende Axis-Extend Funktion
		if self.attributes.alwaysIncludeZero:
			if minValue > 0:
				minValue = 0
			if maxValue < 0:
				maxValue = 0
		self.attributes.ordinateMin = minValue
		self.attributes.ordinateMax = maxValue
		#floorValue = math.floor(minValue)
		#ceilValue = math.ceil(maxValue)
		#
		# some checks before we start
		if  self.attributes.relevantRowCount < 1:
			raise ziktRenderException( "number of relevant rows must be minimum one")
		if rowCount < self.attributes.relevantRowCount:
			raise ziktRenderException( "number of relevant rows is higher than the number of rows in the input table")
		if colCount < 1:
			raise ziktRenderException( "input table has no data columns")
		#
		# Calculate the abscissa attributes
		if self.valueColumnsValues == None:
			# The columns will be omni distant; we can use coordinates as we like and we do it that way:
			# The columns we be placed on whole numbers (0,1,2,…) so the domain of the abscissa is the number of columns plus the start and end margin in proportion.
			# The ordinate Value will be set to the negated proportional Value of the start margin.
			#
			# first, we calculate the length of the abscissa
			if self.attributes.abscissaLength == None:
				self.attributes.abscissaLength =  \
					self.attributes.startMargin + \
					self.attributes.endMargin + \
					self.attributes.columnMargin * colCount
			# calculate the margins in value space (column margin in value space is 1 per definition)
			valueStartMargin = self.attributes.startMargin / self.attributes.columnMargin 
			valueEndMargin = self.attributes.endMargin / self.attributes.columnMargin
			# set the abscissa attributes and the ordinate position
			self.attributes.abscissaDomain = valueStartMargin + valueEndMargin + colCount-1
			self.attributes.abscissaMin = -valueStartMargin
			self.attributes.ordinateValue = -valueStartMargin
# 			# set the tick delta
# 			self.attributes.abscissaTickDelta = 1
		else:
			raise ziktRenderException("specific valueColumnsValues not yet supported")
		
		# Output generation starts here!!
		# Get the coordinate system TikZ code
		result = [TikZCoordinateSystem.render(self, table)]
		
		minValue = self.attributes.ordinateMin
		maxValue = self.attributes.ordinateMax
		
		# Get the n value columns
		for n in range(colCount):
			result.append(self.getValueColumn(n, table,  minValue,  maxValue, labelTable))
			
		# Call the painters…
		if self.attributes.painter != None and len(self.attributes.painter) > 0:
			for rowIndex in range(table.getRowCount()):
				painter = self.attributes.painter[rowIndex % len(self.attributes.painter)]
				result.append(painter.paint(self,table,labelTable,rowIndex))
		
		# Check if a legend is wanted
		if self.attributes.legend:
			legend = Legend(originalTable,self.attributes)
			lowest = self.attributes.ordinateMin# + 1/self.attributes.ordinateRatio
			leftest = self.attributes.abscissaMin
			rightest = self.attributes.abscissaMax
			mid = leftest + (rightest - leftest) / 2
			
			anchor = self.tcoord((mid,lowest))
			
			result.append("\\coordinate(legendanchor) at %s;"%anchor)
			result.append("\\node[below=1cm of legendanchor, anchor=north,text width=10cm]{%s};"%legend.get_hacked_floating_legend())
			
			#TODO: next: mache getter ins CS um coordinaten für die „Ecken“ zu bekommen
			#TODO: dann: mache die Basiskonfiguration in eine map nach Legend
			#TODO: dann: extende die eigene Basiskonfiguration mit dieser Map
			#TDOD: dann: in die Map muss legendPosition mit [north south,east,west]
			#TODO: dann: vertical leitet sich daraus ab
			#TODO: dann: mache primitive ausgabe und refactor die anker u.s.w.
			#TODO: dann: füge abstände, etc in die konfig-map ein
			#TODO: dann: mach geile Ausgabe 
				
		
		# return the result :)
		return "\n".join(result)
	
	def getCellDict(self, colIndex, rowIndex, table, labelTable, designOffset = 0):
		result = {
			'row':rowIndex,
			'col':colIndex,
			'index':colIndex,
			'fillColor' : self.getRowAttribute(rowIndex + designOffset,'fillColors'), 
			'outlineColor' : self.getRowAttribute(rowIndex + designOffset,'outlineColors'), 
			'drawColor' : self.getRowAttribute(rowIndex + designOffset,'drawColors'),
		}
		
		if colIndex != None:
			minV, maxV = labelTable.getMinMaxOfCol(colIndex)
			minVpaint, maxVpaint = table.getMinMaxOfCol(colIndex)
			result.update({
				'min':minV,
				'max':maxV,
				'paintMin':minVpaint,
				'paintMax':maxVpaint,
				'value':labelTable.getCell(colIndex,rowIndex),
				'paintValue':table.getCell(colIndex,rowIndex),
				'sum':table.getColSum(colIndex),
				'range':table.getColRange(colIndex),
			})
		return result
