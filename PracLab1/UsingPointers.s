# long long *p, *q;
# while (p) {
#     *q = *p;
#     q++;
#     p++;
# }
# p: x6
# q: x7

L1: beq x6, x0, Exit
ld x8, 0(x6)   # Load value pointed by p into x8
sd x8, 0(x7)   # Store value from x8 into location pointed by q
addi x6, x6, 8 # Move p to the next element (depends on the size of the data type)
addi x7, x7, 8 # Move q to the next element (q depends on the size of the data type)
beq x0, x0, L1 # Repeat the loop

Exit: 