# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Test environment
# :Creato:    sab 27 set 2008 14:19:56 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import unittest

import transaction

from ..models import Base, DBSession, wipe_database

from .data import (
    ChampionshipData,
    ClubData,
    ClubSpec,
    CompetitorData,
    Fixture,
    MatchData,
    ONEDAY,
    PlayerData,
    RateData,
    RatingData,
    TODAY,
    TourneyData,
    )


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s = DBSession()
        with transaction.manager:
            Fixture.initialize(s)

    @classmethod
    def tearDownClass(cls):
        wipe_database()


_schema_created = False
def setUpModule():
    from pyramid.paster import get_appsettings
    from pyramid.scripts.common import logging_file_config
    from sqlalchemy import engine_from_config
    global _schema_created

    if _schema_created: return

    logging_file_config('../test.ini')
    settings = get_appsettings('../test.ini')
    engine = engine_from_config(settings, 'sqlalchemy.')

    DBSession.configure(bind=engine)
    Base.metadata.create_all(DBSession.bind)

    _schema_created = True
