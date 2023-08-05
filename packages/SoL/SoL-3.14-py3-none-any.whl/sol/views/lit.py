# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Light user interface controller
# :Creato:    ven 12 dic 2008 09:18:37 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from datetime import date
import logging

from markupsafe import escape

from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError
from pyramid.view import view_config

from sqlalchemy import distinct, func, select
from sqlalchemy.orm.exc import NoResultFound

from . import get_request_logger
from ..i18n import translatable_string as _, translator, gettext, ngettext
from ..models import (
    DBSession,
    Championship,
    Club,
    Player,
    Rating,
    Tourney,
    )


logger = logging.getLogger(__name__)


@view_config(route_name="lit", renderer="lit/index.mako")
def index(request):
    from collections import defaultdict

    sess = DBSession()

    clubs = sess.query(Club).all()
    nclubs = len(clubs)
    nfeds = len([c for c in clubs if c.isfederation])
    ntourneys = sess.query(func.count(Tourney.idtourney)).scalar()
    nchampionships = sess.query(func.count(Championship.idchampionship)).scalar()
    nplayers = sess.query(func.count(Player.idplayer)).scalar()
    npcountries = sess.query(func.count(distinct(Player.nationality))) \
                      .filter(Player.nationality != None).scalar()
    nratings = sess.query(func.count(Rating.idrating)).scalar()
    bycountry = defaultdict(list)
    for club in clubs:
        bycountry[(club.country, club.nationality)].append(club)

    return {
        "_": gettext,
        "clubsbycountry": bycountry,
        "nccountries": len(bycountry),
        "nchampionships": nchampionships,
        "nclubs": nclubs,
        "nfederations": nfeds,
        "ngettext": ngettext,
        "npcountries": npcountries,
        "nplayers": nplayers,
        "nratings": nratings,
        "ntourneys": ntourneys,
        "request": request,
        "session": sess,
        "today": date.today(),
        "version": request.registry.settings['desktop.version'],
    }


def get_data(request, klass):
    t = translator(request)

    guid = request.matchdict['guid']
    sess = DBSession()

    try:
        entity = sess.query(klass).filter_by(guid=guid).one()
    except NoResultFound:
        e = t(_('No $entity with guid $guid'),
              mapping=dict(entity=klass.__name__.lower(), guid=guid))
        get_request_logger(request, logger).error("Couldn't create page: %s", e)
        raise HTTPBadRequest(str(e))
    except Exception as e: # pragma: no cover
        get_request_logger(request, logger).critical("Couldn't create page: %s", e,
                                                     exc_info=True)
        raise HTTPInternalServerError(str(e))
    else:
        return {
            '_': gettext,
            'entity': entity,
            'escape': escape,
            'ngettext': ngettext,
            'request': request,
            'session': sess,
            'today': date.today(),
            'version': request.registry.settings['desktop.version'],
        }


@view_config(route_name="lit_championship", renderer="lit/championship.mako")
def championship(request):
    data = get_data(request, Championship)

    if data["entity"].closed:
        request.response.cache_control.public = True
        request.response.cache_control.max_age = 60*60*24*365

    return data


@view_config(route_name="lit_club", renderer="lit/club.mako")
def club(request):
    return get_data(request, Club)


@view_config(route_name="lit_player", renderer="lit/player.mako")
def player(request):
    return get_data(request, Player)


@view_config(route_name="lit_player_opponent", renderer="lit/player_opponent.mako")
def opponent(request):
    data = get_data(request, Player)

    oguid = request.matchdict['opponent']
    try:
        opponent = data['session'].query(Player).filter_by(guid=oguid).one()
    except NoResultFound:
        t = translator(request)
        e = t(_('No player with guid $guid'), mapping=dict(guid=oguid))
        get_request_logger(request, logger).error("Couldn't create page: %s", e)
        raise HTTPBadRequest(str(e))
    except Exception as e: # pragma: no cover
        get_request_logger(request, logger).critical("Couldn't create page: %s", e,
                                                     exc_info=True)
        raise HTTPInternalServerError(str(e))
    else:
        data['opponent'] = opponent
        return data


@view_config(route_name="lit_player_matches", renderer="lit/player_matches.mako")
def matches(request):
    return get_data(request, Player)



