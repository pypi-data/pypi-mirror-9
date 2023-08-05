#!/usr/bin/env python
# -*- coding: utf-8 -*-
#head#
'''
@author: Daniel Llin Ferrero
'''


from distutils.core import setup

try:
	with open ("about", "r") as aboutfile:
		about = aboutfile.read()
except:
	about = ""

setup(
	name='ZikT',
	version='0.1.3',
	description='Python lib for generating TikZ charts from table data',
	author='Daniel Llin Ferrero',
	author_email='texnh@llin.info',
	url='https://pypi.python.org/pypi/zikt/',
	package_dir={'': 'src'},
	packages=['zikt'],
	package_data={'zikt': ['doc/zikt.pdf','latex/zikt.sty']},
	scripts=['scripts/zikt'],
	requires=['unicodecsv'],
	license='LGPL 3  (http://www.gnu.org/licenses/lgpl-3.0)',
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'Environment :: Console',
		'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
	],
	long_description = about
)
