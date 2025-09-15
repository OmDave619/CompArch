# CO22BTECH11006 (Om Dave)

.data              
.dword 8
.dword 12, 3
.dword 125, 50
.dword 16, 32
.dword 0, 99
.dword 42, 42
.dword 14, 25
.dword 1003209532909520095, 0
.dword 8320400993652343220, 5142200000763463264

.text            

lui x6, 0x10000     # Initialize x6 for memory addressing for input
addi x8, x6, 512    # Initialize x8 for memory addressing for output
ld x7, 0(x6)        # Stores the count of gcd pairs 
addi x6, x6, 8      # Move to the next memory location for inputs

# Logic 
# while(x7) {
#     # scan numbers 
#     # calc gcd 
#     # store data 
#     x7--
# }

Loop:
    
    beq x7, x0, Exit    # If count is 0, exit loop

    ld x2, 0(x6)        # Load first number into x2
    ld x3, 8(x6)        # Load second number into x3

    # Calculate GCD (gcd(x2, x3) will be stored in x2 itself)
    gcd_Loop:
        beq x2, x0, gcd_Exit
        bne x3, x0, Check
        sub x2, x2, x2
        beq x0, x0, gcd_Exit

    Check:
        beq x2, x3, gcd_Exit
        bgeu x3, x2, Sub

    Swap:
        add   x5, x0, x3
        add   x3, x0, x2
        add   x2, x0, x5

    Sub:
        sub x3, x3, x2
        bne x3, x2, gcd_Loop

    gcd_Exit:
        sd x2, 0(x8)    # Store GCD result in output memory

    # Increment input and output pointer
    addi x6, x6, 16     # Move to the next pair of inputs
    addi x8, x8, 8

    # Decrement the count of GCD pairs
    addi x7, x7, -1

    beq x0, x0, Loop 

Exit:


