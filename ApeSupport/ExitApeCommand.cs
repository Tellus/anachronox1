using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ApeSupport
{
    /// <summary>
    /// APE command used to break from a segment (usually #window or #switch).
    /// </summary>
    class ExitApeCommand : ApeCommand
    {
        public ExitApeCommand()
            : base(69, "exit")
        { }

        public override void Execute(System.IO.FileStream input)
        {
            ReturnCode = 0;
            return;
        }
    }
    
}
