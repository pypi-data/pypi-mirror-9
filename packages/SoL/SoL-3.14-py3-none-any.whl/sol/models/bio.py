# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Batch I/O
# :Creato:    lun 09 feb 2009 10:29:38 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

"""
This module implements some utilities, mainly related to importing and
exporting tourneys data in a portable format.

Scarry used an ``INI`` file and we had several drawbacks with it, mainly
because sending them with e-mail would result in data corruption.

SoL uses YAML_ instead, by default compressing the outcome with gzip.

.. _YAML: http://yaml.org/
"""

from datetime import datetime
from filecmp import cmp
from glob import glob
from gzip import GzipFile
from io import BytesIO
from os import unlink, utime
from os.path import exists, isdir, join, split
from tempfile import mktemp
from urllib.parse import urljoin
from urllib.request import urlopen
import logging
import zipfile

from yaml import safe_dump_all, safe_load_all

from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from transaction import doom

from ..i18n import gettext as _
from . import (
    Championship,
    Club,
    Competitor,
    Match,
    Player,
    Rate,
    Rating,
    Tourney,
    )
from .errors import OperationAborted, TourneyAlreadyExistsError, UnauthorizedOperation
from .utils import (
    asunicode,
    entity_from_primary_key,
    normalize,
    changes_summary,
    )


logger = logging.getLogger(__name__)
changes_logger = logging.getLogger(__name__ + '.changes')


class Serializer(object):
    """Serialize some SoL entities as flat dictionaries."""

    def __init__(self):
        self.id_map = {}
        "An hash mapping a particular instance to its serial marker"

        self.players = []
        "A list of serialized players"

        self.clubs = []
        "A list of serialized clubs"

        self.championships = []
        "A list of serialized championships"

        self.ratings = []
        "A list of serialized ratings"

        self.rates = []
        "A list of serialized rates"

        self.tourneys = []
        "A list of serialized tourneys"

        self.modified = datetime.min
        "Most recent modification timestamp of any serialized entity"

    def addClub(self, club):
        """Serialize a club, if not already done.

        :param club: a :py:class:`.Club` instance
        :rtype: int
        :returns: an integer marker that identify the given club
        """

        try:
            return self.id_map[(type(club), club.idclub)]
        except KeyError:
            self.clubs.append(None)
            idx = len(self.clubs)
            self.id_map[(type(club), club.idclub)] = idx
            self.clubs[idx-1] = club.serialize(self)
            if self.modified is None or club.modified > self.modified:
                self.modified = club.modified
            return idx

    def addChampionship(self, championship):
        """Serialize a championship, if not already done.

        :param club: a :py:class:`.Championship` instance
        :rtype: int
        :returns: an integer marker that identify the given championship
        """

        try:
            return self.id_map[(type(championship), championship.idchampionship)]
        except KeyError:
            self.championships.append(None)
            idx = len(self.championships)
            self.id_map[(type(championship), championship.idchampionship)] = idx
            self.championships[idx-1] = championship.serialize(self)
            if championship.modified > self.modified:
                self.modified = championship.modified
            return idx

    def addRating(self, rating):
        """Serialize a rating, if not already done.

        :param rating: a :py:class:`.Rating` instance
        :rtype: int
        :returns: an integer marker that identify the given rating
        """

        try:
            return self.id_map[(type(rating), rating.idrating)]
        except KeyError:
            self.ratings.append(None)
            idx = len(self.ratings)
            self.id_map[(type(rating), rating.idrating)] = idx
            self.ratings[idx-1] = rating.serialize(self)
            if rating.modified > self.modified:
                self.modified = rating.modified
            return idx

    def addPlayer(self, player):
        """Serialize a player, if not already done.

        :param player: a :py:class:`.Player` instance
        :rtype: int
        :returns: an integer marker that identify the given player
        """

        try:
            return self.id_map[(type(player), player.idplayer)]
        except KeyError:
            self.players.append(None)
            idx = len(self.players)
            self.id_map[(type(player), player.idplayer)] = idx
            self.players[idx-1] = player.serialize(self)
            if player.modified > self.modified:
                self.modified = player.modified
            return idx

    def addRate(self, rate):
        """Serialize a rate, if not already done.

        :param rate: a :py:class:`.Rate` instance
        :rtype: int
        :returns: an integer marker that identify the given rate
        """

        try:
            return self.id_map[(type(rate), rate.idrate)]
        except KeyError:
            self.rates.append(None)
            idx = len(self.rates)
            self.id_map[(type(rate), rate.idrate)] = idx
            self.rates[idx-1] = rate.serialize(self)
            return idx

    def addTourney(self, tourney):
        """Serialize a tourney, if not already done.

        :param tourney: a :py:class:`.Tourney` instance
        :rtype: int
        :returns: an integer marker that identify the given tourney
        """

        try:
            return self.id_map[(type(tourney), tourney.idtourney)]
        except KeyError:
            self.tourneys.append(None)
            idx = len(self.tourneys)
            self.id_map[(type(tourney), tourney.idtourney)] = idx
            self.tourneys[idx-1] = tourney.serialize(self)
            if tourney.modified > self.modified:
                self.modified = tourney.modified
            return idx

    def dump(self):
        yield dict(players=self.players,
                   clubs=self.clubs,
                   championships=self.championships,
                   ratings=self.ratings,
                   rates=self.rates)
        for tourney in self.tourneys:
            yield tourney


