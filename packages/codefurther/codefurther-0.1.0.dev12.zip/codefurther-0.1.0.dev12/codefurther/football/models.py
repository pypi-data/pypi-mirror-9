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
from re import sub
import arrow
from booby.decoders import Decoder
from booby.encoders import Encoder
from booby.helpers import nullable
from codefurther.helpers import FoundMixin, CF_BAD_DATE
from booby import Model, fields
from collections import OrderedDict
from say import fmt


class DecodeCurrencyToFloat(Decoder):

    #@nullable
    def decode(self, value):
        try:
            ret = float(sub(r'[^\d.]', '', value)) if value else 0.00
        except ValueError:
            ret =  float(0)
        return ret

class DecodeStringToArrow(Decoder):
    def __init__(self, fmt=None):
        self.fmt=fmt if fmt else 'YYYY-MM-DD'

    def decode(self, value):
        try:
            ret = arrow.get(value, self.fmt)
        except:
            ret = CF_BAD_DATE

        return ret

class EncodeArrowToString(Encoder):
    def __init__(self, fmt=None):
        self.fmt = fmt if fmt else 'DD-MMM-YYYY'

    def encode(self, value):
        return value.format(self.fmt)


def arrow_tos(value, fmt=None):
    fmt = fmt if fmt else "DD-MMM-YYYY"
    assert isinstance(value, arrow.Arrow)
    try:
        value = value.format(fmt)
    except:
        value = CF_BAD_DATE

    return value

class FootballLeagueStandingModel(FoundMixin, Model):
    what_am_i = "Football League Standing"

    format_string = "{self.position:2d} {self.team_name:30} " \
                    "{self.games_played:4d} {self.goals_for:4} " \
                    "{self.goals_against:4} {self.goal_difference:4} " \
                    "{self.points:4d}"

    links = fields.Field(name="_links")
    position = fields.Integer(name="position")
    team_name = fields.String(name="teamName")
    games_played = fields.Integer(name="playedGames")
    points = fields.Integer(name="points")
    goals_for = fields.Integer(name="goals")
    goals_against = fields.Integer(name="goalsAgainst")
    goal_difference = fields.Integer(name="goalDifference")


class FootballLeagueModel(FoundMixin, Model):
    what_am_i = "Football League Table"
    format_string = ""
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

    links = fields.Field(name="_links")
    league_caption = fields.String(name="leagueCaption")
    matchday = fields.Integer(name="matchday")
    standing = fields.Collection(FootballLeagueStandingModel)


class FootballTeamModel(FoundMixin, Model):
    what_am_i = "Football Team Summary"
    format_string = "{self.name:30} ({self.short_name:30}) " \
                    "{self.squad_value:15,.0f} " \
                    "{self.crest_url}"
    header_description = OrderedDict(
        [
            ('name', ("Team name", 30, "<")),
            ('short_name', ("Short name", 32, "<")),
            ('squad_value', ("Squad value", 15, ">")),
            ('crest_url', ("Crest URL", 100, "<"))
        ]
    )

    links = fields.Field(name="_links")
    name = fields.String(name="name")
    code = fields.Field(name="code")
    short_name = fields.String(name="shortName")
    squad_value = fields.Float(name="squadMarketValue", decoders=[DecodeCurrencyToFloat()])
    crest_url = fields.String(name="crestUrl")

class FootballResultModel(FoundMixin, Model):
    what_am_i = "Football Result"
    format_string = "{self.result_format}"

    home_goals = fields.Integer(name="goalsHomeTeam")
    away_goals = fields.Integer(name="goalsAwayTeam")

    @property
    def result_format(self):
        return fmt(
            "{self.home_goals:2d} -{self.away_goals:2d}"
        ) if self.home_goals != -1 else "   -  "

class FootballFixtureModel(FoundMixin, Model):

    what_am_i = "Football Fixture"
    format_string = "{self.match_day:3d} " \
                    "{self.formatted_date:22} " \
                    "{self.result} " \
                    "{self.home_team_name:30} " \
                    "v " \
                    "{self.away_team_name:30}"
    header_description = OrderedDict(
        [
            ('match_day', ("#", 3, ">")),
            ('formatted_date', ("Match date", 22, "<")),
            ('result', ("Result", 6, "<")),
            ('home_team_name', ("Home team", 30, "<")),
            ('v', ("v", 1, "<")),
            ('away_team_name', ("Away team", 30, "<"))
        ]
    )

    links = fields.Field(name="_links")
    date = fields.String(name="date")
    match_day = fields.Integer(name="matchday")
    home_team_name = fields.String(name="homeTeamName")
    away_team_name = fields.String(name="awayTeamName")
    result = fields.Embedded(FootballResultModel)

    @property
    def formatted_date(self):
        return arrow.get(self.date).format("dddd D MMM YYYY")


class FootballFixturesModel(FoundMixin, Model):

    what_am_i = "Football Fixtures List"
    format_string = "{self.count}"

    links = fields.Field(name="_links")
    count = fields.Integer(name="count")
    fixtures = fields.Collection(FootballFixtureModel)



class FootballPlayerModel(FoundMixin, Model):
    what_am_i = "Football Player"
    format_string = "{self.formatted_squad_number:3d} " \
                    "{self.name:30} " \
                    "{self.position:20} " \
                    "{self.nationality:20} " \
                    "{self.formatted_date_of_birth} " \
                    "{self.formatted_contract_expires} " \
                    "{self.market_value:15,.0f}"
                    # "{self.formatted_contract_expires:10} " \
    header_description = OrderedDict(
        [
            ('squad_number', ("#", 3, ">")),
            ('name', ("Name", 30, "<")),
            ('position', ("Position", 20, "<")),
            ('nationality', ("Nationality", 20, "<")),
            ('date_of_birth', ("Birth date", 11, "<")),
            ('contract_expires', ("Can leave", 11, "<")),
            ('market_value', ("Market value", 15, ">"))
        ]
    )

    name = fields.String(name="name")
    position = fields.String(name="position")
    squad_number = fields.Integer(name="jerseyNumber")
    date_of_birth = fields.String(name="dateOfBirth", decoders=[DecodeStringToArrow()], encoders=[EncodeArrowToString()])
    nationality = fields.String(name="nationality")
    contract_expires = fields.String(name="contractUntil", decoders=[DecodeStringToArrow()], encoders=[EncodeArrowToString()])
    market_value = fields.Float(0.0, name="marketValue", decoders=[DecodeCurrencyToFloat()])

    @property
    def formatted_squad_number(self):
        return 0 if self.squad_number is None else self.squad_number

    @property
    def formatted_contract_expires(self):
        return arrow_tos(self.contract_expires)

    @property
    def formatted_date_of_birth(self):
        return arrow_tos(self.date_of_birth)


class FootballPlayersModel(FoundMixin, Model):
    what_am_i = "Football Players List"
    format_string = "{self.count}"

    links = fields.Field(name="_links")
    count = fields.Integer(name="count")
    players = fields.Collection(FootballPlayerModel)
