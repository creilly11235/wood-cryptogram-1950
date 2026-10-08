/* The article controls the eight steps; buttons also let a reader explore them.
   Animation is presentational. Every step has a complete reduced-motion view. */
(() => {
  'use strict';

  const DEFAULT_LABELS = {
    label: 'How the cipher becomes a message',
    encoded: 'Encoded',
    decoded: 'Decoded',
    stages: [
      'The 21-letter cipher',
      'The key is a passage from a book',
      'One key word for every cipher letter',
      'Start with F and Unser',
      'Add the letters in Unser',
      'Use Y to shift F back 24 places',
      'The first decoded letter is H',
      'Repeat for all 21 letters'
    ],
    previous: 'Previous',
    next: 'Next',
    replay: 'Replay',
    keyReduction: '77 − (2 × 26) = 25 → Y',
    shiftKey: 'Y means a shift of 24 (A = 0)',
    shift: 'Back 24',
    firstDecoded: 'The message begins',
    step: 'Step',
    keyWord: 'key word',
    keyNote: 'Repeated words are skipped',
    decodedMessage: 'The decoded message'
  };

  class CipherWalkthrough {
    constructor(host, options = {}) {
      this.host = host;
      this.ct = options.ct || 'FVAMINTKFXXWATBOIZVVX';
      this.pt = options.pt || 'HIERBINICHTOTSIENSTEW';
      this.words = (options.words || [
        'Unser', 'Vater', 'in', 'dem', 'Himmel', 'Dein', 'Name',
        'werde', 'geheiligt', 'Reich', 'komme', 'Wille', 'geschehe', 'auf',
        'Erden', 'wie', 'im', 'täglich', 'Brot', 'gib', 'uns'
      ]).map(word => typeof word === 'string' ? word : word[0]);
      if (this.ct.length !== 21 || this.pt.length !== 21 || this.words.length !== 21) {
        throw new Error('CipherWalkthrough requires 21 cipher letters, key words and decoded letters.');
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
          if (this.stage === 7 && ['moving', 'revealing'].includes(this.root.dataset.finale)) {
            this.cancel();
            this.settleMessage();
          }
        }
        this.lastSceneSize = size;
      });
      this.resizeObserver.observe(this.scene);
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
      this.title = this.node('div', 'cw-title');
      this.title.setAttribute('aria-live', 'polite');
      const legend = this.node('div', 'cw-legend');
      ['encoded', 'decoded'].forEach(state => {
        const item = this.node('span', 'cw-legend-item');
        item.append(this.node('i', 'cw-swatch ' + state), document.createTextNode(label[state]));
        legend.append(item);
      });
      header.append(this.title, legend);
      this.scene = this.node('div', 'cw-scene');
      this.source = this.node('div', 'cw-source');
      this.source.setAttribute('role', 'img');
      this.source.setAttribute('aria-label', label.encoded + ': ' + this.ct);
      const sourceGrid = this.node('div', 'cw-source-grid');
      sourceGrid.setAttribute('aria-hidden', 'true');
      this.sourceLetters = this.ct.split('').map(letter => {
        const card = this.node('span', 'cw-source-letter encoded', letter);
        sourceGrid.append(card);
        return card;
      });
      this.source.append(sourceGrid);

      this.keyphrase = this.node('div', 'cw-keyphrase');
      this.prayer = this.node('div', 'cw-prayer');
      this.prayer.lang = 'de';
      this.prayer.setAttribute('translate', 'no');
      const prayerWords = [
        'Unser', 'Vater', 'in', 'dem', 'Himmel!', 'Dein', 'Name', 'werde',
        'geheiligt.', 'Dein', 'Reich', 'komme.', 'Dein', 'Wille', 'geschehe',
        'auf', 'Erden', 'wie', 'im', 'Himmel.', 'Unser', 'täglich', 'Brot', 'gib', 'uns'
      ];
      const seen = new Set();
      this.prayerUnique = [];
      this.prayerRepeats = [];
      prayerWords.forEach((word, index) => {
        if (index) this.prayer.append(document.createTextNode(' '));
        const token = word.toLocaleLowerCase('de').replace(/[.!]/g, '');
        const repeated = seen.has(token);
        const span = this.node('span', 'cw-prayer-word' + (repeated ? ' is-repeat' : ''), word);
        (repeated ? this.prayerRepeats : this.prayerUnique).push(span);
        this.prayer.append(span);
        seen.add(token);
      });
      this.prayer.append(document.createTextNode(' …'));
      this.keyphrase.append(this.prayer, this.node('div', 'cw-key-note', label.keyNote));

      this.grid = this.node('div', 'cw-grid');
      this.grid.setAttribute('role', 'list');
      this.pairs = [];
      this.ct.split('').forEach((letter, index) => {
        const pair = this.node('div', 'cw-pair');
        pair.setAttribute('role', 'listitem');
        const card = this.node('div', 'cw-card');
        card.setAttribute('aria-hidden', 'true');
        const turn = this.node('div', 'cw-card-turn');
        turn.append(this.node('span', 'cw-face encoded', letter), this.node('span', 'cw-face decoded', this.pt[index]));
        card.append(turn);
        pair.append(card, this.node('span', 'cw-word', this.words[index]));
        this.grid.append(pair);
        this.pairs.push(pair);
      });

      this.focus = this.node('div', 'cw-focus');
      this.focusPair = this.node('div', 'cw-focus-pair');
      this.focusCard = this.node('div', 'cw-single encoded', 'F');
      this.focusPair.append(this.focusCard, this.node('span', 'cw-focus-word', 'Unser'));
      this.math = this.node('div', 'cw-math');
      const sum = this.node('div', 'cw-sum');
      ['U', 'N', 'S', 'E', 'R'].forEach((letter, index) => {
        if (index) sum.append(this.node('span', 'cw-plus', '+'));
        const term = this.node('span', 'cw-term');
        term.append(this.node('span', 'cw-term-letter', letter), this.node('b', 'cw-term-value', [21, 14, 19, 5, 18][index]));
        sum.append(term);
      });
      sum.append(this.node('span', 'cw-equals', '='), this.node('strong', 'cw-total', '77'));
      this.math.append(sum, this.node('div', 'cw-reduction', label.keyReduction));
      this.focus.append(this.focusPair, this.math);

      this.shift = this.node('div', 'cw-shift');
      const shiftCards = this.node('div', 'cw-shift-cards');
      this.shiftFrom = this.node('div', 'cw-single encoded', 'F');
      const arrow = this.node('div', 'cw-arrow');
      const arrowLine = this.node('span', 'cw-arrow-line');
      arrowLine.setAttribute('aria-hidden', 'true');
      arrow.append(this.node('span', 'cw-arrow-label', label.shift), arrowLine);
      this.shiftTo = this.node('div', 'cw-single decoded', 'H');
      shiftCards.append(this.shiftFrom, arrow, this.shiftTo);
      this.shift.append(this.node('div', 'cw-shift-key', label.shiftKey), shiftCards);

      this.result = this.node('div', 'cw-result');
      this.resultCard = this.node('div', 'cw-single decoded', 'H');
      this.result.append(this.node('div', 'cw-result-label', label.firstDecoded), this.resultCard);
      this.message = this.node('div', 'cw-message');
      this.message.setAttribute('role', 'group');
      this.message.setAttribute('aria-label', label.decodedMessage);
      this.message.setAttribute('translate', 'no');
      this.reading = this.node('p', 'cw-message-reading');
      this.messageLines = [
        ['Hier bin ich.', 'de'], ['Totsiens.', 'af'], ['T.E.W.', '']
      ].map(([text, lang], index) => {
        const line = this.node('span', 'cw-message-line', text);
        if (lang) line.lang = lang;
        if (index) this.reading.append(document.createTextNode(' '));
        this.reading.append(line);
        return line;
      });
      this.message.append(this.reading);
      this.scene.append(this.source, this.keyphrase, this.grid, this.focus, this.shift, this.result, this.message);

      const controls = this.node('div', 'cw-controls');
      this.previous = this.node('button', 'cw-previous', label.previous);
      this.previous.type = 'button';
      this.previous.addEventListener('click', () => this.choose(this.stage - 1));
      this.counter = this.node('span', 'cw-step-count');
      this.next = this.node('button', 'cw-next', label.next);
      this.next.type = 'button';
      this.next.addEventListener('click', () => this.stage === 7 ? this.replay() : this.choose(this.stage + 1));
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

    moveFrom(element, rect, duration = 500) {
      if (!rect || !rect.width || !rect.height || this.reduced) return;
      const destination = element.getBoundingClientRect();
      if (!destination.width || !destination.height) return;
      const dx = rect.left + rect.width / 2 - destination.left - destination.width / 2;
      const dy = rect.top + rect.height / 2 - destination.top - destination.height / 2;
      this.animate(element, [
        {transform: `translate(${dx}px, ${dy}px) scale(${rect.width / destination.width}, ${rect.height / destination.height})`},
        {transform: 'translate(0, 0) scale(1)'}
      ], {duration});
    }

    settleMessage() {
      if (this.destroyed || this.stage !== 7) return;
      this.ghosts.forEach(ghost => ghost.remove());
      this.ghosts.clear();
      this.grid.hidden = true;
      this.message.hidden = false;
      this.message.removeAttribute('aria-hidden');
      this.root.dataset.finale = 'settled';
      this.title.textContent = this.labels.decodedMessage;
      this.counter.setAttribute('aria-label', this.labels.step + ' 8: ' + this.labels.decodedMessage);
    }

    revealMessage() {
      if (this.destroyed || this.stage !== 7) return;
      if (this.reduced) {
        this.settleMessage();
        return;
      }
      const origins = this.pairs.map(pair => {
        const range = document.createRange();
        range.selectNodeContents(pair.querySelector('.cw-face.decoded'));
        return range.getBoundingClientRect();
      });
      this.message.hidden = false;
      this.message.setAttribute('aria-hidden', 'true');
      this.root.dataset.finale = 'moving';
      const destinations = [];
      this.messageLines.forEach(line => {
        const text = line.firstChild;
        for (let index = 0; index < text.length; index++) {
          const letter = text.textContent[index];
          if (!/[a-z]/i.test(letter)) continue;
          const range = document.createRange();
          range.setStart(text, index);
          range.setEnd(text, index + 1);
          destinations.push({letter, rect: range.getBoundingClientRect()});
        }
      });
      const scene = this.scene.getBoundingClientRect();
      const font = getComputedStyle(this.reading);
      // Fly only the 21 original letters. Spacing, case and punctuation resolve
      // into real, selectable text; there are no permanent letter wrappers.
      destinations.forEach(({letter, rect}, index) => {
        const origin = origins[index];
        const ghost = this.node('span', 'cw-finale-letter', letter);
        ghost.setAttribute('aria-hidden', 'true');
        Object.assign(ghost.style, {
          left: (rect.left - scene.left) + 'px', top: (rect.top - scene.top) + 'px',
          width: rect.width + 'px', height: rect.height + 'px',
          fontFamily: font.fontFamily, fontSize: font.fontSize, fontWeight: font.fontWeight,
          lineHeight: rect.height + 'px'
        });
        this.scene.append(ghost);
        this.ghosts.add(ghost);
        const dx = origin.left + origin.width / 2 - rect.left - rect.width / 2;
        const dy = origin.top + origin.height / 2 - rect.top - rect.height / 2;
        this.animate(ghost, [
          {opacity: 0, transform: `translate(${dx}px, ${dy}px) scale(${origin.width / rect.width}, ${origin.height / rect.height})`},
          {opacity: 1, offset: .12},
          {opacity: 1, transform: 'translate(0, 0) scale(1)'}
        ], {duration: 800, delay: index * 10, fill: 'backwards'});
      });
      this.animate(this.grid, [{opacity: 1}, {opacity: 0}], {duration: 220});
      this.later(() => {
        this.root.dataset.finale = 'revealing';
        this.message.removeAttribute('aria-hidden');
        this.animate(this.reading, [{opacity: 0}, {opacity: 1}], {duration: 180});
        this.ghosts.forEach(ghost => this.animate(ghost, [{opacity: 1}, {opacity: 0}], {duration: 180}));
      }, 1030);
      this.later(() => this.settleMessage(), 1220);
    }

    go(stage, options = {}) {
      stage = Math.max(0, Math.min(7, Number(stage) || 0));
      if (this.destroyed || (stage === this.stage && !options.force)) return;
      const previous = this.stage;
      let from = null;
      let wordOrigins = [];
      let repeatOrigins = [];
      if (previous === 2) from = this.pairs[0].getBoundingClientRect();
      else if (previous === 3 || previous === 4) from = this.focusPair.getBoundingClientRect();
      else if (previous === 5) from = this.shiftTo.getBoundingClientRect();
      else if (previous === 1 && stage === 2) {
        wordOrigins = this.prayerUnique.map(word => word.getBoundingClientRect());
        repeatOrigins = this.prayerRepeats.map(word => ({
          rect: word.getBoundingClientRect(),
          text: word.textContent,
          font: getComputedStyle(word).font,
          color: getComputedStyle(word).color
        }));
      }
      this.cancel();
      this.stage = stage;
      this.root.dataset.stage = String(stage);
      this.root.dataset.finale = '';
      this.host.dataset.walkthroughStage = String(stage);
      this.title.textContent = this.labels.stages[stage];
      this.counter.textContent = (stage + 1) + ' / 8';
      this.counter.setAttribute('aria-label', this.labels.step + ' ' + (stage + 1) + ': ' + this.labels.stages[stage]);
      this.previous.disabled = stage === 0;
      this.next.textContent = stage === 7 ? this.labels.replay : this.labels.next;
      this.source.hidden = stage !== 0;
      this.keyphrase.hidden = stage !== 1;
      this.grid.hidden = stage !== 2 && stage !== 7;
      this.focus.hidden = stage !== 3 && stage !== 4;
      this.math.hidden = stage !== 4;
      this.shift.hidden = stage !== 5;
      this.result.hidden = stage !== 6;
      this.message.hidden = true;
      this.message.setAttribute('aria-hidden', 'true');
      this.shiftTo.textContent = 'H';
      this.shiftTo.classList.add('decoded');
      this.shiftTo.classList.remove('encoded');
      this.pairs.forEach((pair, index) => {
        pair.classList.remove('is-decoded');
        pair.querySelector('.cw-word').removeAttribute('aria-hidden');
        pair.setAttribute('aria-label', `${this.labels.encoded}: ${this.ct[index]}; ${this.labels.keyWord}: ${this.words[index]}`);
      });
      if (stage === 0) {
        if (previous > 0) this.animate(this.source, [{opacity: 0, transform: 'translateY(6px)'}, {opacity: 1, transform: 'translateY(0)'}]);
      } else if (stage === 1) {
        this.animate(this.keyphrase, [{opacity: 0, transform: 'translateY(8px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 400});
      } else if (stage === 2) {
        if (wordOrigins.length && !this.reduced) {
          this.pairs.forEach((pair, index) => {
            this.moveFrom(pair.querySelector('.cw-word'), wordOrigins[index], 650);
            this.animate(pair.querySelector('.cw-card'), [{opacity: 0, transform: 'translateY(-6px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 350, delay: 180 + index * 12, fill: 'backwards'});
          });
          const scene = this.scene.getBoundingClientRect();
          repeatOrigins.forEach(origin => {
            const ghost = this.node('span', 'cw-prayer-word is-repeat cw-repeat-exit', origin.text);
            ghost.setAttribute('aria-hidden', 'true');
            Object.assign(ghost.style, {
              position: 'absolute', left: (origin.rect.left - scene.left) + 'px', top: (origin.rect.top - scene.top) + 'px',
              width: origin.rect.width + 'px', height: origin.rect.height + 'px', font: origin.font,
              color: origin.color, textDecoration: 'line-through', pointerEvents: 'none'
            });
            this.scene.append(ghost);
            this.ghosts.add(ghost);
            this.animate(ghost, [{opacity: 1}, {opacity: 0, transform: 'translateY(-8px)'}], {duration: 250, fill: 'forwards'});
            this.later(() => { ghost.remove(); this.ghosts.delete(ghost); }, 270);
          });
        } else {
          this.animate(this.grid, [{opacity: 0, transform: 'translateY(6px)'}, {opacity: 1, transform: 'translateY(0)'}]);
        }
      } else if (stage === 3) {
        this.moveFrom(this.focusPair, from);
      } else if (stage === 4) {
        this.moveFrom(this.focusPair, from, 360);
        this.math.querySelectorAll('.cw-term, .cw-plus, .cw-equals, .cw-total').forEach((element, index) => {
          this.animate(element, [{opacity: 0, transform: 'translateY(7px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 320, delay: index * 55, fill: 'backwards'});
        });
        this.animate(this.math.querySelector('.cw-reduction'), [{opacity: 0}, {opacity: 1}], {delay: 700, duration: 350, fill: 'backwards'});
      } else if (stage === 5) {
        this.animate(this.shift, [{opacity: 0, transform: 'translateY(7px)'}, {opacity: 1, transform: 'translateY(0)'}], {duration: 350});
        if (!this.reduced) {
          this.shiftTo.classList.replace('decoded', 'encoded');
          this.shiftTo.textContent = 'F';
          for (let step = 1; step <= 24; step++) {
            this.later(() => {
              this.shiftTo.textContent = String.fromCharCode(65 + (5 - step + 26) % 26);
              if (step === 24) {
                this.shiftTo.classList.replace('encoded', 'decoded');
                this.animate(this.shiftTo, [{transform: 'scale(.92)'}, {transform: 'scale(1)'}], {duration: 300});
              }
            }, 250 + step * 43);
          }
        }
      } else if (stage === 6) {
        if (previous === 5) this.moveFrom(this.resultCard, from);
        else this.animate(this.resultCard, [{opacity: 0, transform: 'scale(.85)'}, {opacity: 1, transform: 'scale(1)'}]);
      } else if (stage === 7) {
        this.root.dataset.finale = 'flipping';
        this.animate(this.grid, [{opacity: 0, transform: 'scale(.96)'}, {opacity: 1, transform: 'scale(1)'}], {duration: 400});
        this.pairs.forEach((pair, index) => {
          const flip = () => {
            pair.classList.add('is-decoded');
            pair.setAttribute('aria-label', `${this.labels.decoded}: ${this.pt[index]}`);
            const turn = pair.querySelector('.cw-card-turn');
            this.animate(turn, [{transform: 'rotateY(0deg)'}, {transform: 'rotateY(180deg)'}], {duration: 420, easing: 'cubic-bezier(.4,0,.2,1)'});
            const word = pair.querySelector('.cw-word');
            word.setAttribute('aria-hidden', 'true');
            this.animate(word, [{opacity: 1}, {opacity: 0}], {delay: 420, duration: 160, fill: 'backwards'});
          };
          if (this.reduced) flip();
          else this.later(flip, 450 + index * 110);
        });
        if (this.reduced) this.revealMessage();
        else this.later(() => this.revealMessage(), 3500);
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
      this.cancel();
      this.resizeObserver.disconnect();
      this.destroyed = true;
      this.host.replaceChildren();
    }
  }
  CipherWalkthrough.labels = DEFAULT_LABELS;
  window.CipherWalkthrough = CipherWalkthrough;
})();
