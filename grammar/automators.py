# Low-level execution of AST commands using xdotool.

import os, string
import scan

class Automator:
    def __init__(self, real = True):
        self.char_list = []
        self.real = real

    def add_keystrokes(self, keystrokes):
        self.char_list.append(keystrokes)

    def execute(self, command):
        if command == '': return

        print "`%s`" % command
        if self.real:
            os.system(command)

    def key(self, k):
        """ add keystrokes to the list. The first character will be capitalized. """
        if(len(k) > 1): k = k.capitalize()
        self.key_nocaps(k)

    # abstract methods
    def flush(self):
        """ send the keystroke list in char_list to the OS/keystroke tool """
        pass

    def raw_key(self, k):
        """ add a 'raw' keystroke to the list. see parse.py for which
            keystrokes to support (CoreParser.p_character(), CoreParser.p_editing()) """ 
        pass
    
    def key_movement(self, k):
        """ add keystrokes to the list for up, down, left, right arrows, and
            page up/page down. """
        pass

    def key_nocaps(self, k):
        """ add keystrokes to the list. the keystrokes are added as is, no
            modification is done. """
        pass

    def mod_plus_key(self, mods, k):
        """ add a keystroke, combined with a modifier (ctrl or alt) """
        pass

    

class XDoAutomator(Automator):

    def flush(self):
        if len(self.char_list) == 0: return

        command = '/usr/bin/xdotool' + ' '
        command += ' '.join(self.char_list)
        self.execute(command)
        self.char_list = []

    def raw_key(self, k):
        if(k == "'"): k = 'apostrophe'
        elif(k == '.'): k = 'period'
        elif(k == '-'): k = 'minus'
        self.add_keystrokes('key ' + k)

    def key_movement(self, k):
        k = k.capitalize()
        self.add_keystrokes('key ' + k)
        
    def key_nocaps(self, k):
        self.add_keystrokes('key ' + k)

    def mod_plus_key(self, mods, k):
        command = 'key '
        command += '+'.join(mods)
        if isinstance(k, scan.Token):
            k = k.type
        if(len(k) > 1 and k != 'plus' and k != 'apostrophe' and k != 'period' and k != 'minus' and k != 'space'): k = k.capitalize()
        command += '+' + k
        self.add_keystrokes(command)


class CLIClickAutomator(Automator):

    keymap = {
        "apostrophe": 't:"\'"',
        'quotedbl'  : "t:'\"'",
        'period'    : "t:'.'",
        'minus'     : "t:'-'",
        'equal'     : "t:'='",
        'colon'     : "t:':'",
        'semicolon' : "t:';'",
        'backspace' : "kp:delete",
        'escape'    : "kp:esc",
        'exclam'    : "t:'!'",
        'numbersign': "t:'#'",
        'dollar'    : "t:'$'",
        'percent'   : "t:'%'",
        'caret'     : "t:'^'",
        'ampersand' : "t:'&'",
        'asterisk'  : "t:'*'",
        'parenleft' : "t:'('",
        'parenright': "t:')'",
        'underscore': "t:'_'",
        'plus'      : "t:'+'",
        'backslash' : "t:'\\'",
        'slash'     : "t:'/'",
        'question'  : "t:'?'",
        'comma'     : "t:','",
        'space'     : "kp:space",
        'left'      : "kp:arrow-left",
        'right'     : "kp:arrow-right",
        'up'        : "kp:arrow-up",
        'down'      : "kp:arrow-down"
    }

    def flush(self):
        if len(self.char_list) == 0: return

        command = 'cliclick' + ' '
        command += ' '.join(self.char_list)
        self.execute(command)
        self.char_list = []

    def transform_key(self, k):
        lower_k = k.lower()
        if lower_k in self.keymap:
            return self.keymap[lower_k]
        elif(len(lower_k) == 1 and (lower_k[0].isalpha() or lower_k[0].isdigit())):
            return "t:" + k[0]
        else:
            return 'kp:' + k.lower()
        
    def raw_key(self, k):
        self.add_keystrokes(self.transform_key(k))

    def key_nocaps(self, k):
        self.add_keystrokes('t:'+k)

    def key_movement(self, k):
        if "page" in k:
            self.add_keystrokes('kp:page-' + k[4:].lower())
        else:
            self.add_keystrokes('kp:arrow-' + k.lower())
            
    def mod_plus_key(self, mods, k):
        command = "w:10 kd:"
        command += ','.join(mods)
        if isinstance(k, scan.Token):
            k = k.type
        if(len(k) > 1 and k != 'plus' and k != 'apostrophe' and k != 'period' and k != 'minus'): k = k.capitalize()
        command += " "
        command += self.transform_key(k)
        command += " "
        command += "ku:"
        command += ','.join(mods)
        self.add_keystrokes(command)


