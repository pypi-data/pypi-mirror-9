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

"""The :mod:`utils` module contains utility functions and classes used by the other modules in the suite.

"""
import os

from future.utils import raise_from
from codefurther.errors import CodeFurtherConversionError
from six import iteritems


def isolate_path_filename(uri):
    """Accept a url and return the isolated filename component

    Accept a uri in the following format - http://site/folder/filename.ext and return the filename component.

    Args:
        uri (:py:class:`str`): The uri from which the filename should be returned
    Returns:
        file_component (:py:class:`str`): The isolated filename
    """
    # Look for the last slash
    url_parse = uri.rpartition('/')

    # Take everything to the right of the last slash and seperate it on the '.' if it exists, otherwise return the
    # string as is
    if '.' in url_parse[2]:
        file_parse = url_parse[2].rpartition('.')
        file_component = file_parse[0]
    else:
        file_component = url_parse[2]

    return file_component

def get_file_contents_as_text(url_tail, base_folder="tests/resources/{}.json"):
    path = url_tail.replace("/", "")

    resource_file = os.path.normpath(
        base_folder.format(
            path
        )
    )

    # Read the contents of the JSON file as string
    file_text = open(resource_file, mode='rb').read()
    #json_dict = json.loads(file_text.decode())
    #return json_dict
    return file_text.decode()


def request_send_file(request, uri, headers):
    if uri.endswith('-404-'):
        return (400, headers, "")
    filename = isolate_path_filename(uri)
    file_contents = get_file_contents_as_text(filename)
    return (200 if 'status' not in headers else headers['status'], headers, file_contents)