class Deserializer(object):
    """Deserialize a flat representation of some SoL entities."""

    def __init__(self, session, idowner, update_only_missing_fields):
        self.update_only_missing_fields = update_only_missing_fields
        "A boolean flag, whether only missing fields will be updated."

        self.session = session
        "The SQLAlchemy session."

        self.idowner = idowner
        "The ID of the :py:class:`owner <.Player>` of newly created instances."

        self.players = []
        "A list of :py:class:`player <.Player>` instances."

        self.clubs = []
        "A list of :py:class:`club <.Club>` instances."

        self.championships = []
        "A list of :py:class:`championship <.Championship>` instances."

        self.ratings = []
        "A list of :py:class:`rating <.Rating>` instances."

        self.rates = []
        "A list of :py:class:`rate <.Rate>` instances."

        self.tourneys = []
        "A list of :py:class:`tourney <.Tourney>` instances."

        self.skipped = 0
        "The number of skipped tournaments, because already present."

    def addClub(self, sclub):
        """Deserialize a :py:class:`.Club`.

        :param sclub: a dictionary containing the flatified representation
        :rtype: :py:class:`.Club`
        :returns: either an existing or a new instance
        """

        query = self.session.query

        guid = sclub.pop('guid', None)
        description = normalize(asunicode(sclub.pop('description')))

        club = None
        if guid is not None:
            try:
                club = query(Club).filter_by(guid=guid).one()
            except NoResultFound:
                pass

        if club is None:
            try:
                club = query(Club).filter_by(description=description).one()
            except NoResultFound:
                pass

        if club is None:
            club = Club(guid=guid, description=description, idowner=self.idowner,
                        **sclub)
            self.session.add(club)
            logger.info('New %r', club)
        else:
            smodified = sclub.get('modified')
            tmodified = club.modified

            if smodified is None or tmodified is None or smodified > tmodified:
                changes = club.update(sclub, missing_only=self.update_only_missing_fields)
                if changes:
                    logger.info('Updated %r: %s', club, changes_summary(changes))

        self.clubs.append(club)

        return club

    def addPlayer(self, splayer):
        """Deserialize a :py:class:`.Player`.

        :param splayer: a dictionary containing the flatified representation
        :rtype: :py:class:`.Player`
        :returns: either an existing or a new instance
        """

        guid = splayer.pop('guid', None)
        lastname = normalize(asunicode(splayer.pop('lastname')), True)
        firstname = normalize(asunicode(splayer.pop('firstname')), True)
        nickname = asunicode(splayer.pop('nickname', None))

        # None may cause problems on some dbs...
        if nickname is None:
            nickname = ''

        try:
            player, merged_into = Player.find(self.session, lastname, firstname,
                                              nickname, guid)
        except MultipleResultsFound:
            raise OperationAborted(
                _('Refusing to guess the right player: more than one person with first'
                  ' name "$fname" and last name "$lname", and no nickname was specified',
                  mapping=dict(fname=firstname, lname=lastname)))

        merged = splayer.pop('merged', [])
        if 'owner' in splayer:
            splayer['owner'] = self.players[splayer['owner'] - 1]
        if 'club' in splayer:
            splayer['club'] = self.clubs[splayer['club'] - 1]
        if 'federation' in splayer:
            splayer['federation'] = self.clubs[splayer['federation'] - 1]

        if player is None:
            if not 'owner' in splayer:
                splayer['idowner'] = self.idowner

            player = Player(guid=guid,
                            firstname=firstname, lastname=lastname, nickname=nickname,
                            **splayer)
            self.session.add(player)
            logger.info('New %r', player)
        else:
            smodified = splayer.get('modified')
            tmodified = player.modified

            # Do not update the player if the incoming data is related to
            # a person who has been merged into another player
            if not merged_into:
                if smodified is None or tmodified is None or smodified > tmodified:
                    changes = player.update(splayer, missing_only=self.update_only_missing_fields)
                    if changes:
                        logger.info('Updated %r: %s', player, changes_summary(changes))

        if merged:
            player.mergePlayers(merged)

        self.players.append(player)

        return player

    def addChampionship(self, schampionship):
        """Deserialize a :py:class:`.Championship`.

        :param schampionship: a dictionary containing the flatified representation
        :rtype: :py:class:`.Championship`
        :returns: either an existing or a new instance
        """

        query = self.session.query

        guid = schampionship.pop('guid', None)
        description = normalize(asunicode(schampionship.pop('description')))

        ssc = schampionship.pop('club')
        if isinstance(ssc, dict):
            # Old SoL 2
            club = self.addClub(ssc)
        else:
            club = self.clubs[ssc - 1]

        championship = None
        if guid is not None:
            try:
                championship = query(Championship).filter_by(guid=guid).one()
            except NoResultFound:
                pass

        if championship is None:
            try:
                championship = query(Championship).filter_by(description=description,
                                                             idclub=club.idclub).one()
            except NoResultFound:
                pass

        if 'owner' in schampionship:
            schampionship['owner'] = self.players[schampionship['owner'] - 1]

        if 'prizefactor' in schampionship:
            # Old SoL 2 dump
            del schampionship['prizefactor']

        if championship is None:
            if not 'owner' in schampionship:
                schampionship['idowner'] = self.idowner

            championship = Championship(guid=guid, club=club, description=description,
                                        **schampionship)
            self.session.add(championship)
            logger.info('New %r', championship)
        else:
            smodified = schampionship.get('modified')
            tmodified = championship.modified

            if smodified is None or tmodified is None or smodified > tmodified:
                changes = championship.update(schampionship,
                                              missing_only=self.update_only_missing_fields)
                if changes:
                    logger.info('Updated %r: %s', championship, changes_summary(changes))

        self.championships.append(championship)

        return championship

    def addRating(self, srating):
        """Deserialize a :py:class:`.Rating`.

        :param srating: a dictionary containing the flatified representation
        :rtype: :py:class:`.Rating`
        :returns: either an existing or a new instance
        """

        query = self.session.query

        guid = srating.pop('guid', None)
        description = normalize(asunicode(srating.pop('description')))

        rating = None
        if guid is not None:
            try:
                rating = query(Rating).filter_by(guid=guid).one()
            except NoResultFound:
                pass

        if rating is None:
            try:
                rating = query(Rating).filter_by(description=description).one()
            except NoResultFound:
                pass

        if 'owner' in srating:
            srating['owner'] = self.players[srating['owner'] - 1]

        if 'club' in srating:
            srating['club'] = self.clubs[srating['club'] - 1]

        if rating is None:
            if not 'owner' in srating:
                srating['idowner'] = self.idowner

            rating = Rating(guid=guid, description=description, **srating)
            self.session.add(rating)
            logger.info('New %r', rating)
        else:
            smodified = srating.get('modified')
            tmodified = rating.modified

            if smodified is None or tmodified is None or smodified > tmodified:
                changes = rating.update(srating, missing_only=self.update_only_missing_fields)
                if changes:
                    logger.info('Updated %r: %s', rating, changes_summary(changes))

        self.ratings.append(rating)

        return rating

    def addRate(self, srate):
        """Deserialize a :py:class:`.Rate`.

        :param srate: a dictionary containing the flatified representation
        :rtype: :py:class:`.Rate`
        :returns: either an existing or a new instance
        """

        query = self.session.query

        rating = self.ratings[srate.pop('rating') - 1]
        player = self.players[srate.pop('player') - 1]
        date = srate.pop('date')

        rate = None
        try:
            rate = query(Rate).filter_by(idrating=rating.idrating,
                                         idplayer=player.idplayer,
                                         date=date).one()
        except NoResultFound:
            rate = Rate(rating=rating, player=player, date=date, **srate)
            self.session.add(rate)
        else:
            rate.update(srate)

        self.rates.append(rate)

        return rate

    def addTourney(self, stourney):
        """Deserialize a :py:class:`.Tourney`.

        :param stourney: a dictionary containing the flatified representation
        :rtype: :py:class:`.Tourney`
        :returns: either an existing or a new instance
        """

        query = self.session.query

        guid = stourney.pop('guid', None)
        date = stourney.pop('date')

        if 'season' in stourney:
            # SoL 3 renamed “season” to “championship”
            stc = stourney.pop('season')
        else:
            stc = stourney.pop('championship')
        if isinstance(stc, dict):
            # Old SoL 2 dump
            championship = self.addChampionship(stc)
        else:
            championship = self.championships[stc - 1]

        if 'owner' in stourney:
            stourney['owner'] = self.players[stourney['owner'] - 1]
        if 'description' in stourney:
            stourney['description'] = normalize(asunicode(stourney['description']))
        if 'location' in stourney:
            stourney['location'] = normalize(asunicode(stourney['location']))
        if 'prizes' in stourney:
            # Old SoL 2 allowed the tourney prize-giving-method to be
            # different from the campionship setting, non sense!
            del stourney['prizes']
        if 'rating' in stourney:
            stourney['rating'] = self.ratings[stourney['rating'] - 1]
        if 'prizefactor' in stourney:
            del stourney['prizefactor']
        competitors = stourney.pop('competitors')
        matches = stourney.pop('matches')

        tourney = None
        if guid is not None:
            try:
                tourney = query(Tourney).filter_by(guid=guid).one()
            except NoResultFound:
                pass

        if tourney is None:
            try:
                tourney = query(Tourney).filter_by(
                    date=date, idchampionship=championship.idchampionship).one()
            except NoResultFound:
                pass

        if tourney is None:
            if not 'owner' in stourney:
                stourney['idowner'] = self.idowner

            ctors = stourney['competitors'] = []
            for c in competitors:
                ctor = Competitor()
                for i, p in enumerate(c.pop('players'), 1):
                    if isinstance(p, dict):
                        # Old SoL 2
                        c['player%d' % i] = self.addPlayer(p)
                    else:
                        c['player%d' % i] = self.players[p-1]
                ctor.update(c)
                ctors.append(ctor)

            mtchs = stourney['matches'] = []
            for m in matches:
                m['competitor1'] = (ctors[m['competitor1']-1]
                                    if m['competitor1'] else None)
                m['competitor2'] = (ctors[m['competitor2']-1]
                                    if m['competitor2'] else None)
                match = Match(**m)
                mtchs.append(match)

            tourney = Tourney(guid=guid, championship=championship, date=date,
                              **stourney)
            self.session.add(tourney)
            logger.info('New %r', tourney)
        else:
            # Don't allow updates to existing completed tourneys
            if tourney.matches or tourney.prized or any(
                    c for c in tourney.competitors if c.points or c.bucholz):
                raise TourneyAlreadyExistsError(
                    _('Tourney "$tourney" of championship "$championship" by "$club" on'
                      ' $date already present, cannot update it', mapping=dict(
                          tourney=tourney.description,
                          date=date.strftime(str(_('%m-%d-%Y'))),
                          club=championship.club.description,
                          championship=championship.description)),
                    tourney)
            else:
                # We are reloading a not-yet-played tourney, so we are going
                # to renew its list of competitors: delete existing ones
                while tourney.competitors:
                    c = tourney.competitors.pop()
                    self.session.delete(c)

                smodified = stourney.get('modified')
                tmodified = tourney.modified

                if smodified is None or tmodified is None or smodified > tmodified:
                    ctors = tourney.competitors
                    for c in competitors:
                        ctor = Competitor()
                        for i, p in enumerate(c.pop('players'), 1):
                            if isinstance(p, dict):
                                # Old SoL 2
                                c['player%d' % i] = self.addPlayer(p)
                            else:
                                c['player%d' % i] = self.players[p-1]
                        ctor.update(c)
                        ctors.append(ctor)

                    for m in matches:
                        m['competitor1'] = (ctors[m['competitor1']-1]
                                            if m['competitor1'] else None)
                        m['competitor2'] = (ctors[m['competitor2']-1]
                                            if m['competitor2'] else None)
                        match = Match(**m)
                        tourney.matches.append(match)

                    changes = tourney.update(stourney,
                                             missing_only=self.update_only_missing_fields)
                    if changes:
                        logger.info('Updated %r: %s', tourney, changes_summary(changes))

        self.tourneys.append(tourney)

        return tourney

    def load(self, dump):
        for data in dump:
            if 'clubs' in data:
                pending_owned_instances = []

                for simple in data.get('clubs', []):
                    owner = simple.pop('owner', None)
                    club = self.addClub(simple)
                    if owner is not None:
                        pending_owned_instances.append((club, owner))

                for simple in data.get('players', []):
                    owner = simple.pop('owner', None)
                    player = self.addPlayer(simple)
                    if owner is not None:
                        pending_owned_instances.append((player, owner))

                for instance, owner in pending_owned_instances:
                    instance.idowner = self.players[owner-1].idplayer

                self.session.flush()

                if 'seasons' in data:
                    # Old name for championships
                    championships = data.get('seasons')
                else:
                    championships = data.get('championships', [])

                pending_chained_instances = []

                for simple in championships:
                    previous = simple.pop('previous', None)
                    cship = self.addChampionship(simple)
                    if previous is not None:
                        pending_chained_instances.append((cship, previous))

                for instance, previous in pending_chained_instances:
                    try:
                        previdx = previous - 1
                    except TypeError:
                        # Old SoL 2 dump
                        previdx = None
                        for i, s in enumerate(self.championships):
                            if s.description == previous and s.club is instance.club:
                                previdx = i
                                break

                        if previdx is None:
                            try:
                                pchampionship = self.session.query(Championship).filter_by(
                                    description=previous, idclub=instance.club.idclub).one()
                            except NoResultFound:
                                logger.warning('Could not find previous championship "%s"'
                                               ' for %r', previous, instance)
                            else:
                                instance.previous = pchampionship

                    if previdx is not None:
                        instance.previous = self.championships[previdx]

                for simple in data.get('ratings', []):
                    self.addRating(simple)

                for simple in data.get('rates', []):
                    self.addRate(simple)
            else:
                try:
                    self.addTourney(data)
                except TourneyAlreadyExistsError as e: # pragma: no cover
                    logger.info('Tourney "%s" of championship "%s" by club "%s" on'
                                ' %s already present, cannot update it' % (
                                    e.tourney.description,
                                    e.tourney.championship.description,
                                    e.tourney.championship.club.description,
                                    e.tourney.date.strftime('%m-%d-%Y')))
                    self.skipped += 1


