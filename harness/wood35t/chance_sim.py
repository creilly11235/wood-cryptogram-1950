"""Reproducible version of the report's chance simulation (Round 89, #35 Wood).
P(10 uniform random letters split into common German words of >= 3 letters), using the
top 20,000 German entries of mlseg_lex.pkl (built from Faust, Werther, Wintermaerchen).
Seed and trial count fixed; prints hits, rate and a 95% Clopper-Pearson interval."""
import sys, os, random, functools, math, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
LEX = pickle.load(open(os.path.join(HERE, 'mlseg_lex.pkl'), 'rb'))
de = {w for w, lp in sorted(LEX['de'].items(), key=lambda kv: -kv[1])[:20000] if len(w) >= 3}
@functools.lru_cache(None)
def seg(s):
    return not s or any(s[:k] in de and seg(s[k:]) for k in range(3, min(len(s), 14) + 1))
def cp(k, n, a=0.05):
    from scipy.stats import beta
    lo = beta.ppf(a / 2, k, n - k + 1) if k else 0.0
    hi = beta.ppf(1 - a / 2, k + 1, n - k)
    return lo, hi
if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
    random.seed(5); hit = 0; A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for _ in range(N):
        if seg(''.join(random.choice(A) for _ in range(10))): hit += 1
        if seg.cache_info().currsize > 5_000_000: seg.cache_clear()
    lo, hi = cp(hit, N)
    print(f'German words >=3 letters in list: {len(de)}; trials {N}; hits {hit}; rate {hit/N:.3e}; 95% CI [{lo:.2e}, {hi:.2e}]')
