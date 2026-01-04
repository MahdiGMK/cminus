#!/bin/bash
if [ $# -eq 1 ]; then
  j="$1"
  cp "phase2-tests/T$j/input.txt" input.txt
  python compiled_parser.py
  diff -bBq syntax_error.txt "phase2-tests/T$j/syntax_errors.txt"
  diff -bBq parse_tree.txt "phase2-tests/T$j/parse_tree.txt"
else
  for ((i=1; i<=10; i++)); do
    if [ "$i" -lt 10 ]; then
      j="0$i"
    else
      j="$i"
    fi
    cp "phase2-tests/T$j/input.txt" input.txt
    python compiled_parser.py
    diff -bBq syntax_error.txt "phase2-tests/T$j/syntax_errors.txt"
    diff -bBq parse_tree.txt "phase2-tests/T$j/parse_tree.txt"
  done
fi
