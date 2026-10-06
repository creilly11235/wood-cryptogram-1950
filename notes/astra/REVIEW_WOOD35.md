> Editorial note, 6 October 2026: internal session labels and artifact paths have been made descriptive. The review findings and numerical evidence are unchanged. Checksums of documents below refer to the versions reviewed on 4 October, before these editorial changes.

# CONFIRMED WITH RESERVATIONS

**Independent review of T. E. Wood’s cryptogram, 4 October 2026.**

The claimed 21-letter decryption is correct. It uses the repository’s verified Thouless B convention without a Wood-specific arithmetic or tokenisation exception. The matching prayer exists independently of this repository, and the complete reading **“Hier bin ich — Totsiens — T. E. W.”** is coherent and unusually persuasive. I regard it as a strong, likely intended solution.

The reservations concern what this establishes: **the preregistered acceptance rule failed; the report’s chance estimate is not a calibrated significance level; the physical key edition and first-ever-solve claim are not established.** “Confirmed” here means that the proposed decipherment and its substantive linguistic interpretation survive independent checking, not that those additional claims have been certified.

I ran no git commands, did not import or read `harness/wood35t/verify_wood.py`, and did not modify existing files. I created one independent verifier in `/tmp` and this review. I did not repeat the large corpus searches. All Python commands used `-B` to suppress bytecode writes. Terminal network access was denied; the separate web tool returned useful indexed text, although several direct page/PDF fetches failed.

The report acquired a full-corpus addendum during this review. Both versions and the new saved results are covered below; their hashes are recorded in the evidence appendix.

## 1. Independent decryption and all-letter re-encryption

**Confirmed, 21/21 letters.** My fresh standard-library code starts from the ciphertext and the supplied natural-language prayer, extracts words itself, and only checks the claimed answer after computing the plaintext. It does not start from the report’s key-word or shift arrays.

The exact command and complete output are:

```console
$ python -B /tmp/wood35_independent_review.py
ciphertext: FVAMINTKFXXWATBOIZVVX length: 21
 i word       sum shift ct pt rec
 1 UNSER       77    24  F  H  F
 2 VATER       66    13  V  I  V
 3 IN          23    22  A  E  A
 4 DEM         22    21  M  R  M
 5 HIMMEL      60     7  I  B  I
 6 DEIN        32     5  N  I  N
 7 NAME        33     6  T  N  T
 8 WERDE       55     2  K  I  K
 9 GEHEILIGT   82     3  F  C  F
10 REICH       43    16  X  H  X
11 KOMME       57     4  X  T  X
12 WILLE       61     8  W  O  W
13 GESCHEHE    60     7  A  T  A
14 AUF         28     1  T  S  T
15 ERDEN       46    19  B  I  B
16 WIE         37    10  O  E  O
17 IM          22    21  I  N  I
18 TAGLICH     60     7  Z  S  Z
19 BROT        55     2  V  T  V
20 GIB         18    17  V  E  V
21 UNS         54     1  X  W  X
skipped occurrences: DEIN DEIN HIMMEL UNSER
plaintext: HIERBINICHTOTSIENSTEW length: 21
reencryption: FVAMINTKFXXWATBOIZVVX
roundtrip: True
no dedup: HIERBINICSHSVLUNPPAOZ
ae transliteration: HIERBINICHTOTSIENNTEW
delete umlaut letter: HIERBINICHTOTSIENTTEW
sum without minus one: GHDQAHMHBGSNSRHDMRSDV
reverse direction: DIWHPSZMINBEHUUYDGXMY
1912 verse start words: DARUM SOLLT IHR ALSO BETEN UNSER VATER IN DEM HIMMEL DEIN NAME WERDE GEHEILIGT REICH KOMME WILLE GESCHEHE AUF ERDEN WIE
1912 verse start plaintext: BWSSPPGOKQSQYQLKASUCN
1984 prayer start words: UNSER VATER IM HIMMEL DEIN NAME WERDE GEHEILIGT REICH KOMME WILLE GESCHEHE WIE SO AUF ERDEN TAGLICHES BROT GIB UNS HEUTE
1984 prayer start plaintext: HIFFDHRHPTPPQMAVDXEUR
```

The first 21 distinct words consume **25 word occurrences**, ending at **uns**; `heute` is not used. There are **four** skipped occurrences: the second and third `DEIN`, the second `HIMMEL`, and the second `UNSER`. Thus “three repeated words” is correct only as a count of distinct word types, not of skipped occurrences.

The full verifier source is preserved in Appendix A. No ciphertext edit, invented key word, rearrangement, or approximate character match is needed.

Re-encryption is an essential transcription/arithmetic check, but not independent statistical evidence: any invertible key decrypts and re-encrypts its resulting plaintext. The evidence for this particular key is the externally existing passage and the coherent resulting message.

## 2. Comparison with Thouless Message B

**The convention matches.** I read `harness/verify_thouless_b.py` and `attempts/thouless_b_crack.md`, then ran:

```console
$ python -B harness/verify_thouless_b.py
```

It exited 0 and returned the expected 74-letter message, with `"reencryption_matches": true`. The complete stdout is in Appendix B.

Both decryptions:

- Start the distinct-word set afresh at the chosen passage offset; they do not deduplicate the entire book first.
- Skip every subsequent occurrence of an already selected normalized word, including nonadjacent repeats.
- Fold diacritics before collecting A–Z words. Wood needs `täglich → TAGLICH`; the Thouless verifier already folds `chasmèd` and `unperturbèd`.
- Sum letters with A=1 through Z=26, use `(sum - 1) % 26`, and subtract that zero-based shift from the ciphertext.
- Deduplicate **word identities**, not sums: `DEM` and `IM` both sum to 22 and both remain.

My independent code uses NFD for accent decomposition; the repository uses NFKD. They give the same tokens for every character in this passage. No compatibility-character exception is involved. A German transliteration using `AE` is a plausible alternative convention, but it is not the one already used by the repository.

The controls above show precisely what changes. In particular, changing only the umlaut treatment changes only position 18. The report should avoid suggesting that every nearby convention produces wholly unrelated gibberish.

## 3. Key wording, sources, and edition dependence

**The supplied wording is externally supported, with retrieval limits.**

