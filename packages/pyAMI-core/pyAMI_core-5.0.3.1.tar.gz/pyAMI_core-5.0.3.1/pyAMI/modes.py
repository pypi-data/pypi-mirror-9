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

import sys, code, pyAMI.utils, pyAMI.object, pyAMI.parser, pyAMI.exception

#############################################################################

if sys.version_info[0] == 3:
	eval(compile('def safe_exec(compiled_code, global_ns, local_ns):\n\texec(compiled_code, global_ns, local_ns)', '<safe_exec>', 'exec'))
else:
	eval(compile('def safe_exec(compiled_code, global_ns, local_ns):\n\texec compiled_code in global_ns, local_ns', '<safe_exec>', 'exec'))

#############################################################################
# MODE AUTH                                                                 #
#############################################################################

def auth(client, args):
	client.auth()

	return 0

#############################################################################
# MODE RESET                                                                #
#############################################################################

def reset(client, args):
	client.reset()

	return 0

#############################################################################
# UPLOAD PROXY                                                              #
#############################################################################

def upload_proxy(client, args):
	#####################################################################
	# GENERATE COMMAND                                                  #
	#####################################################################

	cmd_args = ['UploadProxy']

	#####################################################################
	# EXECUTE COMMAND                                                   #
	#####################################################################

	r = client.execute(cmd_args)

	if isinstance(r, pyAMI.object.AMIObject):
		pyAMI.utils.safeprint(r.formated_data)
	else:
		pyAMI.utils.safeprint(r)

	#####################################################################

	return 0

#############################################################################
# MODE COMMAND                                                              #
#############################################################################

def command(client, args):
	#####################################################################
	# TURN THE SHELL BARRIER ON                                         #
	#####################################################################

	pyAMI.parser.shell_barrier = True

	#####################################################################
	# GENERATE COMMAND                                                  #
	#####################################################################

	cmd_args = []
	cmd_args.extend(args['amiCmdName'])
	cmd_args.extend(args['amiCmdArgs'])

	#####################################################################
	# EXECUTE COMMAND                                                   #
	#####################################################################

	r = client.execute(cmd_args)

	if isinstance(r, pyAMI.object.AMIObject):
		pyAMI.utils.safeprint(r.formated_data)
	else:
		pyAMI.utils.safeprint(r)

	#####################################################################

	return 0

#############################################################################
# MODE CONSOLE                                                              #
#############################################################################

def console(client, args):

	local = {
		'client': client,
		'auth': client.auth,
		'reset': client.reset,
		'config': client.config,
		'execute': client.execute,
	}

	if args['scriptName']:
		#############################################################
		# EXECUTE FILE                                              #
		#############################################################

		sys.argv = []
		sys.argv.append(args['scriptName'])
		sys.argv.extend(args['scriptArgs'])

		try:
			f = open(sys.argv[0])
			source_code = f.read()
			f.close()

		except IOError as e:
			raise pyAMI.exception.Error(e)

		compiled_code = compile(source_code, sys.argv[0], 'exec')

		safe_exec(compiled_code, globals(), local)

		#############################################################

	else:
		#############################################################
		# RUN CONSOLE                                               #
		#############################################################

		sys.argv = [sys.argv[0]]

		#############################################################

		banner = pyAMI.config.banner if args['nosplash'] == False else ''

		#############################################################

		if args['gIPython']:
			#####################################################
			# IPYTHON GRAPHICAL MODE                            #
			#####################################################

			try:
				from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
				from IPython.qt.inprocess import QtInProcessKernelManager
				from IPython.lib import guisupport

			except ImportError as e:
				raise pyAMI.exception.Error('module `IPython` not properly installed: %s' % e)

			################################
			# HACK IPYTHON BANNER          #
			################################

			RichIPythonWidget._banner_default = lambda self: banner

			################################
			# KERNEL_MANAGER               #
			################################

			kernel_manager = QtInProcessKernelManager()
			kernel_manager.start_kernel()

			################################
			# KERNEL_CLIENT                #
			################################

			kernel_client = kernel_manager.client()
			kernel_client.start_channels()

			################################
			# PYAMI                        #
			################################

			kernel_manager.kernel.shell.push(local)

			################################
			# APPLICATION                  #
			################################

			a = guisupport.get_app_qt4()

			def stop():
				kernel_client.stop_channels()
				kernel_manager.shutdown_kernel()
				a.exit()

			control = RichIPythonWidget()
			control.kernel_manager = kernel_manager
			control.kernel_client = kernel_client
			control.exit_requested.connect(stop)
			control.show()

			guisupport.start_event_loop_qt4(a)

			#####################################################

		elif args['cIPython']:
			#####################################################
			# IPYTHON CONSOLE MODE                              #
			#####################################################

			try:
				from IPython.terminal.embed import InteractiveShellEmbed

			except ImportError as e:
				raise pyAMI.exception.Error('module `IPython` not properly installed: %s' % e)

			################################
			# SHELL                        #
			################################

			shell = InteractiveShellEmbed(banner1 = banner, banner2 = None)

			shell(local_ns = local)

			#####################################################

		else:
			#####################################################
			# DEFAULT MODE                                      #
			#####################################################

			code.interact(banner = banner, local = local)

			#####################################################

	return 0

#############################################################################
