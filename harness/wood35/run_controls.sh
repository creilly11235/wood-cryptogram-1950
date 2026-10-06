#!/bin/sh
# the English-only search (17 September 2026): gate first, then nulls.  The real ciphertext is NOT touched here --
# the kill criterion in PREREG.md section 8 requires the gate to pass first.
cd "$(dirname "$0")/../.."
python3 harness/wood35/run_gate.py > harness/wood35/out_gate.txt 2> harness/wood35/err_gate.txt
echo "GATE DONE rc=$?"
python3 harness/wood35/run_null.py > harness/wood35/out_null.txt 2> harness/wood35/err_null.txt
echo "NULL DONE rc=$?"
