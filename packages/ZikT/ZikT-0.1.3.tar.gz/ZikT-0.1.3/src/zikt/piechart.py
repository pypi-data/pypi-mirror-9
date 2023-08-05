# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

from helper import ziktRenderException, Attributes
from helper import angleIsNorthernHemisphere,angleIsSouthernHemisphere,angleIsWesternHemisphere,angleIsEasternHemisphere
from helper import normalizeAngle
from math import radians, cos
from zikt.tikzrender import TikZRenderer
from zikt.tables_tests import getBasicTable
from zikt.tables import FloatTable


	

class PieChart(TikZRenderer):
	presettings =  {
		'percent': Attributes(
			areaStyles=["sectorone","sectortwo","sectorthree","sectorfour","sectorfive","sectorsix","sectorseven","sectoreight","sectornine","sectorten","sectoreleven","sectortwelve"],
			areaLabelStyles=["sectorlabelone","sectorlabeltwo","sectorlabelthree","sectorlabelfour","sectorlabelfive","sectorlabelsix","sectorlabelseven","sectorlabeleight","sectorlabelnine","sectorlabelten","sectorlabeleleven","sectorlabeltwelve"],
			areaOuterLabelStyles=["sectorlabelone","sectorlabeltwo","sectorlabelthree","sectorlabelfour","sectorlabelfive","sectorlabelsix","sectorlabelseven","sectorlabeleight","sectorlabelnine","sectorlabelten","sectorlabeleleven","sectorlabeltwelve"],
			areaConnectedLabelStyles=["sectorlabelone","sectorlabeltwo","sectorlabelthree","sectorlabelfour","sectorlabelfive","sectorlabelsix","sectorlabelseven","sectorlabeleight","sectorlabelnine","sectorlabelten","sectorlabeleleven","sectorlabeltwelve"],
			areaConnectorStyles=["sectorconnectorone","sectorconnectortwo","sectorconnectorthree","sectorconnectorfour","sectorconnectorfive","sectorconnectorsix","sectorconnectorseven","sectorconnectoreight","sectorconnectornine","sectorconnectorten","sectorconnectoreleven","sectorconnectortwelve"],
			circleStyle="outercircle",
			delimiterStyle="delimiter",
			clockwise=True,
			startangle=180,
			radius=2,
			areaLabelCenterDistance=1.2,
			showValuePercentage = False,
			showValueOutsideThresholdPercentage =100,
			areaOuterLabelStartDistance = 1.7,
			areaOuterLabelKinkDistance = 2.5,
			areaOuterLabelOffsetMin = 1,
			areaOuterLabelOffsetMax = 2.5,
			baseunit='cm',
			additionalSectorStyle="",
			areaLabel='',
			areaLabel_small=u'',
			connectedLabel=u'',
			connectedLabel_small=u'{valuePercentage:.2f}\,\%',
		)
	}
	
	def __init__(self,preset="percent", row=None, printComments=True, **kwargs):
		self.attributes = PieChart.presettings[preset].copy()
		self.attributes.extend(**kwargs)
		self.row = row
		self.printComments = printComments
		self.attributeDict = self.attributes.getDict()
	
	class _Sector:
		def __init__(self,
					renderer,index,value,lastangle,total,ratioIndexOffset,
					areaStyles,
					areaLabelStyles,
					areaOuterLabelStyles,
					areaConnectedLabelStyles,
					areaConnectorStyles,
					title=None,
					):
			self.renderer = renderer
			self.value=value
			self.valueRatio = value / total
			self.valuePercentage = self.valueRatio * 100
			self.width = 360.0 * self.valueRatio
			self.index = index
			self.ratioIndexStart = ratioIndexOffset
			self.ratioIndexCenter = self.ratioIndexStart + self.valueRatio / 2
			self.ratioIndexEnd = self.ratioIndexStart + self.valueRatio
			self.startangle = lastangle
			if renderer.attributes.clockwise:
				self.endangle = self.startangle - self.width
				self.midangle = self.startangle - self.width / 2
			else:
				self.endangle = self.startangle + self.width
				self.midangle = self.startangle + self.width / 2
			self.attributesDict = renderer.attributes.getDict()
			self.attributesDict.update({
				'title' : title,
				'value' : self.value,
				'valueRatio' : self.valueRatio,
				'valuePercentage' : self.valuePercentage,
				'width' : self.width,
				'index' : self.index,
				'startangle' : self.startangle,
				'endangle' : self.endangle,
				'midangle' : self.midangle,
				'ratioIndexStart' : self.ratioIndexStart,
				'ratioIndexCenter' : self.ratioIndexCenter,
				'ratioIndexEnd' : self.ratioIndexEnd,
				'sectorclass':areaStyles[index],
				'arealabelclass':areaLabelStyles[index],
				'areaouterlabelclass':areaOuterLabelStyles[index],
				'connectedlabelclass':areaConnectedLabelStyles[index],
				'connectorclass':areaConnectorStyles[index],
			})
			self.attributesDict.update({
				'arealabel':self.renderer.attributes.areaLabel.format(**self.attributesDict),
				'arealabel_small':self.renderer.attributes.areaLabel_small.format(**self.attributesDict),
				'connectedlabel':self.renderer.attributes.connectedLabel.format(**self.attributesDict),
				'connectedlabel_small':self.renderer.attributes.connectedLabel_small.format(**self.attributesDict),
			})
		def isNorthernHemisphere(self):
			return angleIsNorthernHemisphere(self.midangle)
		def isSouthernHemisphere(self):
			return angleIsSouthernHemisphere(self.midangle)
		def isWesternHemisphere(self):
			return angleIsWesternHemisphere(self.midangle)
		def isEasternHemisphere(self):
			return angleIsEasternHemisphere(self.midangle)
		def getOuterLabelOffset(self):
			d = (self.renderer.attributes.areaOuterLabelOffsetMax - self.renderer.attributes.areaOuterLabelOffsetMin)
			o = self.renderer.attributes.areaOuterLabelOffsetMin
			return (1 - abs(cos(radians(normalizeAngle(self.midangle))))) * d + o
		def getTikzForSectorArea(self):
			#return ("\t\\path[{sectorclass}]").format(**self.attributesDict)
			add = "" if self.renderer.attributes.additionalSectorStyle == "" else "{"+self.renderer.attributes.additionalSectorStyle+"}"
			return ("\\path[{sectorclass},"+add+"] (0,0) -- ({startangle:.7f}:{radius}) arc ({startangle:.7f}:{endangle:.7f}:{radius}) -- cycle;").format(**self.attributesDict)
		def getTikzForSectorDelimiter(self):
			return ("\\path[{delimiterStyle}] (0,0) -- ({startangle:.7f}:{radius});").format(**self.attributesDict)
		def getTikzForSectorLabel(self):
			label = '{arealabel}' if self.valuePercentage >= self.renderer.attributes.showValueOutsideThresholdPercentage else '{arealabel_small}'
			label_class = '{areaouterlabelclass}' if self.valuePercentage >= self.renderer.attributes.showValueOutsideThresholdPercentage else '{arealabelclass}'
			return ("\\path (0,0) ({midangle:.7f}:{areaLabelCenterDistance}) node["+label_class+"] {{"+label+"}};").format(**self.attributesDict)
		def getTikzForConnectedLabel(self):
			label = ('{connectedlabel}' if self.valuePercentage >= self.renderer.attributes.showValueOutsideThresholdPercentage else '{connectedlabel_small}').format(**self.attributesDict)
			if label == "":
				return None
			return ("\\path[{connectorclass}] (0,0) ({midangle:.7f}:{areaOuterLabelStartDistance}) -- ({midangle:.7f}:{areaOuterLabelKinkDistance}) -- ++({endsign}{enddistance},0) node (l) [{connectedlabelclass}, anchor=south {firstanchor}, node distance=0cm] {{{label}}} -- (l.south {secondanchor});").format(**dict(self.attributesDict.items()+{
				'firstanchor':'west' if self.isEasternHemisphere() else 'east',
				'secondanchor':'east' if self.isEasternHemisphere() else 'west',
				'endsign':'+' if self.isEasternHemisphere() else '-',
				'enddistance':str(self.getOuterLabelOffset())+self.renderer.attributes.baseunit,
				'label':label
			}.items()))
			#TODO mach noch das label unter der linie
		
		
	
	def render(self,table):
		result = []
		if self.row == None:
			for row in table:
				result.append(self.renderSingleRow(table,row))
		else:
			result.append(self.renderSingleRow(table,table.rows[self.row]))
		return u'\n'.join(result)
	
	def renderSingleRow(self,table,row):
		# initialize
		total = 0.0
		values = []
		sectors=[]
		titles=[]
		areaStyles=[]
		areaLabelStyles=[]
		areaOuterLabelStyles=[]
		areaConnectedLabelStyles=[]
		areaConnectorStyles=[]
		i=0
		styleOffset = -1
		#TODO nur spezifizierte Datenzellen verwenden und das Überspringen von Null parametrisierbar machen
		for cell in row:
			i += 1
			try:
				f = float(cell)
				if f == 0:
