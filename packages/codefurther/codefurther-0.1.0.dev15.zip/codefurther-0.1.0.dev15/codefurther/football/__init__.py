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

__all__= [
    'FootballDataBase', 'FootballLeague', 'premier_league', 'bundesliga_1',
    'chelsea', 'manchester_city', 'arsenal', 'manchester_united',
    'southampton', 'liverpool', 'tottenham', 'west_ham',
    'swansea', 'stoke', 'newcastle', 'everton', 'crystal_palace',
    'west_brom', 'hull', 'sunderland', 'qpr', 'burnley',
    'aston_villa', 'leicester'
    'la_liga', 'real_madrid', 'barcelona'
]

from codefurther.football.football import FootballDataBase, FootballLeague, \
    FootballTeam, premier_league, bundesliga_1, la_liga, \
    chelsea, manchester_city, arsenal, manchester_united, \
    southampton, liverpool, tottenham, west_ham, \
    swansea, stoke, newcastle, everton, crystal_palace, \
    west_brom, hull, sunderland, qpr, burnley, \
    aston_villa, leicester, \
    real_madrid, barcelona