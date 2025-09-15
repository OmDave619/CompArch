# We need to merge words (32 bit) P and Q to form PQ (64-bit)
# P: x5
# Q: x6

lwu x7, 0(x5)   # Load lower 32 bits from P into x7
lwu x8, 0(x6)   # Load lower 32 bits from Q
slli x7, x7, 32 # Shift P left by 32 bits
add x7, x7, x8  # Combine P and Q, or/xor can be also be used 


