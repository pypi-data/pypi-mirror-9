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
from collections import OrderedDict
from booby import Model
from codefurther.football.constants import CF_FB_LEAGUE_CODES, CF_FB_LEAGUE_NUMBERS, CF_FB_PREMIER_LEAGUE, \
    CF_FB_BUNDESLIGA_1, CF_FB_PRIMERA_DIVISION, CF_FB_TEAM_NUMBERS, CF_FB_MANCHESTER_UNITED, CF_FB_SOUTHAMPTON, \
    CF_FB_REAL_MADRID, CF_FB_BARCELONA, CF_FB_LIVERPOOL, CF_FB_MANCHESTER_CITY, CF_FB_CHELSEA, CF_FB_ARSENAL, \
    CF_FB_TOTTENHAM_HOTSPUR, CF_FB_SWANSEA_CITY, CF_FB_STOKE_CITY, CF_FB_WEST_HAM_UNITED, CF_FB_EVERTON, \
    CF_FB_NEWCASTLE_UNITED, CF_FB_SUNDERLAND, CF_FB_HULL_CITY, CF_FB_WEST_BROMWICH_ALBION, CF_FB_CRYSTAL_PALACE, \
    CF_FB_BURNLEY, CF_FB_QUEENS_PARK_RANGERS, CF_FB_LEICESTER_CITY, CF_FB_ASTON_VILLA
from codefurther.helpers import ApiWithCache, stufify, OutputHelper, FoundMixin
from stuf import stuf, orderedstuf
from say import say, fmt
from codefurther.football.models import FootballLeagueModel, FootballLeagueStandingModel, FootballTeamModel, \
    FootballFixturesModel, FootballFixtureModel, FootballPlayersModel, FootballPlayerModel


class FootballDataBase(ApiWithCache):
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
    base_url_default = "http://api.football-data.org/alpha/"
    extra_headers = {
        'x-auth-token': 'd436ea6d766a4f68aee6da3f6b88a53a'
    }

    def __init__(self, authentication=None, **kwargs):
        self.extra_headers['x-auth-token'] = authentication if authentication else {}
        super(ApiWithCache, self).__init__(**kwargs)


class FootballTeam(FootballDataBase):
    """A CodeFurther object that manages the collection of data associated with a football team
    """
    team_api_url = "teams/{team_number}"
    fixtures_api_url = "teams/{team_number}/fixtures"
    players_api_url = "teams/{team_number}/players"
    team_model = FootballTeamModel()
    fixtures_model = FootballFixturesModel()
    fixture_model = FootballFixtureModel()
    player_model = FootballPlayerModel()
    players_model = FootballPlayersModel()

    def __init__(self, team_number, **kwargs):
        if team_number not in CF_FB_TEAM_NUMBERS:
            raise ValueError(
                fmt(
                    "The team number: {team_number} is not recognised a a valid team number."
                )
            )
        self.team_number = team_number
        super(FootballDataBase, self).__init__(**kwargs)

    def _team_cache_id(self, team_number):
        return fmt('teamNumber/{team_number}')

    def _fixtures_cache_id(self, team_number):
        return fmt('fixtures/{team_number}')

    def _players_cache_id(self, team_number):
        return fmt('players/{team_number}')

    def _get_team(self, team_number):
        team_details = self._get_data(fmt(self.team_api_url))
        cache_id = self._team_cache_id(team_number)
        self.set_cache(cache_id, team_details)
        return self.get_cache(cache_id)

    def _get_fixtures(self, team_number):
        fixture_details = self._get_data(fmt(self.fixtures_api_url))
        cache_id = self._fixtures_cache_id(team_number)
        self.set_cache(cache_id, fixture_details)
        return self.get_cache(cache_id)

    def _get_players(self, team_number):
        player_details = self._get_data(fmt(self.players_api_url))
        cache_id = self._players_cache_id(team_number)
        self.set_cache(cache_id, player_details)
        return self.get_cache(cache_id)

    @property
    def team_heading(self):
        return self.team_model.heading

    @property
    def fixtures_heading(self):
        return self.fixture_model.heading

    @property
    def players_heading(self):
        return self.player_model.heading

    @property
    def team_underline(self):
        return self.team_model.underline

    @property
    def fixtures_underline(self):
        return self.fixture_model.underline

    @property
    def players_underline(self):
        return self.player_model.underline

    @property
    def team_headings(self):
        yield self.team_heading
        yield self.team_underline

    @property
    def fixtures_headings(self):
        yield self.fixtures_heading
        yield self.fixtures_underline

    @property
    def players_headings(self):
        yield self.players_heading
        yield self.players_underline

    def _team_details(self):
        if self.get_cache(self._team_cache_id(self.team_number)) is None:
            self._get_team(self.team_number)

        team_raw = self._get_cache_or_none(self._team_cache_id(self.team_number))
        team_details = FootballTeamModel(**FootballTeamModel.decode(team_raw))

        return team_details

    team_details = property(_team_details)

    def _fixtures_details(self):
        if self.get_cache(self._fixtures_cache_id(self.team_number)) is None:
            self._get_fixtures(self.team_number)

        fixtures_raw = self._get_cache_or_none(self._fixtures_cache_id(self.team_number))
        fixture_details = FootballFixturesModel(**FootballFixturesModel.decode(fixtures_raw))

        return fixture_details.fixtures

    fixtures = property(_fixtures_details)

    def _players_details(self):
        if self.get_cache(self._players_cache_id(self.team_number)) is None:
            self._get_players(self.team_number)

        players_raw = self._get_cache_or_none(self._players_cache_id(self.team_number))
        players_details = FootballPlayersModel(**FootballPlayersModel.decode(players_raw))

        return players_details.players

    players = property(_players_details)


