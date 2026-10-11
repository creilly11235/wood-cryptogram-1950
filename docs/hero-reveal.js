/* The ciphertext at the top of the article stays in view while the opening
   scrolls beneath it, and decodes as the reader goes: the letters turn to
   their decoded values, regroup into words, and each word gains a gloss. */
(() => {
  'use strict';
  const figure = document.querySelector('.hero .cipher-row');
  const start = document.querySelector('.hero .reveal-start');
  if (!figure || !start) return;
  const hero = figure.closest('.hero');
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
  function update() {
    framePending = false;
    const top = parseFloat(getComputedStyle(figure).top) || 0;
    const scrolled = top - start.getBoundingClientRect().bottom;
    // The cipher can stay pinned until the opening has passed beneath it.
    const range = Math.max(1, hero.getBoundingClientRect().bottom - start.getBoundingClientRect().bottom - figure.offsetHeight);
    const progress = scrolled / range;
    figure.classList.toggle('is-stuck', scrolled > 0 && progress < 1);
    const stage = progress < .12 ? 0 : progress < .4 ? 1 : progress < .62 ? 2 : 3;
    if (figure.dataset.stage !== String(stage)) apply(stage);
  }
  function schedule() {
    if (framePending) return;
    framePending = true;
    requestAnimationFrame(update);
  }
  addEventListener('scroll', schedule, {passive: true});
  addEventListener('resize', schedule, {passive: true});
  document.fonts?.ready.then(schedule);
  figure.dataset.stage = '0';
  update();
})();
