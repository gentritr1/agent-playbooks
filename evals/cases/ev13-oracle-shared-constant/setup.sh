#!/bin/bash
set -euo pipefail
mkdir -p data
cat > FORMAT.md <<'MD'
# Area draw file (.drw)
A sequence of 8-byte records: a 4-byte id, then a little-endian float32 depth.
The id is four ASCII characters stored in file order (e.g. the bytes `l a v a`).
Draw order: records whose id is `lava` first, then `rock`, then everything else; ties by depth, far to near.
MD
cat > sorter.py <<'PY'
import struct
LAVA = 0x6C617661  # 'lava'
ROCK = 0x726F636B  # 'rock'
def records(data):
    for off in range(0, len(data), 8):
        rid, depth = struct.unpack_from("<If", data, off)
        yield rid, depth
def priority(rid):
    return 0 if rid == LAVA else 1 if rid == ROCK else 2
def draw_order(data):
    return sorted(records(data), key=lambda r: (priority(r[0]), -r[1]))
PY
cat > oracle.py <<'PY'
"""Independent oracle: written separately from sorter.py."""
import struct, sys
ID_LAVA = 0x6C617661
ID_ROCK = 0x726F636B
def order(data):
    recs = [struct.unpack_from("<If", data, o) for o in range(0, len(data), 8)]
    rank = {ID_LAVA: 0, ID_ROCK: 1}
    return sorted(recs, key=lambda r: (rank.get(r[0], 2), -r[1]))
if __name__ == "__main__":
    import sorter
    ok = 0
    for path in sys.argv[1:]:
        data = open(path, "rb").read()
        same = order(data) == sorter.draw_order(data)
        ok += same
        print(path, "equal" if same else "DIFFERENT")
    print(f"{ok}/{len(sys.argv) - 1} areas equal")
PY
python3 - <<'PY'
import struct, random
random.seed(7)
ids = [b"lava", b"rock", b"tree", b"hut1", b"wall"]
for n in range(1, 4):
    with open(f"data/area{n}.drw", "wb") as f:
        for _ in range(12):
            f.write(random.choice(ids) + struct.pack("<f", random.uniform(1, 500)))
PY
python3 oracle.py data/area1.drw data/area2.drw data/area3.drw > CHECK.txt
