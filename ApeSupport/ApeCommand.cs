using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace ApeSupport
{
    /// <summary>
    /// A generalized class for APE commands. By using reflection we can later retrieve all subclasses
    /// of this class to assemble a complete bytecode library and *dynamically* decompile according to
    /// that commands class definition.
    /// Two upshots:
    /// 1. MUCH more readable code in calling sources.
    /// 2. Future-proof. If we should decide to expand upon APE itself we simply create new classes
    ///        that inherit from this and it'll automatically be used at compile- and decompile-time.
    /// </summary>
    public abstract class ApeCommand
    {
        /// <summary>
        /// The bytecode for the command as found in compiled formats.
        /// </summary>
        private Int32 _bytecode;

        /// <summary>
        /// The bytecode for the command as found in compiled formats.
        /// </summary>
        public Int32 Bytecode
        {
            get
            {
                return _bytecode;
            }
            set
            {
                _bytecode = value;
            }
        }

        /// <summary>
        /// Human-readable name of the command.
        /// </summary>
        private string _name;

        /// <summary>
        /// Human-readable name of the command.
        /// </summary>
        public string Name
        {
            get
            {
                return _name;
            }
            set
            {
                _name = value;
            }
        }

        /// <summary>
        /// Constructor for a new ApeCommand.
        /// </summary>
        /// <param name="bytecode">Bytecode to set for the command.</param>
        public ApeCommand(Int32 bytecode, string name)
        {
            Bytecode = bytecode;
            Name = name;
        }

        public byte[] Compile(string input)
        {
            return new byte[0];
        }

        public void Decompile(FileStream input)
        {

        }

        public abstract void Execute(FileStream input);
    }
}
