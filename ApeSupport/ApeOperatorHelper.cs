using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Reflection;

namespace ApeSupport
{
    public class ApeOperatorHelper
    {
        private Dictionary<EApeOperators, string> _stringValues;

        /// <summary>
        /// Returns the proper APE string representation of a EApeOperator enum value.
        /// Additionally, it'll perfectly match the operator itself so no key skewing
        /// should occur.
        /// </summary>
        /// <param name="value">EApeOperator value to get the string equivalent for.</param>
        /// <returns>String representation, for for decompiled APE.</returns>
        /// <remarks>See EApeOperators and their attributes for the string representations.</remarks>
        public string this[EApeOperators value]
        {
            get
            {
                string output = null;
                    
                //Check first in our cached results...
                if (_stringValues.ContainsKey(value))
                {
                    // output = (_stringValues[value] as StringValueAttribute).Value;
                    output = _stringValues[value];
                }
                else
                {
                    Type type = value.GetType();

                    //in the field's custom attributes

                    // Retrieve the field corresponding to the value passed. Recall that
                    // since we're working with enums every enum value will look like a
                    // field.
                    FieldInfo enumInfo = type.GetField(value.ToString());

                    StringValueAttribute[] attrs = enumInfo.GetCustomAttributes(typeof(StringValueAttribute), false) as StringValueAttribute[];

                    if (attrs.Length > 0)
                    {
                        _stringValues.Add(value, attrs[0].Value);
                        output = attrs[0].Value;
                    }
                }

                return output;
            }
        }
    }
}
