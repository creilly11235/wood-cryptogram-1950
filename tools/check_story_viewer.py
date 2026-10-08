#!/usr/bin/env python3
"""Exercise the real mobile article, including trusted native touch input.

Requires Playwright and a local HTTP server for this repository. Example:
  python3 -m http.server 8000
  python3 tools/check_story_viewer.py --base http://127.0.0.1:8000/docs/

Screenshots and JSON results are written outside the repository by default.
The HTML helper separately covers every desktop scroll state and mobile layout.
"""

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:8000/docs/")
    parser.add_argument("--browser", choices=["chromium", "webkit"], default="chromium")
    parser.add_argument("--executable")
    parser.add_argument("--out", default=str(Path(tempfile.gettempdir()) / "wood-story-viewer"))
    parser.add_argument("--quick", action="store_true", help="Run the first phone/language only")
    parser.add_argument("--arrival-only", action="store_true", help="Run Chromium's native late-load arrival regressions only")
    parser.add_argument("--case", choices=["phone", "small", "landscape"], help="Run one viewport after a targeted fix")
    args = parser.parse_args()
    if args.arrival_only and args.browser != "chromium":
        parser.error("--arrival-only requires Chromium native touch input")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []

    def check(page, label, expression):
        value = page.evaluate(expression)
        results.append({"check": label, "passed": bool(value), "value": value})
        print(("PASS " if value else "FAIL ") + label, flush=True)
        return bool(value)

    with sync_playwright() as pw:
        executable = args.executable or (shutil.which("chromium") if args.browser == "chromium" else None)
        browser = getattr(pw, args.browser).launch(
            executable_path=executable,
            headless=True,
            args=["--no-sandbox"] if args.browser == "chromium" else [],
        )
        cases = [(390, 844, "en", "no-preference"), (320, 568, "de", "reduce"),
                 (844, 390, "en", "reduce")]
        if args.quick:
            cases = cases[:1]
        if args.case:
            cases = [{"phone": (390, 844, "en", "no-preference"), "small": (320, 568, "de", "reduce"),
                      "landscape": (844, 390, "en", "reduce")}[args.case]]
        if args.arrival_only:
            cases = [(390, 844, "en", "no-preference")]
        for w, h, lang, motion in cases:
            prefix = f"{args.browser} {lang} {w}x{h} {motion}"
            context = browser.new_context(viewport={"width": w, "height": h},
                                          is_mobile=True, has_touch=True, reduced_motion=motion)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            cd = context.new_cdp_session(page) if args.browser == "chromium" else None
            url = args.base.rstrip("/") + ("/de/" if lang == "de" else "/")

            def load(reset=False, suffix="", refresh=False):
                if refresh:
                    page.reload(wait_until="networkidle")
                else:
                    page.goto(url + suffix, wait_until="networkidle")
                page.wait_for_function("!!window.WoodStoryController")
                if reset:
                    page.evaluate("sessionStorage.clear()")
                    page.reload(wait_until="networkidle")
                    page.wait_for_function("!!window.WoodStoryController")
                page.evaluate("document.fonts.ready")
                page.wait_for_timeout(1000)

            def drag(x0, y0, x1, y1, wait=700, steps=10, delay=30):
                if cd:
                    cd.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y0}]})
                    for i in range(1, steps + 1):
                        cd.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": x0 + (x1 - x0) * i / steps, "y": y0 + (y1 - y0) * i / steps}]})
                        page.wait_for_timeout(delay)
                    cd.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
                else:
                    # WebKit's mobile driver has no native touch/wheel dispatch.
                    # Trusted keyboard input still exercises downward intent.
                    key = "ArrowDown" if y1 < y0 else "ArrowUp"
                    for _ in range(max(1, round(abs(y0 - y1) / 90))):
                        page.keyboard.press(key)
                        page.wait_for_timeout(60)
                page.wait_for_timeout(wait)

            def closed():
                page.wait_for_function("!WoodStoryController.dialog.open && !WoodStoryController.current")
                page.wait_for_timeout(450)

            def open_card(number):
                card = page.locator(f'.mobile-story-card[data-chapter="{number}"]')
                card.scroll_into_view_if_needed()
                page.wait_for_timeout(450)
                check(page, f"{prefix}: programmatic card {number} arrival does not open", "!WoodStoryController.current")
                card.locator(".mobile-story-open").click()
                page.wait_for_function(f"String(WoodStoryController.current?.number)==='{number}'")
                page.wait_for_timeout(600)
                return card

            def geometry(label):
                check(page, f"{prefix}: {label} full screen and modal", """(()=>{
                  const d=WoodStoryController.dialog, b=d.getBoundingClientRect();
                  return d.matches(':modal') && Math.abs(b.top)<2 && Math.abs(b.height-innerHeight)<2 && Math.abs(b.width-innerWidth)<2;
                })()""")
                check(page, f"{prefix}: {label} controls contained", """(()=>{
                  const d=WoodStoryController.dialog, nav=d.querySelector('.mobile-viewer-nav').getBoundingClientRect();
                  const stage=d.querySelector('.mobile-viewer-stage').getBoundingClientRect();
                  return nav.bottom<=innerHeight+1 && stage.bottom<=nav.top+1 && [...d.querySelectorAll('.mobile-viewer-close,.mobile-viewer-prev,.mobile-viewer-next')].every(e=>{
                    const b=e.getBoundingClientRect();return b.width>=43&&b.height>=43&&b.left>=-1&&b.right<=innerWidth+1&&b.top>=-1&&b.bottom<=innerHeight+1;
                  }) && document.documentElement.scrollWidth<=innerWidth+1;
                })()""")

            def expansion_motion():
                # Pause the browser's real animations to exercise layout while
                # the morph is unfinished, independent of machine speed.
                page.evaluate("""()=>{
                  const r=WoodStoryController.records[1];
                  scrollBy({top:r.card.getBoundingClientRect().top-96,behavior:'instant'});
                  WoodStoryController.open(r);
                  window.__viewerEffects=WoodStoryController.dialog.getAnimations({subtree:true});
                  __viewerEffects.forEach(a=>{a.pause();a.currentTime=80;});
                }""")
                page.set_viewport_size({"width": w, "height": max(320, h - 80)})
                page.wait_for_timeout(120)
                check(page, f"{prefix}: toolbar resize preserves unfinished expansion",
                      "WoodStoryController.phase==='opening'")
                page.evaluate("__viewerEffects.forEach(a=>a.finish());delete window.__viewerEffects")
                page.wait_for_function("WoodStoryController.phase==='open'")
                geometry("expansion after toolbar resize")
                page.set_viewport_size({"width": w, "height": h})
                page.wait_for_timeout(100)
                page.evaluate("""()=>{
                  const r=WoodStoryController.current,cv=r.el.querySelector('canvas');
                  window.__viewerCanvasReturns=[];
                  // Resizing a canvas clears its bitmap. Observe the end of
                  // that callback, before another rendered frame can reveal a
                  // blank return card; restore both accessors after the test.
                  const originals={};let pending=false;
                  for(const key of ['width','height']){
                    const native=Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype,key);
                    originals[key]=Object.getOwnPropertyDescriptor(cv,key);
                    Object.defineProperty(cv,key,{configurable:true,get(){return native.get.call(this);},set(value){
                      native.set.call(this,value);
                      if(pending)return;pending=true;
                      queueMicrotask(()=>{
                        pending=false;
                        const pixels=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;
                        __viewerCanvasReturns.push(pixels.some((value,index)=>index%4===3&&value>0));
                      });
                    }});
                  }
                  window.__restoreViewerCanvas=()=>{
                    for(const key of ['width','height']){
                      if(originals[key])Object.defineProperty(cv,key,originals[key]);else delete cv[key];
                    }
                  };
                  WoodStoryController.close(false);
                  window.__viewerEffects=WoodStoryController.dialog.getAnimations({subtree:true});
                  __viewerEffects.forEach(a=>{a.pause();a.currentTime=60;});
                }""")
                check(page, f"{prefix}: closing returns original graphic before the reveal", """(()=>{
                  const r=WoodStoryController.current;
                  return WoodStoryController.phase==='closing'&&r.el.parentNode===r.preview;
                })()""")
                check(page, f"{prefix}: outgoing visual copy is inert and has no duplicate IDs", """(()=>{
                  const copy=document.querySelector('.mobile-viewer-departure');
                  return !!copy&&copy.inert&&copy.getAttribute('aria-hidden')==='true'&&!copy.id&&!copy.querySelector('[id]');
                })()""")
                page.wait_for_function("__viewerCanvasReturns.length>0")
                check(page, f"{prefix}: return canvas is painted in the resize callback",
                      "__viewerCanvasReturns.every(Boolean)")
                page.evaluate("__viewerEffects.forEach(a=>a.finish());__restoreViewerCanvas();delete window.__viewerEffects;delete window.__restoreViewerCanvas;delete window.__viewerCanvasReturns")
                closed()
                check(page, f"{prefix}: expansion cleanup removes visual copies", "!document.querySelector('.mobile-viewer-snapshot,.mobile-viewer-departure')")

            try:
                if cd and w == 390 and h == 844:
                    # Readers can start scrolling once the article is visible,
                    # while an async analytics request is still loading. The
                    # initial pageshow used to clear a genuine native pan here.
                    # Hold that existing request, never the controller or DOM,
                    # then release it during the same fling from the page top.
                    page.add_init_script("""window.__arrivalLoadEvents=[];window.__arrivalMaxY=0;
                      addEventListener('scroll',()=>__arrivalMaxY=Math.max(__arrivalMaxY,scrollY),{passive:true});
                      for(const type of ['load','pageshow','touchend']) addEventListener(type,
                        event=>__arrivalLoadEvents.push({type,time:performance.now(),y:scrollY,
                          persisted:!!event.persisted}),{passive:true});""")
                    held_analytics = []
                    analytics_pattern = "**/gc.zgo.at/count.js"
                    def hold_analytics(route):
                        held_analytics.append(route)
                    page.route(analytics_pattern, hold_analytics)
                    for release_ms in (80, 200, 2500):
                        attempts = []
                        for attempt in range(3):
                            held_analytics.clear()
                            page.goto(url, wait_until="domcontentloaded")
                            page.wait_for_function("!!window.WoodStoryController")
                            page.evaluate("document.fonts.ready")
                            page.wait_for_timeout(300)
                            check(page, f"{prefix}: late-load {release_ms}ms starts before pageshow at page top",
                                  "scrollY===0&&!__arrivalLoadEvents.some(event=>event.type==='pageshow')")
                            if not held_analytics:
                                raise RuntimeError("The existing analytics request was not intercepted")
                            card_top = page.evaluate("WoodStoryController.records[0].card.getBoundingClientRect().top")
                            drag(w * .525, h * .936, w * .525, h * .22,
                                 wait=0, steps=3, delay=8)
                            page.wait_for_timeout(release_ms)
                            released_before_arrival = page.evaluate("!WoodStoryController.current")
                            held_analytics.pop().fulfill(status=200,
                                content_type="application/javascript", body="/* Delayed analytics response */")
                            page.wait_for_timeout(2800)
                            trace = page.evaluate("""({events:__arrivalLoadEvents,maxY:__arrivalMaxY,
                              y:scrollY,cardTop:WoodStoryController.records[0].card.getBoundingClientRect().top,
                              line:innerHeight*.30,current:WoodStoryController.current?.number||null})""")
                            trace["initialCardTop"] = card_top
                            trace["releasedBeforeArrival"] = released_before_arrival
                            attempts.append(trace)
                            # CDP occasionally ends a gesture without inertia.
                            # Retry if it never reaches the card, or arrives
                            # before the delayed response can test the race.
                            # Passing a card unopened is always a hard failure.
                            in_time = released_before_arrival or release_ms >= 1000
                            if in_time and (trace["current"] or trace["maxY"] >= card_top - trace["line"]):
                                break
                        if release_ms < 1000:
                            results.append({"check": f"{prefix}: late-load {release_ms}ms releases during the approach",
                                            "passed": released_before_arrival})
                        reached = bool(trace["current"]) or trace["maxY"] >= card_top - trace["line"]
                        results.append({"check": f"{prefix}: late-load {release_ms}ms native fling reaches entry",
                                        "passed": reached, "value": attempts})
                        check(page, f"{prefix}: late-load {release_ms}ms arrival survives initial pageshow",
                              "String(WoodStoryController.current?.number)==='1'")
                    page.unroute(analytics_pattern, hold_analytics)
                    # A reader can also start panning before the controller
                    # itself arrives. Cover both an ongoing touch and momentum
                    # after fingerlift, with no further touch events to observe.
                    held_controller = []
                    controller_pattern = "**/story-scroll.js*"
                    def hold_controller(route):
                        held_controller.append(route)
                    page.route(controller_pattern, hold_controller)
                    for release in ("during touch", "after fingerlift"):
                        attempts = []
                        for attempt in range(3):
                            held_controller.clear()
                            page.goto(url, wait_until="commit")
                            page.wait_for_function("window.WoodStory && document.querySelector('.chapter')")
                            page.wait_for_timeout(300)
                            check(page, f"{prefix}: controller {release} starts with article visible at page top",
                                  "!window.WoodStoryController&&scrollY===0")
                            cd.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": 205, "y": 790}]})
                            if release == "during touch":
                                cd.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": 205, "y": 760}]})
                                page.wait_for_timeout(20)
                            else:
                                for y in (556, 323, 90):
                                    cd.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": 205, "y": y}]})
                                    page.wait_for_timeout(8)
                                cd.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
                                page.wait_for_timeout(80)
                            if not held_controller:
                                raise RuntimeError("The controller request was not intercepted")
                            held_controller.pop().continue_()
                            page.wait_for_function("!!window.WoodStoryController")
                            check(page, f"{prefix}: controller {release} consumes startup input recorder",
                                  "!window.WoodStoryPendingInput")
                            card_top = page.evaluate("scrollY+WoodStoryController.records[0].card.getBoundingClientRect().top")
                            if release == "during touch":
                                for y in (580, 330, 90):
                                    cd.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": 205, "y": y}]})
                                    page.wait_for_timeout(8)
                                cd.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
                            page.wait_for_timeout(2800)
                            trace = page.evaluate("""({events:__arrivalLoadEvents,maxY:__arrivalMaxY,
                              y:scrollY,cardTop:WoodStoryController.records[0].card.getBoundingClientRect().top,
                              line:innerHeight*.30,current:WoodStoryController.current?.number||null})""")
                            trace["initialCardTop"] = card_top
                            attempts.append(trace)
                            if trace["current"] or trace["maxY"] >= card_top - trace["line"]:
                                break
                        reached = bool(trace["current"]) or trace["maxY"] >= card_top - trace["line"]
                        results.append({"check": f"{prefix}: controller {release} native fling reaches entry",
                                        "passed": reached, "value": attempts})
                        check(page, f"{prefix}: controller {release} accepts the ongoing native pan",
                              "String(WoodStoryController.current?.number)==='1'")
                    page.unroute(controller_pattern, hold_controller)
                if args.arrival_only:
                    results.append({"check": prefix + ": page errors", "passed": not errors, "errors": errors})
                    continue
                load(reset=True)
                check(page, f"{prefix}: initial load does not open", "!WoodStoryController.current")
                if cd:
                    # Begin at the real page top and keep the momentum of an
                    # ordinary brisk phone flick. Preparing a scroll position
                    # immediately above the card hid the former debounce bug:
                    # the card was passed before its delayed entry check ran.
                    check(page, f"{prefix}: fresh flick test starts at page top", "scrollY===0")
                    for _ in range(20):
                        drag(w * .55, h * .85, w * .55, h * .30, wait=600, steps=6, delay=18)
                        if page.evaluate("!!WoodStoryController.current || document.querySelector('.mobile-story-card').getBoundingClientRect().bottom < -innerHeight"):
                            break
                    opened_first = check(page, f"{prefix}: brisk native flicks from page top open first card", "String(WoodStoryController.current?.number)==='1'")
                    if opened_first:
                        geometry("brisk first arrival")
                        check(page, f"{prefix}: arrival gesture keeps first step", "WoodStoryController.current.stage===0")
                        page.locator(".mobile-viewer-close").click()
                        closed()
                        page.wait_for_timeout(800)
                        check(page, f"{prefix}: closing brisk arrival does not reopen or cascade", "!WoodStoryController.current&&!WoodStoryController.dialog.open&&document.body.style.position!=='fixed'")
                        check(page, f"{prefix}: closing brisk arrival returns focus to card", "document.activeElement.closest('.mobile-story-card')!==null")
                    # Read continuously through the real article and complete
                    # each viewer. Testing X on the first card alone does not
                    # cover entry after the final-step Close and focus restore.
                    if w == 390 and h == 844:
                        load(reset=True)
                        for number in range(1, 7):
                            for _ in range(40):
                                if page.evaluate("!!WoodStoryController.current"):
                                    break
                                drag(w * .55, h * .85, w * .55, h * .30,
                                     wait=600, steps=6, delay=18)
                                if page.evaluate(f"!WoodStoryController.current && WoodStoryController.records[{number - 1}].card.getBoundingClientRect().bottom < -innerHeight"):
                                    break
                            entered = check(page, f"{prefix}: continuous reading auto-opens card {number}", f"String(WoodStoryController.current?.number)==='{number}'")
                            if not entered:
                                break
                            page.wait_for_function("WoodStoryController.phase==='open'")
                            total = page.evaluate("WoodStoryController.current.count")
                            for _ in range(total - 1):
                                page.locator(".mobile-viewer-next").tap()
                                page.wait_for_timeout(160)
                            check(page, f"{prefix}: card {number} reaches final Close", "WoodStoryController.current.stage===WoodStoryController.current.count-1")
                            page.locator(".mobile-viewer-next").tap()
                            closed()
                            check(page, f"{prefix}: final Close {number} releases page without cascading", "!WoodStoryController.current&&!WoodStoryController.dialog.open&&document.body.style.position!=='fixed'")
                            if number == 1:
                                page.wait_for_timeout(2400)
                    load(reset=True)
                # Actual downward finger movement carries an unseen card across
                # its entry line. Programmatic preparation has no input intent.
                page.evaluate("const c=document.querySelector('.mobile-story-card');scrollTo(0,scrollY+c.getBoundingClientRect().top-innerHeight*.72)")
                page.wait_for_timeout(750)
                check(page, f"{prefix}: positioning before card does not open", "!WoodStoryController.current")
                drag(w * .55, h * .85, w * .55, h * .24)
                entered = check(page, f"{prefix}: native downward arrival opens first card", "String(WoodStoryController.current?.number)==='1'")
                if not entered:
                    open_card(1)
                geometry("automatic entry")
                check(page, f"{prefix}: initial stage", "WoodStoryController.current.stage===0")
                page.screenshot(path=str(out / f"{args.browser}-{lang}-{w}-open.png"))
                # Vertical dragging is isolated from both article and animation.
                frozen = page.evaluate("({y:scrollY,top:document.body.style.top,stage:WoodStoryController.current.stage})")
                drag(w * .55, h * .75, w * .55, h * .28)
                check(page, f"{prefix}: vertical touch does not advance", f"WoodStoryController.current.stage==={frozen['stage']}")
                check(page, f"{prefix}: vertical touch does not scroll article", f"Math.abs(scrollY-{frozen['y']})<2&&document.body.style.top==={json.dumps(frozen['top'])}")
                if cd:
                    drag(w * .83, h * .50, w * .18, h * .50)
                    check(page, f"{prefix}: horizontal swipe advances", "WoodStoryController.current.stage===1")
                    drag(w * .18, h * .50, w * .83, h * .50)
                    check(page, f"{prefix}: reverse horizontal swipe goes back", "WoodStoryController.current.stage===0")
                    cd.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": w * .32, "y": h * .5}, {"x": w * .67, "y": h * .5}]})
                    cd.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [{"x": w * .19, "y": h * .5}, {"x": w * .78, "y": h * .5}]})
                    cd.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
                    page.wait_for_timeout(300)
                    check(page, f"{prefix}: multi-touch does not advance", "WoodStoryController.current.stage===0")
                    # Pinch zoom is allowed for accessibility. Return to the
                    # initial scale before Playwright's CSS-coordinate clicks.
                    cd.send("Emulation.setPageScaleFactor", {"pageScaleFactor": 1})
                    page.wait_for_timeout(300)
                page.locator(".mobile-viewer-next").click()
                page.locator(".mobile-viewer-close").click()
                closed()
                check(page, f"{prefix}: early X returns focus to card", "document.activeElement.closest('.mobile-story-card')!==null")
                # The first automatic entry is consumed even when exited early.
                drag(w * .55, h * .28, w * .55, h * .79)
                drag(w * .55, h * .82, w * .55, h * .24)
                check(page, f"{prefix}: reversing then revisiting does not auto-open", "!WoodStoryController.current")
                first = page.locator('.mobile-story-card[data-chapter="1"] .mobile-story-preview')
                first.scroll_into_view_if_needed()
                first.tap()
                page.wait_for_function("String(WoodStoryController.current?.number)==='1'")
                page.wait_for_timeout(500)
                check(page, f"{prefix}: tapping the card reopens and resumes", "WoodStoryController.current.stage===1")
                page.keyboard.press("Escape")
                closed()
                check(page, f"{prefix}: Escape returns focus", "document.activeElement.closest('.mobile-story-card')!==null")
                # Old deployments persisted visits for the browser tab. A
                # refresh now resets arrival behavior, including for readers
                # who still have the old storage entry.
                page.evaluate("sessionStorage.setItem('wood-story-viewed-v1', JSON.stringify(['1','2','3','4','5','6']))")
                load(refresh=True)
                check(page, f"{prefix}: reload resets every card's first-arrival state", "WoodStoryController.records.every(record=>!record.opened)")
                page.evaluate("const c=document.querySelector('.mobile-story-card');scrollTo(0,scrollY+c.getBoundingClientRect().top-innerHeight*.72)")
                page.wait_for_timeout(750)
                drag(w * .55, h * .85, w * .55, h * .24)
                reopened = check(page, f"{prefix}: first arrival opens again after reload", "String(WoodStoryController.current?.number)==='1'")
                if reopened:
                    page.wait_for_function("WoodStoryController.phase==='open'")
                    page.locator(".mobile-viewer-close").click()
                    closed()
                # Fresh pages isolate non-downward arrival and browser geometry.
                load(reset=True)
                page.evaluate("const c=document.querySelector('.mobile-story-card');scrollTo(0,scrollY+c.getBoundingClientRect().bottom+50)")
                page.wait_for_timeout(750)
                drag(w * .55, h * .25, w * .55, h * .8)
                check(page, f"{prefix}: upward arrival does not open", "!WoodStoryController.current")
                page.set_viewport_size({"width": h, "height": w})
                page.wait_for_timeout(600)
                check(page, f"{prefix}: rotation does not open", "!WoodStoryController.current")
                page.set_viewport_size({"width": w, "height": h})
                page.wait_for_timeout(600)
                load(reset=True, suffix="#the-hit")
                check(page, f"{prefix}: hash arrival does not open", "!WoodStoryController.current")
                if motion == "no-preference":
                    expansion_motion()
                # Every chart has the same buttons, last-step Close and swipe.
                for number in range(1, 7):
                    card = open_card(number)
                    count = page.evaluate("WoodStoryController.current.count")
                    check(page, f"{prefix}: chart {number} focus is in dialog", "WoodStoryController.dialog.contains(document.activeElement)")
                    if number == 2:
                        trapped = True
                        for _ in range(8):
                            page.keyboard.press("Tab")
                            trapped &= page.evaluate("!document.hasFocus()||WoodStoryController.dialog.contains(document.activeElement)")
                        results.append({"check": prefix + ": Tab stays inside modal", "passed": trapped})
                    for stage in range(count):
                        if stage:
                            page.locator(".mobile-viewer-next").click()
                            page.wait_for_timeout(150)
                        check(page, f"{prefix}: chart {number} Next selects {stage}", f"WoodStoryController.current.stage==={stage}")
                        geometry(f"chart {number} stage {stage}")
                    close_text = "Schließen" if lang == "de" else "Close"
                    check(page, f"{prefix}: chart {number} last button says Close", f"document.querySelector('.mobile-viewer-next').textContent.includes({json.dumps(close_text)})")
                    page.locator(".mobile-viewer-prev").click()
                    s = page.evaluate("WoodStoryController.current.stage")
                    if cd:
                        drag(w * .83, h * .50, w * .18, h * .50)
                        check(page, f"{prefix}: chart {number} supports sideways swipe", f"WoodStoryController.current.stage==={s+1}")
                        page.locator(".mobile-viewer-prev").click()
                    for rw, rh in [(844, 390), (w, max(320, h - 80)), (w, h)]:
                        page.set_viewport_size({"width": rw, "height": rh})
                        page.wait_for_timeout(400)
                        check(page, f"{prefix}: chart {number} rotation/toolbar {rw}x{rh} keeps step", f"WoodStoryController.current.stage==={s}")
                        geometry(f"chart {number} resized {rw}x{rh}")
                    page.locator(".mobile-viewer-next").click()
                    page.locator(".mobile-viewer-next").click()
                    closed()
                    check(page, f"{prefix}: chart {number} final Close restores graphic", f"document.querySelector('.mobile-story-card[data-chapter=\"{number}\"] .graphic')!==null")
                    check(page, f"{prefix}: chart {number} close prevents cascade", "!WoodStoryController.current&&document.body.style.position!=='fixed'")
                # A mobile modal must not leak locks across the desktop breakpoint.
                open_card(2)
                page.set_viewport_size({"width": 1440, "height": 900})
                page.wait_for_timeout(600)
                check(page, f"{prefix}: desktop breakpoint closes and unlocks", "!WoodStoryController.current&&!WoodStoryController.dialog.open&&document.body.style.position!=='fixed'")
                check(page, f"{prefix}: desktop restores six original graphics", "document.querySelectorAll('.chapter > .graphic').length===6&&document.querySelectorAll('.graphic').length===6")
                page.set_viewport_size({"width": w, "height": h})
                page.wait_for_timeout(600)
                check(page, f"{prefix}: returning mobile stays closed", "!WoodStoryController.current&&document.querySelectorAll('.mobile-story-card').length===6")
                check(page, f"{prefix}: no horizontal page overflow", "document.documentElement.scrollWidth<=innerWidth+1")
                if w == 390 and h == 844:
                    load(reset=True)
                    open_card(1)
                    page.locator(".mobile-viewer-close").click()
                    closed()
                    page.evaluate("const c=WoodStoryController.records[1].card;scrollTo(0,scrollY+c.getBoundingClientRect().top-innerHeight*.30-60)")
                    page.wait_for_timeout(800)
                    check(page, f"{prefix}: keyboard continuation starts on restored launch button", "document.activeElement.matches('.mobile-story-open')")
                    page.keyboard.press("PageDown")
                    page.wait_for_timeout(700)
                    check(page, f"{prefix}: PageDown after closing opens the next card", "String(WoodStoryController.current?.number)==='2'")
                results.append({"check": prefix + ": page errors", "passed": not errors, "errors": errors})
            except Exception as error:
                results.append({"check": prefix + ": execution", "passed": False, "error": str(error)})
                page.screenshot(path=str(out / f"{args.browser}-{lang}-{w}-failure.png"))
                print(str(error), flush=True)
            finally:
                context.close()
        browser.close()
    suffix = f"-{args.case}" if args.case else ""
    (out / f"interaction-{args.browser}{suffix}.json").write_text(json.dumps(results, indent=2))
    failures = [item for item in results if not item["passed"]]
    print(json.dumps({"checks": len(results), "failures": failures}, indent=2))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
