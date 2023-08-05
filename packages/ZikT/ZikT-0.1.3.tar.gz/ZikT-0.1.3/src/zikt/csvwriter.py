# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

import sys
import csv

class CSV:
	def __init__(self,delimiter=None,quotechar=None):
		self.delimiter = delimiter
		self.quotechar = quotechar
			
	def render(self,table):
		array = table.getTableArray()
		writer = csv.writer(sys.stdout)
		for item in array:
			writer.writerow(item)
		