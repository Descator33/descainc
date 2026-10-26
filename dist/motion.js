const root = document.documentElement;
const toggle = document.querySelector('.motion-toggle');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const wideScene = window.matchMedia('(min-aspect-ratio: 1/1)');
const scene = document.querySelector('.motion-scene');

function updateSceneLayout() {
  const wide = wideScene.matches;
  const width = wide ? 2560 : 1086;
  scene.setAttribute('viewBox', `0 0 ${width} 1448`);
  scene.style.setProperty('--train-start', `${width + 14}px`);
  scene.style.setProperty('--train-still', wide ? '1500px' : '740px');
  scene.style.setProperty('--birds-end', `${width + 214}px`);
  document.querySelectorAll('.scene-base').forEach(image => {
    image.setAttribute('href', `assets/stazione-${wide ? 'wide' : 'base'}.webp`);
    image.setAttribute('width', width);
  });
  const cloudClip = document.querySelector('#cloud-band rect');
  cloudClip.setAttribute('y', wide ? 500 : 600);
  cloudClip.setAttribute('height', wide ? 527 : 490);
  // Short, wide screens need a lower cloud bank to keep the contact readable.
  const aspect = window.innerWidth / window.innerHeight;
  const cloudScale = wide ? Math.max(.5, 1 - Math.max(0, aspect - 1.8) * 1.1) : 1;
  const cloudStep = 1086 * cloudScale;
  scene.style.setProperty('--cloud-shift', `${-cloudStep}px`);
  document.querySelectorAll('.cloud-drift image').forEach((image, i) => {
    image.setAttribute('x', (i - 1) * cloudStep);
    image.setAttribute('width', cloudStep + 2);
    image.setAttribute('height', 466 * cloudScale);
    image.setAttribute('y', wide ? 1043 - 466 * cloudScale : 640);
  });
  document.querySelectorAll('.bird-sprite').forEach((bird, i) => {
    bird.setAttribute('y', [635, 600, 650, 615][i] + (1 - cloudScale) * 500);
  });
  document.querySelector('#station-front rect').setAttribute('y', wide ? 1027 : 1090);
  document.querySelector('#station-front rect').setAttribute('height', wide ? 421 : 358);
  document.querySelector('.pole-clip').setAttribute('d', wide
    ? 'M94 794H108L120 1027H90Z M120 947H795L807 1004H120Z'
    : 'M68 966H80L91 1090H65Z');
  document.querySelector('.train-journey image').setAttribute('y', wide ? 926 : 965);
}
wideScene.addEventListener('change', updateSceneLayout);
let resizeFrame;
window.addEventListener('resize', () => {
  cancelAnimationFrame(resizeFrame);
  resizeFrame = requestAnimationFrame(updateSceneLayout);
});
updateSceneLayout();
let loading;

function prepareMotion() {
  if (loading) return;
  loading = Promise.all([wideScene.matches ? 'stazione-wide' : 'stazione-base', 'nuvole', 'treno', 'uccello-sprite'].map(name => {
    const image = new Image();
    image.src = `assets/${name}.webp`;
    return image.decode();
  })).then(() => {
    root.classList.add('motion-ready');
    toggle.hidden = reducedMotion.matches;
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
reducedMotion.addEventListener('change', () => {
  toggle.hidden = reducedMotion.matches || !root.classList.contains('motion-ready');
  prepareMotion();
});
syncVisibility();
prepareMotion();