class FootballLeague(FootballDataBase):
    """A CodeFurther object that manages the collection of data assoicated with a football league
    """
    api_url = "soccerseasons/{league_number}/leagueTable/"
    league_model = FootballLeagueModel()

    def __init__(self, league_number, **kwargs):
        if league_number not in CF_FB_LEAGUE_NUMBERS:
            raise ValueError(fmt("The league_number: {league_number} is not recognised as a valid league number."))
        self.league_number = league_number
        super(FootballDataBase, self).__init__(**kwargs)

    def _table_cache_id(self, league_number):
        return fmt('leagueTable/{league_number}')

    def _get_league(self, league_number):
        league_details = self._get_data(fmt(self.api_url))
        cache_id = self._table_cache_id(league_number)
        self.set_cache(cache_id,league_details)
        return self.get_cache(cache_id)

    @property
    def league_raw(self):
        """A ``property`` that returns a the league details.

        Returns:
            :py:class:`stuf`: A :py:class:`stuf` that describes the league.
        Raises:
            CodeFurtherHTTPError (:py:class:`~errors.CodeFurtherHTTPError`): If a status code that is not 200 is returned
            CodeFurtherConnectionError (:py:class:`~errors.CodeFurtherConnectionError`): If a connection could not be established to the remote server
            CodeFurtherReadTimeoutError (:py:class:`~errors.CodeFurtherReadTimeoutError`): If the remote server took too long to respond
        """
        if self.get_cache(self._table_cache_id(self.league_number)) is None:
            self._get_league(self.league_number)

        return self._get_cache_or_none(self._table_cache_id(self.league_number))

    @property
    def league_heading(self):
        return self.league_model.heading

    @property
    def league_underline(self):
        return self.league_model.underline

    @property
    def league_headings(self):
        yield self.league_heading
        yield self.league_underline

    def _league_table(self):
        league_table = FootballLeagueModel(**FootballLeagueModel.decode(self.league_raw))
        for standing_entry in league_table.standing:
            yield standing_entry

    league_table = property(_league_table)




premier_league = FootballLeague(CF_FB_PREMIER_LEAGUE)
bundesliga_1 = FootballLeague(CF_FB_BUNDESLIGA_1)
la_liga = FootballLeague(CF_FB_PRIMERA_DIVISION)

chelsea = FootballTeam(CF_FB_CHELSEA)
manchester_city = FootballTeam(CF_FB_MANCHESTER_CITY)
arsenal = FootballTeam(CF_FB_ARSENAL)
manchester_united = FootballTeam(CF_FB_MANCHESTER_UNITED)
southampton = FootballTeam(CF_FB_SOUTHAMPTON)
liverpool = FootballTeam(CF_FB_LIVERPOOL)
tottenham = FootballTeam(CF_FB_TOTTENHAM_HOTSPUR)
west_ham = FootballTeam(CF_FB_WEST_HAM_UNITED)
swansea = FootballTeam(CF_FB_SWANSEA_CITY)
stoke = FootballTeam(CF_FB_STOKE_CITY)
newcastle = FootballTeam(CF_FB_NEWCASTLE_UNITED)
everton = FootballTeam(CF_FB_EVERTON)
crystal_palace = FootballTeam(CF_FB_CRYSTAL_PALACE)
west_brom = FootballTeam(CF_FB_WEST_BROMWICH_ALBION)
hull = FootballTeam(CF_FB_HULL_CITY)
sunderland = FootballTeam(CF_FB_SUNDERLAND)
qpr = FootballTeam(CF_FB_QUEENS_PARK_RANGERS)
burnley = FootballTeam(CF_FB_BURNLEY)
aston_villa = FootballTeam(CF_FB_ASTON_VILLA)
leicester = FootballTeam(CF_FB_LEICESTER_CITY)

barcelona = FootballTeam(CF_FB_BARCELONA)
real_madrid = FootballTeam(CF_FB_REAL_MADRID)

if __name__ == '__main__':
    say("{premier_league.league_heading}")
    say("{premier_league.league_underline}")
    for entry in premier_league.league_table:
        say("{entry}")
    say()
    say()

    for team_number in CF_FB_TEAM_NUMBERS:
        say()
        say()
        team = FootballTeam(team_number)
        say("{team.team_heading}")
        say("{team.team_underline}")
        say("{team.team_details}")
        say()
        say("    {team.players_heading}")
        say("    {team.players_underline}")
        say()
        total_market_value = float(0.0)
        for player in team.players:
            say("    {player}")
            total_market_value += player.market_value
        say("    Total market value is: {total_market_value:15,.0f}")
        say()
        say()
        say("        {southampton.fixtures_heading}")
        say("        {southampton.fixtures_underline}")
        for fixture in southampton.fixtures:
            say("        {fixture}")

    say("{CF_FB_TEAM_NUMBERS}")