using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ApeSupport
{
    /// <summary>
    /// Represents all simple APE commands (Richard put them in stringCommands). Possibly there are
    /// others beyond the 16 he has put in the collection.
    /// </summary>
    class SimpleApeCommand : ApeCommand
    {
        public SimpleApeCommand()
            : base(-1, "<VARIABLE>")
        { }

        public override void Execute(System.IO.FileStream input)
        {
            // We assume that ApeFile checked the command as valid within ApeCore.
        }
    }
}
