# SemSec National CTF — 1st Place Write-Ups

## Executive Summary
We competed in a high-stakes Capture The Flag (CTF) competition and took **1st Place**. I operated as the primary reverse engineer and problem solver for the team, successfully tackling a series of complex, deliberately obfuscated binaries and mathematical constraint-solving challenges.

Here is the technical breakdown of the reverse engineering challenges we conquered.

---

## 🛠️ The Challenges

### 1. `baby-check` (Reverse Engineering)
* **The Trap:** A stripped Linux x86-64 binary with no plaintext strings containing the flag.
* **The Solve:** I manually loaded the binary into Ghidra, located `main`, and decompiled the check function. I identified a character-by-character math check:
  $$\text{Input}[i] + i + 17 == \text{Target}[i]$$
* **Execution:** Used `angr` to read the target byte array from `.rodata` memory and wrote a Python solver (`solver.py`) to reverse the math and extract the 20-character flag body:
  $$\text{Input}[i] = \text{Target}[i] - i - 17$$
* **Flag:** `SemSec{s1mpl3_ch4rsum_1s_ez}`

---

### 2. `mixer` (Reverse Engineering — 100 pts, 3 Solves)
* **The Trap:** Forward and backward cumulative sums across 21 characters that generated an exponential number of paths, causing symbolic execution (`angr`) to crash due to state/path explosion.
* **The Solve:** I decompiled the math in Ghidra and recognized it as a set of linear constraints with forward accumulator $A$ (seeded with `0x5a`) and backward accumulator $B$ (seeded with `0x7e`), checking:
  $$(A[i] \oplus B[i]) == \text{Target}[i]$$
* **Execution:** Translated the C code into a Python script using **Z3**, the SMT theorem prover (`mixer.py`). Z3 mathematically modeled the bytes and solved all 21 constraints simultaneously in milliseconds.
* **Flag:** `SemSec{z3_s0lv3s_1t_4_u_fr3e}`

---

### 3. `verdict` (Reverse Engineering / Forensics — 500 Points)
* **The Trap:** A C++ binary that shuffled 25 image tiles using a custom PRNG seeded with `0x1337`, split a file into a grid, and applied a complex diagonal bitwise non-linear mutation (`FUN_00105a00`).
* **The Breakthrough:** Instead of wasting time trying to perfectly replicate the C++ `std::mt19937` PRNG in Python, I extracted the exact tile mapping natively by running the Linux binary on a dummy image and generated mapping tools (`mapper.cpp`).
* **The Critical Discovery:** The binary padded the matrix to $130 \times 130$ with random bytes. However, the true original image was $126 \times 126$. Feeding the random padding into the binary's `--inverse` algorithm corrupted the image. By cropping the matrix back to $126 \times 126$ before running `./verdict --inverse --anti`, the math aligned perfectly.
* **Execution:** Reassembled the 25 `.0b3l1sk` tiles, cropped the padding, inverted the diagonal LCG/affine mutations via `solve_verdict.py`, and extracted the final QR code (`final_solved.png`).

---

### 4. `false-witness` (Reverse Engineering — 500 Points)
* **The Trap:** A massive **64.77 MiB** 32-bit ELF designed to crash Ghidra and waste reverse-engineering time. It contained a massive obfuscated Virtual Machine.
* **The Solve:** I parsed the raw ELF header and section table via a custom Python script (`false.py`) to carve out only the `.text` (code) section, bypassing the 64MB bloat. In Ghidra, I found the actual check right at the entry point: it verified `argc == 5` and ran a simple 24-byte XOR cipher before even touching the VM.
* **Execution:** Reversed the XOR cipher at offset `0xC0E12` with key schedule `b ^ ((i * 0x1d + 0xa7) & 0xFF)` via `solve_false.py`, extracted the decoy string `th3y_c@ll_me_th3_0b3l1sk`, and bypassed the entire 64MB trap.

---

## 📁 Repository Contents
* `solver.py` — `baby-check` memory extraction & linear math inversion solver.
* `mixer.py` — `mixer` Z3 SMT constraint satisfaction solver.
* `solve_verdict.py` / `mapper.cpp` — `verdict` PRNG tile reconstruction & diagonal inverse matrix mutator.
* `final_solved.png` — Reconstructed `verdict` visual output.
* `solve_false.py` / `false.py` — `false-witness` ELF header carver & XOR decryptor.
* Challenge binaries: `baby-check`, `mixer`, `false-witness`, `verdict`.
