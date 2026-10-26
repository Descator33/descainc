const root = document.documentElement;
const toggle = document.querySelector('.motion-toggle');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let loading;

function prepareMotion() {
  if (reducedMotion.matches || loading) return;
  loading = Promise.all(['stazione-base', 'nuvole', 'treno'].map(name => {
    const image = new Image();
    image.src = `assets/${name}.webp`;
    return image.decode();
  })).then(() => {
    root.classList.add('motion-ready');
    toggle.hidden = false;
  }).catch(() => {
    // Keep the original still image if a decorative asset cannot load.
    loading = undefined;
  });
}

toggle.addEventListener('click', () => {
  const paused = root.classList.toggle('motion-paused');
  toggle.setAttribute('aria-pressed', String(paused));
  toggle.setAttribute('aria-label', paused ? 'Riprendi l’animazione' : 'Metti in pausa l’animazione');
});

function syncVisibility() {
  root.classList.toggle('page-hidden', document.hidden);
}
document.addEventListener('visibilitychange', syncVisibility);
reducedMotion.addEventListener('change', prepareMotion);
syncVisibility();
prepareMotion();
