# Parser, based on John Aycock's SPARK examples

from spark import GenericParser
from spark import GenericASTBuilder
from errors import GrammaticalError
from ast import AST

class CoreParser(GenericASTBuilder):
    def __init__(self, ast, start):
        GenericASTBuilder.__init__(self, ast, start)

    def typestring(self, token):
        return token.type

    def error(self, token):
        raise GrammaticalError(
            "Unexpected token `%s' (word number %d)" % (token, token.wordno))

    def p_chained_commands(self, args):
        '''
            chained_commands ::= single_command
            chained_commands ::= single_command chained_commands
        '''

    def p_single_command(self, args):
        '''
            single_command ::= letter
            single_command ::= movement
        '''

    def p_movement(self, args):
        '''
            movement ::= up     repeat
            movement ::= down   repeat
            movement ::= left   repeat
            movement ::= right  repeat
        '''

    def p_repeat(self, args):
        '''
            repeat ::=
            repeat ::= number
        '''

    def p_number(self, args):
        '''
            number ::= zero
            number ::= one
            number ::= two
            number ::= three
            number ::= four
            number ::= five
            number ::= six
            number ::= seven
            number ::= eight
            number ::= nine
        '''
        return args[0] + "##"

    def p_letter(self, args):
        '''
            letter ::= arch
            letter ::= bravo
            letter ::= charlie
            letter ::= delta
            letter ::= echo
            letter ::= fox
            letter ::= golf
            letter ::= hotel
            letter ::= india
            letter ::= julia
            letter ::= kilo
            letter ::= line
            letter ::= mike
            letter ::= november
            letter ::= oscar
            letter ::= papa
            letter ::= queen
            letter ::= romeo
            letter ::= sierra
            letter ::= tango
            letter ::= uniform
            letter ::= victor
            letter ::= whiskey
            letter ::= xray
            letter ::= yankee
            letter ::= zulu
        '''

    def terminal(self, token):
        return AST(token)
        #return GenericASTBuilder.terminal(self, type)

    def nonterminal(self, type, args):
        #print 'NT (', type, args, ')'
        #return AST(type, args)
        return GenericASTBuilder.nonterminal(self, type, args)

class SingleInputParser(CoreParser):
    def __init__(self):
        CoreParser.__init__(self, AST, 'single_input')

    def p_single_input(self, args):
        '''
            single_input ::= END
            single_input ::= chained_commands END
        '''

def parse(tokens):
    parser = SingleInputParser()
    return parser.parse(tokens)
