	.file	"journey.c"
	.option nopic
	.attribute arch, "rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_zicsr2p0_zifencei2p0_zmmul1p0_zaamo1p0_zalrsc1p0_zca1p0_zcd1p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
.Ltext0:
	.cfi_sections	.debug_frame
	.section	.text.make_value,"ax",@progbits
	.align	1
	.globl	make_value
	.type	make_value, @function
make_value:
.LVL0:
.LFB11:
.LM1:
	.cfi_startproc
.LM2:
.LM3:
	lw	a4,seed
.LVL1:
.LM4:
.LM5:
	slliw	a5,a0,1
	addw	a0,a5,a0
.LVL2:
.LM6:
	addw	a0,a0,a4
	ret
	.cfi_endproc
.LFE11:
	.size	make_value, .-make_value
	.section	.rodata.main.str1.8,"aMS",@progbits,1
	.align	3
.LC0:
	.string	"LEARN stage=%u %s\r\n"
	.align	3
.LC1:
	.string	"INIT seed=%u zeroed=137 errors=%u\r\n"
	.align	3
.LC2:
	.string	"LEARN sum=%u errors=%u\r\n"
	.section	.text.startup.main,"ax",@progbits
	.align	1
	.globl	main
	.type	main, @function
main:
.LFB12:
.LM7:
	.cfi_startproc
.LM8:
.LM9:
	addi	sp,sp,-48
	.cfi_def_cfa_offset 48
	sd	s0,32(sp)
	.cfi_offset 8, -16
.LM10:
	lw	s0,seed
.LM11:
	sd	s2,16(sp)
	sd	ra,40(sp)
.LM12:
	addi	s0,s0,-1
.LBB7:
.LM13:
	li	a5,0
	.cfi_offset 18, -32
	.cfi_offset 1, -8
	lla	s2,result
.LBE7:
.LM14:
	snez	s0,s0
.LM15:
.LBB8:
.LM16:
.LVL3:
.LM17:
	li	a3,137
.LVL4:
.L4:
.LM18:
.LM19:
	slli	a2,a5,32
	srli	a4,a2,30
	add	a4,s2,a4
	lw	a4,0(a4)
.LM20:
	addiw	a5,a5,1
.LVL5:
.LM21:
	snez	a4,a4
.LM22:
	addw	s0,a4,s0
.LVL6:
.LM23:
.LM24:
	bne	a5,a3,.L4
.LBE8:
.LM25:
.LM26:
	lw	a4,__base_regs+68
.LVL7:
.LM27:
.LM28:
	li	a5,4096
.LVL8:
.LM29:
	addi	a5,a5,-1597
.LM30:
	li	a0,10
.LM31:
	bleu	a4,a5,.L5
.LM32:
.LM33:
	slli	a0,a4,32
	li	a1,4096
	addi	a1,a1,-1596
	srli	a0,a0,32
	sd	s1,24(sp)
	sd	s3,8(sp)
	.cfi_offset 9, -24
	.cfi_offset 19, -40
.LM34:
	call	clint_get_core_freq
.LVL9:
.LM35:
	li	a2,114688
.LM36:
	mv	a1,a0
.LVL10:
.LM37:
	addi	a2,a2,512
	lla	a0,__base_uart
.LVL11:
.LM38:
	call	uart_init
.LVL12:
.LM39:
	lla	a2,greeting
	li	a1,1
	lla	a0,.LC0
	call	printf_
.LVL13:
.LM40:
	lw	a1,seed
	mv	a2,s0
	lla	a0,.LC1
	call	printf_
.LVL14:
.LM41:
.LBB9:
.LM42:
.LM43:
.LM44:
	li	s1,0
.LM45:
	li	s3,137
.LVL15:
.L6:
.LM46:
.LM47:
	mv	a0,s1
	call	make_value
.LVL16:
.LM48:
	slli	a4,s1,32
	srli	a5,a4,30
	add	a5,s2,a5
	sw	a0,0(a5)
.LM49:
	addiw	s1,s1,1
.LVL17:
.LM50:
	bne	s1,s3,.L6
	li	a2,1
.LBE9:
.LBB10:
.LM51:
	li	a3,0
.LBE10:
.LM52:
	li	a1,0
.LBB11:
.LM53:
	li	a0,137
.L7:
.LVL18:
.LM54:
.LM55:
	slli	a5,a3,32
	srli	a4,a5,30
	add	a4,s2,a4
	lw	a5,0(a4)
.LM56:
	lw	a4,0(a4)
.LM57:
	addiw	a3,a3,1
.LVL19:
.LM58:
	sub	a5,a5,a2
	snez	a5,a5
.LM59:
	addw	s0,a5,s0
.LVL20:
.LM60:
.LM61:
	addw	a1,a4,a1
.LVL21:
.LM62:
.LM63:
	addiw	a2,a2,3
	bne	a3,a0,.L7
.LBE11:
.LM64:
	mv	a2,s0
	lla	a0,.LC2
	call	printf_
.LVL22:
.LM65:
	lla	a0,__base_uart
	call	uart_write_flush
.LVL23:
.LM66:
.LM67:
	ld	s1,24(sp)
	.cfi_restore 9
.LVL24:
.LM68:
	ld	s3,8(sp)
	.cfi_restore 19
	snez	a0,s0
