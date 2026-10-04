"""N-gram language models for cryptanalysis scoring.

Build:  python harness/ngrams.py build   -> harness/data/ngrams/<lang>_<n>.npy
Use:    from ngrams import Scorer; s = Scorer('en', 4); s.score(int_array)
Text is normalized to A-Z (26 symbols). Accented letters are folded (é->E, ß->SS, ä->AE for de).
"""
import os, sys, unicodedata, re
import numpy as np
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
A = 26

FOLD_DE = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "AE", "Ö": "OE", "Ü": "UE"}
FOLD_DA = {"æ": "ae", "ø": "oe", "å": "aa", "ä": "ae", "ö": "oe", "Æ": "AE", "Ø": "OE", "Å": "AA", "Ä": "AE", "Ö": "OE"}

def normalize(text, lang="en"):
    """Return uppercase A-Z only string."""
    if lang == "de":
        for k, v in FOLD_DE.items():
            text = text.replace(k, v)
    if lang in ("da", "no", "sv"):
        for k, v in FOLD_DA.items():
            text = text.replace(k, v)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.upper()
    return re.sub(r"[^A-Z]", "", text)

def to_ints(s):
    return np.frombuffer(s.encode("ascii"), dtype=np.uint8).astype(np.int64) - 65

def to_str(a):
    return "".join(chr(65 + int(x)) for x in a)

@njit(cache=True)
def _count(a, n, counts):
    base = 1
    for i in range(n - 1):
        base *= 26
    idx = 0
    for i in range(n):
        idx = idx * 26 + a[i]
    counts[idx] += 1
    for i in range(n, a.shape[0]):
        idx = (idx - a[i - n] * base) * 26 + a[i]
        counts[idx] += 1

@njit(cache=True)
def score_arr(a, n, table):
    if a.shape[0] < n:
        return 0.0
    base = 1
    for i in range(n - 1):
        base *= 26
    idx = 0
    for i in range(n):
        idx = idx * 26 + a[i]
    s = table[idx]
    for i in range(n, a.shape[0]):
        idx = (idx - a[i - n] * base) * 26 + a[i]
        s += table[idx]
    return s

def build(lang, n, floor_weight=0.01):
    cdir = os.path.join(DATA, "corpus", lang)
    from fetch_corpus import check_cached_corpus
    check_cached_corpus(cdir, lang)
    counts = np.zeros(A ** n, dtype=np.int64)
    total = 0
    uni = np.zeros(A, dtype=np.int64)
    for fn in sorted(os.listdir(cdir)):
        txt = open(os.path.join(cdir, fn), encoding="utf-8").read()
        a = to_ints(normalize(txt, lang))
        if a.shape[0] >= n:
            _count(a, n, counts)
            total += a.shape[0]
        np.add.at(uni, a, 1)
    tot = counts.sum()
    probs = counts / tot
    floor = floor_weight / tot
    table = np.log10(np.where(counts > 0, probs, floor)).astype(np.float32)
    os.makedirs(os.path.join(DATA, "ngrams"), exist_ok=True)
    np.save(os.path.join(DATA, "ngrams", f"{lang}_{n}.npy"), table)
    np.save(os.path.join(DATA, "ngrams", f"{lang}_1.npy"), (uni / uni.sum()).astype(np.float32))
    return total, int((counts > 0).sum())

class Scorer:
    def __init__(self, lang="en", n=4):
        self.lang, self.n = lang, n
        self.table = np.load(os.path.join(DATA, "ngrams", f"{lang}_{n}.npy"))
    def score(self, a):
        return score_arr(np.ascontiguousarray(a, dtype=np.int64), self.n, self.table)
    def score_str(self, s):
        return self.score(to_ints(normalize(s, self.lang)))
    def per_char(self, a):
        L = len(a) - self.n + 1
        return self.score(a) / max(L, 1)

def unigram(lang):
    return np.load(os.path.join(DATA, "ngrams", f"{lang}_1.npy"))

if __name__ == "__main__":
    if sys.argv[1:] and sys.argv[1] == "build":
        langs = sys.argv[2:] or sorted(os.listdir(os.path.join(DATA, "corpus")))
        for lang in langs:
            for n in (3, 4, 5):
                tot, distinct = build(lang, n)
                print(lang, n, "chars", tot, "distinct", distinct)
