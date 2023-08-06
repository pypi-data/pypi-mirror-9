# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Data controller
# :Creato:    mer 15 ott 2008 08:25:21 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import logging
from urllib.parse import quote_plus

from pyramid.view import view_config

from sqlalchemy import and_, distinct, exists, func, or_, select

from ..i18n import translatable_string as _, translator
from ..models import (
    DBSession,
    Championship,
    Club,
    Competitor,
    Player,
    Rate,
    Rating,
    Tourney,
    )
from . import expose


logger = logging.getLogger(__name__)

_clubs_t = Club.__table__
_competitors_t = Competitor.__table__
_ratings_t = Rating.__table__
_championships_t = Championship.__table__
_tourneys_t = Tourney.__table__

_owners_t = Player.__table__.alias('owners')

def add_owner(request, results):
    t = translator(request)

    if 'metadata' in results:
        fields = results['metadata']['fields']
        # The proxy may be called with "only_cols", so check for the presence of the 'idowner'
        # field
        for field in fields:
            if field['name'] == 'idowner':
                fields.append({
                    'label': t(_('Responsible')),
                    'hint': t(_('The user responsible for the record,'
                                ' who can modify or delete it.')),
                    'name': 'Owner',
                    'hidden': True,
                    'nullable': True,
                    'sortable': False,
                    'lookup': dict(url='/data/owners',
                                   lookupField='idowner',
                                   idField='idplayer',
                                   displayField='Fullname'),
                })
                break
    else:
        s = DBSession()
        for r in results['root']:
            try:
                idowner = r['idowner']
            except KeyError:
                # The proxy has been called with "only_cols", probably by a lookup combo
                break

            if idowner is None:
                owner = t(_('Administrator'))
            else:
                player = s.query(Player).get(idowner)
                owner = player.caption(False)
            r['Owner'] = owner
    return results


@view_config(route_name="clubs", renderer="json")
@expose(select([_clubs_t,
                select([func.count(_championships_t.c.idchampionship)],
                       _championships_t.c.idclub==_clubs_t.c.idclub
                   ).as_scalar().label('Championships')]),
        metadata=dict(
    description=dict(flex=1),
    emblem=dict(hidden=True, width=130),
    nationality=dict(width=120),
    prizes=dict(hidden=True, width=180),
    couplings=dict(hidden=True, width=180),
    siteurl=dict(hidden=True, width=250, vtype='url'),
    email=dict(hidden=True, vtype='email'),
    isfederation=dict(nullable=True),
    Championships=dict(label=_('Championships'),
                 hint=_('Number of championships organized by the club.'),
                 width=40,
                 readonly=True,
                 sortable=False)
    ))
def clubs(request, results):
    return add_owner(request, results)


_federations_t = _clubs_t.alias()

@view_config(route_name="federations", renderer="json")
@expose(select([_federations_t.c.idclub,
                _federations_t.c.description,
                _federations_t.c.nationality],
               _federations_t.c.isfederation==True))
def federations(request, results):
    return results


_players_t = Player.__table__
_countplayed = select([func.count(_tourneys_t.c.idtourney)],
                      or_(_competitors_t.c.idplayer1 == _players_t.c.idplayer,
                          _competitors_t.c.idplayer2 == _players_t.c.idplayer,
                          _competitors_t.c.idplayer3 == _players_t.c.idplayer,
                          _competitors_t.c.idplayer4 == _players_t.c.idplayer),
                      from_obj=_competitors_t.join(_tourneys_t))
_firstplayed = select([func.min(_tourneys_t.c.date)],
                      or_(_competitors_t.c.idplayer1 == _players_t.c.idplayer,
                          _competitors_t.c.idplayer2 == _players_t.c.idplayer,
                          _competitors_t.c.idplayer3 == _players_t.c.idplayer,
                          _competitors_t.c.idplayer4 == _players_t.c.idplayer),
                      from_obj=_competitors_t.join(_tourneys_t))
_lastplayed = select([func.max(_tourneys_t.c.date)],
                     or_(_competitors_t.c.idplayer1 == _players_t.c.idplayer,
                         _competitors_t.c.idplayer2 == _players_t.c.idplayer,
                         _competitors_t.c.idplayer3 == _players_t.c.idplayer,
                         _competitors_t.c.idplayer4 == _players_t.c.idplayer),
                     from_obj=_competitors_t.join(_tourneys_t))
