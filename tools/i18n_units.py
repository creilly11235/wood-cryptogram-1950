"""Translation units of docs/index.html: exact source slices that the German build replaces.

Units are the inner HTML of leaf text blocks (p, li, h1, h2, h3, td, th, figcaption, button, the graphic bar names)
plus the text attributes readers or assistive tech see (data-cap, alt, aria-label) and the page's title and
description tags. Anything inside an element marked translate="no" is left out.
"""
import re
from html.parser import HTMLParser

BLOCKS = {"p", "li", "h1", "h2", "h3", "td", "th", "figcaption", "button"}
ATTRS = ("data-cap", "alt", "aria-label")
VOID = {"br", "img", "meta", "link", "input", "hr", "source"}

def _offsets(text):
    starts, pos = [0], 0
    for line in text.splitlines(keepends=True):
        pos += len(line); starts.append(pos)
    return starts

class _P(HTMLParser):
    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src, self.lines, self.stack, self.units = src, _offsets(src), [], []
    def _pos(self):
        line, col = self.getpos(); return self.lines[line - 1] + col
    def handle_starttag(self, tag, attrs):
        a = dict(attrs); start = self._pos(); end = start + len(self.get_starttag_text())
        blocked = any(f.get("no") for f in self.stack) or a.get("translate") == "no"
        for name in ATTRS:
            v = a.get(name)
            if v and not blocked and re.search(r"[a-z]{2,}", v):
                raw = re.search(name + r'="([^"]*)"', self.get_starttag_text())
                if raw: self.units.append(("attr", raw.group(1)))
        if tag in VOID: return
        is_ct = tag == "span" and a.get("class") == "ct"
        self.stack.append({"tag": tag, "inner": end, "block": tag in BLOCKS or is_ct, "no": blocked, "nested": False})
        if tag in BLOCKS:
            for f in self.stack[:-1]:
                if f["block"]: f["nested"] = True
    def handle_endtag(self, tag):
        if tag in VOID: return
        while self.stack:
            f = self.stack.pop()
            if f["tag"] == tag: break
        else: return
        if f["block"] and not f["nested"] and not f["no"]:
            inner = self.src[f["inner"]:self._pos()]
            if re.search(r"[a-z]{2,}", re.sub(r"<[^>]+>", "", inner)): self.units.append((tag, inner))

def units(html):
    head, body = html[:html.index("<body>")], html[html.index("<body>"):html.index("<script")]
    out = [("title", re.search(r"<title>(.*?)</title>", head).group(1))]
    for m in re.finditer(r'<meta (?:name|property)="(?:description|og:title|og:description|og:image:alt)" content="([^"]*)">', head):
        out.append(("meta", m.group(1)))
    p = _P(body); p.feed(body); out += p.units
    seen, uniq = set(), []
    for k, t in out:
        if t not in seen: seen.add(t); uniq.append({"kind": k, "en": t})
    return uniq

if __name__ == "__main__":
    import json, sys
    u = units(open(sys.argv[1], encoding="utf-8").read())
    json.dump(u, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(u), "units,", sum(len(re.sub(r"<[^>]+>", "", x["en"]).split()) for x in u), "words")
