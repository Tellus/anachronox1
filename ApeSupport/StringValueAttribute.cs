using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ApeSupport
{
    class StringValueAttribute : System.Attribute
    {
        private string _value;

        public StringValueAttribute(string newVal)
        {
            _value = newVal;
        }

        public string Value
        {
            get
            {
                return _value;
            }
        }
    }
}
