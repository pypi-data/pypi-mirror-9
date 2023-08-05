# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Autentication views
# :Creato:    lun 15 apr 2013 16:48:23 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import logging
from collections import OrderedDict

from sqlalchemy.orm.exc import NoResultFound
import transaction

from pyramid.events import NewRequest, subscriber
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.view import view_config

from . import get_request_logger
from ..i18n import translatable_string as _, translator
from ..models import DBSession, Player, bio


logger = logging.getLogger(__name__)


NO_SUCH_USER = _('No such user!')
NON_EXISTING_USERNAME = _('Non existing username')
MANDATORY_FIELD = _('Mandatory field')
MISSING_FIELDS = _('Missing fields')
FULL_NAME = _('{first_name} {last_name}')
ADMINISTRATOR = _('Administrator')
ANONYMOUS = _('Anonymous')


@subscriber(NewRequest)
def check_authorized_request(event,
                             authorized_paths={'/',
                                               '/auth/login',
                                               '/catalog',
                                               '/extjs-l10n',
                                               '/favicon.ico',
                                               '/robots.txt',
                                               }):
    """Assert the request is authorized.

    This function gets hooked at the Pyramid's ``NewRequest`` event,
    so it will be executed at the start of each new request.

    If the user has been authenticated, or if she is requesting a
    static resource or one of the authentication views, then nothing
    happens. Otherwise an HTTPUnauthorized exception is raised.
    """

    request = event.request

    # Authenticated user?
    session = request.session
    if 'user_id' in session:
        return

    rpath = request.path

    # Anonymous authorized path or static resource?
    sw = rpath.startswith
    if rpath in authorized_paths or sw('/static/') or sw('/desktop/'):
        return
    if request.method == 'GET' and (sw('/bio/')
                                    or sw('/lit/')
                                    or sw('/pdf/')
                                    or sw('/svg/')
                                    or sw('/tourney/clock')
                                    or rpath == '/lit'):
        return
    if sw('/scripts') and request.registry.settings.get('desktop.debug', False):
        return

    get_request_logger(request, logger).error('Unauthorized access to %s', request.path)

    raise HTTPUnauthorized(_('You must re-authenticate yourself'))


MODULES = OrderedDict((
    ("upload", dict(
        classname = 'SoL.module.Upload')),
    ("clubs", dict(
        classname = 'SoL.module.Clubs',
        quickstart = dict(
            name = _('Clubs'),
            iconCls = 'clubs-icon',
            moduleId = 'clubs-win'))),
    ("championships", dict(
        classname = 'SoL.module.Championships',
        quickstart = dict(
            name = _('Championships'),
            iconCls = 'championships-icon',
            moduleId = 'championships-win'))),
    ("tourneys", dict(
        classname = 'SoL.module.Tourneys',
        quickstart = dict(
            name = _('Tourneys'),
            iconCls = 'tourneys-icon',
            moduleId = 'tourneys-win'))),
    ("tourney", dict(
        classname = 'SoL.module.Tourney')),
    ("players", dict(
        classname = 'SoL.module.Players')),
    ("ratings", dict(
        classname = 'SoL.module.Ratings')),
    ("competitors", dict(
        classname = 'SoL.module.Competitors')),
    ("ratedplayers", dict(
        classname = 'SoL.module.RatedPlayers')),
    ("myclubs", dict(
        classname = 'SoL.module.MyClubs',
        shortcut = dict(
            name = _('My clubs'),
            iconCls = 'clubs-shortcut-icon',
            moduleId = 'my-clubs-win'))),
    ("mychampionships", dict(
        classname = 'SoL.module.MyChampionships',
        shortcut = dict(
            name = _('My championships'),
            iconCls = 'championships-shortcut-icon',
            moduleId = 'my-championships-win'))),
    ("mytourneys", dict(
        classname = 'SoL.module.MyTourneys',
        shortcut = dict(
            name = _('My tourneys'),
            iconCls = 'tourneys-shortcut-icon',
            moduleId = 'my-tourneys-win'))),
    ("myplayers", dict(
        classname = 'SoL.module.MyPlayers',
        shortcut = dict(
            name = _('My players'),
            iconCls = 'players-shortcut-icon',
            moduleId = 'my-players-win'))),
    ("myratings", dict(
        classname = 'SoL.module.MyRatings',
        shortcut = dict(
            name = _('My ratings'),
            iconCls = 'ratings-shortcut-icon',
            moduleId = 'my-ratings-win'))),
))


