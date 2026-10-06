"""Arm G: the September English-only search power gate (PREREG.md section 6).

100 plants.  Each is a held-out 21-letter English plaintext enciphered with a
uniformly drawn row of the registered keystream matrix, then put through the
full two-stage search over all 28,602,798 rows.  Recovered = the rank-1 row
decodes to the planted plaintext exactly.
"""
import os, sys, json, re, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search, w35                                  # noqa: E402

ROOT = search.ROOT
L = search.L
NPLANT = int(os.environ.get("W35_NPLANT", "100"))


def plant_texts(n, seed):
    """21-letter English plaintexts starting at a word boundary, drawn from
    corpus_extra/en, which the en_5 model was NOT built from."""
    held = os.path.join(ROOT, "harness/data/corpus_extra/en")
    trained = set(os.listdir(os.path.join(ROOT, "harness/data/corpus/en")))
    files = [f for f in sorted(os.listdir(held)) if f not in trained]
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        fn = rng.choice(files)
        txt = open(os.path.join(held, fn), encoding="utf-8", errors="replace").read()
        words = re.findall(r"[A-Za-z]+", txt)
        if len(words) < 200:
            continue
        i = rng.randrange(50, len(words) - 60)
        s = "".join(words[i:i + 40]).upper()
        if len(s) < L:
            continue
        out.append({"file": fn, "word": i, "pt": s[:L]})
    return out


def main():
    e = search.Engine()
    rng = np.random.default_rng(search.SEED)
    plants = plant_texts(NPLANT, search.SEED)
    rows = rng.integers(0, e.K, size=NPLANT)
    recovered = 0
    out = open(os.path.join(HERE, "out_gate.jsonl"), "w")
    truth_scores = []
    for j, p in enumerate(plants):
        key = e.keys[rows[j]].astype(np.int16)
        pt = search.to_ints(p["pt"])
        ct = ((pt + key) % 26).astype(np.int16)
        best, res, cand, sc = e.search(ct)
        tsc, _ = e.full_score_rows(ct, np.array([rows[j]]))
        truth_scores.append(float(tsc[0]))
        ok = res[0]["pt"] == p["pt"]
        recovered += ok
        # rank of the true row among the funnel, and after collapsing rows of
        # the same file+variant within +-L tokens (adjacent starts share most
        # of their keystream and are not independent decoys)
        tloc = e.locate(int(rows[j]))
        order = np.argsort(-sc)
        raw_rank = None
        seen, coll_rank = [], None
        for r_i, t in enumerate(order):
            row = int(cand[t])
            if row == int(rows[j]):
                raw_rank = r_i + 1
            loc = e.locate(row)
            k = (loc["tier"], loc["file"], loc["var"])
            if any(k == s[0] and abs(loc["token"] - s[1]) <= L for s in seen):
                continue
            seen.append((k, loc["token"]))
            if row == int(rows[j]):
                coll_rank = len(seen)
                break
        rec = {"j": j, "plant": p, "true_row": int(rows[j]), "true_loc": tloc,
               "true_score": float(tsc[0]), "best_score": best,
               "best_pt": res[0]["pt"], "best_loc": {k: res[0][k] for k in
                                                     ("tier", "file", "var", "token")},
               "recovered": bool(ok), "raw_rank": raw_rank,
               "collapsed_rank": coll_rank}
        out.write(json.dumps(rec) + "\n"); out.flush()
        print(j, "OK" if ok else "--", round(best, 4), "true", round(float(tsc[0]), 4),
              "rank", raw_rank, flush=True)
    lb = search.wilson_lb(recovered, NPLANT)
    summ = {"plants": NPLANT, "recovered": recovered,
            "rate": recovered / NPLANT, "wilson_lb": lb,
            "gate_passes": lb >= 0.20,
            "truth_score_p05": float(np.percentile(truth_scores, 5)),
            "truth_score_median": float(np.median(truth_scores)),
            "K": e.K}
    out.write(json.dumps({"summary": summ}) + "\n")
    out.close()
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
