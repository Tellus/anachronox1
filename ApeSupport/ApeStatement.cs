using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ApeSupport
{
    /// <summary>
    /// This class represents a generalized statement in APE.
    /// I'm not 100% on the design choice of this one, but if I can retrofit Richard's approach
    /// to a more modular one it should be fine.
    /// ~Joe
    /// </summary>
    class ApeStatement
    {
        /// <summary>
        /// Name of the statement. More appropriately, this will most likely be the leftmost value.
        /// </summary>
        private string _name;

        /// <summary>
        /// Name of the statement. More appropriately, this will most likely be the leftmost value.
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

        private List<object> _values;

        /// <summary>
        /// List of values associated with the statement. I'm not sure if there's need for more than
        /// one value, but let's trust Richard on this one.
        /// </summary>
        public List<object> Values
        {
            get
            {
                return _values;
            }
            set
            {
                _values = value;
            }
        }

        /// <summary>
        /// Adds a new value to the statement.
        /// Proxy for Values.Add().
        /// </summary>
        /// <param name="val">Value to add.</param>
        public void AddValue(object val)
        {
            Values.Add(val);
        }

        public ApeStatement()
        {
            Values = new List<object>();
        }

        public ApeStatement(string name)
            : this()
        {
            Name = name;
        }
    }
}
