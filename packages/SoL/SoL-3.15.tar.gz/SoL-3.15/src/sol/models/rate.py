# -*- coding: utf-8 -*-
# :Progetto:  SoL -- The PlayerRating entity
# :Creato:    ven 06 dic 2013 19:20:58 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from decimal import Decimal
import logging

from sqlalchemy import Column, ForeignKey, Index, Sequence
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from ..i18n import translatable_string as N_, gettext as _
from . import Base
from .domains import date_t, intid_t, int_t, volatility_t


logger = logging.getLogger(__name__)


class Rate(Base):
    """The Glicko rating of a player."""

    __tablename__ = 'rates'
    "Related table"

    @declared_attr
    def __table_args__(cls):
        return (Index('%s_uk' % cls.__tablename__,
                      'idrating', 'idplayer', 'date',
                      unique=True),)

    ## Columns

    idrate = Column(
        intid_t, Sequence('gen_idrate', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(label=N_('Player rate ID'),
                  hint=N_('Unique ID of the player rate.')))
    """Primary key."""

    idrating = Column(
        intid_t, ForeignKey('ratings.idrating'),
        nullable=False,
        info=dict(label=N_('Rating ID'),
                  hint=N_('ID of the related rating.')))
    """Related rating's ID."""

    idplayer = Column(
        intid_t, ForeignKey('players.idplayer'),
        nullable=False,
        info=dict(label=N_('Player ID'),
                  hint=N_('ID of the related player.')))
    """Related :py:class:`player <.Player>` ID."""

    date = Column(
        date_t,
        nullable=False,
        info=dict(label=N_('Date'),
                  hint=N_('Date of the rating.')))
    """Rating date."""

    rate = Column(
        int_t,
        nullable=False,
        info=dict(label=N_('Rate'),
                  hint=N_('The value of Glicko rate.')))
    """The value of Glicko rating."""

    deviation = Column(
        int_t,
        nullable=False,
        info=dict(label=N_('Deviation'),
                  hint=N_('The value of Glicko deviation.')))
    """The value of Glicko deviation."""

    volatility = Column(
        volatility_t,
        nullable=False,
        info=dict(label=N_('Volatility'),
                  hint=N_('The value of the Glicko volatility.')))

    ## Relations

    player = relationship('Player')
    """The related :py:class:`player <.Player>`."""

    def __repr__(self):
        r = super(Rate, self).__repr__()
        r = r[:-1] + ': r=%s d=%s v=%s>' % (self.rate,
                                            self.deviation,
                                            self.volatility)
        return r

    def caption(self, html=None, localized=True):
        "A description of the rate."

        format = N_('$player in $rating on $date')
        return _(format, just_subst=not localized, mapping=dict(
            player=self.player.caption(html, localized),
            rating=self.rating.caption(html, localized),
            date=self.date.strftime(_('%m-%d-%Y'))))

    def update(self, data, missing_only=False):
        if 'volatility' in data:
            data['volatility'] = Decimal(data['volatility'])
        return super().update(data, missing_only)

    def serialize(self, serializer):
        """Reduce a single rate to a simple dictionary.

        :param serializer: a :py:class:`.Serializer` instance
        :rtype: dict
        :returns: a plain dictionary containing a flatified view of this rate
        """

        simple = {}
        simple['rating'] = serializer.addRating(self.rating)
        simple['player'] = serializer.addPlayer(self.player)
        simple['date'] = self.date
        simple['rate'] = self.rate
        simple['deviation'] = self.deviation
        simple['volatility'] = str(self.volatility)

        return simple