@view_config(route_name='login', renderer='json')
def auth_user(request):
    from socket import gethostbyaddr
    from pyramid.i18n import make_localizer
    from pyramid.interfaces import ILocalizer, ITranslationDirectories
    from sol.i18n import available_languages

    t = translator(request)

    data = request.params

    username = data.get('username', None)
    password = data.get('password', None)

    ipaddress = request.client_addr
    try:
        host = gethostbyaddr(ipaddress)
    except:
        hostname = "unknown host"
    else:
        hostname = host[0]

    logger.info('Login attempt by "%s" from %s (%s)', username, hostname, ipaddress)

    if username and password:
        settings = request.registry.settings

        adminuser = settings.get('sol.admin.user')
        adminpwd = settings.get('sol.admin.password')
        guestuser = settings.get('sol.guest.user')
        guestpwd = settings.get('sol.guest.password')

        is_admin = False
        is_guest = False
        user_id = None
        ui_language = None

        if adminuser and username == adminuser and password == adminpwd:
            is_admin = True
            fullname = t(ADMINISTRATOR)
        elif guestuser and username == guestuser and password == guestpwd:
            is_guest = True
            fullname = t(ANONYMOUS)
        else:
            sasess = DBSession()
            try:
                user = sasess.query(Player).filter(Player.nickname == username,
                                                   Player.password != '*').one()
            except NoResultFound:
                user = None
            if user is None or not user.check_password(password):
                return {'success': False,
                        'message': t(NO_SUCH_USER),
                        'errors': {'username': t(NON_EXISTING_USERNAME)}}
            else:
                user_id = user.idplayer
                first_name = user.firstname
                last_name = user.lastname
                if user.language in available_languages:
                    ui_language = user.language

                if first_name and last_name:
                    fullname = t(FULL_NAME).format(
                        first_name=first_name, last_name=last_name)
                else:
                    fullname = username

        s = request.session
        s['user_id'] = user_id
        s['user_name'] = username
        s['is_admin'] = is_admin
        s['is_guest'] = is_guest
        s['ui_language'] = ui_language

        def translate_name(cfg):
            copy = dict(cfg)
            copy['name'] = t(copy['name'])
            return copy

        if ui_language:
            req_language = request.accept_language.best_match(
                available_languages, 'en')
            reload_l10n = ui_language != req_language

            if reload_l10n:
                # Reset the Pyramid request localizer to use the preferred language
                registry = request.registry
                request._LOCALE_ = ui_language
                localizer = registry.queryUtility(ILocalizer, name=ui_language)

                if localizer is None:
                    tdirs = registry.queryUtility(ITranslationDirectories, default=[])
                    localizer = make_localizer(ui_language, tdirs)
                    registry.registerUtility(localizer, ILocalizer, name=ui_language)

                request.localizer = localizer
        else:
            reload_l10n = False

        result = {'success': True,
                  'fullname': fullname,
                  'is_admin': is_admin,
                  'user_id': user_id,
                  'reload_l10n': reload_l10n,
                  'modules': [MODULES[m]['classname'] for m in MODULES
                              if not is_guest or m != 'upload'],
                  'shortcuts': [] if is_guest else [translate_name(sc)
                                                    for sc in [MODULES[m]['shortcut']
                                                               for m in MODULES
                                                               if 'shortcut' in MODULES[m]]],
                  'quickstart': [translate_name(qs)
                                 for qs in [MODULES[m]['quickstart']
                                            for m in MODULES
                                            if 'quickstart' in MODULES[m]]]
              }

        get_request_logger(request, logger).info('New session for %s', fullname)

        return result
    else: # pragma: no cover
        errors = {}
        if not username:
            errors['username'] = t(MANDATORY_FIELD)
        if not password:
            errors['password'] = t(MANDATORY_FIELD)
        return {'success': False,
                'message': t(MISSING_FIELDS),
                'errors': errors}


@view_config(route_name='logout', renderer='json')
def logout(request):
    from os.path import isdir

    s = request.session

    get_request_logger(request, logger).info('Session terminated')

    if s['user_id'] or s['is_admin']: # not for guest users
        settings = request.registry.settings
        bckdir = settings.get('sol.backups_dir', None)
        if bckdir and isdir(bckdir):
            logger.info('Performing a database backup, just in case...')

            pdir = settings['sol.portraits_dir']
            edir = settings['sol.emblems_dir']

            with transaction.manager:
                bio.backup(DBSession(), pdir, edir, bckdir)

    s.invalidate()

    return {'success': True, 'message': 'Goodbye'}
