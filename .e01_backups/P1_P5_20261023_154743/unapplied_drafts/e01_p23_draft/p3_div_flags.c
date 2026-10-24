// E01 P3 draft: MVP #18 0/0 exception flags. NOT compiled or run.
// No subnormal operands or FS Dirty checks; #16 is outside this test.
#include <stdint.h>
#include "regs/cheshire.h"
#include "dif/clint.h"
#include "dif/uart.h"
#include "params.h"
#include "util.h"
#include "cheshire_util.h"

#define STR_(x) #x
#define STR(x) STR_(x)
#define UC(p) ((void *)((uintptr_t)(p)+0x04000000UL))
#define NV 0x10U
#define DZ 0x08U
static unsigned checks,failures;
volatile unsigned p3_case_id;

static void check(unsigned id,unsigned lane,uint64_t got,uint64_t want) {
  ++checks;
  if(got!=want) {
    if(failures<20)
      printf("P3_FAIL case=%u lane=%u got=%08x:%08x want=%08x:%08x\r\n",
             id,lane,(unsigned)(got>>32),(unsigned)got,
             (unsigned)(want>>32),(unsigned)want);
    ++failures;
  }
}
static void result(unsigned width,unsigned id,unsigned lane,
                   uint64_t got,uint64_t want,unsigned nan) {
  if(nan) {
    uint64_t exp=width==32?0x7f800000ULL:0x7ff0000000000000ULL;
    uint64_t frac=width==32?0x007fffffULL:0x000fffffffffffffULL;
    check(id,lane,(got&exp)==exp && (got&frac)!=0,1);
  } else check(id,lane,got,want);
}

struct scalar_case { uint64_t a,b,want; unsigned flags,nan; };
static const struct scalar_case sc32[] = {
  {0x00000000,0x00000000,0,NV,1},
  {0x00000000,0x80000000,0,NV,1},
  {0x80000000,0x00000000,0,NV,1},
  {0x80000000,0x80000000,0,NV,1},
  {0x40c00000,0x00000000,0x7f800000,DZ,0},
  {0x40c00000,0x80000000,0xff800000,DZ,0},
  {0xc0c00000,0x00000000,0xff800000,DZ,0},
  {0xc0c00000,0x80000000,0x7f800000,DZ,0},
  {0x40c00000,0x40000000,0x40400000,0,0},
  {0xc0c00000,0x40000000,0xc0400000,0,0}
};
static const struct scalar_case sc64[] = {
  {0x0000000000000000ULL,0x0000000000000000ULL,0,NV,1},
  {0x0000000000000000ULL,0x8000000000000000ULL,0,NV,1},
  {0x8000000000000000ULL,0x0000000000000000ULL,0,NV,1},
  {0x8000000000000000ULL,0x8000000000000000ULL,0,NV,1},
  {0x4018000000000000ULL,0x0000000000000000ULL,0x7ff0000000000000ULL,DZ,0},
  {0x4018000000000000ULL,0x8000000000000000ULL,0xfff0000000000000ULL,DZ,0},
  {0xc018000000000000ULL,0x0000000000000000ULL,0xfff0000000000000ULL,DZ,0},
  {0xc018000000000000ULL,0x8000000000000000ULL,0x7ff0000000000000ULL,DZ,0},
  {0x4018000000000000ULL,0x4000000000000000ULL,0x4008000000000000ULL,0,0},
  {0xc018000000000000ULL,0x4000000000000000ULL,0xc008000000000000ULL,0,0}
};

#define SCALAR(W,T,FMT,INMOVE,OUTMOVE) \
static void scalar##W(unsigned k,unsigned clear,unsigned expected_flags) { \
  const struct scalar_case *c=&sc##W[k]; \
  uintptr_t bits,flags; \
  const unsigned id=10000+W*100+k; \
  p3_case_id=id; \
  asm volatile( \
    INMOVE " ft0,%[a]\n" INMOVE " ft1,%[b]\n" \
    "beqz %[clear],1f\n csrw fflags,zero\n 1:\n" \
    "fdiv." FMT " ft2,ft0,ft1,rne\n" \
    OUTMOVE " %[bits],ft2\n" \
    "csrr %[flags],fflags\n" \
    :[bits]"=&r"(bits),[flags]"=&r"(flags) \
    :[a]"r"((uintptr_t)c->a),[b]"r"((uintptr_t)c->b),[clear]"r"(clear) \
    :"ft0","ft1","ft2","memory"); \
  result(W,id,0,(T)bits,c->want,c->nan); \
  check(id,90,flags,expected_flags); \
}
SCALAR(32,uint32_t,"s","fmv.w.x","fmv.x.w")
SCALAR(64,uint64_t,"d","fmv.d.x","fmv.x.d")

