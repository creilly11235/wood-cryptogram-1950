import sys, os, random, re
sys.path.insert(0, 'harness'); sys.path.insert(0, 'harness/wood35t')
__file__ = 'harness/wood35t/try.py'
exec(open('harness/wood35t/try.py').read().split("if __name__")[0])
from mlseg import score as mls
CTW = 'FVAMINTKFXXWATBOIZVVX'
def variants(words, ct):
    """yield (label, plaintext) for the Thouless convention and its arithmetic variants"""
    out = []
    for d in (True, False):
        seq = []; seen = set()
        for w in words:
            if d:
                if w in seen: continue
                seen.add(w)
            seq.append(w)
            if len(seq) == len(ct): break
        if len(seq) < len(ct): continue
        sums = [sum(ord(c) - 64 for c in w) for w in seq]
        for name, f in (('T-1sub', lambda c, s: c - (s - 1)), ('Tsub', lambda c, s: c - s),
                        ('T-1add', lambda c, s: c + (s - 1)), ('Tadd', lambda c, s: c + s),
                        ('beau-1', lambda c, s: (s - 1) - c), ('beau', lambda c, s: s - c)):
            pt = ''.join(chr(f(ord(c) - 65, s) % 26 + 65) for c, s in zip(ct, sums))
            out.append((('D' if d else 'P') + name, pt))
    return out
if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'calib':
        random.seed(1); vals = []
        for _ in range(20000):
            s = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(21))
            v, _ = mls(s); vals.append(v)
        vals.sort(reverse=True)
        seg = sum(1 for v in vals if v > -90)
        print('random uniform 21-letter: segmentable', seg, '/ 20000; top10', [round(v, 3) for v in vals[:10]])
    else:
        res = []
        for p in sys.argv[2:]:
            for block in open(p, encoding='utf-8').read().split('\n===\n'):
                block = block.strip()
                if not block: continue
                label, _, text = block.partition('\n')
                W = toks(text)
                for i in range(len(W)):
                    for vlab, pt in variants(W[i:], CTW):
                        v, seg = mls(pt)
                        if v > -90:
                            res.append((v, pt, label, i, vlab, seg))
        res.sort(reverse=True)
        print('hypotheses scored; segmentable', len(res))
        for r in res[:25]:
            print(f'{r[0]:7.3f} {r[1]} [{r[2]}] off={r[3]} {r[4]} {" ".join(w + "/" + l for w, l in r[5])}')