@view_config(route_name="lit_players", renderer="lit/players.mako")
def players(request):
    from itertools import groupby
    from operator import itemgetter
    from gettext import translation
    from pycountry import LOCALES_DIR, countries

    lname = getattr(request, 'locale_name', 'en')
    try:
        t = translation('iso3166', LOCALES_DIR, languages=[lname]).gettext
    except IOError:
        t = lambda x: x

    sess = DBSession()
    pt = Player.__table__
    query = sess.execute(select([func.substr(pt.c.lastname, 1, 1),
                                 pt.c.nationality,
                                 func.count()]).group_by(func.substr(pt.c.lastname, 1, 1),
                                                         pt.c.nationality))
    index = []
    for letter, countsbycountry in groupby(query, itemgetter(0)):
        bycountry = []
        for country in countsbycountry:
            ccode = country[1]
            if ccode:
                if ccode == 'eur':
                    cname = translator(request)(_('Europe'))
                else:
                    cname = t(countries.get(alpha3=ccode).name)
            else:
                cname = translator(request)(_('Unspecified country'))

            bycountry.append(dict(code=ccode, country=cname, count=country[2]))
        bycountry.sort(key=itemgetter('country'))
        index.append((letter, bycountry))

    return {
        '_': gettext,
        'ngettext': ngettext,
        'today': date.today(),
        'version': request.registry.settings['desktop.version'],
        'index': index,
        'request': request,
    }


@view_config(route_name="lit_players_list", renderer="lit/players_list.mako")
def players_list(request):
    from gettext import translation
    from pycountry import LOCALES_DIR, countries

    lname = getattr(request, 'locale_name', 'en')
    try:
        t = translation('iso3166', LOCALES_DIR, languages=[lname]).gettext
    except IOError:
        t = lambda x: x

    letter = request.matchdict['letter']
    ccode = request.matchdict['country']

    if ccode == 'None':
        ccode = None

    if ccode:
        if ccode == 'eur':
            cname = translator(request)(_('Europe'))
        else:
            cname = t(countries.get(alpha3=ccode).name)
    else:
        cname = translator(request)(_('Unspecified country'))

    sess = DBSession()
    players = sess.query(Player) \
                  .filter(func.substr(Player.lastname, 1, 1) == letter,
                          Player.nationality == ccode) \
                  .order_by(Player.lastname, Player.firstname)

    return {
        '_': gettext,
        'code': ccode,
        'country': cname,
        'letter': letter,
        'ngettext': ngettext,
        'players': players,
        'request': request,
        'today': date.today(),
        'version': request.registry.settings['desktop.version'],
    }


@view_config(route_name="lit_rating", renderer="lit/rating.mako")
def rating(request):
    data = get_data(request, Rating)
    sess = data['session']
    rating = data['entity']
    tt = Tourney.__table__
    data['ntourneys'] = sess.execute(select([func.count(tt.c.idtourney)],
                                            tt.c.idrating==rating.idrating)).first()[0]
    return data


@view_config(route_name="lit_tourney", renderer="lit/tourney.mako")
def tourney(request):
    t = translator(request)

    turn = request.params.get('turn')
    if turn is not None:
        try:
            turn = int(turn)
        except ValueError:
            e = t(_('Invalid turn: $turn'), mapping=dict(turn=repr(turn)))
            get_request_logger(request, logger).error("Couldn't create page: %s", e)
            raise HTTPBadRequest(str(e))

    data = get_data(request, Tourney)
    data["turn"] = turn
    data["player"] = request.params.get('player')

    if data["entity"].prized:
        request.response.cache_control.public = True
        request.response.cache_control.max_age = 60*60*24*365

    return data


@view_config(route_name="lit_latest", renderer="lit/latest.mako")
def latest(request):
    t = translator(request)

    n = request.params.get('n')
    if n is not None:
        try:
            n = int(n)
        except ValueError:
            e = t(_('Invalid number of tourneys: $n'), mapping=dict(n=repr(n)))
            get_request_logger(request, logger).error("Couldn't create page: %s", e)
            raise HTTPBadRequest(str(e))
    else:
        n = 20

    sess = DBSession()
    tourneys = sess.query(Tourney).filter_by(prized=True).order_by(Tourney.date.desc())[:n]

    return {
        '_': gettext,
        'escape': escape,
        'n': len(tourneys),
        'ngettext': ngettext,
        'request': request,
        'session': DBSession(),
        'today': date.today(),
        'tourneys': tourneys,
        'version': request.registry.settings['desktop.version'],
    }
