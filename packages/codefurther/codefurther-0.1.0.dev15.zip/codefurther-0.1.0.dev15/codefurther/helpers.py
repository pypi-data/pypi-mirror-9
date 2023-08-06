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
"""Helper functions and classes for the codefurther package.

.. moduleauthor:: Danny Goodall <danny@onebloke.com>

"""
from __future__ import (absolute_import, division, print_function, unicode_literals)
from future.standard_library import hooks
from future.utils import iteritems
from past.builtins import basestring
from builtins import *
from six import reraise as raise_, PY2, PY3

import sys
import os
import re
import codecs
import imp
import errno
import json
import arrow

from collections import OrderedDict
import tempfile
from codefurther.errors import CodeFurtherHTTPError, CodeFurtherConnectionError, CodeFurtherReadTimeoutError
import requests
import requests_cache
from say import fmt, say
from stuf import stuf, orderedstuf

with hooks():
    from urllib.parse import unquote, urljoin


# This code from here: http://stackoverflow.com/a/24519338/1300916
ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)

TWITTER_SETTINGS = [
    'CF_TWITTER_APP_KEY',
    'CF_TWITTER_APP_SECRET',
    'CF_TWITTER_OAUTH_TOKEN',
    'CF_TWITTER_OAUTH_TOKEN_SECRET',
]

SLACK_SETTINGS = [
    'CF_SLACK_API_KEY',
]

EMAIL_SETTINGS = [
    'CF_SMTP_SERVER',
    'CF_SMTP_PORT',
    'CF_SMTP_USERNAME',
    'CF_SMTP_PASSWORD',
]

TEXT_SETTINGS = [
    'CF_TWILIO_ACCOUNT',
    'CF_TWILIO_TOKEN',
    'CF_TWILIO_FROM',
]

FORECAST_SETTINGS = [
    'CF_FORECASTIO_API_KEY',
]

KNOWN_SETTINGS = []
KNOWN_SETTINGS.extend(TWITTER_SETTINGS)
KNOWN_SETTINGS.extend(SLACK_SETTINGS)
KNOWN_SETTINGS.extend(EMAIL_SETTINGS)
KNOWN_SETTINGS.extend(TEXT_SETTINGS)
KNOWN_SETTINGS.extend(FORECAST_SETTINGS)

CF_BAD_DATE=arrow.Arrow(2000, 1, 1)

def vic_decode(enciphered):
    return codecs.decode(enciphered, 'rot_13')

def vic_encode(plaintext):
    return codecs.encode(plaintext, 'rot_13')

def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


class FileSpoofer:
    def __init__(self, api_base="http://cflyricsserver.herokuapp.com/lyricsapi", base_folder="tests/resources/lyricsapi", extension=".json"):
        self.api_base = api_base
        self.base_folder = base_folder
        self.extension = extension
        self.base_folder_fmt = base_folder+"{}"+extension if base_folder.endswith("/") else base_folder+"/{}"+extension

    def isolate_path_filename(self, uri, api_base=None):
        """Accept a url and return the part that is unique to this request

        Accept a uri in the following format - http://site/folder/filename.ext and return the component part that is
        unique to the request when the base api of http://site/folder has been removed

        Args:
            uri (:py:class:`str`): The uri from which the filename should be returned
            api_base (:py:class:`str`): The new base to use, defaults to self.api_base
        Returns:
            file_component (:py:class:`str`): The isolated path
        """
        # Did we get an api_base
        api_base = api_base if api_base else self.api_base

        # Look for the part after the api_base
        url_parse = uri.lower().rpartition(api_base)

        # Take everything to the right of the api_base
        file_component = url_parse[2]

        # Remove any URL ? parameters
        if '?' in file_component:
            file_component = file_component.rpartition('?')[0]

        #: Remove URL encoding
        file_component = unquote(file_component)

        #: Remove any spaces in the filename
        file_component = file_component.replace(' ','')

        return file_component

    def get_file_contents_as_text(self, url_tail):
        #path = url_tail.replace("/", "")

        resource_file = os.path.normpath(
            self.base_folder_fmt.format(
                url_tail
            )
        )

        # Read the contents of the JSON file as string
        try:
            file_text = open(resource_file, encoding="utf-8").read()
            #file_text = open(resource_file, 'rb').read()
        except Exception as e:
            print("An error occurred",e)

        # json_dict = json.loads(file_text.decode())
        # return json_dict

        # Let's check for unicode escape characters
        #file_text = file_text.decode('unicode-escape').encode('utf-8')
        #file_text = decode_escapes(file_text)

        return file_text

    def request_send_file(self, request, uri, headers):
        if '-404-' in uri:
            return (404, headers, "")
        filename = self.isolate_path_filename(uri)
        file_contents = self.get_file_contents_as_text(filename)
        return 200 if 'status' not in headers else headers['status'], headers, file_contents


