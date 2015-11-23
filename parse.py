# Parser, based on John Aycock's SPARK examples

from spark import GenericParser
from spark import GenericASTBuilder
from errors import GrammaticalError
from ast import AST

class CoreParser(GenericParser):
    def __init__(self, start):
        GenericParser.__init__(self, start)

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
        if(len(args) == 1):
            return AST('chain', None, [ args[0] ])
        else:
            args[1].children.insert(0, args[0])
            return args[1]

    def p_single_command(self, args):
        '''
            single_command ::= letter
            single_command ::= sky_letter
            single_command ::= movement
            single_command ::= character
        '''
        return args[0]

    def p_movement(self, args):
        '''
            movement ::= up     repeat
            movement ::= down   repeat
            movement ::= left   repeat
            movement ::= right  repeat
        '''
        if args[1] != None:
            return AST('repeat', [ args[1] ], [
                AST('movement', [ args[0] ])
            ])
        else:
            return AST('movement', [ args[0] ])

    def p_repeat(self, args):
        '''
            repeat ::=
            repeat ::= number
        '''
        if len(args) > 0:
            return args[0]
        else:
            return None

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
        # doesn't work right now
        #for v in value:
        #    self.__doc__ += "number ::= " + v
        value = {
            'zero'  : 0,
            'one'   : 1,
            'two'   : 2,
            'three' : 3,
            'four'  : 4,
            'five'  : 5,
            'six'   : 6,
            'seven' : 7,
            'eight' : 8,
            'nine'  : 9
        }
        return value[args[0].type]

    def p_sky_letter(self, args):
        '''
            sky_letter ::= sky letter
        '''
        ast = args[1]
        ast.meta[0] = ast.meta[0].upper()
        return ast

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
        return AST('char', [ args[0].type[0] ])

    def p_character(self, args):
        '''
            character ::= act
            character ::= slap
            character ::= colon
            character ::= single quote
            character ::= double quote
            character ::= equal
        '''
        value = {
            'act'   : 'Escape',
            'slap'  : 'Return',
            'colon' : 'colon',
            'single': 'apostrophe',
            'double': 'quotedbl'
        }
        return AST('raw_char', [ value[args[0].type] ])

class SingleInputParser(CoreParser):
    def __init__(self):
        CoreParser.__init__(self, 'single_input')

    def p_single_input(self, args):
        '''
            single_input ::= END
            single_input ::= chained_commands END
        '''
        if len(args) > 0:
            return args[0]
        else:
            return AST('')

def parse(tokens):
    parser = SingleInputParser()
    return parser.parse(tokens)
