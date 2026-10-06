"""Arm N: 200 null ciphertexts (PREREG.md section 7).

A null is 21 uniform random letters.  Enciphering a uniform random plaintext
with a real key gives exactly this distribution, so the constructions are
identical; the simpler one is used.  Each null gets the identical two-stage
search, and its best full-objective score is recorded.  These scores are the
distribution of "the best this search can do when there is no true plaintext".
"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search                                       # noqa: E402

NNULL = int(os.environ.get("W35_NNULL", "200"))


def main():
    e = search.Engine()
    rng = np.random.default_rng(search.SEED + 1)
    out = open(os.path.join(HERE, "out_null.jsonl"), "w")
    best = []
    for j in range(NNULL):
        ct = rng.integers(0, 26, size=search.L).astype(np.int16)
        b, res, _, _ = e.search(ct, top=1)
        best.append(b)
        out.write(json.dumps({"j": j, "ct": "".join(chr(65 + int(x)) for x in ct),
                              "best_score": b, "best_pt": res[0]["pt"],
                              "best_loc": {k: res[0][k] for k in
                                           ("tier", "file", "var", "token")}}) + "\n")
        out.flush()
        print(j, round(b, 4), res[0]["pt"], flush=True)
    a = np.array(best)
    summ = {"nulls": NNULL, "max": float(a.max()), "p98": float(np.percentile(a, 98)),
            "p95": float(np.percentile(a, 95)), "median": float(np.median(a)),
            "min": float(a.min())}
    out.write(json.dumps({"summary": summ}) + "\n")
    out.close()
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
