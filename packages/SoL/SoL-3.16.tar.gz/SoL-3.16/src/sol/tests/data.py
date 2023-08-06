# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Fixtures
# :Creato:    sab 27 set 2008 14:15:26 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from datetime import date, timedelta


class Fixture(type):
    """A metaclass usable to declare a set of ordered rows of data.
    """

    fixtures = []

    @classmethod
    def __prepare__(mcl, name, bases, **kwds):
        "Install an OrderedDict as the class __dict__"

        from collections import OrderedDict
        return OrderedDict()

    def __new__(mcl, name, bases, nmspc):
        "Collect declared `rows`"

        rows = []
        for n in nmspc:
            if n.startswith('_'):
                continue
            rows.append(n)
        nmspc['rows'] = rows
        return super(Fixture, mcl).__new__(mcl, name, bases, nmspc)

    def __init__(cls, name, bases, nmspc):
        "Register the fixture class in the ordered `fixtures` list"

        super().__init__(name, bases, nmspc)
        cls.fixtures.append(cls)

    @classmethod
    def initialize(cls, session):
        "Insert declared fixtures rows in the database"

        from .. import models

        map = {}

        for fixture in cls.fixtures:
            ename = fixture.__name__[:-4]
            eclass = getattr(models, ename)

            for row in fixture.rows:
                fdata = getattr(fixture, row)
                d = {}
                for k in dir(fdata):
                    if not isinstance(k, str) or k.startswith('_'):
                        continue
                    a = getattr(fdata, k)
                    if a in map:
                        a = map[a]
                    d[k] = a
                instance = map[fdata] = eclass(**d)
                session.add(instance)


class ClubData(metaclass=Fixture):
    class scr:
        description = 'Scarambol Club Rovereto'
        couplings = 'dazed'
        nationality = 'ITA'
        email = 'test@example.it'

    class fic:
        description = 'Federazione Italiana Carrom'
        couplings = 'dazed'
        isfederation = True

    class ccm:
        description = 'Carrom Club Milano'
        couplings = 'serial'

    class ecc:
        description = 'EuroCarromConf'
        nationality = 'eur'


class PlayerData(metaclass=Fixture):
    class lele:
        firstname = 'Emanuele'
        lastname = 'Gaifas'
        nickname = 'Lele'
        password = 'lele'
        email = 'test@example.it'

    class juri:
        firstname = 'Juri'
        lastname = 'Picol'
        email = 'picol@esempio.it'

    class blond:
        firstname = 'Roberto'
        lastname = 'Blond'

    class bob:
        firstname = 'Bob'
        lastname = 'Rock'

    class varechina:
        firstname = 'Sandro'
        lastname = 'Varechina'

    class fata:
        firstname = 'Fata'
        lastname = 'Turchina'
        language = 'zu'
        nationality = 'ZWE'
        citizenship = False
        email = 'fata@miracle.oz'

    class pk:
        firstname = 'Paolo'
        lastname = 'Pk'

    class merge1:
        firstname = 'Merge'
        lastname = 'One'
        sex = 'M'
        email = 'juri@esempio.it'

    class merge2:
        firstname = 'Merge'
        lastname = 'Two'

    class merge3:
        firstname = 'Wrong'
        lastname = 'Tzè'

    class fabiot:
        firstname = 'Fabio'
        lastname = 'T'

    class lucab:
        firstname = 'Luca'
        lastname = 'B'

    class paolor:
        firstname = 'Paolo'
        lastname = 'R'

    class danieled:
        firstname = 'Daniele'
        lastname = 'Da Fatti'

    class elisam:
        firstname = 'Elisa'
        lastname = 'M'
        federation = ClubData.fic

    class carlitob:
        firstname = 'Carlito'
        lastname = 'B'

    class lorenzoh:
        firstname = 'Lorenzo'
        lastname = 'H'

    class martinam:
        firstname = 'Martina'
        lastname = 'W'

    class peterb:
        firstname = 'Peter'
        lastname = 'B'

    class josefm:
        firstname = 'Josef'
        lastname = 'M'

    class barbarat:
        firstname = 'Barbara'
        lastname = 'T'

