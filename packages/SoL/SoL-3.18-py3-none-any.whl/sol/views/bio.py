# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Batched I/O controller
# :Creato:    lun 09 feb 2009 10:32:22 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from datetime import date
import logging

import transaction

from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError
from pyramid.settings import asbool
from pyramid.view import view_config

from . import get_request_logger, unauthorized_for_guest
from ..i18n import translatable_string as _, ngettext, translator
from ..models import DBSession, Player, Rating, Championship, Tourney
from ..models.bio import changes_logger, dump_sol, load_sol, restore, save_changes
from ..models.errors import LoadError, OperationAborted
from ..models.utils import njoin


logger = logging.getLogger(__name__)


@view_config(route_name='backup')
def backup(request):
    "Backup almost everything in a ZIP file."

    from ..models.bio import backup

    only_played_tourneys = asbool(request.params.get('only_played_tourneys', False))
    settings = request.registry.settings
    response = request.response

    response.body = backup(DBSession(),
                           settings['sol.portraits_dir'],
                           settings['sol.emblems_dir'],
                           only_played_tourneys=only_played_tourneys)
    response.content_type = 'application/zip'
    filename = '%s.zip' % date.today().isoformat()
    response.content_disposition = 'attachment; filename=%s' % filename

    return response


@view_config(route_name='dump')
def dump(request):
    "Dump tourneys in a portable format."

    from re import sub
    from sqlalchemy.orm import join

    params = request.params
    settings = request.registry.settings
    debug = asbool(settings['desktop.debug'])

    t = translator(request)

    try:
        sess = DBSession()

        compress = asbool(params.get('gzip', not debug))
        ext = 'sol.gz' if compress else 'sol'

        if 'idtourney' in params:
            idtourney = int(params['idtourney'])
            tourney = sess.query(Tourney).get(idtourney)
            if tourney is None: # pragma: no cover
                raise HTTPBadRequest(
                    t(_('Tourney $idtourney does not exist',
                        mapping=dict(idtourney=idtourney))))

            tourneys = [tourney]
            sdesc = tourneys[0].championship.description
            sdesc = sdesc.encode('ascii', 'ignore').decode('ascii')
            cturn = tourneys[0].currentturn
            filename = '%s-%s%s.%s' % (sub(r'\W+', '_', sdesc),
                                       str(tourneys[0].date),
                                       '+%d' % cturn if cturn else '',
                                       ext)
        elif 'idchampionship' in params:
            idchampionship = int(params['idchampionship'])
            tourneys = sess.query(Tourney) \
                       .filter_by(idchampionship=idchampionship) \
                       .order_by(Tourney.date).all()
            if not tourneys: # pragma: no cover
                raise HTTPBadRequest(
                    t(_('No tourneys in championship $idchampionship',
                        mapping=dict(idchampionship=idchampionship))))

            desc = tourneys[0].championship.description
            sdesc = desc.encode('ascii', 'ignore').decode('ascii')
            filename = '%s.%s' % (sub(r'\W+', '_', sdesc), ext)
        elif 'idclub' in params:
            idclub = int(params['idclub'])
            tourneys = sess.query(Tourney) \
                       .select_from(join(Tourney, Championship)) \
                       .filter(Championship.idclub == idclub) \
                       .order_by(Tourney.date).all()
            if not tourneys: # pragma: no cover
                raise HTTPBadRequest(
                    t(_('No tourneys organized by club $idclub',
                        mapping=dict(idclub=idclub))))

            desc = tourneys[0].championship.club.description
            cdesc = desc.encode('ascii', 'ignore').decode('ascii')
            filename = '%s.%s' % (sub(r'\W+', '_', cdesc), ext)
        else:
            tourneys = sess.query(Tourney).order_by(Tourney.date).all()
            if not tourneys:
                raise HTTPBadRequest(t(_('No tourneys at all')))

            filename = '%s.%s' % (date.today().isoformat(), ext)

        response = request.response
        if compress:
            response.body = dump_sol(tourneys, compress)
            response.content_type = 'application/x-gzip'
        else:
            response.text = dump_sol(tourneys, compress)
            response.content_type = 'text/x-yaml'
        response.content_disposition = 'attachment; filename=%s' % filename

        return response

    except HTTPBadRequest as e: # pragma: no cover
        get_request_logger(request, logger).error("Couldn't dump tourney: %s", e)
        raise

    except Exception as e: # pragma: no cover
        get_request_logger(request, logger).critical("Couldn't dump tourney: %s", e,
                                                     exc_info=True)
        raise HTTPInternalServerError(str(e))


