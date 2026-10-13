/* The reader's own cipher: a message and a key passage, worked by Thouless's
   rule. Each distinct key word in turn is summed (A=1 to Z=26), reduced
   modulo 26 to a key letter, and that letter shifts one message letter
   (A no shift, B one place, and so on). The output refreshes as the reader
   types; the table below it matches the one that explains Wood's key. */
(() => {
  'use strict';

  const PRESETS = {
    hamlet: {
      lang: 'en',
      text: 'To be, or not to be, that is the question. Whether ’tis nobler in the mind to suffer the slings and arrows of outrageous fortune, or to take arms against a sea of troubles, and by opposing end them. To die, to sleep, no more, and by a sleep to say we end the heartache and the thousand natural shocks that flesh is heir to. ’Tis a consummation devoutly to be wished. To die, to sleep. To sleep, perchance to dream. Ay, there’s the rub, for in that sleep of death what dreams may come, when we have shuffled off this mortal coil, must give us pause. There’s the respect that makes calamity of so long life. For who would bear the whips and scorns of time, the oppressor’s wrong, the proud man’s contumely, the pangs of despised love, the law’s delay, the insolence of office, and the spurns that patient merit of the unworthy takes, when he himself might his quietus make with a bare bodkin? Who would fardels bear, to grunt and sweat under a weary life, but that the dread of something after death, the undiscovered country from whose bourn no traveller returns, puzzles the will, and makes us rather bear those ills we have than fly to others that we know not of? Thus conscience does make cowards of us all, and thus the native hue of resolution is sicklied o’er with the pale cast of thought, and enterprises of great pith and moment with this regard their currents turn awry, and lose the name of action.'
    },
    luther: {
      lang: 'de',
      text: 'Unser Vater in dem Himmel! Dein Name werde geheiligt. Dein Reich komme. Dein Wille geschehe auf Erden wie im Himmel. Unser täglich Brot gib uns heute. Und vergib uns unsere Schuld, wie wir unseren Schuldigern vergeben. Und führe uns nicht in Versuchung, sondern erlöse uns von dem Übel. Denn dein ist das Reich und die Kraft und die Herrlichkeit in Ewigkeit. Amen.'
    }
  };

  const letters = text => text.normalize('NFKD').toUpperCase().replace(/[^A-Z]/g, '');

  // Words as printed, each with its letters; the first occurrence of a
  // letter string is a key word and every later one is a repeat.
  function keyWords(passage) {
    const seen = new Set();
    const out = [];
    passage.split(/\s+/).forEach(raw => {
      const token = letters(raw);
      if (!token) return;
      const word = raw.replace(/^[^\p{L}\p{N}’'(]+|[^\p{L}\p{N}’')]+$/gu, '');
      const repeat = seen.has(token);
      seen.add(token);
      out.push({ word, token, repeat });
    });
    return out;
  }

  const keyLetter = sum => String.fromCharCode(65 + (sum - 1) % 26);
  const shiftOf = sum => (sum - 1) % 26;
  const sumOf = token => token.split('').reduce((total, letter) => total + letter.charCodeAt(0) - 64, 0);

  function encipher(message, passage) {
    const words = message.split(/\s+/).map(letters).filter(Boolean);
    const plain = words.join('');
    const all = keyWords(passage);
    const rows = [];
    let used = 0;
    for (const entry of all) {
      if (rows.length === plain.length) break;
      used += 1;
      if (entry.repeat) continue;
      const sum = sumOf(entry.token);
      const index = rows.length;
      const cipher = String.fromCharCode(65 + (plain.charCodeAt(index) - 65 + shiftOf(sum)) % 26);
      rows.push({ word: entry.word, sum, key: keyLetter(sum), plain: plain[index], cipher });
    }
    const distinct = all.filter(entry => !entry.repeat).length;
    return { words, plain, rows, passage: all.slice(0, used), distinct, short: rows.length < plain.length };
  }

  function card(letter, kind) {
    const span = document.createElement('span');
    span.className = kind ? 't ' + kind : 't';
    span.textContent = letter;
    return span;
  }

  function group(cards) {
    const grp = document.createElement('span');
    grp.className = 'grp';
    grp.append(...cards);
    return grp;
  }

  function token(letter, kind) {
    const run = document.createElement('span');
    run.className = 'cipher-run is-whole';
    run.append(card(letter, kind));
    const wrap = document.createElement('span');
    wrap.className = 'cipher-token is-tiled ' + kind;
    wrap.setAttribute('role', 'img');
    wrap.setAttribute('aria-label', letter);
    wrap.append(run);
    return wrap;
  }

  function fill(template, values) {
    return template.replace(/\{(\w+)\}/g, (match, name) => name in values ? values[name] : match);
  }

  window.TryCipher = function (section, labels) {
    const message = section.querySelector('#try-message');
    const preset = section.querySelector('#try-preset');
    const key = section.querySelector('#try-key');
    const plainOut = section.querySelector('.try-plain');
    const passageOut = section.querySelector('.try-passage');
    const cipherOut = section.querySelector('.try-cipher');
    const status = section.querySelector('.try-status');
    const body = section.querySelector('tbody');

    function applyPreset() {
      const chosen = PRESETS[preset.value];
      if (chosen) {
        key.value = chosen.text;
        key.lang = chosen.lang;
      } else {
        key.lang = document.documentElement.lang || 'en';
      }
    }

    function render() {
      const result = encipher(message.value, key.value);
      plainOut.replaceChildren(...result.words.map(word => group(word.split('').map(letter => card(letter, 'decoded')))));
      plainOut.setAttribute('aria-label', result.words.join(' '));

      passageOut.replaceChildren();
      result.passage.forEach((entry, index) => {
        const span = document.createElement('span');
        span.className = entry.repeat ? 'try-word is-repeat' : 'try-word';
        span.textContent = entry.word;
        if (index) passageOut.append(document.createTextNode(' '));
        passageOut.append(span);
      });
      passageOut.lang = key.lang;

      const cipher = result.rows.map(row => row.cipher).join('');
      const groups = [];
      for (let index = 0; index < result.plain.length; index += 5) {
        const cards = [];
        for (let offset = index; offset < Math.min(index + 5, result.plain.length); offset += 1) {
          cards.push(offset < cipher.length ? card(cipher[offset], 'encoded') : card('', ''));
        }
        groups.push(group(cards));
      }
      cipherOut.replaceChildren(...groups);
      cipherOut.setAttribute('aria-label', cipher.replace(/(.{5})/g, '$1 ').trim());

      body.replaceChildren(...result.rows.map((row, index) => {
        const tr = document.createElement('tr');
        [index + 1, row.word, row.sum, row.key].forEach(value => {
          const td = document.createElement('td');
          td.textContent = value;
          tr.append(td);
        });
        const td = document.createElement('td');
        td.append(token(row.plain, 'decoded'), document.createTextNode(' → '), token(row.cipher, 'encoded'));
        tr.append(td);
        return tr;
      }));

      let note = '';
      if (!result.plain.length) note = labels.noMessage;
      else if (!result.distinct) note = labels.noKey;
      else if (result.short) note = fill(labels.shortKey, { words: result.distinct, letters: result.plain.length });
      status.textContent = note;
      section.classList.toggle('is-short', result.short && result.distinct > 0);
    }

    preset.addEventListener('change', () => { applyPreset(); render(); });
    key.addEventListener('input', () => {
      if (PRESETS[preset.value] && key.value !== PRESETS[preset.value].text) preset.value = 'own';
      render();
    });
    message.addEventListener('input', render);

    if (!PRESETS[preset.value] || !key.value) applyPreset();
    render();
    return { encipher, render };
  };
})();
