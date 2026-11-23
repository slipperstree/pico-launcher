import struct
from pathlib import Path
import sys

path = Path(sys.argv[1])
sectors = 131072
fat_sectors = 1024
boot = bytearray(512)
boot[0:3] = b'\xeb\x58\x90'
boot[3:11] = b'MSWIN4.1'
struct.pack_into('<HBHBHHBHHHII', boot, 11, 512, 1, 32, 2, 0, 0, 0xf8, 0, 63, 255, 0, sectors)
struct.pack_into('<IHHIHH', boot, 36, fat_sectors, 0, 0, 2, 1, 6)
boot[64] = 0x80
boot[66] = 0x29
struct.pack_into('<I', boot, 67, 12345678)
boot[71:82] = b'CHINESETEST'
boot[82:90] = b'FAT32   '
boot[510:512] = b'\x55\xaa'
info = bytearray(512)
struct.pack_into('<I', info, 0, 0x41615252)
struct.pack_into('<III', info, 484, 0x61417272, 0xffffffff, 3)
struct.pack_into('<I', info, 508, 0xaa550000)
with path.open('wb') as f:
    f.truncate(sectors * 512)
    for sector, data in [(0, boot), (6, boot), (1, info), (7, info)]:
        f.seek(sector * 512)
        f.write(data)
    for start in [32, 32 + fat_sectors]:
        f.seek(start * 512)
        f.write(struct.pack('<III', 0x0ffffff8, 0xffffffff, 0x0fffffff))
print('Created isolated 64 MiB FAT32 test image:', path)