_players_metadata = dict(
    firstname=dict(flex=1),
    lastname=dict(flex=1),
    nickname=dict(hidden=True, nullable=True),
    password=dict(hidden=True, password=True, width=40, nullable=True),
    sex=dict(hidden=True, width=80),
    nationality=dict(width=120),
    language=dict(hidden=True, width=120),
    citizenship=dict(hidden=True, nullable=True),
    birthdate=dict(hidden=True),
    email=dict(hidden=True, vtype='email'),
    phone=dict(hidden=True, vtype='phone'),
    portrait=dict(hidden=True, width=130),
    Club=dict(label=_clubs_t.c.description.info['label'],
              hint=_('The club this player is affiliated with.'),
              flex=1,
              nullable=True,
              lookup=dict(url=('/data/clubs?only_cols=idclub,description,nationality'
                               '&sort=nationality,description'),
                          idField='idclub',
                          displayField='description',
                          otherFields='nationality',
                          pageSize=12,
                          innerTpl=('<div class="sol-flags-icon sol-flag-{nationality}"'
                                    ' data-qtip="'
                                    '{[ SoL.form.field.FlagsCombo.countries[values.nationality] ]}'
                                    '">{description}'
                                    '</div>'))),
    Federation=dict(label=_('Federation'),
                    hint=_('The federation this player is associated with.'),
                    hidden=True,
                    nullable=True,
                    lookup=dict(url='/data/federations?sort=description',
                                idField='idclub',
                                lookupField='idfederation',
                                displayField='description',
                                otherFields='nationality',
                                innerTpl=('<div class="sol-flags-icon sol-flag-{nationality}"'
                                          ' data-qtip="'
                                          '{[ SoL.form.field.FlagsCombo.countries[values.nationality] ]}'
                                          '">{description}'
                                          '</div>'))),
    CountPlayed=dict(label=_('Tourneys'),
                     hint=_('Number of played tourneys.'),
                     hidden=True,
                     readonly=True),
    FirstPlayed=dict(label=_('First tourney'),
                     hint=_('Oldest partecipation.'),
                     hidden=True,
                     readonly=True),
    LastPlayed=dict(label=_('Last tourney'),
                    hint=_('Most recent partecipation.'),
                    hidden=True,
                    readonly=True),
    )

@view_config(route_name="players", renderer="json")
@expose(select([_players_t,
                _clubs_t.c.description.label('Club'),
                _federations_t.c.description.label('Federation'),
                _countplayed.as_scalar().label('CountPlayed'),
                _firstplayed.as_scalar().label('FirstPlayed'),
                _lastplayed.as_scalar().label('LastPlayed'),],
               from_obj=_players_t
               .outerjoin(_clubs_t, _clubs_t.c.idclub==_players_t.c.idclub)
               .outerjoin(_federations_t,
                          _federations_t.c.idclub==_players_t.c.idfederation)),
        metadata=_players_metadata)
def players(request, results):
    from gettext import translation
    from pycountry import LOCALES_DIR, languages

    if 'metadata' in results:
        t = translator(request)
        results['metadata']['fields'].append({
            'label': t(_('Language')),
            'hint': t(_('The preferred language of the player, used to send email messages'
                        ' and for the user interface when he logs in.')),
            'name': 'Language',
            'hidden': True,
            'nullable': True,
            'lookup': dict(url='/data/languages',
                           remoteFilter=False,
                           lookupField='language',
                           idField='code',
                           displayField='name'),
        })
    else:
        lname = request.locale_name
        try:
            t = translation('iso639', LOCALES_DIR, languages=[lname]).gettext
        except IOError:
            t = lambda x: x
        for r in results['root']:
            code = r['language']
            if code:
                r['Language'] = t(languages.get(alpha2=code).name)
            r['password'] = '' if r['password'] == '*' else '*'
    return add_owner(request, results)


_pdup_t = _players_t.alias('pdup')

