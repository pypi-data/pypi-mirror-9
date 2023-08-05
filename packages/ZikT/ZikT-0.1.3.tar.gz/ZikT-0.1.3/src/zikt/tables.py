# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''
import unicodecsv as csv
import math
from zikt.helper import ziktTableException
from operator import itemgetter
import sys



class Table:
	"""
	The central class that models a single table. All input data is turned into a table object and all output/renderer classes take their information from an C{Table}-Object.
	
	A table consists of a table body that is an two dimensional array. The outer dimension contains the rows, the inner dimension contains the cells of the concerning row. Furthermore, the table can optionally own row headers and/or column headers.
	"""
		
	def __init__(self):
		self.rowHeader=[]
		self.colHeader=[]
		self.rows=[]
		self.hasRowHeader=True
		self.hasColHeader=True
	
	#TODO: refactor: adding a row should be separated into a two-param function: the row label and the content cell array;... 
	#this could be the function declaration; addRow(self, rowLabel="", row) where row is the appendable, one-dimensional cell collection
	def addRow(self,row):
		if self.colHeader == [] and self.hasColHeader:
			self.colHeader = row if not self.hasRowHeader else row[1:]
		else:
			if self.hasRowHeader:
				self.rowHeader.append(row[0])
				self.rows.append(row[1:])
			else:
				self.rows.append(row)
				
	def insertRow(self,index,rowData,rowHeader=None):
		self.rows.insert(index, rowData)
		if self.hasRowHeader:
			self.rowHeader.insert(index, rowHeader)

	def __iter__(self):
		return iter(self.rows)

	def getMinRowLength(self):
		if len(self.rows) == 0:
			return 0
		else:
			result = len(self.rows[0])
			for row in self.rows:
				if len(row) < result:
					result = len(row)
			return result

	def getMaxRowLength(self):
		if len(self.rows) == 0:
			return 0
		else:
			result = len(self.rows[0])
			for row in self.rows:
				if len(row) > result:
					result = len(row)
			return result
			
	def getColHeader(self,index):
		if not self.hasColHeader: return ""
		return self.colHeader[index]
	
	def getColHeaders(self):
		if not self.hasColHeader: return ""
		return self.colHeader
		
	def getRowHeader(self, index):
		if not self.hasRowHeader: return ""
		return self.rowHeader[index]
	
	def getRowHeaders(self):
		if not self.hasRowHeader: return ""
		return self.rowHeader
		
	def getRowCount(self):
		return len(self.rows)
		
	def getColCount(self):
		return self.getMaxRowLength()
		
	def getCell(self,colIndex,rowIndex):
		if rowIndex > len(self.rows)-1:
			raise ziktTableException("row index out of bounds (asked for index %i but have only %i + 1 rows)" %(rowIndex,  len(self.rows)-1))
		if colIndex > self.getColCount()-1:
			raise ziktTableException("col index out of bounds (asked for index %i but have only %i + 1 columns)" %(colIndex,  self.getColCount()-1))
		r = self.rows[rowIndex]
		if colIndex > len(r)-1:
			return None
		return r[colIndex]
	
	def setCell(self, colIndex, rowIndex, value):
		try:
			row = self.rows[rowIndex]
		except IndexError:
			raise ziktTableException("Row index out of bounds.")
		if colIndex > self.getColCount() - 1:
			raise ziktTableException("Column index out of bounds.")
		fill = colIndex - (len(row)-1)
		if fill > 0:
			appendix = [None for x in range(fill-1)]
			appendix.extend([value])
			row.extend(appendix)
		else:
			row[colIndex] = value
		
		
	def swap(self):
		self.colHeader,self.rowHeader = self.rowHeader,self.colHeader
		self.hasRowHeader, self.hasColHeader = self.hasColHeader, self.hasRowHeader
		newTable=[]
		for i in range(self.getColCount()):
			row=[]
			for j in range(self.getRowCount()):
				row.append(self.getCell(i,j))
			newTable.append(row)
		self.rows = newTable
		
	#DODO: Refactor getRow() so it does not return the header field as first element (if the header field exists, of cause)
	def getRow(self,index):
		return self.rows[index]
	
	def getCol(self, index):
		result=[]
		for i in range(self.getRowCount()):
			c = self.getCell(index, i)
