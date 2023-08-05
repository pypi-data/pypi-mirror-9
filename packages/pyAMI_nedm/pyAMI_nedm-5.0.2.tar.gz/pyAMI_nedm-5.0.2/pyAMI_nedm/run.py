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

import time, os.path, hashlib, datetime, pyAMI_nedm.config, pyAMI_nedm.parsers, pyAMI_nedm.exception

#############################################################################

class NEDMRun:
	#####################################################################

	def __init__(self, client, run_number, run_files):
		#############################################################
		#                                                           #
		#############################################################

		self.client = client

		#############################################################
		#                                                           #
		#############################################################

		self.run_number = run_number
		self.run_files = run_files

		self.cycle_number = 0
		self.cycle_duration = 0.0

		self.date_init = 0.0
		self.date_end = 0.0

		#### TMP ####

		if   self.run_number >= 7247 and self.run_number <= 7674:
			self.type = 'nedm'
			self.sub_type = 'nedm'
		elif self.run_number >= 8154 and self.run_number <= 8186:
			self.type = 'hg'
			self.sub_type = 'gpe'
		else:
			self.type = 'unknown'
			self.sub_type = 'unknown'

		#############################################################
		#                                                           #
		#############################################################

		self.meta_file_name = None
		self.slow_control_file_name = None

		for run_file in run_files:

			if run_file.find('_Meta.edm') > 0:
				self.meta_file_name = run_file

			if run_file.find('_TCP-SlowControl.edm') > 0:
				self.slow_control_file_name = run_file

	#####################################################################

	def read(self):
		self.read_files()

		self.post_processing()

	#####################################################################

	def read_files(self):
		#############################################################
		# META FILE                                                 #
		#############################################################

		if not self.meta_file_name is None:

			data = pyAMI_nedm.parsers.parse_meta_file(self.meta_file_name)

			if len(data) >= 2:
				date_init_str = data[ 0]['______Date_and_Time______']
				date_end_str = data[-1]['______Date_and_Time______']

				self.date_init = time.mktime(datetime.datetime.strptime(date_init_str, "%Y-%m-%d_%H:%M:%S.%f_%Z").timetuple())
				self.date_end = time.mktime(datetime.datetime.strptime(date_end_str, "%Y-%m-%d_%H:%M:%S.%f_%Z").timetuple())

				self.cycle_number = int(data[-1]['iIteration'])

		#############################################################
		# SLOW CONTROL FILE                                         #
		#############################################################

		if not self.slow_control_file_name is None:

			data = pyAMI_nedm.parsers.parse_slow_control_file(self.slow_control_file_name)

			for x in data:

				if x[1] == 'STEP_DURATION':

					for i in xrange(2, len(x)):
						self.cycle_duration += float(x[i])

	#####################################################################

	def post_processing(self):

		try:
			self.date_end += (self.cycle_duration / 1000) - (self.date_end - self.date_init) % (self.cycle_duration / 1000)

		except ZeroDivisionError:
			pass

	#####################################################################

	def dump(self):
		print('run_number: %06d' % self.run_number)

		print('  -> type: %s' % self.type)
		print('  -> subType: %s' % self.sub_type)
		print('  -> cycle_number: %d' % self.cycle_number)
		print('  -> cycle_duration: %f' % self.cycle_duration)

		try:
			print('  -> date_init: %d' % int(self.date_init))
			print('  -> date_end: %d' % int(self.date_end))
		except ValueError:
			pass

		print('')

	#####################################################################

	def save(self):
		#############################################################
		#                                                           #
		#############################################################

		result = self.client.execute([
			'SearchQuery',
			'-project=NEDM',
			'-processingStep=metadata',
			'-glite="SELECT metadata_run.runNumber WHERE metadata_run.runNumber=\'%d\'"' % self.run_number
		], 'dict_object')

		t1 = datetime.datetime.fromtimestamp(self.date_init).strftime('%Y-%m-%d %H:%M:%S')
		t2 = datetime.datetime.fromtimestamp(self.date_end).strftime('%Y-%m-%d %H:%M:%S')

		if len(result.rowsets) == 0:

			self.client.execute([
				'AddElement',
				'-project=NEDM',
				'-processingStep=metadata',
				'-entity=metadata_run',
				'-runNumber="%d"' % self.run_number,
				'-dateInit="%s"' % t1,
				'-dateEnd="%s"' % t2,
				'-numberOfCycles="%d"' % self.cycle_number,
				'-@type="%s"' % self.type,
				'-@subType="%s"' % self.sub_type
			], 'dict_object')

		else:
			self.client.execute([
				'UpdateElement',
				'-project=NEDM',
				'-processingStep=metadata',
				'-entity=metadata_run',
				'-runNumber="%d"' % self.run_number,
				'-separator=","',
				'-updateField="dateInit,dateEnd,numberOfCycles"',
				'-updateValue="%s,%s,%d"' % (t1, t2, self.cycle_number)
			], 'dict_object')

		#############################################################
		#                                                           #
		#############################################################

		result = self.client.execute([
			'SearchQuery',
			'-project=NEDM',
			'-processingStep=metadata',
			'-glite="SELECT metadata_file.name WHERE metadata_run.runNumber=\'%d\'"' % (self.run_number)
		], 'dict_object')

		run_files_in_db = set([row['name'] for row in result.get_rows_i()])

		#############################################################
		#                                                           #
		#############################################################

		for run_file in self.run_files:
			name = os.path.basename(run_file)

			#####################################################
			#                                                   #
			#####################################################

			if not name in run_files_in_db:

				self.client.execute([
					'AddElement',
					'-project=NEDM',
					'-processingStep=metadata',
					'-entity=metadata_file',
					'-name="%s"' % name,
					'-md5="%s"' % hashlib.md5(run_file).hexdigest(),
					'-runNumber="%d"' % self.run_number
				], 'dict_object')

		#############################################################
		#                                                           #
		#############################################################

		result = self.client.execute([
			'SearchQuery',
			'-project=NEDM',
			'-processingStep=metadata',
			'-glite="SELECT metadata_file.name WHERE metadata_run.runNumber=\'%d\' AND metadata_file#metadata_site.name=\'%s\'"' % (self.run_number, pyAMI_nedm.config.current_site_name)
		], 'dict_object')

		run_file_sites_in_db = set([row['name'] for row in result.get_rows_i()])

		#############################################################
		#                                                           #
		#############################################################

		for run_file in self.run_files:
			path, name = os.path.os.path.split(run_file)

			#####################################################
			#                                                   #
			#####################################################

			if path.startswith(pyAMI_nedm.config.current_site_path):

				path = path.replace(pyAMI_nedm.config.current_site_path, '', 1)

				while len(path) > 0 and path[0] == '/':
					path = path[1: ]

			else:
				raise pyAMI_nedm.exception.NEDMException('error: file `%s` not found in site `%s` !' % (run_file, pyAMI_nedm.config.current_site_name))

			#####################################################
			#                                                   #
			#####################################################

			if not name in run_file_sites_in_db:

				self.client.execute([
					'AddBridgeElement',
					'-project=NEDM',
					'-processingStep=metadata',
					'-entity=metadata_file',
					'-bridgeTo=metadata_site',
					'-metadata_file_site.path="%s"' % path,
					'-metadata_file_site.md5="%s"' % hashlib.md5(run_file).hexdigest(),
					'-metadata_run.runNumber="%d"' % self.run_number,
					'-metadata_file.name="%s"' % name,
					'-metadata_site.name="%s"' % pyAMI_nedm.config.current_site_name
				], 'dict_object')

	#####################################################################

	def cond(self):
		#############################################################
		#                                                           #
		#############################################################

		cond_values_in_db = set([])

		t1 = datetime.datetime.fromtimestamp(self.date_init).strftime('%Y-%m-%d %H:%M:%S')
		t2 = datetime.datetime.fromtimestamp(self.date_end).strftime('%Y-%m-%d %H:%M:%S')

		result = self.client.execute([
			'SearchQuery',
			'-project=NEDM',
			'-processingStep=metadata',
			'-glite="SELECT cond_parameter.name WHERE cond_value.dateInit <= \'%s\' AND cond_value.dateEnd >= \'%s\'"' % (t1, t2)
		], 'dict_object')

		cond_values_in_db = set([row['name'] for row in result.get_rows_i()])

		#############################################################
		#                                                           #
		#############################################################

		for run_file in self.run_files:
			#####################################################

			if run_file.find('_Hg_lamps.edm') > 0 and not 'subflag_hg_lamps' in cond_values_in_db:

				self.client.execute([
					'AddElement',
					'-project=NEDM',
					'-processingStep=metadata',
					'-entity=cond_value',
					'-booleanValue="1"',
					'-dateInit="%s"' % t1,
					'-dateEnd="%s"' % t2,
					'-cond_parameter.name="subflag_hg_lamps"',
				], 'dict_object')

			#####################################################

			if run_file.find('_PMT-readout.edm') > 0 and not 'subflag_pmt' in cond_values_in_db:

				self.client.execute([
					'AddElement',
					'-project=NEDM',
					'-processingStep=metadata',
					'-entity=cond_value',
					'-booleanValue="1"',
					'-dateInit="%s"' % t1,
					'-dateEnd="%s"' % t2,
					'-cond_parameter.name="subflag_pmt"',
				], 'dict_object')

			#####################################################

			if run_file.find('_Hg_lamps.edm') > 0 and run_file.find('_PMT-readout.edm') > 0 and not 'flag_hgm' in cond_values_in_db:

				self.client.execute([
					'AddElement',
					'-project=NEDM',
					'-processingStep=metadata',
					'-entity=cond_value',
					'-booleanValue="1"',
					'-dateInit="%s"' % t1,
					'-dateEnd="%s"' % t2,
					'-cond_parameter.name="flag_hgm"',
				], 'dict_object')

			#####################################################

			if run_file.find('_Cesium-A.edm') > 0 and not 'flag_csa' in cond_values_in_db:

				self.client.execute([
					'AddElement',
					'-project=NEDM',
					'-processingStep=metadata',
					'-entity=cond_value',
					'-booleanValue="1"',
					'-dateInit="%s"' % t1,
					'-dateEnd="%s"' % t2,
					'-cond_parameter.name="flag_csa"',
				], 'dict_object')

			#####################################################

			if run_file.find('_Cesium-B.edm') > 0 and not 'flag_csb' in cond_values_in_db:

				self.client.execute([
					'AddElement',
					'-project=NEDM',
					'-processingStep=metadata',
					'-entity=cond_value',
					'-booleanValue="1"',
					'-dateInit="%s"' % t1,
					'-dateEnd="%s"' % t2,
					'-cond_parameter.name="flag_csb"',
				], 'dict_object')

			#####################################################

			if run_file.find('_HV.edm') > 0 and not 'flag_hv' in cond_values_in_db:

				self.client.execute([
					'AddElement',
					'-project=NEDM',
					'-processingStep=metadata',
					'-entity=cond_value',
					'-booleanValue="1"',
					'-dateInit="%s"' % t1,
					'-dateEnd="%s"' % t2,
					'-cond_parameter.name="flag_hv"',
				], 'dict_object')

#############################################################################
