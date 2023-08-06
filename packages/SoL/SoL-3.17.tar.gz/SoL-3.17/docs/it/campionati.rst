.. -*- coding: utf-8 -*-
.. :Progetto:   -- SoL
.. :Creato:    mer 25 dic 2013 11:13:02 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _gestione campionati:

Gestione campionati
-------------------

.. index::
   pair: Gestione; Campionati

Un *campionato* raggruppa uno o più *tornei*, organizzati dallo stesso *club*, con regole di
gioco omogenee: tutti i tornei di uno stesso campionato sono necessariamente tutti *singoli*
**oppure** a *squadre* e usano il medesimo metodo di assegnazione dei premi finali.


Voci del menu
~~~~~~~~~~~~~

Oltre alle :ref:`azioni standard <pulsanti-standard>` il menu contiene queste voci:

.. figure:: campionati.png
   :figclass: float-right

   Gestione campionati

:guilabel:`Tornei`
  Apre la :ref:`gestione dei tornei <gestione tornei>` organizzati nell'ambito del campionato
  selezionato

:guilabel:`Scarica`
  Permette di scaricare i dati di tutti i tornei organizzati nell'ambito del campionato
  selezionato

:guilabel:`Classifica`
  Produce un documento PDF con la classifica del campionato selezionato


Inserimento e modifica
~~~~~~~~~~~~~~~~~~~~~~

.. index::
   pair: Inserimento e modifica; Campionato

Ogni campionato ha una :guilabel:`descrizione` che deve essere univoca per un certo
:guilabel:`club`.

.. _giocatori per squadra:

:guilabel:`Giocatori per squadra` determina il numero massimo di giocatori che compongono un
singolo :ref:`concorrente <pannello concorrenti>`: 1 per i singoli, 2 per il doppio e fino a 4
per i tornei a squadre.

Con :guilabel:`ignora i peggiori risultati` si specifica quanti risultati *peggiori* di ogni
giocatore verranno ignorati nel calcolo della classifica di fine campionato. In genere viene
usato per consentire ai giocatori di non partecipare a **tutte** le tappe di un campionato e di
rimanere comunque in competizione.

Il :guilabel:`metodo abbinamenti` viene usato come valore di default quando si creano nuovi
tornei nel campionato e determina come verranno create le coppie di avversari ad ogni nuovo
turno (vedi :ref:`sistema di generazione abbinamenti <abbinamenti>` del torneo per i
dettagli).

.. index:: Premi finali

Il :guilabel:`metodo premiazione` determina come verranno assegnati i premi finali. Tali premi
hanno due funzioni primarie:

1. uniformare, rendendo quindi `sommabili`, i risultati dei singoli tornei per produrre la
   classifica del campionato

2. essendo di fatto liberamente assegnabili, consentono di invertire la posizione dei primi due
   (o quattro) giocatori qualora l'eventuale `finale` tra il primo e il secondo classificato (e
   tra il terzo e il quarto) dovesse così stabilire

Un caso particolare è il valore ``Nessun premio finale``, che in pratica significa la
premiazione assegnerà semplicemente una sequenza decrescente di numeri interi a cominciare dal
numero di concorrenti fino a 1 come premio finale, solo al fine di consentire l'aggiustamento
delle posizioni in classifica al termine dei turni finali del torneo. Questo premi non
compariranno nella stampa della classifica del torneo. Inoltre, nella classifica del campionato
non verranno considerati i premi finali dei concorrenti, bensì il loro punteggio.

I rimanenti quattro valori identificano altrettanti metodi di generazione dei premi finali:

``Premi fissi``
  assegna 18 punti al primo, 16 al secondo, 14 al terzo, 13 al quarto e così via fino al
  sedicesimo piazzamento;

``40 premi fissi``
  assegna 1000 punti al primo, 900 al secondo, 800 al terzo, 750 al quarto e così via, fino a
  un punto per il quarantesimo classificato;

``Millesimale classico``
  assegna 1000 punti al vincitore e un premio proporzionale a tutti gli altri; in genere è il
  metodo preferito quando il numero di concorrenti è maggiore di 20 o giù di lì;

``Centesimale``
  assegna 100 punti al vincitore, 1 punto all'ultimo classificato, interpolando linearmente il
  premio da assegnare agli altri concorrenti.

Il campo :guilabel:`concluso` indica se il campionato è terminato: in questo caso nessun altro
torneo potrà esservi associato e pertanto il selettore di campionato (ad esempio inserendo
nuovi :ref:`tornei <gestione tornei>`) mostrerà solo quelli ancora attivi.

Il campo :guilabel:`campionato precedente` consente di consultare le varie stagioni di
tornei. È possibile selezionare solo campionati *conclusi*.

Il :guilabel:`responsabile` generalmente indica l'utente che ha inserito quel particolare
campionato: i dati del campionato potranno essere modificati solo da lui (oltre che
dall'*amministratore* del sistema.).
