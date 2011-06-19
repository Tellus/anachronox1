using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ApeSupport
{
    /// <summary>
    /// Represents the general concept of windows and switches.
    /// </summary>
    class ApeSegment
    {
        private Int16 _bank, _entry;

        /// <summary>
        /// The Bank value of the segment.
        /// </summary>
        public Int16 Bank
        {
            get
            {
                return _bank;
            }
            set
            {
                _bank = value;
            }
        }

        /// <summary>
        /// Entry value of the segment.
        /// </summary>
        public Int16 Entry
        {
            get
            {
                return _entry;
            }
            set
            {
                _entry = value;
            }
        }

        /// <summary>
        /// The label of the segment is the identifier of it in both binary and pure-text form.
        /// </summary>
        public Int32 Label
        {
            get
            {
                // Add the two label parts as a string and parse into a larger int size... will this work?
                return Int32.Parse(Bank.ToString() + Entry.ToString());
            }
            set
            {
                // This code may fail. I haven't made sure the string splitting goes without issue.
                string str = ApeCore.IntegerToLabel(value);
                Bank = Int16.Parse(str.Substring(0, str.IndexOf(':')));
                Entry = Int16.Parse(str.Substring(str.IndexOf(':')));
            }
        }
    }
}
