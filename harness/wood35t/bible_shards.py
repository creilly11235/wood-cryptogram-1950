"""Convert christos-c/bible-corpus XML Bibles (raw.githubusercontent.com) into the English-only search (17 September 2026)-style
key shards (harness/wood35/w35.py tokenisation), one shard per language, verse order."""
import os, sys, re, glob, html, hashlib, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'wood35'))
import w35
SRC = sys.argv[1]; OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
for f in sorted(glob.glob(os.path.join(SRC, '*.xml'))):
    lang = os.path.basename(f)[:-4]
    if lang in ('Greek', 'Hebrew'): continue
    raw = open(f, 'rb').read(); t = raw.decode('utf-8', errors='replace')
    segs = re.findall(r'<seg[^>]*>(.*?)</seg>', t, re.S)
    text = '\n'.join(html.unescape(s) for s in segs)
    toks = w35.key_tokens(text)
    shifts = np.array([w35.word_shift(w) for w in toks], np.uint8)
    vocab = {}; wid = np.empty(len(toks), np.int32)
    for i, w in enumerate(toks): wid[i] = vocab.setdefault(w, len(vocab))
    np.savez(os.path.join(OUT, f'bible_{lang}.npz'), shifts=shifts, wid=wid, meta=np.array([0, len(toks)]), sha256=np.array([hashlib.sha256(raw).hexdigest()]))
    print(lang, len(segs), len(toks), ' '.join(toks[:8]))
