"""Rebuild the September English-only search amendment-1 key corpus (same book list, same tokenisation via
harness/wood35/w35.py) into local shards, for multilingual re-scoring.

Each shard records the SHA-256 of the bytes Gutenberg served. `corpus_manifest.jsonl`
beside this script pins those hashes: a shard whose hash disagrees with the manifest is
rejected (deleted and logged as a mismatch) so a changed upstream text cannot silently
replace the input behind a reported run. Any fetch failure also makes the exit code non-zero,
so a partial corpus is never scored by mistake. Without RECORD=1 every book in the list must already
be pinned, or the script stops before fetching; RECORD=1 appends unlisted books. The manifest was not captured by the original 3,847-book run (its shards
were never committed), so the first recording run defines it; see RESULT.md."""
import os, sys, json, threading, queue
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'wood35'))
os.environ.setdefault('W35_SHARDS', '.cache/wood35/w35_shards')
import fetch_books as fb
OUT = os.environ['W35_SHARDS']; fb.OUT = OUT
os.makedirs(OUT, exist_ok=True)
MANIFEST = os.path.join(HERE, 'corpus_manifest.jsonl')
RECORD = os.environ.get('RECORD') == '1'
pinned = {}
if os.path.exists(MANIFEST):
    for l in open(MANIFEST):
        m = json.loads(l); pinned[(m['lang'], m['id'])] = m['sha256']
rows = [json.loads(l) for l in open(os.path.join(HERE, '..', 'wood35', 'fetch.jsonl'))]
todo = []; seen = set()
for r in rows:
    k = (r['lang'], r['id'])
    if 'tokens' in r and k not in seen:
        seen.add(k); todo.append(k)
missing = [k for k in todo if k not in pinned]
print('books', len(todo), 'pinned', len(pinned), 'unpinned', len(missing), 'record', RECORD, flush=True)
if missing and not RECORD:
    print('ERROR: %d books have no entry in corpus_manifest.jsonl; nothing fetched. Run with RECORD=1 to '
          'define the manifest, and say so in the RESULT (a run on unpinned inputs is not reproducible)' % len(missing), flush=True)
    sys.exit(1)
q = queue.Queue()
for t in todo: q.put(t)
lock = threading.Lock(); st = {'ok': 0, 'tok': 0, 'fail': 0, 'mismatch': 0, 'unpinned': 0}
log = open(os.path.join(OUT, 'refetch_log.jsonl'), 'a')
man = open(MANIFEST, 'a') if RECORD else None
def shard_sha(lang, pid):
    p = fb.shard_path(lang, pid)
    return str(np.load(p)['sha256'][0]) if os.path.exists(p) else None
def worker():
    while True:
        try: lang, pid = q.get_nowait()
        except queue.Empty: return
        try:
            n = fb.fetch_one(lang, pid)
            sha = shard_sha(lang, pid)
            if n and sha is None:
                raise KeyError('shard has no sha256 member')
        except Exception as ex:
            with lock:
                st['fail'] += 1; log.write(json.dumps({'lang': lang, 'id': pid, 'error': type(ex).__name__}) + '\n')
            continue
        with lock:
            want = pinned.get((lang, pid))
            if want is not None and sha != want:
                st['mismatch'] += 1
                log.write(json.dumps({'lang': lang, 'id': pid, 'mismatch': True, 'expected': want, 'got': sha}) + '\n')
                try: os.remove(fb.shard_path(lang, pid))
                except OSError: pass
                continue
            if want is None:
                if man is None or sha is None:
                    st['unpinned'] += 1
                    log.write(json.dumps({'lang': lang, 'id': pid, 'unpinned': True}) + '\n')
                    try: os.remove(fb.shard_path(lang, pid))
                    except OSError: pass
                    continue
                man.write(json.dumps({'lang': lang, 'id': pid, 'sha256': sha, 'tokens': n}) + '\n')
                pinned[(lang, pid)] = sha
            st['ok'] += 1; st['tok'] += n
            log.write(json.dumps({'lang': lang, 'id': pid, 'tokens': n, 'sha256': sha}) + '\n')
            if st['ok'] % 200 == 0:
                log.flush(); print(st, flush=True)
ts = [threading.Thread(target=worker, daemon=True) for _ in range(int(os.environ.get('W', '12')))]
for t in ts: t.start()
for t in ts: t.join()
log.close()
if man is not None: man.close()
print('DONE', st, flush=True)
processed = st['ok'] + st['fail'] + st['mismatch'] + st['unpinned']
if processed != len(todo):
    st['fail'] += len(todo) - processed
    print('ERROR: %d of %d books were never processed (worker died?)' % (len(todo) - processed, len(todo)), flush=True)
if st['mismatch'] or st['unpinned'] or st['fail']:
    print('ERROR: %d books differ from corpus_manifest.jsonl, %d have no entry (shards removed), %d failed to '
          'fetch; the corpus is incomplete and must not be scored' % (st['mismatch'], st['unpinned'], st['fail']), flush=True)
    sys.exit(1)
