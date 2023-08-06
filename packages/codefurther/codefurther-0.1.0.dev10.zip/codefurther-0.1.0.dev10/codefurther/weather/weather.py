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
from booby import Model, fields
from booby.validators import Validator, nullable
from booby.decoders import Decoder
from booby.encoders import Encoder
import booby.errors
from codefurther import cf_config
from codefurther.errors import CodeFurtherWeatherError
from codefurther.helpers import vic_decode, FoundMixin, FORECAST_SETTINGS
import arrow

import forecastio
from gmaps import Geocoding
import arrow
from say import fmt
import re

# Check that the FORECASTIO_API_KEY is set
for setting in FORECAST_SETTINGS:
    if setting not in cf_config or cf_config[setting] is None:
        raise ValueError(fmt("The essential CodeFurther setting: {setting} has not been set. Weather forecasts cannot be accessed."))


geocoder = Geocoding()

"""
class ArrowEncoder(Encoder):
    def __init__(self, format=None):
        self._format = format

    @nullable
    def encode(self, value):
        if self._format is None:
            return value.isoformat()

        return value.strftime(self._format)


class ArrowDecoder(Decoder):
    def __init__(self, format=None):
        self._format = format

    @nullable
    def decode(self, value):
        format = self._format_for(value)

        try:
            return arrow.Arrow.strptime(value, format)
        except ValueError:
            raise booby.errors.DecodeError()

    def _format_for(self, value):
        if self._format is not None:
            return self._format

        format = '%Y-%m-%dT%H:%M:%S'

        if self._has_microseconds(value):
            format += '.%f'

        return format

    def _has_microseconds(self, value):
        return re.match('^.*\.[0-9]+$', value) is not None


class ArrowInteger(fields.Integer):
    def __repr__(self):
        print("__REPR__ CALLED.")
        return fmt("ArrowInteger({self:%d})")

    def __str__(self):
        print("__STR__ called.")
        return arrow.get(self).format('YYYY-MM-DD HH:mm:ss ZZ')


class Test(Model):
    time = ArrowInteger()

class OuterModel(Model):
    def __init__(self, *args, **kwargs):
        print("OuterModel CALLED")
        super(OuterModel, self).__init__(*args, **kwargs)
"""

class DailyWeather(FoundMixin, Model):
    what_am_i = "Weather forecast"
    format_string = "{self.summary} The temperature will be between {self.temperature_min} and {self.temperature_max}."

    def __init__(self, *args, **kwargs):
        super(DailyWeather, self).__init__(*args, **kwargs)

    actual_max_temp = fields.Float(name='apparentTemperatureMax')
    actual_min_temp = fields.Float(name='apparentTemperatureMin')
    actual_max_temp_when = fields.Integer(name='apparentTemperatureMaxTime')
    actual_min_temp_when = fields.Integer(name='apparentTemperatureMinTime')
    cloud_cover = fields.Float(name='cloudCover')
    dew_point = fields.Float(name='dewPoint')
    humidity = fields.Float(name='humidity')
    icon = fields.String(name='icon')
    moon_phase = fields.Float(name='moonPhase')
    ozone = fields.Float(name='ozone')
    precip_intensity = fields.Float(name='precipIntensity')
    precip_intensity_max = fields.Float(name='precipIntensityMax')
    precip_intensity_max_when = fields.Integer(name='precipIntensityMaxTime')
    precip_probability = fields.Float(name='precipProbability')
    precip_type = fields.String(name='precipType')
    pressure = fields.Float(name='pressure')
    summary = fields.String(name='summary')
    sunrise_time = fields.Integer(name='sunriseTime')
    sunset_time = fields.Integer(name='sunsetTime')
    temperature_max = fields.Float(name='temperatureMax')
    temperature_max_when = fields.Integer(name='temperatureMaxTime')
    temperature_min = fields.Float(name='temperatureMin')
    temperature_min_when = fields.Integer(name='temperatureMinTime')
    time = fields.Integer(name='time')
    visibility = fields.Float(name='visibility')
    wind_bearing = fields.Integer(name='windBearing')
    wind_speed = fields.Float(name='windSpeed')


