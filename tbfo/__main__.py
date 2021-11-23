import argparse
from tbfo.grammar import CFG
from tbfo.lexer import Lexer
from tbfo.parser.cyk import cyk

args = argparse.ArgumentParser()
args.add_argument("file", help="path to the file input you want to check")
args.add_argument("-t", "--token_file", help="path to the token keyword file")
args.add_argument("-g", "--grammar_file", help="path to the grammar (in CFG) file you want to use")
args.add_argument("-v", "--verbose", help="verbose output", action="store_true")
args = args.parse_args()

lex = Lexer(args.token_file)
grammar = CFG(args.grammar_file)
grammar.to_cnf()
vars, terms = grammar.get_cyk_form

with open(args.file, "r") as f:
    text = f.readlines()
res = lex.lex_lines(text)
if res:
    res = ' '.join([
        str(line)
        for x in res
        for line in x
    ]).split(' NL ')
    res = [
        x + ' NL' if x != 'NL' else x
        for x in res
    ]
    res = [
        x.split(' ')
        for x in res
    ]
    print(res)
    for line in res:
        cyk(vars, terms, line, args.verbose)
