import struct

with open("false-witness", "rb") as f:
    data = f.read()

# Read ELF header
e_shoff = struct.unpack_from("<I", data, 0x20)[0]
e_shentsize = struct.unpack_from("<H", data, 0x2e)[0]
e_shnum = struct.unpack_from("<H", data, 0x30)[0]
e_shstrndx = struct.unpack_from("<H", data, 0x32)[0]

# Get string table offset
sh_strtab_offset = struct.unpack_from("<I", data, e_shoff + e_shstrndx * e_shentsize + 0x10)[0]
sh_strtab = data[sh_strtab_offset:]

print(f"Number of sections: {e_shnum}")
for i in range(e_shnum):
    offset = e_shoff + i * e_shentsize
    sh_name = struct.unpack_from("<I", data, offset)[0]
    sh_addr = struct.unpack_from("<I", data, offset + 0x0c)[0]
    sh_offset = struct.unpack_from("<I", data, offset + 0x10)[0]
    sh_size = struct.unpack_from("<I", data, offset + 0x14)[0]
    
    name = sh_strtab[sh_name:sh_strtab.find(b'\x00', sh_name)].decode()
    print(f"[{i}] {name} (Addr: {hex(sh_addr)}, Offset: {hex(sh_offset)}, Size: {hex(sh_size)})")
    
    if name == ".text":
        with open("text_section.bin", "wb") as out:
            out.write(data[sh_offset:sh_offset+sh_size])
        print(f"    -> Extracted .text to text_section.bin")