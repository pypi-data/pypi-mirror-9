#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Armor
# Copyright (c) 2008-2015 Hive Solutions Lda.
#
# This file is part of Hive Armor.
#
# Hive Armor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Armor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Armor. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import appier

from . import node
from . import domain

BASE_URL = "http://armor/api/"
""" The default base url to be used when no other
base url value is provided to the constructor """

class Api(
    appier.Api,
    node.NodeApi,
    domain.DomainApi
):

    def __init__(self, *args, **kwargs):
        appier.Api.__init__(self, *args, **kwargs)
        self.base_url = appier.conf("ARMOR_BASE_URL", BASE_URL)
        self.username = appier.conf("ARMOR_USERNAME", None)
        self.password = appier.conf("ARMOR_PASSWORD", None)
        self.base_url = kwargs.get("base_url", self.base_url)
        self.session_id = kwargs.get("session_id", None)
        self.username = kwargs.get("username", self.username)
        self.password = kwargs.get("password", self.password)
        self.object_id = kwargs.get("object_id", None)
        self.acl = kwargs.get("acl", None)
        self.tokens = kwargs.get("tokens", None)
        self.wrap_exception = kwargs.get("wrap_exception", True)

    def build(self, method, url, headers, kwargs):
        auth = kwargs.get("auth", True)
        if auth: kwargs["session_id"] = self.get_session_id()
        if "auth" in kwargs: del kwargs["auth"]

    def get_session_id(self):
        if self.session_id: return self.session_id
        return self.login()

    def auth_callback(self, params):
        self.session_id = None
        session_id = self.get_session_id()
        params["session_id"] = session_id

    def login(self, username = None, password = None):
        username = username or self.username
        password = password or self.password
        url = self.base_url + "admin/login"
        contents = self.get(
            url,
            auth = False,
            username = username,
            password = password
        )
        self.username = contents.get("username", None)
        self.object_id = contents.get("object_id", None)
        self.tokens = contents.get("tokens", None)
        self.session_id = contents.get("session_id", None)
        self.trigger("auth", contents)
        return self.session_id

    def ping(self):
        url = self.base_url + "admin/ping"
        return self.get(url, auth = False)
