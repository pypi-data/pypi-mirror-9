# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    ven 31 ott 2008 16:56:00 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from . import FunctionalTestCase


class TestPdf(FunctionalTestCase):

    def test_participants(self):
        self.app.get('/pdf/participants/1')

    def test_ranking(self):
        self.app.get('/pdf/ranking/1')

    def test_ranking_for_turn(self):
        self.app.get('/pdf/ranking/1?turn=1')

    def test_nationalranking(self):
        self.app.get('/pdf/nationalranking/1')

    def test_nationalranking_for_turn(self):
        self.app.get('/pdf/nationalranking/1?turn=1')

    def test_results(self):
        self.app.get('/pdf/results/1')

    def test_all_results(self):
        self.app.get('/pdf/results/1?turn=0')
        self.app.get('/pdf/results/1?turn=all')

    def test_matches(self):
        self.app.get('/pdf/matches/1')

    def test_scorecards(self):
        self.app.get('/pdf/scorecards/1')

    def test_blank_scorecards(self):
        self.app.get('/pdf/scorecards/blank')

    def test_badges(self):
        self.app.get('/pdf/badges/1')

    def test_championshipranking(self):
        self.app.get('/pdf/championshipranking/1')

    def test_ratingranking(self):
        self.app.get('/pdf/ratingranking/1')


class TestPdfByGuid(FunctionalTestCase):

    def test_participants(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/pdf/participants/%s' % tourney.guid)

    def test_ranking(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/pdf/ranking/%s' % tourney.guid)

    def test_nationalranking(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/pdf/nationalranking/%s' % tourney.guid)

    def test_results(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/pdf/results/%s' % tourney.guid)

    def test_all_results(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/pdf/results/%s?turn=0' % tourney.guid)
        self.app.get('/pdf/results/%s?turn=all' % tourney.guid)

    def test_matches(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/pdf/matches/%s' % tourney.guid)

    def test_scorecards(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/pdf/scorecards/%s' % tourney.guid)

    def test_badges(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/pdf/badges/%s' % tourney.guid)

    def test_championshipranking(self):
        from ...models import DBSession, Championship

        s = DBSession()
        cship = s.query(Championship).first()
        self.app.get('/pdf/championshipranking/%s' % cship.guid)

    def test_ratingranking(self):
        from ...models import DBSession, Rating

        s = DBSession()
        r = s.query(Rating).first()
        self.app.get('/pdf/ratingranking/%s' % r.guid)