.LVL25:
.L5:
.LM69:
	ld	ra,40(sp)
	.cfi_restore 1
	ld	s0,32(sp)
	.cfi_restore 8
.LVL26:
.LM70:
	ld	s2,16(sp)
	.cfi_restore 18
	addi	sp,sp,48
	.cfi_def_cfa_offset 0
	jr	ra
	.cfi_endproc
.LFE12:
	.size	main, .-main
	.globl	greeting
	.section	.rodata.greeting,"a"
	.align	3
	.type	greeting, @object
	.size	greeting, 16
greeting:
	.string	"Hello Cheshire!"
	.globl	result
	.section	.bss.result,"aw",@nobits
	.align	3
	.type	result, @object
	.size	result, 548
result:
	.zero	548
	.globl	seed
	.section	.sdata.seed,"aw"
	.align	2
	.type	seed, @object
	.size	seed, 4
seed:
	.word	1
	.text
.Letext0:
	.section	.debug_info,"",@progbits
.Ldebug_info0:
	.4byte	0x463
	.2byte	0x5
	.byte	0x1
	.byte	0x8
	.4byte	.Ldebug_abbrev0
	.uleb128 0x16
	.4byte	.LASF40
	.byte	0x1d
	.byte	0x3
	.4byte	0x31647
	.4byte	.LASF0
	.4byte	.LASF1
	.4byte	.LLRL11
	.8byte	0
	.4byte	.Ldebug_line0
	.uleb128 0x1
	.byte	0x1
	.byte	0x6
	.4byte	.LASF2
	.uleb128 0x4
	.4byte	.LASF6
	.byte	0x2
	.byte	0x2b
	.byte	0x17
	.4byte	0x42
	.uleb128 0x1
	.byte	0x1
	.byte	0x8
	.4byte	.LASF3
	.uleb128 0x1
	.byte	0x2
	.byte	0x5
	.4byte	.LASF4
	.uleb128 0x1
	.byte	0x2
	.byte	0x7
	.4byte	.LASF5
	.uleb128 0x17
	.byte	0x4
	.byte	0x5
	.string	"int"
	.uleb128 0x4
	.4byte	.LASF7
	.byte	0x2
	.byte	0x4f
	.byte	0x16
	.4byte	0x6a
	.uleb128 0x1
	.byte	0x4
	.byte	0x7
	.4byte	.LASF8
	.uleb128 0x1
	.byte	0x8
	.byte	0x5
	.4byte	.LASF9
	.uleb128 0x4
	.4byte	.LASF10
	.byte	0x2
	.byte	0x69
	.byte	0x1b
	.4byte	0x84
	.uleb128 0x1
	.byte	0x8
	.byte	0x7
	.4byte	.LASF11
	.uleb128 0x4
	.4byte	.LASF12
	.byte	0x3
	.byte	0x18
	.byte	0x13
	.4byte	0x36
	.uleb128 0x4
	.4byte	.LASF13
	.byte	0x3
	.byte	0x30
	.byte	0x14
	.4byte	0x5e
	.uleb128 0x5
	.4byte	0x97
	.uleb128 0xd
	.4byte	0x97
	.uleb128 0x4
	.4byte	.LASF14
	.byte	0x3
	.byte	0x3c
	.byte	0x14
	.4byte	0x78
	.uleb128 0x5
	.4byte	0xad
	.uleb128 0x18
	.byte	0x8
	.uleb128 0x5
	.4byte	0xbe
	.uleb128 0xe
	.4byte	.LASF15
	.byte	0x11
	.4byte	0xbe
	.uleb128 0xe
	.4byte	.LASF16
	.byte	0x13
	.4byte	0xbe
	.uleb128 0x8
	.4byte	.LASF17
	.byte	0x25
	.byte	0x17
	.4byte	0xa3
	.4byte	0x1c200
	.uleb128 0x19
	.4byte	.LASF18
	.byte	0x4
	.byte	0x28
	.byte	0x17
	.4byte	0xb9
	.byte	0x60
	.uleb128 0x8
	.4byte	.LASF19
	.byte	0x2b
	.byte	0x14
	.4byte	0xc0
	.4byte	0x80800000
	.uleb128 0x8
	.4byte	.LASF20
	.byte	0x2c
	.byte	0x14
	.4byte	0xc0
	.4byte	0x80000000
	.uleb128 0x9
	.4byte	0xb9
	.4byte	0x123
	.uleb128 0xa
	.4byte	0x84
	.byte	0x1
	.byte	0
	.uleb128 0x5
	.4byte	0x113
	.uleb128 0xb
	.4byte	.LASF21
	.byte	0x2f
	.4byte	0x123
	.byte	0x10
	.byte	0x6a
	.byte	0xb2
	.byte	0x69
	.byte	0x2
	.byte	0x95
	.byte	0xfd
	.byte	0xe4
	.byte	0x4c
	.byte	0x98
	.byte	0xcf
	.byte	0x94
	.byte	0x14
	.byte	0x1
	.byte	0x41
	.byte	0x2c
	.byte	0x62
	.uleb128 0xb
	.4byte	.LASF22
	.byte	0x32
	.4byte	0x123
	.byte	0x10
	.byte	0x61
	.byte	0x2f
	.byte	0x44
	.byte	0xba
	.byte	0xef
	.byte	0x2a
	.byte	0xde
	.byte	0x42
	.byte	0x92
	.byte	0x33
	.byte	0xe4
	.byte	0xd7
	.byte	0x5d
	.byte	0x3a
	.byte	0xcb
	.byte	0x9d
	.uleb128 0xb
	.4byte	.LASF23
	.byte	0x35
	.4byte	0x123
	.byte	0x10
	.byte	0xda
	.byte	0x86
	.byte	0xec
	.byte	0x99
	.byte	0x5b
	.byte	0x3f
	.byte	0xd
	.byte	0x4b
	.byte	0x8f
	.byte	0x4b
	.byte	0xc4
	.byte	0xba
	.byte	0xcf
	.byte	0xa5
	.byte	0xf8
	.byte	0x59
	.uleb128 0x1
	.byte	0x8
	.byte	0x5
	.4byte	.LASF24
	.uleb128 0x1
	.byte	0x10
	.byte	0x4
	.4byte	.LASF25
	.uleb128 0xc
	.4byte	.LASF26
	.byte	0x12
	.byte	0x13
	.4byte	0xa8
	.uleb128 0x9
	.byte	0x3
	.8byte	seed
	.uleb128 0x9
	.4byte	0xa8
	.4byte	0x1ac
	.uleb128 0xa
	.4byte	0x84
	.byte	0x88
	.byte	0
	.uleb128 0xd
	.4byte	0x19c
	.uleb128 0xc
	.4byte	.LASF27
	.byte	0x13
	.byte	0x13
	.4byte	0x1ac
	.uleb128 0x9
	.byte	0x3
	.8byte	result
	.uleb128 0x9
	.4byte	0x1e2
	.4byte	0x1d6
	.uleb128 0xa
	.4byte	0x84
	.byte	0xf
	.byte	0
	.uleb128 0x5
	.4byte	0x1c6
	.uleb128 0x1
	.byte	0x1
	.byte	0x8
	.4byte	.LASF28
	.uleb128 0x5
	.4byte	0x1db
	.uleb128 0xc
	.4byte	.LASF29
	.byte	0x14
	.byte	0xc
	.4byte	0x1d6
	.uleb128 0x9
	.byte	0x3
	.8byte	greeting
	.uleb128 0xf
	.4byte	.LASF30
	.byte	0x26
	.4byte	0x20c
	.uleb128 0x3
	.4byte	0xbe
	.byte	0
	.uleb128 0x10
	.4byte	.LASF32
	.byte	0x6
	.byte	0x3d
	.byte	0x5
	.4byte	0x57
	.4byte	0x223
	.uleb128 0x3
	.4byte	0x223
	.uleb128 0x1a
	.byte	0
	.uleb128 0x11
	.4byte	0x1e2
	.uleb128 0xf
	.4byte	.LASF31
	.byte	0x1e
	.4byte	0x242
	.uleb128 0x3
	.4byte	0xbe
	.uleb128 0x3
	.4byte	0xad
	.uleb128 0x3
	.4byte	0xad
	.byte	0
	.uleb128 0x10
	.4byte	.LASF33
	.byte	0x7
	.byte	0x14
	.byte	0xa
	.4byte	0xad
	.4byte	0x25d
	.uleb128 0x3
	.4byte	0xad
	.uleb128 0x3
	.4byte	0xad
	.byte	0
	.uleb128 0x12
	.4byte	.LASF35
	.byte	0x3c
	.byte	0x5
	.4byte	0x57
	.8byte	.LFB12
	.8byte	.LFE12-.LFB12
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x3f5
	.uleb128 0x13
	.4byte	.LASF34
	.byte	0x3e
	.4byte	0x6a
	.4byte	.LLST2
	.4byte	.LVUS2
	.uleb128 0x6
	.string	"rtc"
	.byte	0x40
	.byte	0xe
	.4byte	0x97
	.4byte	.LLST3
	.4byte	.LVUS3
	.uleb128 0x6
	.string	"hz"
	.byte	0x42
	.byte	0xe
	.4byte	0xad
	.4byte	.LLST4
	.4byte	.LVUS4
	.uleb128 0x6
	.string	"sum"
	.byte	0x66
	.byte	0xe
	.4byte	0x97
	.4byte	.LLST5
	.4byte	.LVUS5
	.uleb128 0x14
	.4byte	.LLRL6
	.4byte	0x2e3
	.uleb128 0x6
	.string	"i"
	.byte	0x3f
	.byte	0x13
	.4byte	0x6a
	.4byte	.LLST7
	.4byte	.LVUS7
	.byte	0
	.uleb128 0x1b
	.8byte	.LBB9
	.8byte	.LBE9-.LBB9
	.4byte	0x31e
	.uleb128 0x6
	.string	"i"
	.byte	0x63
	.byte	0x13
	.4byte	0x6a
	.4byte	.LLST8
	.4byte	.LVUS8
	.uleb128 0x1c
	.8byte	.LVL16
	.4byte	0x3f5
	.uleb128 0x2
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x2
	.byte	0x79
	.sleb128 0
	.byte	0
	.byte	0
	.uleb128 0x14
	.4byte	.LLRL9
	.4byte	0x339
	.uleb128 0x6
	.string	"i"
	.byte	0x67
	.byte	0x13
	.4byte	0x6a
	.4byte	.LLST10
	.4byte	.LVUS10
	.byte	0
	.uleb128 0x7
	.8byte	.LVL9
	.4byte	0x242
	.4byte	0x352
	.uleb128 0x2
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x3
	.byte	0xa
	.2byte	0x9c4
	.byte	0
	.uleb128 0x7
	.8byte	.LVL12
	.4byte	0x228
	.4byte	0x36c
	.uleb128 0x2
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x4
	.byte	0x8
	.byte	0xe1
	.byte	0x39
	.byte	0x24
	.byte	0
	.uleb128 0x7
	.8byte	.LVL13
	.4byte	0x20c
	.4byte	0x39d
	.uleb128 0x2
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x9
	.byte	0x3
	.8byte	.LC0
	.uleb128 0x2
	.uleb128 0x1
	.byte	0x5b
	.uleb128 0x1
	.byte	0x31
	.uleb128 0x2
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x9
	.byte	0x3
	.8byte	greeting
	.byte	0
	.uleb128 0x7
	.8byte	.LVL14
	.4byte	0x20c
	.4byte	0x3c2
	.uleb128 0x2
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x9
	.byte	0x3
	.8byte	.LC1
	.uleb128 0x2
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x2
	.byte	0x78
	.sleb128 0
	.byte	0
	.uleb128 0x7
	.8byte	.LVL22
	.4byte	0x20c
	.4byte	0x3e7
	.uleb128 0x2
	.uleb128 0x1
	.byte	0x5a
	.uleb128 0x9
	.byte	0x3
	.8byte	.LC2
	.uleb128 0x2
	.uleb128 0x1
	.byte	0x5c
	.uleb128 0x2
	.byte	0x78
	.sleb128 0
	.byte	0
	.uleb128 0x1d
	.8byte	.LVL23
	.4byte	0x1fc
	.byte	0
	.uleb128 0x12
	.4byte	.LASF36
	.byte	0x15
	.byte	0x24
	.4byte	0x97
	.8byte	.LFB11
	.8byte	.LFE11-.LFB11
	.uleb128 0x1
	.byte	0x9c
	.4byte	0x43b
	.uleb128 0x1e
	.string	"i"
	.byte	0x1
	.byte	0x15
	.byte	0x38
	.4byte	0x6a
	.4byte	.LLST0
	.4byte	.LVUS0
	.uleb128 0x13
	.4byte	.LASF37
	.byte	0x16
	.4byte	0x97
	.4byte	.LLST1
	.4byte	.LVUS1
	.byte	0
	.uleb128 0x1f
	.4byte	.LASF41
	.byte	0x8
	.byte	0x14
	.byte	0x22
	.4byte	0x461
	.byte	0x3
	.4byte	0x461
	.uleb128 0x15
	.4byte	.LASF38
	.byte	0x2e
	.4byte	0xbe
	.uleb128 0x15
	.4byte	.LASF39
	.byte	0x38
	.4byte	0x57
	.byte	0
	.uleb128 0x11
	.4byte	0xa8
	.byte	0
	.section	.debug_abbrev,"",@progbits
