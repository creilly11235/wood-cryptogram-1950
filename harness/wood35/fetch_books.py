"""Amendment 1 fetcher: stream Gutenberg texts into compact key shards.

Registered order (AMEND_EN_1.md): round-robin across the Latin-script
non-English languages, ascending Gutenberg ID within each language, until the
token budget is reached.  Each book is downloaded, tokenised to its shift array
and word-identity array, saved as a small .npz, and the text deleted.
"""
import os, sys, csv, json, hashlib, threading, queue
import urllib.request
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w35                                          # noqa: E402

ROOT = w35.ROOT
LANGS = ("fr", "de", "it", "es", "nl", "la", "pt", "da", "sv", "ca", "eo",
         "fi", "hu", "pl")
BUDGET = int(os.environ.get("W35_BUDGET", "200000000"))
OUT = os.environ.get("W35_SHARDS", ".cache/wood35"
                     "/w35_shards")
WORKERS = int(os.environ.get("W35_WORKERS", "8"))
URL = "https://www.gutenberg.org/cache/epub/{i}/pg{i}.txt"


def order():
    by = {l: [] for l in LANGS}
    with open(os.path.join(ROOT, "harness/data/pg_catalog.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["Type"] != "Text":
                continue
            if r["Language"] in by:
                by[r["Language"]].append(int(r["Text#"]))
    for l in LANGS:
        by[l].sort()
    out, i = [], 0
    while any(len(by[l]) > i for l in LANGS):
        for l in LANGS:
            if len(by[l]) > i:
                out.append((l, by[l][i]))
        i += 1
    return out


def shard_path(lang, pid):
    return os.path.join(OUT, "%s_%d.npz" % (lang, pid))


def fetch_one(lang, pid):
    p = shard_path(lang, pid)
    if os.path.exists(p):
        return int(np.load(p)["shifts"].shape[0])
    req = urllib.request.Request(URL.format(i=pid),
                                 headers={"User-Agent": "wood-cryptogram-1950/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    txt = raw.decode("utf-8", errors="replace")
    toks = w35.key_tokens(txt)
    if len(toks) < w35.L:
        return 0
    shifts = np.array([w35.word_shift(w) for w in toks], dtype=np.uint8)
    vocab, wid = {}, np.empty(len(toks), dtype=np.int32)
    for i, w in enumerate(toks):
        wid[i] = vocab.setdefault(w, len(vocab))
    np.savez(p, shifts=shifts, wid=wid,
             meta=np.array([pid, len(toks)], dtype=np.int64),
             sha256=np.array([hashlib.sha256(raw).hexdigest()]))
    return len(toks)


def main():
    os.makedirs(OUT, exist_ok=True)
    todo = order()
    print("candidates", len(todo), flush=True)
    q = queue.Queue()
    for t in todo:
        q.put(t)
    lock = threading.Lock()
    state = {"tokens": 0, "books": 0, "fail": 0, "stop": False}
    log = open(os.path.join(HERE, "fetch.jsonl"), "a")

    def worker():
        while not state["stop"]:
            try:
                lang, pid = q.get_nowait()
            except queue.Empty:
                return
            try:
                n = fetch_one(lang, pid)
            except Exception as ex:                   # noqa: BLE001
                with lock:
                    state["fail"] += 1
                    log.write(json.dumps({"lang": lang, "id": pid,
                                          "error": type(ex).__name__}) + "\n")
                continue
            with lock:
                if n:
                    state["tokens"] += n
                    state["books"] += 1
                    log.write(json.dumps({"lang": lang, "id": pid, "tokens": n}) + "\n")
                if state["books"] % 100 == 0:
                    log.flush()
                    print(state["books"], state["tokens"], state["fail"], flush=True)
                if state["tokens"] >= BUDGET:
                    state["stop"] = True

    ts = [threading.Thread(target=worker, daemon=True) for _ in range(WORKERS)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    log.flush(); log.close()
    print(json.dumps({"books": state["books"], "tokens": state["tokens"],
                      "failed": state["fail"], "budget": BUDGET}, indent=1))


if __name__ == "__main__":
    main()
