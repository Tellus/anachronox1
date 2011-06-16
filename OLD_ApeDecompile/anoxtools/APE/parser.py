# TODO:
#
# - Find out how to binary diff the ape files so that I can work out why they
#   differ (usually recompiled versions are bigger) when I recompile them.
#
#   Need to write a script that goes through all the ape files and decompiles
#   them and recompiles them, noting the errors both in the decompilation
#   process and in the recompilation process.  Perhaps spit out a test report
#   in HTML which links to the output from both parts.
#

import sys, os
import struct
from StringIO import StringIO
import parserEntities as entities

DEBUG = 0

def Binary(x1, bits=32):
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

def DumpString(s):
    if not len(s):
        return
    print >>sys.stderr, "  DUMP %d\n" % len(s)
    print >>sys.stderr, "  ",
    for c in s:
        print >>sys.stderr, "%02x " % ord(c),
    print >>sys.stderr

def ReadBytes(f, n):
    return f.read(n)

def ReadAndDump(f, out=None, cnt=None):
    if cnt is None:
        s = f.read()
    else:
        s = f.read(cnt)
    DumpString(s)
    if cnt is None:
        if out is not None:
            print >>sys.stderr, out.getvalue()
        raise RuntimeError("ReadAndDump", out)

stringCommands = {
    4:  ("goto", 0),
    5:  ("gosub", 0),
    6:  ("console", 1),
    7:  ("echo", 1),
    8:  ("target", 0),
    9:  ("pathtarget", 0),
    10: ("extern", 0),
    12: ("playambient", 0),
    13: ("loopambient", 0),
    14: ("stopambient", 0),
    15: ("playscene", 0),
    16: ("loopscene", 0),
    17: ("stopscene", 0),
    18: ("chainscripts", 0),
    19: ("closewindow", 0),
    20: ("loadape", 1),
}


# ================================================================

from anoxtools import structures
from anoxtools.APE import parserEntities
from anoxtools.APE.parserEntities import FormattingValue, StatementValue, StringValue, ExpressionValue, AssignmentExpressionValue, CommaSeparatedValues

