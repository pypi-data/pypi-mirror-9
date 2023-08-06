# -*- coding: utf-8 -*-
# :Progetto:  SoL -- The Club entity
# :Creato:    gio 27 nov 2008 13:49:40 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import logging

from sqlalchemy import Column, ForeignKey, Index, Sequence
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from ..i18n import translatable_string as N_, translator
from . import Base, GloballyUnique
from .domains import (
    boolean_t,
    code_t,
    description_t,
    email_t,
    filename_t,
    intid_t,
    nationality_t,
    url_t,
    )


logger = logging.getLogger(__name__)


class Club(GloballyUnique, Base):
    """A club, which organizes championships of tourneys."""

    __tablename__ = 'clubs'
    "Related table"

    @declared_attr
    def __table_args__(cls):
        return (GloballyUnique.__table_args__(cls) +
                (Index('%s_uk' % cls.__tablename__, 'description',
                       unique=True),))

    ## Columns

    idclub = Column(
        intid_t, Sequence('gen_idclub', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(label=N_('Club ID'),
                  hint=N_('Unique ID of the club.')))
    """Primary key."""

    idowner = Column(
        intid_t, ForeignKey('players.idplayer', use_alter=True, name="fk_club_owner",
                            ondelete="SET NULL"),
        info=dict(label=N_('Owner ID'),
                  hint=N_('ID of the user that is responsible for this record.')))
    """ID of the :py:class:`user <.Player>` that is responsible for this record."""

    description = Column(
        description_t,
        nullable=False,
        info=dict(label=N_('Club'),
                  hint=N_('Description of the club.')))
    """Description of the club."""

    emblem = Column(
        filename_t,
        info=dict(label=N_('Emblem'),
                  hint=N_('File name of the PNG, JPG or GIF'
                          ' logo of the club.')))
    """Logo of the club, used on badges.

    This is just the filename, referencing a picture inside the
    ``sol.emblems_dir`` directory.
    """

    nationality = Column(
        nationality_t,
        info=dict(label=N_('Country'),
                  hint=N_('Nationality of the club.')))
    """`ISO country code <http://en.wikipedia.org/wiki/ISO_3166-1_alpha-3>`_
    to compute national rankings."""

    couplings = Column(
        code_t,
        default='serial',
        info=dict(label=N_('Pairings'),
                  hint=N_('Default method used to pair competitors at each round.'),
                  dictionary=dict(serial=N_('Ranking order'),
                                  dazed=N_('Cross ranking order'))))
    """Kind of pairing method used to build next round, used as default value
    for the corresponding field when creating a new championship."""

    prizes = Column(
        code_t,
        nullable=False,
        default='fixed',
        info=dict(label=N_('Prizes'),
                  hint=N_('Default method used to assign final prizes.'),
                  dictionary=dict(
                      asis=N_('Simple tourneys, no special prizes'),
                      fixed=N_('Fixed prizes: 18,16,14,13…'),
                      fixed40=N_('Fixed prizes: 1000,900,800,750…'),
                      millesimal=N_('Classic millesimal prizes'))))
    """Kind of prize-giving, used as default value for the corresponding
    field when creating a new championship.

    This is used to determine which method will be used to assign
    final prizes. It may be:

    `asis`
      means that the final prize is the same as the competitor's points;

    `fixed`
      means the usual way, that is 18 points to the winner, 16 to the
      second, 14 to the third, 13 to the fourth, …, 1 point to the
      16th, 0 points after that;

    `fixed40`
      similar to `fixed`, but applied to best fourty scores starting
      from 1000:

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
      is the classic method, that distributes a multiple of
      1000/num-of-competitors."""

    siteurl = Column(
        url_t,
        info=dict(label=N_('Website'),
                  hint=N_('URL of the web site of the club.')))
    """Web site URL."""

    email = Column(
        email_t,
        info=dict(label=N_('Email'),
                  hint=N_('Email address of the club.')))
    """Email address of the club."""

    isfederation = Column(
        boolean_t,
        nullable=False,
        default=False,
        info=dict(label=N_('Federation'),
                  hint=N_('Whether the club is also a federation.')))
    """Flag indicating whether the club is also a federation."""

    ## Relations

    owner = relationship('Player', backref='owned_clubs',
                         primaryjoin="Club.idowner==Player.idplayer")
    """The :py:class:`owner <.Player>` of this record, `admin` when ``None``."""

    championships = relationship('Championship', backref='club',
                                 cascade="all, delete-orphan",
                                 order_by="Championship.description")
    """:py:class:`Championships <.Championship>` organized by this club."""

    associated_players = relationship('Player', backref='club',
                                      primaryjoin='Player.idclub==Club.idclub',
                                      passive_updates=False)
    """Players associated with this club."""

    federated_players = relationship('Player', backref='federation',
                                      primaryjoin='Player.idfederation==Club.idclub',
                                      passive_updates=False)
    """Players associated with this federation."""

    ratings = relationship('Rating', backref='club')
    """:py:class:`Ratings <.Rating>` reserved for tourneys organized by this club."""

    @property
    def country(self):
        "The name of the club's country."

        from gettext import translation
        from pycountry import LOCALES_DIR, countries
        from pyramid.threadlocal import get_current_request

        request = get_current_request()
        lname = getattr(request, 'locale_name', 'en')
        try:
            t = translation('iso3166', LOCALES_DIR, languages=[lname]).gettext
        except IOError:
            t = lambda x: x

        ccode = self.nationality
        if ccode:
            if ccode == 'eur':
                country = translator(request)(N_('Europe'))
            else:
                country = t(countries.get(alpha3=ccode).name)
        else:
            country = translator(request)(N_('Unspecified country'))

        return country

    def serialize(self, serializer):
        """Reduce a single club to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :rtype: dict
        :returns: a plain dictionary containing a flatified view of this club
        """

        simple = {}
        simple['guid'] = self.guid
        simple['modified'] = self.modified
        if self.idowner:
            simple['owner'] = serializer.addPlayer(self.owner)
        simple['description'] = self.description
        if self.emblem:
            simple['emblem'] = self.emblem
        simple['prizes'] = self.prizes
        simple['couplings'] = self.couplings
        if self.nationality:
            simple['nationality'] = self.nationality
        if self.siteurl:
            simple['siteurl'] = self.siteurl
        if self.email:
            simple['email'] = self.email
        if self.isfederation:
            simple['isfederation'] = self.isfederation

        return simple
