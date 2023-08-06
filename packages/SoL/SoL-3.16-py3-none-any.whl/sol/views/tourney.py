# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Tourney controller
# :Creato:    gio 23 ott 2008 11:13:02 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import logging

from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.view import view_config

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query

from . import get_request_logger
from ..i18n import translatable_string as _, translator
from ..models import (
    Competitor,
    DBSession,
    Match,
    Player,
    Tourney,
    )
from ..models.errors import OperationAborted
from . import expose, unauthorized_for_guest


logger = logging.getLogger(__name__)


@view_config(route_name="tourney_players", renderer="json")
@expose(Player, fields='idplayer,description'.split(','))
def players(request, results):
    return results


@view_config(route_name="competitors", renderer="json")
@expose(Competitor,
        fields=('player1FullName,player2FullName,'
                'player3FullName,player4FullName,'
                'player1Nationality,player1Sex,'
                'idcompetitor,retired,idplayer1,'
                'idplayer2,idplayer3,idplayer4,'
                'rate,idtourney,player1LastName,player1FirstName').split(','),
        metadata=dict(
    player1FullName=dict(label=_('Player'),
                         hint=_('Full name of the player.'),
                         lookup=dict(url='/tourney/players?sort=lastname,firstname',
                                     idField='idplayer',
                                     lookupField='idplayer1',
                                     displayField='description',
                                     width=200,
                                     pageSize=12)),
    player2FullName=dict(label=_('2nd player'),
                         hint=_('Full name of the second player.'),
                         lookup=dict(url='/tourney/players?sort=lastname,firstname',
                                     idField='idplayer',
                                     lookupField='idplayer2',
                                     displayField='description',
                                     width=200,
                                     pageSize=12)),
    player3FullName=dict(label=_('3rd player'),
                         hint=_('Full name of the third player.'),
                         lookup=dict(url='/tourney/players?sort=lastname,firstname',
                                     idField='idplayer',
                                     lookupField='idplayer3',
                                     displayField='description',
                                     width=200,
                                     pageSize=12)),
    player4FullName=dict(label=_('4th player'),
                         hint=_('Full name of the fourth player.'),
                         lookup=dict(url='/tourney/players?sort=lastname,firstname',
                                     idField='idplayer',
                                     lookupField='idplayer4',
                                     displayField='description',
                                     width=200,
                                     pageSize=12)),
    player1Nationality=dict(label=_('Nationality'),
                            hint=_('First player nationality.'),
                            hidden=True,
                            readOnly=True),
    player1Sex=dict(label=_('Sex'),
                    hint=_('First player sex.'),
                    hidden=True,
                    readOnly=True),
    player1FirstName=dict(label=_("First player's name"),
                          hint=_("First name of the first player."),
                          hidden=True,
                          readOnly=True),
    player1LastName=dict(label=_("First player's surname"),
                         hint=_("Last name of the first player."),
                         hidden=True,
                         readOnly=True),
    rate=dict(label=_('Rate'),
              hint=_('Most recent Glicko rate value of the competitor.'),
              hidden=True,
              readonly=True)
    ))
def competitors(request, results):
    from gettext import translation
    from pycountry import LOCALES_DIR, countries

    # Add the full name of the first player country, used as an hint
    # on the competitors pane flag icons
    if 'metadata' in results:
        t = translator(request)
        results['metadata']['fields'].append({
            'label': t(_('Country')),
            'hint': t(_('Country name')),
            'name': 'player1Country',
            'hidden': True
        })
    else:
        lname = request.locale_name
        try:
            t = translation('iso3166', LOCALES_DIR, languages=[lname]).gettext
        except IOError:
            t = lambda x: x
        for r in results['root']:
            code = r['player1Nationality']
            if code:
                r['player1Country'] = t(countries.get(alpha3=code).name)
    return results


@view_config(route_name="matches", renderer="json")
@expose(Match,
        fields=('board,description,score1,score2,turn,final,'
                'idmatch,idcompetitor1,idcompetitor2').split(','),
        metadata=dict(
    description=dict(label=_('Match'),
                     hint=_('Competitor 1 vs Competitor 2.'),
                     sortable=False,
                     readonly=True,
                     flex=1),
    turn=dict(hidden=True, readonly=True, width=70),
    board=dict(readonly=True, width=70),
    score1=dict(width=70),
    score2=dict(width=70),
    final=dict(hidden=True, readonly=True),
    ))
def matches(request, results):
    return results


@view_config(route_name="ranking", renderer="json", request_param="turn")
def rankingForTurn(request):
    try:
        sess = DBSession()
        params = request.params
        idtourney = int(params['filter_idtourney'])
        turn = int(params['turn'])

        tourney = sess.query(Tourney).get(idtourney)

        ranking = [dict(rank=i, idcompetitor=c.idcompetitor, description=c.description,
                        points=r.points, netscore=r.netscore, totscore=r.totscore,
                        bucholz=r.bucholz, rate=r.rate, prize=0,
                        player1Nationality=c.player1Nationality)
                   for i, (c, r) in enumerate(tourney.computeRanking(turn), 1)]

        return dict(success=True, message='Ok', count=len(ranking), root=ranking)
    except Exception as e: # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical("Couldn't compute ranking: %s", message,
                                                     exc_info=True)
        return dict(success=False, message=message)


