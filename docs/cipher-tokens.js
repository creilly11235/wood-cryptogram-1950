/* Inline cipher text in the prose is set one letter per card, the same cards
   the graphics use, so a quoted ciphertext reads as the thing it refers to. */
(() => {
  'use strict';
  function tile(token) {
    const kind = token.classList.contains('decoded') ? 'decoded' : 'encoded';
    const text = token.textContent;
    const fragment = document.createDocumentFragment();
    let run = null;
    for (const character of text) {
      if (/[\p{L}\p{N}]/u.test(character)) {
        // A run of letters stays on one line, so groups never split mid-word.
        if (!run) {
          run = document.createElement('span');
          run.className = 'cipher-run';
          fragment.append(run);
        }
        const card = document.createElement('span');
        card.className = 't ' + kind;
        card.textContent = character;
        run.append(card);
      } else {
        run = null;
        if (character === ' ') {
          // A fixed gap between groups, so word spacing does not depend on the prose font.
          const gap = document.createElement('span');
          gap.className = 'cipher-gap';
          gap.textContent = ' ';
          fragment.append(gap);
        } else {
          fragment.append(document.createTextNode(character));
        }
      }
    }
    // Short runs (cipher groups, words) stay whole; a long unbroken string may wrap.
    fragment.querySelectorAll('.cipher-run').forEach(run => { if (run.childElementCount <= 6) run.classList.add('is-whole'); });
    token.setAttribute('role', 'img');
    token.setAttribute('aria-label', text);
    token.replaceChildren(fragment);
    token.classList.add('is-tiled');
  }
  document.querySelectorAll('.cipher-token').forEach(tile);
  // The try-it section builds its key table with the same tiler.
  window.tileCipherToken = tile;
})();
