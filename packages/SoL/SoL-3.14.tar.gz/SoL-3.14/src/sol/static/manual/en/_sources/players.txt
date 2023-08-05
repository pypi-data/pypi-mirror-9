.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 11:11:43 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _players management:

Players management
------------------

.. index::
   pair: Management; Players

The *players* are obviously the cornerstone of the whole system, mainly from the point of view
of their participation to the tourneys, but also as potential *users* of the system itself:
when a player is assigned a *nickname* **and** a *password* he will be able to log in into the
system and insert new players, championships, tournaments and so on.


Menu actions
~~~~~~~~~~~~

In addition to the :ref:`standard actions <standard actions>` the menu at the top contains the
following items:

.. figure:: players.png
   :figclass: float-right

   Players management

:guilabel:`Tourneys`
  Opens the :ref:`management of the tourneys <tourneys management>`
  which the selected players participated to

:guilabel:`Duplicates`
  Switches from the normal visualization of the players to the one
  showing potential :ref:`duplicates <duplicates>`

:guilabel:`Distribution`
  Show the distribution of the players around the world

.. _players insert and edit:

Insert and edit
~~~~~~~~~~~~~~~

Player's :guilabel:`first name` and :guilabel:`last name` are mandatory, while
:guilabel:`nickname` may be used either to provide an :ref:`account <authentication>` or to
disambiguate homonyms. When changes are committed SoL does check for the presence of players
with a similar name to avoid duplicates_.

.. hint:: Usually the nickname of the player is shown in the interface and on printouts. When
          the nickname is used *only* for the authentication purpose, we suggest to compose it
          using the last name plus the first letter of the first name, or the other way around,
          possibly dropping spaces or quote characters: SoL recognizes these cases and omits
          the nickname, with the goal of reducing clutter in the interface and printouts.

          In other words, for the player “John De Beers”, in the following cases the nickname
          will be **omitted**:

          * ``john``
          * ``de beers``
          * ``debeers``
          * ``jdebeers``
          * ``jde beers``
          * ``debeersj``
          * ``de beersj``
          * ``johnd``
          * ``djohn``

Player's :guilabel:`sex`, :guilabel:`birthdate`, :guilabel:`nationality` and :guilabel:`club`
are optional and used to compute different kinds of ranking, while :guilabel:`language` and
:guilabel:`email` can be used to send email messages.

Very often to be accepted as a participant to international events a player must have the
:guilabel:`citizenship` of the country he plays for, and usually he must be affiliated to the
:guilabel:`federation` of the same country.

The :guilabel:`responsible` is usually the user that inserted that particular person: the
information related to the player are changeable only by him (and also by the *administrator*
of the system).

.. _portrait:

The :guilabel:`portrait` may be any image (preferred formats are ``.png``, ``.jpg`` or
``.gif``) and will be used in his personal page. Even if the image will be scaled as needed, it
is recommended to assign reasonable sized images (the program imposes a limit of 256Kb).


Tourney registration
~~~~~~~~~~~~~~~~~~~~

.. figure:: subscribe.png
   :figclass: float-left

   Adding other players

When you prepare a new tournament and want to subscribe the participant players, the
:guilabel:`add…` action of the :ref:`competitors panel` on the left of the :ref:`tourney
<tourneys management>` window will open the players window, where you can select one or more
players (the usual :kbd:`shift`\-click and :kbd:`ctrl`\-click allow to extend the selection).

The grid automatically shows **only** the players **not yet** present in the current tourney.
By default it also shows only the players considered *active*, i.e. those who partecipated to
at least one tourney in the last year: there is a :guilabel:`Show all players` button in the
lower right corner to toggle between this view and the *show all* view.

To add the selected players you can *drag and drop* them into the left panel of the tourney's
management window, or more simply you can use the :guilabel:`Insert selected players` button,
if present.


.. _duplicates:

Merging players
~~~~~~~~~~~~~~~

.. index:
   pair: Players; Duplicated

.. figure:: duplicated.png
   :figclass: float-left

   Potentially duplicated players

Sometime a player gets registered twice (or more) with slightly different names, for whatever
reason. The typical case is when the same player partecipates to different tourneys: being
known with different names, his results cannot be correctly summarized in the championship's
ranking, where he appears more than once, with different *aliases*.

In this situation a *merge* is needed, that is, his various *aliases* must be unified into a
single person, possibly that with the right and complete name, his *canonical name*; also,
those names must be replaced in every tourney he partecipated to with the canonical one and
finally deleted from the database.

This can be done by selecting the *wrong* aliases to be unified and :kbd:`ALT`\-dragging
(that is, dragging the selected names keeping the :kbd:`ALT` key pressed) them over the *right*
name. You must of course filter the players so that all the names are visible in a single page
at the same time, possibly prepending a temporary marker (for example ``**``) to the players'
:guilabel:`last name` and filtering on that marker.

The server application will ensure that the operation is possible, for example you'll get an
error if the replacement would cause a conflict.

To make the task easier, the :guilabel:`Duplicates` action in the menu may be handy, because it
applies a particular filter to the list of players showing only those that *appear to be*
duplicated: the first and the last name of the players are compared and only those with very
similar names, tipically differing only by a couple of letters, are shown.

.. warning:: Do **not** perform this cleanup **while** you are setting up a new tourney, as
             this may easily do the wrong thing with regard to not-yet-committed changes:
             *close the tourney management window*!
