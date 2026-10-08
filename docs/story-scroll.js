/* Desktop follows the reading column. Mobile offers one preview card per
   chapter, opening into a button/swipe-driven dialog on its first arrival. */
(() => {
  'use strict';

  function start() {
    const api = window.WoodStory;
    if (!api) throw new Error('The Wood graphic factory must load before story-scroll.js');
    const mobile = matchMedia('(max-width: 900px)');
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const root = document.documentElement;
    const records = [];
    const german = root.lang.startsWith('de');
    const labels = german ? {
      explore: 'Animation ansehen', resume: 'Animation fortsetzen', replay: 'Animation wiederholen',
      close: 'Schließen', dismiss: 'Animation schließen und zum Artikel zurückkehren',
      previous: 'Vorheriger Schritt', next: 'Weiter', navigation: 'Animationsschritte',
      steps: count => `${count} Schritte`, step: (index, count) => `Schritt ${index} von ${count}`,
    } : {
      explore: 'Explore animation', resume: 'Continue animation', replay: 'Replay animation',
      close: 'Close', dismiss: 'Close animation and return to the article',
      previous: 'Previous step', next: 'Next', navigation: 'Animation steps',
      steps: count => `${count} steps`, step: (index, count) => `Step ${index} of ${count}`,
    };
    const storageKey = 'wood-story-viewed-v1';
    let visited;
    try { visited = new Set(JSON.parse(sessionStorage.getItem(storageKey) || '[]')); }
    catch (_) { visited = new Set(); }
    let current = null;
    let phase = 'closed';
    let transition = null;
    let transitionToken = 0;
    let lockedPosition = 0;
    let lockedCardTop = 0;
    let originalBodyStyle = null;
    let returnFocus = null;
    let framePending = false;
    let lastY = window.scrollY;
    let viewportWidth = 0;
    let pageTouch = null;
    let userScrollUntil = 0;
    let suppressAutoUntil = performance.now() + 700;

    function node(tag, className, text) {
      const el = document.createElement(tag);
      if (className) el.className = className;
      if (text !== undefined) el.textContent = text;
      return el;
    }
    function button(className, text, callback) {
      const el = node('button', className, text);
      el.type = 'button';
      el.addEventListener('click', callback);
      return el;
    }
    function labelButton(el, text, direction) {
      const children = text ? [document.createTextNode(text)] : [];
      if (direction) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('width', '18');
        svg.setAttribute('height', '18');
        svg.setAttribute('aria-hidden', 'true');
        svg.setAttribute('focusable', 'false');
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '1.75');
        svg.setAttribute('stroke-linecap', 'round');
        svg.setAttribute('stroke-linejoin', 'round');
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', direction === 'back' ? 'M19 12H5m6-6-6 6 6 6' : direction === 'expand' ? 'M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5' : 'M5 12h14m-6-6 6 6-6 6');
        svg.append(path);
        children.push(svg);
      }
      el.replaceChildren(...children);
    }
    function setPhase(next) {
      phase = next;
      root.dataset.viewerOpen = String(next !== 'closed');
      dialog.dataset.phase = next;
    }
    function suppressAuto(duration = 500) {
      userScrollUntil = 0;
      suppressAutoUntil = performance.now() + duration;
    }
    function rememberPositions() {
      records.forEach(record => { record.previousTop = record.card.getBoundingClientRect().top; });
      lastY = window.scrollY;
    }

    const dialog = node('dialog', 'mobile-story-dialog mobile-visual');
    dialog.setAttribute('aria-labelledby', 'mobile-viewer-title');
    const frame = node('div', 'mobile-viewer-frame');
    const header = node('header', 'mobile-viewer-header');
    const title = node('h2', 'mobile-viewer-title');
    title.id = 'mobile-viewer-title';
    const dismiss = button('mobile-viewer-close', '×', () => close());
    dismiss.setAttribute('aria-label', labels.dismiss);
    const stageHost = node('div', 'mobile-viewer-stage');
    const nav = node('nav', 'mobile-viewer-nav');
    nav.setAttribute('aria-label', labels.navigation);
    const previous = button('mobile-viewer-prev', '', () => advance(-1));
    labelButton(previous, '', 'back');
    previous.setAttribute('aria-label', labels.previous);
    const count = node('span', 'mobile-viewer-count');
    count.setAttribute('aria-live', 'polite');
    count.setAttribute('aria-atomic', 'true');
    const next = button('mobile-viewer-next', labels.next, () => {
      if (!current || phase !== 'open') return;
      if (current.stage === current.count - 1) close(true);
      else advance(1);
    });
    header.append(title, dismiss);
    nav.append(previous, count, next);
    frame.append(header, stageHost, nav);
    dialog.append(frame);
    document.body.append(dialog);
    dialog.addEventListener('cancel', event => { event.preventDefault(); close(); });

    document.querySelectorAll('.chapter').forEach(chapter => {
      const el = chapter.querySelector('.graphic');
      const steps = [...chapter.querySelectorAll('.step[data-s]')];
      if (!el || !steps.length) return;
      const home = document.createComment('Desktop graphic position');
      el.before(home);
      const graphic = new api.Graphic(el);
      graphic.visible = false;
      const number = chapter.dataset.ch;
      const card = node('section', 'mobile-story-card');
      card.dataset.chapter = number;
      const preview = node('div', 'mobile-story-preview');
      preview.setAttribute('role', 'button');
      preview.setAttribute('tabindex', '0');
      preview.setAttribute('aria-haspopup', 'dialog');
      const footer = node('footer', 'mobile-story-footer');
      const launch = button('mobile-story-open', labels.explore, () => open(record, launch));
      launch.setAttribute('aria-haspopup', 'dialog');
      const detail = node('span', 'mobile-story-detail');
      footer.append(launch, detail);
      card.append(preview, footer);
      const record = {
        number, chapter, el, graphic, home, steps, card, preview, launch, detail,
        title: el.querySelector('.gbar .ct')?.textContent.trim() || '',
        stage: 0, count: graphic.walkthrough ? 8 : steps.length,
        opened: visited.has(number), completed: false, previousTop: Infinity,
        renderMode: null, desktopState: null, desktopStage: -1,
        walkTargets: [...chapter.querySelectorAll('[data-walk-stage]')],
      };
      card.dataset.stages = String(record.count);
      detail.textContent = labels.steps(record.count);
      preview.addEventListener('click', () => open(record, preview));
      preview.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          open(record, preview);
        }
      });
      const progress = el.querySelector('.progress');
      if (progress) progress.innerHTML = steps.map(() => '<i></i>').join('');
      if (graphic.walkthrough) {
        // The shared mobile viewer owns swipes; desktop buttons follow prose.
        graphic.walkthrough.onNavigate = index => {
          if (mobile.matches) {
            if (current === record) setStage(record, index);
            return;
          }
          const target = record.walkTargets.find(item => Number(item.dataset.walkStage) === index);
          if (!target) return;
          const following = record.walkTargets.find(item => Number(item.dataset.walkStage) === index + 1);
          const box = target.getBoundingClientRect();
          const inset = following ? Math.min(32, (following.getBoundingClientRect().top - box.top) / 2) : 32;
          window.scrollTo({top: window.scrollY + box.top - innerHeight * .55 + inset, behavior: reduced.matches ? 'instant' : 'smooth'});
          schedule();
        };
      }
      records.push(record);
      updateControls(record);
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
      record.el.querySelectorAll('.progress i').forEach((dot, i) => dot.classList.toggle('on', i <= index));
    }

    function updateControls(record) {
      const label = record.completed ? labels.replay : record.opened ? labels.resume : labels.explore;
      labelButton(record.launch, '', 'expand');
      record.launch.setAttribute('aria-label', `${label}: ${record.title}`);
      record.preview.setAttribute('aria-label', `${label}: ${record.title}`);
      record.card.dataset.stage = String(record.stage);
      record.card.dataset.opened = String(record.opened);
      record.card.dataset.completed = String(record.completed);
      if (current !== record) return;
      previous.disabled = record.stage === 0;
      count.textContent = `${record.stage + 1} / ${record.count}`;
      count.setAttribute('aria-label', labels.step(record.stage + 1, record.count));
      labelButton(next, record.stage === record.count - 1 ? labels.close : labels.next, record.stage === record.count - 1 ? null : 'forward');
      dialog.dataset.chapter = record.number;
      dialog.dataset.stage = String(record.stage);
    }

    function setStage(recordOrNumber, requested, force = false) {
      const record = typeof recordOrNumber === 'object' ? recordOrNumber : records.find(item => item.number === String(recordOrNumber));
      if (!record || !Number.isFinite(requested)) return;
      const stage = Math.max(0, Math.min(record.count - 1, Math.round(requested)));
      const changed = record.stage !== stage || record.renderMode !== 'mobile';
      record.stage = stage;
      record.renderMode = 'mobile';
      const index = record.graphic.walkthrough ? (stage === 0 ? 0 : stage === 7 ? 2 : 1) : stage;
      if (changed || force) {
        record.graphic.go(record.steps[index].dataset.s);
        if (record.graphic.walkthrough) record.graphic.showStage(stage);
        if (force && !changed) record.graphic.replay();
        describe(record, index);
        if (!record.graphic.visible) record.graphic.pause();
      }
      updateControls(record);
      updateVisibility();
    }

    function advance(direction) {
      if (!current || phase !== 'open') return;
      setStage(current, current.stage + direction);
    }

    function lockPage() {
      lockedPosition = window.scrollY;
      lockedCardTop = current.card.getBoundingClientRect().top;
      originalBodyStyle = document.body.getAttribute('style');
      Object.assign(document.body.style, {
        position: 'fixed', top: `${-lockedPosition}px`, left: '0', right: '0', width: '100%',
      });
      document.body.classList.add('story-viewer-open');
    }
    function unlockPage() {
      if (originalBodyStyle === null) document.body.removeAttribute('style');
      else document.body.setAttribute('style', originalBodyStyle);
      document.body.classList.remove('story-viewer-open');
      window.scrollTo({top: lockedPosition, behavior: 'instant'});
    }

    function cardTransform(record) {
      const card = record.card.getBoundingClientRect();
      const target = frame.getBoundingClientRect();
      return `translate(${card.left - target.left}px, ${card.top - target.top}px) scale(${card.width / target.width}, ${card.height / target.height})`;
    }
    async function animateFrame(record, opening, interrupted = null) {
      if (reduced.matches || typeof frame.animate !== 'function') return;
      const compact = {transform: cardTransform(record), borderRadius: '18px'};
      const full = {transform: 'translate(0, 0) scale(1)', borderRadius: '0px'};
      const animation = frame.animate(opening ? [compact, full] : [interrupted || full, compact], {
        duration: opening ? 420 : 340, easing: 'cubic-bezier(.22,.8,.22,1)', fill: 'both',
      });
      transition = animation;
      try { await animation.finished; } catch (_) { /* Resizing safely settles the current transition. */ }
      if (transition === animation) transition = null;
      animation.cancel();
    }

    async function open(recordOrNumber, source) {
      const record = typeof recordOrNumber === 'object' ? recordOrNumber : records.find(item => item.number === String(recordOrNumber));
      if (!record || current || !mobile.matches) return;
      suppressAuto();
      returnFocus = source || record.launch;
      visited.add(record.number);
      try { sessionStorage.setItem(storageKey, JSON.stringify([...visited])); }
      catch (_) { /* The current page still remembers visits when storage is unavailable. */ }
      record.opened = true;
      if (record.completed) {
        record.completed = false;
        setStage(record, 0, true);
      }
      current = record;
      const token = ++transitionToken;
      setPhase('opening');
      title.textContent = record.title;
      record.card.dataset.viewerActive = 'true';
      lockPage();
      stageHost.append(record.el);
      dialog.showModal();
      updateControls(record);
      updateVisibility();
      dismiss.focus({preventScroll: true});
      await animateFrame(record, true);
      if (token !== transitionToken || current !== record) return;
      setPhase('open');
      updateVisibility();
    }

    function finishClose(record, completed, restoreFocus) {
      transitionToken++;
      transition?.cancel();
      transition = null;
      record.completed = completed;
      record.preview.append(record.el);
      record.card.dataset.viewerActive = 'false';
      current = null;
      setPhase('closed');
      if (dialog.open) dialog.close();
      unlockPage();
      suppressAuto(700);
      if (restoreFocus && returnFocus?.isConnected) returnFocus.focus({preventScroll: true});
      updateControls(record);
      rememberPositions();
      updateVisibility();
    }

    async function close(completed = current?.stage === current?.count - 1, immediate = false) {
      if (!current || phase === 'closing') return;
      const record = current;
      const token = ++transitionToken;
      const style = transition ? getComputedStyle(frame) : null;
      const interrupted = style ? {transform: style.transform, borderRadius: style.borderRadius} : null;
      transition?.cancel();
      transition = null;
      setPhase('closing');
      updateVisibility();
      if (!immediate) await animateFrame(record, false, interrupted);
      if (token !== transitionToken || current !== record) return;
      finishClose(record, Boolean(completed), mobile.matches);
    }

    function layout() {
      const widthChanged = root.clientWidth !== viewportWidth;
      viewportWidth = root.clientWidth;
      // Browser toolbar height changes belong to the current native gesture.
      // Only a width/breakpoint change invalidates its arrival measurements.
      if (widthChanged) suppressAuto(400);
      root.dataset.storyLayout = mobile.matches ? 'stack' : 'side';
      root.style.setProperty('--story-viewport-height', `${innerHeight}px`);
      const desktopReturn = !mobile.matches && current ? {record: current, stage: current.stage} : null;
      if (desktopReturn) finishClose(current, current.stage === current.count - 1, false);
      if (widthChanged && current) {
        // Rotation reflows the article underneath its fixed-body scroll lock.
        // Keep the originating card visible for the return morph, adjusting the
        // stored document offset rather than restoring an obsolete pixel offset.
        const box = current.card.getBoundingClientRect();
        const target = Math.max(16, Math.min(lockedCardTop, Math.max(16, innerHeight - box.height - 24)));
        lockedPosition = Math.max(0, lockedPosition + box.top - target);
        document.body.style.top = `${-lockedPosition}px`;
        lockedCardTop = target;
      }
      // A toolbar resize must not dismiss the viewer or change its selected step.
      if (transition) transition.finish();
      records.forEach(record => {
        if (mobile.matches) {
          if (!record.card.isConnected) {
            const wood = record.steps.find(step => step.dataset.s === 'wood');
            if (record.graphic.walkthrough && wood) wood.before(record.card);
            else record.steps[record.steps.length - 1].after(record.card);
          }
          if (current !== record && record.el.parentNode !== record.preview) record.preview.append(record.el);
          if (record.renderMode !== 'mobile') setStage(record, record.stage, true);
        } else {
          if (record.card.isConnected) {
            record.home.after(record.el);
            record.card.remove();
          }
          if (record.renderMode !== 'desktop') {
            record.renderMode = 'desktop';
            record.desktopState = null;
            record.desktopStage = -1;
          }
        }
      });
      if (desktopReturn) {
        // A tablet can cross the breakpoint on rotation. Return to the same
        // scene's prose in the desktop column, rather than an obsolete offset.
        const record = desktopReturn.record;
        const target = record.graphic.walkthrough
          ? record.walkTargets.find(item => Number(item.dataset.walkStage) === desktopReturn.stage)
          : record.steps[desktopReturn.stage];
        if (target) {
          target.setAttribute('tabindex', '-1');
          target.focus({preventScroll: true});
          window.scrollTo({top: window.scrollY + target.getBoundingClientRect().top - innerHeight * .55 + 18, behavior: 'instant'});
        }
      }
      if (widthChanged) rememberPositions();
      update();
    }

    function updateVisibility() {
      records.forEach(record => {
        const box = record.el.getBoundingClientRect();
        const visible = current ? current === record && phase === 'open' : box.height > 0 && box.bottom > 0 && box.top < innerHeight;
        record.inView = box.height > 0 && box.bottom > 0 && box.top < innerHeight;
        if (record.graphic.visible === visible) return;
        record.graphic.visible = visible;
        if (visible) record.graphic.resume();
        else record.graphic.pause();
      });
    }

    function update() {
      framePending = false;
      if (!mobile.matches) {
        records.forEach(record => {
          let index = 0;
          record.steps.forEach((step, i) => { if (step.getBoundingClientRect().top <= innerHeight * .55) index = i; });
          const state = record.steps[index].dataset.s;
          if (record.desktopState !== state) {
            record.desktopState = state;
            record.graphic.go(state);
            describe(record, index);
            if (!record.graphic.visible) record.graphic.pause();
          }
          if (record.graphic.walkthrough) {
            let stage = 0;
            record.walkTargets.forEach(target => { if (target.getBoundingClientRect().top <= innerHeight * .55) stage = Number(target.dataset.walkStage); });
            if (record.desktopStage !== stage) {
              record.desktopStage = stage;
              record.graphic.showStage(stage);
            }
          }
        });
      }
      updateVisibility();
    }
    function schedule() {
      if (framePending) return;
      framePending = true;
      requestAnimationFrame(update);
    }

    function scroll() {
      if (current) return;
      const y = window.scrollY;
      const delta = y - lastY;
      const now = performance.now();
      const eligible = mobile.matches && (window.visualViewport?.scale || 1) <= 1.01 && now > suppressAutoUntil && now < userScrollUntil;
      const line = innerHeight * .30;
      let arrival = null;
      records.forEach(record => {
        const box = record.card.getBoundingClientRect();
        if (!arrival && eligible && delta > 0 && !visited.has(record.number) && box.top <= line &&
            (record.previousTop > line || box.bottom > line)) arrival = record;
        record.previousTop = box.top;
      });
      lastY = y;
      if (arrival) {
        // Capture arrival during the scroll itself. Waiting for momentum to
        // stop lets an ordinary phone flick carry the card out of view.
        const box = arrival.card.getBoundingClientRect();
        if (box.top < 0) {
          // Browsers can combine several scroll updates into one. Keep the
          // crossed card visible as the viewer expands and when it closes.
          const top = Math.max(16, Math.min(line, innerHeight - box.height - 16));
          window.scrollTo({top: window.scrollY + box.top - top, behavior: 'instant'});
        }
        open(arrival);
      }
      schedule();
    }
    addEventListener('scroll', scroll, {passive: true});
    const scrollingIntent = event => {
      if (!event.isTrusted || current) return;
      if (event.type === 'keydown' && (!['ArrowDown', 'PageDown', ' '].includes(event.key) || event.target.closest('button, input, textarea, select, [contenteditable]'))) return;
      if (event.type === 'wheel' && event.deltaY <= 0) return;
      if (event.type === 'touchmove') {
        if (!pageTouch || event.touches.length !== 1 || (window.visualViewport?.scale || 1) > 1.01) {
          pageTouch = null;
          return;
        }
        const touch = event.touches[0];
        const dy = pageTouch.y - touch.clientY;
        const dx = Math.abs(pageTouch.x - touch.clientX);
        if (dy < 5 || dy <= dx) return;
      }
      userScrollUntil = performance.now() + 1800;
      suppressAutoUntil = 0;
    };
    addEventListener('touchstart', event => {
      if (!event.isTrusted || current || event.touches.length !== 1) {
        pageTouch = null;
        if (event.touches.length > 1) suppressAuto();
        return;
      }
      pageTouch = {x: event.touches[0].clientX, y: event.touches[0].clientY};
      // Scroll direction comes from scrollY. Arm before the browser takes over
      // a native pan, which can cancel delivery of subsequent touch events.
      if ((window.visualViewport?.scale || 1) <= 1.01) {
        userScrollUntil = performance.now() + 1800;
        suppressAutoUntil = 0;
      }
    }, {passive: true});
    addEventListener('touchcancel', () => { pageTouch = null; }, {passive: true});
    addEventListener('wheel', scrollingIntent, {passive: true});
    addEventListener('touchmove', scrollingIntent, {passive: true});
    addEventListener('keydown', scrollingIntent);
    document.addEventListener('click', event => {
      if (event.target.closest('a[href*="#"]')) suppressAuto();
    }, {capture: true});
    addEventListener('hashchange', () => { suppressAuto(); rememberPositions(); });
    addEventListener('pageshow', () => { suppressAuto(); layout(); });
    addEventListener('resize', layout, {passive: true});
    mobile.addEventListener('change', layout);
    document.fonts?.ready.then(layout);

    let swipe = null;
    let ignoreClickUntil = 0;
    stageHost.addEventListener('touchstart', event => {
      swipe = null;
      if (phase !== 'open' || event.touches.length !== 1 || (window.visualViewport?.scale || 1) > 1.01 || event.target.closest('button, a, input, select, textarea')) return;
      const touch = event.touches[0];
      swipe = {id: touch.identifier, x: touch.clientX, y: touch.clientY, direction: null, started: performance.now()};
    }, {passive: true});
    stageHost.addEventListener('touchmove', event => {
      if (!swipe || event.touches.length !== 1) { swipe = null; return; }
      const touch = event.touches[0];
      const dx = touch.clientX - swipe.x, dy = touch.clientY - swipe.y;
      if (!swipe.direction && Math.max(Math.abs(dx), Math.abs(dy)) > 12) swipe.direction = Math.abs(dx) > Math.abs(dy) * 1.3 ? 'horizontal' : 'vertical';
    }, {passive: true});
    stageHost.addEventListener('touchend', event => {
      const origin = swipe;
      swipe = null;
      if (!origin || origin.direction !== 'horizontal' || phase !== 'open' || performance.now() - origin.started > 1500) return;
      const touch = [...event.changedTouches].find(item => item.identifier === origin.id);
      if (!touch) return;
      const dx = touch.clientX - origin.x, dy = touch.clientY - origin.y;
      if (Math.abs(dx) < Math.max(42, Math.min(65, innerWidth * .12)) || Math.abs(dx) < Math.abs(dy) * 1.3) return;
      ignoreClickUntil = performance.now() + 350;
      advance(dx < 0 ? 1 : -1);
    }, {passive: true});
    stageHost.addEventListener('touchcancel', () => { swipe = null; }, {passive: true});
    stageHost.addEventListener('click', event => {
      if (performance.now() < ignoreClickUntil) { event.preventDefault(); event.stopPropagation(); }
    }, {capture: true});
    // Fixed body keeps the article still on iOS. Prevent single-finger rubber
    // banding inside the dialog, while allowing multi-touch browser zoom.
    dialog.addEventListener('touchmove', event => {
      if (event.touches.length === 1 && (window.visualViewport?.scale || 1) <= 1.01 && event.cancelable) event.preventDefault();
    }, {passive: false});
    dialog.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight'].includes(event.key) || event.target.closest('input, textarea, select, [contenteditable]')) return;
      event.preventDefault();
      advance(event.key === 'ArrowRight' ? 1 : -1);
    });

    document.querySelectorAll('.replay').forEach(button => button.addEventListener('click', () => {
      const record = records.find(item => item.chapter === button.closest('.chapter'));
      if (!record) return;
      if (mobile.matches) {
        record.completed = false;
        setStage(record, 0, true);
        open(record, button);
      } else {
        const index = record.steps.findIndex(step => step.dataset.s === 'prayer');
        if (index >= 0) record.steps[index].scrollIntoView({block: 'start', behavior: 'instant'});
        record.graphic.replay();
        schedule();
      }
    }));

    function paint(now) {
      records.forEach(record => { if (record.inView) record.graphic.frame(now); });
      requestAnimationFrame(paint);
    }
    layout();
    requestAnimationFrame(paint);
    root.dataset.storyReady = 'true';
    window.WoodStoryController = {records, open, close, setStage, dialog,
      get current() { return current; }, get phase() { return phase; }};
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once: true});
  else start();
})();
