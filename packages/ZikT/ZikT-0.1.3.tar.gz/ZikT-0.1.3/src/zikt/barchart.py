# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''
from __future__ import division
from zikt.helper import ziktRenderException, Attributes, decimalCeil
from cs import TikZCoordinateSystem


class BarChart(TikZCoordinateSystem):
	preset_bar = Attributes(
			parent=TikZCoordinateSystem.empty_preset,
			#
			abscissaJutStyle=None,
			#
			fallbackOrdinateLength=5,
			#
			barWidth=1,
			startMargin=0.5,
			midMargin=0.6,
			endMargin=0.2,
			barMargin=0.3,
			#
			barStyleMode='single', #single or multiple
			barStyle="catsvBarChartBar",	barStyles=["catsvBarChartBarOne","catsvBarChartBarTwo","catsvBarChartBarThree","catsvBarChartBarFour","catsvBarChartBarFive","catsvBarChartBarSix","catsvBarChartBarSeven","catsvBarChartBarEight","catsvBarChartBarNine","catsvBarChartBarTen","catsvBarChartBarEleven","catsvBarChartBarTwelve"],
			#
			additionalBarStyle='',
			additionalOuterLowerLabelStyle='',
			additionalInnerLowerLabelStyle='',
			additionalCenterLabelStyle='',
			additionalInnerUpperLabelStyle='',
			additionalOuterUpperLabelStyle='',
			#
			outerLowerLabelStyle=u'catsvBarChartOuterLowerLabel',
			innerLowerLabelStyle=u'catsvBarChartInnerLowerLabel',
			centerLabelStyle=[u'catsvBarChartCenterLabelHorizontal',u'catsvBarChartCenterLabelVertical'],
			innerUpperLabelStyle=u'catsvBarChartInnerUpperLabel',
			outerUpperLabelStyle=u'catsvBarChartOuterUpperLabel',
			#
			groupUpperLabelStyle=u'catsvBarChartGroupUpperLabel',
			groupLowerLabelStyle=u'catsvBarChartGroupLowerLabel',
			#
			additionalGroupUpperLabelStyle='',
			additionalGroupLowerLabelStyle='',
			#
			outerLowerLabelString=u'{n}',
			innerLowerLabelString=u'',
			centerLabelString=u'',
			innerUpperLabelString=u'',
			outerUpperLabelString=u'',
			#
			groupUpperLabelString=u'',
			groupLowerLabelString=u'',
			#
			flipLowerLabelsWhenNegative=False,
			flipUpperLabelsWhenNegative=False, 
			flipOuterLabelsWhenNegative=True,
			flipInnerLabelsWhenNegative=True, 
			valueConversion='int',#'int','round' or a callable (lambda)
			#
			#TODO fullValue
			#
			barLengthThreshold=1,
			flipLowerAboveWhenThreshold=False,
			flipUpperAboveWhenThreshold=True,
			flipCenterAboveWhenThreshold=False,
			flipLowerBelowWhenThreshold=False,
			flipUpperBelowWhenThreshold=False,
			flipCenterBelowWhenThreshold=False,
		)
	preset_groupedbar = Attributes(
			parent=preset_bar,
			#
			barStyleMode='multiple',
			barWidth=0.5,
			midMargin=0.7,
			barMargin=0.1,
			#
			outerLowerLabelString='',
			innerUpperLabelString='{v}\,\%',
			groupLowerLabelString='{n}',
			#innerUpperLabelStyle='catsvBarChartInnerUpperLabelRotated',
		)
	presettings =  {
		'bar': preset_bar,
		'groupedbar' : preset_groupedbar,
	}
	
	def __init__(self,preset="bar", printComments=True, **kwargs):
		self.attributes = BarChart.presettings[preset].copy()
		self.attributes.extend(**kwargs)
		self.printComments = printComments
		self.attributeDict = self.attributes.getDict()
		
		
	def drawBar(self,index,firstValue,secondValue, percentage,maxValue,minValue,maxOrdinateValue,minOrdinateValue,name,abscissaLeftAnchor,abscissaMidAnchor,abscissaRightAnchor,style,cs):
		result=[]
		#TODO additionalStyles für alle Labels und styles
		#
		# Convert displayed value (v)
		lowerValue = min(firstValue, secondValue)
		greaterValue = max(firstValue, secondValue)
		value = greaterValue - lowerValue
		if lowerValue == 0:
			v = greaterValue
		elif greaterValue == 0:
			v = lowerValue
		else:
			v=value
		if self.attributes.valueConversion=='int':
			if (v%1==0): v=int(v)
		if self.attributes.valueConversion=='round':
			v=int(round(v))
		if callable(self.attributes.valueConversion):
			v=self.attributes.valueConversion(v)
		#TODO mehr davon: länge des balken in baseunit, startseite des balken (left,right, top, down), endseite des balken
		#
		# make a dict with relevant data for this item (used for format string in labels and styles)
		startSide=''
		endSide=''
		if (self.attributes.abscissaDirection == 'right' or self.attributes.abscissaDirection == 'left'):
			if self.attributes.ordinateInversion:
				startSide='top'
				endSide='bottom'
			else:
				startSide='bottom'
				endSide='top'
		else:
			if self.attributes.ordinateInversion:
				startSide='left'
				endSide='right'
			else:
				startSide='right'
				endSide='left'
		if value < 0:
			startSide, endSide = endSide, startSide
		itemDict={
			'v':v,
			'value':v,
			'p':percentage,
			'absPercentage':abs(percentage),
			'n':name,
			'name':name,
			'r':percentage/100,
			'absRatio':abs(percentage)/100,
			'max':maxValue,
			'min':minValue,
			'maxOrdinate':maxOrdinateValue,
			'minOrdinate':minOrdinateValue,
			#TODO: bug: maxValue-minValue can be zero
			#TODO: bug: may be the same as above: If a tables first row has a sum of zero, i get a divided by zero exception
			'totalRatio':(value-minValue) / (maxValue-minValue),
			'totalPercentage':100 * (value-minValue) / (maxValue-minValue),
			'totalRatioOrdinate':(value-minOrdinateValue) / (maxOrdinateValue-minOrdinateValue),
			'absMax':abs(maxValue),
			'absMin':abs(minValue),
			'absMaxOrdinate':abs(maxOrdinateValue),
			'absMinOrdinate':abs(minOrdinateValue),
			'absTotalRatio':abs(value) / max(abs(minValue),abs(maxValue)),
			'absTotalPercentage':100 * abs(value) / max(abs(minValue),abs(maxValue)),
			'totalRatioOrdinate':abs(value)-min(abs(minOrdinateValue),abs(maxOrdinateValue)) / (max(abs(minOrdinateValue),abs(maxOrdinateValue))-min(abs(minOrdinateValue),abs(maxOrdinateValue))),
			'startSide':startSide,
			'endSide':endSide,
		}
		#
		# draw the bar
		result.append(cs.drawRectangle((abscissaLeftAnchor,lowerValue),(abscissaRightAnchor,greaterValue),style+","+self.attributes.additionalBarStyle.format(**itemDict)))
		#
		# initialize the label texts
		olL=self.attributes.outerLowerLabelString.format(**dict(self.attributeDict.items()+itemDict.items()))
		ilL=self.attributes.innerLowerLabelString.format(**dict(self.attributeDict.items()+itemDict.items()))
		cL=self.attributes.centerLabelString.format(**dict(self.attributeDict.items()+itemDict.items()))
		iuL=self.attributes.innerUpperLabelString.format(**dict(self.attributeDict.items()+itemDict.items()))
		ouL=self.attributes.outerUpperLabelString.format(**dict(self.attributeDict.items()+itemDict.items()))
		# make label flips that depend on bar length
		if abs(cs.realToTikzY(value)) < self.attributes.barLengthThreshold:
			if self.attributes.flipLowerAboveWhenThreshold: ilL,ouL = ouL,ilL
			if self.attributes.flipUpperAboveWhenThreshold: iuL,ouL = ouL,iuL
			if self.attributes.flipCenterAboveWhenThreshold: cL,ouL = ouL,cL
			if self.attributes.flipLowerBelowWhenThreshold: ilL,olL = olL,ilL
			if self.attributes.flipUpperBelowWhenThreshold: iuL,olL = olL,iuL
			if self.attributes.flipCenterBelowWhenThreshold: cL,olL = olL,cL
		# make label flips that depend on negative value
		if lowerValue < 0:
			if self.attributes.flipLowerLabelsWhenNegative:
				olL,ilL = ilL,olL
			if self.attributes.flipUpperLabelsWhenNegative:
				ouL,iuL = iuL,ouL
			if self.attributes.flipOuterLabelsWhenNegative:
				olL,ouL = ouL,olL
			if self.attributes.flipInnerLabelsWhenNegative:
				ilL,iuL = iuL,ilL
		#outer lower label
		if self.attributes.outerLowerLabelStyle != None and olL != "":
			style=(cs.getStyle('orientedLabelStyleBelow') if value > 0 else cs.getStyle('orientedLabelStyleAbove'))+","+cs.getStyle('outerLowerLabelStyle')
			style=style+','+self.attributes.additionalOuterLowerLabelStyle.format(**dict(self.attributeDict.items()+itemDict.items()))
			label=olL
			result.append("\\path {c} node[{style}] {{{label}}};".format(c=cs.tcoord((abscissaMidAnchor, lowerValue)),style=style,label=label))
		#inner lower label
		if self.attributes.innerLowerLabelStyle != None and ilL != "":
			style=(cs.getStyle('orientedLabelStyleAbove') if value > 0 else cs.getStyle('orientedLabelStyleBelow'))+","+cs.getStyle('innerLowerLabelStyle')
			style=style+','+self.attributes.additionalInnerLowerLabelStyle.format(**dict(self.attributeDict.items()+itemDict.items()))
			label=ilL
			result.append("\\path {c} node[{style}] {{{label}}};".format(c=cs.tcoord((abscissaMidAnchor,lowerValue)),style=style,label=label))
		#center
		if self.attributes.centerLabelStyle != None and cL != "":
			style=cs.getStyle('orientedLabelStyleCenter')+","+cs.getStyle('centerLabelStyle')
			style=style+','+self.attributes.additionalCenterLabelStyle.format(**dict(self.attributeDict.items()+itemDict.items()))
			label=cL
			result.append("\\path {c} node[{style}] {{{label}}};".format(c=cs.tcoord((abscissaMidAnchor,lowerValue+value/2)),style=style,label=label))
		#inner upper label
		if self.attributes.innerUpperLabelStyle != None and iuL != "":
			style=(cs.getStyle('orientedLabelStyleBelow') if value > 0 else cs.getStyle('orientedLabelStyleAbove'))+","+cs.getStyle('innerUpperLabelStyle')
			style=style+','+self.attributes.additionalInnerUpperLabelStyle.format(**dict(self.attributeDict.items()+itemDict.items()))
			label=iuL
			result.append("\\path {c} node[{style}] {{{label}}};".format(c=cs.tcoord((abscissaMidAnchor,greaterValue)),style=style,label=label))
		#outer upper label
		if self.attributes.outerUpperLabelStyle != None and ouL != "":
			style=(cs.getStyle('orientedLabelStyleAbove') if value > 0 else cs.getStyle('orientedLabelStyleBelow'))+","+cs.getStyle('outerUpperLabelStyle')
			style=style+','+self.attributes.additionalOuterUpperLabelStyle.format(**dict(self.attributeDict.items()+itemDict.items()))
			label=ouL
			result.append("\\path {c} node[{style}] {{{label}}};".format(c=cs.tcoord((abscissaMidAnchor,greaterValue)),style=style,label=label))
		#TODO: low : Schriftdefinitionen aus den tikz-styles in separate defs auslagern
		#
		return '\n'.join(result)
	
	def getCsAndMinAndMax(self,realMinValue,realMaxValue,width):
		if self.attributes.ordinateLength==None and self.attributes.ordinateTickDelta==None:
			self.attributes.extend(ordinateLength=self.attributes.fallbackOrdinateLength)
		if self.attributes.ordinateMin == None:
			minValue=decimalCeil(min(realMinValue,0))
			self.attributes.extend(ordinateMin=minValue)
		if self.attributes.ordinateMax == None:
			maxValue=decimalCeil(max(realMaxValue,0))
			self.attributes.extend(ordinateMax=maxValue)
		if self.attributes.abscissaLength==None:			
			self.attributes.extend(abscissaLength=width)
		self.attributes.extend(abscissaDomain=self.attributes.abscissaLength)
		self.attributes.extend(abscissaMin=-self.attributes.startMargin)
		self.attributes.extend(ordinateValue=-self.attributes.startMargin)
		#	
		self.attributes.extend(abscissaTickDelta=0)
		#
		cs = TikZCoordinateSystem(**self.attributes.getDict())
		return cs,minValue,maxValue
	
	def render(self,table):
		rowCount = table.getRowCount()
		colCount = table.getColCount()
		# initialize
		total = []
		realMinValue=float(table.getCell(0,0))
		realMaxValue=float(table.getCell(0,0))
		values = []
		for j in range(0,rowCount):
			values.append([])
			total.append(0.0)
			for i in range(0,colCount):
				try:
					cell=table.getCell(i,j)
					try:
						f = float(cell)
					except:
						f=0
					values[j].append(f)
					total[j] += f
					realMinValue = min(f,realMinValue)
					realMaxValue = max(f,realMaxValue)
				except ValueError, e:
					raise ziktRenderException( "Minimum one cell does not contain a valid number. (%s)" % str(e))
