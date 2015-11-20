# Generate language model

from scan import scan
from parse import parse
from parse import SingleInputParser
from copy import deepcopy

def find_terminals(rules, visited, which, found):
    if which in visited: return
    visited[which] = 1

    for r in rules[which]:
        (name, tokens) = r
        for t in tokens:
            if t in rules:
                find_terminals(rules, visited, t, found)
            elif t != 'END' and t != '|-':
                found.append(t)

def find_sequences(rules, visited, which, found=[], level=0):
    if which in visited and visited[which]: return
    visited[which] = 1

    for r in rules[which]:
        (name, tokens) = r
        new_level = level
        new_found = deepcopy(found)
        for t in tokens:
            if t in rules:
                find_sequences(rules, visited, t, new_found, new_level)
            elif t != 'END' and t != '|-':
                if len(new_found) <= new_level: new_found.append([])
                new_found[new_level].append(t)
                new_level += 1
        #print new_found
    visited[which] = 0

def build_n_grams(rules, n_max):
    gram = [{}]
    for n in range(1, n_max+1):
        gram.append({})
        # leaf rules
        for which in rules:
            gram[n][which] = []
            for r in rules[which]:
                (name, tokens) = r
                fragment = []
                for t in tokens:
                    if t in rules:
                        if len(fragment) > 0 and n - len(fragment) > 0:
                            for q in gram[n - len(fragment)][t]:
                                qq = fragment[:]
                                qq.extend(q)
                                gram[n][which].append(qq)
                        #pass
                    elif t != 'END' and t != '|-':
                        fragment.append(t)
                if len(fragment) == n:
                    gram[n][which].append(fragment)

        # self-recursion
        for which in rules:
            for r in rules[which]:
                (name, tokens) = r
                if which in tokens:
                    for i in range(1, n):
                        for q in gram[n - i][which]:
                            for z in gram[i][which]:
                                qq = q[:]
                                qq.extend(z)
                                if qq not in gram[n][which]:
                                    gram[n][which].append(qq)
                    break

        # propagate to other rules (left recursion)
        for which in rules:
            for r in rules[which]:
                (name, tokens) = r
                fragment = []
                for t in tokens:
                    if t == which: continue
                    if t in rules:
                        if n - len(fragment) > 0:
                            for q in gram[n - len(fragment)][t]:
                                qq = fragment[:]
                                qq.extend(q)
                                if qq not in gram[n][which]:
                                    gram[n][which].append(qq)
                    elif t != 'END' and t != '|-':
                        fragment.append(t)
    #print gram
    for g in gram[n]:
        for seq in gram[n][g]:
            for word in seq:
                print word,
            print

def make_lm(rules, visited, which, prefix):
    if which in visited: return
    visited[which] = 1

    new_prefix = prefix[:]

    for r in rules[which]:
        (name, tokens) = r
        for t in tokens:
            if t in rules:
                make_lm(rules, visited, t, new_prefix)
            elif t != 'END' and t != '|-':
                print prefix, t
                new_prefix.append(t)

if __name__ == '__main__':
    import sys
    parser = SingleInputParser()
    #for rule in parser.rules:
    #    print rule, parser.rules[rule]

    visited = {}
    #make_lm(parser.rules, visited, 'START', [])
    terminals = []
    find_terminals(parser.rules, visited, 'START', terminals)
    #print terminals

    visited = {}
    find_sequences(parser.rules, visited, 'START')

    build_n_grams(parser.rules, int(sys.argv[1]))

