"""Independent verifier for T. E. Wood's 1950 cryptogram (#35 of Schmeh's Top 50).

Ciphertext (Schmeh, Cipherbrain, 17 Apr 2017): FVAMI NTKFX XWATB OIZVV X
Key text: Matthew 6:9-11, Luther Bible 1912, from "Unser Vater" -- the Lord's Prayer --
as printed by bibel-online.net (luther_1912/matthaeus/6) and BibleGateway (LUTH1545 text):
    9  Darum sollt ihr also beten: Unser Vater in dem Himmel! Dein Name werde geheiligt.
    10 Dein Reich komme. Dein Wille geschehe auf Erden wie im Himmel.
    11 Unser täglich Brot gib uns heute.
Method (Thouless's, as recovered by Richard Bean for Message B, harness/verify_thouless_b.py):
consecutive DISTINCT words (repeats skipped), accents folded (ä -> a), each word's letter sum
A=1..Z=26, shift = (sum - 1) mod 26, plaintext = ciphertext - shift.
No repository code is imported."""
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
    return "".join(chr((ord(c) - 65 - shift(w, minus_one)) % 26 + 65) for c, w in zip(ct, key))

def encrypt(pt, key, minus_one=True):
    return "".join(chr((ord(c) - 65 + shift(w, minus_one)) % 26 + 65) for c, w in zip(pt, key))

if __name__ == "__main__":
    key = keyseq(KEY, len(CT))
    pt = decrypt(CT, key)
    print("key words :", " ".join(key))
    print("shifts    :", [shift(w) for w in key])
    print("ciphertext:", CT)
    print("plaintext :", pt)
    assert pt == EXPECTED, pt
    assert encrypt(pt, key) == CT
    print("re-encryption matches the published ciphertext exactly")
    print("reading   : HIER BIN ICH (German: here am I) / TOTSIENS (Afrikaans: goodbye) / T. E. W.")
    # controls: how specific deviations change the reading
    print("control, all words (no dedup)   :", decrypt(CT, keyseq(KEY, 21, distinct=False)))
    print("control, shift = sum mod 26     :", decrypt(CT, key, minus_one=False))
    print("control, liturgical wording     :", decrypt(CT, keyseq("Vater unser im Himmel, geheiligt werde dein Name. Dein Reich komme. Dein Wille geschehe, wie im Himmel so auf Erden. Unser tägliches Brot gib uns heute. Und vergib uns unsere Schuld", 21)))
    print("control, Thouless B text (Hound):", decrypt(CT, keyseq("I fled Him, down the nights and down the days; I fled Him, down the arches of the years; I fled Him, down the labyrinthine ways Of my own mind; and in the mist of tears I hid from Him, and under running laughter. Up vistaed hopes I sped", 21)))
    sys.exit(0)
