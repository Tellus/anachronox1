using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ApeSupport
{
    /// <summary>
    /// Exception used when the binary data in an APE file is invalid. It has a thousand and one uses!
    /// </summary>
    class ApeBinaryDataException : Exception
    {
        public ApeBinaryDataException() : base() { }
        public ApeBinaryDataException(string message) : base(message) { }
        public ApeBinaryDataException(string message, System.Exception inner) : base(message, inner) { }

        // A constructor is needed for serialization when an
        // exception propagates from a remoting server to the client. 
        protected ApeBinaryDataException(System.Runtime.Serialization.SerializationInfo info,
            System.Runtime.Serialization.StreamingContext context) { }
    }
}
