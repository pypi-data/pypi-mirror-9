# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Basic tests on the DB modelization
# :Creato:    lun 22 set 2008 16:13:43 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from decimal import Decimal
import logging
from operator import attrgetter

import transaction
from sqlalchemy.orm.exc import NoResultFound

from sol import models
from sol.models.errors import OperationAborted
from sol.tests import (
    ClubData,
    ClubSpec,
    ONEDAY,
    PlayerData,
    RateData,
    RatingData,
    ChampionshipData,
    TODAY,
    TestCase,
    TourneyData,
    )


class TestModels(TestCase):
    def test_club(self):
        s = models.DBSession()
        ecc = s.query(models.Club).filter_by(description=ClubData.ecc.description).one()
        self.assertEqual(ecc.country, 'Europe')

    def test_player(self):
        s = models.DBSession()
        juri = s.query(models.Player) \
               .filter_by(firstname=PlayerData.juri.firstname).one()
        self.assertEqual(juri.lastname, PlayerData.juri.lastname)
        self.assert_(juri.description)

        p = juri.partecipations()
        self.assert_(p)

        m = juri.matchesSummary()
        self.assertEqual(len(m), 4)

        o = juri.opponents()
        self.assertEqual(len(o), 3)

        lele = s.query(models.Player) \
               .filter_by(firstname=PlayerData.lele.firstname).one()

        m = juri.opponentMatches(lele)
        self.assertEqual(len(m), 2)

    def test_player_nickname_as_username(self):
        s = models.DBSession()
        danieled = s.query(models.Player) \
                    .filter_by(firstname=PlayerData.danieled.firstname).one()

        danieled.nickname = 'dd'
        self.assertFalse(danieled.shouldOmitNickName())

        danieled.nickname = PlayerData.danieled.firstname
        self.assertTrue(danieled.shouldOmitNickName())

        danieled.nickname = PlayerData.danieled.lastname
        self.assertTrue(danieled.shouldOmitNickName())

        danieled.nickname = 'da fattid'
        self.assertTrue(danieled.shouldOmitNickName())

        danieled.nickname = 'dafattid'
        self.assertTrue(danieled.shouldOmitNickName())

        danieled.nickname = 'ddafatti'
        self.assertTrue(danieled.shouldOmitNickName())

        danieled.nickname = 'dda fatti'
        self.assertTrue(danieled.shouldOmitNickName())

        danieled.nickname = 'danieled'
        self.assertTrue(danieled.shouldOmitNickName())

        danieled.nickname = 'ddaniele'
        self.assertTrue(danieled.shouldOmitNickName())

    def test_federated_player(self):
        s = models.DBSession()
        elisa = s.query(models.Player) \
               .filter_by(firstname=PlayerData.elisam.firstname).one()
        self.assertEqual(elisa.lastname, PlayerData.elisam.lastname)
        self.assertEqual(elisa.federation.description,
                         ClubData.fic.description)

    def test_competitor(self):
        s = models.DBSession()
        fcomp1 = s.query(models.Competitor).first()
        desc = fcomp1.description
        self.assertEqual(
            desc, "<b>Gaifas</b> Emanuele “Lele” and <b>Turchina</b> Fata")

    def test_match(self):
        s = models.DBSession()
        match = s.query(models.Match).first()
        desc = match.description
        self.assertIn('vs.', desc)

    def test_previous_championship(self):
        s = models.DBSession()
        championship = s.query(models.Championship) \
                 .filter_by(description=ChampionshipData.next.description).one()
        self.assertEqual(championship.previous.description, ChampionshipData.current.description)

    def test_merge(self):
        s = models.DBSession()
        juri = s.query(models.Player) \
                .filter_by(firstname=PlayerData.juri.firstname).one()
        self.assertIsNone(juri.sex)
        self.assertEqual(juri.merged, [])
        tobemerged = s.query(models.Player) \
                     .filter_by(firstname=PlayerData.merge1.firstname).all()
        tobemerged_guids = [p.guid for p in tobemerged]
        merge1_id, = [p.idplayer for p in tobemerged
                     if p.lastname == PlayerData.merge1.lastname]
        juri.mergePlayers([p.idplayer for p in tobemerged])
        s.flush()
        self.assertEqual(set(m.guid for m in juri.merged), set(tobemerged_guids))
        self.assertEqual(juri.sex, PlayerData.merge1.sex)
        self.assertEqual(juri.email, PlayerData.juri.email)
        tobemerged = s.query(models.Player) \
                     .filter_by(firstname=PlayerData.merge1.firstname).all()
        self.assertEqual(tobemerged, [])
        merge1_rates = s.query(models.Rate).filter_by(idplayer=merge1_id).all()
        self.assertEqual(merge1_rates, [])

        bob = s.query(models.Player) \
              .filter_by(firstname=PlayerData.bob.firstname).one()
        try:
            bob.mergePlayers([juri.idplayer])
        except OperationAborted:
            pass
        else:
            assert False, "Should have raised an error!"

    def test_merge_guid(self):
        s = models.DBSession()
        pk = s.query(models.Player) \
              .filter_by(lastname=PlayerData.pk.lastname).one()
        self.assertEqual(pk.merged, [])
        tobemerged = s.query(models.Player) \
                     .filter_by(firstname=PlayerData.merge3.firstname).all()
        tobemerged_guids = [p.guid for p in tobemerged]
        pk.mergePlayers(tobemerged_guids)
        s.flush()
        self.assertIn(tobemerged_guids[0], set(m.guid for m in pk.merged))
        tobemerged = s.query(models.Player) \
                     .filter_by(firstname=PlayerData.merge3.firstname).all()
        self.assertEqual(tobemerged, [])
        player, merged_into = models.Player.find(s,
                                                 PlayerData.merge3.lastname,
                                                 PlayerData.merge3.firstname)
        self.assertIs(player, pk)
        self.assertTrue(merged_into)

    def test_rating(self):
        s = models.DBSession()
        rating = s.query(models.Rating) \
                 .filter_by(description=RatingData.national.description).one()
        self.assertEqual(rating.description, RatingData.national.description)

    def test_guid(self):
        s = models.DBSession()
        juri = s.query(models.Player) \
               .filter_by(firstname=PlayerData.juri.firstname).one()
        self.assertIsNotNone(juri.modified)
        self.assertIsNotNone(juri.guid)

    def test_readonly_guid(self):
        s = models.DBSession()
        juri = s.query(models.Player) \
               .filter_by(firstname=PlayerData.juri.firstname).one()
        with self.assertRaises(ValueError):
            juri.guid = 'foo'

    def test_owned_club(self):
        s = models.DBSession()
        owned = s.query(models.Club) \
               .filter_by(description=ClubSpec.owned.description).one()
        lele = s.query(models.Player) \
               .filter_by(firstname=PlayerData.lele.firstname).one()
        self.assertEqual(owned.owner, lele)

    def test_owned_championship(self):
        s = models.DBSession()
        owned = s.query(models.Championship) \
               .filter_by(description=ChampionshipData.current.description).one()
        lele = s.query(models.Player) \
               .filter_by(firstname=PlayerData.lele.firstname).one()
        self.assertEqual(owned.owner, lele)

    def test_owned_player(self):
        s = models.DBSession()
        fata = s.query(models.Player) \
               .filter_by(firstname=PlayerData.fata.firstname).one()
        lele = s.query(models.Player) \
               .filter_by(firstname=PlayerData.lele.firstname).one()
        self.assertEqual(fata.owner, lele)

    def test_owned_rating(self):
        s = models.DBSession()
        owned = s.query(models.Rating) \
               .filter_by(description=RatingData.standalone.description).one()
        lele = s.query(models.Player) \
               .filter_by(firstname=PlayerData.lele.firstname).one()
        self.assertEqual(owned.owner, lele)

    def test_owned_tourney(self):
        s = models.DBSession()
        owned = s.query(models.Tourney) \
               .filter_by(description=TourneyData.first.description).one()
        lele = s.query(models.Player) \
               .filter_by(firstname=PlayerData.lele.firstname).one()
        self.assertEqual(owned.owner, lele)



