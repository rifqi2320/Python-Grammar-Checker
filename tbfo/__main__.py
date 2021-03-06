import argparse
import time
from tbfo.grammar import CFG
from tbfo.lexer import Lexer
from tbfo.parser.cyk import CYK

args = argparse.ArgumentParser()
args.add_argument("file", help="path to the file input you want to check")
args.add_argument("-t", "--token_file", help="path to the token keyword file")
args.add_argument("-g", "--grammar_file", help="path to the grammar (in CFG) file you want to use")
args.add_argument("-v", "--verbose", help="verbose output", action="store_true")
args.add_argument("-st", "--show_table", help="show CYK table generation", action="store_true")
args.add_argument("-ni", "--no_indent", help="disable indentation check", action="store_true")
args = args.parse_args()

lex = Lexer(args.token_file)
grammar = CFG(args.grammar_file)
grammar.to_cnf()
parser = CYK(grammar, args.show_table)

with open(args.file, "r") as f:
    text = f.readlines()
start_time = time.perf_counter_ns()
if args.verbose:
    print("Change input into tokens by passing it in lexer...")
inp = lex.lex_lines(text, not args.no_indent)
if inp:
    inp = [
        [
            str(line)
            for line in x
        ]
        for x in inp
    ]
    if args.verbose:
        print("Tokenized input:")
        print(' '.join([' '.join(x) for x in inp]))
        print("Checking syntax... (line 1)")
    res = True
    for i in range(len(inp)):
        res = parser.parse(inp[i])
        if not res:
            print(f'Syntax Error in line: {i+1}')
            print(f'"{text[i].strip()}"')
            break
        else:
            if args.verbose and i != len(inp) - 1:
                print(f"Checking syntax... (line {i+2})")
    if res:
        print("Syntax OK!")

print(f"Time: {((time.perf_counter_ns() - start_time) * 0.000001):.2f} ms")