def backup(sasess, pdir, edir, location=None, keep_only_if_changed=True,
           only_played_tourneys=False):
    """Dump almost everything in a ZIP file.

    :param sasess: a SQLAlchemy session
    :param pdir: the base path of the portrait images, ``sol.portraits_dir``
    :param edir: the base path of the emblem images, ``sol.emblems_dir``
    :param location: either None or a string
    :param keep_only_if_changed: a boolean flag
    :param only_played_tourneys: a boolean flag
    :rtype: bytes
    :return: the ZIP archive

    This function builds a ``ZIP`` archive containing both a standard ``.sol`` dump made with
    :func:`dump_sol` named ``everything.sol`` with *all* tourneys and *all* players (that is,
    not just those who actually played) and two subdirectories ``portraits`` and ``emblems``,
    respectively containing the images associated to the players and to the clubs.

    If `location` is given, it may be either the full path name of the output file where the
    backup will be written or the path of a directory. In the latter case the file name will be
    automatically computed using current time, giving something like
    ``sol-backup_2014-02-03T14:35:12.zip``.

    When `keep_only_if_changed is ``True`` (the default) and `location` is a directory, the
    newly generated backup will be compared with the previous one (if there is at least one, of
    course) and if nothing has changed it will be removed.

    When `only_played_tourneys` is ``True`` (the default is ``False``), the tourneys "in
    preparation" (that is, those without played matches) are ignored and not included in the
    dump.
    """

    if location is None:
        backupfn = mktemp(prefix='sol')
    else:
        if isdir(location):
            now = datetime.now()
            backupfn = join(location,
                            now.strftime('sol-backup_%Y-%m-%dT%H:%M:%S.zip'))
        else:
            keep_only_if_changed = False
            if exists(location):
                raise OperationAborted(
                    "The backup file “%s” does already exist!" % location)

    serializer = Serializer()

    # Dump all players
    for player in sasess.query(Player) \
                        .options(joinedload('merged')) \
                        .order_by(Player.lastname, Player.firstname):
        serializer.addPlayer(player)

    # Dump all player's rates
    for rate in sasess.query(Rate) \
                      .options(joinedload('player')) \
                      .order_by(Rate.idrating, Rate.date):
        serializer.addRate(rate)

    # Dump all played tourneys, possibly ignoring those "in preparation", i.e. without matches
    for tourney in sasess.query(Tourney) \
                         .order_by(Tourney.date):
        if not only_played_tourneys or tourney.rankedturn > 0:
            serializer.addTourney(tourney)

    yaml = safe_dump_all(serializer.dump())

    content = open(mktemp(prefix='sol'), 'w')
    try:
        content.write(yaml)
        content.close()
        modified = serializer.modified.timestamp()
        utime(content.name, (modified, modified))

        out = BytesIO()
        zipf = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
        zipf.write(content.name, 'everything.sol')

        for player in serializer.players:
            if 'portrait' in player:
                portrait = join(pdir, player['portrait'])
                if exists(portrait): # pragma: no cover
                    zipf.write(portrait, 'portraits/' + player['portrait'])

        for club in serializer.clubs:
            if 'emblem' in club:
                emblem = join(edir, club['emblem'])
                if exists(emblem): # pragma: no cover
                    zipf.write(emblem, 'emblems/' + club['emblem'])

        zipf.close()
        zip = out.getvalue()
    finally:
        try:
            unlink(content.name)
        except OSError: # pragma: no cover
            pass

    if location is not None:
        with open(backupfn, 'wb') as f:
            f.write(zip)

        removed = False
        if keep_only_if_changed:
            all_backups = glob(join(location, "sol-backup_*.zip"))
            if len(all_backups) > 1: # pragma: no cover
                all_backups.sort()
                previous_backup = all_backups[-2]

                if cmp(previous_backup, backupfn, shallow=False):
                    unlink(backupfn)
                    removed = True
                    logger.debug('Nothing changed since %s', previous_backup)

        if not removed:
            logger.info('New backup written to %s', backupfn)

    return zip