.Ldebug_abbrev0:
	.uleb128 0x1
	.uleb128 0x24
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0x3e
	.uleb128 0xb
	.uleb128 0x3
	.uleb128 0xe
	.byte	0
	.byte	0
	.uleb128 0x2
	.uleb128 0x49
	.byte	0
	.uleb128 0x2
	.uleb128 0x18
	.uleb128 0x7e
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x3
	.uleb128 0x5
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x4
	.uleb128 0x16
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x5
	.uleb128 0x26
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x6
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0x21
	.sleb128 1
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.uleb128 0x2137
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x7
	.uleb128 0x48
	.byte	0x1
	.uleb128 0x7d
	.uleb128 0x1
	.uleb128 0x7f
	.uleb128 0x13
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x8
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0x21
	.sleb128 4
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1c
	.uleb128 0x6
	.byte	0
	.byte	0
	.uleb128 0x9
	.uleb128 0x1
	.byte	0x1
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xa
	.uleb128 0x21
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2f
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0xb
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0x21
	.sleb128 4
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0x21
	.sleb128 23
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1c
	.uleb128 0xa
	.byte	0
	.byte	0
	.uleb128 0xc
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0x21
	.sleb128 1
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0xd
	.uleb128 0x35
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xe
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0x21
	.sleb128 4
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0x21
	.sleb128 14
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3c
	.uleb128 0x19
	.byte	0
	.byte	0
	.uleb128 0xf
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0x21
	.sleb128 5
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0x21
	.sleb128 6
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x3c
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x10
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x3c
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x11
	.uleb128 0xf
	.byte	0
	.uleb128 0xb
	.uleb128 0x21
	.sleb128 8
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x12
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0x21
	.sleb128 1
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x7
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x7a
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x13
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0x21
	.sleb128 1
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0x21
	.sleb128 14
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.uleb128 0x2137
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x14
	.uleb128 0xb
	.byte	0x1
	.uleb128 0x55
	.uleb128 0x17
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x15
	.uleb128 0x5
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0x21
	.sleb128 8
	.uleb128 0x3b
	.uleb128 0x21
	.sleb128 20
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x16
	.uleb128 0x11
	.byte	0x1
	.uleb128 0x25
	.uleb128 0xe
	.uleb128 0x13
	.uleb128 0xb
	.uleb128 0x90
	.uleb128 0xb
	.uleb128 0x91
	.uleb128 0x6
	.uleb128 0x3
	.uleb128 0x1f
	.uleb128 0x1b
	.uleb128 0x1f
	.uleb128 0x55
	.uleb128 0x17
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x10
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x17
	.uleb128 0x24
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0x3e
	.uleb128 0xb
	.uleb128 0x3
	.uleb128 0x8
	.byte	0
	.byte	0
	.uleb128 0x18
	.uleb128 0xf
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0x19
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1c
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0x1a
	.uleb128 0x18
	.byte	0
	.byte	0
	.byte	0
	.uleb128 0x1b
	.uleb128 0xb
	.byte	0x1
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x7
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x1c
	.uleb128 0x48
	.byte	0x1
	.uleb128 0x7d
	.uleb128 0x1
	.uleb128 0x7f
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x1d
	.uleb128 0x48
	.byte	0
	.uleb128 0x7d
	.uleb128 0x1
	.uleb128 0x7f
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x1e
	.uleb128 0x5
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.uleb128 0x2137
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x1f
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3
	.uleb128 0xe
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x20
	.uleb128 0xb
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.byte	0
	.section	.debug_loclists,"",@progbits
	.4byte	.Ldebug_loc3-.Ldebug_loc2
