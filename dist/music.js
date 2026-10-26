const musicButton = document.querySelector('.music-toggle');
const soundtrack = document.querySelector('#soundtrack');
const musicStatus = document.querySelector('#music-status');
let wantsMusic = false;
let fadeFrame;

soundtrack.volume = 0;
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

async function startMusic() {
  musicButton.setAttribute('aria-busy', 'true');
  if (soundtrack.error) soundtrack.load();
  try {
    await soundtrack.play();
    if (!wantsMusic || document.hidden) {
      soundtrack.pause();
      return;
    }
    showMusicState(true);
    musicStatus.textContent = '';
    fadeTo(.45);
  } catch {
    wantsMusic = false;
    showMusicState(false);
    musicStatus.textContent = 'Audio non disponibile. Tocca musica per riprovare.';
  } finally {
    musicButton.setAttribute('aria-busy', 'false');
  }
}

musicButton.addEventListener('click', () => {
  wantsMusic = !wantsMusic;
  if (wantsMusic) startMusic();
  else {
    showMusicState(false);
    fadeTo(0, () => soundtrack.pause());
  }
});

// Audio follows the tab's visibility; the visitor's on/off preference is retained.
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    cancelAnimationFrame(fadeFrame);
    soundtrack.pause();
    soundtrack.volume = 0;
  } else if (wantsMusic) startMusic();
});

soundtrack.addEventListener('error', () => {
  if (!wantsMusic) return;
  wantsMusic = false;
  showMusicState(false);
  musicStatus.textContent = 'Audio non disponibile. Tocca musica per riprovare.';
});
