/* shared.h: a set of simple functions used by both exponential.h and normal.h */
#ifndef __fast_prng_shared__
#define __fast_prng_shared__

#include <stdlib.h>
#include <math.h>
#include "MT19937.h"

#define MAX_INT64  0x7fffffffffffffff

/* Uses WDS_SAMPLER algorithm cited in main text to sample from A_i */
/* Draws random uniform doubles beginning at start, ending at end, using an
 * integer source of randomness U, with domain [0, scale). */

#define _WDS_SAMPLER()  ( (Rand->l & MAX_INT64) >= pmf[Rand->l & 255] ? map[Rand++->l & 255] : (Rand++->l & 255) )

/* Test to see if rejection sampling is required in the overhang. See Fig. 2
 * in main text. */

#define _CDM_SAMPLE(start, end, U) ((start)*pow(2, 63) + ((end) - (start))*(U))

/* All of the arrays are scaled by 2**63 (not 2**64), so this operation is used 
 * to draw uniform values in the ziggurat overhangs*/

#define GET_63_BITS     (Rand++->l & MAX_INT64)

#endif
