// Shared site navigation: mobile menu with focus trap, and in-page anchor offset for the sticky nav.
(() => {
  'use strict';
  const burger = document.getElementById('nav-burger');
  const menu = document.getElementById('mobile-menu');
  const closeIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg>';
  const openIcon = burger ? burger.innerHTML : '';

  let isOpen = false;

  function toggle(open, restoreFocus = true) {
    if (!menu || !burger) return;
    isOpen = open;
    if (open) {
      menu.hidden = false;
      void menu.offsetHeight; // apply display before the slide-in transition starts
      menu.classList.add('open');
    } else {
      menu.classList.remove('open');
      setTimeout(() => { if (!isOpen) menu.hidden = true; }, 300);
    }
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    burger.innerHTML = open ? closeIcon : openIcon;
    document.body.classList.toggle('menu-open', open);
    if (open) { const first = menu.querySelector('a'); if (first) first.focus(); }
    else if (restoreFocus) burger.focus();
  }

  if (burger && menu) {
    burger.addEventListener('click', () => toggle(!isOpen));
    menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => toggle(false, false)));
    document.addEventListener('keydown', event => {
      if (!isOpen) return;
      if (event.key === 'Escape') { toggle(false); return; }
      if (event.key !== 'Tab') return;
      const items = [...menu.querySelectorAll('a'), burger];
      const first = items[0], last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
    matchMedia('(min-width: 981px)').addEventListener('change', event => {
      if (event.matches && isOpen) toggle(false, false);
    });
  }

  // Keep in-page anchors clear of the sticky pill nav.
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', event => {
      const id = link.getAttribute('href');
      if (id.length < 2) return;
      const target = document.getElementById(id.slice(1));
      if (!target) return;
      event.preventDefault();
      window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - 90, behavior: reduced.matches ? 'auto' : 'smooth' });
      history.pushState(null, '', id);
      if (target.tabIndex < 0 && !/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(target.tagName)) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    });
  });
})();
