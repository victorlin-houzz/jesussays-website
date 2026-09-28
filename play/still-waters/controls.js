(() => {
  'use strict';
  const renderer = window.StillWaters;
  const canvas = document.getElementById('water');
  const status = document.getElementById('status');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let paused = false, drift = true, ink = 1;
  const command = message => renderer.command(message);
  function unavailable() {
    document.getElementById('fallback').hidden = false;
    document.querySelectorAll('.controls button').forEach(button => button.disabled = true);
    canvas.removeAttribute('tabindex');
    status.textContent = 'A quiet moment with Psalm 46:10.';
  }
  if (!renderer || renderer.metrics().events.some(e => e.event === 'failed')) { unavailable(); return; }
  function configure() {
    document.getElementById('drift').setAttribute('aria-pressed', String(drift && !motion.matches));
    command({type: 'configure', active: !paused && !document.hidden, playing: drift && !motion.matches, reducedMotion: motion.matches, ink, quietBand: [0, .26, true]});
  }
  configure();
  if (motion.matches) status.textContent = 'Reduced motion is enabled. Add ink for a still pattern.';
  document.querySelectorAll('[data-ink]').forEach(button => button.addEventListener('click', () => {
    ink = Number(button.dataset.ink);
    document.querySelectorAll('[data-ink]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    configure(); status.textContent = button.textContent + ' ink selected.';
  }));
  function drop() {
    if (paused) { status.textContent = 'Resume motion to add ink.'; return; }
    command({type: 'drop', x: .25 + Math.random() * .5, y: .3 + Math.random() * .4, ink});
    status.textContent = 'Ink on the water. Take a quiet breath.';
  }
  document.getElementById('drop').addEventListener('click', drop);
  canvas.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); drop(); } });
  document.getElementById('drift').addEventListener('click', e => {
    drift = !drift; e.currentTarget.setAttribute('aria-pressed', String(drift)); configure();
    status.textContent = motion.matches ? 'Reduced motion is enabled. Add ink for a still pattern.' : drift ? 'Let the ink drift. Nothing to finish.' : 'Drift stopped. Touch the water to stir.';
  });
  document.getElementById('pause').addEventListener('click', e => {
    paused = !paused; e.currentTarget.setAttribute('aria-pressed', String(paused)); e.currentTarget.textContent = paused ? 'Resume motion' : 'Pause motion'; configure();
    status.textContent = paused ? 'Motion paused.' : 'Motion resumed.';
  });
  document.getElementById('wash').addEventListener('click', () => { command({type: 'clear'}); status.textContent = 'Fresh water. Begin again whenever you like.'; });
  motion.addEventListener('change', () => {
    configure();
    status.textContent = motion.matches ? 'Reduced motion is enabled. Add ink for a still pattern.' : 'Touch the water, or let the ink drift.';
  });
  document.addEventListener('visibilitychange', configure);
  canvas.addEventListener('webglcontextlost', unavailable);
  // Pause pointer input along with animation.
  ['pointerdown','pointermove','pointerup'].forEach(type => canvas.addEventListener(type, e => { if (paused) e.stopImmediatePropagation(); }, true));
})();