class ApiWithCache:
    """ Provides the programmer with properties that return the Top 40 chart data.

    The programmer creates an instance of this object, and then uses the exposed properties to access the data about
    the singles and albums charts.

    Creates and returns the object instance.

    All results will be cached for the duration of the existence of this instance in memory. However, if
    cache_duration is specified (not None), then results will be persisted to a local
    sqlite DB for the duration, in seconds, or cache_duration. A config for requests cache can also
    be passed in cache_config too, or if None, the default setting is used.

    Args:
        base_url (str): The base url of the remote API before the specific service details are appended.
            For example, the base url might be "a.site.com/api/", and the service "/albums/", when appended to the
            base url, creates the total url required to access the album data.
        cache_duration (:py:class:`int`): If None, then the persistent cache will be disabled. Otherwise
            the cache duration specified will be used.
        cache_config (:py:class:`dict`): If None the default config will be used to pass to the
            ``install_cache`` method of requests_cache, otherwise the config in this parameter will be used.
            Any 'expire_after' key in the cache config will be replaced and the duration set to
            cache_duration.
    Attributes:
        error_format (str): The format string to be used when creating error messages.
        base_url (:py:class:`str`): The base url used to access the remote api
        cache_duration (:py:class:`int`): The duration in seconds that results will be returned from the cache before
            a fresh read of the external API will replace them.
        cache_config (:py:class:`dict`): A dictionary that describes the config that will be passed to the
            ``request_cache`` instance - allowing different backends and other options to be set.
    Returns:
        Top40 (:py:class:`Top40`): The Top40 instance.
    """
    error_format = "Received an error whist reading from {}: Returned code: {}"
    base_url_default = None
    extra_headers = None

    def __init__(self, base_url_param=None,
                 cache_duration=3600,
                 cache_config=None,
                 cache_prefix="codefurthercache"):

        if base_url_param is None and self.base_url_default is None:
            raise ValueError("A base URL must be specified.")

        # Store the base url that we will append our service url enpoints to
        self.base_url = base_url_param if base_url_param else self.base_url_default

        # If cache_duration is not None, then we will use a persistent request_cache
        self.cache_duration = cache_duration

        # If we've been passed a different config, then we should use that instead of the class-level version
        if cache_config is None:
            self.cache_config = {
                'cache_name': '{}/{}'.format(
                    tempfile.gettempdir(),
                    cache_prefix
                )
            }
        else:
            self.cache_config = cache_config

        # The cache_duration tells us how long responses will be cached in
        # persistent storage (in seconds)
        self.reset_cache(self.cache_duration)

    def reset_cache(self, cache_duration=None):
        """Remove any cached singles or albums charts

        Because the UK Top40 charts only change once per week, :py:class:`Top40` will cache the results of singles and
        albums. This means that during the execution of a program, repeated calls to retrieve singles and albums chart
        information will only actually call the remote API once. If, for whatever reason you need to ensure that an
        attempt to access single or album information actually results in a call to the remote API, then calling the
        :py:meth:`Top40.reset_cache` method will do this, by clearing down any existing cached chart information.

        If a cache is in place, then the results will also be cached across python runtime executions.

        Params:
            cache_duration (:py:class:`int`): If ``None`` we will uninstall the requests cache and the next
                read from the API will cause a remote call to be executed. Otherwise it specifies the number of
                seconds before the persistent cache will expire.
        """

        if cache_duration is None:
            # We are disabling the existing persistent_cache
            requests_cache.uninstall_cache()
        else:
            # We are setting a persistent cache so insert the duration into our cache config
            self.cache_config['expire_after'] = cache_duration

            # and then install the cache with this configuration
            requests_cache.install_cache(**self.cache_config)

        # Remember the new duration
        self.cache_duration = cache_duration

        # Rest the in-memory caches to force a read from remote site
        self._cache = dict()

    def _get_cache_or_none(self, cache_item):
        return self._cache.get(cache_item, None)

    def _set_cache(self, cache_item, value):
        self._cache[cache_item] = value

    def get_cache(self, cache_item):
        return self._get_cache_or_none(cache_item)

    def set_cache(self, cache_item, value):
        self._set_cache(cache_item, value)

    def _get_data(self, service_url, params=None):
        """Internal routine to retrieve data from the external service.

        The URL component that is passed is added to the base URL that was specified when the object was instantiated.
        Additional params passed will be passed to the API as key=value pairs, and the return data converted from JSON
        to a Python :class:`dict` .

        Args:
            service_url (str): The remote url to connect to.
            params (dict): Additional parameters will be passed as key=value pairs to the URL as query variables
                ?key=value.
        Returns:
            response (JSON): A JSON document converted to Python equivalent classes.
        Raises:
            Top40HTTPError (:py:class:`~errors.Top40HTTPError`): If a status code that is not 200 is returned
            Top40ConnectionError (:py:class:`~errors.Top40ConnectionError`): If a connection could not be established to the remote server
            Top40ReadTimeoutError (:py:class:`~errors.Top40ReadTimeoutError`): If the remote server took too long to respond
        """
        # TODO - Change the Munch references to dict

        if not params:
            params = {}

        # Build the full url from the base url + the url for this service
        full_url = urljoin(self.base_url, service_url.lstrip('/'))
        try:
            response = requests.get(full_url, params=params, headers=self.extra_headers)
        except requests.exceptions.HTTPError as e:
            message = ApiWithCache.error_format.format(
                service_url,
                e.response.status_code
            )
            raise CodeFurtherHTTPError(message, e.response.status_code)
        except (
                requests.exceptions.ConnectionError, requests.exceptions.SSLError, requests.exceptions.ConnectTimeout):
            raise CodeFurtherConnectionError("Could not connect to remote server.")
        except requests.exceptions.ReadTimeout:
            raise CodeFurtherReadTimeoutError("The remote server took longer than expected to reply.")
        except Exception as e:
            raise

        # Check for status code and raise Top40HTTPError if a non 200 result is received.
        if response.status_code != 200:
            message = ApiWithCache.error_format.format(
                service_url,
                response.status_code
            )
            raise CodeFurtherHTTPError(message, response.status_code)

        # Treat the response text as JSON and return the Python equivalent
        return response.json()

