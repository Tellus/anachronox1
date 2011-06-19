using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace ApeSupport
{
    /// <summary>
    /// Enumerator of all APE operators.
    /// Use ApeCore.Operators[ApeOperators] to reference their string representations.
    /// </summary>
    /// <remarks>Only concern at this point is whether the compiled APE code has relatively matching values.</remarks>
    public enum EApeOperators
    {
        [StringValue("||")]
        OR = 1,
        [StringValue("&&")]
        AND,
        [StringValue("^^")]
        XOR,
        [StringValue(">")]
        GT,
        [StringValue("<")]
        LT,
        [StringValue(">=")]
        GE,
        [StringValue("<=")]
        LE,
        [StringValue("==")]
        EQ,
        [StringValue("+")]
        ADD,
        [StringValue("-")]
        SUB,
        [StringValue("*")]
        MUL,
        [StringValue("/")]
        DIV,
        [StringValue("!=")]
        NE,
        [StringValue("=")]
        ASSIGN
    }
}
