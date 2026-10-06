import fetch_corpus as fc, os, csv, time
ids = [16732, 27889, 48105, 39281, 9105, 63190, 26150, 7018, 33670, 39204]
rows = {r["Text#"]: r for r in csv.DictReader(open("data/pg_catalog.csv", encoding="utf-8"))}
fiction = [int(r["Text#"]) for r in rows.values() if r["Language"] == "en" and r["Type"] == "Text" and int(r["Text#"]) < 3000 and "fiction" in r["Subjects"].lower()]
ids += fiction[:110]
os.makedirs("data/corpus_extra/en", exist_ok=True)
have = set(os.listdir("data/corpus/en"))
for pgid in ids:
    out = f"data/corpus_extra/en/{pgid}.txt"
    if os.path.exists(out) or f"{pgid}.txt" in have: continue
    try:
        open(out, "w", encoding="utf-8").write(fc.strip(fc.fetch(pgid))); print("got", pgid, flush=True)
    except Exception as e: print("fail", pgid, e, flush=True)
    time.sleep(0.2)