def stufify(x):
    """ Recursively transforms a dictionary into a Stuf via copy.
        >>> b = stufify({'urmom': {'sez': {'what': 'what'}}})
        >>> b.urmom.sez.what
        'what'
        stufify can handle intermediary dicts, lists and tuples (as well as
        their subclasses), but ymmv on custom datatypes.
        >>> b = stufify({ 'lol': ('cats', {'hah':'i win again'}),
        ...         'hello': [{'french':'salut', 'german':'hallo'}] })
        >>> b.hello[0].french
        'salut'
        >>> b.lol[1].hah
        'i win again'
        nb. As dicts are not hashable, they cannot be nested in sets/frozensets.

        Taken from here:https://github.com/Infinidat/munch/blob/master/munch/__init__.py
    """
    if isinstance(x, dict):
        ret = stuf()
        #: This needs to be done long-hand because the update method of the stuf() seems
        #: to convert everything to a dict - specifically lists got converted to stuf()
        for k,v in iteritems(x):
            ret[k] = stufify(v)
        return ret
    elif isinstance(x, list):
        ret = [stufify(v) for v in x ]
        return ret
    elif isinstance(x, tuple):
        ret = type(x)( stufify(v) for v in x )
        return ret
    else:
        return x

def unstufify(x):
    """ Recursively converts a Stuf into a dictionary.
        >>> b = stufify(foo=stufify(lol=True), hello=42, ponies='are pretty!')
        >>> unstufify(b)
        {'ponies': 'are pretty!', 'foo': {'lol': True}, 'hello': 42}
        unstufify will handle intermediary dicts, lists and tuples (as well as
        their subclasses), but ymmv on custom datatypes.
        >>> b = stuf(foo=['bar', stuf(lol=True)], hello=42,
        ...         ponies=('are pretty!', stuf(lies='are trouble!')))
        >>> unstufify(b) #doctest: +NORMALIZE_WHITESPACE
        {'ponies': ('are pretty!', {'lies': 'are trouble!'}),
         'foo': ['bar', {'lol': True}], 'hello': 42}
        nb. As dicts are not hashable, they cannot be nested in sets/frozensets.

        Taken from here:https://github.com/Infinidat/munch/blob/master/munch/__init__.py
    """
    if isinstance(x, dict):
        return dict( (k, unstufify(v)) for k,v in iteritems(x) )
    elif isinstance(x, (list, tuple)):
        return type(x)( unstufify(v) for v in x )
    else:
        return x

