# Lexer that produces a sequence of tokens (keywords + ANY).

import re

keywords = [
    'act',
    'alternative',
    'ampersand',
    'arch',
    'backslash',
    'bang',
    'bravo',
    'carrot',
    'charlie',
    'colon',
    'control',
    'delta',
    'dollar',
    'dot',
    'down',
    'echo',
    'eco',
    'eight',
    'equal',
    'expert',
    'five',
    'four',
    'fox',
    'golf',
    'hash',
    'hotel',
    'india',
    'julia',
    'kilo',
    'late',
    'left',
    'line',
    'mike',
    'minus',
    'nine',
    'november',
    'one',
    'oscar',
    'papa',
    'percent',
    'plus',
    'phrase',
    'queen',
    'question',
    'rate',
    'right',
    'romeo',
    'scratch',
    'sentence',
    'seven',
    'sierra',
    'six',
    'sky',
    'slap',
    'slash',
    'space',
    'star',
    'tab',
    'tango',
    'three',
    'two',
    'underscore',
    'uniform',
    'up',
    'victor',
    'whiskey',
    'whisky',
    'word',
    'xray',
    'yankee',
    'zero',
    'zulu'
]

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
        else:
            tokens.append(Token('ANY', wordno, t))
    tokens.append(Token('END'))
    print tokens
    return tokens