// Vector rows: all 0/0 signs; finite/zero signs; exact normal divisions;
// masked-off exceptional lanes; both active NV and DZ in a single instruction.
struct vector_case { uint64_t a[4],b[4],want[4]; unsigned nanmask,mask,flags; };
static const struct vector_case vc32[] = {
  {{0,0,0x80000000,0x80000000},{0,0x80000000,0,0x80000000},{0,0,0,0},15,15,NV},
  {{0x40c00000,0x40c00000,0xc0c00000,0xc0c00000},{0,0x80000000,0,0x80000000},
   {0x7f800000,0xff800000,0xff800000,0x7f800000},0,15,DZ},
  {{0x40c00000,0xc0c00000,0x41000000,0xc1000000},{0x40000000,0x40000000,0xc0000000,0xc0000000},
   {0x40400000,0xc0400000,0xc0800000,0x40800000},0,15,0},
  {{0x40c00000,0,0x40c00000,0x41000000},{0x40000000,0,0,0x40000000},
   {0x40400000,0x44800000,0x44800000,0x40800000},0,9,0},
  {{0,0x40c00000,0x40c00000,0x41000000},{0,0,0x40000000,0x40000000},
   {0,0x7f800000,0x40400000,0x40800000},1,15,NV|DZ}
};
static const struct vector_case vc64[] = {
  {{0,0,0x8000000000000000ULL,0x8000000000000000ULL},
   {0,0x8000000000000000ULL,0,0x8000000000000000ULL},{0,0,0,0},15,15,NV},
  {{0x4018000000000000ULL,0x4018000000000000ULL,0xc018000000000000ULL,0xc018000000000000ULL},
   {0,0x8000000000000000ULL,0,0x8000000000000000ULL},
   {0x7ff0000000000000ULL,0xfff0000000000000ULL,0xfff0000000000000ULL,0x7ff0000000000000ULL},0,15,DZ},
  {{0x4018000000000000ULL,0xc018000000000000ULL,0x4020000000000000ULL,0xc020000000000000ULL},
   {0x4000000000000000ULL,0x4000000000000000ULL,0xc000000000000000ULL,0xc000000000000000ULL},
   {0x4008000000000000ULL,0xc008000000000000ULL,0xc010000000000000ULL,0x4010000000000000ULL},0,15,0},
  {{0x4018000000000000ULL,0,0x4018000000000000ULL,0x4020000000000000ULL},
   {0x4000000000000000ULL,0,0,0x4000000000000000ULL},
   {0x4008000000000000ULL,0x4090000000000000ULL,0x4090000000000000ULL,0x4010000000000000ULL},0,9,0},
  {{0,0x4018000000000000ULL,0x4018000000000000ULL,0x4020000000000000ULL},
   {0,0,0x4000000000000000ULL,0x4000000000000000ULL},
   {0,0x7ff0000000000000ULL,0x4008000000000000ULL,0x4010000000000000ULL},1,15,NV|DZ}
};

#define VECTOR_ASM(W,SUFFIX) \
  "vle" STR(W) ".v v2,(%[a])\n" \
  "vle" STR(W) ".v v4,(%[b])\n" \
  "vle" STR(W) ".v v8,(%[out])\n" \
  "vlm.v v0,(%[mask])\n" \
  "vmv.x.s %[bits],v4\n" \
  "beqz %[clear],1f\n csrw fflags,zero\n 1:\n" \
  "vfdiv.vv v8,v2,v4" SUFFIX "\n" \
  "vse" STR(W) ".v v8,(%[out])\n" \
  "vmv.x.s %[bits],v8\n" \
  "fence\n csrr %[flags],fflags\n"
