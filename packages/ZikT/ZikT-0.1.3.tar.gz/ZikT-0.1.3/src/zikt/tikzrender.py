# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''

import re

class TikZRenderer():
	# TODO: low : add comments to TikZ output everywhere
	def printComment(self, prefix,comment,outputlist):
		if self.printComments:
			s = re.sub(ur'^', prefix+u"% ", (u"-" * 80)+u"\n"+comment+u"\n"+(u"-" * 80), flags=re.M)
			outputlist.append(s)