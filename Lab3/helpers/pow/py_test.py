#!/usr/bin/env python3
import struct, json, subprocess, tempfile, shutil, pathlib, re, sys

# ------------ CONFIG ------------
ASM_SOURCE   = "/home/omdave/CompArch/Lab3/helpers/pow/pow.s"
VM_EXPECT    = "./run_vm.exp"                    # your existing expect runner
OUT_BASE_HEX = "0x0000000010000200"              # where results start (fsd)
TESTS = [
    (0x3f800000, 3),  
    (0x40000000, 2),  
    (0x3f19999a, 5),  
    (0x40200000, 4),  
    (0x3fc00000, 7),   
    (0x0000000, 7),   
]
# ---------------------------------

HERE = pathlib.Path.cwd()

# --- FP32 helpers ---
def f32(x: float) -> float:
    """Round to IEEE-754 single precision."""
    return struct.unpack('<f', struct.pack('<f', x))[0]

def f32_from_bits(u32: int) -> float:
    """Interpret 32-bit pattern as IEEE-754 single float."""
    return struct.unpack('<f', struct.pack('<I', u32 & 0xffffffff))[0]

def f32_bits(x: float) -> int:
    """Return 32-bit pattern of IEEE-754 single float."""
    return struct.unpack('<I', struct.pack('<f', x))[0]

def ref_bits_from_bits(x_bits: int, n: int) -> int:
    """Simulate your asm semantics: x from bits (flw), then n x fmul.s."""
    x = f32_from_bits(x_bits)
    y = f32(1.0)
    for _ in range(n):
        y = f32(y * x)   # force single-precision rounding each multiply
    return f32_bits(y)

# --- Rewrite the .word line for T pairs (bits, n) ---
def rewrite_inputs_to_temp(asm_path: pathlib.Path, test_pairs) -> pathlib.Path:
    src = asm_path.read_text()
    T = len(test_pairs)
    # Build: .word T, x1_bits, n1, x2_bits, n2, ...
    items = [str(T)]
    for xb, n in test_pairs:
        # Keep hex formatting for readability in the .s
        xb_str = xb if isinstance(xb, str) else hex(int(xb))
        items.extend([xb_str, str(int(n))])
    new_word = ".word " + ", ".join(items)

    out = re.sub(r'(?m)^\s*\.word\s+.*$', new_word, src, count=1)
    tmpdir = pathlib.Path(tempfile.mkdtemp(prefix="powmulti_"))
    tmpasm = tmpdir / "pow_multi_tmp.s"
    tmpasm.write_text(out)
    return tmpasm

# --- Run VM via expect and get memory_dump.json path ---
def run_vm(asm_temp: pathlib.Path, T: int):
    # Clean previous dumps
    for p in [HERE/"memory_dump.json", HERE/"vm_state"/"memory_dump.json"]:
        if p.exists(): p.unlink()
    # Third arg is number of QWORDS to dump (T results)
    cmd = [VM_EXPECT, str(asm_temp), OUT_BASE_HEX, str(T)]
    subprocess.run(cmd, check=True)
    # Prefer vm_state/ if present
    cand = HERE/"vm_state"/"memory_dump.json"
    if cand.exists(): return cand
    cand = HERE/"memory_dump.json"
    if cand.exists(): return cand
    raise FileNotFoundError("memory_dump.json not found after VM run")

def load_dump_as_int_map(dump_path: pathlib.Path) -> dict[int,int]:
    j = json.loads(dump_path.read_text())
    return {int(k, 16): int(v, 16) for k, v in j.items()}

def main():
    asm = pathlib.Path(ASM_SOURCE)
    T = len(TESTS)
    tmpasm = rewrite_inputs_to_temp(asm, TESTS)
    try:
        dump_path = run_vm(tmpasm, T)
        dump = load_dump_as_int_map(dump_path)

        base = int(OUT_BASE_HEX, 16)
        print("\nRESULTS (one VM run)")
        print("idx  x_bits       n    PASS  asm_bits     ref_bits     asm_float        ref_float")
        all_ok = True
        for i, (x_bits, n) in enumerate(TESTS):
            addr = base + 8*i               # one QWORD per result
            v64  = dump.get(addr)
            if v64 is None:
                raise KeyError(f"Address 0x{addr:016x} missing in dump")
            asm_bits = v64 & 0xffffffff     # low 32 bits hold the single
            ref_bits = ref_bits_from_bits(int(x_bits), int(n))

            asm_f = struct.unpack('<f', struct.pack('<I', asm_bits))[0]
            ref_f = struct.unpack('<f', struct.pack('<I', ref_bits))[0]
            ok = (asm_bits == ref_bits)
            all_ok &= ok
            print(f"{i:>3}  0x{int(x_bits):08x}  {int(n):<4} {'PASS' if ok else 'FAIL'}  "
                  f"0x{asm_bits:08x}  0x{ref_bits:08x}  {asm_f:.9g}  {ref_f:.9g}")

        if not all_ok:
            sys.exit(1)

    finally:
        shutil.rmtree(tmpasm.parent, ignore_errors=True)

if __name__ == "__main__":
    main()
