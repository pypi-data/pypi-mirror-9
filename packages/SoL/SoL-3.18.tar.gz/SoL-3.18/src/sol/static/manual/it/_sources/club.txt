.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 11:12:34 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _gestione club:

Gestione club
-------------

.. index::
   pair: Gestione; Club

Un *club* è l'entità che organizza uno o più *campionati* di *tornei*. Può anche avere un
elenco di *giocatori* associati.

.. index:: Federazioni nazionali

Un club può anche essere una *federazione nazionale*, che solitamente coordina vari club di un
certo paese. Molto spesso i tornei internazionali vengono ospitati a turno da questa o quella
federazione e in genere è richiesto che i partecipanti a questi tornei siano affiliati a una
particolare federazione.


Voci del menu
~~~~~~~~~~~~~

Oltre alle :ref:`azioni standard <pulsanti-standard>` il menu contiene queste voci:

.. figure:: club.png
   :figclass: float-right

   Gestione club

:guilabel:`Campionati`
  Apre la :ref:`gestione dei campionati <gestione campionati>` organizzati dal club selezionato

:guilabel:`Giocatori`
  Apre la :ref:`gestione dei giocatori <gestione giocatori>` associati al club selezionato

:guilabel:`Scarica`
  Permette di scaricare i dati di tutti i tornei organizzati dal club selezionato


Inserimento e modifica
~~~~~~~~~~~~~~~~~~~~~~

.. index::
   pair: Inserimento e modifica; Club

Ogni club ha una :guilabel:`descrizione` che deve essere univoca: non ci possono essere due
club con la stessa descrizione.

Sia :guilabel:`nazionalità`, che :guilabel:`URL del sito web` che :guilabel:`email` sono
facoltativi. Quest'ultimo può essere eventualmente utilizzato per inviare messaggi di posta
elettronica al responsabile del club.

Un club può essere contrassegnato come :guilabel:`federazione`: per poter partecipare a tornei
internazionali spesso si richiede che il singolo giocatore sia affiliato ad una federazione
nazionale.

Il :guilabel:`metodo abbinamenti` e il :guilabel:`metodo premiazione` sono usati come valori
di default nella creazione di nuovi campionati organizzati dal club.

Il :guilabel:`responsabile` generalmente indica l'utente che ha inserito quel particolare club:
i dati del club potranno essere modificati solo da lui (oltre che dall'*amministratore* del
sistema.).

.. _stemma:

Ad ogni club può essere assegnata un'immagine (nei formati ``.png``, ``.jpg`` o ``.gif``)
utilizzata come :guilabel:`stemma` che verrà stampato sulle :ref:`tessere` personali. Sebbene
venga automaticamente scalata alla bisogna, si raccomanda di usare immagini di dimensioni
ragionevoli (di fatto il programma impone un limite di 256Kb).
