import sys, struct

from anoxtools import structures

# As can be seen below, we assign some of the standalone functions from
# structures to the classes as their reader functions.  However, this act
# turns them into bound functions on the instances created, which in turn
# causes errors when they are called and they are now expected to take a
# self argument in addition to their actual ones.  Wrapping them in this
# Callable class stops the reference to them from being changed.
class Callable:
    def __init__(self, f):
        self.__call__ = f

class Value:
    Read = None

    formatting = None

    # Constructor, takes a single value...thingy.
    def __init__(self, value=None):
        # If the passed var is a file, then send it to SetValue. If not... then send it to SetValue.
        # What the fuckety-fuck is going on here?!
        if type(value) is file:
            self.SetValue(self.Read(value), False)
        else:
            self.SetValue(value, True)

    # Sets .value to the value of value - christ, who came up with these names?!
    def SetValue(self, value, direct=True):
        self.value = value

    def SetFormatting(self, formatting):
        self.formatting = formatting

    def Binary(self, value, bits=32):
        """ value: The number to convert.
            bits: How many bits make up the number.

            Purpose: Create a string representation of the numbers binary form.

            This takes a number and returns a readable string that represents
            each bit in the number with a '0' or '1' character respectively.
            e.g. Binary(12, 4)
                 "1100"
        """
        s = ""
        x = value
        for i in range(bits):
            s = ['0','1'][x & 1] + s
            x = x >> 1
        return s

    def __str__(self):
        s = self.str()
        if self.formatting:
            return s + str(self.formatting)
        return s

class FloatValue(Value):
    Read = Callable(structures.ReadFloat)

    def str(self):
        if self.value == 0.0:
            return "0"

        # Prevent things like 1e-5 which APE cannot handle.
        if self.value < 0.001:
            return "%f" % self.value

        intValue = int(self.value)
        if abs(intValue - self.value) < 1e-8:
            return str(intValue)

        return str(self.value)

class StringValue(Value):
    Read = Callable(structures.ReadString)

    def str(self):
        return self.value

class QuotedStringValue(Value):
    Read = Callable(structures.ReadQuotedString)

    def SetValue(self, value, direct=True):
        if direct:
            value = '"'+ value +'"'
        self.value = value

    def str(self):
        return self.value

class FilenameValue(QuotedStringValue):
    # Reads as a string.
    # Written out in quotes in APE.
    def str(self):
        return self.value

class CommaSeparatedValues:
    def __init__(self):
        self.values = []

    def Add(self, value):
        self.values.append(value)

    def __len__(self):
        return len(self.values)

    def __str__(self):
        return ", ".join([ str(v) for v in self.values ])

class FuncValue(Value):
    """ %s(%s) % (k, v) """
    def __init__(self, k, v):
        self.key = k
        self.value = v

    def str(self):
        return "%s(%s)" % (self.key, self.value)

OP_OR    = 1
OP_AND   = 2
OP_XOR   = 3
OP_GT    = 4
OP_LT    = 5
OP_GE    = 6
OP_LE    = 7
OP_EQ    = 8
OP_ADD   = 9
OP_SUB   = 10
OP_MUL   = 11
OP_DIV   = 12
OP_NE    = 13

OP_ASSIGN = -1

operators = {
    # Custom.
    OP_ASSIGN:  "=",    

    # APE binary constants.
    OP_OR:  "||",
    OP_AND: "&&",
    OP_XOR: "^^",
    OP_GT:   ">",
    OP_LT:   "<",
    OP_GE:  ">=",
    OP_LE:  "<=",
    OP_EQ:  "==",
    OP_ADD:  "+",
    OP_SUB:  "-",
    OP_MUL:  "*",
    OP_DIV:  "/",
    OP_NE:  "!=",
}

def ExpressionValue(f):
    expr = ExpressionValue2(f)
    if isinstance(expr.lValue, FloatValue) and expr.lValue.value == 0.0 and expr.operatorIdx == OP_ADD:
        return expr.rValue
    return expr    

