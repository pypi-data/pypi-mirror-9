.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 11:16:58 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _tourneys management:

Tourneys management
-------------------

.. index::
   pair: Management; Clubs

The *tourney* is clearly the primary element of the whole system, everything has been designed
to allow an easy and fast management of these events.

The tourneys window by default does **not** show *future* tournaments: to see them, :ref:`reset
the filter <filtering>` applied to the :guilabel:`date` field.


Menu actions
~~~~~~~~~~~~

In addition to the :ref:`standard actions <standard actions>` the menu at the top contains the
following items:

.. figure:: tourneys.png
   :figclass: float-right

   Tourneys management

:guilabel:`Details`
  Opens the :ref:`management <tourney management>` window of the selected tourney.

:guilabel:`Competitors`
  Opens the :ref:`competitors fixup` window that allows the correction of the competitors of
  old tourneys.

:guilabel:`Replay again`
  Allows *duplicating* an existing tourney, expecially handy on teams events: it basically
  clones a tourney on the current date, with all its competitors; just be sure to update the
  description, maybe adjusting the date of the event!

:guilabel:`Download`
  Downloads an archive of the selected tourney's data.


.. _tourney insert and edit:

Insert and edit
~~~~~~~~~~~~~~~

.. index::
   pair: Insert and edit; Tourney

Each tourney has a :guilabel:`date` and a :guilabel:`description` of the event and there cannot
be two dictinct tourneys in the same date associated to a single championship.

The :guilabel:`location` is optional.

The :guilabel:`duration` and :guilabel:`prealarm` refer to the length of a single round, and
are expressed in *minutes*. They will be used by the :ref:`clock` window.

A tourney may use a particular :guilabel:`rating`: in such a case, the first round is generated
accordingly with the rate of each player instead of using a random order.

.. _pairings:

The :guilabel:`pairing method` determines how the pairing are done at each new round:

``Ranking order``
  the ``serial`` algorithm will try to pair a player with one of the players that follows him
  in the current ranking order, for example the first with the second, the third with the
  fourth, and so on;

``Cross ranking order``
  to delay as much as possible most exciting matches, the ``dazed`` method is more elaborated:
  it takes the players with same points as the pivot, and tries to pair the first with the
  one in the middle of that series, the second with the middle+1 one, and so on.

The :guilabel:`delay top players pairing`, meaningful only when the tourney is associated with
a rating, determines how many rounds will use an higher priority for the Glicko rate of each
competitor over the *net score* in the ordering used by the pairing method.

.. note::

   SoL uses five parameters to rank the competitors:

   1. points
   2. bucholz
   3. net score
   4. total score
   5. Glicko rate

   Before playing the first round the first 4 values are all zero, so only the fifth
   is crucial. At the beginning of the second round, all winners have the same score and
   the same bucholz, thus the net score become decisive.

   From the point of view of rounds generation, for the beauty of the game it is
   generally desirable to delay as much as possible the matches between *top players*: to
   this end it is sufficient to give an higher priority to the Glicko rate, moving it to
   the third place, after the bucholz and before the net score.

   The value assigned to this field controls how many turns shall be generated using this
   different sorting criteria: the default value of ``1`` means that it will be used at
   the end of the first round to generate the second one; a value of ``0`` instead
   inhibits this delay and therefore only the first round is determined by the Glicko
   rate, from the second onward it becomes irrelevant. Values higher than ``1`` have an
   impact less and less significant, because from the third round on the points and the
   bucholz become more and more predominant.

The :guilabel:`phantom score` is the score assigned to a player in the matches against the
*phantom player*, when there are an odd number of competitors. By convention these matches
assign a score of 25 to the player but there may be cases where a different score is more
appropriate, for example when the number of competitors is very low and winning 25—0 would be
an unfair advantage.

The :guilabel:`responsible` is usually the user that inserted that particular tournament: the
information related to the tournament are changeable only by him (and also by the
*administrator* of the system).

.. _finals field:

The :guilabel:`finals` is the number of finals that will be played. It can be either left blank
or it must be a number between ``0`` and ``2`` inclusive: in the former case, finals will be
handled *manually*, that is SoL won't generate final matches but the results shall be reflected
by adjusting the bounties. A value of ``0`` means that there won't be any final, ``1`` means
that SoL will generate one single final match for the first and the second place, with ``2``
SoL will generate two final matches, one for the first and second place and another for the
third and fourth place.

The :guilabel:`final kind` determine the kind of finals that will be played:

``Single match``
  the ``single`` kind will create one single round, with a match between the first and the
  second ranked competitors and, if :guilabel:`finals` is set to ``2``, another one pairing the
  third and the fourth ranked competitors

``Best of three matches``
  the ``bestof3`` method will create at most three rounds, the final is won by the competitor
  that wins at least two of them.

As soon as the final scores of all these rounds are entered the *bounty giving* operation to
assign final bounties is performed automatically.

.. toctree::
   :maxdepth: 2

   tourney
   competitors