@view_config(route_name="ranking", renderer="json")
@expose(Query([Competitor]),
        fields=('description,points,bucholz,netscore,prize,totscore,'
                'rate,player1Nationality,idcompetitor').split(','),
        metadata=dict(
    description=dict(label=_('Competitor'),
                     hint=_('Full name of the players.'),
                     sortable=False,
                     readonly=True,
                     flex=1),
    points=dict(readonly=True, width=40, sortable=False),
    bucholz=dict(readonly=True, width=40, sortable=False),
    netscore=dict(readonly=True, width=40, sortable=False),
    totscore=dict(hidden=True, readonly=True, width=40, sortable=False),
    prize=dict(hidden=True, width=55, sortable=False, decimals=2, type='float'),
    rate=dict(label=_('Rate'),
              hint=_('Most recent Glicko rate of the competitor (if'
                     ' tourney is associated with a rating).'),
              hidden=True,
              align='right',
              type='int',
              readonly=True,
              width=50),
    player1Nationality=dict(label=_('Nationality'),
                            hint=_('Nationality of the competitor.'),
                            hidden=True,
                            readonly=True,
                            width=40)
    ))
def ranking(request, results):
    from operator import itemgetter

    t = translator(request)
    if 'metadata' in results:
        results['metadata']['fields'].insert(0, {
            'label': t(_('Rank')),
            'hint': t(_('Position in the ranking.')),
            'width': 30,
            'readonly': True,
            'name': 'rank',
            'align': 'right',
            'type': 'int' })
    else:
        ranking = results['root']
        # Match the local ordering applied by the Ranking panel, so the "rank" field is
        # reasonable: by ascending player's name, then by descending ranking position.
        ranking.sort(key=itemgetter('description'))
        ranking.sort(key=itemgetter('prize', 'points', 'bucholz',
                                    'netscore', 'totscore', 'rate'),
                     reverse=True)
        for i, r in enumerate(ranking, 1):
            r['rank'] = i
    return results


_matches_t = Match.__table__
_tourneys_t = Tourney.__table__

@view_config(route_name="boards", renderer="json")
@expose(Query([Match])
        .filter(_matches_t.c.turn==_tourneys_t.c.currentturn)
        .filter(_matches_t.c.idtourney==_tourneys_t.c.idtourney)
        .order_by(_matches_t.c.board),
        fields=('board,idcompetitor1,competitor1FullName,'
                'idcompetitor2,competitor2FullName,idmatch,'
                'idtourney,score1,score2').split(','))
def boards(request, results):
    return results


@view_config(route_name="delete_from_turn", renderer="json")
@unauthorized_for_guest
def deleteFromTurn(request):
    "Delete already played turns, recomputing the ranking."

    try:
        sess = DBSession()
        params = request.params
        idtourney = int(params['idtourney'])
        fromturn = int(params['fromturn'])

        tourney = sess.query(Tourney).get(idtourney)

        if tourney.prized:
            tourney.resetPrizes()

        delmatches = [m for m in tourney.matches if m.turn >= fromturn]
        for match in delmatches:
            sess.delete(match)

        tourney.currentturn = fromturn-1
        if tourney.finalturns:
            tourney.finalturns = any(m for m in tourney.matches
                                     if m.turn < fromturn and m.final)
        tourney.countdownstarted = None
        sess.flush()

        # recompute the ranking
        sess.expunge(tourney)
        tourney = sess.query(Tourney).get(idtourney)
        tourney.updateRanking()
        sess.flush()

        success = True
        message = 'Ok'
    except Exception as e: # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical("Couldn't delete turns: %s", message,
                                                     exc_info=True)
        success = False

    return dict(success=success, message=message,
                currentturn=tourney.currentturn,
                rankedturn=tourney.rankedturn,
                finalturns=tourney.finalturns,
                prized=tourney.prized)


@view_config(route_name="new_turn", renderer="json")
@unauthorized_for_guest
def newTurn(request):
    "Create next turn, if possible."

    try:
        sess = DBSession()
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.query(Tourney).get(idtourney)
        tourney.makeNextTurn()

        sess.flush()

        success = True
        message = 'Ok'
    except OperationAborted as e: # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).error("Couldn't create next turn: %s", message)
        success = False
    except Exception as e: # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical("Couldn't create next turn: %s",
                                                     message, exc_info=True)
        success = False

    return dict(success=success, message=message,
                currentturn=tourney.currentturn,
                rankedturn=tourney.rankedturn,
                finalturns=tourney.finalturns,
                prized=tourney.prized)

