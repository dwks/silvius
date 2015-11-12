# Parser, based on John Aycock's SPARK examples

from spark import GenericParser

class CoreParser(GenericParser):
    def __init__(self, start):
        GenericParser.__init__(self, start)

    def typestring(self, token):
        return token.type

    def error(self, token):
        print "Syntax error at `%s' (word number %d)" % (token, token.wordno)
        raise SystemExit

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

class SingleInputParser(CoreParser):
    def __init__(self):
        CoreParser.__init__(self, 'single_input')

    def p_single_input(self, args):
        '''
            single_input ::= END
            single_input ::= chained_commands END
        '''

def parse(tokens):
    parser = SingleInputParser()
    return parser.parse(tokens)
