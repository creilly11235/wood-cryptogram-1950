/* The ciphertext at the top of the article pins to the middle of the screen
   and decodes as the reader scrolls: the letters turn to their decoded
   values, regroup into words, and each word gains a gloss. Then it lets go
   and the opening continues. */
(() => {
  'use strict';
  const figure = document.querySelector('.hero .cipher-row');
  const track = figure && figure.closest('.reveal-track');
  if (!track) return;
  const line = figure.querySelector('.line');
  const tiles = [...line.querySelectorAll('.t')];
  const cipher = tiles.map(tile => tile.textContent);
  const words = (figure.dataset.message || '').split(' ').filter(Boolean);
  const plain = words.join('');
  if (plain.length !== tiles.length) return;
  const glosses = [...figure.querySelectorAll('.hero-gloss li')].map(item => item.textContent);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const animate = () => !reduced.matches && typeof tiles[0].animate === 'function';
  const timers = new Set();
  let decoded = false, inWords = false, framePending = false;

  function node(className, text) {
    const el = document.createElement('div');
    el.className = className;
    if (text) el.textContent = text;
    return el;
  }
  // Every group, in either mode, leaves the same room beneath its tiles for a
  // gloss, so the figure keeps one height and the page below never shifts.
  function group(from, count, gloss) {
    const wrap = node('word'), tiles5 = node('grp');
    tiles.slice(from, from + count).forEach(tile => tiles5.append(tile));
    wrap.append(tiles5);
    if (gloss !== undefined) {
      const label = document.createElement('small');
      label.className = 'gloss';
      label.textContent = gloss;
      wrap.append(label);
    }
    return wrap;
  }
  // Regroup the tiles, then slide each one from where it was to where it is.
  function regroup(toWords) {
    const before = tiles.map(tile => tile.getBoundingClientRect());
    line.replaceChildren();
    if (toWords) {
      let at = 0;
      words.forEach((word, i) => { line.append(group(at, word.length, glosses[i] || '')); at += word.length; });
    } else {
      const groups = [];
      for (let i = 0; i < tiles.length; i += 5) groups.push(group(i, 5));
      // The short last group stays beside the one before it, so it never wraps alone.
      const tail = node('tail');
      tail.append(...groups.splice(-2));
      line.append(...groups, tail);
    }
    if (!animate()) return;
    tiles.forEach((tile, i) => {
      const after = tile.getBoundingClientRect();
      const dx = before[i].left - after.left, dy = before[i].top - after.top;
      if (dx || dy) tile.animate([{transform: `translate(${dx}px, ${dy}px)`}, {transform: 'none'}], {duration: 650, easing: 'cubic-bezier(.2, .7, .2, 1)'});
    });
  }
  // Turn each tile over to show its decoded letter, one after another.
  function turn(toPlain) {
    timers.forEach(clearTimeout);
    timers.clear();
    tiles.forEach((tile, i) => {
      const show = () => {
        tile.textContent = toPlain ? plain[i] : cipher[i];
        tile.className = 't ' + (toPlain ? 'decoded' : 'encoded');
      };
      if (!animate()) { show(); return; }
      tile.animate([{transform: 'scaleX(1)'}, {transform: 'scaleX(0)', offset: .5}, {transform: 'scaleX(1)'}], {duration: 360, delay: i * 50, easing: 'ease-in-out'});
      timers.add(setTimeout(show, i * 50 + 180));
    });
  }
  function apply(stage) {
    if ((stage >= 1) !== decoded) { decoded = stage >= 1; turn(decoded); }
    if ((stage >= 2) !== inWords) { inWords = stage >= 2; regroup(inWords); }
    figure.dataset.stage = String(stage);
  }
  // The row sticks centred on the screen, so the stylesheet needs its height.
  // When the page opens with the row above that line it is held there from
  // the start, and the hold beneath it grows by the same distance so the
  // reveal still takes a full hold of scrolling.
  function measure() {
    figure.style.setProperty('--hero-h', figure.offsetHeight + 'px');
    const top = parseFloat(getComputedStyle(figure).top) || 0;
    const trackTop = track.getBoundingClientRect().top + scrollY;
    track.style.setProperty('--hero-extra', Math.max(0, top - trackTop) + 'px');
  }
  // How far the row has been held before any scrolling, if the page opens
  // with it above its sticking line.
  function held(top, box) {
    return Math.max(0, top - (box.top + scrollY));
  }
  function update() {
    framePending = false;
    const top = parseFloat(getComputedStyle(figure).top) || 0;
    const box = track.getBoundingClientRect();
    const start = held(top, box);
    const scrolled = top - box.top - start;
    // The cipher stays pinned through the hold beneath it, and the reveal
    // finishes before the opening's text arrives.
    const range = Math.max(1, box.height - figure.offsetHeight - start);
    const progress = scrolled / range;
    figure.classList.toggle('is-stuck', scrolled > 0 && progress < 1);
    const stage = progress < .08 ? 0 : progress < .42 ? 1 : progress < .66 ? 2 : 3;
    if (figure.dataset.stage !== String(stage)) apply(stage);
  }
  function schedule() {
    if (framePending) return;
    framePending = true;
    requestAnimationFrame(update);
  }
  addEventListener('scroll', schedule, {passive: true});
  addEventListener('resize', () => { measure(); schedule(); }, {passive: true});
  document.fonts?.ready.then(() => { measure(); schedule(); });
  figure.dataset.stage = '0';
  measure();
  update();
})();
