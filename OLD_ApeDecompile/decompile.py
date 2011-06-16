# TODO: "console %f", xxx
# the place where I normally find 0xffff after an expression is 0x0500 followed by the string "xxx"
# This implies that the 0xffff is actually an indication of combination.
# Need to read it before finishing an expression.

import os, sys
import struct
from StringIO import StringIO
from lib import *

# Syntax: decompile <file>

# All these values are
bitHeader = (317, 0xFFFFFFFFL)

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
        # f.read(8) => read at most 8 bytes from file. Recall that 8 bytes match the 
        # struct.unpack => unpack the 8 bytes into a double long (LL), each Long begin 8 bytes.
        # The tuple comparison compares the first 32 bits (4 bytes) of the file with the number 317
        # and the second 32 bits with the hexadecimal 0xFFFFFFFF (signed... -1?)
        v = struct.unpack("LL", f.read(8))
        # If both match (or, case of dynamic typing, the TYPEs match... whut?!), then:
        if v == bitHeader:
           args = APE.APEDecompiler(f)
           APE.OutputAPECode(args.windows, args.switches, args.switchesByLabel)
        else:
            print "** Not an APE file:", fileName, hex(v)
    except:
        f.close()
        raise

    f.close()

# Main loopage.
if __name__ == '__main__':
    # If we don't have exactly two arguments (wtf?)
    if len(sys.argv) != 2:
        PrintHelp()
        sys.exit()

    arg = sys.argv[1]
    
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
                    print
                    print "#### ERROR ERROR ERROR ####"
                    oldStdout.write(out.getvalue())
                    raise
                s = out.getvalue()
                out.close()
                oldStdout.write(".. %s\n" % len(s))

                f = open("apes\\"+ fileName[:-4] +".txt", 'w')
                f.write(s)
                f.close()
        sys.stdout = oldStdout
    else:
        DecompileFile(arg)
