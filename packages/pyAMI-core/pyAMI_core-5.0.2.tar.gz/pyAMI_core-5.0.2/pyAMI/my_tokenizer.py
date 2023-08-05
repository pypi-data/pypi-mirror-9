# -*- coding: utf-8 -*-
from __future__ import (division, print_function, unicode_literals)
#############################################################################
# Author  : Jerome ODIER
#
# Email   : jerome.odier@cern.ch
#
#############################################################################

import pyAMI.exception

#############################################################################

def tokenize(s, spaces = [], kwords = [], quotes = [], escape = '\\', line = 1):

	result_tokens = []
	result_lines = []

	i = 0x0000
	l = len(s)

	word = ''

	while i < l:
		#############################################################
		# COUNT LINES                                               #
		#############################################################

		if s[i] == '\n':
			line += 1

		#############################################################
		# EAT SAPCES                                                #
		#############################################################

		if s[i] in spaces:

			if word:
				result_tokens.append(word)
				result_lines.append(line)
				word = ''

			i += 1

			continue

		#############################################################
		# EAT KWORDS                                                #
		#############################################################

		found = False

		for kword in kwords:

			if s[i: ].startswith(kword):

				if word:
					result_tokens.append(word)
					result_lines.append(line)
					word = ''

				j = i + len(kword)

				result_tokens.append(s[i: j])
				result_lines.append(line)

				i = j

				found = True
				break

		if found:
			continue

		#############################################################
		# EAT STRINGS                                               #
		#############################################################

		found = False

		for quote in quotes:

			if s[i: ].startswith(quote):

				if word:
					result_tokens.append(word)
					result_lines.append(line)
					word = ''

				j = i + _shift(s[i: ], quote, escape, line)

				result_tokens.append(s[i: j])
				result_lines.append(line)

				i = j

				found = True
				break

		if found:
			continue

		#############################################################
		# EAT REMAINING CHARACTERES                                 #
		#############################################################

		word += s[i]
		i += 1

	#####################################################################

	if word:
		result_tokens.append(word)
		result_lines.append(line)

	return result_tokens, result_lines

#############################################################################

def _shift(s, quote, escape, line):

	l = len(s)
	m = len(quote)
	n = len(escape)

	i = m
	cnt = 0

	while i < l:

		if   s[i: ].startswith(quote):
			i += m
			if cnt % 2 == 0: return i
			cnt = 0
		elif s[i: ].startswith(escape):
			i += n
#			if 0x00001 == 0: return i
			cnt += 1
		else:
			i += 1
#			if 0x00001 == 0: return i
			cnt = 0

	raise pyAMI.exception.Error('syntax error, line `%d`, missing token `%s`' % (line, quote))

#############################################################################
