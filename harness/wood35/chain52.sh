#!/bin/sh
# Round 52: gate first, then nulls.  The real ciphertext is NOT touched here --
# the kill criterion in PREREG_R52.md section 8 requires the gate to pass first.
cd "$(dirname "$0")/../.."
python3 harness/wood35/run_gate.py > harness/wood35/out_gate_r52.txt 2> harness/wood35/err_gate_r52.txt
echo "GATE DONE rc=$?"
python3 harness/wood35/run_null.py > harness/wood35/out_null_r52.txt 2> harness/wood35/err_null_r52.txt
echo "NULL DONE rc=$?"
