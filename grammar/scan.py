import re

class Token:
    def __init__(self, type, wordno=-1):
        self.type = type
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
        tokens.append(Token(t, wordno))
    tokens.append(Token('END'))
    print tokens
    return tokens
