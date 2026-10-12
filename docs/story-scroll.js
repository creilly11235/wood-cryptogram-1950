/* Every chapter pins its graphic beside the passages that explain it. On
   desktop the graphic follows the reading column; on phones it fills the
   screen while the passages rise over its lower part, one card per stage. */
(() => {
  'use strict';

  function start() {
    const api = window.WoodStory;
    if (!api) throw new Error('The Wood graphic factory must load before story-scroll.js');
    const mobile = matchMedia('(max-width: 900px)');
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const root = document.documentElement;
    const records = [];
    let framePending = false;

    // Each prose element carries the stage it explains. The graphic only
    // changes as the reader moves from one passage to the next, so nothing
    // moves while a passage is being read. A sequence ("1 2") is still
    // accepted and shows its first stage going forward, its last going back.
    function walkSequence(target) {
      return target.dataset.walkStage.trim().split(/\s+/).map(Number).filter(Number.isFinite);
    }
    // On phones the passages are cards that rise over the full-screen graphic;
    // a card takes over its stage as it enters the lower part of the screen.
    function walkLine() {
      return innerHeight * (mobile.matches ? .88 : .55);
    }
    function fadeCards(record) {
      // Short portrait screens read the card a little lower, leaving the chart its space.
      const focal = innerHeight * (innerWidth > innerHeight ? .8 : innerHeight < 640 ? .76 : .72);
      record.cards.forEach(card => {
        const box = card.getBoundingClientRect();
        const distance = Math.abs((box.top + box.bottom) / 2 - focal) / innerHeight;
        const opacity = Math.max(0, Math.min(1, 1 - (distance - .14) / .18));
        card.style.opacity = opacity.toFixed(3);
      });
    }
    function playWalk(record, index, forward, preferred) {
      record.walkIndex = index;
      const target = record.walkTargets[index];
      const sequence = walkSequence(target);
      if (!sequence.length) return;
      let start = forward ? 0 : sequence.length - 1;
      if (sequence.includes(preferred)) start = sequence.indexOf(preferred);
      record.graphic.showStage(sequence[start]);
      record.walkTargets.forEach((item, i) => item.classList.toggle('is-walk-active', i === index));
    }

    document.querySelectorAll('.chapter').forEach(chapter => {
      const el = chapter.querySelector('.graphic');
      const steps = [...chapter.querySelectorAll('.step[data-s]')];
      if (!el || !steps.length) return;
      const graphic = new api.Graphic(el);
      graphic.visible = false;
      chapter.classList.add('pinned-chapter');
      const record = {
        chapter, el, graphic, steps,
        state: null, renderMode: null,
        walkTargets: [...chapter.querySelectorAll('[data-walk-stage]')], walkIndex: null, walkPreferred: undefined,
        cards: [...chapter.querySelectorAll('.pin > .text [data-walk-stage]')],
      };
      if (!graphic.walkthrough) {
        // On phones the next section rises to meet the graphic, so the
        // chapter learns how much empty panel sits below the drawing.
        const body = el.querySelector('.gbody') || el;
        // A chapter with no closing text hands the measure to the next one,
        // whose opening text rises to meet this graphic instead.
        const next = chapter.querySelector('.text-after') ? null : chapter.nextElementSibling;
        const measureTail = () => {
          const tail = el.getBoundingClientRect().bottom - body.getBoundingClientRect().bottom - 28;
          const value = Number.isFinite(tail) && tail > 0 ? Math.round(tail) + 'px' : '';
          chapter.style.setProperty('--walk-tail', value);
          if (next) next.style.setProperty('--walk-tail-prev', value);
        };
        new ResizeObserver(() => requestAnimationFrame(measureTail)).observe(el);
        measureTail();
      }
      if (graphic.walkthrough) {
        // The buttons follow the prose: a stage within the current passage
        // shows at once; any other scrolls to the passage that explains it.
        graphic.walkthrough.onNavigate = index => {
          const targetIndex = record.walkTargets.findIndex(item => walkSequence(item).includes(index));
          if (targetIndex < 0) return;
          if (targetIndex === record.walkIndex) {
            playWalk(record, targetIndex, true, index);
            return;
          }
          const target = record.walkTargets[targetIndex];
          const following = record.walkTargets[targetIndex + 1];
          const box = target.getBoundingClientRect();
          const inset = following ? Math.min(32, (following.getBoundingClientRect().top - box.top) / 2) : 32;
          record.walkPreferred = index;
          window.scrollTo({top: window.scrollY + box.top - walkLine() + inset, behavior: reduced.matches ? 'instant' : 'smooth'});
          schedule();
        };
      }
      records.push(record);
    });

    function describe(record, index) {
      const step = record.steps[index];
      const description = step.dataset.cap || step.querySelector('h2, h3')?.textContent || '';
      record.el.dataset.state = step.dataset.s;
      const caption = record.el.querySelector('.beatcap');
      if (caption) caption.textContent = description;
      const canvas = record.el.querySelector('canvas');
      if (canvas && description) {
        canvas.setAttribute('role', 'img');
        canvas.setAttribute('aria-label', description);
      }
      record.steps.forEach((item, i) => item.classList.toggle('on', i === index));
      // The passage driving a chart is marked for scripts and checks; the
      // cipher walkthrough marks its passages stage by stage instead.
      if (!record.graphic.walkthrough) record.steps.forEach((item, i) => item.classList.toggle('is-walk-active', i === index));
    }

    function layout() {
      root.dataset.storyLayout = mobile.matches ? 'stack' : 'side';
      root.style.setProperty('--story-viewport-height', `${innerHeight}px`);
      const mode = mobile.matches ? 'pinned' : 'desktop';
      records.forEach(record => {
        if (record.renderMode === mode) return;
        record.renderMode = mode;
        record.state = null;
        record.walkIndex = null;
        if (mode === 'desktop') record.cards.forEach(card => { card.style.opacity = ''; });
      });
      update();
    }

    function updateVisibility() {
      records.forEach(record => {
        const box = record.el.getBoundingClientRect();
        const visible = box.height > 0 && box.bottom > 0 && box.top < innerHeight;
        record.inView = visible;
        if (record.graphic.visible === visible) return;
        record.graphic.visible = visible;
        if (visible) record.graphic.resume();
        else record.graphic.pause();
      });
    }

    function update() {
      framePending = false;
      const line = walkLine();
      records.forEach(record => {
        let index = 0;
        record.steps.forEach((step, i) => { if (step.getBoundingClientRect().top <= line) index = i; });
        const state = record.steps[index].dataset.s;
        if (record.state !== state) {
          record.state = state;
          record.graphic.go(state);
          describe(record, index);
          if (!record.graphic.visible) record.graphic.pause();
        }
        if (mobile.matches) fadeCards(record);
        if (record.graphic.walkthrough) {
          let walkIndex = 0;
          record.walkTargets.forEach((target, i) => { if (target.getBoundingClientRect().top <= line) walkIndex = i; });
          if (record.walkIndex !== walkIndex) {
            const forward = record.walkIndex === null || walkIndex > record.walkIndex;
            // A requested stage is kept until the passage that holds it is reached.
            const preferred = record.walkPreferred;
            if (preferred === undefined || walkSequence(record.walkTargets[walkIndex]).includes(preferred)) record.walkPreferred = undefined;
            playWalk(record, walkIndex, forward, preferred);
          }
        }
      });
      updateVisibility();
    }
    function schedule() {
      if (framePending) return;
      framePending = true;
      requestAnimationFrame(update);
    }

    addEventListener('scroll', schedule, {passive: true});
    addEventListener('resize', layout, {passive: true});
    addEventListener('pageshow', layout);
    mobile.addEventListener('change', layout);
    document.fonts?.ready.then(layout);

    document.querySelectorAll('.replay').forEach(button => button.addEventListener('click', () => {
      const record = records.find(item => item.chapter === button.closest('.chapter'));
      if (!record) return;
      const index = record.steps.findIndex(step => step.dataset.s === 'prayer');
      if (index >= 0) record.steps[index].scrollIntoView({block: 'start', behavior: 'instant'});
      record.graphic.replay();
      schedule();
    }));

    function paint(now) {
      records.forEach(record => { if (record.inView) record.graphic.frame(now); });
      requestAnimationFrame(paint);
    }
    layout();
    requestAnimationFrame(paint);
    root.dataset.storyReady = 'true';
    window.WoodStoryController = {records};
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once: true});
  else start();
})();
