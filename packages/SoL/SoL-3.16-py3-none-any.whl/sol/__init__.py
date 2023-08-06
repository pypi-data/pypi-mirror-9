# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    lun 13 ott 2008 16:24:21 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

"""
================
 Scarry On Line
================

Easy management of Carrom Tournaments
=====================================

This application implements the following features:

* basic tables editing, like adding a new player, opening a new
  championship, manually tweaking the scores, and so on

* handle a single tourney

  a. compose a list of `competitors`: usually this is just a single
     player, but there are two people in doubles, or more (teams)

  b. set up the first turn, made up of `matches`, each pairing two
     distinct `competitors`: this is usually done randomly, but the
     secretary must be able to manually change the combinations

  c. print the game sheets, where the player will write the scores

  d. possibly show a clock, to alert the end of the game

  e. insert the score of each table

  f. compute the ranking

  g. print the current ranking

  h. possibly offer a way to retire some competitors, or to add a new
     competitor

  i. compute the next turn

  j. repeat steps c. thru i. usually up to seven turns

  k. possibly offer a way to go back, delete last turn, correct a
     score and repeat

  l. recompute the ranking, assigning prizes

* handle a championship of tourneys

  * each tourney is associated to one championship

  * print the championship ranking

* data exchange, to import/export whole tourneys in a portable way

* browseable history thru a light HTML readonly interface
"""

# This is injected automatically at release time
__exact_version__ = 'v3.16'

import logging

from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

from sqlalchemy import engine_from_config

from .models import DBSession

logger = logging.getLogger(__name__)


def favicon_view(request):
    "Serve /favicon.ico as an alias to /static/favicon.png"

    from os.path import dirname, join
    from pyramid.response import FileResponse

    here = dirname(__file__)
    icon = join(here, 'static', 'favicon.png')
    return FileResponse(icon, request=request)


def robots_view(request):
    "Serve /robots.txt as an alias to /static/robots.txt"

    from os.path import dirname, join
    from pyramid.response import FileResponse

    here = dirname(__file__)
    icon = join(here, 'static', 'robots.txt')
    return FileResponse(icon, request=request)


def main(global_config, **settings):
    "This function returns a Pyramid WSGI application."

    from os import makedirs
    from os.path import exists
    from metapensiero.extjs.desktop.pyramid import configure

    if not 'desktop.version' in settings:
        settings['desktop.version'] = __exact_version__

    if settings['desktop.version'] != 'test':
        engine = engine_from_config(settings, 'sqlalchemy.')
        DBSession.configure(bind=engine)

    if not exists(settings['sol.portraits_dir']):
        makedirs(settings['sol.portraits_dir'], mode=0o700)

    if not exists(settings['sol.emblems_dir']):
        makedirs(settings['sol.emblems_dir'], mode=0o700)

    bckdir = settings.get('sol.backups_dir', None)
    if bckdir and bckdir != 'None' and not exists(bckdir):
        makedirs(bckdir, mode=0o700)

    timeout = settings.get('session.timeout', 24*60*60)
    if timeout == 'None':
        timeout = None
    else:
        timeout = int(timeout)

    reissue_time = settings.get('session.reissue_time', 24*60*60)
    if reissue_time == 'None':
        reissue_time = None
    else:
        reissue_time = int(reissue_time)

    session_factory = SignedCookieSessionFactory(settings['session.secret'],
                                                 timeout=timeout,
                                                 reissue_time=reissue_time)
    config = Configurator(settings=settings, session_factory=session_factory)

    config.include('pyramid_chameleon')
    config.include('pyramid_mako')

    configure(config)

    config.add_translation_dirs('sol:locale/')

    config.add_static_view('static', 'static', cache_max_age=12*60*60)

    config.add_route('favicon', '/favicon.ico')
    config.add_view(favicon_view, route_name='favicon')

    config.add_route('robots', '/robots.txt')
    config.add_view(robots_view, route_name='robots')

    # auth

    config.add_route('login', '/auth/login')
    config.add_route('logout', '/auth/logout')

    # bio

    config.add_route('backup', '/bio/backup')
    config.add_route('dump', '/bio/dump')
    config.add_route('merge_players', '/bio/mergePlayers')
    config.add_route('recompute_rating', '/bio/recomputeRating')
    config.add_route('save_changes', '/bio/saveChanges')
    config.add_route('upload', '/bio/upload')

    # data

    config.add_route('championships', '/data/championships')
    config.add_route('clubs', '/data/clubs')
    config.add_route('countries', '/data/countries')
    config.add_route('federations', '/data/federations')
    config.add_route('languages', '/data/languages')
    config.add_route('owners', '/data/owners')
    config.add_route('players', '/data/players')
    config.add_route('rated_players', 'data/ratedPlayers')
    config.add_route('ratings', '/data/ratings')
    config.add_route('tourneys', '/data/tourneys')

    # tourney

    config.add_route('assign_prizes', '/tourney/assignPrizes')
    config.add_route('boards', '/tourney/boards')
    config.add_route('clock', '/tourney/clock')
    config.add_route('competitors', '/tourney/competitors')
    config.add_route('delete_from_turn', '/tourney/deleteFromTurn')
    config.add_route('matches', '/tourney/matches')
    config.add_route('new_turn', '/tourney/newTurn')
    config.add_route('final_turn', '/tourney/finalTurn')
    config.add_route('ranking', '/tourney/ranking')
    config.add_route('replay_today', '/tourney/replayToday')
    config.add_route('reset_prizes', '/tourney/resetPrizes')
    config.add_route('tourney_players', '/tourney/players')
    config.add_route('update_ranking', '/tourney/updateRanking')

    # lit

    config.add_route('lit', '/lit')
    config.add_route('lit_championship', '/lit/championship/{guid}')
    config.add_route('lit_club', '/lit/club/{guid}')
    config.add_route('lit_latest', '/lit/latest')
    config.add_route('lit_player', '/lit/player/{guid}')
    config.add_route('lit_player_opponent', '/lit/player/{guid}/{opponent}')
    config.add_route('lit_player_matches', '/lit/matches/{guid}')
    config.add_route('lit_players', '/lit/players')
    config.add_route('lit_players_list', '/lit/players/{letter}/{country}')
    config.add_route('lit_rating', '/lit/rating/{guid}')
    config.add_route('lit_tourney', '/lit/tourney/{guid}')

    config.add_static_view('/lit/emblem', settings['sol.emblems_dir'])
    config.add_static_view('/lit/portrait', settings['sol.portraits_dir'])

    # printouts

    config.add_route('pdf_badges', '/pdf/badges/{id}')
    config.add_route('pdf_matches', '/pdf/matches/{id}')
    config.add_route('pdf_nationalranking', '/pdf/nationalranking/{id}')
    config.add_route('pdf_participants', '/pdf/participants/{id}')
    config.add_route('pdf_ranking', '/pdf/ranking/{id}')
    config.add_route('pdf_ratingranking', '/pdf/ratingranking/{id}')
    config.add_route('pdf_results', '/pdf/results/{id}')
    config.add_route('pdf_scorecards', '/pdf/scorecards/{id}')
    config.add_route('pdf_championshipranking', '/pdf/championshipranking/{id}')

    # charts

    config.add_route('svg_playersdist', '/svg/playersdist')
    config.add_route('svg_ratingchart', '/svg/ratingchart/{id}')
    config.add_route('svg_player_opponent', '/svg/player/{guid}/{opponent}')

    config.scan(ignore='sol.tests')

    return config.make_wsgi_app()
