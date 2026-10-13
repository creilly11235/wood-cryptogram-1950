/* The article controls the ten steps; buttons also let a reader explore them.
   The example is Thouless's own from 1948, THERE IS NO DEATH enciphered with
   the opening of Hamlet's soliloquy, worked in the enciphering direction.
   Animation is presentational. Every step has a complete reduced-motion view. */
(() => {
  'use strict';

  const DEFAULT_LABELS = {
    label: 'How a message becomes a cipher',
    encoded: 'Cipher',
    decoded: 'Message',
    stages: [
      'The 14-letter message',
      'The key is a passage from a book',
      'Repeated words are skipped',
      'One key word for every letter',
      'Start with T and To',
      'Add the letters in To',
      'Use I to shift T forward 8 places',
      'The first cipher letter is B',
      'Repeat for all 14 letters',
      'Message, key and cipher together'
    ],
    previous: 'Previous',
    next: 'Next',
    replay: 'Replay',
    keyReduction: '35 − 26 = 9 → I',
    shiftKey: 'I means a shift of 8',
    shift: 'Forward 8',
    firstDecoded: 'The ciphertext begins',
    step: 'Step',
    keyWord: 'key word',
    encryptedMessage: 'The message',
    keyLabel: 'The key',
    decodedMessage: 'The cipher',
    swipeHint: 'Scroll to explore · or use the buttons'
  };

  class CipherWalkthrough {
    constructor(host, options = {}) {
      this.host = host;
      // The message as spoken, the key passage as printed, and the cipher
      // Thouless's arithmetic gives (his printed version ends in B, a slip).
      this.messageWords = options.messageWords || ['THERE', 'IS', 'NO', 'DEATH'];
      this.passage = options.passage || [
        'To', 'be,', 'or', 'not', 'to', 'be,', 'that', 'is', 'the', 'question.',
        'Whether', '’tis', 'nobler', 'in', 'the', 'mind', 'to', 'suffer'
      ];
      this.passageLang = options.passageLang || 'en';
      this.groups = options.groups || ['BNKNA', 'JYCWY', 'RWGD'];
      this.pt = this.messageWords.join('');
      this.ct = this.groups.join('');
      const seen = new Set();
      this.keyWords = [];
      this.passage.forEach(word => {
        const token = this.letters(word);
        if (!seen.has(token)) this.keyWords.push(word.replace(/[.,;!?]+$/g, ''));
        seen.add(token);
      });
      this.words = this.keyWords.slice(0, this.pt.length);
      if (this.ct.length !== this.pt.length || this.words.length !== this.pt.length) {
        throw new Error('CipherWalkthrough needs one key word and one cipher letter per message letter.');
      }
      // The first pair, worked in full on screen.
      const first = this.letters(this.words[0]);
      this.firstTerms = first.split('').map(letter => [letter, letter.charCodeAt(0) - 64]);
      this.firstSum = this.firstTerms.reduce((total, term) => total + term[1], 0);
      this.firstKey = String.fromCharCode(65 + (this.firstSum - 1) % 26);
      this.firstShift = (this.firstSum - 1) % 26;
      this.firstPlain = this.pt[0];
      this.firstCipher = this.ct[0];
      if (String.fromCharCode(65 + (this.firstPlain.charCodeAt(0) - 65 + this.firstShift) % 26) !== this.firstCipher) {
        throw new Error('CipherWalkthrough: the first cipher letter does not follow from the key word.');
      }
      this.labels = Object.assign({}, DEFAULT_LABELS, options.labels || {});
      this.reduced = Boolean(options.reduced);
      this.onStageChange = options.onStageChange;
      this.onNavigate = options.onNavigate;
      this.stage = -1;
      this.paused = false;
      this.destroyed = false;
      this.animations = new Set();
      this.timers = new Set();
      this.ghosts = new Set();
      this.build();
      this.go(0);
      // A resized scene invalidates the flight paths between the old cards
      // and the reading. Finish cleanly rather than leaving letters adrift.
      this.lastSceneSize = null;
      this.resizeObserver = new ResizeObserver(() => {
        const rect = this.scene.getBoundingClientRect();
        const size = [rect.width, rect.height];
        if (this.lastSceneSize && size.some((value, index) => Math.abs(value - this.lastSceneSize[index]) > 1)) {
          if (this.stage === 8 && ['moving', 'revealing'].includes(this.root.dataset.finale)) {
            this.cancel();
            this.settleMessage();
          }
        }
        this.lastSceneSize = size;
      });
      this.resizeObserver.observe(this.scene);
    }

    letters(word) {
      return word.normalize('NFKD').toUpperCase().replace(/[^A-Z]/g, '');
    }

    node(tag, className, text) {
      const element = document.createElement(tag);
      if (className) element.className = className;
      if (text !== undefined) element.textContent = text;
      return element;
    }

    build() {
      const label = this.labels;
      this.root = this.node('div', 'cw');
      this.root.setAttribute('role', 'group');
      this.root.setAttribute('aria-label', label.label);
      const header = this.node('div', 'cw-head');
      const legend = this.node('div', 'cw-legend');
      ['encoded', 'decoded'].forEach(state => {
        const item = this.node('span', 'cw-legend-item');
        item.append(this.node('i', 'cw-swatch ' + state), document.createTextNode(label[state]));
        legend.append(item);
      });
      header.append(legend);
      this.scene = this.node('div', 'cw-scene');
      this.source = this.node('div', 'cw-source');
      this.source.setAttribute('role', 'img');
      this.source.setAttribute('aria-label', label.decoded + ': ' + this.messageWords.join(' '));
      const sourceGrid = this.node('div', 'cw-source-grid');
      sourceGrid.setAttribute('aria-hidden', 'true');
      this.sourceLetters = [];
      this.messageWords.forEach(word => {
        const group = this.node('span', 'cw-source-word');
        word.split('').forEach(letter => {
          const card = this.node('span', 'cw-source-letter decoded', letter);
          this.sourceLetters.push(card);
          group.append(card);
        });
        sourceGrid.append(group);
      });
      this.source.append(this.node('div', 'cw-scene-label', label.encryptedMessage), sourceGrid);

      this.keyphrase = this.node('div', 'cw-keyphrase');
      this.prayer = this.node('div', 'cw-prayer');
      this.prayer.lang = this.passageLang;
      this.prayer.setAttribute('translate', 'no');
      const seen = new Set();
      this.prayerUnique = [];
      this.prayerRepeats = [];
      this.passage.forEach((word, index) => {
        if (index) this.prayer.append(document.createTextNode(' '));
        const token = this.letters(word);
        const repeated = seen.has(token);
        const span = this.node('span', 'cw-prayer-word' + (repeated ? ' is-repeat' : ''), word);
        (repeated ? this.prayerRepeats : this.prayerUnique).push(span);
        this.prayer.append(span);
        seen.add(token);
      });
      this.prayer.append(document.createTextNode(' …'));
      this.keyphrase.append(this.node('div', 'cw-scene-label', label.keyLabel), this.prayer);

      this.grid = this.node('div', 'cw-grid');
      this.grid.setAttribute('role', 'list');
      this.pairs = [];
      this.ct.split('').forEach((letter, index) => {
        const pair = this.node('div', 'cw-pair');
        pair.setAttribute('role', 'listitem');
        const card = this.node('div', 'cw-card');
        card.setAttribute('aria-hidden', 'true');
        const turn = this.node('div', 'cw-card-turn');
        turn.append(this.node('span', 'cw-face decoded', this.pt[index]), this.node('span', 'cw-face cw-back encoded', letter));
        card.append(turn);
        pair.append(card, this.node('span', 'cw-word', this.words[index]));
        this.grid.append(pair);
        this.pairs.push(pair);
      });

      this.focus = this.node('div', 'cw-focus');
      this.focusPair = this.node('div', 'cw-focus-pair');
      this.focusCard = this.node('div', 'cw-single decoded', this.firstPlain);
      this.focusPair.append(this.focusCard, this.node('span', 'cw-focus-word', this.words[0]));
      this.math = this.node('div', 'cw-math');
      const sum = this.node('div', 'cw-sum');
      this.firstTerms.forEach(([letter, value], index) => {
        if (index) sum.append(this.node('span', 'cw-plus', '+'));
        const term = this.node('span', 'cw-term');
        term.append(this.node('span', 'cw-term-letter', letter), this.node('b', 'cw-term-value', String(value)));
        sum.append(term);
      });
      sum.append(this.node('span', 'cw-equals', '='), this.node('strong', 'cw-total', String(this.firstSum)));
      const reduction = this.node('div', 'cw-reduction');
      label.keyReduction.split('→').forEach((part, index) => {
        if (index) reduction.append(this.node('span', 'cw-reduction-arrow', '→'));
        reduction.append(part);
      });
      this.math.append(sum, reduction);
      this.focus.append(this.focusPair, this.math);

      this.shift = this.node('div', 'cw-shift');
      const shiftCards = this.node('div', 'cw-shift-cards');
      this.shiftFrom = this.node('div', 'cw-single decoded', this.firstPlain);
      const arrow = this.node('div', 'cw-arrow');
      const arrowLine = this.node('span', 'cw-arrow-line');
      arrowLine.setAttribute('aria-hidden', 'true');
      arrow.append(this.node('span', 'cw-arrow-label', label.shift), arrowLine);
      this.shiftTo = this.node('div', 'cw-single encoded', this.firstCipher);
      shiftCards.append(this.shiftFrom, arrow, this.shiftTo);
      this.shift.append(this.node('div', 'cw-shift-key', label.shiftKey), shiftCards);

      this.result = this.node('div', 'cw-result');
      this.resultCard = this.node('div', 'cw-single encoded', this.firstCipher);
      this.result.append(this.node('div', 'cw-result-label', label.firstDecoded), this.resultCard);
      this.message = this.node('div', 'cw-message');
      this.message.setAttribute('role', 'group');
      this.message.setAttribute('aria-label', label.decodedMessage);
      this.message.setAttribute('translate', 'no');
      this.message.setAttribute('role', 'img');
      this.message.setAttribute('aria-label', this.groups.join(' '));
      // The cipher letters stay on their cards, regrouped in fives the way
      // Thouless printed them.
      this.messageLetters = [];
      this.message.append(this.node('div', 'cw-scene-label cw-msg-label', label.decodedMessage));
      this.groups.forEach(group => {
        const row = this.node('span', 'cw-msg-word');
        group.split('').forEach(letter => {
          const card = this.node('span', 'cw-msg-letter encoded', letter);
          this.messageLetters.push(card);
          row.append(card);
        });
        this.message.append(row);
      });
      // The last step shows the whole system at once: message, key and cipher.
      this.overview = this.node('div', 'cw-overview');
      const block = (title, body) => {
        const section = this.node('div', 'cw-ov-block');
        section.append(this.node('div', 'cw-scene-label', title), body);
        this.overview.append(section);
      };
      const cards = (groups, kind) => {
        const holder = this.node('div', 'cw-ov-cards');
        holder.setAttribute('aria-hidden', 'true');
        groups.forEach(group => {
          const word = this.node('span', 'cw-ov-word');
          group.split('').forEach(letter => word.append(this.node('span', 'cw-ov-letter ' + kind, letter)));
          holder.append(word);
        });
        return holder;
      };
      block(label.encryptedMessage, cards(this.messageWords, 'decoded'));
      const passage = this.node('div', 'cw-ov-passage');
      passage.lang = this.passageLang;
      passage.setAttribute('translate', 'no');
      const used = new Set();
      this.passage.forEach((word, index) => {
        if (index) passage.append(document.createTextNode(' '));
        const token = this.letters(word);
        passage.append(this.node('span', 'cw-prayer-word' + (used.has(token) ? ' is-repeat' : ''), word));
        used.add(token);
      });
      passage.append(document.createTextNode(' …'));
      block(label.keyLabel, passage);
      block(label.decodedMessage, cards(this.groups, 'encoded'));
      this.overview.setAttribute('role', 'img');
      this.overview.setAttribute('aria-label', label.encryptedMessage + ': ' + this.messageWords.join(' ') + '. ' + label.keyLabel + ': ' + this.passage.join(' ') + '. ' + label.decodedMessage + ': ' + this.groups.join(' '));
      this.scene.append(this.source, this.keyphrase, this.grid, this.focus, this.shift, this.result, this.message, this.overview);

      const controls = this.node('div', 'cw-controls');
      this.previous = this.node('button', 'cw-previous', label.previous);
      this.previous.type = 'button';
      this.previous.addEventListener('click', () => this.choose(this.stage - 1));
      this.counter = this.node('span', 'cw-step-count');
      this.next = this.node('button', 'cw-next', label.next);
      this.next.type = 'button';
      this.next.addEventListener('click', () => this.stage === 9 ? this.replay() : this.choose(this.stage + 1));
      controls.append(this.previous, this.counter, this.next);
      this.root.append(header, this.scene, controls);
      this.host.replaceChildren(this.root);
    }

    choose(stage) {
      if (this.onNavigate) {
        this.onNavigate(stage);
        return;
      }
      this.go(stage);
      if (this.onStageChange) this.onStageChange(stage);
    }

    enableSwipes() {
      if (this.swipeController) return;
      this.swipeController = new AbortController();
      const options = {passive: true, signal: this.swipeController.signal};
      const hint = this.node('div', 'cw-swipe-hint', this.labels.swipeHint);
      this.root.querySelector('.cw-head').append(hint);
      this.scene.classList.add('cw-swipe-scene');
      let start = null;
      this.scene.addEventListener('pointerdown', event => {
        if (!event.isPrimary || event.pointerType !== 'touch') {
          start = null;
          return;
        }
        start = {id: event.pointerId, x: event.clientX, y: event.clientY};
      }, options);
      this.scene.addEventListener('pointercancel', () => { start = null; }, options);
      this.scene.addEventListener('pointerup', event => {
        const origin = start;
        start = null;
        if (!origin || event.pointerId !== origin.id) return;
        const dx = event.clientX - origin.x, dy = event.clientY - origin.y;
        // Vertical motion belongs to the page; a deliberate horizontal swipe
        // chooses one step through the same navigation callback as the buttons.
        if (Math.abs(dx) < 45 || Math.abs(dx) <= 1.5 * Math.abs(dy)) return;
        const stage = Math.max(0, Math.min(9, this.stage + (dx < 0 ? 1 : -1)));
        if (stage !== this.stage) this.choose(stage);
      }, options);
    }

    animate(element, keyframes, options = {}) {
      if (this.reduced || this.destroyed || typeof element.animate !== 'function') return;
      const animation = element.animate(keyframes, Object.assign({duration: 450, easing: 'cubic-bezier(.2,.7,.2,1)'}, options));
      this.animations.add(animation);
      animation.onfinish = animation.oncancel = () => this.animations.delete(animation);
      if (this.paused) animation.pause();
      return animation;
    }

    later(callback, delay) {
      const timer = {callback, remaining: delay, started: 0, id: null};
      this.timers.add(timer);
      if (!this.paused) this.arm(timer);
    }

    arm(timer) {
      timer.started = performance.now();
      timer.id = setTimeout(() => {
        this.timers.delete(timer);
        if (!this.destroyed) timer.callback();
      }, Math.max(0, timer.remaining));
    }

    cancel() {
      this.animations.forEach(animation => animation.cancel());
      this.animations.clear();
      this.timers.forEach(timer => clearTimeout(timer.id));
      this.timers.clear();
      this.ghosts.forEach(ghost => ghost.remove());
      this.ghosts.clear();
    }

    moveFrom(element, rect, duration = 500, delay = 0) {
      if (!rect || !rect.width || !rect.height || this.reduced) return;
      const destination = element.getBoundingClientRect();
      if (!destination.width || !destination.height) return;
      const dx = rect.left + rect.width / 2 - destination.left - destination.width / 2;
      const dy = rect.top + rect.height / 2 - destination.top - destination.height / 2;
      this.animate(element, [
        {transform: `translate(${dx}px, ${dy}px) scale(${rect.width / destination.width}, ${rect.height / destination.height})`},
        {transform: 'translate(0, 0) scale(1)'}
      ], {duration, delay, fill: delay ? 'backwards' : 'none'});
    }

    // The words keep the lines they landed on: each line becomes a row
    // before the cards fade, so tightening the spacing never rewraps them.
    freezeMessageRows() {
      const words = [...this.message.querySelectorAll('.cw-msg-word')];
      if (!words.length || this.message.querySelector('.cw-msg-row')) return;
      const tops = words.map(word => word.offsetTop);
      let row = null, top = null;
      words.forEach((word, index) => {
        const wordTop = tops[index];
        if (row === null || Math.abs(wordTop - top) > 1) {
          row = this.node('span', 'cw-msg-row');
          top = wordTop;
          this.message.append(row);
        }
        row.append(word);
      });
    }

    // The text keeps the lines its cards will take, so forming the cards
    // never rewraps the sentence.
    freezeSourceRows() {
      const words = [...this.source.querySelectorAll('.cw-source-word')];
      const grid = this.source.querySelector('.cw-source-grid');
      if (!words.length || grid.querySelector('.cw-source-row')) return;
      const tops = words.map(word => word.offsetTop);
      let row = null, top = null;
      words.forEach((word, index) => {
        if (row === null || Math.abs(tops[index] - top) > 1) {
          row = this.node('span', 'cw-source-row');
          top = tops[index];
          grid.append(row);
        }
        row.append(word);
      });
    }

    flattenSourceRows() {
      this.source.querySelectorAll('.cw-source-row').forEach(row => row.replaceWith(...row.childNodes));
    }

    flattenMessageRows() {
      this.message.querySelectorAll('.cw-msg-row').forEach(row => {
        row.replaceWith(...row.childNodes);
      });
    }

    settleMessage() {
      if (this.destroyed || this.stage !== 8) return;
      this.ghosts.forEach(ghost => ghost.remove());
      this.ghosts.clear();
      this.grid.hidden = true;
      this.message.hidden = false;
      this.message.removeAttribute('aria-hidden');
      this.freezeMessageRows();
      this.message.offsetWidth;
      this.root.dataset.finale = 'settled';
      this.counter.setAttribute('aria-label', this.labels.step + ' 9: ' + this.labels.decodedMessage);
    }

    revealMessage() {
      if (this.destroyed || this.stage !== 8) return;
      if (this.reduced) {
        this.settleMessage();
        return;
      }
      const origins = this.pairs.map(pair => pair.querySelector('.cw-card').getBoundingClientRect());
      this.message.hidden = false;
      this.message.setAttribute('aria-hidden', 'true');
      this.root.dataset.finale = 'moving';
      const scene = this.scene.getBoundingClientRect();
      // Each card flies from its grid position to its place in the words.
      this.messageLetters.forEach((letter, index) => {
        const rect = letter.getBoundingClientRect();
        const origin = origins[index];
        const ghost = this.node('span', 'cw-finale-letter cw-msg-letter encoded', letter.textContent);
        ghost.setAttribute('aria-hidden', 'true');
        Object.assign(ghost.style, {
          left: (rect.left - scene.left) + 'px', top: (rect.top - scene.top) + 'px',
          width: rect.width + 'px', height: rect.height + 'px'
        });
        this.scene.append(ghost);
        this.ghosts.add(ghost);
        const dx = origin.left + origin.width / 2 - rect.left - rect.width / 2;
        const dy = origin.top + origin.height / 2 - rect.top - rect.height / 2;
        this.animate(ghost, [
          {opacity: 0, transform: `translate(${dx}px, ${dy}px) scale(${origin.width / rect.width}, ${origin.height / rect.height})`},
          {opacity: 1, offset: .12},
          {opacity: 1, transform: 'translate(0, 0) scale(1)'}
        ], {duration: 700, delay: index * 12, fill: 'backwards'});
      });
      this.animate(this.grid, [{opacity: 1}, {opacity: 0}], {duration: 220});
      this.later(() => {
        this.root.dataset.finale = 'revealing';
        this.message.removeAttribute('aria-hidden');
        this.ghosts.forEach(ghost => this.animate(ghost, [{opacity: 1}, {opacity: 0}], {duration: 180}));
      }, 1000);
      this.later(() => this.settleMessage(), 1500);
    }

    go(stage, options = {}) {
      stage = Math.max(0, Math.min(9, Number(stage) || 0));
      if (this.destroyed || (stage === this.stage && !options.force)) return;
      const previous = this.stage;
      let from = null;
      let wordOrigins = [];
      let repeatOrigins = [];
      let cipherOrigins = [];
      if (previous === 8 && stage === 9 && !this.message.hidden) cipherOrigins = this.messageLetters.map(letter => letter.getBoundingClientRect());
      if (previous === 3) from = this.pairs[0].getBoundingClientRect();
      else if (previous === 5 && stage === 6) from = this.focusCard.getBoundingClientRect();
      else if (previous === 4 || previous === 5) from = this.focusPair.getBoundingClientRect();
      else if (previous === 6) from = this.shiftTo.getBoundingClientRect();
      else if (previous === 7) from = this.resultCard.getBoundingClientRect();
      else if (previous === 2 && stage === 3) {
        wordOrigins = this.prayerUnique.map(word => word.getBoundingClientRect());
        repeatOrigins = this.prayerRepeats.map(word => ({
          rect: word.getBoundingClientRect(),
          text: word.textContent,
          font: getComputedStyle(word).font,
          color: getComputedStyle(word).color
        }));
      }
      this.cancel();
      this.flattenMessageRows();
      this.stage = stage;
      this.root.dataset.stage = String(stage);
      this.root.dataset.finale = '';
      this.root.dataset.intro = '';
      this.host.dataset.walkthroughStage = String(stage);
      this.counter.textContent = (stage + 1) + ' / 10';
      this.counter.setAttribute('aria-label', this.labels.step + ' ' + (stage + 1) + ': ' + this.labels.stages[stage]);
      this.previous.disabled = stage === 0;
      this.next.textContent = stage === 9 ? this.labels.replay : this.labels.next;
      this.source.hidden = stage !== 0;
      this.keyphrase.hidden = stage !== 1 && stage !== 2;
      this.grid.hidden = stage !== 3 && stage !== 8;
      this.focus.hidden = stage !== 4 && stage !== 5;
      this.math.hidden = stage !== 5;
      this.shift.hidden = stage !== 6;
      this.result.hidden = stage !== 7;
      this.overview.hidden = stage !== 9;
      this.message.hidden = true;
      this.message.setAttribute('aria-hidden', 'true');
      this.shiftTo.textContent = this.firstCipher;
      this.shiftTo.classList.add('encoded');
      this.shiftTo.classList.remove('decoded');
      this.pairs.forEach((pair, index) => {
        pair.classList.remove('is-flipped');
        pair.querySelector('.cw-word').removeAttribute('aria-hidden');
        pair.setAttribute('aria-label', `${this.labels.decoded}: ${this.pt[index]}; ${this.labels.keyWord}: ${this.words[index]}`);
      });
      if (stage === 0) {
        if (previous > 0) this.animate(this.source, [{opacity: 0, transform: 'translateY(6px)'}, {opacity: 1, transform: 'translateY(0)'}]);
        // The sentence reads as text first, then the cards form around its letters.
        if (!this.reduced) {
          this.flattenSourceRows();
          this.freezeSourceRows();
          this.root.dataset.intro = 'text';
          this.source.offsetWidth;
          this.later(() => { this.root.dataset.intro = ''; }, previous < 0 || options.force ? 1400 : 800);
        }
      } else if (stage === 1) {
        this.prayerRepeats.forEach(word => { word.style.transitionDelay = '0ms'; });
        if (previous !== 2) this.animate(this.keyphrase, [{opacity: 0, transform: 'translateY(8px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 400});
      } else if (stage === 2) {
        // The strike-throughs belong to this step. Arriving from step 1 draws
        // them in one after another; from anywhere else they are simply there.
        const stagger = previous === 1 && !this.reduced;
        this.prayerRepeats.forEach((word, index) => { word.style.transitionDelay = stagger ? (120 + index * 90) + 'ms' : '0ms'; });
        if (previous !== 1) this.animate(this.keyphrase, [{opacity: 0, transform: 'translateY(8px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 400});
      } else if (stage === 3) {
        if (wordOrigins.length && !this.reduced) {
          // The struck words fade first, then the kept words glide and shrink
          // into their places, and only then do the cipher letters appear above.
          const FADE = 260, GLIDE = 650;
          this.pairs.forEach((pair, index) => {
            this.moveFrom(pair.querySelector('.cw-word'), wordOrigins[index], GLIDE, FADE);
            this.animate(pair.querySelector('.cw-card'), [{opacity: 0, transform: 'translateY(-6px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 350, delay: FADE + GLIDE + index * 12, fill: 'backwards'});
          });
          const scene = this.scene.getBoundingClientRect();
          repeatOrigins.forEach(origin => {
            const ghost = this.node('span', 'cw-prayer-word is-repeat cw-repeat-exit', origin.text);
            ghost.setAttribute('aria-hidden', 'true');
            Object.assign(ghost.style, {
              position: 'absolute', left: (origin.rect.left - scene.left) + 'px', top: (origin.rect.top - scene.top) + 'px',
              width: origin.rect.width + 'px', height: origin.rect.height + 'px', font: origin.font,
              color: origin.color, pointerEvents: 'none'
            });
            this.scene.append(ghost);
            this.ghosts.add(ghost);
            this.animate(ghost, [{opacity: 1}, {opacity: 0}], {duration: FADE, fill: 'forwards'});
            this.later(() => { ghost.remove(); this.ghosts.delete(ghost); }, FADE + 20);
          });
        } else {
          this.animate(this.grid, [{opacity: 0, transform: 'translateY(6px)'}, {opacity: 1, transform: 'translateY(0)'}]);
        }
      } else if (stage === 4) {
        this.moveFrom(this.focusPair, from);
      } else if (stage === 5) {
        this.moveFrom(this.focusPair, from, 360);
        this.math.querySelectorAll('.cw-term, .cw-plus, .cw-equals, .cw-total').forEach((element, index) => {
          this.animate(element, [{opacity: 0, transform: 'translateY(7px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 320, delay: index * 55, fill: 'backwards'});
        });
        this.animate(this.math.querySelector('.cw-reduction'), [{opacity: 0}, {opacity: 1}], {delay: 700, duration: 350, fill: 'backwards'});
      } else if (stage === 6) {
        // From the sum, the message card travels to its place on the left and
        // the rest of the scene follows; the count starts once it has landed.
        const glide = previous === 5 && Boolean(from) && !this.reduced;
        const settle = glide ? 420 : 0;
        if (glide) {
          this.moveFrom(this.shiftFrom, from, 520);
          this.shift.querySelectorAll('.cw-shift-key, .cw-arrow, .cw-single.encoded').forEach(element => {
            this.animate(element, [{opacity: 0, transform: 'translateY(7px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 350, delay: 300, fill: 'backwards'});
          });
        } else {
          this.animate(this.shift, [{opacity: 0, transform: 'translateY(7px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 350});
        }
        if (!this.reduced) {
          this.shiftTo.classList.replace('encoded', 'decoded');
          this.shiftTo.textContent = this.firstPlain;
          const start = this.firstPlain.charCodeAt(0) - 65;
          for (let step = 1; step <= this.firstShift; step++) {
            this.later(() => {
              this.shiftTo.textContent = String.fromCharCode(65 + (start + step) % 26);
              if (step === this.firstShift) {
                this.shiftTo.classList.replace('decoded', 'encoded');
                this.animate(this.shiftTo, [{transform: 'scale(.92)'}, {transform: 'scale(1)'}], {duration: 300});
              }
            }, settle + 250 + step * 43);
          }
        }
      } else if (stage === 7) {
        if (previous === 6) this.moveFrom(this.resultCard, from);
        else this.animate(this.resultCard, [{opacity: 0, transform: 'scale(.85)'}, {opacity: 1, transform: 'scale(1)'}]);
      } else if (stage === 8) {
        this.root.dataset.finale = 'flipping';
        // Arriving from the previous step, the first cipher letter glides from
        // the big card to its place in the grid before the other cards flip.
        const glide = Boolean(from) && !this.reduced;
        this.animate(this.grid, [{opacity: 0, transform: 'scale(.96)'}, {opacity: 1, transform: 'scale(1)'}], {duration: 400});
        this.pairs.forEach((pair, index) => {
          const word = pair.querySelector('.cw-word');
          const decode = () => {
            pair.classList.add('is-flipped');
            pair.setAttribute('aria-label', `${this.labels.encoded}: ${this.ct[index]}`);
            word.setAttribute('aria-hidden', 'true');
          };
          const flip = () => {
            decode();
            this.animate(pair.querySelector('.cw-card-turn'), [{transform: 'rotateY(0deg)'}, {transform: 'rotateY(180deg)'}], {duration: 420, easing: 'cubic-bezier(.4,0,.2,1)'});
          };
          if (this.reduced) decode();
          else if (glide && index === 0) {
            decode();
            this.moveFrom(pair.querySelector('.cw-card'), from, 520);
          } else this.later(flip, (glide ? 640 : 450) + index * 110);
        });
        if (this.reduced) this.revealMessage();
        else this.later(() => this.revealMessage(), glide ? 3700 : 3500);
      } else if (stage === 9) {
        // Coming from the finished cipher, its cards glide down into the
        // overview while the message and the key fade in above them.
        const glide = cipherOrigins.length > 0 && !this.reduced;
        this.overview.querySelectorAll('.cw-ov-block').forEach((section, index) => {
          if (glide && index === 2) return;
          this.animate(section, [{opacity: 0, transform: 'translateY(8px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 400, delay: index * 140, fill: 'backwards'});
        });
        if (glide) {
          this.overview.querySelectorAll('.cw-ov-letter.encoded').forEach((letter, index) => {
            this.moveFrom(letter, cipherOrigins[index], 650, index * 12);
          });
          const label = this.overview.querySelector('.cw-ov-block:nth-child(3) .cw-scene-label');
          if (label) this.animate(label, [{opacity: 0}, {opacity: 1}], {duration: 400, delay: 500, fill: 'backwards'});
        }
      }
    }

    pause() {
      if (this.paused || this.destroyed) return;
      this.paused = true;
      this.animations.forEach(animation => animation.pause());
      this.timers.forEach(timer => {
        clearTimeout(timer.id);
        timer.remaining = Math.max(0, timer.remaining - (performance.now() - timer.started));
      });
    }

    resume() {
      if (!this.paused || this.destroyed) return;
      this.paused = false;
      this.animations.forEach(animation => animation.play());
      this.timers.forEach(timer => this.arm(timer));
    }

    replay() {
      this.go(this.stage, {force: true});
    }

    destroy() {
      this.swipeController?.abort();
      this.cancel();
      this.resizeObserver.disconnect();
      this.destroyed = true;
      this.host.replaceChildren();
    }
  }
  CipherWalkthrough.labels = DEFAULT_LABELS;
  window.CipherWalkthrough = CipherWalkthrough;
})();
