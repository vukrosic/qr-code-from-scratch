"""Run every part on real text, print what each step produces, and check the result with a real QR reader."""
import json
import random
import time

from encode import encode, to_bits
from rs import ec_codewords, generator, EXP, LOG, mul
from layout import blank, zigzag
from mask import apply, penalty, format_bits, draw_format, MASKS
from qr import make_qr, save_png, blocks

TEXT = 'hello, world'
URL = 'https://github.com/vukrosic/qr-code-from-scratch'
out = {'text': TEXT, 'url': URL}
bits = lambda v, w: ''.join(map(str, to_bits(v, w)))

print('== 1. encode')
data = TEXT.encode()
print('bytes:', list(data))
print('mode 0100 | length', bits(len(data), 8), '|', ' '.join(bits(b, 8) for b in data[:3]), '...')
words = encode(TEXT, 16)
print('16 data codewords:', words)
out['bytes'] = list(data)
out['data'] = words

print('\n== 2. error correction')
print('2^0..2^9 in GF(256):', EXP[:10], ' 2^8 =', EXP[8], ' 2^9 =', EXP[9])
print('mul(3, 7) =', mul(3, 7), '   3 xor 7 =', 3 ^ 7, '   mul(200, 100) =', mul(200, 100))
g = generator(10)
print('generator, 11 coefficients:', g)
print('as powers of 2:', [LOG[c] for c in g])
ec = ec_codewords(words, 10)
print('10 error-correction codewords:', ec)
out.update(exp=EXP[:12], gen=g, gen_log=[LOG[c] for c in g], ec=ec,
           mul_examples=[[3, 7, mul(3, 7)], [200, 100, mul(200, 100)], [2, 128, mul(2, 128)]])

print('\n== 3. layout')
grid, fixed = blank(1)
nfixed = sum(map(sum, fixed))
order = zigzag(21, fixed)
print(f'21 x 21 = {21 * 21} modules, {nfixed} fixed, {len(order)} for data = {len(order) // 8} codewords')
out.update(fixed=[''.join('1' if f else '0' for f in row) for row in fixed],
           blank=[''.join(map(str, row)) for row in grid], order=order, nfixed=nfixed)

print('\n== 4. masks')
final, info = make_qr(TEXT, 'M')
assert info['words'] == words + ec
from layout import place
raw, fx = blank(1)
place(raw, fx, words + ec)
draw_format(raw, format_bits('M', 0))
print('no mask penalty:', penalty(raw), '=', sum(penalty(raw)))
for m, s in enumerate(info['scores']):
    print(f'mask {m}: {s} = {sum(s)}', '<- lowest' if m == info['mask'] else '')
out.update(raw=[''.join(map(str, r)) for r in raw], raw_score=penalty(raw),
           scores=info['scores'], mask=info['mask'],
           masked=[[''.join(str(int(MASKS[m](x, y))) for x in range(21)) for y in range(21)] for m in range(8)])

print('\n== 5. format')
fb = format_bits('M', info['mask'])
print(f"level M = 00, mask {info['mask']} = {bits(info['mask'], 3)} -> 15 bits {bits(fb, 15)}")
out['format'] = bits(fb, 15)
out['final'] = [''.join(map(str, r)) for r in final]
save_png(final, 'hello.png')

print('\n== 6. read it back')
try:
    import cv2
    reader = cv2.QRCodeDetector()
    read = lambda path: reader.detectAndDecode(cv2.imread(path))[0]
except ImportError:
    read = None
    print('(pip install opencv-python to check with a real reader)')
if read:
    print('hello.png says:', repr(read('hello.png')))
    out['read'] = read('hello.png')

t0 = time.perf_counter()
for _ in range(20):
    make_qr(URL, 'M')
ms = (time.perf_counter() - t0) / 20 * 1000
big, binfo = make_qr(URL, 'M')
save_png(big, 'repo.png')
n = len(big)
print(f"repo link: version {binfo['version']}, {n} x {n}, mask {binfo['mask']}, built in {ms:.1f} ms")
out.update(repo=[''.join(map(str, r)) for r in big], repo_version=binfo['version'], repo_ms=round(ms, 1))
if read:
    print('repo.png says:', repr(read('repo.png')))
    out['repo_read'] = read('repo.png')

if read:
    print('\n== 7. damage: flip whole codewords, does it still read?')
    random.seed(7)
    cells = order[:208]
    rows = []
    for k in range(0, 9):
        ok = 0
        for trial in range(20):
            g2 = [row[:] for row in final]
            for w in random.sample(range(26), k):
                for x, y in cells[w * 8:w * 8 + 8]:
                    g2[y][x] ^= 1                  # every bit of that byte wrong
            save_png(g2, 'damaged.png')
            ok += read('damaged.png') == TEXT
        rows.append([k, ok])
        print(f'{k} bad codewords of 26: read {ok}/20')
    out['damage'] = rows

    print('\n== 8. a logo in the middle: biggest square that still reads')
    cover = []
    for level in 'LMQH':
        g0, li = make_qr(URL, level)
        n = len(g0)
        best = 0
        for k in range(1, n):
            g2 = [row[:] for row in g0]
            a = (n - k) // 2
            for y in range(a, a + k):
                for x in range(a, a + k):
                    g2[y][x] = 0
            save_png(g2, 'logo.png')
            if read('logo.png') == URL:
                best = k
        pct = round(100 * best * best / (n * n))
        cover.append([level, li['version'], n, best, pct])
        print(f'level {level}: version {li["version"]} ({n} x {n}), logo up to {best} x {best} = {pct}% of the code')
        if level == 'H':
            g2 = [row[:] for row in g0]
            a = (n - best) // 2
            for y in range(a, a + best):
                for x in range(a, a + best):
                    g2[y][x] = 0
            out['logo_grid'] = [''.join(map(str, r)) for r in g2]
            out['logo_best'] = best
    out['cover'] = cover

json.dump(out, open('demo.json', 'w'))
print('\nwrote demo.json')
