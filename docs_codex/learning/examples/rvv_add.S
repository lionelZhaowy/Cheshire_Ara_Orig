// SPDX-License-Identifier: Apache-2.0
// a0=a, a1=b, a2=c, a3=count. Caller enables VS first. Integer-only RVV.
.section .text.learn_vadd,"ax",@progbits
.global learn_vadd
.type learn_vadd,@function
learn_vadd:
    beqz a3, 2f
1:  vsetvli t0, a3, e32, m1, ta, ma
    vle32.v v0, (a0)
    vle32.v v1, (a1)
    vadd.vv v2, v0, v1
    vse32.v v2, (a2)
    sub a3, a3, t0
    slli t1, t0, 2
    add a0, a0, t1
    add a1, a1, t1
    add a2, a2, t1
    bnez a3, 1b
2:  ret
.size learn_vadd, .-learn_vadd
