"""Gate, nulls and Wood's ciphertext through the multilingual pipeline (PREREG.md)."""
import os, sys, glob, json, random, time, heapq, numpy as np
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'wood35'))
import mlsearch
from mlseg import score as mls, LEX
SH = os.environ.get('W35_SHARDS', '.cache/wood35/w35_shards')
WOOD = 'FVAMINTKFXXWATBOIZVVX'
NP, NN, T, NPROC = int(os.environ.get('NP', 40)), int(os.environ.get('NN', 20)), int(os.environ.get('T', 3000)), int(os.environ.get('NPROC', 4))
SEED = 20261004

def make_plants(files, rng):
    langs = ['en', 'fr', 'de', 'la', 'it', 'es', 'pt']
    top = {l: [w for w, _ in sorted(LEX[l].items(), key=lambda kv: -kv[1])[:4000] if len(w) >= 2] for l in langs}
    plants = []
    while len(plants) < NP:
        ls = rng.sample(langs, rng.randint(2, 4)); s = ''; words = []
        while len(s) < 21:
            l = rng.choice(ls); w = rng.choice(top[l]); s += w; words.append((w, l))
        if len(s) != 21: continue
        f = rng.choice(files); z = np.load(f); sh = z['shifts'].astype(int); wid = z['wid'].astype(int)
        var = rng.choice('DP')
        if sh.shape[0] < 400: continue
        i = rng.randrange(0, sh.shape[0] - 200)
        # encrypt: ct = pt + shift
        if var == 'P': key = list(sh[i:i + 21])
        else:
            key = []; seen = set(); j = i
            while len(key) < 21:
                if wid[j] not in seen: seen.add(wid[j]); key.append(sh[j])
                j += 1
        ct = ''.join(chr((ord(c) - 65 + int(k)) % 26 + 65) for c, k in zip(s, key))
        plants.append(dict(pt=s, words=words, ct=ct, shard=os.path.basename(f), var=var, off=i))
    return plants

def part(args):
    k, files, cts = args
    heaps, K = mlsearch.search(cts, files_override=files) if False else (None, None)
    return None

def worker(args):
    files, cts = args
    import mlsearch as ms
    heaps = {nm: [] for nm in cts}; K = 0
    sub_glob = None
    # inline version of ms.search over an explicit file list
    arrs = {nm: np.array([ord(c) - 65 for c in s], np.int64) for nm, s in cts.items()}
    bp = np.empty(200000, np.int64); bs = np.empty(200000, np.float64)
    for f in files:
        z = np.load(f); sh = z['shifts'].astype(np.int64); wid = z['wid'].astype(np.int64); K += 2 * sh.shape[0]
        for nm, ct in arrs.items():
            h = heaps[nm]; th = max(-95.0, h[0][0]) if len(h) >= T else -95.0
            for var in ('D', 'P'):
                k = ms.score_P(ct, sh, ms.TABLE, th, bp, bs) if var == 'P' else ms.score_D(ct, sh, wid, ms.TABLE, th, bp, bs)
                for t in range(k):
                    it = (float(bs[t]), os.path.basename(f), var, int(bp[t]))
                    if len(h) < T: heapq.heappush(h, it)
                    elif it[0] > h[0][0]: heapq.heapreplace(h, it)
    return heaps, K

if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(SH, '*.npz')))
    rng = random.Random(SEED)
    plants = make_plants(files, rng)
    nulls = [''.join(rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(21)) for _ in range(NN)]
    cts = {'WOOD': WOOD} if not os.environ.get('NOWOOD') else {'WOOD': 'A' * 21}
    for i, p in enumerate(plants): cts[f'P{i:02d}'] = p['ct']
    for i, c in enumerate(nulls): cts[f'N{i:02d}'] = c
    t0 = time.time()
    chunks = [files[i::NPROC] for i in range(NPROC)]
    with Pool(NPROC, initializer=lambda: None) as pool:
        outs = pool.map(worker, [(c, cts) for c in chunks])
    K = sum(o[1] for o in outs)
    merged = {nm: heapq.nlargest(T, [x for o in outs for x in o[0][nm]]) for nm in cts}
    print('shards', len(files), 'K', K, 'search s', round(time.time() - t0), flush=True)
    cache = {}
    def rescore(nm):
        res = []
        for (s, shard, var, off) in merged[nm]:
            z = cache.get(shard)
            if z is None:
                zz = np.load(os.path.join(SH, shard)); z = (zz['shifts'].astype(int), zz['wid'].astype(int)); cache[shard] = z
            pt = mlsearch.decrypt_at(cts[nm], z[0], z[1], var, off)
            v, seg = mls(pt)
            res.append((v, s, pt, shard, var, off, seg))
        res.sort(key=lambda r: (r[0], r[1]), reverse=True)
        return res
    out = {'K': K, 'shards': len(files), 'plants': [], 'nulls': [], 'wood': None}
    rec = 0; floor_vals = []
    for i, p in enumerate(plants):
        r = rescore(f'P{i:02d}'); best = r[0] if r else None
        truev, _ = mls(p['pt']); floor_vals.append(truev)
        ok = best is not None and best[2] == p['pt']
        rec += ok
        out['plants'].append(dict(pt=p['pt'], true_score=truev, ok=ok, best=best[:6] if best else None, in_top=any(x[2] == p['pt'] for x in r)))
    nullmax = -99
    for i in range(NN):
        r = rescore(f'N{i:02d}'); b = r[0] if r else None
        out['nulls'].append(b[:6] if b else None); nullmax = max(nullmax, b[0] if b else -99)
    w = rescore('WOOD'); out['wood'] = [x[:7] for x in w[:30]]
    floor = sorted(floor_vals)[max(0, int(0.05 * len(floor_vals)) - 1)]
    out.update(recovered=rec, n_plants=NP, null_ceiling=nullmax, plant_floor=floor)
    json.dump(out, open(os.environ.get('OUT', os.path.join(HERE, 'run_ml_out.json')), 'w'), indent=1, default=str)
    print(f'GATE {rec}/{NP} recovered; plant floor {floor:.3f}; null ceiling {nullmax:.3f}')
    for x in w[:15]:
        print(f'WOOD {x[0]:7.3f} {x[1]:7.1f} {x[2]} {x[3]} {x[4]} {x[5]} {" ".join(a + "/" + b for a, b in x[6])}')
