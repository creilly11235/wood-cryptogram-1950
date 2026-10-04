"""Pooled multilingual 4-gram model (equal letter budget per language) for the Wood #35
multilingual-plaintext prefilter."""
import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from ngrams import normalize, to_ints, _count
SCR = '.cache/wood35/fr'
SRC = {'en': ['moore_en'], 'fr': ['g27625', 'g36011'], 'de': ['g2229', 'g2407', 'g6079'], 'la': ['g227'],
       'it': ['g1000'], 'es': ['g2000'], 'pt': ['g3333']}
EN_EXTRA = ['harness/data/corpus/en/pg1342.txt', 'harness/data/corpus/en/pg84.txt']
def build(n=4, budget=350000, out='harness/wood35t/pooled_4.npy'):
    counts = np.zeros(26 ** n, np.int64)
    for lang, fs in SRC.items():
        txt = ''
        paths = [f'{SCR}/{f}.txt' for f in fs] + (EN_EXTRA if lang == 'en' else [])
        for p in paths:
            t = open(p, encoding='utf-8', errors='replace').read(); txt += t[len(t) // 20:]
        a = to_ints(normalize(txt, lang))[:budget]
        c = np.zeros(26 ** n, np.int64); _count(a, n, c); counts += c
        print(lang, a.shape[0])
    tot = counts.sum(); floor = 0.01 / tot
    table = np.log10(np.where(counts > 0, counts / tot, floor)).astype(np.float32)
    np.save(out, table); return table
if __name__ == '__main__':
    build()
