# .data              
# .word 12, 3

# .text

# lui x10, 0x10000
# addi x11, x10, 512  # Base address for input and output

# # x (float) in f1 using int to float conversion 
# lw x5, 0(x10)  
# fcvt.s.w f1, x5

# # n (int) in x1
# lw x1, 4(x10)  

# # logic
# # if(n==0) return 1;
# # temp = x
# # while(n) {
# #     temp = temp*x
# #     n--
# # }

# pow:
#     li x5, 1
#     fcvt.s.w f2, x5

#     Loop:
#     beq x1, x0, pow_Exit  # if n == 0, exit loop
#     fmul.s f2, f2, f1
#     addi x1, x1, -1
#     beq x0, x0, Loop

#     pow_Exit:
#     fsd f2, 0(x11)  # Store result in memory location of f2

.data
# Layout: T, x1_bits, n1, x2_bits, n2, ..., xT_bits, nT
# test.py will overwrite the line below with your cases.
.word 10, 
    0x40200000, 0,  
    0x3fc00000, 2,   
    0x40200000, 3,  
    0x3fc00000, 4, 
    0x40200000, 5,  
    0x3fc00000, 6,   
    0x00000000, 7,
    0x3f800000, 3,  
    0x40000000, 2,  
    0x3f19999a, 5  
   # example: T=1, x=1.0f bits, n=3

.text
lui   t0, 0x10000           # t0 = 0x10000000 (input base)
addi  t1, t0, 512           # t1 = 0x10000200 (output base)

# Load T and set pointers
lw    t2, 0(t0)             # t2 = T
addi  t0, t0, 4             # t0 -> first x_bits
mv    t3, t1                # t3 = output pointer

LoopPairs:
    beq   t2, x0, DonePairs     # if T==0, finish

    # Load one (x_bits, n)
    flw   fa0, 0(t0)            # fa0 = x_i (interpret 32-bit bits as float)
    lw    t5,  4(t0)            # t5  = n_i (int)
    addi  t0, t0, 8             # advance input ptr

    # result = 1.0f (accumulator)
    li    t6, 1
    fcvt.s.w ft1, t6            # ft1 = 1.0f

PowLoop:
    beq   t5, x0, PowExit
    fmul.s ft1, ft1, fa0        # single-precision multiply
    addi  t5,  t5,  -1
    beq  x0,  x0, PowLoop

PowExit:
    fsd   ft1, 0(t3)            # store 8 bytes/result (float in low 32 bits)
    addi  t3,  t3,  8           # next output slot
    addi  t2,  t2, -1
    beq   x0,  x0, LoopPairs

DonePairs:
    # Program end; VM should report VM_PROGRAM_END


