
.data
.word 0x40000000, 7   # 2.0 in IEEE 754, upto 8 terms 

.text

lui t0, 0x10000
addi  t1, t0, 512 
flw fa0, 0(t0) 
lw a0, 4(t0)
jal ra, exp
fsw fa0, 0(t1)
beq x0, x0, Exit

# Input: a0 = n
# Output: a0 = n!
# uses: t0
fact:
    li t0, 1
    beq a0, x0, factExit

    factLoop:
        mul t0, t0, a0
        addi a0, a0, -1
        bne a0, x0, factLoop

    factExit:
        mv a0, t0
        jalr x0, 0(ra)


# Input: fa0 = x (float), a0 = n (int)
# Output: fa0 = x^n (float)
# uses: t0, ft0
pow:
    li t0, 1
    fcvt.s.w ft0, t0            # ft0 = 1.0f

    powLoop:
        beq a0, x0, powExit            # if n == 0, exit loop
        fmul.s ft0, ft0, fa0        # ft0 = ft0 * x
        addi a0, a0, -1
        beq x0, x0, powLoop

    powExit:
        fsgnj.s fa0, ft0, ft0  # move result to fa0
        jalr x0, 0(ra)



# e^x
# int terms;
# int temp0 = 0  (saved reg fs0)
# while(terms) {
#     terms--;
#     temp1 = fact(terms);
#     temp2 = pow(x, terms);
#     temp3 = temp2/temp1;
#     temp0 += temp3;
# }

# # Input: fa0 = x (float), a0 = terms (int)
# # Output: fa0 = e^x (float)
exp:
    li t0, 0                     # temp0 = 0
    fcvt.s.w fs0, t0            # fs0 = 0.0f

    addi sp, sp, -16        # make space on stack
    sw ra, 0(sp)            # save return address
    fsw fa0, 4(sp)           # save input x
    sw a0, 8(sp)             # save terms

    expLoop:
        beq a0, x0, expExit            # while(terms)
        addi a0, a0, -1                # terms--

        sw a0, 8(sp)                    # store a0, will be used in fact

        jal ra, fact                 # compute fact(terms)
        fcvt.s.w ft1, a0            # store ans as float
        
        lw a0, 8(sp)                             
        fsw fa0, 4(sp)

        jal ra, pow                    # compute pow(x, terms)
        fsgnj.s ft2, fa0, fa0 

        flw fa0, 4(sp)
        lw a0, 8(sp)

        fdiv.s ft3, ft2, ft1    # ft3 = temp2/temp1
        fadd.s fs0, fs0, ft3    # temp0 += temp3

        beq x0, x0, expLoop

    expExit:
        lw ra, 0(sp)            # restore return address
        addi sp, sp, 16          # restore stack pointer
        fsgnj.s fa0, fs0, fs0  # move result to fa0
        jalr x0, 0(ra)

Exit:

