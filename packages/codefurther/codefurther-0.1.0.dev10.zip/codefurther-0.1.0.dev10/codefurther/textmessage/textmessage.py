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
from codefurther.helpers import vic_decode, TEXT_SETTINGS
from say import fmt
from twilio.rest import TwilioRestClient

for setting in TEXT_SETTINGS:
    if setting not in cf_config or cf_config[setting] is None:
        raise ValueError(fmt("The essential CodeFurther setting: {setting} has not been set. Text messages cannot be sent."))


class TextMessage:
    def __init__(self):
        self.twilio = TwilioRestClient(
            account=vic_decode(
                cf_config['CF_TWILIO_ACCOUNT']
            ), token=vic_decode(
                cf_config['CF_TWILIO_TOKEN']
            )
        )

    def send(self, to, message):
        message = self.twilio.messages.create(
            to=to,
            from_= vic_decode(cf_config['CF_TWILIO_FROM']),
            body=message
        )

    def messages(self, to=None, from_=None, date_sent=None, after=None, before=None):

        messages = self.twilio.messages.list(
            to=to,
            from_=from_,
            date_sent=date_sent,
            after=after,
            before=before
        )

        return self.twilio.messages.list()

    def incoming(self, from_=None, date_sent=None, after=None, before=None):
        to = vic_decode(cf_config['CF_TWILIO_FROM'])

        return self.messages(
            to=to,
            from_=from_,
            date_sent=date_sent,
            after=after,
            before=before
        )