@view_config(route_name="players", renderer="json", request_param='dups')
@expose(select([_players_t,
                _clubs_t.c.description.label('Club'),
                _countplayed.as_scalar().label('CountPlayed'),
                _firstplayed.as_scalar().label('FirstPlayed'),
                _lastplayed.as_scalar().label('LastPlayed'),],
               from_obj=_players_t.outerjoin(
                   _clubs_t, _clubs_t.c.idclub==_players_t.c.idclub))
        .where(exists().where(
            and_(_players_t.c.idplayer != _pdup_t.c.idplayer,
                 or_(_players_t.c.sex == None,
                     _pdup_t.c.sex == None,
                     _players_t.c.sex == _pdup_t.c.sex),
                 or_(and_(func.soundex(_players_t.c.firstname) == func.soundex(_pdup_t.c.firstname),
                          func.soundex(_players_t.c.lastname) == func.soundex(_pdup_t.c.lastname)),
                     and_(func.soundex(_players_t.c.firstname) == func.soundex(_pdup_t.c.lastname),
                          func.soundex(_players_t.c.lastname) == func.soundex(_pdup_t.c.firstname)))))),
        metadata=_players_metadata)
def duplicated_players(request, results):
    return add_owner(request, results)


@view_config(route_name="owners", renderer="json")
@expose(select([_owners_t.c.idplayer,
                _owners_t.c.firstname,
                _owners_t.c.lastname,
                _owners_t.c.nickname])
        .where(and_(_owners_t.c.nickname != None,
                    _owners_t.c.password != '*')))
def owners(request, results):
    from operator import itemgetter

    t = translator(request)
    if 'metadata' in results:
        results['metadata']['fields'] = [f for f in results['metadata']['fields']
                                         if f['name'] == 'idplayer']
        results['metadata']['fields'].append({
            'label': t(_('Responsible')),
            'hint': t(_('The fullname of the responsible.')),
            'name': 'Fullname',
        })
    else:
        owners = results['root']
        format = _('$lastname $firstname $nickname')
        for owner in owners:
            firstname = owner.pop('firstname')
            lastname = owner.pop('lastname')
            nickname = '“%s”' % owner.pop('nickname')
            owner['Fullname'] = t(format, mapping=dict(
                lastname=lastname,
                firstname=firstname,
                nickname=nickname))
        owners.append({
            'idplayer': None,
            'Fullname': t(_('Administrator')),
        })
        owners.sort(key=itemgetter('Fullname'))
        results['count'] = results['count'] + 1
    return results


_pchampionships_t = _championships_t.alias()

@view_config(route_name="championships", renderer="json")
@expose(select([_championships_t, _clubs_t.c.description.label('Club'),
                select([_pchampionships_t.c.description],
                       _pchampionships_t.c.idchampionship==_championships_t.c.idprevious
                   ).as_scalar().label('Previous'),
                select([func.count(_tourneys_t.c.idtourney)],
                       _tourneys_t.c.idchampionship==_championships_t.c.idchampionship
                   ).as_scalar().label('Tourneys')],
               from_obj=_championships_t.join(_clubs_t)),
        metadata=dict(
    description=dict(flex=1),
    prizes=dict(hidden=True, width=180),
    couplings=dict(hidden=True, width=180),
    skipworstprizes=dict(hidden=True),
    playersperteam=dict(hidden=True),
    closed=dict(hidden=True, nullable=True),
    Club=dict(label=_clubs_t.c.description.info['label'],
              hint=_('Club that organize the tourneys of the championship.'),
              flex=1,
              lookup=dict(url=('/data/clubs?only_cols=idclub,description,nationality'
                               '&sort=nationality,description'),
                          idField='idclub',
                          displayField='description',
                          otherFields='nationality',
                          pageSize=12,
                          innerTpl=('<div class="sol-flags-icon sol-flag-{nationality}"'
                                    ' data-qtip="'
                                    '{[ SoL.form.field.FlagsCombo.countries[values.nationality] ]}'
                                    '">{description}'
                                    '</div>'))),
    Previous=dict(label=_('Previous championship'),
                  hint=_('Previous championship.'),
                  hidden=True,
                  nullable=True,
                  lookup=dict(url='/data/championships?only_cols=idchampionship,description&sort=description&filter_closed=true',
                              idField='idchampionship',
                              lookupField='idprevious',
                              displayField='description')),
    Tourneys=dict(label=_('Tourneys'),
                  hint=_('Number of tourneys in the championship.'),
                  width=40,
                  readonly=True,
                  sortable=False)
    ))
def championships(request, results):
    return add_owner(request, results)


