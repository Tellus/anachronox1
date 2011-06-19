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

        private Int32 _returnCode;

        /// <summary>
        /// The return code is currently only 0 or 1 depending on whether a general exit command
        /// was issued.
        /// </summary>
        /// <remarks>There are two approaches. Legacy APE only supports one real exit condition, the
        /// exit command itself (bytecode 69...). However, future revision might benefit from various
        /// branching exit statements (who knows) - it could also be used to further compress the
        /// binary format by adding in an exit flag in a bytecode instead. Given the latter option,
        /// using this form of exit status is preferable as it is both backwards and forwards compatbiel.
        /// </remarks>
        public Int32 ReturnCode
        {
            get
            {
                return _returnCode;
            }
            set
            {
                _returnCode = value;
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

        public abstract void Execute(FileStream input);
    }
}
