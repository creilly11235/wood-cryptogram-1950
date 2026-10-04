"""Multilingual word-segmentation score for short plaintexts (Wood #35: the plaintext is
reportedly in several languages).  Lexicons: per-language word unigram frequencies from
Gutenberg texts (fr la it es pt de) and the repo's English list.  Score of a string = best
segmentation into lexicon words, each word scored by its best language, minus a per-word
penalty and a language-switch penalty; reported per letter (log10)."""
import os, re, sys, math, unicodedata, collections, functools, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
SCR = '.cache/wood35/fr'
SRC = {'fr': ['g27625', 'g36011', 'g39739', 'g15790'], 'la': ['g227'], 'it': ['g1000'],
       'es': ['g2000', 'g5201'], 'pt': ['g3333'], 'de': ['g2229', 'g2407', 'g6079'], 'en': None}

def fold(s):
    s = unicodedata.normalize('NFKD', s); s = ''.join(c for c in s if not unicodedata.combining(c))
    return s.replace('ß', 'SS').upper()

def build():
    lex = {}
    for lang, files in SRC.items():
        c = collections.Counter()
        if files is None:
            p = os.path.join(HERE, '..', 'data', 'words', 'en_common.txt')
            words = [w.strip() for w in open(p, encoding='utf-8', errors='replace')]
            # rank-based Zipf frequencies for an unranked list: give uniform-ish weight
            for i, w in enumerate(words):
                w = re.sub('[^A-Z]', '', fold(w.split()[0] if w.split() else ''))
                if w: c[w] += max(1, 100000 // (i + 10))
        else:
            for f in files:
                t = open(f'{SCR}/{f}.txt', encoding='utf-8', errors='replace').read()
                t = t[t.find('***'):]
                for w in re.findall(r'[A-Z]+', fold(t)):
                    c[w] += 1
        tot = sum(c.values())
        lex[lang] = {w: math.log10(n / tot) for w, n in c.items() if n >= 2 or len(w) >= 5}
    return lex

CACHE = os.path.join(HERE, 'mlseg_lex.pkl')
if os.path.exists(CACHE):
    LEX = pickle.load(open(CACHE, 'rb'))
else:
    LEX = build(); pickle.dump(LEX, open(CACHE, 'wb'))
LANGS = list(LEX)
FLOOR = -7.5
SINGLE_OK = {'A', 'I', 'O', 'Y', 'E', 'U'}

def score(s, word_pen=1.0, switch_pen=0.5, maxlen=18):
    """DP over positions x current language. Returns (per-letter score, segmentation)."""
    n = len(s)
    best = [dict() for _ in range(n + 1)]
    best[0] = {None: (0.0, [])}
    for i in range(n):
        if not best[i]: continue
        for prev_lang, (sc, seg) in best[i].items():
            for j in range(i + 1, min(n, i + maxlen) + 1):
                w = s[i:j]
                if len(w) == 1 and w not in SINGLE_OK: continue
                for lang in LANGS:
                    lp = LEX[lang].get(w)
                    if lp is None: continue
                    v = sc + lp - word_pen - (switch_pen if prev_lang not in (None, lang) else 0)
                    cur = best[j].get(lang)
                    if cur is None or v > cur[0]:
                        best[j][lang] = (v, seg + [(w, lang)])
    if not best[n]:
        return -99.0, []
    v, seg = max(best[n].values(), key=lambda x: x[0])
    return v / n, seg

if __name__ == '__main__':
    for s in sys.argv[1:]:
        print(s, score(s))
