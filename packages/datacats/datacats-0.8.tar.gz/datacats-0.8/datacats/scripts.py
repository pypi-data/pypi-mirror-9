# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import abspath, dirname

SCRIPTS_DIR = dirname(abspath(__file__)) + '/scripts'

SHELL = SCRIPTS_DIR + '/shell.sh'
PASTER = SCRIPTS_DIR + '/paster.sh'
PASTER_CD = SCRIPTS_DIR + '/paster_cd.sh'
WEB = SCRIPTS_DIR + '/web.sh'
KNOWN_HOSTS = SCRIPTS_DIR + '/known_hosts'
SSH_CONFIG = SCRIPTS_DIR + '/ssh_config'
PURGE = SCRIPTS_DIR + '/purge.sh'
