import os
from PIL import Image

# 1. Replicate the exact MT19937 PRNG (GCC Standard)
class MT19937:
    def __init__(self, seed):
        self.mt = [0] * 624
        self.mt[0] = seed & 0xFFFFFFFF
        for i in range(1, 624):
            self.mt[i] = (1812433253 * (self.mt[i-1] ^ (self.mt[i-1] >> 30)) + i) & 0xFFFFFFFF
        self.index = 624

    def generate(self):
        if self.index >= 624:
            self.twist()
        y = self.mt[self.index]
        y ^= (y >> 11)
        y ^= (y << 7) & 0x9d2c5680
        y ^= (y << 15) & 0xefc60000
        y ^= (y >> 18)
        self.index += 1
        return y & 0xFFFFFFFF

    def twist(self):
        for i in range(624):
            y = (self.mt[i] & 0x80000000) + (self.mt[(i+1) % 624] & 0x7fffffff)
            self.mt[i] = self.mt[(i+397) % 624] ^ (y >> 1)
            if y % 2 != 0:
                self.mt[i] ^= 2567483615
        self.index = 0

def uniform_int_distribution(gen, lower, upper):
    urngrange = 0x100000000 # Exactly 2^32
    urange = upper - lower
    if urngrange > urange:
        uerange = urange + 1
        scaling = urngrange // uerange
        past = uerange * scaling
        while True:
            ret = gen.generate()
            if ret < past:
                return lower + ret // scaling
    return lower + (gen.generate() % (urange + 1))

# Forward Fisher-Yates (Exact C++ std::shuffle logic)
def std_shuffle(v, gen):
    for i in range(1, len(v)):
        j = uniform_int_distribution(gen, 0, i)
        v[i], v[j] = v[j], v[i]
    return v

# 2. Generate the exact write sequence
gen = MT19937(0x1337)
perm = list(range(25))
std_shuffle(perm, gen)

filenames = []
for _ in range(25):
    name = ""
    for _ in range(6):
        name += "0123456789abcdef"[uniform_int_distribution(gen, 0, 15)]
    filenames.append(name + ".0b3l1sk")

print("Expected first 5 files:", filenames[:5])

# 3. Read and assemble the 130x130 matrix
N = 130
tile_size = 26
matrix = bytearray(N * N)
tiles_dir = "verdict/verdict-tiles" if os.path.exists("verdict/verdict-tiles") else "verdict-tiles"
zip_path = "verdict/verdict-tiles.zip" if os.path.exists("verdict/verdict-tiles.zip") else "verdict-tiles.zip"

missing = False
for name in filenames:
    if not os.path.exists(os.path.join(tiles_dir, name)):
        print(f"[-] Missing predicted file: {name}")
        missing = True
        break

if missing:
    print("[-] PRNG mismatch. Falling back to zip insertion order...")
    import zipfile
    with zipfile.ZipFile(zip_path) as z:
        names = [n for n in z.namelist() if n.endswith(".0b3l1sk")]
        for i, name in enumerate(names):
            data = z.read(name)
            orig_idx = perm[i]
            row = orig_idx // 5
            col = orig_idx % 5
            for r in range(tile_size):
                for c in range(tile_size):
                    matrix[(row * tile_size + r) * N + (col * tile_size + c)] = data[r * tile_size + c]
else:
    for i, name in enumerate(filenames):
        with open(os.path.join(tiles_dir, name), "rb") as f:
            data = f.read()
        orig_idx = perm[i]
        row = orig_idx // 5
        col = orig_idx % 5
        for r in range(tile_size):
            for c in range(tile_size):
                matrix[(row * tile_size + r) * N + (col * tile_size + c)] = data[r * tile_size + c]

# 4. Apply the Inverse Mutation (FUN_00105a00)
def inverse_mutation(matrix, N, x, y):
    n = N - y
    if N - x < N - y:
        n = N - x
    if n == 0:
        return
    
    idx = x * N + y
    bVar1 = (matrix[idx] * 205 + 131) & 0xFF
    
    s = [0] * n
    bVar2 = bVar1
    for i in range(1, n):
        bVar2 = (bVar2 * 137 + 187) & 0xFF
        s[i] = bVar2
    
    for i in range(1, n):
        idx_next = (x + i) * N + (y + i)
        val = matrix[idx_next]
        
        term = ((bVar1 * 0x802) & 0x22110) | ((bVar1 * 0x8020) & 0x88440)
        term = (term * 0x10101) >> 16
        term = term & 0xFF
        
        bVar2 = (val ^ term) & 0xFF
        
        shift = bVar1 & 7
        if shift == 0:
            rotated = bVar2
        else:
            rotated = ((bVar2 >> shift) | (bVar2 << (8 - shift))) & 0xFF
        
        matrix[idx_next] = (rotated - s[i]) & 0xFF
    
    matrix[x * N + y] = bVar1

# Unmix diagonals (order doesn't matter since they are disjoint)
for i in range(1, N):
    inverse_mutation(matrix, N, i, 0)
for i in range(N):
    inverse_mutation(matrix, N, 0, i)

# 5. Save the final image
img = Image.frombytes("L", (N, N), bytes(matrix))
img = img.resize((N * 4, N * 4), Image.NEAREST)
img.save("final_solved.png")
print("[+] Saved final_solved.png. Open it to get the flag!")