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
    parser.add_argument("--case", choices=["phone", "small", "landscape"], help="Run one viewport after a targeted fix")
    args = parser.parse_args()
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
        for w, h, lang, motion in cases:
            prefix = f"{args.browser} {lang} {w}x{h} {motion}"
            context = browser.new_context(viewport={"width": w, "height": h},
                                          is_mobile=True, has_touch=True, reduced_motion=motion)
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            cd = context.new_cdp_session(page) if args.browser == "chromium" else None
            url = args.base.rstrip("/") + ("/de/" if lang == "de" else "/")

            def load(reset=False, suffix=""):
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

            try:
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
                load()
                page.evaluate("const c=document.querySelector('.mobile-story-card');scrollTo(0,scrollY+c.getBoundingClientRect().top-innerHeight*.72)")
                page.wait_for_timeout(750)
                drag(w * .55, h * .85, w * .55, h * .24)
                check(page, f"{prefix}: automatic-entry visit survives reload", "!WoodStoryController.current")
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
