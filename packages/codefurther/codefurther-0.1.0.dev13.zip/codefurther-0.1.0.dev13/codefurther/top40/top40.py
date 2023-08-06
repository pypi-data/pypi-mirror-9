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

"""The ``top40`` module contains the high level classes that are used to package the returned data such as
:py:class:`Entry`, :py:class:`Chart` and :py:class:`Change`.

In addition the :py:class:`Top40` class provides the main external interface into the module. Once an instance of the
:py:class:`Top40` class has been instantiated it can be used to return data from the remote API to the called program::

    from pythontop40 import Top40

    top40 = Top40()

    album_list = top40.albums
    singles_list = top40.singles

    albums_chart = top40.albums_chart
    singles_chart = top40.singles_chart

From there, the returned objects can be interrogated and interacted with::

    first_album = album_list[0]
    print( first_album.position )
    print( first_album.artist )

    print("The date of the singles chart is", singles_chart.date)
    print(The album_chart was retrieved from the server on", albums_chart.retrieved

And this, don't forget this::

    class Repo(Model):
         name = fields.String()
         owner = fields.Embedded(User)

    booby = Repo(
        name='Booby',
        owner={
            'login': 'jaimegildesagredo',
            'name': 'Jaime Gil de Sagredo'
        })

    print booby.to_json()
    '{"owner": {"login": "jaimegildesagredo", "name": "Jaime Gil de Sagredo"}, "name": "Booby"}'
"""
from __future__ import print_function
import tempfile
from codefurther.helpers import ApiWithCache

from future.standard_library import hooks

# Import urljoin for V2 and V3 - http://python-future.org/compatible_idioms.html
from say import fmt

with hooks():
    from urllib.parse import urljoin

__author__ = 'Danny Goodall'
import requests
import requests.exceptions
import requests_cache
from booby import Model, fields
from codefurther.errors import CodeFurtherConnectionError, CodeFurtherError, CodeFurtherHTTPError, CodeFurtherReadTimeoutError


class Change(Model):
    """The Change model that describes the change of this entry since last week's chart.

    This class isn't made publicly visible, so it should never really need to be initialised manually. That said,
    it is initialised by passing a series of keyword arguments, like so::

        change = Change(
            direction = "down",
            amount = 2,
            actual = -2
        )

    The model does not feature any validation.

    Args:
        \*\*kwargs: Keyword arguments with the fields values to initialize the model.
    Attributes:
        direction (str): The direction of the change "up" or "down".
        amount (int): The amount of change in chart position expressed as a positive integer.
        actual (int): The amount of the change in chart position expressed as positive or negative (or 0).
    Returns:
        :py:class:`Change`: The Change model instance created from the passed arguments.
    """
    direction = fields.String()
    amount = fields.Integer()
    actual = fields.Integer()


class Entry(Model):
    """The Entry model that contains the details about the chart entry, a Change Model is embedded in each Entry model.

    Args:
        position (:py:class:`int`): The position of this entry in the chart.
        previousPosition (:py:class:`int`): The position of this entry in the previous week's chart.
        numWeeks (:py:class:`int`): The number of weeks this entry has been in the chart.
        artist (:py:class:`str`): The name of the artist for this entry.
        title (:py:class:`str`): The title of this entry.
        change (:py:class:`Change`): The embedded change model that describes the change in position.
        status (:py:class:`str`): **NEW in dev6** The text status from the BBC chart - takes the format of
            "new" ¦ "up 3" ¦ "down 4" ¦ "non-mover". Not used in Ben Major's V1 API - optional
    Attributes:
        position (:py:class:`int`): The position of this entry in the chart.
        previousPosition (:py:class:`int`): The position of this entry in the previous week's chart.
        numWeeks (:py:class:`int`): The number of weeks this entry has been in the chart.
        artist (:py:class:`str`): The name of the artist for this entry.
        title (:py:class:`str`): The title of this entry.
        change (:py:class:`Change`): The embedded change model that describes the change in position.
        status (:py:class:`str`): **NEW in dev6** The text status from the BBC chart - takes the format of
            "new" ¦ "up 3" ¦ "down 4" ¦ "non-mover". Not used in Ben Major's V1 API - optional
    Returns:
        :class:`Entry`: The Entry model instance created from the arguments.
    """

    position = fields.Integer()
    previousPosition = fields.Integer()
    numWeeks = fields.Integer()
    artist = fields.String()
    title = fields.String()
    change = fields.Embedded(Change)

    # Status is optional
    status = fields.String(required=False)

    def __repr__(self):
        return fmt("{self.position:2d} {self.title:40} {self.artist:40} {self.numWeeks:4d} {self.previousPosition:4d}")