class ExpressionValue2(Value):
    def Read(self, f):
        self.operatorIdx = ord(structures.ReadByte(f))
        self.valueFlags = ord(structures.ReadByte(f))

        self.ReadLValue(f)
        self.ReadRValue(f)

    def ReadLValue(self, f):
        v = structures.ReadLong(f) # Unused.
        if self.valueFlags in (0x00, 0x08, 0x0a):
            self.lValue = ExpressionValue(f)
        elif self.valueFlags in (0x04, 0x0c, 0x0e):
            self.lValue = FloatValue(f)
        elif self.valueFlags in (0x05, 0x0d, 0x0f, 0x31):
            self.lValue = StringValue(f)
            if self.lValue == "":
                raise RuntimeError("UnexpectedLValue", self.operatorIdx, self.valueFlags)
        elif self.valueFlags in (0x30, 0x32, 0x33):
            self.lValue = QuotedStringValue(f)
        else:
            raise RuntimeError("BadLValue", self.operatorIdx, self.valueFlags)

    def ReadRValue(self, f):
        v = structures.ReadLong(f) # Unused.
        if self.valueFlags in (0x00, 0x04, 0x05):
            self.rValue = ExpressionValue(f)
        elif self.valueFlags in (0x08, 0x0c, 0x0d):
            self.rValue = FloatValue(f)
        elif self.valueFlags in (0x0a, 0x0e, 0x0f):
            self.rValue = StringValue(f)
            if self.rValue == "":
                raise RuntimeError("UnexpectedRValue", self.operatorIdx, self.valueFlags)
        elif self.valueFlags in (0x30, 0x31, 0x32, 0x33):
            self.rValue = QuotedStringValue(f)
        else:
            raise RuntimeError("BadRValue", self.operatorIdx, self.valueFlags)

    def SetOperatorIdx(self, operatorIdx):
        self.operatorIdx = operatorIdx

    def SetLValue(self, lValue):
        self.lValue = lValue

    def SetRValue(self, rValue):
        self.rValue = rValue

    def __str__(self):
        s = str(self.lValue) +" "+ operators[self.operatorIdx] +" "+ str(self.rValue)
        if self.operatorIdx == OP_ASSIGN:
            return s
        return "("+ s +")"

def AssignmentExpressionValue(key, value):
    expr = ExpressionValue2()
    expr.SetOperatorIdx(OP_ASSIGN)
    expr.SetLValue(key)
    expr.SetRValue(value)
    return expr

class FormattingValue(Value):
    def Read(self, f):
        self.members = [ '' ]

        done = ord(structures.ReadByte(f))
        valueFlag = ord(structures.ReadByte(f))
        while not done:
            if valueFlag == 0x05:
                self.Add(structures.ReadString(f))
            elif valueFlag == 0x04:
                self.Add(structures.ReadFloat(f))
            elif valueFlag == 0x10:
                self.Add(structures.ReadQuotedString(f))
            elif valueFlag == 0x11:
                self.Add(structures.ReadString(f))
            else:
                raise RuntimeError("BadFormatting", done, valueFlag)
            done = ord(structures.ReadByte(f))
            valueFlag = ord(structures.ReadByte(f))

    def Add(self, x):
        self.members.append(x)

    def __str__(self):
        if len(self.members) == 1:
            return ""
        return ", ".join([ str(x) for x in self.members ])

    def __len__(self):
        return len(self.members) - 1

class StatementValue(Value):
    condition = None

    def __init__(self, name=None):
        self.name = name
        self.values = []

    def Add(self, value):
        self.values.append(value)

    def SetName(self, name):
        self.name = name

    def SetCondition(self, condition):
        self.condition = condition

    def str(self):
        return self.name +" "+ " ".join([ str(v) for v in self.values ])

# When more bits are added, its a new statement of deeper nestedness.
# When bits are removed, its dropping back levels of nestedness.
shiftMaskIn    = 0xfffffffffffffffcL # 1100
shiftMaskInNew = 0x0000000000000003L # 0011

