using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Reflection;
using System.IO;

namespace ApeSupport
{
    /// <summary>
    /// Contains an amount of static methods used by ApeFile (and possibly other assemblies) for APE-specific conversions.
    /// Command/bytecode constants and the like is also defined herein.
    /// </summary>
    public static class ApeCore
    {
        /// <summary>
        /// The Operators member offers methods to translate operator enums to their
        /// APE decompiled counterparts.
        /// </summary>
        /// <seealso cref="ApeOperatorHelper[]"/>
        public static ApeOperatorHelper Operators;

        /// <summary>
        /// Dictionary of all known Commands. Initialized during startup.
        /// Keyed by bytecode.
        /// </summary>
        public static Dictionary<Int32, ApeCommand> Commands;

        /// <summary>
        /// Collection of simple commands. There are about 16 of them in Richard's model,
        /// possibly even more if the other bytecodes ar analyzed.
        /// </summary>
        public static Dictionary<Int32, StringCommandStruct> StringCommands;

        static ApeCore()
        {
            InitializeOperatorsList();
            InitializeCommands();
            InitializeStringCommands();
        }

        /// <summary>
        /// Initializes the Commands collection with all commands in the ApeCommand assembly
        /// (this project).
        /// </summary>
        static public void InitializeCommands()
        {
            // Create new Dictionary (of course).
            Commands = new Dictionary<int, ApeCommand>();

            // Get the proper Type object.
            Type cBase = typeof(ApeCommand);

            // I love this kind of code. Get all subtypes of ApeCommand from the current assembly.
            List<Type> types = Assembly.GetAssembly(cBase).GetTypes().ToList()
                                       .Where(t => t.IsSubclassOf(cBase)).ToList();

            // Now we create a new instance of all the commands, one by one, and add them correctly
            // to the Commands collection.
            ApeCommand created;
            foreach (Type t in types)
            {
                created = _createCommandInstance(t);
                Commands.Add(created.Bytecode, created);
            }

            if (Commands.Count == 0) throw new Exception("ApeCore failed to load any commands.");
        }

        /// <summary>
        /// Creates a new instance of a given type. Used by InitializeCommands().
        /// </summary>
        /// <param name="ofCommand">Type of ApeCommand to initialize.</param>
        /// <returns>A new instance of the requested command type.</returns>
        static private ApeCommand _createCommandInstance(Type ofCommand)
        {
            // We can't limit Type types in parameters, so make sure the passed type is valid.
            if (!ofCommand.IsSubclassOf(typeof(ApeCommand))) throw new ArgumentException("The passed Type to initialize is not an ApeCommand derivative.");

            // Get the non-parametrized constructor.
            ConstructorInfo ci = ofCommand.GetConstructor(new Type[] { });

            // Create a new instance, cast it as an ApeCommand and return it.
            return ci.Invoke(new object[] { }) as ApeCommand;
        }

        /// <summary>
        /// Creates the list of operators known in APE.
        /// </summary>
        /// <remarks>WIP/TODO/NOT DONE</remarks>
        static public void InitializeOperatorsList()
        {
            Operators = new ApeOperatorHelper();
        }

        static public void InitializeStringCommands()
        {
            // Shorthand because my hand will hurt otherwise.
            Dictionary<Int32, StringCommandStruct> c = StringCommands;

            c.Add(4, new StringCommandStruct("goto", false));
            c.Add(5, new StringCommandStruct("gosub", false));
            c.Add(6, new StringCommandStruct("console", true));
            c.Add(7, new StringCommandStruct("echo", true));
            c.Add(8, new StringCommandStruct("target", false));
            c.Add(9, new StringCommandStruct("pathtarget", false));
            c.Add(10, new StringCommandStruct("extern", false));
            c.Add(12, new StringCommandStruct("playambient", false));
            c.Add(13, new StringCommandStruct("loopambient", false));
            c.Add(14, new StringCommandStruct("stopambient", false));
            c.Add(15, new StringCommandStruct("playscene", false));
            c.Add(16, new StringCommandStruct("loopscene", false));
            c.Add(17, new StringCommandStruct("stopscene", false));
            c.Add(18, new StringCommandStruct("chainscripts", false));
            c.Add(19, new StringCommandStruct("closewindow", false));
            c.Add(20, new StringCommandStruct("loadape", true));
        }

        /// <summary>
        /// Converts a label in compiled form and turns it into a decompiled label.
        /// </summary>
        /// <param name="v">Label to convert. Should this be in some integer format?</param>
        /// <returns>Pure-text version of the label in the form BANK:ENTRY.</returns>
        static public string IntegerToLabel(Int64 label)
        {
            // The principle is quite simple. If 0, it's a 0:0 label (special EOF label).
            if (label == 0)
            {
                return "0:0";
            }
            else
            {
                string s = label.ToString();
                string bank, entry; // The bank and the entry.
                bank = s.Substring(0, s.Length / 2);
                entry = s.Substring(s.Length / 2);
                return String.Format("{0}:{1}", bank, entry);
            }
        }

