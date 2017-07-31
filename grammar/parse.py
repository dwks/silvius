# Parser, based on John Aycock's SPARK examples

from spark import GenericParser
from spark import GenericASTBuilder
from ast import AST

class GrammaticalError(Exception):
    def __init__(self, string):
        self.string = string
    def __str__(self):
        return self.string

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
            single_command ::= number_rule
            single_command ::= movement
            single_command ::= character
            single_command ::= editing
            single_command ::= modifiers
            single_command ::= english
            single_command ::= word_sentence
            single_command ::= word_phrase
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
            repeat ::= _number
        '''
        if len(args) > 0:
            return args[0]
        else:
            return None

    def p_number_rule(self, args):
        '''
            number_rule ::= number _number
        '''
        return AST('char', [ chr(ord('0') + args[1]) ])

    def p__number(self, args):
        '''
            _number ::= zero
            _number ::= one
            _number ::= two
            _number ::= three
            _number ::= four
            _number ::= five
            _number ::= six
            _number ::= seven
            _number ::= eight
            _number ::= nine
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
            letter ::= eco
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
            letter ::= whisky
            letter ::= xray
            letter ::= expert
            letter ::= yankee
            letter ::= zulu
        '''
        if(args[0].type == 'expert'): args[0].type = 'x'
        return AST('char', [ args[0].type[0] ])

    def p_character(self, args):
        '''
            character ::= act
            character ::= colon
            character ::= semicolon
            character ::= single quote
            character ::= double quote
            character ::= equal
            character ::= space
            character ::= tab
            character ::= bang
            character ::= hash
            character ::= dollar
            character ::= percent
            character ::= carrot
            character ::= ampersand
            character ::= star
            character ::= late
            character ::= rate
            character ::= minus
            character ::= underscore
            character ::= plus
            character ::= backslash
            character ::= dot
            character ::= dit
            character ::= slash
            character ::= question
            character ::= comma
        '''
        value = {
            'act'   : 'Escape',
            'colon' : 'colon',
            'semicolon' : 'semicolon',
            'single': 'apostrophe',
            'double': 'quotedbl',
            'equal' : 'equal',
            'space' : 'space',
            'tab'   : 'Tab',
            'bang'  : 'exclam',
            'hash'  : 'numbersign',
            'dollar': 'dollar',
            'percent': 'percent',
            'carrot': 'caret',
            'ampersand': 'ampersand',
            'star': 'asterisk',
            'late': 'parenleft',
            'rate': 'parenright',
            'minus': 'minus',
            'underscore': 'underscore',
            'plus': 'plus',
            'backslash': 'backslash',
            'dot': 'period',
            'dit': 'period',
            'slash': 'slash',
            'question': 'question',
            'comma': 'comma'
        }
        return AST('raw_char', [ value[args[0].type] ])

    def p_editing(self, args):
        '''
            editing ::= slap        repeat
            editing ::= scratch     repeat
        '''
        value = {
            'slap'  : 'Return',
            'scratch': 'BackSpace'
        }
        if args[1] != None:
            return AST('repeat', [ args[1] ], [
                AST('raw_char', [ value[args[0].type] ])
            ])
        else:
            return AST('raw_char', [ value[args[0].type] ])

    def p_modifiers(self, args):
        '''
            modifiers ::= control single_command
            modifiers ::= alt single_command
            modifiers ::= alternative single_command
        '''
        value = {
            'control' : 'ctrl',
            'alt' : 'alt',
            'alternative' : 'alt'
        }
        return AST('mod_plus_key', [ value[args[0].type], args[1].meta[0] ])

    def p_english(self, args):
        '''
            english ::= word ANY
        '''
        return AST('sequence', [ args[1].extra ])

    def p_word_sentence(self, args):
        '''
            word_sentence ::= sentence word_repeat
        '''
        if(len(args[1].children) > 0):
            args[1].children[0].meta = args[1].children[0].meta.capitalize()
        return args[1]

    def p_word_phrase(self, args):
        '''
            word_phrase ::= phrase word_repeat
        '''
        return args[1]

    def p_word_repeat(self, args):
        '''
            word_repeat ::= ANY
            word_repeat ::= ANY word_repeat
        '''
        if(len(args) == 1):
            return AST('word_sequence', None,
                [ AST('null', args[0].extra) ])
        else:
            args[1].children.insert(0, AST('null', args[0].extra))
            return args[1]

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

def parse(parser, tokens):
    return parser.parse(tokens)
