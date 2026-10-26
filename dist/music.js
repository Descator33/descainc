const musicButton = document.querySelector('.music-toggle');
const soundtrack = document.querySelector('#soundtrack');
const musicStatus = document.querySelector('#music-status');
let wantsMusic = true;
let waitingForGesture = false;
let fadeFrame;
let playRequest = 0;

// Keep the first play attempt audible so browser autoplay permissions apply.
soundtrack.volume = .01;
musicButton.hidden = false;

function showMusicState(playing) {
  musicButton.setAttribute('aria-pressed', String(playing));
  musicButton.setAttribute('aria-label', playing ? 'Disattiva musica' : 'Attiva musica');
}

function fadeTo(target, done) {
  cancelAnimationFrame(fadeFrame);
  const initial = soundtrack.volume;
  const start = performance.now();
  function frame(now) {
    const progress = Math.min((now - start) / 700, 1);
    soundtrack.volume = initial + (target - initial) * progress;
    if (progress < 1) fadeFrame = requestAnimationFrame(frame);
    else if (done) done();
  }
  fadeFrame = requestAnimationFrame(frame);
}

function clearGestureStart() {
  waitingForGesture = false;
  document.removeEventListener('click', startFromGesture, true);
  document.removeEventListener('keydown', startFromGesture, true);
}

function waitForGesture() {
  if (waitingForGesture) return;
  waitingForGesture = true;
  document.addEventListener('click', startFromGesture, true);
  document.addEventListener('keydown', startFromGesture, true);
}

function startFromGesture(event) {
  if (!wantsMusic || document.hidden || event.target.closest?.('.music-toggle')) return;
  if (event.type === 'keydown' && (event.metaKey || event.ctrlKey || event.altKey || !['Enter', ' '].includes(event.key))) return;
  clearGestureStart();
  startMusic();
}

async function startMusic() {
  if (!wantsMusic || document.hidden) return;
  const request = ++playRequest;
  musicButton.setAttribute('aria-busy', 'true');
  if (soundtrack.error) soundtrack.load();
  if (soundtrack.volume === 0) soundtrack.volume = .01;
  try {
    await soundtrack.play();
    if (request !== playRequest) return;
    if (!wantsMusic || document.hidden) {
      soundtrack.pause();
      return;
    }
    clearGestureStart();
    showMusicState(true);
    musicStatus.textContent = '';
    fadeTo(.45);
  } catch (error) {
    if (request !== playRequest) return;
    showMusicState(false);
    if (error.name === 'NotAllowedError') {
      // Autoplay can be blocked; retry synchronously on the first user gesture.
      musicStatus.textContent = '';
      waitForGesture();
    } else {
      wantsMusic = false;
      clearGestureStart();
      musicStatus.textContent = 'Audio non disponibile. Tocca musica per riprovare.';
    }
  } finally {
    if (request === playRequest) musicButton.setAttribute('aria-busy', 'false');
  }
}

musicButton.addEventListener('click', () => {
  if (waitingForGesture || !wantsMusic) {
    wantsMusic = true;
    clearGestureStart();
    startMusic();
  } else {
    wantsMusic = false;
    ++playRequest;
    clearGestureStart();
    showMusicState(false);
    musicButton.setAttribute('aria-busy', 'false');
    fadeTo(0, () => soundtrack.pause());
  }
});

// Preserve the visitor's explicit mute choice while following tab visibility.
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    ++playRequest;
    cancelAnimationFrame(fadeFrame);
    soundtrack.pause();
    soundtrack.volume = 0;
    musicButton.setAttribute('aria-busy', 'false');
  } else if (wantsMusic) startMusic();
});

soundtrack.addEventListener('error', () => {
  if (!wantsMusic) return;
  ++playRequest;
  wantsMusic = false;
  clearGestureStart();
  showMusicState(false);
  musicButton.setAttribute('aria-busy', 'false');
  musicStatus.textContent = 'Audio non disponibile. Tocca musica per riprovare.';
});

waitForGesture();
startMusic();
