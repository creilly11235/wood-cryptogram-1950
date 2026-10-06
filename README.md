# T. E. Wood's 1950 cryptogram, solved

In 1950 T. E. Wood published a 21-letter cryptogram in the *Proceedings of the Society for
Psychical Research*. It was a test of survival after death: he would die, then try to send the
key back through a medium. No successful transmission of the key is known, and no earlier published solution has been found.
It is #35 on Klaus Schmeh's list of the Top 50 unsolved encrypted messages.

This repository holds the solution, the code that found it, and the checks. **Klaus Schmeh
confirmed the solution on 4 October 2026; Richard Bean confirmed the reading on 6 October.**
His announcement: ["Wood's cryptogram from the crypt: Another top 50 crypto mystery
solved"](https://klausschmeh.net/woods-cryptogram-from-the-crypt-another-top-50-crypto-mystery-solved/).

| | |
|---|---|
| Ciphertext | `FVAMI NTKFX XWATB OIZVV X` |
| Key passage | The Lord's Prayer in German, 1912 Luther Bible text, from "Unser Vater in dem Himmel" (Matthew 6:9b-11) |
| Method | Robert Thouless's 1948 word-sum system, which Wood said he used |
| Plaintext | `HIERBINICHTOTSIENSTEW` |
| Reading | "Hier bin ich. Totsiens. T.E.W." German for "here I am", Afrikaans for "goodbye", and Wood's initials |

## Check it yourself

```
python3 harness/wood35t/verify_wood.py
```

Python 3.6 or later, standard library only. The script builds the key from the prayer text,
decrypts all 21 letters, re-encrypts them to Wood's exact ciphertext, and shows that near misses
(the modern church wording, keeping repeated words, dropping the off-by-one) give junk.

## The method in brief

Take the key passage word by word, skipping any word already used. Add up each word's letters
(A=1 to Z=26) and keep the remainder after dividing by 26; that number picks a key letter
(1 is A, 25 is Y, 0 is Z). Shift one message letter by that key letter through a Vigenère
square, where A means no shift. Twenty-one distinct words make 21 letters.

For example, UNSER = 21+14+19+5+18 = 77, which leaves 25, so the key letter is Y, a shift of 24.
The first cipher letter F goes back 24 places to H.

## How it was found

Wood's key was constrained to consecutive words in a published book. That made
the search finite: choose a book and a starting word, derive the key, and rank
the resulting plaintext. The first searches ranked everything as English and
found nothing. Taking Wood's multilingual clue seriously changed the scorer;
adding Bible texts supplied the missing key. The full Bible text contained the
Luther wording that the earlier hand-entered church prayer did not.

The ordinary-arithmetic Bible row put the reading first. The alternative
sum-mod-26 row had a nonsense candidate with a slightly higher score, so the
automatic ranking alone did not settle the result. The rules were committed
before the Bible run (`harness/wood35t/PREREG.md`); their failed acceptance bar
remains part of the result.

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

## A slip in Thouless's own example

Thouless's 1948 worked example mis-adds one word. "Suffer" is 75, which gives W, but he printed U,
and his ciphertext follows the mistake: the last letter should be D, not B. See
`research/incoming/wood35_primary/thouless_1948_suffer_slip.png`.

![Thouless 1948, pp. 259-260, with the slip marked](research/incoming/wood35_primary/thouless_1948_suffer_slip.png)

## Running the searches

The standalone verifier needs only Python's standard library. The historical
searches require NumPy and Numba, plus external inputs. The saved multilingual
models let you reproduce the score of a candidate immediately:

```sh
python3 harness/wood35t/verify_wood.py
python3 harness/wood35t/mlseg.py HIERBINICHTOTSIENSTEW
```

`harness/fetch_corpus.py` now exposes the available Gutenberg training-text
recipe; `harness/ngrams.py` builds tables from those files. It does **not** restore
the unmanifested historical English training directory. `harness/build_wordlists.py`
and `harness/fetch_extra.py` expose the available English word-list and held-out
text recipes; their source dumps/catalogue must be supplied. Run those two from
`harness/`; the English search expects its resulting `en_freq.txt` at the separate
root `data/words/` path listed below.

`harness/wood35/fetch_books.py` downloads key books from a supplied Gutenberg
catalogue CSV. For the recorded book-ID list, `harness/wood35t/refetch.py` now
requires a pinned manifest, or an explicit `RECORD=1` first recording run. It
rejects changed hashes and incomplete fetches. This protection is prospective;
it does not recover the original bytes. Use it instead of the historical mirror
helper for a new audited fetch. `harness/wood35t/bible_shards.py` converts locally
downloaded [Bible XML](https://github.com/christos-c/bible-corpus) into shards.
Search working files go in `.cache/wood35/`; run search drivers from the repository
root. There is no claim that the complete historical searches can be rerun
byte-for-byte from this repository alone.

`harness/wood35t/chance_sim.py` additionally needs SciPy. To run
`harness/verify_thouless_b.py`, save Gutenberg book 41215 (Thompson's *The Hound
of Heaven*) as `harness/data/keytexts/41215.txt`.

## Scoring

The recorded runs used **different objectives**. The September book searches were
not English 4-gram searches; `harness/wood35/search.py` sets `ORDER = 5`.
English 4-grams were used for the later hand-entered passage check. The multilingual
book search used pooled 4-grams only to select candidates for word scoring.

| Search | Fast letter score and retention | Final objective |
|---|---|---|
| English-only, 17 September 2026 | Sum of English 5-gram log10 probabilities; retain 5,000 candidates over the original 129 texts, or **50** in the expanded streaming run | `ln(10) × sum5 / 17 + EnglishSeg / 21` for a 21-letter plaintext |
| Targeted passages, 4 October 2026 | English 4-gram check: `sum4 / 18`; a separate multilingual segmentation check | The two checks are reported separately, not added together |
| Multilingual books and Bibles, 4 October 2026 | Sum of pooled seven-language 4-gram log10 probabilities; driver floor −95, retain the best 3,000 per ciphertext across workers | Best complete word segmentation, divided by 21; pooled score breaks final-score ties |

`ngrams.py` counts overlapping A–Z n-grams, including across word boundaries but
not across input files. A seen n-gram gets `log10(count / total_windows)`; an unseen
one gets `log10(0.01 / total_windows)`. Tables are float32. Its method named
`per_char` actually divides by the **number of windows**, `length − n + 1`.
The September final objective mixes a natural-log letter term and a log10 word
term; it should not be described as a pure log10-per-character score.

EnglishSeg is a dynamic program over dictionary words of at most 12 letters,
using up to 60,000 distinct entries from `data/words/en_freq.txt` at the repository
root. A word on zero-based source line `r` weighs `−log10(r + 1) − 0.5`;
an unmatched letter costs −4.0. This path differs from the multilingual English list.

The multilingual program (`mlseg.py`) maximizes
`[Σ log10 p_language(word) − 1.0 × words − 0.5 × language_changes] / length`.
It chooses word boundaries and languages jointly: a locally best language need not
win after the switch penalty. Words may have 1–18 letters; the only permitted
single-letter words are A, I, O, Y, E and U. No complete dictionary split means
−99. There is no unknown-word or initials model (the declared `FLOOR` is unused).
Non-English lexicons retain words seen at least twice **or** at least five letters
long, with probabilities normalized by all source tokens before that cut-off.
The English list instead supplies rank weights `max(1, 100000 // (r + 10))`.

`pooled.py` takes up to 350,000 normalized letters per language. It removes the
first 5% of each source file by character count, concatenates the remaining text
within each language, then applies that cap. It does not balance the languages by
word count. Lexicon building uses text from the first `***` marker onward, so
Gutenberg boilerplate after that marker is retained. Key tokenization is NFKD,
combining marks removed, uppercase A–Z runs; the German letter model's umlaut
expansion differs from the key tokenizer's accent folding. The code records these
choices, not a linguistically clean training corpus.

**Why these orders?** Four was the shared scorer's default, not the outcome of a
controlled comparison; the builder supports 3/4/5, while the September engine
explicitly chose five. No saved ablation establishes an optimal order for Wood.
Lasry's *A Methodology for the Cryptanalysis of Classical Ciphers with Search
Metaheuristics* (2018), §3.2.3, warns that higher n is “more selective” but “less
resilient to key errors”. Here the search enumerates exact book/offset keys; it
does not need a smooth score to improve a partially correct key by hill climbing.
That changes the trade-off, but does not make wrong offsets independent or
eliminate spelling errors and corpus mismatch. The recovery controls test the
whole pipeline, including losses from its prefilter, rather than justify n in isolation.

The multilingual controls used 40 synthetic 21-letter plants assembled from the
top 4,000 words per language (2–4 chosen languages, words at least two letters),
and 20 independent uniform A–Z ciphertexts, seed 20261004. They were not samples
of natural mixed-language sentences. The Bible run recovered 40/40 plants. Wood
scored −1.270257, above the null maximum −1.273171 but below the registered plant
floor −1.081264. The scorer split the ending as `TOT/de SIEN/fr STEW/en` because
it had neither Afrikaans nor a signature model. Recognizing TOTSIENS and TEW was
manual, after the hit; the automatic acceptance rule was not retroactively passed.

## Input data

Inventory checked against code and saved artifacts on **6 October 2026**. “Unknown”
means the historical input was not retained or manifested; it is not a size estimate.
The table separates key texts, language-model inputs and controls. Book languages
describe catalogue labels, not a fresh language validation of every text.

| Corpus or lexicon | Source and selection rule | Recorded size | Exclusions / preprocessing | Hash or manifest status |
|---|---|---|---|---|
| English letter-model training | `harness/data/corpus/en/`, every file read by `ngrams.py`. The available `fetch_corpus.py` recipe names Gutenberg IDs 2701, 1342, 84, 98, 1661, 345, 1400, 2600, 76, 1232, 5200, 174, 43, 120, 35, 36, 2554, 1952, 30254, 4300 | Recipe: 20 seed books; actual historical file count, bytes and normalized-letter total unknown | Fetch recipe strips Gutenberg headers/footers; model keeps normalized A–Z only | No historical training manifest or saved English tables. These seeds do **not** prove the full historical directory contents. Wikipedia membership is unverified |
| English segmentation list | `data/words/en_freq.txt`; available `build_wordlists.py` recipe ranks words from the English Tatoeba sentence dump | At most 60,000 distinct words accepted, length ≤12; historical accepted count and dump size unknown | Alphabetic entries, uppercase, duplicates skipped; rank-based weights | Neither the historical list nor dump hash is retained with this run; recipe alone cannot reproduce its exact ranks |
| English held-out plant texts | `harness/data/corpus_extra/en/`; `fetch_extra.py` specifies 10 seed IDs plus the first 110 catalogue English fiction texts below ID 3000, excluding existing seeds | 100 plants in the first run; 40 in the expansion; historical corpus bytes unknown | Exclude basenames present in training directory; sample 21 letters at a word boundary. Non-English quotations and names remain possible | Plant text, source filename and offset saved in gate outputs; no complete source-byte manifest |
| Original book-key collection | Existing Gutenberg directories da/de/es/fr/it/la/nl/sv and en, plus the 1773 Dutch psalter | 129 file entries: 81 non-English (7,414,993 tokens) and 48 English (6,889,227); 28,602,798 valid D/P starts | All files in the selected directories; D skips repeated word identities, P keeps repeats | Aggregate counts and candidate sources retained; no complete committed source inventory/hash manifest |
| Secondary sentence-key collection | Tatoeba dumps labelled bel/ces/est/fin/lat/lit/pol/rulat/ukr; separate from published-book keys | 9 files, 11,066,448 tokens; 22,132,525 D/P starts | A–Z tokenization; concatenated sentence order is an artifact of the dump | Result retained; dump versions/hashes not retained |
| Expanded Gutenberg keys, September | Catalogue `Type=Text`, single language fr/de/it/es/nl/la/pt/da/sv/ca/eo/fi/hu/pl; ascending ID, round-robin languages, 200-million-token stopping budget | 3,848 successful books, 200,184,725 tokens; joined to the original collection: 3,977 file entries, 428,787,544 valid D/P starts | Failed downloads / <21 tokens skipped; raw download headers and footers retained. 69 entries duplicated original books, as recorded in the result | Successful IDs/token counts in `harness/wood35/fetch.jsonl`; raw texts deleted, shards not retained. Log hash is **not** a source-byte manifest |
| Gutenberg rebuild for multilingual scoring, October | Successful-ID list from the September fetch log, same tokenizer | **3,847 books actually scored**, 200,147,467 tokens; K=400,294,934 | One of the 3,848 listed books failed to refetch; its identity is not identified in the saved result. Original 129-text tier not separately re-added | No committed hash manifest; original shards not kept, so exact scored bytes cannot now be reconstructed. `refetch.py` pins hashes only from the next recording run |
| Hand-entered key passages | Four committed files in `harness/wood35t/passages/`: classical poetry/prose, prayers and liturgy, selected from memory | Current snapshot: 173 labelled blocks (65 Latin, 48 French, 31 German, 29 other), 42,059 bytes | Labels excluded by parser; starts needing more words than the block supplies cannot yield a key | Text bytes committed. Original result says “about 140”; no frozen run-input manifest establishes which snapshot that estimate covered |
| Pooled letter model | `pooled.py`: en `moore_en` plus PG 1342/84; fr PG 27625/36011; de 2229/2407/6079; la 227; it 1000; es 2000; pt 3333 | Cap 350,000 letters/language (at most 2,450,000); actual historical totals unknown. Saved table: 456,976 float32 entries, 1,828,032 file bytes | First 5% of each text removed; normalization and within-language cap as above | Exact `pooled_4.npy` committed and hashed below. Raw training bytes and provenance of `moore_en` not recorded |
| French segmentation lexicon | PG 27625, 36011, 39739, 15790, the four fixed sources in `mlseg.py` | **20,703 word types** | First `***` onward; folded A–Z; count≥2 or length≥5 | Exact derived lexicon committed in `mlseg_lex.pkl`; source byte hashes/totals absent |
| Latin segmentation lexicon | PG 227, fixed source | **16,951 word types** | Same lexicon cut-off | Same saved lexicon; source byte hash/total absent |
| Italian segmentation lexicon | PG 1000, fixed source | **12,848 word types** | Same lexicon cut-off | Same saved lexicon; source byte hash/total absent |
| Spanish segmentation lexicon | PG 2000, 5201, fixed sources | **26,632 word types** | Same lexicon cut-off | Same saved lexicon; source byte hashes/totals absent |
| Portuguese segmentation lexicon | PG 3333, fixed source | **9,163 word types** | Same lexicon cut-off | Same saved lexicon; source byte hash/total absent |
| German segmentation lexicon | PG 2229, 2407, 6079, fixed sources | **10,933 word types** | Same lexicon cut-off; accents folded, ß→SS | Same saved lexicon; source byte hashes/totals absent |
| English multilingual lexicon | `harness/data/words/en_common.txt`, 40,000 entries in source order; upstream origin not recorded | Source list 342,327 bytes; **40,000 derived word types** | Rank weights above, first whitespace-delimited field, folded A–Z | Exact derived lexicon committed. Retained source-list SHA-256 recorded below; upstream provenance unresolved |
| Bible key tier | Latin-script XML texts downloaded from `christos-c/bible-corpus`, chosen because Wood specified an accessible foreign-language book | 19 shards, 13,365,009 tokens; K=26,730,018 per arithmetic convention | `bible_shards.py` extracts `<seg>` contents, unescapes entities, excludes Greek/Hebrew files, applies key tokenizer | No complete historical 19-file hash manifest. Winning German XML hash is recorded below; XML/shards not bundled |
| Multilingual control vocabulary | Derived from the seven saved segmentation lexicons | First 4,000 entries per language before length filtering; 40 plants and 20 nulls per full run | Words ≥2 letters; reject concatenations not exactly 21 letters | Seeds and generated controls retained in `bib_ml.json` and `full_gutenberg_ml.json` |
| Post-hoc signature-test lexicons | Top 20,000 entries per saved lexicon plus top 20,000 tokens each from Dutch and Afrikaans Bible XML | Nine-language union; historical final union size not recorded in the run output | Words 3–10 letters. Full-18 detector adds TOTSIENS **after** the solve; 500 control signatures | Code and results retained; Dutch/Afrikaans XML hashes absent. Separate from the seven-language search score and from Astra's analytical bound |

The October K values are the driver's `2 × token_count` bookkeeping counts for
D and P, including unusable terminal starts, not a count of independent trials.
The September engine counts valid starts. The two conventions must not be silently
equated. The retained candidate lists also do not amount to a human review of every key.

The English download recipe available now names Gutenberg books, not Wikipedia
articles. A separate Wikipedia fetcher in the working repository writes to
`data/wiki_crypto/`, which `ngrams.py` does not read. No retained manifest or copy
step supports assigning any particular Wikipedia articles or byte count to the
Wood model. The claim that its historical training input was a known
Gutenberg-and-Wikipedia corpus is therefore **not verified**.

Exact retained-input SHA-256 values (these pin artifacts, not missing upstream corpora):

```text
c0b24e6f368316af468dd42b44383904467710721e21f7e1a0dd20279d1ca262  mlseg_lex.pkl
615ee533663b2b472383ca0d4e3e6685f9c1f36168f5e975d99a133ef0dd8a39  pooled_4.npy
a6f3be41fd3e5b2c515ac9c5113e630fa421346c8f4f0b84affe900a72bdc54f  en_common.txt (retained in the working repository)
1e28e58cf7a6e17f58f575f84a9720ff3bc64dce7cc667e10c40d577e75a68ab  fetch.jsonl
49be6f5e464ff94982c8ca58a9ff3afafbcea14eccdaf41b88c02f53792952a3  German.xml (recorded at discovery)
```

## Open questions

- What connected Wood to Afrikaans? The reading supplies the question; the
  sources reviewed so far do not answer it.
- Which physical Bible edition did he use? The wording alone cannot identify a copy.
- What does the Society for Psychical Research's Wood file at Cambridge
  University Library establish? Schmeh has offered photographs; their retrieval
  and review are pending, and they are not evidence for additional claims here.
- The Berger / Survival Research Foundation cryptograms are a **separate story**,
  raised by Schmeh's post. The Berger chapter located so far adds no Wood evidence.

## Reading and method lineage

- Richard Bean, [*The use of Project Gutenberg and hexagram statistics to help
  solve famous unsolved ciphers*](https://richardbean.id.au/papers/HistoCrypt2020_paper_18.pdf),
  HistoCrypt 2020, pp. 31–35: the book-search approach that recovered Thouless's
  Message B, and explicit language-model input data.
- Richard Bean and Louie Helm, [*New records for Playfair solutions*](https://richardbean.id.au/papers/playfair_histocrypt2025.pdf),
  HistoCrypt 2025, pp. 12–17: letter and word scoring, vocabulary cut-offs and
  the difficulty of ranking short readable candidates. These are methodological
  predecessors, not claims that Wood used their models or datasets.
- George Lasry, *A Methodology for the Cryptanalysis of Classical Ciphers with
  Search Metaheuristics* (2018), §3.2.3: selectivity versus resilience to key errors.

## About this repository

These files were extracted, with their commit history, from a larger working repository.
Commit dates are the originals and messages are lightly edited; commit IDs are new. A few
documents mention files from that repository that are not included here.

## Credits

The project was run by Colin Reilly. Robert Thouless designed the method, and Richard Bean's 2019 solution of Thouless's own
Message B showed exactly how it works. Klaus Schmeh kept the puzzle in view and confirmed the
answer; Bean confirmed the reading on 6 October 2026 and supplied the input-data and scoring critique addressed here. Claude (Anthropic) wrote the search code and found the key; GPT-6 Astra (OpenAI)
reviewed it independently.

## License

The code is under the MIT License (see `LICENSE`). The quotations and page images from the 1948
and 1950 *Proceedings of the Society for Psychical Research* are short extracts included for
commentary, and are not covered by that license. Nor are the third-party texts and data: the
key-text passages in `harness/wood35t/passages/`, the word lists behind `mlseg_lex.pkl` and
`pooled_4.npy`, and the Bible and Gutenberg texts the searches download.
