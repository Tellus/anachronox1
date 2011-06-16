import os, sys
import StringIO

# BSP file processing:
import structures
import texture
from structures import DefineStructure, DefineList, DefineListItem

# Face polygon processing:
from contrib.polygontessellator import PolygonTessellator
from nedu.vector import normalize

# Entities lump processing:
from contrib.Plex import *

from OpenGL import GLU

# ...

LUMP_ENTITIES       = 0
LUMP_PLANES         = 1
LUMP_VERTEXES       = 2
LUMP_VISIBILITY     = 3
LUMP_NODES          = 4
LUMP_TEXINFO        = 5
LUMP_FACES          = 6
LUMP_LIGHTING       = 7
LUMP_LEAFS          = 8
LUMP_LEAFFACES      = 9
LUMP_LEAFBRUSHES    = 10
LUMP_EDGES          = 11
LUMP_SURFEDGES      = 12
LUMP_MODELS         = 13
LUMP_BRUSHES        = 14
LUMP_BRUSHSIDES     = 15
LUMP_POP            = 16
LUMP_AREAS          = 17
LUMP_AREAPORTALS    = 18

# What are the various lumps used for?

class BSPReader(structures.Reader):
    endianChar = "<"

    def __init__(self, f, dataPath, filename):
        self.dataPath = dataPath

        self.structure = self.ReadStruct(f, "BSPHeader")

## By checking the lowest lump offset against the end of the headers
## it can be seen if there is extra data in the file.
##        currentOffset = f.tell()
##
##        lowestOffset = 1<<32L
##        for lump in structure.lumps:
##            if lump.offset < lowestOffset:
##                lowestOffset = lump.offset

        # for s in ("BSPTexInfo", "point3f"):
        #    print s, self.GetStructSize(s)

        self.faces = self.ParseLumpStructs(f, LUMP_FACES, "Face")
        self.surfedges = self.ParseLumpStructs(f, LUMP_SURFEDGES, "SurfEdge")
        self.edges = self.ParseLumpStructs(f, LUMP_EDGES, "Edge")
        self.vertexes = self.ParseLumpStructs(f, LUMP_VERTEXES, "Vertex")
        self.texInfo = self.ParseLumpStructs(f, LUMP_TEXINFO, "TexInfo")
        self.planes = self.ParseLumpStructs(f, LUMP_PLANES, "Plane")

        self.imageInfoByFileName = {}

        if False:
            self.ParseEntities(f)

    ## Parsing of the lumps.

    def ParseLumpStructs(self, f, lumpID, structName):
        l = []
        offset = self.structure.lumps[lumpID].offset
        cnt = self.structure.lumps[lumpID].length / self.GetStructSize(structName)
        self.ParseListOfStructures(f, offset, cnt, structName, l)
        return l

    def ParseEntities(self, f):
        # I read the entity lump out into a string stream.
        # This is because I have no idea how the the Plex
        # scanner will handle being given a stream with no
        # known end.
        stream = StringIO.StringIO()
        f.seek(self.structure.lumps[LUMP_ENTITIES].offset)
        stream.write(f.read(self.structure.lumps[LUMP_ENTITIES].length))
        stream.seek(0)

        parser = EntityLumpParser(stream, verbose=False)
        parser.read()

        self.entryList = parser.entryList

    def DumpEntityLump(self, f):
        f.seek(self.structure.lumps[LUMP_ENTITIES].offset)
        sys.stdout.write(f.read(self.structure.lumps[LUMP_ENTITIES].length))


    ## Helper functions.

    def GetImageInfo(self, fileName):
        fileName = fileName.lower() +".tga"
        if not self.imageInfoByFileName.has_key(fileName):
            path = os.path.join(self.dataPath, "textures", fileName)
            self.imageInfoByFileName[fileName] = texture.GetImageInfo(path)
        return self.imageInfoByFileName[fileName]

    def MakeTextureCoordinate(self, point, texInfo):
        x, y, z = normalize(point)
        imageInfo = self.GetImageInfo(texInfo.textureName)

        uAxisX, uAxisY, uAxisZ = texInfo.uAxis
        vAxisX, vAxisY, vAxisZ = texInfo.vAxis
        u = x * uAxisX + y * uAxisY + z * uAxisZ + (texInfo.uOffset / imageInfo.width)
        v = x * vAxisX + y * vAxisY + z * vAxisZ + (texInfo.vOffset / imageInfo.height)

        if texInfo.uOffset > imageInfo.width or texInfo.vOffset > imageInfo.height:
            print (texInfo.uOffset, imageInfo.width), (texInfo.vOffset, imageInfo.height)
            raise "ERROR"

        #if u < -1 or u > 1:
        #    print "##", (x,y,z), (u,v), "TEX", texInfo.uAxis, texInfo.vAxis, texInfo.uOffset, texInfo.vOffset
        return u, v

    def GetTrianglesForFace(self, faceIdx):
        class Vertex:
            def __init__(self, point, texCoord):
                self.point = point
                self.texCoord = texCoord

        l = []
        face = self.faces[faceIdx]
        texInfo = self.texInfo[face.texInfo]
        for i in range(face.numEdges):
            edgeIdx = self.surfedges[face.firstEdge + i]
            if edgeIdx > 0:
                vi = self.edges[edgeIdx][0]
            else:
                vi = self.edges[-edgeIdx][1]

            v = self.vertexes[vi]
            vertex = Vertex(v, self.MakeTextureCoordinate(v, texInfo))
            l.append(vertex)

        return PolygonTessellator(Vertex).tessellate(l)

    ## Structure definitions.

    structures = {
      "BSPLump":    DefineStructure(
        ("uint32",    "offset"),
        ("uint32",    "length"),
      ),

      "BSPHeader":  DefineStructure(
        ("string.4",  "magic"),
        ("uint32",    "version"),
        ("BSPLump",   "lumps",          19),
      ),

      "Face":       DefineStructure(
        ("uint16",      "planeNum"),
        ("uint16",      "side"),
        ("uint32",      "firstEdge"),
        ("uint16",      "numEdges"),
        ("uint16",      "texInfo"),
        # Lighting info.
        ("uchar",       "styles",       4),
        ("int32",       "lightofs"),
      ),

      "SurfEdge":   DefineListItem("int32",     "v"),
      "Edge":       DefineListItem("uint16",    "v",     2, castWith=tuple), # Vertex offsets.
      "Vertex":     DefineListItem("float",     "point", 3, castWith=tuple),

      "TexInfo":    DefineStructure(
        ("float",       "uAxis",        3),
        ("float",       "uOffset"),
        ("float",       "vAxis",        3),
        ("float",       "vOffset"),
        ("uint32",      "flags"),
        ("uint32",      "value"),
        ("string.32",   "textureName"),
        ("uint32",      "nextTexInfo"),
      ),

      "Plane":      DefineStructure(
        ("float",       "normal",       3),
        ("float",       "distance"),
        ("uint32",      "type"),
      ),
    }


