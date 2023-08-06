#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2015 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

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

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

from appier_extras.parts.admin import models

class Live(object):

    def has_live(self):
        try: import live
        except: live = None
        if not live: return False
        if not appier.conf("LIVE_ID"): return False
        if not appier.conf("LIVE_SECRET"): return False
        return True

    def ensure_live_account(self):
        api = self.get_live_api()
        user = api.self_user()
        email = user["emails"]["preferred"]
        account = models.Account.get(
            email = email,
            rules = False,
            raise_e = False
        )

        if not account:
            account = models.Account(
                username = email,
                email = email,
                password = api.access_token,
                password_confirm = api.access_token,
                live_id = user["id"],
                live_token = api.access_token,
                type = models.Account.USER_TYPE
            )
            account.save()
            account = account.reload(rules = False)

        if not account.live_id:
            account.live_id = user["id"]
            account.live_token = api.access_token
            account.save()

        if not account.live_token == account.live_token:
            account.live_token = api.access_token
            account.save()

        account.touch_s()

        self.session["username"] = account.username
        self.session["email"] = account.email
        self.session["type"] = account.type_s()
        self.session["tokens"] = account.tokens()

        return account

    def ensure_live_api(self, state = None):
        access_token = self.session.get("live.access_token", None)
        if access_token: return
        api = self.get_live_api()
        return api.oauth_authorize(state = state)

    def get_live_api(self):
        import live
        redirect_url = self.url_for("admin.oauth_live", absolute = True)
        access_token = self.session and self.session.get("live.access_token", None)
        return live.Api(
            client_id = appier.conf("LIVE_ID"),
            client_secret = appier.conf("LIVE_SECRET"),
            redirect_url = redirect_url,
            access_token = access_token
        )
