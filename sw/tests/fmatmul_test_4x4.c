#include "regs/cheshire.h"
#include "dif/clint.h"
#include "dif/uart.h"
#include "params.h"
#include "printf.h" 
#include "util.h"   // <--- 新增这一行，提供 reg32 宏定义

#define THRESHOLD 0.001

// ==========================================
// 1. Python 生成的测试数据 (请用脚本输出替换)
// ==========================================
double mat_a[16] __attribute__((aligned(32))) = {
       -2.509198,     9.014286,     4.639879,     1.973170,
       -6.879627,    -6.880110,    -8.838328,     7.323523,
        2.022300,     4.161452,    -9.588310,     9.398197,
        6.648853,    -5.753218,    -6.363501,    -6.331910,
};
double mat_b[16] __attribute__((aligned(32))) = {
       -3.915155,     0.495129,    -1.361100,    -4.175417,
        2.237058,    -7.210123,    -4.157107,    -2.672763,
       -0.878600,     5.703519,    -6.006524,     0.284689,
        1.848291,    -9.070992,     2.150897,    -6.589518,
};
double mat_gold[16] __attribute__((aligned(32))) = {
       29.559771,   -57.671453,   -57.683545,   -25.297420,
       32.844966,   -70.641054,   106.804985,    -3.660438,
       27.186688,  -168.941357,    57.754821,   -84.225790,
      -45.013812,    65.915797,    39.470227,    27.527867,
};

double mat_c_scalar[16] __attribute__((aligned(32))) = {0};
double mat_c_vector[16] __attribute__((aligned(32))) = {0};
// -----------------------------------------
// 2. 性能测试工具
// ==========================================
static inline uint64_t get_cycle() {
    uint64_t cycle;
    __asm__ __volatile__("rdcycle %0" : "=r"(cycle));
    return cycle;
}

static inline uint64_t get_instret() {
    uint64_t instret;
    __asm__ __volatile__("rdinstret %0" : "=r"(instret));
    return instret;
}

// ==========================================
// 3. 标量基准函数 (Pure Scalar Matrix Mul)
// ==========================================
void fmatmul_scalar(double *c, const double *a, const double *b, int M, int N, int P) {
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < P; j++) {
            double sum = 0.0;
            for (int k = 0; k < N; k++) {
                sum += a[i * N + k] * b[k * P + j];
            }
            c[i * P + j] = sum;
        }
    }
}

// ==========================================
// 4. 向量加速函数 (从原工程解耦的底层实现)
// ==========================================
void fmatmul_vec_4x4_slice_init() {
    asm volatile("vmv.v.i v0,  0");
    asm volatile("vmv.v.i v4,  0");
    asm volatile("vmv.v.i v8,  0");
    asm volatile("vmv.v.i v12, 0");
}

void fmatmul_vec_4x4(double *c, const double *a, const double *b, const unsigned long int N, const unsigned long int P) {
    double t0, t1, t2, t3;
    const double *a_ = a;

    asm volatile("vle64.v v16, (%0);" ::"r"(b));
    b += P;

    t0 = *a, a += N;
    t1 = *a, a += N;
    t2 = *a, a += N;
    t3 = *a;

    unsigned long int n = 0;
    while (n != N) {
        a = a_ + ++n;

        asm volatile("vfmacc.vf v0, %0, v16" ::"f"(t0));
        t0 = *a, a += N;

        asm volatile("vle64.v v20, (%0);" ::"r"(b));
        b += P;

        asm volatile("vfmacc.vf v4, %0, v16" ::"f"(t1));
        t1 = *a, a += N;
        asm volatile("vfmacc.vf v8, %0, v16" ::"f"(t2));
        t2 = *a, a += N;
        asm volatile("vfmacc.vf v12, %0, v16" ::"f"(t3));
        t3 = *a;

        a = a_ + ++n;
        if (n == N) break;

        asm volatile("vfmacc.vf v0, %0, v20" ::"f"(t0));
        t0 = *a, a += N;

        asm volatile("vle64.v v16, (%0);" ::"r"(b));
        b += P;

        asm volatile("vfmacc.vf v4, %0, v20" ::"f"(t1));
        t1 = *a, a += N;
        asm volatile("vfmacc.vf v8, %0, v20" ::"f"(t2));
        t2 = *a, a += N;
        asm volatile("vfmacc.vf v12, %0, v20" ::"f"(t3));
        t3 = *a;
    }

    asm volatile("vfmacc.vf v0, %0, v20" ::"f"(t0));
    asm volatile("vse64.v v0, (%0);" ::"r"(c));  c += P;
    asm volatile("vfmacc.vf v4, %0, v20" ::"f"(t1));
    asm volatile("vse64.v v4, (%0);" ::"r"(c));  c += P;
    asm volatile("vfmacc.vf v8, %0, v20" ::"f"(t2));
    asm volatile("vse64.v v8, (%0);" ::"r"(c));  c += P;
    asm volatile("vfmacc.vf v12, %0, v20" ::"f"(t3));
    asm volatile("vse64.v v12, (%0);" ::"r"(c));
}

