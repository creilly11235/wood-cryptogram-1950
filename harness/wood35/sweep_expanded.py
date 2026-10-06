"""Amendment 1 sweep: stream every key shard past all ciphertexts at once.

No global key matrix: each book is turned into its two keystream blocks, all
141 ciphertexts are scored against that block, the per-ciphertext top-T rows are
kept with provenance, and the block is dropped.  Memory stays flat and the
corpus can grow past what would fit.
"""
import os, sys, json, glob, math, time
import numpy as np
from numba import njit, prange
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import search, w35                                  # noqa: E402

ROOT = search.ROOT
L = search.L
ORDER = search.ORDER
TOPT = int(os.environ.get("W35_TOPT", "50"))
SHARDS = os.environ.get("W35_SHARDS", ".cache/wood35"
                        "/w35_shards")
NPLANT = int(os.environ.get("W35_NPLANT", "40"))
NNULL = int(os.environ.get("W35_NNULL", "100"))


@njit(parallel=True, cache=True)
def stage1_multi(cts, keys, table, out):
    """out[c, r] = 5-gram log10 total of ciphertext c decrypted under row r.
    Rows are the outer loop so each key is read once and reused across all
    ciphertexts."""
    n = keys.shape[0]
    C = cts.shape[0]
    base = 26 ** (ORDER - 1)
    for r in prange(n):
        for c in range(C):
            idx = 0
            for i in range(ORDER):
                p = cts[c, i] - keys[r, i]
                if p < 0:
                    p += 26
                idx = idx * 26 + p
            s = table[idx]
            for i in range(ORDER, L):
                p0 = cts[c, i - ORDER] - keys[r, i - ORDER]
                if p0 < 0:
                    p0 += 26
                p = cts[c, i] - keys[r, i]
                if p < 0:
                    p += 26
                idx = (idx - p0 * base) * 26 + p
                s += table[idx]
            out[c, r] = s


def shard_iter():
    """(source name, variant, keystream block, token offsets) for every indexed
    text: first the tier B and E files already in the repository, then every
    downloaded Gutenberg shard."""
    for tier in ("B", "E"):
        for name, path in w35.tier_files(tier):
            kd, pd, kp, pp = w35.file_streams(path)
            yield (tier + ":" + name, kd, pd, kp, pp)
    for p in sorted(glob.glob(os.path.join(SHARDS, "*.npz"))):
        z = np.load(p)
        shifts = z["shifts"].astype(np.int64)
        wid = z["wid"].astype(np.int64)
        if shifts.shape[0] < L:
            continue
        kd = np.zeros((shifts.shape[0], L), dtype=np.uint8)
        pd = np.zeros(shifts.shape[0], dtype=np.int32)
        n = w35._dedup_stream(shifts, wid, kd, pd, L)
        kd, pd = kd[:n], pd[:n]
        m = shifts.shape[0] - L + 1
        kp = np.ascontiguousarray(np.lib.stride_tricks.sliding_window_view(
            z["shifts"], L))
        yield ("G:" + os.path.basename(p)[:-4], kd, pd, kp,
               np.arange(m, dtype=np.int32))


@njit(cache=True)
def dedup_count(wid, L):
    """How many starts admit L distinct words, without materialising keys."""
    n = wid.shape[0]
    seen = np.empty(L, dtype=np.int64)
    k = 0
    for i in range(n):
        m = 0
        j = i
        while j < n and m < L:
            w = wid[j]
            dup = False
            for t in range(m):
                if seen[t] == w:
                    dup = True
                    break
            if not dup:
                seen[m] = w
                m += 1
            j += 1
        if m < L:
            break
        k += 1
    return k


@njit(parallel=True, cache=True)
def collect(buf, n, thresh, flags):
    """flags[c, r] = 1 where the score clears that ciphertext's current cut."""
    C = buf.shape[0]
    for c in prange(C):
        t = thresh[c]
        for r in range(n):
            flags[c, r] = 1 if buf[c, r] > t else 0


def count_rows():
    tot, files = 0, 0
    for name, kd, pd, kp, pp in shard_iter():
        tot += kd.shape[0] + kp.shape[0]
        files += 1
    return tot, files


def meta_iter():
    """(name, word ids, token count) without materialising any keystream --
    enough to count rows for the plan."""
    for tier in ("B", "E"):
        for name, path in w35.tier_files(tier):
            toks = w35.key_tokens(open(path, encoding="utf-8",
                                       errors="replace").read())
            vocab = {}
            wid = np.empty(len(toks), dtype=np.int64)
            for i, w in enumerate(toks):
                wid[i] = vocab.setdefault(w, len(vocab))
            yield tier + ":" + name, wid
    for p in sorted(glob.glob(os.path.join(SHARDS, "*.npz"))):
        z = np.load(p)
        yield "G:" + os.path.basename(p)[:-4], z["wid"].astype(np.int64)


