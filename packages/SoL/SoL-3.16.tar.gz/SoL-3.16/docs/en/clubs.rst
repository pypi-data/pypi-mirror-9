.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 11:15:35 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _clubs management:

Clubs management
----------------

.. index::
   pair: Management; Clubs

A *club* is the entity that organizes one or more *championships* of *tourneys*. It can also
have a list of associated *players*.

.. index:: National federations

A club may also be a *national federation*, which usually coordinates the clubs of a particular
country. Often the international tourneys are hosted by this or that federation in turn and
usually it is mandatory for a player to be affiliated with a particular federation before she
can participate to an event.


Menu actions
~~~~~~~~~~~~

In addition to the :ref:`standard actions <standard actions>` the menu at the top contains the
following items:

.. figure:: clubs.png
   :figclass: float-right

   Clubs management

:guilabel:`Championship`
  Opens the :ref:`management of the championships <championships management>` organized by the
  selected club.

:guilabel:`Players`
  Opens the :ref:`management of the players <championships management>` associated with the
  selected club.

:guilabel:`Download`
  Downloads an archive of all the tourneys organized by the selected club.


Insert and edit
~~~~~~~~~~~~~~~

.. index::
   pair: Insert and edit; Club

Each club has a :guilabel:`description`, that must be unique: there cannot be two distinct
clubs with the same description.

The :guilabel:`nationality`, the :guilabel:`web site URL` and the :guilabel:`email` are
optional. The latter may be used to send email messages to the responsible for the club.

A club may be marked as a :guilabel:`federation`: to be accepted at international events it is
often mandatory for a player to be affiliated with a national federation.

The :guilabel:`pairing method` and the :guilabel:`prize-giving method` are used as default
values when new championships are added to the club.

The :guilabel:`responsible` is usually the user that inserted that particular club: the
information related to the club are changeable only by him (and also by the *administrator* of
the system).

.. _emblem:

The :guilabel:`emblem` field may contain the name of an image file (either a ``.png``, a
``.gif``, or ``.jpg``) that will printed on the :ref:`badges`. Although it will be scaled as
needed, it's recommended to put there a reasonably sized logo (the application imposes a 256Kb
limit).
