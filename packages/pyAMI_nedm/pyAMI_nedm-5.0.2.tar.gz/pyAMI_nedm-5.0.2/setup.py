#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################################
# Author  : Jerome ODIER, Jerome FULACHIER, Fabian LAMBERT, Solveig ALBRAND
#
# Email   : jerome.odier@lpsc.in2p3.fr
#           jerome.fulachier@lpsc.in2p3.fr
#           fabian.lambert@lpsc.in2p3.fr
#           solveig.albrand@lpsc.in2p3.fr
#
#############################################################################

import os, pyAMI_nedm.config

#############################################################################

if __name__ == '__main__':
	#####################################################################

	try:
		from setuptools import setup

	except ImportError:
		from distutils.core import setup

	#####################################################################

	scripts = [
		'ami_nedm',
	]

	if os.name == 'nt':
		scripts.append('ami_nedm.bat')

	#####################################################################

	setup(
		name = 'pyAMI_nedm',
		version = pyAMI_nedm.config.version.encode('utf-8'),
		author = 'Jerome Odier',
		author_email = 'jerome.odier@cern.ch',
		description = 'Python ATLAS Metadata Interface (pyAMI) for nEDM',
		url = 'http://ami.in2p3.fr/',
		license = 'CeCILL-C',
		packages = ['pyAMI_nedm'],
		package_data = {'': ['README', 'CHANGELOG', '*.txt'], 'pyAMI_nedm': ['*.txt']},
		scripts = scripts,
		install_requires = ['pyAMI_core'],
		platforms = 'any',
		zip_safe = False
	)

#############################################################################
