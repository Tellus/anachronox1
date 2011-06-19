using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using ApeSupport;

namespace DebugApp
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Name for a long: " + typeof(long).AssemblyQualifiedName);

            TestApeDecompilation();
        }

        public static void TestApeDecompilation()
        {
            ApeFile af = new ApeFile(@".\files\braintrain.ape");

            af.Decompile();
        }
        
        public static void TestDatExtraction()
        {
            DatSupport.DatArchive df = new DatSupport.DatArchive();

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