#define VOUTPUTS [bits]"=&r"(bits),[flags]"=&r"(flags)
#define VINPUTS [a]"r"(p->a),[b]"r"(p->b),[out]"r"(p->out),[mask]"r"(p->mask),[clear]"r"(clear)
#define VCLOBBERS "v0","v2","v4","v8","memory"
#define VECTOR(W,T,SENT) \
struct vector_data##W { T a[6],b[6],out[6]; uint8_t mask[8]; }; \
static struct vector_data##W vector_data##W __attribute__((aligned(64))); \
static void vector##W(unsigned k,unsigned clear,unsigned expected_flags) { \
  volatile struct vector_data##W *p=UC(&vector_data##W); \
  const struct vector_case *c=&vc##W[k]; \
  uintptr_t vl,bits,flags; const unsigned id=20000+W*100+k; \
  for(unsigned i=0;i<6;++i) { \
    p->a[i]=i<4?(T)c->a[i]:(T)SENT; \
    p->b[i]=i<4?(T)c->b[i]:(T)SENT; p->out[i]=SENT; \
  } \
  for(unsigned i=0;i<8;++i)p->mask[i]=0; p->mask[0]=c->mask; \
  p3_case_id=id; \
  asm volatile("fence\n vsetvli %0,%1,e" STR(W) ",m1,tu,mu" \
               :"=r"(vl):"r"((uintptr_t)4):"memory"); \
  check(id,91,vl,4); if(vl!=4)return; \
  if(c->mask==15) \
    asm volatile(VECTOR_ASM(W,""):VOUTPUTS:VINPUTS:VCLOBBERS); \
  else \
    asm volatile(VECTOR_ASM(W,",v0.t"):VOUTPUTS:VINPUTS:VCLOBBERS); \
  check(id,90,flags,expected_flags); \
  result(W,id,92,(T)bits,c->want[0],c->nanmask&1); \
  for(unsigned i=0;i<4;++i)result(W,id,i,p->out[i],c->want[i],(c->nanmask>>i)&1); \
  for(unsigned i=4;i<6;++i)check(id,i,p->out[i],SENT); \
}
VECTOR(32,uint32_t,0x44800000U)
VECTOR(64,uint64_t,0x4090000000000000ULL)

int main(void) {
  cheshire_start();
  uintptr_t ms,saved_frm;
  asm volatile("csrr %0,mstatus":"=r"(ms));
  check(0,0,((ms>>13)&3)!=0,1);
  // Current common.ldh gives spm.ld a 64 KiB window, starting at 0x10000000.
  check(0,1,(uintptr_t)&vector_data32>=0x10000000UL &&
        (uintptr_t)&vector_data32<=0x10010000UL-sizeof(vector_data32),1);
  check(0,2,(uintptr_t)&vector_data64>=0x10000000UL &&
        (uintptr_t)&vector_data64<=0x10010000UL-sizeof(vector_data64),1);
  if(failures) {
    printf("P3_PRECONDITION_FAIL: require FP enabled and spm.ld buffers\r\n");
    cheshire_end(); return 43;
  }
  asm volatile("csrs mstatus,%0"::"r"(0x600UL):"memory");
  asm volatile("csrrw %0,frm,zero":"=r"(saved_frm)::"memory");
  for(unsigned k=0;k<sizeof(sc32)/sizeof(sc32[0]);++k)scalar32(k,1,sc32[k].flags);
  for(unsigned k=0;k<sizeof(sc64)/sizeof(sc64[0]);++k)scalar64(k,1,sc64[k].flags);
  scalar32(0,1,NV); scalar32(4,0,NV|DZ);
  scalar64(0,1,NV); scalar64(4,0,NV|DZ);
  for(unsigned k=0;k<sizeof(vc32)/sizeof(vc32[0]);++k)vector32(k,1,vc32[k].flags);
  for(unsigned k=0;k<sizeof(vc64)/sizeof(vc64[0]);++k)vector64(k,1,vc64[k].flags);
  vector32(0,1,NV); vector32(1,0,NV|DZ);
  vector64(0,1,NV); vector64(1,0,NV|DZ);
  asm volatile("csrw frm,%0"::"r"(saved_frm):"memory");
  printf("P3_DONE c=%u e=%u\r\n",checks,failures);
  cheshire_end();
  return failures ? 43 : 0;
}
