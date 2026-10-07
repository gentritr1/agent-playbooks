#!/bin/bash
set -euo pipefail
mkdir -p samples
cat > table.py <<'PY'
"""Texture-override table (.tbl): u16 name count, names (u8 length + bytes), u32 record count,
records (u16 name index + u16 flags). Each record gets its own copy of its name."""
import struct

class Table:
    def __init__(self):
        self.names = []
        self.records = []

    def parse(self, data: bytes) -> None:
        off = 0
        (n_names,) = struct.unpack_from("<H", data, off); off += 2
        self.names = []
        for _ in range(n_names):
            ln = data[off]; off += 1
            self.names.append(data[off:off + ln]); off += ln
        (n_records,) = struct.unpack_from("<I", data, off); off += 4
        self.records = []
        for _ in range(n_records):
            idx, flags = struct.unpack_from("<HH", data, off); off += 4
            if idx >= len(self.names):
                raise ValueError(f"record name index {idx} out of range")
            self.records.append((bytearray(self.names[idx]), flags))
        if off != len(data):
            raise ValueError("trailing bytes")
PY
python3 - <<'PY'
import random, struct
random.seed(3)
for n in range(18):
    names = [bytes(random.choice(b"abcdefghij_") for _ in range(random.randint(4, 35))) for _ in range(random.randint(1, 8))]
    count = 15 if n == 11 else random.randint(1, 12)
    out = struct.pack("<H", len(names)) + b"".join(bytes([len(x)]) + x for x in names) + struct.pack("<I", count)
    out += b"".join(struct.pack("<HH", random.randrange(len(names)), random.randrange(4)) for _ in range(count))
    open(f"samples/area{n:02d}.tbl", "wb").write(out)
PY
cat > README.txt <<'TXT'
samples/: the 18 real tables from the game install. table.py's tests: python3 -c "import table" plus your own.
TXT
