"""Check the Wood convention against Thouless's own printed worked example (Proc. SPR 48,
1948, pp. 259-260; page image research/incoming/wood35_primary/thouless_1948_suffer_slip.png):
key passage "To be or not [to be], that is the question. Whether 'tis nobler in [the] mind
[to] suffer", plaintext THERE IS NO DEATH; printed key letters IGGWW BG PI VNWNU, printed
ciphertext BNKNA JYCWY RWGB.  The convention reproduces letters 1-13 exactly; for letter 14
the key word SUFFER sums to 75 = 2*26 + 23 -> W, whereas Thouless printed U: his own
arithmetic slip, visible in the page image (not an OCR error)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_wood import keyseq, encrypt, shift
k = keyseq("To be or not to be, that is the question. Whether 'tis nobler in the mind to suffer", 14)
keyl = ''.join(chr(shift(w) + 65) for w in k)
ct = encrypt('THEREISNODEATH', k)
print('key words  :', ' '.join(k))
print('key letters:', keyl, '| printed: IGGWWBGPIVNWNU')
print('ciphertext :', ct, '| printed: BNKNAJYCWYRWGB')
assert keyl[:13] == 'IGGWWBGPIVNWN' and ct[:13] == 'BNKNAJYCWYRWG'
assert sum(ord(c) - 64 for c in 'SUFFER') == 75 and keyl[13] == 'W'
print('letters 1-13 match the printed example; letter 14 differs by Thouless\'s slip (SUFFER = 75 -> W, printed U)')