        /// <summary>
        /// Reads a number of bytes from a FileStream corresponding to the size of the passed generic type T.
        /// </summary>
        /// <typeparam name="T">The generic type to retrieve. Only works for types supported by BitConverter.</typeparam>
        /// <param name="f">FileStream to read from. File position will *not* be preserved.</param>
        /// <returns>A converted T matching the requested from the file.</returns>
        static public T ReadValue<T>(FileStream f)
        {
            // Retrieve the byte size of target type.
            int size = System.Runtime.InteropServices.Marshal.SizeOf(typeof(T));

            // Prepare an array with the space for the read.
            byte[] b = new byte[size];

            // Read the data.
            f.Read(b, 0, size);

            // Special branching case. We want byte support, but it is a type that cannot be handled
            // by BitConverter (because... well... bitconverter converts FROM bytes.
            if (typeof(T) == typeof(Byte))
            {
                // The compiler dislikes cast from byte to T although we know it's valid byte to byte.
                // We use object as a middleman. Ugly, but safe given the context.
                object tmp = (object)b[0];
                return (T)tmp;
            }
            else
            {
                // Convert correctly and return.
                return (T)_getCastMethod(typeof(T)).Invoke(null, new object[] { b, 0 });
            }
        }

        /// <summary>
        /// Uses reflection to retrieve the appropriate conversion method from BitConverter
        /// to convert the specified type.
        /// </summary>
        /// <param name="t">Type to find a conversion for.</param>
        /// <returns></returns>
        /// <remarks>Difference between C# type and framework type (e.g. float vs. single)
        /// might cause problems, I'm not sure. It should, however, work for 6 of Richard's 8 original
        /// methods. The latter two have been redone in ReadQuotedString and ReadString.</remarks>
        private static MethodInfo _getCastMethod(Type t)
        {
            // Retrieve all methods from BitConverter that are static and contain the name of the
            // type we're working with. This will fail with some value types, I think.
            List<MethodInfo> meths = typeof(BitConverter).GetMethods()
                                           .Where(meth => meth.Name.Contains(t.Name))
                                           .Where(meth => meth.IsStatic == true).ToList();

            // Hopefully, we only have one hit... and one hit exactly.
            if (meths.Count == 1)
            {
                // This is good.
                return meths.First();
            }
            else if (meths.Count == 0)
            {
                throw new InvalidOperationException("No conversion methods found for the type " + t.Name + ".");
            }
            else
            {
                throw new InvalidOperationException("Too many hits for type " + t.Name + ".");
            }
        }

        /// <summary>
        /// Specialized read method for reading quotedstrings from a binary APE file.
        /// This is a proxy for ReadString with unescaped characters.
        /// </summary>
        /// <param name="input">File to read from. Pointer position will NOT be reversed.</param>
        /// <param name="numBytes">Number of bytes to read.</param>
        static public string ReadQuotedString(FileStream input, int numBytes = 1)
        {
            string s = ReadString(input, numBytes);

            s.Replace("\\", "\\\\")
             .Replace("\n", "\\n")
             .Replace("\"", "\\\"");

            return s;
        }

        /// <summary>
        /// Specialized read method for reading strings from a binary APE file.
        /// </summary>
        /// <param name="input">File to read from. Pointer position will NOT be reset.</param>
        /// <param name="numBytes">Number of bytes to read. If omitted, the next Int32 in the filestream
        /// is assumed to contain string length.</param>
        static public string ReadString(FileStream input, int numBytes = -1)
        {
            // If numbytes have been left out, we make the assumption that the first integer gives us
            // the string's length.
            if (numBytes == -1)
            {
                numBytes = ReadValue<Int32>(input);
            }
            else if (numBytes <= 0)
            {
                throw new ArgumentOutOfRangeException("The passed number of of bytes (" + numBytes + ") is invalid. Use a positive value.");
            }

            // Prepare the output byte array.
            byte[] bytes = new byte[numBytes];

            // Read as many elements from the stream as requsted. Minus one. We expect that one to be 0x00.
            input.Read(bytes, 0, numBytes-1);

            // Convert the array to a string. This may result in really ugly strings.
            string s = BitConverter.ToString(bytes, 0);

            input.ReadByte(); // Disregard a byte.

            return s;
        }

        /// <summary>
        /// Retrieves a known ApeCommand instance or null.
        /// </summary>
        /// <param name="bytecode">Bytecode of the requested command.</param>
        /// <returns>ApeCommand instance from Commands or null.</returns>
        static public ApeCommand GetApeCommand(Int32 bytecode)
        {
            // If the complex command list (Commands) contains the command, return it.
            // If *not*, see if the simple command list (StringCommands) has it. If that
            // is the case, prep SimpleApeCommand for that simple command and return it.
            if (Commands.ContainsKey(bytecode))
            {
                return Commands[bytecode];
            }
            else if (StringCommands.ContainsKey(bytecode))
            {
                // Prepare the SimpleApeCommand instance with the bytecode and name of the requested
                // command.
                Commands[-1].Bytecode = bytecode;
                Commands[-1].Name = StringCommands[bytecode].Name;
                return Commands[-1];
            }
            else
            {
                return null;
            }
        }
    }

    /// <summary>
    /// Simple struct of name and quote modifier for simple one-parameter APE commands.
    /// </summary>
    public struct StringCommandStruct
    {
        /// <summary>
        /// Name of the command in question.
        /// </summary>
        public string Name;

        /// <summary>
        /// True if the value for the command should be quoted, false otherwise.
        /// </summary>
        public bool IsQuoted;

        public StringCommandStruct(string name, bool quoted)
        {
            Name = name;
            IsQuoted = quoted;
        }
    }
}