## Entity lump related.

class EntityLumpObject:
    # Output a string representation of this dictionary in the
    # original BSP lump form, but mess with it and put the classname
    # first.
    def String(self, skipKeynames=None):
        s = ""
        scn = ""
        line = ""
        for k, v in self.__dict__.iteritems():
            if skipKeynames is not None and skipKeynames.has_key(k):
                continue
            line = "\"%s\" \"%s\"\n" % (k, v)
            if k == "classname":
                s += line
            else:
                scn = line
        return "{\n"+ scn + s +"}\n"

    def HTML(self):
        s = ""
        scn = ""
        line = ""
        for k, v in self.__dict__.iteritems():
            if k in ("sequence", "removed_sequence", "seqence"):
                v = "<a href=\"switch:unknown\">"+ v +"</a>"
            elif k == "gamevar":
                bits = v.split(" ")
                bits[0] = "<a href=\"gamevar:unknown\">"+ bits[0] +"</a>"
                v = " ".join(bits)
            elif k in ("command", "touchconsole"):
                bits = v.split(" ")
                if bits[0] == "gamevar":
                    bits[1] = "<a href=\"gamevar:unknown\">"+ bits[1] +"</a>"
                    v = " ".join(bits)
                elif bits[0] == "invoke":
                    bits[1] = "<a href=\"switch:unknown\">"+ bits[1] +"</a>"
                    v = " ".join(bits)
            line = "&quot;<b>%s</b>&quot; &quot;%s&quot;<br>" % (k, v)
            if k == "classname":
                scn = line
            else:
                s += line
        return "{<br>"+ scn + s +"}<br>"

class EntityLumpParser(Scanner):
    def __init__(self, f, verbose=False):
        self.verbose = verbose

        # State variables.
        self.currentOb = None
        self.currentKeyName = None

        # Result variables.
        self.entryList = []

        Scanner.__init__(self, self.lexicon, f, "xx")

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

    def StartObject(self, name):
        if self.verbose:
            print "StartObject", '"'+ name +'"'
        self.currentOb = EntityLumpObject()
        self.begin('keyName')

    def EndObject(self, text):
        if self.verbose:
            print "EndObject", text
        self.entryList.append(self.currentOb)
        self.currentOb = None
        self.begin('')

    def StoreKeyName(self, name):
        self.stringOffset = 0
        self.begin('valueString')

    def StartString(self, name):
        self.stringOffset = 1
        self.begin('valueString')

    def EndString(self, name):
        if self.verbose:
            print "EndString", '"%s"'% getattr(self.currentOb, self.currentKeyName, "FUCKED-STRING")
        self.begin('keyName')

    def StoreValueString(self, string):
        if self.stringOffset == 0 and string == '"':
            self.begin('startString')
            return

        if self.verbose:
            print "StoreValueString", self.stringOffset, '"'+ string +'"'
        if self.stringOffset == 0:
            self.currentKeyName = string
        else:
            if hasattr(self.currentOb, self.currentKeyName):
                string = getattr(self.currentOb, self.currentKeyName) + string
            setattr(self.currentOb, self.currentKeyName, string)

    lexicon = Lexicon([
        (Str('{'), StartObject),
        State('keyName', [
            (Str('{'), StartObject),
            (Str('}'), EndObject),
            (comment, IGNORE),
            (stringDelimiter, StoreKeyName),
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
        (space, IGNORE),
        (comment, IGNORE),
        (AnyChar, IGNORE)
    ])
