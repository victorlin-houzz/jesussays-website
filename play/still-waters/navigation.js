(() => {
  'use strict';
  const burger = document.getElementById('nav-burger');
  const menu = document.getElementById('mobile-menu');
  function toggle(open) {
    menu.hidden = !open;
    menu.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    document.body.classList.toggle('menu-open', open);
    (open ? menu.querySelector('a') : burger).focus();
  }
  burger.addEventListener('click', () => toggle(menu.hidden));
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => toggle(false)));
  document.addEventListener('keydown', event => {
    if (menu.hidden) return;
    if (event.key === 'Escape') toggle(false);
    if (event.key !== 'Tab') return;
    const links = [...menu.querySelectorAll('a'), burger];
    const first = links[0], last = links[links.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  matchMedia('(min-width: 981px)').addEventListener('change', event => {
    if (event.matches && !menu.hidden) toggle(false);
  });
})();
