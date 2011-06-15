using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ModelSupport
{
    class AnoxModelHeader
    {
        /// <summary>
        /// Denotes the size (in bytes) of the header. Very useful for loading binaries.
        /// </summary>
        public const Int32 HEADERSIZE = 16 * sizeof(Int32);

        /// <summary>
        /// Magic number... IDP2??
        /// </summary>
        public Int32 Ident;

        /// <summary>
        /// Version: must be 8 (according to MD2 specs)... possibly 9 in Anox?
        /// </summary>
        public Int32 Version;

        /// <summary>
        /// Texture Width;
        /// </summary>
        public Int32 SkinWidth;

        /// <summary>
        /// Texture Height;
        /// </summary>
        public Int32 SkinHeight;

        /// <summary>
        /// Size in bytes of a frame (wtf?!)
        /// </summary>
        public Int32 FrameSize;

        /// <summary>
        /// Number of skins.
        /// </summary>
        public Int32 SkinCount;

        /// <summary>
        /// Number of vertices per frame.
        /// </summary>
        public Int32 VerticeCount;

        /// <summary>
        /// Number of texture coordinates.
        /// </summary>
        public Int32 TextureCoordinateCount;

        /// <summary>
        /// Number of triangles.
        /// </summary>
        public Int32 TriangleCount;

        /// <summary>
        /// Number of GL commands (no clue).
        /// </summary>
        public Int32 GlCmdCount;

        /// <summary>
        /// Number of frames.
        /// </summary>
        public Int32 FrameCount;

        /// <summary>
        /// Offset skin data.
        /// </summary>
        public Int32 SkinsOffset;

        /// <summary>
        /// Offset texture coordinate data.
        /// </summary>
        public Int32 TextureCoordinateOffset;

        /// <summary>
        /// Offset frame data.
        /// </summary>
        public Int32 FramesOffset;
        
        /// <summary>
        /// GL Command data offsets (again, wtf?!).
        /// </summary>
        public Int32 GlCmdData;

        /// <summary>
        /// Offset end of file.
        /// </summary>
        public Int32 EndOfFileOffset;
    }
}
