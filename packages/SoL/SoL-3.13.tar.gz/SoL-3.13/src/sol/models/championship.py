# -*- coding: utf-8 -*-
# :Progetto:  SoL -- The Championship entity
# :Creato:    gio 27 nov 2008 13:53:28 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import logging

from sqlalchemy import Column, ForeignKey, Index, Sequence
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, relationship

from ..i18n import translatable_string as N_, gettext as _
from . import Base, GloballyUnique
from .domains import (
    boolean_t,
    code_t,
    description_t,
    intid_t,
    smallint_t,
    )


logger = logging.getLogger(__name__)


class Championship(GloballyUnique, Base):
    """A series of tournaments organized by the same club."""

    __tablename__ = 'championships'
    "Related table"

    @declared_attr
    def __table_args__(cls):
        return (GloballyUnique.__table_args__(cls) +
                (Index('%s_uk' % cls.__tablename__,
                       'description', 'idclub',
                       unique=True),))

    ## Columns

    idchampionship = Column(
        intid_t, Sequence('gen_idchampionship', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(label=N_('Championship ID'),
                  hint=N_('Unique ID of the championship.')))
    """Primary key."""

    idprevious = Column(
        intid_t, ForeignKey('championships.idchampionship'),
        info=dict(label=N_('Previous championship ID'),
                  hint=N_('ID of the previous championship.')))
    """Previous championship's ID."""

    idclub = Column(
        intid_t, ForeignKey('clubs.idclub'), nullable=False,
        info=dict(label=N_('Club ID'),
                  hint=N_('ID of the club the championship is organized by.')))
    """Organizer :py:class:`club <.Club>`'s ID."""

    idowner = Column(
        intid_t, ForeignKey('players.idplayer', ondelete="SET NULL"),
        info=dict(label=N_('Owner ID'),
                  hint=N_('ID of the user that is responsible for this record.')))
    """ID of the :py:class:`user <.Player>` that is responsible for this record."""

    description = Column(
        description_t,
        nullable=False,
        info=dict(label=N_('Championship'),
                  hint=N_('Description of the championship.')))
    """Description of the championship."""

    prizes = Column(
        code_t,
        nullable=False,
        default='fixed',
        info=dict(label=N_('Prizes'),
                  hint=N_('Method used to assign final prizes.'),
                  dictionary=dict(
                      asis=N_('No final prizes'),
                      fixed=N_('Fixed prizes: 18,16,14,13…'),
                      fixed40=N_('Fixed prizes: 1000,900,800,750…'),
                      millesimal=N_('Classic millesimal prizes'),
                      centesimal=N_('Centesimal prizes'))))
    """Kind of prize-giving.

    This is used to determine which method will be used to assign
    final prizes. It may be:

    `asis`
      means that the final prize is a plain integer number, monotonically decreasing down to 1
      starting from num-of-competitors: this is meant to give the chance of swapping
      competitors positions after tournament's final rounds, the `final prize` column won't
      even show up in the final ranking printout;

    `fixed`
      means the usual way, that is 18 points to the winner, 16 to the second, 14 to the third,
      13 to the fourth, …, 1 point to the 16th, 0 points after that;

    `fixed40`
      similar to `fixed`, but applied to best fourty scores starting from 1000:

        1. 1000
        2. 900
        3. 800
        4. 750
        5. 700
        6. 650
        7. 600
        8. 550
        9. 500
        10. 450
        11. 400
        12. 375
        13. 350
        14. 325
        15. 300
        16. 275
        17. 250
        18. 225
        19. 200
        20. 175
        21. 150
        22. 140
        23. 130
        24. 120
        25. 110
        26. 100
        27. 90
        28. 80
        29. 70
        30. 60
        31. 50
        32. 40
        33. 35
        34. 30
        35. 25
        36. 20
        37. 15
        38. 10
        39. 5
        40. 1

    `millesimal`
      is the classic method, that distributes a multiple of 1000/num-of-competitors;

    `centesimal`
      assigns 100 to the first ranked competitor, 1 to the last, linear interpolation
      to the other competitors.
    """

    skipworstprizes = Column(
        smallint_t,
        nullable=False,
        default=0,
        info=dict(label=N_('Skip'),
                  hint=N_('Number of worst results to skip in computing'
                          ' the final ranking of the championship.'),
                  min=0, max=5))
    """Number of worst results to skip in computing the ranking."""

    playersperteam = Column(
        smallint_t,
        nullable=False,
        default=1,
        info=dict(label=N_('Players'),
                  hint=N_('Number of players in each team, 1 for singles, 2 for doubles.'),
                  min=1, max=4))
    """Number of players per team."""

    closed = Column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(label=N_('Closed'),
                  hint=N_('Should be activated once the championship'
                          ' has been completed and no other'
                          ' tourney can be associated with it.')))
    """Whether the championships is close, and its ranking finalized."""

    couplings = Column(
        code_t,
        default='serial',
        info=dict(label=N_('Pairings'),
                  hint=N_('Default method used to pair competitors at each round.'),
                  dictionary=dict(serial=N_('Ranking order'),
                                  dazed=N_('Cross ranking order'))))
    """Kind of pairing method used to build next round, used as default value
    for the corresponding field when creating a new tourney."""

    ## Relations

    owner = relationship('Player', backref='owned_championships')
    "The :py:class:`owner <.Player>` of this record, `admin` when ``None``."

    tourneys = relationship('Tourney', backref='championship',
                            cascade="all, delete-orphan",
                            order_by="Tourney.date",
                            lazy=True)
    """:py:class:`Tourneys <.Tourney>` in this championship."""

    previous = relationship('Championship', uselist=False,
                            backref=backref('next', uselist=False),
                            remote_side='Championship.idchampionship')
    """Previous championship."""

    def caption(self, html=None, localized=True):
        return _('$championship of $club',
                 just_subst=not localized, mapping=dict(
                     championship=self.description,
                     club=self.club.caption(html, localized)))

    def ranking(self, limit=None, onlywomen=False):
        """Summarize the championship, collecting final prizes of the players.

        :param limit: the earliest date to consider
        :type limit: either ``None`` or a date instance
        :param onlywomen: whether only women should be considered
        :type onlywomen: a boolean
        :rtype: a tuple of two slots

        For each tuple of players collect the earned prize in each tourney of the championship,
        or zero if the players did not participate to a given event.

        `limit` and `onlywomen` are used by the general rankings, to consider only last year
        tourneys and to produce women ranking respectively.

        Results in a tuple of two items, the first being a list of two slots tuples,
        respectively the date and the guid of a tourney, the second a list of tuples, sorted by
        total prize: each tuple contains five items, a tuple of players, their total prize, a
        list of their prizes sorted by date of event, the number of prizes and finally either
        `None` or a list of skipped prizes.
        """

        dates = []
        allprizes = {}
        for t in self.tourneys:
            if t.prized and (limit is None or t.date>=limit):
                prizes = t.championship.prizes
                dates.append((t.date, t.guid))
                for c in t.competitors:
                    if not onlywomen or c.player1.sex == 'F':
                        players = (c.player1, c.player2, c.player3, c.player4)
                        prizes = allprizes.setdefault(players, {})
                        prize = c.points if prizes == 'asis' else c.prize
                        prizes[t.date] = prize
        dates.sort()

        championship = []
        for players in allprizes:
            prizes = allprizes[players]
            nprizes = len(prizes)
            for d,g in dates:
                if not d in prizes: # pragma: no cover
                    prizes[d] = 0
            championship.append((players, [prizes[d] for d,g in dates], nprizes))

        totalprizes = []
        for players, prizes, nprizes in championship:
            swp = self.skipworstprizes
            if swp and limit is None and nprizes > swp:
                pts = prizes[:]
                pts.sort()
                skipped = pts[:swp]
                pts = pts[swp:]
            else:
                pts = prizes
                skipped = None
            totalprizes.append((players, sum(pts), prizes, nprizes, skipped))

        return dates, sorted(totalprizes, key=lambda i: (-i[1], -i[3]))

    def serialize(self, serializer):
        """Reduce a single championship to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :rtype: dict
        :returns: a plain dictionary containing a flatified view of this championship
        """

        simple = {}
        simple['guid'] = self.guid
        simple['modified'] = self.modified
        simple['club'] = serializer.addClub(self.club)
        if self.idowner:
            simple['owner'] = serializer.addPlayer(self.owner)
        simple['description'] = self.description
        simple['prizes'] = self.prizes
        simple['couplings'] = self.couplings
        simple['skipworstprizes'] = self.skipworstprizes
        simple['playersperteam'] = self.playersperteam
        simple['closed'] = self.closed
        if self.previous:
            simple['previous'] = serializer.addChampionship(self.previous)

        return simple
