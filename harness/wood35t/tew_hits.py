"""List every decryption (both conventions, both variants, all 3,866 shards) that ends in TEW and
whose first 10 letters split into >=3-letter lexicon words (union lexicon), and test the full
18-letter split (union lexicon + TOTSIENS, which is disclosed as a post-hoc addition because
the Afrikaans Bible vocabulary lacks it).  Also counts full-18 hits for control signatures."""
import os, sys, glob, json, random, numpy as np
from numba import njit
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lookelsewhere as le
SCR = le.SCR

@njit(cache=True)
def segN(pt, N, lex):
    reach = np.zeros(N + 1, np.bool_); reach[0] = True
    for i in range(N):
        if not reach[i]: continue
        v = 0
        for j in range(i, min(N, i + 12)):
            v = v * 27 + pt[j] + 1
            if j - i + 1 >= 3 and le.inset(lex, v): reach[j + 1] = True
    return reach[N]

@njit(cache=True)
def scan2(cts, shifts, wid, sigmask, lex, out, rec, nrec, tewcode):
    n = shifts.shape[0]
    key = np.empty(21, np.int64); seen = np.empty(21, np.int64); pt = np.empty(21, np.int64)
    for var in range(2):
        for i in range(n):
            if var == 1:
                if i + 21 > n: break
                for q in range(21): key[q] = shifts[i + q]
            else:
                m = 0; j = i
                while j < n and m < 21:
                    w = wid[j]; dup = False
                    for t in range(m):
                        if seen[t] == w: dup = True; break
                    if not dup: seen[m] = w; key[m] = shifts[j]; m += 1
                    j += 1
                if m < 21: break
            for c in range(cts.shape[0]):
                s = 0
                for q in range(18, 21):
                    p = cts[c, q] - key[q]
                    if p < 0: p += 26
                    s = s * 26 + p
                if not sigmask[s]: continue
                for q in range(18):
                    p = cts[c, q] - key[q]
                    if p < 0: p += 26
                    pt[q] = p
                if segN(pt, 18, lex): out[c, s] += 1
                full = segN(pt, 18, lex)
                if ((s == tewcode and segN(pt, 10, lex)) or (s != tewcode and full)) and nrec[0] < rec.shape[0]:
                    k = nrec[0]; rec[k, 0] = c; rec[k, 1] = var; rec[k, 2] = i
                    for q in range(18): rec[k, 3 + q] = pt[q]
                    rec[k, 21] = (1 if full else 0) + 2 * s
                    nrec[0] += 1

def work(args):
    files, cts, sigmask, lex, tewcode = args
    out = np.zeros((2, 26 ** 3), np.int64); hits = []
    for f in files:
        z = np.load(f)
        rec = np.zeros((200, 22), np.int64); nrec = np.zeros(1, np.int64)
        scan2(cts, z['shifts'].astype(np.int64), z['wid'].astype(np.int64), sigmask, lex, out, rec, nrec, tewcode)
        for k in range(nrec[0]):
            r = rec[k]
            hits.append(dict(file=os.path.basename(f), conv=['sum-1', 'sum'][r[0]], var='DP'[r[1]], off=int(r[2]),
                             pt=''.join(chr(65 + x) for x in r[3:21]) + ''.join(chr(65 + (r[21] // 2 // 26 ** e) % 26) for e in (2, 1, 0)), full18=bool(r[21] % 2)))
    return out, hits

if __name__ == '__main__':
    lde, lun = le.lexicons()
    lun = np.array(sorted(set(lun.tolist()) | {le.enc('TOTSIENS')}), np.int64)
    rng = random.Random(20261004); A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'; ctrl = set()
    while len(ctrl) < 500:
        s = ''.join(rng.choice(A) for _ in range(3))
        if s != 'TEW': ctrl.add(s)
    sigs = ['TEW'] + sorted(ctrl)
    sigmask = np.zeros(26 ** 3, np.bool_)
    for s in sigs: sigmask[le.sigcode(s)] = True
    W = le.WOOD
    cts = np.array([[ord(c) - 65 for c in W], [(ord(c) - 66) % 26 for c in W]], np.int64)
    files = sorted(glob.glob(f'{SCR}/w35_shards/*.npz')) + sorted(glob.glob(f'{SCR}/bible_shards/*.npz'))
    with Pool(4) as pool:
        outs = pool.map(work, [(files[i::4], cts, sigmask, lun, le.sigcode('TEW')) for i in range(4)])
    out = sum(o[0] for o in outs); hits = [h for o in outs for h in o[1]]
    tew = int(out[:, le.sigcode('TEW')].sum()); c = np.array([out[:, le.sigcode(s)].sum() for s in sigs[1:]])
    print(f'FULL 18-letter split + signature: TEW {tew}; controls mean {c.mean():.4f}, max {c.max()}, fraction >=1 {(c >= 1).mean():.3f}')
    print('control-signature full-length hits:')
    for h in [h for h in hits if not h['pt'].endswith('TEW')]:
        print(f"  {h['pt']}  {h['file']} {h['var']} {h['off']} {h['conv']}")
    hits_t = [h for h in hits if h['pt'].endswith('TEW')]
    print(f'TEW decryptions with a 10-letter word opening: {len(hits_t)}')
    for h in sorted(hits_t, key=lambda h: -h['full18']):
        print(f"  {h['pt']}  full18={h['full18']}  {h['file']} {h['var']} {h['off']} {h['conv']}")
    json.dump(dict(full18_TEW=tew, full18_ctrl_mean=float(c.mean()), full18_ctrl_frac_ge1=float((c >= 1).mean()), tew_hits=hits),
              open(f'{SCR}/tew_hits.json', 'w'), indent=1)