class NirCmdAutomator(Automator):

    # nircmd.exe transformations used here are keyboard layout specific;
    # they rely on virtual key codes
    # (https://docs.microsoft.com/en-us/windows/desktop/inputdev/virtual-key-codes)
    # the character that actually comes out is dependent on the keyoard
    # layout you have configured.
    keymap = 'english_us' #'belgian'
    keymaps = {
        'escape':    { 'belgian': 'esc',
                       'english_us': 'esc' },
        'colon':     { 'belgian': '0xBF',
                       'english_us': 'shift+0xba' },
        'semicolon': { 'belgian': '0xBE',
                       'english_us': '0xba' },
        'apostrophe':{ 'belgian': '0x34',
                       'english_us': '0xde' },
        'quotedbl':  { 'belgian': '0x33',
                       'english_us': 'shift+0xde' },
        'period':    { 'belgian': 'shift+0xBE',
                       'english_us': '0xBE' },
        'equal':     { 'belgian': '0xbb',
                       'english_us': '0xbb' },
        'space':     { 'belgian': 'spc',
                       'english_us': 'spc' },
        'exclam':    { 'belgian': '0x38',
                       'english_us': 'shift+0x31' },
        'numbersign':{ 'belgian': 'ctrl+alt+0x33',
                       'english_us': 'shift+0x33' },
        'dollar':    { 'belgian': '0xba',
                       'english_us': 'shift+0x34' },
        'percent':   { 'belgian': 'shift+0xC0',
                       'english_us': 'shift+0x35' },
        'caret':     { 'belgian': 'ctrl+alt+0x36',
                       'english_us': 'shift+0x36' },
        'ampersand': { 'belgian': '0x31',
                       'english_us': 'shift+0x37' },
        'asterisk':  { 'belgian': 'shift+0xBA',
                       'english_us': 'shift+0x38' },
        'parenleft': { 'belgian': '0x35',
                       'english_us': 'shift+0x39' },
        'parenright':{ 'belgian': '0xdb',
                       'english_us': 'shift+0x30' },
        'minus':     { 'belgian': 'minus',
                       'english_us': 'minus' },
        'underscore':{ 'belgian': 'shift+0xBD',
                       'english_us': 'shift+0xBD' },
        'plus':      { 'belgian': 'shift+0xBB',
                       'english_us': 'shift+0xBB' },
        'backslash': { 'belgian': 'ctrl+alt+0xe2',
                       'english_us': '0xe2' },
        'slash':     { 'belgian': 'shift+0xBF',
                       'english_us': '0xBF' },
        'question':  { 'belgian': 'shift+0xBC',
                       'english_us': 'shift+0xBf' },
        'comma':     { 'belgian': '0xbc',
                       'english_us': '0xbc' },
        'backspace': { 'belgian': 'backspace',
                       'english_us': 'backspace' },
        'return':    { 'belgian': '0x0d',
                       'english_us': '0x0d' },
        'tab':       { 'belgian': 'tab',
                       'english_us': 'tab' },
    }

    def transform_key(self, k):
        if k.lower() in self.keymaps:
            return self.keymaps[k.lower()][self.keymap].lower()
        else:
            return k    
    
    def flush(self):
        if len(self.char_list) == 0: return

        command = 'C:\\Tools\\nircmd-x64\\nircmd.exe sendkeypress' + ' '
        command += ' '.join(self.char_list)
        self.execute(command)
        self.char_list = []

    def raw_key(self, k):
        self.add_keystrokes(self.transform_key(k))

    def key_movement(self, k):
        self.add_keystrokes(k)

    def key_nocaps(self, k):
        if k in string.ascii_uppercase:
            k = "shift+" + k
        self.add_keystrokes(k)

    def mod_plus_key(self, mods, k):
        if (type(k) is not str):
            k = k.type
        command = ""
        command += '+'.join(mods)
        command += "+"
        command += self.transform_key(k)
        self.key_nocaps(command)
