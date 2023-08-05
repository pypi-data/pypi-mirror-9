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

version = '5.0.2'

#############################################################################

bug_report = 'Bug reports: ami@lpsc.in2p3.fr'

#############################################################################

nedm_run_types = [
	{'type': 'unknown', 'subType': 'unknown'},
	{'type': 'nedm', 'subType': 'nedm'},
	{'type': 'hg', 'subType': 'gpe'},
]

#############################################################################

nedm_sites = [
	{'name': 'ccin2p3', 'path': '/sps/hep/nedm/ALTERNATIVE'},
	{'name': 'psi', 'path': '/afs/psi.ch/project/nedm/data.nobackup'},
]

#############################################################################

nedm_component_parameters = {
	'hg_magnetometer': ['subflag_hg_lamps', 'subflag_pmt', 'flag_hgm'],
	'cs_magnetometer': ['flag_csa', 'flag_csb'],
	'vacuum': [],
	'thermometer': [],
	'high_voltage': ['flag_hv'],
	'trim_coils': ['sfc_status'],
	'sfc': ['sfc_status'],
	'rb_clock': [],
	'b0_power_supply': ['bo_status'],
	'valves': [],
	'neutron_detector': ['subflag_ch1', 'subflag_ch2', 'subflag_ch3', 'subflag_ch4', 'subflag_ch5', 'subflag_ch6', 'subflag_ch7', 'subflag_ch8', 'subflag_ch9'],
	'switch': [],
}

#############################################################################

current_site_name = '???'
current_site_path = '???'

#############################################################################

sender = 'ami@lpsc.in2p3.fr'
receivers = 'jerome.odier@lpsc.in2p3.fr,kermaidic@lpsc.in2p3.fr'

smtp_server = 'lpsc-mail.in2p3.fr'
smtp_login = None
smtp_passw = None

#############################################################################
