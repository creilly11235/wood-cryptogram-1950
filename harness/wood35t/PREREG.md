# #35 Wood: multilingual-plaintext re-scoring of the Round 52 key class (pre-registration)

Written 2026-10-04 before Wood's ciphertext is scored against the rebuilt corpus.
(The ~140 hand-entered famous passages in `passages/` were already scored, see RESULT.md;
they are a separate, small arm and are not part of this decision.)

## Why
Round 52 and its amendment searched 428,787,544 (book, offset, variant) hypotheses but
decided on an **English-only** plaintext score (PREREG_R52 "Plaintext language: English
only"). Schmeh (Cipherbrain #35, 17 Apr 2017) reports that Wood's cleartext "is allegedly
authored in several different languages". A correct key with a mixed-language plaintext can
fail an English bar, so the Round 52 negative does not cover this case.

## Mechanism (unchanged, verified)
Round 52 tokenisation (`harness/wood35/w35.py key_tokens`), one key word per letter,
shift = (sum A=1..Z=26 - 1) mod 26, pt = ct - shift; variant D (consecutive distinct words)
and P (all words). Key corpus: the Round 52 amendment-1 book list
(`harness/wood35/fetch_r52.jsonl`, rows with tokens), rebuilt by `refetch.py`.
Books that cannot be fetched after retries are listed, not silently dropped.

## Scoring
1. Prefilter: pooled 4-gram table over en/fr/de/la/it/es/pt with an equal letter budget
   (`pooled.py`), log10 total over the 18 4-grams; keep the top T = 3000 per ciphertext.
2. Rescore: multilingual segmentation `mlseg.score` (best split into lexicon words from
   en fr de la it es pt, word penalty 1.0, language-switch penalty 0.5), per letter.
   Final rank by the mlseg score; unsegmentable strings rank last.

## Gate (plants)
40 plants: plaintext = random frequent words from 2-4 random languages of the lexicon,
concatenated to exactly 21 letters; key = a uniformly random (book, variant, offset) of the
rebuilt class; full search. Recovery = true plaintext ranked 1. Required: Wilson 95% LB
>= 0.20 (the Round 52 standard). Plant floor = 5th percentile of the true plaintexts'
final scores.

## Nulls
20 ciphertexts of 21 uniform random letters, same pipeline. Null ceiling = max final score.

## Bar for Wood (all required)
(a) best final score > null ceiling; (b) >= plant floor; (c) the plaintext reads as words a
human accepts in the stated languages; (d) named book, variant and token offset; exact
re-encryption by script. Anything less is reported as a lead.

## Kill criterion
If the gate fails, the arm reports "not powered" and no claim either way is made.