PlayerData.fata.owner = PlayerData.lele


# The following is here to workaround chicken-and-egg limit of the Fixture class
class ClubSpec(metaclass=Fixture):
    class owned:
        description = 'Owned Club'
        owner = PlayerData.lele


class ChampionshipPrev(metaclass=Fixture):
    class prev:
        description = 'Previous championship'
        club = ClubData.scr
        closed = True
        owner = PlayerData.lele


class ChampionshipData(metaclass=Fixture):
    class current:
        description = 'Current championship'
        club = ClubData.scr
        closed = True
        owner = PlayerData.lele
        previous = ChampionshipPrev.prev

    class next:
        description = 'Next championship'
        club = ClubData.ccm
        closed = False

    class scr2010:
        description = 'SCR 2010 (test)'
        club = ClubData.scr
        closed = False

    class skipworstprize:
        description = 'Skip worst prize'
        club = ClubData.scr
        skipworstprizes = 1
        closed = False

    class simpletourneys:
        description = 'Simple tourneys, no prizes'
        club = ClubData.scr
        prizes = 'none'
        couplings = 'dazed'

    class double:
        description = 'Double events'
        club = ClubData.scr
        playersperteam = 2
        closed = False

    class owned:
        description = 'Owned championship'
        club = ClubSpec.owned

ChampionshipData.next.previous = ChampionshipData.current


TODAY = date.today()
ONEDAY = timedelta(days=1)

class RatingData(metaclass=Fixture):
    class european:
        description = 'European rating'
        level = '1'

    class national:
        description = 'National rating'
        level = '2'
        inherit = True

    class standalone:
        description = 'Standalone rating'
        level = '2'
        inherit = False
        owner = PlayerData.lele
        club = ClubData.scr

    class exponential:
        description = 'Exponential outcomes'
        level = '2'
        outcomes = 'expds'


class RateData(metaclass=Fixture):
    class lele_yesterday:
        rating = RatingData.national
        player = PlayerData.lele
        date = TODAY - ONEDAY
        rate = 1000
        deviation = 350
        volatility = '0.006'

    class lele_today:
        rating = RatingData.national
        player = PlayerData.lele
        date = TODAY
        rate = 1500
        deviation = 200
        volatility = '0.06'

    class lele_tomorrow:
        rating = RatingData.national
        player = PlayerData.lele
        date = TODAY+ONEDAY
        rate = 1505
        deviation = 200
        volatility = '0.06'

    class bob_today:
        rating = RatingData.national
        player = PlayerData.bob
        date = TODAY
        rate = 1400
        deviation = 30
        volatility = '0.06'

    class pk_today:
        rating = RatingData.national
        player = PlayerData.pk
        date = TODAY
        rate = 1550
        deviation = 100
        volatility = '0.06'

    class juri_today:
        rating = RatingData.national
        player = PlayerData.juri
        date = TODAY
        rate = 1700
        deviation = 300
        volatility = '0.06'

    class merge1_ten_days_ago:
        rating = RatingData.national
        player = PlayerData.merge1
        date = TODAY - ONEDAY*10
        rate = 1700
        deviation = 300
        volatility = '0.06'

    class danieled_today:
        rating = RatingData.european
        player = PlayerData.danieled
        date = TODAY-ONEDAY*2
        rate = 1600
        deviation = 300
        volatility = '0.06'

    class paolor_today:
        rating = RatingData.european
        player = PlayerData.paolor
        date = TODAY-ONEDAY*2
        rate = 1700
        deviation = 300
        volatility = '0.06'

    class lucab_today:
        rating = RatingData.european
        player = PlayerData.lucab
        date = TODAY-ONEDAY*2
        rate = 1800
        deviation = 300
        volatility = '0.06'

    class fabiot_today:
        rating = RatingData.european
        player = PlayerData.fabiot
        date = TODAY-ONEDAY*2
        rate = 1900
        deviation = 300
        volatility = '0.06'

    class varechina_national:
        rating = RatingData.national
        player = PlayerData.varechina
        date = TODAY - ONEDAY
        rate = 1200
        deviation = 250
        volatility = '0.06'

    class varechina_european:
        rating = RatingData.european
        player = PlayerData.varechina
        date = TODAY
        rate = 1300
        deviation = 250
        volatility = '0.06'

    class varechina_standalone:
        rating = RatingData.standalone
        player = PlayerData.varechina
        date = TODAY - ONEDAY
        rate = 1200
        deviation = 250
        volatility = '0.06'


class TourneyData(metaclass=Fixture):
    class first:
        championship = ChampionshipData.current
        date = TODAY
        description = 'First test tournament'
        currentturn = 3
        owner = PlayerData.lele
        finals = 0

    class second:
        championship = ChampionshipData.current
        date = TODAY+ONEDAY
        description = 'Second test tournament'

    class third:
        championship = ChampionshipData.next
        date = TODAY
        description = 'Another tourney'
        currentturn = 1

    class odd:
        championship = ChampionshipData.next
        date = TODAY+ONEDAY*2
        description = 'Odd tourney'
        phantomscore = 15

    class dazedodd:
        championship = ChampionshipData.current
        date = TODAY+ONEDAY*5
        description = 'Dazed odd tourney'
        couplings = 'dazed'

    class merge1:
        championship = ChampionshipData.current
        date = TODAY+ONEDAY*2
        description = 'Merging test tournament'

    class merge2:
        championship = ChampionshipData.current
        date = TODAY+ONEDAY*3
        description = 'Merging test tournament'

    class apr24:
        championship = ChampionshipData.scr2010
        date = date(2010, 4, 24)
        description = '5 torneo'
        rankedturn = 0
        currentturn = 5
        finals = 2
        finalkind = 'bestof3'

    class rated:
        championship = ChampionshipData.current
        date = TODAY+ONEDAY*4
        description = 'Rated test tournament'
        rating = RatingData.national
        currentturn = 3
        finals = 1
        finalkind = 'bestof3'

    class rated_no_turns:
        championship = ChampionshipData.current
        date = TODAY-ONEDAY
        description = 'Rated empty tournament'
        rating = RatingData.european

    class rated_no_turns_odd:
        championship = ChampionshipData.current
        date = TODAY+ONEDAY*20
        description = 'Rated empty tournament odd number of players'
        rating = RatingData.national
        couplings = 'dazed'

    class rated_exponential:
        championship = ChampionshipData.current
        date = date(2001, 1, 2)
        description = 'Rated with exponential outcomes'
        rating = RatingData.exponential
        rankedturn = 0
        currentturn = 1

    class skipworstprize_first:
        championship = ChampionshipData.skipworstprize
        date = TODAY-ONEDAY
        description = 'Skip worst prize first tourney'
        rankedturn = 0
        currentturn = 1

    class simple:
        championship = ChampionshipData.simpletourneys
        date = date(2001, 1, 1)
        description = 'VerySimpleTourney'

    class double:
        championship = ChampionshipData.double
        date = TODAY
        description = 'Double event'

    class owned:
        championship = ChampionshipData.owned
        date = TODAY
        description = 'Owned tournament'


