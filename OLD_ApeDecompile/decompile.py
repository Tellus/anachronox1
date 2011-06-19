# TODO: "console %f", xxx
# the place where I normally find 0xffff after an expression is 0x0500 followed by the string "xxx"
# This implies that the 0xffff is actually an indication of combination.
# Need to read it before finishing an expression.

import os, sys
import struct
from StringIO import StringIO
from anoxtools import APE

# Syntax: decompile <file>

# These values must match in the header of the compiled APE file.
# The first 4 bytes (32 bits) must match decimal 317 and the latter 4 bytes
# must match hex 0xFFFFFFFF (quick quess: decimal -1 if signed, which it is).
bitHeader = (317, 0xFFFFFFFFL)

# Simple usage information.
def PrintHelp():
    fileName = os.path.split(sys.argv[0])[-1]
    print fileName, "<filename>"

# Decompile function.
def DecompileFile(fileName):
    # Safety catch - make sure opening the file works.
    try:
        f = open(fileName, 'rb')
    except IOError:
        PrintHelp()
        print "** File not found:", fileName
        sys.exit()

    
    try:
        # Unpack v into a tuple.
        # f.read(8) => read at most 8 bytes from file. Recall that 8 bytes match the bitheader length.
        # struct.unpack => unpack the 8 bytes into a double long (LL), each Long begin 8 bytes.
        # The tuple comparison compares the first 32 bits (4 bytes) of the file with the number 317
        # and the second 32 bits with the hexadecimal 0xFFFFFFFF (signed... -1?)
        v = struct.unpack("LL", f.read(8))
        # If both match (or, case of dynamic typing, the TYPEs match... whut?!), then:
        if v == bitHeader:
            # APEDecompiler is a parserEntities.Value subclass.
           args = APE.APEDecompiler(f)
           APE.OutputAPECode(args.windows, args.switches, args.switchesByLabel)
        else:
            print "** Not an APE file:", fileName, hex(v)
    except:
        # Clean up
        f.close()
        raise
    # Clean up
    f.close()

# Main loopage.
if __name__ == '__main__':
    # If we don't have exactly two arguments (wtf?)
    sys.argv = ["fuck", "you"]
    if len(sys.argv) != 2:
        PrintHelp()
        sys.exit()

    arg = sys.argv[1]
    arg = "ape\\braintrain.ape"
    
    # Case: argument is "--all".
    if arg == "--all":
        # Ensure the "ape\" directory exists.
        if os.access("ape", os.F_OK) != 1:
            print os.path.split(sys.argv[0])[-1] +": ape sub-directory not found.."
            sys.exit()
        # Ensure the "apes\" directory exists.
        if os.access("apes", os.F_OK) != 1:
            os.makedirs("apes")

        # We replace the stdout method later on in order to be able to catch process output from one
        # function without writing to the real stdout.
        oldStdout = sys.stdout
        
        # For each file in the ape directory...
        for fileName in os.listdir("ape"):
            # If it's a valid ape file.
            if fileName.endswith(".ape"):
                oldStdout.write(fileName +".. ")
                # Install our own stdout replacement. T-Chip: Why are we doing this?
                out = sys.stdout = StringIO()
                # Decompile the file catching the output.
                try:
                    DecompileFile("ape\\"+ fileName)
                except:
                    # We may have errors.
                    print
                    print "#### ERROR ERROR ERROR ####"
                    oldStdout.write(out.getvalue())
                    raise
                # Retrieve whatever was printing to stdout in previous calls and close the stream.
                s = out.getvalue()
                out.close()
                # Print it.
                oldStdout.write(".. %s\n" % len(s))

                # Open a decompiled APE file for writing and print the output from the decompile functions here.
                f = open("apes\\"+ fileName[:-4] +".txt", 'w')
                f.write(s)
                # Clean up.
                f.close()
        sys.stdout = oldStdout
    else:
        # Single file case, decompile that one file.
        DecompileFile(arg)

    exit()