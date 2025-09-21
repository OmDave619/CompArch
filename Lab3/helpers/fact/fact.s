# int temp = 1
# if(n==0) return temp
# while(n>=1) {
#     temp*=n
#     n--
# }

addi a0, a0, 0

fact:

    li t0, 1
    beq a0, x0, factExit

    factLoop:
        mul t0, t0, a0
        addi a0, a0, -1
        bne a0, x0, factLoop

    factExit:






