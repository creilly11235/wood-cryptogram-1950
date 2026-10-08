/* Desktop graphics follow the reading column. Mobile visuals are ordinary
   full-screen sections: scrolling and buttons lead to the same fixed scenes. */
(() => {
  'use strict';

  function start() {
    const api = window.WoodStory;
    if (!api) throw new Error('The Wood graphic factory must load before story-scroll.js');

    const { Graphic } = api;
    const phone = matchMedia('(max-width: 900px)');
    const root = document.documentElement;
    const chapters = [];
    const records = [];
    const mobileWalk = [];
    let mobileBuilt = false;
    let viewportWidth = 0;
    let viewportHeight = 0;
    let framePending = false;

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const record = records.find(item => item.el === entry.target);
        if (record) setVisibility(record, entry.isIntersecting, entry.intersectionRatio);
      });
    }, { threshold: [0, .25, .5, .55, .9] });

    function createRecord(el, chapter, steps, flow = false, stage = null) {
      const graphic = new Graphic(el);
      graphic.visible = false;
      const progress = el.querySelector('.progress');
      if (progress && !flow) progress.innerHTML = steps.map(() => '<i></i>').join('');
      const record = {
        chapter, el, steps, graphic, progress, flow, stage,
        walkTargets: flow ? [] : [...chapter.querySelectorAll('[data-walk-stage]')],
        walkStage: -1,
        inView: false,
        needsReveal: stage !== null,
        caption: el.querySelector('.beatcap'),
        state: null,
      };
      records.push(record);
      select(record, 0);
      if (stage !== null) {
        const walk = graphic.walkthrough;
        walk.go(stage);
        walk.title.removeAttribute('aria-live');
        walk.title.tabIndex = -1;
        walk.onNavigate = next => {
          const target = mobileWalk[Math.max(0, Math.min(7, next))];
          if (!target) return;
          target.graphic.walkthrough.title.focus({ preventScroll: true });
          target.el.parentElement.scrollIntoView({ block: 'start', behavior: api.reduced ? 'instant' : 'smooth' });
        };
      }
      graphic.pause();
      observer.observe(el);
      return record;
    }

    document.querySelectorAll('.chapter').forEach(chapter => {
      const el = chapter.querySelector('.graphic');
      const steps = [...chapter.querySelectorAll('.step[data-s]')];
      if (!el || !steps.length) return;
      // Keep the uninitialized markup. The walkthrough replaces its canvas DOM.
      const template = el.cloneNode(true);
      const record = createRecord(el, chapter, steps);
      record.template = template;
      chapters.push(record);
    });

    function buildMobile() {
      if (mobileBuilt || !phone.matches) return;
      mobileBuilt = true;
      chapters.forEach(chapterRecord => {
        const { chapter, steps, template } = chapterRecord;
        function panel(step, stage = null, parent = null) {
          const section = document.createElement('section');
          section.className = 'mobile-visual';
          section.dataset.scene = stage === null ? step.dataset.s : `walk-${stage}`;
          const el = template.cloneNode(true);
          section.append(el);
          if (parent) parent.append(section);
          else step.after(section);
          const record = createRecord(el, chapter, [step], true, stage);
          if (stage !== null) mobileWalk.push(record);
        }
        if (chapter.dataset.ch === '1') {
          const sequence = document.createElement('div');
          sequence.className = 'mobile-walkthrough';
          const wood = steps.find(step => step.dataset.s === 'wood');
          wood.before(sequence);
          for (let stage = 0; stage < 8; stage++) panel(wood, stage, sequence);
        } else {
          steps.forEach(step => panel(step));
        }
      });
    }

    /* Freeze phone geometry while browser bars expand/collapse. Width changes
       still remeasure, and the two layouts are built once and reused. */
    function measureViewport(force = false) {
      const width = root.clientWidth;
      const height = Math.min(window.innerHeight, root.clientHeight);
      if (!force && phone.matches && Math.abs(width - viewportWidth) < 2) return;
      viewportWidth = width;
      viewportHeight = height;
      root.dataset.storyLayout = phone.matches ? 'flow' : 'side';
      root.style.setProperty('--story-viewport-height', `${height}px`);
      buildMobile();
      records.forEach(record => {
        const box = record.el.getBoundingClientRect();
        const exposed = Math.max(0, Math.min(height, box.bottom) - Math.max(0, box.top));
        setVisibility(record, exposed > 0, box.height ? exposed / box.height : 0);
      });
    }

    function select(record, index) {
      const step = record.steps[index];
      const state = step.dataset.s;
      if (record.state === state) return;
      record.state = state;
      record.el.dataset.state = state;
      record.graphic.go(state);
      if (!record.graphic.visible) record.graphic.pause();
      const description = step.dataset.cap || step.querySelector('h2, h3')?.textContent || '';
      if (record.caption) record.caption.textContent = description;
      const canvas = record.el.querySelector('canvas');
      if (canvas && description) {
        canvas.setAttribute('role', 'img');
        canvas.setAttribute('aria-label', description);
      }
      if (!record.flow) record.steps.forEach((item, i) => item.classList.toggle('on', i === index));
      record.progress?.querySelectorAll('i').forEach((dot, i) => dot.classList.toggle('on', i <= index));
    }

    function update() {
      framePending = false;
      if (phone.matches) return;
      const line = viewportHeight * .55;
      const changes = chapters.map(record => {
        let index = 0;
        record.steps.forEach((step, i) => {
          if (step.getBoundingClientRect().top <= line) index = i;
        });
        let walkStage = 0;
        record.walkTargets.forEach(target => {
          if (target.getBoundingClientRect().top <= line) walkStage = Number(target.dataset.walkStage);
        });
        return [record, index, walkStage];
      });
      changes.forEach(([record, index, walkStage]) => {
        select(record, index);
        if (record.walkTargets.length && record.walkStage !== walkStage) {
          record.walkStage = walkStage;
          record.graphic.showStage(walkStage);
        }
      });
    }

    function schedule() {
      if (framePending) return;
      framePending = true;
      requestAnimationFrame(update);
    }

    function setVisibility(record, inView, ratio) {
      const enabled = record.flow === phone.matches;
      record.inView = enabled && inView;
      const height = record.el.getBoundingClientRect().height;
      const threshold = record.flow ? Math.min(.5, viewportHeight / Math.max(1, height) * .5) : .55;
      const visible = enabled && inView && ratio >= threshold;
      if (record.graphic.visible === visible) return;
      record.graphic.visible = visible;
      if (visible && record.needsReveal) {
        record.needsReveal = false;
        // Measure the transition origins on arrival, after fonts and the
        // current orientation have established the panel's real geometry.
        const walk = record.graphic.walkthrough;
        if (record.stage > 0) walk.go(record.stage - 1);
        walk.go(record.stage, { force: true });
      }
      if (visible) record.graphic.resume();
      else record.graphic.pause();
    }

    measureViewport(true);
    update();
    function frame(now) {
      records.forEach(record => {
        if (record.inView) record.graphic.frame(now);
      });
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);

    addEventListener('scroll', schedule, { passive: true });
    addEventListener('resize', () => { measureViewport(); schedule(); }, { passive: true });
    phone.addEventListener('change', () => { measureViewport(true); schedule(); });
    addEventListener('orientationchange', () => {
      requestAnimationFrame(() => { measureViewport(true); schedule(); });
    }, { passive: true });
    addEventListener('pageshow', () => { measureViewport(true); schedule(); });
    document.fonts?.ready.then(() => { measureViewport(true); schedule(); });

    document.querySelectorAll('.replay').forEach(button => {
      button.addEventListener('click', () => {
        const record = records.find(item => item.flow === phone.matches && item.chapter === button.closest('.chapter') && item.steps.some(step => step.dataset.s === 'prayer'));
        if (!record) return;
        const index = record.steps.findIndex(step => step.dataset.s === 'prayer');
        const target = record.flow ? record.el.parentElement : record.steps[index];
        target.scrollIntoView({ block: 'start', behavior: 'instant' });
        select(record, index);
        record.graphic.replay();
        if (!record.graphic.visible) record.graphic.pause();
        schedule();
      });
    });
    root.dataset.storyReady = 'true';
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
