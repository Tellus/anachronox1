import sys
from StringIO import StringIO
from parserEntities import NestedStatementsValue, StatementValue, ExpressionValue2

# Translates a condition into a string, most likely conditionals from APE.
def ConditionToString(condition):
    condition2 = str(condition)
    # ExpressionValue2 is a value object, so we ensure condition is also.
    # The point here is that if the passed object is NOT an ExpressionValue2 object, we add parenthesis,
    # otherwise we return it as-is. Recall that this will make a+x==j+a turn into something like (a+x)==(j+a).
    if not isinstance(condition, ExpressionValue2):
        condition2 = "("+ condition2 +")"
    return condition2

# TODO: Write-up better.
# I believe this funtion outputs functional APE code depending on detected windows (remember APE loves these),
# swiches (... love them too?), and switches...by...label?
def OutputAPECode(windows, switches, switchesByLabel):
    def Indent(indentCnt, s, out, nl=True):
        """Simple indentation maker.
        
        Keyword arguments:
        indentCnt -- number of double spaces to indent by (two whitespaces every time).
        s -- The text to write after indentation.
        out -- The output stream.
        nl -- Make a newline?
        
        """
        if indentCnt > 0:
            out.write("  " * indentCnt)
        out.write(s)
        if nl:
            out.write("\n")

    # Switches are always enclosed in curly brackets.
    # Analysis of hex in binaries confirms.
    def IndentNestedCommands(cmds, indentCnt=1):
        """Creates pretty nesting of commands.
        
        Keyword arguments:
            cmds -- Set, list, tuple, array of commands to nest?
            indentCnt -- Most likely a recursive indentation counter.
        
        """
        out = StringIO() # Creates a string buffer that works just like an in-memory file.
        # Open parentheses.
        # If there are conditions.
        if cmds.condition is not None:
            condition = str(cmds.condition)
            if not isinstance(cmds.condition, ExpressionValue2):
                condition = "("+ condition +")"
            Indent(indentCnt-1, "%s %s" % (cmds.name, ConditionToString(cmds.condition)), out, nl=False)
            if len(cmds.values) > 1:
                out.write(" {") #  // %d values" % len(cmds.values))
            out.write("\n")
        elif cmds.name is not None:
            Indent(indentCnt-1, cmds.name, out, nl=False)
            if len(cmds.values) > 1 or cmds.name.endswith('switch'):
                out.write(" {")
            out.write("\n")
            
        # Go through the elements.
        for i, element in enumerate(cmds.values):
            if element is None:
                if i == len(cmds.values)-2:
                    # By clearing the name of the current nested level,
                    # we make sure its clear we are no longer responsible for
                    # closing it.
                    cmds.name = None
                    # Do the last element by hand.
                    element = cmds.values[i+1]
                    if isinstance(element, NestedStatementsValue):
                        element.name = "} else "+ element.name
                        out.write(IndentNestedCommands(element, indentCnt))
                    else:
                        Indent(indentCnt-1, "} else", out)
                        Indent(indentCnt, str(element), out)
                    break
                Indent(indentCnt-1, "} else {", out)
            elif isinstance(element, NestedStatementsValue):
                out.write(IndentNestedCommands(element, indentCnt+1))
            else:
                Indent(indentCnt, str(element), out)

        # Close parentheses.
        if cmds.name is not None:
            if len(cmds.values) > 1 or cmds.name.endswith('switch'):
                Indent(indentCnt-1, "}", out)
        return out.getvalue()

    # ACTUAL FUNCTION STARTS HERE!
    # For each label, wCmds (window commands?) and references in each window.
    for label, wCmds, refs in windows:
        # Print window information. This is APE syntax.
        print "#window %s" % label
        # For each element within wCmds.values
        for element in wCmds.values:
            if not isinstance(element, NestedStatementsValue):
                if element.name in ("startswitch", "thinkswitch", "finishswitch"):
                    elementName, label = element.name, element.values[0].value
                    element, idx = switchesByLabel[label]
                    switches[idx] = None
                    if not isinstance(element, NestedStatementsValue):
                        raise RuntimeError("Window clause processing expected NestedStatementsValue, got %s" % element.__class__.__name__)
                    element.name = elementName
            if isinstance(element, NestedStatementsValue):
                print IndentNestedCommands(element)
            elif isinstance(element, StatementValue) and element.condition is not None:
                Indent(0, "%s %s" % ("if", ConditionToString(element.condition)), sys.stdout)
                Indent(1, str(element), sys.stdout)
            else:
                print element
        print

    first = True
    for label in switches:
        # If the label is empty, go to next iteration.
        if label is None:
            continue
        # If we're working with the first token (I assume), create a newline to split.
        if not first:
            sys.stdout.write("\n")
        # At this point remove the first marker.
        first = False
        sys.stdout.write("#switch %s\n" % label)
        sCmds = switchesByLabel[label][0]
        sys.stdout.write(IndentNestedCommands(sCmds, indentCnt=0))
