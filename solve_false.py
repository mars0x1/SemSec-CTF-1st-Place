import os
import zipfile

# Auto-extract binary if compressed
if not os.path.exists("false-witness") and os.path.exists("false-witness.zip"):
    print("[*] Extracting false-witness from zip...")
    with zipfile.ZipFile("false-witness.zip") as z:
        z.extract("false-witness")

with open("false-witness", "rb") as f:
    # Seek to authentic payload offset
    f.seek(0xC0E12)
    target = f.read(24)

flag = ""
for i, b in enumerate(target):
    val = b ^ ((i * 0x1d + 0xa7) & 0xFF)
    flag += chr(val)

print(f"[+] Real Flag Body: {flag}")
print(f"[+] Flag: SemSec{{{flag}}}")