.Ldebug_loc2:
	.2byte	0x5
	.byte	0x8
	.byte	0
	.4byte	0
.Ldebug_loc0:
.LVUS2:
	.uleb128 0xa
	.uleb128 0x3f
.LLST2:
	.byte	0x8
	.8byte	.LVL3
	.uleb128 .LVL26-.LVL3
	.uleb128 0x1
	.byte	0x58
	.byte	0
.LVUS3:
	.uleb128 0x14
	.uleb128 0x1c
.LLST3:
	.byte	0x8
	.8byte	.LVL7
	.uleb128 .LVL9-1-.LVL7
	.uleb128 0x1
	.byte	0x5e
	.byte	0
.LVUS4:
	.uleb128 0x1e
	.uleb128 0x1f
	.uleb128 0x1f
	.uleb128 0x20
.LLST4:
	.byte	0x6
	.8byte	.LVL10
	.byte	0x4
	.uleb128 .LVL10-.LVL10
	.uleb128 .LVL11-.LVL10
	.uleb128 0x1
	.byte	0x5a
	.byte	0x4
	.uleb128 .LVL11-.LVL10
	.uleb128 .LVL12-1-.LVL10
	.uleb128 0x1
	.byte	0x5b
	.byte	0
.LVUS5:
	.uleb128 0x2f
	.uleb128 0x3a
