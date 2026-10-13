/* The reader's own cipher, built in three steps inside a panel that fills
   the screen the way the article's graphics do, with the button that moves
   the reader on at the right of its foot and Back or Start again at the
   left. First the message becomes letter cards. Then every letter gets a
   key word, from a chosen passage (repeats skipped, as Thouless's rule
   says) or typed by the reader one word per letter. On generate each word
   turns into its key letter (A=1 to Z=26, summed and reduced modulo 26),
   the card flips to the cipher letter, and the cards slide into groups of
   five below the key phrase. Done scrolls on to the key table. */
(() => {
  'use strict';

  const PRESETS = {
    hamlet: { lang: 'en', text: 'To be, or not to be, that is the question. Whether ’tis nobler in the mind to suffer the slings and arrows of outrageous fortune, or to take arms against a sea of troubles, and by opposing end them. To die, to sleep, no more, and by a sleep to say we end the heartache and the thousand natural shocks that flesh is heir to. ’Tis a consummation devoutly to be wished. To die, to sleep. To sleep, perchance to dream. Ay, there’s the rub, for in that sleep of death what dreams may come, when we have shuffled off this mortal coil, must give us pause. There’s the respect that makes calamity of so long life. For who would bear the whips and scorns of time, the oppressor’s wrong, the proud man’s contumely, the pangs of despised love, the law’s delay, the insolence of office, and the spurns that patient merit of the unworthy takes, when he himself might his quietus make with a bare bodkin? Who would fardels bear, to grunt and sweat under a weary life, but that the dread of something after death, the undiscovered country from whose bourn no traveller returns, puzzles the will, and makes us rather bear those ills we have than fly to others that we know not of? Thus conscience does make cowards of us all, and thus the native hue of resolution is sicklied o’er with the pale cast of thought, and enterprises of great pith and moment with this regard their currents turn awry, and lose the name of action.' },
    luther: { lang: 'de', text: 'Unser Vater in dem Himmel! Dein Name werde geheiligt. Dein Reich komme. Dein Wille geschehe auf Erden wie im Himmel. Unser täglich Brot gib uns heute. Und vergib uns unsere Schuld, wie wir unseren Schuldigern vergeben. Und führe uns nicht in Versuchung, sondern erlöse uns von dem Übel. Denn dein ist das Reich und die Kraft und die Herrlichkeit in Ewigkeit. Amen.' },
    gettysburg: { lang: 'en', text: 'Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal. Now we are engaged in a great civil war, testing whether that nation, or any nation so conceived and so dedicated, can long endure. We are met on a great battlefield of that war. We have come to dedicate a portion of that field, as a final resting place for those who here gave their lives that that nation might live. It is altogether fitting and proper that we should do this. But, in a larger sense, we can not dedicate, we can not consecrate, we can not hallow this ground. The brave men, living and dead, who struggled here, have consecrated it, far above our poor power to add or detract. The world will little note, nor long remember what we say here, but it can never forget what they did here. It is for us the living, rather, to be dedicated here to the unfinished work which they who fought here have thus far so nobly advanced. It is rather for us to be here dedicated to the great task remaining before us, that from these honored dead we take increased devotion to that cause for which they gave the last full measure of devotion, that we here highly resolve that these dead shall not have died in vain, that this nation, under God, shall have a new birth of freedom, and that government of the people, by the people, for the people, shall not perish from the earth.' },
    genesis: { lang: 'en', text: 'In the beginning God created the heaven and the earth. And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters. And God said, Let there be light: and there was light. And God saw the light, that it was good: and God divided the light from the darkness. And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day. And God said, Let there be a firmament in the midst of the waters, and let it divide the waters from the waters. And God made the firmament, and divided the waters which were under the firmament from the waters which were above the firmament: and it was so. And God called the firmament Heaven. And the evening and the morning were the second day.' },
    dickens: { lang: 'en', text: 'It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness, it was the spring of hope, it was the winter of despair, we had everything before us, we had nothing before us, we were all going direct to Heaven, we were all going direct the other way, in short, the period was so far like the present period, that some of its noisiest authorities insisted on its being received, for good or for evil, in the superlative degree of comparison only.' },
    sonnet: { lang: 'en', text: 'Shall I compare thee to a summer’s day? Thou art more lovely and more temperate. Rough winds do shake the darling buds of May, and summer’s lease hath all too short a date. Sometime too hot the eye of heaven shines, and often is his gold complexion dimmed, and every fair from fair sometime declines, by chance, or nature’s changing course untrimmed. But thy eternal summer shall not fade, nor lose possession of that fair thou ow’st, nor shall death brag thou wander’st in his shade, when in eternal lines to time thou grow’st. So long as men can breathe or eyes can see, so long lives this, and this gives life to thee.' },
    declaration: { lang: 'en', text: 'When in the Course of human events, it becomes necessary for one people to dissolve the political bands which have connected them with another, and to assume among the powers of the earth, the separate and equal station to which the Laws of Nature and of Nature’s God entitle them, a decent respect to the opinions of mankind requires that they should declare the causes which impel them to the separation. We hold these truths to be self evident, that all men are created equal, that they are endowed by their Creator with certain unalienable Rights, that among these are Life, Liberty and the pursuit of Happiness.' }
  };

  const letters = text => text.normalize('NFKD').toUpperCase().replace(/[^A-Z]/g, '');
  const trim = raw => raw.replace(/^[^\p{L}\p{N}’'(]+|[^\p{L}\p{N}’')]+$/gu, '');
  const sumOf = token => token.split('').reduce((total, letter) => total + letter.charCodeAt(0) - 64, 0);
  const keyLetter = sum => String.fromCharCode(65 + (sum - 1) % 26);
  const shiftOf = sum => (sum - 1) % 26;
  const encipherLetter = (plain, sum) => String.fromCharCode(65 + (plain.charCodeAt(0) - 65 + shiftOf(sum)) % 26);

  // Words as printed, each with its letters; the first occurrence of a
  // letter string is a key word and every later one is a repeat.
  function passageWords(passage) {
    const seen = new Set();
    const out = [];
    passage.split(/\s+/).forEach(raw => {
      const token = letters(raw);
      if (!token) return;
      const repeat = seen.has(token);
      seen.add(token);
      out.push({ word: trim(raw), token, repeat });
    });
    return out;
  }

  // The words a passage supplies for a message of the given length, and how
  // much of the passage that took.
  function keyFromPassage(passage, length) {
    const all = passageWords(passage);
    const words = [];
    let used = 0;
    for (const entry of all) {
      if (words.length === length) break;
      used += 1;
      if (!entry.repeat) words.push(entry.word);
    }
    return { words, excerpt: all.slice(0, used), distinct: all.filter(entry => !entry.repeat).length };
  }

  function rowsFor(plain, words) {
    return words.map((word, index) => {
      const sum = sumOf(letters(word));
      return { word, sum, key: keyLetter(sum), plain: plain[index], cipher: encipherLetter(plain[index], sum) };
    });
  }

  function encipher(message, passage) {
    const words = message.split(/\s+/).map(letters).filter(Boolean);
    const plain = words.join('');
    const key = keyFromPassage(passage, plain.length);
    const rows = rowsFor(plain, key.words);
    return { words, plain, rows, passage: key.excerpt, distinct: key.distinct, short: rows.length < plain.length };
  }

  const node = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  };
  const card = (letter, kind) => node('span', kind ? 't ' + kind : 't', letter);
  const token = (letter, kind) => {
    const run = node('span', 'cipher-run is-whole');
    run.append(card(letter, kind));
    const wrap = node('span', 'cipher-token is-tiled ' + kind);
    wrap.setAttribute('role', 'img');
    wrap.setAttribute('aria-label', letter);
    wrap.append(run);
    return wrap;
  };
  const fill = (template, values) => template.replace(/\{(\w+)\}/g, (match, name) => name in values ? values[name] : match);
  const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

  window.TryCipher = function (section, labels) {
    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const panel = section.querySelector('.try-panel');
    const steps = {
      message: section.querySelector('[data-step="message"]'),
      key: section.querySelector('[data-step="key"]'),
      cipher: section.querySelector('[data-step="cipher"]')
    };
    const buttons = {
      message: section.querySelector('[data-act="message"]'),
      key: section.querySelector('[data-act="generate"]'),
      cipher: section.querySelector('[data-act="done"]')
    };
    const back = section.querySelector('[data-act="back"]');
    const restart = section.querySelector('[data-act="restart"]');
    const message = section.querySelector('#try-message');
    const preset = section.querySelector('#try-preset');
    const plainOut = steps.message.querySelector('.try-plain');
    const passageOut = steps.key.querySelector('.try-passage');
    const pairsOut = steps.key.querySelector('.try-pairs');
    const cipherOut = steps.cipher.querySelector('.try-cipher');
    const table = section.querySelector('.try-table');
    const body = table.querySelector('tbody');
    const status = section.querySelector('.try-status');
    const state = { words: [], plain: '', keyWords: [], pairs: [], busy: false };
    let run = 0; // bumps on every edit so an animation in flight stops

    // The foot of the panel carries the primary button for the current stage
    // at the right, with Back at the left while the key is chosen and Start
    // again once the cipher is made.
    function stage(name) {
      Object.keys(buttons).forEach(key => { buttons[key].hidden = key !== name; });
      back.hidden = name !== 'key';
      restart.hidden = name !== 'cipher';
      panel.dataset.stage = name;
    }
    // A panel taller than the screen scrolls up until its foot reaches the
    // bottom of the screen, then locks there the way the graphics do.
    function fit() {
      panel.style.setProperty('--try-top', Math.min(0, window.innerHeight - panel.offsetHeight) + 'px');
    }
    if (typeof ResizeObserver === 'function') new ResizeObserver(fit).observe(panel);
    window.addEventListener('resize', fit);
    fit();
    function show(step, visible) {
      const el = steps[step];
      if (!visible) { el.hidden = true; el.classList.remove('is-entering'); return; }
      if (!el.hidden) return;
      el.hidden = false;
      if (reduced) return;
      el.classList.add('is-entering');
      requestAnimationFrame(() => requestAnimationFrame(() => el.classList.remove('is-entering')));
    }
    function lock(step, locked) {
      steps[step].classList.toggle('is-locked', locked);
    }
    function reveal(items, gap) {
      if (reduced) return Promise.resolve();
      items.forEach((item, index) => {
        item.animate([{ opacity: 0, transform: 'translateY(6px)' }, { opacity: 1, transform: 'none' }], { duration: 320, delay: index * gap, easing: 'ease-out', fill: 'backwards' });
      });
      return wait(items.length ? (items.length - 1) * gap + 320 : 0);
    }
    function fade(items, ms) {
      if (reduced) return Promise.resolve();
      items.forEach(item => item.animate([{ opacity: 1 }, { opacity: 0 }], { duration: ms, fill: 'forwards' }));
      return wait(ms);
    }
    // A card that shows the message letter and flips to the cipher letter.
    function flipCard(letter) {
      const flip = node('span', 'try-card');
      const turn = node('span', 'try-card-turn');
      turn.append(node('span', 't decoded try-face', letter), node('span', 't encoded try-face try-back', ''));
      flip.append(turn);
      return flip;
    }
    const hold = section.querySelector('.try-hold');
    function settle() {
      // The panel fills the screen; the heading above it scrolls away. Its
      // place in the flow is read from the hold below it, since the panel's
      // own box is pinned while the page scrolls on.
      const natural = hold.getBoundingClientRect().top - panel.offsetHeight;
      if (Math.abs(natural) > 2) window.scrollBy({ top: natural, behavior: reduced ? 'auto' : 'smooth' });
    }

    // Step 1: the message becomes cards, one letter each, grouped by word.
    function setMessage() {
      const words = message.value.split(/\s+/).map(letters).filter(Boolean);
      if (!words.length) { status.textContent = labels.noMessage; message.focus(); return; }
      status.textContent = '';
      state.words = words;
      state.plain = words.join('');
      plainOut.replaceChildren(...words.map(word => {
        const group = node('span', 'grp');
        group.append(...word.split('').map(letter => card(letter, 'decoded')));
        return group;
      }));
      plainOut.setAttribute('aria-label', words.join(' '));
      plainOut.hidden = false;
      lock('message', true);
      message.blur();
      settle();
      reveal([...plainOut.querySelectorAll('.t')], 40).then(() => {
        show('key', true);
        stage('key');
        renderKey();
      });
    }

    // Step 2: one key word under every letter, from the passage or typed.
    function renderKey() {
      run += 1;
      const chosen = PRESETS[preset.value];
      const length = state.plain.length;
      let words = [];
      passageOut.replaceChildren();
      passageOut.hidden = true;
      pairsOut.hidden = false;
      status.textContent = '';
      buttons.key.disabled = false;
      if (chosen) {
        const key = keyFromPassage(chosen.text, length);
        words = key.words;
        key.excerpt.forEach((entry, index) => {
          if (index) passageOut.append(document.createTextNode(' '));
          passageOut.append(node('span', entry.repeat ? 'try-word-src is-repeat' : 'try-word-src', entry.word));
        });
        passageOut.lang = chosen.lang;
        passageOut.hidden = false;
        if (words.length < length) {
          status.textContent = fill(labels.shortKey, { words: key.distinct, letters: length });
          buttons.key.disabled = true;
        }
      }
      state.pairs = [];
      let index = 0;
      pairsOut.replaceChildren(...state.words.map(word => {
        const group = node('span', 'try-group');
        word.split('').forEach(letter => {
          const pair = node('span', 'try-pair');
          const flip = flipCard(letter);
          pair.append(flip);
          let input = null;
          if (chosen) {
            pair.append(node('span', 'try-word', words[index] || ''));
          } else {
            input = node('input', 'try-word-input');
            input.type = 'text';
            input.autocomplete = 'off';
            input.spellcheck = false;
            input.setAttribute('autocapitalize', 'none');
            input.setAttribute('aria-label', fill(labels.wordFor, { n: index + 1, letter }));
            if (state.keyWords[index]) input.value = state.keyWords[index];
            pair.append(input);
          }
          state.pairs.push({ pair, flip, letter, input, back: flip.firstChild.lastChild });
          group.append(pair);
          index += 1;
        });
        return group;
      }));
      pairsOut.classList.toggle('is-custom', !chosen);
      if (chosen) {
        state.keyWords = words;
        reveal(state.pairs.map(item => item.pair), 50);
      } else {
        validateCustom();
      }
    }

    // Typed words: every letter needs one, and no word may repeat. A phrase
    // pasted into one field spreads over the fields that follow it.
    function validateCustom() {
      const seen = new Map();
      let missing = false, duplicate = false;
      state.keyWords = state.pairs.map(item => item.input ? item.input.value.trim() : '');
      state.pairs.forEach((item, index) => {
        const tok = letters(state.keyWords[index]);
        let bad = false;
        if (!tok) missing = true;
        else if (seen.has(tok)) { duplicate = true; bad = true; item.input.classList.add('is-duplicate'); seen.get(tok).classList.add('is-duplicate'); }
        else seen.set(tok, item.input);
        if (!bad) item.input.classList.remove('is-duplicate');
      });
      status.textContent = duplicate ? labels.repeatWord : '';
      buttons.key.disabled = missing || duplicate;
      return !(missing || duplicate);
    }
    function spread(index) {
      const input = state.pairs[index].input;
      const parts = input.value.trim().split(/\s+/).filter(Boolean);
      if (parts.length < 2) return;
      parts.forEach((part, offset) => {
        const target = state.pairs[index + offset];
        if (target && target.input) target.input.value = part;
      });
      const next = state.pairs[Math.min(index + parts.length, state.pairs.length - 1)];
      if (next && next.input) next.input.focus();
    }

    // Step 3: the key words stay as a phrase, each word under its card becomes
    // its key letter and the card flips to the cipher letter, one pair after
    // another, then the key letters fade and the cards slide into fives.
    async function generateCipher() {
      if (state.busy) return;
      if (!PRESETS[preset.value] && !validateCustom()) { if (!status.textContent) status.textContent = labels.missingWords; return; }
      state.busy = true;
      run += 1;
      const ticket = run;
      const rows = rowsFor(state.plain, state.keyWords);
      lock('key', true);
      stage('none');
      settle();
      if (!PRESETS[preset.value]) {
        // Typed words read as a phrase of their own above the cards.
        passageOut.replaceChildren();
        rows.forEach((row, index) => {
          if (index) passageOut.append(document.createTextNode(' '));
          passageOut.append(node('span', 'try-word-src', row.word));
        });
        passageOut.removeAttribute('lang');
        passageOut.hidden = false;
      }
      pairsOut.querySelectorAll('.try-word-input').forEach((input, index) => {
        input.replaceWith(node('span', 'try-word', rows[index].word));
      });
      const pairs = state.pairs;
      const gap = reduced ? 0 : 130;
      const turn = (item, row) => {
        const word = item.pair.querySelector('.try-word');
        item.back.textContent = row.cipher;
        const swap = () => { word.textContent = row.key; word.classList.add('is-key'); };
        if (reduced) { swap(); item.pair.classList.add('is-flipped'); return; }
        word.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 160, fill: 'forwards' }).finished.then(() => {
          if (run !== ticket) return;
          swap();
          word.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 220, fill: 'forwards' });
          item.pair.classList.add('is-flipped');
        });
      };
      for (let index = 0; index < rows.length; index += 1) {
        if (run !== ticket) { state.busy = false; return; }
        turn(pairs[index], rows[index]);
        if (gap) await wait(gap);
      }
      if (run !== ticket) { state.busy = false; return; }
      if (!reduced) await wait(700);
      await fade([...pairsOut.querySelectorAll('.try-word')], 300);
      if (run !== ticket) { state.busy = false; return; }
      // The cards slide from their pairs into groups of five under the
      // cipher's own label; the pairs give way at the same moment.
      const cipher = rows.map(row => row.cipher).join('');
      const first = pairs.map(item => item.flip.getBoundingClientRect());
      const groups = [];
      for (let index = 0; index < cipher.length; index += 5) {
        const group = node('span', 'grp');
        group.append(...cipher.slice(index, index + 5).split('').map(letter => card(letter, 'encoded')));
        groups.push(group);
      }
      cipherOut.replaceChildren(...groups);
      cipherOut.setAttribute('aria-label', cipher.replace(/(.{5})/g, '$1 ').trim());
      body.replaceChildren(...rows.map((row, index) => {
        const tr = node('tr');
        [index + 1, row.word, row.sum, row.key].forEach(value => tr.append(node('td', '', String(value))));
        const td = node('td');
        td.append(token(row.plain, 'decoded'), document.createTextNode(' → '), token(row.cipher, 'encoded'));
        tr.append(td);
        return tr;
      }));
      steps.cipher.hidden = false;
      pairsOut.hidden = true;
      table.hidden = false;
      if (!reduced) {
        const cards = [...cipherOut.querySelectorAll('.t')];
        const label = steps.cipher.querySelector('.try-label');
        cards.forEach((item, index) => {
          const last = item.getBoundingClientRect();
          const dx = first[index].left - last.left, dy = first[index].top - last.top;
          item.animate([{ transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'none' }], { duration: 650, delay: index * 12, easing: 'cubic-bezier(.2,.7,.2,1)', fill: 'backwards' });
        });
        label.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 400, delay: 350, fill: 'backwards' });
        await wait(650 + cards.length * 12);
      }
      if (run !== ticket) { state.busy = false; return; }
      stage('cipher');
      if (panel.offsetHeight <= window.innerHeight) settle();
      state.busy = false;
    }

    function editMessage() {
      run += 1; state.busy = false;
      show('cipher', false); show('key', false);
      table.hidden = true;
      lock('key', false);
      lock('message', false);
      plainOut.hidden = true;
      status.textContent = '';
      stage('message');
      message.focus();
    }
    // Done moves on to the key table, which rises over the panel.
    function done() {
      table.scrollIntoView({ block: 'start', behavior: reduced ? 'auto' : 'smooth' });
    }

    buttons.message.addEventListener('click', setMessage);
    message.addEventListener('keydown', event => { if (event.key === 'Enter') { event.preventDefault(); setMessage(); } });
    back.addEventListener('click', editMessage);
    preset.addEventListener('change', () => { state.keyWords = []; renderKey(); });
    pairsOut.addEventListener('input', event => {
      const index = state.pairs.findIndex(item => item.input === event.target);
      if (index < 0) return;
      spread(index);
      validateCustom();
    });
    pairsOut.addEventListener('keydown', event => {
      if (event.key !== 'Enter' || !event.target.classList.contains('try-word-input')) return;
      event.preventDefault();
      const index = state.pairs.findIndex(item => item.input === event.target);
      const next = state.pairs[index + 1];
      if (next && next.input) next.input.focus(); else buttons.key.focus();
    });
    buttons.key.addEventListener('click', generateCipher);
    buttons.cipher.addEventListener('click', done);
    restart.addEventListener('click', () => { state.keyWords = []; editMessage(); });
    stage('message');

    return { encipher, setMessage, generateCipher };
  };
  window.TryCipher.encipher = encipher;
})();
