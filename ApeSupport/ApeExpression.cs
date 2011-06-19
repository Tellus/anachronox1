using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace ApeSupport
{
    /// <summary>
    /// An APE expression is basically an expression in the form [expr1][flag][expr2] and is used
    /// in correspondance with several parsing passes in ApeFile.
    /// The class is recursive in that both left and right values in the expression can be yet
    /// another expression itself. 
    /// </summary>
    /// <remarks>
    /// I dislike the solution of using Object as a type for the values, but there are no other
    /// inheritance hierarchies that works for all combinations of ApeExpression, String and Double.
    /// Indeed, it is the *only* immediate base of both String and Double.
    /// </remarks>
    /// <example>
    /// Consider as an example, (x + y) != ((z*z) & b^2) - the base expression
    /// would contain (x + y), != and ((z*z) & b^2).
    /// LValue would be x, + and y
    /// RValue would be (z*z), & and (b^2). RValue has yet another set, RValue.LValue being z, * and z
    /// and RValue.RValue would be b^2.
    /// </example>
    class ApeExpression
    {
        /// <summary>
        /// The LValue and RValue fields are the left and right parts of an expression, respectively.
        /// </summary>
        private Object _lvalue, _rvalue;

        /// <summary>
        /// Left part of an expression. Should only be a String, a Double or another ApeExpression.
        /// </summary>
        public Object LValue
        {
            get
            {
                return _lvalue;
            }
            set
            {
                _lvalue = value;
            }
        }

        /// <summary>
        /// Right part of an expression.
        /// Should only be a String, a Double or another ApeExpression.
        /// </summary>
        public Object RValue
        {
            get
            {
                return _rvalue;
            }
            set
            {
                _rvalue = value;
            }
        }

        /// <summary>
        /// SingleValue has a combined usage. It's reference status (actual or null) determines
        /// whether the expression contains both LValue and RValue or only a single value (which,
        /// for the sake of simplicity, will be LValue).
        /// Returns LValue if there is only 1 value in the expression, null otherwise.
        /// </summary>
        public Object SingleValue
        {
            get
            {
                if (RValue != null)
                {
                    return null;
                }
                else
                {
                    return LValue;
                }
            }
            set
            {
                LValue = value;
            }
        }

        private Byte _operatorId;

        /// <summary>
        /// The operator determines the binary operator used between the two values in the expression.
        /// </summary>
        public Byte OperatorId
        {
            get
            {
                return _operatorId;
            }
            set
            {
                _operatorId = value;
            }
        }

        private Byte _valueFlags;

        /// <summary>
        /// The value flag determines the type of data in an expression.
        /// </summary>
        public Byte ValueFlags
        {
            get
            {
                return _valueFlags;
            }
            set
            {
                _valueFlags = value;
            }
        }

        /// <summary>
        /// Quick reference to the filestream we work with. Using methods with empty parameters
        /// forces us to make use of it. For some reason I feel this makes it more secure.
        /// </summary>
        protected FileStream _file;

        public ApeExpression()
        {
            _file = null;
            return;
        }

        /// <summary>
        /// Creates a new APE expression using a FileStream.
        /// </summary>
        /// <param name="input">The FileStream to read from during initialization.</param>
        /// <remarks>The constructor will *immediately* read from the file to initialize values.
        /// If this is undesired, use ApeExpression() instead.</remarks>
        public ApeExpression(FileStream input)
            : this()
        {
            _file = input;

            OperatorId = ApeCore.ReadValue<Byte>(input); // Get operator id.
            ValueFlags = ApeCore.ReadValue<Byte>(input); // Get value flags. Determines type of data in expression.

            readLValue();
            readRValue();
        }

        /// <summary>
        /// Read in the left part of the expression. It may turn out to be yet another expression which
        /// will be sequentially, and recursively, read from the file.
        /// </summary>
        protected void readLValue()
        {
            ApeCore.ReadValue<Int64>(_file); // Dump this. Ignored.

            if (ValueFlags == 0x00 ||
                ValueFlags == 0x08 ||
                ValueFlags == 0x0a)
            {
                LValue = new ApeExpression(_file);
            }
            else if (ValueFlags == 0x04 ||
                     ValueFlags == 0x0c ||
                     ValueFlags == 0x0e)
            {
                LValue = ApeCore.ReadValue<float>(_file);
            }
            else if (ValueFlags == 0x05 ||
                     ValueFlags == 0x0d ||
                     ValueFlags == 0x0f ||
                     ValueFlags == 0x31)
            {
                LValue = ApeCore.ReadString(_file);
                if (LValue as string == "")
                {
                    throw new ApeBinaryDataException("Unexpected LValue");
                }
            }
            else if (ValueFlags == 0x30 ||
                     ValueFlags == 0x32 ||
                     ValueFlags == 0x33)
            {
                LValue = ApeCore.ReadQuotedString(_file);
            }
            else
            {
                throw new ApeBinaryDataException("The value flag " + BitConverter.ToString(new byte[] { ValueFlags }) + " is invalid.");
            }
        }

        /// <summary>
        /// Read in the right part of the expression. It may turn out to be yet another expression which
        /// will be sequentially, and recursively, read from the file.
        /// </summary>
        protected void readRValue()
        {
            ApeCore.ReadValue<Int64>(_file); // Ignore these bytes.

            if (ValueFlags == 0x00 ||
                ValueFlags == 0x04 ||
                ValueFlags == 0x05)
            {
                RValue = new ApeExpression(_file);
            }
            else if (ValueFlags == 0x08 ||
                     ValueFlags == 0x0c ||
                     ValueFlags == 0x0d)
            {
                RValue = ApeCore.ReadValue<float>(_file);
            }
            else if (ValueFlags == 0x0a ||
                     ValueFlags == 0x0e ||
                     ValueFlags == 0x0f)
            {
                RValue = ApeCore.ReadString(_file);
                if (RValue as string == "")
                {
                    throw new ApeBinaryDataException("Unexpected RValue");
                }
            }
            else if (ValueFlags == 0x30 ||
                     ValueFlags == 0x31 ||
                     ValueFlags == 0x32 ||
                     ValueFlags == 0x33)
            {
                RValue = ApeCore.ReadQuotedString(_file);
            }
            else
            {
                throw new ApeBinaryDataException("The value flag " + BitConverter.ToString(new byte[] { ValueFlags }) + " is invalid.");
            }

        }
    }
}