.LLST5:
	.byte	0x8
	.8byte	.LVL18
	.uleb128 .LVL22-1-.LVL18
	.uleb128 0x1
	.byte	0x5b
	.byte	0
.LVUS7:
	.uleb128 0xa
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0xe
	.uleb128 0x11
	.uleb128 0x16
.LLST7:
	.byte	0x6
	.8byte	.LVL3
	.byte	0x4
	.uleb128 .LVL3-.LVL3
	.uleb128 .LVL4-.LVL3
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL4-.LVL3
	.uleb128 .LVL5-.LVL3
	.uleb128 0x1
	.byte	0x5f
	.byte	0x4
	.uleb128 .LVL6-.LVL3
	.uleb128 .LVL8-.LVL3
	.uleb128 0x1
	.byte	0x5f
	.byte	0
.LVUS8:
	.uleb128 0x24
	.uleb128 0x27
	.uleb128 0x27
	.uleb128 0x3d
.LLST8:
	.byte	0x6
	.8byte	.LVL14
	.byte	0x4
	.uleb128 .LVL14-.LVL14
	.uleb128 .LVL15-.LVL14
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL15-.LVL14
	.uleb128 .LVL24-.LVL14
	.uleb128 0x1
	.byte	0x59
	.byte	0
.LVUS10:
	.uleb128 0x2f
	.uleb128 0x33
	.uleb128 0x38
	.uleb128 0x3a
.LLST10:
	.byte	0x6
	.8byte	.LVL18
	.byte	0x4
	.uleb128 .LVL18-.LVL18
	.uleb128 .LVL19-.LVL18
	.uleb128 0x1
	.byte	0x5d
	.byte	0x4
	.uleb128 .LVL21-.LVL18
	.uleb128 .LVL22-1-.LVL18
	.uleb128 0x1
	.byte	0x5d
	.byte	0
.LVUS0:
	.uleb128 0
	.uleb128 0x5
	.uleb128 0x5
	.uleb128 0
.LLST0:
	.byte	0x6
	.8byte	.LVL0
	.byte	0x4
	.uleb128 .LVL0-.LVL0
	.uleb128 .LVL2-.LVL0
	.uleb128 0x1
	.byte	0x5a
	.byte	0x4
	.uleb128 .LVL2-.LVL0
	.uleb128 .LFE11-.LVL0
	.uleb128 0x4
	.byte	0xa3
	.uleb128 0x1
	.byte	0x5a
	.byte	0x9f
	.byte	0
