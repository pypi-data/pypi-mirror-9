# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Track players merges
# :Creato:    sab 21 dic 2013 13:12:36 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import logging

from sqlalchemy import Column, ForeignKey, Index, Sequence
from sqlalchemy.ext.declarative import declared_attr

from ..i18n import translatable_string as N_
from . import Base, GloballyUnique
from .domains import intid_t, name_t, nickname_t


logger = logging.getLogger(__name__)


class MergedPlayer(GloballyUnique, Base):
    """A player who has been merged into another."""

    __tablename__ = 'mergedplayers'
    "Related table."

    @declared_attr
    def __table_args__(cls):
        return (GloballyUnique.__table_args__(cls) +
                (Index('%s_names' % cls.__tablename__,
                       'lastname', 'firstname', 'nickname'),
                 Index('%s_idplayer' % cls.__tablename__,
                       'idplayer')))

    ## Columns

    idmergedplayer = Column(
        intid_t, Sequence('gen_idmergedplayer', optional=True),
        primary_key=True,
        nullable=False,
        info=dict(label=N_('Merge ID'),
                  hint=N_('Unique ID of the merged player.')))
    """Primary key."""

    firstname = Column(
        name_t,
        nullable=False,
        default='',
        info=dict(label=N_('First name'),
                  hint=N_('First name of the player.')))
    """Player's first name."""

    lastname = Column(
        name_t,
        nullable=False,
        default='',
        info=dict(label=N_('Last name'),
                  hint=N_('Last name of the player.')))
    """Player's last name."""

    nickname = Column(
        nickname_t,
        nullable=False,
        default='',
        info=dict(label=N_('Nickname'),
                  hint=N_('Nickname of the player, for'
                          ' login and to disambiguate homonyms.')))
    """Player's nickname, used also for login purposes."""

    idplayer = Column(
        intid_t, ForeignKey('players.idplayer'),
        nullable=False,
        info=dict(label=N_('Player ID'),
                  hint=N_('ID of the target player.')))
    """Target :py:class:`player <.Player>`'s ID."""

    def shouldOmitNickName(self):
        "Determine if the nickname should be omitted because redundant."

        from . import Player

        return Player.shouldOmitNickName(self)

    def caption(self, html=None, localized=True):
        "Description of the player, made up concatenating his names."

        from . import Player

        if self.lastname:
            oldname = Player.caption(self, html, localized=localized)
        else:
            oldname = self.guid

        newname = self.player.caption(html, localized=localized)
        return '%s -> %s' % (oldname, newname)

    description = property(caption)
