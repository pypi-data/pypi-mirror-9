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

from linshareapi.core import CoreCli
from linshareapi.admin.domains import Domains
from linshareapi.admin.domainpatterns import DomainPatterns
from linshareapi.admin.functionalities import Functionalities
from linshareapi.admin.threads import  Threads
from linshareapi.admin.threadmembers import ThreadsMembers
from linshareapi.admin.users import Users
from linshareapi.admin.ldapconnections import LdapConnections


# -----------------------------------------------------------------------------
class AdminCli(CoreCli):
    # pylint: disable=R0902
    def __init__(self, *args, **kwargs):
        super(AdminCli, self).__init__(*args, **kwargs)
        self.base_url = "linshare/webservice/rest/admin"
        self.threads = Threads(self)
        self.thread_members = ThreadsMembers(self)
        self.users = Users(self)
        self.domains = Domains(self)
        self.ldap_connections = LdapConnections(self)
        self.domain_patterns = DomainPatterns(self)
        self.funcs = Functionalities(self)