class NestedStatementsValue(Value):
    condition = None

    cntStart = None

    ccStart = None
    ccEnd = None
    
    def __init__(self, parentEntity=None):
        self.name = None
        self.values = []
        self.exitCount = 0
        self.parent = parentEntity

    def SetName(self, name):
        self.name = name

    def SetCondition(self, condition):
        self.condition = condition

    def Add(self, value):
        self.values.append(value)

    def Read(self, f, cc, readCommand):
        self.cntStart = self.CountBits(cc)
        self.ccStart = cc

        # print "NSV - START     ", self.Binary(cc), self.parent is not None and self.parent.__class__.__name__, "|", self.name, self.condition
        while 1:
            lastCC = cc
            ret, cc = readCommand(f, self)

            #value = self.values[-1]
            #if isinstance(value, NestedStatementsValue):
            #    print "READ", value.name, "_condition=", value.condition
            #else:
            #    print "READ", value, "_condition=", value is not None and value.condition
            #
            #print "NSV - RC", self.Binary(cc), self.Binary(lastCC << 2)
            if ret == 0:
                raise RuntimeError("Unexpected ret", ret, cc)
            if cc is None:
                raise RuntimeError("Expected condition code", self)

            lastCC0 = lastCC
            lastCC1 = lastCC << 2
            # Staying at the same level?
            if cc & shiftMaskIn != lastCC1:
                cntBefore = self.CountBits(lastCC) # Zero bits before the read command.
                cntAfter  = self.CountBits(cc)     # Zero bits after the read command.

                if cntBefore < cntAfter:
                    if self.IsFromParentLevel(cc):
                        #print "NO EXIT (ccStart)", (self.Binary(self.ccStart), self.cntStart)
                        #print "NO EXIT (  ccEnd)", (self.Binary(cc), cntAfter)
                        #print "PARENT           ", self.parent is not None and (self.Binary(self.parent.ccStart), self.CountBits(self.parent.ccStart))
                        #print "NSV - EXIT - 4"
                        break
                    elif cc & shiftMaskInNew == 2:
                        self.exitCount = 0
                        cntBeforeShifted = cntBefore
                        while cntBeforeShifted < cntAfter:
                            # Get the next sequence and move the lastCC to account for it.
                            if lastCC & shiftMaskInNew == 2:
                                self.exitCount += 1
                            lastCC = lastCC >> 2
                            cntBeforeShifted += 2

                        if self.exitCount > 0:
                            self.exitCount -= 1
                            # print "NSV - EXIT - 1"
                            break

                        self.Add(None)
                    else:
                        # Last statement in a nesting.
                        # print "NSV - EXIT - 2"
                        break
                elif cntBefore == cntAfter and (lastCC & shiftMaskInNew) in (1, 2) and (cc & shiftMaskInNew) == 3:
                    # This was the only clause following an else.  Drop out to give the next clause to the container.
                    # print "NSV - EXIT - 3"
                    break
                elif cntBefore == cntAfter and (lastCC & shiftMaskInNew) == 1 and (cc & shiftMaskInNew) == 2:
                    self.Add(None)
                else:
                    raise RuntimeError("Unexpected movement", Binary(lastCC, 64), cntBefore, Binary(cc, 64), cntAfter, cmds)
            #elif cc & shiftMaskInNew == 1:
            #    print "NSV - EXIT - 4"
            #    break
            elif cc & shiftMaskInNew != 3:
                print "NSV lastCC1", self.Binary(lastCC1)
                print "NSV lastCC ", self.Binary(lastCC)
                print "NSV cc     ", self.Binary(cc)
                raise RuntimeError("Unexpected flags", cc & shiftMaskInNew)

        self.ccEnd = cc

    def IsFromParentLevel(self, cc):
        if isinstance(self.parent, NestedStatementsValue) and self.parent.name == "if":
            if (self.parent.ccStart & shiftMaskIn) == (cc & shiftMaskIn):
                return True
        return False

    def CountBits(self, value):
        """ value: The long sized value to count.

            Purpose: Count the number of leading 0 bits in the value.

            This has a one bit mask which it shifts from the high end to the
            low end of the long until the whole long is covered or a 1 bit is
            found.
        """
        cnt = 0
        mask = 0x8000000000000000L
        while mask and not (value & mask):
            cnt += 1
            mask = mask >> 1
        return cnt

    def Binary(self, x1, bits=64):
        """ x1: The number to convert.
            bits: How many bits make up the number.

            Purpose: Create a string representation of the numbers binary form.

            This takes a number and returns a readable string that represents
            each bit in the number with a '0' or '1' character respectively.
            e.g. Binary(12, 4)
                 "1100"
        """
        s = ""
        x = x1
        for i in range(bits):
            s = ['0','1'][x & 1] + s
            x = x >> 1
        return s

    def __len__(self):
        return len(self.values)
