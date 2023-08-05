.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 11:16:02 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _championships management:

Championships management
------------------------

.. index::
   pair: Championships; Management

A *championship* is a set of one or more *tourneys*, organized by the same *club* with the same
`format`: all tourneys of a particular championship are obligatorily all *singles* **or** all
*doubles* and use the same prize-giving method.


Menu actions
~~~~~~~~~~~~

In addition to the :ref:`standard actions <standard actions>` the menu at the top contains the
following items:

.. figure:: championships.png
   :figclass: float-right

   Championships management

:guilabel:`Tourneys`
  Opens the :ref:`management of the tourneys <tourneys management>` organized within the
  selected championship

:guilabel:`Download`
  Downloads an archive of all the tourneys organized within the selected championship

:guilabel:`Ranking`
  Creates a PDF document with the ranking of the selected championship


Insert and edit
~~~~~~~~~~~~~~~

.. index::
   pair: Insert and edit; Championship

Each championship has a :guilabel:`description` that must be unique within the same club.

:guilabel:`Players per team` determines the maximum number of players participating as a single
:ref:`competitor <competitors panel>`: 1 for singles, 2 for doubles, up to 4 for teams.

With :guilabel:`skip worst results` you specify how many *worst* result will be ignored in the
final sum for each player at the end of the season. This is in order not to penalize who have
not been able to participate in **all** the events.

The :guilabel:`pairing method` is used as the default value when creating new tourneys within
the championship and determines how SoL will pair the participants at each round (see
:ref:`pairing generation method <pairings>` of the tourney for details).

.. index:: Bounties

The :guilabel:`bounty-giving method` field determine the method used to assign final
bounties. These bounties have two primary scopes:

1. to have uniform, and thus `addable`, tourney results with the goal of producing the
   championship ranking

2. by being essentially freely assignable, it becomes possible to swap the positions of the
   first two (or four) players, should the final matches between the first and the second (or
   between the third and the fourth) competitors determine a different winner

One particular case is the value ``No final bounties``, which basically means that the
bounty-giving will simply assigns a monotonically decreasing sequence of integer numbers,
starting from the number of competitors down to 1 as the bounty, just to allow swapping
competitors ranking positions after tournament's final rounds. These bounties won't appear in
the final ranking printout of the tourney. Moreover, the championship's ranking does not sum up
competitor's bounties, but rather his points.

The other four values have the following meanings:

``Fixed bounties``
  assigns 18 points to the winner, 16 to the second, 14 to the third, 13 to the fourth and so
  on down to the 16th place;

``Fixed 40 bounties``
  assigns 1000 points to the winner, 900 to the second, 800 to the third, 750 to the fourth
  etc, down to 1 point to the 40th place;

``Classic millesimal bounties``
  assigns 1000 points to the winner and a proportional prize to all other players; this is
  usually preferable when the number of competitors is higher than 20 or so;

``Centesimal bounties``
  assigns 100 points to the winner, 1 point to the last competitor in the ranking, and a linear
  interpolation to the other competitors.

The field :guilabel:`closed` indicates whether the championship is complete: no other tourney
can be associated with these championships. The championship lookup combos (for example, when
inserting :ref:`new tourneys <tourneys management>`) show only those still active.

:guilabel:`Previous championship` allows browsing the various seasons of tournaments. It allows
the selection of one *closed* championship.

The :guilabel:`responsible` is usually the user that inserted that particular championship: the
information related to the championship are changeable only by him (and also by the
*administrator* of the system).
