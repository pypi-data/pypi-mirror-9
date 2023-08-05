.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 12:25:33 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _authentication:

.. figure:: authentication.png
   :figclass: float-right

   The authentication panel


Authentication
==============

First of all, you must authenticate yourself.

.. rubric::  *Hey, what the heck… ⁉⁈*

SoL is a `client/server` application, that is, there are two components. On one side there is
the *client*, an application running within any modern graphical web browser such as Firefox__;
this application talks with a *server*, the other side, that effectively manages the database,
and implements the so called `business logic`__.

The two components talk to each other thru a *connection*, that can be either a **local** one,
where both side actually run on a **single** machine, as two different programs that run in
parallel, or a **network** connection, where there are **two** (or more) computers involved,
either on a `LAN`__ or even thru Internet.

This allows three scenarios:

1. the most simple one, a single standalone machine without any network capability, possibly
   with a printer: everything is done on this single station;

2. a set of computers connected thru a ``LAN``, one of which is the server, where one or more
   clients connect to it: imagine you are organizing the European Championship, and there are
   pressmen who'd like to see the ranking directly on their laptop, possibly using the local
   wireless network…

3. the server is on the Internet, accessible from the outside: this may be just for showing
   your club's championship, or even to supply it as a on-line public service, where other
   people can organize their own.

So, back to the question: yes, it may be a little annoying to enter your credentials, but it's
an honest price to pay for these capabilities.

Any registered player may be allowed to login, simply assigning him a `nickname` and a
`password`: only authenticated users are allowed to insert new content or change existing
information they owns (see :ref:`here <players insert and edit>` for details).


Administrator and guest users
-----------------------------

There are two special users, not considered as :ref:`players <players management>` but are
configured externally to the application, in a configuration file.

The most important one is the *system administrator*, allowed to do everything and in
particular to assign and/or change the authentication password of the other users.

.. hint:: In a private instance of SoL, not accessible from the outside, the amministrator
          account may be used exclusively to insert and manage all the data, possibly assigning
          a simple and mnemonic password.

          On the other hand, for a public instance it is recommended to assign a *non trivial*
          password to this account and keep it secret, using such account only for
          administration purposes. Allow one of the players\ [*]_ to connect to the system,
          giving him a *nickname* and a *password* (hopefully not a *weak* one…) and use that
          account to manage the tournaments.

The other special user is the *guest*, introduced mainly for demonstration purposes: from the
application point of view it is treated as any other *ordinary* user, but it **cannot**
permanently save **any** of the changes it may apply.

Both accounts are managed in the configuration file of the application, in its ``[app:main]``
section. For example::

    sol.admin.user = admin
    sol.admin.password = SomeGùdUndStrangePassword
    #sol.guest.user = guest
    #sol.guest.password = guest

that uses “admin” as the administrator *username* and assigns it a quite good password, while
disabling the *guest* user (the ``#`` character in the configuration file introduces a
*comment*, i.e. that character and the remaining part of the line are ignored).


Ownership
---------

All *top level* entities, that is championships_, clubs_, players_, ratings_ and tournaments_,
*belong* to either a particular user or to the *administrator* of the system: this means that
the user is responsible for the entity, that may be modified or deleted only by him\ [*]_.

By default, new content is owned by the user that inserts it.

This is particularly handy on a public SoL instance, where more than one person may be allowed
to insert and manage Carrom tournaments, even at the same time, from different parts of the
world: while everybody may see each other changes, they cannot interfere in any way.

The responsibility on an entity may be reassigned at any time to a different user, either by
the current owner or by the administrator. Of course this imply that the previous owner won't
be able to change its content anymore.


__ http://en.wikipedia.org/wiki/Business_logic
__ http://en.wikipedia.org/wiki/Local_area_network
__ http://www.mozilla.org/en-US/firefox/new

.. _championships: ../championships.html
.. _clubs: ../clubs.html
.. _players: ../players.html
.. _ratings: ../ratings.html
.. _tournaments: ../tourneys.html

.. [*] Possibly yourself… you play Carrom, right⁈
.. [*] As said, the system administrator has *super powers* and thus can always do whatever he
       wants, whenever he wants.
