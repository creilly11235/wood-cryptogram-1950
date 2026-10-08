"""Build docs/de/index.html, the German page, from docs/index.html and i18n/de.json.

Fails if any English unit or script string in the table no longer exists in the English page,
and if any English unit of the page has no German entry, so English edits cannot drift silently.
Run from the repository root:  python3 tools/build_de.py
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from i18n_units import units

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://creilly11235.github.io/wood-cryptogram-1950/"
en = (ROOT / "docs/index.html").read_text(encoding="utf-8")
table = json.loads((ROOT / "i18n/de.json").read_text(encoding="utf-8"))

problems = []
known = {u["en"] for u in table["units"]}
for u in units(en):
    if u["en"] not in known:
        problems.append("untranslated unit: " + u["en"][:90])

body_start = en.index("<body>")
cut = en.index("<script", body_start)
head, body, script = en[:body_start], en[body_start:cut], en[cut:]

def swap(text, a, b, where):
    if a not in text:
        problems.append(f"{where}: not found: {a[:90]}")
        return text
    return text.replace(a, b)

# longest first, and always with its delimiters, so a short unit never lands inside a longer one
for u in sorted(table["units"], key=lambda u: -len(u["en"])):
    a, b = u["en"], u["de"]
    if u["kind"] == "title":
        head = swap(head, f"<title>{a}</title>", f"<title>{b}</title>", "title")
        # Unit extraction deduplicates identical text across title, metadata and H1.
        head = head.replace(f'content="{a}"', f'content="{b}"')
        body = body.replace(f"<h1>{a}</h1>", f"<h1>{b}</h1>")
    elif u["kind"] == "meta":
        head = swap(head, f'content="{a}"', f'content="{b}"', "meta")
    else:
        # a sentence can serve as an attribute and as visible text (an alt text repeated as its caption)
        forms = [(f'="{a}"', f'="{b}"'), (">" + a + "</", ">" + b + "</")]
        hit = [f for f in forms if f[0] in body]
        if not hit:
            body = swap(body, a, b, u["kind"])
        for x, y in hit:
            body = body.replace(x, y)
for j in sorted(table["js"], key=lambda j: -len(j["en"])):
    script = swap(script, j["en"], j["de"], "js")

head = head.replace('<html lang="en">', '<html lang="de">')
head = head.replace(f'<link rel="canonical" href="{BASE}">', f'<link rel="canonical" href="{BASE}de/">')
for a, b in [(f'<meta property="og:url" content="{BASE}">', f'<meta property="og:url" content="{BASE}de/">'),
             ('<meta property="og:locale" content="en_GB">', '<meta property="og:locale" content="de_DE">\n<meta property="og:locale:alternate" content="en_GB">')]:
    head = swap(head, a, b, "head")
card = re.search(r'<meta property="og:image" content="' + re.escape(BASE) + r'(card\.png(?:\?[^\"]*)?)">', head)
if card:
    head = swap(head, card.group(0), f'<meta property="og:image" content="{BASE}de/{card.group(1)}">', "head")
else:
    problems.append("head: English preview card not found")
body = re.sub(r'\s*<p class="langhint"[^\n]*</p>', "", body)
for asset in ("wood_1950_p105.png", "luther_1922_mt6_9-11.jpg", "thouless_1948_suffer_slip.png"):
    body = swap(body, f'src="{asset}"', f'src="../{asset}"', "asset")
body = swap(body, '<p class="small">Besuche gezählt', '<p class="small">Diese deutsche Fassung wurde mit KI-Unterstützung aus dem Englischen übersetzt und von einem zweiten KI-System gegengelesen, aber noch nicht von einem Muttersprachler geprüft. Hinweise auf Fehler sind willkommen, gern als <a href="https://github.com/creilly11235/wood-cryptogram-1950/issues">Issue auf GitHub</a>.</p>\n<p class="small">Besuche gezählt', "footer")
de = head + body + script
# The translated page is one directory deeper; share the layout and scroll code.
for asset in ("story-layout.css", "story-graphics.css", "story-viewer.css", "story-scroll.js", "cipher-cards.css", "cipher-walkthrough.css", "cipher-walkthrough.js"):
    de = re.sub(r'((?:src|href)=\")' + re.escape(asset) + r'(?=[?\"])', r'\1../' + asset, de)
if problems:
    sys.exit("build_de: " + str(len(problems)) + " problem(s)\n" + "\n".join(problems))
out = ROOT / "docs/de/index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(de, encoding="utf-8")

# leftover check: no unit of the German page may still be an English unit
left = [u["en"] for u in units(de) if u["en"] in known and u["en"] not in {x["de"] for x in table["units"]}]
if left:
    sys.exit("build_de: English left in German page:\n" + "\n".join(x[:90] for x in left))
print("built", out.relative_to(ROOT), f"({len(table['units'])} units, {len(table['js'])} script strings)")
