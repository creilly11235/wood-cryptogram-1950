# English-only search pre-registration (17 September 2026): #35, T. E. Wood's cryptogram

Written and committed **before any score of Wood's ciphertext exists**. Nothing
in this repository has ever scored it: `attempts/NOTES.md` records the item as
"Not attempted".

## 1. Target and why now

`ciphers/wood_35.json` — 21 letters, published 1950:

```
FVAMI NTKFX XWATB OIZVV X
```

Wood stated his cipher uses the **same method as Thouless**, and that the key
derives from **a specific published non-English text**. Thouless's Message B was
solved in 2019 by Richard Bean and is reproduced exactly here by
`harness/verify_thouless_b.py`. The method is therefore not a hypothesis: it is
a known, verified mechanism.

**Why this round exists.** The repository already dismissed #35, twice, on this
argument (`attempts/NOTES.md` line 46, `notes/STOPPING_REVIEW_R45.md` §3):

> at 21 letters, any key sequence produces plausible text

That statement is *true of an unrestricted running key* and *false of Wood's
declared mechanism*, and the difference is arithmetic, not opinion:

| hypothesis class | K | ln K | N·D (D_en = 1.4247 nats) | unicity margin |
|---|---:|---:|---:|---:|
| unrestricted 21-letter running key | 26^21 | 68.42 | 29.92 | **−38.50** |
| word-sum key from a corpus of published texts (this round) | 28,602,798 | 17.17 | 29.92 | **+12.75** |

The dismissal used the first row's number against the second row's mechanism.
A margin of +12.75 nats means the expected number of spurious hypotheses that
match true English as well as the truth does is about e^−12.75 ≈ 3 × 10^−6.
The class is finite and enumerable, so it is exhaustible in the sense
`notes/STOPPING_REVIEW_R45.md` requires, and a hit is *verifiable* the way
Bean's was: by naming the book and the word offset and re-encrypting.

**Margin is not power.** The earlier power-control finding. The margin above says the
answer is identifiable in principle; §6's gate is what decides whether the
search actually finds it. If the gate fails, this round reports #35 as
**untested**, never as negative.

## 2. Mechanism (frozen)

Exactly the convention `harness/verify_thouless_b.py` verifies:

- tokenise the key text: NFKD, drop combining marks, uppercase, maximal `[A-Z]+` runs;
- one key **word** per ciphertext **letter**;
- `shift = (sum of the word's letters, A=1..Z=26, − 1) mod 26`;
- `plaintext = (ciphertext − shift) mod 26`.

Two readings of Thouless's "consecutive distinct words" are both swept:

- **variant D** — walk forward from the start offset, skipping any word already
  used in this keystream (Bean's reading; first-occurrence order);
- **variant P** — plain consecutive words, repeats kept.

Keystreams never cross a file boundary.

**Known-answer check, run before this registration was committed**
(`harness/wood35/known_answer.py`): applying the same index code at L = 74 to
Francis Thompson's *The Hound of Heaven* recovers Thouless Message B exactly,
at **one row out of 33,321**, variant D, token offset 12210. The tokenisation,
dedupe walk, shift convention and row→offset mapping are therefore the ones
that actually solved a cipher of this family.

## 3. Hypothesis class (frozen)

Primary sweep: tiers **B** and **E**, variants **D** and **P**, every start
offset, from `harness/wood35/w35.py`:

| tier | what | files | words | hypotheses |
|---|---|---:|---:|---:|
| B | non-English published books (Gutenberg da/de/es/fr/it/la/nl/sv) + the 1773 Dutch psalter | 81 | 7,414,993 | 14,826,428 |
| E | published English books (Gutenberg) | 48 | 6,889,227 | 13,776,370 |
| | **primary total** | **129** | **14,304,220** | **K = 28,602,798** |

Wood said the key text is non-English; that is his claim, not an observation,
so tier E is swept too and reported separately.

Secondary sweep, reported separately and never merged into the primary bar:
tier **S**, the Tatoeba sentence dumps (bel ces est fin lat lit pol rulat ukr),
9 files, 11,066,448 words, 22,132,525 hypotheses. These are not continuous
published texts — their word order is an artefact of the collection — so they
carry near-zero prior and are excluded from the primary class on purpose.

Also registered as secondary, run only if the primary gate passes:
convention B (`shift = sum mod 26`, i.e. the primary plaintext Caesar-shifted by
one), and the additive direction (`plaintext = ciphertext + shift`).

**Plaintext language: English only** for the decision. Wood was English and
Thouless B's plaintext is English. (`attempts/NOTES.md` line 46 calls the
plaintext "multilingual"; no source in this repository supports that, and
`research/status/group-31-40.md` does not say it. Other plaintext languages are
a separate exploratory arm, reported without a decision.)

