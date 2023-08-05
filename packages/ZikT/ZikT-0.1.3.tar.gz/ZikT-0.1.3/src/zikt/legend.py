# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

class Legend():
	##
	def __init__(self, table, attributes):
		self.table = table
		self.attributes = attributes
		self.basicLegendItemStyle = "basiclegenditem"
		##
		##
	def getRowAttribute(self, rowIndex, attributeName):
# 		if self.attributes.stackmode and self.attributes.stackmode == "onTopOfFirstRow":
# 			rowIndex -= 1
		attribute = self.attributes.getDict()[attributeName]
		if not isinstance(attribute, list):
			return attribute
		else:
			return attribute[rowIndex % len(attribute)]
		##
		##
	def get_tikz(self,anchor):
		result = []
		rowCount = 1
		if self.attributes.stackmode and self.attributes.stackmode == "onTopOfFirstRow":
			rowHeaders = self.table.getRowHeaders()[1:]
		else:
			rowHeaders = self.table.getRowHeaders()
		for rowHeader in rowHeaders:
			style = self.attributes.legendItemStyle if hasattr(self.attributes, 'legendItemStyle') else self.basicLegendItemStyle
			name = "legend"+str(rowCount)
			isVertical = True if hasattr(self.attributes, 'legendDirection') and self.attributes.legendDirection == "Vertical" else False
			style += (",right=of (%s)" if isVertical else ",below=of (%s)")%(anchor) 
			result.append("\\path ({c}) node[{style}] ({name}) {{{label}}};".format(c=anchor, style=style, name = name, label=rowHeader))
			anchor=name
			rowCount += 1
		
	def get_hacked_floating_legend(self):
		index = 0
		result=[]
		if self.attributes.stackmode and self.attributes.stackmode == "onTopOfFirstRow":
			rowHeaders = self.table.getRowHeaders()[1:]
		else:
			rowHeaders = self.table.getRowHeaders()
		for rowHeader in rowHeaders:
			draw = self.getRowAttribute(index,"drawColors")
			fill = self.getRowAttribute(index,"fillColors")
			legendFont = self.getRowAttribute(index, "legendFont")
			index += 1
			if legendFont == None or legendFont == "":
				legendfontstyle = ""
			else:
				legendfontstyle = "font="+legendFont
			result.append("\\tikz{")
			result.append("\\coordinate(a);\\path[ fill=%s, draw=%s,ziktBaseLine] (a) ++(-1mm,0mm) -- ++(0mm,1mm) -- ++(2mm,0mm) -- ++(0mm,-2mm) -- ++(-2mm,0mm) -- cycle;"%(fill,draw))
			result.append("\\node[right=1mm of a.east, anchor=west,text width=,text depth=-0.1ex,%s]{%s};"%(legendfontstyle, rowHeader))
			result.append('}')
		return '\n'.join(result)  