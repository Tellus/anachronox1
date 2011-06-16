import os
from Plex import *

class Object:
    pass

class GDBReader(Scanner):
    def __init__(self, f, filename, verbose=False):
        self.verbose = verbose

        # State variables.
        self.currentOb = None
        self.currentName = None
        self.currentKeyName = None
        self.currentValueType = None

        # Result variables.
        self.objectsByName = {}

        Scanner.__init__(self, self.lexicon, f, filename)

    # lexer stuff
    letter = Range('AZaz')
    digit = Range('09')
    alphanum = letter | digit
    name = letter + Rep(alphanum | Str('_') | Str('.'))
    spaceortab = Any(' \t')
    space = Any(' \t\n\r')
    notspace = AnyBut(' \t\n\r')
    cr = Str('\n')
    crlf = Str('\r\n')
    eol = Alt(crlf | cr)
    quotationMark = Str('"')
    eos = quotationMark + Rep(spaceortab) + eol

    comment = Str('//') + Rep(AnyBut('\n'))
    keyName = Rep(letter | Str('_'))
    valueType = Rep(letter)
    stringDelimiter = quotationMark
    quotedString = Str('\\"')
    valueString = Rep(quotedString | AnyBut('"'))
    valueNumber = Rep(Alt(Str('.') | Rep(digit)))
    textUntilEOL = Rep(AnyBut('\n\r')) # + Rep(AnyBut(''))
    dictName = Str('#')+ Rep(notspace)

    def ObserveObject(self, name):
        if self.verbose:
            print "ObserveObject", '"'+ name +'"'
        self.begin('objectName')
    
    def StartObject(self, name):
        if self.verbose:
            print "StartObject", '"'+ name +'"'
        self.currentOb = Object()
        self.currentOb.name = self.currentName

    def EndObject(self, text):
        if self.verbose:
            print "EndObject", text
        self.begin('')

    def StoreObjectName(self, name):
        if self.verbose:
            print "SetObjectName", '"'+ name +'"'
        self.currentName = name
        self.begin('keyName')

    def StoreKeyName(self, name):
        if self.verbose:
            print "StoreKeyName", '"'+ name +'"'
        self.currentKeyName = name
        self.begin('valueType')

    def StoreValueType(self, name):
        if self.verbose:
            print "StoreValueType", '"'+ name +'"'
        self.currentValueType = name
        if name == "string":
            self.begin('startString')
        elif name == "int" or name == "float":
            self.begin('valueNumber')
        else:
            raise RuntimeError("Unexpected data-type '%s', key-name '%s', object-name '%s'" % (name, self.currentKeyName, self.currentOb.name))

    def StartString(self, name):
        self.begin('valueString')

    def EndString(self, name):
        if self.verbose:
            print "EndString", '"%s"'% getattr(self.currentOb, self.currentKeyName, "FUCKED-STRING")
        self.begin('keyName')

    def StoreValueString(self, string):
        if self.verbose:
            print "StoreValueString", '"'+ string +'"'
        if hasattr(self.currentOb, self.currentKeyName):
            string = getattr(self.currentOb, self.currentKeyName) + string
        setattr(self.currentOb, self.currentKeyName, string)

    def StoreValueNumber(self, number):
        if self.currentValueType == "int":
            caster = int
        elif self.currentValueType == "float":
            caster = float
        setattr(self.currentOb, self.currentKeyName, caster(number))
        self.begin('keyName')
        
    lexicon = Lexicon([
        (dictName, ObserveObject),
        State('objectName', [
            (textUntilEOL, StoreObjectName),
            (AnyChar, IGNORE)
        ]),
        State('keyName', [
            (Str('{'), StartObject),
            (Str('}'), EndObject),
            (comment, IGNORE),            
            (keyName, StoreKeyName),
            (AnyChar, IGNORE)
        ]),
        State('valueType', [
            (valueType, StoreValueType),
            (AnyChar, IGNORE)
        ]),
        State('startString', [
            (stringDelimiter, StartString),
            (AnyChar, IGNORE)
        ]),
        State('valueString', [
            (eos, EndString),
            (quotationMark, StoreValueString),
            (valueString, StoreValueString),
        ]),
        State('valueNumber', [
            (valueNumber, StoreValueNumber),
            (AnyChar, IGNORE)
        ]),
        (space, IGNORE),
        (comment, IGNORE),
        (AnyChar, IGNORE)
    ])
