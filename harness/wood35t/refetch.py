"""Rebuild the Round 52 amendment-1 key corpus (same book list, same tokenisation via
harness/wood35/w35.py) into local shards, for multilingual re-scoring."""
import os, sys, json, threading, queue
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'wood35'))
os.environ.setdefault('W35_SHARDS', '.cache/wood35/w35_shards')
import fetch_books as fb
OUT = os.environ['W35_SHARDS']; fb.OUT = OUT
os.makedirs(OUT, exist_ok=True)
rows = [json.loads(l) for l in open(os.path.join(HERE, '..', 'wood35', 'fetch_r52.jsonl'))]
todo = []; seen = set()
for r in rows:
    k = (r['lang'], r['id'])
    if 'tokens' in r and k not in seen:
        seen.add(k); todo.append(k)
print('books', len(todo), flush=True)
q = queue.Queue()
for t in todo: q.put(t)
lock = threading.Lock(); st = {'ok': 0, 'tok': 0, 'fail': 0}
log = open(os.path.join(OUT, 'refetch_log.jsonl'), 'a')
def worker():
    while True:
        try: lang, pid = q.get_nowait()
        except queue.Empty: return
        try:
            n = fb.fetch_one(lang, pid)
        except Exception as ex:
            with lock:
                st['fail'] += 1; log.write(json.dumps({'lang': lang, 'id': pid, 'error': type(ex).__name__}) + '\n')
            continue
        with lock:
            st['ok'] += 1; st['tok'] += n
            log.write(json.dumps({'lang': lang, 'id': pid, 'tokens': n}) + '\n')
            if st['ok'] % 200 == 0:
                log.flush(); print(st, flush=True)
ts = [threading.Thread(target=worker, daemon=True) for _ in range(int(os.environ.get('W', '12')))]
for t in ts: t.start()
for t in ts: t.join()
log.close(); print('DONE', st, flush=True)
