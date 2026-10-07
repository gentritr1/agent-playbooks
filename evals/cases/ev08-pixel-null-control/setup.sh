#!/bin/bash
set -euo pipefail
python3 - <<'PY'
import random
W, H = 64, 64
def img(seed, extra=()):
    random.seed(1)
    px = [[(240, 240, 240) for _ in range(W)] for _ in range(H)]
    for y in range(20, 44):
        for x in range(10, 54):
            px[y][x] = (40, 40, 60)
    random.seed(seed)
    for _ in range(4):                       # antialiasing jitter between launches
        y, x = random.choice([20, 43]), random.randrange(10, 54)
        r, g, b = px[y][x]; px[y][x] = (r + 3, g + 3, b + 3)
    for (y, x) in extra:
        px[y][x] = (255, 0, 0)
    return px
def save(name, px):
    with open(name, "w") as f:
        f.write(f"P3\n{W} {H}\n255\n")
        for row in px:
            f.write(" ".join(f"{r} {g} {b}" for r, g, b in row) + "\n")
save("base-a.ppm", img(11))
save("base-b.ppm", img(12))          # same build, reinstalled
save("off.ppm", img(13))             # flag-OFF build of the change
PY
echo "base-a and base-b: the same APK installed twice. off: the new build with the feature flag OFF." > README.txt