class Weather:
    def __init__(self):
        self.geocoder = Geocoding()

    def f_to_c(self, fahrenheit):
        return

    def _get_lat_lng(self, address):
        response = self.geocoder.geocode(address)
        if not response:
            return None, None
        location = response[0]['geometry']['location']
        return location['lat'], location['lng']

    def _future_forecast(self, address):
        #todo Error checking required here
        lat, lng = self._get_lat_lng(address)
        if lat is None:
            raise CodeFurtherWeatherError(
                fmt("We can't find a weather forecast for: {address}")
            )
        #todo Error checking required here
        forecast = forecastio.load_forecast(vic_decode(cf_config['CF_FORECASTIO_API_KEY']), lat, lng, units='uk')
        daily = forecast.daily()
        #: daily.data is a list of daily forecasts. daily.data[0] is today's 'forecast'
        #: daily.data[1-7] are the forecasts for the next 7 days

        return daily

    def _specific_day_forecast(self,address, days):
        try:
            if days not in range(0, 7):
                raise CodeFurtherWeatherError(
                    fmt("We can't find a weather forecast for: {address} for: {days} days from now.")
                )
            weeks_forecast = self._future_forecast(address)
        except CodeFurtherWeatherError as e:
            dw = DailyWeather()
            dw.set_found(False, str(e))
            return dw

        #: Grab the forecast dictionary
        day_forecast = weeks_forecast.data[days].d

        #: Create a DailyWeather instance and decode the day_forecast from forecastio
        dw = DailyWeather(**DailyWeather.decode(day_forecast))

        return dw



    def tomorrow(self, address):
        ret = self._specific_day_forecast(address, 1)
        return ret

    def today(self, address):
        ret = self._specific_day_forecast(address, 0)
        return ret

    def day(self, address, days):
        return self._specific_day_forecast(address, days)

    def daily(self, address):
        try:
            ret = self._future_forecast(address)
        except CodeFurtherWeatherError as e:
            return [str(e)]

        for daily in ret.data:
            day_forecast = daily.d
            dw = DailyWeather(**DailyWeather.decode(day_forecast))
            yield dw

"""
{
    'types': ['street_address'],
    'address_components': [
        {
            'short_name': '36',
            'types': [
                'street_number'
            ],
            'long_name': '36'
        },
        {
            'short_name': "St Andrew's Rd",
            'types': [
                'route'
            ],
            'long_name': "Saint Andrew's Road"
        },
        {
            'short_name': 'Gosport',
            'types': [
                'locality',
                'political'
            ],
            'long_name': 'Gosport'
        },
        {
            'short_name': 'Gosport',
            'types': [
                'postal_town'
            ],
            'long_name': 'Gosport'
        },
        {
            'short_name': 'Hants',
            'types': [
                'administrative_area_level_2',
                'political'
            ],
            'long_name': 'Hampshire'
        },
        {
            'short_name': 'GB',
            'types': [
                'country',
                'political'
            ],
            'long_name': 'United Kingdom'
        },
        {
            'short_name': 'PO12',
            'types': [
                'postal_code_prefix',
                'postal_code'
            ],
            'long_name': 'PO12'
        }
    ],
    'formatted_address': "36 Saint Andrew's Road, Gosport, Hampshire PO12, UK",
    'geometry': {
        'bounds': {
            'southwest': {'lng': -1.1380689, 'lat': 50.7937043},
            'northeast': {'lng': -1.1380506, 'lat': 50.7937059}
        },
        'location': {
            'lng': -1.1380506,
            'lat': 50.7937043
        },
        'location_type': 'RANGE_INTERPOLATED',
        'viewport': {
            'southwest': {
                'lng': -1.139408730291502,
                'lat': 50.7923561197085},
            'northeast': {
                'lng': -1.136710769708498,
                'lat': 50.7950540802915
            }
        }
    }
}
"""

if __name__ == '__main__':
    weather = Weather()
    location = input("Enter the location (Portsmouth, UK): ")
    location = "Portsmouth, UK" if location == "" else location
    t = weather.tomorrow(location)
    print(t)
    #print(t.temperatureMax)
    print(t.temperature_max)
    for day_forecast in weather.daily(location):
        print(
            "On",
            arrow.get(day_forecast.time).format('dddd D MMMM YYYY'),
            "the forecast will be",
            day_forecast
        )
    #test = Test(time=arrow.utcnow().timestamp)
    #print(test.time)
    #print(test.time.__repr__())
    #print(test.time.__str__())
