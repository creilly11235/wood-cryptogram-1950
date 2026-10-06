"""Known-answer check: the September English-only search index must recover Thouless Message B.

Message B is 74 letters, not 21, so this runs the same machinery at L=74 on the
one text Bean identified (Francis Thompson, The Hound of Heaven).  It proves the
tokenisation, the dedupe walk, the shift convention and the row->offset mapping
are the ones that actually solved a cipher of this family.  It does not touch
Wood's ciphertext.
"""
import json, re, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import w35

ROOT = w35.ROOT
EXPECT = "ANUMBEROFSUCCESSFULEXPERIMENTSOFTHISKINDWOULDGIVESTRONGEVIDENCEFORSURVIVAL"


def main():
    ct = re.sub(r"[^A-Z]", "", json.loads(
        open(os.path.join(ROOT, "ciphers/thouless_b_35_SOLVED.json")).read())["text"].upper())
    assert len(ct) == 74, len(ct)
    path = os.path.join(ROOT, "harness/data/keytexts/41215.txt")
    kd, pd, kp, pp = w35.file_streams(path, L=74)
    c = np.frombuffer(ct.encode(), dtype=np.uint8).astype(np.int16) - 65
    pt = (c[None, :] - kd.astype(np.int16)) % 26
    want = np.frombuffer(EXPECT.encode(), dtype=np.uint8).astype(np.int16) - 65
    hit = np.flatnonzero((pt == want[None, :]).all(axis=1))
    out = {"variant": "D", "rows_matching_full_plaintext": hit.tolist(),
           "token_offsets": pd[hit].tolist(), "starts_D": int(kd.shape[0])}
    if hit.size:
        agree = (pt == want[None, :]).mean(axis=1)
        out["best_other_agreement"] = float(np.sort(agree)[-2])
    print(json.dumps(out, indent=1))
    assert hit.size == 1, "expected exactly one exact recovery"
    return out


if __name__ == "__main__":
    main()
