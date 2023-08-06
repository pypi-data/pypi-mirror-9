# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.


import pkg_resources

from steelscript.appfwk.apps.plugins import Plugin


class BusinessHoursPlugin(Plugin):
    title = 'Business Hours Report Plugin'
    description = 'A business hours plugin with reports and support libraries'
    version = pkg_resources.get_distribution('steelscript.appfwk.business-hours').version
    author = 'Riverbed Technology'

    enabled = True
    can_disable = True

    reports = ['reports']
    libraries = ['libs']
