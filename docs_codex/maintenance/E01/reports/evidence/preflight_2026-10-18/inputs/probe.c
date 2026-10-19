// SPDX-License-Identifier: Apache-2.0
// Force real libc memcpy and libgcc signed 128-bit division references.
#include <stdint.h>
#include <string.h>

volatile __int128 dividend = ((__int128)1 << 80) + 12345;
volatile __int128 divisor = 7;
volatile __int128 quotient;
volatile uint32_t probe_status = 0xffffffffu;
static const char source[] = "E01 compiler and runtime link probe";
static char destination[sizeof(source)];

int probe_main(void) {
    memcpy(destination, source, sizeof(source));
    quotient = dividend / divisor;
    for (unsigned i = 0; i < sizeof(source); ++i)
        if (destination[i] != source[i]) return 1;
    return quotient == ((((__int128)1 << 80) + 12345) / 7) ? 0 : 2;
}
