# Low-level execution of AST commands using xdotool.

import os
from spark import GenericASTTraversal

class ExecuteCommands(GenericASTTraversal):
    def __init__(self, ast, real = True):
        GenericASTTraversal.__init__(self, ast)
        self.output = []
        self.automator = Automator(real)

        self.postorder_flat()
        self.automator.flush()

    # a version of postorder which does not visit children recursively
    def postorder_flat(self, node=None):
        if node is None:
            node = self.ast

        #for kid in node:
        #    self.postorder(kid)

        name = 'n_' + self.typestring(node)
        if hasattr(self, name):
            func = getattr(self, name)
            func(node)
        else:
            self.default(node)

    def n_chain(self, node):
        for n in node.children:
            self.postorder_flat(n)
    def n_char(self, node):
        self.automator.key(node.meta[0])
    def n_raw_char(self, node):
        self.automator.raw_key(node.meta[0])
    def n_mod_plus_key(self, node):
        self.automator.mod_plus_key(node.meta, node.children[0].meta[0])
    def n_movement(self, node):
        self.automator.key(node.meta[0].type)
    def n_sequence(self, node):
        for c in node.meta[0]:
            self.automator.raw_key(c)
    def n_word_sequence(self, node):
        n = len(node.children)
        for i in range(0, n):
            word = node.children[i].meta
            for c in word:
                self.automator.raw_key(c)
            if(i + 1 < n):
                self.automator.raw_key('space')
    def n_null(self, node):
        pass

    def n_repeat(self, node):
        self.postorder_flat(node.children[0])
        xdo = self.automator.xdo_list[-1]
        for n in range(1, node.meta[0]):
            self.automator.xdo(xdo)

    def default(self, node):
        pass

class Automator:
    def __init__(self, real = True):
        self.xdo_list = []
        self.real = real

    def xdo(self, xdo):
        self.xdo_list.append(xdo)

    def flush(self):
        if len(self.xdo_list) == 0: return

        command = '/usr/bin/xdotool' + ' '
        command += ' '.join(self.xdo_list)
        self.execute(command)
        self.xdo_list = []

    def execute(self, command):
        if command == '': return

        print "`%s`" % command
        if self.real:
            os.system(command)

    def raw_key(self, k):
        if(k == "'"): k = 'apostrophe'
        elif(k == '.'): k = 'period'
        elif(k == '-'): k = 'minus'
        self.xdo('key ' + k)
    def key(self, k):
        if(len(k) > 1): k = k.capitalize()
        self.xdo('key ' + k)
    def mod_plus_key(self, mods, k):
        command = 'key '
        command += '+'.join(mods)
        if(len(k) > 1 and k != 'plus' and k != 'apostrophe' and k != 'period' and k != 'minus'): k = k.capitalize()
        command += '+' + k
        self.xdo(command)

def execute(ast, real):
    ExecuteCommands(ast, real)
