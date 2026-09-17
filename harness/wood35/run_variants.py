"""Secondary arms registered in PREREG_R52.md section 3, run because the
primary gate passed.

  S     tier S (Tatoeba sentence dumps), primary convention
  convB shift = sum mod 26 instead of (sum - 1) mod 26
  add   plaintext = ciphertext + shift instead of minus

convB and add reuse arm N's nulls and arm G's gate.  That is exact, not a
shortcut: both are deterministic relabellings of the same key matrix over the
same K, so the distribution of "best score over K rows against a uniform random
ciphertext" is identical, and so is the recovery rate.  convB is the primary
search run on (ciphertext - 1); add negates the key matrix.

Tier S has a SMALLER K than B+E (22,132,525 vs 28,602,798), so reusing the
B+E null maximum is conservative for it: a smaller search cannot beat a larger
one's noise ceiling more easily.
"""
import os, sys, json, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search, run_real                             # noqa: E402

ROOT = search.ROOT
L = search.L


def bar_for(best, g, n, vals):
    reach = sum(1 for v in vals if v >= best)
    return {"cond1_beats_null_max": best > n["max"],
            "cond2_under_2pct": reach / len(vals) < 0.02,
            "cond3_above_plaintext_floor": best > g["truth_score_p05"],
            "nulls_reaching_real": reach, "null_max": n["max"],
            "plaintext_floor_p05": g["truth_score_p05"]}


def main():
    g = run_real.gate_summary()
    n = run_real.null_summary()
    vals = [json.loads(l)["best_score"] for l in
            open(os.path.join(HERE, "out_null_r52.jsonl")) if "best_score" in l]
    ct_s = re.sub(r"[^A-Z]", "", json.loads(
        open(os.path.join(ROOT, "ciphers/wood_35.json")).read())["text"].upper())
    ct = search.to_ints(ct_s)
    out = {}

    e = search.Engine(tiers=("B", "E"))
    for name, cta, neg in (("convB", (ct - 1) % 26, False), ("add", ct, True)):
        if neg:
            keep = e.keys
            e.keys = np.ascontiguousarray((26 - keep.astype(np.int16)) % 26).astype(np.uint8)
        best, res, _, _ = e.search(cta.astype(np.int16), top=10)
        if neg:
            e.keys = keep
        out[name] = {"K": e.K, "best_score": best, "bar": bar_for(best, g, n, vals),
                     "top": [{k: r[k] for k in ("tier", "file", "var", "token",
                                                "score", "pt")} for r in res]}
        print(name, round(best, 4), res[0]["pt"], res[0]["file"], flush=True)
    del e

    es = search.Engine(tiers=("S",))
    best, res, _, _ = es.search(ct, top=10)
    out["S"] = {"K": es.K, "best_score": best, "bar": bar_for(best, g, n, vals),
                "note": "B+E nulls reused; tier S has the smaller K, so this is conservative",
                "top": [{k: r[k] for k in ("tier", "file", "var", "token",
                                           "score", "pt")} for r in res]}
    print("S", round(best, 4), res[0]["pt"], res[0]["file"], flush=True)

    for v in out.values():
        v["passes_all_three"] = all(v["bar"][k] for k in v["bar"] if k.startswith("cond"))
    json.dump(out, open(os.path.join(HERE, "out_variants_r52.json"), "w"), indent=1)
    print(json.dumps({k: {"best_score": v["best_score"],
                          "passes_all_three": v["passes_all_three"]}
                      for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
