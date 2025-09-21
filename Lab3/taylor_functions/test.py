# Float32 Taylor-series exp & sin verifiers for RISC-V lab
# - Mirrors the user's helper-based algorithm exactly (pow_f32 + fact_int), with float32 rounding
# - Sums terms in the SAME order as the assembly loop: terms-1 down to 0
# - Prints IEEE-754 single-precision hex for easy matching with simulator outputs

import struct

def to_f32(x: float) -> float:
    """Round Python float to IEEE-754 single precision (float32)."""
    return struct.unpack('>f', struct.pack('>f', float(x)))[0]

def f32_hex(f: float) -> str:
    """Return hex of IEEE-754 float32 bits (e.g., 0x3f800000)."""
    b = struct.pack('>f', float(f))
    u = struct.unpack('>I', b)[0]
    return f"0x{u:08x}"

def fact_int(n: int) -> int:
    """Exact integer factorial (non-negative)."""
    if n <= 1:
        return 1
    p = 1
    for k in range(2, n+1):
        p *= k
    return p

def pow_f32(x_f32: float, n: int) -> float:
    """Compute x^n using float32 multiplies each step."""
    x = to_f32(x_f32)
    if n == 0:
        return to_f32(1.0)
    acc = to_f32(1.0)
    for _ in range(n):
        acc = to_f32(acc * x)
    return acc

def exp_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    """exp(x) ≈ sum_{n=0..terms-1} x^n/n!, using helpers, summing n=terms-1..0 (float32)."""
    s = to_f32(0.0)
    for n in range(terms-1, -1, -1):
        fn = fact_int(n)
        fn_f32 = to_f32(float(fn))
        px = pow_f32(x_f32, n)
        term = to_f32(px / fn_f32)
        s = to_f32(s + term)
    return s

def sin_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    """
    sin(x) ≈ sum_{k=0..terms-1} (-1)^k * x^(2k+1)/(2k+1)!
    Implemented to mirror assembly structure:
      for k in terms-1 down to 0:
        e = 2*k + 1
        term = pow_f32(x,e) / float32(fact_int(e))
        if k is odd: term = -term
        s += term
    All ops rounded to float32.
    """
    s = to_f32(0.0)
    for k in range(terms-1, -1, -1):
        e = 2*k + 1
        fe = fact_int(e)
        fe_f32 = to_f32(float(fe))
        px = pow_f32(x_f32, e)
        term = to_f32(px / fe_f32)
        if (k & 1) == 1:  # odd k -> negative term
            term = to_f32(-term)
        s = to_f32(s + term)
    return s

def cos_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    """
    cos(x) ≈ sum_{k=0..terms-1} (-1)^k * x^(2k)/(2k)!
    Mirrors the assembly structure:
      for k = terms-1 down to 0:
        e = 2*k
        term = pow_f32(x,e) / float32(fact_int(e))
        if k is odd: term = -term
        s += term
    All ops rounded to float32.
    """
    s = to_f32(0.0)
    for k in range(terms-1, -1, -1):
        e = 2*k
        fe = fact_int(e)
        fe_f32 = to_f32(float(fe))
        px = pow_f32(x_f32, e)
        term = to_f32(px / fe_f32)
        if (k & 1) == 1:
            term = to_f32(-term)
        s = to_f32(s + term)
    return s


# Quick demo: x=2.0f; terms for exp and sin (you can adjust)
x = to_f32(1.0)
terms = 5

ex = exp_taylor_f32_using_helpers(x, terms)
si = sin_taylor_f32_using_helpers(x, terms)
co = cos_taylor_f32_using_helpers(x, terms)


print("Input x (float32):", x, "hex:", f32_hex(x), "terms:", terms)
print("exp result:", ex, " hex:", f32_hex(ex))
print("sin result:", si, " hex:", f32_hex(si))
print("cos result:", co, "hex:", f32_hex(co))


