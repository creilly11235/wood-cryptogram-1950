"""Targeted test of Wood's cryptogram (#35) against named key passages.
Convention verified on Thouless B (harness/verify_thouless_b.py): NFKD fold, A-Z runs,
shift = (letter sum, A=1..Z=26, - 1) mod 26, plaintext = ct - shift; consecutive DISTINCT words
(variant D) and all words (variant P).  Every start offset inside each passage is tried."""
import sys, os, re, unicodedata, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from ngrams import Scorer, to_ints, to_str, score_arr
CT = 'FVAMINTKFXXWATBOIZVVX'
sc = Scorer('en', 4)

def toks(text, mode='fold'):
    t = text
    if mode == 'fold':
        t = unicodedata.normalize('NFKD', t); t = ''.join(c for c in t if not unicodedata.combining(c))
    t = t.replace('ß', 'SS').replace('æ', 'AE').replace('œ', 'OE').replace('Æ', 'AE').replace('Œ', 'OE')
    return re.findall(r'[A-Z]+', t.upper())

def shift(w): return (sum(ord(c) - 64 for c in w) - 1) % 26

def decrypt(words, ct=CT, distinct=True):
    seq = []; seen = set()
    for w in words:
        if distinct:
            if w in seen: continue
            seen.add(w)
        seq.append(w)
        if len(seq) == len(ct): break
    if len(seq) < len(ct): return None, seq
    return ''.join(chr((ord(c) - 65 - shift(w)) % 26 + 65) for c, w in zip(ct, seq)), seq

def best_for(text, label, top=3, ct=CT):
    W = toks(text)
    res = []
    for d in (True, False):
        for i in range(len(W)):
            pt, seq = decrypt(W[i:], ct, d)
            if pt is None: break
            s = score_arr(to_ints(pt), 4, sc.table) / (len(pt) - 3)
            res.append((s, pt, i, d, ' '.join(seq[:5])))
    res.sort(reverse=True)
    return res[:top]

if __name__ == '__main__':
    import json
    for p in sys.argv[1:]:
        for block in open(p, encoding='utf-8').read().split('\n===\n'):
            block = block.strip()
            if not block: continue
            label, _, text = block.partition('\n')
            for s, pt, i, d, head in best_for(text, label, top=1):
                print(f'{s:7.3f} {pt} off={i:3d} {"D" if d else "P"} [{label}] {head}')
