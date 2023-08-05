# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

import unittest
from tables import Table, FloatTable, StringTable
from helper import ziktTableException

def getBasicTable():
	table = Table()
	table.addRow(["","A", "B", "C", "D", "E", "F"])
	table.addRow(["α","1", "2", "3", "4", "5"])
	table.addRow(["β","11", "12", "13", "14", "15", "16"])
	table.addRow(["γ","21", "22", "23"])
	return table

class TableTests(unittest.TestCase):
	
	def test_getColCount(self):
		table = getBasicTable()
		self.failUnlessEqual(table.getColCount(),6)
		
	def test_getRowCount(self):
		table = getBasicTable()
		self.failUnlessEqual(table.getRowCount(),3)
		
	def test_getMinRowLength(self):
		table = getBasicTable()
		self.failUnlessEqual(table.getMinRowLength(), 3)
		
	def test_getMaxRowLength(self):
		table = getBasicTable()
		self.failUnlessEqual(table.getMaxRowLength(), 6)
		
	def test_getCell(self):
		table = getBasicTable()
		self.failUnlessEqual(table.getCell(3, 0), '4')
		
	def test_setCell_cell_exists(self):
		table = getBasicTable()
		self.assertEqual(table.getCell(2, 2), '23')
		table.setCell(2, 2, "Wurst")
		self.assertEqual(table.getCell(2, 2), 'Wurst')
		
	def test_setCell_cell_does_not_exist(self):
		table = getBasicTable()
		table.setCell(4, 2, "Wurst")
		self.assertEqual(table.getCell(3, 2), None)
		self.assertEqual(table.getCell(4, 2), 'Wurst')	
		
	def test_getCell_exceptionOnColOutOfRange(self):
		table = getBasicTable()
		self.failUnlessRaises(ziktTableException, table.getCell, 6, 0)
		
	def test_getCell_exceptionOnRowOutOfRange(self):
		table = getBasicTable()
		self.failUnlessRaises(ziktTableException, table.getCell, 0, 4)
		
	def test_swap(self):
		table = getBasicTable()
		self.failUnlessEqual(table.getCell(1, 2), '22')
		self.failUnlessEqual(table.getCell(2, 1), '13')
		table.swap()
		self.failUnlessEqual(table.getCell(1, 2), '13')
		self.failUnlessEqual(table.getCell(2, 1), '22')
		
	def test_unfoldRow(self):
		row = ["header","a:1,b:2","c:3,d:4"]
		table = StringTable()
		table.hasColHeader=False
		table.addRow(row)
		table.unfoldRow(rowIndex = 0, fillValue="0",line_delimiter=',',tuple_delimiter=':')
		#
		self.assertEqual(table.getRowCount(),4)
		self.assertEqual(table.getRowHeader(0),"a")
		self.assertEqual(table.getRowHeader(1),"b")
		self.assertEqual(table.getRowHeader(2),"c")
		self.assertEqual(table.getRowHeader(3),"d")
		self.assertEqual(table.getCell(0,0),"1")
		self.assertEqual(table.getCell(0,1),"2")
		self.assertEqual(table.getCell(0,2),"0")
		self.assertEqual(table.getCell(0,3),"0")
		self.assertEqual(table.getCell(1,0),"0")
		self.assertEqual(table.getCell(1,1),"0")
		self.assertEqual(table.getCell(1,2),"3")
		self.assertEqual(table.getCell(1,3),"4")


class FloatTableTests(unittest.TestCase):
	
	def test_instantiation(self):
		table = getBasicTable()
		table.addRow(["δ","3", "-2", "3.5", "3"])
		floatTable=FloatTable(table)
		self.failUnlessEqual(floatTable.getCell(2, 3),3.5)
		self.assertEqual(len(table.rowHeader), 4)
		
	def test_instantiation_exceptionOnConvert(self):
		table = getBasicTable()
		table.addRow(["3", "a", "3.0"])
		self.failUnlessRaises(ziktTableException, FloatTable, table)
	
	def test_getColCount(self):
		table = FloatTable(getBasicTable())
		self.failUnlessEqual(table.getColCount(),6)
		
	def test_getRowCount(self):
		table = FloatTable(getBasicTable())
		self.failUnlessEqual(table.getRowCount(),3)
		
	def test_getMinRowLength(self):
		table = FloatTable(getBasicTable())
		self.failUnlessEqual(table.getMinRowLength(), 3)
		
	def test_getMaxRowLength(self):
		table = FloatTable(getBasicTable())
		self.failUnlessEqual(table.getMaxRowLength(), 6)
		
	def test_getCell(self):
		table = FloatTable(getBasicTable())
		self.failUnlessEqual(table.getCell(3, 0), 4)
		
	def test_getMinMax(self):
		table = Table()
		table.addRow(['', 'A', 'B', 'C'])
		table.addRow([u'α', 3, 4, 5])
		table.addRow([u'β', 3, 7, 5])
		floatTable = FloatTable(table)
		minV, maxV = floatTable.getMinMax()
		self.failUnlessEqual(minV,3)
		self.failUnlessEqual(maxV,7)
		floatTable.addRow([u'γ', 30, 7, -5])
		minV, maxV = floatTable.getMinMax()
		self.failUnlessEqual(minV,-5)
		self.failUnlessEqual(maxV,30)
		
	def test_getMinMaxOfCol(self):
		table = FloatTable(getBasicTable())
		minV, maxV = table.getMinMaxOfCol(1)
		self.failUnlessEqual(minV, 2)
		self.failUnlessEqual(maxV, 22)
		
	def test_getMinMaxIndicesOfCol(self):
		table = FloatTable(getBasicTable())
		minV, maxV = table.getMinMaxIndicesOfCol(1)
		self.failUnlessEqual(minV, 0)
		self.failUnlessEqual(maxV, 2)
		
	def test_getMinMaxColSum(self):
		table = FloatTable(getBasicTable())
		minV, maxV = table.getMinMaxColSum()
		self.assertEqual(minV, 16)
		self.assertEqual(maxV, 39)
		
	def test_allPositive_positive(self):
		table = FloatTable(getBasicTable())
		self.assertTrue(table.allPositive())
		
	def test_allPositive_negative(self):
		table = FloatTable(getBasicTable())
		table.addRow(["Δ",3,4,-6,20])
		self.assertFalse(table.allPositive())
		
	def test_allPositiveExceptFirstRow_positive1(self):
		table = FloatTable(getBasicTable())
		self.assertTrue(table.allPositiveExceptFirstRow())
		
	def test_allPositiveExceptFirstRow_positive2(self):
		table = FloatTable(getBasicTable())
		table.rows.insert(0, ["Δ",2,-2,20])
		self.assertTrue(table.allPositiveExceptFirstRow())
		
	def test_allPositiveExceptFirstRow_negative(self):
		table = FloatTable(getBasicTable())
		table.addRow(["Δ",3,4,-6,20])
		self.assertFalse(table.allPositiveExceptFirstRow())
	
	def test_getStacked(self):
		table = FloatTable(getBasicTable())
		stackedTable = table.getStacked(onTopOfZero = True)
		self.assertEqual(stackedTable.getCol(0)[0], 0)
		self.assertEqual(stackedTable.getCol(0)[1], 1)
		self.assertEqual(stackedTable.getCol(0)[2], 12)
		self.assertEqual(stackedTable.getCol(0)[3], 33)
		
#	def test_getStackMinMax(self):
#		raise "mööp"
#	
#	def test_getStackMinMaxOfCol(self):
#		raise "mööp"

if __name__ == "__main__": 
	unittest.main()
