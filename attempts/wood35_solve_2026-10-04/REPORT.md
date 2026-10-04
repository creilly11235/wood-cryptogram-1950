# #35 T. E. Wood's cryptogram (1950): decipherment, 4 October 2026

**Status, stated precisely (revised after Astra's independent review,
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

## Addendum: the pre-registered full-corpus arm (Round 52 key class, multilingual scoring)

Rebuilt Round 52 amendment-1 corpus: 3,847 of 3,848 books (one fetch failure), 14 languages,
K = 400,294,934 hypotheses (variants D and P). Gate **40/40** plants recovered at rank 1,
plant floor -1.081, null ceiling -1.207 (20 nulls). Wood's best decryption here is junk
("OFERANTREFUSAIDAUTIOR", -1.313, below the null ceiling); the literal sum-mod-26 row is junk
too ("ALENRENDRAYCUTREFUGES"). This is the expected negative -- the German Bible is not in that
book list -- and it is qualitative context only: its saved top candidates per row (30 for Wood) are junk, but
the pipeline did not apply the human criterion to every output and it scores signatures poorly,
so it does not certify that no wrong key anywhere produced a comparable reading.
Outputs: `full_gutenberg_ml.json`, `full_gutenberg_ml.out`.
