"""Part 5 - put it together: pick a version, add error correction, place, mask, save a PNG."""
import struct
import sys
import zlib

from encode import encode
from rs import ec_codewords
from layout import blank, place
from mask import apply, penalty, format_bits, draw_format

# error-correction bytes per block and number of blocks, versions 1-6 (ISO/IEC 18004 table 9)
EC_TABLE = {
    'L': [(7, 1), (10, 1), (15, 1), (20, 1), (26, 1), (18, 2)],
    'M': [(10, 1), (16, 1), (26, 1), (18, 2), (24, 2), (16, 4)],
    'Q': [(13, 1), (22, 1), (18, 2), (26, 2), (18, 4), (24, 4)],
    'H': [(17, 1), (28, 1), (22, 2), (16, 4), (22, 4), (28, 4)],
}


def total_codewords(version):
    grid, fixed = blank(version)
    return sum(not f for row in fixed for f in row) // 8


def blocks(version, level):
    ec, n = EC_TABLE[level][version - 1]
    total = total_codewords(version)
    short = n - total % n                           # some blocks hold one byte more
    return [total // n - ec + (i >= short) for i in range(n)], ec


def make_qr(text, level='M', mask=None):
    for version in range(1, 7):                     # the smallest version that fits
        sizes, ec = blocks(version, level)
        if len(text.encode('utf-8')) + 2 <= sum(sizes):
            break
    else:
        raise ValueError('text too long for versions 1-6')
    data = encode(text, sum(sizes))
    parts, i = [], 0
    for s in sizes:
        parts.append(data[i:i + s])
        i += s
    checks = [ec_codewords(p, ec) for p in parts]
    words = [p[k] for k in range(max(sizes)) for p in parts if k < len(p)]
    words += [c[k] for k in range(ec) for c in checks]   # interleave the blocks
    grid, fixed = blank(version)
    place(grid, fixed, words)
    scores = []
    for m in range(8):                              # try all 8 masks, keep the cheapest
        g = apply(grid, fixed, m)
        draw_format(g, format_bits(level, m))
        scores.append(penalty(g))
    best = min(range(8), key=lambda m: sum(scores[m])) if mask is None else mask
    out = apply(grid, fixed, best)
    draw_format(out, format_bits(level, best))
    return out, dict(version=version, level=level, mask=best, data=data,
                     ec=checks, words=words, scores=scores)


def save_png(grid, path, scale=10, border=4):
    n = len(grid) + 2 * border
    rows = []
    for y in range(n * scale):
        gy = y // scale - border
        row = bytes(0 if 0 <= gy < len(grid) and 0 <= x // scale - border < len(grid)
                    and grid[gy][x // scale - border] else 255 for x in range(n * scale))
        rows.append(b'\0' + row)
    def chunk(tag, body):
        return struct.pack('>I', len(body)) + tag + body + struct.pack('>I', zlib.crc32(tag + body))
    head = struct.pack('>IIBBBBB', n * scale, n * scale, 8, 0, 0, 0, 0)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', head) +
                chunk(b'IDAT', zlib.compress(b''.join(rows))) + chunk(b'IEND', b''))


if __name__ == '__main__':
    text = sys.argv[1] if len(sys.argv) > 1 else 'hello, world'
    grid, info = make_qr(text)
    save_png(grid, 'qr.png')
    for row in grid:
        print(''.join('██' if v else '  ' for v in row))
    print(f"version {info['version']}, level {info['level']}, mask {info['mask']} -> qr.png")
