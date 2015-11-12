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
        node.command = 'key ' + str(node.meta[0])
        self.automator.xdo(node.command)
    def n_movement(self, node):
        node.command = 'key ' + str(node.meta[0]).capitalize()
        self.automator.xdo(node.command)

    def n_repeat(self, node):
        xdo = self.automator.xdo_list[0]
        for n in range(1, 3):
            self.automator.xdo(xdo)
#        node.command = 'for x in `seq 1 ' + str(node.meta[0]) + '`; do ' \
#            + node.children[0].command \
#            + '; done'

    def default(self, node):
#        for child in node.children:
#            self.automator.execute(child.command)
        pass

def execute(ast, real):
    ExecuteCommands(ast, real)
