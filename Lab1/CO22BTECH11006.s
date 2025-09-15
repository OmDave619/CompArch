# CO22BTECH11006 (Final program with extended)

lui x1, 0x10000     

ld x7, 0(x1)         
ld x8, 8(x1)        

sub x9, x9, x9        
addi x2, x0, 0        

blt x7, x0, neg_a
beq x0, x0, check_b

neg_a:
sub x7, x0, x7        
addi x2, x2, 1       

check_b:
blt x8, x0, neg_b
beq x0, x0, loop

neg_b:
sub x8, x0, x8       
xori x2, x2, 1     
  
loop:
beq x8, x0, add_sign
add x9, x9, x7    
addi x8, x8, -1
beq x0, x0, loop

add_sign:
beq x2, x0, store_ans
sub x9, x0, x9       

store_ans:
sd x9, 80(x1)        