The web search tool returned the full relevant verse text from [Bibel-Online’s Luther 1912 Matthew 6](https://www.bibel-online.net/text/luther_1912/matthaeus/6/) and from [BibleGateway’s displayed LUTH1545 Matthew 6:9–13](https://www.biblegateway.com/passage/?search=Matthaeus+6%3A9-13&version=LUTH1545%3BSCH2000). Both match the report’s key passage. These were indexed extracts: direct opening of Bibel-Online returned 403 and direct BibleGateway fetches failed. I did not inspect a scanned 1912 printed volume.

The crucial start is **Matthew 6:9b, at the sixth word of verse 9**, after its five-word introduction. It is the beginning of the prayer, a natural passage boundary, but **not a verse start**. The first control in task 1 demonstrates that beginning at the verse’s first word fails.

| Text witness | Relevant differences | Effect |
|---|---|---|
| Luther 1912 as displayed by Bibel-Online | Matches the supplied passage | Produces the claimed plaintext |
| BibleGateway’s modern-spelling text labelled LUTH1545 | Same relevant word stream as that 1912 copy | Produces the same plaintext; does not identify a unique edition |
| Historical-spelling 1545 transcription | Forms including `Himel`, `geheiliget`, `kome`, `auff`, `teglich`, and historical u/v spellings | Several sums change; does not yield the claimed plaintext without further modernization |
| Luther 1984 | `im` replaces `in dem`; the heaven/earth clause is reordered and adds `so`; `tägliches` replaces `täglich` | Changes both word alignment and sums; fails |

For the historical spellings I consulted [Stilkunst’s transcription of Matthew 6 in the 1545 Bible](https://www.stilkunst.de/lutherbibel-1545/Mt/mt-06.php). Its decorative letter spacing should not be mistaken for original word boundaries. My control normalizes that spacing and long-s typography, then preserves the lexical spelling differences. For 1984, the differences were checked against [the explicitly labelled verse comparison](https://www.sermon-online.com/contents/40006009) and [a quotation explicitly attributed to Luther 1984](https://www.allaboutgod.com/german/wenn-christen-beten.htm).

Additional control output, obtained by the command reproduced in Appendix D:

```text
only taeglich: HIERBINICHTOTSIENNTEW
changed positions: [(18, 'TAGLICH', 'TAEGLICH')]
only taegliches folded: HIERBINICHTOTSIENUTEW
changed positions: [(18, 'TAGLICH', 'TAGLICHES')]
1545 lexical spelling, u/v modernized: HIEROINIXHGOTMIENOTEW
changed positions: [(5, 'HIMMEL', 'HIMEL'), (9, 'GEHEILIGT', 'GEHEILIGET'), (11, 'KOMME', 'KOME'), (14, 'AUF', 'AUFF'), (18, 'TAGLICH', 'TEGLICH')]
1545 lexical spelling, original v: GIEROINIXHGOTMIENOTEV
changed positions: [(1, 'UNSER', 'VNSER'), (5, 'HIMMEL', 'HIMEL'), (9, 'GEHEILIGT', 'GEHEILIGET'), (11, 'KOMME', 'KOME'), (14, 'AUF', 'AUFF'), (18, 'TAGLICH', 'TEGLICH'), (21, 'UNS', 'VNS')]
```

The label “only taegliches folded” in my diagnostic means the literal substitution `täglich → tägliches` followed by accent folding; the resulting key word is `TAGLICHES`.

The 1984 edition postdates the 1950 cryptogram and cannot have been Wood’s source. Its failure is a useful edition-sensitivity demonstration, not evidence against the pre-1950 wording.

**Unverified provenance:** the web tool rejected the corpus’s raw `German.xml` as too large; terminal downloads were prohibited. I therefore could not independently confirm its complete SHA-256, the zero-based corpus offset 533250, or its edition metadata. The report prints only a truncated digest. Matching the passage establishes a viable key text, not that Wood necessarily owned a particular 1912 Bible rather than another edition or book quoting the same prayer.

## 4. Linguistic reading and Wood’s statements

**The complete reading works naturally.**

- **Hier bin ich** is idiomatic German: “Here I am” or “Here am I.” Its word order is correct.
- **Totsiens**, also written **tot siens**, is an Afrikaans farewell. “Until we meet again” is a particularly apt rendering here; “goodbye” is also right. The [Dictionary of South African English](https://dsae.co.za/entry/totsiens/e07270) documents the expression and examples from 1937 and 1944, so it is not an anachronistic interpretation.
- **T. E. W.** exactly matches the author’s published initials. A terminal signature is a normal reading, though its punctuation and status as a signature are inferred.

Initials are **not a third language**. The report’s “German, Afrikaans, and English initials” should not be presented as three-language evidence. However, this does not create a historical contradiction. Indexed text of [Wood’s original paper, Proceedings of the SPR 49, pp. 105–106](https://iapsop.com/archive/materials/spr_proceedings/spr_proceedings_v49_1949-52.pdf) says:

> The message, if and when deciphered, will not be in any one language.

Two languages satisfy that wording. The same indexed paper independently supplies the ciphertext and the rule of omitting repeated words, and explains that using foreign languages was intended to frustrate English-word attacks. The [SPR’s own bibliography](https://www.spr.ac.uk/11-survival-theories-and-speculations) confirms the paper’s author, title, volume and pages. Direct PDF retrieval failed; I relied on the indexed passage, not a visual inspection of the printed page.

A German Bible satisfies the non-English-book clue. That clue does not require the underlying biblical works to have been composed originally in German. A greeting, farewell and signature fit a survival-test message, although this thematic judgment is not independent proof.

I found no equally good complete alternative reading. One can read the prefix as “Hier bin ich tot” (“Here I am dead”), but that leaves `SIENSTEW` unexplained. The automatic split `HIER/de BIN/de ICH/de TOT/de SIEN/fr STEW/en` is a list of dictionary matches, not a coherent competing sentence. Dutch would normally have `tot ziens`, so Afrikaans is the more exact attribution.

I did not establish that Wood knew Afrikaans or possessed a German Bible. Those would be useful independent biographical checks. Their absence does not make this short multilingual message linguistically defective.

## 5. Significance, selection effects, and my chance calculations

### What the saved experiment actually establishes

The saved Bible results report:

| Quantity | Value |
|---|---:|
| Book/offset/dedup hypotheses, one arithmetic convention | 26,730,018 |
| Bible shards | 19 |
| Plants recovered | 40/40 |
| Claimed candidate’s final score | -1.270257200624433 |
| Best of 20 null final scores | -1.2731706558566063 |
| Plant floor | -1.0812636268194866 |
| Margin above null ceiling | 0.0029134552321732343 |
| Margin below plant floor | 0.1889935738049464 |

The candidate is below **every** planted plaintext’s score, not merely below the fifth-percentile threshold. The exact extraction command and all 20 null winners appear in Appendix C.

The preregistration says **“Bar for Wood (all required)”** and **“Anything less is reported as a lead.”** Passing (c) and (d) cannot satisfy that rule after failing (b). Missing Afrikaans and a signature model is a credible explanation for the score shortfall, but it is a **post-hoc explanation**, not a successful preregistered test. A human may reasonably find the decipherment compelling despite that failure; the report must describe that as a separate evidentiary judgment.

Also, the alternative arithmetic row `WOODm1` scores **-1.2640577391435683**, higher than the claimed plaintext, while yielding `ALENRENDRAYCUTREFUGES`. Thus the claimed plaintext wins the ordinary-arithmetic row; it does **not** win the final segmentation score across both arithmetic conventions. This is an instructive false positive of the automatic scoring rule.

Twenty nulls cannot support a tiny empirical tail probability. For a single fixed score/search procedure, zero exceedances gives the usual add-one rank value **1/21 = 0.047619**, and the exact one-sided 95% upper confidence bound on its exceedance probability is **0.139108**. These are calibration limits, not posterior probabilities that the candidate is wrong. Testing both arithmetic conventions and choosing additional human criteria adds selection that those 20 nulls do not calibrate.

The JSON saves 30 Wood candidates and only the final-score winner for each null. A null’s saved pooled score is **not necessarily its best pooled score**. Consequently, the available artifacts do not independently substantiate “better than every null’s best” under the pooled prefilter. Nor do 30 retained Wood rows prove the pooled ranking over every candidate. The observed candidate’s own pooled score, -80.14478540420532, is recorded.

### Audit of the report’s numerical argument

The arithmetic of the stated narrow model is right:

```text
(1 / 2,000,000) × (1 / 26^3) = approximately 2.845e-11 per hypothesis
26,730,018 × that probability = 0.0007604124374146564 expected hits
```

Its interpretation needs these corrections:

1. **Wrong-key outputs are not automatically independent uniform strings.** Bible word sums have biases, adjacent windows overlap, translations repeat passages, and D/P variants often coincide. Under a uniform-random-ciphertext null, each fixed key does yield a uniform plaintext; that is a clean model, but it must be stated.
2. **The search was not one a-priori key.** Choosing the Lord’s Prayer beforehand would justify a different experiment. Recognizing its naturalness after searching millions of positions cannot retroactively replace the trial count with one.
3. **The verse-start calculation does not describe this search or even include this exact starting position.** The successful start is inside verse 9.
4. **There were two arithmetic conventions.** The script counts D/P variants in K, then also searches `WOODm1`. The Bible tier therefore considers approximately **53,460,036** plaintext hypotheses. K itself is a bookkeeping count of twice token length, including a few unusable end positions, rather than an exact count of distinct valid keys.
5. **The ten-letter German prefix, three-letter terminal signature, minimum word length and their placement were not the preregistered acceptance test.** They are a plausible retrospective template, not a calibrated general meaning detector. The author’s initials were known beforehand, which makes them much stronger than arbitrary initials, but the choice to use them as the decisive criterion was still retrospective.
6. **Ignoring the middle eight letters is conservative within that fixed template.** It does not fix the template-selection problem. Conversely, multiplying by `26^-8` for the exact observed word `TOTSIENS` would be unjustified unless that word had been specified beforehand; other meaningful farewells and utterances would also have been welcomed.
7. **The reported simulation is not reproducible from the cited materials.** I found no accompanying simulation code, exact lexicon, trial count, seed, number of hits or uncertainty interval in the reviewed Wood directories. “One in two million” is insufficient reporting, particularly if it came from very few successes.

### My own small-computation estimate

I used exact combinatorial bounds rather than a large simulation. Let a fixed acceptable set contain M strings of 21 letters. Under a uniform-ciphertext null, for N tested keys:

```text
expected accepted decryptions = N M / 26^21
Pr(at least one accepted decryption) <= min(1, N M / 26^21)
```

The upper bound needs **no independence between keys**. For a fixed actual historical ciphertext, it is a model-based estimate, not a distribution-free guarantee about the author’s intention.

Here is a deliberately permissive, reproducible surrogate for meaningfulness: any 18-letter sequence of dictionary words of length at least three, followed by the **specific** signature `TEW`. I pooled the top 20,000 entries per language from the saved seven-language lexicon, deduplicated their spellings, and added `TOTSIENS` explicitly because Afrikaans is absent. This has 93,188 eligible words. It admits the observed reading and large amounts of incoherent word salad; it does not insist on German, a 10+8 split, grammar, or religious content.

For counts c[k] of words of length k, compute:

```text
D[0] = 1
D[n] = sum(c[k] * D[n-k], k = 3..n)
```

D[n] counts segmentation derivations, so it **upper-bounds** distinct strings. I obtain:

| Explicit acceptance model | Expected-hit / union-probability upper bound, N=26,730,018 |
|---|---:|
| German dictionary words filling 10 letters; any eight letters; exact terminal TEW | 5.47838e-4 |
| German dictionary words filling 10 letters; pooled dictionary words filling eight; terminal TEW | 9.80602e-8 |
| Pooled dictionary words filling 18 letters, all words at least three letters; terminal TEW | **1.99649e-4** |
| Same 18-letter model but permit two-letter words | **0.319850** |
| Same, also permit six ordinary one-letter forms | Bound is **1**, hence uninformative |

The first model’s German dictionary has only 10,933 entries before filtering, so it does not reproduce the report’s unspecified 20,000-word source. Its ten-letter segmentability probability lies between **1.10640e-7 and 3.60224e-7**; the report’s 5e-7 is plausible in scale, not verified.

For the broad **three-letter-minimum** signed-message model, doubling for the two arithmetic conventions gives **3.99297e-4**. Also allowing the exact signature at any of 19 contiguous positions gives the loose bound **0.00758665**. These are conditional bounds for explicit word-list classes, **not an estimated probability that Wood’s solution is false**. Including short words greatly enlarges those classes; allowing arbitrary initials would remove the identifying evidence. The higher bounds do not show that equally coherent false solutions actually occur at those rates.

As a sensitivity calculation, an acceptable set of 10^18 distinct 21-letter messages would give a union bound of **5.15892e-5** over N keys; 10^20 messages gives **0.00515892**. We do not know how many strings a human, allowed arbitrary languages, abbreviations and interpretations, would call “at least this meaningful.”

**My quantitative conclusion:** under a constrained, exact-signature and longer-word model, this is a rare chance hit even across the Bible search, with an upper bound of about **4e-4** including both arithmetic conventions. There is **no defensible single calibrated probability for unrestricted human meaningfulness** in the available evidence. The lexical calculations and the empirical score test answer different questions. I would not turn either into a “99.9% solved” claim. The exact source passage, clean reading and specific signature together are more persuasive than the automatic score alone.

The full exact calculation commands and stdout are in Appendices C–D; each took well under a second of wall time as reported by the execution tool.

### Addendum that appeared during review

The added Gutenberg results are internally consistent with their log: K=400,294,934; 3,847 shards; 40/40 plants; null ceiling -1.2068555307731; ordinary-arithmetic winner `OFERANTREFUSAIDAUTIOR`, score -1.3125684883681035. The alternate-arithmetic winner is again `ALENRENDRAYCUTREFUGES`. I read these outputs; I did not regenerate them.

This is useful qualitative context, but the claim that **no wrong key anywhere** resembled a German phrase plus initials is not established by saving 30 score-ranked candidates per row. The pipeline did not test that human criterion on every output, and it demonstrably scores signatures poorly.

If the two reported corpus arms are included in the exploratory search family, the bookkeeping total across both arithmetic conventions is **854,049,904** hypotheses, before accounting for earlier experiments and before collapsing duplicate keys. Using that conservative union count, my three-letter-minimum signed-message bound becomes **0.00637897**. This does not cancel the candidate’s plausibility; it prevents portraying all exploration as a single preselected prayer or a Bible-only experiment.

## 6. Coincidence, fabrication, and prior solutions

I found **no positive evidence of fabrication**. The strongest checks against it are independent agreement on the ciphertext and the prayer wording, and exact recovery using an already established convention. None of the 21 letters requires repair. The terminal initials and ordinary farewell provide substantially more structure than a vaguely suggestive prefix.

There are nevertheless limits:

- A 21-letter word-sum cipher cannot uniquely identify a physical book: different words and passages can collide modulo 26.
- Reproducing the answer does not authenticate the claimed discovery chronology, blindness, corpus completeness or every logged score.
- I did not obtain the raw Bible corpus, a facsimile of Wood’s article, private correspondence, an author-deposited key, or evidence of Wood’s particular language knowledge.
- The working-tree preregistration has an assertion about its timing, not independently immutable proof of that timing. I did not use git, as instructed.
- The report changed while I was reviewing it. The change observed was an added full-corpus section, not a change to the key or plaintext. That is a scope/provenance observation, not evidence of dishonesty.

**Priority is unconfirmed.** Exact web searches for `"HIERBINICHTOTSIENSTEW"` and `"Hier bin ich" "Totsiens" "Wood"` each returned **“Empty search results / No results were found for the provided queries.”** Ciphertext searches returned the historical puzzle and primary publication. Indexed [Schmeh coverage of Bean’s 2019 solution](https://scienceblogs.de/klausis-krypto-kolumne/2019/08/16/richard-bean-solves-another-top-50-crypto-mystery/) distinguishes solved Thouless B from unsolved Wood; [his later cold-case article](https://scienceblogs.de/klausis-krypto-kolumne/cryptographic-cold-cases-from-parapsychology/) also describes Wood as open.

Searches of Schmeh’s newer site and the indexed [Bourdeau working notes](https://dbourdeau.github.io/cyphersolver/index.html) produced no matching T. E. Wood decipherment. Results mentioning John Wood concern other historical ciphers. However, direct blog fetches and comment retrieval failed, and I did not independently reproduce the report’s complete claimed novelty audit. Search-engine absence, or an old article still saying “unsolved,” cannot establish world priority as of 4 October 2026.

## Corrections the report needs

1. **Separate the conclusions:** exact decipherment independently reproduced; intended reading highly plausible; first publication/priority unverified. Do not claim that this review proves a first-ever solve.
2. **State that the full preregistered acceptance rule failed.** Under that rule the result remains a lead; a stronger human conclusion must be labelled a separate post-hoc assessment.
3. **Replace the advertised chance level with explicitly conditional calculations.** Include both arithmetic conventions, broader search history, the lack of calibration for human acceptance, and simulation reproducibility details.
4. **Report the higher-scoring `WOODm1` candidate**, and qualify the pooled-null ranking claim unless the actual per-null pooled maxima can be supplied.
5. **Change “three repeated words are skipped” to “four repeated occurrences of three distinct words are skipped.”**
6. **Describe two plaintext languages plus a signature.** Do not count initials as English-language content. Quote Wood’s actual multilingual condition with a source and retrieval limitation.
7. **Identify the start as Matthew 6:9b**, not a verse start. Identify Luther 1912 as a matching wording, not a uniquely established physical edition. Distinguish BibleGateway’s modern spelling under its 1545 label from historical 1545 spelling.
8. **Supply a complete corpus digest, immutable source reference and offset reproduction.** These are not replaced by a truncated digest or the prayer quotation.
9. **Qualify the new Gutenberg control:** its retained candidates look unconvincing; it does not certify a human review of every rejected output.
10. **Temper “each deviation destroys the reading” and “the most natural possible choice.”** Small spelling changes can affect one letter, and a familiar prayer is a strong prior candidate without being the only natural one.

A defensible short description is: **“A likely decipherment of Wood’s cryptogram, independently reproduced with the established Thouless convention and an externally attested Luther-prayer wording; statistical calibration and publication priority remain unresolved.”**

## Appendix A. Fresh verifier source

Created exclusively as a new file at `/tmp/wood35_independent_review.py`, using `Path.open('x')`. This is the actual source executed above:

```python
"""Independent Wood audit. Standard library only; no repository code imports."""
import re
import unicodedata
import json
import math
from pathlib import Path

CIPHER = "FVAMI NTKFX XWATB OIZVV X".replace(" ", "")
PASSAGE = ("Unser Vater in dem Himmel! Dein Name werde geheiligt. "
           "Dein Reich komme. Dein Wille geschehe auf Erden wie im Himmel. "
           "Unser täglich Brot gib uns heute.")
def tokens(text, accent="fold"):
    if accent == "ae":
        text = text.replace("ä", "ae")
    elif accent == "fold":
        text = "".join(c for c in unicodedata.normalize("NFD", text)
                       if unicodedata.category(c) != "Mn")
    elif accent == "drop":
        text = text.replace("ä", "")
    return re.findall("[A-Z]+", text.upper())

def derive(text, unique=True, accent="fold", delta=-1):
    seen, words, skipped = set(), [], []
    for token in tokens(text, accent):
        if unique and token in seen:
            skipped.append(token)
            continue
        words.append(token)
        seen.add(token)
        if len(words) == len(CIPHER):
            break
    if len(words) != len(CIPHER):
        raise ValueError("Too few key words")
    totals = [sum(ord(c) - ord("A") + 1 for c in w) for w in words]
    shifts = [(n + delta) % 26 for n in totals]
    return words, totals, shifts, skipped

def crypt(text, shifts, direction):
    if len(text) != len(shifts):
        raise ValueError("Length mismatch")
    return "".join(chr(ord("A") + (ord(c)-ord("A")+direction*k) % 26)
                   for c, k in zip(text, shifts))

words, totals, shifts, skipped = derive(PASSAGE)
plain = crypt(CIPHER, shifts, -1)
print("ciphertext:", CIPHER, "length:", len(CIPHER))
print(" i word       sum shift ct pt rec")
for i, (w, n, k, c, p) in enumerate(zip(words, totals, shifts, CIPHER, plain), 1):
    print(f"{i:2} {w:10} {n:3} {k:5}  {c}  {p}  {crypt(p, [k], 1)}")
print("skipped occurrences:", " ".join(skipped))
print("plaintext:", plain, "length:", len(plain))
print("reencryption:", crypt(plain, shifts, 1))
print("roundtrip:", crypt(plain, shifts, 1) == CIPHER)
assert plain == "HIERBINICHTOTSIENSTEW"
assert crypt(plain, shifts, 1) == CIPHER
for label, options, sign in [
    ("no dedup", {"unique":False}, -1),
    ("ae transliteration", {"accent":"ae"}, -1),
    ("delete umlaut letter", {"accent":"drop"}, -1),
    ("sum without minus one", {"delta":0}, -1),
    ("reverse direction", {}, 1)]:
    k = derive(PASSAGE, **options)[2]
    print(label + ":", crypt(CIPHER, k, sign))
for label, text in [
    ("1912 verse start", "Darum sollt ihr also beten: " + PASSAGE),
    ("1984 prayer start", "Unser Vater im Himmel! Dein Name werde geheiligt. "
     "Dein Reich komme. Dein Wille geschehe wie im Himmel so auf Erden. "
     "Unser tägliches Brot gib uns heute. Und vergib uns unsere Schuld.")]:
    w, _, k, _ = derive(text)
    print(label + " words:", " ".join(w))
    print(label + " plaintext:", crypt(CIPHER, k, -1))
```

## Appendix B. Thouless B stdout

The following is the complete output, including the source digest and the complete word/shift arrays:

```console
$ python -B harness/verify_thouless_b.py
{
  "attribution": "Richard Bean, 2019; independently reproduced here",
  "plaintext": "A number of successful experiments of this kind would give strong evidence for survival",
  "letters": 74,
  "ciphertext": "INXPHCJKGMJIRPRFBCVYWYWESNOECNSCVHEGYRJQTEBJMTGXATTWPNHCNYBCFNXPFLFXRVQWQL",
  "reencryption_matches": true,
  "source": "https://www.gutenberg.org/ebooks/41215",
  "source_sha256": "9c8ad37c42b5fe8daf8c0ff7ee87c05e1749264b4edb9abf359fb593cffdbeff",
  "key_words": [
    "I",
    "FLED",
    "HIM",
    "DOWN",
    "THE",
    "NIGHTS",
    "AND",
    "DAYS",
    "ARCHES",
    "OF",
    "YEARS",
    "LABYRINTHINE",
    "WAYS",
    "MY",
    "OWN",
    "MIND",
    "IN",
    "MIST",
    "TEARS",
    "HID",
    "FROM",
    "UNDER",
    "RUNNING",
    "LAUGHTER",
    "UP",
    "VISTAED",
    "HOPES",
    "SPED",
    "SHOT",
    "PRECIPITATED",
    "ADOWN",
    "TITANIC",
    "GLOOMS",
    "CHASMED",
    "FEARS",
    "THOSE",
    "STRONG",
    "FEET",
    "THAT",
    "FOLLOWED",
    "AFTER",
    "BUT",
    "WITH",
    "UNHURRYING",
    "CHASE",
    "UNPERTURBED",
    "PACE",
    "DELIBERATE",
    "SPEED",
    "MAJESTIC",
    "INSTANCY",
    "THEY",
    "BEAT",
    "A",
    "VOICE",
    "MORE",
    "INSTANT",
    "THAN",
    "ALL",
    "THINGS",
    "BETRAY",
    "THEE",
    "WHO",
    "BETRAYEST",
    "ME",
    "PLEADED",
    "OUTLAW",
    "WISE",
    "BY",
    "MANY",
    "HEARTED",
    "CASEMENT",
    "CURTAINED",
    "RED"
  ],
  "zero_based_shifts": [
    8,
    0,
    3,
    3,
    6,
    24,
    18,
    22,
    1,
    20,
    15,
    6,
    15,
    11,
    25,
    13,
    22,
    8,
    10,
    20,
    25,
    9,
    18,
    13,
    10,
    1,
    10,
    17,
    9,
    21,
    4,
    23,
    2,
    0,
    22,
    14,
    14,
    9,
    22,
    13,
    23,
    16,
    7,
    24,
    9,
    13,
    24,
    2,
    22,
    1,
    0,
    5,
    1,
    0,
    1,
    24,
    18,
    16,
    24,
    24,
    18,
    11,
    19,
    10,
    17,
    20,
    13,
    3,
    0,
    0,
    8,
    1,
    16,
    0
  ]
}
[exit 0]
```

## Appendix C. Saved-result extraction and independent probability calculation

These commands only read existing repository data and print results. Loading the saved lexicon does not import the Wood verifier or execute the search pipeline.

```console
$ python -B - <<'PY'
import json
from pathlib import Path
j=json.loads(Path('attempts/wood35_solve_2026-10-04/bib_ml.json').read_text())
print('keys:', list(j))
for k in ['K','shards','recovered','n_plants','null_ceiling','plant_floor']:
 print(k, j[k])
for k in ['wood','wood_m1']:
 print(k, 'best:', j[k][0])
print('nulls:')
for i,r in enumerate(j['nulls']): print(i, r)
print('plant score range:',min(p['true_score'] for p in j['plants']),max(p['true_score'] for p in j['plants']))
PY
keys: ['K', 'shards', 'plants', 'nulls', 'wood', 'wood_m1', 'recovered', 'n_plants', 'null_ceiling', 'plant_floor']
K 26730018
shards 19
recovered 40
n_plants 40
null_ceiling -1.2731706558566063
plant_floor -1.0812636268194866
wood best: [-1.270257200624433, -80.14478540420532, 'HIERBINICHTOTSIENSTEW', 'bible_German.npz', 'D', 533250, [['HIER', 'de'], ['BIN', 'de'], ['ICH', 'de'], ['TOT', 'de'], ['SIEN', 'fr'], ['STEW', 'en']]]
wood_m1 best: [-1.2640577391435683, -91.36147618293762, 'ALENRENDRAYCUTREFUGES', 'bible_Danish.npz', 'D', 407328, [['AL', 'es'], ['EN', 'es'], ['RENDRA', 'fr'], ['Y', 'es'], ['CUT', 'en'], ['REFUGES', 'en']]]
nulls:
0 [-1.6108869504064296, -91.60612154006958, 'JIDISGALLIIHMERMANUMS', 'bible_Esperanto.npz', 'D', 659137]
1 [-1.5759936281195879, -88.45524907112122, 'GARAMERSAUFFIERPOCVOU', 'bible_Afrikaans.npz', 'P', 467894]
2 [-1.5088511198204484, -87.95905447006226, 'VUESADEHYAVERONARDOFY', 'bible_Maori.npz', 'P', 74681]
3 [-1.39173912537055, -94.92346358299255, 'ZUTIMESELUNSRAREEXFAZ', 'bible_Latin.npz', 'P', 185956]
4 [-1.2967194936518904, -84.26414394378662, 'NOTTOTEMOSFENIXAVEAST', 'bible_Danish.npz', 'D', 453084]
5 [-1.4962263078032159, -93.11062812805176, 'CIYITMOHABIAEGARELATO', 'bible_Danish.npz', 'D', 453841]
6 [-1.5089586440414118, -91.2927565574646, 'SEIDABITAEPICTAXIPLAN', 'bible_Swedish.npz', 'D', 449338]
7 [-1.4725768611657815, -88.50743103027344, 'EQUOIDOMMENBYLUNACHEI', 'bible_Norwegian.npz', 'P', 248911]
8 [-1.4279658475151793, -91.64534497261047, 'BOCKIHRAETOFDEBALIAAN', 'bible_Esperanto.npz', 'D', 359642]
9 [-1.2731706558566063, -84.41792559623718, 'COAPEXILLEESTGETORBEM', 'bible_Portuguese.npz', 'P', 392826]
10 [-1.4439369999243017, -90.34139394760132, 'HOGSDEESTICHIFIELBUEY', 'bible_Italian.npz', 'D', 93114]
11 [-1.4941350949076613, -90.10410284996033, 'WEASAGUESIXRENDUCEVAA', 'bible_Danish.npz', 'P', 399110]
12 [-1.4770222991116821, -87.04166460037231, 'UNEMEONTDALILLIESIHEB', 'bible_Danish.npz', 'D', 125901]
13 [-1.517427246556366, -91.3186616897583, 'QUMEDREINOFFULODUMTUT', 'bible_Finnish.npz', 'D', 413875]
14 [-1.5470004922251261, -93.02251148223877, 'NIVINWARCILEIDESTUVRE', 'bible_Romanian.npz', 'P', 631505]
15 [-1.5087501718792158, -90.087238073349, 'NIADANSCHSONOSIYMITIR', 'bible_Portuguese.npz', 'D', 130837]
16 [-1.5037640887027042, -90.46428632736206, 'CREFLORECAESAUNLAAEIM', 'bible_Esperanto.npz', 'P', 357694]
17 [-1.522781360780969, -92.41789436340332, 'MUTINOECRAPEBELESLOON', 'bible_German.npz', 'D', 71251]
18 [-1.5464291804887171, -87.32325029373169, 'TIAIDWENTFORDINIOPUSS', 'bible_Maori.npz', 'P', 944865]
19 [-1.423963563242331, -90.3804702758789, 'IUSLADARREADUPONYORBE', 'bible_Latin.npz', 'P', 251401]
plant score range: -1.2044265717681426 -0.5454828641906856
[exit 0]
```

```console
$ python -B - <<'PY'
import pickle, collections, math, json
from pathlib import Path
lex=pickle.loads(Path('harness/wood35t/mlseg_lex.pkl').read_bytes())
N=26730018
print('IID UNIFORM LETTER MODELS; union bounds, not semantic p-values')
print('N:',N,'two arithmetic conventions:',2*N)
print('26^21:',26**21,'exact fixed text expectation:',N/26**21)
print('report prefix probability times TEW:',N/(2000000*26**3))
print('TEW alone expectation:',N/26**3)
print('0/20 null exceedances: rank p:',1/21,'one-sided 95% upper:',1-0.05**(1/20))

def bounds(words,L):
 counts=collections.Counter(map(len,words))
 totals=[1]+[0]*L
 for n in range(1,L+1):
  totals[n]=sum(counts[k]*totals[n-k] for k in range(3,n+1))
 return totals[L],counts

german=set(w for w,v in sorted(lex['de'].items(),key=lambda x:-x[1])[:20000] if len(w)>=3)
s10,counts=bounds(german,10)
lo10=max(counts[10],counts[3]*counts[7],counts[4]*counts[6],counts[5]**2,counts[3]**2*counts[4])
print('German stored lexicon total:',len(lex['de']),'top-20000 eligible:',len(german))
print('German length counts:',dict(sorted((k,v) for k,v in counts.items() if k<=10)))
print('German 10-letter probability bounds:',lo10/26**10,s10/26**10)
print('German10 + arbitrary8 + TEW expected-hit bounds:',N*lo10/26**13,N*s10/26**13)
pooled=set()
for lang in lex:
 pooled.update(w for w,v in sorted(lex[lang].items(),key=lambda x:-x[1])[:20000] if len(w)>=3)
pooled.add('TOTSIENS')
s8,c8=bounds(pooled,8)
s18,c18=bounds(pooled,18)
print('pooled languages:',sorted(lex),'words including TOTSIENS:',len(pooled))
print('pooled counts lengths 3..18:',{k:c18[k] for k in range(3,19)})
print('German10 + pooled8 + TEW expected-hit upper:',N*s10*s8/26**21)
print('pooled18 + TEW expected-hit upper:',N*s18/26**21)
print('pooled18 + any 3 initials expected-hit upper:',N*s18/26**18)
for M in [1e6,1e9,1e12,1e15,1e18,1e20]:
 print('accepted 21-letter strings',format(M,'.0e'),'search union bound:',min(1,N*M/26**21))
print('strings needed for 0.001 union bound:',0.001*26**21/N)
print('strings needed for 0.05 union bound:',0.05*26**21/N)
j=json.loads(Path('attempts/wood35_solve_2026-10-04/bib_ml.json').read_text())
print('Wood minus null ceiling:',j['wood'][0][0]-j['null_ceiling'])
print('Wood minus plant floor:',j['wood'][0][0]-j['plant_floor'])
print('alternative minus Wood:',j['wood_m1'][0][0]-j['wood'][0][0])
PY
IID UNIFORM LETTER MODELS; union bounds, not semantic p-values
N: 26730018 two arithmetic conventions: 53460036
26^21: 518131871275444637960845131776 exact fixed text expectation: 5.158921788424404e-23
report prefix probability times TEW: 0.0007604124374146564
TEW alone expectation: 1520.8248748293126
0/20 null exceedances: rank p: 0.047619047619047616 one-sided 95% upper: 0.13910834066826516
German stored lexicon total: 10933 top-20000 eligible: 10870
German length counts: {3: 175, 4: 510, 5: 1278, 6: 1768, 7: 1594, 8: 1453, 9: 1167, 10: 991}
German 10-letter probability bounds: 1.1064015964705072e-07 3.6022406471308517e-07
German10 + arbitrary8 + TEW expected-hit bounds: 0.0001682643069463211 0.000547837718127784
pooled languages: ['de', 'en', 'es', 'fr', 'it', 'la', 'pt'] words including TOTSIENS: 93188
pooled counts lengths 3..18: {3: 1117, 4: 3797, 5: 10271, 6: 14909, 7: 17418, 8: 16370, 9: 12158, 10: 8139, 11: 4588, 12: 2354, 13: 1155, 14: 526, 15: 202, 16: 114, 17: 30, 18: 18}
German10 + pooled8 + TEW expected-hit upper: 9.806019288070697e-08
pooled18 + TEW expected-hit upper: 0.00019964869317584547
pooled18 + any 3 initials expected-hit upper: 3.50902543125866
accepted 21-letter strings 1e+06 search union bound: 5.158921788424404e-17
accepted 21-letter strings 1e+09 search union bound: 5.158921788424404e-14
accepted 21-letter strings 1e+12 search union bound: 5.158921788424404e-11
accepted 21-letter strings 1e+15 search union bound: 5.158921788424404e-08
accepted 21-letter strings 1e+18 search union bound: 5.1589217884244044e-05
accepted 21-letter strings 1e+20 search union bound: 0.005158921788424404
strings needed for 0.001 union bound: 1.9383895337273795e+19
strings needed for 0.05 union bound: 9.691947668636898e+20
Wood minus null ceiling: 0.0029134552321732343
Wood minus plant floor: -0.1889935738049464
alternative minus Wood: 0.006199461480864699
[exit 0]
```

## Appendix D. Sensitivity controls and evidence hashes

This uses `runpy` only on my own new `/tmp` verifier, suppressing its previously recorded stdout. The historical-spelling controls are explicitly transcribed comparison passages, not claims to have downloaded a 1545 scan.

```console
$ python -B - <<'PY'
import pickle, collections, json, hashlib, runpy
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
N=26730018
lex=pickle.loads(Path('harness/wood35t/mlseg_lex.pkl').read_bytes())
allwords={w for lang in lex.values() for w,v in sorted(lang.items(),key=lambda x:-x[1])[:20000]}
allwords.add('TOTSIENS')
for minimum in (3,2,1):
 words={w for w in allwords if len(w)>=minimum and (len(w)>1 or w in {'A','I','O','Y','E','U'})}
 c=collections.Counter(map(len,words)); d=[1]+[0]*18
 for n in range(1,19): d[n]=sum(c[k]*d[n-k] for k in range(1,n+1))
 expected=N*d[18]/26**21
 print('minimum length',minimum,'n1',c[1],'n2',c[2],'18-letter derivations',d[18],'expected-hit upper',expected,'union probability upper',min(1,expected))
print('closed >=3 model, TEW at any one of 19 slots, two arithmetic conventions upper:',2*19*0.00019964869317584547)
with redirect_stdout(StringIO()): m=runpy.run_path('/tmp/wood35_independent_review.py')
t=m['PASSAGE']; derive=m['derive']; crypt=m['crypt']; ct=m['CIPHER']
variants=[('only taeglich',t.replace('täglich','taeglich')),
 ('only taegliches folded',t.replace('täglich','tägliches')),
 ('1545 lexical spelling, u/v modernized', 'Unser Vater in dem Himel. Dein Name werde geheiliget. Dein Reich kome. Dein Wille geschehe auff Erden wie im Himel. Unser teglich Brot gib uns heute.'),
 ('1545 lexical spelling, original v', 'Vnser Vater in dem Himel. Dein Name werde geheiliget. Dein Reich kome. Dein Wille geschehe auff Erden wie im Himel. Vnser teglich Brot gib vns heute.')]
for label,t in variants:
 w,s,k,sk=derive(t)
 print(label+':',crypt(ct,k,-1))
 print('changed positions:',[(i+1,a,b) for i,(a,b) in enumerate(zip(m['words'],w)) if a!=b])
for p in ['attempts/wood35_solve_2026-10-04/REPORT.md','harness/wood35t/PREREG.md','attempts/wood35_solve_2026-10-04/bib_ml.json','harness/wood35t/mlseg_lex.pkl','harness/verify_thouless_b.py','/tmp/wood35_independent_review.py']:
 print('sha256',hashlib.sha256(Path(p).read_bytes()).hexdigest(),p)
PY
minimum length 3 n1 0 n2 0 18-letter derivations 3869969372744077720 expected-hit upper 0.00019964869317584547 union probability upper 0.00019964869317584547
minimum length 2 n1 0 n2 209 18-letter derivations 6199935610535915203974 expected-hit upper 0.3198498290802209 union probability upper 0.3198498290802209
minimum length 1 n1 6 n2 209 18-letter derivations 124618508819540549591910 expected-hit upper 6.428971403900865 union probability upper 1
closed >=3 model, TEW at any one of 19 slots, two arithmetic conventions upper: 0.007586650340682128
only taeglich: HIERBINICHTOTSIENNTEW
changed positions: [(18, 'TAGLICH', 'TAEGLICH')]
only taegliches folded: HIERBINICHTOTSIENUTEW
changed positions: [(18, 'TAGLICH', 'TAGLICHES')]
1545 lexical spelling, u/v modernized: HIEROINIXHGOTMIENOTEW
changed positions: [(5, 'HIMMEL', 'HIMEL'), (9, 'GEHEILIGT', 'GEHEILIGET'), (11, 'KOMME', 'KOME'), (14, 'AUF', 'AUFF'), (18, 'TAGLICH', 'TEGLICH')]
1545 lexical spelling, original v: GIEROINIXHGOTMIENOTEV
changed positions: [(1, 'UNSER', 'VNSER'), (5, 'HIMMEL', 'HIMEL'), (9, 'GEHEILIGT', 'GEHEILIGET'), (11, 'KOMME', 'KOME'), (14, 'AUF', 'AUFF'), (18, 'TAGLICH', 'TEGLICH'), (21, 'UNS', 'VNS')]
sha256 ce045f73b4c83d9400ef96b1c064ec234112bd9a5ba8c9462aba6b11f37f5b81 attempts/wood35_solve_2026-10-04/REPORT.md
sha256 83818f9824fad704f5db327dba80d232eb185b0b8d4f117defd07386c9377de9 harness/wood35t/PREREG.md
sha256 d6ed76fef39138da45ba5bda8dd3370100bf11fef79eeae8f848c64db52f6ffd attempts/wood35_solve_2026-10-04/bib_ml.json
sha256 c0b24e6f368316af468dd42b44383904467710721e21f7e1a0dd20279d1ca262 harness/wood35t/mlseg_lex.pkl
sha256 1c9f2f19d01c5b93bd6bdbf1e0543a1cd2e846ee56daeec2109fab04582d468f harness/verify_thouless_b.py
sha256 e7199cbf9dea3b1a82c63167055af080d36f8caeddea496f1f831615279b91c4 /tmp/wood35_independent_review.py
[exit 0]
```

## Appendix E. Newly added full-corpus results

```console
$ python -B - <<'PY'
from pathlib import Path
import json, hashlib
root=Path('attempts/wood35_solve_2026-10-04')
for name in ['full_gutenberg_ml.json','full_gutenberg_ml.out']:
 p=root/name
 print(name,'exists:',p.exists())
 if not p.exists(): continue
 print('sha256:',hashlib.sha256(p.read_bytes()).hexdigest())
 if name.endswith('.json'):
  j=json.loads(p.read_text())
  for k in ['K','shards','recovered','n_plants','plant_floor','null_ceiling']: print(k,j[k])
  print('Wood best:',j['wood'][0])
  print('Woodm1 best:',j['wood_m1'][0])
  print('saved Wood rows:',len(j['wood']),len(j['wood_m1']))
 else:
  for line in p.read_text().splitlines():
   if line.startswith(('shards','GATE','WOOD ')):
    print(line)
combined=2*(26730018+400294934)
print('combined hypotheses including both arithmetic conventions:',combined)
print('closed >=3 pooled18+TEW union bound over combined:',combined/26730018*0.00019964869317584547)
PY
full_gutenberg_ml.json exists: True
sha256: 16e5f86bb127aaa4391516633e0ab5fb5b427cf949354bd51770da3fdfd0de91
K 400294934
shards 3847
recovered 40
n_plants 40
plant_floor -1.0812636268194866
null_ceiling -1.2068555307731
Wood best: [-1.3125684883681035, -78.31541061401367, 'OFERANTREFUSAIDAUTIOR', 'es_26947.npz', 'P', 6848, [['O', 'pt'], ['FERANT', 'la'], ['REFUSA', 'la'], ['IDA', 'la'], ['UTI', 'la'], ['OR', 'la']]]
Woodm1 best: [-1.2640577391435683, -91.36147618293762, 'ALENRENDRAYCUTREFUGES', 'da_2144.npz', 'D', 408858, [['AL', 'es'], ['EN', 'es'], ['RENDRA', 'fr'], ['Y', 'es'], ['CUT', 'en'], ['REFUGES', 'en']]]
saved Wood rows: 30 30
full_gutenberg_ml.out exists: True
sha256: 5f42d1ea8dc2104a8ae6708dd536f1e7081551ef91394b7d19332975efc9c290
shards 3847 K 400294934 search s 1324
GATE 40/40 recovered; plant floor -1.081; null ceiling -1.207
WOOD  -1.313   -78.3 OFERANTREFUSAIDAUTIOR es_26947.npz P 6848 O/pt FERANT/la REFUSA/la IDA/la UTI/la OR/la
WOOD  -1.313   -78.3 OFERANTREFUSAIDAUTIOR es_26947.npz D 6848 O/pt FERANT/la REFUSA/la IDA/la UTI/la OR/la
WOOD  -1.318   -88.3 SUMACASYYAURASPARTYON de_20780.npz P 8711 SU/es MACAS/pt Y/es Y/es AURAS/la PARTY/en ON/en
WOOD  -1.371   -90.4 ACHBOUNDJUCASASETWELT it_45698.npz D 33151 ACH/de BOUND/en JU/en CASAS/pt ET/la WELT/de
WOOD  -1.417   -94.0 HUICDISSRFINSCISADEST nl_21409.npz D 35107 HUIC/la DIS/fr SR/fr FIN/fr SCIS/la ADEST/la
WOOD  -1.426   -93.1 POURANTOJEDAVAVALYMED nl_17549.npz D 38365 POUR/fr ANTOJE/fr DAVA/pt VAL/pt Y/es MED/en
WOOD  -1.431   -92.1 DIAJOESLEGGEESEXADAMS fr_16236.npz P 50043 DIA/es JOES/en LEGGE/it E/it SEX/en ADAMS/en
WOOD  -1.467   -84.3 STAYEARSOMASTILEODUNE la_27672.npz D 476434 STAY/en EAR/en SOMA/it STILE/it OD/it UNE/fr
WOOD  -1.504   -79.9 EELISUREINCOMEFELULES fi_15632.npz D 21707 E/it E/it LI/it SURE/en INCOME/en FE/it LU/fr LES/fr
WOOD  -1.506   -86.0 DIREASTEVUSARARICAEJA nl_23759.npz D 12440 DIRE/fr AS/pt TE/pt VU/fr SARA/it RICA/pt E/pt JA/pt
WOOD  -1.517   -94.0 DELTOPOCALAGEILLIYISY hu_67540.npz P 15449 DEL/es TO/es POCA/es LAGE/de ILLI/la Y/es IS/es Y/es
WOOD  -1.526   -87.5 CHETEMOENUGARYNASEAST eo_49233.npz D 658 CHE/it TEMO/it EN/es U/de GAR/de Y/es NAS/pt EAST/en
WOOD  -1.527   -84.8 OCHECASOARTHITUDALHIS nl_36225.npz P 90590 O/pt CHE/it CASO/pt ART/de HI/la TU/it DAL/it HIS/en
WOOD  -1.536   -80.5 ATSECAVENDTRADIGNALEX fr_12666.npz P 79028 AT/en SECA/pt VEND/fr TRA/it DIGNA/la LEX/en
WOOD  -1.538   -90.5 DCOSECCEUDOTOALSINIEO it_29325.npz P 29835 DC/fr OS/pt ECCE/la UDO/la TO/de ALS/de INIEO/pt
combined hypotheses including both arithmetic conventions: 854049904
closed >=3 pooled18+TEW union bound over combined: 0.00637896866513731
[exit 0]
```

## Appendix F. Source access and novelty-check commands

Exact terminal network probe and output:

```console
$ python -B - <<'PY'
import urllib.request, hashlib, re
urls = [
 'https://raw.githubusercontent.com/christos-c/bible-corpus/master/bibles/German.xml',
 'https://iapsop.com/archive/materials/spr_proceedings/spr_proceedings_v49_1949-52.pdf',
 'https://scienceblogs.de/klausis-krypto-kolumne/2017/04/17/the-top-50-unsolved-encrypted-messages-35-cryptograms-from-the-crypt/',
 'https://www.biblegateway.com/passage/?search=Matthew%206%3A9-13&version=LUTH1545'
]
for u in urls:
 print('URL:', u)
 try:
  with urllib.request.urlopen(u, timeout=15) as r: b=r.read()
  print('bytes:',len(b), 'sha256:', hashlib.sha256(b).hexdigest())
  if 'German.xml' in u:
   s=b.decode()
   for v in ['b.MAT.6.9','b.MAT.6.10','b.MAT.6.11']:
    m=re.search(r'<seg[^>]*'+re.escape(v)+r'[^>]*>.*?</seg>',s,re.S)
    print(m.group() if m else 'not found: '+v)
 except Exception as e: print(type(e).__name__, str(e))
PY
URL: https://raw.githubusercontent.com/christos-c/bible-corpus/master/bibles/German.xml
URLError <urlopen error [Errno 1] Operation not permitted>
URL: https://iapsop.com/archive/materials/spr_proceedings/spr_proceedings_v49_1949-52.pdf
URLError <urlopen error [Errno 1] Operation not permitted>
URL: https://scienceblogs.de/klausis-krypto-kolumne/2017/04/17/the-top-50-unsolved-encrypted-messages-35-cryptograms-from-the-crypt/
URLError <urlopen error [Errno 1] Operation not permitted>
URL: https://www.biblegateway.com/passage/?search=Matthew%206%3A9-13&version=LUTH1545
URLError <urlopen error [Errno 1] Operation not permitted>
[exit 0]
```

The following are exact **web tool arguments**, not shell commands. I give the relevant returned results and retrieval errors; unrelated search hits are omitted. Indexed text and successful direct page reads are distinguished.

**1912 wording search:**

```json
{"search_query":[{"q":"site.scienceblogs.de/klausis-krypto-kolumne/2017/04/17/ \"35\""},{"q":"site.bibel-online.net/buch/luther_1912/matthaeus/6 \"Unser\" \"täglich\""},{"q":"site.biblegateway.com/passage \"LUTH1545\" \"Unser Vater\" \"täglich\""},{"q":"\"Lutherbibel 1984\" \"Matthäus 6\" \"Unser Vater\""}],"response_length":"long"}
```

Result: the indexed Bibel-Online `/text/luther_1912/matthaeus/6/` page supplied verses 9–11 matching the user-provided wording. A later direct opening of that actual URL returned `(403) Forbidden`.

**1545-labelled wording and historical spelling search:**

```json
{"search_query":[{"q":"site:iapsop.com/archive/materials/spr_proceedings/spr_proceedings_v49_1949-52.pdf \"language\""},{"q":"site:biblegateway.com \"Matthäus 6:9-13\" \"LUTH1545\""},{"q":"site:stilkunst.de/lutherbibel-1545/Mt/mt-06.php"}],"response_length":"long"}
```

Result: the BibleGateway dual-version URL cited in task 3 supplied the matching modern-spelling LUTH1545 verses. The Stilkunst result supplied the historical edition page. Direct reading and a subsequent find on that page succeeded; the prayer occurs at extracted line 222. Distinctive spelling examples used in the controls: `Himel, geheiliget, kome, auff, teglich, Vnſer, vns`. Direct opening of the BibleGateway URL returned `Cache miss`.

**1984 wording:**

```json
{"open":[{"ref_id":"https://scienceblogs.de/klausis-krypto-kolumne/2017/04/17/the-top-50-unsolved-encrypted-messages-35-cryptograms-from-the-crypt/"}],"search_query":[{"q":"\"Matthäus 6\" \"Luther 1984\" \"Unser\""}],"response_length":"short"}
```

Results included the two 1984 sources linked in task 3, with the differences recorded there. Direct opening of the Schmeh page failed.

**Wood’s original language condition:**

```json
{"open":[{"ref_id":"https://www.stilkunst.de/lutherbibel-1545/Mt/mt-06.php"},{"ref_id":"https://iapsop.com/archive/materials/spr_proceedings/"}],"search_query":[{"q":"\"Wood\" \"the message\" \"not be in any one language\""},{"q":"\"Wood\" \"cryptogram\" \"solved\" \"totsiens\""}],"response_length":"short"}
```

Result: the indexed Wood paper returned the condition quoted in task 4 and described his foreign-language and distinct-word instructions. The archive index opened successfully. The old PDF URL returned 404 on direct access; following the archive’s current volume-49 link produced `Cache miss`, and opening the equivalent non-www URL also failed. No facsimile was viewed.

**Afrikaans and historical use:**

```json
{"search_query":[{"q":"\"T. E. Wood\" \"any one language\""},{"q":"\"totsiens\" dictionary South African English"},{"q":"\"Luther 1545\" \"Vnser\" \"Matth\" \"Himel\""}],"response_length":"long"}
```

Result: the Dictionary of South African English entry supplied the meaning, alternative spacing, Afrikaans origin, and dated 1937/1944 examples summarized in task 4.

**Exact novelty searches, issued separately:**

```json
{"search_query":[{"q":"\"HIERBINICHTOTSIENSTEW\""}],"response_length":"short"}
```

```text
Empty search results
No results were found for the provided queries
```

```json
{"search_query":[{"q":"\"Hier bin ich\" \"Totsiens\" \"Wood\""}],"response_length":"short"}
```

```text
Empty search results
No results were found for the provided queries
```

**Ciphertext and broader novelty searches:**

```json
{"search_query":[{"q":"\"FVAMI NTKFX XWATB OIZVV X\""},{"q":"\"T. E. Wood\" cryptogram solved"},{"q":"\"HIERBINICHTOTSIENSTEW\""}],"response_length":"long"}
```

Result: indexed Wood paper and Schmeh’s actual 2017 #35 page, both agreeing with the ciphertext. No matching published decipherment appeared.

```json
{"search_query":[{"q":"Wood cryptogram solved site:klausschmeh.net"},{"q":"\"Wood\" \"Totsiens\""},{"q":"\"HIERBINICHTOTSIENSTEW\""},{"q":"\"Wood\" \"Thouless\" \"Bourdeau\""}],"response_length":"short"}
```

Result: no relevant prior solve; most returned matches were unrelated. This weak search result is not proof of novelty.

```json
{"open":[{"ref_id":"https://dbourdeau.github.io/cyphersolver/"},{"ref_id":"https://www.spr.ac.uk/11-survival-theories-and-speculations"}],"search_query":[{"q":"site:scienceblogs.de/klausis-krypto-kolumne/cryptographic-cold-cases-from-parapsychology/ \"Wood\""},{"q":"site:dbourdeau.github.io/cyphersolver \"Wood\""}],"response_length":"short"}
```

Result: indexed Schmeh cold-case text describes Wood as unsolved; indexed Bourdeau pages updated 2 October 2026 mention other Wood-related historical ciphers, with no matching T. E. Wood solution in the returned material. Direct opening of Bourdeau’s home URL failed. The SPR page opened successfully and confirmed the bibliographic entry at extracted line 89.

The raw corpus attempt was:

```json
{"open":[{"ref_id":"https://scienceblogs.de/klausis-krypto-kolumne/2017/04/17/the-top-50-unsolved-encrypted-messages-35-cryptograms-from-the-crypt/?all=1"},{"ref_id":"https://www.biblegateway.com/passage/?search=Matthew%206%3A9-13&version=LUTH1545"},{"ref_id":"https://www.bibleserver.com/LUT84/Matth%C3%A4us6%2C9-11"},{"ref_id":"https://raw.githubusercontent.com/christos-c/bible-corpus/master/bibles/German.xml"}],"response_length":"long"}
```

The first three direct accesses failed. The corpus response was:

```text
Failed to fetch https://raw.githubusercontent.com/christos-c/bible-corpus/master/bibles/German.xml: (400) Content length is too large: 4194305+
```

## Appendix G. Read-only inspection and the changing report

The principal exact source-inspection commands were:

```sh
cat attempts/wood35_solve_2026-10-04/REPORT.md harness/verify_thouless_b.py attempts/thouless_b_crack.md
cat harness/wood35t/PREREG.md harness/wood35t/RESULT.md harness/wood35t/run_ml.py harness/wood35t/mlseg.py harness/wood35t/mlsearch.py harness/wood35t/bible_shards.py
cat attempts/wood35_solve_2026-10-04/bib_ml.out ciphers/wood_35.json notes/astra/PROMPT_WOOD35.md
sed -n '1,130p' harness/wood35/w35.py
```

All exited 0. The source files themselves are the outputs of those `cat` commands; material excerpts underlying the review are reproduced below rather than duplicating the entire claim and all search code.

Preregistration excerpt:

```text
## Bar for Wood (all required)
(a) best final score > null ceiling; (b) >= plant floor; (c) the plaintext reads as words a
human accepts in the stated languages; (d) named book, variant and token offset; exact
re-encryption by script. Anything less is reported as a lead.
```

Search-code excerpts:

```python
z = np.load(f); sh = z['shifts'].astype(np.int64); wid = z['wid'].astype(np.int64); K += 2 * sh.shape[0]
cts = {'WOOD': WOOD, 'WOODm1': ''.join(chr((ord(c) - 66) % 26 + 65) for c in WOOD)} if not os.environ.get('NOWOOD') else {'WOOD': 'A' * 21}
out['nulls'].append(b[:6] if b else None); nullmax = max(nullmax, b[0] if b else -99)
w = rescore('WOOD'); out['wood'] = [x[:7] for x in w[:30]]
```

These are noncontiguous original source lines. They establish the trial-count convention, second arithmetic search, and saved-candidate limitations. The scorer’s source declares seven lexicon languages and contains no explicit initials rule.

The exact focused search for a supporting simulation was:

```sh
rg -n '1.?in.?2.?000.?000|2000000|20000000|2_000_000|top_n_list|german.*initial|initial.*german|TOTSIENS|Totsiens' attempts/wood35* harness/wood35* --glob '!verify_wood.py' --glob '!*.json' --glob '!*.out' --glob '!*.pkl'
```

It exited 0 and found the claim/reading in the report and saved verifier output, plus an unrelated 200,000,000 book-fetch budget. It found no simulation implementation. This is a bounded search of the reviewed Wood directories, not a claim about every temporary file ever used.

The report hash in Appendix D was:

```text
ce045f73b4c83d9400ef96b1c064ec234112bd9a5ba8c9462aba6b11f37f5b81
```

Later I ran:

```sh
python -B - <<'PY'
import hashlib
from pathlib import Path
for p in ['attempts/wood35_solve_2026-10-04/REPORT.md','harness/wood35t/PREREG.md','attempts/wood35_solve_2026-10-04/bib_ml.json','harness/verify_thouless_b.py']:
 print(hashlib.sha256(Path(p).read_bytes()).hexdigest(),p)
PY
```

Output:

```text
968d444c0f62eeb89bbc6c79bff8107e97628f6877f14975f1df6e646a977f5f attempts/wood35_solve_2026-10-04/REPORT.md
83818f9824fad704f5db327dba80d232eb185b0b8d4f117defd07386c9377de9 harness/wood35t/PREREG.md
d6ed76fef39138da45ba5bda8dd3370100bf11fef79eeae8f848c64db52f6ffd attempts/wood35_solve_2026-10-04/bib_ml.json
1c9f2f19d01c5b93bd6bdbf1e0543a1cd2e846ee56daeec2109fab04582d468f harness/verify_thouless_b.py
```

Re-reading with `cat attempts/wood35_solve_2026-10-04/REPORT.md` showed the added section headed `Addendum: the pre-registered full-corpus arm (the English-only search (17 September 2026) key class, multilingual scoring)`; it reported K=400,294,934 and named the two new result files. Appendix E records my independent inspection of them. I did not write that addition.

No `AGENTS.md` was found by the parent-path checks or the repository `rg --files --hidden -g AGENTS.md` inspection. The review destination did not exist before creation.
