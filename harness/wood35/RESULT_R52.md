# Round 52 result: #35, T. E. Wood's cryptogram — powered NEGATIVE over 129 books

Registered in `PREREG_R52.md`, committed on 17 Sep 2026 (07:00 UTC) before any score of
Wood's ciphertext existed. **#35 is not solved.**

## 1. Headline

| | |
|---|---|
| Gate (arm G) | **97 / 100 recovered at rank 1**, Wilson 95% LB = **0.915** — passes |
| Primary sweep (arm R) | best **−14.678** over 28,602,798 hypotheses — **fails all three bar conditions** |
| Null ceiling | max over 200 nulls = **−14.306** |
| Plaintext floor | 5th percentile of true-key plant scores = **−13.976** |
| Where the real result sits | the **92.5th percentile of the null distribution** — inside the noise |

The exclusion this buys: **Wood's key text is not any of these 129 published
books, at any of 28,602,798 (file, offset, variant) hypotheses, under either
reading of "consecutive distinct words", with an English plaintext.** It does
not exclude the mechanism, another book, another plaintext language, or a
different tokenisation of the same book.

## 2. The claim this round was opened to check

`attempts/NOTES.md` line 46 and `notes/STOPPING_REVIEW_R45.md` §3 both dismiss
#35 with:

> at 21 letters, any key sequence produces plausible text

**That is true of an unrestricted running key and false of Wood's declared
mechanism, and this round measured the difference rather than arguing it.**

| hypothesis class | K | ln K | N·D | margin | measured rank-1 recovery |
|---|---:|---:|---:|---:|---:|
| unrestricted 21-letter key | 26²¹ | 68.42 | 29.92 | −38.50 | — (not identifiable) |
| word-sum key over this corpus | 28,602,798 | 17.17 | 29.92 | **+12.75** | **97 / 100** |

The dismissal applied the first row's arithmetic to the second row's mechanism.
At 21 letters a *book-constrained* word-sum key is not merely identifiable in
principle — the search finds it, first try, 97 times in 100.

This is the Round 51 lesson used in the direction it actually works: a positive
margin licensed building the gate, and only the gate certified the arm.

## 3. Known-answer check

`harness/wood35/known_answer.py`, run before the registration was committed: the
same index code at L = 74 applied to Francis Thompson's *The Hound of Heaven*
recovers Thouless Message B exactly, at **one row out of 33,321**, variant D,
token offset 12210. Tokenisation, dedupe walk, shift convention and the
row→offset mapping are the ones that solved a cipher of this family.

`harness/wood35/run_real.py` re-derives each candidate's keystream from the named
file and token offset independently of the cached matrix; that path was verified
against the indexed rows on eight gate plants, both variants, before arm R ran.

## 4. Arm G — the power gate

100 plants: a held-out 21-letter English plaintext from `corpus_extra/en`
(excluded from the `en_5` model's training set) enciphered with a uniformly
drawn row, then the full two-stage search over all 28,602,798 rows.

- **97 recovered exactly at rank 1**; Wilson 95% LB **0.9155** ≥ 0.20.
- The true row reached the 5,000-row funnel in **99 / 100**.
- Truth scores: min −20.57, **p05 −13.976**, median −11.996, max −10.288.

**All three failures are plants that are not English**, which the sampler could
not know when it drew them:

| j | planted 21 letters | what it is | true rank |
|---:|---|---|---:|
| 37 | `CARPENTERMRPYNCHEONTU` | proper nouns (*The House of the Seven Gables*) | 7 |
| 55 | `DITJAIBONDROITCADAOLL` | French inside an English-catalogued file | not in funnel |
| 66 | `CELISALIMAELLADORLOOK` | Spanish | 3 |

Recovery on plants that are actually English prose is **97/97**. The registered
number stands as registered — 97/100, LB 0.915 — and this is recorded as an
observation about the plant sampler, not as a re-scored gate.

## 5. Arm N — nulls

200 ciphertexts of 21 uniform random letters, identical search:

```
max -14.306   p98 -14.534   p95 -14.627   median -15.429   min -16.315
```

The gap between the plaintext floor (−13.976) and the null ceiling (−14.306) is
only 0.33, which is exactly why Round 50's third condition is in the bar: the
window in which a real hit must land is narrow, and conditions 1–2 alone would
not have policed it.

## 6. Arm R — Wood's ciphertext

`FVAMI NTKFX XWATB OIZVV X` — 21 letters.

Best over 28,602,798 hypotheses: **−14.678**, at `nl/8099.txt` variant P token
24380 (and the identical passage in `nl/8100.txt`), decoding to
`TGEHADREEKSSENTEASYBI`. It re-encrypts correctly, which only confirms the
bookkeeping; the string is not English.

| condition | requirement | value | verdict |
|---|---|---|---|
| 1 | beat the null maximum, −14.306 | −14.678 | **fail** |
| 2 | fewer than 2% of nulls reach it | 15 / 200 = 7.5% | **fail** |
| 3 | beat the plaintext floor, −13.976 | −14.678 | **fail** |

The real ciphertext scores at the **92.5th percentile of the null
distribution**. Against this corpus it is indistinguishable from 21 random
letters. Every one of the top 25 candidates is nonsense.

## 7. Secondary arms (registered §3, run because the gate passed)

| arm | what | K | best | verdict |
|---|---|---:|---:|---|
| convB | `shift = sum mod 26` | 28,602,798 | −15.366 | negative |
| add | `plaintext = ciphertext + shift` | 28,602,798 | −14.913 | negative |
| S | Tatoeba sentence dumps | 22,132,525 | −16.045 | negative |

convB and add reuse arm N's nulls and arm G's gate exactly, not as a shortcut:
each is a deterministic relabelling of the same key matrix over the same K, so
the best-score distribution against a uniform random ciphertext and the recovery
rate are identical. Tier S has the smaller K, so reusing the B+E null ceiling is
conservative for it.

## 8. What was swept

| tier | contents | files | words | hypotheses |
|---|---|---:|---:|---:|
| B | Gutenberg da/de/es/fr/it/la/nl/sv + the 1773 Dutch psalter | 81 | 7,414,993 | 14,826,428 |
| E | Gutenberg English | 48 | 6,889,227 | 13,776,370 |
| S | Tatoeba dumps (secondary) | 9 | 11,066,448 | 22,132,525 |

CPU: gate 12 min, nulls 17 min, real 12 s, secondaries 51 s — about **0.7
CPU-hours** against a registered 12-hour cap.

## 9. The honest limitation, and what it implies

The dominant weakness is **corpus coverage**, not power. 129 published texts is
a small slice of what was in print before 1950, and Wood said only that his key
text was "a specific published non-English text". A negative over 129 books is
a real exclusion and a small one.

But the gate changes what is worth doing next. At 97% rank-1 recovery and a
+12.75-nat margin, the identifiability budget is nowhere near spent: the margin
stays positive up to K ≈ e²⁹·⁹ ≈ 10¹³ hypotheses, thirteen thousand times the
corpus swept here. **#35 is not information-limited; it is corpus-limited.**
That is a materially different status from the one the repository recorded, and
it makes expanding the key corpus the highest-value follow-up — see
`AMEND_R52_1.md`.
