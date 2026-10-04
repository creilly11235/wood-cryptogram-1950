"""Wood #35 multilingual re-scoring of the Round 52 key class.

For every shard (one Gutenberg book, Round 52 tokenisation) and every start offset, under
variant D (consecutive distinct words) and P (all words), decrypt the 21-letter ciphertext
with the verified Thouless convention (pt = ct - ((sum-1) mod 26)) and score the plaintext
with the pooled 7-language 4-gram table.  Keep the global top-T; the caller rescores them
with the multilingual segmentation model (mlseg.py)."""
import os, sys, glob, heapq, json, time, numpy as np
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'wood35'))
import w35
L = 21
TABLE = np.load(os.path.join(HERE, 'pooled_4.npy'))

@njit(cache=True)
def score_P(ct, shifts, table, thresh, out_pos, out_sc):
    n = shifts.shape[0] - L + 1
    k = 0
    pt = np.empty(L, np.int64)
    for i in range(n):
        for j in range(L):
            p = ct[j] - shifts[i + j]
            if p < 0: p += 26
            pt[j] = p
        s = 0.0
        for j in range(3, L):
            s += table[((pt[j - 3] * 26 + pt[j - 2]) * 26 + pt[j - 1]) * 26 + pt[j]]
        if s > thresh:
            out_pos[k] = i; out_sc[k] = s; k += 1
            if k >= out_pos.shape[0]: break
    return k

@njit(cache=True)
def score_D(ct, shifts, wid, table, thresh, out_pos, out_sc):
    n = shifts.shape[0]
    seen = np.empty(L, np.int64); key = np.empty(L, np.int64); pt = np.empty(L, np.int64)
    k = 0
    for i in range(n):
        m = 0; j = i
        while j < n and m < L:
            w = wid[j]; dup = False
            for t in range(m):
                if seen[t] == w:
                    dup = True; break
            if not dup:
                seen[m] = w; key[m] = shifts[j]; m += 1
            j += 1
        if m < L: break
        for q in range(L):
            p = ct[q] - key[q]
            if p < 0: p += 26
            pt[q] = p
        s = 0.0
        for q in range(3, L):
            s += table[((pt[q - 3] * 26 + pt[q - 2]) * 26 + pt[q - 1]) * 26 + pt[q]]
        if s > thresh:
            out_pos[k] = i; out_sc[k] = s; k += 1
            if k >= out_pos.shape[0]: break
    return k

def decrypt_at(ct_str, shifts, wid, var, i):
    ct = [ord(c) - 65 for c in ct_str]
    if var == 'P':
        key = shifts[i:i + L]
    else:
        key = []; seen = set(); j = i
        while len(key) < L:
            w = wid[j]
            if w not in seen:
                seen.add(w); key.append(shifts[j])
            j += 1
    return ''.join(chr((c - int(s)) % 26 + 65) for c, s in zip(ct, key))

def search(cts, shard_glob, thresh=-75.0, top=3000):
    """cts: dict name -> ciphertext string.  Returns dict name -> top list of
    (score, shard, var, offset, plaintext)."""
    files = sorted(glob.glob(shard_glob))
    heaps = {nm: [] for nm in cts}
    arrs = {nm: np.array([ord(c) - 65 for c in s], np.int64) for nm, s in cts.items()}
    buf_p = np.empty(200000, np.int64); buf_s = np.empty(200000, np.float64)
    K = 0
    for f in files:
        z = np.load(f)
        shifts = z['shifts'].astype(np.int64); wid = z['wid'].astype(np.int64)
        K += 2 * shifts.shape[0]
        for nm, ct in arrs.items():
            h = heaps[nm]
            th = max(thresh, h[0][0]) if len(h) >= top else thresh
            for var in ('D', 'P'):
                if var == 'P':
                    k = score_P(ct, shifts, TABLE, th, buf_p, buf_s)
                else:
                    k = score_D(ct, shifts, wid, TABLE, th, buf_p, buf_s)
                for t in range(k):
                    item = (float(buf_s[t]), os.path.basename(f), var, int(buf_p[t]))
                    if len(h) < top: heapq.heappush(h, item)
                    elif item[0] > h[0][0]: heapq.heapreplace(h, item)
    return heaps, K