.LVUS1:
	.uleb128 0x3
	.uleb128 0x5
	.uleb128 0x5
	.uleb128 0
.LLST1:
	.byte	0x6
	.8byte	.LVL1
	.byte	0x4
	.uleb128 .LVL1-.LVL1
	.uleb128 .LVL2-.LVL1
	.uleb128 0x8
	.byte	0x7a
	.sleb128 0
	.byte	0x33
	.byte	0x1e
	.byte	0x7e
	.sleb128 0
	.byte	0x22
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL2-.LVL1
	.uleb128 .LFE11-.LVL1
	.uleb128 0x9
	.byte	0xa3
	.uleb128 0x1
	.byte	0x5a
	.byte	0x33
	.byte	0x1e
	.byte	0x7e
	.sleb128 0
	.byte	0x22
	.byte	0x9f
	.byte	0
.Ldebug_loc3:
	.section	.debug_aranges,"",@progbits
	.4byte	0x3c
	.2byte	0x2
	.4byte	.Ldebug_info0
	.byte	0x8
	.byte	0
	.2byte	0
	.2byte	0
	.8byte	.LFB11
	.8byte	.LFE11-.LFB11
	.8byte	.LFB12
	.8byte	.LFE12-.LFB12
	.8byte	0
	.8byte	0
	.section	.debug_rnglists,"",@progbits
.Ldebug_ranges0:
	.4byte	.Ldebug_ranges3-.Ldebug_ranges2
.Ldebug_ranges2:
	.2byte	0x5
	.byte	0x8
	.byte	0
	.4byte	0
.LLRL6:
	.byte	0x5
	.8byte	.LBB7
	.byte	0x4
	.uleb128 .LBB7-.LBB7
	.uleb128 .LBE7-.LBB7
	.byte	0x4
	.uleb128 .LBB8-.LBB7
	.uleb128 .LBE8-.LBB7
	.byte	0
.LLRL9:
	.byte	0x5
	.8byte	.LBB10
	.byte	0x4
	.uleb128 .LBB10-.LBB10
	.uleb128 .LBE10-.LBB10
	.byte	0x4
	.uleb128 .LBB11-.LBB10
	.uleb128 .LBE11-.LBB10
	.byte	0
.LLRL11:
	.byte	0x7
	.8byte	.LFB11
	.uleb128 .LFE11-.LFB11
	.byte	0x7
	.8byte	.LFB12
	.uleb128 .LFE12-.LFB12
	.byte	0
.Ldebug_ranges3:
	.section	.debug_line,"",@progbits
.Ldebug_line0:
	.4byte	.LELT0-.LSLT0
.LSLT0:
	.2byte	0x5
	.byte	0x8
	.byte	0
	.4byte	.LELTP0-.LASLTP0
.LASLTP0:
	.byte	0x1
	.byte	0x1
	.byte	0x1
	.byte	0xf6
	.byte	0xf2
	.byte	0xd
	.byte	0
	.byte	0x1
	.byte	0x1
	.byte	0x1
	.byte	0x1
	.byte	0
	.byte	0
	.byte	0
	.byte	0x1
	.byte	0
	.byte	0
	.byte	0x1
	.byte	0x1
	.uleb128 0x1
	.uleb128 0x1f
	.uleb128 0x7
	.4byte	.LASF1
	.4byte	.LASF42
	.4byte	.LASF43
	.4byte	.LASF44
	.4byte	.LASF45
	.4byte	.LASF46
	.4byte	.LASF47
	.byte	0x2
	.uleb128 0x1
	.uleb128 0x1f
	.uleb128 0x2
	.uleb128 0xb
	.uleb128 0x9
	.4byte	.LASF0
	.byte	0
	.4byte	.LASF48
	.byte	0x1
	.4byte	.LASF49
	.byte	0x5
	.4byte	.LASF50
	.byte	0x6
	.4byte	.LASF51
	.byte	0x4
	.4byte	.LASF52
	.byte	0x3
	.4byte	.LASF53
	.byte	0x2
	.4byte	.LASF54
	.byte	0x3
	.4byte	.LASF55
	.byte	0x4