class Chart(Model):
    """The Chart model that contains the embedded list of entries.

    Args:
        entries (:py:class:`list` of :py:class:`dict`): A list of Python dictionaries. Each dictionary describes each
            :class:`Entry` type in the chart, so the keys in the dictionary should match the properties of the
            :class:`Entry` class.
        date (:py:class:`int`): The date of this chart as an integer timestamp containing the total number of seconds.
        retrieved (:py:class:`int`): The date that this chart was retrieved from the API server as an integer timestamp
            containing the total number of seconds.
        current (:py:class:`bool`): **Optional**. A flag used in V2 of the API to signify if the last scheduled read from the BBC's
            server worked on not. A value ``True`` means that the returned chart is the latest version that we have
            tried to read. A value of ``False`` means that the chart that is being returned is old. In all liekliehood
            the chart is probably still in accurate as it is only updated once per week, so this flag only means that
            the last scheduled read from the BBC's server did not work.
    Attributes:
        entries (:py:class:`list` of :py:class:`Entry`): A list of :py:class:`Entry` types for each entry in the
            specific :py:class:`Chart`. The entries are returned in the :py:class:`list` with the highest chart position
            (i.e. the lowest number - #1 in the chart) first.
        date (:py:class:`int`): The date of this chart as an integer timestamp containing the total number of seconds.
            This value can then be converted to a Python :py:class:`datetime.datetime` type by
            ``datetime_type = datetime.datetime.fromtimestamp(chart.date)``
            (assuming that the ``chart`` variable was of type :py:class:`Chart`).
        retrieved (:py:class:`int`): The date that this chart was retrieved from the API server as an integer timestamp
            containing the total number of seconds. This can be converted to a datetime type in the same as described
            for ``date`` above.
        current (:py:class:`bool`): **Optional**. A flag used in V2 of the API to signify if the last scheduled read from the BBC's
            server worked on not. A value ``True`` means that the returned chart is the latest version that we have
            tried to read. A value of ``False`` means that the chart that is being returned is old. In all liekliehood
            the chart is probably still in accurate as it is only updated once per week, so this flag only means that
            the last scheduled read from the BBC's server did not work.
    Returns:
        Chart (:py:class:`Chart`): The Chart model instance created from the arguments.

    """
    date = fields.Integer()
    retrieved = fields.Integer()
    entries = fields.Collection(Entry)
    current = fields.Boolean(required=False)


class Top40(ApiWithCache):
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
    base_url_default = "http://ben-major.co.uk/labs/top40/api/"

    def _get_albums_chart(self):
        """Internal routine to pull the albums chart information into the cache
        """
        albums = self._get_data("/albums")
        self.set_cache('albums_chart', Chart(**albums))


    @property
    def albums_chart(self):
        """A ``property`` that returns the :py:class:`Chart` object for the current Top40 albums

        Returns:
            :py:class:`Chart`: The albums' chart object - an instance of the :class:`Chart` class containing the album
                information and the and the issue and retrieval dates specific to this chart.
        Raises:
            Top40HTTPError (:py:class:`~errors.Top40HTTPError`): If a status code that is not 200 is returned
            Top40ConnectionError (:py:class:`~errors.Top40ConnectionError`): If a connection could not be established to the remote server
            Top40ReadTimeoutError (:py:class:`~errors.Top40ReadTimeoutError`): If the remote server took too long to respond
        """
        if self.get_cache('albums_chart') is None:
            self._get_albums_chart()
        return self.get_cache('albums_chart')

    @property
    def albums(self):
        """A ``property`` that returns a :py:class:`list` of album :py:class:`Entry` types.

        Returns:
            :py:class:`list` : A :py:class:`list` of :class:`Entry` instances. Each entry describes an album in the
                chart.
        Raises:
            Top40HTTPError (:py:class:`~errors.Top40HTTPError`): If a status code that is not 200 is returned
            Top40ConnectionError (:py:class:`~errors.Top40ConnectionError`): If a connection could not be established to the remote server
            Top40ReadTimeoutError (:py:class:`~errors.Top40ReadTimeoutError`): If the remote server took too long to respond
        """
        albums_chart = self.albums_chart
        return albums_chart.entries

    def _get_singles_chart(self):
        """Internal routine to pull the singles chart information into the cache
        """
        singles = self._get_data("/singles")
        self.set_cache('singles_chart', Chart(**singles))

    @property
    def singles_chart(self):
        """A ``property`` that returns the :py:class:`Chart` object for the current Top40 singles

        Returns:
            :py:class:`Chart`: The singles' chart object - an instance of the :class:`Chart` class containing the
                singles information and the issue and retrieval dates specific to this chart.
        Raises:
            Top40HTTPError (:py:class:`~errors.Top40HTTPError`): If a status code that is not 200 is returned
            Top40ConnectionError (:py:class:`~errors.Top40ConnectionError`): If a connection could not be established to the remote server
            Top40ReadTimeoutError (:py:class:`~errors.Top40ReadTimeoutError`): If the remote server took too long to respond
        """
        if self.get_cache('singles_chart') is None:
            self._get_singles_chart()
        return self.get_cache('singles_chart')

    @property
    def singles(self):
        """A ``property`` that returns a list of single entries.

        Returns:
            :py:class:`list`: A :py:class:`list` of :class:`Entry` instances. Each entry describes a single in the
                chart.
        Raises:
            Top40HTTPError (:py:class:`~errors.Top40HTTPError`): If a status code that is not 200 is returned
            Top40ConnectionError (:py:class:`~errors.Top40ConnectionError`): If a connection could not be established to the remote server
            Top40ReadTimeoutError (:py:class:`~errors.Top40ReadTimeoutError`): If the remote server took too long to respond
        """
        singles_chart = self.singles_chart
        return singles_chart.entries