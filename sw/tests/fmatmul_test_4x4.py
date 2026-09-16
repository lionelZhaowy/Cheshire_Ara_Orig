import numpy as np

# 设置随机种子，保证每次生成的数据一致，方便在波形和串口中对照查错
np.random.seed(42)

# 生成 4x4 矩阵，数值限制在 -10.0 到 10.0 之间
A = np.random.uniform(-10.0, 10.0, (4, 4))
B = np.random.uniform(-10.0, 10.0, (4, 4))
# 计算基准结果 (Gold)
G = np.dot(A, B)

def print_c_array(name, matrix):
    flat = matrix.flatten()
    # 强制 32 字节对齐，以满足 AXI 总线和 Vector 访存的最佳性能要求
    print(f"double {name}[16] __attribute__((aligned(32))) = {{")
    for i in range(0, 16, 4):
        row_str = ", ".join([f"{val:>12.6f}" for val in flat[i:i+4]])
        print(f"    {row_str},")
    print("};")

print("// --- 请将以下代码直接复制到 main.c 中 ---")
print_c_array("mat_a", A)
print_c_array("mat_b", B)
print_c_array("mat_gold", G)
print("// -----------------------------------------")