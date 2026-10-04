# #35 Wood, Round 89: targeted and multilingual arms

## Arm A: hand-entered famous non-English passages (done, negative)
`passages/{latin,french,german,other}.txt`: about 140 passages typed from memory
(Vulgate and liturgy, Virgil, Horace, Catullus, Lucretius, Ovid, Cicero, Caesar, Augustine,
Boethius, Imitatio, Emerald Tablet; Lamartine, Hugo, Baudelaire, Verlaine, Villon, Ronsard,
Du Bellay, La Fontaine, Musset, Vigny, Pascal, Descartes, Rousseau, Montaigne, Kardec,
Rimbaud, Chenier, Gilbert, Malherbe, Proust, Corneille, Racine, French Bible; Goethe, Heine,
Schiller, Luther, Hoelderlin, Rilke, Novalis, Eichendorff, Uhland, Kant, Nietzsche, Claudius;
Dante, Petrarch, Leopardi, Cervantes, Manrique, Calderon, Teresa, Juan de la Cruz, Camoes,
Lord's Prayer in Welsh/Gaelic/Irish/Esperanto/Dutch/Italian/Spanish/Greek translit., Homer
translit.). Every start offset, distinct-word and all-word streams, six arithmetic variants
(sum-1 or sum, subtract/add, Beaufort). Because each key word sets one letter, a slightly
misremembered text still gives a mostly-correct plaintext, so memory errors cost little.
- English 4-gram (`try.py`): best -6.34/char, gibberish (true English 21-letter: about -4.45,
  e.g. Thouless B's first 21 letters under its true key). `attempts/wood35t/passages_en.txt`.
- Multilingual segmentation (`try_ml.py`): best segmentable decryption -1.94/letter
  ("WEY KAW KW CUI..."); real multilingual phrases score -0.7..-1.1; uniform random strings
  segment in 16/20000 cases, best -2.15. `attempts/wood35t/passages_ml.txt`.
**Negative for these passages.**

## Arm B: multilingual re-scoring of the Round 52 key class (pre-registered, done, negative)
See PREREG.md. Pilot on the first 786 rebuilt books (K = 79,173,018, plants only, Wood not
scored): gate 8/8 plants recovered at rank 1, plant floor -1.05, null ceiling -1.37 (4 nulls).

Full run: 3,847 books, K = 400,294,934; gate 40/40; plant floor -1.081; null ceiling -1.207;
Wood best -1.313 (junk). Negative, as expected (key not in the book list).

## Arm C: Bible tier (Amendment 2) -- SOLVED
19 Latin-script Bibles, K = 26,730,018; gate 40/40; floor -1.081; null ceiling -1.273.
Wood's top decryption: German Bible, Matthew 6:9 from "Unser Vater", variant D:
HIERBINICHTOTSIENSTEW. See attempts/wood35_solve_2026-10-04/REPORT.md.