def restore(sasess, pdir=None, edir=None, url=None, content=None, idowner=None):
    """Restore everything from a backup.

    :param sasess: a SQLAlchemy session
    :param pdir: the base path of the portrait images, ``sol.portraits_dir``
    :param edir: the base path of the emblem images, ``sol.emblems_dir``
    :param url: the URL of the file containing the archive, or None
    :param content: the content of the archive
    :param idowner: the ID of the responsible for newly created instances
    :rtype: tuple
    :return: the list of loaded tourney instances and the number of skipped tourneys

    This reads the ``ZIP`` created by :func:`backup` and loads its content into the database,
    writing the images in the right place (pre-existing images **won't** be overwritten,
    though).
    """

    if content is None: # pragma: no cover
        assert url, "Must provide either a file or an URL!"
        url = urljoin('file:', url)
        logger.info('Retrieving %s', url)
        content = BytesIO(urlopen(url).read())

    zipf = zipfile.ZipFile(content, 'r')
    content = BytesIO(zipf.read('everything.sol'))
    tourneys, skipped = load_sol(sasess, 'everything.sol', content, True, idowner)

    names = zipf.namelist()
    names.sort()

    for name in names:
        if pdir is not None and name.startswith('portraits/'):
            portrait = join(pdir, split(name)[1])
            if not exists(portrait):
                outfile = open(portrait, 'wb')
                outfile.write(zipf.read(name))
                outfile.close()
            else:
                logger.debug('Not overwriting %s', portrait)
        elif edir is not None and name.startswith('emblems/'):
            emblem = join(edir, split(name)[1])
            if not exists(emblem):
                outfile = open(emblem, 'wb')
                outfile.write(zipf.read(name))
                outfile.close()
            else: # pragma: no cover
                logger.debug('Not overwriting %s', emblem)

    return tourneys, skipped


