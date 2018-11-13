
# Introduction

The broad goal of Silvius is to generate keystrokes based on voice
commands. In contrast to more mainstream voice recognition solutions,
the focus of Silvius is to generate commands, rather than perform
transcription of "long-form" speech input. You won't use Silvius to
dictate an e-mail, but on the other hand it is very well suited to
control other applications.

Silvius is an open-ended system: it can generate series of more or
less arbitrary keystroke events based on speech input; and, with the
grammar part being written in Python, it can easily be extended with
new speech input patterns to generate new series of keystrokes.

This works particularly well for keyboard-focused applications, where
you can make Silvius send series of commands to perform complex
manipulations in response to speech commands. Essentially, Silvius
provides "macro" functionality for the application that is in focus. 

As an example, suppose you use "shell" as the "trigger word" for Bash
actions. It's very easy to extend the Silvius grammar to recognize
"shell list", and make it produce the keystroke series ``ls -la
``. For the command "shell change", you could make Silvius produce the
keystroke series ``cd ``.

With your shell in focus, you can then say "shell list slap" to view
the contents of the current directory ("slap" produces an 'enter'
keystroke). Or say "shell change dot dot slap" to go up one directory
level. 

You can do the same thing, for example, for your most frequently used
Git commands, and for frequently used Emacs or Vim commands, etc. In
this way, you build up a repertoire of voice commands that are
applicable across the applications that you use.

