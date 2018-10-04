# Low-level execution of AST commands using xdotool.

import os, platform
from spark import GenericASTTraversal
from automators import XDoAutomator, CLIClickAutomator, NirCmdAutomator

class ExecuteCommands(GenericASTTraversal):
    def __init__(self, ast, real = True):
        GenericASTTraversal.__init__(self, ast)
        self.output = []
        
        if 'Linux' in platform.system():
            self.automator = XDoAutomator(real)
        elif 'Darwin' in platform.system():
            self.automator = CLIClickAutomator(real)
        elif 'Windows' in platform.system():
            self.automator = NirCmdAutomator(real)
        else:
            print "No suitable automator for platform", platform.system()

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
        self.automator.key_movement(node.meta[0].type)
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
        char_list = self.automator.char_list[-1]
        for n in range(1, node.meta[0]):
            self.automator.add_keystrokes(char_list)

    def default(self, node):
        pass


def execute(ast, real):
    ExecuteCommands(ast, real)
