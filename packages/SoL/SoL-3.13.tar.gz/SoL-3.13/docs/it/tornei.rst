.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 11:13:43 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _gestione tornei:

Gestione tornei
---------------

.. index::
   pair: Gestione; Tornei

Il *torneo* è chiaramente l'elemento primario di tutto il sistema, tutto quanto verte a
permettere di gestire in maniera facile e veloce questi eventi.

La finestra di gestione dei tornei di default **non** mostra i tornei *futuri*: per vederli,
:ref:`annulla il filtro <filtri>` applicato al campo :guilabel:`data`.


Voci del menu
~~~~~~~~~~~~~

Oltre alle :ref:`azioni standard <pulsanti-standard>` il menu contiene queste voci:

.. figure:: tornei.png
   :figclass: float-right

   Gestione tornei

:guilabel:`Dettagli`
  Mostra la :ref:`gestione <gestione torneo>` del torneo selezionato.

:guilabel:`Concorrenti`
  Consente di :ref:`correggere i concorrenti <correzione concorrenti>` di un torneo già svolto.

:guilabel:`Rigioca di nuovo`
  Consente di *duplicare* un torneo: particolarmente utile nei tornei di doppio o a squadre: in
  pratica replica il torneo sul giorno corrente, con tutti i suoi concorrenti; assicurati di
  aggiornarne la descrizione ed eventualmente la data dell'evento!

:guilabel:`Scarica`
  Permette di scaricare i dati del torneo.


.. _inserimento e modifica torneo:

Inserimento e modifica
~~~~~~~~~~~~~~~~~~~~~~

.. index::
   pair: Inserimento e modifica; Tornei

Ogni torneo ha una :guilabel:`data` e una :guilabel:`descrizione` dell'evento e non ci possono
essere due distinti tornei nella stessa data associati al medesimo campionato.

Il :guilabel:`posto` è opzionale.

:guilabel:`Durata` e :guilabel:`preavviso` si riferiscono alla durata di un singolo turno e
sono espressi in *minuti*. Vengono usati per visualizzare l':ref:`orologio`.

Un torneo può essere associato a una particolare :guilabel:`valutazione`: in questo caso il
primo turno verrà generato tenendo conto del valore di ciascun giocatore invece che usando un
ordine casuale.

.. _abbinamenti:

Il :guilabel:`metodo abbinamenti` determina come verranno create le coppie di avversari ad
ogni nuovo turno:

``Classifica``
  l'algoritmo ``serial`` cercherà di abbinare un giocatore con uno di quelli che lo seguono
  nella classifica corrente, ad esempio il primo col secondo, il terzo con il quarto e così
  via;

``Classifica incrociata``
  per ritardare per quanto possibile gli incontri tra le teste di serie, questo metodo
  (``dazed``) usa un sistema più elaborato: prende i giocatori a pari punti di quello che sta
  esaminando e cerca di abbinare il primo con quello che sta a metà di questa serie, il
  secondo con quello a metà+1, e così via.

Il campo :guilabel:`ritarda abbinamenti teste di serie`, significativo solo quando il torneo è
associato a una valutazione, determina per quanti turni viene data priorità alla quotazione
Glicko di ciascun concorrente rispetto alla *differenza pedine* nell'ordinamento utilizzato per
effettuare gli abbinamenti.

.. note::

   SoL utilizza cinque parametri per stabilire l'ordinamento della classifica:

   1. punteggio
   2. bucholz
   3. differenza score
   4. score totale
   5. quotazione Glicko

   Prima di giocare il primo turno i primi 4 valori sono tutti nulli, quindi solo il
   quinto è determinante. All'inizio del secondo turno tutti i vincitori hanno lo stesso
   punteggio e lo stesso bucholz, per cui è la differenza pedine ad essere determinante.

   Dal punto di vista della generazione dei turni, per la bellezza del gioco è
   generalmente desiderabile ritardare quanto più possibile gli scontri tra le *teste di
   serie*: a tal fine è sufficiente dare una priorità maggiore alla quotazione Glicko,
   spostandola al terzo posto, dopo il bucholz e prima della differenza score.

   Il valore assegnato a questo campo controlla appunto per quanti turni debba venire
   utilizzato questo diverso criterio di ordinamento: il valore di default è ``1``,
   indica che si desidera usarlo al termine del primo turno per la generazione del
   secondo; un valore ``0`` invece inibisce questo ritardo e quindi solo il primo turno è
   determinato dalla quotazione Glicko, dal secondo in poi diventa di fatto
   ininfluente. Valori maggiori di ``1`` hanno un impatto via via meno significativo, dal
   momento che dal terzo turno in avanti il punteggio e i bucholz diventano comunque
   predominanti.

Lo :guilabel:`score fantasma` è il punteggio assegnato al giocatore negli incontri con il
*fantasma*, quando il numero di concorrenti è dispari. Per convenzione questi incontri
assegnano uno score pari a 25 al giocatore ma ci possono essere casi in cui sia preferibile un
punteggio diverso, ad esempio quando il numero di concorrenti è molto basso e il vincere 25—0
darebbe un vantaggio inappropriato ai giocatori più deboli.

Il :guilabel:`responsabile` generalmente indica l'utente che ha inserito quel particolare
torneo: i dati del torneo potranno essere modificati solo da lui (oltre che
dall'*amministratore* del sistema.).

.. _campo finali:

Il campo :guilabel:`finali` stabilisce quante finali verranno giocate. Può essere lasciato in
bianco oppure può essere un numero tra ``0`` e ``2`` compresi: nel primo caso le finali
verranno gestite *manualmente*, nel senso che SoL non genererà gli incontri finali ma il loro
esito potrà essere applicato correggendo i premi finali. Il valore ``0`` indica che non ci sarà
alcuna finale, ``1`` indica che SoL genererà un singolo match finale per il primo e secondo
posto, mentre con il valore ``2`` verranno generati due incontri, uno per il primo e secondo
posto e l'altro per il terzo e quarto posto.

Il :guilabel:`Tipo di finale` determina la modalità di svolgimento delle finali:

``Match singolo``
  il tipo ``single`` creerà un singolo round, con un match tra il primo e secondo concorrente
  e, se :guilabel:`finali` è impostato a ``2``, un altro tra il terzo e il quarto concorrente;

``Al meglio di tre match``
  il tipo ``bestof3`` creerà al massimo tre turni e la finale sarà vinta dal concorrente che ne
  vince almeno due.

Non appena i risultati di tutti i turni sono stati inseriti, l'assegnazione dei *premi finali*
avviene automaticamente.

.. toctree::
   :maxdepth: 2

   torneo
   concorrenti
