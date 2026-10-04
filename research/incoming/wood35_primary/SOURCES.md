# Primary sources

Both papers are in the *Proceedings of the Society for Psychical Research*, scanned by IAPSOP.
Quotations are from the scans' OCR text layer, checked against the page images.

## T. E. Wood, "A Further Test for Survival", *Proceedings* 49 (Part 178), pp. 105-106

PDF: http://www.iapsop.com/archive/materials/spr_proceedings/proceedings_of_the_spr_v49_1949-52.pdf
(SHA-256 668c24d8f7e64584dd25fc2e00d32695ebe713cfdc3e7ca24d6ec98c7141f811; PDF pages 109-110)

> My ciphered passage is : FVAMI NTKFX XWATB OIZVV X

> The first 21 words of the key passage are used as the bases of the 21 letters in the key
> series of letters, but (as Dr Thouless suggests) all second and later repetitions of words
> already used in the key passage have been omitted, when constructing the key series of letters.

> The key passage to the decipherment of my message is in an accessible book.

> I shall also try to communicate in what foreign language the key passage is. The message, if
> and when deciphered, will not be in any one language.

> Will anyone attempting to decipher it, please communicate the result (even if negative) to the Society.

## R. H. Thouless, "A Test of Survival", *Proceedings* 48, pp. 258-260

PDF: http://www.iapsop.com/archive/materials/spr_proceedings/proceedings_of_the_spr_v48_1946-49.pdf
(SHA-256 7086056a72ebcdf6b756a82728d68dfd9b9e077cb42b60da95a1817799bc9039; PDF pages 272-274)

> Each word in a continuous passage is replaced by a single letter which is obtained by adding up
> the serial numbers of the letters in the word (i.e. 1 for a, 2 for b, etc.), and then taking the
> letter whose serial number is this total or, if the total is greater than 26, taking the letter
> whose serial number is the remainder after division by 26.

> ... all second and later repetitions of words already used are omitted. Words joined by a hyphen
> are treated as two words.

His worked example (p. 260), keyed with Hamlet's "To be or not to be" speech:

> Key-letter series : IGGWW BG PI VNWNU
> Original passage : THERE IS NO DEATH
> Enciphered passage : BNKNA JYCWY RWGB

The 14th key word, "suffer", adds up to 75 = 2 x 26 + 23, which gives W, not the printed U. With W
the last cipher letter would be D, not B. See `thouless_1948_suffer_slip.png` and
`harness/wood35t/thouless_example_check.py`.

## Key text

Luther Bible, 1912 text, Matthew 6:9-11: https://www.bibel-online.net/text/luther_1912/matthaeus/6/
The search found it in `bibles/German.xml` of https://github.com/christos-c/bible-corpus.