# Big schizmo decompiler fagimmeny.
class APEDecompiler(parserEntities.Value):
    def Read(self, f):
        self.fileLength = os.path.getsize(f.name)
        self.windows = []
        self.switches = []
        self.switchesByLabel = {}
        while 1:
            v = structures.ReadInteger(f)
            if v == 0:
                v = structures.ReadInteger(f)
                if v == 0xFFFFFFFEL:
                    self.ReadSwitches(f)
                else:
                    ReadAndDump(f, out)
                break
            self.ReadWindow(f, v)

    def ReadWindow(self, f, v):
        if DEBUG:
            print >>sys.stderr, "-- WINDOW START --"

        refs = []
        nestedStatements = parserEntities.NestedStatementsValue()
        self.ReadCommands(f, nestedStatements, refs)

        label = IntegerToLabel(v)
        self.windows.append((label, nestedStatements, refs))

        if DEBUG:
            # print >>sys.stderr, self.windows[-1][1].getvalue()
            print >>sys.stderr, "-- WINDOW END --"

    def ReadSwitches(self, f):
        if DEBUG:
            print >>sys.stderr, "-- SWITCHES START --"

        l = []
        value = structures.ReadInteger(f)
        while value != 0:
            label = IntegerToLabel(value)

            if DEBUG:
                print >>sys.stderr, "-- SWITCH START --", label

            nestedStatements = parserEntities.NestedStatementsValue()
            v1, v2 = structures.ReadInteger(f), structures.ReadInteger(f)
            if v1 != 1 or v2 != 0:
                raise RuntimeError("Unexpected", v1, v2)

            self.ReadCommands(f, nestedStatements, None)

            if self.switchesByLabel.has_key(label):
                print >>sys.stderr, "** Warning: Found switch for label already", label
            self.switches.append(label)
            self.switchesByLabel[label] = [ nestedStatements, len(self.switches)-1 ]

            if DEBUG:
                print >>sys.stderr, cmds.values, nestedStatements
                print >>sys.stderr, "-- SWITCH END --", label, f.tell() / float(self.fileLength)

            value = structures.ReadInteger(f)

        if DEBUG:
            print >>sys.stderr, "-- SWITCHES END --"

    def ReadCommands(self, f, nestedStatements, refs):
        flag = True
        while flag:
            flag, lastCC = self.ReadCommand(f, nestedStatements, refs)

    def ReadCommand(self, f, nestingLevel, refs=None):
        command = ord(structures.ReadByte(f))
        cc = None
        if DEBUG:
            print >>sys.stderr, "  -- READ COMMAND --", command
        if command == 0:
            v = structures.ReadInteger(f)
            fmt = FormattingValue(f)
            expr1, expr2, cc = self.ReadExpressionSegment(f)
        elif command in (1, 11):
            value = structures.ReadInteger(f)
            if value != 0:
                raise RuntimeError("NestedCommand 1 got", value, "expected 0")

            fmt = FormattingValue(f)
            expr1, expr2, cc = self.ReadExpressionSegment(f)
            if cc & 3 != 1:
                raise RuntimeError("NestedCommand 2 got", cc, "expected 1")

            nestedStatements = parserEntities.NestedStatementsValue(nestingLevel)
            if command == 1:
                nestedStatements.SetName("if")
            else:
                nestedStatements.SetName("while")
            nestedStatements.SetCondition(expr1)
            nestedStatements.Read(f, cc, self.ReadCommand)
            nestingLevel.Add(nestedStatements)
            cc = nestedStatements.ccEnd
        elif command == 2:
            variable = structures.ReadString(f)
            fmt = FormattingValue(f)
            expr1, expr2, cc = self.ReadExpressionSegment(f)
            if expr1 is not None:
                expr1.SetFormatting(fmt)
                statement = StatementValue("set")
                expr = AssignmentExpressionValue(StringValue(variable), expr1)
                statement.Add(expr)
                if expr2 is not None:
                    raise RuntimeError("Unexpected expr2, expected None, got:", expr2)
            else:
                statement = StatementValue("unset")
                statement.Add(StringValue(variable))
                if len(fmt):
                    raise RuntimeError("Unexpected formatting, deal with it:", fmt)
            nestingLevel.Add(statement)
        elif command == 3: # e.g. timed_message$="Use SHIFT + TAB to PerComm Between Party Members"
            variable = structures.ReadString(f)
            fmt = FormattingValue(f)
            expr1, expr2, cc = self.ReadExpressionSegment(f)
            if expr1 is not None or expr2 is not None:
                raise RuntimeError("Expected no expressions, got:", expr1, expr2)
            # Replace the newlines with the standard text representation.
            variable = variable.replace("\n", "\\n")
            # Locate the string specified (if there is one) then replace
            # all speech marks with quoted speech marks inside it.
            lIdx = variable.find("\"")
            rIdx = variable.rfind("\"")
            if lIdx != -1 and rIdx != -1:
                # We have a string in which to look.
                substring = variable[lIdx+1:rIdx]
                variable = variable.replace(substring, substring.replace("\"", "\\\""))
            elif lIdx == -1 and rIdx == -1:
                # No string.  Probably an unset of a string.
                if variable.endswith("$"):
                    variable = "unset "+ variable
            # Done fooling around with it.
            statement = StatementValue(variable)
            statement.SetFormatting(fmt)
            nestingLevel.Add(statement)
        elif stringCommands.has_key(command):
            statementName, quoteFlag = stringCommands[command]
            if quoteFlag:
                txt = structures.ReadQuotedString(f)
            else:
                txt = structures.ReadString(f)
            statement = StatementValue(statementName)
            statement.SetFormatting(FormattingValue(f))
            statement.Add(StringValue(txt))
            nestingLevel.Add(statement)
            expr1, expr2, cc = self.ReadExpressionSegment(f)
            if expr1 is not None or expr2 is not None:
                raise RuntimeError("Expected no expressions, got:", expr1, expr2)
        elif command == 49:
            label = IntegerToLabel(structures.ReadInteger(f))
            statement = StatementValue("startswitch")
            statement.Add(StringValue(label))
            nestingLevel.Add(statement)

            refs.append(label)
        elif command == 50:
            label = IntegerToLabel(structures.ReadInteger(f))
            statement = StatementValue("thinkswitch")
            statement.Add(StringValue(label))
            nestingLevel.Add(statement)

            refs.append(label)
        elif command == 51:
            label = IntegerToLabel(structures.ReadInteger(f))
            statement = StatementValue("finishswitch")
            statement.Add(StringValue(label))
            nestingLevel.Add(statement)

            refs.append(label)
        elif command == 65:
            statement = StatementValue("startconsole")
            statement.Add(parserEntities.QuotedStringValue(structures.ReadString(f, stripEOL=True)))
            nestingLevel.Add(statement)
        elif command == 66:
            conditions = []
            while structures.ReadLong(f) == 1:
                conditions.append(ExpressionValue(f))
            if len(conditions) not in (0, 1):
                raise RuntimeError("body, too many conditions", conditions)

            s = structures.ReadQuotedString(f)
            fmt = FormattingValue(f)

            statement = StatementValue("body")
            if len(conditions) == 1:
                statement.SetCondition(conditions[0])
            statement.SetFormatting(fmt)
            statement.Add(StringValue(s))
            nestingLevel.Add(statement)
        elif command == 67:
            conditions = []
            while structures.ReadLong(f) == 1:
                conditions.append(ExpressionValue(f))
            if len(conditions) not in (0, 1):
                raise RuntimeError("choice, too many conditions", conditions)

            s = structures.ReadQuotedString(f)
            fmt = FormattingValue(f)
            label = IntegerToLabel(structures.ReadInteger(f))

            # Debugging helper.
            #idx1 = f.tell()
            #fmt = FormattingValue(f)
            #idx2 = f.tell()
            #print "fmt",
            #f.seek(idx1)
            #while idx1 < idx2:
            #    print ord(f.read(1)),
            #    idx1 += 1
            #print

            # We need to kludge this statement a little depending on
            # whether the print parameters have just a string or
            # formatting information.  The reason for this is that
            # if there is formatting information, then there is a
            # comma trailing the print parameters before the label
            # and otherwise there is no comma.
            #
            # choice "%s", wibble$, 3:3
            # choice "blah" 3:3

            statement = StatementValue("choice")
            if len(conditions) == 1:
                statement.SetCondition(conditions[0])
            if len(fmt):
                paramList = parserEntities.CommaSeparatedValues()
                statement.Add(paramList)
            else:
                paramList = statement
            choiceString = StringValue(s)
            choiceString.SetFormatting(fmt)
            paramList.Add(choiceString)
            paramList.Add(StringValue(label))
            nestingLevel.Add(statement)
        elif command == 68:
            statement = StatementValue("background")
            for i in range(1, 5):
                lValue = StringValue("color%d" % i)
                rValue = StringValue("%02x%02x%02x%02x" % (ord(structures.ReadByte(f)), ord(structures.ReadByte(f)), ord(structures.ReadByte(f)), ord(structures.ReadByte(f))))
                expr = AssignmentExpressionValue(lValue, rValue)
                statement.Add(expr)
            nestingLevel.Add(statement)
        elif command == 69:
            return 0, cc
        elif command == 70:
            statement = StatementValue("font")
            statement.Add(parserEntities.QuotedStringValue(structures.ReadString(f)))
            nestingLevel.Add(statement)
        elif command == 71:
            tokens = (("xpos", 0), ("ypos", 0), ("width", 1), ("height", 1))
            for token, moreIfSet in tokens:
                if structures.ReadLong(f) == 1:
                    statement = StatementValue(token)
                    statement.Add(ExpressionValue(f))
                    nestingLevel.Add(statement)

                    if structures.ReadLong(f) == 1:
                        statement = StatementValue(token +"-x")
                        statement.Add(ExpressionValue(f))
                        nestingLevel.Add(statement)
        elif command == 72:
            v = structures.ReadLong(f)
            if v != 0:
                raise RuntimeError("SubwindowError", v)
            label = IntegerToLabel(structures.ReadInteger(f))
            statement = StatementValue("subwindow")
            statement.Add(StringValue(label))
            nestingLevel.Add(statement)
        elif command == 73:        
            conditions = []
            while structures.ReadLong(f) == 1:
                conditions.append(ExpressionValue(f))
            if len(conditions) not in (0, 1):
                raise RuntimeError("image, too many conditions", conditions)

            statement = StatementValue("image")
            if len(conditions) == 1:
                statement.SetCondition(conditions[0])
            statement.Add(parserEntities.FilenameValue(f))

            onlyZeroes = True
            csv = parserEntities.CommaSeparatedValues()
            for token in ("xpos", "ypos", "width", "height"):
                idx1 = f.tell()
                if structures.ReadLong(f) == 1:
                    v = ExpressionValue(f)                        
                    if onlyZeroes and not (isinstance(v, parserEntities.FloatValue) and v.value == 0.0):
                        onlyZeroes = False

                    csv.Add(v)
                    if structures.ReadLong(f) == 1:
                        # Unexpected?
                        expr = ExpressionValue(f)

            # It seems if this statement is actually a background statement
            # then it has two blank x pos and y pos entries and no width or
            # height.
            if len(csv) == 2 and onlyZeroes:
                statement.name = "background"
                csv.values = []

            flags = structures.ReadInteger(f)
            for bitmask, label in ((1, "stretch"), (2, "tile"), (4, "solid")):
                if flags & bitmask:
                    csv.Add(parserEntities.StringValue(label))

            statement.Add(csv)
            nestingLevel.Add(statement)
        elif command == 76:
            # TODO:
            # - Maybe have a LabelValue class (no maybe about it).
            # - Need statements to have the ability to arbitrarily add commas between arguments.
            #   Maybe best to leave as a formatting option.
            #
            # .. track current window
            # .. track current switch
            # .. identify references to filenames and labels by these.

            flags = structures.ReadInteger(f)
            if flags & 0x20000000:
                statement = StatementValue("flags")
                csv = CommaSeparatedValues()
                csv.Add(StringValue("passive2d"))
                csv.Add(StringValue("TRUE"))
                statement.Add(csv)
                nestingLevel.Add(statement)
            if flags & 0x40000000:
                statement = StatementValue("flags")
                csv = CommaSeparatedValues()
                csv.Add(StringValue("passive"))
                csv.Add(StringValue("TRUE"))
                statement.Add(csv)
                nestingLevel.Add(statement)
            if flags & 0x00000001:
                statement = StatementValue("flags")
                csv = CommaSeparatedValues()
                csv.Add(StringValue("persist"))
                csv.Add(StringValue("TRUE"))
                statement.Add(csv)
                nestingLevel.Add(statement)
            if flags & 0x00000004:
                statement = StatementValue("flags")
                csv = CommaSeparatedValues()
                csv.Add(StringValue("noscroll"))
                csv.Add(StringValue("TRUE"))
                statement.Add(csv)
                nestingLevel.Add(statement)
            if flags & 0x00000008:
                statement = StatementValue("flags")
                csv = CommaSeparatedValues()
                csv.Add(StringValue("nograb"))
                csv.Add(StringValue("TRUE"))
                statement.Add(csv)
                nestingLevel.Add(statement)
            if flags & 0x00000010:
                statement = StatementValue("flags")
                csv = CommaSeparatedValues()
                csv.Add(StringValue("norelease"))
                csv.Add(StringValue("TRUE"))
                statement.Add(csv)
                nestingLevel.Add(statement)
            if flags & 0x00000020:
                statement = StatementValue("flags")
                csv = CommaSeparatedValues()
                csv.Add(StringValue("subtitle"))
                csv.Add(StringValue("TRUE"))
                statement.Add(csv)
                nestingLevel.Add(statement)
            # norelease
            # flags unknown! 0x18L 00000000000000000000000000011000
            # flags unknown! 0x6L 00000000000000000000000000000110
            # Write a warning if we find something unexpected.
            if flags & ~0x6000003F:
                print >>sys.stderr, "// flags unknown! "+ str(hex(flags)) +" "+ Binary(flags) +"\n"
        elif command == 77:
            statement = StatementValue("cam")
            statement.Add(StringValue(structures.ReadString(f)))

            for key in ("from", "to", "owner"):
                bytes = structures.ReadInteger(f)
                if bytes != 0:
                    statement.Add(parserEntities.FuncValue(key, structures.ReadString(f, bytes)))

            for key in ("yaw", "pitch", "fov", "far", "near", "fwd", "speed", "lift", "lag", "occlude"):
                v = structures.ReadWord(f)
                if v != 0x8001:
                    if key == "occlude":
                        v = ["no","yes"][v]
                    statement.Add(parserEntities.FuncValue(key, v))

            if structures.ReadWord(f):
                statement.Add(StringValue("restore"))
            if structures.ReadWord(f):
                statement.Add(StringValue("zip"))
            nestingLevel.Add(statement)
        elif command == 78:
            statement = StatementValue("finishconsole")
            qsv = parserEntities.QuotedStringValue(structures.ReadString(f, stripEOL=True))
            statement.Add(qsv)
            nestingLevel.Add(statement)
        elif command == 79:
            statement = StatementValue("nextwindow")
            statement.Add(StringValue(f))
            nestingLevel.Add(statement)
        elif command == 80:
            statement = StatementValue()

            args = parserEntities.CommaSeparatedValues()
            v1, v2, cc = self.ReadExpressionSegment(f)
            args.Add(v1)
            v3 = ExpressionValue(f)
            args.Add(v3)
            for i in range(6):
                flag = structures.ReadLong(f)
                if flag == 1:
                    args.Add(ExpressionValue(f))

            if len(args) > 3:
                statement.SetName("xyprintfx")
                for i in range(3):
                    if structures.ReadLong(f) == 1:
                        args.Add(ExpressionValue(f))
                # Font name.
                args.Add(structures.ReadString(f))
            else:
                statement.SetName("xyprint")
                value = structures.ReadInteger(f)
                if value != 0:
                    raise RuntimeError("ParseFailure", commandName, value)
            args.Add(structures.ReadQuotedString(f))
            statement.Add(args)

            conditions = []
            while structures.ReadLong(f) == 1:
                conditions.append(ExpressionValue(f))

            statement.SetFormatting(FormattingValue(f))
            if len(conditions) == 1:
                statement.SetCondition(conditions[0])
            elif len(conditions) > 1:
                raise RuntimeError("Too many conditions (xyprint)", conditions)

            #nestingLevel.Add("%s %s, %s%s\n" % (commandName, argString,txt,fmt))

            nestingLevel.Add(statement)        
        elif command == 84:
            conditions = []
            while structures.ReadLong(f) == 1:
                conditions.append(ExpressionValue(f))

            statement = StatementValue("title")
            statement.Add(structures.ReadQuotedString(f))
            statement.SetFormatting(FormattingValue(f))
            if len(conditions) == 1:
                statement.SetCondition(conditions[0])
            elif len(conditions):
                raise RuntimeError("Too many conditions (title)", conditions)
            nestingLevel.Add(statement)
        elif command == 87:
            statement = StatementValue("style")
            statement.Add(structures.ReadQuotedString(f))
            nestingLevel.Add(statement)
        elif command == 89:
            animation1 = structures.ReadString(f)
            animation2 = ""
            bytes = structures.ReadInteger(f)
            if bytes != 0:
                animation2 = structures.ReadString(f, bytes)
            name1 = structures.ReadString(f)
            name2 = structures.ReadString(f)
            xtra1 = [ "nostay", "stay" ][structures.ReadInteger(f)]
            xtra2 = [ "nostay", "stay" ][structures.ReadInteger(f)]

            if name1 == '_click_' and name2 == 'playerchar0':
                statement = StatementValue("talk")
                statement.Add(StringValue("npc"))
                statement.Add(StringValue(animation1))
                statement.Add(StringValue(xtra1))
            elif name2 == '_click_' and name1 == 'playerchar0':
                statement = StatementValue("talk")
                statement.Add(StringValue("player"))
                statement.Add(StringValue(animation1))
                statement.Add(StringValue(xtra1))
            else:
                statement = StatementValue("talk_ex")
                statement.Add(StringValue(name1))
                statement.Add(StringValue(name2))
                statement.Add(StringValue(animation1))
                statement.Add(StringValue(animation2))
                statement.Add(StringValue(xtra1))
                statement.Add(StringValue(xtra2))
            nestingLevel.Add(statement)
        else:
            raise RuntimeError("UnknownCommand", command)
    # Debug the condition code for each command.
    #    if len(nestingLevel.values):
    #        if cc is not None and type(nestingLevel.values[-1]) is str:
    #            nestingLevel.values[-1] = Binary(cc, 64) +"\n"+ nestingLevel.values[-1]
        return 1, cc

    def ReadExpressionSegment(self, f):
        exprFlag = structures.ReadLong(f)
        if exprFlag == 1:
            expr1 = ExpressionValue(f)
            exprFlag = structures.ReadLong(f)
            if exprFlag == 1:
                expr2 = ExpressionValue(f)
            elif exprFlag == 0:
                expr2 = None
        elif exprFlag == 0:
            expr1, expr2 = None, None
        else:
            raise RuntimeError("Bad exprFlag", exprFlag, f.tell())
        cc = structures.ReadLong(f)
        return expr1, expr2, cc

# ================================================================

def IntegerToLabel(v):
    """ v: The integer which is an APE label.

        Purpose: Take the compiled label form and convert it to the APE code label form.
    """
    if v == 0:
        return "0:0"
    s = str(v)
    s1, s2 = s[:-4], int(s[-4:])
    return "%s:%s" % (s1, s2)
