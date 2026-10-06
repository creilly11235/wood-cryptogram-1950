"""the English-only search (17 September 2026) search engine: rank every registered (file, offset, variant) key
hypothesis against a 21-letter ciphertext.

Two stages, as registered in PREREG.md section 4: stage 1 ranks all K rows
by the 5-gram term alone, stage 2 rescores the top FUNNEL under the full
English combined objective.
"""
import os, sys, json, math
import numpy as np
from numba import njit, prange

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "harness"))
sys.path.insert(0, os.path.join(ROOT, "harness"))
import w35                                        # noqa: E402
from ngrams import Scorer                          # noqa: E402
import wordlm                                      # noqa: E402

L = w35.L
ORDER = 5
W_SEG = 1.0
FUNNEL = 5000
SEED = 20260918
LN10 = math.log(10.0)
CACHE = os.environ.get("W35_CACHE",
                       ".cache/wood35/w35_keys")


@njit(parallel=True, cache=True)
def stage1(ct, keys, table, out):
    """5-gram log10 total for every row's decryption.  ct is int16[L]."""
    K = keys.shape[0]
    for r in prange(K):
        idx = 0
        for i in range(ORDER):
            p = ct[i] - keys[r, i]
            if p < 0:
                p += 26
            idx = idx * 26 + p
        s = table[idx]
        base = 26 ** (ORDER - 1)
        for i in range(ORDER, L):
            p0 = ct[i - ORDER] - keys[r, i - ORDER]
            if p0 < 0:
                p0 += 26
            p = ct[i] - keys[r, i]
            if p < 0:
                p += 26
            idx = (idx - p0 * base) * 26 + p
            s += table[idx]
        out[r] = s


@njit(cache=True)
def _full(ct, keys, rows, table, wkeys, wvals, scratch, out, pts):
    nscored = L - ORDER + 1
    for t in range(rows.shape[0]):
        r = rows[t]
        for i in range(L):
            p = ct[i] - keys[r, i]
            if p < 0:
                p += 26
            pts[t, i] = p
        idx = 0
        for i in range(ORDER):
            idx = idx * 26 + pts[t, i]
        s = table[idx]
        base = 26 ** (ORDER - 1)
        for i in range(ORDER, L):
            idx = (idx - pts[t, i - ORDER] * base) * 26 + pts[t, i]
            s += table[idx]
        g = s * LN10 / nscored
        out[t] = g + W_SEG * wordlm.seg(pts[t], wkeys, wvals, scratch) / L


class Engine:
    def __init__(self, tiers=("B", "E"), cache=CACHE):
        tag = cache + "_" + "".join(tiers)
        self.keys, self.meta = w35.build_index(tiers, cache=tag)
        self.keys = np.ascontiguousarray(self.keys)
        self.K = self.keys.shape[0]
        self.table = Scorer("en", ORDER).table
        self.wkeys, self.wvals = wordlm.build()
        self.starts = np.array([e["start"] for e in self.meta["index"]], dtype=np.int64)
        self._s1 = np.empty(self.K, dtype=np.float32)
        self._scratch = np.empty(L + 1, dtype=np.float32)

    def locate(self, row):
        j = int(np.searchsorted(self.starts, row, side="right")) - 1
        e = self.meta["index"][j]
        return dict(tier=e["tier"], file=e["name"], var=e["var"],
                    token=e["first_token"] + (int(row) - e["start"]), row=int(row))

    def full_score_rows(self, ct, rows):
        rows = np.ascontiguousarray(rows, dtype=np.int64)
        out = np.empty(rows.shape[0], dtype=np.float64)
        pts = np.empty((rows.shape[0], L), dtype=np.int64)
        _full(ct, self.keys, rows, self.table, self.wkeys, self.wvals,
              self._scratch, out, pts)
        return out, pts

    def search(self, ct, funnel=FUNNEL, top=20):
        """ct: int16[L] of 0..25.  Returns (best_score, top candidates)."""
        stage1(ct, self.keys, self.table, self._s1)
        cand = np.argpartition(self._s1, self.K - funnel)[self.K - funnel:]
        sc, pts = self.full_score_rows(ct, cand)
        order = np.argsort(-sc)
        res = []
        for t in order[:top]:
            d = self.locate(cand[t])
            d["score"] = float(sc[t])
            d["pt"] = "".join(chr(65 + int(x)) for x in pts[t])
            res.append(d)
        return float(sc[order[0]]), res, cand, sc


def to_ints(s):
    return (np.frombuffer(s.encode(), dtype=np.uint8).astype(np.int16) - 65)


def wilson_lb(k, n, z=1.96):
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d
