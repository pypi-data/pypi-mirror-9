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
from codefurther.helpers import vic_decode, SLACK_SETTINGS
from say import fmt
from slacker import Slacker


# Check if the SLACK_SETTINGS vars have been set
for setting in SLACK_SETTINGS:
    if setting not in cf_config or cf_config[setting] is None:
        raise ValueError(fmt("The essential CodeFurther setting: {setting} has not been set. Slack messages cannot be sent."))


class Slack:
    def __init__(self, channel='#general', username="CodeFurther 'bot"):
        self.slacker = Slacker(vic_decode(cf_config['CF_SLACK_API_KEY']))
        self.default_channel = channel
        self.default_username = username

    def post_message(self, message, channel=None, username=None):
        self.slacker.chat.post_message(
            channel if channel else self.default_channel,
            message,
            username=username if username else self.default_username
        )