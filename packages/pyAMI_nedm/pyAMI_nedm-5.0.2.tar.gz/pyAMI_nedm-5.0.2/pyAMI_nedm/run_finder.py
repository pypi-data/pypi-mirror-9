# -*- coding: utf-8 -*-
from __future__ import (division, print_function, unicode_literals)
#############################################################################
# Author  : Jerome ODIER
#
# Email   : jerome.odier@cern.ch
#           jerome.odier@lpsc.in2p3.fr
#
# Version : 1.X.X for pyAMI_nedm (2013-2014)
#
#############################################################################

import os

#############################################################################

def isInteger(s):

	try:
		int(s)

		return True

	except ValueError:
		return False

#############################################################################

def runs_finder(path, timestamp = 0):
	result = {}

	for dir_name, dir_names, file_names in os.walk(path):

		for file_name in file_names:

			root, ext = os.path.splitext(file_name)

			tokens = root.replace('_', '-').split('-')

			if len(tokens) >= 2 and isInteger(tokens[0]) and ext == '.gz':

				if not result.has_key(tokens[0]):
					result[tokens[0]] = []

				FILE_NAME = dir_name + os.path.sep + file_name

				if os.stat(FILE_NAME).st_mtime >= timestamp:
					result[tokens[0]].append(FILE_NAME)

	return result

#############################################################################