def load_sol(sasess, url=None, content=None, restore=False, idowner=None):
    """Load the archive exported from SoL.

    :param sasess: a SQLAlchemy session
    :param url: the URL of the ``.sol`` (or ``.sol.gz``) file
    :param content: the content of a ``.sol`` (or ``.sol.gz``) file
    :param restore: whether this is a restore, ``False`` by default
    :param idowner: the ID of the responsible for newly created instances
    :rtype: tuple
    :return: the list of loaded tourney instances and number of skipped tournaments

    If `content` is not specified, it will be loaded with ``urlopen()`` from the given `url`.

    Normally only missing data is updated, except when `restore` is True.
    """

    if content is None:
        assert url, "Must provide either a file or an URL!"
        url = urljoin('file:', url)
        logger.info('Retrieving %s', url)
        content = BytesIO(urlopen(url).read())

    if url and url.endswith('.sol.gz'):
        content = GzipFile(fileobj=content, mode='rb')

    yaml = content.read()

    deserializer = Deserializer(sasess, idowner, not restore)
    deserializer.load(safe_load_all(yaml))

    for rating in deserializer.ratings:
        mindate = None
        for t in deserializer.tourneys:
            if t.rating is rating:
                if mindate is None or mindate > t.date:
                    mindate = t.date

        rating.recompute(mindate)

    return deserializer.tourneys, deserializer.skipped


