from spark import GenericASTTraversal
from automator import Automator

class ExecuteCommands(GenericASTTraversal):
    def __init__(self, ast, real = True):
        GenericASTTraversal.__init__(self, ast)
        self.output = []
        self.automator = Automator(real)

        self.postorder()
        self.automator.flush()

    def n_char(self, node):
        self.automator.key(node.meta[0])
    def n_raw_char(self, node):
        self.automator.raw_key(node.meta[0])
    def n_movement(self, node):
        self.automator.key(node.meta[0].type)
    def n_sequence(self, node):
        for c in node.meta[0]:
            self.automator.raw_key(c)

    def n_repeat(self, node):
        xdo = self.automator.xdo_list[-1]
        for n in range(1, node.meta[0]):
            self.automator.xdo(xdo)

    def default(self, node):
#        for child in node.children:
#            self.automator.execute(child.command)
        pass

def execute(ast, real):
    ExecuteCommands(ast, real)
