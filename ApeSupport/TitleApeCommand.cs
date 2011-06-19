using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace ApeSupport
{
    /// <summary>
    /// Class for the "title" APE command.
    /// </summary>
    class TitleApeCommand : ApeCommand
    {
        public TitleApeCommand()
            : base(84, "title") { }

        public override void Execute(FileStream input)
        {
            /* I've skipped the following code pieces from Richard's work so far:
             * conditions = []
             * while structures.ReadLone(input) == 1:
             *      conditions.append(ExpressionValue(f))
             *      
             * */

            List<object> conditions = new List<object>();

            while (ApeCore.ReadValue<long>(input) == 1)
            {

            }

            ApeStatement st = new ApeStatement(Name);
            


            return;
        }
    }
}