def dump_sol(tourneys, gzipped=False):
    """Dump tourneys as a YAML document.

    :param tourneys: the sequence of tourneys to dump
    :param gzipped: a boolean indicating whether the output will be compressed
                    with ``gzip``
    :rtype: bytes
    :return: the YAML document, possibly gzipped
    """

    serializer = Serializer()

    for tourney in tourneys:
        serializer.addTourney(tourney)

    yaml = safe_dump_all(serializer.dump())

    if gzipped:
        out = BytesIO()
        gzipped = GzipFile(fileobj=out, mode='wb')
        gzipped.write(yaml.encode('utf-8'))
        gzipped.close()
        yaml = out.getvalue()

    return yaml


def _save_image(dir, fname, data, clogger):
    """Save an image and return its name

    :param dir: the directory where to store the image
    :param fname: the uploaded file name
    :param data: a data-uri encoded image
    :param clogger: where to log applied changes
    :rtype: string
    :return: the filename where the image was written
    """

    from base64 import decodestring
    from hashlib import md5
    from os.path import exists, join

    if not data.startswith('data:image'):
        raise OperationAborted('Image is not a data URI')

    kind = data[data.index('/')+1:data.index(';')]
    data = decodestring(data[data.index(',')+1:].encode('ascii'))

    newname = md5(data).hexdigest() + '.' + kind
    fullname = join(dir, newname)

    if not exists(fullname):
        with open(fullname, 'wb') as f:
            f.write(data)
        clogger.info('Wrote new image "%s" as "%s"', fname, fullname)
    else:
        logger.debug('Image "%s" already exists as "%s"', fname, fullname)

    return newname


