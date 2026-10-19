// SPDX-License-Identifier: Apache-2.0
// Isolates libc memcpy from the libgcc 128-bit division dependency.
#include <stdint.h>
#include <string.h>
volatile uint32_t probe_status = 0xffffffffu;
static const char source[] = "E01 libc-only relocation isolation";
static char destination[sizeof(source)];
int probe_main(void) {
    memcpy(destination, source, sizeof(source));
    for (unsigned i = 0; i < sizeof(source); ++i)
        if (source[i] != destination[i]) return 1;
    return 0;
}
