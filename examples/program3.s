ADDI x1, x0, 0xF0F0
ADDI x2, x0, 0x0FF0
AND x3, x1, x2  # → x3 = 0x00F0
OR  x4, x1, x2  # → x4 = 0xFFF0
XOR x5, x1, x2  # → x5 = 0xFF00
