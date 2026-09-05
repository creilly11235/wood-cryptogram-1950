"""Fully reproduce Richard Bean's 2019 decryption of Thouless Message B.

Key: Francis Thompson, The Hound of Heaven, starting 'I fled Him, down'.
Source: the already tracked Gutenberg text data/keytexts/41215.txt.
This is a known-answer reproduction, not a new cryptanalytic discovery.
Uses only the Python standard library; run from any working directory.
"""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = "A number of successful experiments of this kind would give strong evidence for survival"


def key_words(text, count):
    start = text.index("I fled Him, down")
    text = unicodedata.normalize("NFKD", text[start:])
    text = "".join(c for c in text if not unicodedata.combining(c))
    # Hyphens/dashes separate words; accents stay inside the word after folding.
    # In particular: chasmèd -> CHASMED, unperturbèd -> UNPERTURBED,
    # beat--and -> BEAT AND, outlaw-wise -> OUTLAW WISE.
    words = list(dict.fromkeys(re.findall(r"[A-Z]+", text.upper())))
    if len(words) < count:
        raise ValueError("Key text is too short")
    return words[:count]


def shifts(words):
    # Sum word letters as A=1..Z=26, then convert the resulting key letter
    # to a zero-based Vigenere shift. The -1 is essential (first key is I=8).
    return [(sum(ord(c)-64 for c in word)-1) % 26 for word in words]


def crypt(text, key, decrypt=False):
    if len(text) != len(key):
        raise ValueError("One key word is required per message letter")
    sign = -1 if decrypt else 1
    return "".join(chr(65+(ord(c)-65+sign*k) % 26) for c, k in zip(text, key))


def verify():
    source = ROOT / "harness/data/keytexts/41215.txt"
    data = json.loads((ROOT / "ciphers/thouless_b_35_SOLVED.json").read_text())
    ciphertext = re.sub(r"[^A-Z]", "", data["text"].upper())
    words = key_words(source.read_text(encoding="utf-8"), len(ciphertext))
    key = shifts(words)
    plaintext = crypt(ciphertext, key, decrypt=True)
    assert plaintext == re.sub(r"[^A-Z]", "", EXPECTED.upper())
    assert crypt(plaintext, key) == ciphertext
    # Detect accidental loss of accented letters or accidental token joining.
    assert words[33] == "CHASMED" and words[45] == "UNPERTURBED"
    assert words[66:68] == ["OUTLAW", "WISE"]
    return {"attribution": "Richard Bean, 2019; independently reproduced here",
            "plaintext": EXPECTED, "letters": len(ciphertext),
            "ciphertext": ciphertext, "reencryption_matches": True,
            "source": "https://www.gutenberg.org/ebooks/41215",
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "key_words": words, "zero_based_shifts": key}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