# 			if c != None:
# 				result.append(c)
			result.append(c)
		return result
		
	def getTableArray(self):
		result=[]
		if self.hasColHeader:
			if self.hasRowHeader:
				result.append(['']+self.colHeader)
			else:
				result.append(self.colHeader)
		for i in range(self.getRowCount()):
			if self.hasRowHeader:
				result.append([self.getRowHeader(i)]+self.getRow(i))
			else:
				result.append(self.getRow(i))
		return result

	def unfoldRow(self,rowIndex, fillValue=None,line_delimiter=',',tuple_delimiter=':'):
		row = self.rows.pop(rowIndex)
		if self.hasRowHeader:
			self.rowHeader.pop(rowIndex)
		# extract data
		all_keys = []
		columns_maps = []
		for cell in row:
			column_map = {}
			if cell != None:
				lines = cell.split(line_delimiter)
				for line in lines:
					if line != "":
						value_tuple = line.split(tuple_delimiter)
						if len(value_tuple) != 2:
							raise ziktTableException("Cell content to unfold has a line value that can not be splitted into a key and a value. (%s)"%line)
						key = value_tuple[0]
						value = value_tuple[1]
						if key in column_map:
							raise ziktTableException("Cell content to unfold has an ambiguous key. (%s)"%key)
						column_map[key] = value
						if key not in all_keys:
							all_keys.append(key)
						##
					##
				##
			columns_maps.append(column_map)
		# insert new rows
		for key in reversed(all_keys):
			new_row = []
			if self.hasRowHeader:
				self.rowHeader.insert(rowIndex, key)
			for column_map in columns_maps:
				if key in column_map:
					value = column_map[key]
				else:
					value = fillValue
				new_row.append(value)
			self.rows.insert(rowIndex,new_row)

		

class StringTable(Table):
	def __init__(self,infile=None,delimiter=',', quotechar='"'):
		Table.__init__(self)
		
		if infile!=None:
			self.initByCSV(infile,delimiter=delimiter,quotechar=quotechar)
	
	def initByCSV(self,infile,delimiter=',', quotechar='"'):
		csvReader = csv.reader(infile, delimiter=delimiter, quotechar=quotechar)
		for row in csvReader:
			self.addRow(row)



class FloatTable(Table):
	def __init__(self, table=None, hasRowHeader=None, hasColHeader=None):
		Table.__init__(self)
		if table != None:
			if isinstance(table,Table): 
				self.colHeader = table.colHeader
				self.hasColHeader = table.hasColHeader
				self.hasRowHeader = table.hasRowHeader
				for rowNumber in range(table.getRowCount()):
					newRow=[]
					if table.hasRowHeader:
						newRow.append(table.getRowHeader(rowNumber))
					row = table.getRow(rowNumber)
					for element in row:
						try:
							if element == None:
								newRow.append(None)
							else:
								newRow.append(float(element))
						except ValueError:
							raise ziktTableException("Cell content can not be converted to float value.")
					self.addRow(newRow)
			else:
				if hasColHeader == None:
					self.hasColHeader = True
				else:
					self.hasColHeader = hasColHeader
				if hasRowHeader == None:  
					self.hasRowHeader = False
				else:
					self.hasRowHeader = hasRowHeader
				for row in table:
					self.addRow(row)
				
				
	def setCell(self, colIndex, rowIndex, value):
		if value != None:
			try:
				value = float(value)
			except:
				raise ziktTableException("The value to set is not a float.")
		Table.setCell(self, colIndex, rowIndex, value)
				
	def getMinMax(self):
		rowCount = self.getRowCount()
		colCount = self.getColCount()
		if colCount < 1:
			raise ziktTableException("no data columns in table")
		if rowCount < 1:
			raise ziktTableException("no data rows in table")
		minValue = None
		maxValue = None
		for i in range (0, colCount):
			for j in range (0, rowCount):
				v = self.getCell(i, j)
				#TODO: bug: min/max-Berechnungen berücksichtigen die Nones nicht
				#TODO: hack: lokaler work-around für obigen bug
				if v == None:
					continue
				if minValue == None or (minValue != None and v < minValue):
					minValue = v
				if maxValue == None or (maxValue != None and v > maxValue):
					maxValue = v
		return minValue, maxValue
	
	def getMinMaxOfCol(self, colIndex):
		col = [0 if c == None else c for c in self.getCol(colIndex)]
		if len(col) < 1:
			raise ziktTableException("No data rows in column; No Min/Max calculations possible")
