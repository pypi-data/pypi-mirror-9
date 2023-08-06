# -*- coding: utf-8 -*-
#
# Copyright 2014 Danny Goodall
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import (absolute_import, division, print_function, unicode_literals)
from builtins import *
from codefurther import cf_config
from codefurther.helpers import vic_decode, TWITTER_SETTINGS
from say import fmt
from twython import Twython

# Check that the TWITTER_SETTINGS have been set
for setting in TWITTER_SETTINGS:
    if setting not in cf_config or cf_config[setting] is None:
        raise ValueError(fmt("The essential CodeFurther setting: {setting} has not been set. Twitter can not be accessed."))

class Twitter:
    def __init__(self):
        self.twitter_api = Twython(
            vic_decode(cf_config['CF_TWITTER_APP_KEY']),
            vic_decode(cf_config['CF_TWITTER_APP_SECRET']),
            vic_decode(cf_config['CF_TWITTER_OAUTH_TOKEN']),
            vic_decode(cf_config['CF_TWITTER_OAUTH_TOKEN_SECRET'])
        )

    def tweet(self,status):
        self.twitter_api.update_status(status=status)