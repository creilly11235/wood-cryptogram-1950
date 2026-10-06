"""Download Project Gutenberg texts per language and strip headers.
Usage: python harness/fetch_corpus.py
Writes harness/data/corpus/<lang>/<id>.txt
"""
import os, re, sys, urllib.request, time, hashlib

BOOKS = {
    "en": [2701, 1342, 84, 98, 1661, 345, 1400, 2600, 76, 1232, 5200, 174, 43, 120, 35, 36, 2554, 1952, 30254, 4300],
    "de": [2229, 2407, 22367, 5323, 34811, 7205, 2408, 19460],
    "fr": [17489, 13951, 14155, 17989, 5097, 2650, 4650, 799, 19657, 6318, 14158, 34204, 16816],
    "la": [218],
    "it": [1000, 45334],
    "es": [2000, 24925, 17073, 14329],
}
LANGUAGES = {"en": "English", "de": "German", "fr": "French", "la": "Latin", "it": "Italian", "es": "Spanish"}
# Confirmed wrong-language books (and one invalid download) in the old seed list.
# Retain this list so cached, header-stripped files cannot silently contaminate builds.
REJECTED = {
    "de": [6248, 26568, 24003, 18004, 7176, 6099, 13635],
    "fr": [13701, 18000],
    "la": [3623, 6316, 2802, 232, 2874, 10645, 34203, 59389, 8880],
    "it": [25120, 22540, 32173, 15992, 31542, 35750],
    "es": [16109, 23052, 35779],
}
HDR = re.compile(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.S | re.I)
FTR = re.compile(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG EBOOK", re.I)

def validate_source(txt, lang):
    """Reject HTML/errors and language mismatches before stripping metadata."""
    header = HDR.search(txt)
    if not header or not FTR.search(txt):
        raise ValueError("Missing Gutenberg text delimiters")
    m = re.search(r"^Language:\s*([^\r\n]+)", txt[:header.start()], re.M | re.I)
    if not m or m.group(1).strip().casefold() != LANGUAGES[lang].casefold():
        actual = m.group(1).strip() if m else "missing"
        raise ValueError(f"Expected {LANGUAGES[lang]}; source declares {actual}")

def check_cached_corpus(cdir, lang):
    bad = [str(i) for i in REJECTED.get(lang, []) if os.path.exists(os.path.join(cdir, f"{i}.txt"))]
    if bad:
        raise ValueError(f"Known mislabelled corpus files in {cdir}: {', '.join(bad)}. "
                         "Run fetch_corpus.py to quarantine them, then rebuild the models.")

def quarantine_rejected(base):
    for lang, ids in REJECTED.items():
        for pgid in ids:
            src = os.path.join(base, lang, f"{pgid}.txt")
            if not os.path.exists(src): continue
            with open(src, "rb") as cached:
                digest = hashlib.sha256(cached.read()).hexdigest()[:16]
            destdir = os.path.join(os.path.dirname(base), "rejected_corpus", lang)
            os.makedirs(destdir, exist_ok=True)
            dest = os.path.join(destdir, f"{pgid}_{digest}.txt")
            suffix = 1
            while os.path.exists(dest):
                dest = os.path.join(destdir, f"{pgid}_{digest}_{suffix}.txt")
                suffix += 1
            os.rename(src, dest)
            print("QUARANTINED", src, "->", dest)

def fetch(pgid):
    for url in (f"https://www.gutenberg.org/cache/epub/{pgid}/pg{pgid}.txt",
                f"https://www.gutenberg.org/files/{pgid}/{pgid}-0.txt",
                f"https://www.gutenberg.org/files/{pgid}/{pgid}-8.txt"):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                raw = r.read()
            for enc in ("utf-8", "latin-1"):
                try:
                    return raw.decode(enc)
                except UnicodeDecodeError:
                    pass
        except Exception as e:
            last = e
    raise RuntimeError(f"{pgid}: {last}")

def strip(txt):
    m = HDR.search(txt)
    if m: txt = txt[m.end():]
    m = FTR.search(txt)
    if m: txt = txt[:m.start()]
    return txt

def main():
    base = os.path.join(os.path.dirname(__file__), "data", "corpus")
    quarantine_rejected(base)
    for lang, ids in BOOKS.items():
        os.makedirs(os.path.join(base, lang), exist_ok=True)
        for pgid in ids:
            out = os.path.join(base, lang, f"{pgid}.txt")
            if os.path.exists(out): continue
            try:
                txt = fetch(pgid)
                validate_source(txt, lang)
            except Exception as e:
                print("FAIL", lang, pgid, e); continue
            head = txt[:600]
            title = re.search(r"Title:\s*(.*)", head)
            language = re.search(r"Language:\s*(.*)", txt[:3000])
            body = strip(txt)
            print(lang, pgid, len(body), (title.group(1).strip() if title else "?")[:50], "|", language.group(1).strip() if language else "?")
            with open(out, "w", encoding="utf-8") as f: f.write(body)
            time.sleep(0.3)

if __name__ == "__main__":
    main()