class CompetitorData(metaclass=Fixture):
    # First tourney

    class fcomp1:
        tourney = TourneyData.first
        player1 = PlayerData.lele
        player2 = PlayerData.fata

    class fcomp2:
        tourney = TourneyData.first
        player1 = PlayerData.juri

    class fcomp3:
        tourney = TourneyData.first
        player1 = PlayerData.blond

    class fcomp4:
        tourney = TourneyData.first
        player1 = PlayerData.bob

    class fcomp5:
        tourney = TourneyData.first
        player1 = PlayerData.varechina

    class fcomp6:
        tourney = TourneyData.first
        player1 = PlayerData.pk

    # Second tourney

    class scomp1:
        tourney = TourneyData.second
        player1 = PlayerData.lele

    class scomp2:
        tourney = TourneyData.second
        player1 = PlayerData.varechina

    class scomp3:
        tourney = TourneyData.second
        player1 = PlayerData.bob

    class scomp4:
        tourney = TourneyData.second
        player1 = PlayerData.fata

    # Third tourney

    class pcomp1:
        tourney = TourneyData.third
        player1 = PlayerData.lele

    class pcomp2:
        tourney = TourneyData.third
        player1 = PlayerData.varechina

    class pcomp3:
        tourney = TourneyData.third
        player1 = PlayerData.bob

    class pcomp4:
        tourney = TourneyData.third
        player1 = PlayerData.fata

    # Odd tourney

    class ocomp1:
        tourney = TourneyData.odd
        player1 = PlayerData.lele

    class ocomp2:
        tourney = TourneyData.odd
        player1 = PlayerData.fata

    class ocomp3:
        tourney = TourneyData.odd
        player1 = PlayerData.bob

    class ocomp4:
        tourney = TourneyData.odd
        player1 = PlayerData.pk

    class ocomp5:
        tourney = TourneyData.odd
        player1 = PlayerData.blond

    class ocomp6:
        tourney = TourneyData.odd
        player1 = PlayerData.juri

    class ocomp7:
        tourney = TourneyData.odd
        player1 = PlayerData.fabiot

    class ocomp8:
        tourney = TourneyData.odd
        player1 = PlayerData.lucab

    class ocomp9:
        tourney = TourneyData.odd
        player1 = PlayerData.paolor

    class ocomp10:
        tourney = TourneyData.odd
        player1 = PlayerData.danieled

    class ocomp11:
        tourney = TourneyData.odd
        player1 = PlayerData.elisam

    class ocomp12:
        tourney = TourneyData.odd
        player1 = PlayerData.carlitob

    class ocomp13:
        tourney = TourneyData.odd
        player1 = PlayerData.lorenzoh

    class ocomp14:
        tourney = TourneyData.odd
        player1 = PlayerData.martinam

    class ocomp15:
        tourney = TourneyData.odd
        player1 = PlayerData.peterb

    class ocomp16:
        tourney = TourneyData.odd
        player1 = PlayerData.josefm

    class ocomp17:
        tourney = TourneyData.odd
        player1 = PlayerData.barbarat

    # Dazedodd tourney

    class docomp1:
        tourney = TourneyData.dazedodd
        player1 = PlayerData.lele

    class docomp2:
        tourney = TourneyData.dazedodd
        player1 = PlayerData.pk

    class docomp3:
        tourney = TourneyData.dazedodd
        player1 = PlayerData.bob

    class docomp4:
        tourney = TourneyData.dazedodd
        player1 = PlayerData.varechina

    class docomp5:
        tourney = TourneyData.dazedodd
        player1 = PlayerData.blond

    # Merge1 tourney

    class mcomp1:
        tourney = TourneyData.merge1
        player1 = PlayerData.merge1

    class mcomp2:
        tourney = TourneyData.merge1
        player1 = PlayerData.fata

    class mcomp3:
        tourney = TourneyData.merge1
        player1 = PlayerData.bob

    # Merge2 tourney

    class mcompa:
        tourney = TourneyData.merge2
        player1 = PlayerData.lele

    class mcompb:
        tourney = TourneyData.merge2
        player1 = PlayerData.merge2

    class mcompc:
        tourney = TourneyData.merge2
        player1 = PlayerData.bob

    # Apr24 tourney

    class apr24_bob:
        tourney = TourneyData.apr24
        player1 = PlayerData.bob

    class apr24_lele:
        tourney = TourneyData.apr24
        player1 = PlayerData.lele

    class apr24_danieled:
        tourney = TourneyData.apr24
        player1 = PlayerData.danieled

    class apr24_pk:
        tourney = TourneyData.apr24
        player1 = PlayerData.pk

    class apr24_lucab:
        tourney = TourneyData.apr24
        player1 = PlayerData.lucab

    class apr24_fabiot:
        tourney = TourneyData.apr24
        player1 = PlayerData.fabiot

    class apr24_paolor:
        tourney = TourneyData.apr24
        player1 = PlayerData.paolor

    # Rated tourney

    class rated_lele:
        tourney = TourneyData.rated
        player1 = PlayerData.lele

    class rated_juri:
        tourney = TourneyData.rated
        player1 = PlayerData.juri

    class rated_pk:
        tourney = TourneyData.rated
        player1 = PlayerData.pk

    class rated_bob:
        tourney = TourneyData.rated
        player1 = PlayerData.bob

    # Rated tourney no rounds

    class rated_nt_danieled:
        tourney = TourneyData.rated_no_turns
        player1 = PlayerData.danieled

    class rated_nt_paolor:
        tourney = TourneyData.rated_no_turns
        player1 = PlayerData.paolor

    class rated_nt_lucab:
        tourney = TourneyData.rated_no_turns
        player1 = PlayerData.lucab

    class rated_nt_fabiot:
        tourney = TourneyData.rated_no_turns
        player1 = PlayerData.fabiot

    # Rated tourney, no rounds, odd number of players

    class rated_nto_danieled:
        tourney = TourneyData.rated_no_turns_odd
        player1 = PlayerData.danieled

    class rated_nto_paolor:
        tourney = TourneyData.rated_no_turns_odd
        player1 = PlayerData.paolor

    class rated_nto_lucab:
        tourney = TourneyData.rated_no_turns_odd
        player1 = PlayerData.lucab

    class rated_nto_fabiot:
        tourney = TourneyData.rated_no_turns_odd
        player1 = PlayerData.fabiot

    class rated_nto_varechina:
        tourney = TourneyData.rated_no_turns_odd
        player1 = PlayerData.varechina

    class rated_nto_bob:
        tourney = TourneyData.rated_no_turns_odd
        player1 = PlayerData.bob

    class rated_nto_lele:
        tourney = TourneyData.rated_no_turns_odd
        player1 = PlayerData.lele

    # Rated exponential

    class rated_exp_bob:
        tourney = TourneyData.rated_exponential
        player1 = PlayerData.bob

    class rated_exp_lele:
        tourney = TourneyData.rated_exponential
        player1 = PlayerData.lele

    # Skip worst prize first tourney

    class cs1_lele:
        tourney = TourneyData.skipworstprize_first
        player1 = PlayerData.lele

    class cs1_juri:
        tourney = TourneyData.skipworstprize_first
        player1 = PlayerData.juri

    # Double event tourney

    class de_comp1:
        tourney = TourneyData.double
        player1 = PlayerData.lele
        player2 = PlayerData.fata

    class de_comp2:
        tourney = TourneyData.double
        player1 = PlayerData.paolor
        player2 = PlayerData.lucab


