using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace ApeSupport
{
    /// <summary>
    /// The ApeFile class represents a single ApeFile with access to opening (herin lies decompilation) and recompilation. 
    /// This would also be the perfect place to place export code for specific intermediate languages.
    /// ApeFile relies on ApeCore for core functionality.
    /// </summary>
    public class ApeFile
    {
        private string _sourcePath, _targetPath;
        private FileStream _sourceFile, _targetFile;

        /// <summary>
        /// Path to the file being opened for reading (decompilation).
        /// </summary>
        public string SourcePath
        {
            get
            {
                return _sourcePath;
            }
            set
            {
                _sourcePath = value;
            }
        }

        /// <summary>
        /// Path to the file being opened for writing (compilation).
        /// </summary>
        public string TargetPath
        {
            get
            {
                return _targetPath;
            }
            set
            {
                _targetPath = value;
            }
        }

        /// <summary>
        /// FileStream being read from (compiled APE file, most likely).
        /// </summary>
        public FileStream SourceFile
        {
            get
            {
                return _sourceFile;
            }
            set
            {
                _sourceFile = value;
            }
        }

        /// <summary>
        /// FileStream being written to (most likely decompiled APE file in making).
        /// </summary>
        public FileStream targetFile
        {
            get
            {
                return _targetFile;
            }
            set
            {
                _targetFile = value;
            }
        }

        private List<Object> _windows;

        /// <summary>
        /// List of all #window entries in the file.
        /// </summary>
        public List<Object> Windows
        {
            get
            {
                return _windows;
            }
            set
            {
                _windows = value;
            }
        }

        private List<Object> _switches;

        /// <summary>
        /// List of all #switch entries in the file.
        /// </summary>
        public List<Object> Switches
        {
            get
            {
                return _switches;
            }
            set
            {
                _switches = value;
            }
        }

        /// <summary>
        /// I think this ought to be incorporated into Switches as a Dictionary in total.
        /// ... who knows.
        /// </summary>
        private List<Object> _switchesByLabel;

        /// <summary>
        /// I think this ought to be incorporated into Switches as a Dictionary in total.
        /// ... who knows.
        /// </summary>
        public List<Object> SwitchesByLabel
        {
            get
            {
                return _switchesByLabel;
            }
            set
            {
                _switchesByLabel = value;
            }
        }

        /// <summary>
        /// The size of the source file.
        /// </summary>
        public Int64 FileSize
        {
            get
            {
                if (SourceFile == null)
                {
                    return 0;
                }
                else
                {
                    return SourceFile.Length;
                }
            }
        }

        public ApeFile()
        {

        }

        public ApeFile(string sourcePath)
            : this()
        {
            try
            {
                SourceFile = new FileStream(sourcePath, FileMode.Open);
            }
            catch (FileNotFoundException e)
            {
                throw e;
            }
        }

        /// <summary>
        /// Decompiles the entire file, start to finish.
        /// </summary>
        public void Decompile()
        {
            // Make sure the file reference is good
            if (SourceFile == null)
            {
                __fErr();
            }
            
            // Reset position to start.
            SourceFile.Seek(0, SeekOrigin.Begin);

            // Check file validity.
            if (!IsValidSource(false))
            {
                throw new ApeBinaryDataException("The passed APE file is not a valid binary file.");
            }

            // Array for the bytes containing label data at each loop.
            byte[] labelBytes = new byte[sizeof(Int32)]; // The labels are integer-sized 32-bit.

            // Do window looping. Recall that in a compiled APE file, all windows are before the
            // switches... apparently.
            bool done = false;
            while (!done)
            {
                SourceFile.Read(labelBytes, 0, sizeof(Int32));

                if (BitConverter.ToInt32(labelBytes, 0) != 0)
                {
                    DecompileWindow(BitConverter.ToInt32(labelBytes, 0));
                }
                else
                {
                    // We reverse the file pointer to before reading the label so the next loop will work.
                    SourceFile.Seek(-sizeof(Int32), SeekOrigin.Current);
                    done = true;
                }
            }

            // Re-initialize byte array.
            labelBytes = new byte[sizeof(Int64)];

            // Do switch looping.
            done = false;
            while (!done)
            {
                SourceFile.Read(labelBytes, 0, sizeof(Int32));

                // A porting issue here: the original Python compares int to uint (it seems).
                // The code here is rewritten to measure against an unsigned version.
                if (BitConverter.ToUInt32(labelBytes, 0) != 0xFFFFFFFE)
                {
                    DecompileSwitch(BitConverter.ToInt32(labelBytes, 0));
                    // Read switch.
                }
                else
                {
                    // Break.
                    done = true;
                }
            }

            // Aaand done!
            return;
        }

        /// <summary>
        /// Decompiles a switch segment of the APE file.
        /// This version expects SourceFile.Position to be right past the starting point of the segment.
        /// </summary>
        /// <param name="label"></param>
        protected void DecompileSwitch(Int32 label)
        {

        }

        /// <summary>
        /// Decompiles a switch segment of the APE file.
        /// This version takes a file position to start from.
        /// </summary>
        /// <param name="label">Integer version of the label. Will be decompiled by the method itself.</param>
        /// <param name="filePos">The file position right after the label of the switch.</param>
        /// <param name="resetFilePos">Whether to reset the streams position after decompilation.</param>
        protected void DecompileSwitch(Int32 label, long filePos, bool resetFilePos = false)
        {
            // Mandatory check.
            if (SourceFile == null) __fErr();

            // Store the previous file position.
            long prevPosition = SourceFile.Position;

            // Call the base method for this.
            DecompileSwitch(label);

            if (resetFilePos) SourceFile.Position = prevPosition;

            return;
        }

        /// <summary>
        /// Decompiles a window segment of the currently opened APE file.
        /// </summary>
        /// <param name="label">Integer version of the label. Will be decompiled by the method itself.</param>
        protected void DecompileWindow(Int32 label)
        {
            // Not exactly sure what this is for just yet.
            List<object> references = new List<object>();

            // List of nested statements in the window.
            List<object> nestedStatements = new List<object>();

            // Start decompiling commands for the window.
            DecompileCommands(nestedStatements, references);

            string strLabel = ApeCore.IntegerToLabel(label);
        }

        /// <summary>
        /// Decompile a window starting at SourceFile's specific position.
        /// </summary>
        /// <param name="label">Integer version of the label. Will be decompiled by the method itself.</param>
        /// <param name="filePos">The file position right after the label of the switch.</param>
        /// <param name="resetFilePos">Whether to reset the streams position after decompilation.</param>
        protected void DecompileWindow(Int32 label, long filePos, bool resetFilePos = false)
        {
            // Mandatory check.
            if (SourceFile == null) __fErr();

            // Store the previous file position.
            long prevPosition = SourceFile.Position;

            // Call the base method for this.
            DecompileWindow(label);

            if (resetFilePos) SourceFile.Position = prevPosition;

            return;
        }

        /// <summary>
        /// Decompiles all commands until the exit command (bytecode 69) is reached.
        /// </summary>
        /// <param name="nestingLevel"></param>
        /// <param name="refs"></param>
        protected void DecompileCommands(List<object> nestingLevel, List<object> refs)
        {
            bool done = false;

            while (!done)
            {
                done = DecompileCommand(nestingLevel, refs);
            }
        }

        /// <summary>
        /// Decompiles a single command from the current point of SourceFile.
        /// </summary>
        /// <param name="nestingLevel">Current level of ... nesting? ... we're working in.</param>
        /// <param name="refs">References. Still no clue.</param>
        /// <remarks>
        /// I've no idea how the two parameters should be used. May not be used in my variation.
        /// WIP/TODO/NOT DONE/UNFINISHED.
        /// </remarks>
        /// <returns>EOF bool indicating whether this command was the last in current segment.</returns>
        protected bool DecompileCommand(List<object> nestingLevel, List<object> refs)
        {
            // Short-lived byte array to contain our next command code.
            byte[] commandCodeAsByte = new byte[sizeof(Int32)]; // One byte in a command. Really!

            // Read the next command code into the array.
            SourceFile.Read(commandCodeAsByte, 0, 1);

            // Convert the command code to something more manageable, keywise.
            Int32 commandCode = BitConverter.ToInt32(commandCodeAsByte, 0);

            // Is it a known command?
            if (ApeCore.Commands.ContainsKey(commandCode))
            {
                ApeCore.Commands[commandCode].Execute(SourceFile);
            }
            else
            {
                // Throw the appropriate exception if we haven't any way of decompiling said command.
                throw new NotImplementedException(String.Format("The command matching bytecode {0} has not yet been implemented or does not exist.", commandCode));
            }

            return false;
        }

        /// <summary>
        /// Determines whether the currently open file is a valid compiled APE file.
        /// </summary>
        /// <param name="resetFilePos">Determines whether to reset the file pointer after check.</param>
        public bool IsValidSource(bool resetFilePos = false)
        {
            if (SourceFile == null)
            {
                __fErr();
            }
            else
            {
                // The return value.
                bool retValue;

                // Store the position until we're done.
                long prevPos = SourceFile.Position;
                // Start from the top.
                SourceFile.Seek(0, SeekOrigin.Begin);
                    
                // Size of an integer. Note we work with fixed-size integers to ensure future-support.
                int iSize = sizeof(Int32);

                // Array of bytes we use to contain read data.
                Byte[] bitHeader1 = new Byte[iSize]; // For the first integer, should be 317
                Byte[] bitHeader2 = new Byte[iSize]; // For the second integer, should be 0xFFFFFFFF

                // Read the first 4 bytes of the file.
                SourceFile.Read(bitHeader1, 0, iSize);
                SourceFile.Read(bitHeader2, 0, iSize);

                // Check for 317.
                UInt32 header1 = BitConverter.ToUInt32(bitHeader1, 0);
                UInt32 header2 = BitConverter.ToUInt32(bitHeader2, 0);
                if (header1 != 317 || header2 != 0xFFFFFFFF)
                {
                    retValue = false;
                }
                else
                {
                    retValue = true;
                }
                    
                // Return the FileStream position to where we got it from.
                if (resetFilePos) SourceFile.Position = prevPos;

                return retValue;
            }
            // If something completely mad happened we might end here. Return false as a failsafe.
            return false;
        }

        /// <summary>
        /// Shorthand method for the countless times we MAY have to bail out due to bad FileStream references.
        /// </summary>
        private void __fErr()
        {
            throw new NullReferenceException("The source file has not been properly initialized.");
        }
    }
}
