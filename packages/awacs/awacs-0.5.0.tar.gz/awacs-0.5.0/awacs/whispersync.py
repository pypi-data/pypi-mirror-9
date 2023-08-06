# Copyright (c) 2012-2013, Mark Peek <mark@peek.org>
# All rights reserved.
#
# See LICENSE file for full license.

from aws import Action

service_name = 'AWS Whispersync'
prefix = 'whispersync'

GetDatamapUpdates = Action(prefix, 'GetDatamapUpdates')
PatchDatamapUpdates = Action(prefix, 'PatchDatamapUpdates')
