using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace DebugApp
{
    class Program
    {
        static void Main(string[] args)
        {
            DAT_Extract.DatArchive df = new DAT_Extract.DatArchive();

            df.OpenFile(@"D:\git\Anachronox\Anchronox\DebugApp\SPRITES.dat");


            List<string> stuff = df.GetDirectories();
            
            foreach (string s in stuff)
            {
                Console.WriteLine(s);
            }

            df.ExtractAll(@"D:\sprites");
        }
    }
}
