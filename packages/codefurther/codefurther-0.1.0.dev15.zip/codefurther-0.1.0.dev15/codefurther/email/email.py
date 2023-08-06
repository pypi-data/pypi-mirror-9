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
from say import say, fmt
from email.mime.text import MIMEText
import smtplib
from codefurther.helpers import vic_decode, EMAIL_SETTINGS
from codefurther import cf_config


# Check if the EMAIL_SETTINGS has been set
for setting in EMAIL_SETTINGS:
    if setting not in cf_config or cf_config[setting] is None:
        raise ValueError(fmt("The essential CodeFurther setting: {setting} has not been set. Emails cannot be sent."))


class Email:
    def __init__(self):
        self.mail = smtplib.SMTP(vic_decode(cf_config['CF_SMTP_SERVER']), cf_config['CF_SMTP_PORT'])

    def send(self, from_, to, subject, message):
        self.mail.starttls()
        self.mail.login(vic_decode(cf_config['CF_SMTP_USERNAME']), vic_decode(cf_config['CF_SMTP_PASSWORD']))
        self.mail.sendmail(from_, to, self._make_message(from_, to, subject, message).as_string())
        self.mail.quit()

    def _make_message(self, from_, to, subject, message):
        if not isinstance(to, list):
            to_list = []
            to_list.append(to)
        else:
            to_list = to
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['To'] = ' ,'.join(to_list)
        msg['From'] = from_

        return msg