@view_config(route_name='merge_players', renderer='json')
@unauthorized_for_guest
def mergePlayers(request):
    "Merge several players into a single one."

    tid = int(request.params['tid'])
    sids = request.params.getall('sids')
    if not isinstance(sids, list):
        sids = [sids]
    sids = [int(i) for i in sids]

    sas = DBSession()
    player = sas.query(Player).get(tid)
    try:
        replaced = player.mergePlayers(sids, get_request_logger(request, changes_logger))
    except OperationAborted as e:
        msg = str(e)
        get_request_logger(request, logger).error("Couldn't merge players: %s", msg)
        success = False
    except Exception as e:
        msg = str(e)
        get_request_logger(request, logger).exception("Couldn't merge players: %s", msg)
        success = False
    else:
        count = len(replaced)
        msg = ngettext('$count player has been merged into $player',
                       '$count players has been merged into $player',
                       count, mapping=dict(count=count,
                                           player=player.caption(False)))
        success = True
    return dict(success=success, message=msg)


@view_config(route_name='save_changes', renderer='json')
@unauthorized_for_guest
def saveChanges(request):
    """Save changes made to a set of records."""

    from sqlalchemy.exc import DBAPIError, IntegrityError, InvalidRequestError
    from metapensiero.sqlalchemy.proxy.json import json2py

    t = translator(request)
    rlogger = get_request_logger(request, logger)

    params = request.params
    mr = json2py(params['modified_records'])
    dr = json2py(params['deleted_records'])

    sess = DBSession()

    success = False
    try:
        clogger = get_request_logger(request, changes_logger)
        iids, mids, dids = save_changes(sess, request, mr, dr, clogger)
        sess.flush()
        success = True
        message = 'Ok'
        infomsg = []
        ni = len(iids)
        if ni:
            infomsg.append('%d new records' % ni)
        nm = len(mids)
        if nm:
            infomsg.append('%d changed records' % nm)
        nd = len(dids)
        if nd:
            infomsg.append('%d deleted records' % nd)
        if infomsg:
            rlogger.info('Changes successfully committed: %s',
                         njoin(infomsg, localized=False))
    except OperationAborted as e:
        message = str(e)
        rlogger.warning('Operation refused: %s', message)
    except (IntegrityError, InvalidRequestError) as e:
        # Catch most common reasons, ugly as it is
        excmsg = str(e)
        if ('columns date, idchampionship are not unique' in excmsg
            or (' UNIQUE constraint failed:'
                ' tourneys.date, tourneys.idchampionship') in excmsg):
            rlogger.warning('Not allowing duplicated event: %s', excmsg)
            message = t(_('There cannot be two tourneys of the same'
                          ' championship on the same day, sorry!'))
        elif (' UNIQUE constraint failed:'
                ' championships.description, championships.idclub') in excmsg:
            rlogger.warning('Not allowing duplicated championship: %s', excmsg)
            message = t(_('There cannot be two championships with the same'
                          ' description organized by the same club!'))
        elif ' UNIQUE constraint failed: clubs.description' in excmsg:
            rlogger.warning('Not allowing duplicated club: %s', excmsg)
            message = t(_('There cannot be two clubs with the same description!'))
        elif ' UNIQUE constraint failed: ratings.description' in excmsg:
            rlogger.warning('Not allowing duplicated rating: %s', excmsg)
            message = t(_('There cannot be two ratings with the same description!'))
        elif ' UNIQUE constraint failed: championships.description' in excmsg:
            rlogger.warning('Not allowing duplicated championship: %s', excmsg)
            message = t(_('There cannot be two championships with the same description!'))
        elif (' UNIQUE constraint failed: players.lastname, players.firstname,'
              ' players.nickname' in excmsg or 'columns lastname, firstname, nickname'
              ' are not unique' in excmsg):
            rlogger.warning('Not allowing duplicated player: %s', excmsg)
            message = t(_('There cannot be two players with the same'
                          ' firstname, lastname and nickname!'))
        elif (' may not be NULL' in excmsg
              or ' NOT NULL constraint failed' in excmsg):
            rlogger.warning('Incomplete data: %s', excmsg)
            message = t(_('Missing information prevents saving changes!'))
            message += "<br/>"
            message += t(_('Some mandatory fields were not filled in, please recheck.'))
        else:
            rlogger.error('Could not save changes: %s', excmsg)
            message = t(_('Integrity error prevents saving changes!'))
            message += "<br/>"
            message += t(_('Most probably a field contains an invalid value:'
                           ' consult the application log for details.'))
    except DBAPIError as e:
        rlogger.error('Could not save changes: %s', e)
        message = t(_('Error occurred while saving changes!'))
        message += "<br/>"
        message += t(_('Please inform the admin or consult the application log.'))
    except Exception as e: # pragma: no cover
        rlogger.critical('Could not save changes: %s', e, exc_info=True)
        message = t(_('Internal error!'))
        message += "<br/>"
        message += t(_('Please inform the admin or consult the application log.'))

    return dict(success=success, message=message)