#					styleOffset += 1
					continue
				values.append(f)
				titles.append(table.colHeader[i-1] if table.hasColHeader else None)
				areaStyles.append(self.attributes.areaStyles[(i + styleOffset)%len(self.attributes.areaStyles)])
				areaLabelStyles.append(self.attributes.areaLabelStyles[(i + styleOffset)%len(self.attributes.areaLabelStyles)])
				areaOuterLabelStyles.append(self.attributes.areaOuterLabelStyles[(i + styleOffset)%len(self.attributes.areaOuterLabelStyles)])
				areaConnectedLabelStyles.append(self.attributes.areaConnectedLabelStyles[(i + styleOffset)%len(self.attributes.areaConnectedLabelStyles)])
				areaConnectorStyles.append(self.attributes.areaConnectorStyles[(i + styleOffset)%len(self.attributes.areaConnectorStyles)])
				total += f
			except ValueError, e:
				raise ziktRenderException("Minimum one cell does not contain a valid number. (%s)" % str(e))
		if total == 0:
			raise ziktRenderException("The sum of all values is 0.")
		lastangle = self.attributes.startangle
		ratioIndexOffset = 0
		for i in range(len(values)):
			sectors.append(PieChart._Sector(
				self,
				i,
				values[i],
				lastangle,
				total,
				title = titles[i],
				ratioIndexOffset = ratioIndexOffset,
				areaStyles = areaStyles,
				areaLabelStyles = areaLabelStyles,
				areaOuterLabelStyles = areaOuterLabelStyles,
				areaConnectedLabelStyles = areaConnectedLabelStyles,
				areaConnectorStyles = areaConnectorStyles,
			))
			lastangle = sectors[i].endangle
			ratioIndexOffset = sectors[i].ratioIndexEnd
		self.attributes.extend(total=total, items=len(sectors))
			
		# building output
		result = []
		
		# draw sector areas
		self.printComment(u"\t",u"Drawing the sector areas",result)
		for sector in sectors:
			result.append(u"\t"+sector.getTikzForSectorArea())
			
		# draw sector labels
		for sector in sectors:
			result.append(u"\t"+sector.getTikzForSectorLabel())
		
		# draw sector delimiters
		if self.attributes.delimiterStyle != None:
			for sector in sectors:
				result.append(u"\t"+sector.getTikzForSectorDelimiter())
		
		# draw surrounding circle
		if self.attributes.circleStyle != None:
			result.append(u"\t\\path[{circleStyle}] (0,0) circle ({radius});".format(**self.attributeDict))
		
		# draw connected labels
		for sector in sectors:
			l = sector.getTikzForConnectedLabel()
			if l != None:
				result.append(u"\t"+sector.getTikzForConnectedLabel())
		
		#TODO mach noch das outer label
		
		return u"\n".join(result)

if __name__ == "__main__":
	c =  PieChart(ordinateLength=6,stackmode = True)
	print c.render(table = FloatTable(getBasicTable()))