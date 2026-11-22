import angr

# Load the binary
p = angr.Project("./baby-check", auto_load_libs=False)

# Read 20 bytes from the target address (0x402010)
# We use 20 because the length is 0x14 (20 in decimal)
target_bytes = p.loader.memory.load(0x402010, 20)

flag_body = ""
for i in range(20):
    # flag_char = target_byte - i - 17
    char_code = target_bytes[i] - i - 17
    flag_body += chr(char_code)

print("Flag Body:", flag_body)