import struct
from constants import *

class Header:
    """Read and provide interface to header"""
    
    def __init__(self, file):
        bytes = file.read(56) # 2 unsigned shorts, 4 unsigned ints and 9 uint-bools
        self.number_of_input_symbols             = struct.unpack_from("<H", bytes, 0)[0]
        self.number_of_symbols                   = struct.unpack_from("<H", bytes, 2)[0]
        self.size_of_transition_index_table      = struct.unpack_from("<I", bytes, 4)[0]
        self.size_of_transition_target_table     = struct.unpack_from("<I", bytes, 8)[0]
        self.number_of_states                    = struct.unpack_from("<I", bytes, 12)[0]
        self.number_of_transitions               = struct.unpack_from("<I", bytes, 16)[0]
        self.weighted                            = struct.unpack_from("<I", bytes, 20)[0] != 0
        self.deterministic                       = struct.unpack_from("<I", bytes, 24)[0] != 0
        self.input_deterministic                 = struct.unpack_from("<I", bytes, 28)[0] != 0
        self.minimized                           = struct.unpack_from("<I", bytes, 32)[0] != 0
        self.cyclic                              = struct.unpack_from("<I", bytes, 36)[0] != 0
        self.has_epsilon_epsilon_transitions     = struct.unpack_from("<I", bytes, 40)[0] != 0
        self.has_input_epsilon_transitions       = struct.unpack_from("<I", bytes, 44)[0] != 0
        self.has_input_epsilon_cycles            = struct.unpack_from("<I", bytes, 48)[0] != 0
        self.has_unweighted_input_epsilon_cycles = struct.unpack_from("<I", bytes, 52)[0] != 0

class Alphabet:
    """Read and provide interface to alphabet"""

    def __init__(self, file, number_of_symbols):
        self.keyTable = [] # list of unicode objects, use foo.encode("utf-8") to print
        self.flagDiacriticOperations = dict() # of symbol numbers to string triples
        for x in range(number_of_symbols):
            symbol = ""
            while True:
                byte = file.read(1)
                if byte == '\0': # a symbol has ended
                    symbol = unicode(symbol, "utf-8")
                    if symbol[0] == '@' and symbol [-1] == '@' and symbol[2] == '.':
                        # this is a flag diacritic
                        op = feat = val = u""
                        parts = symbol[1:-1].split(u'.')
                        if len(parts) == 2:
                            op, feat = parts
                        elif len(parts) == 3:
                            op, feat, val = parts
                        else:
                            self.keyTable.append(symbol)
                            break
                        self.flagDiacriticOperations[x] = FlagDiacriticOperation(op, feat, val)
                        self.keyTable.append(u"")
                        break
                    self.keyTable.append(symbol)
                    break
                symbol += byte

class LetterTrie:
    """Insert and prefix-retrieve string / symbol number pairs"""

    class Node:
        
        def __init__(self):
            self.symbols = dict()
            self.children = dict()
            
        def add(self, string, symbolNumber):
            """
            Add string to trie, having it resolve to symbolNumber
            """
            if len(string) > 1:
                if not string[0] in self.children:
                    self.children[string[0]] = self.__class__() # instantiate a new node
                self.children[string[0]].add(string[1:], symbolNumber)
            elif len(string) == 1:
                self.symbols[string[0]] = symbolNumber
            else:
                self.symbols[string] = symbolNumber

        def find(self, indexstring):
            """
            Find symbol number corresponding to longest match in indexstring
            (starting from the position held by indexstring.pos)
            """
            if indexstring.pos >= len(indexstring.s):
                return NO_SYMBOL_NUMBER
            indexstring.pos += 1
            if not indexstring.get(-1) in self.children:
                if not indexstring.get(-1) in self.symbols:
                    return NO_SYMBOL_NUMBER
                return self.symbols[indexstring.get(-1)]
            indexstring.save()
            temp = self.children[indexstring.get(-1)].find(indexstring)
            if temp == NO_SYMBOL_NUMBER:
                indexstring.restore()
                return self.symbols[indexstring.get(-1)]
            return temp
    
    def __init__(self):
        self.root = self.Node()

    def addString(self, string, symbolNumber):
        self.root.add(string, symbolNumber)

    def findKey(self, indexstring):
        return self.root.find(indexstring)

class Indexlist:
    """Utility class to keep track of where we are in a list"""

    def __init__(self, items = []):
        self.s = list(items)
        self.pos = 0
    
    def get(self, adjustment = 0):
        return self.s[self.pos + adjustment]

    def put(self, val, adjustment = 0):
        if (self.pos + adjustment) < len(self.s):
            self.s[self.pos + adjustment] = val
        else:
            self.s.append(val)

    def save(self):
        self.temp = self.pos

    def restore(self):
        self.pos = self.temp

class FlagDiacriticOperation:
    """Represents one flag diacritic operation"""
    
    def __init__(self, op, feat, val):
        self.operation = op
        self.feature = feat
        self.value = val

def match(transitionSymbol, inputSymbol):
    """Utility function to check whether we want to traverse a transition/index"""
    if transitionSymbol == NO_SYMBOL_NUMBER:
        return False
    if inputSymbol == NO_SYMBOL_NUMBER:
        return True
    return symbol == inputSymbol
