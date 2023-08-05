#! /usr/bin/env python
#! /home/fred/.virtualenvs/migration-linshare-cc/bin/python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
from __future__ import unicode_literals

import sys
import logging
import json

from linshareapi.user import UserCli
from linshareapi.admin import AdminCli
from argtoolbox import DEBUG_LOGGING_FORMAT

host="http://192.168.1.106:8080"
user="bart.simpson@nodomain.com"
password="secret"
user="root@localhost.localdomain"
password="adminlinshare"
verbose = True
debug=1

log = logging.getLogger()
log.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(DEBUG_LOGGING_FORMAT)
log.addHandler(streamHandler)


cli = UserCli(host, user, password, verbose, debug)
cli = AdminCli(host, user, password, verbose, debug)
cli.nocache = True
cli.nocache = False

#cli.auth()
#data = cli.documents.invalid()
#data = cli.users.search()
#data = cli.users.invalid()
data = cli.domain_patterns.invalid()
print data

