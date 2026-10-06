"""the English-only search (17 September 2026): #35 T. E. Wood's cryptogram, book-derived word-sum running key.

The mechanism is Wood's own declared one ("same method as Thouless"), already
reproduced exactly on the solved Thouless Message B by
`harness/verify_thouless_b.py`:

    one key WORD per ciphertext LETTER;
    shift = (sum of the word's letters, A=1..Z=26, minus 1) mod 26;
    plaintext letter = ciphertext letter - shift  (mod 26).

Thouless's instruction says *consecutive distinct* words, and Bean's recovery
drops repeats while keeping first-occurrence order.  That makes the hypothesis
class the set of (file, start offset, variant) triples over a corpus of
published texts -- finite and enumerable, which is the whole point of this
round.  This module only builds and indexes that class; it never reads a
ciphertext.
"""
import os, re, sys, json, hashlib, unicodedata
import numpy as np
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repository root
DATA = os.path.join(HERE, "..", "data")
DATA = os.path.normpath(DATA)

L = 21                      # Wood's ciphertext length; one key word per letter
SEED = 20260918

# Tier B: published non-English books (Project Gutenberg texts, one dir per
# language) plus the 1773 Dutch psalter.
TIER_B_LANGS = ("da", "de", "es", "fr", "it", "la", "nl", "sv")
# Tier E: published English books.  Wood said the key text is non-English; that
# is his claim, not an observation, so English is swept too.
TIER_E_LANGS = ("en",)
# Tier S: Tatoeba sentence dumps.  These are not continuous published texts --
# their word order is an artefact of the collection -- so they are a separate,
# secondary sweep, not part of the primary hypothesis class.
TIER_S_LANGS = ("bel", "ces", "est", "fin", "lat", "lit", "pol", "rulat", "ukr")


def key_tokens(text):
    """Exactly the tokenisation verified against Bean's Thouless B solution:
    NFKD, drop combining marks, uppercase, maximal runs of A-Z."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.findall(r"[A-Z]+", text.upper())


def word_shift(w):
    return (sum(ord(c) - 64 for c in w) - 1) % 26


def tier_files(tier):
    langs = {"B": TIER_B_LANGS, "E": TIER_E_LANGS, "S": TIER_S_LANGS}[tier]
    out = []
    for lang in langs:
        d = os.path.join(DATA, "corpus", lang)
        for fn in sorted(os.listdir(d)):
            out.append((f"{lang}/{fn}", os.path.join(d, fn)))
    if tier == "B":
        p = os.path.join(DATA, "keytexts", "psalmen1773.txt")
        if os.path.exists(p):
            out.append(("nl/psalmen1773.txt", p))
    return out


@njit(cache=True)
def _dedup_stream(shifts, wid, out_keys, out_pos, L):
    """Variant D: from each start, walk forward collecting DISTINCT words until
    L are collected.  Returns the number of usable starts."""
    n = shifts.shape[0]
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
                out_keys[k, m] = shifts[j]
                m += 1
            j += 1
        if m < L:
            break
        out_pos[k] = i
        k += 1
    return k


def file_streams(path, L=L):
    """Return (keys_D, pos_D, keys_P, pos_P) for one file.

    keys_* are uint8 [n, L] shift matrices; pos_* are the token offsets that
    generated them, so any hit names a reproducible (file, token index)."""
    toks = key_tokens(open(path, encoding="utf-8", errors="replace").read())
    if len(toks) < L:
        z8 = np.zeros((0, L), dtype=np.uint8)
        z4 = np.zeros(0, dtype=np.int32)
        return z8, z4, z8, z4
    shifts = np.array([word_shift(w) for w in toks], dtype=np.int64)
    vocab = {}
    wid = np.empty(len(toks), dtype=np.int64)
    for i, w in enumerate(toks):
        wid[i] = vocab.setdefault(w, len(vocab))
    kd = np.zeros((len(toks), L), dtype=np.uint8)
    pd = np.zeros(len(toks), dtype=np.int32)
    n = _dedup_stream(shifts, wid, kd, pd, L)
    kd, pd = kd[:n], pd[:n]
    m = len(toks) - L + 1
    kp = np.ascontiguousarray(np.lib.stride_tricks.sliding_window_view(
        shifts.astype(np.uint8), L))
    pp = np.arange(m, dtype=np.int32)
    return kd, pd, kp, pp


def build_index(tiers=("B", "E"), cache=None):
    """Concatenate every hypothesis in the given tiers into one keystream
    matrix, with a parallel table naming (tier, file, variant, token offset)."""
    if cache and os.path.exists(cache + ".npy"):
        keys = np.load(cache + ".npy", mmap_mode="r")
        meta = json.load(open(cache + ".json"))
        return keys, meta
    blocks, meta = [], {"tiers": list(tiers), "L": L, "files": [], "index": []}
    at = 0
    for tier in tiers:
        for name, path in tier_files(tier):
            kd, pd, kp, pp = file_streams(path)
            h = hashlib.sha256(open(path, "rb").read()).hexdigest()
            meta["files"].append({"tier": tier, "name": name, "sha256": h,
                                  "n_D": int(kd.shape[0]), "n_P": int(kp.shape[0])})
            for var, k, p in (("D", kd, pd), ("P", kp, pp)):
                if k.shape[0]:
                    blocks.append(k)
                    meta["index"].append({"tier": tier, "name": name, "var": var,
                                          "start": at, "n": int(k.shape[0]),
                                          "first_token": int(p[0])})
                    at += int(k.shape[0])
    keys = np.concatenate(blocks, axis=0)
    meta["K"] = int(keys.shape[0])
    if cache:
        np.save(cache + ".npy", keys)
        json.dump(meta, open(cache + ".json", "w"), indent=1)
    return keys, meta


def locate(meta, row):
    """Map a row of the keystream matrix back to (tier, file, variant, token)."""
    for e in meta["index"]:
        if e["start"] <= row < e["start"] + e["n"]:
            return dict(tier=e["tier"], file=e["name"], var=e["var"],
                        token=e["first_token"] + (row - e["start"]), row=int(row))
    raise IndexError(row)


if __name__ == "__main__":
    tiers = tuple(sys.argv[1:]) or ("B", "E")
    tot = {}
    for tier in tiers:
        nD = nP = words = nfile = 0
        for name, path in tier_files(tier):
            kd, pd, kp, pp = file_streams(path)
            nD += kd.shape[0]; nP += kp.shape[0]
            words += len(key_tokens(open(path, encoding="utf-8", errors="replace").read()))
            nfile += 1
        tot[tier] = dict(files=nfile, words=words, starts_D=int(nD), starts_P=int(nP),
                         hypotheses=int(nD + nP))
        print(tier, json.dumps(tot[tier]))
    K = sum(v["hypotheses"] for v in tot.values())
    print(json.dumps({"tiers": list(tiers), "K": K, "lnK": round(float(np.log(K)), 4)}))
