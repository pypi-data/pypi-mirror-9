# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Printouts views
# :Creato:    ven 31 ott 2008 16:48:27 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import logging
from os import unlink
from tempfile import mktemp

from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError
from pyramid.view import view_config

from ..models import DBSession
from ..models.errors import OperationAborted
from ..printouts import (
    Badges,
    ChampionshipRanking,
    Matches,
    NationalRanking,
    Participants,
    Ranking,
    RatingRanking,
    Results,
    ScoreCards,
    )

logger = logging.getLogger(__name__)


def _createPdf(request, maker):
    try:
        session = DBSession()
        output = mktemp(prefix='sol')
        args = maker.getArgumentsFromRequest(session, request)
        builder = maker(output, *args)
        try:
            builder.execute(request)

            f = open(output, 'rb')
            content = f.read()
            f.close()
        finally:
            try:
                unlink(output)
            except OSError:
                pass

        response = request.response
        response.content_type = 'application/pdf'
        cdisp = 'attachment; filename=%s.pdf' % maker.__name__
        response.content_disposition = cdisp
        response.body = content
        response.cache_control.public = True
        response.cache_control.max_age = builder.cache_max_age
        return response
    except OperationAborted as e:
        logger.error("Couldn't create report %s: %s", maker.__name__, e)
        raise HTTPBadRequest(str(e))
    except Exception as e:
        logger.critical("Couldn't create report %s: %s", maker.__name__, e, exc_info=True)
        raise HTTPInternalServerError(str(e))


@view_config(route_name='pdf_participants')
def participants(request):
    from os.path import dirname, join
    import sol

    Participants.flags = join(dirname(sol.__file__),
                              'static', 'images', 'flags')
    return _createPdf(request, Participants)


@view_config(route_name='pdf_ranking')
def ranking(request):
    return _createPdf(request, Ranking)


@view_config(route_name='pdf_nationalranking')
def nationalranking(request):
    from os.path import dirname, join
    import sol

    NationalRanking.flags = join(dirname(sol.__file__),
                                 'static', 'images', 'flags')
    return _createPdf(request, NationalRanking)


@view_config(route_name='pdf_results')
def results(request):
    return _createPdf(request, Results)


@view_config(route_name='pdf_matches')
def matches(request):
    return _createPdf(request, Matches)


@view_config(route_name='pdf_scorecards')
def scorecards(request):
    return _createPdf(request, ScoreCards)


@view_config(route_name='pdf_badges')
def badges(request):
    from os.path import dirname, join
    import sol

    settings = request.registry.settings
    Badges.flags = join(dirname(sol.__file__), 'static', 'images', 'flags')
    Badges.emblems = settings['sol.emblems_dir']
    return _createPdf(request, Badges)


@view_config(route_name='pdf_championshipranking')
def championshipranking(request):
    return _createPdf(request, ChampionshipRanking)


@view_config(route_name='pdf_ratingranking')
def ratingranking(request):
    return _createPdf(request, RatingRanking)