class OutputHelper:
    def __init__(self, header_description, underline_char="-", intra_col=" "):
        """

        :param header_description:
        :return:
        """
        self.header_description = header_description
        self.underline_char = underline_char
        self.intra_col = intra_col

    def pad_out(self, thing, width, alignment, padder=" "):
        pad = abs( width - len(thing) ) * padder
        alignment = '<' if alignment != '>' else alignment
        return thing+pad if alignment == "<" else pad+thing

    def _build_line(self, mode, suppress = None, padder=" ", intra_col=None):
        if mode not in ["header","underline"]:
            raise ValueError("mode must be one of the following: "+fmt("{mode}"))
        intra_col = self.intra_col if intra_col is None else intra_col
        suppress = suppress if suppress else []
        return_string= ""
        for key, (thing, width, alignment) in iteritems(self.header_description):
            if key in suppress:
                continue
            return_string += self.pad_out(
                thing if mode=='header' else self.underline_char,
                width,
                alignment,
                padder
            ) + intra_col

        return return_string

    def header(self, suppress = None, padder=" ", intra_col=None):
        """Return the header text
        :return:
        """
        return self._build_line('header', suppress=suppress, padder=padder, intra_col=intra_col)

    def underline(self, suppress=None, padder="-", intra_col=None):
        """

        :param suppress:
        :param padder:
        :param intra_col:
        :return:
        """
        return self._build_line('underline', suppress=suppress, padder=padder, intra_col=intra_col)


class FoundMixin(object):
    what_am_i = "Generic object"
    format_string = "NO FORMAT SUPPLIED"
    header_description = OrderedDict([])

    def __init__(self, *args, **kwargs):
        self.__found = True
        self.__found_reason = ""
        self.output_helper = OutputHelper(self.header_description)
        super(FoundMixin, self).__init__(*args, **kwargs)

    def __str__(self):
        return fmt(
            self.format_string
        ) if self.found else self.found_reason

    def set_found(self, found, found_reason=None):
        self.__found = found
        self.__found_reason = found_reason if found_reason is not None else ""

    def get_found(self):
        return self.__found

    def get_found_reason(self):
        return self.__found_reason

    found = property(get_found, set_found)
    found_reason = property(get_found_reason)

    def not_found_str(self):
        pass

    def str_or_not_found(self, output):
        if self.found:
            return fmt(self.format_string)
        else:
            return fmt("{self.what_am_i} was not found.")
    @property
    def heading(self):
        return self.output_helper.header()

    @property
    def underline(self):
        return self.output_helper.underline()


#: The following classes and fuctions were snaffled from the excellent Flask/Werkzeug modules
class ImportStringError(ImportError):
    """Provides information about a failed :func:`import_string` attempt."""

    #: String in dotted notation that failed to be imported.
    import_name = None
    #: Wrapped exception.
    exception = None

    def __init__(self, import_name, exception):
        self.import_name = import_name
        self.exception = exception

        msg = (
            'import_string() failed for %r. Possible reasons are:\n\n'
            '- missing __init__.py in a package;\n'
            '- package or module path not included in sys.path;\n'
            '- duplicated package or module name taking precedence in '
            'sys.path;\n'
            '- missing module, class, function or variable;\n\n'
            'Debugged import:\n\n%s\n\n'
            'Original exception:\n\n%s: %s')

        name = ''
        tracked = []
        for part in import_name.replace(':', '.').split('.'):
            name += (name and '.') + part
            imported = import_string(name, silent=True)
            if imported:
                tracked.append((name, getattr(imported, '__file__', None)))
            else:
                track = ['- %r found in %r.' % (n, i) for n, i in tracked]
                track.append('- %r not found.' % name)
                msg = msg % (import_name, '\n'.join(track),
                             exception.__class__.__name__, str(exception))
                break

        ImportError.__init__(self, msg)

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.import_name,
                                 self.exception)


