# #35 T. E. Wood's cryptogram (1950): decipherment, 4 October 2026

**Confirmed by Klaus Schmeh on 4 October 2026 and Richard Bean on 6 October 2026.**

**Status before confirmation, stated precisely (revised after Astra's independent review,
`notes/astra/REVIEW_WOOD35.md`, verdict CONFIRMED WITH RESERVATIONS):**
1. **The decipherment is exact and independently reproduced**: 21/21 letters, exact
   re-encryption, using the repository's established Thouless convention with no
   Wood-specific exception, and an externally attested Luther wording of the Lord's Prayer.
2. **The intended reading is highly plausible**: "Hier bin ich -- Totsiens -- T. E. W."
3. **Under this round's own pre-registered automatic bar it is only a lead** (criterion (b)
   failed; see below). Calling it a solution is a separate, post-hoc human judgment, which this
   project makes and Astra shares in substance.
4. **Priority is not proven.** No earlier published solution was found by this project or by
   Astra (searches listed below), but absence from search results cannot establish that
   nobody solved it first.

Novelty checks: Schmeh's Cipherbrain #35 page and comments (2017-2020), his 2019 Bean article
and later parapsychology cold-case article (both describe Wood as open), klausschmeh.net
search (Wood, Thouless; to Sept 2026), the Top 50 list page, Daniel Bourdeau's Sept 2026
decipherment log, and exact-phrase web searches for the ciphertext and for
`HIERBINICHTOTSIENSTEW` / "Hier bin ich" "Totsiens" "Wood" (no results).

## Result

| | |
|---|---|
| Ciphertext (Schmeh, Cipherbrain, 17 Apr 2017) | `FVAMI NTKFX XWATB OIZVV X` |
| Key text | Matthew 6:9b-11 (the prayer begins at the sixth word of verse 9), in the Luther Bible wording attested for the 1912 text, from "Unser Vater", i.e. the Lord's Prayer: *Unser Vater in dem Himmel! Dein Name werde geheiligt. Dein Reich komme. Dein Wille geschehe auf Erden wie im Himmel. Unser täglich Brot gib uns ...* |
| Method | Thouless's own, exactly as Bean recovered it for Message B: consecutive **distinct** words (four repeated occurrences of three distinct words are skipped: the 2nd and 3rd DEIN, the 2nd HIMMEL, the 2nd UNSER; the 21 key words use 25 word occurrences, ending at UNS), accents folded, word letter-sum A=1..Z=26, shift = (sum - 1) mod 26, plaintext = ciphertext - shift |
| Key words | UNSER VATER IN DEM HIMMEL DEIN NAME WERDE GEHEILIGT REICH KOMME WILLE GESCHEHE AUF ERDEN WIE IM TAGLICH BROT GIB UNS |
| Plaintext | **HIERBINICHTOTSIENSTEW** |
| Reading | **HIER BIN ICH -- TOTSIENS -- T. E. W.**: German "Hier bin ich" ("here am I"), Afrikaans "Totsiens" ("goodbye / until we meet again"; attested in the Dictionary of South African English from 1937), signed with Wood's initials. Two plaintext languages plus a signature. |

Reproduce: `python harness/wood35t/verify_wood.py` (standalone; no repository code imported).
It prints the key words and shifts, asserts the plaintext, re-encrypts it to the published
ciphertext exactly, and shows how specific deviations from the method change the reading (no deduplication breaks it after the first repeat; the off-by-one and the liturgical wording give no reading; a single spelling change alters a single letter).
Output: `verify_output.txt`.

## Evidence for the reading, and its limits

1. **Fit to Wood's statements.** Key from a book not written in English (a German Bible).
   Wood's own paper (*Proceedings of the SPR* 49, 1949-52, pp. 105-106, as indexed; found by
   Astra; direct PDF retrieval failed) says: "The message, if and when deciphered, will not be
   in any one language" -- satisfied by German plus Afrikaans (the initials are not counted as
   a language). The same paper gives the rule of omitting repeated words, which this key needs.
   Method: Thouless's, unchanged.
2. **A strong prior candidate key:** the opening words of the Lord's Prayer in a German Bible.
   This is a natural choice, not the only natural one, and it was recognised as natural after
   the search, so it does not reduce the trial count to one.
3. **The message suits a survival test** ("here am I -- goodbye -- T. E. W."). Thematic, not
   independent proof.
