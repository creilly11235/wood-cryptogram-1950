"""Reproduce the Bible-tier hit location from the source XML (christos-c/bible-corpus,
bibles/German.xml, fetched 2026-10-04 from raw.githubusercontent.com master).
Usage: python offset_check.py German.xml"""
import sys, re, html, hashlib, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'wood35'))
import w35
raw = open(sys.argv[1], 'rb').read()
print('sha256', hashlib.sha256(raw).hexdigest())
t = raw.decode('utf-8', errors='replace')
toks, where = [], []
for attr, s in re.findall(r'<seg([^>]*)>(.*?)</seg>', t, re.S):
    m = re.search(r'id=["\']([^"\']+)', attr); vid = m.group(1) if m else 'header'
    for w in w35.key_tokens(html.unescape(s)):
        toks.append(w); where.append(vid)
i = 533250
print('token offset', i, 'verse', where[i], 'words', ' '.join(toks[i - 5:i + 25]))
assert toks[i:i + 2] == ['UNSER', 'VATER'] and where[i] == 'b.MAT.6.9'
print('offset 533250 = 6th word of Matthew 6:9 ("Unser"), as reported')