.LELTP0:
	.byte	0
	.uleb128 0x9
	.byte	0x2
	.8byte	.LM1
	.byte	0x2b
	.byte	0x5
	.uleb128 0x3b
	.byte	0x9
	.2byte	.LM2-.LM1
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM3-.LM2
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x21
	.byte	0x9
	.2byte	.LM4-.LM3
	.byte	0x6
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM5-.LM4
	.byte	0x6
	.byte	0x16
	.byte	0x5
	.uleb128 0x1d
	.byte	0x9
	.2byte	.LM6-.LM5
	.byte	0x19
	.byte	0x5
	.uleb128 0x1
	.byte	0
	.uleb128 0x9
	.byte	0x2
	.8byte	.LFE11
	.byte	0
	.uleb128 0x1
	.byte	0x1
	.byte	0
	.uleb128 0x9
	.byte	0x2
	.8byte	.LM7
	.byte	0x52
	.byte	0x5
	.uleb128 0x10
	.byte	0x9
	.2byte	.LM8-.LM7
	.byte	0x19
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM9-.LM8
	.byte	0x6
	.byte	0x15
	.byte	0x5
	.uleb128 0x10
	.byte	0x9
	.2byte	.LM10-.LM9
	.byte	0x19
	.byte	0x5
	.uleb128 0x1c
	.byte	0x9
	.2byte	.LM11-.LM10
	.byte	0x15
	.byte	0x5
	.uleb128 0x10
	.byte	0x9
	.2byte	.LM12-.LM11
	.byte	0x19
	.byte	0x5
	.uleb128 0x1c
	.byte	0x9
	.2byte	.LM13-.LM12
	.byte	0x18
	.byte	0x5
	.uleb128 0x13
	.byte	0x9
	.2byte	.LM14-.LM13
	.byte	0x16
	.byte	0x5
	.uleb128 0x1c
	.byte	0x9
	.2byte	.LM15-.LM14
	.byte	0x6
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM16-.LM15
	.byte	0x1
	.byte	0x5
	.uleb128 0xa
	.byte	0x9
	.2byte	.LM17-.LM16
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x1
	.byte	0x1
	.byte	0x5
	.uleb128 0x1c
	.byte	0x9
	.2byte	.LM18-.LM17
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x3
	.byte	0x1
	.byte	0x5
	.uleb128 0x29
	.byte	0x9
	.2byte	.LM19-.LM18
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x39
	.byte	0x9
	.2byte	.LM20-.LM19
	.byte	0x1
	.byte	0x5
	.uleb128 0x24
	.byte	0x9
	.2byte	.LM21-.LM20
	.byte	0x1
	.byte	0x5
	.uleb128 0x3d
	.byte	0x9
	.2byte	.LM22-.LM21
	.byte	0x1
	.byte	0x5
	.uleb128 0x30
	.byte	0x9
	.2byte	.LM23-.LM22
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x24
	.byte	0x9
	.2byte	.LM24-.LM23
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x1
	.byte	0x1
	.byte	0x5
	.uleb128 0x1c
	.byte	0x9
	.2byte	.LM25-.LM24
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM26-.LM25
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x1
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0xe
	.byte	0x9
	.2byte	.LM27-.LM26
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0
	.byte	0x6
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM28-.LM27
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x8
	.byte	0x9
	.2byte	.LM29-.LM28
	.byte	0x1
	.byte	0x5
	.uleb128 0x8
	.byte	0x9
	.2byte	.LM30-.LM29
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x1
	.byte	0x1
	.byte	0x5
	.uleb128 0x1c
	.byte	0x9
	.2byte	.LM31-.LM30
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0
	.byte	0x1
	.byte	0x5
	.uleb128 0x8
	.byte	0x9
	.2byte	.LM32-.LM31
	.byte	0x6
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM33-.LM32
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x13
	.byte	0x9
	.2byte	.LM34-.LM33
	.byte	0x1
	.byte	0x5
	.uleb128 0x13
	.byte	0x9
	.2byte	.LM35-.LM34
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM36-.LM35
	.byte	0x16
	.byte	0x5
	.uleb128 0x13
	.byte	0x9
	.2byte	.LM37-.LM36
	.byte	0x6
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM38-.LM37
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM39-.LM38
	.byte	0x6
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM40-.LM39
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM41-.LM40
	.byte	0x35
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM42-.LM41
	.byte	0x1
	.byte	0x5
	.uleb128 0xa
	.byte	0x9
	.2byte	.LM43-.LM42
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x3
	.byte	0x1
	.byte	0x5
	.uleb128 0x1c
	.byte	0x9
	.2byte	.LM44-.LM43
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x13
	.byte	0x9
	.2byte	.LM45-.LM44
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x3
	.byte	0x1
	.byte	0x5
	.uleb128 0x1c
	.byte	0x9
	.2byte	.LM46-.LM45
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x4
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x29
	.byte	0x9
	.2byte	.LM47-.LM46
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x35
	.byte	0x9
	.2byte	.LM48-.LM47
	.byte	0x1
	.byte	0x5
	.uleb128 0x33
	.byte	0x9
	.2byte	.LM49-.LM48
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x24
	.byte	0x9
	.2byte	.LM50-.LM49
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x3
	.byte	0x1
	.byte	0x5
	.uleb128 0x1c
	.byte	0x9
	.2byte	.LM51-.LM50
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0
	.byte	0x6
	.byte	0x1b
	.byte	0x5
	.uleb128 0x13
	.byte	0x9
	.2byte	.LM52-.LM51
	.byte	0x16
	.byte	0x5
	.uleb128 0xe
	.byte	0x9
	.2byte	.LM53-.LM52
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x1
	.byte	0x18
	.byte	0x5
	.uleb128 0x1c
	.byte	0x9
	.2byte	.LM54-.LM53
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0
	.byte	0x6
	.byte	0x18
	.byte	0x5
	.uleb128 0x9
	.byte	0x9
	.2byte	.LM55-.LM54
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x19
	.byte	0x9
	.2byte	.LM56-.LM55
	.byte	0x18
	.byte	0x5
	.uleb128 0x16
	.byte	0x9
	.2byte	.LM57-.LM56
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x3
	.byte	0x15
	.byte	0x5
	.uleb128 0x24
	.byte	0x9
	.2byte	.LM58-.LM57
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0
	.byte	0x18
	.byte	0x5
	.uleb128 0x1d
	.byte	0x9
	.2byte	.LM59-.LM58
	.byte	0x1
	.byte	0x5
	.uleb128 0x10
	.byte	0x9
	.2byte	.LM60-.LM59
	.byte	0x6
	.byte	0x18
	.byte	0x5
	.uleb128 0x9
	.byte	0x9
	.2byte	.LM61-.LM60
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0xd
	.byte	0x9
	.2byte	.LM62-.LM61
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x3
	.byte	0x6
	.byte	0x15
	.byte	0x5
	.uleb128 0x24
	.byte	0x9
	.2byte	.LM63-.LM62
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0x1
	.byte	0x1
	.byte	0x5
	.uleb128 0x1c
	.byte	0x9
	.2byte	.LM64-.LM63
	.byte	0
	.uleb128 0x2
	.byte	0x4
	.uleb128 0
	.byte	0x1b
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM65-.LM64
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM66-.LM65
	.byte	0x18
	.byte	0x5
	.uleb128 0x5
	.byte	0x9
	.2byte	.LM67-.LM66
	.byte	0x6
	.byte	0x1
	.byte	0x5
	.uleb128 0x17
	.byte	0x9
	.2byte	.LM68-.LM67
	.byte	0x1
	.byte	0x5
	.uleb128 0x17
	.byte	0x9
	.2byte	.LM69-.LM68
	.byte	0x18
	.byte	0x5
	.uleb128 0x1
	.byte	0x9
	.2byte	.LM70-.LM69
	.byte	0x1
	.byte	0x5
	.uleb128 0x1
	.byte	0
	.uleb128 0x9
	.byte	0x2
	.8byte	.LFE12
	.byte	0
	.uleb128 0x1
	.byte	0x1
