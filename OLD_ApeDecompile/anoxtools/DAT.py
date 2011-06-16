import sys, zlib, os
import structures

class DATReader(structures.Reader):
    endianChar = "<"

    def __init__(self, f):
        self.ParseFile(f)

    def ParseFile(self, f):
        self.header = self.ReadStruct(f, "DATHeader")
        self.WriteStructure(sys.stdout, self.header)

        self.fileEntriesByName = {}
        fileCount = self.header.dirLength / self.GetStructSize("FileEntry")
        f.seek(self.header.dirOffset)
        for i in xrange(fileCount):
            fileEntry = self.ReadStruct(f, "FileEntry")
            self.fileEntriesByName[fileEntry.filename] = fileEntry

    def GetCompressedFile(self, filename):
        fileEntry = self.fileEntriesByName[filename]
        f.seek(fileEntry.fileOffset)
        return f.read(fileEntry.compressedFileLength)

    def GetDecompressedFile(self, filename):
        compressedData = self.GetCompressedFile(filename)
        data = zlib.decompress(compressedData)

        fileEntry = self.fileEntriesByName[filename]
        assert len(data) == fileEntry.decompressedFileLength
        
        return data

    # ------------------------------------------------------------------------

    structures = {
      "DATHeader": structures.DefineStructure(
        ("string.4",   "ident"),
        ("uint32",     "dirOffset"),
        ("uint32",     "dirLength"),
        ("uint32",     "unknown"),
      ),
      "FileEntry": structures.DefineStructure(
        ("string.128", "filename"),
        ("uint32",     "fileOffset"),
        ("uint32",     "decompressedFileLength"),
        ("uint32",     "compressedFileLength"),
        ("uint32",     "unknown"),
      ),
    }

if __name__ == "__main__":
    action = "extract all ape files"
    if action == "random decompress":
        f = open("..\\anoxdata\\GAMEFLOW.dat", 'rb')
        dr = DATReader(f)

        fileEntry = None
        for filename, entry in dr.fileEntriesByName.iteritems():
            if filename.endswith(".ape"):
                fileEntry = entry

        if fileEntry is None:
            raise RuntimeError("No APE script files found.")

        data = dr.GetDecompressedFile(fileEntry.filename)
        print "Read", fileEntry.filename, len(data)
    elif action == "extract all ape files":
        f = open("..\\anoxdata\\GAMEFLOW.dat", 'rb')
        dr = DATReader(f)
        extractPath = "..\\anoxdata\\"

        for filename, entry in dr.fileEntriesByName.iteritems():
            if filename.endswith(".ape"):
                if filename.find("\\") == -1:
                    extractFilename = os.path.join(extractPath, filename)
                    if not os.path.exists(extractFilename):
                        data = dr.GetDecompressedFile(filename)
                        f2 = open(extractFilename, "wb")
                        f2.write(data)
                        f2.close()
                        print filename, len(data)
