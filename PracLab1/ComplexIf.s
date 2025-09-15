# if (p>=q || m==n) a++;
# b-=2;
# m: x10
# n: x11
# p: x12
# q: x13
# a: x14
# b: x15

bge x12, x13, op1
beq x10, x11, op1
beq x0, x0, op2
op1: addi x14, x14, 1
op2: addi x15, x15, -2
