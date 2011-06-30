/*
 * jaricom.c
 *
 * Developed 1997 by Guido Vollbeding.
 * This file is part of the Independent JPEG Group's software.
 * For conditions of distribution and use, see the accompanying README file.
 *
 * This file contains probability estimation tables for common use in
 * arithmetic entropy encoding and decoding routines.
 *
 * This data represents Table D.2 in the JPEG spec (ISO/IEC IS 10918-1
 * and CCITT Recommendation ITU-T T.81) and Table 24 in the JBIG spec
 * (ISO/IEC IS 11544 and CCITT Recommendation ITU-T T.82).
 */

#define JPEG_INTERNALS
#include "jinclude.h"
#include "jpeglib.h"

/* The following #define specifies the packing of the four components
 * into the compact INT32 representation.
 * Note that this formula must match the actual arithmetic encoder
 * and decoder implementation.  The implementation has to be changed
 * if this formula is changed.
 * The current organization is leaned on Markus Kuhn's JBIG
 * implementation (jbig_tab.c).
 */

#include "jaritab.h"
