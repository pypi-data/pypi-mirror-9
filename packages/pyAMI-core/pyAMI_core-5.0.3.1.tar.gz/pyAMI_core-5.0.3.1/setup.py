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

import os, sys, pyAMI.config

#############################################################################

if __name__ == '__main__':
	#####################################################################

	try:
		from setuptools import setup

	except ImportError:
		from distutils.core import setup

	#####################################################################

	scripts = ['ami']

	if os.name == 'nt':
		scripts.append('ami.bat')

	#####################################################################

	setup(
		name = 'pyAMI_core',
		version = pyAMI.config.version.encode('utf-8'),
		author = pyAMI.config.author_names.encode('utf-8'),
		author_email = pyAMI.config.author_emails.encode('utf-8'),
		description = 'Python ATLAS Metadata Interface (pyAMI)',
		url = 'http://ami.in2p3.fr/',
		license = 'CeCILL-C',
		packages = ['pyAMI'],
		package_data = {'': ['README', 'CHANGELOG', '*.txt'], 'pyAMI': ['*.txt']},
		scripts = scripts,
		install_requires = ['argparse', 'argparseplus', 'tiny_xslt'],
		platforms = 'any',
		zip_safe = False
	)

	#####################################################################

	if 'install' in sys.argv:
		print(pyAMI.config.banner)
		print(pyAMI.config.authors)
		print('')

#############################################################################
