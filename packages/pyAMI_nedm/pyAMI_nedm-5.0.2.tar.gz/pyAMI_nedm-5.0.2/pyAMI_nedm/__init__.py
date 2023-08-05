#############################################################################
# Author  : Jerome ODIER
#
# Email   : jerome.odier@cern.ch
#           jerome.odier@lpsc.in2p3.fr
#
# Version : 1.X.X for pyAMI_nedm (2013-2014)
#
#############################################################################

import pyAMI.config, pyAMI_nedm.config

#############################################################################

pyAMI.config.version = pyAMI_nedm.config.version

pyAMI.config.bug_report = pyAMI_nedm.config.bug_report

#############################################################################

pyAMI.config.endpoints['nedm'] = {'prot': 'https', 'host': 'lpsc.in2p3.fr', 'port': '443', 'path': '/AMI/nedm/net.hep.atlas.Database.Bookkeeping.AMI.Servlet.FrontEnd'}

#############################################################################
