
.data
.word 0x40000000, 5   # 2.0 in IEEE 754, upto 8 terms 

.text

lui t0, 0x10000
flw fa0, 0(t0) 
lw a0, 4(t0)
jal ra, lnx
lui t0, 0x10000
addi t1, t0, 512 
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

# sin(x)
# int terms;
# int temp0 = 0  (saved reg fs0)
# while(terms) {
#     terms--;
#     k = terms;                       
#     e = 2*k + 1;                    
#     temp1 = fact(e);                 # (2k+1)!
#     temp2 = pow(x, e);               # x^(2k+1)
#     temp3 = temp2/temp1;             
#     if (k is odd) temp3 = -temp3;    # alternating sign
#     temp0 += temp3;
# }

# # Input: fa0 = x (float), a0 = terms (int)
# # Output: fa0 = sin(x) (float)
sin:
    li t0, 0                      # temp0 = 0
    fcvt.s.w fs0, t0              # fs0 = 0.0f

    addi sp, sp, -16              # make space on stack
    sw   ra, 0(sp)                # save return address
    fsw  fa0, 4(sp)               # save input x
    sw   a0, 8(sp)                # save terms

    sinLoop:
        beq  a0, x0, sinExit          # while(terms)
        addi a0, a0, -1               # terms--

        sw   a0, 8(sp)                # store k (= current terms)

        mv   t2, a0                    # t2 = k
        slli t3, t2, 1                 # t3 = 2*k
        addi t3, t3, 1                 # t3 = 2*k + 1

        mv   a0, t3
        jal  ra, fact               # compute fact(e)
        fcvt.s.w ft1, a0            # ft1 = float(temp1)

        # temp2 = pow(x, e); ft2 = temp2
        fsw  fa0, 4(sp)               

        mv   a0, t3                   # a0 = e
        jal  ra, pow
        fsgnj.s ft2, fa0, fa0

        flw  fa0, 4(sp)
        lw   a0, 8(sp)

        # temp3 = temp2 / temp1
        fdiv.s ft3, ft2, ft1

        # if (k is odd) temp3 = -temp3
        andi t4, a0, 1
        beq  t4, x0, sinEven
        fsgnjn.s ft3, ft3, ft3        # negate: ft3 = -ft3

    sinEven:
        fadd.s fs0, fs0, ft3 # temp0 += temp3
        beq  x0, x0, sinLoop

    sinExit:
        lw   ra, 0(sp)                # restore return address
        addi sp, sp, 16               # restore stack pointer
        fsgnj.s fa0, fs0, fs0         # move result to fa0
        jalr x0, 0(ra)

# cos(x)
# int terms;
# int temp0 = 0  (saved reg fs0)
# while(terms) {
#     terms--;
#     k = terms;                       
#     e = 2*k;                         
#     temp1 = fact(e);                 # (2k)!
#     temp2 = pow(x, e);               # x^(2k)
#     temp3 = temp2/temp1;             
#     if (k is odd) temp3 = -temp3;    # alternating sign
#     temp0 += temp3;
# }

# # Input: fa0 = x (float), a0 = terms (int)
# # Output: fa0 = cos(x) (float)
cos:
    li t0, 0                       # temp0 = 0
    fcvt.s.w fs0, t0               # fs0 = 0.0f

    addi sp, sp, -16               # make space on stack
    sw   ra, 0(sp)                 # save return address
    fsw  fa0, 4(sp)                # save input x
    sw   a0, 8(sp)                 # save terms

    cosLoop:
        beq  a0, x0, cosExit       # while(terms)
        addi a0, a0, -1            # terms--

        sw   a0, 8(sp)             # store k (= current terms)

        mv   t2, a0                # t2 = k
        slli t3, t2, 1             # t3 = 2*k          (e = 2k)

        # temp1 = fact(e); ft1 = float(temp1)
        mv   a0, t3
        jal  ra, fact
        fcvt.s.w ft1, a0

        # temp2 = pow(x, e); ft2 = temp2
        fsw  fa0, 4(sp)            # keep style same as exp/sin
        mv   a0, t3                # a0 = e
        jal  ra, pow
        fsgnj.s ft2, fa0, fa0

        flw  fa0, 4(sp)            # restore x to fa0 (style parity)
        lw   a0, 8(sp)             # restore k to a0

        # temp3 = temp2 / temp1
        fdiv.s ft3, ft2, ft1

        # if (k is odd) temp3 = -temp3
        andi t4, a0, 1
        beq  t4, x0, cosEven
        fsgnjn.s ft3, ft3, ft3     # negate: ft3 = -ft3

    cosEven:
        fadd.s fs0, fs0, ft3       # temp0 += temp3
        beq  x0, x0, cosLoop

    cosExit:
        lw   ra, 0(sp)             # restore return address
        addi sp, sp, 16            # restore stack pointer
        fsgnj.s fa0, fs0, fs0      # move result to fa0
        jalr x0, 0(ra)


# ln(x)
# int terms;
# int temp0 = 0  (saved reg fs0)
# while(terms) {
#     k   = terms;                 # use current terms directly
#     u   = x - 1;
#     temp1 = k;                   # as float
#     temp2 = pow(u, k);           # u^k
#     temp3 = temp2 / temp1;       # u^k / k
#     if (k is even) temp3 = -temp3;   # (-1)^{k+1}
#     temp0 += temp3;
#     terms--;
# }
#
# # Input: fa0 = x (float), a0 = terms (int)
# # Output: fa0 = ln(x) (float)
lnx:
    li  t0, 0                      # temp0 = 0
    fcvt.s.w fs0, t0               # fs0 = 0.0f

    # u = x - 1.0f 
    li    t1, 1
    fcvt.s.w ft4, t1               # ft4 = 1.0f
    fsub.s ft4, fa0, ft4           # ft4 = x - 1.0 = u

    addi sp, sp, -16               # make space on stack
    sw   ra, 0(sp)                 # save return address
    fsw  ft4, 4(sp)                # save var u = x - 1
    sw   a0, 8(sp)                 # save terms

    lnLoop:
        beq  a0, x0, lnExit            # while(terms)
        sw   a0, 8(sp)                 # store k (= current terms)
        mv   t2, a0                    # t2 = k

        # temp1 = float(k) -> ft1
        fcvt.s.w ft1, t2

        # temp2 = pow(u, k) -> ft2
        flw  fa0, 4(sp)                # fa0 = u
        mv   a0,  t2                   # a0  = k
        jal  ra, pow
        fsgnj.s ft2, fa0, fa0

        # temp3 = temp2 / temp1
        fdiv.s ft3, ft2, ft1

        # if (k is even) temp3 = -temp3  (since (-1)^{k+1})
        andi t4, t2, 1
        bne  t4, x0, lnOdd             # odd -> keep sign
        fsgnjn.s ft3, ft3, ft3         # even -> negate
    
    lnOdd:
        # temp0 += temp3
        fadd.s fs0, fs0, ft3

        mv   a0, t2
        addi a0, a0, -1                # terms--
        beq  x0, x0, lnLoop

    lnExit:
        lw   ra, 0(sp)                 # restore return address
        addi sp, sp, 16                # restore stack pointer
        fsgnj.s fa0, fs0, fs0          # move result to fa0
        jalr x0, 0(ra)

Exit:

