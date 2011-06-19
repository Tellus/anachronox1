import struct

def ReadByte(f):
    return f.read(1)

def ReadWord(f):
    return struct.unpack("<H", f.read(2))[0]

def ReadInteger(f):
    return struct.unpack("<I", f.read(4))[0] # Force little-endian result of the read.

def ReadLong(f):
    return struct.unpack("<q", f.read(8))[0]

def ReadFloat(f):
    return struct.unpack("<f", f.read(4))[0]

def ReadDouble(f):
    return struct.unpack("<d", f.read(8))[0]

def ReadString(f, bytes=None, stripEOL=False):
    if bytes is None:
        bytes = ReadInteger(f)
    if bytes > 1000:
        raise RuntimeError("string length too large", bytes)
    s = f.read(bytes-1)
    f.read(1)
    if stripEOL and s[-1] == '\n':
        s = s[:-1]
    return s

def ReadQuotedString(f, bytes=None):
    s = ReadString(f, bytes)
    s = s.replace("\\", "\\\\")
    s = s.replace("\n", "\\n")
    s = s.replace("\"", "\\\"")
    return '"'+ s +'"'

class Structure:
    pass

class Definition:
    castWith = None

    def __init__(self, which, fields, **kwargs):
        self.which = which
        self.fields = fields

        self.__dict__.update(kwargs)

def DefineStructure(*fields, **kwargs):
    """ This produces a class with the fields set as attributes on it. """
    return Definition("structure", fields, **kwargs)

def DefineList(*fields, **kwargs):
    """ This produces a list with the fields appended as list elements. """
    return Definition("list", fields, **kwargs)

def DefineListItem(*field, **kwargs):
    """ This can be used to parse a list of structures, where each list
        item is just the result of a parsed field. """
    return Definition("listitem", [ field ], **kwargs)

class Reader:
    endianChar = "<"
    structures = None

    def __init__(self, f):
        pass

    def GetOrderedFieldNames(self, structName):
        return [ t[1] for t in self.structures[structName].fields ]

    def GetFmtLen(self, datatype):
        if datatype == "int32":
            fmt, cnt = "i", 4
        elif datatype == "float":
            fmt, cnt = "f", 4
        elif datatype == "uchar":
            fmt, cnt = "B", 1
        elif datatype == "int16":
            fmt, cnt = "h", 2
        elif datatype == "uint16":
            fmt, cnt = "H", 2
        elif datatype == "uint32":
            fmt, cnt = "I", 4
        elif datatype.startswith("string"):
            bits = datatype.split(".")
            cnt = int(bits[1])
            fmt = "%ds" % cnt
        else:
            raise RuntimeError("GetFmtLen passed unknown datatype:", datatype)
        return self.endianChar + fmt, cnt

    def GetStructSize(self, structName):
        if not self.structures.has_key(structName):
            return self.GetFmtLen(structName)[1]

        totalSize = 0
        for fieldInfo in self.structures[structName].fields:
            if len(fieldInfo) == 2:
                (datatype, fieldName), listSize = fieldInfo, 1
            else:
                datatype, fieldName, listSize = fieldInfo
            if self.structures.has_key(datatype):
                fieldSize = self.GetStructSize(datatype)
            else:
                fmt, fieldSize = self.GetFmtLen(datatype)
            totalSize += fieldSize * listSize
        return totalSize

    def ReadValue(self, f, datatype):
        fmt, cnt = self.GetFmtLen(datatype)
        s = f.read(cnt)
        v = struct.unpack(fmt, s)[0]
        if datatype.startswith("string"):
            idx = v.find(chr(0))
            if idx != -1:
                v = v[:idx]
        return v

    def ReadStruct(self, f, structName, listSizes=None):
        if not self.structures.has_key(structName):
            return self.ReadValue(f, structName)

        defn = self.structures[structName]

        if defn.which == "structure":
            result = Structure()
            result.structName = structName
        elif defn.which == "list":
            result = []
        elif defn.which == "listitem":
            result = None
        else:
            raise RuntimeError("Unknown defined type")

        for fieldInfo in defn.fields:
            if len(fieldInfo) == 2:
                datatype, fieldName = fieldInfo
                listSize = None
                if listSizes is not None and listSizes.has_key(datatype):
                    listSize = listSizes[datatype]
            else:
                datatype, fieldName, listSize = fieldInfo

            if listSize is None:
                if self.structures.has_key(datatype):
                    v = self.ReadStruct(f, datatype)
                else:
                    v = self.ReadValue(f, datatype)
            else:
                v = []
                for i in range(listSize):
                    if self.structures.has_key(datatype):
                        v2 = self.ReadStruct(f, datatype)
                    else:
                        v2 = self.ReadValue(f, datatype)
                    v.append(v2)

            if result is None:          # listitem
                result = v
                break
            elif type(result) is list:  # list
                result.append(v)
            else:                       # structure
                setattr(result, fieldName, v)

        if defn.castWith is not None:
            return defn.castWith(result)

        return result

    def ParseListOfStructures(self, f, offset, cnt, structName, l=None):
        f.seek(offset)

        for i in range(cnt):
            if structName == "string":
                v = self.ReadString(f)
            else:
                v = self.ReadStruct(f, structName)
            if l is not None:
                l.append(v)

    def WriteStructure(self, out, info):
        out.write("  Structure: %s\n" % info.structName)
        for fieldName in self.GetOrderedFieldNames(info.structName):
            out.write("    %s: %s\n" % (fieldName, getattr(info, fieldName)))
        out.write("\n")

    def DumpStruct(self, structure, depth=2):
        print " " * depth,
        print structure.structName +":"
        for fieldName in self.GetOrderedFieldNames(structure.structName):
            fieldValue = getattr(structure, fieldName)
            if type(fieldValue) is list:
                for i in range(len(fieldValue)):
                    self.DumpField(structure, fieldName, depth=depth, index=i)
            else:
                self.DumpField(structure, fieldName, depth=depth)

    def DumpField(self, structure, fieldName, index=None, depth=2):
        fieldValue = getattr(structure, fieldName)
        if index is not None:
            fieldValue = fieldValue[index]
        if isinstance(fieldValue, Structure):
            self.DumpStruct(fieldValue, depth+2)
        else:
            print " " * (depth + 2), fieldName, fieldValue