def build_plan(path):
    """One counting pass, so plant keys can be drawn uniformly over the whole
    expanded class before anything is scored."""
    idx, at = [], 0
    for name, wid in meta_iter():
        if wid.shape[0] < L:
            continue
        for var, n in (("D", dedup_count(wid, L)), ("P", wid.shape[0] - L + 1)):
            if n > 0:
                idx.append({"name": name, "var": var, "start": at, "n": int(n)})
                at += int(n)
    plan = {"K": at, "blocks": idx}
    json.dump(plan, open(path, "w"))
    return plan


def row_to_block(plan, row):
    lo, hi = 0, len(plan["blocks"]) - 1
    while lo < hi:
        m = (lo + hi + 1) // 2
        if plan["blocks"][m]["start"] <= row:
            lo = m
        else:
            hi = m - 1
    b = plan["blocks"][lo]
    return b, row - b["start"]


class Running:
    """Per-ciphertext best-T rows, kept with their keystreams so stage 2 never
    revisits a shard.  Every update is one vectorised merge."""
    def __init__(self, C, t):
        self.C, self.t = C, t
        self.sc = np.full((C, t), -1e30, dtype=np.float32)
        self.key = np.zeros((C, t, L), dtype=np.uint8)
        self.blk = np.full((C, t), -1, dtype=np.int32)
        self.tok = np.zeros((C, t), dtype=np.int32)

    def offer(self, buf, n, keys, blk_id, tokens):
        k = min(self.t, n)
        sub = buf[:, :n]
        part = (np.argpartition(sub, n - k, axis=1)[:, n - k:] if n > k
                else np.broadcast_to(np.arange(n), (self.C, n)))
        csc = np.take_along_axis(sub, part, axis=1)
        ckey = keys[part]                                  # (C, k, L)
        ctok = tokens[part].astype(np.int32)
        allsc = np.concatenate([self.sc, csc], axis=1)
        sel = np.argpartition(allsc, allsc.shape[1] - self.t, axis=1)[:, -self.t:]
        self.sc = np.take_along_axis(allsc, sel, axis=1)
        self.key = np.take_along_axis(
            np.concatenate([self.key, ckey], axis=1), sel[:, :, None], axis=1)
        self.blk = np.take_along_axis(
            np.concatenate([self.blk, np.full(ctok.shape, blk_id, np.int32)],
                           axis=1), sel, axis=1)
        self.tok = np.take_along_axis(
            np.concatenate([self.tok, ctok], axis=1), sel, axis=1)