class TestRating(TestCase):
    def test_rates(self):
        s = models.DBSession()

        lele = s.query(models.Player) \
               .filter_by(nickname=PlayerData.lele.nickname).one()

        rating = s.query(models.Rating) \
                 .filter_by(description=RatingData.national.description).one()

        latest_rate = rating.getPlayerRating(lele)
        self.assertEqual(latest_rate.mu, RateData.lele_tomorrow.rate)

        previous_rate = rating.getPlayerRating(lele, RateData.lele_today.date)
        self.assertEqual(previous_rate.mu, RateData.lele_yesterday.rate)

    def test_ratings_level(self):
        s = models.DBSession()

        varechina = s.query(models.Player) \
                     .filter_by(lastname=PlayerData.varechina.lastname).one()

        rating = s.query(models.Rating) \
                 .filter_by(description=RatingData.national.description).one()

        varechina_rate = rating.getPlayerRating(varechina)
        self.assertEqual(varechina_rate.mu, RateData.varechina_european.rate)

    def test_standalone_ratings_level(self):
        s = models.DBSession()

        varechina = s.query(models.Player) \
                     .filter_by(lastname=PlayerData.varechina.lastname).one()

        rating = s.query(models.Rating) \
                 .filter_by(description=RatingData.standalone.description).one()

        varechina_rate = rating.getPlayerRating(varechina)
        self.assertEqual(varechina_rate.mu, RateData.varechina_standalone.rate)

    def test_competitor(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.rated.description).one()
        c = t.competitors[0]
        self.assertEqual(c.player1.nickname, PlayerData.lele.nickname)
        self.assertEqual(c.rate, RateData.lele_tomorrow.rate)

    def test_recompute(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.rated.description).one()
        t.assignPrizes()

        c = t.competitors[0]
        r = t.rating.getPlayerRating(c.player1)
        self.assertEqual(r.rate, 1492)
        self.assertEqual(r.deviation, 151)
        self.assertEqual(r.volatility, Decimal('0.05999'))

    def test_recompute_exponential(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.rated_exponential.description).one()
        ranking = t.ranking
        self.assertEqual(len(ranking), 2)
        t.assignPrizes()
        c = t.competitors[0]
        r = t.rating.getPlayerRating(c.player1)
        self.assertEqual(r.rate, 1595)

    def test_first_turn(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.rated_no_turns.description).one()
        self.assertEqual(t.matches, [])
        t.makeNextTurn()
        self.assertEqual(len(t.matches), (len(t.competitors) + 1) // 2)
        fm = t.matches[0]
        self.assertEqual(fm.turn, 1)
        self.assertEqual(fm.competitor1.player1.firstname,
                         PlayerData.fabiot.firstname)
        self.assertEqual(fm.competitor2.player1.firstname,
                         PlayerData.lucab.firstname)

    def test_first_turn_odd(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.rated_no_turns_odd.description).one()
        self.assertEqual(t.matches, [])
        byrevrate = list(sorted(t.competitors, key=attrgetter('rate'), reverse=True))
        self.assertFalse(any(c.rate==1500 for c in t.competitors))
        t.makeNextTurn()
        self.assertEqual(len(t.matches), (len(t.competitors) + 1) // 2)
        fm = t.matches[0]
        self.assertEqual(fm.turn, 1)
        self.assertIs(fm.competitor1.player1, byrevrate[0].player1)
        self.assertIs(fm.competitor2.player1, byrevrate[3].player1)
        fm = t.matches[1]
        self.assertIs(fm.competitor1.player1, byrevrate[1].player1)
        self.assertIs(fm.competitor2.player1, byrevrate[4].player1)
        fm = t.matches[2]
        self.assertIs(fm.competitor1.player1, byrevrate[2].player1)
        self.assertIs(fm.competitor2.player1, byrevrate[5].player1)
        fm = t.matches[3]
        self.assertIs(fm.competitor1.player1, byrevrate[6].player1)
        self.assertIs(fm.competitor2, None) # Phantom

    def test_ranking(self):
        s = models.DBSession()

        rating = s.query(models.Rating) \
                 .filter_by(description=RatingData.national.description).one()

        ranking = rating.ranking

        self.assertEqual(ranking[0][0].firstname, PlayerData.juri.firstname)
        self.assertEqual(ranking[0][1], 1700)
        self.assertEqual(ranking[-1][0].firstname, PlayerData.varechina.firstname)
        self.assertEqual(ranking[-1][1], 1200)

    def test_timespan(self):
        s = models.DBSession()

        rating = s.query(models.Rating) \
                 .filter_by(description=RatingData.european.description).one()

        self.assertEqual(rating.time_span, (TODAY-ONEDAY*2, TODAY))

    def test_outcomes(self):
        for oc in ('glicko', 'guido', 'expds'):
            r = models.Rating(outcomes=oc)
            compute_outcomes = getattr(r, "_compute%sOutcomes" % oc.capitalize())
            self.assertEqual(compute_outcomes(25, 0), (1, 0))
            self.assertEqual(compute_outcomes(0, 25), (0, 1))
            for s in range(26):
                self.assertEqual(compute_outcomes(s, s), (0.5, 0.5))


class TestTourney(TestCase):
    def test_tourney(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()
        self.assertEqual(t.description, TourneyData.first.description)
        self.assertEqual(t.championship.description, ChampionshipData.current.description)
        self.assertEqual(len(t.competitors), 6)

    def test_first_turn(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.second.description).one()
        self.assertEqual(t.matches, [])
        t.makeNextTurn()
        self.assertEqual(len(t.matches), (len(t.competitors) + 1) // 2)

    def test_next_turn(self):
        from random import randint
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()
        t.prized = False
        lastturn = t.currentturn
        t.makeNextTurn()
        self.assertEqual(t.currentturn, lastturn+1)
        self.assertEqual(len(t.matches), 12)
        lastturn = t.currentturn
        for m in t.matches:
            if m.turn == lastturn:
                m.score1 = randint(1, 25)
                m.score2 = randint(1, 25)
        t.makeNextTurn()
        self.assertEqual(t.currentturn, lastturn+1)
        self.assertEqual(t.rankedturn, lastturn)
        self.assertEqual(len(t.matches), 15)
        # Here we cannot generate the next turn, because have
        # non-scored matches
        try:
            t.makeNextTurn()
        except OperationAborted:
            # The ranking should not fail, just ignore the
            # not yet scored turn
            t.ranking
            self.assertEqual(t.currentturn, t.rankedturn+1)
        else:
            assert False, "Should have raised an error!"

    def test_next_turn_few_players(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.apr24.description).one()
        best = t.ranking[0]
        s.flush()
        self.assertEqual(best.player1.firstname, 'Emanuele')
        self.assertEqual(len(t.matches), 20)

        lastturn = t.currentturn
        t.makeNextTurn()
        self.assertEqual(t.currentturn, lastturn+1)
        self.assertEqual(len(t.matches), 24)

    def test_odd(self):
        from random import randint

        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.odd.description).one()
        self.assertEqual(t.matches, [])
        t.makeNextTurn()
        self.assertEqual(len(t.matches), (len(t.competitors) + 1) // 2)
        self.assertEqual(len([m for m in t.matches if m.competitor2 is None]), 1)
        self.assertEqual([m for m in t.matches if m.competitor2 is None][0].score1,
                         t.phantomscore)
        self.assertIs(t.matches[-1].competitor2, None)
        for m in t.matches:
            if m.turn==t.currentturn:
                m.score1 = randint(1, 25)
                m.score2 = 0
        t.makeNextTurn()
        self.assertEqual(len(t.matches), (len(t.competitors)+1))
        self.assertEqual(len([m for m in t.matches if m.competitor2 is None]), 2)
        try:
            t.makeNextTurn()
        except OperationAborted as e:
            self.assertIn("without result", str(e))
        else:
            assert False, "Should have raised an error!"

    def test_dazed_odd(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.dazedodd.description).one()
        self.assertEqual(t.matches, [])
        nboards = (len(t.competitors) + 1) // 2
        for turn in range(1, 4):
            t.makeNextTurn()
            self.assertEqual(len(t.matches), nboards*turn)
            self.assertEqual(len([m for m in t.matches if m.competitor2 is None]), turn)
            self.assertEqual([m for m in t.matches if m.competitor2 is None][0].score1,
                             t.phantomscore)
            self.assertIs(t.matches[-1].competitor2, None)
            for m in t.matches:
                if m.turn == t.currentturn and m.competitor2 is not None:
                    m.score1 = 10
                    m.score2 = 0
        try:
            t.makeNextTurn()
        except OperationAborted:
            pass
        else:
            assert False, "Should have raised an error!"

    def test_no_matches(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.odd.description).one()
        self.assertEqual(t.matches, [])
        # force update
        t.rankedturn = -1
        ranking = t.ranking
        self.assertEqual(len(ranking), len(t.competitors))

    def test_dazed_iterator(self):
        class C(object):
            def __init__(self, id, points):
                self.id = id
                self.points = points

        a = C('A', 10) # 0
        b = C('B', 10) # 1
        c = C('C', 10) # 2
        d = C('D', 10) # 3
        e = C('E', 10) # 4
        f = C('F', 9)  # 5
        g = C('G', 8)  # 6
        h = C('H', 8)  # 7

        ranking = [a, b, c, d, e, f, g, h]
        done = set([(a, f), (f, a),
                    (b, e), (e, b),
                    (c, d), (d, c),
                    (g, h), (h, g)])

        t = models.Tourney()
        order = t._dazedVisitor(a, ranking, done)
        order = list(order)
        expected = [2, 3, 4, 1, 6, 7]
        self.assertEqual(order, expected)

    def test_dazed_iterator_initial_even(self):
        class C(object):
            def __init__(self, id, points):
                self.id = id
                self.points = points

        a = C('A', 0) # 0
        b = C('B', 0) # 1
        c = C('C', 0) # 2
        d = C('D', 0) # 3
        e = C('E', 0) # 4
        f = C('F', 0) # 5
        g = C('G', 0) # 6
        h = C('H', 0) # 7

        ranking = [a, b, c, d, e, f, g, h]
        done = set()

        t = models.Tourney()
        order = t._dazedVisitor(a, ranking, done)
        order = list(order)
        expected = [4, 5, 6, 7, 1, 2, 3]
        self.assertEqual(order, expected)

    def test_dazed_iterator_initial_odd(self):
        class C(object):
            def __init__(self, id, points):
                self.id = id
                self.points = points

        a = C('A', 0) # 0
        b = C('B', 0) # 1
        c = C('C', 0) # 2
        d = C('D', 0) # 3
        e = C('E', 0) # 4
        f = C('F', 0) # 5
        g = C('G', 0) # 6

        ranking = [a, b, c, d, e, f, g]
        done = set()

        t = models.Tourney()
        order = t._dazedVisitor(a, ranking, done)
        order = list(order)
        expected = [3, 4, 5, 6, 1, 2]
        self.assertEqual(order, expected)

    def test_serial_iterator(self):
        class C(object):
            def __init__(self, id, points):
                self.id = id
                self.points = points

        a = C('A', 10) # 0
        b = C('B', 10) # 1
        c = C('C', 10) # 2
        d = C('D', 10) # 3
        e = C('E', 10) # 4
        f = C('F', 9)  # 5
        g = C('G', 8)  # 6
        h = C('H', 8)  # 7

        ranking = [a, b, c, d, e, f, g, h]
        done = set([(a, f), (f, a),
                    (b, e), (e, b),
                    (c, d), (d, c),
                    (g, h), (h, g)])

        t = models.Tourney()
        order = t._serialVisitor(a, ranking, done)
        order = list(order)
        expected = [1, 2, 3, 4, 6, 7]
        self.assertEqual(order, expected)

    def test_combine(self):
        models.tourney.logger.setLevel(logging.ERROR)
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.second.description).one()
        c = [1, 2, 3, 4, 5, 6]
        d = set()
        a = []
        n = t._combine(c, d)
        while n:
            a.append(n)
            for m in n:
                c1, c2 = m
                d.add((c1, c2))
                d.add((c2, c1))
            n = t._combine(c, d)
        self.assertEqual(len(a), 5)

    def test_asis_prizes(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()
        t.championship.prizes = 'asis'
        t.prized = False
        t.assignPrizes()
        s.flush()
        prizes = []
        for c in t.ranking:
            prizes.append(c.prize)
        self.assertEqual(list(range(len(prizes), 0, -1)), prizes)

    def test_fixed_prizes(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()
        t.championship.prizes = 'fixed'
        t.prized = False
        t.assignPrizes()
        s.flush()
        dates, cship = t.championship.ranking()
        self.assertEqual(len(dates), len([st for st in t.championship.tourneys if st.prized]))
        self.assertEqual(len(cship), 6)
        self.assertEqual(cship[0][1], 18)

    def test_fixed40_prizes(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()
        t.championship.prizes = 'fixed40'
        t.prized = False
        t.assignPrizes()
        s.flush()
        r = t.ranking
        self.assertEqual(r[0].prize, 1000)
        self.assertEqual(r[1].prize, 900)
        self.assertEqual(r[2].prize, 800)
        self.assertEqual(r[3].prize, 750)

    def test_millesimal_prizes(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.third.description).one()
        t.championship.prizes = 'millesimal'
        t.prized = False
        t.assignPrizes()
        s.flush()
        dates, cship = t.championship.ranking()
        self.assertEqual(len(dates), len([st for st in t.championship.tourneys if st.prized]))
        self.assertEqual(len(cship), len(t.competitors))
        r = t.ranking
        self.assertEqual(r[0].prize, 1000)
        self.assertEqual(r[1].prize, 750)
        self.assertEqual(r[2].prize, 500)
        self.assertEqual(r[3].prize, 250)

    def test_centesimal_prizes(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()
        t.championship.prizes = 'centesimal'
        t.prized = False
        t.assignPrizes()
        self.assertEqual(t.ranking[0].prize, 100)
        self.assertEqual(t.ranking[-1].prize, 1)

    def test_replay(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.third.description).one()
        d = TODAY+10*ONEDAY
        n = t.replay(d)
        s.flush()
        s = models.DBSession()
        n = s.query(models.Tourney) \
            .filter_by(idchampionship=t.idchampionship,
                       date=d).one()
        self.assertEqual(len(t.competitors), len(n.competitors))

    def test_replay_closed_championship(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.second.description).one()
        n = t.replay(TODAY)
        s.flush()
        self.assertEqual(n.championship.description, 'SCR 2010 (test)')

    def test_replay_double(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.double.description).one()
        n = t.replay(TODAY+1*ONEDAY)
        s.flush()
        self.assertEqual(n.championship.description,
                         ChampionshipData.double.description)

    def test_skip_worst_prize(self):
        s = models.DBSession()

        championship = s.query(models.Championship) \
            .filter_by(description=ChampionshipData.skipworstprize.description).one()
        dates, ranking = championship.ranking()
        self.assertEqual(len(dates), 0)

        t1 = championship.tourneys[0]
        t1.assignPrizes()
        s.flush()

        dates, ranking = championship.ranking()
        self.assertEqual(len(dates), 1)
        self.assertEqual(len(ranking), 2)

        first = ranking[0]
        players, prize, prizes, nprizes, skipped = first
        self.assertEqual(players[0].firstname, PlayerData.juri.firstname)
        self.assertEqual(skipped, None)

        d = TODAY
        t2 = t1.replay(d)
        t2.makeNextTurn()
        for m in t2.matches:
            m.score1 = 10
            m.score2 = 0
        s.flush()

        t2.assignPrizes()
        s.flush()

        dates, ranking = championship.ranking()
        self.assertEqual(len(dates), 2)
        self.assertEqual(len(ranking), 2)

        first = ranking[0]
        players, prize, prizes, nprizes, skipped = first
        self.assertEqual(len(skipped), 1)


class TestTourneyBoardNumber(TestCase):
    def test_phantom_match_last(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.odd.description).one()
        ncompetitors = len(t.competitors)
        self.assertEqual(ncompetitors % 2, 1)
        self.assertEqual(t.matches, [])
        for turn in range(1, ncompetitors-1):
            t.makeNextTurn()
            newmatches = [m for m in t.matches if m.turn == t.currentturn]
            newmatches.sort(key=lambda m: m.board)
            self.assertIs(newmatches[-1].competitor2, None)
            self.assertEqual(newmatches[-1].board, (ncompetitors+1)/2)
            for m in newmatches:
                if m.competitor2 is not None:
                    m.score1 = 10
                    m.score2 = 0


class TestTourneyFinals(TestCase):
    def test_no_finals(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()
        self.assertRaises(OperationAborted, t.makeFinalTurn)

    def test_apr24_finals_same_winners(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.apr24.description).one()

        c1, c2, c3, c4 = t.ranking[:4]

        t.makeFinalTurn()
        finals = [m for m in t.matches if m.final]
        self.assertEqual(len(finals), 2)
        self.assertEqual(finals[0].turn, t.currentturn)
        self.assertTrue(t.finalturns)
        self.assertFalse(t.prized)
        finals[0].score1 = 10
        finals[1].score2 = 10

        t.makeNextTurn()
        finals = [m for m in t.matches if m.final]
        self.assertEqual(len(finals), 4)
        finals[2].score1 = 10
        finals[3].score2 = 10

        t.updateRanking()
        self.assertTrue(t.prized)
        self.assertEqual(t.ranking[:4], [c1, c2, c4, c3])

        transaction.abort()

    def test_apr24_finals_two_and_three(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.apr24.description).one()

        c1, c2, c3, c4 = t.ranking[:4]

        t.makeFinalTurn()
        self.assertFalse(t.prized)
        finals = [m for m in t.matches if m.final]
        finals[0].score1 = 10
        finals[1].score2 = 10

        t.makeNextTurn()
        finals = [m for m in t.matches if m.final]
        self.assertEqual(len(finals), 4)
        finals[2].score1 = 10
        finals[3].score1 = 10

        t.makeNextTurn()
        finals = [m for m in t.matches if m.final]
        self.assertEqual(len(finals), 5)
        finals[4].score1 = 10

        t.updateRanking()
        self.assertTrue(t.prized)
        self.assertEqual(t.ranking[:4], [c1, c2, c3, c4])

        transaction.abort()

    def test_rated_finals_two(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.rated.description).one()

        c1, c2 = t.ranking[:2]

        t.makeFinalTurn()
        finals = [m for m in t.matches if m.final]
        self.assertEqual(len(finals), 1)
        self.assertTrue(t.finalturns)
        finals[0].score2 = 10

        t.makeNextTurn()
        finals = [m for m in t.matches if m.final]
        self.assertEqual(len(finals), 2)
        finals[1].score2 = 10

        self.assertRaises(OperationAborted, t.makeNextTurn)

        t.updateRanking()
        self.assertTrue(t.prized)
        self.assertEqual(t.ranking[:2], [c2, c1])

        transaction.abort()

    def test_rated_finals_three(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.rated.description).one()

        c1, c2 = t.ranking[:2]

        t.makeFinalTurn()
        finals = [m for m in t.matches if m.final]
        self.assertEqual(len(finals), 1)
        self.assertTrue(t.finalturns)
        finals[0].score2 = 10

        t.makeNextTurn()
        finals = [m for m in t.matches if m.final]
        self.assertEqual(len(finals), 2)
        finals[1].score1 = 10

        t.makeNextTurn()
        finals = [m for m in t.matches if m.final]
        self.assertEqual(len(finals), 3)
        finals[2].score2 = 20

        self.assertRaises(OperationAborted, t.makeNextTurn)

        t.updateRanking()
        self.assertTrue(t.prized)
        self.assertEqual(t.ranking[:2], [c2, c1])

        transaction.abort()


class TestTourneyRanking(TestCase):
    def test_ranking(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()
        ranking = t.ranking
        self.assertEqual(len(ranking), 6)
        first = ranking[0]
        self.assertEqual(first.player1.lastname, PlayerData.blond.lastname)
        self.assertEqual(first.points, 5)
        self.assertEqual(first.bucholz, 7)

    def test_compute_ranking(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()

        c, r = t.computeRanking(1)[0]
        self.assertEqual(c.player1.lastname, PlayerData.blond.lastname)
        self.assertEqual(r.points, 2)
        self.assertEqual(r.bucholz, 0)
        self.assertEqual(r.netscore, 20)

        c, r = t.computeRanking(2)[0]
        self.assertEqual(c.player1.lastname, PlayerData.blond.lastname)
        self.assertEqual(r.points, 4)
        self.assertEqual(r.bucholz, 1)
        self.assertEqual(r.netscore, 22)

        c, r = t.computeRanking(3)[0]
        firstr = t.ranking[0]
        self.assertEqual(c.player1.lastname, firstr.player1.lastname)
        self.assertEqual(c.points, firstr.points)
        self.assertEqual(c.bucholz, firstr.bucholz)
        self.assertEqual(c.netscore, firstr.netscore)


class TestTourneyResetPrizes(TestCase):
    def test_reset_prizes(self):
        from time import sleep

        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()
        modified = t.modified
        t.assignPrizes()
        s.flush()
        r = t.ranking
        self.assertEqual(r[0].prize, 18)
        self.assertEqual(r[-1].prize, 11)
        # Sleep for one second, to test the modified timestamp
        sleep(1)
        t.resetPrizes()
        s.flush()
        self.assertEqual(t.prized, False)
        r = t.ranking
        self.assertEqual(r[0].prize, 0)
        self.assertEqual(r[-1].prize, 0)
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()
        self.assertGreater(t.modified, modified)

    def test_reset_rated_tourney_prizes(self):
        with transaction.manager:
            s = models.DBSession()
            t = s.query(models.Tourney) \
                .filter_by(description=TourneyData.rated.description).one()
            oneplayerid = t.competitors[0].idplayer1
            t.assignPrizes()
            s.flush()
            t.resetPrizes()
            s.flush()

        s = models.DBSession()
        self.assertRaises(NoResultFound,
                          s.query(models.Rate)
                          .filter_by(idplayer=oneplayerid,
                                     date=TourneyData.rated.date).one)


class TestRetirement(TestCase):
    def test_retirement(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()
        t.prized = False
        comp = t.competitors[0]
        comp.retired = True
        lastturn = t.currentturn
        t.makeNextTurn()
        self.assertEqual(t.currentturn, lastturn+1)
        newmatches = [m for m in t.matches if m.turn == t.currentturn]
        assert [m for m in newmatches if not m.idcompetitor2]
        assert not [m for m in newmatches
                    if m.idcompetitor1 == comp.idcompetitor
                    or m.idcompetitor2 == comp.idcompetitor]


class TestUpdateDefault(TestCase):
    def test_update(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()

        result = t.update(dict(
            couplings='foo',
            location='bar',
            currentturn=1,
            prized=True
        ))

        self.assertEqual(result, dict(
            couplings=('serial', 'foo'),
            location=(None, 'bar'),
            currentturn=(3, 1),
            prized=(False, True)
        ))


class TestUpdateMissing(TestCase):
    def test_update(self):
        s = models.DBSession()
        t = s.query(models.Tourney) \
            .filter_by(description=TourneyData.first.description).one()

        result = t.update(dict(
            couplings='foo',
            location='bar',
            currentturn=1,
            prized=True
        ), missing_only=True)

        self.assertEqual(result, dict(
            location=(None, 'bar'),
            prized=(False, True)
        ))
