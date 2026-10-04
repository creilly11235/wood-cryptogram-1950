"""Standalone verifier for a proposed solution of T. E. Wood's 1950 cryptogram.

Ciphertext: FVAMI NTKFX XWATB OIZVV X
Ciphertext and instructions: T. E. Wood, "A Further Test for Survival",
Proceedings of the Society for Psychical Research 49 (1950), pp. 105-106.
Method: R. H. Thouless, "A Test of Survival",
Proceedings of the Society for Psychical Research 48 (1948), pp. 258-260.

Key wording: the Lord's Prayer, Luther Bible 1912 text as displayed at
https://www.bibel-online.net/text/luther_1912/matthaeus/6/
Start at "Unser Vater" in Matthew 6:9b. The first 21 distinct words end
at "uns" in Matthew 6:11; "heute" is not used.
The matching wording does not identify Wood's physical book or edition.

Omit second and later occurrences of words; split hyphenated words.
Sum A=1 through Z=26; zero-based Vigenere shift = (sum - 1) % 26.
Subtract that shift from the ciphertext letter.
Normalization used here: uppercase, fold diacritics, and extract A-Z words.
In particular, a with diaeresis becomes A; the papers do not specify this.

This checks the proposed arithmetic, not uniqueness or historical intent.
Python 3.6+; standard library only; no other files are required.
"""
import unicodedata, re, sys

CT = "FVAMI NTKFX XWATB OIZVV X".replace(" ", "")
KEY = ("Unser Vater in dem Himmel! Dein Name werde geheiligt. Dein Reich komme. "
       "Dein Wille geschehe auf Erden wie im Himmel. Unser täglich Brot gib uns heute.")
EXPECTED = "HIERBINICHTOTSIENSTEW"

def words(text):
    t = unicodedata.normalize("NFKD", text)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.findall(r"[A-Z]+", t.upper())

def keyseq(text, n, distinct=True):
    out, seen = [], set()
    for w in words(text):
        if distinct and w in seen:
            continue
        seen.add(w); out.append(w)
        if len(out) == n:
            return out
    raise ValueError("key text too short")

def shift(w, minus_one=True):
    s = sum(ord(c) - 64 for c in w)
    return (s - 1) % 26 if minus_one else s % 26

def decrypt(ct, key, minus_one=True):
    if len(ct) != len(key):
        raise ValueError("one key word is required per message letter")
    return "".join(chr((ord(c) - 65 - shift(w, minus_one)) % 26 + 65) for c, w in zip(ct, key))

def encrypt(pt, key, minus_one=True):
    if len(pt) != len(key):
        raise ValueError("one key word is required per message letter")
    return "".join(chr((ord(c) - 65 + shift(w, minus_one)) % 26 + 65) for c, w in zip(pt, key))

if __name__ == "__main__":
    key = keyseq(KEY, len(CT))
    pt = decrypt(CT, key)
    print("key words :", " ".join(key))
    print("shifts    :", [shift(w) for w in key])
    print("ciphertext:", CT)
    print("plaintext :", pt)
    if pt != EXPECTED:
        raise SystemExit("FAIL: unexpected plaintext: " + pt)
    if encrypt(pt, key) != CT:
        raise SystemExit("FAIL: re-encryption differs from the ciphertext")
    print("verified  : plaintext matches; re-encryption matches the published ciphertext exactly")
    print("proposed reading: HIER BIN ICH (German: here I am) / TOTSIENS (Afrikaans: goodbye) / T. E. W. (Wood's initials)")
    # Sensitivity examples on Wood's ciphertext, not statistical tests.
    print("control, all words (no dedup)   :", decrypt(CT, keyseq(KEY, 21, distinct=False)))
    print("control, shift = sum mod 26     :", decrypt(CT, key, minus_one=False))
    print("control, liturgical wording     :", decrypt(CT, keyseq("Vater unser im Himmel, geheiligt werde dein Name. Dein Reich komme. Dein Wille geschehe, wie im Himmel so auf Erden. Unser tägliches Brot gib uns heute. Und vergib uns unsere Schuld", 21)))
    print("alternative key, Hound of Heaven, applied to Wood:", decrypt(CT, keyseq("I fled Him, down the nights and down the days; I fled Him, down the arches of the years; I fled Him, down the labyrinthine ways Of my own mind; and in the mist of tears I hid from Him, and under running laughter. Up vistaed hopes I sped", 21)))
    sys.exit(0)
