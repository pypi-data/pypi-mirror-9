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

import re, string, smtplib, pyAMI_nedm.config

#############################################################################

nedm_config_receivers = [email for email in re.split('[,;\s]+', pyAMI_nedm.config.receivers) if len(email) > 0]

#############################################################################

class NEDMException(Exception):
	#####################################################################

	def __init__(self, value):

		self.value = value

		body = string.join((
			'From: %s' % pyAMI_nedm.config.sender,
			'To: %s' % pyAMI_nedm.config.receivers,
			'Subject: %s' % 'nEDM metadata error (%s)' % pyAMI_nedm.config.current_site_name,
			'',
			value
		), '\r\n')

		try:
			smtp = smtplib.SMTP(pyAMI_nedm.config.smtp_server)

			if not pyAMI_nedm.config.smtp_login is None and len(pyAMI_nedm.config.smtp_login) > 0\
			   and                                                                               \
			   not pyAMI_nedm.config.smtp_passw is None and len(pyAMI_nedm.config.smtp_passw) > 0:

				smtp.login(pyAMI_nedm.config.smtp_login, pyAMI_nedm.config.smtp_passw)

			smtp.sendmail(pyAMI_nedm.config.sender, pyAMI_nedm.config.receivers, body)

			smtp.quit()

		except Exception as e:
			print('error: could not send emails (%s) !' % e)

	#####################################################################

	def __str__(self):
		return self.value

#############################################################################