4. **Exact re-encryption** of all 21 letters, no edits.
5. **Found by a blind search**: the Bible tier (19 Latin-script Bibles, 26,730,018 book/offset/
   variant hypotheses per arithmetic convention) put this decryption first in the ordinary
   arithmetic row under the multilingual segmentation score; its pooled 4-gram score is -80.1.
   Correction: in the alternative (sum mod 26) row, the junk string ALENRENDRAYCUTREFUGES
   scored higher (-1.264), so the automatic score does not single it out across both
   conventions; and because only each null's final-score winner was saved, the earlier claim
   "better than every null's best pooled score" is not supported by the saved artifacts.
6. **Chance level (conditional, not a calibrated probability).** Under a uniform-ciphertext
   null each fixed wrong key gives a uniform plaintext. Astra's exact combinatorial union bound
   for a permissive class -- any 18 letters of dictionary words of three or more letters
   (pooled seven-language lexicon plus TOTSIENS) followed by the specific signature TEW --
   is 2.0e-4 expected chance hits over the Bible tier, 4.0e-4 counting both arithmetic
   conventions, and 6.4e-3 over the whole exploratory family of this round (854,049,904
   bookkeeping hypotheses); allowing two-letter words makes the bound uninformative (0.32).
   This project's earlier simulation figure (1 in 2,000,000 for a German ten-letter prefix)
   rests on a single hit in 2,000,000 trials (95% CI 1.3e-8 .. 2.8e-6;
   `harness/wood35t/chance_sim.py`) and is superseded by Astra's bounds. There is no
   defensible single probability for "at least this meaningful" under unrestricted human
   judgment.
7. **Edition sensitivity.** Small spelling differences change single letters (e.g.
   "taeglich" changes only position 18: HIERBINICHTOTSIENNTEW); historical 1545 spellings
   (Himel, geheiliget, kome, auff, teglich) and the 1984 revision do not give the reading.
   The key wording matches the 1912 text; the physical edition Wood used is not established.

## Honest note on the pre-registered automatic bar

`harness/wood35t/PREREG.md` (Amendment 2, Bible tier) set an automatic bar: (a) best score >
null ceiling, (b) >= 5th-percentile plant floor. The gate passed (40/40 plants recovered at rank
1). Wood's best scored -1.270 against a null ceiling of -1.273 (passes by 0.003) and a plant
floor of -1.081 (**fails**). The scorer's lexicons (en fr de la it es pt) contain neither
Afrikaans nor initials, so it parsed TOTSIENS TEW as "TOT/de SIEN/fr STEW/en" and penalised it.
**The full pre-registered rule therefore failed, and under that rule the result is a lead.**
Criteria (c)-(d) pass (a reading a human accepts; named book, offset and exact re-encryption by
script), but the rule required all four. That the scorer lacks Afrikaans and a signature model
is a credible but post-hoc explanation of the shortfall. Treating the result as a solution is a
separate human judgment, stated as such. The Bible-tier results file (04:44:29 UTC) postdates
the Amendment 2 commit (04:41:37 UTC).

## Key-text provenance

- Search hit: christos-c/bible-corpus `bibles/German.xml`, fetched 2026-10-04 from
  raw.githubusercontent.com (master), SHA-256
  49be6f5e464ff94982c8ca58a9ff3afafbcea14eccdaf41b88c02f53792952a3; token offset 533,250
  (the sixth word of b.MAT.6.9), variant D. Reproduce with `harness/wood35t/offset_check.py`.
- Independently confirmed wording: bibel-online.net, Luther 1912, Matthäus 6:9-11; and
  BibleGateway Matthäus 6:9-13 (a modern-spelling text displayed under the LUTH1545 label, not the historical 1545 spelling): "Darum sollt ihr also beten: Unser Vater in
  dem Himmel! Dein Name werde geheiligt. / Dein Reich komme. Dein Wille geschehe auf Erden wie
  im Himmel. / Unser täglich Brot gib uns heute."
- The common liturgical wording ("Vater unser im Himmel ...") does not work; the earlier
  hand-entered passage arm (Arm A) contained only that wording, which is why it missed.

## Credit and context
Method: Robert Thouless (1948); its exact convention recovered by Richard Bean (2019).
Ciphertext and Wood's statements: Klaus Schmeh (Cipherbrain #35; *Nicht zu knacken*).
The multilingual-plaintext reading of Schmeh's note and the Bible-tier search are this round's.

