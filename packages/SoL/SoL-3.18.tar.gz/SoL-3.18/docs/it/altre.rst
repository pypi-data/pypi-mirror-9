.. -*- coding: utf-8 -*-
.. :Progetto:  SoL
.. :Creato:    mer 25 dic 2013 12:20:17 CET
.. :Autore:    Lele Gaifax <lele@metapensiero.it>
.. :Licenza:   GNU General Public License version 3 or later
..

Altre finestre
==============

.. _orologio:

.. figure:: orologio.png
   :figclass: float-right

   L'orologio con allarme.

Orologio
--------

Il semplice orologio analogico è basato su CoolClock_ e su SoundManager_ per poter ottenere un
allarme sonoro.

Il *conto alla rovescia* può essere attivato sia con un doppio click sull'orologio oppure
usando il primo pulsante in basso; un altro modo di farlo è usando il secondo pulsante che farà
partire il tempo dopo 15 secondi, dando così modo all'operatore di raggiungere il proprio
tavolo di gioco.

L'orologio utilizza i valori impostati in :guilabel:`durata` e :guilabel:`preavviso` sul
:ref:`torneo <gestione tornei>` per disegnare tre cerchietti colorati in verde, arancio e
rosso, a rappresentare rispettivamente il minuto di partenza, quello di preavviso e quello di
conclusione del turno. Se si sta utilizzando un moderno browser HTML5, oppure se si è
installato correttamente il plugin Flash_, l'orologio emette un breve suono.

Al raggiungimento del preavviso apparirà la lancetta dei secondi e viene emesso un suono
differente: in genere questo significa che, mancando pochi minuti al termine, non possono
essere iniziate nuove partite, mentre quelle in corso possono terminare.

A un minuto dal termine l'orologio emette un *tic-tac* ad ogni secondo. Alla fine, raggiunto il
punto rosso, viene emesso il suono di termine: a quel punto le partite ancora in corso devono
essere fermate e il punteggio verrà determinato dalla sola differenza pedine ancora in gioco,
senza tener conto della `Regina`.

Chiudere la finestra con l'orologio (o usa il terzo pulsante in basso) per annullare l'allarme:
per prevenire chiusure accidentali, viene richiesta una conferma esplicita.

.. hint:: Dal momento che l'istante di attivazione del conto alla rovescia viene inviato a SoL
          e memorizzato nel database, se per qualsiasi ragione il computer dovesse essere fatto
          ripartire il conto alla rovescia verrà ripristinato dal medesimo istante.

          Questo consente inoltre di mostrare più orologi, anche su computer diversi, ad
          esempio quando si desideri mostrare lo stesso conto alla rovescia in stanze diverse.
          Ovviamente in questo caso il conto alla rovescia deve essere fatto partire da una
          sola postazione, mentre sulle altre basterà richiedere la visualizzazione
          dell'orologio **dopo** aver fatto partire il conto alla rovescia.

.. _coolclock: http://simonbaird.com/coolclock/
.. _soundmanager: http://schillmania.com/projects/soundmanager2/
.. _flash: http://www.adobe.com/go/getflash
.. _caricamento:

.. figure:: caricamento.png
   :figclass: float-right

   Caricamento dati torneo.

Caricamento
-----------

Con questa semplice finestra è possibile caricare i dati di un intero torneo, provenienti da
un'altra istanza di SoL. I nuovi dati non sovrascriveranno quelli esistenti, delle entità
preesistenti verranno aggiornati solo i dati mancanti.

Chiunque può caricare archivi ``.sol`` (o la versione compressa ``.sol.gz``). Gli utenti
autenticati, tranne l'utente `guest`, possono caricare anche archivi ``.zip`` con i dati dei
tornei insieme ai ritratti dei giocatori e agli stemmi dei club.

.. topic:: Esportazione dei dati

   I dati dei tornei possono essere estratti con il pulsante :guilabel:`Scarica` nelle gestioni
   dei :ref:`tornei <gestione tornei>` e dei :ref:`campionati <gestione campionati>`: si tratta
   di file di testo, in formato YAML__ (eventualmente compresso), che possono essere ricaricati
   in un'altra istanza di SoL, piuttosto che archiviati per sicurezza. L'archivio creato in
   questo modo contiene tutti i tornei specificati così come i dati relativi a tutti i
   giocatori, club e campionati coinvolti. **Non** contiene nessuna immagine, né ritratti né
   stemmi.

   Un altro modo consente di esportare l'intero database, cioè *tutti* i tornei e *tutti* i
   giocatori (indipendentemente se abbiano partecipato a un torneo o meno) **e tutte** le
   immagini associate. Visitando l'indirizzo::

     http://localhost:6996/bio/backup

   si otterrà un archivio ``ZIP`` contenente tutto quanto, che potrà essere caricato in
   un'altra installazione di SoL, copiando/aggiornando così praticamente tutte le informazioni
   memorizzate e le relative immagini. Chiaramente l'archivio prodotto in questo modo avrà
   dimensioni molto maggiori del precedente: questo metodo è raccomandato solo per migrare
   l'intero database a una nuova versione di SoL, oppure qualora si desideri copiare tutte le
   immagini in un colpo solo.

__ http://www.yaml.org/
