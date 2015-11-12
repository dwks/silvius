from copy import deepcopy

class AST:
    def __init__(self, command, children = []):
        self.command = command
        self.children = deepcopy(children)  # or just set to []

    def __repr__(self):
        return "`" + str(self.command) + "`"

    def __getitem__(self, i): 
        return self.children[i]
    def __len__(self):
        return len(self.children)
    def __setslice__(self, low, high, seq):
        self.children[low:high] = seq 
    def __cmp__(self, o): 
        return cmp(self.command, o)

def printAST(ast, level=0):
    if level > 10: return

    print '    ' * level,
    if len(ast) > 0:
        print ast, '{'
        for child in ast:
            printAST(child, level + 1)
        print '    ' * level, '}'
    else:
        print ast
