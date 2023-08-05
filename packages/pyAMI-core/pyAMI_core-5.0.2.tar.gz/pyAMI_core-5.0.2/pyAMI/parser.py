# -*- coding: utf-8 -*-
from __future__ import (division, print_function, unicode_literals)
#############################################################################
# Author  : Jerome ODIER, Jerome FULACHIER, Fabian LAMBERT, Solveig ALBRAND
#
# Email   : jerome.odier@lpsc.in2p3.fr
#           jerome.fulachier@lpsc.in2p3.fr
#           fabian.lambert@lpsc.in2p3.fr
#           solveig.albrand@lpsc.in2p3.fr
#
# Version : 5.X.X (2014)
#
#############################################################################

import pyAMI.utils, pyAMI.exception, pyAMI.my_tokenizer

#############################################################################

shell_barrier = False

#############################################################################

def _shell_barrier(arg):

	if shell_barrier:

		idx = arg.find('=')

		if idx != -1:
			left_part = arg[: idx + 0].strip()
			right_part = arg[idx + 1: ].strip()

			if len(right_part) >= 2:

				if (right_part[0] != '\'' or right_part[-1] != '\'')\
				   and                                              \
				   (right_part[0] != '\"' or right_part[-1] != '\"'):

					arg = '%s="%s"' % (left_part, right_part)

	return arg

#############################################################################

DASH = 0
EQUAL = 1
STRING = 2
ERR = 9

CMD = 0
ARG = 1
VAL = 2
NIL = 9

#############################################################################

TRANSITIONS = [
	#	DASH	EQUAL	STRING  #
	[	ERR,	ERR,	  1	],
	[	  2,	ERR,	  3	],
	[	  2,	ERR,	  3	],
	[	  2,	  4,	  3	],
	[	ERR,	ERR,	  1	],
]

OPERATIONS = [
	#	DASH	EQUAL	STRING  #
	[	NIL,	NIL,	CMD	],
	[	NIL,	NIL,	ARG	],
	[	NIL,	NIL,	ARG	],
	[	NIL,	NIL,	ARG	],
	[	NIL,	NIL,	VAL	],
]

FINAL = [1, 3]

#############################################################################

def parse(args):
	#####################################################################
	# TOKENIZE COMMAND                                                  #
	#####################################################################

	tokens = []

	for arg in pyAMI.utils.to_array(args):

		TOKENS, _ = pyAMI.my_tokenizer.tokenize(
			_shell_barrier(arg),
			spaces = [' ', '\t', '\n'],
			kwords = ['-', '/', '='],
			quotes = ['\'', '\"'],
			escape = '\\'
		)

		tokens.extend(TOKENS)

	#####################################################################
	# GENERATE COMMAND                                                  #
	#####################################################################

	if not tokens:
		return ''

	#####################################################################

	idx = 0

	cur_state = 0
	new_state = 0

	result = ''

	for token in tokens:
		#############################################################
		# LEXER                                                     #
		#############################################################

		if   token == '-'\
		     or          \
		     token == '/':
			idx = DASH

		elif token == '=':
			idx = EQUAL

		else:
			idx = STRING

			if token[0] == '\''\
			   or              \
			   token[0] == '\"':
				token = token[+1: -1]

		#############################################################
		# PARSER                                                    #
		#############################################################

		new_state = TRANSITIONS[cur_state][idx]
		operation = OPERATIONS[cur_state][idx]

		if new_state == ERR:
			raise pyAMI.exception.Error('syntax error, line `1`, unexpected token `%s`' % token)

		if   operation == CMD:

			if token.startswith('AMI'):
				result += '%s' % token[3: ]
			else:
				result += '%s' % token[0: ]

		elif operation == ARG:
			result += ' -%s' % token

		elif operation == VAL:
			result += '="%s"' % token

		cur_state = new_state

	#####################################################################

	if not cur_state in FINAL:
		raise pyAMI.exception.Error('syntax error, line `1`, truncated command')

	#####################################################################

	return result

#############################################################################
