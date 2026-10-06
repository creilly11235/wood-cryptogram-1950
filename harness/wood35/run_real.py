"""Arm R: Wood's ciphertext (PREREG.md sections 5 and 7).

Runs only after the gate in out_gate.jsonl passes Wilson LB >= 0.20.  Any
candidate is re-encrypted from its named (file, token offset, variant) and the
result compared to the ciphertext byte for byte, which is the acceptance test
the registration requires.
"""
import os, sys, json, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search, w35                                  # noqa: E402

ROOT = search.ROOT
L = search.L
TIERS = tuple(os.environ.get("W35_TIERS", "B,E").split(","))


def gate_summary():
    p = os.path.join(HERE, "out_gate.jsonl")
    last = None
    for line in open(p):
        d = json.loads(line)
        if "summary" in d:
            last = d["summary"]
    return last


def null_summary():
    p = os.path.join(HERE, "out_null.jsonl")
    for line in open(p):
        d = json.loads(line)
        if "summary" in d:
            return d["summary"]
    return None


def reencrypt(loc, pt):
    """Independent re-derivation of the keystream from the named file and token
    offset -- not from the cached matrix -- then plaintext + key."""
    path = os.path.join(ROOT, "harness/data/corpus",
                        loc["file"]) if "/" in loc["file"] else None
    if not os.path.exists(path):
        path = os.path.join(ROOT, "harness/data/keytexts",
                            os.path.basename(loc["file"]))
    toks = w35.key_tokens(open(path, encoding="utf-8", errors="replace").read())
    i, words, seen = loc["token"], [], set()
    while len(words) < L:
        w = toks[i]
        if loc["var"] == "P" or w not in seen:
            seen.add(w); words.append(w)
        i += 1
    key = [w35.word_shift(w) for w in words]
    p = [ord(c) - 65 for c in pt]
    return "".join(chr(65 + (a + k) % 26) for a, k in zip(p, key)), words


def main():
    g = gate_summary()
    if not g or not g["gate_passes"]:
        print(json.dumps({"status": "UNTESTED",
                          "reason": "gate did not reach Wilson LB >= 0.20",
                          "gate": g}, indent=1))
        return
    data = json.loads(open(os.path.join(ROOT, "ciphers/wood_35.json")).read())
    ct_s = re.sub(r"[^A-Z]", "", data["text"].upper())
    assert len(ct_s) == L, (ct_s, len(ct_s))
    e = search.Engine(tiers=TIERS)
    ct = search.to_ints(ct_s)
    best, res, cand, sc = e.search(ct, top=25)
    n = null_summary()
    bar = {"cond1_beats_null_max": n is not None and best > n["max"],
           "cond2_under_2pct": None,
           "cond3_above_plaintext_floor": best > g["truth_score_p05"],
           "null_max": None if n is None else n["max"],
           "plaintext_floor_p05": g["truth_score_p05"]}
    if n is not None:
        nn = [json.loads(l) for l in open(os.path.join(HERE, "out_null.jsonl"))]
        vals = [d["best_score"] for d in nn if "best_score" in d]
        reach = sum(1 for v in vals if v >= best)
        bar["cond2_under_2pct"] = reach / len(vals) < 0.02
        bar["nulls_reaching_real"] = reach
        bar["nulls"] = len(vals)
    for r in res:
        try:
            back, words = reencrypt(r, r["pt"])
            r["reencrypts"] = (back == ct_s)
            r["key_words"] = words
        except Exception as ex:                       # noqa: BLE001
            r["reencrypts"] = False
            r["reencrypt_error"] = str(ex)
    out = {"tiers": list(TIERS), "K": e.K, "ciphertext": ct_s,
           "best_score": best, "bar": bar,
           "passes_all_three": all(v is True for k, v in bar.items()
                                   if k.startswith("cond")),
           "top": res}
    json.dump(out, open(os.path.join(HERE, "out_real_%s.json" %
                                     "".join(TIERS)), "w"), indent=1)
    print(json.dumps({k: out[k] for k in
                      ("tiers", "K", "best_score", "bar", "passes_all_three")}, indent=1))
    for r in res[:10]:
        print(r["score"].__round__(4), r["tier"], r["file"], r["var"], r["token"],
              r["pt"], "reenc" if r.get("reencrypts") else "BAD")


if __name__ == "__main__":
    main()
