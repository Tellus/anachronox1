using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace DatSupport
{
    /// <summary>
    /// Contains information about a single DAT file... file.
    /// </summary>
    public class DatFileInfo
    {
        /// <summary>
        /// Name of the file... nuh-duh?
        /// </summary>
	    public string FileName;

        /// <summary>
        /// Start of the file within its parent DAT.
        /// </summary>
        public UInt32 StartPos;

        /// <summary>
        /// Size of the extracted file (decompressed).
        /// </summary>
        public UInt32 Length;
	
        /// <summary>
        /// If >0 the compressed size of the file.
        /// </summary>
        public UInt32 Compressed;

        /// <summary>
        /// No clue, possibly checksum.
        /// </summary>
        public UInt32 Unknown;

        public DatFileInfo()
        {
            FileName = "";
            StartPos = Length = Compressed = Unknown = 0;
        }

        /// <summary>
        /// Creates a new DatFileInfo object with contents derived from a byte array.
        /// </summary>
        /// <param name="infoBytes">Array of bytes that contains file info. See reference doucmentation for file structure.</param>
        public DatFileInfo(byte[] infoBytes)
        {
            // Bitconverter converts to hex when we want strings from bytes.
            // Instead, we convert bytes separately to chars and add them to the string.
            byte b;
            for (int i = 0; i < 128; i++)
            {
                b = infoBytes[i];
                if (b > 0)
                {
                    
                    FileName += BitConverter.ToChar(new byte[] {b, 0}, 0);
                }
            }

            int intSize = sizeof(UInt32);
            byte[] fragment = new byte[intSize];

            // Copy StartPos.
            Array.ConstrainedCopy(infoBytes, 128, fragment, 0, intSize);
            StartPos = BitConverter.ToUInt32(fragment, 0);

            // Copy Length/size.
            Array.ConstrainedCopy(infoBytes, 128 + intSize * 1, fragment, 0, intSize);
            Length = BitConverter.ToUInt32(fragment, 0);

            Array.ConstrainedCopy(infoBytes, 128 + intSize * 2, fragment, 0, intSize);
            Compressed = BitConverter.ToUInt32(fragment, 0);

            return;
        }

        /// <summary>
        /// Retrieves the directory path from the root of the DAT file to the file itself.
        /// </summary>
        /// <returns>A list of directory names, traversing from root out to the file.</returns>
        public List<string> GetDirectoryPath()
        {
            List<string> retList = new List<string>();
            String path = FileName;
            // Always add the default root... maybe?
            // retList.Add(".");
            while (path.Contains(@"\"))
            {
                retList.Add(path.Substring(0, path.IndexOf(@"\")));
                path = path.Substring(path.IndexOf(@"\") + 1);
            }

            return retList;
        }
    }
}
