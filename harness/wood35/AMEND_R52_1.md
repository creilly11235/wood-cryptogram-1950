# Round 52, amendment 1: expand the key corpus

Written and committed **before any expanded-corpus book is downloaded or
scored**. The primary round is finished and reported in `RESULT_R52.md`; this
amendment does not change any number in it.

## Why

The primary gate measured **97/100 rank-1 recovery** at K = 28,602,798 with a
+12.75-nat unicity margin. The identifiability budget is barely touched: the
margin stays positive to K ≈ e^29.9 ≈ 10^13. #35 is therefore **corpus-limited,
not information-limited**, and the one move that raises the chance of a solve is
more key texts.

## What is added (frozen before fetching)

Source: Project Gutenberg, via `harness/data/pg_catalog.csv` (already in the
repository), rows with `Type == Text`.

**Languages**, Latin-script only because the mechanism sums A–Z letters:
`fr, de, it, es, nl, la, pt, da, sv, ca, eo, fi, hu, pl`.
Greek and Chinese holdings are excluded — `key_tokens` would return almost
nothing from them. English is not re-added; tier E already covers the repository's
English books.

**Order**: round-robin across those languages, ascending Gutenberg ID within each
language. Round-robin so that a budget cut falls evenly instead of truncating
whichever language sorts last; ascending ID because low IDs are the earliest and
most canonical additions, which is the better prior for "a published text a
British author would name in 1950".

**Budget**: stop once **200,000,000 key tokens** have been indexed, or the list
is exhausted. Texts are streamed: each is downloaded, tokenised to its shift and
word-identity arrays, and the text file deleted. Books that fail to download or
yield fewer than 21 tokens are skipped and counted.

At the budget the expanded class is K ≈ 4.3 × 10^8, ln K ≈ 19.9, and the margin
is **≈ +10.0 nats** — still positive, and §"gate" below measures what it is
worth.

## Arms, gate and bar at the expanded K

Nothing is inherited from the primary run. All three are recomputed:

- **Gate**: 40 plants, the *same* sampler as §6 of the registration (held-out
  `corpus_extra/en`), full two-stage search over the expanded class.
  **Wilson 95% LB ≥ 0.20 required.** Both the raw rate and the rate over plants
  that are actually English prose are reported; the raw rate is the one that
  decides.
- **Nulls**: 100 ciphertexts of 21 uniform random letters.
- **Bar**: the same three conditions, with the null maximum and the 5th-percentile
  plaintext floor taken from *these* runs.
- **Acceptance**: unchanged — a named file and token offset, a readable English
  plaintext, and exact re-encryption.

Plants are enciphered with rows drawn uniformly from the **expanded** class, so
the gate measures the search that will actually be run.

## Kill criterion

- Gate Wilson LB < 0.20 → the expanded sweep is reported **untested**, not negative.
- The registered 12 CPU-hour cap for Round 52 is unchanged; 0.7 hours are spent.
  If the cap is reached, report on the books indexed so far and say so.
- Any book that cannot be re-fetched and re-tokenised to the same shift array is
  discarded rather than patched.

## What a negative would mean

That Wood's key text is not among the indexed Gutenberg texts at any offset
under either reading of "distinct", with an English plaintext. Gutenberg's
non-English holdings are dominated by canonical literature, which is the right
place to look, but they are still a minority of what was in print before 1950.
A negative here would narrow the search; it would not close #35.
