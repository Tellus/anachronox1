using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace DAT_Extract
{
    /// <summary>
    /// Struct class for the header of a DAT file.
    /// </summary>
    class DatHeader
    {
        /// <summary>
        /// Id of the file. Should read as "ADAT".
        /// </summary>
        public char[] Id;

        /// <summary>
        /// Position in the file of the information segment.
        /// </summary>
        public UInt32 FileInfoPosition;

        /// <summary>
        /// ... length of the file?
        /// </summary>
        public UInt32 FileLength;

        /// <summary>
        /// Version number? It's always 9.
        /// </summary>
        public UInt32 Unknown;

        public DatHeader()
        {
            Id = new char[4];
        }

        public Boolean IsValidDat
        {
            get
            {
                string checker = "";

                foreach (char c in Id)
                {
                    checker += c.ToString();
                }

                if (checker == "ADAT")
                {
                    return true;
                }
                else
                {
                    return false;
                }
            }
        }
    }
}
