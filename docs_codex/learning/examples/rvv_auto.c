// SPDX-License-Identifier: Apache-2.0
#include <stdint.h>
// restrict is a contract: these three buffers must not overlap.
void learn_vadd(const uint32_t *restrict a, const uint32_t *restrict b,
                uint32_t *restrict c, unsigned long n) {
    for (unsigned long i = 0; i < n; ++i) c[i] = a[i] + b[i];
}
uint32_t learn_sum(const uint32_t *a, unsigned long n) {
    uint32_t sum = 0;
    for (unsigned long i = 0; i < n; ++i) sum += a[i];
    return sum;
}