# 		col = self.getCol(colIndex)
		col.sort()
		if len(col) == 0:
			return None
		return col[0],  col[len(col)-1]
		
	def getMinMaxIndicesOfCol(self, colIndex):
		indexValuePairs=[]
		col=self.getCol(colIndex)
		for i in range(len(col)):
			indexValuePairs.append((i, col[i]))
		sortedPairs = sorted(indexValuePairs,  key=itemgetter(1))
		return sortedPairs[0][0],  sortedPairs[len(sortedPairs)-1][0]
	
	def getColSum(self,columnIndex):
		return FloatTable.sumList([0 if c == None else c for c in self.getCol(columnIndex)])
	
	def getColRange(self,columnIndex):
		minV, maxV = self.getMinMaxOfCol(columnIndex)
		return abs(minV-maxV)
	
	def getMinMaxColSum(self):
		if self.getColCount() < 1:
			return None
		firstCol = self.getCol(0)
		firstColSum = FloatTable.sumList(firstCol)
		minV = firstColSum
		maxV = firstColSum
		for i in range(self.getColCount()):
			colsum = self.getColSum(i)
			minV = min(minV,colsum)
			maxV = max(maxV,colsum)
		return minV, maxV
	
	def allPositive(self):
		for i in range(self.getColCount()):
			col = self.getCol(i)
			for c in col:
				if c < 0:
					return False
				##
			##
		return True
	
	def allPositiveExceptFirstRow(self):
		rowCount = self.getRowCount()
		i = 1
		while i < rowCount:
			for c in self.getRow(i):
				if c < 0:
					return False
				##
			i += 1
		return True
	
	def allPositiveInColumn(self,columnIndex,exceptFirst=False):
		column = self.getCol(columnIndex)
		if exceptFirst:
			column = column[1:]
		for cell in column:
			if cell < 0:
				return False
		return True
	
	def getStackedColumn(self,columnIndex):
		if not self.allPositiveInColumn(columnIndex,exceptFirst=True):
			raise ziktTableException("To get a stacked column, all values in the column must be positive.")
		result = []
		column = self.getCol(columnIndex)
		stacksum = 0
		for cell in column:
			stacksum += cell
			result.append(stacksum)
		return result
			
	
	def getStacked(self,onTopOfZero):
		if (onTopOfZero):
			if not self.allPositive():
				raise ziktTableException("When making a stacked table on top of zero, all values in table must be positive.")
			##
		else:
			if not self.allPositiveExceptFirstRow():
				raise ziktTableException("When making a stacked table on top of the first row, all values in the second and following rows must be positive.")
			##
		result = FloatTable(table = self)
		if onTopOfZero:
			firstRow = [0 for x in range(self.getColCount())]
			result.insertRow(0, firstRow, "")
		for columnIndex in range(result.getColCount()):
			stackedColumn = result.getStackedColumn(columnIndex)
			for cellIndex in range(result.getRowCount()):
				result.setCell(columnIndex, cellIndex, stackedColumn[cellIndex] if cellIndex < len(stackedColumn) else None)
			##
		return result
			
		
	@staticmethod
	def sumList(floatlist):
		listsum = 0
		for i in floatlist:
			listsum += i
		return listsum
		
