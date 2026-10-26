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

Il viewBox SVG mantiene i livelli allineati anche quando lo schermo ritaglia la scena. Nuvole: traslazione continua di 180 secondi con copie ripetute. Treno: attraversamento di 38 secondi, ripartenza fuori campo. `motion.js` carica gli asset prima di sostituire la foto, gestisce pausa/ripresa e sospende il movimento nelle schede nascoste. `prefers-reduced-motion` mantiene la foto originale. Il controllo pausa è accessibile da tastiera. Nessun audio.
