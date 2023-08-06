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

import re, sys, json, argparse, pyAMI.config, pyAMI.exception

#############################################################################

from pyAMI.config import tables

#############################################################################

def safe_decoded_string(s):
	return s.decode(pyAMI.config.console_encoding, 'replace')

#############################################################################

def safe_encoded_string(s):
	return s.encode(pyAMI.config.console_encoding, 'replace')

#############################################################################

def safestring(s):
	r = safe_encoded_string("%s" % (s))

	if sys.version_info[0] == 3:
		return safe_decoded_string(r)
	else:
		return r

#############################################################################

def safeprint(s, endl = '\n'):
	r = safe_encoded_string("%s%s" % (s, endl))

	if sys.version_info[0] == 3:
		sys.stdout.write(safe_decoded_string(r))
	else:
		sys.stdout.write(r)

#############################################################################

def metaclass(metacls):
	'''Decorator for creating a class with a metaclass.'''

	def wrapper(cls):
		orig_vars = cls.__dict__.copy()

		orig_vars.pop('__dict__', None)
		orig_vars.pop('__weakref__', None)

		slots = orig_vars.get('__slots__')

		for slot in to_array(slots):
				orig_vars.pop(slot)

		return metacls(cls.__name__, cls.__bases__, orig_vars)

	return wrapper

#############################################################################

def to_array(x, sep = None):
	#####################################################################
	# NONE                                                              #
	#####################################################################

	if x is None:
		return [ ]

	#####################################################################
	# LIST OR TUPLE                                                     #
	#####################################################################

	if isinstance(x, (list, tuple)):
		return (x)

	#####################################################################
	# STRING OR UNICODE                                                 #
	#####################################################################

	return x.split(sep) if sep else [x]

#############################################################################

def _resolve_field(table, field):
	#####################################################################
	# RESOLVE TABLE                                                     #
	#####################################################################

	try:
		fields = tables[table]

	except KeyError:
		raise pyAMI.exception.Error('invalid table `%s`, not in [%s]' % (
			table,
			', '.join(['`%s`' % x for x in tables if not x.startswith('@')]),
		))

	#####################################################################
	# RESOLVE FIELD                                                     #
	#####################################################################

	try:
		result = fields[field]

	except KeyError:
		raise pyAMI.exception.Error('invalid field `%s`, not in [%s]' % (
			field,
			', '.join(['`%s`' % x for x in fields if not x.startswith('@')]),
		))

	#####################################################################
	# EXTRACT FIELD NAME                                                #
	#####################################################################

	if not field.startswith('@'):
		result = result.split('=')[0]

	#####################################################################

	return result

#############################################################################

def resolve_field(table, field):
	#####################################################################
	# SPLIT FIELD                                                       #
	#####################################################################

	field_parts = field.split('.')

	if len(field_parts) > 1:

		if len(field_parts) > 2:
			raise pyAMI.exception.Error('invalid field format `%s`' % field)

		new_table = field_parts[0]
		new_field = field_parts[1]

	else:
		new_table = table
		new_field = field

	#####################################################################
	# RESOLVE ENTITY AND FIELD                                          #
	#####################################################################

	name = _resolve_field(new_table, new_field)

	#####################################################################

	if table != new_table:
		return '%s.%s' % (new_table, name)
	else:
		return '%s' % (name)

#############################################################################

def get_entity(table):
	return _resolve_field(table, '@entity')

#############################################################################

def get_project(table):
	return _resolve_field(table, '@project')

#############################################################################

def get_processing_step(table):
	return _resolve_field(table, '@processing_step')

#############################################################################

def get_primary_fields(table):

	try:
		return re.split('\W+', tables[table]['@primary'])

	except KeyError:
		raise pyAMI.exception.Error('no primary field for table `%s`' % table)

#############################################################################

def get_foreign_tables(table):

	try:
		return re.split('\W+', tables[table]['@foreign'])

	except KeyError:
		return (((((((((((((((((((((((((((((([ ]))))))))))))))))))))))))))))))

#############################################################################