class MatchData(metaclass=Fixture):
    # First tourney

    class match1_1:
        tourney = TourneyData.first
        turn = 1
        board = 1
        competitor1 = CompetitorData.fcomp1
        competitor2 = CompetitorData.fcomp2
        score1 = 25
        score2 = 10

    class match1_2:
        tourney = TourneyData.first
        turn = 1
        board = 2
        competitor1 = CompetitorData.fcomp3
        competitor2 = CompetitorData.fcomp4
        score1 = 20
        score2 = 0

    class match1_3:
        tourney = TourneyData.first
        turn = 1
        board = 3
        competitor1 = CompetitorData.fcomp5
        competitor2 = CompetitorData.fcomp6
        score1 = 20
        score2 = 25

    class match2_1:
        tourney = TourneyData.first
        turn = 2
        board = 1
        competitor1 = CompetitorData.fcomp3
        competitor2 = CompetitorData.fcomp2
        score1 = 12
        score2 = 10

    class match2_2:
        tourney = TourneyData.first
        turn = 2
        board = 2
        competitor1 = CompetitorData.fcomp1
        competitor2 = CompetitorData.fcomp5
        score1 = 2
        score2 = 8

    class match2_3:
        tourney = TourneyData.first
        turn = 2
        board = 3
        competitor1 = CompetitorData.fcomp4
        competitor2 = CompetitorData.fcomp6
        score1 = 8
        score2 = 8

    class match3_1:
        tourney = TourneyData.first
        turn = 3
        board = 1
        competitor1 = CompetitorData.fcomp6
        competitor2 = CompetitorData.fcomp2
        score1 = 0
        score2 = 10

    class match3_2:
        tourney = TourneyData.first
        turn = 3
        board = 2
        competitor1 = CompetitorData.fcomp1
        competitor2 = CompetitorData.fcomp3
        score1 = 2
        score2 = 2

    class match3_3:
        tourney = TourneyData.first
        turn = 3
        board = 3
        competitor1 = CompetitorData.fcomp5
        competitor2 = CompetitorData.fcomp4
        score1 = 2
        score2 = 2

    # Third tourney

    class match_p_1_1:
        tourney = TourneyData.third
        turn = 1
        board = 1
        competitor1 = CompetitorData.pcomp1
        competitor2 = CompetitorData.pcomp2
        score1 = 10
        score2 = 5

    class match_p_1_2:
        tourney = TourneyData.third
        turn = 1
        board = 2
        competitor1 = CompetitorData.pcomp3
        competitor2 = CompetitorData.pcomp4
        score1 = 15
        score2 = 0

    # Apr24 tourney

    class match_apr24_1_1:
        tourney = TourneyData.apr24
        turn = 1
        board = 1
        competitor1 = CompetitorData.apr24_bob
        competitor2 = CompetitorData.apr24_lele
        score1 = 8
        score2 = 12

    class match_apr24_1_2:
        tourney = TourneyData.apr24
        turn = 1
        board = 2
        competitor1 = CompetitorData.apr24_lucab
        competitor2 = CompetitorData.apr24_danieled
        score1 = 0
        score2 = 25

    class match_apr24_1_3:
        tourney = TourneyData.apr24
        turn = 1
        board = 3
        competitor1 = CompetitorData.apr24_paolor
        competitor2 = CompetitorData.apr24_pk
        score1 = 4
        score2 = 19

    class match_apr24_1_4:
        tourney = TourneyData.apr24
        turn = 1
        board = 4
        competitor1 = CompetitorData.apr24_fabiot
        score1 = 25
        score2 = 0

    class match_apr24_2_1:
        tourney = TourneyData.apr24
        turn = 2
        board = 1
        competitor1 = CompetitorData.apr24_fabiot
        competitor2 = CompetitorData.apr24_danieled
        score1 = 10
        score2 = 7

    class match_apr24_2_2:
        tourney = TourneyData.apr24
        turn = 2
        board = 2
        competitor1 = CompetitorData.apr24_pk
        competitor2 = CompetitorData.apr24_lele
        score1 = 7
        score2 = 11

    class match_apr24_2_3:
        tourney = TourneyData.apr24
        turn = 2
        board = 3
        competitor1 = CompetitorData.apr24_bob
        competitor2 = CompetitorData.apr24_paolor
        score1 = 21
        score2 = 7

    class match_apr24_2_4:
        tourney = TourneyData.apr24
        turn = 2
        board = 4
        competitor1 = CompetitorData.apr24_lucab
        score1 = 25
        score2 = 0

    class match_apr24_3_1:
        tourney = TourneyData.apr24
        turn = 3
        board = 1
        competitor1 = CompetitorData.apr24_bob
        competitor2 = CompetitorData.apr24_lucab
        score1 = 8
        score2 = 2

    class match_apr24_3_2:
        tourney = TourneyData.apr24
        turn = 3
        board = 2
        competitor1 = CompetitorData.apr24_lele
        competitor2 = CompetitorData.apr24_fabiot
        score1 = 5
        score2 = 19

    class match_apr24_3_3:
        tourney = TourneyData.apr24
        turn = 3
        board = 3
        competitor1 = CompetitorData.apr24_danieled
        competitor2 = CompetitorData.apr24_pk
        score1 = 6
        score2 = 13

    class match_apr24_3_4:
        tourney = TourneyData.apr24
        turn = 3
        board = 4
        competitor1 = CompetitorData.apr24_paolor
        score1 = 25
        score2 = 0

    class match_apr24_4_1:
        tourney = TourneyData.apr24
        turn = 4
        board = 1
        competitor1 = CompetitorData.apr24_lele
        competitor2 = CompetitorData.apr24_paolor
        score1 = 25
        score2 = 2

    class match_apr24_4_2:
        tourney = TourneyData.apr24
        turn = 4
        board = 2
        competitor1 = CompetitorData.apr24_fabiot
        competitor2 = CompetitorData.apr24_bob
        score1 = 6
        score2 = 11

    class match_apr24_4_3:
        tourney = TourneyData.apr24
        turn = 4
        board = 3
        competitor1 = CompetitorData.apr24_pk
        competitor2 = CompetitorData.apr24_lucab
        score1 = 25
        score2 = 0

    class match_apr24_4_4:
        tourney = TourneyData.apr24
        turn = 4
        board = 4
        competitor1 = CompetitorData.apr24_danieled
        score1 = 25
        score2 = 0

    class match_apr24_5_1:
        tourney = TourneyData.apr24
        turn = 5
        board = 1
        competitor1 = CompetitorData.apr24_fabiot
        competitor2 = CompetitorData.apr24_paolor
        score1 = 25
        score2 = 2

    class match_apr24_5_2:
        tourney = TourneyData.apr24
        turn = 5
        board = 2
        competitor1 = CompetitorData.apr24_bob
        competitor2 = CompetitorData.apr24_danieled
        score1 = 25
        score2 = 8

    class match_apr24_5_3:
        tourney = TourneyData.apr24
        turn = 5
        board = 3
        competitor1 = CompetitorData.apr24_lele
        competitor2 = CompetitorData.apr24_lucab
        score1 = 25
        score2 = 7

    class match_apr24_5_4:
        tourney = TourneyData.apr24
        turn = 5
        board = 4
        competitor1 = CompetitorData.apr24_pk
        score1 = 25
        score2 = 0

    # Rated tourney

    class match_rated_1:
        tourney = TourneyData.rated
        turn = 1
        board = 1
        competitor1 = CompetitorData.rated_lele
        competitor2 = CompetitorData.rated_bob
        score1 = 15
        score2 = 10

    class match_rated_2:
        tourney = TourneyData.rated
        turn = 2
        board = 1
        competitor1 = CompetitorData.rated_lele
        competitor2 = CompetitorData.rated_pk
        score1 = 10
        score2 = 15

    class match_rated_3:
        tourney = TourneyData.rated
        turn = 3
        board = 1
        competitor1 = CompetitorData.rated_lele
        competitor2 = CompetitorData.rated_juri
        score1 = 10
        score2 = 25

    # Rated exponential tourney

    class match_exp_1:
        tourney = TourneyData.rated_exponential
        turn = 1
        board = 1
        competitor1 = CompetitorData.rated_exp_lele
        competitor2 = CompetitorData.rated_exp_bob
        score1 = 10
        score2 = 25

    # Skip worst prize first tourney

    class match_cs1_1:
        tourney = TourneyData.skipworstprize_first
        turn = 1
        board = 1
        competitor1 = CompetitorData.cs1_lele
        competitor2 = CompetitorData.cs1_juri
        score1 = 10
        score2 = 20
