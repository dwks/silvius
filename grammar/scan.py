# Lexer that produces a sequence of tokens (keywords + ANY).

import re
from lm import get_terminals

def find_keywords(parser):
    global keywords
    keywords = get_terminals(parser)
    global noise
    noise = set([x.lower() for x in ['[BREATH]', '[COUGH]', '[NOISE]', \
        '[SMACK]', '[UH]', '[UM]', '<unk>']])

class Token:
    def __init__(self, type, wordno=-1, extra=''):
        self.type = type
        self.extra = extra
        self.wordno = wordno

    def __cmp__(self, o):
        return cmp(self.type, o)
    def __repr__(self):
        return str(self.type)

def scan(line):
    tokens = []
    wordno = 0
    for t in line.lower().split():
        wordno += 1
        if(t in keywords):
            tokens.append(Token(t, wordno))
        elif(t in noise):
            pass
        else:
            tokens.append(Token('ANY', wordno, t))
    tokens.append(Token('END'))
    print tokens
    return tokens
