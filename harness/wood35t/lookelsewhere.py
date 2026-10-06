"""Look-elsewhere test for the #35 Wood decipherment, on Wood's REAL ciphertext and the REAL
key corpora (the English-only search (17 September 2026) Gutenberg rebuild + 19 Bibles), both Thouless variants (D/P) and both
arithmetic conventions.

Detector(signature S): plaintext[18:21] == S  and  plaintext[0:10] splits completely into
lexicon words of >= 3 letters.  Count hits for S = TEW (Wood's initials, known in advance from
his 1950 paper) and for N_CTRL random control signatures.  The control mean estimates how many
chance hits an arbitrary pre-specified 3-letter signature collects over the same search.
Lexicons: German-only (top 20k of mlseg 'de') and a union (top 20k each of de en fr la it es pt,
plus Dutch and Afrikaans Bible vocabularies)."""
import os, sys, glob, re, html, json, random, pickle, time, collections, numpy as np
from numba import njit
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
SCR = '.cache/wood35'
WOOD = 'FVAMINTKFXXWATBOIZVVX'
N_CTRL = int(os.environ.get('N_CTRL', 500))

def enc(w):
    v = 0
    for c in w: v = v * 27 + (ord(c) - 64)
    return v

def lexicons():
    LEX = pickle.load(open(os.path.join(HERE, 'mlseg_lex.pkl'), 'rb'))
    top = lambda l: [w for w, _ in sorted(LEX[l].items(), key=lambda kv: -kv[1])[:20000] if 3 <= len(w) <= 10]
    de = set(top('de'))
    uni = set(de)
    for l in ('en', 'fr', 'la', 'it', 'es', 'pt'): uni |= set(top(l))
    sys.path.insert(0, os.path.join(HERE, '..', 'wood35')); import w35
    for lang in ('Dutch', 'Afrikaans'):
        t = open(f'{SCR}/bibles/{lang}.xml', encoding='utf-8').read()
        c = collections.Counter(w35.key_tokens(' '.join(html.unescape(s) for s in re.findall(r'<seg[^>]*>(.*?)</seg>', t, re.S))))
        uni |= {w for w, _ in c.most_common(20000) if 3 <= len(w) <= 10}
    return np.array(sorted(enc(w) for w in de), np.int64), np.array(sorted(enc(w) for w in uni), np.int64)

@njit(cache=True)
def inset(arr, v):
    lo, hi = 0, arr.shape[0] - 1
    while lo <= hi:
        m = (lo + hi) >> 1
        if arr[m] == v: return True
        if arr[m] < v: lo = m + 1
        else: hi = m - 1
    return False

@njit(cache=True)
def seg10(pt, lex):
    reach = np.zeros(11, np.bool_); reach[0] = True
    for i in range(10):
        if not reach[i]: continue
        v = 0
        for j in range(i, 10):
            v = v * 27 + pt[j] + 1
            if j - i + 1 >= 3 and inset(lex, v): reach[j + 1] = True
    return reach[10]

@njit(cache=True)
def scan(cts, shifts, wid, sigmask, lex_de, lex_un, out):
    # out[c, sig, 0] German-lexicon hits, out[c, sig, 1] union-lexicon hits; cts: [C,21]
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
                for q in range(10):
                    p = cts[c, q] - key[q]
                    if p < 0: p += 26
                    pt[q] = p
                if seg10(pt, lex_un):
                    out[c, s, 1] += 1
                    if seg10(pt, lex_de): out[c, s, 0] += 1

def work(args):
    files, cts, sigmask, lde, lun = args
    out = np.zeros((cts.shape[0], 26 ** 3, 2), np.int64)
    for f in files:
        z = np.load(f)
        scan(cts, z['shifts'].astype(np.int64), z['wid'].astype(np.int64), sigmask, lde, lun, out)
    return out

def sigcode(s): return ((ord(s[0]) - 65) * 26 + ord(s[1]) - 65) * 26 + ord(s[2]) - 65

if __name__ == '__main__':
    t0 = time.time()
    lde, lun = lexicons()
    print('lexicon sizes: German', len(lde), 'union', len(lun), flush=True)
    rng = random.Random(20261004)
    A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    ctrl = set()
    while len(ctrl) < N_CTRL:
        s = ''.join(rng.choice(A) for _ in range(3))
        if s != 'TEW': ctrl.add(s)
    sigs = ['TEW'] + sorted(ctrl)
    sigmask = np.zeros(26 ** 3, np.bool_)
    for s in sigs: sigmask[sigcode(s)] = True
    cts = np.array([[ord(c) - 65 for c in WOOD], [(ord(c) - 66) % 26 for c in WOOD]], np.int64)
    files = sorted(glob.glob(f'{SCR}/w35_shards/*.npz')) + sorted(glob.glob(f'{SCR}/bible_shards/*.npz'))
    K = 0
    for f in files: K += 2 * int(np.load(f)['shifts'].shape[0])
    print('shards', len(files), 'hypotheses per convention ~', K, flush=True)
    NP = int(os.environ.get('NPROC', 4))
    with Pool(NP) as pool:
        outs = pool.map(work, [(files[i::NP], cts, sigmask, lde, lun) for i in range(NP)])
    out = sum(outs)
    res = {}
    for li, lname in ((0, 'German'), (1, 'union')):
        tew = int(out[:, sigcode('TEW'), li].sum())
        c = np.array([out[:, sigcode(s), li].sum() for s in sigs[1:]])
        res[lname] = dict(TEW=tew, ctrl_mean=float(c.mean()), ctrl_max=int(c.max()),
                          ctrl_frac_ge1=float((c >= 1).mean()), ctrl_frac_ge_tew=float((c >= tew).mean()))
        print(f'{lname:7s} lexicon: TEW hits {tew}; control signatures ({len(c)}): mean {c.mean():.4f}, '
              f'max {c.max()}, fraction with >=1 hit {(c >= 1).mean():.3f}, fraction with >= TEW hits {(c >= tew).mean():.3f}', flush=True)
    res.update(K_per_convention=K, conventions=2, n_ctrl=N_CTRL, cpu_wall_s=round(time.time() - t0))
    json.dump(res, open(os.path.join(SCR, 'lookelsewhere.json'), 'w'), indent=1)