.LELT0:
	.section	.debug_str,"MS",@progbits,1
.LASF31:
	.string	"uart_init"
.LASF32:
	.string	"printf_"
.LASF27:
	.string	"result"
.LASF20:
	.string	"__BOOT_ZSL_FW"
.LASF36:
	.string	"make_value"
.LASF14:
	.string	"uint64_t"
.LASF4:
	.string	"short int"
.LASF17:
	.string	"__BOOT_BAUDRATE"
.LASF35:
	.string	"main"
.LASF7:
	.string	"__uint32_t"
.LASF34:
	.string	"errors"
.LASF40:
	.string	"GNU C23 15.2.0 -mabi=lp64d -mcmodel=medany -mstrict-align -misa-spec=20191213 -march=rv64imafdc_zicsr_zifencei_zmmul_zaamo_zalrsc_zca_zcd -g -O2 -fno-builtin -fno-tree-vectorize -ffunction-sections -fdata-sections"
.LASF15:
	.string	"__base_regs"
.LASF39:
	.string	"offs"
.LASF33:
	.string	"clint_get_core_freq"
.LASF24:
	.string	"long long int"
.LASF29:
	.string	"greeting"
.LASF9:
	.string	"long int"
.LASF6:
	.string	"__uint8_t"
.LASF25:
	.string	"long double"
.LASF3:
	.string	"unsigned char"
.LASF37:
	.string	"temporary"
.LASF2:
	.string	"signed char"
.LASF22:
	.string	"__BOOT_DTB_TYPE_GUID"
.LASF13:
	.string	"uint32_t"
.LASF8:
	.string	"unsigned int"
.LASF41:
	.string	"reg32"
.LASF5:
	.string	"short unsigned int"
.LASF28:
	.string	"char"
.LASF26:
	.string	"seed"
.LASF16:
	.string	"__base_uart"
.LASF10:
	.string	"__uint64_t"
.LASF11:
	.string	"long unsigned int"
.LASF23:
	.string	"__BOOT_FW_TYPE_GUID"
.LASF12:
	.string	"uint8_t"
.LASF30:
	.string	"uart_write_flush"
.LASF21:
	.string	"__BOOT_ZSL_TYPE_GUID"
.LASF38:
	.string	"base"
.LASF18:
	.string	"__BOOT_SPM_MAX_LBAS"
.LASF19:
	.string	"__BOOT_ZSL_DTB"
	.section	.debug_line_str,"MS",@progbits,1
.LASF50:
	.string	"_stdint.h"
.LASF44:
	.string	"/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara/sw/include/dif"
.LASF48:
	.string	"journey.c"
.LASF46:
	.string	"/home/zhaowenyao/riscv_toolchain/riscv64-unknown-elf/include/machine"
.LASF45:
	.string	"/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara/sw/include"
.LASF0:
	.string	"/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara/docs_codex/learning/examples/journey.c"
.LASF51:
	.string	"params.h"
.LASF49:
	.string	"_default_types.h"
.LASF55:
	.string	"util.h"
.LASF47:
	.string	"/home/zhaowenyao/riscv_toolchain/riscv64-unknown-elf/include/sys"
.LASF42:
	.string	"/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara/docs_codex/learning/examples"
.LASF54:
	.string	"clint.h"
.LASF53:
	.string	"printf.h"
.LASF52:
	.string	"uart.h"
.LASF1:
	.string	"/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara"
.LASF43:
	.string	"/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara/sw/deps/printf"
	.ident	"GCC: (g5115c7e44) 15.2.0"
	.section	.note.GNU-stack,"",@progbits