@view_config(route_name="tourneys", renderer="json")
@expose(select([_tourneys_t,
                _championships_t.c.description.label('Championship'),
                _championships_t.c.idclub.label('IDClub'),
                select([_clubs_t.c.description],
                       _clubs_t.c.idclub==_championships_t.c.idclub
                   ).as_scalar().label('Club'),
                _championships_t.c.playersperteam.label('PlayersPerTeam'),
                _championships_t.c.prizes.label('Prizes'),
                select([_ratings_t.c.description],
                       _ratings_t.c.idrating==_tourneys_t.c.idrating
                   ).as_scalar().label('Rating'),
                (_championships_t.c.playersperteam
                 * select([func.count(_competitors_t.c.idcompetitor)],
                          _competitors_t.c.idtourney==_tourneys_t.c.idtourney
                      ).as_scalar()).label('Participants')],
               from_obj=_tourneys_t.join(_championships_t)),
        metadata=dict(
    description=dict(flex=3),
    location=dict(flex=2),
    currentturn=dict(hidden=True, readonly=True),
    rankedturn=dict(hidden=True, readonly=True),
    prized=dict(hidden=True),
    duration=dict(hidden=True),
    prealarm=dict(hidden=True),
    couplings=dict(hidden=True, width=180),
    delaytoppairing=dict(hidden=True),
    phantomscore=dict(hidden=True),
    countdownstarted=False,
    finals=dict(hidden=True),
    finalturns=dict(hidden=True),
    finalkind=dict(hidden=True, nullable=True),
    Prizes=dict(hidden=True,
                label=_championships_t.c.prizes.info['label'],
                hint=_championships_t.c.prizes.info['hint']),
    Championship=dict(label=_championships_t.c.description.info['label'],
                      hint=_('Championship this tourney belongs to.'),
                      flex=3,
                      lookup=dict(url=('/data/championships?only_cols=idchampionship,description,Club,idclub'
                                       '&sort=Club,description'
                                       '&filter_closed=false'),
                                  idField='idchampionship',
                                  displayField='description',
                                  otherFields='Club,idclub',
                                  innerTpl='<div>{description}&nbsp;<small>({Club})</small></div>')),
    IDClub=dict(label=_championships_t.c.idclub.info['label'],
                hint=_('ID of the club this tourney is organized by.'),
                hidden=True),
    Club=dict(label=_clubs_t.c.description.info['label'],
              hint=_('Club this tourney is organized by.'),
              flex=3,
              readonly=True,
              # This is effective only for filtering purposes
              lookup=dict(url=('/data/clubs?only_cols=idclub,description,nationality'
                               '&sort=nationality,description'),
                          idField='idclub',
                          displayField='description',
                          otherFields='nationality',
                          pageSize=12,
                          innerTpl=('<div class="sol-flags-icon sol-flag-{nationality}"'
                                    ' data-qtip="'
                                    '{[ SoL.form.field.FlagsCombo.countries[values.nationality] ]}'
                                    '">{description}'
                                    '</div>'))),
    Rating=dict(label=_ratings_t.c.description.info['label'],
                      hint=_('The rating this tourney will use and update, if any.'),
                      hidden=True,
                      nullable=True,
                      lookup=dict(url='/data/ratings?only_cols=idrating,description&sort=description&'
                                  +'filter=' + quote_plus('[{"property":"level","value":"0","operator":"<>"}]'),
                                  idField='idrating',
                                  displayField='description')),
    PlayersPerTeam=dict(label=_championships_t.c.playersperteam.info['label'],
                        hint=_championships_t.c.playersperteam.info['hint'],
                        width=40,
                        readonly=True,
                        hidden=True),
    Participants=dict(label=_('Players'),
                      hint=_('Number of participant players.'),
                      width=40,
                      readonly=True,
                      sortable=False)
    ))
def tourneys():
    request, params = (yield)
    if 'idplayer' in params:
        idplayer = int(params.pop('idplayer'))
        condition = exists().where(and_(
            _competitors_t.c.idtourney == _tourneys_t.c.idtourney,
            or_(_competitors_t.c.idplayer1 == idplayer,
                _competitors_t.c.idplayer2 == idplayer,
                _competitors_t.c.idplayer3 == idplayer,
                _competitors_t.c.idplayer4 == idplayer)))
        results = yield params, (condition,)
    else:
        results = yield params
    yield add_owner(request, results)