@view_config(route_name="final_turn", renderer="json")
@unauthorized_for_guest
def finalTurn(request):
    "Create final turn."

    try:
        sess = DBSession()
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.query(Tourney).get(idtourney)
        tourney.makeFinalTurn()

        sess.flush()

        success = True
        message = 'Ok'
    except OperationAborted as e: # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).error("Couldn't create final turn: %s", message)
        success = False
    except Exception as e: # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical("Couldn't create final turn: %s",
                                                     message, exc_info=True)
        success = False

    return dict(success=success, message=message,
                currentturn=tourney.currentturn,
                rankedturn=tourney.rankedturn,
                finalturns=tourney.finalturns,
                prized=tourney.prized)


@view_config(route_name="update_ranking", renderer="json")
@unauthorized_for_guest
def updateRanking(request):
    "Recompute current ranking."

    try:
        sess = DBSession()
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.query(Tourney).get(idtourney)
        tourney.updateRanking()

        sess.flush()

        success = True
        message = 'Ok'
    except Exception as e:
        message = str(e)
        get_request_logger(request, logger).critical("Couldn't update the ranking: %s",
                                                     message, exc_info=True)
        success = False
    return dict(success=success, message=message,
                currentturn=tourney.currentturn,
                rankedturn=tourney.rankedturn,
                finalturns=tourney.finalturns,
                prized=tourney.prized)


@view_config(route_name="assign_prizes", renderer="json")
@unauthorized_for_guest
def assignPrizes(request):
    "Assign final prizes."

    try:
        sess = DBSession()
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.query(Tourney).get(idtourney)
        tourney.assignPrizes()

        if tourney.rating is not None:
            tourney.rating.recompute(tourney.date)

        sess.flush()

        success = True
        message = 'Ok'
    except Exception as e: # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical("Couldn't assign prizes: %s", message,
                                                     exc_info=True)
        success = False
    return dict(success=success, message=message,
                currentturn=tourney.currentturn,
                rankedturn=tourney.rankedturn,
                finalturns=tourney.finalturns,
                prized=tourney.prized)


@view_config(route_name="reset_prizes", renderer="json")
@unauthorized_for_guest
def resetPrizes(request):
    "Reset assigned final prizes."

    try:
        sess = DBSession()
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.query(Tourney).get(idtourney)
        tourney.resetPrizes()

        sess.flush()

        success = True
        message = 'Ok'
    except Exception as e: # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical("Couldn't reset prizes: %s", message,
                                                     exc_info=True)
        success = False
    return dict(success=success, message=message,
                currentturn=tourney.currentturn,
                rankedturn=tourney.rankedturn,
                finalturns=tourney.finalturns,
                prized=tourney.prized)


@view_config(route_name="replay_today", renderer="json")
@unauthorized_for_guest
def replayToday(request):
    "Replicate the given tourney today."

    from datetime import date

    t = translator(request)

    try:
        sess = DBSession()
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.query(Tourney).get(idtourney)
        new = tourney.replay(date.today(), request.session['user_id'])

        sess.flush()

        success = True
        message = t(_('Created "$tourney" in championship "$championship"',
                      mapping=dict(tourney=new.description,
                                   championship=new.championship.description)))
    except IntegrityError as e: # pragma: no cover
        message = t(_('Could not duplicate the tourney because there is'
                      ' already an event today, sorry!'))
        get_request_logger(request, logger).error("Couldn't duplicate tourney:"
                                                  " there is already an event today, sorry!")
        success = False
    except Exception as e: # pragma: no cover
        message = str(e)
        get_request_logger(request, logger).critical("Couldn't duplicate tourney: %s",
                                                     message, exc_info=True)
        success = False
    return dict(success=success, message=message)


@view_config(route_name="clock", request_method="POST", renderer="json")
def clockCountdownStarted(request):
    "Register the countdown start timestamp."

    sess = DBSession()
    params = request.params
    idtourney = int(params['idtourney'])
    start = int(params['start'])
    tourney = sess.query(Tourney).get(idtourney)
    if not tourney.prized:
        tourney.countdownstarted = start
        logger.debug("Countdown for %s started", repr(tourney))
        return dict(success=True, message="Ok")
    else:
        get_request_logger(request, logger).error("Attempt to start countdown for %s ignored",
                                                  repr(tourney))
        return dict(success=False, message="Tourney is prized")


@view_config(route_name="clock", renderer="clock.mako")
def clock(request):
    "Show the clock."

    from ..printouts import ordinal

    t = translator(request)

    try:
        sess = DBSession()
        params = request.params
        idtourney = int(params['idtourney'])

        tourney = sess.query(Tourney).get(idtourney)

        return dict(
            _=t,
            # get_javascripts(config['debug'], appname='clock')
            javascripts=[('Alarm clock',
                          ('/static/clock/alarmclock.js',
                           '/static/clock/soundmanager2.js'))],
            # get_stylesheets(config['debug'], appname='clock')
            stylesheets=[('Alarm clock',
                          ('/static/clock/clock.css',))],
            duration=tourney.duration,
            prealarm=tourney.prealarm,
            currentturn=ordinal(tourney.currentturn),
            starttime=tourney.countdownstarted or '',
            notifystart=request.path_qs)
    except Exception as e: # pragma: no cover
        get_request_logger(request, logger).critical("Couldn't show the clock: %s", e,
                                                     exc_info=True)
        raise HTTPInternalServerError(str(e))
