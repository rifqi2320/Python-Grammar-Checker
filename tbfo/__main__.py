import argparse
from tbfo.grammar import CFG
from tbfo.lexer import Lexer
from tbfo.parser.cyk import CYK

args = argparse.ArgumentParser()
args.add_argument("file", help="path to the file input you want to check")
args.add_argument("-t", "--token_file", help="path to the token keyword file")
args.add_argument("-g", "--grammar_file", help="path to the grammar (in CFG) file you want to use")
args.add_argument("-v", "--verbose", help="verbose output", action="store_true")
args = args.parse_args()

lex = Lexer(args.token_file)
grammar = CFG(args.grammar_file)
grammar.to_cnf()
parser = CYK(grammar, args.verbose)

with open(args.file, "r") as f:
    text = f.readlines()
inp = lex.lex_lines(text)
if inp:
    inp = [
        [
            str(line)
            for line in x
        ]
        for x in inp
    ]
    if args.verbose:
        print(' '.join([' '.join(x) for x in inp]))
    res = True
    for i in range(len(inp)):
        res = parser.parse(inp[i])
        if not res:
            print(f'Syntax Error in line: {i+1}')
            print(f'"{text[i].strip()}"')
            break
    if res:
        print("Syntax OK!")
