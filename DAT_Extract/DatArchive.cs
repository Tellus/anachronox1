using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.IO.Compression;

namespace DatSupport
{
    /// <summary>
    /// The DatFile class represents a complete DAT file used for storing data/files in Anachronox.
    /// It's preliminary goal is listing and extraction, with a secondary goal to work as a virtual
    /// file system handler.
    /// </summary>
    public class DatArchive : IDisposable
    {
        /// <summary>
        /// Path to the currently opened file.
        /// </summary>
        public string FilePath;

        /// <summary>
        /// Number of files contained within the DAT.
        /// </summary>
        public UInt32 FileCount;

        /// <summary>
        /// List of all files contained in the DAT.
        /// </summary>
        public List<DatFileInfo> Files;

        /// <summary>
        /// File handle to the DAT archive. In later revisions I'll try to make this thing asynchronous.
        /// </summary>
        public FileStream DatFileHandle;

        public DatArchive()
        {
            Files = new List<DatFileInfo>();
        }

        /// <summary>
        /// Create a new DatArchive instance and immediately open a DAT file.
        /// </summary>
        /// <param name="filePath">Path to the DAT file you want to open.</param>
        public DatArchive(string filePath)
            : this()
        {
            try
            {
                OpenFile(filePath);
            }
            catch (FileNotFoundException e)
            {
                // We finish intialization, but could not open the file. We do *not* catch other unexpected exceptions.
                Console.WriteLine(@"Following error was reported opening the file: \n{0}", e.Message);
                return;
            }
        }

        /// <summary>
        /// Opens a given DAT file, placing the inventory/file view in the Files collection.
        /// </summary>
        /// <param name="filePath">Path to the .dat file to read.</param>
        public void OpenFile(string filePath)
        {
            if (!File.Exists(filePath)) throw new FileNotFoundException("The requested file could not be found.");

            // Make sure to close any earlier instance.
            if (DatFileHandle != null) DatFileHandle.Close();

            DatFileHandle = new FileStream(filePath, FileMode.Open);

            DatFileHandle.Seek(0, SeekOrigin.End);

            long size = DatFileHandle.Position;

            DatFileHandle.Seek(0, SeekOrigin.Begin);

            if (size == 0) throw new Exception("The size of the DAT file is invalid (" + size.ToString() + ").");

            /** STRUCT METHOD **/
            // DATHeader_Struct fHeader = new DATHeader_Struct();

            // datFileHandler.Read((char[])fHeader, 0, sizeof(fHeader));

            /** CLASS METHOD **/
            DatHeader fHeader = new DatHeader();

            byte[] goingIn = new byte[4];
            DatFileHandle.Read(goingIn, 0, 4);

            int i = 0;
            foreach (byte b in goingIn)
            {
                fHeader.Id[i++] = (char)b;
            }

            if (!fHeader.IsValidDat) throw new InvalidDataException("The passed file is not a valid Anachronox legacy DAT file.");
            // Console.WriteLine("Id read as {0}{1}{2}{3}.", fHeader.Id[0], fHeader.Id[1], fHeader.Id[2], fHeader.Id[3]);

            // Re-initialize the array with the number of entries matching the number of bytes in a ulong.

            // Read in the position of file information in the DAT.
            DatFileHandle.Read(goingIn, 0, 4);
            fHeader.FileInfoPosition = BitConverter.ToUInt32(goingIn, 0);
            // Console.WriteLine("FileInfoPosition read as {0}.", fHeader.FileInfoPosition);

            // Read FileLength (total length of files).
            DatFileHandle.Read(goingIn, 0, 4);
            fHeader.FileLength = BitConverter.ToUInt32(goingIn, 0);
            // Console.WriteLine("FileLength read as {0}.", fHeader.FileLength);

            // Read in unknown value. Is 9... done.
            DatFileHandle.Read(goingIn, 0, 4);
            fHeader.Unknown = BitConverter.ToUInt32(goingIn, 0);
            // Console.WriteLine("Unknown read as {0}.", fHeader.Unknown);

            FileCount = fHeader.FileLength / 144;

            /** DONE getting base info. Now load up single files. **/

            DatFileHandle.Seek(fHeader.FileInfoPosition, SeekOrigin.Begin);

            // Now read them into the list.
            byte[] tmpByte = new byte[144];
            for (int iterator = 0; iterator < FileCount; iterator++)
            {
                DatFileHandle.Read(tmpByte, 0, 144);
                Files.Add(new DatFileInfo(tmpByte));
                // Console.WriteLine(Files[iterator].FileName);
            }
        }

