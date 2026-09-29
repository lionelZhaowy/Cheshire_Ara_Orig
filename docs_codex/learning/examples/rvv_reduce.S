// SPDX-License-Identifier: Apache-2.0
// uint32_t learn_sum(const uint32_t *a, unsigned long count)
// Wrap modulo 2^32; scalar ABI, VS must be enabled by caller.
.section .text.learn_sum,"ax",@progbits
.global learn_sum
.type learn_sum,@function
learn_sum:
    li t2, 0
    beqz a1, 2f
1:  vsetvli t0, a1, e32, m1, ta, ma
    vle32.v v1, (a0)
    vmv.s.x v2, zero
    vredsum.vs v3, v1, v2
    vmv.x.s t1, v3
    addw t2, t2, t1
    sub a1, a1, t0
    slli t1, t0, 2
    add a0, a0, t1
    bnez a1, 1b
2:  slli a0, t2, 32
    srli a0, a0, 32
    ret
.size learn_sum, .-learn_sum
