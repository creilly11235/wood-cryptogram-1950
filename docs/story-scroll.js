/* Keep the article's own text in charge of the graphic. Native scrolling
   changes the state when the next paragraph reaches the reading area below
   the phone panel (or the middle of the desktop reading column). */
(() => {
  'use strict';

  function start() {
    const api = window.WoodStory;
    if (!api) throw new Error('The Wood graphic factory must load before story-scroll.js');

    const { Graphic } = api;
    const phone = matchMedia('(max-width: 900px)');
    const root = document.documentElement;
    const chapters = [];
    let viewportWidth = 0;
    let viewportHeight = 0;
    let sideBySide = false;
    let framePending = false;

    /* Browser toolbar changes resize the visual viewport on phones. Freeze
       the reading geometry until width/orientation changes so those toolbar
       changes cannot move a paragraph across the activation threshold. */
    function measureViewport(force = false) {
      const width = root.clientWidth;
      const height = window.innerHeight;
      if (!force && phone.matches && Math.abs(width - viewportWidth) < 2) return;
      viewportWidth = width;
      viewportHeight = height;
      // Keep CSS and activation geometry on the same cached layout. A browser
      // toolbar crossing 450px must not rearrange the article during a swipe.
      sideBySide = !phone.matches || (width >= 500 && height <= 450);
      root.dataset.storyLayout = sideBySide ? 'side' : 'stack';
      root.dataset.storyShort = String(height <= 450);
      root.style.setProperty('--story-viewport-height', `${height}px`);
      chapters.forEach(record => {
        record.panelHeight = record.el.getBoundingClientRect().height;
        record.panelTop = parseFloat(getComputedStyle(record.el).top) || 0;
      });
    }

    document.querySelectorAll('.chapter').forEach(chapter => {
      const el = chapter.querySelector('.graphic');
      const steps = [...chapter.querySelectorAll('.step[data-s]')];
      if (!el || !steps.length) return;

      const graphic = new Graphic(el);
      graphic.visible = false;
      const progress = el.querySelector('.progress');
      if (progress) progress.innerHTML = steps.map(() => '<i></i>').join('');
      const record = {
        chapter, el, steps, graphic, progress,
        caption: el.querySelector('.beatcap'),
        state: null,
        panelHeight: 0,
        panelTop: 0,
      };
      chapters.push(record);
      select(record, 0);
    });

    function select(record, index) {
      const step = record.steps[index];
      const state = step.dataset.s;
      if (record.state === state) return;
      record.state = state;
      record.el.dataset.state = state;
      // The factory freezes its own timeline while paused. Starting normally
      // here lets a chapter's first animation play when it enters the viewport.
      record.graphic.go(state);
      if (!record.graphic.visible) record.graphic.pause();

      const description = step.dataset.cap || step.querySelector('h2, h3')?.textContent || '';
      if (record.caption) record.caption.textContent = description;
      const canvas = record.el.querySelector('canvas');
      if (canvas && description) {
        canvas.setAttribute('role', 'img');
        canvas.setAttribute('aria-label', description);
      }
      record.steps.forEach((item, i) => item.classList.toggle('on', i === index));
      record.progress?.querySelectorAll('i').forEach((dot, i) => {
        dot.classList.toggle('on', i <= index);
      });
    }

    function update() {
      framePending = false;
      /* Read all positions before changing any strip text. The threshold is
         48–88px inside the exposed reading area, so the next heading is visible
         as its graphic changes. There is no extra blank scrolling distance. */
      const changes = chapters.map(record => {
        const exposed = Math.max(0, viewportHeight - record.panelHeight - record.panelTop);
        const line = !sideBySide
          ? record.panelTop + record.panelHeight + Math.min(88, Math.max(48, exposed * .2))
          : viewportHeight * .55;
        let index = 0;
        record.steps.forEach((step, i) => {
          if (step.getBoundingClientRect().top <= line) index = i;
        });
        return [record, index];
      });
      changes.forEach(([record, index]) => select(record, index));
    }

    function schedule() {
      if (framePending) return;
      framePending = true;
      requestAnimationFrame(update);
    }

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const record = chapters.find(item => item.el === entry.target);
        const visible = entry.isIntersecting;
        if (record.graphic.visible === visible) return;
        record.graphic.visible = visible;
        if (visible) record.graphic.resume();
        else record.graphic.pause();
      });
    }, { threshold: 0 });

    measureViewport(true);
    update();
    chapters.forEach(record => observer.observe(record.el));

    function frame(now) {
      chapters.forEach(record => {
        if (record.graphic.visible) record.graphic.frame(now);
      });
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);

    addEventListener('scroll', schedule, { passive: true });
    addEventListener('resize', () => {
      measureViewport();
      schedule();
    }, { passive: true });
    phone.addEventListener('change', () => {
      measureViewport(true);
      schedule();
    });
    addEventListener('orientationchange', () => {
      requestAnimationFrame(() => {
        measureViewport(true);
        schedule();
      });
    }, { passive: true });
    addEventListener('pageshow', () => {
      measureViewport(true);
      schedule();
    });
    document.fonts?.ready.then(schedule);

    document.querySelectorAll('.replay').forEach(button => {
      button.addEventListener('click', () => {
        const record = chapters.find(item => item.chapter === button.closest('.chapter'));
        if (!record) return;
        const index = record.steps.findIndex(step => step.dataset.s === 'prayer');
        if (index < 0) return;
        const step = record.steps[index];
        /* Replay stays with its paragraph. The normal trigger reads the same
           target afterward; no delayed animation fights with scrolling. */
        step.scrollIntoView({ block: 'start', behavior: 'instant' });
        select(record, index);
        record.graphic.replay();
        if (!record.graphic.visible) record.graphic.pause();
        schedule();
      });
    });

    /* An explicit marker lets browser checks distinguish initialized state
       from a page that only happened to render the first canvas. */
    root.dataset.storyReady = 'true';
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
