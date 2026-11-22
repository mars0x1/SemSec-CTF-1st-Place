import angr
import z3
import logging

# Suppress angr logs
logging.getLogger('angr').setLevel('ERROR')
logging.getLogger('cle').setLevel('ERROR')

# 1. Load the binary to extract the target array
proj = angr.Project("./mixer", auto_load_libs=False)
# Read 21 bytes from DAT_00402010
target_bytes = proj.loader.memory.load(0x402010, 21)

# 2. Set up the Z3 solver
s = z3.Solver()

# Create 21 symbolic bytes for the flag body
flag = [z3.BitVec(f'c{i}', 8) for i in range(21)]

# Constrain the flag to printable ASCII characters
for c in flag:
    s.add(c >= 0x20, c <= 0x7e)

# 3. Recreate the forward mixing (abStack_48)
A = [z3.BitVecVal(0, 8) for _ in range(21)]
prev_A = z3.BitVecVal(0x5a, 8)
for i in range(21):
    A[i] = flag[i] + prev_A
    prev_A = A[i]

# 4. Recreate the backward mixing (abStack_28)
B = [z3.BitVecVal(0, 8) for _ in range(21)]
prev_B = z3.BitVecVal(0x7e, 8)
for i in range(20, -1, -1):
    B[i] = flag[i] + prev_B
    prev_B = B[i]

# 5. Add the final target check constraints
for i in range(21):
    s.add((A[i] ^ B[i]) == target_bytes[i])

# 6. Solve!
if s.check() == z3.sat:
    m = s.model()
    body = bytes([m.eval(c).as_long() for c in flag]).decode()
    print(f"\n[+] Flag body found: {body}")
    print(f"[+] Submit as: SemSec{{{body}}}")
else:
    print("[-] Z3 could not solve it.")