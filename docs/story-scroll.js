/* Desktop follows the reading column. On phones, one full-screen graphic
   advances through a dedicated stretch of native page scrolling, with the
   article outside that stretch. Buttons use the same scroll positions. */
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
    let activeRun = null;

    /* Freeze the distance between states while a phone's browser chrome opens
       or closes. The panel itself can follow 100dvh without moving a state. */
    function measureViewport(force = false, resetGeometry = false) {
      const width = root.clientWidth;
      const height = window.innerHeight;
      const geometryChanged = resetGeometry || !phone.matches || Math.abs(width - viewportWidth) >= 2;
      // Capture the last stable reading position before orientation reflows the
      // article. Height-only browser-toolbar changes never scroll the page.
      const anchor = geometryChanged && phone.matches && !sideBySide ? activeRun : null;
      if (geometryChanged) {
        viewportWidth = width;
        viewportHeight = height;
      }
      sideBySide = !phone.matches;
      root.dataset.storyLayout = sideBySide ? 'side' : 'stack';
      root.dataset.storyShort = String(viewportHeight <= 450);
      root.style.setProperty('--story-viewport-height', `${viewportHeight}px`);
      if (geometryChanged || force) {
        chapters.forEach(record => layout(record, geometryChanged));
      }
      refreshRunHeights();
      if (anchor && anchor.record.run.isConnected) {
        const record = anchor.record;
        window.scrollTo({
          top: window.scrollY + record.run.getBoundingClientRect().top + anchor.progress * record.runStep,
          behavior: 'instant',
        });
      }
      chapters.forEach(record => {
        const box = record.el.getBoundingClientRect();
        record.panelHeight = box.height;
        record.panelTop = parseFloat(getComputedStyle(record.el).top) || 0;
        const exposed = Math.max(0, Math.min(height, box.bottom) - Math.max(0, box.top));
        setVisibility(record, exposed > 0, box.height ? exposed / box.height : 0);
      });
    }

    function layout(record, resetGeometry) {
      if (sideBySide) {
        if (record.run.isConnected) {
          record.home.after(record.el);
          record.run.remove();
        }
        return;
      }
      if (!record.run.isConnected) {
        const wood = record.steps.find(step => step.dataset.s === 'wood');
        if (record.graphic.walkthrough && wood) wood.before(record.run);
        else record.steps[record.steps.length - 1].after(record.run);
        record.run.append(record.el);
      }
      if (resetGeometry || !record.runStep) {
        record.runStep = Math.round(Math.max(140, Math.min(240, viewportHeight * .32)));
        record.runPanelHeight = viewportHeight;
      }
      record.run.style.setProperty('--run-panel-height', `${record.runPanelHeight}px`);
      record.run.style.setProperty('--run-step', `${record.runStep}px`);
      record.run.style.setProperty('--run-travel', `${(record.runCount - 1) * record.runStep}px`);
    }

    /* Offscreen runways keep their last measured height. Otherwise a toolbar
       resize adds its height difference once per earlier chapter and moves the
       current chart to a different state. Refresh only visible/entering runs;
       their own top stays fixed and native touch scrolling stays untouched. */
    function refreshRunHeights() {
      if (sideBySide) return;
      const height = window.innerHeight;
      const visible = chapters.filter(record => {
        if (!record.run.isConnected || record.runPanelHeight === height) return false;
        const box = record.run.getBoundingClientRect();
        return box.bottom > 0 && box.top < height;
      });
      visible.forEach(record => {
        record.runPanelHeight = height;
        record.run.style.setProperty('--run-panel-height', `${height}px`);
      });
    }

    function runIndex(record) {
      return Math.max(0, Math.min(record.runCount - 1,
        Math.round(-record.run.getBoundingClientRect().top / record.runStep)));
    }

    function navigateRun(record, index, behavior) {
      const stage = Math.max(0, Math.min(record.runCount - 1, index));
      window.scrollTo({
        top: window.scrollY + record.run.getBoundingClientRect().top + stage * record.runStep,
        behavior,
      });
      schedule();
    }

    document.querySelectorAll('.chapter').forEach(chapter => {
      const el = chapter.querySelector('.graphic');
      const steps = [...chapter.querySelectorAll('.step[data-s]')];
      if (!el || !steps.length) return;

      const home = document.createComment('Desktop graphic position');
      el.before(home);
      const run = document.createElement('div');
      run.className = 'story-run mobile-visual';
      const graphic = new Graphic(el);
      graphic.visible = false;
      const progress = el.querySelector('.progress');
      if (progress) progress.innerHTML = steps.map(() => '<i></i>').join('');
      const record = {
        chapter, el, steps, graphic, progress, home, run,
        runStep: 0,
        runPanelHeight: 0,
        runCount: graphic.walkthrough ? 8 : steps.length,
        walkTargets: [...chapter.querySelectorAll('[data-walk-stage]')],
        walkStage: -1,
        inView: false,
        caption: el.querySelector('.beatcap'),
        state: null,
        panelHeight: 0,
        panelTop: 0,
      };
      run.dataset.chapter = chapter.dataset.ch;
      run.dataset.stages = String(record.runCount);
      chapters.push(record);
      if (graphic.walkthrough) {
        graphic.walkthrough.enableSwipes();
        graphic.walkthrough.onNavigate = stage => {
          if (!sideBySide) {
            navigateRun(record, stage, api.reduced ? 'instant' : 'smooth');
            return;
          }
          const target = record.walkTargets.find(item => Number(item.dataset.walkStage) === stage);
          if (!target) return;
          const next = record.walkTargets.find(item => Number(item.dataset.walkStage) === stage + 1);
          const box = target.getBoundingClientRect();
          // Land inside this paragraph's range, leaving a little room to scroll
          // either way without immediately undoing the button selection.
          const inset = next ? Math.min(32, (next.getBoundingClientRect().top - box.top) / 2) : 32;
          window.scrollTo({
            top: window.scrollY + box.top - readingLine(record) + inset,
            behavior: api.reduced ? 'instant' : 'smooth',
          });
          schedule();
        };
      }
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

    function readingLine() {
      return viewportHeight * .55;
    }

    function update() {
      framePending = false;
      refreshRunHeights();
      // Remember progress only at the measured width; a pending resize may have
      // already reflowed the DOM before its geometry callback has run.
      if (root.clientWidth === viewportWidth) {
        activeRun = null;
        if (!sideBySide) {
          chapters.some(record => {
            const box = record.run.getBoundingClientRect();
            if (box.top > 1 || box.bottom < window.innerHeight - 1) return false;
            activeRun = {record, progress: Math.max(0, Math.min(record.runCount - 1, -box.top / record.runStep))};
            return true;
          });
        }
      }
      /* Read every position first. A phone's stage depends only on its own
         native scroll run; no paragraph can show through behind the graphic. */
      const changes = chapters.map(record => {
        if (!sideBySide) {
          const stage = runIndex(record);
          // The opening graphic has eight stages but only three prose states.
          // Its visual stage is independent of the article's paragraph labels.
          const index = record.graphic.walkthrough ? (stage === 0 ? 0 : stage === 7 ? 2 : 1) : stage;
          return [record, index, record.graphic.walkthrough ? stage : 0];
        }
        const line = readingLine();
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
      record.inView = inView;
      /* Let a new panel arrive before starting its reveal. Otherwise a
         phone chart can finish animating while only its heading is visible
         below the preceding section. Keep painting its paused baseline as
         it enters, then play when the chart can actually be read. */
      const visible = ratio >= (sideBySide ? .55 : .9);
      if (record.graphic.visible === visible) return;
      record.graphic.visible = visible;
      if (visible) record.graphic.resume();
      else record.graphic.pause();
    }

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const record = chapters.find(item => item.el === entry.target);
        setVisibility(record, entry.isIntersecting, entry.intersectionRatio);
      });
    }, { threshold: [0, .55, .9] });

    measureViewport(true);
    update();
    chapters.forEach(record => observer.observe(record.el));

    function frame(now) {
      chapters.forEach(record => {
        if (record.inView) record.graphic.frame(now);
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
        measureViewport(true, true);
        schedule();
      });
    }, { passive: true });
    addEventListener('pageshow', () => {
      measureViewport(true);
      schedule();
    });
    document.fonts?.ready.then(() => { measureViewport(true); schedule(); });

    document.querySelectorAll('.replay').forEach(button => {
      button.addEventListener('click', () => {
        const record = chapters.find(item => item.chapter === button.closest('.chapter'));
        if (!record) return;
        const index = record.steps.findIndex(step => step.dataset.s === 'prayer');
        if (index < 0) return;
        const step = record.steps[index];
        /* Replay and ordinary navigation land on the same activation point. */
        if (sideBySide) step.scrollIntoView({ block: 'start', behavior: 'instant' });
        else navigateRun(record, index, 'instant');
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
