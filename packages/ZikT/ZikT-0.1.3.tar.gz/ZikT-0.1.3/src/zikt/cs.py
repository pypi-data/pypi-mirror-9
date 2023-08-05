# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

from __future__ import division
from zikt.helper import ziktRenderException, Attributes, Coord
from math import ceil, log, pow, floor
import logging
from zikt.tikzrender import TikZRenderer
from zikt.tables import FloatTable
from types import LambdaType

#TODO: vision: support non-linear axes (exponential, logarithmic,...)
#TODO: high: support additional style for (outer) axis labels; I had a problem with an non-breakable outer ordinate label because "text width" could not be specified
#TODO: high: same for tick labels: I need "additional style" attributes; maybe that should be checked for all labels
class TikZCoordinateSystem(TikZRenderer):
	empty_preset = Attributes(
			ordinateLength=None,
			ordinateMin=None,
			ordinateMax=None,
			ordinateDomain=None,
			ordinateTickDelta=None,  # distance in value space
			ordinateTickAnchorValue = 0,
			ordinateValue = 0,
			ordinateRatio=None, # domain * ratio = length
			ordinateForcedDisplayMin = None,
			ordinateForcedDisplayMax = None,
			#
			abscissaLength=None,
			abscissaMin=None,
			abscissaMax=None,
			abscissaDomain=None,
			abscissaTickDelta=None,
			abscissaTickAnchorValue = 0,
			abscissaValue = 0,
			abscissaRatio=None,
			#
			baseunit='cm',
			abscissaDirection='right',
			ordinateInversion=False,
			ordinateOffset=0, #TODO: whats that?
			goodHorizontalTickDistance = 2,
			goodVerticalTickDistance = 0.8,
			forceWholeNumberedAbscissaTickDelta = False, # if True, a delta < 1 will be forced to 1
			forceWholeNumberedOrdinateTickDelta = False,
			#
			ordinateTickDivider=1,
			ordinateTickDividerOffset=0,
			skipOrdinateTickOnAbscissa=True,
			abscissaTickDivider=1,
			abscissaTickDividerOffset=0,
			skipAbscissaTickOnOrdinate=True,
			#
			ordinateTickLabelDivider=1,
			ordinateTickLabelDividerOffset=0,
			skipOrdinateTickLabelOnAbscissa=None,
			abscissaTickLabelDivider=1,
			abscissaTickLabelDividerOffset=0,
			skipAbscissaTickLabelOnOrdinate=None,
			#
			ordinateJutLength=0.5,
			abscissaJutLength=0.5,
			#
			ordinateTickNegativeLength=0.1,
			ordinateTickPositiveLength=0.1,
			abscissaTickNegativeLength=0.1,
			abscissaTickPositiveLength=0.1,
			#
			ordinateHelpLineDivider=1,
			ordinateHelpLineDividerOffset=0,
			skipOrdinateHelpLineOnAbscissa=True,
			abscissaHelpLineDivider=1,
			abscissaHelpLineDividerOffset=0,
			skipAbscissaHelpLineOnOrdinate=True,
			#
			ordinateHelpLineStyle='catsvOrdinateHelpLine',
			abscissaHelpLineStyle='catsvAbscissaHelpLine',
			#
			bodyStyle=u'catsvBody',
			ordinateStyle=u'catsvOrdinate',
			abscissaStyle=u'catsvAbscissa',
			ordinateJutStyle=u'catsvOrdinateJut',
			abscissaJutStyle=u'catsvAbscissaJut',
			ordinateTickStyle=u'catsvOrdinateTick',
			abscissaTickStyle=u'catsvAbscissaTick',
			#
			ordinateTickLabelStyle=['catsvTickLabelLeft','catsvTickLabelRight','catsvTickLabelBelow','catsvTickLabelAbove'],
			abscissaTickLabelStyle=[None,'catsvTickLabelBelow','catsvTickLabelLeft','catsvTickLabelAbove','catsvTickLabelRight',],
			outerOrdinateLabelStyle=['catsvOuterAxisLabel1','catsvOuterAxisLabel2','catsvOuterAxisLabel3','catsvOuterAxisLabel4','catsvOuterAxisLabel5','catsvOuterAxisLabel6','catsvOuterAxisLabel7','catsvOuterAxisLabel8',],
			outerAbscissaLabelStyle=['catsvOuterAxisLabel3','catsvOuterAxisLabel7','catsvOuterAxisLabel1','catsvOuterAxisLabel5','catsvOuterAxisLabel4','catsvOuterAxisLabel8','catsvOuterAxisLabel2','catsvOuterAxisLabel6',],
			alongsideOrdinateLabelStyle=['catsvAlongsideLabelRight','catsvAlongsideLabelLeft','catsvAlongsideLabelBelow','catsvAlongsideLabelAbove',],
			alongsideAbscissaLabelStyle=[None,'catsvAlongsideLabelBelow','catsvAlongsideLabelRight','catsvAlongsideLabelAbove','catsvAlongsideLabelLeft',],
			orientedLabelStyleAbove=[None,'catsvOrientedLabelAbove','catsvOrientedLabelRight','catsvOrientedLabelBelow','catsvOrientedLabelLeft',],
			orientedLabelStyleBelow=[None,'catsvOrientedLabelBelow','catsvOrientedLabelLeft','catsvOrientedLabelAbove','catsvOrientedLabelRight',],
			orientedLabelStyleLeft=[None,'catsvOrientedLabelLeft','catsvOrientedLabelAbove','catsvOrientedLabelRight','catsvOrientedLabelBelow',],
			orientedLabelStyleRight=[None,'catsvOrientedLabelRight','catsvOrientedLabelBelow','catsvOrientedLabelLeft','catsvOrientedLabelAbove',],
			orientedLabelStyleCenter='catsvOrientedLabelCenter',
			#
			alongsideOrdinateLabelPosition=None,
			alongsideAbscissaLabelPosition=None,
			#
			outerOrdinateLabelString=u"",
			outerAbscissaLabelString=u"",
			alongsideOrdinateLabelString=u"",
			alongsideAbscissaLabelString=u"",
			ordinateTickLabelString=u'{v}',
			abscissaTickLabelString=u'{v}',
			#
			tdhInteger_10Thres = 7,
			tdhInteger_5Thres = 4.2,
			tdhInteger_2Thres = 1.5,
			#
			csBodyHook = None,
		)
	simple_preset = Attributes(
			parent = empty_preset,
			#
			ordinateLength=5,
			ordinateTickDistance=None,
			ordinateMin=0,
			ordinateMax=10,
			ordinateDomain=None,
			ordinateTickCount=None,
			ordinateValue=0,
			ordinateRatio=None,
			#
			abscissaLength=10,
			abscissaTickDistance=None,
			abscissaMin=0,
			abscissaMax=20,
			abscissaDomain=None,
			abscissaTickCount=None,
			abscissaValue=0,
			abscissaRatio=None,
		)
	presettings =  {
		'empty': empty_preset,
		'simple': simple_preset
	}
			
			
	def __init__(self,preset="empty", printComments=True, **kwargs):
		self.attributes = TikZCoordinateSystem.presettings[preset].copy()
		self.attributes.extend(**kwargs)
		self.printComments = printComments
		self.abscissaDefined = False # will be set to true by the getTikZ-Method if the abscissa is in visible range
		self.ordinateDefined = False # will be set to true by the getTikZ-Method if the ordinate is in visible range
		#
		self.attributeDict = self.attributes.getDict()
		##
		##
	def coord(self,c):
		return self.transformCoord(self.realToTikzX(c[0]),self.realToTikzY(c[1]))
	def realToTikzX(self,x):
		return x*self.attributes.abscissaRatio
	def realToTikzY(self,y):
		return y*self.attributes.ordinateRatio
	def tikzToRealX(self,x):
		return x/self.attributes.abscissaRatio
	def tikzToRealY(self,y):
		return y/self.attributes.abscissaRatio
		##
	def tcoord(self,c):
		k= self.coord(c)
		result = "(%f%s,%f%s)"% (k[0],self.attributes.baseunit,k[1],self.attributes.baseunit)
		return result
		##
	def transformTikZVector(self,x,y):
		if self.attributes.abscissaDirection == 'right':
			return (x,-y) if self.attributes.ordinateInversion else (x,y)
		if self.attributes.abscissaDirection == 'left':
			return (-x,-y) if self.attributes.ordinateInversion else (-x,y)
		if self.attributes.abscissaDirection == 'top':
			return (y,-x) if self.attributes.ordinateInversion else (y,x)
		if self.attributes.abscissaDirection == 'down':
			return (-y,-x) if self.attributes.ordinateInversion else (-y,x)
		##
	#TODO: low: getStyle should always add an additional "additionalStyle" if its present :)
	#TODO: low: give this method a better error handling and API docs!
	def getStyle(self, style):
		styleEntry = self.attributeDict[style]
		if not isinstance(styleEntry, list):
			return styleEntry
		l=len(styleEntry)
		if l == 1:
			return styleEntry[0]
		if l == 2:
			return styleEntry[0] if self.attributes.abscissaDirection=='right' or self.attributes.abscissaDirection=='left' else styleEntry[1]
		##
		i = -1
		if self.attributes.abscissaDirection=='right': i=0
		if self.attributes.abscissaDirection=='left': i=1
		if self.attributes.abscissaDirection=='top': i=2
		if self.attributes.abscissaDirection=='down': i=3
		if i < 0:
			raise ziktRenderException("unknown abscissa direction")
		##
		if l == 4:
			return styleEntry[i]
		if l == 5:
			if self.attributes.ordinateInversion:
				i+=4
			i=int(i/2)+1
			return styleEntry[i]
		if l == 8:
			if self.attributes.ordinateInversion:
				i+=4
			return styleEntry[i]
		##
		##
	@staticmethod	
	def axisDistribution(delta, anchorValue, minValue, maxValue):
		offset = (anchorValue - minValue) % delta
		if offset < 0:
			offset += delta
		if offset < 0:
			raise "Algorithm hurts assumption. Debugging necessary."
		value = minValue + offset
		while value <= maxValue:
			yield round(value,3)
			value += delta
		##
		##
	def getAxisString(
					self,
					minValue,
					maxValue,
					axisValue,
					orthogonalMinValue,
					orthogonalMaxValue,
					orthogonalAxisValue,
					tickDelta,
					tickAnchorValue,
					tickStyle,
					helpLineStyle,
					helpLineDivider,
					helpLineDividerOffset,
					tickLabelStyle,
					tickLabelString,
					tickLabelDivider,
					tickLabelDividerOffset,
					skipTickOnOrthogonalAxis,
					skipHelpLineOnOrthogonalAxis,
					skipTickLabelOnOrthogonalAxis,
					tickCoordToNegativeVector,
					tickNegativeToPositiveVector,
					coordinateMapFunction
			):
		#ordinate ticks, help lines and tick labels
		if tickDelta > 0:
			tickStringArray = []
			tickLabelStringArray = []
			helpLineArray = []
			iterationIndex = 0
			for tickValue in TikZCoordinateSystem.axisDistribution(
				delta = tickDelta,
				anchorValue = tickAnchorValue,
				minValue = minValue,
				maxValue = maxValue
			):
				coordinateMapFunction(tickValue,axisValue)
				tickCoordinate = self.tcoord(coordinateMapFunction(tickValue,axisValue))
				#help line
				if helpLineStyle != None and helpLineDivider != 0:
					if (
						(helpLineDivider < 0 or (iterationIndex+helpLineDividerOffset) % ceil(helpLineDivider) == 0) 
						and
						(not skipHelpLineOnOrthogonalAxis or tickValue != orthogonalAxisValue)
						):
						if  helpLineDivider < 0:
							c = -helpLineDivider
						else:
							c = 1
						lineDistance = tickDelta / c
						for i in range(c):
							a = coordinateMapFunction(orthogonalMinValue,tickValue-i*lineDistance)
							b = coordinateMapFunction(orthogonalMaxValue,tickValue-i*lineDistance)
							helpLineArray.append("\\path[{helpLineStyle}] {start} -- {end};".format(**{
								'start':self.tcoord((a[1],a[0])),
								'end':self.tcoord((b[1],b[0])),
								'helpLineStyle':helpLineStyle
							}))
				#tick
				if tickValue != orthogonalAxisValue or not skipTickOnOrthogonalAxis:
					tickStringArray.append(
						"\\path[{tickStyle}] {c}  ++{v1} -- ++{v2};".format(					
							c=tickCoordinate,
							v1=tickCoordToNegativeVector,
							v2=tickNegativeToPositiveVector,
							tickStyle=tickStyle
						)
					)
				# tick label
				if ((iterationIndex + tickLabelDividerOffset) % tickLabelDivider == 0) and (not skipTickLabelOnOrthogonalAxis or tickValue != orthogonalAxisValue):
					v=int(tickValue) if tickValue%1==0 else tickValue 
					tickStringMap = {'v':v, 'value':v}
					tickLabelStringArray.append("\\path{c} node [{tickLabelStyle}] {{{label}}};".format(**{
						'c': tickCoordinate,
						'label':(tickLabelString(tickStringMap) if isinstance(tickLabelString, LambdaType) else tickLabelString.format(**tickStringMap)),
						'tickLabelStyle':tickLabelStyle
					}))
				iterationIndex += 1
				##
			result = []
			if helpLineStyle != None:
				result.append('\n'.join(helpLineArray))
			if tickStyle != None:
				result.append('\n'.join(tickStringArray))
			result.append('\n'.join(tickLabelStringArray))
			return '\n'.join(result)
			##
		else:
			return ''
		##
		##
	#TODO: low: write test cases for this method
	@staticmethod
	def initializeDimension(minValue, maxValue, domain, length, ratio, forcedMin = None, forcedMax = None):
		if domain != None and (not isinstance(domain, int) and not isinstance(domain,float)):
			raise ziktRenderException("domain value must be a number (integer or float)")
		if length != None and (not isinstance(length, int) and not isinstance(length,float)):
			raise ziktRenderException("domain value must be a number (integer or float)")
		if ratio != None and (not isinstance(ratio, int) and not isinstance(ratio,float)):
			raise ziktRenderException("domain value must be a number (integer or float)")
		##
		if ratio == None and length == None:
			raise ziktRenderException("ratio or length must be specified")
		if ratio != None and length != None:
			derivedDomain = length / ratio
			if domain == None:
				domain = derivedDomain
			else:
				if domain != derivedDomain:
					raise ziktRenderException(u"Length, ratio and domain are specified but length ≠ ratio × domain so the ratio is overspecified. Set one of them to None.")
		dataDomainIntervallConstraints = 0
		if minValue != None: dataDomainIntervallConstraints += 1
		if maxValue != None: dataDomainIntervallConstraints += 1
		if domain != None: dataDomainIntervallConstraints += 1
		if dataDomainIntervallConstraints < 2:
			raise ziktRenderException("Domain interval underspecified.")
		if dataDomainIntervallConstraints > 2:
			raise ziktRenderException("Domain interval overspecified.")
		if minValue == None:
			minValue = maxValue - domain
		if maxValue == None:
			maxValue = minValue + domain
		if forcedMin != None:
			minValue = min(forcedMin,minValue)
		if forcedMax != None:
			maxValue = max(forcedMax,maxValue)
		domain = maxValue - minValue
		if domain <= 0:
			raise ziktRenderException("Minimum and maximum value defines a negative or empty domain.")
			##
		if length == None:
			length = domain * ratio
		if ratio == None:
			ratio = length / domain
		if length <= 0:
			raise ziktRenderException("Length is negative or zero.")
		return minValue, maxValue, domain, length, ratio
		##
		##
	def initializeAxisDecoration(self, tickDelta, tickAnchorValue, helpLineDivider, helpLineDividerOffset, labelDivider, labelDividerOffset, minValue, maxValue, domain, length, axisIsHorizontal):
		if tickDelta == None:
			# tick delta is None, so we use a little heuristic algorithm to calculate it
			if axisIsHorizontal:
				goodTickDistance = self.attributes.goodHorizontalTickDistance
			else:
				goodTickDistance = self.attributes.goodVerticalTickDistance
			goodTickCount = length / goodTickDistance
			goodTickDelta = domain / goodTickCount
			decimalDimension = floor(log(goodTickDelta, 10))
			densityKey = goodTickDelta * pow(10,-decimalDimension)
			#TODO: low: in tick distribution heuristic: serve an optional fraction of [0,1/4,2/4,3/4,1] (and make it default for decimal dimensions < 0)
			if densityKey < self.attributes.tdhInteger_2Thres:
				multiplier = 1
			elif densityKey > self.attributes.tdhInteger_10Thres:
				multiplier = 10
			elif densityKey > self.attributes.tdhInteger_5Thres:
				multiplier = 5
			else:
				multiplier = 2
			tickDelta = pow(10,(decimalDimension)) * multiplier
		return tickDelta, tickAnchorValue, helpLineDivider, helpLineDividerOffset, labelDivider, labelDividerOffset
		##
		##
	def getTikZ(self):
		# initialize ordinate
		try:
			(self.attributes.ordinateMin,
			self.attributes.ordinateMax,
			self.attributes.ordinateDomain,
			self.attributes.ordinateLength,
			self.attributes.ordinateRatio) = TikZCoordinateSystem.initializeDimension(
		            self.attributes.ordinateMin,
		            self.attributes.ordinateMax,
		            self.attributes.ordinateDomain,
		            self.attributes.ordinateLength,
		            self.attributes.ordinateRatio,
		            forcedMin = self.attributes.ordinateForcedDisplayMin,
		            forcedMax = self.attributes.ordinateForcedDisplayMax,
		        )
		except Exception as e:
			logging.error("Initializing ordinate failed: " + e.message)
			raise e
		# initialize abscissa
		try:
			(self.attributes.abscissaMin,
			self.attributes.abscissaMax,
			self.attributes.abscissaDomain,
			self.attributes.abscissaLength,
			self.attributes.abscissaRatio) = TikZCoordinateSystem.initializeDimension(
		            self.attributes.abscissaMin, self.attributes.abscissaMax, self.attributes.abscissaDomain, self.attributes.abscissaLength, self.attributes.abscissaRatio
		        )
		except Exception as e:
			logging.error("Initializing abscissa failed: " + e.message)
			raise e
		# initialize ordinate decoration
		(
		self.attributes.ordinateTickDelta,
		self.attributes.ordinateTickAnchorValue,
		self.attributes.ordinateHelpLineDivider,
		self.attributes.ordinateHelpLineDividerOffset,
		self.attributes.ordinateTickLabelDivider,
		self.attributes.ordinateTickLabelDividerOffset
		) = self.initializeAxisDecoration(
			tickDelta = self.attributes.ordinateTickDelta,
			tickAnchorValue = self.attributes.ordinateTickAnchorValue,
			helpLineDivider = self.attributes.ordinateHelpLineDivider,
			helpLineDividerOffset = self.attributes.ordinateHelpLineDividerOffset,
			labelDivider = self.attributes.ordinateTickLabelDivider,
			labelDividerOffset = self.attributes.ordinateTickLabelDividerOffset,
			minValue = self.attributes.ordinateMin,
			maxValue = self.attributes.ordinateMax,
			domain = self.attributes.ordinateDomain,
			length = self.attributes.ordinateLength,
			axisIsHorizontal = self.attributes.abscissaDirection == 'top' or self.attributes.abscissaDirection == 'down'
		)
		if self.attributes.ordinateTickDelta < 1 and self.attributes.forceWholeNumberedOrdinateTickDelta:
			self.attributes.ordinateTickDelta = 1
		# initialize abscissa decoration
		(
		self.attributes.abscissaTickDelta,
		self.attributes.abscissaTickAnchorValue,
		self.attributes.abscissaHelpLineDivider,
		self.attributes.abscissaHelpLineDividerOffset,
		self.attributes.abscissaTickLabelDivider,
		self.attributes.abscissaTickLabelDividerOffset
		) = self.initializeAxisDecoration(
			tickDelta = self.attributes.abscissaTickDelta,
			tickAnchorValue = self.attributes.abscissaTickAnchorValue,
			helpLineDivider = self.attributes.abscissaHelpLineDivider,
			helpLineDividerOffset = self.attributes.abscissaHelpLineDividerOffset,
			labelDivider = self.attributes.abscissaTickLabelDivider,
			labelDividerOffset = self.attributes.abscissaTickLabelDividerOffset,
			minValue = self.attributes.abscissaMin,
			maxValue = self.attributes.abscissaMax,
			domain = self.attributes.abscissaDomain,
			length = self.attributes.abscissaLength,
			axisIsHorizontal = self.attributes.abscissaDirection == 'left' or self.attributes.abscissaDirection == 'right'
		)
		if self.attributes.abscissaTickDelta < 1 and self.attributes.forceWholeNumberedAbscissaTickDelta:
			self.attributes.abscissaTickDelta = 1
		# initialize tick skips
		if self.attributes.skipOrdinateTickLabelOnAbscissa == None:
			if self.attributes.ordinateValue >  self.attributes.abscissaMin:
				self.attributes.skipOrdinateTickLabelOnAbscissa = True
			else:
				self.attributes.skipOrdinateTickLabelOnAbscissa = False
		if self.attributes.skipAbscissaTickLabelOnOrdinate == None:
			if self.attributes.abscissaValue >  self.attributes.ordinateMin:
				self.attributes.skipAbscissaTickLabelOnOrdinate = True
			else:
				self.attributes.skipAbscissaTickLabelOnOrdinate = False
		# initialize the array that will be used to add output strings; the fields will be
		#  concatenated (separated by \n) at the end of this method to form the resulting TikZ string  
		result=[]
		#body
		if self.getStyle("bodyStyle") != None:
			result.append(
				"\\path[{bodyStyle}] {start} rectangle {end};".format(**{
					'start':self.tcoord((self.attributes.abscissaMin,self.attributes.ordinateMin)),
					'end':self.tcoord((self.attributes.abscissaMax,self.attributes.ordinateMax)),
					'bodyStyle':self.getStyle("bodyStyle")
				}))
		# body hook
		if self.attributes.csBodyHook:
			result.append(self.attributes.csBodyHook(self))
		#ORDINATE
		if (self.attributes.ordinateValue >= self.attributes.abscissaMin) and (self.attributes.ordinateValue <= self.attributes.abscissaMax):
			self.ordinateDefined = True
			#ordinate coordinates
			result.append("\\path[coordinate]\n\t{ordinatestart} coordinate (ordinateStart)\n\t{ordinateend} coordinate (ordinateEnd);".format(**{
					'ordinatestart':self.tcoord((self.attributes.ordinateValue,self.attributes.ordinateMin)),
					'ordinateend':self.tcoord((self.attributes.ordinateValue,self.attributes.ordinateMax))
				}))
			# help lines, ticks, tick labels
			result.append(self.getAxisString(
				minValue = self.attributes.ordinateMin,
				maxValue = self.attributes.ordinateMax,
				axisValue = self.attributes.ordinateValue,
				orthogonalMinValue = self.attributes.abscissaMin,
				orthogonalMaxValue = self.attributes.abscissaMax,
				orthogonalAxisValue = self.attributes.abscissaValue,
				tickDelta = self.attributes.ordinateTickDelta,
				tickAnchorValue = self.attributes.ordinateTickAnchorValue,
				tickStyle = self.attributes.ordinateTickStyle,
				helpLineStyle = self.attributes.ordinateHelpLineStyle,
				helpLineDivider = self.attributes.ordinateHelpLineDivider,
				helpLineDividerOffset = self.attributes.ordinateHelpLineDividerOffset,
				tickLabelStyle = self.getStyle('ordinateTickLabelStyle'),
				tickLabelString = self.attributes.ordinateTickLabelString,
				tickLabelDivider = self.attributes.ordinateTickLabelDivider,
				tickLabelDividerOffset = self.attributes.ordinateTickLabelDividerOffset,
				skipTickOnOrthogonalAxis = self.attributes.skipOrdinateTickOnAbscissa,
				skipTickLabelOnOrthogonalAxis = self.attributes.skipOrdinateTickLabelOnAbscissa,
				skipHelpLineOnOrthogonalAxis = self.attributes.skipOrdinateHelpLineOnAbscissa,
				tickCoordToNegativeVector = self.transformTikZVector(-self.attributes.ordinateTickNegativeLength,0),
				tickNegativeToPositiveVector = self.transformTikZVector(self.attributes.ordinateTickNegativeLength + self.attributes.ordinateTickPositiveLength,0),
				coordinateMapFunction = (lambda a,x: (x,a))
			))
			#ordinate line
			if self.attributes.ordinateStyle != None:
				result.append("\path [{ordinateStyle}] (ordinateStart) -- (ordinateEnd);".format(ordinateStyle=self.getStyle('ordinateStyle')))
			#ordinate jut and its coordinate
			if self.attributes.ordinateJutStyle != None:
				vector=self.transformCoord(0,self.attributes.ordinateJutLength)
				jutend=self.coord((self.attributes.ordinateValue,self.attributes.ordinateMax))+vector
				result.append("\\path[coordinate] {jutend} coordinate (ordinateJut);".format(jutend=jutend))
				result.append("\\path[{ordinateJutStyle}] (ordinateEnd) -- (ordinateJut);".format(ordinateJutStyle=self.getStyle('ordinateJutStyle')))
			#outer ordinate label
			if self.attributes.outerOrdinateLabelString != "" and self.attributes.outerOrdinateLabelStyle != None:
				result.append("\t\\path (ordinateEnd) node[{outerOrdinateLabelStyle}] {{{label}}};".format(**{
					'outerOrdinateLabelStyle':self.getStyle('outerOrdinateLabelStyle'),
					'label':self.attributes.outerOrdinateLabelString.format(**self.attributeDict)
				}))
			#alongside ordinate label
			if self.attributes.alongsideOrdinateLabelString != "" and self.attributes.alongsideOrdinateLabelStyle != None:
				y=self.attributes.alongsideOrdinateLabelPosition
				if y == None:
					if self.attributes.abscissaValue <= self.attributes.ordinateMin:
						y=self.attributes.ordinateMin + self.attributes.ordinateDomain * 3 / 5
					else:
						y=((self.attributes.ordinateMin + (self.attributes.abscissaValue - self.attributes.ordinateMin) / 3) if abs(self.attributes.abscissaValue-self.attributes.ordinateMin) > abs(self.attributes.abscissaValue - self.attributes.ordinateMax) else self.attributes.abscissaValue + (self.attributes.ordinateMax - self.attributes.abscissaValue)*2 / 3)
				result.append("\t\\path {c} node[{alongsideOrdinateLabelStyle}] {{{label}}};".format(**{
					'c':self.tcoord((self.attributes.ordinateValue,y)),
					'alongsideOrdinateLabelStyle':self.getStyle('alongsideOrdinateLabelStyle'),
					'label':self.attributes.alongsideOrdinateLabelString.format(**self.attributeDict)
				}))
		#ORDINATE＿END
		#ABSCISSA
		if (self.attributes.abscissaValue >= self.attributes.ordinateMin) and (self.attributes.abscissaValue <= self.attributes.ordinateMax):
			self.abscissaDefined = True
			#abscissa coordinates
			result.append("\\path[coordinate]\n\t{abscissastart} coordinate (abscissaStart)\n\t{abscissaend} coordinate (abscissaEnd)\n;".format(**{
					'abscissastart':self.tcoord((self.attributes.abscissaMin,self.attributes.abscissaValue)),
					'abscissaend':self.tcoord((self.attributes.abscissaMax,self.attributes.abscissaValue))
				}))
			# help lines, ticks, tick labels
			result.append(self.getAxisString(
				minValue = self.attributes.abscissaMin,
				maxValue = self.attributes.abscissaMax,
				axisValue = self.attributes.abscissaValue,
				orthogonalMinValue = self.attributes.ordinateMin,
				orthogonalMaxValue = self.attributes.ordinateMax,
				orthogonalAxisValue = self.attributes.ordinateValue,
				tickDelta = self.attributes.abscissaTickDelta,
				tickAnchorValue = self.attributes.abscissaTickAnchorValue,
				tickStyle = self.attributes.abscissaTickStyle,
				helpLineStyle = self.attributes.abscissaHelpLineStyle,
				helpLineDivider = self.attributes.abscissaHelpLineDivider,
				helpLineDividerOffset = self.attributes.abscissaHelpLineDividerOffset,
				tickLabelStyle = self.getStyle('abscissaTickLabelStyle'),
				tickLabelString = self.attributes.abscissaTickLabelString,
				tickLabelDivider = self.attributes.abscissaTickLabelDivider,
				tickLabelDividerOffset = self.attributes.abscissaTickLabelDividerOffset,
				skipTickOnOrthogonalAxis = self.attributes.skipAbscissaTickOnOrdinate,
				skipTickLabelOnOrthogonalAxis = self.attributes.skipAbscissaTickLabelOnOrdinate,
				skipHelpLineOnOrthogonalAxis = self.attributes.skipAbscissaHelpLineOnOrdinate,
				tickCoordToNegativeVector = self.transformTikZVector(0,-self.attributes.abscissaTickNegativeLength),
				tickNegativeToPositiveVector = self.transformTikZVector(0,self.attributes.abscissaTickNegativeLength + self.attributes.abscissaTickPositiveLength),
				coordinateMapFunction = (lambda a,x: (a,x))
			))
			#abscissa line
			if self.attributes.abscissaStyle != None:
				result.append("\path [{abscissaStyle}] (abscissaStart) -- (abscissaEnd);".format(abscissaStyle=self.getStyle('abscissaStyle')))		
			#abscissa jut and its coordinate
			if self.attributes.abscissaJutStyle != None:
				vector=self.transformCoord(self.attributes.abscissaJutLength,0)
				jutend=self.coord((self.attributes.abscissaMax,self.attributes.abscissaValue))+vector
				result.append("\\path[coordinate] {jutend} coordinate (abscissaJut);".format(jutend=jutend))
				result.append("\\path[{abscissaJutStyle}] (abscissaEnd) -- (abscissaJut);".format(abscissaJutStyle=self.getStyle('abscissaJutStyle')))
			#outer abscissa label
			if self.attributes.outerAbscissaLabelString != "" and self.attributes.outerAbscissaLabelStyle != None:
				result.append("\t\\path (abscissaEnd) node[{outerAbscissaLabelStyle}] {{{label}}};".format(**{
					'outerAbscissaLabelStyle':self.getStyle('outerAbscissaLabelStyle'),
					'label':self.attributes.outerAbscissaLabelString.format(**self.attributeDict)
				}))
			#alongside abscissa label
			if self.attributes.alongsideAbscissaLabelString != "" and self.attributes.alongsideAbscissaLabelStyle != None:
				x=self.attributes.alongsideAbscissaLabelPosition
				if x == None:
					if self.attributes.ordinateValue <= self.attributes.abscissaMin:
						x=self.attributes.abscissaMin + self.attributes.abscissaDomain * 3/5
					else:
						x=((self.attributes.abscissaMin + (self.attributes.ordinateValue - self.attributes.abscissaMin) / 3) if abs(self.attributes.ordinateValue-self.attributes.abscissaMin) > abs(self.attributes.ordinateValue - self.attributes.abscissaMax) else self.attributes.ordinateValue + (self.attributes.abscissaMax - self.attributes.ordinateValue) *2/3)
				result.append("\t\\path {c} node[{alongsideAbscissaLabelStyle}] {{{label}}};".format(**{
					'c':self.tcoord((x,self.attributes.abscissaValue)),
					'alongsideAbscissaLabelStyle':self.getStyle('alongsideAbscissaLabelStyle'),
					'label':self.attributes.alongsideAbscissaLabelString.format(**self.attributeDict)
				}))
		#ABSCISSA＿END
		return "\n".join(result)
		##
		##
	def drawLine(self,start,end,style):
		return "\\path[{style}] {start} -- {end};".format(style=style,start=self.tcoord(start),end=self.tcoord(end))
		##
		##
	def drawRectangle(self,start,end,style):
		return "\\path[{style}] {start} rectangle {end};".format(style=style,start=self.tcoord(start),end=self.tcoord(end))
		##
		##
	def transformCoord(self,x,y):
		if self.attributes.abscissaDirection == 'right':
			return Coord([x,y if not self.attributes.ordinateInversion else -y])
		if self.attributes.abscissaDirection == 'left':
			return Coord([-x,y if not self.attributes.ordinateInversion else -y])
		if self.attributes.abscissaDirection == 'top':
			return Coord([y if not self.attributes.ordinateInversion else -y,x])
		if self.attributes.abscissaDirection == 'down':
			return Coord([y if not self.attributes.ordinateInversion else -y,-x])
		raise ziktRenderException( "unknown abscissa direction")
		##
		##
	def render(self,table):
		return self.getTikZ()
		##
		##
