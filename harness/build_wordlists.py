"""Build frequency-ordered word lists data/words/<lang>_freq.txt from Tatoeba sentence dumps
(data/sentsrc/<code>_sentences.tsv.bz2) or Gutenberg corpora. German is folded ae/oe/ue/ss
(de) and also to bare vowels (de2)."""
import bz2, re, os, sys, unicodedata
from collections import Counter
SRC = {"de": ("sentsrc", "deu"), "de2": ("sentsrc", "deu"), "en": ("sentsrc", "eng"), "fr": ("sentsrc", "fra"),
       "la": ("sentsrc", "lat"), "he": ("sentsrc", "heb"), "yi": ("sentsrc", "yid"), "nl": ("sentsrc", "nld"), "eo": ("sentsrc", "epo"), "da": ("sentsrc", "dan"), "sv": ("sentsrc", "swe"), "no": ("sentsrc", "nob"), "it": ("corpus", "it"), "es": ("corpus", "es")}
def fold(w, lang):
    if lang == "de":
        for k, v in {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}.items(): w = w.replace(k, v)
    if lang in ("da", "no", "sv"):
        # historical Latin-alphabet spellings; matches FOLD_DA in ngrams.normalize
        for k, v in {"æ": "ae", "ø": "oe", "å": "aa", "ä": "ae", "ö": "oe"}.items(): w = w.replace(k, v)
    w = unicodedata.normalize("NFKD", w)
    w = "".join(c for c in w if not unicodedata.combining(c))
    if lang in ("he", "yi"):
        # map Hebrew final forms to base forms; keep Hebrew letters only
        fin = {"\u05da": "\u05db", "\u05dd": "\u05de", "\u05df": "\u05e0", "\u05e3": "\u05e4", "\u05e5": "\u05e6"}
        w = "".join(fin.get(c, c) for c in w)
        return w if all("\u05d0" <= c <= "\u05ea" for c in w) else ""
    return w.lower()
for lang in sys.argv[1:] or SRC:
    kind, code = SRC[lang]
    cnt = Counter()
    if kind == "sentsrc":
        with bz2.open(f"data/sentsrc/{code}_sentences.tsv.bz2", "rt", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 3: continue
                for w in re.findall(r"[^\W\d_]+", parts[2]):
                    cnt[fold(w, lang)] += 1
    else:
        for fn in os.listdir(f"data/corpus/{code}"):
            for w in re.findall(r"[^\W\d_]+", open(f"data/corpus/{code}/{fn}", errors="ignore").read()):
                cnt[fold(w, lang)] += 1
    os.makedirs("data/words", exist_ok=True)
    with open(f"data/words/{lang}_freq.txt", "w", encoding="utf-8") as out:
        for w, c in cnt.most_common():
            if w and w.isalpha() and (w.isascii() or lang in ("he", "yi")): out.write(w + "\n")
    print(lang, len(cnt), "types")