#		n = len(values)
#		width=self.attributes.startMargin+self.attributes.endMargin+n*self.attributes.barWidth+(n-1)*self.attributes.midMargin
		#print rowCount," ",colCount
		groupWidth = (
			colCount * self.attributes.barWidth +
			(colCount - 1) * self.attributes.barMargin
		)
		width = (
			self.attributes.startMargin +
			self.attributes.endMargin +
			(rowCount - 1) * self.attributes.midMargin +
			(rowCount) * groupWidth
		)
			
		cs,minValue,maxValue = self.getCsAndMinAndMax(realMinValue,realMaxValue,width)
			
		# building output
		result = []
		
		result.append(cs.getTikZ())
		
		#draw the n × m bars
		for j in range(0,rowCount):
			maxInRow=values[j][0]
			minInRow=values[j][0]
			for i in range(0,colCount):
				if values[j][i] > maxInRow: maxInRow=values[j][i]
				if values[j][i] < minInRow: minInRow=values[j][i]
				leftAnchor = (
					j * (groupWidth + self.attributes.midMargin) +
					i * (self.attributes.barWidth + self.attributes.barMargin)
				)
				result.append(self.drawBar(**{
					'index':i,
					'firstValue':0, 
					'secondValue':values[j][i],
					'percentage':100*values[j][i]/total[j] if total[j] != 0 else 0,
					'maxValue':realMaxValue,
					'minValue':realMinValue,
					'maxOrdinateValue':maxValue,
					'minOrdinateValue':minValue,
					'name':table.getColHeader(i),
					'abscissaLeftAnchor': leftAnchor,
					'abscissaMidAnchor': (0.5)*self.attributes.barWidth + leftAnchor,
					'abscissaRightAnchor': self.attributes.barWidth + leftAnchor,
					'style':(self.attributes.barStyle if self.attributes.barStyleMode == 'single' else self.attributes.barStyles[i % len(self.attributes.barStyles)]),
					'cs':cs
				}))
			leftAnchor= j * (groupWidth + self.attributes.midMargin)
			midAnchor = leftAnchor + groupWidth/2
			#TODO: low: das wurde auskommentiert weil es nicht genutzt wurde; ich weiß aber nicht warum das da steht...
			#rightAnchor = leftAnchor + groupWidth
			groupDict = {
				'n':table.getRowHeader(j),
				'name':table.getRowHeader(j),
				'total':total[j],
			}
			if self.attributes.groupUpperLabelString != "" and self.attributes.groupUpperLabelStyle != None:
				style = cs.getStyle('groupUpperLabelStyle') + ',' + cs.getStyle('orientedLabelStyleAbove') + ',' + self.attributes.additionalGroupUpperLabelStyle.format(**groupDict)
				label = self.attributes.groupUpperLabelString.format(**groupDict)
				result.append("\\path {c} node [{style}] {{{label}}};".format(c=cs.tcoord((midAnchor,max(maxInRow,0))),style=style,label=label))
			if self.attributes.groupLowerLabelString != "" and self.attributes.groupLowerLabelStyle != None:
				style = cs.getStyle('groupLowerLabelStyle') + ',' + cs.getStyle('orientedLabelStyleBelow') + ',' + self.attributes.additionalGroupLowerLabelStyle.format(**groupDict)
				label = self.attributes.groupLowerLabelString.format(**groupDict)
				result.append("\\path {c} node [{style}] {{{label}}};".format(c=cs.tcoord((midAnchor,min(minInRow,0))),style=style,label=label))
		return "\n".join(result)

#t = FloatTable()
#t.addRow([0.5,1,1])
#t.addRow([0.5,1,1])
#b = BarChart()
#b.render(t)
