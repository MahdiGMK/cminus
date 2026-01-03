cp phase2-tests/T$1/input.txt input.txt
python parser.py
delta syntax_error.txt phase2-tests/T$1/syntax_errors.txt
delta parse_tree.txt phase2-tests/T$1/parse_tree.txt
