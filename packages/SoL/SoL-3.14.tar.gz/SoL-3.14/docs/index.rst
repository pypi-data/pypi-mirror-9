.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    gio 06 nov 2008 14:09:01 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

=====================
 Scarry On Lin{e|ux}
=====================

Introduction
============

This application has the goal of making it easier the organization of a championship of
Carrom_.

.. _Carrom: http://en.wikipedia.org/wiki/Carrom

Its short codename, ``SoL``, may stand either as *Scarry On (GNU)/Linux* or as *Scarry On
Line*, until a better description comes out. Both are a bit imprecise, because

* ``SoL`` should run perfectly well on many other operating systems, being written in Python_
  and (currently) JavaScript

* despite it being a *client/server* application, potentially exposed on Internet or on the
  local LAN, it does **not** require the network, everything can run on a single disconnected
  machine.

In turn ``Scarry``, the ancestor of ``SoL``, was named after the word I'm used to call Carrom_
with, Scarambol__.

.. _python: http://www.python.org/
__ https://www.facebook.com/Scarambol

Brief history
-------------

``Scarry`` was a Delphi application I wrote years ago, with the equivalent goal. It started as
a "quick and dirty" solution to the problem, and Delphi was quite good at that. It served us
for years, with good reliability, but since I find programming in that claudicant environment
really boring, there was no way I can be convinced to enhance it further.

This is a complete reimplementation, restarting from scratch: it's built exclusively with `free
software`__ components, so that I won't be embaraced to public the whole source code.

__ http://en.wikipedia.org/wiki/Free_software

User manuals
============

The user manual is currently available in the following languages:

* `English <en/index.html>`_
* `Italiano <it/index.html>`_

Developers
==========

.. toctree::
   :maxdepth: 2

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