def _delete_image(dir, fname, clogger):
    """Delete an image

    :param dir: the directory containing the image
    :param fname: the image file name
    :param clogger: where to log applied changes
    """

    fullname = join(dir, fname)
    if exists(fullname): # pragma: no cover
        unlink(fullname)
        logger.info('Deleted image "%s"', fullname)


def save_changes(sasess, request, modified, deleted, clogger=changes_logger):
    """Save insertions, changes and deletions to the database.

    :param sasess: the SQLAlchemy session
    :param request: the Pyramid web request
    :param modified: a sequence of record changes, each represented by
                     a tuple of two items, the PK name and a
                     dictionary with the modified fields; if the value
                     of the PK field is null or 0 then the record is
                     considered new and will be inserted instead of updated
    :param deleted: a sequence of deletions, each represented by a tuple
                    of two items, the PK name and the ID of the record to
                    be removed
    :param clogger: where to log applied changes
    :rtype: tuple
    :return: three lists, respectively inserted, modified and deleted record IDs,
             grouped in a dictionary keyed on PK name
    """

    iids = []
    mids = []
    dids = []

    if request is not None:
        settings = request.registry.settings
        pdir = settings['sol.portraits_dir']
        edir = settings['sol.emblems_dir']
        user_id = request.session['user_id']
    else:
        # tests
        from tempfile import gettempdir
        edir = pdir = gettempdir()
        user_id = None

    # Perform insertions after updates: this is to handle the corner
    # case on competitors in team events, when a player can be moved
    # from an existing team to a new one
    inserted = []

    for key, mdata in modified:
        entity = entity_from_primary_key(key)
        table = entity.__table__

        fvalues = {}
        for f, v in mdata.items():
            if f in table.c and f != key:
                if v != '':
                    fvalues[f] = v
                else:
                    fvalues[f] = None
            elif f == 'image' and v:
                # Must be either a new emblem or a new portrait
                if entity is Player:
                    fname = mdata["portrait"]
                    fvalues['portrait'] = mdata["portrait"] = _save_image(pdir, fname, v,
                                                                          clogger)
                elif entity is Club:
                    fname = mdata["emblem"]
                    fvalues['emblem'] = mdata["emblem"] = _save_image(edir, fname, v, clogger)

        # If there are no changes, do not do anything
        if not fvalues:
            continue

        # Set the modified timestamp, if the entity has it
        if hasattr(entity, 'modified'):
            fvalues['modified'] = func.now()

        # If the PK is missing or None, assume it's a new record
        idrecord = int(mdata.get(key) or 0)

        if idrecord == 0:
            inserted.append((entity, key, fvalues))
        else:
            instance = sasess.query(entity).get(idrecord)
            if instance is not None:
                if user_id is not None:
                    if hasattr(entity, 'idowner') and instance.idowner != user_id:
                        # Abort current transaction
                        doom()
                        logger.warning('Unauthorized attempt to modify %r', instance)
                        raise UnauthorizedOperation(_("Cannot modify not owned records!"))

                if entity is Player and 'portrait' in mdata:
                    fname = mdata["portrait"]
                    if not fname and instance.portrait:
                        _delete_image(pdir, instance.portrait, clogger)
                elif entity is Club and 'emblem' in mdata:
                    fname = mdata["emblem"]
                    if not fname and instance.emblem:
                        _delete_image(edir, instance.emblem, clogger)

                mids.append({key: idrecord})
                changes = instance.update(fvalues)
                sasess.flush()
                clogger.info('Updated %r: %s', instance, changes_summary(changes))

    for entity, key, fvalues in inserted:
        entity.check_insert(sasess, fvalues)

        if user_id is not None and hasattr(entity, 'idowner'):
            fvalues['idowner'] = user_id

        instance = entity(**fvalues)
        sasess.add(instance)
        sasess.flush()
        nextid = getattr(instance, key)
        iids.append({key: nextid})
        clogger.info('Inserted new %r', instance)

    for key, ddata in deleted:
        entity = entity_from_primary_key(key)
        instance = sasess.query(entity).get(ddata)
        if instance is not None:
            if user_id is not None: # pragma: no cover
                if hasattr(entity, 'idowner') and instance.idowner != user_id:
                    # Abort current transaction
                    doom()
                    logger.warning('Unauthorized attempt to delete %r', instance)
                    raise UnauthorizedOperation(_("Cannot delete not owned records!"))

            instance.delete()
            dids.append({key: ddata})
            clogger.info('Deleted %r', instance)

    return iids, mids, dids
