.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 11:05:11 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

.. _gestione giocatori:

Gestione giocatori
------------------

.. index::
   pair: Gestione; Giocatori

I *giocatori* sono chiaramente il fulcro di tutto il sistema, primariamente nell'ottica della
loro partecipazione ai tornei, ma anche come potenziali *utenti* del sistema stesso: quando a
un giocatore viene assegnato un *soprannome* **e** una *password* sarà in grado di connettersi
al sistema e di inserire nuovi giocatori, campionati, tornei e così via.


Voci del menu
~~~~~~~~~~~~~

Oltre alle :ref:`azioni standard <pulsanti-standard>` il menu contiene queste voci:

.. figure:: giocatori.png
   :figclass: float-right

   Gestione giocatori

:guilabel:`Tornei`
  Apre la :ref:`gestione dei tornei <gestione tornei>` a cui ha
  partecipato il giocatore selezionato

:guilabel:`Duplicati`
  Passa dal normale elenco dei giocatori a quello dei potenziali
  :ref:`duplicati <doppioni>`

:guilabel:`Distribuzione`
  Mostra la distribuzione dei giocatori in giro per il mondo

.. _inserimento e modifica giocatori:

Inserimento e modifica
~~~~~~~~~~~~~~~~~~~~~~

.. index::
   pair: Inserimento e modifica; Giocatori

Il :guilabel:`nome` e il :guilabel:`cognome` di un giocatore sono dati obbligatori, mentre il
:guilabel:`soprannome` è facoltativo e viene usato sia come :ref:`account <autenticazione>`,
insieme all'eventuale :guilabel:`password`, che per disambiguare gli omonimi. Quando vengono
memorizzate le modifiche SoL esegue una verifica sui nomi già presenti nel database, per
evitare doppioni_, per quanto possibile.

.. hint:: Generalmente il soprannome del giocatore viene visualizzato nell'interfaccia e nelle
          stampe. Quando il nomignolo viene usato *solo* ai fini dell'autenticazione, si
          consiglia di usarne uno composto dal cognome più la prima lettera del nome, o
          viceversa, magari eliminando gli eventuali spazi o apostrofi: SoL riconosce questi
          casi e omette il soprannome, al fine di non appesantire inutilmente le
          visualizzazioni e le stampe.

          In altre parole, per il giocatore “Mario De Rossi”, nei seguenti casi il soprannome
          **non** verrà mostrato:

          * ``mario``
          * ``de rossi``
          * ``derossi``
          * ``mderossi``
          * ``mde rossi``
          * ``derossim``
          * ``de rossim``
          * ``mariod``
          * ``dmario``

I campi :guilabel:`sesso`, :guilabel:`data di nascita`, :guilabel:`nazionalità` e
:guilabel:`club` sono opzionali e vengono usati per produrre vari tipi di classifica, mentre la
:guilabel:`lingua` e l':guilabel:`email` per eventuali messaggi inviati per posta elettronica.

Generalmente per poter partecipare a tornei internazionali è richiesta la
:guilabel:`cittadinanza` per il paese per cui si gioca, oltre all'iscrizione alla
:guilabel:`federazione` del medesimo paese.

Il :guilabel:`responsabile` generalmente indica l'utente che ha inserito quel particolare
nominativo: i dati del giocatore potranno essere modificati solo da lui (oltre che
dall'*amministratore* del sistema.).

.. _ritratto:

Al giocatore può essere assegnata un'immagine (nei formati ``.png``, ``.jpg`` o ``.gif``)
utilizzata come :guilabel:`ritratto` nella sua pagina personale. Sebbene venga automaticamente
scalata alla bisogna, si raccomanda di usare immagini di dimensioni ragionevoli (di fatto il
programma impone un limite di 256Kb).


Iscrizione al torneo
~~~~~~~~~~~~~~~~~~~~

.. figure:: iscrivi.png
   :figclass: float-left

   Iscrizione altri giocatori

Quando si sta preparando un nuovo torneo e si procede con l'iscrizione dei giocatori,
dall'apposita voce :guilabel:`aggiungi…` nel menu del :ref:`pannello concorrenti` della
:ref:`gestione torneo` si accede alla maschera dei giocatori, da dove è possibile selezionare
uno o più giocatori (possibilmente estendendo la selezione usando i classici
:kbd:`shift`\-click e :kbd:`ctrl`\-click).

La maschera viene filtrata automaticamente per mostrare **solo** i giocatori **non ancora**
iscritti al torneo in questione. Inoltre di default vengono mostrati solo i giocatori
considerati *attivi*, vale a dire quelli che hanno partecipato ad almeno un torneo nel corso
dell'ultimo anno: c'è un pulsante :guilabel:`Mostra tutti i giocatori` in basso a destra che
consente di passare da questa visualizzazione a quella completa e viceversa.

Per aggiungere i giocatori selezionati al torneo si possono sia *trascinare* nel pannello
sinistro della gestione torneo, o più semplicemente si può usare il pulsante
:guilabel:`Inserisci giocatori selezionati`, se presente.


.. _doppioni:

Doppia registrazione di un giocatore
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. index::
   pair: Giocatori; Duplicati

.. figure:: duplicati.png
   :figclass: float-left

   Giocatori potenzialmente duplicati

Talvolta un giocatore viene inserito nel database due (o più) volte con nomi leggermente
diversi, per errore o incomprensione. Il caso tipico è quello di un particolare giocatore che
partecipa a diversi tornei: essendo identificato in maniera non univoca, i suoi risultati non
possono essere riassunti correttamente nella classifica del campionato, dove appare più volte
con le sue varie identità.

In questa situazione è necessario eseguire una correzione ai dati, sostituendo le varie
identità con una unica, in tutti i tornei dove ha partecipato. Infine, le identità *sbagliate*
devono essere cancellate dal database.

Questo può essere fatto selezionando le identità *sbagliate* e trascinandole sopra quella
*giusta* mantenendo premuto il tasto :kbd:`ALT`. È necessario ovviamente fare in modo che tutti
i giocatori interessati siano visibili allo stesso momento applicando un filtro opportuno,
eventualmente inserendo un marcatore temporaneo (tipo `**`) nel cognome dei giocatori su cui si
intende operare e filtrando su quello.

L'applicazione verificherà che l'operazione non generi alcun conflitto, segnalando un errore ad
esempio quando in uno stesso torneo risulti presente *sia* il nome *giusto* che uno di quelli
*sbagliati*.

Per facilitare il compito, può tornare comoda la voce :guilabel:`Duplicati` nel menu, che
applica un filtro particolare all'elenco dei giocatori evidenziando quelli che *potrebbero
essere* dei duplicati: in sostanza vengono confrontati i nomi e cognomi dei giocatori e vengono
mostrati solo i giocatori che hanno nomi *molto* simili tra loro, tipicamente perché
differiscono solo per poche lettere.

.. warning:: **Non** eseguire questa operazione **mentre** si sta preparando un nuovo torneo,
             perché i dati modificati e non ancora memorizzati potrebbero facilmente risultare
             non più corretti: *la finestra di gestione del torneo deve essere chiusa*!
