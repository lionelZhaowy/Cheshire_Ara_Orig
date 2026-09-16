	.file	"asm-offsets.c"
	.option pic
	.attribute arch, "rv64i2p1_m2p0_a2p1_c2p0_zicsr2p0_zifencei2p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
# GNU C11 (Buildroot 2023.08-rc1) version 13.2.0 (riscv64-buildroot-linux-gnu)
#	compiled by GNU C version 13.3.0, GMP version 6.2.1, MPFR version 4.1.1, MPC version 1.2.1, isl version none
# GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072
# options passed: -mabi=lp64 -mcmodel=medlow -misa-spec=20191213 -march=rv64imac_zicsr_zifencei -g -gdwarf-2 -Os -std=gnu11 -fstack-protector-strong -fno-builtin -ffreestanding -fshort-wchar -fno-strict-aliasing -fno-stack-protector -fno-delete-null-pointer-checks -fstack-usage -ffixed-gp -fpic -fno-common -ffunction-sections -fdata-sections
	.text
.Ltext0:
	.file 1 "lib/asm-offsets.c"
	.section	.text.startup.main,"ax",@progbits
	.align	1
	.globl	main
	.type	main, @function
main:
.LFB132:
	.loc 1 21 1
	.cfi_startproc
	.loc 1 23 2
#APP
# 23 "lib/asm-offsets.c" 1
	
.ascii "->GENERATED_GBL_DATA_SIZE 400 (sizeof(struct global_data) + 15) & ~15"	#
# 0 "" 2
	.loc 1 26 2
# 26 "lib/asm-offsets.c" 1
	
.ascii "->GENERATED_BD_INFO_SIZE 160 (sizeof(struct bd_info) + 15) & ~15"	#
# 0 "" 2
	.loc 1 29 2
# 29 "lib/asm-offsets.c" 1
	
.ascii "->GD_SIZE 400 sizeof(struct global_data)"	#
# 0 "" 2
	.loc 1 31 2
# 31 "lib/asm-offsets.c" 1
	
.ascii "->GD_BD 0 offsetof(struct global_data, bd)"	#
# 0 "" 2
	.loc 1 33 2
# 33 "lib/asm-offsets.c" 1
	
.ascii "->GD_MALLOC_BASE 288 offsetof(struct global_data, malloc_base)"	#
# 0 "" 2
	.loc 1 36 2
# 36 "lib/asm-offsets.c" 1
	
.ascii "->GD_RELOCADDR 112 offsetof(struct global_data, relocaddr)"	#
# 0 "" 2
	.loc 1 38 2
# 38 "lib/asm-offsets.c" 1
	
.ascii "->GD_RELOC_OFF 152 offsetof(struct global_data, reloc_off)"	#
# 0 "" 2
	.loc 1 40 2
# 40 "lib/asm-offsets.c" 1
	
.ascii "->GD_START_ADDR_SP 144 offsetof(struct global_data, start_addr_sp)"	#
# 0 "" 2
	.loc 1 42 2
# 42 "lib/asm-offsets.c" 1
	
.ascii "->GD_NEW_GD 160 offsetof(struct global_data, new_gd)"	#
# 0 "" 2
	.loc 1 44 2
# lib/asm-offsets.c:45: }
	.loc 1 45 1 is_stmt 0
#NO_APP
	li	a0,0		#,
	ret	
	.cfi_endproc
.LFE132:
	.size	main, .-main
	.text
.Letext0:
	.file 2 "include/errno.h"
	.section	.debug_info,"",@progbits
.Ldebug_info0:
	.4byte	0xd2
	.2byte	0x2
	.4byte	.Ldebug_abbrev0
	.byte	0x8
	.byte	0x1
	.4byte	.LASF12
	.byte	0xc
	.4byte	.LASF13
	.4byte	.LASF14
	.4byte	.Ldebug_ranges0+0
	.8byte	0
	.8byte	0
	.4byte	.Ldebug_line0
	.byte	0x2
	.byte	0x4
	.byte	0x5
	.string	"int"
	.byte	0x3
	.4byte	0x5b
	.4byte	0x48
	.byte	0x4
	.4byte	0x4d
	.byte	0
	.byte	0
	.byte	0x5
	.4byte	0x38
	.byte	0x6
	.byte	0x8
	.byte	0x7
	.4byte	.LASF0
	.byte	0x6
	.byte	0x1
	.byte	0x8
	.4byte	.LASF1
	.byte	0x5
	.4byte	0x54
	.byte	0x7
	.4byte	.LASF15
	.byte	0x2
	.byte	0x1f
	.byte	0x13
	.4byte	0x48
	.string	""
	.byte	0x6
	.byte	0x2
	.byte	0x7
	.4byte	.LASF2
	.byte	0x6
	.byte	0x8
	.byte	0x5
	.4byte	.LASF3
	.byte	0x6
	.byte	0x4
	.byte	0x7
	.4byte	.LASF4
	.byte	0x6
	.byte	0x8
	.byte	0x5
	.4byte	.LASF5
	.byte	0x6
	.byte	0x1
	.byte	0x6
	.4byte	.LASF6
	.byte	0x6
	.byte	0x1
	.byte	0x8
	.4byte	.LASF7
	.byte	0x6
	.byte	0x2
	.byte	0x5
	.4byte	.LASF8
	.byte	0x6
	.byte	0x8
	.byte	0x7
	.4byte	.LASF9
	.byte	0x6
	.byte	0x10
	.byte	0x4
	.4byte	.LASF10
	.byte	0x6
	.byte	0x1
	.byte	0x2
	.4byte	.LASF11
	.byte	0x8
	.byte	0x1
	.4byte	.LASF16
	.byte	0x1
	.byte	0x14
	.byte	0x5
	.byte	0x1
	.4byte	0x31
	.8byte	.LFB132
	.8byte	.LFE132
	.byte	0x2
	.byte	0x72
	.byte	0
	.byte	0x1
	.byte	0
	.section	.debug_abbrev,"",@progbits
