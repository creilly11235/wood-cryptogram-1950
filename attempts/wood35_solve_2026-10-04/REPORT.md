# #35 T. E. Wood's cryptogram (1950): solved, 4 October 2026

**This is the project's first solve of a previously unsolved Top 50 item.** Novelty was
checked against Schmeh's Cipherbrain #35 page and comments (2017-2020), klausschmeh.net
search (Wood, Thouless; to Sept 2026), the Top 50 list page, Daniel Bourdeau's Sept 2026
decipherment log, and web searches for the ciphertext and the plaintext. No published
solution was found. Thouless's Message B (same list entry) was solved by Richard Bean in 2019;
Wood's cryptogram was the part of #35 still open.

## Result

| | |
|---|---|
| Ciphertext (Schmeh, Cipherbrain, 17 Apr 2017) | `FVAMI NTKFX XWATB OIZVV X` |
| Key text | Matthew 6:9-11, Luther Bible 1912, from "Unser Vater", i.e. the Lord's Prayer: *Unser Vater in dem Himmel! Dein Name werde geheiligt. Dein Reich komme. Dein Wille geschehe auf Erden wie im Himmel. Unser täglich Brot gib uns ...* |
| Method | Thouless's own, exactly as Bean recovered it for Message B: consecutive **distinct** words (the repeated DEIN, HIMMEL, UNSER are skipped), accents folded, word letter-sum A=1..Z=26, shift = (sum - 1) mod 26, plaintext = ciphertext - shift |
| Key words | UNSER VATER IN DEM HIMMEL DEIN NAME WERDE GEHEILIGT REICH KOMME WILLE GESCHEHE AUF ERDEN WIE IM TAGLICH BROT GIB UNS |
| Plaintext | **HIERBINICHTOTSIENSTEW** |
| Reading | **HIER BIN ICH -- TOTSIENS -- T. E. W.**: German "Hier bin ich" ("here am I"), Afrikaans "Totsiens" ("goodbye"), signed with Wood's initials |

Reproduce: `python harness/wood35t/verify_wood.py` (standalone; no repository code imported).
It prints the key words and shifts, asserts the plaintext, re-encrypts it to the published
ciphertext exactly, and shows that each deviation from the method destroys the reading.
Output: `verify_output.txt`.

## Why this is the answer, not a coincidence

1. **It matches everything Wood said.** The key comes from "a book which is not written in
   English" (a German Bible). The cleartext is "authored in several different languages"
   (German, Afrikaans, and English initials). He used "the same method as Thouless" (the
   decryption uses Bean's verified convention unchanged, including the distinct-word rule,
   which matters here: three repeated words are skipped).
2. **The key is the most natural possible choice:** the opening words of the Lord's Prayer,
   in the wording of the German Bible. Thouless chose a famous religious poem from its first
   line; Wood chose the most famous prayer from its first line.
3. **The message fits the experiment.** A survival test whose plaintext is "Here am I --
   goodbye -- T. E. W." is what a man who meant to speak from beyond the grave would write.
4. **Exact re-encryption:** all 21 letters, no edits, no source corrections.
5. **It was found blind**, not fitted: the Bible-tier search (19 Latin-script Bibles,
   26,730,018 key hypotheses, both variants) ranked this decryption first for Wood's
   ciphertext under both the pooled 7-language 4-gram prefilter (-80.1, better than every
   null's best) and the multilingual segmentation score (`bib_ml.json`, `bib_ml.out`).
6. **Chance level:** a wrong key gives 21 uniform letters. Probability that 10 random
   letters split into common German words of three or more letters: 1 in 2,000,000 by
   simulation (top 20,000 German words); probability that the last three are the author's
   initials: 1/17,576. Joint about 2.8e-11 per hypothesis; expected chance hits about 3e-11
   for the single a-priori key, 9e-7 over every verse start of the German Bible, and 7.6e-4
   even over the entire blind Bible search. This ignores the eight further letters that spell
   "Totsiens", which would lower these numbers by several more orders of magnitude.

## Honest note on the pre-registered automatic bar

`harness/wood35t/PREREG.md` (Amendment 2, Bible tier) set an automatic bar: (a) best score >
null ceiling, (b) >= 5th-percentile plant floor. The gate passed (40/40 plants recovered at rank
1). Wood's best scored -1.270 against a null ceiling of -1.273 (passes by 0.003) and a plant
floor of -1.081 (**fails**). The scorer's lexicons (en fr de la it es pt) contain neither
Afrikaans nor initials, so it parsed TOTSIENS TEW as "TOT/de SIEN/fr STEW/en" and penalised it.
The automatic bar was not met; the solve rests on criteria (c)-(d) of the same bar (a reading
a human accepts, a named book and offset, exact re-encryption by script) together with the
chance calculation above. The score shortfall is a property of the scorer, not of the text.

## Key-text provenance

- Search hit: christos-c/bible-corpus `German.xml` (SHA-256 49be6f5e...52a3), verse
  b.MAT.6.9-11, token offset 533,250, variant D.
- Independently confirmed wording: bibel-online.net, Luther 1912, Matthäus 6:9-11; and
  BibleGateway Matthäus 6:9-13 (LUTH1545 text): "Darum sollt ihr also beten: Unser Vater in
  dem Himmel! Dein Name werde geheiligt. / Dein Reich komme. Dein Wille geschehe auf Erden wie
  im Himmel. / Unser täglich Brot gib uns heute."
- The common liturgical wording ("Vater unser im Himmel ...") does not work; the earlier
  hand-entered passage arm (Arm A) contained only that wording, which is why it missed.

## Credit and context
Method: Robert Thouless (1948); its exact convention recovered by Richard Bean (2019).
Ciphertext and Wood's statements: Klaus Schmeh (Cipherbrain #35; *Nicht zu knacken*).
The multilingual-plaintext reading of Schmeh's note and the Bible-tier search are this round's.
