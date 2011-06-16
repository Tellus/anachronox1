import os
from StringIO import StringIO

import data
import structures, texture

vertexResTable = {
  0: 3,
  1: 4,
  2: 6,
}

class MeshZeroError(RuntimeError):
    pass

class Mesh:
    def __init__(self):
        self.triangles = []
        self.vertices = []

class MD2Reader(structures.Reader):
    endianChar = "<"

    def __init__(self, f):
        self.skinNames = []
        self.triangles = []
        self.textureCoords = []
        self.multipleSurfaceData = []
        self.taggedSurfaceData = []

        self.numPrimitives = 0
        self.numStrips = 0
        self.numFans = 0
        self.primitives = []

        self.meshes = []        

        self.ParseFile(f)

    def ParseFile(self, f):
        self.ParseHeaders(f)
        self.CalculateVerticeInfo()

        self.ParseListOfStructures(f, self.header.ofs_skins, self.header.num_skins, "string.64", l=self.skinNames)
        self.ParseListOfStructures(f, self.multipleSurfaceHeader.ofs_prims, self.multipleSurfaceHeader.num_prims, "MultipleSurfaceData", l=self.multipleSurfaceData)

        self.ParseFrames(f)

        # --------------------------------------------------------------------
        # Our goal is to extract a mesh.  However, it seems that some frames
        # have no vertices (all packed vertices have a value of zero).  So,
        # we go through all the animations looking for a valid one.  I have
        # a suspicion that its just some unnamed frames that are in the models.

        frameNames = self.framesByAnim.keys()
        frameNames.sort()

        import sys
        sys.stderr.write("Animation count: %d\n" % len(frameNames))
        for frameName in frameNames:
            sys.stderr.write("Animation: %s\n" % frameName)            

        frame = self.meshFrame
        meshFrameSucked = False
        try:
            self.ParseVertices(frame)
        except MeshZeroError:
            sys.stderr.write("Mesh frame sucked: %s\n" % frame.name)            
            meshFrameSucked = True

        if meshFrameSucked:
            for frameName in frameNames:
                idList = self.frameKeysByAnim[frameName]
                frame = self.framesByAnim[frameName][idList[0]]
                try:
                    self.ParseVertices(frame)
                except MeshZeroError:
                    sys.stderr.write("Mesh frame sucked: %s\n" % frame.name)            
                    continue
                break

        sys.stderr.write("Mesh frame accepted: %s %s\n" % (frame.name, self.frameKeysByAnim[frameName]))            

        # --------------------------------------------------------------------

        self.ParseListOfStructures(f, self.header.ofs_st, self.header.num_st, "TextureCoordinateData", l=self.textureCoords)        
        self.ParseListOfStructures(f, self.header.ofs_tris, self.header.num_tris, "TriangleData", l=self.triangles)
        self.ParseListOfStructures(f, self.taggedSurfaceHeader.ofs_surface, self.taggedSurfaceHeader.num_surface, "TaggedSurfaceData", l=self.taggedSurfaceData)

        self.ParsePrimitives(f)

        # Build a list of shapes, one for each surface.
        numVertices = 0
        numTriangles = 0
        primitiveIdx = 0
        for surfaceInfo in self.multipleSurfaceData:
            mesh = Mesh()
            primitiveCount = surfaceInfo.primitiveCount
            while primitiveCount:
                # Every point is the start of a triangle.  Except when there are
                # not enough points left to make a triangle.
                primitiveList = self.primitives[primitiveIdx]
                for i in range(len(primitiveList)):
                    if i < 2:
                        continue

                    # Convert the strip into triangles.
                    if i % 2:
                        pv1 = primitiveList[i-2]
                        pv2 = primitiveList[i-1]
                        pv3 = primitiveList[i]
                    else:
                        pv1 = primitiveList[i]
                        pv2 = primitiveList[i-1]
                        pv3 = primitiveList[i-2]

                    triangleVertices = []
                    vertices = (pv1, pv2, pv3)
                    for j in range(len(vertices)):
                        l = []
                        vertex, normalIdx = self.vertices[vertices[j].vertexIdx]
                        l.extend(vertex)
                        l.extend([ -v for v in data.norm1024[normalIdx] ])

                        textureFilename = os.path.join(self.directoryPath, self.skinNames[len(self.meshes)])
                        textureInfo = texture.GetImageInfo(textureFilename)
                        width, height = textureInfo.width, textureInfo.height
                        # It looks like Nebula 2 extends textures with a width or height
                        # that is not a power of 2 out to the next power of 2.  This means
                        # that if we base our texture coordinates on the "known" width and
                        # height, we get a distorted textured mesh.  So, we need to calculate
                        # our texture coordinates with this taken into account.
                        u = (vertices[j].u * width) / texture.AdjustMeasure(width)
                        v = (vertices[j].v * height) / texture.AdjustMeasure(height)

                        l.append(u)
                        l.append(v)
                        mesh.vertices.append(l)
                        triangleVertices.append(numVertices)
                        numVertices += 1
                    mesh.triangles.append(tuple(triangleVertices))
                    numTriangles += 1

                primitiveCount -= 1
                primitiveIdx += 1
            self.meshes.append(mesh)

        import sys
        meshIO = self.BuildN3D2()
        sys.stdout.write(meshIO.getvalue())
        for skinName in self.skinNames:
            sys.stderr.write(skinName +"\n")

    def GetDescription(self):
        # Build the descriptive text.
        IO = StringIO()
        printIO.write("\n")
        printIO.write("Filename:  %s\n" % os.path.basename(filename))
        printIO.write("Directory: %s\n" % os.path.dirname(filename))
        printIO.write("\n")


        printIO.write("Headers:\n")
        printIO.write("\n")

        for info in [ md2Header, md2Header3, md2Header4 ]:
            WriteStructure(printIO, info)

        printIO.write("TPrims:\n")
        for info in prims:
            WriteStructure(printIO, info)

        printIO.write("Tagged surfaces:\n")
        for info in surfaceBlocks:
            WriteStructure(printIO, info)

        printIO.write("Skins:\n")
        for i in range(len(skinNames)):
            printIO.write("  %d: %s\n" % (i, skinNames[i]))
        printIO.write("\n")

        if 0:
            printIO.write("Animations\n")
            keys = framesByAnim.keys()
            keys.sort()
            for i in range(len(framesByAnim)):
                key = keys[i]
                printIO.write("  %d: %s (%d frames)\n" % (i, key, len(framesByAnim[key])))
            printIO.write("\n")

            printIO.write("  Default frame: %s\n" % frame.name)

        printIO.write("GL commands: strips %d fans %d loops %d\n" % (strips, fans, loops))

        print printIO.getvalue()

    def ParseHeaders(self, f):
        self.header = self.ReadStruct(f, "MD2Header")
        self.multipleSurfaceHeader = self.ReadStruct(f, "MultipleSurfaceHeader")
        self.lodData = self.ReadStruct(f, "TLODData")
        self.taggedSurfaceHeader = self.ReadStruct(f, "TaggedSurfaceHeader")

    def CalculateVerticeInfo(self):
        self.frameVertexStructName = "FrameVertexData%d" % vertexResTable[self.header.vertexres]
        self.frameHeaderStructName = "FrameHeader%d" % vertexResTable[self.header.vertexres]

        headerSize = self.GetStructSize(self.frameHeaderStructName)
        vertexSize = self.GetStructSize(self.frameVertexStructName)

        self.numVertices = (self.header.framesize - headerSize + vertexSize) / vertexSize

    def ParseFrames(self, f):
        f.seek(self.header.ofs_frames)

        self.framesByAnim = {}
        self.frameKeysByAnim = {}

        meshFrames = []
        lastFrame = None
        for i in range(self.header.num_frames):
            lastFrame = frame = self.ReadStruct(f, self.frameHeaderStructName, listSizes={ self.frameVertexStructName: self.numVertices })
            nameBits = frame.name.split("_")
            try:
                frameID = int(nameBits[-1])
                frameName = ",".join(nameBits[:-1])
                if not self.framesByAnim.has_key(frameName):
                    self.framesByAnim[frameName] = { frameID: frame }
                    self.frameKeysByAnim[frameName] = [ frameID ]
                else:
                    self.framesByAnim[frameName][frameID] = frame
                    self.frameKeysByAnim[frameName].append(frameID)
            except ValueError:
                meshFrames.append(frame)

        # Order the frame ids.
        for frameName, idList in self.frameKeysByAnim.iteritems():
            idList.sort()
                
        if len(meshFrames) == 0:
            meshFrames.append(lastFrame)
        elif len(meshFrames) != 1:
            raise RuntimeError("Incorrect number of mesh frames", [ frame.name for frame in meshFrames ])

        # Pick the non-animation sequence frame for the mesh.
        self.meshFrame = meshFrames[0]

    def ParseVertices(self, frame):
        # Decode and index the existing vertices.
        self.vertices = []
        zeroCount = 0
        for j in range(len(frame.verts)):
            vertex = frame.verts[j]
            args = []
            for k in range(3):
                if vertex.v == 0:
                    zeroCount += 1
                args.append(self.DecodeVertice(self.header.vertexres, frame, vertex.v, k))
            self.vertices.append((args, vertex.normalIdx))
        if zeroCount == 3 * len(frame.verts):
            raise MeshZeroError(frame.name, self.header.vertexres)

    def ParsePrimitives(self, f):
        f.seek(self.header.ofs_glcmds)

        count = self.ReadValue(f, "int32")
        while count != 0:
            self.numPrimitives += 1

            if count > 0:
                cmdType = "strip"
                self.numStrips += 1
            else:
                cmdType = "fan"
                count = -count
                self.numFans += 1

            primitiveList = []
            for i in range(count):
                primitive = self.ReadStruct(f, "PrimitiveData")
                primitive.name = cmdType
                primitiveList.append(primitive)
            self.primitives.append(primitiveList)

            count = self.ReadValue(f, "int32")

    def DecodeVertice(self, vertexres, frame, v, i):
        vertexshift = [ 0, 11, 21 ]
        vertexmask  = [ 0x000007ff, 0x000003ff, 0x000007ff ]
        vertexmax   = [ 2047.0, 1023.0, 2047.0 ]

        if vertexres == 0:
            return v[i] * frame.scaleVector[i] + frame.translationVector[i]
        elif vertexres == 1:
            rawvert = ((v >> vertexshift[i]) & vertexmask[i])
            return rawvert * frame.scaleVector[i] + frame.translationVector[i]
        elif vertexres == 2:
            return v[i] * frame.scaleVector[i] + frame.translationVector[i]

    def BuildN3D2(self):
        meshOut = StringIO()
        meshOut.write("type n3d2\n")
        meshOut.write("numgroups %d\n" % len(self.meshes))
        meshOut.write("numvertices %d\n" % sum([ len(mesh.vertices) for mesh in self.meshes ]))
        meshOut.write("vertexwidth %d\n" % (3 + 3 + 2))
        meshOut.write("numtris %d\n" % sum([ len(mesh.triangles) for mesh in self.meshes ]))
        meshOut.write("numedges %d\n" % 0)
        meshOut.write("vertexcomps coord normal uv0\n")

        vertexCount = 0
        triangleCount = 0
        for mesh in self.meshes:
            meshOut.write("g %d %d %d %d %d %d\n" % (vertexCount, len(mesh.vertices), triangleCount, len(mesh.triangles), 0, 0))
            vertexCount += len(mesh.vertices)
            triangleCount += len(mesh.triangles)

        for mesh in self.meshes:
            for vertexData in mesh.vertices:
                meshOut.write("v " + " ".join([ str(bit) for bit in vertexData ]) +"\n")

        for mesh in self.meshes:
            for vertexOffsets in mesh.triangles:
                meshOut.write("t %d %d %d\n" % vertexOffsets)

        return meshOut

    # ------------------------------------------------------------------------

    structures = {
      "MD2Header": [                   # MD2 header.
        ("string.4",   "ident"),
        ("int16",    "version"),
        ("int16",    "vertexres"),

        ("int32",   "skinwidth"),
        ("int32",   "skinheight"),
        ("int32",   "framesize"),        # Byte size of each frame.

        ("int32",   "num_skins"),
        ("int32",   "num_xyz"),
        ("int32",   "num_st"),           # Greater than num_xyz for seams.
        ("int32",   "num_tris"),
        ("int32",   "num_glcmds"),       # Dwords in strip/fan command list.
        ("int32",   "num_frames"),

        ("int32",   "ofs_skins"),        # Each skin is a MAX_SKINNAME string.
        ("int32",   "ofs_st"),           # Byte offset from start for stverts.
        ("int32",   "ofs_tris"),         # Offset for dtriangles.
        ("int32",   "ofs_frames"),       # Offset for first frame.
        ("int32",   "ofs_glcmds"),
        ("int32",   "ofs_end"),          # End of file.
      ],

      "MultipleSurfaceHeader": [
        ("int32",   "num_prims"),
        ("int32",   "ofs_prims"),
      ],

      "TLODData": [
        ("float",   "scaleFactor", 3),
      ],

      "TaggedSurfaceHeader": [
        ("int32",   "num_surface"),
        ("int32",   "ofs_surface"),
      ],

      "TaggedSurfaceData": [
        ("string.8",   "name"),
        ("uint32",      "triangleIdx"),
      ],

      "MultipleSurfaceData": [
        ("int16",   "primitiveCount"),
      ],

      "TSkinName": [
        ("string.64",   "name"),
      ],

      # ---------------------------------------------------------

      "FrameHeader3": [
        ("float", "scaleVector", 3),
        ("float", "translationVector", 3),
        ("string.16", "name"),
        ("FrameVertexData3", "verts"),
      ],
      "FrameHeader4": [
        ("float", "scaleVector", 3),
        ("float", "translationVector", 3),
        ("string.16", "name"),
        ("FrameVertexData4", "verts"),
      ],
      "FrameHeader6": [
        ("float", "scaleVector", 3),
        ("float", "translationVector", 3),
        ("string.16", "name"),
        ("FrameVertexData6", "verts"),
      ],

      "FrameVertexData3": [
        ("uchar",    "v", 3),
        ("uint16",    "normalIdx"),
      ],
      "FrameVertexData4": [
        ("uint32",    "v"),
        ("uint16",    "normalIdx"),
      ],
      "FrameVertexData6": [
        ("uint16",    "v", 3),
        ("uint16",    "normalIdx"),
      ],

      "TextureCoordinateData": [
        ("int16", "u"),
        ("int16", "v"),
      ],

      "TriangleData": [
        ("int16", "index_xyz", 3),
        ("int16", "index_st",  3),
      ],

      "PrimitiveData": [
        ("float", "u"),
        ("float", "v"),
        ("int32", "vertexIdx"),
      ],
    }