@view_config(route_name='upload')
def upload(request):
    "Handle the upload of tourneys data."

    from metapensiero.sqlalchemy.proxy.json import py2json

    t = translator(request)

    params = request.params
    archive = params.get('archive')

    if 'user_name' not in request.session or request.session['is_guest']:
        get_request_logger(request, logger).warning('Not allowed to upload %s', archive)

        msg = t(_('Guest users are not allowed to perform this operation, sorry!'))

        # The answer must be "text/html", even if we really return JSON:
        # see the remark regarding `fileUpload` in the ExtJS BasicForm.js

        response = request.response
        response.content_type = 'text/html'
        response.text = py2json(dict(success=False, message=msg))

        return response

    settings = request.registry.settings
    idowner = request.session['user_id']

    success = False
    load = None

    if archive is not None:
        fnendswith = archive.filename.endswith

        if fnendswith('.sol') or fnendswith('.sol.gz'):
            load = load_sol
        elif fnendswith('.zip'):
            if request.session['is_admin']:
                load = lambda sasess, url, content, idowner: restore(
                    sasess,
                    settings['sol.portraits_dir'],
                    settings['sol.emblems_dir'],
                    url,
                    content,
                    idowner)
            else:
                msg = t(_('Only admin can restore whole ZIPs, sorry!'))
                get_request_logger(request, logger).warning('Attempt to restore %s rejected',
                                                            archive.filename)
        else:
            msg = t(_('Unknown file type: $file',
                      mapping=dict(file=archive.filename)))
            get_request_logger(request, logger).warning('Attempt to upload %s rejected',
                                                        archive.filename)
    else:
        msg = t(_('Required "archive" parameter is missing!'))

    if load is not None:
        sas = DBSession()
        try:
            with transaction.manager:
                tourneys, skipped = load(sas, url=archive.filename, content=archive.file,
                                         idowner=idowner)
        except (LoadError, OperationAborted) as e: # pragma: no cover
            msg = str(e)
            success = False
            get_request_logger(request, logger).error('Upload of %s failed: %s',
                                                      archive.filename, msg)
        except Exception as e: # pragma: no cover
            transaction.abort()
            success = False
            msg = t(_('Upload of $file failed: $error',
                      mapping=dict(file=archive.filename, error=type(e).__name__)))
            get_request_logger(request, logger).error('Upload of %s failed: %s',
                                                      archive.filename, e)
        else:
            success = True
            msg = ngettext(
                '$num tourney successfully loaded',
                '$num tourneys successfully loaded',
                len(tourneys), mapping=dict(num=len(tourneys)))
            if skipped:
                msg += ', ' + ngettext(
                    '$num skipped because already present',
                    '$num skipped because already present',
                    skipped, mapping=dict(num=skipped))
            get_request_logger(request, logger).info(
                'Successful upload of %s: %d new tourneys, %d skipped because'
                ' already present', archive.filename, len(tourneys), skipped)

    # The answer must be "text/html", even if we really return JSON:
    # see the remark regarding `fileUpload` in the ExtJS BasicForm.js

    response = request.response
    response.content_type = 'text/html'
    response.text = py2json(dict(success=success, message=msg))

    return response


@view_config(route_name='recompute_rating', renderer='json')
@unauthorized_for_guest
def recomputeRating(request):
    "Recompute a whole Rating."

    t = translator(request)

    rid = int(request.params['idrating'])

    sas = DBSession()
    rating = sas.query(Rating).get(rid)
    if rating is None:
        raise HTTPBadRequest(
            t(_('Rating $idrating does not exist',
                mapping=dict(idrating=rid))))
    else:
        try:
            rating.recompute(scratch=True)
        except Exception as e:
            msg = str(e)
            get_request_logger(request, logger).exception("Couldn't recompute rating: %s", msg)
            success = False
        else:
            msg = t(_('Recomputed rating “$rating”',
                      mapping=dict(rating=rating.caption(False))))
            get_request_logger(request, logger).info('Recomputed rating %r', rating)
            success = True
    return dict(success=success, message=msg)