## 4. Objective and search (frozen)

Identical to the earlier power-control experiment so the numbers are comparable:

```
score(pt) = (5-gram log-probability, nats, per scored character)
          + W_SEG * seg(pt) / len(pt)
ORDER = 5, W_SEG = 1.0, NORD = 20000, model = harness/data/ngrams/en_5.npy
```

Two-stage, because the full objective over 28.6M rows per ciphertext is wasteful:

- **stage 1** — rank all K rows by the 5-gram term alone;
- **stage 2** — rescore the top **5,000** under the full objective; report the top 20.

The funnel can in principle drop the truth. The gate measures the whole
two-stage pipeline end to end, so that loss is inside the measured power.

`SEED = 20260918`.

## 5. Arms

- **Arm G** — power gate, §6.
- **Arm N** — 200 nulls, §7.
- **Arm R** — the real ciphertext, decided against §7's bar.
- **Arm S** — the tier-S sweep, reported, no decision.

## 6. Power gate

100 plants. Plant *j*:

1. draw a 21-letter English plaintext beginning at a word boundary from
   `harness/data/corpus_extra/en` — **held out** from the `en_5` model, which
   `harness/ngrams.py` builds from `harness/data/corpus/en`; any file whose
   basename also occurs in `corpus/en` is excluded;
2. draw a row of the primary keystream matrix uniformly at random;
3. encipher; run the full two-stage search over all 28,602,798 rows.

**Recovered** = the rank-1 row under the full objective decodes to the planted
21 letters exactly. Also recorded, for the record and not for the decision: the
raw rank of the true row, and its rank after collapsing neighbourhoods (rows of
the same file and variant within ±21 tokens of each other count once, because
adjacent starts share most of their keystream and are not independent decoys).

**Gate condition: Wilson 95% lower bound on the exact-recovery rate ≥ 0.20.**
If it fails, arm R is reported as **untested**, not negative, and no bar is
applied to it.

## 7. Decision bar (all three, fixed here)

Nulls: 200 ciphertexts of 21 uniform random letters. (Enciphering a uniform
random plaintext with a real key gives exactly this distribution, so the two
constructions are identical; the simpler one is used.) Each is swept
identically and its best full-objective score recorded.

1. real best score **>** the maximum of the 200 null best scores;
2. **<2%** of the nulls (≤ 3 of 200) reach the real best score;
3. **absolute floor** — real best score **>** the 5th percentile of the 100
   gate plants' scores *under their true keys*.

Condition 3 is the plant-floor repair: conditions 1–2 alone are vacuous when the
null is empty and saturated when it is full.

A **solve** is declared only if all three pass **and** the top row's plaintext
is readable English **and** re-encryption under the named (file, token offset,
variant) reproduces the ciphertext exactly. Anything less is reported as a
candidate, not a solution.

## 8. Kill criterion

- Gate Wilson LB < 0.20 → stop; report #35 untested; do not run arms N or R's decision.
- 12 CPU-hours total → stop; report on whatever plants completed, with the
  reduced Wilson bound.
- Any hit that cannot be re-encrypted exactly from its named offset is discarded.

## 9. What a negative here would and would not mean

A clean negative would mean: **Wood's key text is not one of these 129 books at
any offset, under either reading of "distinct", with an English plaintext.**
It would not exclude the mechanism, another book, another plaintext language,
or a different tokenisation of the same book. The dominant limitation is
corpus coverage — 129 published texts is a small slice of what was in print
before 1950 — and that is the honest reason to expect a negative.
