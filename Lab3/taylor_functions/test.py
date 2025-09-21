# Float32 Taylor-series verifiers using helpers (fact + pow), mirroring your assembly style.
# - All math rounded to float32 via to_f32()
# - Sums in the SAME order as your loops: from terms-1 down to 0
# - Functions: exp, sin, cos, ln, one_over_x (1/x via 1/(1+u) with u=x-1)

import struct

def to_f32(x: float) -> float:
    return struct.unpack('>f', struct.pack('>f', float(x)))[0]

def f32_hex(f: float) -> str:
    b = struct.pack('>f', float(f))
    u = struct.unpack('>I', b)[0]
    return f"0x{u:08x}"

def fact_int(n: int) -> int:
    if n <= 1:
        return 1
    p = 1
    for k in range(2, n+1):
        p *= k
    return p

def pow_f32(x_f32: float, n: int) -> float:
    x = to_f32(x_f32)
    if n == 0:
        return to_f32(1.0)
    acc = to_f32(1.0)
    for _ in range(n):
        acc = to_f32(acc * x)
    return acc

def exp_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    s = to_f32(0.0)
    for n in range(terms-1, -1, -1):
        fn = fact_int(n)
        fn_f32 = to_f32(float(fn))
        px = pow_f32(x_f32, n)
        term = to_f32(px / fn_f32)
        s = to_f32(s + term)
    return s

def sin_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    # sin(x) ≈ Σ_{k=0..terms-1} (-1)^k x^(2k+1)/(2k+1)!
    s = to_f32(0.0)
    for k in range(terms-1, -1, -1):
        e = 2*k + 1
        fe = fact_int(e)
        fe_f32 = to_f32(float(fe))
        px = pow_f32(x_f32, e)
        term = to_f32(px / fe_f32)
        if (k & 1) == 1:                # odd k -> negative
            term = to_f32(-term)
        s = to_f32(s + term)
    return s

def cos_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    # cos(x) ≈ Σ_{k=0..terms-1} (-1)^k x^(2k)/(2k)!
    s = to_f32(0.0)
    for k in range(terms-1, -1, -1):
        e = 2*k
        fe = fact_int(e)
        fe_f32 = to_f32(float(fe))
        px = pow_f32(x_f32, e)
        term = to_f32(px / fe_f32)
        if (k & 1) == 1:                # odd k -> negative
            term = to_f32(-term)
        s = to_f32(s + term)
    return s

def ln_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    """
    ln(x) ≈ Σ_{k=1..terms} (-1)^{k+1} (x-1)^k / k
    Mirrors the assembly control flow:
      while (k > 0):
        term = pow_f32(u, k) / float32(k)
        if k even: term = -term
        sum += term
        k -= 1
    All ops rounded to float32.
    """
    s = to_f32(0.0)
    u = to_f32(to_f32(x_f32) - to_f32(1.0))
    k = int(terms)
    while k > 0:
        k_f32 = to_f32(float(k))
        pk = pow_f32(u, k)
        term = to_f32(pk / k_f32)
        if (k & 1) == 0:                 # even k -> negate (since (-1)^{k+1})
            term = to_f32(-term)
        s = to_f32(s + term)
        k -= 1
    return s


def one_over_x_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    """
    1/x with u = 1 - x:
      1/x = 1/(1 - u) = Σ_{k=0..terms-1} u^k,  |u| < 1
    Mirrors the assembly: compute u = 1 - x, sum k = terms-1..0, float32 rounding each step.
    """
    s = to_f32(0.0)
    u = to_f32(to_f32(1.0) - to_f32(x_f32))
    for k in range(terms-1, -1, -1):
        pk = pow_f32(u, k)          # u^k in float32
        s = to_f32(s + pk)
    return s


# ---- demo ----
if __name__ == "__main__":
    x = to_f32(0.7)      
    terms = 5

    ex  = exp_taylor_f32_using_helpers(x, terms)
    si  = sin_taylor_f32_using_helpers(x, terms)
    co  = cos_taylor_f32_using_helpers(x, terms)
    ln_ = ln_taylor_f32_using_helpers(x, terms)
    inv = one_over_x_taylor_f32_using_helpers(x, terms)

    print("x:", x, "hex:", f32_hex(x), " terms:", terms)
    print("exp:", ex,  "hex:", f32_hex(ex))
    print("sin:", si,  "hex:", f32_hex(si))
    print("cos:", co,  "hex:", f32_hex(co))
    print("ln :", ln_, "hex:", f32_hex(ln_))
    print("1/x:", inv, "hex:", f32_hex(inv))
