ADDI x2, x0, 42     # x2 = 42
STORE   x2, 0(x1)      # MEM[x1+0] = x2 (store word)
LOAD   x3, 0(x1)      # x3 = MEM[x1+0] (load word)