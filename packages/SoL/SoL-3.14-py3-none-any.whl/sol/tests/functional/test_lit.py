# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    sab 13 dic 2008 16:35:46 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from . import FunctionalTestCase


class TestLitViews(FunctionalTestCase):

    def test_index(self):
        self.app.get('/lit')

    def test_latest(self):
        self.app.get('/lit/latest')

    def test_championship(self):
        from ...models import DBSession, Championship

        s = DBSession()
        cship = s.query(Championship).first()
        self.app.get('/lit/championship/%s' % cship.guid)

    def test_tourney(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/lit/tourney/%s' % tourney.guid)

    def test_tourney_turn(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/lit/tourney/%s?turn=1' % tourney.guid)

    def test_tourney_player(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        player = tourney.competitors[0].player1
        self.app.get('/lit/tourney/%s?player=%s' % (tourney.guid, player.guid))

    def test_tourney_player_turn(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        player = tourney.competitors[0].player1
        self.app.get('/lit/tourney/%s?player=%s&turn=1' % (tourney.guid, player.guid))

    def test_player(self):
        from ...models import DBSession, Player

        s = DBSession()
        player = s.query(Player).first()
        self.app.get('/lit/player/%s' % player.guid)

    def test_players(self):
        self.app.get('/lit/players')

    def test_players_listing(self):
        from ...models import DBSession, Player

        s = DBSession()
        player = s.query(Player).first()
        self.app.get('/lit/players/%s/%s' % (player.lastname[0], player.nationality))

    def test_rating(self):
        from ...models import DBSession, Rating

        s = DBSession()
        rating = s.query(Rating).first()
        self.app.get('/lit/rating/%s' % rating.guid)

    def test_club(self):
        from ...models import DBSession, Club

        s = DBSession()
        club = s.query(Club).first()
        self.app.get('/lit/club/%s' % club.guid)

    def test_no_club(self):
        from webtest.app import AppError

        try:
            self.app.get('/lit/club/foo')
        except AppError as e:
            self.assertIn('400 Bad Request', str(e))
        else:
            assert False, "Should raise a 400 status"

    def test_emblem(self):
        from webtest.app import AppError

        response = self.app.get('/lit/emblem/emblem.png')
        assert response.headers['content-type'].startswith('image')

        try:
            self.app.get('/lit/emblem')
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"

        try:
            self.app.get('/lit/emblem/foo')
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"

    def test_portrait(self):
        from webtest.app import AppError

        response = self.app.get('/lit/portrait/portrait.png')
        assert response.headers['content-type'].startswith('image')

        try:
            self.app.get('/lit/portrait'),
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"

        try:
            self.app.get('/lit/portrait/foo')
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"