def main():
    import re, run_gate
    t0 = time.time()
    planp = os.path.join(SHARDS, "plan.json")
    plan = json.load(open(planp)) if os.path.exists(planp) else build_plan(planp)
    K = plan["K"]
    bidx = {(b["name"], b["var"]): i for i, b in enumerate(plan["blocks"])}
    print("expanded class K =", K, " ln K =", round(math.log(K), 3),
          " margin =", round(21 * 1.4247 - math.log(K), 3),
          " blocks", len(plan["blocks"]), flush=True)

    rng = np.random.default_rng(search.SEED + 2)
    plants = run_gate.plant_texts(NPLANT, search.SEED + 2)
    rows = rng.integers(0, K, size=NPLANT)
    want = {}
    for j, r in enumerate(rows):
        b, off = row_to_block(plan, int(r))
        want.setdefault(b["name"], []).append((j, b["var"], off))

    keystreams = {}
    for name, kd, pd, kp, pp in shard_iter():
        if name not in want:
            continue
        for j, var, off in want[name]:
            k, p = (kd, pd) if var == "D" else (kp, pp)
            keystreams[j] = (k[off].copy(), name, var, int(p[off]))
    assert len(keystreams) == NPLANT, (len(keystreams), NPLANT)

    cts, meta = [], []
    for j, p in enumerate(plants):
        key = keystreams[j][0].astype(np.int16)
        cts.append(((search.to_ints(p["pt"]) + key) % 26).astype(np.int16))
        meta.append({"kind": "plant", "j": j, "pt": p["pt"], "plant": p,
                     "true": {"name": keystreams[j][1], "var": keystreams[j][2],
                              "token": keystreams[j][3]}})
    nrng = np.random.default_rng(search.SEED + 3)
    for j in range(NNULL):
        cts.append(nrng.integers(0, 26, size=L).astype(np.int16))
        meta.append({"kind": "null", "j": j})
    real = re.sub(r"[^A-Z]", "", json.loads(
        open(os.path.join(ROOT, "ciphers/wood_35.json")).read())["text"].upper())
    cts.append(search.to_ints(real))
    meta.append({"kind": "real", "ct": real})
    cts = np.ascontiguousarray(np.array(cts, dtype=np.int16))
    C = cts.shape[0]
    print("ciphertexts", C, "=", NPLANT, "plants +", NNULL, "nulls + 1 real",
          flush=True)

    table = search.Scorer("en", ORDER).table
    run = Running(C, TOPT)
    buf = np.empty((C, 1), dtype=np.float32)
    done = rows_seen = 0
    for name, kd, pd, kp, pp in shard_iter():
        for var, k, p in (("D", kd, pd), ("P", kp, pp)):
            n = k.shape[0]
            if not n:
                continue
            if buf.shape[1] < n:
                buf = np.empty((C, n + 100000), dtype=np.float32)
            kk = np.ascontiguousarray(k)
            stage1_multi(cts, kk, table, buf[:, :n])
            run.offer(buf, n, kk, bidx.get((name, var), -1), p)
            rows_seen += n
        done += 1
        if done % 250 == 0:
            el = time.time() - t0
            print("texts", done, "rows", rows_seen, "elapsed", round(el), "s",
                  "eta", round(el * (K / max(rows_seen, 1) - 1)), "s", flush=True)

    wkeys, wvals = search.wordlm.build()
    scratch = np.empty(L + 1, dtype=np.float32)
    out = []
    for c in range(C):
        keep = np.flatnonzero(run.sc[c] > -1e29)
        ks = np.ascontiguousarray(run.key[c][keep])
        sc = np.empty(keep.shape[0]); pts = np.empty((keep.shape[0], L), dtype=np.int64)
        search._full(cts[c], ks, np.arange(keep.shape[0], dtype=np.int64),
                     table, wkeys, wvals, scratch, sc, pts)
        o = np.argsort(-sc)
        def src(i):
            b = plan["blocks"][int(run.blk[c][keep[i]])]
            return [b["name"], b["var"], int(run.tok[c][keep[i]])]
        rec = dict(meta[c])
        rec["best_score"] = float(sc[o[0]])
        rec["top"] = [{"score": float(sc[i]), "src": src(i),
                       "pt": "".join(chr(65 + int(x)) for x in pts[i])}
                      for i in o[:10]]
        if rec["kind"] == "plant":
            rec["recovered"] = rec["top"][0]["pt"] == rec["pt"]
            t = rec["true"]
            rec["true_rank"] = next((r + 1 for r, i in enumerate(o)
                                     if src(i) == [t["name"], t["var"], t["token"]]),
                                    None)
        out.append(rec)

    pl = [r for r in out if r["kind"] == "plant"]
    nu = np.array([r["best_score"] for r in out if r["kind"] == "null"])
    rl = next(r for r in out if r["kind"] == "real")
    rec_n = sum(r["recovered"] for r in pl)
    lb = search.wilson_lb(rec_n, len(pl))
    truth = []
    for r in pl:
        key = keystreams[r["j"]][0].reshape(1, L).astype(np.uint8)
        sc = np.empty(1); pts = np.empty((1, L), dtype=np.int64)
        search._full(cts[r["j"]], key, np.zeros(1, dtype=np.int64), table,
                     wkeys, wvals, scratch, sc, pts)
        truth.append(float(sc[0]))
    floor = float(np.percentile(truth, 5))
    reach = int((nu >= rl["best_score"]).sum())
    summ = {"K": K, "ln_K": math.log(K), "margin_nats": 21 * 1.4247 - math.log(K),
            "texts": done, "plants": len(pl), "recovered": rec_n, "wilson_lb": lb,
            "gate_passes": lb >= 0.20, "nulls": int(nu.shape[0]),
            "null_max": float(nu.max()), "null_median": float(np.median(nu)),
            "plaintext_floor_p05": floor, "real_best": rl["best_score"],
            "cond1_beats_null_max": bool(rl["best_score"] > float(nu.max())),
            "cond2_under_2pct": bool(reach / nu.shape[0] < 0.02),
            "cond3_above_plaintext_floor": bool(rl["best_score"] > floor),
            "nulls_reaching_real": reach,
            "real_percentile_in_nulls": float(100 * (nu < rl["best_score"]).mean()),
            "topT": TOPT, "elapsed_s": round(time.time() - t0)}
    summ["passes_all_three"] = all(summ[k] for k in
                                   ("cond1_beats_null_max", "cond2_under_2pct",
                                    "cond3_above_plaintext_floor"))
    with open(os.path.join(HERE, "out_expanded.jsonl"), "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
        f.write(json.dumps({"summary": summ}) + "\n")
    print(json.dumps(summ, indent=1))
    print("\nreal top 10:")
    for b in rl["top"]:
        print(" ", round(b["score"], 4), b["src"], b["pt"])


if __name__ == "__main__":
    main()
