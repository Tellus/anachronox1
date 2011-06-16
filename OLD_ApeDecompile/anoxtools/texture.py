import os
import structures

class ImageInfo(structures.Reader):
    endianChar = "<"
    filename = None
    suffix = None
    width = None
    height = None

    def Read(self, filename):
        self.filename = filename
        self.directoryPath = os.path.dirname(filename)

        f = open(filename, "rb")
        try:
            self.ParseFile(f)
        finally:
            f.close()

class TGAImageInfo(ImageInfo):
    def ParseFile(self, f):
        self.identsize = self.ReadValue(f, "uchar")
        self.colourmaptype = self.ReadValue(f, "uchar")
        self.imagetype = self.ReadValue(f, "uchar")

        self.colourmapstart = self.ReadValue(f, "int16")
        self.colourmaplength = self.ReadValue(f, "int16")
        self.colourmapbits = self.ReadValue(f, "uchar")

        self.xstart = self.ReadValue(f, "int16")
        self.ystart = self.ReadValue(f, "int16")
        self.width = self.ReadValue(f, "int16")
        self.height = self.ReadValue(f, "int16")

class PNGImageInfo(ImageInfo):
    endianChar = ">"
    headerBytes = [ 137, 80, 78, 71, 13, 10, 26, 10 ]
    def ParseFile(self, f):
        for i in range(len(self.headerBytes)):
            v = self.ReadValue(f, "uchar")
            if v != self.headerBytes[i]:
                raise RuntimeError("Unexpected PNG header byte", i, "expected:", self.headerBytes[i], "got:", v)

        while 1:
            chunkType, chunkLength = self.ReadChunkHeader(f)
            if chunkType == "IHD":
                self.width = self.ReadValue(f, "int")
                self.height = self.ReadValue(f, "int")
                self.bitdepth = self.ReadValue(f, "uchar")
                self.colortype = self.ReadValue(f, "uchar")
                self.compressiontype = self.ReadValue(f, "uchar")
                self.filtertype = self.ReadValue(f, "uchar")
                self.interlacetype = self.ReadValue(f, "uchar")
                return
            elif chunkType == "IEN":
                return
            else:
                f.read(chunkLength)
            chunkCRC = self.ReadValue(f, "ulong")

    def ReadChunkHeader(self, f):
        chunkLength = self.ReadValue(f, "ulong")
        chunkType = self.ReadValue(f, "string.4")
        return chunkType, chunkLength

classBySuffix = {
    "tga": TGAImageInfo,
    "png": PNGImageInfo,
}

suffixOrder = [ "tga", "png" ]

def GetImageInfo(filename):
    suffixIdx = filename.rfind(".")
    suffix = filename[suffixIdx+1:].lower()

    if not classBySuffix.has_key(suffix):
        # Some skin names are for BMP files. We need to look for TGA or PNG replacements.
        dirPath, baseName = os.path.split(filename)
        prefix = filename[:suffixIdx]
        for newSuffix in suffixOrder:
            newFilename = os.path.join(dirPath, prefix +"."+ newSuffix)
            if os.path.exists(newFilename):
                filename = newFilename
                suffix = newSuffix
                break
        else:
            raise RuntimeError("Unknown image suffix", suffix, prefix, baseName)

    info = classBySuffix[suffix](None)
    info.suffix = suffix
    info.Read(filename)

    return info

def AdjustMeasure(v):
    measure = 2.0
    limit = 2**16
    while measure < limit:
        newMeasure = measure * 2.0
        if v == measure:
            return v
        elif v < newMeasure:
            return newMeasure
        measure = newMeasure