.Ldebug_abbrev0:
	.byte	0x1
	.byte	0x11
	.byte	0x1
	.byte	0x25
	.byte	0xe
	.byte	0x13
	.byte	0xb
	.byte	0x3
	.byte	0xe
	.byte	0x1b
	.byte	0xe
	.byte	0x55
	.byte	0x6
	.byte	0x11
	.byte	0x1
	.byte	0x52
	.byte	0x1
	.byte	0x10
	.byte	0x6
	.byte	0
	.byte	0
	.byte	0x2
	.byte	0x24
	.byte	0
	.byte	0xb
	.byte	0xb
	.byte	0x3e
	.byte	0xb
	.byte	0x3
	.byte	0x8
	.byte	0
	.byte	0
	.byte	0x3
	.byte	0x1
	.byte	0x1
	.byte	0x49
	.byte	0x13
	.byte	0x1
	.byte	0x13
	.byte	0
	.byte	0
	.byte	0x4
	.byte	0x21
	.byte	0
	.byte	0x49
	.byte	0x13
	.byte	0x2f
	.byte	0xb
	.byte	0
	.byte	0
	.byte	0x5
	.byte	0x26
	.byte	0
	.byte	0x49
	.byte	0x13
	.byte	0
	.byte	0
	.byte	0x6
	.byte	0x24
	.byte	0
	.byte	0xb
	.byte	0xb
	.byte	0x3e
	.byte	0xb
	.byte	0x3
	.byte	0xe
	.byte	0
	.byte	0
	.byte	0x7
	.byte	0x34
	.byte	0
	.byte	0x3
	.byte	0xe
	.byte	0x3a
	.byte	0xb
	.byte	0x3b
	.byte	0xb
	.byte	0x39
	.byte	0xb
	.byte	0x49
	.byte	0x13
	.byte	0x1c
	.byte	0x8
	.byte	0
	.byte	0
	.byte	0x8
	.byte	0x2e
	.byte	0
	.byte	0x3f
	.byte	0xc
	.byte	0x3
	.byte	0xe
	.byte	0x3a
	.byte	0xb
	.byte	0x3b
	.byte	0xb
	.byte	0x39
	.byte	0xb
	.byte	0x27
	.byte	0xc
	.byte	0x49
	.byte	0x13
	.byte	0x11
	.byte	0x1
	.byte	0x12
	.byte	0x1
	.byte	0x40
	.byte	0xa
	.byte	0x97,0x42
	.byte	0xc
	.byte	0
	.byte	0
	.byte	0
	.section	.debug_aranges,"",@progbits
	.4byte	0x2c
	.2byte	0x2
	.4byte	.Ldebug_info0
	.byte	0x8
	.byte	0
	.2byte	0
	.2byte	0
	.8byte	.LFB132
	.8byte	.LFE132-.LFB132
	.8byte	0
	.8byte	0
	.section	.debug_ranges,"",@progbits
.Ldebug_ranges0:
	.8byte	.LFB132
	.8byte	.LFE132
	.8byte	0
	.8byte	0
	.section	.debug_line,"",@progbits
.Ldebug_line0:
	.section	.debug_str,"MS",@progbits,1
.LASF4:
	.string	"unsigned int"
.LASF16:
	.string	"main"
.LASF12:
	.ascii	"GNU C11 13.2.0 -mabi=lp64 -mcmodel=medlow -misa-spec=2019121"
	.ascii	"3 -march=rv64imac_zicsr_"
	.string	"zifencei -g -gdwarf-2 -Os -std=gnu11 -fstack-protector-strong -fno-builtin -ffreestanding -fshort-wchar -fno-strict-aliasing -fno-stack-protector -fno-delete-null-pointer-checks -fstack-usage -ffixed-gp -fpic -fno-common -ffunction-sections -fdata-sections"
.LASF0:
	.string	"long unsigned int"
.LASF9:
	.string	"long long unsigned int"
.LASF14:
	.string	"/home/zhaowenyao/RISC_CVA6_prj/cheshire_ara/.bender/git/checkouts/ara-2c7b103275a16c87/cheshire/sw/cva6-sdk/u-boot"
.LASF7:
	.string	"unsigned char"
.LASF13:
	.string	"lib/asm-offsets.c"
.LASF1:
	.string	"char"
.LASF3:
	.string	"long int"
.LASF15:
	.string	"error_message"
.LASF11:
	.string	"_Bool"
.LASF5:
	.string	"long long int"
.LASF2:
	.string	"short unsigned int"
.LASF6:
	.string	"signed char"
.LASF10:
	.string	"long double"
.LASF8:
	.string	"short int"
	.ident	"GCC: (Buildroot 2023.08-rc1) 13.2.0"
	.section	.note.GNU-stack,"",@progbits
