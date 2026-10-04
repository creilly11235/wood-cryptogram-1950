"""A word-segmentation score fast enough to sit inside a numba search loop.

Words of up to 12 letters pack into one int64 (5 bits a letter, values 1..26),
so the dictionary is an open-addressed table of packed keys and log10 unigram
weights.  The segmentation itself is the usual left-to-right DP: best[i] is the
best score for the first i letters, either extending with a dictionary word or
paying BAD for one unsegmentable letter.
"""
import os, sys, math
import numpy as np
from numba import njit

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ngrams import normalize as _nz   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS_TXT = os.path.join(os.path.dirname(HERE), "data", "words", "en_freq.txt")
MAXW = 12
NWORDS = 60000
BAD = -4.0
TSIZE = 1 << 20        # power of two, ~17x the word count


@njit(cache=True, inline="always")
def _probe(keys, vals, k):
    h = (k * np.int64(1099511628211)) & np.int64(0x7FFFFFFFFFFFFFFF)
    i = h & (keys.shape[0] - 1)
    while True:
        if keys[i] == 0:
            return np.float32(0.0), False
        if keys[i] == k:
            return vals[i], True
        i = (i + 1) & (keys.shape[0] - 1)


def build(path=None, lang="en"):
    """Words in frequency order.  `lang` only folds the script (de umlauts and
    the like) so a non-English list lands in the same A-Z alphabet the n-gram
    tables use; for English it is a no-op on the existing list."""
    keys = np.zeros(TSIZE, dtype=np.int64)
    vals = np.zeros(TSIZE, dtype=np.float32)
    seen = set()
    with open(path or WORDS_TXT, encoding="utf-8") as f:
        for r, raw in enumerate(f):
            w = raw.strip().upper() if lang == "en" else _nz(raw.strip(), lang)
            if not w or len(w) > MAXW or not w.isalpha() or len(seen) >= NWORDS:
                continue
            if w in seen:
                continue
            seen.add(w)
            k = 0
            for c in w:
                k = k * 26 + (ord(c) - 64)      # 1..26, so no all-zero key
            _insert(keys, vals, np.int64(k), np.float32(-math.log10(r + 1) - 0.5))
    return keys, vals


@njit(cache=True)
def _insert(keys, vals, k, v):
    h = (k * np.int64(1099511628211)) & np.int64(0x7FFFFFFFFFFFFFFF)
    i = h & (keys.shape[0] - 1)
    while keys[i] != 0 and keys[i] != k:
        i = (i + 1) & (keys.shape[0] - 1)
    keys[i] = k
    vals[i] = v


@njit(cache=True)
def seg(text, keys, vals, best):
    """text: int64 letters 0..25. best: scratch of length len(text)+1."""
    N = text.shape[0]
    best[0] = 0.0
    for i in range(1, N + 1):
        b = best[i - 1] + BAD
        k = np.int64(0)
        L = 1
        while L <= MAXW and L <= i:
            k = np.int64(0)
            for j in range(i - L, i):
                k = k * 26 + (text[j] + 1)
            v, ok = _probe(keys, vals, k)
            if ok:
                s = best[i - L] + v
                if s > b:
                    b = s
            L += 1
        best[i] = b
    return best[N]
