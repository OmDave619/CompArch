# Float32 Taylor-series driver (matches your assembly input pattern)
# - Input format: [N, func_code1, x1_bits_or_float, terms1, func_code2, x2, terms2, ...]
# - func_code: 0=exp, 1=sin, 2=cos, 3=ln, 4=1/x
# - Outputs each result with function name, code, decimal value, and hex bits.
# - All math is rounded to float32 at every step, like your helpers.

import struct

# -------- float32 utils --------
def to_f32(x: float) -> float:
    return struct.unpack('>f', struct.pack('>f', float(x)))[0]

def f32_hex(f: float) -> str:
    return f"0x{struct.unpack('>I', struct.pack('>f', float(f)))[0]:08x}"

def bits_to_f32(u32: int) -> float:
    return struct.unpack('>f', struct.pack('>I', u32 & 0xffffffff))[0]

def qnan_f32() -> float:
    return bits_to_f32(0x7fc00000)

# -------- helpers used by “assembly-like” implementations --------
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

# -------- series (mirror your assembly order & rounding) --------
def exp_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    s = to_f32(0.0)
    for n in range(terms-1, -1, -1):
        fn_f32 = to_f32(float(fact_int(n)))
        px = pow_f32(x_f32, n)
        term = to_f32(px / fn_f32)
        s = to_f32(s + term)
    return s

def sin_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    s = to_f32(0.0)
    for k in range(terms-1, -1, -1):
        e = 2*k + 1
        fe_f32 = to_f32(float(fact_int(e)))
        px = pow_f32(x_f32, e)
        term = to_f32(px / fe_f32)
        if (k & 1) == 1:  # odd -> negative
            term = to_f32(-term)
        s = to_f32(s + term)
    return s

def cos_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    s = to_f32(0.0)
    for k in range(terms-1, -1, -1):
        e = 2*k
        fe_f32 = to_f32(float(fact_int(e)))
        px = pow_f32(x_f32, e)
        term = to_f32(px / fe_f32)
        if (k & 1) == 1:  # odd -> negative
            term = to_f32(-term)
        s = to_f32(s + term)
    return s

def ln_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    # while (k>0): term = (x-1)^k / k; if k even negate; sum+=term; k--
    s = to_f32(0.0)
    u = to_f32(to_f32(x_f32) - to_f32(1.0))
    k = int(terms)
    while k > 0:
        term = to_f32(pow_f32(u, k) / to_f32(float(k)))
        if (k & 1) == 0:  # even -> negate (since (-1)^(k+1))
            term = to_f32(-term)
        s = to_f32(s + term)
        k -= 1
    return s

def one_over_x_taylor_f32_using_helpers(x_f32: float, terms: int) -> float:
    # Using u = 1 - x: 1/x = 1/(1-u) ≈ sum u^k, k=0..terms-1
    s = to_f32(0.0)
    u = to_f32(to_f32(1.0) - to_f32(x_f32))
    for k in range(terms-1, -1, -1):
        s = to_f32(s + pow_f32(u, k))
    return s

# -------- dispatcher / driver --------
FUNC_MAP = {
    0: ("exp", exp_taylor_f32_using_helpers,  False, None),             # no domain check
    1: ("sin", sin_taylor_f32_using_helpers,  False, None),
    2: ("cos", cos_taylor_f32_using_helpers,  False, None),
    3: ("ln",  ln_taylor_f32_using_helpers,   True,  lambda x: x > 0.0), # domain: x>0
    4: ("inv", one_over_x_taylor_f32_using_helpers, True,  lambda x: x != 0.0), # domain: x!=0
}

def parse_x(x_word_or_float):
    # Accept either a float (e.g., 2.0) or a 32-bit int word (e.g., 0x40000000)
    if isinstance(x_word_or_float, float):
        return to_f32(x_word_or_float)
    if isinstance(x_word_or_float, int):
        return bits_to_f32(x_word_or_float)
    # strings like "0x3f800000"
    if isinstance(x_word_or_float, str) and x_word_or_float.lower().startswith("0x"):
        return bits_to_f32(int(x_word_or_float, 16))
    # fallback
    return to_f32(float(x_word_or_float))

def process_inputs(data):
    """
    data = [N, func, x_bits_or_float, terms, func, x, terms, ...]
    Returns list of (func_code, func_name, result_float32).
    Applies:
      - terms > 0 check
      - basic domain checks for ln and inv
      - qNaN on invalid cases
    """
    out = []
    if not data:
        return out
    N = int(data[0])
    idx = 1
    for _ in range(N):
        func_code = int(data[idx]); x_in = data[idx+1]; terms = int(data[idx+2]); idx += 3
        name, fn, needs_domain, pred = FUNC_MAP.get(func_code, ("invalid", None, False, None))

        # decode x to float32
        x = parse_x(x_in)

        # default result is qNaN if invalid func or bad params
        res = qnan_f32()
        if name == "invalid" or terms <= 0:
            out.append((func_code, name, res))
            continue

        # domain checks (if required)
        if needs_domain and pred is not None:
            try:
                if not pred(x):
                    out.append((func_code, name, res))
                    continue
            except Exception:
                out.append((func_code, name, res))
                continue

        # compute
        try:
            res = fn(x, terms)
        except Exception:
            res = qnan_f32()
        out.append((func_code, name, res))
    return out

def print_results(results):
    for code, name, val in results:
        print(f"{name} (code {code}): {val}   hex: {f32_hex(val)}")

# -------- demo --------
if __name__ == "__main__":
    # Example input buffer equivalent to:
    # N=5
    #   (sin, 1.0f, 5)
    #   (exp, 2.0f, 8)
    #   (cos, 1.0f, 5)
    #   (ln,  1.5f, 6)
    #   (1/x, 0.5f, 6)
    data = [
        5,
        1, 0x3f800000, 5,
        0, 0x40000000, 8,
        2, 0x3f800000, 5,
        3, 0x3fc00000, 6,
        4, 0x3f000000, 6,
    ]
    results = process_inputs(data)
    print_results(results)
