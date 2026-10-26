# Desca Inc.

Landing page statica, mobile first, in italiano. Nessuna libreria JavaScript esterna, nessun tracker. Il pulsante apre WhatsApp al numero +39 335 653 5173 con messaggio precompilato.

## Anteprima locale

Eseguire `npm run dev` e aprire http://localhost:4173.

## Struttura

- `dist/index.html`: nome, testi e collegamento WhatsApp.
- `dist/styles.css`: layout responsive, font locali, focus e movimento ridotto.
- `dist/assets/stazione.webp`: illustrazione generata con lo strumento integrato imagegen, convertita in WebP per il web.

Prompt immagine: stazione giapponese sul mare, pixel art, cielo blu vuoto nella parte superiore, nuvole bianche con ombre lavanda, pensilina in legno e treno argento con fascia azzurra nella parte inferiore, composizione verticale ispirata alla reference fornita, senza testo né cornice.

Font: Pixelify Sans e DM Sans (SIL Open Font License), ospitati localmente. Le licenze sono incluse in `dist/assets/`.

La pubblicazione iniziale Sites è privata. Per usare il link su un biglietto da visita occorre successivamente renderla pubblica.

## Animazione della scena

Tre livelli WebP, preparati con imagegen integrato a partire dall’illustrazione originale: `stazione-base.webp` (rimozione di nuvole e treno preservando stazione e paesaggio), `nuvole.webp` (banco di nuvole su trasparenza) e `treno.webp` (treno completo su trasparenza). Prompt: composizione e palette dell’originale, pixel art, asset separati per animazione; nessun testo aggiunto. Gli asset sono conservati in `dist/assets/`.

Il viewBox SVG mantiene i livelli allineati anche quando lo schermo ritaglia la scena. Nuvole: traslazione continua di 180 secondi con copie ripetute. Treno: attraversamento di 28 secondi, ripartenza fuori campo. Quattro uccelli neri ricavati dal video `uccello.mp4` fornito dall’utente attraversano in direzione opposta con battito delle ali a quattro fotogrammi (ciclo di 0,5 secondi, sfalsato tra gli uccelli): partono 3 secondi dopo il treno a ogni ciclo. Le animazioni iniziano insieme solo quando gli asset sono pronti e condividono pausa e ripresa. `motion.js` carica gli asset prima di sostituire la foto, gestisce pausa/ripresa e sospende il movimento nelle schede nascoste. `prefers-reduced-motion` mantiene la foto originale. Il controllo pausa è accessibile da tastiera. La musica ha un comando indipendente ed è inizialmente spenta.

Lo sprite `dist/assets/uccello-sprite.webp` è estratto con FFmpeg dal segmento 0,625–1,125 secondi del video utente: ritaglio allineato, rimozione dello sfondo chiaro e conversione della palette in nero/antracite. I primi fotogrammi con il simbolo play sovrapposto sono esclusi. Il video originale non viene caricato dal sito.

## Musica

`dist/assets/komorebi.mp3` è una composizione originale sintetizzata con `scripts/compose-music.py` (NumPy e FFmpeg per la codifica MP3). Nessun campione o brano di terze parti: corde pizzicate ispirate al koto, scala in-sen su Re, 64 BPM, 60 secondi stereo. Le code e i riverberi vengono avvolti nel buffer per un loop continuo. Il file audio si carica soltanto al primo tocco su “musica”.

`dist/music.js` gestisce attivazione/silenziamento, volume contenuto con dissolvenza, pausa nelle schede nascoste e messaggi di errore accessibili. Audio inizialmente spento; nessuna preferenza persistente tra visite.

## Pubblicazione statica

La cartella da pubblicare è `dist/`: contiene la pagina e tutti gli asset, senza passaggi di build né dipendenze da installare. Il file `.openai/hosting.json` conserva la configurazione del sito Sites esistente; non è necessario per altri hosting statici.

Repository: https://github.com/Descator33/descainc

Per rigenerare la musica originale, installare NumPy e FFmpeg, eseguire `python3 scripts/compose-music.py`, quindi convertire `output/music-original.wav` in `dist/assets/komorebi.mp3`. I file in `output/` sono locali e ignorati da Git.