@view_config(route_name="countries", renderer="json")
def countries(request):
    from gettext import translation
    from pycountry import LOCALES_DIR, countries

    lname = request.locale_name
    try:
        t = translation('iso3166', LOCALES_DIR, languages=[lname]).gettext
    except IOError:
        t = lambda x: x
    result = [dict(code=c.alpha3, name=t(c.name)) for c in countries]

    # Add "eur" for Europe, lowercase code to avoid future conflict with
    # official ISO code...
    t = translator(request)
    result.append(dict(code="eur", name=t(_('Europe'))))

    return dict(count=len(result),
                message="Ok",
                root=result,
                success=True)


@view_config(route_name="languages", renderer="json")
def languages(request):
    from operator import itemgetter
    from gettext import translation
    from pycountry import LOCALES_DIR, languages

    lname = request.locale_name
    try:
        t = translation('iso639', LOCALES_DIR, languages=[lname]).gettext
    except IOError:
        t = lambda x: x
    result = [dict(code=l.alpha2, name=t(l.name))
              for l in languages if hasattr(l, 'alpha2')]
    return dict(count=len(result),
                message="Ok",
                root=sorted(result, key=itemgetter('name')),
                success=True)


_rates_t = Rate.__table__

@view_config(route_name="ratings", renderer="json")
@expose(select([_ratings_t,
                select([_clubs_t.c.description],
                       _clubs_t.c.idclub==_ratings_t.c.idclub
                   ).as_scalar().label('Club'),
                select([func.count(_tourneys_t.c.idtourney)],
                       _tourneys_t.c.idrating==_ratings_t.c.idrating
                   ).as_scalar().label('Tourneys'),
                select([func.count(distinct(_rates_t.c.idplayer))],
                       _rates_t.c.idrating==_ratings_t.c.idrating
                   ).as_scalar().label('Players')]),
        metadata=dict(
    description=dict(flex=1),
    level=dict(width=180),
    inherit=dict(hidden=True, nullable=True),
    tau=dict(hidden=True, decimals=2, type='float'),
    default_rate=dict(hidden=True),
    default_deviation=dict(hidden=True),
    default_volatility=dict(hidden=True, decimals=5, type='float'),
    lower_rate=dict(hidden=True),
    higher_rate=dict(hidden=True),
    outcomes=dict(hidden=True, width=200),
    Club=dict(label=_clubs_t.c.description.info['label'],
              hint=_('Club this rating is restricted to.'),
              flex=1,
              hidden=True,
              nullable=True,
              lookup=dict(url=('/data/clubs?only_cols=idclub,description,nationality'
                               '&sort=nationality,description'),
                          idField='idclub',
                          displayField='description',
                          otherFields='nationality',
                          pageSize=12,
                          innerTpl=('<div class="sol-flags-icon sol-flag-{nationality}"'
                                    ' data-qtip="'
                                    '{[ SoL.form.field.FlagsCombo.countries[values.nationality] ]}'
                                    '">{description}'
                                    '</div>'))),
    Tourneys=dict(label=_('Tourneys'),
                 hint=_('Number of tourneys using this rating.'),
                 width=80,
                 readonly=True,
                 sortable=False),
    Players=dict(label=_('Players'),
                 hint=_('Number of rated players in this rating.'),
                 width=80,
                 readonly=True,
                 sortable=False)
    ))
def ratings(request, results):
    return add_owner(request, results)


_ratesc_t = _rates_t.alias()
_ratesl_t = _rates_t.alias()
_countrates = select([func.count(_ratesc_t.c.idrate)],
                     and_(_ratesc_t.c.idrating == _rates_t.c.idrating,
                          _ratesc_t.c.idplayer == _rates_t.c.idplayer))
_lastrate = select([func.max(_ratesl_t.c.date)]) \
    .where(_ratesl_t.c.idrating == _rates_t.c.idrating) \
    .where(_ratesl_t.c.idplayer == _rates_t.c.idplayer)
_rated_players_metadata = _players_metadata
_rated_players_metadata['CountRates'] = dict(
    label=_('Rates'),
    hint=_('Number of rates of the player.'),
    width=40,
)
_rated_players_metadata['volatility'] = dict(
    decimals=5,
    hidden=True,
    type='float',
)

@view_config(route_name="rated_players", renderer="json")
@expose(select([_players_t,
                _countrates.as_scalar().label('CountRates'),
                _rates_t.c.rate,
                _rates_t.c.deviation,
                _rates_t.c.volatility,
                ],
               _rates_t.c.date == _lastrate,
               from_obj=_players_t.join(_rates_t)),
        metadata=_rated_players_metadata)
def ratedPlayers(request, results):
    return results
