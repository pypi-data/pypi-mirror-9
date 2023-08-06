# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    lun 16 dic 2013 20:20:40 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from pyramid.view import view_config

from pyramid.httpexceptions import HTTPBadRequest

from sqlalchemy import select
from sqlalchemy.orm.exc import NoResultFound

from ..i18n import translatable_string as _, translator
from ..models import DBSession, Player, Rate, Rating


@view_config(route_name="svg_ratingchart")
def ratingChart(request):
    from itertools import groupby
    from operator import itemgetter
    import pygal

    t = translator(request)

    sas = DBSession()

    try:
        idrating = int(request.matchdict['id'])
    except ValueError:
        try:
            rating = sas.query(Rating).filter_by(guid=request.matchdict['id']).one()
        except NoResultFound:
            raise HTTPBadRequest("Bad rating guid")
    else:
        rating = sas.query(Rating).get(idrating)
        if rating is None:
            raise HTTPBadRequest("Bad rating id")

    if 'idplayer' in request.params:
        try:
            playerids = list(map(int, request.params.getall('idplayer')))
        except (TypeError, ValueError):
            raise HTTPBadRequest("Bad player ids")
    else:
        playerguids = list(request.params.getall('player'))
        if not playerguids:
            raise HTTPBadRequest("Missing players guids")
        pt = Player.__table__
        playerids = [p[0] for p in sas.execute(select([pt.c.idplayer])
                                               .where(pt.c.guid.in_(playerguids)))]
        if not playerids:
            raise HTTPBadRequest("Wrong players guids")

    width = int(request.params.get('width', 800))
    height = int(request.params.get('height', 600))

    chart = pygal.Line(x_label_rotation=20, margin=30,
                       width=width, height=height)
    chart.title = t(_('Rating “$rating”',
                      mapping=dict(rating=rating.caption(False))))

    rt = Rate.__table__

    q = select([rt.c.idplayer, rt.c.date, rt.c.rate]) \
        .where(rt.c.idrating == rating.idrating)

    if playerids:
        q = q.where(rt.c.idplayer.in_(playerids))

    q = q.order_by(rt.c.idplayer, rt.c.date)

    dates = set()
    pdata = []

    for pid, rates in groupby(sas.execute(q), itemgetter(0)):
        p = {}
        pdata.append((pid, p))
        for rate in rates:
            d = rate[1]
            r = rate[2]
            dates.add(d)
            p[d] = r

    dates = list(sorted(dates))
    # TRANSLATORS: this is a Python strftime() format, see
    # http://docs.python.org/3/library/time.html#time.strftime
    dfmt = t(_('%m-%d-%y'))
    chart.x_labels = [date.strftime(dfmt) for date in dates]

    for pid, data in pdata:
        player = sas.query(Player).get(pid)
        chart.add(player.caption(False), [data.get(date, None) for date in dates])

    response = request.response
    response.body = chart.render()
    response.content_type = 'image/svg+xml'

    return response


@view_config(route_name="svg_playersdist")
def playersDistribution(request):
    from gettext import translation
    from collections import Counter
    from pycountry import LOCALES_DIR, countries
    import pygal

    width = int(request.params.get('width', 800))
    height = int(request.params.get('height', 600))

    lname = request.locale_name
    try:
        ct = translation('iso3166', LOCALES_DIR, languages=[lname]).gettext
    except IOError:
        ct = lambda x: x

    pygal_countries = pygal.i18n.COUNTRIES
    for alpha2 in pygal_countries:
        try:
            c = countries.get(alpha2=alpha2.upper())
        except KeyError:
            pass
        else:
            pygal_countries[alpha2] = ct(c.name)

    t = translator(request)

    chart = pygal.Worldmap(show_legend=False, width=width, height=height)
    chart.title = t(_('Players distribution around the globe'))

    sas = DBSession()

    pt = Player.__table__
    players = sas.execute(select([pt.c.sex, pt.c.nationality])
                          .where(pt.c.nationality != None))

    men = Counter()
    women = Counter()

    for sex, nationality in players:
        try:
            country = countries.get(alpha3=nationality)
        except KeyError:
            pass
        else:
            if sex == 'F':
                counter = women
            else:
                counter = men
            counter[country.alpha2.lower()] += 1

    chart.add(t(_('Females')), women)
    chart.add(t(_('Males')), men)

    response = request.response
    response.body = chart.render()
    response.content_type = 'image/svg+xml'

    return response


@view_config(route_name="svg_player_opponent")
def opponentChart(request):
    import pygal

    t = translator(request)

    sas = DBSession()

    pguid = request.matchdict['guid']
    oguid = request.matchdict['opponent']

    try:
        player = sas.query(Player).filter_by(guid=pguid).one()
    except NoResultFound:
        t = translator(request)
        e = t(_('No player with guid $guid'), mapping=dict(guid=pguid))
        raise HTTPBadRequest(str(e))

    try:
        opponent = sas.query(Player).filter_by(guid=oguid).one()
    except NoResultFound:
        t = translator(request)
        e = t(_('No player with guid $guid'), mapping=dict(guid=oguid))
        raise HTTPBadRequest(str(e))

    width = int(request.params.get('width', 800))
    height = int(request.params.get('height', 600))

    chart = pygal.Line(x_label_rotation=60, margin=30,
                       width=width, height=height, show_y_labels=False)
    chart.title = t(_('Wins trend between $player and $opponent',
                      mapping=dict(player=player.caption(html=False),
                                   opponent=opponent.caption(html=False))))

    matches = player.opponentMatches(opponent)

    # TRANSLATORS: this is a Python strftime() format, see
    # http://docs.python.org/3/library/time.html#time.strftime
    dfmt = t(_('%m-%d-%y'))
    chart.x_labels = [m.tourney.date.strftime(dfmt) for m in matches]

    pwins = 0
    pdata = []
    owins = 0
    odata = []
    for match in matches:
        if match.score1 != match.score2:
            if match.competitor1.player1 is player:
                if match.score1 > match.score2:
                    pwins += 1
                else:
                    owins += 1
            else:
                if match.score1 < match.score2:
                    pwins += 1
                else:
                    owins += 1
        pdata.append(pwins)
        odata.append(owins)

    chart.add(player.caption(False), pdata)
    chart.add(opponent.caption(False), odata)

    response = request.response
    response.body = chart.render()
    response.content_type = 'image/svg+xml'

    return response