void fmatmul_4x4(double *c, const double *a, const double *b, const unsigned long int M, const unsigned long int N, const unsigned long int P) {
    const unsigned long int block_size = 4;
    unsigned long int block_size_p;

    asm volatile("vsetvli %0, %1, e64, m4, ta, ma" : "=r"(block_size_p) : "r"(P));

    for (unsigned long int p = 0; p < P; p += block_size_p) {
        const unsigned long int p_ = MIN(P - p, block_size_p);
        const double *b_ = b + p;
        double *c_ = c + p;

        asm volatile("vsetvli zero, %0, e64, m4, ta, ma" ::"r"(p_));

        for (unsigned long int m = 0; m < M; m += block_size) {
            const double *a_ = a + m * N;
            double *c__ = c_ + m * P;

            fmatmul_vec_4x4_slice_init();
            fmatmul_vec_4x4(c__, a_, b_, N, P);
        }
    }
}

// ==========================================
// 5. 结果校验逻辑
// ==========================================
int verify_result(double *res, double *gold, int size) {
    for (int i = 0; i < size; i++) {
        double diff = res[i] - gold[i];
        // 浮点数比较需要使用一个很小的阈值
        if (diff > THRESHOLD || diff < -THRESHOLD) {
            printf("Mismatch at index [%d]: Expected %f, Got %f\r\n", i, gold[i], res[i]);
            return -1;
        }
    }
    return 0; // Passed
}

// ==========================================
// Main 函数
// ==========================================
int main(void) {
    // 关键！开启 Vector (mstatus.VS) 和 FPU (mstatus.FS) 单元
    // FS = bits[14:13], VS = bits[10:9] -> 设置为 11 (Dirty/Initial)
    asm volatile("csrs mstatus, %0" :: "r"((3 << 13) | (3 << 9)));

    // 初始化 UART
    uint32_t rtc_freq = *reg32(&__base_regs, CHESHIRE_RTC_FREQ_REG_OFFSET);
    uint64_t reset_freq = clint_get_core_freq(rtc_freq, 2500);
    uart_init(&__base_uart, reset_freq, __BOOT_BAUDRATE);

    printf("\r\n==============================================\r\n");
    printf("=   Ara Vector Bare-metal Test: fmatmul_4x4  =\r\n");
    printf("==============================================\r\n");

    uint64_t begin_instret, end_instret;
    uint64_t begin_cycle, end_cycle;

    // ------------------------------------------
    // 测试 1：纯标量 (Scalar) 版本
    // ------------------------------------------
    begin_instret = get_instret();
    begin_cycle   = get_cycle();
    
    fmatmul_scalar(mat_c_scalar, mat_a, mat_b, 4, 4, 4);
    
    end_instret = get_instret();
    end_cycle   = get_cycle();
    
    uint64_t scalar_instret = end_instret - begin_instret;
    uint64_t scalar_cycle   = end_cycle - begin_cycle;

    // ------------------------------------------
    // 测试 2：RVV 向量化 (Vector) 版本
    // ------------------------------------------
    begin_instret = get_instret();
    begin_cycle   = get_cycle();
    
    fmatmul_4x4(mat_c_vector, mat_a, mat_b, 4, 4, 4);
    
    end_instret = get_instret();
    end_cycle   = get_cycle();
    
    uint64_t vector_instret = end_instret - begin_instret;
    uint64_t vector_cycle   = end_cycle - begin_cycle;

    // ------------------------------------------
    // 打印对比结果与校验
    // ------------------------------------------
    printf("\r\n[Scalar] Performance:\r\n");
    printf("  Instret : %llu\r\n", (unsigned long long)scalar_instret);
    printf("  Cycles  : %llu\r\n", (unsigned long long)scalar_cycle);

    printf("\r\n[Vector] Performance:\r\n");
    printf("  Instret : %llu\r\n", (unsigned long long)vector_instret);
    printf("  Cycles  : %llu\r\n", (unsigned long long)vector_cycle);

    // 计算加速比
    float speedup = (float)scalar_cycle / (float)vector_cycle;
    printf("\r\n=> Hardware Speedup (Cycles): %.2f x\r\n", speedup);

    printf("\r\nVerifying Scalar Result... ");
    if(verify_result(mat_c_scalar, mat_gold, 16) == 0) printf("PASS\r\n");

    printf("Verifying Vector Result... ");
    if(verify_result(mat_c_vector, mat_gold, 16) == 0) printf("PASS\r\n");

    printf("==============================================\r\n");

    return 0;
}