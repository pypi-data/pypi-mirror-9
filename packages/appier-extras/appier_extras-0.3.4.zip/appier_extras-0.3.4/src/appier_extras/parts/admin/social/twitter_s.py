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

class Twitter(object):

    def has_twitter(self):
        try: import twitter
        except: twitter = None
        if not twitter: return False
        if not appier.conf("TWITTER_KEY"): return False
        if not appier.conf("TWITTER_SECRET"): return False
        return True

    def ensure_twitter_account(self):
        api = self.get_twitter_api()
        user = api.verify_account()
        email = "%s@twitter.com" % user["screen_name"]
        account = models.Account.get(
            email = email,
            rules = False,
            raise_e = False
        )

        if not account:
            account = models.Account(
                username = user["screen_name"],
                email = email,
                password = api.oauth_token,
                password_confirm = api.oauth_token,
                twitter_username = user["screen_name"],
                twitter_token = api.oauth_token,
                type = models.Account.USER_TYPE
            )
            account.save()
            account = account.reload(rules = False)

        if not account.twitter_username:
            account.twitter_username = user["screen_name"]
            account.twitter_token = api.oauth_token
            account.save()

        if not account.twitter_token == account.twitter_token:
            account.twitter_token = api.oauth_token
            account.save()

        account.touch_s()

        self.session["username"] = account.username
        self.session["email"] = account.email
        self.session["type"] = account.type_s()
        self.session["tokens"] = account.tokens()

        return account

    def ensure_twitter_api(self, state = None):
        oauth_token = self.session.get("tw.oauth_token", None)
        oauth_token_secret = self.session.get("tw.oauth_token_secret", None)
        oauth_temporary = self.session.get("tw.oauth_temporary", True)
        if not oauth_temporary and oauth_token and oauth_token_secret: return
        self.session["tw.oauth_token"] = None
        self.session["tw.oauth_token_secret"] = None
        self.session["tw.oauth_temporary"] = True
        api = self.get_twitter_api()
        url = api.oauth_authorize(state = state)
        self.session["tw.oauth_token"] = api.oauth_token
        self.session["tw.oauth_token_secret"] = api.oauth_token_secret
        self.session["tw.oauth_temporary"] = True
        return url

    def get_twitter_api(self):
        import twitter
        redirect_url = self.url_for("admin.oauth_twitter", absolute = True)
        oauth_token = self.session and self.session.get("tw.oauth_token", None)
        oauth_token_secret = self.session and self.session.get("tw.oauth_token_secret", None)
        return twitter.Api(
            client_key = appier.conf("TWITTER_KEY"),
            client_secret = appier.conf("TWITTER_SECRET"),
            redirect_url = redirect_url,
            oauth_token = oauth_token,
            oauth_token_secret = oauth_token_secret
        )