#	def configureOrdinateByAxisHeuristic(self, heuristicClass):
#		heuristic = heuristicClass(
#			minValue=self.attributes.minOrdinateValue,
#			maxValue=self.attributes.maxOrdinateValue,
#			length=self.attributes.ordinateLength,
#			attributesDict = self.attributes.getDict()
#		)
	def configureOrdinateByAxisHeuristic(self, heuristic):
		if self.ordinateSpecificationState() < 0:
			self.attributes.ordinateMin = heuristic.getMinValue()
			self.attributes.ordinateMax = heuristic. getMaxValue()
			self.attributes.ordinateDomain = None
		if self.attributes.ordinateTickDelta == None:
			self.attributes.ordinateTickDelta = heuristic. getTickValueDistance()
		
		
		#sys.stderr.write("CONFIGURE min: %s   max: %s   domain: %s\n" %(str(self.attributes.ordinateMin), str(self.attributes.ordinateMax), str(self.attributes.ordinateDomain)))
		#this.attributes.??? = heuristic. getTickValueOffset()
		#this.attributes.ordinateMin = heuristic. getTickLabelValueDistance()
		#this.attributes.ordinateMin = heuristic. getTickLabelValueOffset()
if __name__ == "__main__":
	c =  TikZCoordinateSystem(
		preset='simple',
		ordinateLength=2,
		abscissaLength=12,
		ordinateMin=-1,
		abscissaMin=-1,
		ordinateMax=1,
		abscissaMax=1,
		)
	print c.render(FloatTable())

#c = TikZCoordinateSystem(preset='simple')
#c.render(FloatTable())

#print c.getTikZ()
