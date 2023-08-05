#! /usr/bin/env python
# -*- coding: utf-8 -*-


# This file is part of Linshare api.
#
# LinShare api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LinShare api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare api.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


from __future__ import unicode_literals

import logging
import logging.handlers
import json

from linshareapi.core import ResourceBuilder
from linshareapi.cache import CacheManager
from linshareapi.cache import Time as CTime


# pylint: disable=C0111
# Missing docstring
# pylint: disable=R0903
# Too few public methods
# -----------------------------------------------------------------------------
CM = CacheManager()

# -----------------------------------------------------------------------------
class Time(CTime):
    def __init__(self, suffix, **kwargs):
        super(Time, self).__init__('linshareapi.admin.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class GenericClass(object):
    def __init__(self, corecli):
        self.core = corecli
        self.log = logging.getLogger('linshareapi.admin.rbu')

    def get_rbu(self):
        # pylint: disable=R0201
        rbu = ResourceBuilder("generic")
        return rbu

    def get_resource(self):
        return self.get_rbu().to_resource()

    def debug(self, data):
        self.log.debug("input data :")
        self.log.debug(json.dumps(data, sort_keys=True, indent=2))

    def _check(self, data):
        rbu = self.get_rbu()
        rbu.copy(data)
        rbu.check_required_fields()