## Addendum: the pre-registered full-corpus arm (the English-only search (17 September 2026) key class, multilingual scoring)

Rebuilt the English-only search (17 September 2026) amendment-1 corpus: 3,847 of 3,848 books (one fetch failure), 14 languages,
K = 400,294,934 hypotheses (variants D and P). Gate **40/40** plants recovered at rank 1,
plant floor -1.081, null ceiling -1.207 (20 nulls). Wood's best decryption here is junk
("OFERANTREFUSAIDAUTIOR", -1.313, below the null ceiling); the literal sum-mod-26 row is junk
too ("ALENRENDRAYCUTREFUGES"). This is the expected negative -- the German Bible is not in that
book list -- and it is qualitative context only: its saved top candidates per row (30 for Wood) are junk, but
the pipeline did not apply the human criterion to every output and it scores signatures poorly,
so it does not certify that no wrong key anywhere produced a comparable reading.
Outputs: `full_gutenberg_ml.json`, `full_gutenberg_ml.out`.

## Addendum 2: further local validation (after Astra's review)

**Primary sources obtained** (`research/incoming/wood35_primary/`, PDFs from iapsop.com, hashes
in SOURCES.md):
- Wood, "A Further Test for Survival", *Proc. SPR* 49 (Part 178), pp. 105-106. Confirms the
  ciphertext `FVAMI NTKFX XWATB OIZVV X`; method = Thouless 1948 pp. 258-260; "The first 21
  words of the key passage are used ... all second and later repetitions of words already used
  in the key passage have been omitted"; "The key passage ... is in an accessible book"; he will
  communicate "in what foreign language the key passage is" (one language); "The message, if
  and when deciphered, will not be in any one language"; the foreign languages are meant to
  defeat attacks by lists of common English words; "My name is T. E. Wood"; born 21 June 1887,
  Yorkshire; practised as a solicitor in Burma. (No South African connection is stated.)
- Thouless, "A Test of Survival", *Proc. SPR* 48 (1948), pp. 258-260: word -> letter whose
  serial number is the letter-sum (remainder mod 26), enciphered through the Vigenere square
  with key A = no shift, i.e. shift = (sum - 1) mod 26 -- **the convention follows from the
  1948 primary text itself**, not only from Bean's reconstruction. Thouless's printed worked
  example (key "To be or not [to be], that is the question. Whether 'tis nobler in [the] mind
  [to] suffer", plaintext THERE IS NO DEATH) is reproduced on letters 1-13 by
  `harness/wood35t/thouless_example_check.py`; letter 14 differs because Thouless himself
  mis-added SUFFER (75 -> W; he printed U, confirmed on the page image
  `thouless_1948_suffer_slip.png`).

**Empirical look-elsewhere test on Wood's real ciphertext** (`harness/wood35t/lookelsewhere.py`,
`tew_hits.py`; outputs `lookelsewhere.json`, `tew_hits.json`). All 3,866 shards (3,847 Gutenberg
books + 19 Bibles), variants D and P, both arithmetic conventions: 854,049,904 decryptions.
Detectors use Wood's initials TEW, known in advance from his paper, as the signature, and 500
random control signatures to measure chance:

| detector | TEW hits | control signatures: mean hits, share with >= 1 |
|---|---:|---|
| first 10 letters = German words (>= 3 letters), last 3 = signature | 1 (ours) | 0.014, 1.4% |
| first 10 letters = words of any of 9 languages, last 3 = signature | 18 | 10.4, 100% (not discriminating) |
| all 18 letters = words (>= 3 letters; union lexicon + TOTSIENS), last 3 = signature | **1 (ours)** | 0.016, 1.4% |

- Of the 18 TEW decryptions with a word-like opening, only one reads all the way through:
  HIERBINICHTOTSIENSTEW at the start of the Lord's Prayer. The other 17 collapse after a few
  letters (LATOSACJAYQJ..., UNDWALKARCQX..., ALLWOOLPYPQF...).
- The rare full-length chance hits for control signatures are word salad from obscure lexicon
  entries (PAYNAULADDUCDAEEVA..., BUMTOPSOIWEIIWATAYE..., WANMOSCALMTORNTOUR...).