def smart_execute(client, table, patterns = None, fields = None, order = None, limit = None, show_archived = False, **kwargs):
	#####################################################################
	# GET TABLE INFO                                                    #
	#####################################################################

	ENTITY = get_entity(table)
	PROJECT = get_project(table)
	PROCESSING_STEP = get_processing_step(table)

	#####################################################################
	# GET PRIMARY AND EXTRA FIELDS                                      #
	#####################################################################

	primary_and_extra_fields = []

	for field in get_primary_fields(table) + to_array(fields, sep = ','):

		if not field in primary_and_extra_fields:
			primary_and_extra_fields.append(field)

	#####################################################################
	# FIELD PART                                                        #
	#####################################################################

	tmp = []

	for field in primary_and_extra_fields:

		resolved_field = resolve_field(table, field)

		tmp.append('%s AS %s' % (resolved_field, field.replace('.', '_')))

	field_part = ', '.join(tmp)

	#####################################################################
	# PATTERN PART                                                      #
	#####################################################################

	tmp = []

	for pattern in to_array(patterns, sep = ','):

		resolved_field = resolve_field(table, primary_and_extra_fields[0])

		if pattern.count('%') > 0:
			tmp.append('%s like \'%s\'' % (resolved_field, pattern))
		else:
			tmp.append('%s = \'%s\'' % (resolved_field, pattern))

	#####################################################################

	if tmp:
		pattern_part = '(' + ' OR '.join(tmp) + ')'
	else:
		pattern_part = '(1 = 1)'

	#####################################################################
	# CONDITION PART                                                    #
	#####################################################################

	tmp = []

	for field, values in list(kwargs.items()):

		if values:
			TMP = []

			resolved_field = resolve_field(table, field)

			for value in to_array(values, sep = ','):

				if value.count('%') > 0:
					TMP.append('%s like \'%s\'' % (resolved_field, value))
				else:
					TMP.append('%s = \'%s\'' % (resolved_field, value))

			if TMP:
				tmp.append('(' + ' OR '.join(TMP) + ')')
			else:
				tmp.append('(1 = 1)')

	#####################################################################

	if tmp:
		condition_part = '(' + ' AND '.join(tmp) + ')'
	else:
		condition_part = '(1 = 1)'

	#####################################################################
	# ORDER PART                                                        #
	#####################################################################

	if order:
		tmp = to_array(order, ',')
	else:
		tmp = primary_and_extra_fields

	order = ' ORDER BY ' + ', '.join([resolve_field(table, field) for field in tmp])

	#####################################################################
	# LIMIT PART                                                        #
	#####################################################################

	if limit:

		if isinstance(limit, (list, tuple)):
			limit = ' LIMIT %i,%i' % (limit[0], limit[1])
		else:
			limit = ' LIMIT 0,%i' % limit

	else:
		limit = ''

	#####################################################################
	# BUILD COMMAND                                                     #
	#####################################################################

	command = [
		'SearchQuery',
		'-entity=%s' % ENTITY,
		'-project=%s' % PROJECT,
		'-processingStep=%s' % PROCESSING_STEP,
		'-glite="SELECT %s WHERE %s AND %s%s%s"' % (field_part, pattern_part, condition_part, order, limit),
	]

	if show_archived:
		command.append('-showArchived=true')

	#####################################################################
	# EXECUTE COMMAND                                                   #
	#####################################################################

	return client.execute(command, format = 'dict_object')

#############################################################################

def smart_execute_parser(parser, table, include_pattern = True):
	#####################################################################
	# CUSTOM PARAMETERS                                                 #
	#####################################################################

	parameters = {}

	for field, descr in tables[table].items():
		if not field.startswith('@'):
			parameters[field.replace('_', '-')] = {
				'foreign': False,
				'descr': [x.strip() for x in descr.split('=')],
			}

	for TABLE in get_foreign_tables(table):

		for field, descr in tables[TABLE].items():
			if not field.startswith('@'):
				parameters[TABLE + '.' + field.replace('_', '-')] = {
					'foreign': True,
					'descr': [x.strip() for x in descr.split('=')],
				}

	#####################################################################
	# DEFAULT PARAMETERS                                                #
	#####################################################################

	FIELDS = ', '.join(sorted(parameters.keys()))

	parser.add_argument('-l', '--limit', help = 'limit number of results', type = int, default = None)
	parser.add_argument('-o', '--order', help = 'order by fields (comma separated parameter, possible fields: %s)' % FIELDS, type = str, default = None, metavar = 'FIELD1,FIELD2,...')
	parser.add_argument('-f', '--fields', help = 'display extra fields (comma separated parameter, possible fields: %s)' % FIELDS, type = str, default = None, metavar = 'FIELDS,FIELD2,...')
	parser.add_argument('--show-archived', help = 'search in archived catalogues as well', action = 'store_true', default = False)

	if include_pattern:
		parser.add_argument('patterns', help = 'matches have to contain one of these patterns (glob with %%)', nargs = '*', default = None)

	#####################################################################
	# ENTITY PARAMETERS                                                 #
	#####################################################################

	for field, data in sorted(parameters.items()):
		#############################################################
		# OPTION NAME                                               #
		#############################################################

		OPTION = '--%s' % field

		#############################################################
		# DEFAULT VALUE AND HELP                                    #
		#############################################################

		if not data['foreign'] and len(data['descr']) > 1:

			DEFAULT = data['descr'][1]
			HELP = 'comma separated parameters, default: `%s`' % data['descr'][1]

		else:
			DEFAULT = None
			HELP = 'comma separated parameters'

		#############################################################
		# ADD OPTION                                                #
		#############################################################

		try:
			parser.add_argument(OPTION, help = HELP, default = DEFAULT, metavar = 'XXX')

		except argparse.ArgumentError:
			pass

#############################################################################

def print_json(table, stream = sys.stdout):
	stream.write(json.dumps(table) + '\n')

#############################################################################