def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    #XXX: py3 review needed
    assert isinstance(import_name, basestring)
    # force the import name to automatically convert to strings
    import_name = str(import_name)
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        # __import__ is not able to handle unicode strings in the fromlist
        # if the module is a package
        if PY2 and isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        try:
            return getattr(__import__(module, None, None, [obj]), obj)
        except (ImportError, AttributeError):
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            modname = module + '.' + obj
            __import__(modname)
            return sys.modules[modname]
    except ImportError as e:
        if not silent:
            raise_(
                ImportStringError,
                ImportStringError(import_name, e),
                sys.exc_info()[2])


class ConfigAttribute(object):
    """Makes an attribute forward to the config"""

    def __init__(self, name, get_converter=None):
        self.__name__ = name
        self.get_converter = get_converter

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        rv = obj.config[self.__name__]
        if self.get_converter is not None:
            rv = self.get_converter(rv)
        return rv

    def __set__(self, obj, value):
        obj.config[self.__name__] = value



class Config(dict):
    """Works exactly like a dict but provides ways to fill it from files
    or special dictionaries.  There are two common patterns to populate the
    config.
    Either you can fill the config from a config file::
        app.config.from_pyfile('yourconfig.cfg')
    Or alternatively you can define the configuration options in the
    module that calls :meth:`from_object` or provide an import path to
    a module that should be loaded.  It is also possible to tell it to
    use the same module and with that provide the configuration values
    just before the call::
        DEBUG = True
        SECRET_KEY = 'development key'
        app.config.from_object(__name__)
    In both cases (loading from any Python file or loading from modules),
    only uppercase keys are added to the config.  This makes it possible to use
    lowercase values in the config file for temporary values that are not added
    to the config or to define the config keys in the same file that implements
    the application.
    Probably the most interesting way to load configurations is from an
    environment variable pointing to a file::
        app.config.from_envvar('YOURAPPLICATION_SETTINGS')
    In this case before launching the application you have to set this
    environment variable to the file you want to use.  On Linux and OS X
    use the export statement::
        export YOURAPPLICATION_SETTINGS='/path/to/config/file'
    On windows use `set` instead.
    :param root_path: path to which files are read relative from.  When the
                      config object is created by the application, this is
                      the application's :attr:`~flask.Flask.root_path`.
    :param defaults: an optional dictionary of default values
    """

    def __init__(self, root_path, defaults=None):
        dict.__init__(self, defaults or {})
        self.root_path = root_path

    def from_envvars(self, variable_thing, silent=False, overwrite_with_none=False):
        """Takes a list of env vars and sets config based on those values

        DG Created method for CodeFurther"""

        values = {}

        # If we've got a string, then use it on its own, otherwise loop through the list
        variable_list = [variable_thing] if isinstance(variable_thing, basestring) else variable_thing
        for envvar in variable_list:
            value = os.getenv(envvar)
            if value is None and not silent:
                raise ValueError(fmt("Environment variable: {envvar} was not found."))
            if value is None and not overwrite_with_none:
                continue
            values[envvar] = value

        return self.from_mapping(values)


    def from_envvar(self, variable_name, silent=False):
        """Loads a configuration from an environment variable pointing to
        a configuration file.  This is basically just a shortcut with nicer
        error messages for this line of code::
            app.config.from_pyfile(os.environ['YOURAPPLICATION_SETTINGS'])
        :param variable_name: name of the environment variable
        :param silent: set to ``True`` if you want silent failure for missing
                       files.
        :return: bool. ``True`` if able to load config, ``False`` otherwise.
        """
        rv = os.environ.get(variable_name)
        if not rv:
            if silent:
                return False
            raise RuntimeError('The environment variable %r is not set '
                               'and as such configuration could not be '
                               'loaded.  Set this variable and make it '
                               'point to a configuration file' %
                               variable_name)
        return self.from_pyfile(rv, silent=silent)

    def from_pyfile(self, filename, silent=False):
        """Updates the values in the config from a Python file.  This function
        behaves as if the file was imported as module with the
        :meth:`from_object` function.
        :param filename: the filename of the config.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        :param silent: set to ``True`` if you want silent failure for missing
                       files.
        .. versionadded:: 0.7
           `silent` parameter.
        """
        filename = os.path.join(self.root_path, filename)
        d = imp.new_module('config')
        d.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        self.from_object(d)
        return True

    def from_object(self, obj):
        """Updates the values from the given object.  An object can be of one
        of the following two types:
        -   a string: in this case the object with that name will be imported
        -   an actual object reference: that object is used directly
        Objects are usually either modules or classes.
        Just the uppercase variables in that object are stored in the config.
        Example usage::
            app.config.from_object('yourapplication.default_config')
            from yourapplication import default_config
            app.config.from_object(default_config)
        You should not use this function to load the actual configuration but
        rather configuration defaults.  The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.
        :param obj: an import name or object
        """
        if isinstance(obj, basestring):
            obj = import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def from_json(self, filename, silent=False):
        """Updates the values in the config from a JSON file. This function
        behaves as if the JSON object was a dictionary and passed to the
        :meth:`from_mapping` function.
        :param filename: the filename of the JSON file.  This can either be an
                         absolute filename or a filename relative to the
                         root path.
        :param silent: set to ``True`` if you want silent failure for missing
                       files.
        .. versionadded:: 1.0
        """
        filename = os.path.join(self.root_path, filename)

        try:
            with open(filename) as json_file:
                obj = json.loads(json_file.read())
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR):
                return False
            e.strerror = 'Unable to load configuration file (%s)' % e.strerror
            raise
        return self.from_mapping(obj)

    def from_mapping(self, *mapping, **kwargs):
        """Updates the config like :meth:`update` ignoring items with non-upper
        keys.
        .. versionadded:: 1.0
        """
        mappings = []
        if len(mapping) == 1:
            if hasattr(mapping[0], 'items'):
                mappings.append(mapping[0].items())
            else:
                mappings.append(mapping[0])
        elif len(mapping) > 1:
            raise TypeError(
                'expected at most 1 positional argument, got %d' % len(mapping)
            )
        mappings.append(kwargs.items())
        for mapping in mappings:
            for (key, value) in mapping:
                if key.isupper():
                    self[key] = value
        return True

    def get_namespace(self, namespace, lowercase=True, trim_namespace=True):
        """Returns a dictionary containing a subset of configuration options
        that match the specified namespace/prefix. Example usage::
            app.config['IMAGE_STORE_TYPE'] = 'fs'
            app.config['IMAGE_STORE_PATH'] = '/var/app/images'
            app.config['IMAGE_STORE_BASE_URL'] = 'http://img.website.com'
            image_store_config = app.config.get_namespace('IMAGE_STORE_')
        The resulting dictionary `image_store` would look like::
            {
                'type': 'fs',
                'path': '/var/app/images',
                'base_url': 'http://img.website.com'
            }
        This is often useful when configuration options map directly to
        keyword arguments in functions or class constructors.
        :param namespace: a configuration namespace
        :param lowercase: a flag indicating if the keys of the resulting
                          dictionary should be lowercase
        :param trim_namespace: a flag indicating if the keys of the resulting
                          dictionary should not include the namespace
        .. versionadded:: 1.0
        """
        rv = {}
        for k, v in iteritems(self):
            if not k.startswith(namespace):
                continue
            if trim_namespace:
                key = k[len(namespace):]
            else:
                key = k
            if lowercase:
                key = key.lower()
            rv[key] = v
        return rv

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))

    if __name__ == '__main__':
        header_description = OrderedDict(
            [
                ('position', ("#", 2, ">")),
                ('team', ("Team", 30, "<")),
                ('played_games', ("Plyd", 4, ">")),
                ('goals', ("GlsF", 4, ">")),
                ('goals_against', ("GlsA", 4, ">")),
                ('goal_difference', ("GD", 4, ">")),
                ('points', ("Pts", 4, ">"))
            ]
        )
        for x in header_description.items():
            say(x)
        header = OutputHelper(header_description)
        say(header.header())
        say(header.underline())

        another = OrderedDict(
            [
                ('One', (1, 2, 3)),
                ('Two', (4, 5, 6)),
                ('Three', (7, 8, 9))
            ]
        )
        say(another)
        for x in another.items():
            say(x)