        /// <summary>
        /// Gets a list of all directories within the DAT file, optionally within a specific directory.
        /// </summary>
        /// <returns>List of strings, each one containing a full directory descriptor.</returns>
        public List<String> GetDirectories(string parentDir = ".")
        {
            // List to return.
            List<String> retList = new List<string>();

            // Initialize
            string dirName = "";

            // For each file info in our list, extract its full path (that is, anything leading up to a backslash).
            foreach (DatFileInfo file in Files)
            {
                // Branch: if the backslash is not a lie, use it. Otherwise, the file's in the root.
                if (file.FileName.Contains(@"\"))
                {
                    // If the double backslash (directory notifier) exists, add it if it DOESN'T exist.
                    dirName = file.FileName.Substring(0, file.FileName.LastIndexOf(@"\"));
                }
                else
                {
                    // If the double backslash is missing, add a root dir.
                    dirName = ".";
                }

                // If the directory isn't already in the list, add it.
                if (!retList.Contains(dirName)) retList.Add(dirName);
            }

            // Finally, send back the entire list.
            return retList;
        }

        /// <summary>
        /// Extracts a file from the DAT archive into a given path. Creates directories if need be.
        /// </summary>
        /// <param name="filename">Complete DAT path of the file.</param>
        /// <param name="path">Where to store the file, including new name.</param>
        /// <returns>Reference to the newly-created file.</returns>
        public FileStream ExtractFile(string filename, string path)
        {
            // First, get the directory path, make sure it exists (or create it).
            string dirPath = path.Substring(0, path.LastIndexOf(@"\"));

            if (!Directory.Exists(dirPath)) Directory.CreateDirectory(dirPath);

            // Check for file existance, print a warning (just ignore it), and then create a new file handler.
            if (File.Exists(path)) Console.WriteLine("WARNING! Target file already exists. Overwriting.");

            FileStream newFile = new FileStream(path, FileMode.Create);

            // Now we find the appropriate file in the DAT file.
            DatFileInfo datFile = GetFileInfoByPath(filename);

            if (datFile == null) throw new FileNotFoundException("The requested file could not be found in the DAT archive.");

            // AAaand now the fun. Write archive file data into the file system.
            // Byte array to store temp files in.
            byte[] data = new byte[datFile.Length];
            
            // File the file data in the archive.
            DatFileHandle.Seek(datFile.StartPos, SeekOrigin.Begin);

            // At this point we need to slightly branch depending on whether the file is compressed or not.
            if (datFile.Compressed > 0)
            {
                // Skip two bytes. Apparently, their magic numbers (... or lack thereof) bug out the Deflate stuff.
                DatFileHandle.ReadByte();
                DatFileHandle.ReadByte();

                // Create a decompression stream. By default, it'll have its pointer set at where DatFileHandle did.
                DeflateStream decomp = new DeflateStream(DatFileHandle, CompressionMode.Decompress);
                
                // Read data into the temporary byte array.
                decomp.Read(data, 0, (int)datFile.Length);
            }
            else
            {
                // Write the data to the temp array.
                DatFileHandle.Read(data, 0, data.Length);
            }

            // Finally, write to the external file handler.
            newFile.Write(data, 0, data.Length);

            // And return the file.
            return newFile;
        }

        /// <summary>
        /// Extracts all files of the archive into the target directory.
        /// </summary>
        /// <param name="targetDir">Directory to extract the files into.</param>
        public void ExtractAll(string targetDir)
        {
            if (!Directory.Exists(targetDir)) Directory.CreateDirectory(targetDir);

            foreach (DatFileInfo file in Files)
            {
                ExtractFile(file.FileName, targetDir + (targetDir.EndsWith(@"\") ? "" : @"\") + file.FileName);
            }
        }

        /// <summary>
        /// Retrieves a DAT file object from the archive by its path.
        /// </summary>
        /// <param name="path">Full path (from the root of the DAT archive) to the file.</param>
        /// <returns>The object found.</returns>
        public DatFileInfo GetFileInfoByPath(string path)
        {
            return Files.First(f => f.FileName == path);
        }

        public void Dispose()
        {
            try
            {
                DatFileHandle.Close();
            }
            finally
            {
                // Do nothing.
            }
        }
    }
}