Silvius provides a bunch of basics, such as cursor navigation commands
("up", "down", "left", "right"), a command for typing each letter
(like the NATO alphabet), a command for typing numbers ("number two
hundred fifteen") etc. 

Beyond that, you are encouraged to experiment and add your own
commands to the grammar.  This document explains how the grammar
works, to enable you to do just that.

# Silvius structure

Silvius is built up out of two main parts, in a client-server setup:

           client          server

       --> mic in ------------+ 
                              |
                        speech -> text
                              |
       <-- keystrokes --------+

The Silvius git repository contains the code for the client-side
components. The mic-in part is located in the ``stream`` subdirectory,
while the keystrokes part is located in the ``grammar`` subdirectory.

The remainder of this document will concentrate on generating
keystrokes from the transcribed speech.   


Transforming transcribed speech into keystrokes can be broken down in
several steps:

    --> scanner --> parser --> executor --> automator

Briefly, the scanner reads the input and augments it with additional
information. The parser will match the input to grammar rules that we
define, to determine the actions to take for the input. The executor
accepts the actions, and turns them into low-level actions for the
automator. The automator is platform-dependent, and will actually
perform the low-level actions triggered by the executor.

# Scanner & Parser

## Tokens

The scanner produces a list of tokens from the input. In the Silvius
client, a ``Token`` is a simple Python object that contains three
pieces of information (see file ``scan.py``):

* a ``type``
* a ``wordno``
* optional ``extra`` information

The scanner in this project, which takes the input and transforms it
into a list of tokens, is simple. It reads a single line from the
input, splits it in words based on whitespace, and then creates a
``Token`` for each word.

The scanner has a list of keywords; the keywords correspond to words
that have a special meaning in the parser, i.e., words that are
associated with specific actions in the parser. For example, the word
"arch" will be recognized as a letter in the parser, and it will cause
the parser to add a keystroke for the letter "a" to the output.

If the scanner finds a keyword string in the input, the corresponding
``Token`` will have the keyword as its ``type``, and no ``extra`` information.

If the input word is not a keyword, the corresponding ``Token`` will
have the ``ANY`` as its ``type``, and the word will be stored in the
``extra`` information.

In both cases, the ``wordno`` field is filled with a number that
contains the position of the word in the input. 

After all words have been processed, the scanner attaches a special
token with type ``END`` to the token list.

Example:

"charlie delta space word silvius"

will be transformed into the following token list:

    [ Token("charlie", 0), Token("delta", 1),
      Token("space", 2), Token("word", 3),
	  Token("ANY", 4, "silvius") Token("END", 5) ]



## Abstract Syntax Tree

The list of tokens, constructed from the speech input, is then fed
into the Spark parser. The Spark parser will match its set of rules
against the token list, and produce an Abstract Syntax Tree (AST).

In our case, the AST contains commands to be executed by Silvius'
keystroke automator. Here is an example, of the AST tree produced by
parsing the input "charlie delta space word silvius":

    Input words:  charlie  delta  space  word  silvius
    Token types: [charlie, delta, space, word, ANY,    END]
    Resulting AST:
           chain {
               char ['c']
               char ['d']
               raw_char ['space']
               sequence ['silvius']
           }

The AST consists of nodes that are connected together in a tree
structure; this means that AST nodes can have other AST nodes as
*children*. Each node will always have one *parent* node:

                        AST 
                 ____ 'chain' ____
              __/     /     \     \__
         AST      AST       AST       AST
       'char'   'char'  'raw_char'  'sequence'
        'c'      'd'      'space'    'silvius'

Each node in the AST tree is a Python object of type ``AST`` (see file
``ast.py``), which has a ``type``, optional ``meta``information, and a
list of ``children``that are also ``AST``nodes.

``AST``types are different from ``Token`` types: the ``AST`` types
describe the actions that the executor and automator should
perform. These are the different possible action types:

* ``chain``
  Make a chain of keyboard actions. The actions are listed in the AST
  node's ``children``. All actions in the chain will be performed in 
  the order in which they appear in the list.
* ``char``
  The character that will be sent to the automator is the first
  character of the ``meta``-information (``AST.meta[0]``). This type
  is used for "text" characters, i.e. characters that are to appear
  on the screen.
* ``raw_char``
  The character that will be sent to the automator is the first
  character of the ``meta``-information (``AST.meta[0]``). "Raw"
  characters are any "non-text" characters: punctuation marks,
  different styles of parentheses, the "escape" character/key,...
* ``mod_plus_key``
  Insert a modifier+keystroke action in the parse tree. This allows
  you to perform keystrokes like "control-<key>" with one command.
* ``movement``
  This is intended for movement keystrokes, such as the arrow keys or
  page-up/page-down/home/end keys.
* ``sequence``
  Insert a sequence of actions. These actions can be e.g. char or
  raw_char actions. The actions will be performed in the order in 
  which they appear in the AST node's ``children`` list.
* ``word_sequence``
  Insert sequences of space-separated words. The characters in each
  word are sent as individual keystrokes, as if they were ``raw_char``s. 
* ``null``
  No action
* ``repeat``
  Repeat actions. The action(s) to repeat are stored in the AST nodes
  ``children``. The number of times to repeat the action(s) is stored
  in the AST node's ``meta`` information (``AST.meta[0]``).


## Parser implementation

The transformation of a token list into an AST requires two parts:
*rules*, to match the input against; and *code* to manipulate the AST
when a rule matches.

The parser starts at the top level rule; in the example below, we'll
assume this is the rule ``single_command``. (In the real parser, there
are some additional rules, to handle consecutive commands etc. The
start rule in the real parser is ``single_input``.)

The Spark parser uses specially-crafted Python functions to implement
both parts. Here are some examples:

    def p_single_command(self, args):
        '''
            single_command ::= letter
            single_command ::= sky_letter
			<...>
            single_command ::= word_phrase
        '''
        return args[0]

    def p_letter(self, args):
       '''
            letter ::= arch
            letter ::= bravo
            letter ::= charlie
            <...>
            letter ::= xray
            letter ::= expert
            letter ::= yankee
            letter ::= zulu
        '''
        if(args[0].type == 'expert'): args[0].type = 'x'
        return AST('char', [ args[0].type[0] ])

There are two specific things to note about these functions: the
declaration of the rules in the function's docstring, and the code in
the function body that can manipulate the parsing state.

### Rule declaration

First of all, note that the function names are ``p_single_command``and
``p_letter``. The ``p_`` prefix tells Spark that these functions
declare parsing rules. The ``single_command`` and ``letter`` parts
matches the left-hand side of the rule declarations in the function's
docstring.

The docstrings, then, list all the different rules for
``single_command`` and ``letter``. In these two examples, all rules
happen to have a right-hand side that consists of a single terminal.

## Rule matching

Suppose the input is the word "charlie". The parser always starts by
looking for a match for the ``single_input`` rule. The way it does
this is by looking one-by-one at the right-hand sides of the rules
listed in the docstring of the function ``p_single_input``.

The first rule listed in the docstring of ``p_single_input`` has
right-hand side ``letter``. If there would be *no* function
``p_letter`` (with rules ``letter ::= ...`` in its docstring), then
this would produce a match, if the word "letter" would have been the
input, instead of "charlie".

However, since a function ``p_letter`` exists, the parser will look at
that function's doctring. The first rule (right-hand side) in the
docstring is ``arch``. "Arch" does not match "charlie", and there is
also no function ``p_arch`` with "rewrite" rules for ``arch``, so this
is a dead-end. Likewise for ``bravo`` ("charlie" does not match
"bravo", and there is no function ``p_bravo``).

The third ``letter`` rule, with right-hand side ``charlie``, matches
input word "charlie". The parser knows that it can stop matching
there, and that it can start running the function bodies to create the
AST.

The rules matched, in order, are these ones:

    single_input ::= letter
	letter ::= charlie

So the function bodies executed, in reverse order, will be
``p_letter``and ``p_single_input``.

### Function body

The ``p_letter`` function has the following declaration:

    def p_letter(self, args):
        <...>

The ``args`` argument of the function is a list, where the n-th
element corresponds to the n-th symbol (terminal or not) in the
right-hand side of the rule that matched the input.

In our example, where the input is "charlie", the rule that matches is
``letters ::= charlie``.  In this case, ``args[0]`` will contain a
``Token`` for ``charlie``. A ``Token``contains a type; ``charlie`` in
this case.

The function body for ``p_letter`` looks like this:

        if(args[0].type == 'expert'): args[0].type = 'x'
        return AST('char', [ args[0].type[0] ])

In the first line, the token type is checked. If it happens to be
"expert", it is replaced with just "x".

The ``return``statement will return the AST node that will be inserted
in the AST that is the result of the parse. In this case, a ``char``
node is created; the character itself is placed into the AST node's
``type`` field. The actual character is taken from the ``Token``'s
type field; in the example this will be the first letter of "charlie",
i.e. the letter 'c'. 

(This explains the previous line in the function body: the first
letter of "expert" is 'e', but we want to use "expert" to produce 'x'
in the output. So, if we detect "expert", we replace its token type
with 'x', before grabbing the first character of it and inserting it
into the AST node's type. (This is only needed for "expert"; for all
other words, the first letter is actually the one we want to insert in
the output.)   

Going up the stack of rules that matched, we next find ``single_input
::= letter``.  The function body for ``p_single_input`` is simply:

    return args[0]
	
This means that the first element of the argument list is returned
as-is, without additional manipulation. The final AST, in this case,
is then a single AST node:

        AST
       'char'
	    'c'
		
		
# Executor & Automator

## Executor

The executor (in ``execute.py``) walks the AST produced by the parser,
and translates the commands (``chain``, ``raw_char``, ``repeat``,...)
into lower-level commands for the automator.

Similar to the parser, the executor uses function prefix ``n_`` to
designate functions that implement a command:

    def n_chain(self, node):
        <...>

    def n_char(self, node):
        <...>

    <...> 

    def n_repeat(self, node):
       <...>
	   
Depending on the platform, the executor will select a different
automator to generate the actual keystrokes.

## Automator

The automator exists in 3 flavors, for the 3 main operating
systems. The general operating principle for each automator is that it
uses an external, platform-specific tool to generate keystroke
events. The keystrokes are then sent to the application that is in
focus, as if you pressed these keys on the keyboard.

* Linux:

    this implementation uses ``xdotool`` to implement the keystroke
    generation behavior. This tool requires X-windows to be installed.
	
* Windows:

    this implementation uses ``nircmd`` to implement the keystroke
    generation behavior.
	
* Mac OS X:

    this implementation uses ``CLI-Click`` to implement the keystroke
    generation behavior.


