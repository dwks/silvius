# Main file. Parse new commands from stdin until EOF.

from scan import find_keywords
from scan import scan
from parse import parse
from parse import GrammaticalError
from parse import SingleInputParser
from execute import execute
from ast import printAST

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        f = open(filename)
    else:
        f = sys.stdin

    parser = SingleInputParser()
    find_keywords(parser)  # init lexer

    while True:
        line = f.readline()
        if line == '': break
        if line == '\n': continue

        print ">", line,
        try:
            ast = parse(parser, scan(line))
            printAST(ast)
            execute(ast, f == sys.stdin)
        except GrammaticalError as e:
            print "Error:", e

    if f != sys.stdin:
        f.close()

    print 'ok'