- Reading: a mechanical "words + pre-specified signature" criterion is met by chance for about
  1.4% of signatures over this entire search, but none of those chance hits is grammatical or
  meaningful; the Wood decryption is the unique hit for his own initials and is coherent
  German and Afrikaans, at the most natural passage start in an accessible non-English book.

## Addendum — 6 October 2026: confirmation and documentation review

Richard Bean confirmed the reading on 6 October. His review asked what was
searched before the Bibles, what trained the English scorer, and why those
n-gram orders were used. The search is not being reopened. This addendum names
the available inputs and states the missing provenance rather than filling gaps
with a later reconstruction.

Checking code and saved outputs corrected three descriptions: the September
book engine used English **5-grams plus word segmentation**; the full multilingual
Gutenberg result was recorded **after** the Bible hit; and the one-book refetch
failure belongs to that October rebuild, not to the September expansion. The
claim of a verified Gutenberg-and-Wikipedia training mixture is unsupported by
the retained inputs. The committed passage snapshot contains 173 blocks, while
the original result's “about 140” was only an estimate.

Lessons for future runs: name and hash every corpus before scoring; justify
n-gram order against the key class's error model; build lexicons from the
author's known languages first; decide how initials and signatures will score
before the run. Keep internal session labels out of public accounts.

The complete scoring description and input-data inventory are in [the README](../../README.md#scoring).

## What was tried, and when

Dates below are UTC. They describe this project's recorded searches, not every
earlier attempt by other researchers.

1. **17 September 2026 — 129 published texts.** English scoring over 28,602,798
   valid book/offset/variant keys; 97/100 planted messages recovered, but Wood's
   best was unreadable and below the null ceiling. Alternative arithmetic and a
   separate nine-file Tatoeba sentence-key sweep were also negative.
2. **17 September — expanded Gutenberg search.** Added 3,848 books in 14 languages
   to those 129 entries: 3,977 file entries and 428,787,544 valid starts. English
   scoring again gave junk; 12 of 100 random ciphertexts scored higher. The later
   October rebuild scored **3,847 of the 3,848 listed books**, because one refetch
   failed. These are different runs, not two counts of the same run.
3. **4 October, before 04:38 — targeted passages and a multilingual pilot.**
   Famous non-English passages, including the church wording of the German
   Lord's Prayer, were negative. The seven-language pipeline recovered all eight
   plants in a 786-book pilot; Wood was not scored in that pilot.
4. **4 October, 04:41–04:44 — Bible tier.** The amendment adding 19 Latin-script
   Bibles was committed at 04:41:37; the saved result is timed 04:44:29. The
   German Bible's prayer came first in the ordinary-arithmetic row, over a
   bookkeeping key count of 26,730,018. Manual review recognized the reading.
5. **4 October, recorded at 05:11 — full multilingual Gutenberg follow-up.**
   The rebuilt corpus gave junk (best −1.313, null ceiling −1.207; 40/40 plants
   recovered). Its result was recorded **after the Bible hit**, during review,
   although that arm had been registered beforehand. It was not a further
   unsuccessful search completed before trying Bibles.

The September results are in `harness/wood35/RESULT.md`; the targeted,
pilot and Bible arms in `harness/wood35t/RESULT.md`; the solve and later controls
in `attempts/wood35_solve_2026-10-04/REPORT.md`. The historical result files retain
their original verdicts; a negative there is a result for that input and scorer,
not a claim that Wood remained unsolved after 4 October.

## What this does and does not establish

**The cryptogram is solved:** the prayer decrypts all 21 letters and re-encrypts
them exactly. Klaus Schmeh confirmed the reading on 4 October 2026, Richard Bean
on 6 October, and Astra reproduced it independently. The reading is
“Hier bin ich. Totsiens. T.E.W.”

- **The pre-registered automatic bar was not met.** The result beat the null
  ceiling but missed the plant floor. The absence of Afrikaans and initials in
  the scorer explains its awkward split; that explanation and the acceptance of
  the reading are human judgments made after the hit.
- **The chance estimate is a bound, not a calibrated p-value.** Astra's bound
  assumes uniform random letters and a specified dictionary/signature rule,
  chosen after seeing the message. The later 1.4% control-signature result is
  also not the probability that this meaningful reading is wrong.
- **Wording and priority have limits.** The successful wording matches the
  1912 Luther text, but Wood's physical Bible edition is unknown. No earlier
  published solution was found; that does not prove first-ever priority.

The full independent assessment is `notes/astra/REVIEW_WOOD35.md`.
